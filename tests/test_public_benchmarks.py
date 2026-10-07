from pathlib import Path

from tfoesuu.public_benchmarks import (
    public_benchmark_registry_v1,
    read_public_benchmark_registry,
    write_public_benchmark_registry,
)


def test_public_benchmark_registry_roundtrip(tmp_path: Path):
    rows = public_benchmark_registry_v1()
    assert len(rows) == 7
    assert len({row.benchmark_id for row in rows}) == 7
    assert {row.loader_family for row in rows} == {
        "uci", "propublica", "aif360"
    }
    assert all(row.status == "planned" for row in rows)
    assert all(row.protected_attributes for row in rows)

    out = tmp_path / "public_benchmarks.jsonl"
    write_public_benchmark_registry(rows, out)
    assert read_public_benchmark_registry(out) == rows

    committed = read_public_benchmark_registry(
        "data/public_benchmark_registry_v1.jsonl"
    )
    assert committed == rows
