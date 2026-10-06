import numpy as np
import pytest

from tfoesuu.graphs import clique_graph, matching_graph, path_graph
from tfoesuu.partial_replay import minimum_replay_group_cover
from tfoesuu.separations import binary_decision_kl
from tfoesuu.partial_replay_lower import (
    active_vertex_contrast_schedule,
    fractional_group_replay_lower_bound,
    fractional_replay_schedule,
    minimum_fractional_active_vertex_cover,
    minimum_fractional_replay_cover,
    raw_group_contrast_witness,
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


def test_group_coherent_matching_has_equal_vertex_and_edge_geometries():
    g = matching_graph(2)
    groups = [(0, 1), (2, 3)]
    costs = [1.0, 1.0]
    vertex = minimum_fractional_active_vertex_cover(g, groups, costs)
    edge = minimum_fractional_replay_cover(g, groups, costs)
    assert vertex.success and edge.success
    assert vertex.cost == pytest.approx(2.0)
    assert edge.cost == pytest.approx(2.0)


@pytest.mark.parametrize("n", range(3, 9))
def test_complete_graph_pair_groups_have_linear_geometry_gap(n):
    g = clique_graph(n)
    groups = list(g.edges)
    costs = [1.0] * len(groups)
    vertex = minimum_fractional_active_vertex_cover(g, groups, costs)
    edge = minimum_fractional_replay_cover(g, groups, costs)
    assert vertex.success and edge.success
    assert vertex.cost == pytest.approx(n / 2.0)
    assert edge.cost == pytest.approx(n * (n - 1) / 2.0)
    assert edge.cost / vertex.cost == pytest.approx(n - 1.0)


def test_raw_information_can_be_finite_when_witness_geometry_is_infeasible():
    g = path_graph(3)
    groups = [(0, 2), (1, 2)]
    costs = [1.0, 1.0]
    vertex = minimum_fractional_active_vertex_cover(g, groups, costs)
    edge = minimum_fractional_replay_cover(g, groups, costs)
    raw = _raw(g, groups, costs)
    assert vertex.success
    assert vertex.cost == pytest.approx(2.0)
    assert not edge.success
    assert np.isinf(edge.cost)
    assert raw.success
    assert np.isfinite(raw.expected_cost_floor)



def test_active_vertex_contrast_schedule_covers_every_active_vertex():
    g = clique_graph(5)
    groups = list(g.edges)
    costs = [1.0] * len(groups)
    s = active_vertex_contrast_schedule(g, groups, costs, d=0.05, beta=0.01)
    assert s.normalized_fractional_cost == pytest.approx(2.5)
    assert s.scale > 0
    for x in s.active_vertices:
        exposure = sum(
            int(s.counts[i]) for i, group in enumerate(groups) if x in group
        )
        assert exposure >= s.scale
    assert s.total_cost <= (
        s.scale * s.normalized_fractional_cost + s.additive_rounding_cap + 1e-8
    )


def test_active_vertex_contrast_schedule_works_without_joint_edge_replay():
    g = path_graph(3)
    groups = [(0, 2), (1, 2)]
    costs = [1.0, 1.0]

    edge = minimum_fractional_replay_cover(g, groups, costs)
    assert not edge.success

    s = active_vertex_contrast_schedule(g, groups, costs, d=0.05, beta=0.05)
    assert s.normalized_fractional_cost == pytest.approx(2.0)
    assert tuple(s.active_vertices) == (0, 1, 2)
    assert np.all(s.counts >= s.scale)
    assert s.total_cost == pytest.approx(2.0 * s.scale)


def test_active_vertex_contrast_schedule_rejects_unobservable_active_vertex():
    g = path_graph(3)
    with pytest.raises(ValueError, match="absent from every legal replay group"):
        active_vertex_contrast_schedule(
            g, [(0, 2)], [1.0], d=0.05, beta=0.05
        )



def test_raw_group_contrast_witness_matches_frozen_threshold_intervals():
    p, s, d = 0.20, 0.10, 0.05

    def bit(threshold, u):
        return int(u <= threshold)

    # Two synchronized vertices. Vertex 0 is the uniquely changed endpoint.
    for u in (0.10, 0.25, 0.325, 0.50):
        old = [bit(p, u), bit(p, u)]
        null_new = [bit(p + s, u), bit(p + s, u)]
        alt_new = [bit(p + s + d, u), bit(p + s, u)]

        assert not raw_group_contrast_witness(old, null_new)
        assert raw_group_contrast_witness(old, alt_new) == (p + s < u <= p + s + d)


def test_raw_group_contrast_witness_uses_unrelated_reference():
    # This is the path-3 structural case: group {0,2} does not contain fairness
    # edge {0,1}, yet vertex 2 is a valid synchronized control in the frozen
    # homogeneous single-changed-endpoint family.
    p, s, d = 0.20, 0.10, 0.05
    u = 0.325

    def bit(threshold):
        return int(u <= threshold)

    old = [bit(p), bit(p)]
    new = [bit(p + s + d), bit(p + s)]
    assert raw_group_contrast_witness(old, new)


def test_raw_group_contrast_witness_validates_group_shape():
    with pytest.raises(ValueError, match="at least two"):
        raw_group_contrast_witness([0], [1])
    with pytest.raises(ValueError, match="equal-length vectors"):
        raw_group_contrast_witness([0, 0], [1])


def test_raw_lower_and_contrast_upper_share_active_vertex_geometry():
    g = clique_graph(4)
    groups = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]
    costs = [1.0] * len(groups)
    cover = minimum_fractional_active_vertex_cover(g, groups, costs)
    raw = _raw(g, groups, costs)
    schedule = active_vertex_contrast_schedule(
        g, groups, costs, d=0.05, beta=0.05
    )
    assert cover.success and raw.success
    assert cover.cost == pytest.approx(4.0 / 3.0)
    assert schedule.normalized_fractional_cost == pytest.approx(cover.cost)
    positive_kl = raw.information_matrix[raw.information_matrix > 0.0][0]
    lower_scale = binary_decision_kl(0.05) / positive_kl
    assert raw.expected_cost_floor == pytest.approx(lower_scale * cover.cost)


def test_raw_contrast_is_not_valid_for_heterogeneous_composite_null():
    """Scope guard: heterogeneous fair nulls can trigger the raw contrast.

    Both new-version Bernoulli means are within tau=0.20 of one another, so the
    state is fairness-preserving for the single edge.  Nevertheless unequal
    old-to-new patch shifts make the synchronized delta vector nonconstant on a
    positive-measure tape interval.  This is a constructive false-positive
    witness against extending P17-A beyond its frozen homogeneous null.
    """
    tau = 0.20
    old_thresholds = (0.20, 0.40)
    new_thresholds = (0.30, 0.45)
    assert abs(new_thresholds[0] - new_thresholds[1]) <= tau

    u = 0.25
    old = [int(u <= t) for t in old_thresholds]
    new = [int(u <= t) for t in new_thresholds]
    assert raw_group_contrast_witness(old, new)



def test_group_coherent_heterogeneous_components_support_raw_contrast():
    """A heterogeneous null can be valid when each legal group is coherent."""
    g = matching_graph(2)
    groups = [(0, 1), (2, 3)]
    costs = [1.0, 1.0]
    schedule = active_vertex_contrast_schedule(
        g, groups, costs, d=0.05, beta=0.05
    )
    assert schedule.normalized_fractional_cost == pytest.approx(2.0)

    # Replay component A has patch interval (0.20, 0.30]; component B has
    # a different null patch interval (0.40, 0.45].  The null is globally
    # heterogeneous but pathwise coherent inside each legal group.
    for u in (0.10, 0.25, 0.425, 0.50):
        old_a = [int(u <= 0.20), int(u <= 0.20)]
        new_a = [int(u <= 0.30), int(u <= 0.30)]
        old_b = [int(u <= 0.40), int(u <= 0.40)]
        new_b = [int(u <= 0.45), int(u <= 0.45)]
        assert not raw_group_contrast_witness(old_a, new_a)
        assert not raw_group_contrast_witness(old_b, new_b)

    # A single changed endpoint in component A extends only vertex 0 by d=0.05.
    u = 0.325
    old = [int(u <= 0.20), int(u <= 0.20)]
    alt_new = [int(u <= 0.35), int(u <= 0.30)]
    assert raw_group_contrast_witness(old, alt_new)

    # The unrelated replay component remains contrast-free at the same tape.
    old_b = [int(u <= 0.40), int(u <= 0.40)]
    new_b = [int(u <= 0.45), int(u <= 0.45)]
    assert not raw_group_contrast_witness(old_b, new_b)
