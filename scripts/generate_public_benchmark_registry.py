#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tfoesuu.public_benchmarks import (
    public_benchmark_registry_v1,
    write_public_benchmark_registry,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("data/public_benchmark_registry_v1.jsonl"),
    )
    args = ap.parse_args()
    rows = public_benchmark_registry_v1()
    write_public_benchmark_registry(rows, args.output)
    print(f"wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
