#!/usr/bin/env python3
"""Run the replay theorem on an executable randomized software subject."""

from __future__ import annotations

import argparse
import json

import numpy as np

from tfoesuu.separations import location_replay_bounds
from tfoesuu.software_subjects import (
    RandomizedResourceAllocatorPair,
    linear_baseline,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contexts", type=int, default=64)
    ap.add_argument("--changed-context", type=int, default=17)
    ap.add_argument("--delta", type=float, default=0.01)
    ap.add_argument("--beta", type=float, default=0.05)
    ap.add_argument("--trials", type=int, default=100_000)
    ap.add_argument("--seed", type=int, default=20271005)
    args = ap.parse_args()

    if not (0 <= args.changed_context < args.contexts):
        raise ValueError("changed-context must be inside context range")

    baseline = linear_baseline(args.contexts, low=0.25, high=0.70)
    subject = RandomizedResourceAllocatorPair.from_sequences(
        baseline,
        affected_contexts=[args.changed_context],
        delta=args.delta,
    )

    p = float(baseline[args.changed_context])
    bounds = location_replay_bounds(
        args.contexts,
        p,
        args.delta,
        args.beta,
    )

    rng = np.random.default_rng(args.seed)
    changed_vertex = subject.encode_vertex(args.changed_context, 1)
    misses = 0
    for _ in range(args.trials):
        z = subject.sample_paired_delta(
            changed_vertex,
            bounds.per_candidate_upper_rounds,
            rng,
        )
        misses += int(not np.any(z != 0))

    out = {
        "subject": "randomized_resource_allocator",
        "contexts": args.contexts,
        "vertices": subject.n_vertices,
        "fairness_edges": subject.fairness_graph.m,
        "changed_context": args.changed_context,
        "impacted_edges": len(subject.impacted_edges),
        "delta": args.delta,
        "beta": args.beta,
        "trials": args.trials,
        "per_candidate_paired_calls": bounds.per_candidate_upper_rounds,
        "total_unknown_location_paired_calls": bounds.total_upper_rounds,
        "concrete_program_executions": 2 * bounds.total_upper_rounds,
        "theoretical_null_expected_lower": bounds.null_expected_lower,
        "empirical_alternative_miss": misses / args.trials,
        "exact_alternative_miss": (
            (1.0 - args.delta) ** bounds.per_candidate_upper_rounds
        ),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
