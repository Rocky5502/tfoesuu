from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import linprog

from .graphs import GraphSpec
from .partial_replay import _canonical_groups
from .separations import binary_decision_kl


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
    c = np.asarray(costs, dtype=float)
    if c.shape != (len(gs),) or np.any(c <= 0) or np.any(~np.isfinite(c)):
        raise ValueError("costs must be finite, positive, and match groups")

    A = np.zeros((graph.m, len(gs)), dtype=float)
    for ei, (u, v) in enumerate(graph.edges):
        for gi, g in enumerate(gs):
            S = set(g)
            if u in S and v in S:
                A[ei, gi] = -1.0
    if np.any((-A).sum(axis=1) == 0):
        return FractionalReplayLowerBound(
            float("inf"), np.zeros(len(gs)), float("inf"), False,
            "some fairness edge is not jointly replayable",
        )

    res = linprog(
        c,
        A_ub=A,
        b_ub=-np.ones(graph.m),
        bounds=[(0.0, None)] * len(gs),
        method="highs",
    )
    if not res.success:
        return FractionalReplayLowerBound(
            float("inf"), np.zeros(len(gs)), float("inf"), False, str(res.message)
        )

    scale = binary_decision_kl(beta) / per_informative_query_kl
    return FractionalReplayLowerBound(
        normalized_cost=float(res.fun),
        query_weights=np.asarray(res.x),
        expected_cost_floor=float(res.fun) * scale,
        success=True,
        message=str(res.message),
    )
