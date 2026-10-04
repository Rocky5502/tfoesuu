from pathlib import Path

from tfoesuu.subject_benchmarks import (
    read_software_subject_jsonl,
    software_subject_benchmark_v1,
    write_software_subject_jsonl,
)


def test_software_subject_benchmark_is_deterministic_and_roundtrips(tmp_path: Path):
    rows = software_subject_benchmark_v1()
    assert len(rows) == 32
    assert len({row.benchmark_id for row in rows}) == len(rows)
    assert {row.contexts for row in rows} == {16, 64, 256, 1024}
    assert min(row.delta for row in rows) == 0.005

    out = tmp_path / "subjects.jsonl"
    write_software_subject_jsonl(rows, out)
    assert read_software_subject_jsonl(out) == rows
