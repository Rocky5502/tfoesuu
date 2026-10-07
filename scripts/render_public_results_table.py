#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import numpy as np

from tfoesuu.public_results import read_public_results, validate_public_result_matrix


METHOD_ORDER = ["independent", "vertex-paired", "four-way", "suite", "tfoesuu"]


def _fmt_count(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value)):,}"
    return f"{value:,.1f}"


def render_table(rows, output: Path, patch_size: float | None = None) -> float:
    validate_public_result_matrix(rows)
    available = sorted({row.patch_size for row in rows})
    chosen = min(available) if patch_size is None else patch_size
    selected = [row for row in rows if abs(row.patch_size - chosen) < 1e-12]
    if not selected:
        raise ValueError(f"no result rows for patch size {chosen}")

    grouped = defaultdict(dict)
    meta = {}
    for row in selected:
        if row.method in grouped[row.dataset_id]:
            raise ValueError(
                f"multiple rows for {row.dataset_id}/{row.method} at d={chosen}; "
                "aggregate seeds before rendering the main table"
            )
        grouped[row.dataset_id][row.method] = row
        meta[row.dataset_id] = row

    lines = [
        "\\begin{table}[t]",
        "\\centering",
        (
            "\\caption{Public-benchmark execution cost at the frozen patch size "
            f"$d={chosen:g}$. Concrete program executions are lower-is-better. "
            "Max error is $\\max(\\widehat{\\alpha},\\widehat{\\beta})$ for TFOESUU; "
            "all rows use the same frozen confidence target and result commit.}"
        ),
        "\\label{tab:public-main-results}",
        "\\scriptsize",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{@{}lrrrrrrrrr@{}}",
        "\\toprule",
        "Dataset & $|V|$ & $|E|$ & Independent & Vertex-paired & Four-way & Suite & TFOESUU & Max error \\\\",
        "\\midrule",
    ]
    for dataset_id in sorted(grouped, key=lambda key: meta[key].dataset_name):
        methods = grouped[dataset_id]
        missing = [method for method in METHOD_ORDER if method not in methods]
        if missing:
            raise ValueError(f"{dataset_id}: missing methods {missing}")
        anchor = meta[dataset_id]
        tfo = methods["tfoesuu"]
        max_err = max(tfo.type_i_error, tfo.type_ii_error)
        values = [
            anchor.dataset_name.replace("&", "\\&"),
            str(anchor.graph_vertices),
            str(anchor.graph_edges),
            *[_fmt_count(methods[m].concrete_program_executions) for m in METHOD_ORDER],
            f"{max_err:.4f}",
        ]
        lines.append(" & ".join(values) + " \\\\")
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}%",
        "}",
        "\\end{table}",
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return chosen


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("paper/generated/public_results_table.tex"),
    )
    ap.add_argument("--patch-size", type=float)
    args = ap.parse_args()
    rows = read_public_results(args.results)
    chosen = render_table(rows, args.output, args.patch_size)
    print(f"wrote {args.output} for d={chosen:g}")


if __name__ == "__main__":
    main()