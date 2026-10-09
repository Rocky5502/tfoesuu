from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from external_subjects.fairlearn_public_v2.runner_core import (
    OLD_COMMIT,
    ScoreLookupEstimator,
    run_dataset_transcript,
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


class _FakeThresholdOptimizer:
    def __init__(self, *, estimator, constraints, objective, prefit):
        assert constraints == "demographic_parity"
        assert objective == "accuracy_score"
        assert prefit is True
        self.estimator = estimator

    def fit(self, X, y, *, sensitive_features):
        assert len(X) == len(y) == len(sensitive_features)
        return self

    def _pmf_predict(self, X, *, sensitive_features):
        assert len(X) == len(sensitive_features)
        scores = self.estimator.predict(X)
        return np.column_stack((1.0 - scores, scores))

    def predict(self, X, *, sensitive_features, random_state):
        pmf = self._pmf_predict(X, sensitive_features=sensitive_features)
        uniforms = np.random.RandomState(random_state).rand(len(X))
        return (pmf[:, 1] >= uniforms).astype(int)


def test_run_dataset_transcript_freezes_common_tapes_and_provenance():
    record = run_dataset_transcript(
        threshold_optimizer_cls=_FakeThresholdOptimizer,
        dataset_id="toy",
        version="old",
        commit=OLD_COMMIT,
        training_positions=[10, 11, 12, 13],
        training_scores=[0.1, 0.8, 0.3, 0.7],
        training_labels=[0, 1, 0, 1],
        evaluation_positions=[20, 21],
        evaluation_scores=[0.25, 0.75],
        native_training_groups=[["a", "x"], ["b", "x"], ["a", "y"], ["b", "y"]],
        native_evaluation_groups=[["a", "x"], ["b", "y"]],
        canonical_training_groups=["a|x", "b|x", "a|y", "b|y"],
        canonical_evaluation_groups=["a|x", "b|y"],
        prepared_manifest_sha256="b" * 64,
        companion_manifest_sha256="c" * 64,
        plan_sha256="d" * 64,
        seeds=[1, 7],
    )

    assert record["schema"] == "tfoesuu-fairlearn-public-v2-transcript-v1"
    assert record["source_row_positions"] == [20, 21]
    assert record["native_group_count"] == record["canonical_group_count"] == 4
    assert record["modes"]["multi"]["pmf"] == [[0.75, 0.25], [0.25, 0.75]]
    assert record["modes"]["multi"]["seeds"]["7"]["uniforms"] == record["modes"][
        "canonical"
    ]["seeds"]["7"]["uniforms"]
    assert record["modes"]["canonical"]["seeds"]["1"]["repeat_identical"] is True
    assert record["modes"]["canonical"]["seeds"]["1"]["threshold_correspondence"] is True


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"evaluation_positions": [13, 20]}, "disjoint"),
        ({"native_evaluation_groups": [["a", "x"]]}, "evaluation"),
        ({"canonical_training_groups": ["a|x"]}, "training"),
    ],
)
def test_run_dataset_transcript_rejects_misaligned_inputs(changes, message):
    arguments = {
        "threshold_optimizer_cls": _FakeThresholdOptimizer,
        "dataset_id": "toy",
        "version": "new",
        "commit": "0cf59eccfdd364417787fe2c368a1c77c3f378b8",
        "training_positions": [10, 11, 12, 13],
        "training_scores": [0.1, 0.8, 0.3, 0.7],
        "training_labels": [0, 1, 0, 1],
        "evaluation_positions": [20, 21],
        "evaluation_scores": [0.25, 0.75],
        "native_training_groups": [["a", "x"], ["b", "x"], ["a", "y"], ["b", "y"]],
        "native_evaluation_groups": [["a", "x"], ["b", "y"]],
        "canonical_training_groups": ["a|x", "b|x", "a|y", "b|y"],
        "canonical_evaluation_groups": ["a|x", "b|y"],
        "prepared_manifest_sha256": "b" * 64,
        "companion_manifest_sha256": "c" * 64,
        "plan_sha256": "d" * 64,
        "seeds": [1],
    }
    arguments.update(changes)

    with pytest.raises(ValueError, match=message):
        run_dataset_transcript(**arguments)


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
