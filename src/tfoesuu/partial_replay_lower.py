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
    """Withdrawn P17 lower-bound helper.

    This routine used an edge-by-group incidence relaxation that is valid for
    witness scheduling but is not a lower bound for the frozen raw-output
    oracle: a legal group containing the perturbed endpoint can carry KL even
    when it omits the endpoint's fairness partner.

    Use raw_output_information_lower_bound for the audited necessary
    information-allocation floor. Keeping this symbol as an explicit failure
    prevents older scripts from silently reporting the withdrawn quantity as a
    theorem-level lower bound.
    """
    raise RuntimeError(
        "fractional_group_replay_lower_bound is withdrawn for the raw-output "
        "P17 oracle; use raw_output_information_lower_bound instead"
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
class FractionalActiveVertexCover:
    """Minimum-cost fractional cover of fairness-active vertices by legal groups."""

    cost: float
    weights: np.ndarray
    active_vertices: tuple[int, ...]
    success: bool
    message: str


def minimum_fractional_active_vertex_cover(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
) -> FractionalActiveVertexCover:
    """Solve the active-vertex/group incidence LP used by the P17 information floor."""
    gs = _canonical_groups(graph, groups)
    c = np.asarray(costs, dtype=float)
    if c.shape != (len(gs),) or np.any(c <= 0) or np.any(~np.isfinite(c)):
        raise ValueError("costs must be finite, positive, and match groups")

    active = tuple(sorted({v for edge in graph.edges for v in edge}))
    if not active:
        return FractionalActiveVertexCover(
            0.0, np.zeros(len(gs)), active, True, "edgeless graph"
        )

    B = np.zeros((len(active), len(gs)), dtype=float)
    for xi, x in enumerate(active):
        for gi, group in enumerate(gs):
            if x in group:
                B[xi, gi] = 1.0

    if np.any(B.sum(axis=1) == 0.0):
        return FractionalActiveVertexCover(
            float("inf"), np.zeros(len(gs)), active, False,
            "some fairness-active vertex is absent from every legal replay group",
        )

    res = linprog(
        c,
        A_ub=-B,
        b_ub=-np.ones(len(active)),
        bounds=[(0.0, None)] * len(gs),
        method="highs",
    )
    if not res.success:
        return FractionalActiveVertexCover(
            float("inf"), np.zeros(len(gs)), active, False, str(res.message)
        )
    return FractionalActiveVertexCover(
        float(res.fun), np.asarray(res.x), active, True, str(res.message)
    )


def raw_group_contrast_witness(
    old_outputs: Sequence[float],
    new_outputs: Sequence[float],
) -> bool:
    """Return whether synchronized group outputs expose unequal patch deltas.

    The P17 homogeneous Bernoulli contrast tester rejects when the vector
    P1(v;U)-P0(v;U) is nonconstant within a queried legal replay group.
    Legal groups contain at least two vertices.  This predicate is deliberately
    observation-level and makes no distributional claim by itself.
    """
    old = np.asarray(old_outputs)
    new = np.asarray(new_outputs)
    if old.ndim != 1 or new.ndim != 1 or old.shape != new.shape:
        raise ValueError("old_outputs and new_outputs must be equal-length vectors")
    if old.size < 2:
        raise ValueError("a contrast witness requires at least two group members")
    delta = new - old
    return bool(np.any(delta != delta[0]))


@dataclass(frozen=True)
class ActiveVertexContrastSchedule:
    """Fixed-design raw-output contrast schedule for the frozen P17 family."""

    normalized_fractional_cost: float
    scale: int
    counts: np.ndarray
    total_cost: float
    additive_rounding_cap: float
    active_vertices: tuple[int, ...]


def active_vertex_contrast_schedule(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float],
    d: float,
    beta: float,
) -> ActiveVertexContrastSchedule:
    """Schedule legal groups from the active-vertex cover.

    This construction is valid for the frozen homogeneous P17 Bernoulli family:
    under the null every active vertex has old threshold p and new threshold
    p+s; under an oriented alternative exactly one fairness-active endpoint x
    has new threshold p+s+d and every other vertex remains at p+s.

    In a legal group containing x, compare the old/new patch deltas across group
    members.  Because every legal group has at least two vertices and x is the
    unique changed endpoint, the group contains an unchanged synchronized
    reference.  Under the null all patch deltas are identical pathwise.  Under
    the alternative, a contrast witness appears with probability d on each
    independent query containing x.

    The function returns only the deterministic query counts.  It does not claim
    validity for broader heterogeneous fairness-preserving null classes.
    """
    if not (0.0 < d < 1.0):
        raise ValueError("d must lie in (0,1)")
    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")

    gs = _canonical_groups(graph, groups)
    cost = np.asarray(costs, dtype=float)
    if cost.shape != (len(gs),) or np.any(cost <= 0) or np.any(~np.isfinite(cost)):
        raise ValueError("costs must be finite, positive, and match groups")

    cover = minimum_fractional_active_vertex_cover(graph, gs, cost)
    if not cover.success:
        raise ValueError(cover.message)
    if not cover.active_vertices:
        return ActiveVertexContrastSchedule(
            0.0, 0, np.zeros(len(gs), dtype=int), 0.0, 0.0, cover.active_vertices
        )

    L = math.ceil(math.log(beta) / math.log1p(-d))
    counts = np.ceil(L * cover.weights - 1e-12).astype(int)

    for x in cover.active_vertices:
        exposure = sum(int(counts[i]) for i, group in enumerate(gs) if x in group)
        if exposure < L:
            raise RuntimeError("rounded contrast schedule failed an active-vertex exposure")

    total = float(cost @ counts)
    support = cover.weights > 1e-12
    rounding_cap = float(cost[support].sum())
    return ActiveVertexContrastSchedule(
        normalized_fractional_cost=cover.cost,
        scale=L,
        counts=counts,
        total_cost=total,
        additive_rounding_cap=rounding_cap,
        active_vertices=cover.active_vertices,
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
    endpoint receives the additional differential shift d.  The frozen P17 oracle
    permits replay groups of size at least two.  Under the homogeneous threshold
    family, a legal group therefore has:
      * zero KL if it omits the changed endpoint;
      * joint KL if it contains the changed endpoint.

    The second synchronized vertex need not be the fairness partner.  This is
    exactly why the earlier edge-incidence fractional-cover lower bound is invalid
    for the raw-output oracle.
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

    # Legal replay groups have size at least two, so every informative group has
    # the same null-to-alternative KL.  The raw-output information geometry thus
    # depends only on group-by-active-vertex incidence, not edge incidence.
    K = np.zeros((len(gs), len(alternatives)), dtype=float)
    for gi, group in enumerate(gs):
        S = set(group)
        for ai, (_, _, changed) in enumerate(alternatives):
            if changed in S:
                K[gi, ai] = k_joint

    cover = minimum_fractional_active_vertex_cover(graph, gs, cost)
    if not cover.success:
        return RawOutputInformationLowerBound(
            float("inf"), np.zeros(len(gs)), alternatives, K, False, cover.message
        )

    target = binary_decision_kl(beta)
    scale = target / k_joint
    return RawOutputInformationLowerBound(
        expected_cost_floor=float(scale * cover.cost),
        expected_query_counts=scale * cover.weights,
        alternatives=alternatives,
        information_matrix=K,
        success=True,
        message=cover.message,
    )
