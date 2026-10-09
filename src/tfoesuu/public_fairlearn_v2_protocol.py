from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "tfoesuu-fairlearn-public-v2-analysis-v1"
EXPECTED_DATASETS = {
    "public-adult": ("sex", "race"),
    "public-bank": ("age",),
    "public-compas": ("race", "sex"),
    "public-default-credit": ("sex", "age"),
    "public-german": ("sex", "age"),
    "public-lawschool": ("race", "gender"),
    "public-meps21": ("race",),
}
NUMERIC_AGE_DATASETS = {
    "public-bank",
    "public-default-credit",
    "public-german",
}
EXPECTED_OLD = "e8cc63784de5410805c156715175fc60e2cd5653"
EXPECTED_NEW = "0cf59eccfdd364417787fe2c368a1c77c3f378b8"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _positive_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise TypeError(f"{field} must be a positive integer")
    return value


def validate_public_fairlearn_v2_protocol(protocol: dict[str, Any]) -> dict[str, Any]:
    """Validate the frozen no-outcome Fairlearn public-context analysis contract."""

    if protocol.get("schema") != SCHEMA:
        raise ValueError("analysis protocol schema mismatch")
    if protocol.get("outcome_authorized") is not False:
        raise ValueError("outcome_authorized must remain false before explicit approval")
    if protocol.get("post_outcome_changes_allowed") is not False:
        raise ValueError("post_outcome_changes_allowed must remain false")

    prepared = protocol.get("prepared_input")
    if not isinstance(prepared, dict):
        raise TypeError("prepared_input must be an object")
    if prepared.get("schema") != "tfoesuu-public-context-v2.1":
        raise ValueError("prepared input schema mismatch")
    if not _GIT_RE.fullmatch(str(prepared.get("preparation_commit", ""))):
        raise ValueError("prepared input requires a full Git commit")
    if not _SHA256_RE.fullmatch(str(prepared.get("manifest_sha256", ""))):
        raise ValueError("prepared input requires a SHA-256 manifest")

    subject = protocol.get("subject")
    if not isinstance(subject, dict):
        raise TypeError("subject must be an object")
    if subject.get("old_commit") != EXPECTED_OLD or subject.get("new_commit") != EXPECTED_NEW:
        raise ValueError("Fairlearn old/new source pair mismatch")
    if subject.get("prefit") is not True:
        raise ValueError("subject must use the frozen prefit score model")

    support = protocol.get("support_gate")
    if not isinstance(support, dict):
        raise TypeError("support_gate must be an object")
    for field in (
        "minimum_training_rows_per_group",
        "minimum_training_rows_per_label_per_group",
        "minimum_evaluation_rows_per_group",
    ):
        _positive_integer(support.get(field), field)
    if support.get("require_every_evaluation_group_in_training") is not True:
        raise ValueError("evaluation groups must all occur in training")
    if "no adaptive merge or exclusion" not in str(support.get("failure_policy", "")):
        raise ValueError("support failure policy must forbid adaptive changes")

    datasets = protocol.get("datasets")
    if not isinstance(datasets, dict) or set(datasets) != set(EXPECTED_DATASETS):
        raise ValueError("protocol must contain exactly seven registered datasets")
    multi_count = 0
    for dataset_id, expected_columns in EXPECTED_DATASETS.items():
        entry = datasets[dataset_id]
        if not isinstance(entry, dict):
            raise TypeError(f"{dataset_id}: dataset entry must be an object")
        columns = tuple(entry.get("protected_columns", ()))
        if columns != expected_columns:
            raise ValueError(f"{dataset_id}: protected column order mismatch")
        expected_role = (
            "multi-attribute subject" if len(columns) > 1 else "single-attribute negative control"
        )
        if entry.get("role") != expected_role:
            raise ValueError(f"{dataset_id}: role mismatch")
        multi_count += len(columns) > 1
        transforms = entry.get("transforms")
        if not isinstance(transforms, dict) or tuple(transforms) != columns:
            raise ValueError(f"{dataset_id}: transforms must follow protected column order")
        for column in columns:
            transform = transforms[column]
            if not isinstance(transform, dict):
                raise TypeError(f"{dataset_id}/{column}: transform must be an object")
            if column == "age" and dataset_id in NUMERIC_AGE_DATASETS:
                if transform.get("kind") != "threshold" or transform.get("cut") != 25:
                    raise ValueError(f"{dataset_id}: numeric age must use frozen threshold 25")
                if transform.get("lower_label") == transform.get("upper_label"):
                    raise ValueError(f"{dataset_id}: age labels must be distinct")
            elif transform != {"kind": "identity"}:
                raise ValueError(f"{dataset_id}/{column}: categorical transform must be identity")

    estimands = protocol.get("estimands")
    if not isinstance(estimands, dict) or not str(estimands.get("primary", "")).strip():
        raise ValueError("protocol requires a primary estimand")
    randomness = protocol.get("randomness")
    if not isinstance(randomness, dict):
        raise TypeError("randomness must be an object")
    if randomness.get("common_tape_required") is not True:
        raise ValueError("common tape must be required")
    if randomness.get("primary_analysis_uses_exact_pmf") is not True:
        raise ValueError("primary analysis must use exact PMFs")
    seeds = randomness.get("seeds")
    if seeds != [1, 104729, 130363, 155921] or len(set(seeds)) != len(seeds):
        raise ValueError("frozen seed list mismatch")

    return {
        "schema": SCHEMA,
        "dataset_count": len(datasets),
        "multi_attribute_dataset_count": multi_count,
        "outcome_authorized": False,
        "post_outcome_changes_allowed": False,
    }


def load_and_validate_public_fairlearn_v2_protocol(path: str | Path) -> dict[str, Any]:
    protocol = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(protocol, dict):
        raise TypeError("analysis protocol root must be an object")
    return validate_public_fairlearn_v2_protocol(protocol)
