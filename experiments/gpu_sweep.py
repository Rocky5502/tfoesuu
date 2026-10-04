#!/usr/bin/env python3
"""Resumable multi-GPU Monte Carlo stress test for the Gaussian core theorem.

The experiment samples directly from Gaussian sample-mean distributions, so each
GPU trial is statistically equivalent to executing all raw program runs but much
more efficient for checking theorem constants and rare error probabilities.

No AI model is loaded or used.
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
from pathlib import Path

import numpy as np

from tfoesuu.allocation import solve_psi
from tfoesuu.benchmarks import BenchmarkSpec, benchmark_v1, read_jsonl
from tfoesuu.graphs import clique_graph, matching_graph, path_graph, star_graph


def make_graph(spec: BenchmarkSpec):
    n = spec.n
    if spec.graph_family == "matching":
        return matching_graph(n // 2)
    if spec.graph_family == "star":
        return star_graph(n - 1)
    if spec.graph_family == "path":
        return path_graph(n)
    if spec.graph_family == "clique":
        return clique_graph(n)
    raise ValueError(spec.graph_family)


def run_one(spec: BenchmarkSpec, trials: int, device: str) -> dict:
    import torch

    graph = make_graph(spec)
    base = 2.0 * (1.0 - spec.correlation)
    if spec.variance_profile == "homogeneous":
        profile = np.ones(graph.n)
    elif spec.variance_profile == "degree_weighted":
        deg = np.zeros(graph.n, dtype=float)
        for u, v in graph.edges:
            deg[u] += 1
            deg[v] += 1
        profile = 1.0 + 7.0 * deg / max(1.0, float(deg.max()))
    elif spec.variance_profile == "lognormal":
        rng_profile = np.random.default_rng(spec.seed)
        profile = np.exp(rng_profile.normal(0.0, 0.8, size=graph.n))
        profile /= float(np.mean(profile))
    else:
        raise ValueError(f"unknown variance profile: {spec.variance_profile}")
    variance = np.maximum(base * profile, 1e-12)
    alloc = solve_psi(graph, variance)
    L = math.log(2 * graph.m / spec.beta)
    counts = np.ceil(8 * L * alloc.q / spec.gamma**2).astype(np.int64)
    active = counts > 0
    sd = np.zeros(graph.n, dtype=np.float64)
    sd[active] = np.sqrt(variance[active] / counts[active])

    torch.manual_seed(spec.seed)
    dev = torch.device(device)
    sd_t = torch.tensor(sd, dtype=torch.float64, device=dev)
    theta = torch.zeros(graph.n, dtype=torch.float64, device=dev)
    u0, v0 = graph.edges[0]
    theta[u0] = spec.gamma / 2
    theta[v0] = -spec.gamma / 2
    edges = torch.tensor(graph.edges, dtype=torch.long, device=dev)

    batch = min(250_000, trials)
    null_errors = 0
    alt_errors = 0
    done = 0
    while done < trials:
        b = min(batch, trials - done)
        noise0 = torch.randn((b, graph.n), dtype=torch.float64, device=dev) * sd_t
        diffs0 = torch.abs(noise0[:, edges[:, 0]] - noise0[:, edges[:, 1]])
        null_reject = torch.any(diffs0 >= spec.gamma / 2, dim=1)
        null_errors += int(null_reject.sum().item())

        noise1 = torch.randn((b, graph.n), dtype=torch.float64, device=dev) * sd_t + theta
        diffs1 = torch.abs(noise1[:, edges[:, 0]] - noise1[:, edges[:, 1]])
        alt_reject = torch.any(diffs1 >= spec.gamma / 2, dim=1)
        alt_errors += int((~alt_reject).sum().item())
        done += b

    return {
        **spec.__dict__,
        "device": device,
        "trials": trials,
        "psi": alloc.objective,
        "total_queries": int(counts.sum()),  # backward-compatible alias\n        "total_paired_oracle_calls": int(counts.sum()),\n        "concrete_program_executions": 2 * int(counts.sum()),
        "null_error_rate": null_errors / trials,
        "alternative_error_rate": alt_errors / trials,
    }


def worker(device_id: int, specs: list[BenchmarkSpec], trials: int, output: str) -> None:
    device = f"cuda:{device_id}"
    path = Path(output)
    shard = path.with_name(f"{path.stem}.gpu{device_id}{path.suffix}")
    completed: set[str] = set()
    if shard.exists():
        for line in shard.read_text(encoding="utf-8").splitlines():
            if line.strip():
                completed.add(json.loads(line)["benchmark_id"])
    with shard.open("a", encoding="utf-8") as fh:
        for spec in specs:
            if spec.benchmark_id in completed:
                continue
            row = run_one(spec, trials, device)
            fh.write(json.dumps(row, sort_keys=True) + "\n")
            fh.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--devices", default="0", help="comma-separated CUDA device ids, e.g. 0,1")
    ap.add_argument("--trials", type=int, default=1_000_000)
    ap.add_argument("--benchmark", type=Path, help="JSONL benchmark; defaults to benchmark_v1()")
    ap.add_argument("--output", type=Path, default=Path("results/gpu_sweep.jsonl"))
    args = ap.parse_args()

    devices = [int(x) for x in args.devices.split(",") if x.strip()]
    if not devices:
        raise ValueError("at least one device is required")
    specs = read_jsonl(args.benchmark) if args.benchmark else benchmark_v1()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    shards = [[] for _ in devices]
    for i, spec in enumerate(specs):
        shards[i % len(devices)].append(spec)

    ctx = mp.get_context("spawn")
    procs = [
        ctx.Process(target=worker, args=(dev, shard, args.trials, str(args.output)))
        for dev, shard in zip(devices, shards)
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
        if p.exitcode != 0:
            raise SystemExit(f"GPU worker failed with exit code {p.exitcode}")

    rows = []
    for dev in devices:
        shard = args.output.with_name(f"{args.output.stem}.gpu{dev}{args.output.suffix}")
        if shard.exists():
            rows.extend(json.loads(line) for line in shard.read_text(encoding="utf-8").splitlines() if line.strip())
    rows.sort(key=lambda r: r["benchmark_id"])
    with args.output.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
