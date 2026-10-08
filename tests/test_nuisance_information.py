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
