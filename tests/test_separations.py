import math

import pytest

from tfoesuu.separations import (
    binary_decision_kl,
    independent_per_round_kl,
    location_replay_bounds,
    paired_per_round_kl,
    replay_separation_bounds,
)


def test_one_edge_bounds_are_ordered_and_finite():
    b = replay_separation_bounds(0.5, 0.02, 0.05)
    assert b.paired_upper_rounds > 0
    assert b.independent_upper_rounds > 0
    assert 0 < b.paired_null_expected_lower < math.inf
    assert 0 < b.independent_null_expected_lower < math.inf


def test_small_d_information_exponents():
    p = 0.4
    d1, d2 = 1e-4, 5e-5
    # Halving d approximately halves paired KL but quarters independent KL.
    pair_ratio = paired_per_round_kl(p, d1) / paired_per_round_kl(p, d2)
    ind_ratio = independent_per_round_kl(p, d1) / independent_per_round_kl(p, d2)
    assert pair_ratio == pytest.approx(2.0, rel=5e-4)
    assert ind_ratio == pytest.approx(4.0, rel=2e-3)


def test_location_replay_scales_exactly_with_candidates():
    one = location_replay_bounds(1, 0.5, 0.01, 0.05)
    many = location_replay_bounds(37, 0.5, 0.01, 0.05)
    assert many.total_upper_rounds == 37 * one.total_upper_rounds
    assert many.null_expected_lower == pytest.approx(37 * one.null_expected_lower)


def test_location_upper_miss_probability():
    b = location_replay_bounds(10, 0.5, 0.03, 0.05)
    assert (1.0 - 0.03) ** b.per_candidate_upper_rounds <= 0.05


def test_location_validation():
    with pytest.raises(ValueError):
        location_replay_bounds(0, 0.5, 0.01, 0.05)
