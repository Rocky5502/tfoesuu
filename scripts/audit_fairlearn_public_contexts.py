#!/usr/bin/env python3
"""Fail-closed audit of frozen public-v1 Fairlearn context readiness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.public_benchmarks import audit_prepared_v1_fairlearn_contexts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prepared_dir", type=Path)
    parser.add_argument("--expected-source-commit")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="exit 2 unless at least one genuine multi-column context is materialized",
    )
    args = parser.parse_args()
    report = audit_prepared_v1_fairlearn_contexts(
        args.prepared_dir,
        expected_source_commit=args.expected_source_commit,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_ready and not report["ready"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
