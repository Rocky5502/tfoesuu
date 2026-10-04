#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

import numpy as np

from tfoesuu.oracles import BernoulliCommonUniformPair


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p0", type=float, default=0.5)
    ap.add_argument("--delta", type=float, default=0.01)
    ap.add_argument("--samples", type=int, default=1_000_000)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    p1 = args.p0 + args.delta
    if not (0 <= p1 <= 1):
        raise ValueError("p0 + delta must be in [0,1]")

    oracle = BernoulliCommonUniformPair.from_sequences([args.p0], [p1])
    rng = np.random.default_rng(args.seed)
    paired = oracle.sample_delta(0, args.samples, rng, paired=True)
    independent = oracle.sample_delta(0, args.samples, rng, paired=False)

    payload = {
        "p0": args.p0,
        "p1": p1,
        "delta": args.delta,
        "samples": args.samples,
        "theory_paired_variance": float(oracle.paired_delta_variance[0]),
        "theory_independent_variance": float(oracle.independent_delta_variance[0]),
        "empirical_paired_variance": float(np.var(paired)),
        "empirical_independent_variance": float(np.var(independent)),
        "theory_variance_ratio": float(
            oracle.paired_delta_variance[0] / oracle.independent_delta_variance[0]
        ),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
