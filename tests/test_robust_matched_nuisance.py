import math
from fractions import Fraction

import pytest

from tfoesuu.robust_matched_nuisance import (
    mean_matched_false_rejection_probability,
    shared_nuisance_laws,
    shifted_mean_matched_law,
    single_marginal_overlap,
    transcript_kl,
    witness_horizon,
    witness_probability,
)


def test_shared_nuisance_full_atom_laws_and_witness():
    p = Fraction(1, 4)
    h = Fraction(1, 2)
    d = Fraction(1, 100)
    null, alternative = shared_nuisance_laws(p, h, d)

    assert null == {
        (1, 1, 1, 1): p,
        (0, 1, 0, 1): h - p,
        (0, 0, 0, 0): 1 - h,
    }
    assert alternative == {
        (1, 1, 1, 1): p,
        (0, 1, 0, 1): h - p,
        (0, 1, 0, 0): d,
        (0, 0, 0, 0): 1 - h - d,
    }
    assert witness_probability(null) == 0
    assert witness_probability(alternative) == d


def test_kl_direction_and_support_are_explicit():
    p = Fraction(1, 4)
    h = Fraction(1, 2)
    d = Fraction(1, 100)
    null, alternative = shared_nuisance_laws(p, h, d)

    expected = float(1 - h) * math.log(float((1 - h) / (1 - h - d)))
    assert transcript_kl(null, alternative) == pytest.approx(expected)
    assert math.isinf(transcript_kl(alternative, null))


@pytest.mark.parametrize(
    "p,h,d",
    [
        (Fraction(1, 8), Fraction(1, 4), Fraction(1, 100)),
        (Fraction(1, 4), Fraction(1, 2), Fraction(1, 20)),
        (Fraction(3, 8), Fraction(5, 8), Fraction(1, 10)),
    ],
)
def test_unknown_shared_nuisance_is_uniformly_witnessed(p, h, d):
    null, alternative = shared_nuisance_laws(p, h, d)
    assert witness_probability(null) == 0
    assert witness_probability(alternative) == d


def test_mean_matching_counterexample_exact_value():
    d = Fraction(1, 100)
    eta = Fraction(1, 200)
    delta = 0.05
    rounds = witness_horizon(float(d), delta)
    assert rounds == 299
    false_rejection = mean_matched_false_rejection_probability(
        eta, rounds
    )
    assert false_rejection == pytest.approx(0.9504637433623376)


def test_mean_matching_counterexample_full_law_and_domain():
    p = Fraction(1, 5)
    s = Fraction(1, 5)
    eta = Fraction(1, 100)
    law = shifted_mean_matched_law(p, s, eta)
    assert law == {
        (1, 1, 1, 1): p,
        (0, 1, 1, 1): eta,
        (0, 1, 0, 1): s - eta,
        (0, 0, 0, 1): eta,
        (0, 0, 0, 0): 1 - p - s - eta,
    }
    assert witness_probability(law) == 2 * eta

    with pytest.raises(ValueError, match=r"require 0 < p"):
        shifted_mean_matched_law(
            Fraction(-1, 20), Fraction(1, 10), Fraction(1, 50)
        )


def test_uncalibrated_single_marginal_null_and_alternative_overlap():
    overlap = single_marginal_overlap(
        Fraction(1, 4), Fraction(1, 2), Fraction(1, 20)
    )
    assert overlap == (Fraction(3, 10), Fraction(1, 4))


def test_invalid_shared_nuisance_parameters_fail_closed():
    with pytest.raises(ValueError, match=r"0 < p < h < h \+ d < 1"):
        shared_nuisance_laws(
            Fraction(1, 2), Fraction(1, 2), Fraction(1, 100)
        )
