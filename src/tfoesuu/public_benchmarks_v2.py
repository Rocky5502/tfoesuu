from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np

from .public_benchmarks import PublicBenchmarkSpec, public_benchmark_registry_v1

V2_SCHEMA = "tfoesuu-public-context-v2.1"
V2_VALUE_ENCODING = "canonical-json-scalars-v1"
V2_NPZ_KEYS = {
    "baseline_probabilities",
    "evaluation_labels",
    "source_row_positions",
    "protected_attribute_values",
    "non_protected_feature_values",
    "training_labels",
    "training_source_row_positions",
    "training_protected_attribute_values",
    "training_non_protected_feature_values",
}

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_scalar_token(value: object) -> str:
    """Encode one heterogeneous table scalar without pickle or ambiguity."""

    if isinstance(value, np.generic):
        value = value.item()
    if value is None or (isinstance(value, float) and math.isnan(value)):
        payload = {"kind": "missing"}
    elif isinstance(value, bool):
        payload = {"kind": "bool", "value": value}
    elif isinstance(value, int):
        payload = {"kind": "int", "value": value}
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite table scalars are not supported")
        payload = {"kind": "float", "value": value.hex()}
    elif isinstance(value, str):
        payload = {"kind": "str", "value": value}
    else:
        raise TypeError(f"unsupported table scalar type: {type(value).__name__}")
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate_scalar_token(token: str, dataset_id: str) -> None:
    try:
        payload = json.loads(token)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{dataset_id}: invalid canonical scalar token") from exc
    if not isinstance(payload, dict) or payload.get("kind") not in {
        "missing",
        "bool",
        "int",
        "float",
        "str",
    }:
        raise ValueError(f"{dataset_id}: invalid canonical scalar token")
    kind = payload["kind"]
    if kind == "missing":
        valid = set(payload) == {"kind"}
    else:
        valid = set(payload) == {"kind", "value"}
        value = payload.get("value")
        if kind == "bool":
            valid = valid and isinstance(value, bool)
        elif kind == "int":
            valid = valid and isinstance(value, int) and not isinstance(value, bool)
        elif kind == "float":
            try:
                valid = valid and isinstance(value, str) and math.isfinite(float.fromhex(value))
            except ValueError:
                valid = False
        elif kind == "str":
            valid = valid and isinstance(value, str)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if not valid or canonical != token:
        raise ValueError(f"{dataset_id}: noncanonical scalar token")


def evaluation_alignment_sha256(
    *,
    baseline_probabilities: np.ndarray,
    evaluation_labels: np.ndarray,
    source_row_positions: np.ndarray,
    protected_attribute_values: np.ndarray,
    non_protected_feature_values: np.ndarray,
) -> str:
    """Hash the row-wise alignment of every V2 evaluation array."""

    probabilities = np.asarray(baseline_probabilities)
    labels = np.asarray(evaluation_labels)
    positions = np.asarray(source_row_positions)
    protected = np.asarray(protected_attribute_values)
    features = np.asarray(non_protected_feature_values)
    lengths = {len(probabilities), len(labels), len(positions), len(protected), len(features)}
    if len(lengths) != 1:
        raise ValueError("cannot hash misaligned V2 arrays")
    digest = hashlib.sha256()
    for index in range(len(probabilities)):
        row = {
            "features": features[index].tolist(),
            "label": int(labels[index]),
            "position": int(positions[index]),
            "probability_hex": float(probabilities[index]).hex(),
            "protected": protected[index].tolist(),
        }
        digest.update(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
                "utf-8"
            )
        )
        digest.update(b"\n")
    return digest.hexdigest()


def training_alignment_sha256(
    *,
    training_labels: np.ndarray,
    training_source_row_positions: np.ndarray,
    training_protected_attribute_values: np.ndarray,
    training_non_protected_feature_values: np.ndarray,
) -> str:
    """Hash the row-wise alignment of every V2.1 training array."""

    labels = np.asarray(training_labels)
    positions = np.asarray(training_source_row_positions)
    protected = np.asarray(training_protected_attribute_values)
    features = np.asarray(training_non_protected_feature_values)
    lengths = {len(labels), len(positions), len(protected), len(features)}
    if len(lengths) != 1:
        raise ValueError("cannot hash misaligned V2.1 training arrays")
    digest = hashlib.sha256()
    for index in range(len(labels)):
        row = {
            "features": features[index].tolist(),
            "label": int(labels[index]),
            "position": int(positions[index]),
            "protected": protected[index].tolist(),
        }
        digest.update(
            json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
                "utf-8"
            )
        )
        digest.update(b"\n")
    return digest.hexdigest()


def _require_int(metadata: dict, field: str, dataset_id: str) -> int:
    value = metadata.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{dataset_id}: metadata {field} must be an integer")
    return value


def _load_arrays(npz_path: Path, dataset_id: str) -> dict[str, np.ndarray]:
    try:
        with np.load(npz_path, allow_pickle=False) as stored:
            if set(stored.files) != V2_NPZ_KEYS:
                raise ValueError(f"{dataset_id}: unexpected V2 NPZ schema")
            return {name: np.asarray(stored[name]) for name in stored.files}
    except (OSError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith(f"{dataset_id}:"):
            raise
        raise ValueError(f"{dataset_id}: unreadable V2 NPZ") from exc


def _validate_source_artifacts(
    metadata: dict,
    dataset_id: str,
    source_root: Path | None,
) -> bool:
    artifacts = metadata.get("source_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError(f"{dataset_id}: source_artifacts must be a nonempty list")
    relative_paths: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise TypeError(f"{dataset_id}: invalid source artifact entry")
        relative = artifact.get("relative_path")
        size = artifact.get("bytes")
        digest = artifact.get("sha256")
        if not isinstance(relative, str) or not relative:
            raise ValueError(f"{dataset_id}: invalid source artifact relative path")
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"{dataset_id}: source artifact path must remain relative")
        if relative in relative_paths:
            raise ValueError(f"{dataset_id}: duplicate source artifact path")
        relative_paths.add(relative)
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise ValueError(f"{dataset_id}: invalid source artifact byte count")
        if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
            raise ValueError(f"{dataset_id}: invalid source artifact SHA-256")
        if source_root is not None:
            path = source_root / relative_path
            if not path.is_file():
                raise ValueError(f"{dataset_id}: source artifact is missing: {relative}")
            if path.stat().st_size != size:
                raise ValueError(f"{dataset_id}: source artifact {relative} byte-count mismatch")
            if _file_sha256(path) != digest:
                raise ValueError(f"{dataset_id}: source artifact {relative} SHA-256 mismatch")
    return source_root is not None


def _validate_subject(
    npz_path: Path,
    metadata: dict,
    spec: PublicBenchmarkSpec,
    source_root: Path | None,
) -> dict:
    dataset_id = spec.benchmark_id
    if metadata.get("schema") != V2_SCHEMA:
        raise ValueError(f"{dataset_id}: V2 schema mismatch")
    expected_identity = {
        "dataset_id": dataset_id,
        "dataset_name": spec.name,
        "source_url": spec.source_url,
        "source_doi": spec.doi,
        "protected_attributes": list(spec.protected_attributes),
    }
    for field, expected in expected_identity.items():
        if metadata.get(field) != expected:
            raise ValueError(f"{dataset_id}: metadata {field} mismatch")
    if metadata.get("value_encoding") != V2_VALUE_ENCODING:
        raise ValueError(f"{dataset_id}: value encoding mismatch")
    if metadata.get("row_id_semantics") != "zero-based canonical-loaded row position":
        raise ValueError(f"{dataset_id}: row ID semantics mismatch")
    if metadata.get("protected_missing_policy") != "explicit-category":
        raise ValueError(f"{dataset_id}: protected missingness policy mismatch")
    if metadata.get("counterfactual_semantics") != "observational-context-only":
        raise ValueError(f"{dataset_id}: counterfactual semantics mismatch")
    transform = metadata.get("counterfactual_transform")
    if not isinstance(transform, dict) or transform.get("status") != "not-defined" or not isinstance(
        transform.get("reason"), str
    ):
        raise ValueError(f"{dataset_id}: invalid counterfactual transform declaration")
    if metadata.get("identifiability_scope") != "observed-joint-group-comparisons-only":
        raise ValueError(f"{dataset_id}: identifiability scope mismatch")
    environment = metadata.get("preparation_environment")
    if (
        not isinstance(environment, dict)
        or not isinstance(environment.get("python"), str)
        or not environment["python"]
        or not isinstance(environment.get("platform"), str)
        or not environment["platform"]
        or not isinstance(environment.get("packages"), dict)
        or set(environment["packages"])
        != {"aif360", "numpy", "pandas", "scikit-learn", "ucimlrepo", "xlrd"}
        or any(
            not isinstance(version, str) or not version
            for version in environment["packages"].values()
        )
    ):
        raise ValueError(f"{dataset_id}: incomplete preparation environment")

    protected_columns = metadata.get("protected_columns")
    semantics = metadata.get("protected_semantics")
    if (
        not isinstance(protected_columns, list)
        or len(protected_columns) != len(spec.protected_attributes)
        or any(not isinstance(name, str) or not name for name in protected_columns)
        or len(set(protected_columns)) != len(protected_columns)
    ):
        raise ValueError(f"{dataset_id}: invalid protected column declaration")
    if [name.casefold() for name in protected_columns] != [
        name.casefold() for name in spec.protected_attributes
    ]:
        raise ValueError(f"{dataset_id}: protected column semantics mismatch")
    if not isinstance(semantics, dict) or set(semantics) != set(protected_columns) or any(
        not isinstance(value, str) or not value.strip() for value in semantics.values()
    ):
        raise ValueError(f"{dataset_id}: protected semantics are incomplete")

    feature_columns = metadata.get("non_protected_feature_columns")
    if (
        not isinstance(feature_columns, list)
        or not feature_columns
        or any(not isinstance(name, str) or not name for name in feature_columns)
        or len(set(feature_columns)) != len(feature_columns)
    ):
        raise ValueError(f"{dataset_id}: invalid non-protected feature columns")
    protected_folded = {name.casefold() for name in protected_columns}
    if any(name.casefold() in protected_folded for name in feature_columns):
        raise ValueError(f"{dataset_id}: protected-feature leakage")

    canonical_sha = metadata.get("canonical_loaded_data_sha256")
    source_commit = metadata.get("preparation_source_commit")
    if not isinstance(canonical_sha, str) or not _SHA256_RE.fullmatch(canonical_sha):
        raise ValueError(f"{dataset_id}: invalid canonical loaded-data SHA-256")
    if not isinstance(source_commit, str) or not _GIT_SHA_RE.fullmatch(source_commit):
        raise ValueError(f"{dataset_id}: invalid preparation source commit")
    source_verified = _validate_source_artifacts(metadata, dataset_id, source_root)

    rows_loaded = _require_int(metadata, "rows_loaded", dataset_id)
    train_rows = _require_int(metadata, "train_rows", dataset_id)
    heldout_rows = _require_int(metadata, "heldout_rows", dataset_id)
    contexts = _require_int(metadata, "evaluation_contexts", dataset_id)
    max_contexts = _require_int(metadata, "max_contexts", dataset_id)
    _require_int(metadata, "split_seed", dataset_id)
    min_support = _require_int(metadata, "minimum_joint_group_support", dataset_id)
    if not (0 < train_rows < rows_loaded) or heldout_rows != rows_loaded - train_rows:
        raise ValueError(f"{dataset_id}: inconsistent split row counts")
    if not (0 < contexts <= heldout_rows and contexts <= max_contexts):
        raise ValueError(f"{dataset_id}: inconsistent evaluation context counts")
    if min_support < 1:
        raise ValueError(f"{dataset_id}: minimum joint-group support must be positive")

    arrays = _load_arrays(npz_path, dataset_id)
    probabilities = arrays["baseline_probabilities"]
    labels = arrays["evaluation_labels"]
    positions = arrays["source_row_positions"]
    protected = arrays["protected_attribute_values"]
    features = arrays["non_protected_feature_values"]
    training_labels = arrays["training_labels"]
    training_positions = arrays["training_source_row_positions"]
    training_protected = arrays["training_protected_attribute_values"]
    training_features = arrays["training_non_protected_feature_values"]
    if probabilities.ndim != 1 or len(probabilities) != contexts:
        raise ValueError(f"{dataset_id}: probability shape/count mismatch")
    if not np.issubdtype(probabilities.dtype, np.number) or np.issubdtype(
        probabilities.dtype, np.bool_
    ):
        raise ValueError(f"{dataset_id}: probabilities must be numeric")
    if not np.all(np.isfinite(probabilities)) or np.any(
        (probabilities <= 0.0) | (probabilities >= 1.0)
    ):
        raise ValueError(f"{dataset_id}: probabilities must be finite and interior")
    clip = metadata.get("probability_clip")
    if not isinstance(clip, list) or len(clip) != 2:
        raise ValueError(f"{dataset_id}: invalid probability clip")
    clip_low, clip_high = map(float, clip)
    if not (0.0 < clip_low < clip_high < 1.0) or np.any(
        (probabilities < clip_low) | (probabilities > clip_high)
    ):
        raise ValueError(f"{dataset_id}: probabilities violate clip bounds")
    if labels.shape != (contexts,) or not (
        np.issubdtype(labels.dtype, np.integer) or np.issubdtype(labels.dtype, np.bool_)
    ) or not np.all(np.isin(labels, [0, 1])):
        raise ValueError(f"{dataset_id}: labels must be an aligned binary vector")
    if positions.shape != (contexts,) or not np.issubdtype(positions.dtype, np.integer):
        raise ValueError(f"{dataset_id}: source row positions must be an integer vector")
    if len(set(map(int, positions))) != contexts or np.any((positions < 0) | (positions >= rows_loaded)):
        raise ValueError(f"{dataset_id}: source row positions must be unique and in range")
    if protected.shape != (contexts, len(protected_columns)):
        raise ValueError(f"{dataset_id}: protected matrix shape mismatch")
    if features.shape != (contexts, len(feature_columns)):
        raise ValueError(f"{dataset_id}: non-protected feature matrix shape mismatch")
    if training_labels.shape != (train_rows,) or not (
        np.issubdtype(training_labels.dtype, np.integer)
        or np.issubdtype(training_labels.dtype, np.bool_)
    ) or not np.all(np.isin(training_labels, [0, 1])):
        raise ValueError(f"{dataset_id}: training labels must be an aligned binary vector")
    if training_positions.shape != (train_rows,) or not np.issubdtype(
        training_positions.dtype, np.integer
    ):
        raise ValueError(f"{dataset_id}: training source positions must be an integer vector")
    training_position_set = set(map(int, training_positions))
    if len(training_position_set) != train_rows or np.any(
        (training_positions < 0) | (training_positions >= rows_loaded)
    ):
        raise ValueError(f"{dataset_id}: training source positions must be unique and in range")
    if training_position_set.intersection(map(int, positions)):
        raise ValueError(f"{dataset_id}: training/evaluation source positions overlap")
    if training_protected.shape != (train_rows, len(protected_columns)):
        raise ValueError(f"{dataset_id}: training protected matrix shape mismatch")
    if training_features.shape != (train_rows, len(feature_columns)):
        raise ValueError(f"{dataset_id}: training feature matrix shape mismatch")
    if any(
        array.dtype.kind != "U"
        for array in (protected, features, training_protected, training_features)
    ):
        raise ValueError(f"{dataset_id}: table values must be pickle-free Unicode tokens")
    for token in np.concatenate(
        (
            protected.reshape(-1),
            features.reshape(-1),
            training_protected.reshape(-1),
            training_features.reshape(-1),
        )
    ):
        _validate_scalar_token(str(token), dataset_id)

    all_protected = np.concatenate((training_protected, protected), axis=0)
    expected_catalog = {
        name: sorted(set(all_protected[:, column].tolist()))
        for column, name in enumerate(protected_columns)
    }
    if metadata.get("protected_value_catalog") != expected_catalog:
        raise ValueError(f"{dataset_id}: protected value catalog mismatch")
    evaluation_joint_counts: dict[str, int] = {}
    for row in protected.tolist():
        key = json.dumps(row, separators=(",", ":"))
        evaluation_joint_counts[key] = evaluation_joint_counts.get(key, 0) + 1
    training_joint_counts: dict[str, int] = {}
    for row in training_protected.tolist():
        key = json.dumps(row, separators=(",", ":"))
        training_joint_counts[key] = training_joint_counts.get(key, 0) + 1
    if metadata.get("evaluation_joint_group_counts") != evaluation_joint_counts:
        raise ValueError(f"{dataset_id}: evaluation joint group counts mismatch")
    if metadata.get("training_joint_group_counts") != training_joint_counts:
        raise ValueError(f"{dataset_id}: training joint group counts mismatch")
    supported = sorted(
        key for key, count in training_joint_counts.items() if count >= min_support
    )
    if len(supported) < 2:
        raise ValueError(f"{dataset_id}: fewer than two supported joint groups")
    evaluation_supported = sorted(set(evaluation_joint_counts).intersection(supported))
    if len(evaluation_supported) < 2:
        raise ValueError(f"{dataset_id}: fewer than two evaluation groups have training support")

    expected_alignment = evaluation_alignment_sha256(
        baseline_probabilities=probabilities,
        evaluation_labels=labels,
        source_row_positions=positions,
        protected_attribute_values=protected,
        non_protected_feature_values=features,
    )
    if metadata.get("evaluation_alignment_sha256") != expected_alignment:
        raise ValueError(f"{dataset_id}: evaluation alignment SHA-256 mismatch")
    expected_training_alignment = training_alignment_sha256(
        training_labels=training_labels,
        training_source_row_positions=training_positions,
        training_protected_attribute_values=training_protected,
        training_non_protected_feature_values=training_features,
    )
    if metadata.get("training_alignment_sha256") != expected_training_alignment:
        raise ValueError(f"{dataset_id}: training alignment SHA-256 mismatch")
    accuracy = metadata.get("base_accuracy")
    if isinstance(accuracy, bool) or not isinstance(accuracy, (int, float)) or not (
        math.isfinite(accuracy) and 0.0 <= accuracy <= 1.0
    ):
        raise ValueError(f"{dataset_id}: invalid base accuracy")
    return {
        "dataset_id": dataset_id,
        "multicolumn": len(protected_columns) >= 2,
        "source_bytes_verified": source_verified,
        "supported_joint_groups": supported,
        "evaluation_groups_with_training_support": evaluation_supported,
        "source_commit": source_commit,
    }


def validate_prepared_public_v2_directory(
    prepared_dir: str | Path,
    *,
    expected_source_commit: str | None = None,
    source_root: str | Path | None = None,
) -> dict:
    """Validate the complete, non-overwriting public-context V2 contract."""

    root = Path(prepared_dir)
    if not root.is_dir():
        raise ValueError(f"prepared V2 directory does not exist: {root}")
    if expected_source_commit is not None and not _GIT_SHA_RE.fullmatch(expected_source_commit):
        raise ValueError("expected source commit must be a full lowercase Git SHA")
    resolved_source_root = Path(source_root) if source_root is not None else None
    if resolved_source_root is not None and not resolved_source_root.is_dir():
        raise ValueError(f"source root does not exist: {resolved_source_root}")

    registry = public_benchmark_registry_v1()
    specs = {spec.benchmark_id: spec for spec in registry}
    expected_ids = set(specs)
    npz_ids = {path.stem for path in root.glob("public-*.npz")}
    json_ids = {path.stem for path in root.glob("public-*.json")}
    if npz_ids != expected_ids or json_ids != expected_ids:
        raise ValueError("prepared V2 dataset IDs do not match the frozen registry")

    manifest_path = root / "prepared_v2_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("prepared V2 manifest is missing or invalid") from exc
    if not isinstance(manifest, list):
        raise TypeError("prepared V2 manifest must be a list")
    manifest_by_id = {
        row.get("dataset_id"): row
        for row in manifest
        if isinstance(row, dict) and isinstance(row.get("dataset_id"), str)
    }
    if len(manifest_by_id) != len(manifest) or set(manifest_by_id) != expected_ids:
        raise ValueError("prepared V2 manifest IDs do not match the frozen registry")

    reports = []
    artifact_paths = [manifest_path]
    for dataset_id in sorted(expected_ids):
        metadata_path = root / f"{dataset_id}.json"
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{dataset_id}: metadata is unreadable or invalid") from exc
        if metadata != manifest_by_id[dataset_id]:
            raise ValueError(f"{dataset_id}: metadata does not match V2 manifest")
        reports.append(
            _validate_subject(
                root / f"{dataset_id}.npz",
                metadata,
                specs[dataset_id],
                resolved_source_root,
            )
        )
        artifact_paths.extend([root / f"{dataset_id}.npz", metadata_path])

    source_commits = {report["source_commit"] for report in reports}
    if len(source_commits) != 1:
        raise ValueError("prepared V2 subjects do not share one source commit")
    source_commit = next(iter(source_commits))
    if expected_source_commit is not None and source_commit != expected_source_commit:
        raise ValueError("prepared V2 source commit does not match expectation")
    source_verified = all(report["source_bytes_verified"] for report in reports)
    ready_ids = sorted(
        report["dataset_id"]
        for report in reports
        if report["multicolumn"] and report["source_bytes_verified"]
    )
    return {
        "schema": V2_SCHEMA,
        "dataset_ids": sorted(expected_ids),
        "source_commit": source_commit,
        "source_bytes_verified": source_verified,
        "multicolumn_ready_ids": ready_ids,
        "ready": source_verified and bool(ready_ids),
        "files": [
            {"path": path.name, "bytes": path.stat().st_size, "sha256": _file_sha256(path)}
            for path in sorted(artifact_paths)
        ],
        "subjects": reports,
    }
