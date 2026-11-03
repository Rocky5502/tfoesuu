#!/usr/bin/env python3
"""Resumable multi-GPU stress test for P15 four-way counterfactual replay.

The experiment samples theorem sufficient statistics directly:
- four-way replay: sparse fairness-differential witnesses ~ Binomial(n, d);
- vertex-paired replay: old/new discordances ~ Binomial(n, s) or Binomial(n, s+d).

No AI model, model API, network access, or pretrained weights are used.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
from pathlib import Path

from tfoesuu.counterfactual_benchmarks import (
    CounterfactualReplayBenchmarkSpec,
    counterfactual_replay_benchmark_v1,
    read_counterfactual_replay_jsonl,
)
from tfoesuu.separations import counterfactual_replay_bounds


def run_one(
    spec: CounterfactualReplayBenchmarkSpec,
    trials: int,
    device: str,
) -> dict:
    import torch

    b = counterfactual_replay_bounds(
        spec.p,
        spec.shared_patch,
        spec.d,
        spec.beta,
    )
    dev = torch.device(device)
    gen = torch.Generator(device=dev)
    gen.manual_seed(spec.seed)

    edge_n = b.edge_coupled_upper_rounds
    edge_totals = torch.full((trials,), float(edge_n), device=dev)
    edge_probs = torch.full((trials,), spec.d, device=dev)
    edge_hits = torch.binomial(edge_totals, edge_probs, generator=gen)
    edge_alt_miss = float((edge_hits == 0).float().mean().cpu())

    vertex_n = b.vertex_paired_upper_rounds
    vertex_totals = torch.full((trials,), float(vertex_n), device=dev)
    null_probs = torch.full((trials,), spec.shared_patch, device=dev)
    alt_probs = torch.full(
        (trials,),
        spec.shared_patch + spec.d,
        device=dev,
    )
    null_hits = torch.binomial(vertex_totals, null_probs, generator=gen)
    alt_hits = torch.binomial(vertex_totals, alt_probs, generator=gen)
    cutoff = spec.shared_patch + spec.d / 2.0
    vertex_null_error = float(
        ((null_hits / vertex_n) >= cutoff).float().mean().cpu()
    )
    vertex_alt_miss = float(
        ((alt_hits / vertex_n) < cutoff).float().mean().cpu()
    )

    return {
        **spec.__dict__,
        "device": device,
        "trials": trials,
        "edge_coupled_upper_rounds": edge_n,
        "edge_coupled_concrete_executions": 4 * edge_n,
        "edge_coupled_null_expected_lower": (
            b.edge_coupled_null_expected_lower
        ),
        "edge_coupled_per_round_kl": b.edge_coupled_per_round_kl,
        "edge_coupled_alt_miss_empirical": edge_alt_miss,
        "vertex_paired_upper_rounds": vertex_n,
        "vertex_paired_concrete_executions": 2 * vertex_n,
        "vertex_paired_null_expected_lower": (
            b.vertex_paired_null_expected_lower
        ),
        "vertex_paired_per_round_kl": b.vertex_paired_per_round_kl,
        "vertex_paired_null_error_empirical": vertex_null_error,
        "vertex_paired_alt_miss_empirical": vertex_alt_miss,
        "upper_round_ratio_vertex_over_edge": vertex_n / edge_n,
        "lower_round_ratio_vertex_over_edge": (
            b.vertex_paired_null_expected_lower
            / b.edge_coupled_null_expected_lower
        ),
    }


def worker(
    device_id: int,
    specs: list[CounterfactualReplayBenchmarkSpec],
    trials: int,
    output: str,
) -> None:
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--devices", default="0")
    ap.add_argument("--trials", type=int, default=1_000_000)
    ap.add_argument("--benchmark", type=Path)
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("results/counterfactual_gpu_sweep.jsonl"),
    )
    args = ap.parse_args()

    devices = [int(x) for x in args.devices.split(",") if x.strip()]
    if not devices:
        raise ValueError("at least one CUDA device is required")

    specs = (
        read_counterfactual_replay_jsonl(args.benchmark)
        if args.benchmark
        else counterfactual_replay_benchmark_v1()
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)

    shards: list[list[CounterfactualReplayBenchmarkSpec]] = [
        [] for _ in devices
    ]
    for i, spec in enumerate(specs):
        shards[i % len(devices)].append(spec)

    ctx = mp.get_context("spawn")
    procs = [
        ctx.Process(
            target=worker,
            args=(dev, shard, args.trials, str(args.output)),
        )
        for dev, shard in zip(devices, shards)
    ]
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()
        if proc.exitcode != 0:
            raise SystemExit(
                f"GPU worker failed with exit code {proc.exitcode}"
            )

    rows: list[dict] = []
    for dev in devices:
        shard = args.output.with_name(
            f"{args.output.stem}.gpu{dev}{args.output.suffix}"
        )
        if shard.exists():
            rows.extend(
                json.loads(line)
                for line in shard.read_text(encoding="utf-8").splitlines()
                if line.strip()
            )

    rows.sort(key=lambda row: row["benchmark_id"])
    with args.output.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")

    print(f"wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
