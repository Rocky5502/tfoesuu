#!/usr/bin/env python3
"""Prepare aligned score arrays for public V2 without running Fairlearn."""

from __future__ import annotations

import argparse
import json
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
    from scripts.prepare_public_benchmarks_v2 import (
        _load_default_credit_from_frozen_source,
        load_source_map,
        partition_feature_columns,
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
    from prepare_public_benchmarks_v2 import (  # type: ignore[no-redef]
        _load_default_credit_from_frozen_source,
        load_source_map,
        partition_feature_columns,
    )

from tfoesuu.public_benchmarks import public_benchmark_registry_v1
from tfoesuu.public_benchmarks_v2 import validate_prepared_public_v2_directory
from tfoesuu.public_score_companion_v2 import (
    SCORE_SCHEMA,
    score_alignment_sha256,
    validate_public_score_companion_v2,
)


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fit_scores(model_X, y, train_positions, evaluation_positions, lib):
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
    predictor.fit(model_X.iloc[train_positions], y.iloc[train_positions])
    training_scores = np.clip(
        np.asarray(predictor.predict_proba(model_X.iloc[train_positions])[:, 1], dtype=np.float64),
        0.10,
        0.80,
    )
    evaluation_scores = np.clip(
        np.asarray(
            predictor.predict_proba(model_X.iloc[evaluation_positions])[:, 1],
            dtype=np.float64,
        ),
        0.10,
        0.80,
    )
    return training_scores, evaluation_scores


def prepare_one(
    dataset_id: str,
    *,
    prepared_dir: Path,
    data_home: Path,
    source_root: Path,
    source_paths: list[str],
    output_dir: Path,
    accept_meps_terms: bool,
) -> dict:
    lib = _imports()
    pd = lib["pd"]
    if dataset_id == "public-default-credit":
        X, y_raw = _load_default_credit_from_frozen_source(source_root, source_paths, pd)
    else:
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
    X = X.reset_index(drop=True)
    y, _ = binarize_target(dataset_id, y_raw, pd)

    metadata = json.loads(
        (prepared_dir / f"{dataset_id}.json").read_text(encoding="utf-8")
    )
    if canonical_sha256(X, y) != metadata["canonical_loaded_data_sha256"]:
        raise ValueError(f"{dataset_id}: canonical loaded-data hash mismatch")
    _, feature_columns = partition_feature_columns(
        dataset_id, list(X.columns), configured_protected
    )
    if feature_columns != metadata["non_protected_feature_columns"]:
        raise ValueError(f"{dataset_id}: non-protected feature columns drifted")
    with np.load(prepared_dir / f"{dataset_id}.npz", allow_pickle=False) as prepared:
        train_positions = prepared["training_source_row_positions"]
        evaluation_positions = prepared["source_row_positions"]
        expected_training_labels = prepared["training_labels"]
        expected_evaluation_scores = prepared["baseline_probabilities"]
    if not np.array_equal(np.asarray(y.iloc[train_positions], dtype=np.int8), expected_training_labels):
        raise ValueError(f"{dataset_id}: training labels drifted")

    training_scores, evaluation_scores = _fit_scores(
        X.loc[:, feature_columns], y, train_positions, evaluation_positions, lib
    )
    if not np.array_equal(evaluation_scores, expected_evaluation_scores):
        difference = float(np.max(np.abs(evaluation_scores - expected_evaluation_scores)))
        raise ValueError(
            f"{dataset_id}: fitted evaluation scores do not exactly reproduce V2.1 "
            f"(max_abs={difference})"
        )
    arrays = {
        "training_source_row_positions": np.asarray(train_positions, dtype=np.int64),
        "evaluation_source_row_positions": np.asarray(evaluation_positions, dtype=np.int64),
        "training_scores": training_scores,
        "evaluation_scores": evaluation_scores,
    }
    np.savez_compressed(output_dir / f"{dataset_id}.npz", **arrays)
    score_metadata = {
        "schema": SCORE_SCHEMA,
        "dataset_id": dataset_id,
        "prepared_training_alignment_sha256": metadata["training_alignment_sha256"],
        "prepared_evaluation_alignment_sha256": metadata["evaluation_alignment_sha256"],
        "model_contract": "V2.1 logistic regression, clipped to [0.1,0.8]",
        "score_alignment_sha256": score_alignment_sha256(**arrays),
    }
    (output_dir / f"{dataset_id}.json").write_text(
        json.dumps(score_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return score_metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--data-home", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-map", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--accept-meps-terms", action="store_true")
    args = parser.parse_args()

    source_commit, dirty = git_state()
    if dirty:
        raise SystemExit("working tree is dirty; commit before preparing score companion")
    if args.output_dir.exists():
        raise SystemExit(f"refusing to overwrite existing output path: {args.output_dir}")
    validate_prepared_public_v2_directory(args.prepared_dir, source_root=args.source_root)
    dataset_ids = [spec.benchmark_id for spec in public_benchmark_registry_v1()]
    source_map = load_source_map(args.source_map, dataset_ids)

    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{args.output_dir.name}.staging-", dir=args.output_dir.parent
        )
    )
    datasets = [
        prepare_one(
            dataset_id,
            prepared_dir=args.prepared_dir,
            data_home=args.data_home,
            source_root=args.source_root,
            source_paths=source_map[dataset_id],
            output_dir=staging,
            accept_meps_terms=args.accept_meps_terms,
        )
        for dataset_id in dataset_ids
    ]
    manifest = {
        "schema": SCORE_SCHEMA,
        "prepared_manifest_sha256": _sha256(args.prepared_dir / "prepared_v2_manifest.json"),
        "preparation_source_commit": source_commit,
        "datasets": datasets,
    }
    (staging / "score_companion_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    validate_public_score_companion_v2(staging, args.prepared_dir)
    staging.rename(args.output_dir)
    print(f"wrote validated score companion {args.output_dir}")


if __name__ == "__main__":
    main()
