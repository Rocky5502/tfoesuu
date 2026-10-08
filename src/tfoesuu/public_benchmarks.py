from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PREPARATION_CONTRACT_PATHS = (
    "scripts/prepare_public_benchmarks.py",
    "data/public_benchmark_registry_v1.jsonl",
    "requirements-public.txt",
)


@dataclass(frozen=True)
class PublicBenchmarkSpec:
    """Metadata contract for one planned public fairness-regression subject.

    These entries identify public input populations.  They do not encode
    empirical TFOESUU results.  The old/new executable software versions,
    stochastic patch, seeds, and train/evaluation split are generated locally.
    """

    benchmark_id: str
    name: str
    task: str
    protected_attributes: tuple[str, ...]
    source: str
    source_url: str
    doi: str | None
    loader_family: str
    status: str


def public_benchmark_registry_v1() -> list[PublicBenchmarkSpec]:
    """Frozen v1 registry for the submission-facing public benchmark layer."""
    return [
        PublicBenchmarkSpec(
            benchmark_id="public-adult",
            name="Adult Census Income",
            task="binary-classification",
            protected_attributes=("sex", "race"),
            source="UCI Machine Learning Repository",
            source_url="https://archive.ics.uci.edu/dataset/2/adult",
            doi="10.24432/C5XW20",
            loader_family="aif360",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-bank",
            name="Bank Marketing",
            task="binary-classification",
            protected_attributes=("age",),
            source="UCI Machine Learning Repository",
            source_url="https://archive.ics.uci.edu/dataset/222/bank+marketing",
            doi="10.24432/C5K306",
            loader_family="aif360",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-german",
            name="Statlog German Credit",
            task="binary-classification",
            protected_attributes=("sex", "age"),
            source="UCI Machine Learning Repository",
            source_url="https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data",
            doi="10.24432/C5NC77",
            loader_family="aif360",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-compas",
            name="ProPublica COMPAS",
            task="binary-classification",
            protected_attributes=("race", "sex"),
            source="ProPublica compas-analysis",
            source_url="https://github.com/propublica/compas-analysis",
            doi=None,
            loader_family="aif360",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-lawschool",
            name="Law School GPA",
            task="regression-to-thresholded-decision",
            protected_attributes=("race", "gender"),
            source="AIF360 LawSchoolGPADataset",
            source_url="https://aif360.readthedocs.io/en/latest/modules/generated/aif360.datasets.LawSchoolGPADataset.html",
            doi=None,
            loader_family="aif360",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-meps21",
            name="MEPS Panel 21",
            task="binary-classification",
            protected_attributes=("race",),
            source="AIF360 / AHRQ MEPS",
            source_url="https://aif360.readthedocs.io/en/latest/modules/generated/aif360.sklearn.datasets.fetch_meps.html",
            doi=None,
            loader_family="aif360",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-default-credit",
            name="Default of Credit Card Clients",
            task="binary-classification",
            protected_attributes=("sex", "age"),
            source="UCI Machine Learning Repository",
            source_url="https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients",
            doi="10.24432/C55S3H",
            loader_family="uci",
            status="planned",
        ),
    ]


def write_public_benchmark_registry(
    rows: Iterable[PublicBenchmarkSpec],
    path: str | Path,
) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            payload = asdict(row)
            payload["protected_attributes"] = list(row.protected_attributes)
            fh.write(json.dumps(payload, sort_keys=True) + "\n")


def read_public_benchmark_registry(
    path: str | Path,
) -> list[PublicBenchmarkSpec]:
    rows: list[PublicBenchmarkSpec] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            payload = json.loads(line)
            payload["protected_attributes"] = tuple(payload["protected_attributes"])
            rows.append(PublicBenchmarkSpec(**payload))
    return rows


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_int(metadata: dict, field: str, dataset_id: str) -> int:
    value = metadata.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{dataset_id}: metadata {field} must be an integer")
    return value


def _validate_prepared_subject(
    npz_path: Path,
    metadata: dict,
    spec: PublicBenchmarkSpec,
) -> None:
    dataset_id = spec.benchmark_id
    if metadata.get("dataset_id") != dataset_id:
        raise ValueError(f"{dataset_id}: metadata dataset_id mismatch")
    if metadata.get("dataset_name") != spec.name:
        raise ValueError(f"{dataset_id}: metadata dataset_name mismatch")
    if metadata.get("source_url") != spec.source_url:
        raise ValueError(f"{dataset_id}: metadata source_url mismatch")
    if metadata.get("source_doi") != spec.doi:
        raise ValueError(f"{dataset_id}: metadata source_doi mismatch")
    if metadata.get("protected_attributes") != list(spec.protected_attributes):
        raise ValueError(f"{dataset_id}: protected attributes mismatch")

    canonical_sha = metadata.get("canonical_loaded_data_sha256")
    if not isinstance(canonical_sha, str) or not _SHA256_RE.fullmatch(canonical_sha):
        raise ValueError(f"{dataset_id}: invalid canonical loaded-data SHA-256")
    source_commit = metadata.get("preparation_source_commit")
    if not isinstance(source_commit, str) or not _GIT_SHA_RE.fullmatch(source_commit):
        raise ValueError(f"{dataset_id}: invalid preparation source commit")

    rows_loaded = _require_int(metadata, "rows_loaded", dataset_id)
    train_rows = _require_int(metadata, "train_rows", dataset_id)
    evaluation_contexts = _require_int(metadata, "evaluation_contexts", dataset_id)
    max_contexts = _require_int(metadata, "max_contexts", dataset_id)
    _require_int(metadata, "split_seed", dataset_id)
    if not (0 < train_rows < rows_loaded):
        raise ValueError(f"{dataset_id}: inconsistent loaded/train row counts")
    if not (0 < evaluation_contexts <= max_contexts):
        raise ValueError(f"{dataset_id}: inconsistent evaluation/max context counts")
    if evaluation_contexts > rows_loaded - train_rows:
        raise ValueError(f"{dataset_id}: evaluation contexts exceed held-out rows")

    accuracy = metadata.get("base_accuracy")
    if (
        isinstance(accuracy, bool)
        or not isinstance(accuracy, (int, float))
        or not np.isfinite(accuracy)
        or not 0.0 <= float(accuracy) <= 1.0
    ):
        raise ValueError(f"{dataset_id}: base_accuracy must be finite and in [0,1]")

    clip = metadata.get("probability_clip")
    if (
        not isinstance(clip, list)
        or len(clip) != 2
        or any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in clip)
    ):
        raise ValueError(f"{dataset_id}: probability_clip must contain two numbers")
    clip_low, clip_high = (float(value) for value in clip)
    if not (0.0 < clip_low < clip_high < 1.0):
        raise ValueError(f"{dataset_id}: probability_clip must be interior and ordered")

    try:
        with np.load(npz_path, allow_pickle=False) as arrays:
            if set(arrays.files) != {"baseline_probabilities", "evaluation_labels"}:
                raise ValueError(f"{dataset_id}: unexpected prepared NPZ schema")
            probabilities = np.asarray(arrays["baseline_probabilities"])
            labels = np.asarray(arrays["evaluation_labels"])
    except (OSError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith(f"{dataset_id}:"):
            raise
        raise ValueError(f"{dataset_id}: unreadable prepared NPZ") from exc

    if probabilities.ndim != 1 or len(probabilities) != evaluation_contexts:
        raise ValueError(f"{dataset_id}: probability shape/count mismatch")
    if not np.issubdtype(probabilities.dtype, np.number) or np.issubdtype(
        probabilities.dtype, np.bool_
    ):
        raise ValueError(f"{dataset_id}: probabilities must be numeric")
    if not np.all(np.isfinite(probabilities)) or np.any(
        (probabilities <= 0.0) | (probabilities >= 1.0)
    ):
        raise ValueError(f"{dataset_id}: expected finite interior probabilities")
    if np.any((probabilities < clip_low) | (probabilities > clip_high)):
        raise ValueError(f"{dataset_id}: probabilities violate declared clip bounds")

    if labels.ndim != 1 or len(labels) != len(probabilities):
        raise ValueError(f"{dataset_id}: label length/shape mismatch")
    if not (
        np.issubdtype(labels.dtype, np.integer)
        or np.issubdtype(labels.dtype, np.bool_)
    ):
        raise ValueError(f"{dataset_id}: labels must use an integer or boolean dtype")
    if not np.all(np.isin(labels, [0, 1])):
        raise ValueError(f"{dataset_id}: evaluation labels must be binary")


def validate_prepared_public_directory(
    prepared_dir: str | Path,
    *,
    expected_source_commit: str | None = None,
) -> dict:
    """Strictly validate the complete frozen public-subject directory.

    Validation is read-only. The returned byte hashes identify the artifacts
    that were inspected; ``canonical_loaded_data_sha256`` remains the distinct
    digest of the loader's canonical feature/target population.
    """

    root = Path(prepared_dir)
    if not root.is_dir():
        raise ValueError(f"prepared directory does not exist: {root}")
    if expected_source_commit is not None and not _GIT_SHA_RE.fullmatch(
        expected_source_commit
    ):
        raise ValueError("expected source commit must be a 40-character lowercase Git SHA")

    registry = public_benchmark_registry_v1()
    specs = {spec.benchmark_id: spec for spec in registry}
    if len(specs) != len(registry):
        raise ValueError("public benchmark registry contains duplicate IDs")
    expected_ids = set(specs)
    npz_ids = {path.stem for path in root.glob("public-*.npz")}
    json_ids = {path.stem for path in root.glob("public-*.json")}
    if npz_ids != expected_ids:
        raise ValueError(
            f"prepared NPZ IDs do not match registry: expected {sorted(expected_ids)}, "
            f"observed {sorted(npz_ids)}"
        )
    if json_ids != expected_ids:
        raise ValueError(
            f"prepared metadata IDs do not match registry: expected {sorted(expected_ids)}, "
            f"observed {sorted(json_ids)}"
        )

    manifest_path = root / "prepared_manifest.json"
    if not manifest_path.is_file() or manifest_path.stat().st_size == 0:
        raise ValueError("prepared manifest is missing or empty")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("prepared manifest is unreadable or invalid JSON") from exc
    if not isinstance(manifest, list):
        raise TypeError("prepared manifest must be a JSON list")
    manifest_by_id: dict[str, dict] = {}
    for row in manifest:
        if not isinstance(row, dict) or not isinstance(row.get("dataset_id"), str):
            raise TypeError("prepared manifest rows must be metadata objects with dataset_id")
        dataset_id = row["dataset_id"]
        if dataset_id in manifest_by_id:
            raise ValueError(f"prepared manifest has duplicate dataset ID: {dataset_id}")
        manifest_by_id[dataset_id] = row
    if set(manifest_by_id) != expected_ids:
        raise ValueError("prepared manifest IDs do not match the frozen registry")

    source_commits: set[str] = set()
    artifact_paths = [manifest_path]
    for dataset_id in sorted(expected_ids):
        npz_path = root / f"{dataset_id}.npz"
        metadata_path = root / f"{dataset_id}.json"
        if npz_path.stat().st_size == 0 or metadata_path.stat().st_size == 0:
            raise ValueError(f"{dataset_id}: prepared artifact is empty")
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{dataset_id}: metadata is unreadable or invalid JSON") from exc
        if not isinstance(metadata, dict):
            raise TypeError(f"{dataset_id}: metadata must be a JSON object")
        if metadata != manifest_by_id[dataset_id]:
            raise ValueError(f"{dataset_id}: metadata does not match manifest")
        _validate_prepared_subject(npz_path, metadata, specs[dataset_id])
        source_commits.add(metadata["preparation_source_commit"])
        artifact_paths.extend([metadata_path, npz_path])

    if len(source_commits) != 1:
        raise ValueError("prepared subjects do not share one source commit")
    source_commit = next(iter(source_commits))
    if expected_source_commit is not None and source_commit != expected_source_commit:
        raise ValueError(
            f"prepared source commit {source_commit} does not match expected source commit "
            f"{expected_source_commit}"
        )

    files = [
        {
            "path": path.name,
            "bytes": path.stat().st_size,
            "sha256": _file_sha256(path),
        }
        for path in sorted(artifact_paths, key=lambda item: item.name)
    ]
    return {
        "prepared_dir": str(root.resolve()),
        "dataset_ids": sorted(expected_ids),
        "source_commit": source_commit,
        "files": files,
    }


def validate_preparation_source_compatibility(
    preparation_source_commit: str,
    execution_source_commit: str,
    *,
    repo: str | Path = ".",
    contract_paths: tuple[str, ...] = PREPARATION_CONTRACT_PATHS,
) -> dict:
    """Prove that preparation-defining Git objects match at two commits.

    This is intentionally narrower than whole-commit equality. It permits
    validation, reporting, or experiment-runner changes while failing closed
    if the preparation script, frozen registry, or public dependency contract
    changed. The returned digest versions the exact set of Git blobs checked.
    """

    if not _GIT_SHA_RE.fullmatch(preparation_source_commit):
        raise ValueError("preparation source commit must be a full lowercase Git SHA")
    if not _GIT_SHA_RE.fullmatch(execution_source_commit):
        raise ValueError("execution source commit must be a full lowercase Git SHA")
    if not contract_paths or any(not path for path in contract_paths):
        raise ValueError("preparation contract paths must be nonempty")
    if len(set(contract_paths)) != len(contract_paths):
        raise ValueError("preparation contract paths must be unique")

    root = Path(repo).resolve()

    def git(*args: str) -> str:
        try:
            return subprocess.check_output(
                ["git", *args],
                cwd=root,
                text=True,
                stderr=subprocess.STDOUT,
                timeout=15,
            ).strip()
        except (OSError, subprocess.SubprocessError) as exc:
            raise ValueError(f"unable to inspect preparation contract: {' '.join(args)}") from exc

    resolved_preparation = git("rev-parse", f"{preparation_source_commit}^{{commit}}")
    resolved_execution = git("rev-parse", f"{execution_source_commit}^{{commit}}")
    if resolved_preparation != preparation_source_commit:
        raise ValueError("preparation source commit did not resolve exactly")
    if resolved_execution != execution_source_commit:
        raise ValueError("execution source commit did not resolve exactly")

    preparation_blobs = {
        path: git("rev-parse", f"{preparation_source_commit}:{path}")
        for path in contract_paths
    }
    execution_blobs = {
        path: git("rev-parse", f"{execution_source_commit}:{path}")
        for path in contract_paths
    }
    mismatches = [
        path
        for path in contract_paths
        if preparation_blobs[path] != execution_blobs[path]
    ]
    if mismatches:
        raise ValueError(
            "preparation contract mismatch in: " + ", ".join(mismatches)
        )

    contract_payload = {
        "schema": "tfoesuu-public-preparation-compatibility-v1",
        "git_blobs": preparation_blobs,
    }
    canonical = json.dumps(contract_payload, sort_keys=True, separators=(",", ":"))
    return {
        **contract_payload,
        "compatible": True,
        "preparation_source_commit": preparation_source_commit,
        "execution_source_commit": execution_source_commit,
        "contract_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    }
