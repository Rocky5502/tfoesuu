from pathlib import Path

import pytest

from tfoesuu.control_replay import (
    control_replay_information_lower_bound,
    minimum_fractional_control_cover,
)
from tfoesuu.control_replay_benchmarks import (
    control_replay_structural_cases_v1,
    read_control_replay_structural_jsonl,
    write_control_replay_structural_jsonl,
)
from tfoesuu.graphs import complete_bipartite_graph


def test_control_replay_structural_fixture_roundtrip(tmp_path: Path):
    rows = control_replay_structural_cases_v1()
    assert len(rows) == 6
    assert len({row.case_id for row in rows}) == 6

    out = tmp_path / "control_replay.jsonl"
    write_control_replay_structural_jsonl(rows, out)
    assert read_control_replay_structural_jsonl(out) == rows

    committed = read_control_replay_structural_jsonl(
        "data/control_replay_structural_cases_v1.jsonl"
    )
    assert committed == rows


@pytest.mark.parametrize("case", control_replay_structural_cases_v1())
def test_control_replay_structural_fixture_exact_cover(case):
    graph = complete_bipartite_graph(case.high_count, case.low_count)
    high = tuple(range(case.high_count))
    cover = minimum_fractional_control_cover(
        graph,
        case.groups,
        case.costs,
        high,
    )

    assert cover.success is case.expected_control_feasible
    if case.expected_control_feasible:
        assert cover.cost == pytest.approx(case.expected_control_cover)
    else:
        assert cover.cost == float("inf")


def test_boundary_only_fixture_has_finite_quadratic_information_floor():
    case = next(
        row
        for row in control_replay_structural_cases_v1()
        if row.case_id == "p19-boundary-only"
    )
    graph = complete_bipartite_graph(case.high_count, case.low_count)
    high = tuple(range(case.high_count))

    a = control_replay_information_lower_bound(
        graph,
        case.groups,
        case.costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=1e-4,
        beta=0.05,
    )
    b = control_replay_information_lower_bound(
        graph,
        case.groups,
        case.costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=5e-5,
        beta=0.05,
    )

    assert a.success and b.success
    assert b.expected_cost_floor / a.expected_cost_floor == pytest.approx(
        4.0, rel=2e-3
    )
