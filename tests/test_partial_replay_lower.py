import numpy as np
import pytest

from tfoesuu.graphs import clique_graph, matching_graph, path_graph
from tfoesuu.partial_replay import minimum_replay_group_cover
from tfoesuu.separations import binary_decision_kl
from tfoesuu.partial_replay_lower import (
    active_vertex_replay_schedule,
    group_patch_delta_heterogeneous,
    fractional_group_replay_lower_bound,
    fractional_replay_schedule,
    minimum_fractional_active_vertex_cover,
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


def test_active_vertex_cover_never_exceeds_edge_cover():
    g = clique_graph(4)
    groups = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]
    costs = [1.0] * 4
    vertex = minimum_fractional_active_vertex_cover(g, groups, costs)
    edge = minimum_fractional_replay_cover(g, groups, costs)
    assert vertex.success and edge.success
    assert vertex.cost == pytest.approx(4.0 / 3.0)
    assert edge.cost == pytest.approx(2.0)
    assert vertex.cost <= edge.cost


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
    assert "absent from every legal replay group" in r.message


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


def test_raw_information_floor_is_scaled_active_vertex_cover():
    g = clique_graph(4)
    groups = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]
    costs = [1.0] * 4
    cover = minimum_fractional_active_vertex_cover(g, groups, costs)
    raw = raw_output_information_lower_bound(
        g, groups, costs, p=0.2, shared_patch=0.1, d=0.05, beta=0.05
    )
    assert cover.success and raw.success
    k_sync = raw.information_matrix[raw.information_matrix > 0.0][0]
    scale = binary_decision_kl(0.05) / k_sync
    assert raw.expected_cost_floor == pytest.approx(scale * cover.cost)
    assert np.allclose(raw.expected_query_counts, scale * cover.weights)


def test_active_vertex_schedule_covers_every_changed_endpoint():
    g = clique_graph(4)
    groups = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]
    costs = [1.0] * 4
    s = active_vertex_replay_schedule(g, groups, costs, d=0.05, beta=0.01)
    assert s.normalized_fractional_cost == pytest.approx(4.0 / 3.0)
    assert s.scale > 0
    for x in range(g.n):
        exposure = sum(
            int(s.counts[i]) for i, group in enumerate(groups) if x in group
        )
        assert exposure >= s.scale
    assert s.total_cost <= (
        s.scale * s.normalized_fractional_cost + s.additive_rounding_cap + 1e-8
    )


def test_group_delta_heterogeneity_is_pathwise_zero_under_homogeneous_null():
    # Shared tape positions represented by the possible old/new threshold regions.
    null_states = [
        ([1, 1, 1], [1, 1, 1]),
        ([0, 0, 0], [1, 1, 1]),
        ([0, 0, 0], [0, 0, 0]),
    ]
    for old, new in null_states:
        assert not group_patch_delta_heterogeneous(old, new)


def test_group_delta_heterogeneity_detects_changed_endpoint_without_partner():
    # Vertices 0 and 1 may be a fairness edge, but group (0,2) is sufficient:
    # on U in (p+s,p+s+d], only changed endpoint 0 flips in P1.
    assert group_patch_delta_heterogeneous([0, 0], [1, 0])
    assert group_patch_delta_heterogeneous([0, 0, 0], [0, 1, 0])


def test_group_delta_heterogeneity_ignores_uniform_patch_motion():
    assert not group_patch_delta_heterogeneous([0, 0], [1, 1])
    assert not group_patch_delta_heterogeneous([1, 1], [1, 1])


def test_active_vertex_schedule_beats_edge_witness_schedule_on_k4_triples():
    g = clique_graph(4)
    groups = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]
    costs = [1.0] * 4
    raw = active_vertex_replay_schedule(g, groups, costs, d=0.02, beta=0.05)
    edge = fractional_replay_schedule(g, groups, costs, d=0.02, beta=0.05)
    assert raw.normalized_fractional_cost == pytest.approx(4.0 / 3.0)
    assert edge.normalized_fractional_cost == pytest.approx(2.0)
    assert raw.normalized_fractional_cost < edge.normalized_fractional_cost
