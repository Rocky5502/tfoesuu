"""Simultaneous public-error interval tests, without fabricated measurements."""

import pytest

from scripts.render_public_results_table import (
    _clopper_pearson_interval,
    _simultaneous_max_error_interval,
)


def test_clopper_pearson_boundary_counts_are_finite():
    lower0, upper0 = _clopper_pearson_interval(0, 1000, 0.025)
    lower1, upper1 = _clopper_pearson_interval(1000, 1000, 0.025)
    assert lower0 == 0.0
    assert 0.0 < upper0 < 0.01
    assert 0.99 < lower1 < 1.0
    assert upper1 == 1.0


def test_simultaneous_max_interval_contains_both_error_estimates():
    k_i, k_ii, n = 10, 40, 1000
    lo, hi = _simultaneous_max_error_interval(k_i, k_ii, n)
    assert 0.0 <= lo <= max(k_i, k_ii) / n <= hi <= 1.0


def test_max_error_interval_adjusts_for_selection_of_larger_rate():
    count_i, count_ii, trials = 20, 30, 1000
    selected_unadjusted = _clopper_pearson_interval(
        count_ii, trials, alpha=0.05
    )
    simultaneous = _simultaneous_max_error_interval(
        count_i, count_ii, trials, family_alpha=0.05
    )
    assert simultaneous[0] < selected_unadjusted[0]
    assert simultaneous[1] > selected_unadjusted[1]


def test_zero_error_still_has_nonzero_uncertainty_upper_bound():
    lo, hi = _simultaneous_max_error_interval(0, 0, 1000)
    assert lo == 0.0
    assert 0.0 < hi < 0.01


def test_invalid_binomial_counts_are_rejected():
    for k, n in [(-1, 5), (6, 5), (0, 0)]:
        with pytest.raises(ValueError):
            _clopper_pearson_interval(k, n, 0.025)


def test_invalid_family_alpha_is_rejected():
    with pytest.raises(ValueError):
        _simultaneous_max_error_interval(1, 2, 1000, 1.0)
