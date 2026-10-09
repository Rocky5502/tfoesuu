from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from external_subjects.fairlearn_public_v2.runner_core import (
    ScoreLookupEstimator,
    validate_campaign_approval,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_score_lookup_estimator_returns_scores_in_requested_order():
    estimator = ScoreLookupEstimator([4, 9, 2], [0.4, 0.9, 0.2])

    assert estimator.predict(np.array([[2], [4], [9]])).tolist() == [0.2, 0.4, 0.9]


def test_score_lookup_estimator_rejects_unknown_or_duplicate_rows():
    with pytest.raises(ValueError, match="unique"):
        ScoreLookupEstimator([1, 1], [0.2, 0.3])
    estimator = ScoreLookupEstimator([1], [0.2])
    with pytest.raises(ValueError, match="unknown"):
        estimator.predict(np.array([[2]]))


def test_campaign_approval_is_external_and_bound_to_protocol(tmp_path):
    protocol = tmp_path / "protocol.json"
    protocol.write_text('{"outcome_authorized": false}\n', encoding="utf-8")
    approval = {
        "schema": "tfoesuu-public-v2-approval-v1",
        "authorized": True,
        "scope": "bounded-seven-dataset-fairlearn-v2",
        "protocol_sha256": _sha256(protocol),
        "old_commit": "e8cc63784de5410805c156715175fc60e2cd5653",
        "new_commit": "0cf59eccfdd364417787fe2c368a1c77c3f378b8",
        "seeds": [1, 104729, 130363, 155921],
        "authorized_by": "user",
        "authorized_at": "2026-10-10T00:00:00+08:00",
    }
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(json.dumps(approval), encoding="utf-8")

    report = validate_campaign_approval(protocol, approval_path)

    assert report["authorized"] is True
    assert report["protocol_sha256"] == _sha256(protocol)


def test_campaign_approval_rejects_scope_or_protocol_drift(tmp_path):
    protocol = tmp_path / "protocol.json"
    protocol.write_text("{}", encoding="utf-8")
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(
            {
                "schema": "tfoesuu-public-v2-approval-v1",
                "authorized": True,
                "scope": "wrong",
                "protocol_sha256": "0" * 64,
                "old_commit": "e8cc63784de5410805c156715175fc60e2cd5653",
                "new_commit": "0cf59eccfdd364417787fe2c368a1c77c3f378b8",
                "seeds": [1, 104729, 130363, 155921],
                "authorized_by": "user",
                "authorized_at": "2026-10-10T00:00:00+08:00",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="scope"):
        validate_campaign_approval(protocol, approval)
