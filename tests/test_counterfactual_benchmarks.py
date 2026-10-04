from pathlib import Path

from tfoesuu.counterfactual_benchmarks import (
    counterfactual_replay_benchmark_v1,
    read_counterfactual_replay_jsonl,
    write_counterfactual_replay_jsonl,
)


def test_counterfactual_replay_grid_roundtrip(tmp_path: Path):
    rows = counterfactual_replay_benchmark_v1()
    assert len(rows) >= 100
    assert len({row.benchmark_id for row in rows}) == len(rows)
    assert min(row.d for row in rows) == 0.001
    assert {row.shared_patch for row in rows} == {0.05, 0.10, 0.20, 0.30}

    out = tmp_path / "counterfactual.jsonl"
    write_counterfactual_replay_jsonl(rows, out)
    assert read_counterfactual_replay_jsonl(out) == rows
