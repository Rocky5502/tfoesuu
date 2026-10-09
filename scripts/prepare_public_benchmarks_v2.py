#!/usr/bin/env python3
"""Prepare non-overwriting public-context V2 artifacts.

Unlike public V1, this contract preserves row alignment, protected values, and
raw non-protected evaluation features. It performs no fairness outcome test.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import sys
import tempfile
from pathlib import Path

import numpy as np

try:
    from scripts.prepare_public_benchmarks import (
        PROTECTED_COLUMNS,
        _imports,
        binarize_target,
        canonical_sha256,
        git_state,
        load_dataset,
    )
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    from prepare_public_benchmarks import (  # type: ignore[no-redef]
        PROTECTED_COLUMNS,
        _imports,
        binarize_target,
        canonical_sha256,
        git_state,
        load_dataset,
    )

from tfoesuu.public_benchmarks import public_benchmark_registry_v1
from tfoesuu.public_benchmarks_v2 import (
    V2_SCHEMA,
    V2_VALUE_ENCODING,
    canonical_scalar_token,
    evaluation_alignment_sha256,
    validate_prepared_public_v2_directory,
)

_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")


def _preparation_environment() -> dict:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("aif360", "numpy", "pandas", "scikit-learn", "ucimlrepo")
        },
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_safe_relative_path(value: str) -> bool:
    path = Path(value)
    return bool(value) and not (
        path.is_absolute()
        or _WINDOWS_ABSOLUTE_RE.match(value)
        or ".." in path.parts
        or value.startswith(("/", "\\"))
    )


def load_source_map(path: str | Path, selected_ids: list[str]) -> dict[str, list[str]]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("source map is unreadable or invalid JSON") from exc
    if not isinstance(payload, dict):
        raise TypeError("source map must be a JSON object")
    missing = sorted(set(selected_ids) - set(payload))
    if missing:
        raise ValueError(f"source map is missing selected dataset IDs: {missing}")
    result: dict[str, list[str]] = {}
    for dataset_id in selected_ids:
        entries = payload[dataset_id]
        if (
            not isinstance(entries, list)
            or not entries
            or any(not isinstance(value, str) or not _is_safe_relative_path(value) for value in entries)
            or len(set(entries)) != len(entries)
        ):
            raise ValueError(f"{dataset_id}: every source path must be a unique relative source path")
        result[dataset_id] = entries
    return result


def partition_feature_columns(
    dataset_id: str,
    columns: list[object],
    protected_columns: tuple[str, ...],
) -> tuple[list[str], list[str]]:
    names = [str(column) for column in columns]
    folded = [name.casefold() for name in names]
    if len(set(folded)) != len(folded):
        raise ValueError(f"{dataset_id}: case-insensitive duplicate columns are ambiguous")
    by_folded = dict(zip(folded, names, strict=True))
    missing = [name for name in protected_columns if name.casefold() not in by_folded]
    if missing:
        raise ValueError(f"{dataset_id}: missing declared protected columns: {missing}")
    resolved = [by_folded[name.casefold()] for name in protected_columns]
    protected_folded = {name.casefold() for name in resolved}
    features = [name for name in names if name.casefold() not in protected_folded]
    if not features:
        raise ValueError(f"{dataset_id}: no non-protected predictor columns remain")
    return resolved, features


def _encode_frame(frame, pd) -> np.ndarray:
    rows = []
    for row in frame.itertuples(index=False, name=None):
        encoded = []
        for value in row:
            try:
                missing = bool(pd.isna(value))
            except (TypeError, ValueError):
                missing = False
            encoded.append(canonical_scalar_token(None if missing else value))
        rows.append(encoded)
    return np.asarray(rows, dtype=np.str_)


def _source_artifacts(source_root: Path, relative_paths: list[str]) -> list[dict]:
    artifacts = []
    for relative in relative_paths:
        path = source_root / relative
        if not path.is_file() or path.stat().st_size <= 0:
            raise ValueError(f"source artifact is missing or empty: {relative}")
        artifacts.append(
            {
                "relative_path": relative,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return artifacts


def prepare_one_v2(
    dataset_id: str,
    *,
    data_home: Path,
    source_root: Path,
    source_paths: list[str],
    output_dir: Path,
    seed: int,
    max_contexts: int,
    minimum_joint_group_support: int,
    accept_meps_terms: bool,
    source_commit: str,
) -> dict:
    lib = _imports()
    pd = lib["pd"]
    X, y_raw = load_dataset(dataset_id, data_home, accept_meps_terms)
    configured_protected = PROTECTED_COLUMNS[dataset_id]
    loaded_by_folded = {str(column).casefold(): column for column in X.columns}
    index_by_folded = {
        str(name).casefold(): name for name in X.index.names if name is not None
    }
    X = X.copy()
    for protected_name in configured_protected:
        folded = protected_name.casefold()
        if folded not in loaded_by_folded and folded in index_by_folded:
            X[protected_name] = X.index.get_level_values(index_by_folded[folded]).to_numpy()
    # Source row positions refer to this deterministic loader order. Index
    # values are never added as predictors; protected index levels are copied
    # above only when their corresponding columns are absent.
    X = X.reset_index(drop=True)
    y, target_meta = binarize_target(dataset_id, y_raw, pd)
    if len(X) != len(y):
        raise ValueError(f"{dataset_id}: feature/target row count mismatch")
    if len(X.columns) != len(set(map(str, X.columns))):
        raise ValueError(f"{dataset_id}: duplicate loaded column names")

    registry = {row.benchmark_id: row for row in public_benchmark_registry_v1()}
    spec = registry[dataset_id]
    protected_columns, feature_columns = partition_feature_columns(
        dataset_id,
        list(X.columns),
        configured_protected,
    )
    if [name.casefold() for name in protected_columns] != [
        name.casefold() for name in spec.protected_attributes
    ]:
        raise ValueError(f"{dataset_id}: loaded protected columns do not match registry semantics")

    model_X = X.loc[:, feature_columns].copy()
    numeric_columns = list(model_X.select_dtypes(include=["number", "bool"]).columns)
    categorical_columns = [column for column in model_X.columns if column not in numeric_columns]
    numeric_pipeline = lib["Pipeline"](
        [
            ("impute", lib["SimpleImputer"](strategy="median")),
            ("scale", lib["StandardScaler"]()),
        ]
    )
    categorical_pipeline = lib["Pipeline"](
        [
            ("impute", lib["SimpleImputer"](strategy="most_frequent")),
            ("onehot", lib["OneHotEncoder"](handle_unknown="ignore")),
        ]
    )
    predictor = lib["Pipeline"](
        [
            (
                "pre",
                lib["ColumnTransformer"](
                    [
                        ("numeric", numeric_pipeline, numeric_columns),
                        ("categorical", categorical_pipeline, categorical_columns),
                    ]
                ),
            ),
            ("clf", lib["LogisticRegression"](max_iter=2000, solver="lbfgs")),
        ]
    )

    positions = np.arange(len(X), dtype=np.int64)
    stratify = y if y.value_counts().min() >= 2 else None
    train_positions, heldout_positions = lib["train_test_split"](
        positions,
        test_size=0.25,
        random_state=seed,
        stratify=stratify,
    )
    predictor.fit(model_X.iloc[train_positions], y.iloc[train_positions])
    heldout_features = model_X.iloc[heldout_positions]
    probabilities = np.clip(
        np.asarray(predictor.predict_proba(heldout_features)[:, 1], dtype=np.float64),
        0.10,
        0.80,
    )
    predictions = predictor.predict(heldout_features)
    heldout_labels = np.asarray(y.iloc[heldout_positions], dtype=np.int8)
    accuracy = float(lib["accuracy_score"](heldout_labels, predictions))

    if len(heldout_positions) > max_contexts:
        rng = np.random.default_rng(seed + 1)
        chosen = np.sort(rng.choice(len(heldout_positions), max_contexts, replace=False))
    else:
        chosen = np.arange(len(heldout_positions))
    evaluation_positions = np.asarray(heldout_positions[chosen], dtype=np.int64)
    probabilities = probabilities[chosen]
    labels = heldout_labels[chosen]
    protected_values = _encode_frame(X.iloc[evaluation_positions][protected_columns], pd)
    feature_values = _encode_frame(X.iloc[evaluation_positions][feature_columns], pd)
    arrays = {
        "baseline_probabilities": probabilities,
        "evaluation_labels": labels,
        "source_row_positions": evaluation_positions,
        "protected_attribute_values": protected_values,
        "non_protected_feature_values": feature_values,
    }

    catalog = {
        name: sorted(set(protected_values[:, column].tolist()))
        for column, name in enumerate(protected_columns)
    }
    joint_counts: dict[str, int] = {}
    for row in protected_values.tolist():
        key = json.dumps(row, separators=(",", ":"))
        joint_counts[key] = joint_counts.get(key, 0) + 1
    supported = [count for count in joint_counts.values() if count >= minimum_joint_group_support]
    if len(supported) < 2:
        raise ValueError(
            f"{dataset_id}: fewer than two joint groups meet minimum support "
            f"{minimum_joint_group_support}"
        )

    np.savez_compressed(output_dir / f"{dataset_id}.npz", **arrays)
    metadata = {
        "schema": V2_SCHEMA,
        "dataset_id": dataset_id,
        "dataset_name": spec.name,
        "source_url": spec.source_url,
        "source_doi": spec.doi,
        "protected_attributes": list(spec.protected_attributes),
        "protected_columns": protected_columns,
        "protected_semantics": {
            column: (
                f"source-defined {semantic} field preserved without reinterpretation "
                f"from loaded column {column}"
            )
            for column, semantic in zip(protected_columns, spec.protected_attributes, strict=True)
        },
        "non_protected_feature_columns": list(map(str, feature_columns)),
        "canonical_loaded_data_sha256": canonical_sha256(X, y),
        "source_artifacts": _source_artifacts(source_root, source_paths),
        "split_seed": seed,
        "rows_loaded": len(X),
        "train_rows": len(train_positions),
        "heldout_rows": len(heldout_positions),
        "evaluation_contexts": len(evaluation_positions),
        "max_contexts": int(max_contexts),
        "base_predictor": "scikit-learn LogisticRegression on non-protected features",
        "base_accuracy": accuracy,
        "probability_clip": [0.10, 0.80],
        "preparation_source_commit": source_commit,
        "preparation_environment": _preparation_environment(),
        "row_id_semantics": "zero-based canonical-loaded row position",
        "value_encoding": V2_VALUE_ENCODING,
        "protected_missing_policy": "explicit-category",
        "counterfactual_semantics": "observational-context-only",
        "counterfactual_transform": {
            "status": "not-defined",
            "reason": "no causal intervention is identified by this artifact",
        },
        "identifiability_scope": "observed-joint-group-comparisons-only",
        "minimum_joint_group_support": int(minimum_joint_group_support),
        "protected_value_catalog": catalog,
        "joint_group_counts": joint_counts,
        "evaluation_alignment_sha256": evaluation_alignment_sha256(**arrays),
        **target_meta,
    }
    (output_dir / f"{dataset_id}.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", action="append", help="benchmark ID; repeatable; default=all")
    parser.add_argument("--data-home", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-map", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20271008)
    parser.add_argument("--max-contexts", type=int, default=4096)
    parser.add_argument("--minimum-joint-group-support", type=int, default=2)
    parser.add_argument("--accept-meps-terms", action="store_true")
    args = parser.parse_args()

    source_commit, dirty = git_state()
    if dirty:
        raise SystemExit("working tree is dirty; commit before preparing V2")
    if args.output_dir.exists():
        raise SystemExit(f"refusing to overwrite existing output path: {args.output_dir}")
    if not args.source_root.is_dir():
        raise SystemExit(f"source root does not exist: {args.source_root}")
    registry = public_benchmark_registry_v1()
    registered_ids = [row.benchmark_id for row in registry]
    selected_ids = args.dataset or registered_ids
    unknown = sorted(set(selected_ids) - set(registered_ids))
    if unknown:
        raise SystemExit(f"unknown public benchmark IDs: {unknown}")
    if selected_ids != registered_ids:
        raise SystemExit("V2 release preparation requires the complete frozen seven-dataset registry")
    source_map = load_source_map(args.source_map, selected_ids)

    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{args.output_dir.name}.staging-",
            dir=args.output_dir.parent,
        )
    )
    manifest = []
    for dataset_id in selected_ids:
        print(f"preparing V2 {dataset_id} ...", flush=True)
        manifest.append(
            prepare_one_v2(
                dataset_id,
                data_home=args.data_home,
                source_root=args.source_root,
                source_paths=source_map[dataset_id],
                output_dir=staging,
                seed=args.seed,
                max_contexts=args.max_contexts,
                minimum_joint_group_support=args.minimum_joint_group_support,
                accept_meps_terms=args.accept_meps_terms,
                source_commit=source_commit,
            )
        )
    (staging / "prepared_v2_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    validate_prepared_public_v2_directory(
        staging,
        expected_source_commit=source_commit,
        source_root=args.source_root,
    )
    staging.rename(args.output_dir)
    print(f"wrote validated V2 directory {args.output_dir}")


if __name__ == "__main__":
    main()
