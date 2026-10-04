#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tfoesuu.subject_benchmarks import (
    software_subject_benchmark_v1,
    write_software_subject_jsonl,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("data/software_subject_benchmark_v1.jsonl"),
    )
    args = ap.parse_args()
    rows = software_subject_benchmark_v1()
    write_software_subject_jsonl(rows, args.output)
    print(f"wrote {len(rows)} software-subject specifications to {args.output}")


if __name__ == "__main__":
    main()
