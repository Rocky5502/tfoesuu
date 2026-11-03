#!/usr/bin/env python3
"""Resumable multi-GPU sweep for the Bernoulli replay-separation theorem.

The kernel samples sufficient statistics directly:
- paired replay: number of discordant old/new pairs;
- independent replay: number of successes in the new version.

This is exactly distributed as the corresponding raw executions for the theorem
family, while avoiding arrays whose width equals the sample count.

No AI model, model API, pretrained weights, or network access is used.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
from pathlib import Path

from tfoesuu.replay_benchmarks import (
    ReplayBenchmarkSpec,
    read_replay_jsonl,
    replay_benchmark_v1,
)
from tfoesuu.separations import replay_separation_bounds


def run_one(spec: ReplayBenchmarkSpec, trials: int, device: str) -> dict:
    import torch

    b = replay_separation_bounds(spec.p, spec.d, spec.beta)
    dev = torch.device(device)
    gen = torch.Generator(device=dev)
    gen.manual_seed(spec.seed)

    paired_n = b.paired_upper_rounds
    ind_n = b.independent_upper_rounds

    # Direct sufficient-statistic draws.
    totals_pair = torch.full((trials,), float(paired_n), device=dev)
    probs_pair = torch.full((trials,), spec.d, device=dev)
    mismatches = torch.binomial(totals_pair, probs_pair, generator=gen)
    paired_alt_miss = float((mismatches == 0).float().mean().cpu())

    totals_ind = torch.full((trials,), float(ind_n), device=dev)
    null_prob = torch.full((trials,), spec.p, device=dev)
    alt_prob = torch.full((trials,), spec.p + spec.d, device=dev)
    null_successes = torch.binomial(totals_ind, null_prob, generator=gen)
    alt_successes = torch.binomial(totals_ind, alt_prob, generator=gen)
    cutoff = spec.p + spec.d / 2.0
    independent_null_error = float(
        ((null_successes / ind_n) >= cutoff).float().mean().cpu()
    )
    independent_alt_miss = float(
        ((alt_successes / ind_n) < cutoff).float().mean().cpu()
    )

    return {
        **spec.__dict__,
        "device": device,
        "trials": trials,
        "paired_upper_rounds": paired_n,
        "paired_null_expected_lower": b.paired_null_expected_lower,
        "paired_per_round_kl": b.paired_per_round_kl,
        "paired_alt_miss_empirical": paired_alt_miss,
        "independent_upper_rounds": ind_n,
        "independent_null_expected_lower": b.independent_null_expected_lower,
        "independent_per_round_kl": b.independent_per_round_kl,
        "independent_null_error_empirical": independent_null_error,
        "independent_alt_miss_empirical": independent_alt_miss,
        "upper_round_ratio_ind_over_pair": ind_n / paired_n,
        "lower_round_ratio_ind_over_pair": (
            b.independent_null_expected_lower / b.paired_null_expected_lower
        ),
    }


def worker(
    device_id: int,
    specs: list[ReplayBenchmarkSpec],
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
    ap.add_argument("--devices", default="0", help="comma-separated ids, e.g. 0,1")
    ap.add_argument("--trials", type=int, default=1_000_000)
    ap.add_argument("--benchmark", type=Path)
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("results/replay_gpu_sweep.jsonl"),
    )
    args = ap.parse_args()

    devices = [int(x) for x in args.devices.split(",") if x.strip()]
    if not devices:
        raise ValueError("at least one CUDA device is required")

    specs = (
        read_replay_jsonl(args.benchmark)
        if args.benchmark
        else replay_benchmark_v1()
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)

    shards: list[list[ReplayBenchmarkSpec]] = [[] for _ in devices]
    for i, spec in enumerate(specs):
        shards[i % len(devices)].append(spec)

    ctx = mp.get_context("spawn")
    procs = [
        ctx.Process(target=worker, args=(dev, shard, args.trials, str(args.output)))
        for dev, shard in zip(devices, shards)
    ]
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()
        if proc.exitcode != 0:
            raise SystemExit(f"GPU worker failed with exit code {proc.exitcode}")

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
