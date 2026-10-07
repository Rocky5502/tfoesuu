import pytest

from tfoesuu.control_replay import (
    control_replay_information_lower_bound,
    matched_control_contrast_witness,
    matched_control_replay_schedule,
    minimum_fractional_control_cover,
)
from tfoesuu.graphs import complete_bipartite_graph, path_graph
from tfoesuu.separations import (
    edge_coupled_common_patch_kl,
    threshold_fairness_replay_kl,
)


def _family():
    graph = complete_bipartite_graph(3, 2)
    high = (0, 1, 2)
    return graph, high


def test_control_cover_uses_same_background_high_vertices():
    graph, high = _family()
    groups = [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3), (2, 3)]
    costs = [1.0] * len(groups)

    cover = minimum_fractional_control_cover(graph, groups, costs, high)

    assert cover.success
    assert cover.cost == pytest.approx(1.5)
    # The three high-high pair groups fractionally cover the three candidates.
    assert sum(cover.weights[:3]) == pytest.approx(1.5)
    assert sum(cover.weights[3:]) == pytest.approx(0.0)


def test_exact_mixed_information_matrix_matches_p15_and_p18_kl():
    graph, high = _family()
    groups = [(0, 1), (0, 3)]
    costs = [1.0, 1.0]
    p, s, tau, d = 0.20, 0.10, 0.10, 0.01

    lower = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=p,
        shared_patch=s,
        fairness_tolerance=tau,
        d=d,
        beta=0.05,
    )

    assert not lower.success  # candidates 1 and 2 are unobservable in this tiny fixture
    assert lower.control_kl == pytest.approx(
        edge_coupled_common_patch_kl(p, s + tau, d)
    )
    assert lower.boundary_kl == pytest.approx(
        threshold_fairness_replay_kl(p, s, tau, d)
    )
    # Candidate 0 sees linear-KL information from the high-high control group
    # and quadratic boundary information from the high-low group.
    assert lower.information_matrix[0, 0] == pytest.approx(lower.control_kl)
    assert lower.information_matrix[1, 0] == pytest.approx(lower.boundary_kl)


def test_matched_controls_restore_linear_small_d_information():
    graph, high = _family()
    groups = [(0, 1), (1, 2), (0, 2)]
    costs = [1.0] * len(groups)

    a = control_replay_information_lower_bound(
        graph, groups, costs, high,
        p=0.20, shared_patch=0.10, fairness_tolerance=0.10,
        d=1e-4, beta=0.05,
    )
    b = control_replay_information_lower_bound(
        graph, groups, costs, high,
        p=0.20, shared_patch=0.10, fairness_tolerance=0.10,
        d=5e-5, beta=0.05,
    )

    assert a.success and b.success
    assert b.expected_cost_floor / a.expected_cost_floor == pytest.approx(
        2.0, rel=5e-4
    )


def test_without_matched_controls_fixed_tolerance_is_quadratic():
    graph, high = _family()
    groups = [(0, 3), (1, 3), (2, 3)]
    costs = [1.0] * len(groups)

    cover = minimum_fractional_control_cover(graph, groups, costs, high)
    assert not cover.success

    a = control_replay_information_lower_bound(
        graph, groups, costs, high,
        p=0.20, shared_patch=0.10, fairness_tolerance=0.10,
        d=1e-4, beta=0.05,
    )
    b = control_replay_information_lower_bound(
        graph, groups, costs, high,
        p=0.20, shared_patch=0.10, fairness_tolerance=0.10,
        d=5e-5, beta=0.05,
    )

    assert a.success and b.success
    assert b.expected_cost_floor / a.expected_cost_floor == pytest.approx(
        4.0, rel=2e-3
    )


def test_control_schedule_covers_every_high_candidate():
    graph, high = _family()
    groups = [(0, 1), (1, 2), (0, 2)]
    costs = [1.0] * len(groups)

    schedule = matched_control_replay_schedule(
        graph, groups, costs, high, d=0.05, beta=0.01
    )

    assert schedule.normalized_control_cover_cost == pytest.approx(1.5)
    for x in high:
        exposure = sum(
            int(schedule.counts[i])
            for i, group in enumerate(groups)
            if x in group and len(set(group).intersection(high)) >= 2
        )
        assert exposure >= schedule.scale
    assert schedule.total_cost <= (
        schedule.scale * schedule.normalized_control_cover_cost
        + schedule.additive_rounding_cap
        + 1e-8
    )


def test_matched_control_statistic_ignores_cross_class_benign_disparity():
    p, s, tau, d = 0.20, 0.10, 0.10, 0.05

    def bit(threshold, u):
        return int(u <= threshold)

    # Group = two high controls plus one low vertex.
    high_mask = [True, True, False]

    # During the benign tau interval the high class differs from the low class,
    # but the two high patch deltas remain identical, so the control statistic
    # does not false-positive.
    u = 0.35
    old = [bit(p, u)] * 3
    null_new = [
        bit(p + s + tau, u),
        bit(p + s + tau, u),
        bit(p + s, u),
    ]
    assert not matched_control_contrast_witness(old, null_new, high_mask)

    # The extra d interval at candidate 0 breaks only the matched high pair.
    u = 0.425
    old = [bit(p, u)] * 3
    alt_new = [
        bit(p + s + tau + d, u),
        bit(p + s + tau, u),
        bit(p + s, u),
    ]
    assert matched_control_contrast_witness(old, alt_new, high_mask)


def test_control_family_rejects_non_bipartite_fairness_edges():
    graph = path_graph(3)
    # Edge (0,1) is high-high under this assignment, violating P19 scope.
    with pytest.raises(ValueError, match="bipartite fairness graph"):
        minimum_fractional_control_cover(
            graph,
            groups=[(0, 1), (1, 2)],
            costs=[1.0, 1.0],
            high_vertices=(0, 1),
        )


def _shared_tape_transcript_distribution(old_thresholds, new_thresholds):
    cuts = sorted({0.0, 1.0, *old_thresholds, *new_thresholds})
    mass = {}
    for left, right in zip(cuts, cuts[1:]):
        if right <= left:
            continue
        u = (left + right) / 2.0
        state = tuple(
            [int(u <= t) for t in old_thresholds]
            + [int(u <= t) for t in new_thresholds]
        )
        mass[state] = mass.get(state, 0.0) + (right - left)
    return mass


def _categorical_kl(q0, q1):
    import math

    out = 0.0
    for state, p0 in q0.items():
        if p0 == 0.0:
            continue
        p1 = q1.get(state, 0.0)
        assert p1 > 0.0
        out += p0 * math.log(p0 / p1)
    return out


def test_exact_shared_tape_partition_recovers_control_and_boundary_kl():
    p, s, tau, d = 0.20, 0.10, 0.10, 0.01

    # x + matched high control + low vertex.
    old = [p, p, p]
    null_new = [p + s + tau, p + s + tau, p + s]
    alt_new = [p + s + tau + d, p + s + tau, p + s]
    q0 = _shared_tape_transcript_distribution(old, null_new)
    q1 = _shared_tape_transcript_distribution(old, alt_new)
    exact_control = _categorical_kl(q0, q1)

    # x + low reference only.
    old_boundary = [p, p]
    null_boundary = [p + s + tau, p + s]
    alt_boundary = [p + s + tau + d, p + s]
    b0 = _shared_tape_transcript_distribution(old_boundary, null_boundary)
    b1 = _shared_tape_transcript_distribution(old_boundary, alt_boundary)
    exact_boundary = _categorical_kl(b0, b1)

    lower = control_replay_information_lower_bound(
        complete_bipartite_graph(2, 1),
        groups=[(0, 1), (0, 2), (1, 2)],
        costs=[1.0, 1.0, 1.0],
        high_vertices=(0, 1),
        p=p,
        shared_patch=s,
        fairness_tolerance=tau,
        d=d,
        beta=0.05,
    )
    assert lower.success
    assert exact_control == pytest.approx(lower.control_kl)
    assert exact_boundary == pytest.approx(lower.boundary_kl)
    assert exact_control > exact_boundary
