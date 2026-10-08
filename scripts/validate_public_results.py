#!/usr/bin/env python3
"""Strict release gate for public-dataset publication results.

Distinguishes schema-valid exploratory output from a complete matched
seven-dataset, five-method, multi-patch publication matrix.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.public_results import (
    read_public_results,
    validate_publication_coverage,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument(
        "--registry",
        type=Path,
        default=Path("data/public_benchmark_registry_v1.jsonl"),
    )
    ap.add_argument("--require-datasets", type=int, default=7)
    ap.add_argument("--min-patch-sizes", type=int, default=4)
    ap.add_argument("--min-trials", type=int, default=100_000)
    args = ap.parse_args()

    registry = [
        json.loads(line) for line in args.registry.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    expected = [entry["benchmark_id"] for entry in registry]
    if len(expected) != args.require_datasets or len(set(expected)) != len(expected):
        raise SystemExit(
            f"expected {args.require_datasets} unique registry datasets, "
            f"found {len(expected)} rows/{len(set(expected))} unique IDs"
        )

    rows = read_public_results(args.results)
    validate_publication_coverage(
        rows, expected,
        minimum_patch_sizes=args.min_patch_sizes,
        minimum_trials=args.min_trials,
    )

    datasets = sorted({row.dataset_id for row in rows})
    methods = sorted({row.method for row in rows})
    patches = sorted({row.patch_size for row in rows})
    seeds = sorted({row.seed for row in rows})
    worst_i = max(rows, key=lambda row: row.type_i_error)
    worst_ii = max(rows, key=lambda row: row.type_ii_error)
    print(
        "public release matrix has complete coverage: "
        f"{len(rows)} rows, {len(datasets)} registered datasets, "
        f"{len(methods)} methods, {len(patches)} patch sizes, "
        f"{len(seeds)} distinct seed identifiers"
    )
    print(
        f"source commit: {rows[0].source_commit}; confidence target: "
        f"{rows[0].confidence_target:g}; affected fraction: "
        f"{rows[0].affected_fraction:g}"
    )
    print(
        f"worst observed type-I: {worst_i.type_i_error:.6f} "
        f"({worst_i.dataset_id}, {worst_i.method}, d={worst_i.patch_size:g})"
    )
    print(
        f"worst observed type-II: {worst_ii.type_ii_error:.6f} "
        f"({worst_ii.dataset_id}, {worst_ii.method}, d={worst_ii.patch_size:g})"
    )
    print(
        "NOTE: schema and coverage validation do not authenticate raw trials; "
        "verify run logs, hashes, software environments and publication provenance."
    )


if __name__ == "__main__":
    main()
