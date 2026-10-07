from pathlib import Path

import pytest

from tfoesuu.graphs import clique_graph, matching_graph, path_graph
from tfoesuu.partial_replay_lower import (
    active_vertex_contrast_schedule,
    minimum_fractional_active_vertex_cover,
    minimum_fractional_replay_cover,
    raw_group_contrast_witness,
    raw_output_information_lower_bound,
)
from tfoesuu.partial_replay_benchmarks import (
    materialize_partial_replay_spec,
    partial_replay_benchmark_v1,
    partial_replay_scope_cases_v1,
    partial_replay_structural_cases_v1,
    read_partial_replay_jsonl,
    read_partial_replay_scope_jsonl,
    read_partial_replay_structural_jsonl,
    write_partial_replay_jsonl,
    write_partial_replay_scope_jsonl,
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



def test_partial_replay_scope_counterexample_manifest(tmp_path: Path):
    rows = partial_replay_scope_cases_v1()
    assert len(rows) == 1
    row = rows[0]
    assert row.regime == "heterogeneous-null-false-positive"

    fair_null = abs(row.new_threshold_0 - row.new_threshold_1) <= row.fairness_tau
    assert fair_null is row.expected_fair_null
    assert fair_null

    old = [
        int(row.tape_u <= row.old_threshold_0),
        int(row.tape_u <= row.old_threshold_1),
    ]
    new = [
        int(row.tape_u <= row.new_threshold_0),
        int(row.tape_u <= row.new_threshold_1),
    ]
    contrast = raw_group_contrast_witness(old, new)
    assert contrast is row.expected_raw_contrast
    assert contrast

    # Audit the entire piecewise-constant shared-tape geometry rather than
    # protecting only the frozen witness tape.  For threshold Bernoulli draws,
    # the contrast can change only at one of the four old/new thresholds.
    cuts = sorted({
        0.0,
        row.old_threshold_0,
        row.old_threshold_1,
        row.new_threshold_0,
        row.new_threshold_1,
        1.0,
    })
    rejecting_intervals = []
    false_positive_measure = 0.0
    for left, right in zip(cuts, cuts[1:]):
        if right <= left:
            continue
        u = (left + right) / 2.0
        old_u = [
            int(u <= row.old_threshold_0),
            int(u <= row.old_threshold_1),
        ]
        new_u = [
            int(u <= row.new_threshold_0),
            int(u <= row.new_threshold_1),
        ]
        if raw_group_contrast_witness(old_u, new_u):
            rejecting_intervals.append((left, right))
            false_positive_measure += right - left

    assert len(rejecting_intervals) == 2
    for actual, expected in zip(
        rejecting_intervals, [(0.20, 0.30), (0.40, 0.45)]
    ):
        assert actual[0] == pytest.approx(expected[0])
        assert actual[1] == pytest.approx(expected[1])
    assert false_positive_measure == pytest.approx(
        row.expected_false_positive_measure
    )
    assert false_positive_measure == pytest.approx(0.15)

    out = tmp_path / "partial_replay_scope.jsonl"
    write_partial_replay_scope_jsonl(rows, out)
    assert read_partial_replay_scope_jsonl(out) == rows
    committed = read_partial_replay_scope_jsonl(
        "data/partial_replay_scope_cases_v1.jsonl"
    )
    assert committed == rows


def test_all_partial_replay_stress_rows_execute_theorem_geometry():
    rows = partial_replay_benchmark_v1()
    assert len(rows) == 168

    for row in rows:
        graph, groups, costs = materialize_partial_replay_spec(row)
        assert groups
        assert len(groups) == len(costs)
        assert max(len(group) for group in groups) == row.max_group_size
        assert all(cost == pytest.approx(row.cost_per_vertex * len(group))
                   for group, cost in zip(groups, costs))

        vertex = minimum_fractional_active_vertex_cover(graph, groups, costs)
        edge = minimum_fractional_replay_cover(graph, groups, costs)
        raw = raw_output_information_lower_bound(
            graph,
            groups,
            costs,
            p=row.p,
            shared_patch=row.shared_patch,
            d=row.d,
            beta=row.beta,
        )
        contrast = active_vertex_contrast_schedule(
            graph, groups, costs, d=row.d, beta=row.beta
        )

        assert vertex.success
        assert edge.success
        assert raw.success
        assert vertex.cost <= edge.cost + 1e-9
        assert contrast.normalized_fractional_cost == pytest.approx(vertex.cost)
        assert raw.expected_cost_floor > 0.0
        assert contrast.scale > 0
        assert contrast.total_cost <= (
            contrast.scale * vertex.cost
            + contrast.additive_rounding_cap
            + 1e-8
        )

        for x in contrast.active_vertices:
            exposure = sum(
                int(contrast.counts[i])
                for i, group in enumerate(groups)
                if x in group
            )
            assert exposure >= contrast.scale
            exact_miss = (1.0 - row.d) ** exposure
            assert exact_miss <= row.beta + 1e-12
