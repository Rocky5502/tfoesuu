#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tfoesuu.replay_benchmarks import replay_benchmark_v1, write_replay_jsonl


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("data/replay_benchmark_v1.jsonl"),
    )
    args = ap.parse_args()
    rows = replay_benchmark_v1()
    write_replay_jsonl(rows, args.output)
    print(f"wrote {len(rows)} replay benchmark specifications to {args.output}")


if __name__ == "__main__":
    main()
