from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import linprog

from .graphs import GraphSpec
from .partial_replay import _canonical_groups
from .separations import binary_decision_kl


@dataclass(frozen=True)
class FractionalReplayCover:
    """Minimum-cost fractional edge cover by legal replay groups."""

    cost: float
    weights: np.ndarray
    success: bool
    message: str


def minimum_fractional_replay_cover(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
) -> FractionalReplayCover:
    """Solve the replay-group fractional cover independently of any test bound."""
    gs = _canonical_groups(graph, groups)
    c = np.asarray(costs, dtype=float)
    if c.shape != (len(gs),) or np.any(c <= 0) or np.any(~np.isfinite(c)):
        raise ValueError("costs must be finite, positive, and match groups")
    if graph.m == 0:
        return FractionalReplayCover(0.0, np.zeros(len(gs)), True, "edgeless graph")
    A = np.zeros((graph.m, len(gs)), dtype=float)
    for ei, (u, v) in enumerate(graph.edges):
        for gi, g in enumerate(gs):
            if u in g and v in g:
                A[ei, gi] = -1.0
    if np.any((-A).sum(axis=1) == 0):
        return FractionalReplayCover(float("inf"), np.zeros(len(gs)), False,
                                     "some fairness edge is not jointly replayable")
    res = linprog(c, A_ub=A, b_ub=-np.ones(graph.m),
                  bounds=[(0.0, None)] * len(gs), method="highs")
    if not res.success:
        return FractionalReplayCover(float("inf"), np.zeros(len(gs)), False, str(res.message))
    return FractionalReplayCover(float(res.fun), np.asarray(res.x), True, str(res.message))


@dataclass(frozen=True)
class FractionalReplayLowerBound:
    """LP consequence of edge-indexed transcript-KL constraints."""

    normalized_cost: float
    query_weights: np.ndarray
    expected_cost_floor: float
    success: bool
    message: str


def fractional_group_replay_lower_bound(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    per_informative_query_kl: float,
    beta: float,
) -> FractionalReplayLowerBound:
    """Compute a rigorous lower-bound relaxation under the frozen P17 oracle.

    For every edge alternative e, only legal groups containing both endpoints
    have a changed observation law. If each such query contributes exactly K
    null-to-alternative KL and all other groups contribute zero, adaptive
    transcript change of measure implies

        sum_{S contains e} E_0[N_S] >= kl(1-beta,beta)/K.

    Minimizing expected query cost under all edge constraints gives the
    fractional edge-by-group cover LP below. This function does not claim that
    the floor is achievable.
    """

    if graph.m == 0:
        return FractionalReplayLowerBound(0.0, np.zeros(0), 0.0, True, "edgeless graph")
    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")
    if per_informative_query_kl <= 0:
        raise ValueError("per_informative_query_kl must be positive")

    gs = _canonical_groups(graph, groups)
    cover = minimum_fractional_replay_cover(graph, gs, costs)
    if not cover.success:
        return FractionalReplayLowerBound(
            float("inf"), cover.weights, float("inf"), False, cover.message
        )

    scale = binary_decision_kl(beta) / per_informative_query_kl
    return FractionalReplayLowerBound(
        normalized_cost=cover.cost,
        query_weights=cover.weights,
        expected_cost_floor=cover.cost * scale,
        success=True,
        message=cover.message,
    )


@dataclass(frozen=True)
class FractionalReplaySchedule:
    """Integer schedule obtained by scaling and rounding a fractional cover."""

    normalized_fractional_cost: float
    scale: int
    counts: np.ndarray
    total_cost: float
    additive_rounding_cap: float


def fractional_replay_schedule(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    d: float,
    beta: float,
) -> FractionalReplaySchedule:
    """Construct a fixed-confidence schedule from the fractional group cover.

    The LP weights a_S cover every edge to total weight at least one. Scaling by
    L=ceil(log(beta)/log(1-d)) and rounding each group count upward guarantees
    at least L independent informative group queries for every edge alternative.
    Hence the miss probability is at most (1-d)^L <= beta.
    """

    if not (0.0 < d < 1.0):
        raise ValueError("d must lie in (0,1)")
    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")
    gs = _canonical_groups(graph, groups)
    c = np.asarray(costs, dtype=float)
    if c.shape != (len(gs),) or np.any(c <= 0) or np.any(~np.isfinite(c)):
        raise ValueError("costs must be finite, positive, and match groups")
    if graph.m == 0:
        return FractionalReplaySchedule(0.0, 0, np.zeros(len(gs), dtype=int), 0.0, 0.0)

    cover = minimum_fractional_replay_cover(graph, gs, c)
    if not cover.success:
        raise ValueError(cover.message)
    L = math.ceil(math.log(beta) / math.log1p(-d))
    counts = np.ceil(L * cover.weights - 1e-12).astype(int)

    # Defensive verification of the actual integer schedule.
    for u, v in graph.edges:
        exposure = sum(
            int(counts[i]) for i, g in enumerate(gs) if u in g and v in g
        )
        if exposure < L:
            raise RuntimeError("rounded schedule failed an edge exposure constraint")

    total = float(c @ counts)
    active = cover.weights > 1e-12
    rounding_cap = float(c[active].sum())
    return FractionalReplaySchedule(
        normalized_fractional_cost=cover.cost,
        scale=L,
        counts=counts,
        total_cost=total,
        additive_rounding_cap=rounding_cap,
    )


@dataclass(frozen=True)
class RawOutputInformationLowerBound:
    """Transcript-KL allocation floor for the homogeneous raw-output P17 oracle."""

    expected_cost_floor: float
    expected_query_counts: np.ndarray
    alternatives: tuple[tuple[int, int, int], ...]
    information_matrix: np.ndarray
    success: bool
    message: str


def raw_output_information_lower_bound(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    *,
    p: float,
    shared_patch: float,
    d: float,
    beta: float,
) -> RawOutputInformationLowerBound:
    """Lower-bound null expected cost using the *actual raw-output* group KL.

    Alternatives are oriented fairness edges: (u,v,u) and (u,v,v), meaning one
    endpoint receives the additional differential shift d.  Under the homogeneous
    threshold family, a group has:
      * zero KL if it omits the changed endpoint;
      * vertex-paired KL if it is the singleton changed endpoint;
      * joint KL if it contains the changed endpoint and any second unchanged
        vertex.

    The last case is important: the second vertex need not be the fairness
    partner.  This is exactly why the earlier edge-incidence fractional-cover
    lower bound is invalid for the raw-output oracle.
    """
    s = float(shared_patch)
    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")
    if not (p > 0.0 and s > 0.0 and d > 0.0 and p + s + d < 1.0):
        raise ValueError("require p>0, shared_patch>0, d>0, and p+shared_patch+d<1")

    gs = _canonical_groups(graph, groups)
    cost = np.asarray(costs, dtype=float)
    if cost.shape != (len(gs),) or np.any(cost <= 0) or np.any(~np.isfinite(cost)):
        raise ValueError("costs must be finite, positive, and match groups")

    alternatives = tuple(
        (u, v, changed)
        for (u, v) in graph.edges
        for changed in (u, v)
    )
    if not alternatives:
        return RawOutputInformationLowerBound(
            0.0, np.zeros(len(gs)), alternatives,
            np.zeros((len(gs), 0)), True, "edgeless graph"
        )

    r = 1.0 - p - s
    k_joint = r * math.log(r / (r - d))
    k_vertex = s * math.log(s / (s + d)) + r * math.log(r / (r - d))

    K = np.zeros((len(gs), len(alternatives)), dtype=float)
    for gi, group in enumerate(gs):
        S = set(group)
        for ai, (_, _, changed) in enumerate(alternatives):
            if changed not in S:
                continue
            K[gi, ai] = k_vertex if len(S) == 1 else k_joint

    if np.any(K.sum(axis=0) <= 0.0):
        return RawOutputInformationLowerBound(
            float("inf"), np.zeros(len(gs)), alternatives, K, False,
            "some oriented edge alternative has zero information under all legal groups",
        )

    target = binary_decision_kl(beta)
    res = linprog(
        cost,
        A_ub=-K.T,
        b_ub=-target * np.ones(len(alternatives)),
        bounds=[(0.0, None)] * len(gs),
        method="highs",
    )
    if not res.success:
        return RawOutputInformationLowerBound(
            float("inf"), np.zeros(len(gs)), alternatives, K, False, str(res.message)
        )
    return RawOutputInformationLowerBound(
        float(res.fun), np.asarray(res.x), alternatives, K, True, str(res.message)
    )
