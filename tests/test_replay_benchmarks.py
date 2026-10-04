from pathlib import Path

from tfoesuu.replay_benchmarks import (
    read_replay_jsonl,
    replay_benchmark_v1,
    write_replay_jsonl,
)


def test_replay_benchmark_roundtrip(tmp_path: Path):
    rows = replay_benchmark_v1()
    assert len(rows) >= 50
    assert len({row.benchmark_id for row in rows}) == len(rows)
    assert min(row.d for row in rows) <= 0.002
    assert {row.p for row in rows} == {0.25, 0.50, 0.75}

    out = tmp_path / "replay.jsonl"
    write_replay_jsonl(rows, out)
    assert read_replay_jsonl(out) == rows
