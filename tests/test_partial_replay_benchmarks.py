from pathlib import Path

import pytest

from tfoesuu.graphs import clique_graph, matching_graph, path_graph
from tfoesuu.partial_replay_lower import (
    active_vertex_contrast_schedule,
    minimum_fractional_active_vertex_cover,
    minimum_fractional_replay_cover,
)
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



def test_structural_manifest_matches_lp_implementation():
    for row in partial_replay_structural_cases_v1():
        if row.graph_family == "clique":
            graph = clique_graph(row.n)
            groups = list(graph.edges)
        elif row.graph_family == "matching":
            graph = matching_graph(row.n // 2)
            groups = list(graph.edges)
        elif row.graph_family == "path" and row.group_rule == "reference_pairs_02_12":
            graph = path_graph(row.n)
            groups = [(0, 2), (1, 2)]
        else:
            raise AssertionError(f"unsupported structural case: {row}")

        costs = [1.0] * len(groups)
        vertex = minimum_fractional_active_vertex_cover(graph, groups, costs)
        edge = minimum_fractional_replay_cover(graph, groups, costs)

        assert vertex.success
        assert vertex.cost == pytest.approx(row.expected_c_vert)
        contrast = active_vertex_contrast_schedule(
            graph, groups, costs, d=0.05, beta=0.05
        )
        assert contrast.normalized_fractional_cost == pytest.approx(
            row.expected_raw_contrast_cost
        )

        if row.expected_c_edge is None:
            assert not edge.success
            assert edge.cost == float("inf")
        else:
            assert edge.success
            assert edge.cost == pytest.approx(row.expected_c_edge)
            assert edge.cost / vertex.cost == pytest.approx(row.expected_ratio)
