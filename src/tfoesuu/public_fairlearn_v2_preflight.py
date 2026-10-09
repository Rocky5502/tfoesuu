from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

import numpy as np

from .public_benchmarks_v2 import validate_prepared_public_v2_directory
from .public_fairlearn_v2_protocol import validate_public_fairlearn_v2_protocol
from .public_score_companion_v2 import validate_public_score_companion_v2


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decode_scalar(token: str) -> object:
    payload = json.loads(str(token))
    kind = payload["kind"]
    if kind == "missing":
        return None
    value = payload["value"]
    return float.fromhex(value) if kind == "float" else value


def canonical_tuple_key(values: Sequence[object]) -> str:
    """Encode an ordered tuple injectively with byte lengths and hex payloads."""

    parts = []
    for value in values:
        payload = json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
        parts.append(f"{len(payload)}:{payload.hex()}")
    return "|".join(parts)


def transform_protected_rows(
    rows: np.ndarray,
    columns: Sequence[str],
    transforms: dict,
) -> tuple[tuple[object, ...], ...]:
    matrix = np.asarray(rows, dtype=object)
    if matrix.ndim != 2 or matrix.shape[1] != len(columns):
        raise ValueError("protected matrix/column mismatch")
    transformed = []
    for row in matrix.tolist():
        output = []
        for column, value in zip(columns, row, strict=True):
            rule = transforms[column]
            if rule["kind"] == "identity":
                output.append(value)
            elif rule["kind"] == "threshold":
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise TypeError(f"{column}: threshold transform requires numeric values")
                output.append(
                    rule["lower_label"] if value < rule["cut"] else rule["upper_label"]
                )
            else:
                raise ValueError(f"{column}: unknown protected transform")
        transformed.append(tuple(output))
    return tuple(transformed)


def audit_group_support(
    training_groups: Sequence[tuple[object, ...]],
    training_labels: np.ndarray,
    evaluation_groups: Sequence[tuple[object, ...]],
    *,
    minimum_training_rows: int,
    minimum_training_per_label: int,
    minimum_evaluation_rows: int,
) -> dict:
    labels = np.asarray(training_labels)
    if labels.shape != (len(training_groups),) or not np.all(np.isin(labels, [0, 1])):
        raise ValueError("training labels are not an aligned binary vector")
    train_counts = Counter(training_groups)
    evaluation_counts = Counter(evaluation_groups)
    label_counts = Counter(
        (group, int(label))
        for group, label in zip(training_groups, labels, strict=True)
    )
    failures = []
    for group in sorted(set(train_counts) | set(evaluation_counts), key=repr):
        counts = (
            train_counts[group],
            label_counts[(group, 0)],
            label_counts[(group, 1)],
            evaluation_counts[group],
        )
        if (
            counts[0] < minimum_training_rows
            or min(counts[1], counts[2]) < minimum_training_per_label
            or counts[3] < minimum_evaluation_rows
        ):
            failures.append((group, *counts))
    if failures:
        raise ValueError(f"support gate failed: {failures}")
    groups = list(train_counts)
    return {
        "group_count": len(groups),
        "minimum_training_rows": min(train_counts.values()),
        "minimum_training_rows_per_label": min(
            label_counts[(group, label)] for group in groups for label in (0, 1)
        ),
        "minimum_evaluation_rows": min(evaluation_counts[group] for group in groups),
    }


def build_public_fairlearn_v2_preflight(
    prepared_dir: str | Path,
    companion_dir: str | Path,
    protocol_path: str | Path,
) -> dict:
    """Build a fail-closed execution plan without importing or running Fairlearn."""

    prepared = Path(prepared_dir)
    companion = Path(companion_dir)
    protocol_file = Path(protocol_path)
    protocol = json.loads(protocol_file.read_text(encoding="utf-8"))
    validate_public_fairlearn_v2_protocol(protocol)
    prepared_report = validate_prepared_public_v2_directory(prepared)
    companion_report = validate_public_score_companion_v2(companion, prepared)
    if protocol["prepared_input"]["manifest_sha256"] != _file_sha256(
        prepared / "prepared_v2_manifest.json"
    ):
        raise ValueError("protocol/prepared manifest SHA-256 mismatch")
    score_model = protocol["score_model"]
    if score_model["companion_manifest_sha256"] != _file_sha256(
        companion / "score_companion_manifest.json"
    ):
        raise ValueError("protocol/score companion manifest SHA-256 mismatch")
    if (
        score_model["companion_preparation_commit"]
        != companion_report["preparation_source_commit"]
    ):
        raise ValueError("protocol/score companion commit mismatch")

    gate = protocol["support_gate"]
    reports = []
    plan_digest = hashlib.sha256()
    for dataset_id in sorted(protocol["datasets"]):
        entry = protocol["datasets"][dataset_id]
        columns = tuple(entry["protected_columns"])
        with np.load(prepared / f"{dataset_id}.npz", allow_pickle=False) as arrays:
            training_tokens = arrays["training_protected_attribute_values"]
            evaluation_tokens = arrays["protected_attribute_values"]
            training_labels = arrays["training_labels"]
            training_positions = arrays["training_source_row_positions"]
            evaluation_positions = arrays["source_row_positions"]
        training_raw = np.asarray(
            [[_decode_scalar(token) for token in row] for row in training_tokens],
            dtype=object,
        )
        evaluation_raw = np.asarray(
            [[_decode_scalar(token) for token in row] for row in evaluation_tokens],
            dtype=object,
        )
        training_groups = transform_protected_rows(
            training_raw, columns, entry["transforms"]
        )
        evaluation_groups = transform_protected_rows(
            evaluation_raw, columns, entry["transforms"]
        )
        support = audit_group_support(
            training_groups,
            training_labels,
            evaluation_groups,
            minimum_training_rows=gate["minimum_training_rows_per_group"],
            minimum_training_per_label=gate[
                "minimum_training_rows_per_label_per_group"
            ],
            minimum_evaluation_rows=gate["minimum_evaluation_rows_per_group"],
        )
        all_groups = set(training_groups) | set(evaluation_groups)
        key_to_group = {canonical_tuple_key(group): group for group in all_groups}
        if len(key_to_group) != len(all_groups):
            raise ValueError(f"{dataset_id}: canonical protected key collision")
        payload = {
            "dataset_id": dataset_id,
            "role": entry["role"],
            **support,
            "training_rows": len(training_groups),
            "evaluation_rows": len(evaluation_groups),
            "canonical_key_count": len(key_to_group),
        }
        reports.append(payload)
        plan_digest.update(
            json.dumps(
                {
                    **payload,
                    "training_positions": training_positions.tolist(),
                    "evaluation_positions": evaluation_positions.tolist(),
                    "training_groups": training_groups,
                    "evaluation_groups": evaluation_groups,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        )

    return {
        "schema": "tfoesuu-fairlearn-public-v2-preflight-v1",
        "prepared_source_commit": prepared_report["source_commit"],
        "score_companion_commit": companion_report["preparation_source_commit"],
        "datasets": reports,
        "plan_sha256": plan_digest.hexdigest(),
        "outcome_authorized": False,
        "readiness_scope": "runner-preflight-only",
    }
