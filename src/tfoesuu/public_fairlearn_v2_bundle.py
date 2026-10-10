from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .public_fairlearn_v2_preflight import (
    _decode_scalar,
    build_public_fairlearn_v2_preflight,
    canonical_tuple_key,
    transform_protected_rows,
)

INPUT_BUNDLE_SCHEMA = "tfoesuu-fairlearn-public-v2-input-bundle-v1"
DATASET_INPUT_SCHEMA = "tfoesuu-fairlearn-public-v2-dataset-input-v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_dataset_input_payload(
    *,
    dataset_id: str,
    training_positions: np.ndarray,
    training_scores: np.ndarray,
    training_labels: np.ndarray,
    evaluation_positions: np.ndarray,
    evaluation_scores: np.ndarray,
    training_groups: tuple[tuple[object, ...], ...],
    evaluation_groups: tuple[tuple[object, ...], ...],
) -> dict[str, Any]:
    """Serialize one validated context without losing IEEE-754 score bits."""

    train_positions = np.asarray(training_positions)
    train_scores = np.asarray(training_scores)
    train_labels = np.asarray(training_labels)
    eval_positions = np.asarray(evaluation_positions)
    eval_scores = np.asarray(evaluation_scores)
    if not dataset_id:
        raise ValueError("dataset ID must be nonempty")
    if not (
        train_positions.ndim
        == train_scores.ndim
        == train_labels.ndim
        == eval_positions.ndim
        == eval_scores.ndim
        == 1
    ):
        raise ValueError("runner numeric inputs must be vectors")
    if not (
        len(train_positions) == len(train_scores) == len(train_labels) == len(training_groups)
        and len(eval_positions) == len(eval_scores) == len(evaluation_groups)
    ):
        raise ValueError("runner input rows are misaligned")
    if not training_groups or not evaluation_groups:
        raise ValueError("runner protected groups must be nonempty")
    width = len(training_groups[0])
    if width < 1 or any(len(group) != width for group in (*training_groups, *evaluation_groups)):
        raise ValueError("runner protected group widths are inconsistent")

    def native(groups: tuple[tuple[object, ...], ...]) -> list[object]:
        if width == 1:
            return [group[0] for group in groups]
        return [list(group) for group in groups]

    return {
        "schema": DATASET_INPUT_SCHEMA,
        "dataset_id": dataset_id,
        "training_positions": [int(value) for value in train_positions],
        "training_score_hex": [float(value).hex() for value in train_scores],
        "training_labels": [int(value) for value in train_labels],
        "evaluation_positions": [int(value) for value in eval_positions],
        "evaluation_score_hex": [float(value).hex() for value in eval_scores],
        "native_training_groups": native(training_groups),
        "native_evaluation_groups": native(evaluation_groups),
        "canonical_training_groups": [canonical_tuple_key(group) for group in training_groups],
        "canonical_evaluation_groups": [
            canonical_tuple_key(group) for group in evaluation_groups
        ],
    }


def build_public_fairlearn_v2_input_bundle(
    prepared_dir: str | Path,
    companion_dir: str | Path,
    protocol_path: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Materialize validated, outcome-free inputs for the historical runtime."""

    prepared = Path(prepared_dir)
    companion = Path(companion_dir)
    protocol_file = Path(protocol_path)
    output = Path(output_dir)
    if output.exists():
        raise FileExistsError(f"runner input output already exists: {output}")
    if not output.parent.is_dir():
        raise ValueError("runner input output parent must already exist")
    protocol = json.loads(protocol_file.read_text(encoding="utf-8"))
    preflight = build_public_fairlearn_v2_preflight(prepared, companion, protocol_file)
    expected_plan = protocol["runner_preflight"]["plan_sha256"]
    if preflight["plan_sha256"] != expected_plan:
        raise ValueError("runner input plan does not match the frozen protocol")

    payloads: dict[str, dict[str, Any]] = {}
    for dataset_id in sorted(protocol["datasets"]):
        entry = protocol["datasets"][dataset_id]
        with np.load(prepared / f"{dataset_id}.npz", allow_pickle=False) as source:
            training_tokens = source["training_protected_attribute_values"]
            evaluation_tokens = source["protected_attribute_values"]
            training_positions = source["training_source_row_positions"]
            evaluation_positions = source["source_row_positions"]
            training_labels = source["training_labels"]
        with np.load(companion / f"{dataset_id}.npz", allow_pickle=False) as scores:
            training_scores = scores["training_scores"]
            evaluation_scores = scores["evaluation_scores"]
        training_raw = np.asarray(
            [[_decode_scalar(token) for token in row] for row in training_tokens],
            dtype=object,
        )
        evaluation_raw = np.asarray(
            [[_decode_scalar(token) for token in row] for row in evaluation_tokens],
            dtype=object,
        )
        columns = tuple(entry["protected_columns"])
        training_groups = transform_protected_rows(
            training_raw, columns, entry["transforms"]
        )
        evaluation_groups = transform_protected_rows(
            evaluation_raw, columns, entry["transforms"]
        )
        payloads[dataset_id] = build_dataset_input_payload(
            dataset_id=dataset_id,
            training_positions=training_positions,
            training_scores=training_scores,
            training_labels=training_labels,
            evaluation_positions=evaluation_positions,
            evaluation_scores=evaluation_scores,
            training_groups=training_groups,
            evaluation_groups=evaluation_groups,
        )

    output.mkdir()
    rows = []
    for dataset_id, payload in payloads.items():
        path = output / f"{dataset_id}.json"
        _write_json(path, payload)
        rows.append(
            {
                "dataset_id": dataset_id,
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    manifest = {
        "schema": INPUT_BUNDLE_SCHEMA,
        "protocol_sha256": _sha256(protocol_file),
        "prepared_manifest_sha256": protocol["prepared_input"]["manifest_sha256"],
        "companion_manifest_sha256": protocol["score_model"][
            "companion_manifest_sha256"
        ],
        "plan_sha256": expected_plan,
        "datasets": rows,
        "outcome_authorized": False,
        "scope": "historical-runtime-input-only",
    }
    manifest_path = output / "input_bundle_manifest.json"
    _write_json(manifest_path, manifest)
    return {
        "schema": INPUT_BUNDLE_SCHEMA,
        "dataset_count": len(rows),
        "manifest_sha256": _sha256(manifest_path),
        "outcome_authorized": False,
    }
