from __future__ import annotations

import json

import pytest

from tfoesuu.replay_benchmarks import ReplayBenchmarkSpec
from tfoesuu.sweep_integrity import load_compatible_shard


def _spec() -> ReplayBenchmarkSpec:
    return ReplayBenchmarkSpec("r0001", 0.25, 0.1, 0.05, 123)


def _row(**changes):
    row = {
        **_spec().__dict__,
        "device": "cuda:0",
        "trials": 100_000,
        "paired_upper_rounds": 1,
    }
    row.update(changes)
    return row


def test_resume_accepts_fully_matching_row(tmp_path):
    shard = tmp_path / "shard.jsonl"
    shard.write_text(json.dumps(_row()) + "\n", encoding="utf-8")

    rows = load_compatible_shard(shard, [_spec()], trials=100_000, device="cuda:0")

    assert set(rows) == {"r0001"}


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"trials": 10_000}, "incompatible run identity"),
        ({"device": "cuda:1"}, "incompatible run identity"),
        ({"seed": 999}, "specification mismatch"),
        ({"benchmark_id": "r9999"}, "unexpected benchmark ID"),
    ],
)
def test_resume_rejects_incompatible_row(tmp_path, changes, message):
    shard = tmp_path / "shard.jsonl"
    shard.write_text(json.dumps(_row(**changes)) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_compatible_shard(shard, [_spec()], trials=100_000, device="cuda:0")
