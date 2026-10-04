#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tfoesuu.benchmarks import benchmark_v1, write_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Path("data/benchmark_v1.jsonl"))
    args = ap.parse_args()
    rows = benchmark_v1()
    write_jsonl(rows, args.output)
    print(f"wrote {len(rows)} benchmark specifications to {args.output}")


if __name__ == "__main__":
    main()
