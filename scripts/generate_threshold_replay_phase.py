#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tfoesuu.threshold_replay_benchmarks import (
    threshold_replay_phase_benchmark_v1,
    write_threshold_replay_phase_jsonl,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("data/threshold_replay_phase_v1.jsonl"),
    )
    args = ap.parse_args()
    rows = threshold_replay_phase_benchmark_v1()
    write_threshold_replay_phase_jsonl(rows, args.output)
    print(
        f"wrote {len(rows)} P18 phase-transition specifications to {args.output}"
    )


if __name__ == "__main__":
    main()
