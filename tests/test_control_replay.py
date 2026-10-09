import math
from itertools import pairwise

import numpy as np
import pytest

from tfoesuu.control_replay import (
    boundary_familywise_fixed_design_lower_bound,
    boundary_familywise_sequential_bounds,
    boundary_familywise_truncated_sequential_bounds,
    control_replay_information_lower_bound,
    matched_control_contrast_witness,
    matched_control_replay_schedule,
    minimum_fractional_control_cover,
    mixed_control_asymptotic_coefficients,
    mixed_control_leading_coefficient,
    mixed_control_replay_schedule,
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
    assert lower.control_kl == pytest.approx(edge_coupled_common_patch_kl(p, s + tau, d))
    assert lower.boundary_kl == pytest.approx(threshold_fairness_replay_kl(p, s, tau, d))
    # Candidate 0 sees linear-KL information from the high-high control group
    # and quadratic boundary information from the high-low group.
    assert lower.information_matrix[0, 0] == pytest.approx(lower.control_kl)
    assert lower.information_matrix[1, 0] == pytest.approx(lower.boundary_kl)


def test_matched_controls_restore_linear_small_d_information():
    graph, high = _family()
    groups = [(0, 1), (1, 2), (0, 2)]
    costs = [1.0] * len(groups)

    a = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=1e-4,
        beta=0.05,
    )
    b = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=5e-5,
        beta=0.05,
    )

    assert a.success and b.success
    assert b.expected_cost_floor / a.expected_cost_floor == pytest.approx(2.0, rel=5e-4)


def test_without_matched_controls_fixed_tolerance_is_quadratic():
    graph, high = _family()
    groups = [(0, 3), (1, 3), (2, 3)]
    costs = [1.0] * len(groups)

    cover = minimum_fractional_control_cover(graph, groups, costs, high)
    assert not cover.success

    a = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=1e-4,
        beta=0.05,
    )
    b = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=5e-5,
        beta=0.05,
    )

    assert a.success and b.success
    assert b.expected_cost_floor / a.expected_cost_floor == pytest.approx(4.0, rel=2e-3)


def test_control_schedule_covers_every_high_candidate():
    graph, high = _family()
    groups = [(0, 1), (1, 2), (0, 2)]
    costs = [1.0] * len(groups)

    schedule = matched_control_replay_schedule(graph, groups, costs, high, d=0.05, beta=0.01)

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


def test_matched_control_statistic_is_not_valid_for_arbitrary_composite_null():
    p = 0.20

    def bit(threshold, u):
        return int(u <= threshold)

    # Both high--low gaps are null-valid at tolerance 0.10, but the high
    # thresholds are not pathwise exchangeable. A matched-high contrast can
    # therefore fire under this broader composite null. P19 excludes it.
    u = 0.395
    old = [bit(p, u)] * 3
    composite_null_new = [bit(0.40, u), bit(0.39, u), bit(0.30, u)]
    assert matched_control_contrast_witness(
        old,
        composite_null_new,
        high_mask=[True, True, False],
    )


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
    for left, right in pairwise(cuts):
        if right <= left:
            continue
        u = (left + right) / 2.0
        state = tuple([int(u <= t) for t in old_thresholds] + [int(u <= t) for t in new_thresholds])
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


def test_mixed_control_topology_is_quadratic_when_one_candidate_lacks_control():
    graph = complete_bipartite_graph(3, 2)
    high = (0, 1, 2)
    # Candidates 0 and 1 share a first-order matched-control channel; candidate
    # 2 is observable only through a high-low boundary group.  The total exact
    # information floor must therefore retain the d^-2 leading regime.
    groups = ((0, 1), (2, 3))
    costs = (1.0, 1.0)

    a = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=1e-4,
        beta=0.05,
    )
    b = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=5e-5,
        beta=0.05,
    )

    assert a.success and b.success
    assert b.expected_cost_floor / a.expected_cost_floor == pytest.approx(4.0, rel=3e-3)


def test_all_candidates_control_covered_recover_linear_leading_regime():
    graph = complete_bipartite_graph(3, 2)
    high = (0, 1, 2)
    groups = ((0, 1), (1, 2), (0, 2), (0, 3), (1, 3), (2, 4))
    costs = (1.0,) * len(groups)

    a = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=1e-4,
        beta=0.05,
    )
    b = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=5e-5,
        beta=0.05,
    )

    assert a.success and b.success
    assert b.expected_cost_floor / a.expected_cost_floor == pytest.approx(2.0, rel=3e-3)


def test_mixed_information_lp_prefers_first_order_controls_for_small_d():
    graph, high = _family()
    groups = [
        (0, 1),
        (1, 2),
        (0, 2),  # matched high controls
        (0, 3),
        (1, 3),
        (2, 3),  # cheaper boundary-only references
    ]
    costs = [1.0, 1.0, 1.0, 0.1, 0.1, 0.1]

    floors = []
    solutions = []
    for d in (1e-4, 5e-5):
        lower = control_replay_information_lower_bound(
            graph,
            groups,
            costs,
            high,
            p=0.20,
            shared_patch=0.10,
            fairness_tolerance=0.10,
            d=d,
            beta=0.05,
        )
        assert lower.success
        floors.append(lower.expected_cost_floor)
        solutions.append(lower.expected_query_counts)

    # Despite their lower declared price, boundary-only queries carry only
    # second-order information.  At sufficiently small d, the exact LP places
    # all mass on the first-order matched-control channel.
    for q in solutions:
        assert np.allclose(q[3:], 0.0, atol=1e-8)
        assert np.all(q[:3] > 0.0)

    assert floors[1] / floors[0] == pytest.approx(2.0, rel=5e-4)


def test_mixed_control_leading_coefficient_matches_exact_quadratic_limit():
    graph = complete_bipartite_graph(3, 2)
    high = (0, 1, 2)
    groups = ((0, 1), (2, 3))
    costs = (1.0, 1.0)

    lead = mixed_control_leading_coefficient(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        beta=0.05,
    )
    assert lead.success
    assert lead.uncovered_high_vertices == (2,)
    assert lead.coefficient > 0.0

    errors = []
    for d in (2e-4, 1e-4, 5e-5):
        exact = control_replay_information_lower_bound(
            graph,
            groups,
            costs,
            high,
            p=0.20,
            shared_patch=0.10,
            fairness_tolerance=0.10,
            d=d,
            beta=0.05,
        )
        assert exact.success
        scaled = d * d * exact.expected_cost_floor
        errors.append(abs(scaled - lead.coefficient))

    assert errors[2] < errors[1] < errors[0]
    assert errors[2] / lead.coefficient < 2e-3


def test_mixed_control_leading_coefficient_vanishes_under_complete_control_cover():
    graph = complete_bipartite_graph(3, 2)
    high = (0, 1, 2)
    groups = ((0, 1), (1, 2), (0, 2), (0, 3))
    costs = (1.0,) * len(groups)

    lead = mixed_control_leading_coefficient(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        beta=0.05,
    )
    assert lead.success
    assert lead.coefficient == pytest.approx(0.0)
    assert lead.uncovered_high_vertices == ()


@pytest.mark.parametrize(
    ("p", "shared_patch", "tolerance"),
    [
        (0.20, 0.10, 0.10),  # negative boundary cubic coefficient
        (0.20, 0.10, 0.35),  # zero boundary cubic coefficient
        (0.20, 0.10, 0.45),  # positive boundary cubic coefficient
    ],
)
def test_mixed_control_two_term_coefficients_match_exact_lp(p, shared_patch, tolerance):
    graph = complete_bipartite_graph(3, 2)
    high = (0, 1, 2)
    # One control group covers candidates 0 and 1 at declared cost 2.
    # Candidate 2 has two boundary-only choices and uses the cheaper cost 1.
    groups = ((0, 1), (2, 3), (2, 4))
    costs = (2.0, 3.0, 1.0)
    coeff = mixed_control_asymptotic_coefficients(
        graph,
        groups,
        costs,
        high,
        p=p,
        shared_patch=shared_patch,
        fairness_tolerance=tolerance,
        beta=0.05,
    )

    assert coeff.success
    assert coeff.uncovered_high_vertices == (2,)
    assert coeff.covered_high_vertices == (0, 1)
    assert coeff.boundary_minimum_cost == pytest.approx(1.0)
    assert coeff.residual_control_cover_cost == pytest.approx(2.0)
    leading = mixed_control_leading_coefficient(
        graph,
        groups,
        costs,
        high,
        p=p,
        shared_patch=shared_patch,
        fairness_tolerance=tolerance,
        beta=0.05,
    )
    assert leading.success
    assert coeff.inverse_square_coefficient == pytest.approx(leading.coefficient)

    residual_errors = []
    for d in (4e-4, 2e-4, 1e-4):
        exact = control_replay_information_lower_bound(
            graph,
            groups,
            costs,
            high,
            p=p,
            shared_patch=shared_patch,
            fairness_tolerance=tolerance,
            d=d,
            beta=0.05,
        )
        assert exact.success
        scaled_residual = d * (
            exact.expected_cost_floor - coeff.inverse_square_coefficient / (d * d)
        )
        residual_errors.append(abs(scaled_residual - coeff.inverse_linear_coefficient))

    assert residual_errors[2] < residual_errors[1] < residual_errors[0]
    assert residual_errors[2] < 0.01


def test_mixed_control_two_term_coefficients_cover_extreme_topologies():
    graph, high = _family()

    all_control = mixed_control_asymptotic_coefficients(
        graph,
        groups=((0, 1), (1, 2), (0, 2)),
        costs=(1.0, 1.0, 1.0),
        high_vertices=high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        beta=0.05,
    )
    assert all_control.success
    assert all_control.inverse_square_coefficient == pytest.approx(0.0)
    assert all_control.residual_control_cover_cost == pytest.approx(1.5)

    all_boundary = mixed_control_asymptotic_coefficients(
        graph,
        groups=((0, 3), (1, 3), (2, 4)),
        costs=(1.0, 2.0, 3.0),
        high_vertices=high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        beta=0.05,
    )
    assert all_boundary.success
    assert all_boundary.uncovered_high_vertices == high
    assert all_boundary.boundary_minimum_cost == pytest.approx(6.0)
    assert all_boundary.residual_control_cover_cost == pytest.approx(0.0)


def test_mixed_control_two_term_residual_with_two_unmatched_candidates():
    graph = complete_bipartite_graph(4, 2)
    high = (0, 1, 2, 3)
    groups = ((0, 1), (2, 4), (3, 5))
    costs = (2.0, 1.25, 0.75)
    coeff = mixed_control_asymptotic_coefficients(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        beta=0.05,
    )
    leading = mixed_control_leading_coefficient(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        beta=0.05,
    )

    assert coeff.success and leading.success
    assert coeff.uncovered_high_vertices == (2, 3)
    assert coeff.boundary_minimum_cost == pytest.approx(2.0)
    assert coeff.inverse_square_coefficient == pytest.approx(leading.coefficient)

    residual_errors = []
    for d in (4e-4, 2e-4, 1e-4):
        exact = control_replay_information_lower_bound(
            graph,
            groups,
            costs,
            high,
            p=0.20,
            shared_patch=0.10,
            fairness_tolerance=0.10,
            d=d,
            beta=0.05,
        )
        assert exact.success
        scaled_residual = d * (
            exact.expected_cost_floor - coeff.inverse_square_coefficient / (d * d)
        )
        residual_errors.append(abs(scaled_residual - coeff.inverse_linear_coefficient))

    assert residual_errors[2] < residual_errors[1] < residual_errors[0]
    assert residual_errors[2] < 0.01


def test_mixed_control_hybrid_schedule_combines_boundary_and_control_blocks():
    graph = complete_bipartite_graph(3, 2)
    high = (0, 1, 2)
    groups = ((0, 1), (2, 3), (2, 4))
    costs = (2.0, 1.0, 0.5)
    d = 0.01
    beta = 0.05

    schedule = mixed_control_replay_schedule(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=d,
        beta=beta,
    )

    expected_boundary = math.ceil(8.0 * 0.11 * math.log(1.0 / beta) / (d * d))
    expected_control = math.ceil(math.log(beta) / math.log1p(-d))
    assert schedule.uncovered_high_vertices == (2,)
    assert schedule.covered_high_vertices == (0, 1)
    assert schedule.boundary_group_indices == (2,)
    assert schedule.boundary_rounds_per_candidate == expected_boundary
    assert schedule.boundary_error_budget_per_candidate == pytest.approx(beta)
    assert schedule.boundary_minimum_cost == pytest.approx(0.5)
    assert schedule.residual_control_cover_cost == pytest.approx(2.0)
    assert schedule.control_scale == expected_control
    assert tuple(schedule.counts) == (expected_control, 0, expected_boundary)
    assert schedule.total_cost == pytest.approx(
        2.0 * expected_control + 0.5 * expected_boundary
    )


def test_mixed_control_hybrid_schedule_splits_familywise_boundary_error():
    graph, high = _family()
    groups = ((0, 3), (1, 3), (2, 4))
    costs = (1.0, 2.0, 3.0)
    d = 0.01
    beta = 0.03

    schedule = mixed_control_replay_schedule(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=d,
        beta=beta,
    )

    expected_rounds = math.ceil(8.0 * 0.11 * math.log(3.0 / beta) / (d * d))
    assert schedule.uncovered_high_vertices == high
    assert schedule.covered_high_vertices == ()
    assert schedule.boundary_group_indices == (0, 1, 2)
    assert schedule.boundary_error_budget_per_candidate == pytest.approx(beta / 3.0)
    assert schedule.boundary_rounds_per_candidate == expected_rounds
    assert tuple(schedule.counts) == (expected_rounds,) * 3
    assert schedule.residual_control_cover_cost == pytest.approx(0.0)
    assert schedule.control_scale == 0


def test_boundary_familywise_fixed_design_uses_exact_transcript_chi_square():
    p, s, tau, d, beta = 0.20, 0.10, 0.10, 0.01, 0.05
    old = (p, p)
    null_new = (p + s + tau, p + s)
    alt_new = (p + s + tau + d, p + s)
    q0 = _shared_tape_transcript_distribution(old, null_new)
    q1 = _shared_tape_transcript_distribution(old, alt_new)
    chi_square = sum(q1[state] ** 2 / q0[state] for state in q0) - 1.0

    bound = boundary_familywise_fixed_design_lower_bound(
        8,
        p=p,
        shared_patch=s,
        fairness_tolerance=tau,
        d=d,
        beta=beta,
    )

    remainder = 1.0 - p - s - tau
    assert chi_square == pytest.approx(d * d * (1.0 / tau + 1.0 / remainder))
    assert math.expm1(bound.transcript_renyi2) == pytest.approx(chi_square)


def test_boundary_familywise_fixed_design_has_rankwise_logarithmic_floors():
    candidates, beta = 8, 0.05
    bound = boundary_familywise_fixed_design_lower_bound(
        candidates,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=0.01,
        beta=beta,
        unit_cost=2.5,
    )
    decision_chi_square = (1.0 - 2.0 * beta) ** 2 / (beta * (1.0 - beta))
    expected = np.log1p(decision_chi_square * np.arange(1, candidates + 1))
    expected /= bound.transcript_renyi2

    assert np.all(np.diff(bound.sorted_query_count_floors) > 0.0)
    assert bound.sorted_query_count_floors == pytest.approx(expected)
    assert bound.total_query_floor == pytest.approx(expected.sum())
    assert bound.total_cost_floor == pytest.approx(2.5 * expected.sum())


def test_boundary_familywise_fixed_design_is_quadratic_in_small_gap():
    common = {
        "candidates": 8,
        "p": 0.20,
        "shared_patch": 0.10,
        "fairness_tolerance": 0.10,
        "beta": 0.05,
    }
    coarse = boundary_familywise_fixed_design_lower_bound(d=2e-4, **common)
    fine = boundary_familywise_fixed_design_lower_bound(d=1e-4, **common)

    assert fine.total_query_floor / coarse.total_query_floor == pytest.approx(4.0, rel=2e-3)


def test_boundary_familywise_sequential_bounds_match_exact_kl_and_costs():
    costs = np.array([1.0, 2.0, 3.0])
    p, s, tau, d, beta = 0.20, 0.10, 0.10, 0.01, 0.05
    bound = boundary_familywise_sequential_bounds(
        costs,
        p=p,
        shared_patch=s,
        fairness_tolerance=tau,
        d=d,
        beta=beta,
    )

    assert bound.upper_likelihood_threshold == pytest.approx(len(costs) / beta)
    assert bound.lower_likelihood_threshold == pytest.approx(beta)
    assert bound.null_to_alternative_kl == pytest.approx(
        threshold_fairness_replay_kl(p, s, tau, d)
    )
    assert bound.null_expected_total_cost_upper == pytest.approx(
        bound.null_expected_rounds_per_candidate_upper * costs.sum()
    )
    expected_alternative = (
        bound.null_expected_rounds_per_candidate_upper * (costs.sum() - costs)
        + bound.changed_expected_rounds_upper * costs
    )
    assert bound.alternative_expected_cost_upper == pytest.approx(expected_alternative)


def test_boundary_sequential_null_arm_bound_avoids_candidate_log_factor():
    common = {
        "p": 0.20,
        "shared_patch": 0.10,
        "fairness_tolerance": 0.10,
        "d": 0.01,
        "beta": 0.05,
    }
    one = boundary_familywise_sequential_bounds([1.0], **common)
    many = boundary_familywise_sequential_bounds([1.0] * 20, **common)

    assert many.null_expected_rounds_per_candidate_upper == pytest.approx(
        one.null_expected_rounds_per_candidate_upper
    )
    assert many.changed_expected_rounds_upper > one.changed_expected_rounds_upper


def test_boundary_sequential_reports_exact_null_information_lower_bound():
    costs = np.array([1.0, 2.0, 3.0])
    beta = 0.05
    bound = boundary_familywise_sequential_bounds(
        costs,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=0.01,
        beta=beta,
    )
    decision_kl = (1.0 - 2.0 * beta) * math.log((1.0 - beta) / beta)

    assert bound.null_expected_total_cost_lower == pytest.approx(
        decision_kl * costs.sum() / bound.null_to_alternative_kl
    )
    assert bound.null_expected_total_cost_upper > bound.null_expected_total_cost_lower


def test_boundary_sequential_small_gap_constant_ratio_is_confidence_only():
    beta = 0.05
    bound = boundary_familywise_sequential_bounds(
        [1.0, 7.0, 19.0],
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=1e-5,
        beta=beta,
    )
    decision_kl = (1.0 - 2.0 * beta) * math.log((1.0 - beta) / beta)
    expected_ratio = math.log(1.0 / beta) / decision_kl

    assert bound.small_gap_upper_cost_coefficient / bound.small_gap_lower_cost_coefficient == (
        pytest.approx(expected_ratio)
    )
    assert bound.asymptotic_confidence_gap_ratio == pytest.approx(expected_ratio)
    assert bound.asymptotic_confidence_gap_ratio < 1.14


def test_truncated_boundary_sequential_bound_spends_error_by_markov():
    costs = np.array([1.0, 2.0, 5.0])
    beta, internal_error = 0.05, 0.02
    bound = boundary_familywise_truncated_sequential_bounds(
        costs,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=0.01,
        beta=beta,
        internal_error=internal_error,
    )
    sequential = boundary_familywise_sequential_bounds(
        costs,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=0.01,
        beta=internal_error,
    )

    assert bound.internal_error == pytest.approx(internal_error)
    assert bound.truncation_error_budget == pytest.approx(beta - internal_error)
    assert bound.declared_cost_cap == pytest.approx(
        sequential.alternative_expected_cost_upper.max() / (beta - internal_error)
    )
    assert bound.null_expected_total_cost_upper == pytest.approx(
        sequential.null_expected_total_cost_upper
    )
    assert bound.type_i_error_upper == pytest.approx(internal_error)
    assert bound.pointwise_type_ii_error_upper == pytest.approx(beta)


def test_truncated_boundary_sequential_cap_removes_m_log_m_at_fixed_error():
    common = {
        "p": 0.20,
        "shared_patch": 0.10,
        "fairness_tolerance": 0.10,
        "d": 0.01,
        "beta": 0.05,
    }
    small = boundary_familywise_truncated_sequential_bounds([1.0] * 16, **common)
    large = boundary_familywise_truncated_sequential_bounds([1.0] * 256, **common)

    assert large.small_gap_declared_cost_cap_coefficient / 256 < (
        small.small_gap_declared_cost_cap_coefficient / 16
    )
    assert large.small_gap_declared_cost_cap_coefficient / (256 * math.log(256)) < (
        small.small_gap_declared_cost_cap_coefficient / (16 * math.log(16))
    )


def test_truncated_boundary_sequential_cap_uses_worst_heterogeneous_alternative():
    bound = boundary_familywise_truncated_sequential_bounds(
        [1.0, 3.0, 11.0],
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=0.01,
        beta=0.05,
    )

    assert bound.worst_alternative_index == 2
    assert bound.declared_cost_cap == pytest.approx(
        bound.alternative_expected_cost_upper[2] / bound.truncation_error_budget
    )


def test_truncated_boundary_sequential_rejects_invalid_internal_error():
    with pytest.raises(ValueError, match="internal_error"):
        boundary_familywise_truncated_sequential_bounds(
            [1.0],
            p=0.20,
            shared_patch=0.10,
            fairness_tolerance=0.10,
            d=0.01,
            beta=0.05,
            internal_error=0.05,
        )


def test_mixed_control_hybrid_schedule_rejects_unobservable_candidate():
    graph, high = _family()
    with pytest.raises(ValueError, match="absent from every legal group"):
        mixed_control_replay_schedule(
            graph,
            groups=((0, 1), (0, 3)),
            costs=(1.0, 1.0),
            high_vertices=high,
            p=0.20,
            shared_patch=0.10,
            fairness_tolerance=0.10,
            d=0.01,
            beta=0.05,
        )


def test_mixed_control_coefficients_reject_unobservable_candidate():
    graph, high = _family()
    coeff = mixed_control_asymptotic_coefficients(
        graph,
        groups=((0, 1),),
        costs=(1.0,),
        high_vertices=high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        beta=0.05,
    )
    assert not coeff.success
    assert math.isinf(coeff.inverse_square_coefficient)
