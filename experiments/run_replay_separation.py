#!/usr/bin/env python3
"""Stress-test the Bernoulli replay separation.

This script uses only synthetic Bernoulli draws generated locally.  It supports
NumPy on CPU and PyTorch on CUDA when requested.  No model, model API, or network
access is involved.
"""

from __future__ import annotations

import argparse
import json
import math

import numpy as np

from tfoesuu.separations import replay_separation_bounds


def _numpy_experiment(p: float, d: float, beta: float, trials: int, seed: int) -> dict:
    b = replay_separation_bounds(p, d, beta)
    rng = np.random.default_rng(seed)

    # Paired test: reject iff at least one old/new discordance is observed.
    paired_mismatch_counts = rng.binomial(b.paired_upper_rounds, d, size=trials)
    paired_alt_miss = float(np.mean(paired_mismatch_counts == 0))

    # Independent/fresh test: p is known from the retained old certificate.
    # Threshold the new-version empirical mean at p+d/2.
    n = b.independent_upper_rounds
    null_successes = rng.binomial(n, p, size=trials)
    alt_successes = rng.binomial(n, p + d, size=trials)
    cutoff = p + d / 2.0
    independent_null_error = float(np.mean(null_successes / n >= cutoff))
    independent_alt_miss = float(np.mean(alt_successes / n < cutoff))

    return {
        "backend": "numpy",
        "p": p,
        "d": d,
        "beta": beta,
        "trials": trials,
        "paired_upper_rounds": b.paired_upper_rounds,
        "paired_null_expected_lower": b.paired_null_expected_lower,
        "independent_upper_rounds": b.independent_upper_rounds,
        "independent_null_expected_lower": b.independent_null_expected_lower,
        "paired_per_round_kl": b.paired_per_round_kl,
        "independent_per_round_kl": b.independent_per_round_kl,
        "paired_alt_miss_empirical": paired_alt_miss,
        "independent_null_error_empirical": independent_null_error,
        "independent_alt_miss_empirical": independent_alt_miss,
    }


def _torch_experiment(
    p: float, d: float, beta: float, trials: int, seed: int, device: str
) -> dict:
    import torch

    b = replay_separation_bounds(p, d, beta)
    dev = torch.device(device)
    gen = torch.Generator(device=dev)
    gen.manual_seed(seed)

    # Avoid materializing trials x rounds arrays.  Binomial sampling is enough
    # because the theorem depends only on counts.
    probs = torch.full((trials,), d, device=dev)
    totals = torch.full((trials,), float(b.paired_upper_rounds), device=dev)
    mismatches = torch.binomial(totals, probs, generator=gen)
    paired_alt_miss = float((mismatches == 0).float().mean().cpu())

    n = b.independent_upper_rounds
    totals_ind = torch.full((trials,), float(n), device=dev)
    null_probs = torch.full((trials,), p, device=dev)
    alt_probs = torch.full((trials,), p + d, device=dev)
    null_successes = torch.binomial(totals_ind, null_probs, generator=gen)
    alt_successes = torch.binomial(totals_ind, alt_probs, generator=gen)
    cutoff = p + d / 2.0
    independent_null_error = float(((null_successes / n) >= cutoff).float().mean().cpu())
    independent_alt_miss = float(((alt_successes / n) < cutoff).float().mean().cpu())

    return {
        "backend": str(dev),
        "p": p,
        "d": d,
        "beta": beta,
        "trials": trials,
        "paired_upper_rounds": b.paired_upper_rounds,
        "paired_null_expected_lower": b.paired_null_expected_lower,
        "independent_upper_rounds": b.independent_upper_rounds,
        "independent_null_expected_lower": b.independent_null_expected_lower,
        "paired_per_round_kl": b.paired_per_round_kl,
        "independent_per_round_kl": b.independent_per_round_kl,
        "paired_alt_miss_empirical": paired_alt_miss,
        "independent_null_error_empirical": independent_null_error,
        "independent_alt_miss_empirical": independent_alt_miss,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, default=0.5)
    ap.add_argument("--d", type=float, default=0.01)
    ap.add_argument("--beta", type=float, default=0.05)
    ap.add_argument("--trials", type=int, default=100_000)
    ap.add_argument("--seed", type=int, default=20271005)
    ap.add_argument("--device", default="cpu", help="cpu, cuda, cuda:0, ...")
    args = ap.parse_args()

    if args.device == "cpu":
        out = _numpy_experiment(args.p, args.d, args.beta, args.trials, args.seed)
    else:
        out = _torch_experiment(
            args.p, args.d, args.beta, args.trials, args.seed, args.device
        )

    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
