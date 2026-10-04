#!/usr/bin/env python3
"""Finite-sample audit of four-way counterfactual replay.

No model, external API, or network access is used.
"""

from __future__ import annotations

import argparse
import json
import numpy as np

from tfoesuu.separations import counterfactual_replay_bounds


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=float, default=0.35)
    ap.add_argument("--shared-patch", type=float, default=0.20)
    ap.add_argument("--d", type=float, default=0.01)
    ap.add_argument("--beta", type=float, default=0.05)
    ap.add_argument("--trials", type=int, default=100_000)
    ap.add_argument("--seed", type=int, default=20271005)
    args = ap.parse_args()

    b = counterfactual_replay_bounds(
        args.p,
        args.shared_patch,
        args.d,
        args.beta,
    )
    rng = np.random.default_rng(args.seed)

    edge_hits = rng.binomial(
        b.edge_coupled_upper_rounds,
        args.d,
        size=args.trials,
    )
    edge_alt_miss = float(np.mean(edge_hits == 0))

    n = b.vertex_paired_upper_rounds
    null_discordance = rng.binomial(n, args.shared_patch, size=args.trials)
    alt_discordance = rng.binomial(
        n,
        args.shared_patch + args.d,
        size=args.trials,
    )
    cutoff = args.shared_patch + args.d / 2.0
    vertex_null_error = float(np.mean(null_discordance / n >= cutoff))
    vertex_alt_miss = float(np.mean(alt_discordance / n < cutoff))

    print(
        json.dumps(
            {
                "p": args.p,
                "shared_patch": args.shared_patch,
                "d": args.d,
                "beta": args.beta,
                "trials": args.trials,
                "edge_coupled_upper_rounds": b.edge_coupled_upper_rounds,
                "edge_coupled_concrete_executions": 4
                * b.edge_coupled_upper_rounds,
                "edge_coupled_null_expected_lower": (
                    b.edge_coupled_null_expected_lower
                ),
                "edge_coupled_alt_miss_empirical": edge_alt_miss,
                "vertex_paired_upper_rounds": b.vertex_paired_upper_rounds,
                "vertex_paired_concrete_executions": 2
                * b.vertex_paired_upper_rounds,
                "vertex_paired_null_expected_lower": (
                    b.vertex_paired_null_expected_lower
                ),
                "vertex_paired_null_error_empirical": vertex_null_error,
                "vertex_paired_alt_miss_empirical": vertex_alt_miss,
                "upper_round_ratio_vertex_over_edge": (
                    b.vertex_paired_upper_rounds
                    / b.edge_coupled_upper_rounds
                ),
                "lower_round_ratio_vertex_over_edge": (
                    b.vertex_paired_null_expected_lower
                    / b.edge_coupled_null_expected_lower
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
