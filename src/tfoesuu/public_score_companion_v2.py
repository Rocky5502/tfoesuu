from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np

from .public_benchmarks import public_benchmark_registry_v1

SCORE_SCHEMA = "tfoesuu-public-score-companion-v2.2"
SCORE_NPZ_KEYS = {
    "training_source_row_positions",
    "evaluation_source_row_positions",
    "training_scores",
    "evaluation_scores",
}
_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def score_alignment_sha256(
    *,
    training_source_row_positions: np.ndarray,
    evaluation_source_row_positions: np.ndarray,
    training_scores: np.ndarray,
    evaluation_scores: np.ndarray,
) -> str:
    """Hash the exact row/score alignment with normalized numeric dtypes."""

    train_positions = np.asarray(training_source_row_positions)
    eval_positions = np.asarray(evaluation_source_row_positions)
    train_scores = np.asarray(training_scores)
    eval_scores = np.asarray(evaluation_scores)
    if train_positions.ndim != 1 or train_scores.shape != train_positions.shape:
        raise ValueError("training score alignment is malformed")
    if eval_positions.ndim != 1 or eval_scores.shape != eval_positions.shape:
        raise ValueError("evaluation score alignment is malformed")
    digest = hashlib.sha256()
    for name, array in (
        ("training_positions", train_positions.astype("<i8", copy=False)),
        ("training_scores", train_scores.astype("<f8", copy=False)),
        ("evaluation_positions", eval_positions.astype("<i8", copy=False)),
        ("evaluation_scores", eval_scores.astype("<f8", copy=False)),
    ):
        digest.update(name.encode("ascii") + b"\0")
        digest.update(np.asarray(array.shape, dtype="<i8").tobytes())
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _load_npz(path: Path, dataset_id: str, expected_keys: set[str]) -> dict[str, np.ndarray]:
    try:
        with np.load(path, allow_pickle=False) as stored:
            if set(stored.files) != expected_keys:
                raise ValueError(f"{dataset_id}: artifact keys mismatch")
            return {name: stored[name] for name in stored.files}
    except (OSError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith(dataset_id):
            raise
        raise ValueError(f"{dataset_id}: artifact is unreadable") from exc


def validate_public_score_companion_v2(
    companion_dir: str | Path,
    prepared_v2_dir: str | Path,
) -> dict:
    """Validate a score-only companion without treating it as outcome evidence."""

    root = Path(companion_dir)
    prepared = Path(prepared_v2_dir)
    if not root.is_dir() or not prepared.is_dir():
        raise ValueError("score companion and prepared V2 directories must exist")
    expected_ids = {spec.benchmark_id for spec in public_benchmark_registry_v1()}
    if {path.stem for path in root.glob("public-*.npz")} != expected_ids or {
        path.stem for path in root.glob("public-*.json")
    } != expected_ids:
        raise ValueError("score companion must contain exactly seven registered datasets")

    manifest_path = root / "score_companion_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("score companion manifest is missing or invalid") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != SCORE_SCHEMA:
        raise ValueError("score companion manifest schema mismatch")
    prepared_digest = manifest.get("prepared_manifest_sha256")
    if not isinstance(prepared_digest, str) or not _SHA256_RE.fullmatch(prepared_digest):
        raise ValueError("score companion has invalid prepared manifest SHA-256")
    if _file_sha256(prepared / "prepared_v2_manifest.json") != prepared_digest:
        raise ValueError("prepared manifest SHA-256 mismatch")
    source_commit = manifest.get("preparation_source_commit")
    if not isinstance(source_commit, str) or not _GIT_SHA_RE.fullmatch(source_commit):
        raise ValueError("score companion requires a full preparation source commit")
    rows = manifest.get("datasets")
    if not isinstance(rows, list):
        raise TypeError("score companion datasets must be a list")
    by_id = {
        row.get("dataset_id"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("dataset_id"), str)
    }
    if len(by_id) != len(rows) or set(by_id) != expected_ids:
        raise ValueError("score companion manifest dataset IDs mismatch")

    for dataset_id in sorted(expected_ids):
        try:
            metadata = json.loads(
                (root / f"{dataset_id}.json").read_text(encoding="utf-8")
            )
            prepared_metadata = json.loads(
                (prepared / f"{dataset_id}.json").read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{dataset_id}: metadata is unreadable") from exc
        if metadata != by_id[dataset_id]:
            raise ValueError(f"{dataset_id}: metadata does not match score manifest")
        if metadata.get("schema") != SCORE_SCHEMA:
            raise ValueError(f"{dataset_id}: score schema mismatch")
        if metadata.get("prepared_training_alignment_sha256") != prepared_metadata.get(
            "training_alignment_sha256"
        ) or metadata.get("prepared_evaluation_alignment_sha256") != prepared_metadata.get(
            "evaluation_alignment_sha256"
        ):
            raise ValueError(f"{dataset_id}: prepared alignment identity mismatch")
        if not str(metadata.get("model_contract", "")).strip():
            raise ValueError(f"{dataset_id}: model contract is missing")

        score_arrays = _load_npz(root / f"{dataset_id}.npz", dataset_id, SCORE_NPZ_KEYS)
        prepared_arrays = _load_npz(
            prepared / f"{dataset_id}.npz",
            dataset_id,
            {
                "baseline_probabilities",
                "evaluation_labels",
                "source_row_positions",
                "protected_attribute_values",
                "non_protected_feature_values",
                "training_labels",
                "training_source_row_positions",
                "training_protected_attribute_values",
                "training_non_protected_feature_values",
            },
        )
        train_positions = score_arrays["training_source_row_positions"]
        eval_positions = score_arrays["evaluation_source_row_positions"]
        train_scores = score_arrays["training_scores"]
        eval_scores = score_arrays["evaluation_scores"]
        if not np.array_equal(train_positions, prepared_arrays["training_source_row_positions"]):
            raise ValueError(f"{dataset_id}: training row positions mismatch")
        if not np.array_equal(eval_positions, prepared_arrays["source_row_positions"]):
            raise ValueError(f"{dataset_id}: evaluation row positions mismatch")
        for name, scores in (("training", train_scores), ("evaluation", eval_scores)):
            if scores.ndim != 1 or not np.issubdtype(scores.dtype, np.floating):
                raise ValueError(f"{dataset_id}: {name} scores must be a floating vector")
            if not np.all(np.isfinite(scores)) or np.any((scores < 0.1) | (scores > 0.8)):
                raise ValueError(f"{dataset_id}: {name} scores violate the frozen clip")
        if not np.array_equal(eval_scores, prepared_arrays["baseline_probabilities"]):
            raise ValueError(f"{dataset_id}: evaluation scores do not reproduce V2")
        expected_alignment = score_alignment_sha256(**score_arrays)
        if metadata.get("score_alignment_sha256") != expected_alignment:
            raise ValueError(f"{dataset_id}: score alignment SHA-256 mismatch")

    return {
        "schema": SCORE_SCHEMA,
        "dataset_ids": sorted(expected_ids),
        "prepared_manifest_sha256": prepared_digest,
        "preparation_source_commit": source_commit,
        "evaluation_scores_reproduce_v2": True,
        "readiness_scope": "score-replay-only",
        "outcome_ready": False,
    }
