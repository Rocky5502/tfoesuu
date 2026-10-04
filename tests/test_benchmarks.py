from pathlib import Path

from tfoesuu.benchmarks import benchmark_v1, read_jsonl, write_jsonl


def test_benchmark_roundtrip(tmp_path: Path):
    rows = benchmark_v1()
    assert len(rows) > 50
    out = tmp_path / "bench.jsonl"
    write_jsonl(rows, out)
    loaded = read_jsonl(out)
    assert loaded == rows
    assert len({r.benchmark_id for r in rows}) == len(rows)
