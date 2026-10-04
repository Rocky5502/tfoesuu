#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tfoesuu.counterfactual_benchmarks import (
    counterfactual_replay_benchmark_v1,
    write_counterfactual_replay_jsonl,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("data/counterfactual_replay_benchmark_v1.jsonl"),
    )
    args = ap.parse_args()
    rows = counterfactual_replay_benchmark_v1()
    write_counterfactual_replay_jsonl(rows, args.output)
    print(f"wrote {len(rows)} counterfactual replay specifications to {args.output}")


if __name__ == "__main__":
    main()
