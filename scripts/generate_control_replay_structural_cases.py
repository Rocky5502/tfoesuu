#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tfoesuu.control_replay_benchmarks import (
    control_replay_structural_cases_v1,
    write_control_replay_structural_jsonl,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("data/control_replay_structural_cases_v1.jsonl"),
    )
    args = ap.parse_args()
    rows = control_replay_structural_cases_v1()
    write_control_replay_structural_jsonl(rows, args.output)
    print(f"wrote {len(rows)} P19 structural specifications to {args.output}")


if __name__ == "__main__":
    main()
