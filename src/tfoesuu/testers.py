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



@dataclass(frozen=True)
class FullRegressionTestResult:
    """Result for separated Gaussian fairness regression after promise-aware pruning."""

    reject: bool
    safe_edges: tuple[tuple[int, int], ...]
    promise_gap_edges: tuple[tuple[int, int], ...]
    residual_edges: tuple[tuple[int, int], ...]
    estimated_new_gaps: dict[tuple[int, int], float]
    sample_counts: np.ndarray
    allocation: AllocationResult


def run_gaussian_full_regression_test(
    graph: GraphSpec,
    oracle: GaussianVersionPair,
    old_edge_gaps: dict[tuple[int, int], float],
    thresholds: dict[tuple[int, int], float],
    patch_effect_bounds: dict[tuple[int, int], float],
    gamma: float,
    beta: float,
    seed: int,
    paired: bool = True,
) -> FullRegressionTestResult:
    """Test full thresholded fairness after sound deterministic pruning.

    The separated promise is:
      H0: |g1_e| <= tau_e for every edge;
      H1: |g1_e| >= tau_e + gamma for at least one edge.

    Patch envelopes induce three categories:
      * certified safe: |g0_e| + b_e <= tau_e;
      * promise-gap only: tau_e < |g0_e| + b_e < tau_e + gamma;
      * alternative-capable: |g0_e| + b_e >= tau_e + gamma.

    Only alternative-capable edges can realize H1, so the Gaussian allocation is
    solved on that graph. Promise-gap edges are not declared fair; they are
    omitted only because the separated promise rules them out as H1 witnesses.
    The theorem guarantee requires the supplied envelopes to be sound; this
    function cannot infer soundness from samples.
    """

    from .certificate import prune_for_separated_regression

    if gamma <= 0:
        raise ValueError("gamma must be positive")
    if not (0 < beta < 1):
        raise ValueError("beta must lie in (0,1)")
    if oracle.n != graph.n:
        raise ValueError("oracle vertex count must match graph")

    pruning = prune_for_separated_regression(
        graph,
        old_edge_gaps,
        thresholds,
        patch_effect_bounds,
        gamma,
    )
    residual = pruning.alternative_graph
    variances = (
        oracle.paired_delta_variance
        if paired
        else oracle.independent_delta_variance
    )
    counts, allocation = gaussian_static_counts(
        residual,
        variances,
        gamma,
        beta,
    )

    if residual.m == 0:
        return FullRegressionTestResult(
            reject=False,
            safe_edges=pruning.certified_safe_edges,
            promise_gap_edges=pruning.promise_gap_edges,
            residual_edges=(),
            estimated_new_gaps={},
            sample_counts=counts,
            allocation=allocation,
        )

    rng = np.random.default_rng(seed)
    theta_hat = np.zeros(graph.n, dtype=float)
    for vertex, count in enumerate(counts):
        if count > 0:
            theta_hat[vertex] = float(
                np.mean(
                    oracle.sample_delta(
                        vertex,
                        int(count),
                        rng,
                        paired=paired,
                    )
                )
            )

    estimated: dict[tuple[int, int], float] = {}
    reject = False
    for u, v in residual.edges:
        edge = (u, v)
        if edge in old_edge_gaps:
            g0 = float(old_edge_gaps[edge])
        else:
            g0 = -float(old_edge_gaps[(v, u)])
        if edge in thresholds:
            tau = float(thresholds[edge])
        else:
            tau = float(thresholds[(v, u)])

        g1_hat = g0 + theta_hat[u] - theta_hat[v]
        estimated[edge] = g1_hat
        if abs(g1_hat) >= tau + gamma / 2.0:
            reject = True

    return FullRegressionTestResult(
        reject=reject,
        safe_edges=pruning.certified_safe_edges,
        promise_gap_edges=pruning.promise_gap_edges,
        residual_edges=residual.edges,
        estimated_new_gaps=estimated,
        sample_counts=counts,
        allocation=allocation,
    )
