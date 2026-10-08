from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import linprog

from .graphs import GraphSpec
from .partial_replay import _canonical_groups
from .p19_numerics import certified_p19_information_allocation, stable_p19_information_rates
from .separations import binary_decision_kl


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
    """Candidate d^-2 coefficient of the exact P19 information lower LP."""

    coefficient: float
    scaled_query_weights: np.ndarray
    uncovered_high_vertices: tuple[int, ...]
    boundary_quadratic_coefficient: float
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


def _validate_bipartite_threshold_family(
    graph: GraphSpec,
    high_vertices: Iterable[int],
) -> tuple[int, ...]:
    high = tuple(sorted(set(int(v) for v in high_vertices)))
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
    return FractionalControlCover(
        float(res.fun), np.asarray(res.x), high, True, str(res.message)
    )


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
    if not (
        0.0 < p < 1.0
        and s >= 0.0
        and tau >= 0.0
        and d > 0.0
        and p + s + tau + d < 1.0
    ):
        raise ValueError(
            "require p in (0,1), shared_patch>=0, tau>=0, d>0, "
            "and p+shared_patch+tau+d<1"
        )

    high = _validate_bipartite_threshold_family(graph, high_vertices)
    high_set = set(high)
    gs = _canonical_groups(graph, groups)
    c = _validate_costs(gs, costs)

    r = 1.0 - p - s - tau
    k_control, k_boundary = stable_p19_information_rates(r, tau, d)

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
    allocation = certified_p19_information_allocation(K, c, target)
    return ControlReplayInformationLowerBound(
        allocation.cost,
        allocation.counts,
        high,
        K,
        k_control,
        k_boundary,
        allocation.success,
        allocation.message,
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
            0.0, np.zeros(len(gs)), (), b2, True,
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
            float("inf"), np.zeros(len(gs)), uncovered, b2, False,
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
            raise RuntimeError(
                "rounded control schedule failed a high-candidate exposure"
            )

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
