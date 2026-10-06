from pathlib import Path

from tfoesuu.partial_replay_benchmarks import (
    partial_replay_benchmark_v1,
    partial_replay_structural_cases_v1,
    read_partial_replay_jsonl,
    read_partial_replay_structural_jsonl,
    write_partial_replay_jsonl,
    write_partial_replay_structural_jsonl,
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

    committed = read_partial_replay_jsonl("data/partial_replay_benchmark_v1.jsonl")
    assert committed == rows



def test_partial_replay_structural_cases_roundtrip(tmp_path: Path):
    rows = partial_replay_structural_cases_v1()
    assert len(rows) == 8
    assert len({row.case_id for row in rows}) == len(rows)
    assert {row.regime for row in rows} == {
        "coherent-equality", "finite-linear-gap", "infinite-witness-gap"
    }

    finite = [row for row in rows if row.regime == "finite-linear-gap"]
    assert [row.n for row in finite] == list(range(3, 9))
    assert all(row.expected_ratio == row.n - 1.0 for row in finite)

    infinite = next(row for row in rows if row.regime == "infinite-witness-gap")
    assert infinite.expected_c_vert == 2.0
    assert infinite.expected_c_edge is None
    assert infinite.expected_ratio is None

    out = tmp_path / "partial_replay_structural.jsonl"
    write_partial_replay_structural_jsonl(rows, out)
    assert read_partial_replay_structural_jsonl(out) == rows

    committed = read_partial_replay_structural_jsonl(
        "data/partial_replay_structural_cases_v1.jsonl"
    )
    assert committed == rows
