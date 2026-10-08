#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from scipy.stats import beta as beta_distribution

from tfoesuu.public_results import (
    read_public_results,
    validate_public_result_matrix,
    validate_publication_coverage,
)


METHOD_ORDER = ["independent", "vertex-paired", "four-way", "suite", "tfoesuu"]


def _fmt_count(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value)):,}"
    return f"{value:,.1f}"


def _clopper_pearson_interval(
    count: int,
    trials: int,
    alpha: float,
) -> tuple[float, float]:
    """Exact two-sided binomial interval at confidence 1-alpha."""
    if not (0 <= count <= trials) or trials <= 0:
        raise ValueError("invalid binomial count/trial total")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie in (0,1)")
    lo = 0.0 if count == 0 else float(
        beta_distribution.ppf(alpha / 2.0, count, trials - count + 1)
    )
    hi = 1.0 if count == trials else float(
        beta_distribution.ppf(1.0 - alpha / 2.0, count + 1, trials - count)
    )
    return lo, hi


def _simultaneous_max_error_interval(
    type_i_count: int,
    type_ii_count: int,
    trials: int,
    family_alpha: float = 0.05,
) -> tuple[float, float]:
    """Bonferroni-simultaneous interval for max(type-I, type-II) error.

    Uses two Clopper-Pearson intervals, each with individual miscoverage
    family_alpha/2. A union bound gives familywise >=1-family_alpha
    coverage without assuming independence between the error estimators.
    For the maximum parameter, take the maximum of the two lower
    endpoints and the maximum of the two upper endpoints.
    """
    if not (0.0 < family_alpha < 1.0):
        raise ValueError("family_alpha must lie in (0,1)")
    intervals = (
        _clopper_pearson_interval(type_i_count, trials, family_alpha / 2.0),
        _clopper_pearson_interval(type_ii_count, trials, family_alpha / 2.0),
    )
    return max(lo for lo, _ in intervals), max(hi for _, hi in intervals)


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
            "Max error is $\\max(\\widehat{\\alpha},\\widehat{\\beta})$ for TFOESUU. "
            "Its interval is a Bonferroni-simultaneous 95\\% "
            "Clopper--Pearson interval for two binomial error rates; "
            "all rows use the same frozen confidence target and source commit.}"
        ),
        "\\label{tab:public-main-results}",
        "\\scriptsize",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{@{}lrrrrrrrrr@{}}",
        "\\toprule",
        "Dataset & $|V|$ & $|E|$ & Independent & Vertex-paired & Four-way & Suite & TFOESUU & Max error (95\\% CI) & Speedup \\\\",
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
        lo, hi = _simultaneous_max_error_interval(
            tfo.type_i_error_count, tfo.type_ii_error_count, tfo.trials
        )
        speedup = (
            methods["independent"].concrete_program_executions
            / tfo.concrete_program_executions
        )
        values = [
            anchor.dataset_name.replace("&", "\\&"),
            str(anchor.graph_vertices),
            str(anchor.graph_edges),
            *[_fmt_count(methods[m].concrete_program_executions) for m in METHOD_ORDER],
            f"{max_err:.4f} [{lo:.4f},{hi:.4f}]",
            f"${speedup:.2f}\\times$",
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
    ap.add_argument(
        "--registry",
        type=Path,
        default=Path("data/public_benchmark_registry_v1.jsonl"),
    )
    args = ap.parse_args()
    rows = read_public_results(args.results)

    # Exploratory output to an external path may use partial matrices, but
    # anything written into the tracked manuscript-generated directory must
    # first pass the strict seven-dataset publication release gate.
    manuscript_generated_dir = Path("paper/generated").resolve()
    if args.output.resolve().is_relative_to(manuscript_generated_dir):
        registry_rows = [
            json.loads(line)
            for line in args.registry.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        registry_ids = [item["benchmark_id"] for item in registry_rows]
        if len(registry_ids) != 7 or len(set(registry_ids)) != 7:
            raise ValueError("submission table requires exactly seven unique registry IDs")
        validate_publication_coverage(rows, registry_ids)
    chosen = render_table(rows, args.output, args.patch_size)
    print(f"wrote {args.output} for d={chosen:g}")


if __name__ == "__main__":
    main()