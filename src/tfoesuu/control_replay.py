from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog

from .graphs import GraphSpec
from .partial_replay import _canonical_groups
from .separations import binary_decision_kl, threshold_fairness_replay_bounds


@dataclass(frozen=True)
class FractionalControlCover:
    """Fractional cover of high-side candidates by matched-background controls."""

    cost: float
    weights: np.ndarray
    high_vertices: tuple[int, ...]
    success: bool
    message: str


@dataclass(frozen=True)
class ControlReplayInformationLowerBound:
    """Exact transcript-KL allocation floor for the P19 bipartite null family."""

    expected_cost_floor: float
    expected_query_counts: np.ndarray
    high_vertices: tuple[int, ...]
    information_matrix: np.ndarray
    control_kl: float
    boundary_kl: float
    success: bool
    message: str


@dataclass(frozen=True)
class MixedControlLeadingCoefficient:
    """Exact d^-2 coefficient of the exact P19 information lower LP."""

    coefficient: float
    scaled_query_weights: np.ndarray
    uncovered_high_vertices: tuple[int, ...]
    boundary_quadratic_coefficient: float
    success: bool
    message: str


@dataclass(frozen=True)
class MixedControlAsymptoticCoefficients:
    """First two singular coefficients of the exact P19 information LP.

    If ``Q(d)`` denotes the LP value, then within the frozen finite P19
    two-class family

        Q(d) = inverse_square_coefficient / d**2
             + inverse_linear_coefficient / d + O(1).

    This describes the exact information lower program.  The hybrid mixed
    schedule matches its finite-topology d-orders but not these exact two-term
    coefficients.
    """

    inverse_square_coefficient: float
    inverse_linear_coefficient: float
    uncovered_high_vertices: tuple[int, ...]
    covered_high_vertices: tuple[int, ...]
    boundary_minimum_cost: float
    residual_control_cover_cost: float
    boundary_quadratic_coefficient: float
    boundary_cubic_coefficient: float
    success: bool
    message: str


@dataclass(frozen=True)
class ControlReplaySchedule:
    """Zero-type-I matched-control schedule for the P19 family."""

    normalized_control_cover_cost: float
    scale: int
    counts: np.ndarray
    total_cost: float
    additive_rounding_cap: float
    high_vertices: tuple[int, ...]


@dataclass(frozen=True)
class MixedControlReplaySchedule:
    """Hybrid fixed-design schedule for the frozen mixed P19 family.

    Control-uncovered candidates receive individual P18 boundary tests, while
    the remaining candidates use the zero-type-I matched-control schedule.
    This is valid only for P19's exact two-class null and singleton alternatives;
    it is not a tester for an arbitrary heterogeneous composite null.
    """

    counts: np.ndarray
    total_cost: float
    uncovered_high_vertices: tuple[int, ...]
    covered_high_vertices: tuple[int, ...]
    boundary_group_indices: tuple[int, ...]
    boundary_rounds_per_candidate: int
    boundary_error_budget_per_candidate: float
    boundary_minimum_cost: float
    residual_control_cover_cost: float
    control_scale: int
    additive_control_rounding_cap: float


@dataclass(frozen=True)
class BoundaryFamilywiseFixedDesignLowerBound:
    """Familywise lower bound for disjoint unit-cost P19 boundary channels."""

    candidates: int
    transcript_renyi2: float
    sorted_query_count_floors: np.ndarray
    total_query_floor: float
    total_cost_floor: float


@dataclass(frozen=True)
class BoundaryFamilywiseSequentialBounds:
    """Two-sided-SPRT bounds for disjoint P19 boundary channels."""

    candidates: int
    upper_likelihood_threshold: float
    lower_likelihood_threshold: float
    null_to_alternative_kl: float
    alternative_to_null_kl: float
    null_expected_rounds_per_candidate_upper: float
    changed_expected_rounds_upper: float
    null_expected_total_cost_lower: float
    null_expected_total_cost_upper: float
    alternative_expected_cost_upper: np.ndarray
    small_gap_lower_cost_coefficient: float
    small_gap_upper_cost_coefficient: float
    asymptotic_confidence_gap_ratio: float


@dataclass(frozen=True)
class BoundaryFamilywiseTruncatedSequentialBounds:
    """Deterministic-cost truncation of the familywise P19 SPRT."""

    candidates: int
    target_error: float
    internal_error: float
    truncation_error_budget: float
    declared_cost_cap: float
    worst_alternative_index: int
    null_expected_total_cost_upper: float
    alternative_expected_cost_upper: np.ndarray
    type_i_error_upper: float
    pointwise_type_ii_error_upper: float
    small_gap_declared_cost_cap_coefficient: float


def _validate_bipartite_threshold_family(
    graph: GraphSpec,
    high_vertices: Iterable[int],
) -> tuple[int, ...]:
    high = tuple(sorted({int(v) for v in high_vertices}))
    if not high:
        raise ValueError("at least one high-side candidate is required")
    if any(v < 0 or v >= graph.n for v in high):
        raise ValueError("high-side candidate is out of range")
    high_set = set(high)
    active = {v for edge in graph.edges for v in edge}
    if any(v not in active for v in high):
        raise ValueError("every high-side candidate must be fairness-active")
    for u, v in graph.edges:
        if (u in high_set) == (v in high_set):
            raise ValueError(
                "P19 requires a bipartite fairness graph with every edge crossing "
                "the high and low threshold classes"
            )
    return high


def _validate_costs(groups: tuple[tuple[int, ...], ...], costs: Sequence[float]) -> np.ndarray:
    c = np.asarray(costs, dtype=float)
    if c.shape != (len(groups),) or np.any(c <= 0) or np.any(~np.isfinite(c)):
        raise ValueError("costs must be finite, positive, and match groups")
    return c


def minimum_fractional_control_cover(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    high_vertices: Iterable[int],
) -> FractionalControlCover:
    """Cover each high candidate by a group containing a second high control.

    Under the P19 null, all high vertices have the same old/new threshold pair.
    A legal group is control-compatible for candidate x iff it contains x and at
    least one other high vertex.  Such a query can compare patch deltas within
    the high class and has a sparse d-probability witness under alternative x.
    """

    high = _validate_bipartite_threshold_family(graph, high_vertices)
    high_set = set(high)
    gs = _canonical_groups(graph, groups)
    c = _validate_costs(gs, costs)

    A = np.zeros((len(high), len(gs)), dtype=float)
    for xi, x in enumerate(high):
        for gi, group in enumerate(gs):
            if x in group and sum(v in high_set for v in group) >= 2:
                A[xi, gi] = 1.0

    if np.any(A.sum(axis=1) == 0.0):
        return FractionalControlCover(
            float("inf"),
            np.zeros(len(gs)),
            high,
            False,
            "some high-side candidate has no legal matched-background control group",
        )

    res = linprog(
        c,
        A_ub=-A,
        b_ub=-np.ones(len(high)),
        bounds=[(0.0, None)] * len(gs),
        method="highs",
    )
    if not res.success:
        return FractionalControlCover(
            float("inf"), np.zeros(len(gs)), high, False, str(res.message)
        )
    return FractionalControlCover(float(res.fun), np.asarray(res.x), high, True, str(res.message))


def control_replay_information_lower_bound(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    high_vertices: Iterable[int],
    *,
    p: float,
    shared_patch: float,
    fairness_tolerance: float,
    d: float,
    beta: float,
) -> ControlReplayInformationLowerBound:
    """Exact adaptive information floor for the P19 two-class null family.

    Frozen family:
      * every old threshold is p;
      * low vertices have null-new threshold p+s;
      * high vertices have null-new threshold p+s+tau;
      * alternative x increases one high vertex by d.

    Every fairness edge crosses high/low classes, so the null is exactly at
    tolerance tau and alternative x violates every edge incident to x by d.

    For a legal replay group containing x:
      * if it contains another high vertex, the alternative creates a new sparse
        transcript state and the null-to-alternative KL is K_control=Theta(d);
      * if x is the only high vertex in the group, the group sees the ordinary
        threshold-boundary shift and KL is K_boundary=Theta(d^2) for fixed tau>0.
    """

    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")
    tau = float(fairness_tolerance)
    s = float(shared_patch)
    if not (0.0 < p < 1.0 and s >= 0.0 and tau >= 0.0 and d > 0.0 and p + s + tau + d < 1.0):
        raise ValueError(
            "require p in (0,1), shared_patch>=0, tau>=0, d>0, and p+shared_patch+tau+d<1"
        )

    high = _validate_bipartite_threshold_family(graph, high_vertices)
    high_set = set(high)
    gs = _canonical_groups(graph, groups)
    c = _validate_costs(gs, costs)

    r = 1.0 - p - s - tau
    k_control = r * math.log(r / (r - d))
    first = 0.0 if tau == 0.0 else tau * math.log(tau / (tau + d))
    k_boundary = first + k_control

    K = np.zeros((len(gs), len(high)), dtype=float)
    for gi, group in enumerate(gs):
        high_count = sum(v in high_set for v in group)
        for xi, x in enumerate(high):
            if x not in group:
                continue
            K[gi, xi] = k_control if high_count >= 2 else k_boundary

    if np.any(K.sum(axis=0) == 0.0):
        return ControlReplayInformationLowerBound(
            float("inf"),
            np.zeros(len(gs)),
            high,
            K,
            k_control,
            k_boundary,
            False,
            "some high-side alternative is absent from every legal replay group",
        )

    target = binary_decision_kl(beta)
    res = linprog(
        c,
        A_ub=-K.T,
        b_ub=-target * np.ones(len(high)),
        bounds=[(0.0, None)] * len(gs),
        method="highs",
    )
    if not res.success:
        return ControlReplayInformationLowerBound(
            float("inf"),
            np.zeros(len(gs)),
            high,
            K,
            k_control,
            k_boundary,
            False,
            str(res.message),
        )
    return ControlReplayInformationLowerBound(
        float(res.fun),
        np.asarray(res.x),
        high,
        K,
        k_control,
        k_boundary,
        True,
        str(res.message),
    )


def mixed_control_leading_coefficient(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    high_vertices: Iterable[int],
    *,
    p: float,
    shared_patch: float,
    fairness_tolerance: float,
    beta: float,
) -> MixedControlLeadingCoefficient:
    """Leading d^-2 coefficient for P19 alternatives lacking a control channel.

    This is an asymptotic object for the exact information lower LP, not an
    achievable testing guarantee.  For fixed positive tolerance, candidates
    with no legal matched-high control receive only boundary information with
    K_boundary(d) = b2*d^2 + O(d^3).
    """

    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")
    tau = float(fairness_tolerance)
    s = float(shared_patch)
    if not (0.0 < p < 1.0 and s >= 0.0 and tau > 0.0 and p + s + tau < 1.0):
        raise ValueError(
            "leading mixed-control coefficient requires p in (0,1), "
            "shared_patch>=0, fixed tau>0, and p+shared_patch+tau<1"
        )

    high = _validate_bipartite_threshold_family(graph, high_vertices)
    high_set = set(high)
    gs = _canonical_groups(graph, groups)
    c = _validate_costs(gs, costs)

    control = np.zeros((len(high), len(gs)), dtype=float)
    for xi, x in enumerate(high):
        for gi, group in enumerate(gs):
            if x in group and sum(v in high_set for v in group) >= 2:
                control[xi, gi] = 1.0
    uncovered_idx = tuple(i for i in range(len(high)) if control[i].sum() == 0.0)
    uncovered = tuple(high[i] for i in uncovered_idx)

    r = 1.0 - p - s - tau
    b2 = 0.5 * (1.0 / tau + 1.0 / r)
    if not uncovered:
        return MixedControlLeadingCoefficient(
            0.0,
            np.zeros(len(gs)),
            (),
            b2,
            True,
            "all high-side alternatives have a first-order control channel",
        )

    boundary = np.zeros((len(uncovered), len(gs)), dtype=float)
    for ui, xi in enumerate(uncovered_idx):
        x = high[xi]
        for gi, group in enumerate(gs):
            if x in group:
                boundary[ui, gi] = b2

    if np.any(boundary.sum(axis=1) == 0.0):
        return MixedControlLeadingCoefficient(
            float("inf"),
            np.zeros(len(gs)),
            uncovered,
            b2,
            False,
            "some control-uncovered alternative is absent from every legal replay group",
        )

    target = binary_decision_kl(beta)
    res = linprog(
        c,
        A_ub=-boundary,
        b_ub=-target * np.ones(len(uncovered)),
        bounds=[(0.0, None)] * len(gs),
        method="highs",
    )
    if not res.success:
        return MixedControlLeadingCoefficient(
            float("inf"), np.zeros(len(gs)), uncovered, b2, False, str(res.message)
        )
    return MixedControlLeadingCoefficient(
        float(res.fun), np.asarray(res.x), uncovered, b2, True, str(res.message)
    )


def mixed_control_asymptotic_coefficients(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    high_vertices: Iterable[int],
    *,
    p: float,
    shared_patch: float,
    fairness_tolerance: float,
    beta: float,
) -> MixedControlAsymptoticCoefficients:
    """Return the exact d^-2 and d^-1 coefficients of the P19 lower LP.

    A high candidate without a matched-control group cannot share any legal
    group with another high candidate: such a group would itself be a matched
    control.  Its boundary-only LP block therefore separates exactly and uses
    its cheapest containing group.  The remaining control-covered block has
    the fractional-control-cover cost as its d^-1 coefficient.  The d^-1 term
    also includes the cubic curvature of the boundary KL.
    """

    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")
    tau = float(fairness_tolerance)
    s = float(shared_patch)
    if not (0.0 < p < 1.0 and s >= 0.0 and tau > 0.0 and p + s + tau < 1.0):
        raise ValueError(
            "mixed-control coefficients require p in (0,1), "
            "shared_patch>=0, fixed tau>0, and p+shared_patch+tau<1"
        )

    high = _validate_bipartite_threshold_family(graph, high_vertices)
    high_set = set(high)
    gs = _canonical_groups(graph, groups)
    c = _validate_costs(gs, costs)

    control = np.zeros((len(high), len(gs)), dtype=float)
    contains = np.zeros((len(high), len(gs)), dtype=float)
    for xi, x in enumerate(high):
        for gi, group in enumerate(gs):
            if x not in group:
                continue
            contains[xi, gi] = 1.0
            if sum(v in high_set for v in group) >= 2:
                control[xi, gi] = 1.0

    uncovered_idx = tuple(i for i in range(len(high)) if control[i].sum() == 0.0)
    covered_idx = tuple(i for i in range(len(high)) if control[i].sum() > 0.0)
    uncovered = tuple(high[i] for i in uncovered_idx)
    covered = tuple(high[i] for i in covered_idx)

    boundary_minimum_cost = 0.0
    for xi in uncovered_idx:
        eligible = np.flatnonzero(contains[xi] > 0.0)
        if len(eligible) == 0:
            return MixedControlAsymptoticCoefficients(
                float("inf"),
                float("inf"),
                uncovered,
                covered,
                float("inf"),
                float("inf"),
                math.nan,
                math.nan,
                False,
                "some control-uncovered alternative is absent from every legal group",
            )
        # By definition of ``uncovered``, each eligible group contains exactly
        # one high candidate and hence belongs to no other high constraint.
        boundary_minimum_cost += float(np.min(c[eligible]))

    control_cover_cost = 0.0
    if covered_idx:
        A = control[np.asarray(covered_idx), :]
        res = linprog(
            c,
            A_ub=-A,
            b_ub=-np.ones(len(covered_idx)),
            bounds=[(0.0, None)] * len(gs),
            method="highs",
        )
        if not res.success:
            return MixedControlAsymptoticCoefficients(
                float("inf"),
                float("inf"),
                uncovered,
                covered,
                boundary_minimum_cost,
                float("inf"),
                math.nan,
                math.nan,
                False,
                str(res.message),
            )
        control_cover_cost = float(res.fun)

    r = 1.0 - p - s - tau
    b2 = 0.5 * (1.0 / tau + 1.0 / r)
    b3 = (1.0 / 3.0) * (1.0 / (r * r) - 1.0 / (tau * tau))
    target = binary_decision_kl(beta)
    inverse_square = target * boundary_minimum_cost / b2
    inverse_linear = target * (control_cover_cost - b3 * boundary_minimum_cost / (b2 * b2))
    return MixedControlAsymptoticCoefficients(
        inverse_square,
        inverse_linear,
        uncovered,
        covered,
        boundary_minimum_cost,
        control_cover_cost,
        b2,
        b3,
        True,
        "exact finite-family singular coefficients",
    )


def mixed_control_replay_schedule(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    high_vertices: Iterable[int],
    *,
    p: float,
    shared_patch: float,
    fairness_tolerance: float,
    d: float,
    beta: float,
) -> MixedControlReplaySchedule:
    """Construct an order-matching hybrid schedule for mixed P19 topologies.

    Let U contain the high candidates with no legal group containing a second
    high control.  Every group containing x in U then contains x as its only
    high member and at least one low member.  Under P19's frozen two-class null,
    a new-version high/low mismatch in that group is Bernoulli(tau), and under
    singleton alternative x it is Bernoulli(tau+d).  A P18 boundary test on the
    cheapest such group therefore handles x.  A residual fractional control
    cover handles the candidates in A minus U with zero type-I error.

    Boundary tests split the global type-I budget equally over U.  Type-II
    control is pointwise over singleton alternatives, so the residual control
    schedule uses beta directly.  The construction matches the finite-topology
    d^-2/d^-1 orders, not exact minimax constants or arbitrary |U| dependence.
    """

    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")
    if not (0.0 < d < 1.0):
        raise ValueError("d must lie in (0,1)")
    if fairness_tolerance <= 0.0:
        raise ValueError("P19 mixed schedule requires fixed fairness_tolerance>0")
    # Validate the full P19 threshold parameter range even when U is empty.
    threshold_fairness_replay_bounds(
        p,
        shared_patch,
        fairness_tolerance,
        d,
        beta,
    )

    high = _validate_bipartite_threshold_family(graph, high_vertices)
    high_set = set(high)
    gs = _canonical_groups(graph, groups)
    c = _validate_costs(gs, costs)

    control = np.zeros((len(high), len(gs)), dtype=float)
    contains = np.zeros((len(high), len(gs)), dtype=float)
    for xi, x in enumerate(high):
        for gi, group in enumerate(gs):
            if x not in group:
                continue
            contains[xi, gi] = 1.0
            if sum(v in high_set for v in group) >= 2:
                control[xi, gi] = 1.0

    uncovered_idx = tuple(i for i in range(len(high)) if control[i].sum() == 0.0)
    covered_idx = tuple(i for i in range(len(high)) if control[i].sum() > 0.0)
    uncovered = tuple(high[i] for i in uncovered_idx)
    covered = tuple(high[i] for i in covered_idx)
    counts = np.zeros(len(gs), dtype=int)

    boundary_group_indices: list[int] = []
    boundary_minimum_cost = 0.0
    boundary_rounds = 0
    boundary_error_budget = 0.0
    if uncovered_idx:
        boundary_error_budget = beta / len(uncovered_idx)
        boundary_rounds = threshold_fairness_replay_bounds(
            p,
            shared_patch,
            fairness_tolerance,
            d,
            boundary_error_budget,
        ).replay_upper_rounds
        for xi in uncovered_idx:
            eligible = np.flatnonzero(contains[xi] > 0.0)
            if len(eligible) == 0:
                raise ValueError(
                    "some control-uncovered alternative is absent from every legal group"
                )
            gi = int(eligible[np.argmin(c[eligible])])
            # Since x is control-uncovered, this group contains no second high.
            # Group size is at least two, so it contains a low reference.
            if sum(v in high_set for v in gs[gi]) != 1:
                raise RuntimeError("uncovered candidate group is not boundary-only")
            boundary_group_indices.append(gi)
            boundary_minimum_cost += float(c[gi])
            counts[gi] += boundary_rounds

    residual_control_cover_cost = 0.0
    control_scale = 0
    additive_control_rounding_cap = 0.0
    if covered_idx:
        A = control[np.asarray(covered_idx), :]
        res = linprog(
            c,
            A_ub=-A,
            b_ub=-np.ones(len(covered_idx)),
            bounds=[(0.0, None)] * len(gs),
            method="highs",
        )
        if not res.success:
            raise ValueError(str(res.message))
        weights = np.asarray(res.x)
        residual_control_cover_cost = float(res.fun)
        control_scale = math.ceil(math.log(beta) / math.log1p(-d))
        control_counts = np.ceil(control_scale * weights - 1e-12).astype(int)
        counts += control_counts
        for xi in covered_idx:
            exposure = int(control[xi] @ control_counts)
            if exposure < control_scale:
                raise RuntimeError("rounded residual control schedule failed exposure")
        support = weights > 1e-12
        additive_control_rounding_cap = float(c[support].sum())

    return MixedControlReplaySchedule(
        counts=counts,
        total_cost=float(c @ counts),
        uncovered_high_vertices=uncovered,
        covered_high_vertices=covered,
        boundary_group_indices=tuple(boundary_group_indices),
        boundary_rounds_per_candidate=boundary_rounds,
        boundary_error_budget_per_candidate=boundary_error_budget,
        boundary_minimum_cost=boundary_minimum_cost,
        residual_control_cover_cost=residual_control_cover_cost,
        control_scale=control_scale,
        additive_control_rounding_cap=additive_control_rounding_cap,
    )


def boundary_familywise_fixed_design_lower_bound(
    candidates: int,
    *,
    p: float,
    shared_patch: float,
    fairness_tolerance: float,
    d: float,
    beta: float,
    unit_cost: float = 1.0,
) -> BoundaryFamilywiseFixedDesignLowerBound:
    """Lower bound the fixed-design cost of m disjoint boundary alternatives.

    This scoped subfamily has exactly one independent boundary-only transcript
    channel per candidate.  Under alternative i, only channel i changes.  For
    any subset of k candidates, the uniform mixture must be separated from the
    null by total variation at least 1-2*beta.  Its chi-square divergence is

        k^-2 * sum_i (exp(rho2*n_i) - 1),

    where rho2 is the one-query order-2 Renyi divergence and n_i is the fixed
    query count for channel i. Data processing through the reject/accept event
    requires chi-square divergence at least

        D_beta = (1-2*beta)^2 / (beta*(1-beta)).

    Sorting the counts and applying the inequality to every prefix gives

        n_(k) >= log(1 + D_beta*k) / rho2.

    The result proves the m*log(m)/d^2 familywise term for fixed positive
    tolerance and fixed beta.  It does not cover adaptive designs, shared
    groups, heterogeneous costs, or broader composite nulls.
    """

    if isinstance(candidates, bool) or not isinstance(candidates, int) or candidates < 1:
        raise ValueError("candidates must be a positive integer")
    if not (math.isfinite(unit_cost) and unit_cost > 0.0):
        raise ValueError("unit_cost must be finite and positive")
    if fairness_tolerance <= 0.0:
        raise ValueError("familywise boundary lower bound requires fixed tolerance>0")
    threshold_fairness_replay_bounds(
        p,
        shared_patch,
        fairness_tolerance,
        d,
        beta,
    )

    r = 1.0 - p - shared_patch - fairness_tolerance
    transcript_renyi2 = math.log1p(
        d * d * (1.0 / fairness_tolerance + 1.0 / r)
    )
    separation = (1.0 - 2.0 * beta) ** 2 / (beta * (1.0 - beta))
    ranks = np.arange(1, candidates + 1, dtype=float)
    floors = np.log1p(separation * ranks) / transcript_renyi2
    total = float(floors.sum())
    return BoundaryFamilywiseFixedDesignLowerBound(
        candidates=candidates,
        transcript_renyi2=transcript_renyi2,
        sorted_query_count_floors=floors,
        total_query_floor=total,
        total_cost_floor=unit_cost * total,
    )


def boundary_familywise_sequential_bounds(
    costs: Sequence[float],
    *,
    p: float,
    shared_patch: float,
    fairness_tolerance: float,
    d: float,
    beta: float,
) -> BoundaryFamilywiseSequentialBounds:
    """Bound a familywise two-sided SPRT on exact P19 boundary transcripts.

    For m disjoint singleton alternatives, process one likelihood ratio per
    candidate.  Reject if any ratio reaches A=m/beta; move to the next candidate
    when its ratio reaches B=beta; accept after all m lower crossings.  Ville's
    inequality gives global type-I and pointwise type-II errors at most beta.

    The null drift is -KL(P0||P1), so a bounded-overshoot Wald argument makes
    the expected null rounds per candidate independent of A and hence of m.
    The changed channel retains a log(m/beta) delay.  Stopping time is unbounded;
    deterministic fixed designs remain subject to the familywise log(m) lower
    bound above.  The returned null lower bound is the exact pairwise
    information floor, summed over disjoint channels.  The two small-gap
    coefficients expose the remaining confidence-only constant gap.
    """

    c = np.asarray(costs, dtype=float)
    if c.ndim != 1 or len(c) < 1 or np.any(c <= 0.0) or np.any(~np.isfinite(c)):
        raise ValueError("costs must be a nonempty vector of finite positive values")
    if fairness_tolerance <= 0.0:
        raise ValueError("familywise sequential bound requires fixed tolerance>0")
    threshold_fairness_replay_bounds(
        p,
        shared_patch,
        fairness_tolerance,
        d,
        beta,
    )

    tau = float(fairness_tolerance)
    r = 1.0 - p - shared_patch - tau
    null_to_alt = tau * math.log(tau / (tau + d)) + r * math.log(r / (r - d))
    alt_to_null = (tau + d) * math.log((tau + d) / tau) + (r - d) * math.log(
        (r - d) / r
    )
    m = len(c)
    upper = m / beta
    lower = beta
    null_rounds = (
        math.log(1.0 / beta) + math.log(r / (r - d))
    ) / null_to_alt
    changed_rounds = (
        math.log(m / beta) + math.log1p(d / tau)
    ) / alt_to_null
    total_cost = float(c.sum())
    decision_kl = binary_decision_kl(beta)
    null_cost_lower = decision_kl * total_cost / null_to_alt
    b2 = 0.5 * (1.0 / tau + 1.0 / r)
    small_gap_lower = decision_kl * total_cost / b2
    small_gap_upper = math.log(1.0 / beta) * total_cost / b2
    alternative_cost = null_rounds * (total_cost - c) + changed_rounds * c
    return BoundaryFamilywiseSequentialBounds(
        candidates=m,
        upper_likelihood_threshold=upper,
        lower_likelihood_threshold=lower,
        null_to_alternative_kl=null_to_alt,
        alternative_to_null_kl=alt_to_null,
        null_expected_rounds_per_candidate_upper=null_rounds,
        changed_expected_rounds_upper=changed_rounds,
        null_expected_total_cost_lower=null_cost_lower,
        null_expected_total_cost_upper=null_rounds * total_cost,
        alternative_expected_cost_upper=alternative_cost,
        small_gap_lower_cost_coefficient=small_gap_lower,
        small_gap_upper_cost_coefficient=small_gap_upper,
        asymptotic_confidence_gap_ratio=small_gap_upper / small_gap_lower,
    )


def boundary_familywise_truncated_sequential_bounds(
    costs: Sequence[float],
    *,
    p: float,
    shared_patch: float,
    fairness_tolerance: float,
    d: float,
    beta: float,
    internal_error: float | None = None,
) -> BoundaryFamilywiseTruncatedSequentialBounds:
    """Bound a deterministic-cost truncation of the familywise SPRT.

    Run the unbounded sequential test with error ``eta < beta`` and accept the
    null before the next query would make declared cost exceed ``C``.  Under
    singleton alternative i, Markov's inequality bounds the added truncation
    miss probability by ``E_i[cost] / C``.  Taking

        C = max_i E_i[cost] / (beta - eta)

    therefore preserves pointwise error beta, while truncation cannot increase
    type-I error.  At fixed beta and interior P19 parameters, the resulting cap
    is O((sum(costs) + max(costs)*log(m))/d^2).  For unit costs this is O(m/d^2),
    so adaptive allocation removes the fixed-design m*log(m) penalty even with
    a deterministic declared-cost horizon.  The bound uses Markov truncation;
    it is not claimed to have optimal beta dependence or exact constants.
    """

    eta = beta / 2.0 if internal_error is None else float(internal_error)
    if not (math.isfinite(eta) and 0.0 < eta < beta):
        raise ValueError("internal_error must lie strictly between zero and beta")

    sequential = boundary_familywise_sequential_bounds(
        costs,
        p=p,
        shared_patch=shared_patch,
        fairness_tolerance=fairness_tolerance,
        d=d,
        beta=eta,
    )
    c = np.asarray(costs, dtype=float)
    error_budget = beta - eta
    worst = int(np.argmax(sequential.alternative_expected_cost_upper))
    cap = float(sequential.alternative_expected_cost_upper[worst] / error_budget)

    tau = float(fairness_tolerance)
    r = 1.0 - p - shared_patch - tau
    b2 = 0.5 * (1.0 / tau + 1.0 / r)
    null_coefficient = math.log(1.0 / eta) / b2
    changed_coefficient = math.log(len(c) / eta) / b2
    alternative_coefficients = (
        null_coefficient * (float(c.sum()) - c) + changed_coefficient * c
    )

    return BoundaryFamilywiseTruncatedSequentialBounds(
        candidates=len(c),
        target_error=beta,
        internal_error=eta,
        truncation_error_budget=error_budget,
        declared_cost_cap=cap,
        worst_alternative_index=worst,
        null_expected_total_cost_upper=sequential.null_expected_total_cost_upper,
        alternative_expected_cost_upper=sequential.alternative_expected_cost_upper,
        type_i_error_upper=eta,
        pointwise_type_ii_error_upper=eta + error_budget,
        small_gap_declared_cost_cap_coefficient=float(
            alternative_coefficients.max() / error_budget
        ),
    )


def matched_control_replay_schedule(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    high_vertices: Iterable[int],
    *,
    d: float,
    beta: float,
) -> ControlReplaySchedule:
    """Schedule matched-background controls with zero type-I error.

    In every queried group, the tester compares old/new patch deltas only among
    high-class members.  Under the P19 null those deltas are identical pathwise.
    If x is the changed high vertex, every control-compatible query containing x
    exposes a nonconstant high-class delta vector with probability d.
    """

    if not (0.0 < d < 1.0):
        raise ValueError("d must lie in (0,1)")
    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")

    gs = _canonical_groups(graph, groups)
    c = _validate_costs(gs, costs)
    cover = minimum_fractional_control_cover(graph, gs, c, high_vertices)
    if not cover.success:
        raise ValueError(cover.message)

    L = math.ceil(math.log(beta) / math.log1p(-d))
    counts = np.ceil(L * cover.weights - 1e-12).astype(int)
    high_set = set(cover.high_vertices)

    for x in cover.high_vertices:
        exposure = sum(
            int(counts[i])
            for i, group in enumerate(gs)
            if x in group and sum(v in high_set for v in group) >= 2
        )
        if exposure < L:
            raise RuntimeError("rounded control schedule failed a high-candidate exposure")

    total = float(c @ counts)
    support = cover.weights > 1e-12
    return ControlReplaySchedule(
        normalized_control_cover_cost=cover.cost,
        scale=L,
        counts=counts,
        total_cost=total,
        additive_rounding_cap=float(c[support].sum()),
        high_vertices=cover.high_vertices,
    )


def matched_control_contrast_witness(
    old_outputs: Sequence[float],
    new_outputs: Sequence[float],
    high_mask: Sequence[bool],
) -> bool:
    """Whether a synchronized group exposes disagreement among high controls."""

    old = np.asarray(old_outputs)
    new = np.asarray(new_outputs)
    mask = np.asarray(high_mask, dtype=bool)
    if (
        old.ndim != 1
        or new.ndim != 1
        or mask.ndim != 1
        or old.shape != new.shape
        or old.shape != mask.shape
    ):
        raise ValueError("old_outputs, new_outputs, and high_mask must align")
    if int(mask.sum()) < 2:
        raise ValueError("matched-control witness requires at least two high members")
    delta = (new - old)[mask]
    return bool(np.any(delta != delta[0]))
