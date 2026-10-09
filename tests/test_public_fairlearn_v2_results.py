from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import pytest

from tfoesuu.public_fairlearn_v2_results import validate_public_fairlearn_v2_transcripts

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = json.loads(
    (ROOT / "configs" / "fairlearn_public_v2_analysis.json").read_text(encoding="utf-8")
)
COMMITS = {
    "old": "e8cc63784de5410805c156715175fc60e2cd5653",
    "new": "0cf59eccfdd364417787fe2c368a1c77c3f378b8",
}


def _mode(pmf):
    seeds = {}
    for seed in PROTOCOL["randomness"]["seeds"]:
        uniforms = [0.25, 0.75]
        predictions = (np.asarray(pmf)[:, 1] >= uniforms).astype(int).tolist()
        seeds[str(seed)] = {
            "uniforms": uniforms,
            "predictions": predictions,
            "repeat_identical": True,
            "threshold_correspondence": True,
        }
    return {"pmf": copy.deepcopy(pmf), "seeds": seeds}


def _records():
    records = []
    for dataset_id, spec in PROTOCOL["datasets"].items():
        single = spec["role"] == "single-attribute negative control"
        control = [[0.6, 0.4], [0.2, 0.8]]
        for version in ("old", "new"):
            multi = control if single or version == "new" else [[0.7, 0.3], [0.2, 0.8]]
            records.append(
                {
                    "schema": "tfoesuu-fairlearn-public-v2-transcript-v1",
                    "dataset_id": dataset_id,
                    "version": version,
                    "commit": COMMITS[version],
                    "prepared_manifest_sha256": PROTOCOL["prepared_input"][
                        "manifest_sha256"
                    ],
                    "companion_manifest_sha256": PROTOCOL["score_model"][
                        "companion_manifest_sha256"
                    ],
                    "plan_sha256": PROTOCOL["runner_preflight"]["plan_sha256"],
                    "source_row_positions": [10, 20],
                    "native_group_count": 2,
                    "canonical_group_count": 2,
                    "modes": {"multi": _mode(multi), "canonical": _mode(control)},
                }
            )
    return records


def test_transcript_validator_accepts_complete_synthetic_census():
    report = validate_public_fairlearn_v2_transcripts(_records(), PROTOCOL)

    assert len(report["datasets"]) == 7
    assert report["record_count"] == 14
    assert report["new_repair_conformance"] is True
    assert report["single_attribute_negative_controls"] is True


def test_transcript_validator_rejects_new_canonical_mismatch():
    records = _records()
    target = next(
        row
        for row in records
        if row["dataset_id"] == "public-adult" and row["version"] == "new"
    )
    target["modes"]["multi"]["pmf"][0] = [0.7, 0.3]

    with pytest.raises(ValueError, match="repaired multi-column PMF"):
        validate_public_fairlearn_v2_transcripts(records, PROTOCOL)


def test_transcript_validator_rejects_common_tape_drift():
    records = _records()
    target = next(row for row in records if row["version"] == "old")
    target["modes"]["multi"]["seeds"]["1"]["uniforms"][0] = 0.1

    with pytest.raises(ValueError, match="common uniform tape"):
        validate_public_fairlearn_v2_transcripts(records, PROTOCOL)


def test_transcript_validator_rejects_missing_record_or_prediction_drift():
    records = _records()
    with pytest.raises(ValueError, match="complete old/new census"):
        validate_public_fairlearn_v2_transcripts(records[:-1], PROTOCOL)

    records = copy.deepcopy(records)
    records[0]["modes"]["canonical"]["seeds"]["1"]["predictions"][0] ^= 1
    with pytest.raises(ValueError, match="threshold correspondence"):
        validate_public_fairlearn_v2_transcripts(records, PROTOCOL)
