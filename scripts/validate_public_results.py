#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from tfoesuu.public_results import read_public_results, validate_public_result_matrix


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--require-datasets", type=int, default=7)
    args = ap.parse_args()

    rows = read_public_results(args.results)
    validate_public_result_matrix(rows)
    datasets = sorted({row.dataset_id for row in rows})
    methods = sorted({row.method for row in rows})
    patches = sorted({row.patch_size for row in rows})
    if len(datasets) < args.require_datasets:
        raise SystemExit(
            f"expected at least {args.require_datasets} datasets, found {len(datasets)}"
        )

    expected_per_cell = len(methods)
    cells = Counter((row.dataset_id, row.patch_size) for row in rows)
    incomplete = {key: n for key, n in cells.items() if n != expected_per_cell}
    if incomplete:
        raise SystemExit(f"incomplete dataset/patch method cells: {incomplete}")

    worst_i = max(rows, key=lambda row: row.type_i_error)
    worst_ii = max(rows, key=lambda row: row.type_ii_error)
    print(
        "public result matrix valid: "
        f"{len(rows)} rows, {len(datasets)} datasets, "
        f"{len(methods)} methods, {len(patches)} patch sizes"
    )
    print(
        f"source commit: {rows[0].source_commit}; confidence target: "
        f"{rows[0].confidence_target:g}; affected fraction: "
        f"{rows[0].affected_fraction:g}"
    )
    print(
        f"worst type-I: {worst_i.type_i_error:.6f} "
        f"({worst_i.dataset_id}, {worst_i.method}, d={worst_i.patch_size:g})"
    )
    print(
        f"worst type-II: {worst_ii.type_ii_error:.6f} "
        f"({worst_ii.dataset_id}, {worst_ii.method}, d={worst_ii.patch_size:g})"
    )


if __name__ == "__main__":
    main()