from __future__ import annotations

import math
from collections.abc import Mapping
from fractions import Fraction
from itertools import pairwise

Transcript = tuple[int, int, int, int]
TranscriptLaw = dict[Transcript, Fraction]


def threshold_transcript_law(
    old_candidate: Fraction,
    new_candidate: Fraction,
    old_control: Fraction,
    new_control: Fraction,
) -> TranscriptLaw:
    """Enumerate the exact ordered four-output common-uniform law."""

    thresholds = (
        Fraction(old_candidate),
        Fraction(new_candidate),
        Fraction(old_control),
        Fraction(new_control),
    )
    if not all(0 < value < 1 for value in thresholds):
        raise ValueError("all thresholds must lie strictly between zero and one")

    cuts = sorted({Fraction(0), Fraction(1), *thresholds})
    law: TranscriptLaw = {}
    for left, right in pairwise(cuts):
        if left == right:
            continue
        midpoint = (left + right) / 2
        state = tuple(int(midpoint <= value) for value in thresholds)
        law[state] = law.get(state, Fraction(0)) + right - left
    if sum(law.values(), Fraction(0)) != 1:
        raise RuntimeError("transcript law failed to normalize")
    return law


def shared_nuisance_laws(
    p: Fraction, h: Fraction, d: Fraction
) -> tuple[TranscriptLaw, TranscriptLaw]:
    """Return the matched-null and singleton-alternative transcript laws.

    Output order is ``(old candidate, new candidate, old control,
    new control)``. The nuisance ``(p, h)`` is shared across endpoints; the
    alternative raises only the candidate's new threshold by ``d``.
    """

    p, h, d = Fraction(p), Fraction(h), Fraction(d)
    if not (0 < p < h < h + d < 1):
        raise ValueError("require 0 < p < h < h + d < 1")
    null = threshold_transcript_law(p, h, p, h)
    alternative = threshold_transcript_law(p, h + d, p, h)
    return null, alternative


def witness_probability(law: Mapping[Transcript, Fraction]) -> Fraction:
    """Probability that candidate and control patch deltas disagree."""

    return sum(
        (
            mass
            for (old_c, new_c, old_t, new_t), mass in law.items()
            if new_c - old_c != new_t - old_t
        ),
        Fraction(0),
    )


def transcript_kl(
    source: Mapping[Transcript, Fraction],
    target: Mapping[Transcript, Fraction],
) -> float:
    """Compute ``KL(source || target)``, including support failures."""

    divergence = 0.0
    for state, source_mass in source.items():
        if source_mass == 0:
            continue
        target_mass = target.get(state, Fraction(0))
        if target_mass == 0:
            return math.inf
        divergence += float(source_mass) * math.log(
            float(source_mass / target_mass)
        )
    return divergence


def witness_horizon(d: float, delta: float) -> int:
    """Exact fixed horizon ensuring ``(1-d)**L <= delta``."""

    if not (0.0 < d < 1.0):
        raise ValueError("d must lie in (0,1)")
    if not (0.0 < delta < 1.0):
        raise ValueError("delta must lie in (0,1)")
    return math.ceil(math.log(delta) / math.log1p(-d))


def mean_matched_false_rejection_probability(
    eta: Fraction, rounds: int
) -> float:
    """False rejection of the zero-witness rule under shifted supports."""

    eta = Fraction(eta)
    if not (0 < eta < Fraction(1, 2)):
        raise ValueError("eta must lie in (0,1/2)")
    if rounds < 0:
        raise ValueError("rounds must be nonnegative")
    return 1.0 - float((1 - 2 * eta) ** rounds)


def shifted_mean_matched_law(
    p: Fraction, s: Fraction, eta: Fraction
) -> TranscriptLaw:
    """Return the equal-mean-patch null with shifted tape supports."""

    p, s, eta = Fraction(p), Fraction(s), Fraction(eta)
    if not (0 < p < p + eta < p + s < p + s + eta < 1):
        raise ValueError("require 0 < p < p + eta < p + s < p + s + eta < 1")
    return threshold_transcript_law(p, p + s, p + eta, p + s + eta)


def single_marginal_overlap(
    lower: Fraction, upper: Fraction, d: Fraction
) -> tuple[Fraction, Fraction] | None:
    """Return one equal-law null/alternative nuisance pair, if it exists.

    The null family is ``Bernoulli(h0)`` for ``h0 in [lower, upper]``.
    The alternative family is ``Bernoulli(h1 + d)`` for
    ``h1 in [lower, upper]`` with ``h1 + d <= 1``. The returned pair is
    ``(h0, h1)`` and satisfies ``h0 == h1 + d``.
    """

    lower, upper, d = Fraction(lower), Fraction(upper), Fraction(d)
    if not (0 <= lower < upper <= 1 and 0 < d < 1):
        raise ValueError("require 0 <= lower < upper <= 1 and 0 < d < 1")
    h1 = lower
    h0 = h1 + d
    if h0 <= upper and h0 <= 1:
        return h0, h1
    return None
