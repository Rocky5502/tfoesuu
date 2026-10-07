#!/usr/bin/env python3
"""Prepare public datasets as replayable TFOESUU software-subject inputs.

This script downloads data only when invoked explicitly.  Core CI never calls it.
No pretrained model or external model API is used.  A local logistic predictor
is fitted on non-protected features and its evaluation probabilities become the
old-version Bernoulli thresholds used by the stochastic software wrapper.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

from tfoesuu.public_benchmarks import public_benchmark_registry_v1


PROTECTED_COLUMNS = {
    "public-adult": ("sex", "race"),
    "public-bank": ("age",),
    "public-german": ("sex", "age"),
    "public-compas": ("race", "sex"),
    "public-lawschool": ("race", "gender"),
    "public-meps21": ("RACE",),
    "public-default-credit": ("SEX", "AGE"),
}


def git_state() -> tuple[str, bool]:
    sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain"], text=True
        ).strip()
    )
    return sha, dirty


def _imports():
    try:
        import pandas as pd
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler
    except ImportError as exc:
        raise SystemExit(
            "Install public benchmark dependencies with "
            "`pip install -r requirements-public.txt`."
        ) from exc
    return {
        "pd": pd,
        "ColumnTransformer": ColumnTransformer,
        "SimpleImputer": SimpleImputer,
        "LogisticRegression": LogisticRegression,
        "accuracy_score": accuracy_score,
        "train_test_split": train_test_split,
        "Pipeline": Pipeline,
        "OneHotEncoder": OneHotEncoder,
        "StandardScaler": StandardScaler,
    }


def _load_aif360(dataset_id: str, data_home: Path, accept_meps_terms: bool):
    try:
        from aif360.sklearn.datasets import (
            fetch_adult,
            fetch_bank,
            fetch_compas,
            fetch_german,
            fetch_lawschool_gpa,
            fetch_meps,
        )
    except ImportError as exc:
        raise SystemExit("AIF360 is required for this public dataset.") from exc

    home = str(data_home)
    if dataset_id == "public-adult":
        ds = fetch_adult(
            subset="all", data_home=home, binary_race=True, dropna=True
        )
    elif dataset_id == "public-bank":
        ds = fetch_bank(data_home=home, binary_age=True, dropna=True)
    elif dataset_id == "public-german":
        ds = fetch_german(data_home=home, binary_age=True, dropna=True)
    elif dataset_id == "public-compas":
        ds = fetch_compas(
            subset="all", data_home=home, binary_race=True, dropna=True
        )
    elif dataset_id == "public-lawschool":
        ds = fetch_lawschool_gpa(
            subset="all", data_home=home, binary_race=True, dropna=True
        )
    elif dataset_id == "public-meps21":
        if not accept_meps_terms:
            raise SystemExit(
                "MEPS requires explicit acknowledgement. Re-run with "
                "`--accept-meps-terms` only after reading the AHRQ terms."
            )
        ds = fetch_meps(
            21, accept_terms=True, data_home=home, dropna=True
        )
    else:
        raise ValueError(dataset_id)
    return ds.X.copy(), ds.y.copy()


def _load_default_credit():
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError as exc:
        raise SystemExit("ucimlrepo is required for Default Credit.") from exc
    ds = fetch_ucirepo(id=350)
    return ds.data.features.copy(), ds.data.targets.copy()


def load_dataset(dataset_id: str, data_home: Path, accept_meps_terms: bool):
    if dataset_id == "public-default-credit":
        return _load_default_credit()
    return _load_aif360(dataset_id, data_home, accept_meps_terms)


def _as_series(y, pd):
    if hasattr(y, "columns"):
        if len(y.columns) != 1:
            raise ValueError("expected a single target column")
        return y.iloc[:, 0].reset_index(drop=True)
    return pd.Series(y).reset_index(drop=True)


def binarize_target(dataset_id: str, y, pd):
    s = _as_series(y, pd)
    if dataset_id == "public-lawschool":
        numeric = pd.to_numeric(s, errors="coerce")
        if numeric.isna().any():
            raise ValueError("Law School target must be numeric")
        threshold = float(numeric.median())
        return (numeric >= threshold).astype(int), {
            "target_transform": "zfygpa >= median",
            "target_threshold": threshold,
        }

    values = s.dropna().unique()
    if len(values) != 2:
        raise ValueError(
            f"{dataset_id}: expected binary target, observed {len(values)} levels"
        )
    ordered = sorted(str(v) for v in values)
    mapping = {label: i for i, label in enumerate(ordered)}
    out = s.astype(str).map(mapping)
    if out.isna().any():
        raise ValueError("target encoding produced missing values")
    return out.astype(int), {
        "target_transform": "two-level categorical encoding",
        "target_mapping": mapping,
    }


def canonical_sha256(X, y) -> str:
    h = hashlib.sha256()
    x_bytes = X.reset_index().to_csv(index=False).encode("utf-8")
    y_bytes = y.reset_index(drop=True).to_csv(index=False).encode("utf-8")
    h.update(x_bytes)
    h.update(b"\n--TARGET--\n")
    h.update(y_bytes)
    return h.hexdigest()


def prepare_one(
    dataset_id: str,
    *,
    data_home: Path,
    output_dir: Path,
    seed: int,
    max_contexts: int,
    accept_meps_terms: bool,
    source_commit: str,
) -> dict:
    lib = _imports()
    pd = lib["pd"]
    X, y_raw = load_dataset(dataset_id, data_home, accept_meps_terms)
    X = X.reset_index(drop=True)
    y, target_meta = binarize_target(dataset_id, y_raw, pd)
    if len(X) != len(y):
        raise ValueError("feature/target row count mismatch")

    digest = canonical_sha256(X, y)
    protected = PROTECTED_COLUMNS[dataset_id]
    drop_cols = [c for c in protected if c in X.columns]
    model_X = X.drop(columns=drop_cols, errors="ignore").copy()

    # Remove index-derived protected columns as well when AIF360 stores them
    # in a named MultiIndex that becomes ordinary columns after reset_index.
    lower_protected = {str(c).lower() for c in protected}
    derived_drop = [
        c for c in model_X.columns
        if str(c).lower() in lower_protected
    ]
    model_X = model_X.drop(columns=derived_drop, errors="ignore")

    numeric_cols = list(model_X.select_dtypes(include=["number", "bool"]).columns)
    categorical_cols = [c for c in model_X.columns if c not in numeric_cols]

    numeric_pipe = lib["Pipeline"]([
        ("impute", lib["SimpleImputer"](strategy="median")),
        ("scale", lib["StandardScaler"]()),
    ])
    categorical_pipe = lib["Pipeline"]([
        ("impute", lib["SimpleImputer"](strategy="most_frequent")),
        ("onehot", lib["OneHotEncoder"](handle_unknown="ignore")),
    ])
    pre = lib["ColumnTransformer"]([
        ("numeric", numeric_pipe, numeric_cols),
        ("categorical", categorical_pipe, categorical_cols),
    ])
    model = lib["Pipeline"]([
        ("pre", pre),
        ("clf", lib["LogisticRegression"](max_iter=2000, solver="lbfgs")),
    ])

    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_eval, y_train, y_eval = lib["train_test_split"](
        model_X,
        y,
        test_size=0.25,
        random_state=seed,
        stratify=stratify,
    )
    model.fit(X_train, y_train)
    probabilities = model.predict_proba(X_eval)[:, 1]
    predictions = model.predict(X_eval)
    accuracy = float(lib["accuracy_score"](y_eval, predictions))

    # Keep theorem-aligned additive patches away from probability boundaries.
    probabilities = np.clip(np.asarray(probabilities, dtype=float), 0.10, 0.80)

    if len(probabilities) > max_contexts:
        rng = np.random.default_rng(seed + 1)
        chosen = np.sort(rng.choice(len(probabilities), max_contexts, replace=False))
        probabilities = probabilities[chosen]
        y_eval_np = np.asarray(y_eval, dtype=np.int8)[chosen]
    else:
        y_eval_np = np.asarray(y_eval, dtype=np.int8)

    output_dir.mkdir(parents=True, exist_ok=True)
    npz_path = output_dir / f"{dataset_id}.npz"
    np.savez_compressed(
        npz_path,
        baseline_probabilities=probabilities,
        evaluation_labels=y_eval_np,
    )

    registry = {row.benchmark_id: row for row in public_benchmark_registry_v1()}
    spec = registry[dataset_id]
    metadata = {
        "dataset_id": dataset_id,
        "dataset_name": spec.name,
        "source_url": spec.source_url,
        "source_doi": spec.doi,
        "protected_attributes": list(spec.protected_attributes),
        "canonical_loaded_data_sha256": digest,
        "split_seed": seed,
        "rows_loaded": int(len(X)),
        "train_rows": int(len(X_train)),
        "evaluation_contexts": int(len(probabilities)),
        "max_contexts": int(max_contexts),
        "base_predictor": "scikit-learn LogisticRegression on non-protected features",
        "base_accuracy": accuracy,
        "probability_clip": [0.10, 0.80],
        "preparation_source_commit": source_commit,
        **target_meta,
    }
    meta_path = output_dir / f"{dataset_id}.json"
    meta_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", action="append", help="benchmark ID; repeatable; default=all")
    ap.add_argument("--data-home", type=Path, default=Path("data/public_cache"))
    ap.add_argument("--output-dir", type=Path, default=Path("data/public_prepared"))
    ap.add_argument("--seed", type=int, default=20271008)
    ap.add_argument("--max-contexts", type=int, default=4096)
    ap.add_argument("--accept-meps-terms", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true")
    args = ap.parse_args()

    source_commit, dirty = git_state()
    if dirty and not args.allow_dirty:
        raise SystemExit("working tree is dirty; commit/freeze before preparing public datasets")

    registry = public_benchmark_registry_v1()
    ids = [row.benchmark_id for row in registry]
    selected = args.dataset or ids
    unknown = sorted(set(selected) - set(ids))
    if unknown:
        raise SystemExit(f"unknown public benchmark IDs: {unknown}")

    manifest = []
    for dataset_id in selected:
        print(f"preparing {dataset_id} ...", flush=True)
        manifest.append(
            prepare_one(
                dataset_id,
                data_home=args.data_home,
                output_dir=args.output_dir,
                seed=args.seed,
                max_contexts=args.max_contexts,
                accept_meps_terms=args.accept_meps_terms,
                source_commit=source_commit,
            )
        )

    manifest_path = args.output_dir / "prepared_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {manifest_path}")


if __name__ == "__main__":
    main()