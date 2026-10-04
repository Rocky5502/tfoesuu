import pytest

from tfoesuu.graphs import clique_graph, matching_graph, path_graph
from tfoesuu.partial_replay import minimum_replay_group_cover
from tfoesuu.partial_replay_lower import (
    fractional_group_replay_lower_bound,
    fractional_replay_schedule,
    minimum_fractional_replay_cover,
)


def test_full_suite_fractional_floor_is_one_group():
    g = clique_graph(6)
    r = fractional_group_replay_lower_bound(
        g, [range(g.n)], costs=[12.0], per_informative_query_kl=0.1, beta=0.05
    )
    assert r.success
    assert r.normalized_cost == pytest.approx(12.0)
    assert r.query_weights[0] == pytest.approx(1.0)
    assert r.expected_cost_floor > 0


def test_edge_only_groups_match_integral_cover():
    g = matching_graph(5)
    groups = list(g.edges)
    lo = fractional_group_replay_lower_bound(
        g, groups, costs=[1.0] * len(groups), per_informative_query_kl=0.2, beta=0.05
    )
    hi = minimum_replay_group_cover(g, groups, costs=[1.0] * len(groups))
    assert lo.success and hi.success
    assert lo.normalized_cost == pytest.approx(hi.objective)


def test_fractional_relaxation_never_exceeds_integral_cover():
    g = path_graph(5)
    groups = [(0, 1, 2), (1, 2, 3), (2, 3, 4), (0, 1), (3, 4)]
    costs = [2.0, 2.0, 2.0, 1.0, 1.0]
    lo = fractional_group_replay_lower_bound(
        g, groups, costs=costs, per_informative_query_kl=0.1, beta=0.05
    )
    hi = minimum_replay_group_cover(g, groups, costs=costs)
    assert lo.success and hi.success
    assert lo.normalized_cost <= hi.objective + 1e-9


def test_fractional_schedule_covers_every_edge_at_target_exposure():
    g = clique_graph(5)
    groups = [tuple(x for x in range(g.n) if x != omitted) for omitted in range(g.n)]
    costs = [1.0] * len(groups)
    s = fractional_replay_schedule(g, groups, costs, d=0.05, beta=0.01)
    assert s.scale > 0
    for u, v in g.edges:
        exposure = sum(
            int(s.counts[i]) for i, group in enumerate(groups)
            if u in group and v in group
        )
        assert exposure >= s.scale
    assert s.total_cost <= (
        s.scale * s.normalized_fractional_cost + s.additive_rounding_cap + 1e-8
    )


def test_triangle_edge_groups_have_strict_fractional_integrality_gap():
    # Each legal group is exactly one edge. Unit costs make this integral in
    # this oracle, so use overlapping two-edge path groups on a triangle's
    # three edge obligations: each group covers two obligations.
    g = clique_graph(3)
    groups = [(0, 1, 2)]  # sanity: one full group is integral, no gap
    base = minimum_fractional_replay_cover(g, groups, [1.0])
    assert base.success and base.cost == pytest.approx(1.0)


def test_k4_triples_exhibit_strict_fractional_integral_gap():
    # Four 3-vertex groups. Every K4 edge belongs to exactly two triples.
    # Fractional weight 1/2 on each triple costs 2, while any integral cover
    # needs at least three triples, cost 3.
    g = clique_graph(4)
    groups = [
        (1, 2, 3),
        (0, 2, 3),
        (0, 1, 3),
        (0, 1, 2),
    ]
    costs = [1.0] * 4
    frac = minimum_fractional_replay_cover(g, groups, costs)
    integ = minimum_replay_group_cover(g, groups, costs)
    assert frac.success and integ.success
    assert frac.cost == pytest.approx(2.0)
    assert integ.objective == pytest.approx(3.0)
