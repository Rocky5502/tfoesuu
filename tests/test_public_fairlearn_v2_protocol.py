from __future__ import annotations

import json
from pathlib import Path

import pytest

from tfoesuu.public_fairlearn_v2_protocol import (
    load_and_validate_public_fairlearn_v2_protocol,
    validate_public_fairlearn_v2_protocol,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "fairlearn_public_v2_analysis.json"


def _protocol() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def test_committed_public_fairlearn_v2_protocol_is_complete():
    report = load_and_validate_public_fairlearn_v2_protocol(CONFIG)

    assert report["dataset_count"] == 7
    assert report["multi_attribute_dataset_count"] == 5
    assert report["outcome_authorized"] is False
    assert report["post_outcome_changes_allowed"] is False


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda p: p["datasets"].pop("public-adult"), "exactly seven"),
        (
            lambda p: p["datasets"]["public-german"]["transforms"].update(
                {"age": {"kind": "identity"}}
            ),
            "numeric age",
        ),
        (
            lambda p: p["support_gate"].update({"minimum_training_rows_per_group": 0}),
            "positive integer",
        ),
        (
            lambda p: p.update({"outcome_authorized": True}),
            "must remain false",
        ),
        (
            lambda p: p["estimands"].pop("primary"),
            "primary estimand",
        ),
    ],
)
def test_protocol_rejects_scope_or_analysis_drift(mutation, message):
    protocol = _protocol()
    mutation(protocol)
    with pytest.raises((TypeError, ValueError), match=message):
        validate_public_fairlearn_v2_protocol(protocol)
