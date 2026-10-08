"""Adversarial finite-nuisance audits for the P20 information-cover scaffold."""

import math

import numpy as np
import pytest

from tfoesuu.nuisance_information import audit_finite_nuisance_information


def test_crossing_nuisance_preferences_do_not_commute_with_allocation():
    epsilon = 0.01
    # Null nuisance eta is GLOBAL across the two actions. For each eta,
    # one action is informative and the other is nearly useless.
    info = [
        [[1.0], [epsilon]],
        [[epsilon], [1.0]],
    ]
    out = audit_finite_nuisance_information(info, [1.0, 1.0], [1.0])
    assert all(x.success for x in out.pointwise_solutions)
    assert out.worst_pointwise_cost == pytest.approx(1.0)
    assert out.shared_fixed_information_solution.success
    assert out.shared_fixed_information_solution.cost == pytest.approx(
        2.0 / (1.0 + epsilon)
    )
    assert out.shared_to_pointwise_ratio > 1.9
    np.testing.assert_allclose(
        out.shared_fixed_information_solution.action_weights,
        [1.0 / (1.0 + epsilon)] * 2,
        atol=1e-9,
    )


def test_many_nuisances_yield_large_fixed_information_gap():
    # No assertion about an adaptive test is warranted by this LP example.
    n = 4
    info = np.eye(n, dtype=float)[:, :, None]
    out = audit_finite_nuisance_information(info, np.ones(n), [1.0])
    assert out.worst_pointwise_cost == pytest.approx(1.0)
    assert out.shared_fixed_information_solution.cost == pytest.approx(float(n))
    assert out.shared_to_pointwise_ratio == pytest.approx(float(n))


def test_no_quantifier_gap_when_nuisance_laws_identical():
    info = [
        [[0.5, 0.0], [0.0, 1.0]],
        [[0.5, 0.0], [0.0, 1.0]],
    ]
    out = audit_finite_nuisance_information(info, [1.0, 1.0], [1.0, 1.0])
    assert out.worst_pointwise_cost == pytest.approx(3.0)
    assert out.shared_fixed_information_solution.cost == pytest.approx(3.0)
    assert out.shared_to_pointwise_ratio == pytest.approx(1.0)


def test_unobservable_alternative_fails_closed():
    out = audit_finite_nuisance_information(
        [
            [[1.0], [0.0]],
            [[0.0], [0.0]],
        ],
        [1.0, 1.0],
        [1.0],
    )
    assert math.isinf(out.worst_pointwise_cost)
    assert not out.shared_fixed_information_solution.success


@pytest.mark.parametrize(
    "info,costs,needs",
    [
        ([[[1.0]], [[1.0, 2.0]]], [1.0], [1.0]),
        ([ [[-1.0]] ], [1.0], [1.0]),
        ([ [[float('nan')]] ], [1.0], [1.0]),
        ([ [[1.0]] ], [0.0], [1.0]),
        ([ [[1.0]] ], [1.0], [-1.0]),
    ],
)
def test_invalid_nuisance_information_is_rejected(info, costs, needs):
    with pytest.raises(ValueError):
        audit_finite_nuisance_information(info, costs, needs)


def test_single_nuisance_reproduces_p19_exact_information_lower_lp():
    from tfoesuu.control_replay import control_replay_information_lower_bound
    from tfoesuu.graphs import complete_bipartite_graph
    from tfoesuu.separations import binary_decision_kl

    graph = complete_bipartite_graph(3, 2)
    high = (0, 1, 2)
    groups = [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3), (2, 3)]
    costs = [1.0] * len(groups)
    beta = 0.05

    audited_p19 = control_replay_information_lower_bound(
        graph, groups, costs, high,
        p=0.20, shared_patch=0.10, fairness_tolerance=0.10,
        d=0.01, beta=beta,
    )
    assert audited_p19.success
    needs = [binary_decision_kl(beta)] * len(high)
    generalized = audit_finite_nuisance_information(
        audited_p19.information_matrix[np.newaxis, :, :],
        costs,
        needs,
    )
    assert len(generalized.pointwise_solutions) == 1
    assert generalized.worst_pointwise_cost == pytest.approx(
        audited_p19.expected_cost_floor
    )
    assert generalized.shared_fixed_information_solution.cost == pytest.approx(
        audited_p19.expected_cost_floor
    )
