#!/usr/bin/env python3
"""Validate every frozen P17 parameter-stress row against executable theorem code.

This command derives deterministic LP/schedule quantities only. It does not run
Monte Carlo trials and must not be reported as empirical evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.partial_replay_benchmarks import (
    materialize_partial_replay_spec,
    read_partial_replay_jsonl,
)
from tfoesuu.partial_replay_lower import (
    active_vertex_contrast_schedule,
    minimum_fractional_active_vertex_cover,
    minimum_fractional_replay_cover,
    raw_output_information_lower_bound,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--benchmark",
        type=Path,
        default=Path("data/partial_replay_benchmark_v1.jsonl"),
    )
    args = ap.parse_args()

    rows = read_partial_replay_jsonl(args.benchmark)
    if not rows:
        raise SystemExit("partial-replay benchmark manifest is empty")

    family_counts: dict[str, int] = {}
    max_groups = 0
    max_geometry_ratio = 0.0

    for row in rows:
        graph, groups, costs = materialize_partial_replay_spec(row)
        vertex = minimum_fractional_active_vertex_cover(graph, groups, costs)
        edge = minimum_fractional_replay_cover(graph, groups, costs)
        raw = raw_output_information_lower_bound(
            graph,
            groups,
            costs,
            p=row.p,
            shared_patch=row.shared_patch,
            d=row.d,
            beta=row.beta,
        )
        contrast = active_vertex_contrast_schedule(
            graph,
            groups,
            costs,
            d=row.d,
            beta=row.beta,
        )

        if not vertex.success:
            raise RuntimeError(f"{row.benchmark_id}: active-vertex LP failed: {vertex.message}")
        if not edge.success:
            raise RuntimeError(f"{row.benchmark_id}: witness LP failed: {edge.message}")
        if not raw.success:
            raise RuntimeError(f"{row.benchmark_id}: raw-information LP failed: {raw.message}")
        if vertex.cost > edge.cost + 1e-9:
            raise RuntimeError(f"{row.benchmark_id}: violated C_vert <= C_edge")
        if abs(contrast.normalized_fractional_cost - vertex.cost) > 1e-8:
            raise RuntimeError(f"{row.benchmark_id}: raw-contrast geometry drift")
        if raw.expected_cost_floor <= 0.0:
            raise RuntimeError(f"{row.benchmark_id}: nonpositive information floor")
        upper_cap = (
            contrast.scale * vertex.cost
            + contrast.additive_rounding_cap
            + 1e-8
        )
        if contrast.total_cost > upper_cap:
            raise RuntimeError(f"{row.benchmark_id}: contrast rounding bound failed")

        family_counts[row.graph_family] = family_counts.get(row.graph_family, 0) + 1
        max_groups = max(max_groups, len(groups))
        max_geometry_ratio = max(max_geometry_ratio, edge.cost / vertex.cost)

    print(
        json.dumps(
            {
                "schema": "tfoesuu-p17-manifest-validation-v1",
                "rows": len(rows),
                "families": dict(sorted(family_counts.items())),
                "max_groups_per_row": max_groups,
                "max_c_edge_over_c_vert": max_geometry_ratio,
                "checks": [
                    "materialization",
                    "C_vert_feasible",
                    "C_edge_feasible",
                    "raw_information_feasible",
                    "C_vert_le_C_edge",
                    "raw_contrast_uses_C_vert",
                    "positive_information_floor",
                    "contrast_rounding_bound",
                ],
                "empirical_results": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
