#!/usr/bin/env python3
"""Read-only validation and byte-hash snapshot for prepared public subjects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.public_benchmarks import (
    validate_preparation_source_compatibility,
    validate_prepared_public_directory,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prepared_dir", type=Path)
    parser.add_argument("--expected-source-commit")
    parser.add_argument(
        "--execution-source-commit",
        help="also verify the versioned preparation contract against this execution commit",
    )
    args = parser.parse_args()

    report = validate_prepared_public_directory(
        args.prepared_dir,
        expected_source_commit=args.expected_source_commit,
    )
    if args.execution_source_commit:
        report["compatibility"] = validate_preparation_source_compatibility(
            report["source_commit"],
            args.execution_source_commit,
        )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
