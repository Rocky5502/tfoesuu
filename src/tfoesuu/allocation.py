from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import minimize

from .graphs import Edge, GraphSpec


@dataclass(frozen=True)
class AllocationResult:
    objective: float
    q: np.ndarray
    success: bool
    message: str
    max_constraint_violation: float


def _validate(n: int, edges: Iterable[Edge], variances: Sequence[float]) -> tuple[list[Edge], np.ndarray]:
    edge_list = list(edges)
    var = np.asarray(variances, dtype=float)
    if var.shape != (n,):
        raise ValueError(f"expected {n} variances, got shape {var.shape}")
    if np.any(~np.isfinite(var)) or np.any(var <= 0):
        raise ValueError("variances must be finite and strictly positive")
    for u, v in edge_list:
        if not (0 <= u < n and 0 <= v < n) or u == v:
            raise ValueError(f"invalid edge {(u, v)}")
    return edge_list, var


def max_constraint_violation(q: Sequence[float], edges: Iterable[Edge], variances: Sequence[float]) -> float:
    q = np.asarray(q, dtype=float)
    var = np.asarray(variances, dtype=float)
    vals = [var[u] / q[u] + var[v] / q[v] - 1.0 for u, v in edges]
    return max([0.0, *vals])


def solve_psi(graph: GraphSpec, variances: Sequence[float] | None = None) -> AllocationResult:
    """Solve the convex primal defining Psi(H,nu).

    Here ``variances[v]`` is nu_v^2. The primal is

        min sum_v q_v
        s.t. var_u/q_u + var_v/q_v <= 1  for every edge (u,v), q_v > 0.

    Isolated vertices are assigned q=0 after optimization because they require no
    samples for edge testing.
    """

    n = graph.n
    edges = list(graph.edges)
    if variances is None:
        variances = np.ones(n)
    edges, var = _validate(n, edges, variances)
    if not edges:
        return AllocationResult(0.0, np.zeros(n), True, "edgeless graph", 0.0)

    active = sorted({v for e in edges for v in e})
    index = {v: i for i, v in enumerate(active)}
    active_var = var[active]
    active_edges = [(index[u], index[v]) for u, v in edges]

    def objective(q: np.ndarray) -> float:
        return float(np.sum(q))

    constraints = [
        {
            "type": "ineq",
            "fun": lambda q, u=u, v=v: 1.0 - active_var[u] / q[u] - active_var[v] / q[v],
        }
        for u, v in active_edges
    ]

    x0 = np.maximum(4.0 * active_var, 1.0)
    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=[(1e-12, None)] * len(active),
        constraints=constraints,
        options={"ftol": 1e-12, "maxiter": 50_000},
    )

    q = np.zeros(n, dtype=float)
    q[active] = result.x
    violation = max_constraint_violation(q + (q == 0), edges, var)
    return AllocationResult(float(np.sum(result.x)), q, bool(result.success), str(result.message), violation)


def solve_psi_dual(graph: GraphSpec, variances: Sequence[float] | None = None) -> AllocationResult:
    """Solve the Lagrange dual of Psi for numerical proof auditing.

    Strong duality (Slater) gives

      Psi = max_{lambda_e >= 0}
            2 sum_v sqrt(var_v * sum_{e incident v} lambda_e) - sum_e lambda_e.

    The returned ``q`` field contains the dual edge weights lambda, not primal q.
    """

    n = graph.n
    edges = list(graph.edges)
    if variances is None:
        variances = np.ones(n)
    edges, var = _validate(n, edges, variances)
    m = len(edges)
    if m == 0:
        return AllocationResult(0.0, np.zeros(0), True, "edgeless graph", 0.0)

    incident: list[list[int]] = [[] for _ in range(n)]
    for j, (u, v) in enumerate(edges):
        incident[u].append(j)
        incident[v].append(j)

    def dual_value(lam: np.ndarray) -> float:
        s = 0.0
        for v in range(n):
            mass = float(np.sum(lam[incident[v]])) if incident[v] else 0.0
            s += 2.0 * math.sqrt(var[v] * max(mass, 0.0))
        return s - float(np.sum(lam))

    res = minimize(
        lambda lam: -dual_value(lam),
        np.ones(m, dtype=float),
        method="L-BFGS-B",
        bounds=[(0.0, None)] * m,
        options={"ftol": 1e-14, "maxiter": 50_000},
    )
    return AllocationResult(float(dual_value(res.x)), np.asarray(res.x), bool(res.success), str(res.message), 0.0)


def exact_unit_variance_psi(graph: GraphSpec) -> float | None:
    """Closed forms used as theorem sanity checks for selected graph families."""

    if graph.family == "edge":
        return 4.0
    if graph.family == "matching":
        k = int(graph.metadata["k"])
        return 4.0 * k
    if graph.family == "clique":
        return 2.0 * graph.n
    if graph.family == "star":
        k = int(graph.metadata["leaves"])
        return (1.0 + math.sqrt(k)) ** 2
    if graph.family == "complete_bipartite":
        a = int(graph.metadata["a"])
        b = int(graph.metadata["b"])
        return (math.sqrt(a) + math.sqrt(b)) ** 2
    return None
