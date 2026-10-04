from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint

from .graphs import GraphSpec


@dataclass(frozen=True)
class ReplayGroupCover:
    """Minimum-cost integral cover of fairness edges by legal replay groups."""

    objective: float
    selected: tuple[int, ...]
    success: bool
    message: str


@dataclass(frozen=True)
class GroupReplayUpperBound:
    """Audited fixed-design upper bound for partial synchronized replay."""

    cover_cost_per_round: float
    groups_selected: tuple[int, ...]
    rounds: int
    total_cost: float


def _canonical_groups(graph: GraphSpec, groups: Iterable[Iterable[int]]) -> tuple[tuple[int, ...], ...]:
    out = []
    for raw in groups:
        g = tuple(sorted(set(int(v) for v in raw)))
        if len(g) < 2:
            raise ValueError("every replay group must contain at least two vertices")
        if any(v < 0 or v >= graph.n for v in g):
            raise ValueError("replay group contains an out-of-range vertex")
        out.append(g)
    if not out:
        raise ValueError("at least one replay group is required")
    return tuple(out)


def minimum_replay_group_cover(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    costs: Sequence[float] | None = None,
) -> ReplayGroupCover:
    """Solve the exact integral edge-cover problem induced by legal replay groups.

    A group covers edge (u,v) iff it contains both endpoints, which is exactly
    what is needed to form a same-tape four-way counterfactual witness for that
    edge. This is deliberately different from the old fractional-vertex-cover
    conjecture, where observing only one endpoint was incorrectly treated as
    sufficient for the P15 oracle.
    """

    gs = _canonical_groups(graph, groups)
    k = len(gs)
    c = np.ones(k, dtype=float) if costs is None else np.asarray(costs, dtype=float)
    if c.shape != (k,) or np.any(c <= 0) or np.any(~np.isfinite(c)):
        raise ValueError("costs must be finite, positive, and match groups")
    if graph.m == 0:
        return ReplayGroupCover(0.0, tuple(), True, "edgeless graph")

    A = np.zeros((graph.m, k), dtype=float)
    for ei, (u, v) in enumerate(graph.edges):
        for gi, g in enumerate(gs):
            S = set(g)
            if u in S and v in S:
                A[ei, gi] = 1.0
    if np.any(A.sum(axis=1) == 0):
        return ReplayGroupCover(math.inf, tuple(), False, "some fairness edge is not jointly replayable")

    res = milp(
        c=c,
        integrality=np.ones(k),
        bounds=Bounds(np.zeros(k), np.ones(k)),
        constraints=LinearConstraint(A, np.ones(graph.m), np.full(graph.m, np.inf)),
        options={"disp": False},
    )
    if not res.success:
        return ReplayGroupCover(math.inf, tuple(), False, str(res.message))
    x = np.rint(res.x).astype(int)
    selected = tuple(int(i) for i in np.flatnonzero(x))
    return ReplayGroupCover(float(c @ x), selected, True, str(res.message))


def partial_synchronized_replay_upper_bound(
    graph: GraphSpec,
    groups: Iterable[Iterable[int]],
    d: float,
    beta: float,
    costs: Sequence[float] | None = None,
) -> GroupReplayUpperBound:
    """Safe fixed-design bound for the homogeneous sparse-witness family.

    In every macro-round execute each selected legal group once with an
    independent tape. Within a group, synchronize that tape across both versions
    and every member. Because the selected groups jointly cover every fairness
    edge, every legal single-edge alternative has at least one selected group
    containing both endpoints. Its P15 witness appears in that group with
    probability d per macro-round. Thus T=ceil(log(beta)/log(1-d)) macro-rounds
    give miss probability at most beta, with zero false positives under the
    homogeneous null.

    This is an UPPER BOUND only. It does not assert that the integral group cover
    is minimax optimal.
    """

    if not (0.0 < d < 1.0):
        raise ValueError("d must lie in (0,1)")
    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")
    cover = minimum_replay_group_cover(graph, groups, costs)
    if not cover.success:
        raise ValueError(cover.message)
    rounds = 0 if graph.m == 0 else math.ceil(math.log(beta) / math.log1p(-d))
    return GroupReplayUpperBound(
        cover_cost_per_round=cover.objective,
        groups_selected=cover.selected,
        rounds=rounds,
        total_cost=cover.objective * rounds,
    )
