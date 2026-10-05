from pathlib import Path

from tfoesuu.partial_replay_benchmarks import (
    partial_replay_benchmark_v1,
    read_partial_replay_jsonl,
    write_partial_replay_jsonl,
)


def test_partial_replay_grid_roundtrip(tmp_path: Path):
    rows = partial_replay_benchmark_v1()
    assert len(rows) >= 100
    assert len({row.benchmark_id for row in rows}) == len(rows)
    assert {row.graph_family for row in rows} == {"clique", "path", "matching"}
    assert min(row.d for row in rows) == 0.01
    assert max(row.max_group_size for row in rows) == 4
    assert all(row.p + row.shared_patch + row.d < 1.0 for row in rows)

    out = tmp_path / "partial_replay.jsonl"
    write_partial_replay_jsonl(rows, out)
    assert read_partial_replay_jsonl(out) == rows
