from __future__ import annotations

import math
from collections.abc import Hashable
from dataclasses import dataclass


@dataclass(frozen=True)
class ReplaySeparationBounds:
    """Finite-sample bounds for the one-edge Bernoulli replay separation."""

    paired_upper_rounds: int
    paired_null_expected_lower: float
    independent_upper_rounds: int
    independent_null_expected_lower: float
    paired_per_round_kl: float
    independent_per_round_kl: float


def binary_kl(a: float, b: float) -> float:
    """KL(Bernoulli(a) || Bernoulli(b)) with boundary-safe conventions."""

    if not (0.0 <= a <= 1.0 and 0.0 <= b <= 1.0):
        raise ValueError("Bernoulli parameters must lie in [0,1]")
    if a == b:
        return 0.0
    if b == 0.0:
        return math.inf if a > 0.0 else 0.0
    if b == 1.0:
        return math.inf if a < 1.0 else 0.0

    out = 0.0
    if a > 0.0:
        out += a * math.log(a / b)
    if a < 1.0:
        out += (1.0 - a) * math.log((1.0 - a) / (1.0 - b))
    return out


def discrete_kl(
    null: dict[Hashable, float], alternative: dict[Hashable, float]
) -> float:
    """Return KL(null || alternative) for explicit finite transcript laws."""

    if not math.isclose(sum(null.values()), 1.0, abs_tol=1e-12) or not math.isclose(
        sum(alternative.values()), 1.0, abs_tol=1e-12
    ):
        raise ValueError("transcript probabilities must each sum to one")
    if any(value < 0.0 for value in (*null.values(), *alternative.values())):
        raise ValueError("transcript probabilities must be nonnegative")
    total = 0.0
    for outcome, probability in null.items():
        if probability == 0.0:
            continue
        reference = alternative.get(outcome, 0.0)
        if reference == 0.0:
            return math.inf
        total += probability * math.log(probability / reference)
    return total


def binary_decision_kl(beta: float) -> float:
    """kl(1-beta, beta), the data-processing term in fixed-confidence tests."""

    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0, 1/2)")
    return binary_kl(1.0 - beta, beta)


def _validate(p: float, d: float, beta: float) -> None:
    if not (0.0 < p < 1.0):
        raise ValueError("p must lie in (0,1)")
    if not (0.0 < d < 1.0 - p):
        raise ValueError("d must lie in (0,1-p)")
    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")


def paired_per_round_kl(p: float, d: float) -> float:
    """Null-to-alternative KL for a raw common-uniform old/new pair.

    H0 pair probabilities are:
      (1,1): p, (0,0): 1-p.
    H1 adds the discordant pair (0,1) with probability d:
      (1,1): p, (0,0): 1-p-d, (0,1): d.

    Hence KL(H0 || H1) is linear in d to first order.
    """

    if not (0.0 < p < 1.0 and 0.0 < d < 1.0 - p):
        raise ValueError("require p in (0,1) and d in (0,1-p)")
    return (1.0 - p) * math.log((1.0 - p) / (1.0 - p - d))


def independent_per_round_kl(p: float, d: float) -> float:
    """Null-to-alternative KL under independent/fresh replay.

    The old-version observation has the same law under both hypotheses, so only
    the new Bernoulli(p) versus Bernoulli(p+d) sample contributes information.
    """

    if not (0.0 < p < 1.0 and 0.0 < d < 1.0 - p):
        raise ValueError("require p in (0,1) and d in (0,1-p)")
    return binary_kl(p, p + d)


def replay_separation_bounds(p: float, d: float, beta: float) -> ReplaySeparationBounds:
    """Return proved upper/lower bounds for the one-edge separation family.

    The fairness threshold is zero. The old version has probabilities (p,p).
    Under H0 the new version remains (p,p). Under H1 the first endpoint changes
    to p+d while the second remains p.

    A coupled query is one replay round that executes old and new versions on the
    same uniform random tape. Individual program executions differ only by a
    constant factor of two from paired-round counts.
    """

    _validate(p, d, beta)

    paired_kl = paired_per_round_kl(p, d)
    independent_kl = independent_per_round_kl(p, d)
    decision_kl = binary_decision_kl(beta)

    paired_upper = math.ceil(math.log(beta) / math.log1p(-d))
    independent_upper = math.ceil(2.0 * math.log(1.0 / beta) / (d * d))

    return ReplaySeparationBounds(
        paired_upper_rounds=paired_upper,
        paired_null_expected_lower=decision_kl / paired_kl,
        independent_upper_rounds=independent_upper,
        independent_null_expected_lower=decision_kl / independent_kl,
        paired_per_round_kl=paired_kl,
        independent_per_round_kl=independent_kl,
    )


@dataclass(frozen=True)
class LocationReplayBounds:
    """Bounds for the unknown patch-location matching family (P13)."""

    candidates: int
    per_candidate_upper_rounds: int
    total_upper_rounds: int
    null_expected_lower: float
    paired_per_round_kl: float


def location_replay_bounds(candidates: int, p: float, d: float, beta: float) -> LocationReplayBounds:
    """Finite-sample P13 bounds for M possible changed endpoints.

    The graph is a matching with M candidate endpoints u_i. Under H0 no endpoint
    changes. Under alternative i only u_i changes from Bernoulli(p) to
    Bernoulli(p+d), observed through common-uniform old/new replay.

    Sampling every candidate for n=ceil(log(beta)/log(1-d)) rounds gives zero
    type-I error and miss probability at most beta for every alternative.
    Transcript change of measure under the common null yields the summed adaptive
    lower bound M*kl(1-beta,beta)/K_pair.
    """
    if candidates < 1:
        raise ValueError("candidates must be >= 1")
    _validate(p, d, beta)
    per_candidate = math.ceil(math.log(beta) / math.log1p(-d))
    k_pair = paired_per_round_kl(p, d)
    lower = candidates * binary_decision_kl(beta) / k_pair
    return LocationReplayBounds(
        candidates=candidates,
        per_candidate_upper_rounds=per_candidate,
        total_upper_rounds=candidates * per_candidate,
        null_expected_lower=lower,
        paired_per_round_kl=k_pair,
    )



@dataclass(frozen=True)
class CounterfactualReplayBounds:
    """Bounds for four-way counterfactual replay versus vertex-paired replay."""

    edge_coupled_upper_rounds: int
    edge_coupled_null_expected_lower: float
    vertex_paired_upper_rounds: int
    vertex_paired_null_expected_lower: float
    edge_coupled_per_round_kl: float
    vertex_paired_per_round_kl: float


def _validate_common_patch(p: float, s: float, d: float, beta: float) -> None:
    if not (0.0 < p < 1.0):
        raise ValueError("p must lie in (0,1)")
    if not (0.0 < s < 1.0 - p):
        raise ValueError("s must lie in (0,1-p)")
    if not (0.0 < d < 1.0 - p - s):
        raise ValueError("d must lie in (0,1-p-s)")
    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")


def edge_coupled_common_patch_kl(p: float, s: float, d: float) -> float:
    """Null-to-alternative KL for one raw four-way common-uniform transcript.

    Old endpoints both use threshold p. Under H0 both new endpoints use p+s.
    Under H1 the first new endpoint uses p+s+d and the second remains p+s.
    """

    if not (0.0 < p < 1.0 and 0.0 < s < 1.0 - p and 0.0 < d < 1.0 - p - s):
        raise ValueError("require p>0, s>0, d>0, and p+s+d<1")
    r = 1.0 - p - s
    return r * math.log(r / (r - d))


def vertex_paired_common_patch_kl(p: float, s: float, d: float) -> float:
    """Null-to-alternative KL for one raw old/new pair at the changed endpoint."""

    if not (0.0 < p < 1.0 and 0.0 < s < 1.0 - p and 0.0 < d < 1.0 - p - s):
        raise ValueError("require p>0, s>0, d>0, and p+s+d<1")
    r = 1.0 - p - s
    return s * math.log(s / (s + d)) + r * math.log(r / (r - d))


def counterfactual_replay_bounds(
    p: float,
    s: float,
    d: float,
    beta: float,
) -> CounterfactualReplayBounds:
    """Finite-sample bounds for common-patch cancellation by four-way replay.

    H0:
      old endpoints (p,p), new endpoints (p+s,p+s).
    H1:
      old endpoints (p,p), new endpoints (p+s+d,p+s).

    Four-way edge replay shares one uniform tape across both versions and both
    endpoints. The fairness differential is then nonzero with probability d.
    Vertex-paired replay shares randomness only across versions at one endpoint;
    when s>0 it must distinguish an interior Bernoulli(s) from Bernoulli(s+d).
    """

    _validate_common_patch(p, s, d, beta)
    decision_kl = binary_decision_kl(beta)
    edge_kl = edge_coupled_common_patch_kl(p, s, d)
    vertex_kl = vertex_paired_common_patch_kl(p, s, d)

    edge_upper = math.ceil(math.log(beta) / math.log1p(-d))
    vertex_upper = math.ceil(2.0 * math.log(1.0 / beta) / (d * d))

    return CounterfactualReplayBounds(
        edge_coupled_upper_rounds=edge_upper,
        edge_coupled_null_expected_lower=decision_kl / edge_kl,
        vertex_paired_upper_rounds=vertex_upper,
        vertex_paired_null_expected_lower=decision_kl / vertex_kl,
        edge_coupled_per_round_kl=edge_kl,
        vertex_paired_per_round_kl=vertex_kl,
    )


@dataclass(frozen=True)
class ThresholdFairnessReplayBounds:
    """Bounds for thresholded one-edge fairness under synchronized replay."""

    fairness_tolerance: float
    differential_margin: float
    replay_upper_rounds: int
    replay_upper_concrete_executions: int
    null_expected_rounds_lower: float
    per_round_kl: float


def threshold_fairness_replay_kl(
    p: float,
    shared_patch: float,
    tau: float,
    d: float,
) -> float:
    """Null-to-alternative KL at a thresholded fairness boundary.

    Old thresholds are (p,p).  Under the boundary null, the new thresholds are
    (p+s+tau, p+s); under the alternative they are
    (p+s+tau+d, p+s).  One common-uniform tape is shared across both versions
    and both endpoints.

    Only two transcript atoms change mass: tau -> tau+d and
    r -> r-d, where r=1-p-s-tau.  Hence the exact full-transcript KL is

        tau log(tau/(tau+d)) + r log(r/(r-d)),

    with the first term interpreted as zero at tau=0.
    """

    if not (0.0 < p < 1.0):
        raise ValueError("p must lie in (0,1)")
    if not (0.0 <= shared_patch < 1.0 - p):
        raise ValueError("shared_patch must lie in [0,1-p)")
    if tau < 0.0:
        raise ValueError("tau must be nonnegative")
    if d <= 0.0:
        raise ValueError("d must be positive")
    if not (p + shared_patch + tau + d < 1.0):
        raise ValueError("require p+shared_patch+tau+d < 1")

    r = 1.0 - p - shared_patch - tau
    first = 0.0 if tau == 0.0 else tau * math.log(tau / (tau + d))
    second = r * math.log(r / (r - d))
    return first + second


def threshold_fairness_replay_bounds(
    p: float,
    shared_patch: float,
    tau: float,
    d: float,
    beta: float,
) -> ThresholdFairnessReplayBounds:
    """Fixed-confidence bounds for thresholded one-edge synchronized replay.

    The composite null is that the new-version endpoint gap is at most tau; the
    alternative gap is at least tau+d.  In each synchronized edge replay, the
    new-version mismatch indicator is Bernoulli with mean equal to that gap.
    Thresholding its empirical mean at tau+d/2 and applying Bernstein/Chernoff
    bounds gives an upper schedule of

        8 (tau+d) log(1/beta) / d^2

    rounds.  A boundary null/alternative pair gives the transcript-KL lower
    bound returned below.

    This family interpolates between the sparse-witness regime tau=0 and the
    interior-threshold regime tau>0.
    """

    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")
    k = threshold_fairness_replay_kl(p, shared_patch, tau, d)
    upper = math.ceil(
        8.0 * (tau + d) * math.log(1.0 / beta) / (d * d)
    )
    lower = binary_decision_kl(beta) / k
    return ThresholdFairnessReplayBounds(
        fairness_tolerance=tau,
        differential_margin=d,
        replay_upper_rounds=upper,
        replay_upper_concrete_executions=4 * upper,
        null_expected_rounds_lower=lower,
        per_round_kl=k,
    )
