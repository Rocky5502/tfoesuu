#!/usr/bin/env python3
"""Finite-sample audit of P13: unknown patch location on a matching.

Local synthetic computation only; no model or network access.
"""
from __future__ import annotations
import argparse
import json
import numpy as np

from tfoesuu.separations import location_replay_bounds


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidates",type=int,default=64)
    ap.add_argument("--p",type=float,default=0.5)
    ap.add_argument("--d",type=float,default=0.01)
    ap.add_argument("--beta",type=float,default=0.05)
    ap.add_argument("--trials",type=int,default=100000)
    ap.add_argument("--seed",type=int,default=20271005)
    args=ap.parse_args()

    b=location_replay_bounds(args.candidates,args.p,args.d,args.beta)
    rng=np.random.default_rng(args.seed)
    # For any fixed alternative i, only its changed endpoint can produce a
    # discordance. The other M-1 candidates are identically zero under both worlds.
    mismatches=rng.binomial(b.per_candidate_upper_rounds,args.d,size=args.trials)
    empirical_miss=float(np.mean(mismatches==0))
    exact_miss=float((1.0-args.d)**b.per_candidate_upper_rounds)
    out={
        "candidates":args.candidates,"p":args.p,"d":args.d,"beta":args.beta,
        "trials":args.trials,"seed":args.seed,
        "per_candidate_upper_rounds":b.per_candidate_upper_rounds,
        "total_upper_rounds":b.total_upper_rounds,
        "null_expected_lower":b.null_expected_lower,
        "paired_per_round_kl":b.paired_per_round_kl,
        "exact_alternative_miss":exact_miss,
        "empirical_alternative_miss":empirical_miss,
    }
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
