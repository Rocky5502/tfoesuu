#!/usr/bin/env python3
"""Materialize the deterministic replay phase-transition specification grid."""

from __future__ import annotations

import argparse
from pathlib import Path

from tfoesuu.replay_phase_benchmarks import (
    replay_phase_cases_v1,
    write_replay_phase_jsonl,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    rows = replay_phase_cases_v1()
    write_replay_phase_jsonl(rows, args.output)
    print(f"wrote {len(rows)} replay phase specifications to {args.output}")


if __name__ == "__main__":
    main()
