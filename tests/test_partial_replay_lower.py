import numpy as np
import pytest

from tfoesuu.graphs import clique_graph, matching_graph, path_graph
from tfoesuu.partial_replay import minimum_replay_group_cover
from tfoesuu.partial_replay_lower import (
    fractional_group_replay_lower_bound,
    fractional_replay_schedule,
    minimum_fractional_replay_cover,
    raw_output_information_lower_bound,
)


def test_withdrawn_fractional_lower_bound_fails_closed():
    g = matching_graph(2)
    with pytest.raises(RuntimeError, match="withdrawn"):
        fractional_group_replay_lower_bound(
            g, list(g.edges), costs=[1.0] * len(g.edges),
            per_informative_query_kl=0.1, beta=0.05,
        )


def test_fractional_cover_is_only_a_scheduling_object():
    g = path_graph(5)
    groups = [(0, 1, 2), (1, 2, 3), (2, 3, 4), (0, 1), (3, 4)]
    costs = [2.0, 2.0, 2.0, 1.0, 1.0]
    frac = minimum_fractional_replay_cover(g, groups, costs)
    integ = minimum_replay_group_cover(g, groups, costs)
    assert frac.success and integ.success
    assert frac.cost <= integ.objective + 1e-9


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


def test_k4_triples_exhibit_strict_fractional_integral_gap():
    g = clique_graph(4)
    groups = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]
    costs = [1.0] * 4
    frac = minimum_fractional_replay_cover(g, groups, costs)
    integ = minimum_replay_group_cover(g, groups, costs)
    assert frac.success and integ.success
    assert frac.cost == pytest.approx(2.0)
    assert integ.objective == pytest.approx(3.0)


def _raw(g, groups, costs=None):
    if costs is None:
        costs = [1.0] * len(groups)
    return raw_output_information_lower_bound(
        g, groups, costs, p=0.2, shared_patch=0.1, d=0.05, beta=0.05
    )


def test_legal_synchronized_endpoint_group_has_positive_information():
    g = matching_graph(1)
    r = _raw(g, [(0, 1)])
    assert r.success
    # Alternative 0 changes endpoint 0.
    # Singleton groups are not legal in the frozen partial-replay oracle.
    # The joint legal group still carries positive information.
    assert r.information_matrix[0, 0] > 0.0


def test_every_informative_legal_group_has_the_same_kl():
    g = clique_graph(4)
    groups = [(0, 1), (0, 2, 3), (1, 2), (2, 3)]
    r = _raw(g, groups)
    assert r.success
    positive = r.information_matrix[r.information_matrix > 0.0]
    assert positive.size > 0
    assert np.allclose(positive, positive[0])


def test_unrelated_synchronized_reference_matches_partner_information():
    # In K3, alternative (0,1; changed=0) can be observed with either vertex 1
    # (the fairness partner) or vertex 2 (an unrelated synchronized reference).
    g = clique_graph(3)
    r = _raw(g, [(0, 1), (0, 2)])
    assert r.success
    alt = r.alternatives.index((0, 1, 0))
    assert r.information_matrix[0, alt] == pytest.approx(r.information_matrix[1, alt])
    assert r.information_matrix[0, alt] > 0.0


def test_missing_changed_endpoint_makes_oriented_alternative_unobservable():
    g = path_graph(3)
    r = _raw(g, [(0, 2)])
    assert not r.success
    assert np.isinf(r.expected_cost_floor)
    assert "zero information" in r.message


def test_raw_information_columns_collapse_by_changed_vertex():
    g = clique_graph(4)
    groups = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    r = _raw(g, groups)
    assert r.success
    for changed in range(g.n):
        cols = [
            i for i, (_, _, x) in enumerate(r.alternatives)
            if x == changed
        ]
        assert cols
        for i in cols[1:]:
            assert np.allclose(r.information_matrix[:, i], r.information_matrix[:, cols[0]])


def test_edge_rewiring_with_same_active_vertices_preserves_raw_information_floor():
    # Both graphs have the same active vertex set {0,1,2,3}.  Under the frozen
    # homogeneous raw-output family the lower LP depends on changed endpoints,
    # not on which incident fairness edge names an alternative.
    g_path = path_graph(4)
    g_match = matching_graph(2)
    groups = [(0, 1), (1, 2), (2, 3), (0, 3)]
    a = _raw(g_path, groups)
    b = _raw(g_match, groups)
    assert a.success and b.success
    assert a.expected_cost_floor == pytest.approx(b.expected_cost_floor)
