import math

import pytest

from tfoesuu.separations import (
    edge_coupled_common_patch_kl,
    threshold_fairness_replay_bounds,
    threshold_fairness_replay_kl,
)


def test_threshold_replay_recovers_sparse_witness_kl_at_zero_tolerance():
    p = 0.20
    s = 0.10
    d = 0.01

    phase_kl = threshold_fairness_replay_kl(p, s, 0.0, d)
    p15_kl = edge_coupled_common_patch_kl(p, s, d)

    assert phase_kl == pytest.approx(p15_kl)


def test_threshold_replay_linear_kl_at_zero_tolerance():
    p = 0.20
    s = 0.10

    for d in (1e-2, 1e-3, 1e-4):
        k = threshold_fairness_replay_kl(p, s, 0.0, d)
        assert k / d == pytest.approx(1.0, rel=0.01)


def test_threshold_replay_quadratic_kl_at_fixed_positive_tolerance():
    p = 0.20
    s = 0.10
    tau = 0.10
    r = 1.0 - p - s - tau
    asymptotic_constant = 0.5 * (1.0 / tau + 1.0 / r)

    k = threshold_fairness_replay_kl(p, s, tau, 1e-4)
    assert k / (1e-4**2) == pytest.approx(
        asymptotic_constant,
        rel=1e-3,
    )


def test_threshold_replay_upper_schedule_interpolates():
    beta = 0.05

    sparse = threshold_fairness_replay_bounds(
        p=0.20,
        shared_patch=0.10,
        tau=0.0,
        d=0.01,
        beta=beta,
    )
    interior = threshold_fairness_replay_bounds(
        p=0.20,
        shared_patch=0.10,
        tau=0.10,
        d=0.01,
        beta=beta,
    )

    sparse_scale = (
        sparse.replay_upper_rounds
        * 0.01
        / math.log(1.0 / beta)
    )
    interior_scale = (
        interior.replay_upper_rounds
        * (0.01**2)
        / math.log(1.0 / beta)
    )

    assert sparse_scale == pytest.approx(8.0, rel=0.01)
    assert interior_scale == pytest.approx(8.0 * 0.11, rel=0.01)
    assert sparse.replay_upper_concrete_executions == 4 * sparse.replay_upper_rounds
    assert interior.null_expected_rounds_lower > 0.0


def test_threshold_replay_rejects_invalid_boundary_parameters():
    with pytest.raises(ValueError, match=r"p\+shared_patch\+tau\+d"):
        threshold_fairness_replay_bounds(
            p=0.70,
            shared_patch=0.10,
            tau=0.15,
            d=0.10,
            beta=0.05,
        )
