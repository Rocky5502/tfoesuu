import math

from tfoesuu.separations import (
    binary_decision_kl,
    binary_kl,
    paired_per_round_kl,
    independent_per_round_kl,
    replay_separation_bounds,
)


def test_binary_kl_basic_properties():
    assert binary_kl(0.5, 0.5) == 0.0
    assert binary_kl(0.5, 0.6) > 0.0
    assert math.isinf(binary_kl(0.5, 1.0))


def test_replay_bounds_scale_linear_vs_quadratic():
    beta = 0.05
    p = 0.5
    ds = [0.04, 0.02, 0.01, 0.005]

    paired = [replay_separation_bounds(p, d, beta).paired_null_expected_lower for d in ds]
    independent = [replay_separation_bounds(p, d, beta).independent_null_expected_lower for d in ds]

    # Halving d should asymptotically double the paired lower bound and
    # quadruple the independent lower bound.
    paired_ratios = [paired[i + 1] / paired[i] for i in range(len(ds) - 1)]
    independent_ratios = [independent[i + 1] / independent[i] for i in range(len(ds) - 1)]

    assert all(1.8 < r < 2.2 for r in paired_ratios)
    assert all(3.6 < r < 4.4 for r in independent_ratios)


def test_paired_exact_upper_controls_miss_probability():
    p, d, beta = 0.5, 0.01, 0.05
    bounds = replay_separation_bounds(p, d, beta)
    n = bounds.paired_upper_rounds
    assert (1.0 - d) ** n <= beta
    if n > 1:
        assert (1.0 - d) ** (n - 1) > beta


def test_kl_formulas_have_expected_small_d_orders():
    p = 0.4
    d = 1e-5

    paired = paired_per_round_kl(p, d)
    independent = independent_per_round_kl(p, d)

    # Paired KL / d -> 1, while independent KL / d^2
    # -> 1 / (2 p (1-p)).
    assert abs(paired / d - 1.0) < 1e-3
    target = 1.0 / (2.0 * p * (1.0 - p))
    assert abs(independent / (d * d) - target) / target < 1e-3

    assert binary_decision_kl(0.05) > 0.0
