from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .allocation import AllocationResult, solve_psi
from .graphs import GraphSpec
from .oracles import GaussianVersionPair


@dataclass(frozen=True)
class TestResult:
    reject: bool
    edge_statistics: dict[tuple[int, int], float]
    sample_counts: np.ndarray
    allocation: AllocationResult


def gaussian_static_counts(
    graph: GraphSpec,
    variances: np.ndarray,
    gamma: float,
    beta: float,
) -> tuple[np.ndarray, AllocationResult]:
    if gamma <= 0:
        raise ValueError("gamma must be positive")
    if not (0 < beta < 1):
        raise ValueError("beta must lie in (0,1)")
    if graph.m < 1:
        return np.zeros(graph.n, dtype=int), solve_psi(graph, variances)
    allocation = solve_psi(graph, variances)
    if not allocation.success or allocation.max_constraint_violation > 1e-7:
        raise RuntimeError(f"allocation solver failed: {allocation.message}")
    L = math.log(2.0 * graph.m / beta)
    counts = np.ceil((8.0 * L / (gamma**2)) * allocation.q).astype(int)
    counts[allocation.q == 0] = 0
    return counts, allocation


def run_gaussian_static_test(
    graph: GraphSpec,
    oracle: GaussianVersionPair,
    gamma: float,
    beta: float,
    seed: int,
    paired: bool = True,
) -> TestResult:
    variances = oracle.paired_delta_variance if paired else oracle.independent_delta_variance
    counts, allocation = gaussian_static_counts(graph, variances, gamma, beta)
    rng = np.random.default_rng(seed)
    estimates = np.zeros(graph.n, dtype=float)
    for v, count in enumerate(counts):
        if count > 0:
            estimates[v] = float(np.mean(oracle.sample_delta(v, int(count), rng, paired=paired)))
    stats = {(u, v): abs(float(estimates[u] - estimates[v])) for u, v in graph.edges}
    reject = any(value >= gamma / 2.0 for value in stats.values())
    return TestResult(reject, stats, counts, allocation)
