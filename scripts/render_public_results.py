#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from tfoesuu.public_results import read_public_results, validate_public_result_matrix


FOCAL = "#1F6F5F"
RISK = "#B5473C"
INK = "#171717"
GRAY = "#8D8D88"
LIGHT = "#B6B6B0"
GRID = "#E8E8E5"

METHOD_STYLE = {
    "independent": (LIGHT, "o", "--"),
    "vertex-paired": (GRAY, "s", "-."),
    "four-way": ("#5E6462", "^", ":"),
    "suite": ("#404040", "D", "--"),
    "tfoesuu": (FOCAL, "o", "-"),
}


def aggregate(rows):
    by_method_patch = defaultdict(list)
    by_method_patch_err = defaultdict(list)
    by_dataset_speedup = defaultdict(list)
    by_dataset_graph = {}

    independent = {}
    for row in rows:
        key = (row.dataset_id, row.patch_size, row.seed)
        if row.method == "independent":
            independent[key] = row.concrete_program_executions

    for row in rows:
        by_method_patch[(row.method, row.patch_size)].append(
            row.concrete_program_executions
        )
        by_method_patch_err[(row.method, row.patch_size)].append(
            max(row.type_i_error, row.type_ii_error)
        )
        if row.method == "tfoesuu":
            key = (row.dataset_id, row.patch_size, row.seed)
            if key in independent:
                by_dataset_speedup[row.dataset_name].append(
                    independent[key] / row.concrete_program_executions
                )
            by_dataset_graph[row.dataset_name] = (
                row.graph_edges, row.concrete_program_executions
            )
    return by_method_patch, by_method_patch_err, by_dataset_speedup, by_dataset_graph


def render(rows, output: Path, png_output: Path | None = None) -> None:
    validate_public_result_matrix(rows)
    a, b, speedups, graph = aggregate(rows)

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 8.5,
        "axes.titlesize": 9.5,
        "axes.labelsize": 8.5,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "legend.fontsize": 7.5,
        "axes.edgecolor": "#404040",
        "axes.labelcolor": INK,
        "text.color": INK,
    })

    fig, axes = plt.subplots(2, 2, figsize=(7.0, 6.0), constrained_layout=True)

    ax = axes[0, 0]
    for method in METHOD_STYLE:
        points = sorted(
            (patch, float(np.median(vals)))
            for (m, patch), vals in a.items()
            if m == method
        )
        if not points:
            continue
        x, y = zip(*points)
        color, marker, ls = METHOD_STYLE[method]
        ax.plot(x, y, label=method, color=color, marker=marker, linestyle=ls, linewidth=1.4)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("(a) Execution cost tracks replay strength")
    ax.set_xlabel("Patch size d (log scale)")
    ax.set_ylabel("Median concrete executions (log scale)")
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2)

    ax = axes[0, 1]
    for method in METHOD_STYLE:
        points = sorted(
            (patch, float(np.max(vals)))
            for (m, patch), vals in b.items()
            if m == method
        )
        if not points:
            continue
        x, y = zip(*points)
        color, marker, ls = METHOD_STYLE[method]
        ax.plot(x, y, label=method, color=color, marker=marker, linestyle=ls, linewidth=1.4)
    target = rows[0].confidence_target
    ax.axhline(target, color=RISK, linewidth=1.0, linestyle="--", label="confidence target")
    ax.set_xscale("log")
    ax.set_title("(b) Worst observed error stays auditable")
    ax.set_xlabel("Patch size d (log scale)")
    ax.set_ylabel("Max(type-I, type-II error)")
    ax.set_ylim(bottom=0.0)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1, 0]
    names = sorted(speedups)
    values = [float(np.median(speedups[name])) for name in names]
    y = np.arange(len(names))
    ax.barh(y, values, color=FOCAL)
    ax.set_yticks(y, labels=names)
    ax.set_title("(c) TFOESUU execution savings across datasets")
    ax.set_xlabel("Median speedup vs. independent execution (×)")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1, 1]
    for name, (edges, executions) in sorted(graph.items()):
        ax.scatter(edges, executions, color=FOCAL, s=28)
        ax.annotate(name, (edges, executions), xytext=(3, 3), textcoords="offset points", fontsize=7.0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("(d) Cost versus fairness-graph size")
    ax.set_xlabel("Fairness edges |E| (log scale)")
    ax.set_ylabel("TFOESUU executions (log scale)")
    ax.grid(color=GRID, linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight")
    if png_output is not None:
        png_output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(png_output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("paper/figures/public_results.pdf"))
    ap.add_argument("--png-output", type=Path, default=Path("paper/figures/public_results.png"))
    args = ap.parse_args()
    rows = read_public_results(args.results)
    render(rows, args.output, args.png_output)
    print(f"wrote {args.output} and {args.png_output}")


if __name__ == "__main__":
    main()