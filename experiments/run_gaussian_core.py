#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from tfoesuu.allocation import exact_unit_variance_psi, solve_psi, solve_psi_dual
from tfoesuu.graphs import clique_graph, matching_graph, path_graph, star_graph


def make_graph(kind: str, n: int):
    if kind == "matching":
        if n % 2:
            raise ValueError("matching requires even n")
        return matching_graph(n // 2)
    if kind == "star":
        return star_graph(n - 1)
    if kind == "path":
        return path_graph(n)
    if kind == "clique":
        return clique_graph(n)
    raise ValueError(kind)


def simulate_direct_means(graph, q, gamma, beta, trials, seed):
    """Monte Carlo from the exact Gaussian sample-mean law.

    This avoids simulating every raw execution and is therefore appropriate for
    theorem sanity checks. It does not change the distribution of the test statistic.
    """
    rng = np.random.default_rng(seed)
    L = math.log(2 * graph.m / beta)
    counts = np.ceil(8 * L * q / gamma**2).astype(int)
    counts[q == 0] = 0
    sd = np.zeros(graph.n)
    active = counts > 0
    sd[active] = 1.0 / np.sqrt(counts[active])

    means0 = rng.normal(0.0, sd, size=(trials, graph.n))
    reject0 = np.zeros(trials, dtype=bool)
    for u, v in graph.edges:
        reject0 |= np.abs(means0[:, u] - means0[:, v]) >= gamma / 2

    theta = np.zeros(graph.n)
    u0, v0 = graph.edges[0]
    theta[u0] = gamma / 2
    theta[v0] = -gamma / 2
    means1 = rng.normal(theta, sd, size=(trials, graph.n))
    reject1 = np.zeros(trials, dtype=bool)
    for u, v in graph.edges:
        reject1 |= np.abs(means1[:, u] - means1[:, v]) >= gamma / 2

    return {
        "counts": counts.tolist(),
        "total_queries": int(counts.sum()),  # backward-compatible alias\n        "total_paired_oracle_calls": int(counts.sum()),\n        "concrete_program_executions": 2 * int(counts.sum()),
        "null_error_rate": float(np.mean(reject0)),
        "alternative_error_rate": float(np.mean(~reject1)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["matching", "star", "path", "clique"], default="star")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--gamma", type=float, default=0.5)
    ap.add_argument("--beta", type=float, default=0.05)
    ap.add_argument("--trials", type=int, default=10_000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    graph = make_graph(args.graph, args.n)
    var = np.ones(graph.n)
    primal = solve_psi(graph, var)
    dual = solve_psi_dual(graph, var)
    exact = exact_unit_variance_psi(graph)
    mc = simulate_direct_means(graph, primal.q, args.gamma, args.beta, args.trials, args.seed)
    payload = {
        "graph": args.graph,
        "n": graph.n,
        "m": graph.m,
        "gamma": args.gamma,
        "beta": args.beta,
        "trials": args.trials,
        "psi_primal": primal.objective,
        "psi_dual": dual.objective,
        "duality_gap": primal.objective - dual.objective,
        "psi_exact": exact,
        "allocation": primal.q.tolist(),
        **mc,
    }
    print(json.dumps(payload, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
