#!/usr/bin/env python3
"""Dependency-free exact audit for the shared-nuisance replay witness."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from fractions import Fraction as F
from itertools import pairwise


def transcript_law(*thresholds: F) -> dict[tuple[int, ...], F]:
    if len(thresholds) != 4 or not all(F(0) < q < F(1) for q in thresholds):
        raise ValueError("four thresholds must lie strictly in (0,1)")
    cuts = sorted({F(0), F(1), *thresholds})
    law: dict[tuple[int, ...], F] = defaultdict(F)
    for left, right in pairwise(cuts):
        mid = (left + right) / 2
        law[tuple(int(mid <= q) for q in thresholds)] += right - left
    if sum(law.values(), F(0)) != 1:
        raise RuntimeError("law does not normalize")
    return dict(law)


def witness_probability(law: dict[tuple[int, ...], F]) -> F:
    return sum(
        (
            mass
            for (old_c, new_c, old_t, new_t), mass in law.items()
            if new_c - old_c != new_t - old_t
        ),
        F(0),
    )


def transcript_kl(source: dict[tuple[int, ...], F], target: dict[tuple[int, ...], F]) -> float:
    total = 0.0
    for state, mass in source.items():
        if not mass:
            continue
        target_mass = target.get(state, F(0))
        if not target_mass:
            return math.inf
        total += float(mass) * math.log(float(mass / target_mass))
    return total


def shifted_null(p: F, s: F, eta: F) -> dict[tuple[int, ...], F]:
    if not (0 < p < p + eta < p + s < p + s + eta < 1):
        raise ValueError("require 0 < p < p+eta < p+s < p+s+eta < 1")
    return transcript_law(p, p + s, p + eta, p + s + eta)


def run() -> dict[str, object]:
    cases = 0
    for p in (F(1, 8), F(1, 4), F(3, 8)):
        for s in (F(1, 8), F(1, 4)):
            h = p + s
            for d in (F(1, 100), F(1, 50), F(1, 20), F(1, 10)):
                if h + d >= 1:
                    continue
                null = transcript_law(p, h, p, h)
                alt = transcript_law(p, h + d, p, h)
                assert witness_probability(null) == 0
                assert witness_probability(alt) == d
                expected = float(1 - h) * math.log(float((1 - h) / (1 - h - d)))
                assert math.isclose(transcript_kl(null, alt), expected, rel_tol=1e-12)
                assert math.isinf(transcript_kl(alt, null))
                cases += 1

    d, eta, delta = F(1, 100), F(1, 200), 0.05
    horizon = math.ceil(math.log(delta) / math.log1p(-float(d)))
    false_reject = 1 - float((1 - 2 * eta) ** horizon)
    assert horizon == 299
    assert witness_probability(shifted_null(F(1, 5), F(1, 5), eta)) == 2 * eta

    h0, h1 = F(3, 10), F(1, 4)
    assert h0 == h1 + F(1, 20)
    return {
        "exact_shared_nuisance_cases": cases,
        "reverse_kl": "infinity",
        "counterexample_horizon": horizon,
        "counterexample_false_reject": false_reject,
        "shifted_null_witness_mass": "1/100",
        "candidate_only_overlap": {"null_nuisance": str(h0), "alternative_nuisance": str(h1)},
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
