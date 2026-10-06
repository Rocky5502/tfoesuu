#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tfoesuu.partial_replay_benchmarks import (
    partial_replay_structural_cases_v1,
    write_partial_replay_structural_jsonl,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("data/partial_replay_structural_cases_v1.jsonl"),
    )
    args = ap.parse_args()
    rows = partial_replay_structural_cases_v1()
    write_partial_replay_structural_jsonl(rows, args.output)
    print(f"wrote {len(rows)} P17 structural specifications to {args.output}")


if __name__ == "__main__":
    main()
