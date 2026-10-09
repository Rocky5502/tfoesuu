#!/usr/bin/env python3
"""Validate public-context V2 artifacts and optionally require readiness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.public_benchmarks_v2 import validate_prepared_public_v2_directory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prepared_dir", type=Path)
    parser.add_argument("--expected-source-commit")
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    report = validate_prepared_public_v2_directory(
        args.prepared_dir,
        expected_source_commit=args.expected_source_commit,
        source_root=args.source_root,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_ready and not report["ready"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
