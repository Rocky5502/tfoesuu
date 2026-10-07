import math

import numpy as np
import pytest

from tfoesuu.replay_information import minimum_information_cover


def test_joint_action_can_amortize_multiple_alternatives():
    # Three actions: one specialized for each alternative and one joint action.
    I = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    costs = [1.0, 1.0, 1.5]
    requirements = [1.0, 1.0]

    sol = minimum_information_cover(I, costs, requirements)

    assert sol.success
    assert sol.cost == pytest.approx(1.5)
    assert sol.action_weights[2] == pytest.approx(1.0)
    assert np.all(sol.achieved_information >= 1.0 - 1e-10)


def test_zero_information_alternative_is_infeasible():
    I = np.array([[1.0, 0.0], [0.5, 0.0]])
    sol = minimum_information_cover(I, [1.0, 1.0], [1.0, 1.0])

    assert not sol.success
    assert math.isinf(sol.cost)


def test_small_effect_prefers_linear_information_when_cost_is_comparable():
    # Candidate nuisance-aware asymptotic pattern:
    # separated replay offers O(d^2) information while co-replay offers O(d).
    # This is only an LP fixture, not a theorem about a statistical model.
    d = 0.01
    I = np.array([[d * d], [d]])
    costs = [1.0, 10.0]
    sol = minimum_information_cover(I, costs, [1.0])

    assert sol.success
    # Cost per unit information: 1/d^2=10000 versus 10/d=1000.
    assert sol.action_weights[0] == pytest.approx(0.0, abs=1e-10)
    assert sol.action_weights[1] == pytest.approx(1.0 / d)
    assert sol.cost == pytest.approx(10.0 / d)


def test_expensive_coreplay_can_make_quadratic_information_cheaper():
    d = 0.01
    I = np.array([[d * d], [d]])
    costs = [1.0, 1000.0]
    sol = minimum_information_cover(I, costs, [1.0])

    assert sol.success
    assert sol.action_weights[0] == pytest.approx(1.0 / (d * d))
    assert sol.action_weights[1] == pytest.approx(0.0, abs=1e-10)
    assert sol.cost == pytest.approx(1.0 / (d * d))


def test_input_validation_rejects_negative_information():
    with pytest.raises(ValueError):
        minimum_information_cover([[-1.0]], [1.0], [1.0])
