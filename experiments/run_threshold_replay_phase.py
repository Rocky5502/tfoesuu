#!/usr/bin/env python3
"""Finite-instance audit of the P18 thresholded replay phase transition.

The experiment samples the exact sufficient statistic for one synchronized
threshold-Bernoulli edge.  Under a gap g, the new-version mismatch indicator in
one common-uniform replay round is Bernoulli(g).  No model, API, or external data
source is used.
"""

from __future__ import annotations

import argparse
import json

import numpy as np

from tfoesuu.separations import threshold_fairness_replay_bounds


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, default=0.20)
    ap.add_argument("--shared-patch", type=float, default=0.10)
    ap.add_argument("--tau", type=float, default=0.10)
    ap.add_argument("--d", type=float, default=0.01)
    ap.add_argument("--beta", type=float, default=0.05)
    ap.add_argument("--trials", type=int, default=100_000)
    ap.add_argument("--seed", type=int, default=20271008)
    args = ap.parse_args()

    if args.trials < 1:
        raise ValueError("trials must be positive")

    bounds = threshold_fairness_replay_bounds(
        args.p,
        args.shared_patch,
        args.tau,
        args.d,
        args.beta,
    )
    n = bounds.replay_upper_rounds

    rng = np.random.default_rng(args.seed)
    null_hits = rng.binomial(n, args.tau, size=args.trials)
    alt_hits = rng.binomial(n, args.tau + args.d, size=args.trials)
    cutoff = args.tau + args.d / 2.0

    null_error = float(np.mean(null_hits / n >= cutoff))
    alt_error = float(np.mean(alt_hits / n < cutoff))

    payload = {
        "schema": "tfoesuu-p18-threshold-replay-audit-v1",
        "p": args.p,
        "shared_patch": args.shared_patch,
        "tau": args.tau,
        "d": args.d,
        "beta": args.beta,
        "trials": args.trials,
        "seed": args.seed,
        "replay_upper_rounds": n,
        "replay_upper_concrete_executions": (
            bounds.replay_upper_concrete_executions
        ),
        "null_expected_rounds_lower": bounds.null_expected_rounds_lower,
        "per_round_kl": bounds.per_round_kl,
        "null_error_empirical": null_error,
        "alternative_error_empirical": alt_error,
        "decision_cutoff": cutoff,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
