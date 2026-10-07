#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from tfoesuu.control_replay import (
    control_replay_information_lower_bound,
    minimum_fractional_control_cover,
)
from tfoesuu.control_replay_benchmarks import (
    read_control_replay_structural_jsonl,
)
from tfoesuu.graphs import complete_bipartite_graph


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--benchmark",
        type=Path,
        default=Path("data/control_replay_structural_cases_v1.jsonl"),
    )
    args = ap.parse_args()

    rows = read_control_replay_structural_jsonl(args.benchmark)
    summaries = []
    for row in rows:
        graph = complete_bipartite_graph(row.high_count, row.low_count)
        high = tuple(range(row.high_count))
        cover = minimum_fractional_control_cover(
            graph, row.groups, row.costs, high
        )

        if cover.success != row.expected_control_feasible:
            raise RuntimeError(
                f"{row.case_id}: control feasibility mismatch"
            )
        if row.expected_control_feasible:
            if row.expected_control_cover is None:
                raise RuntimeError(
                    f"{row.case_id}: missing expected control-cover value"
                )
            if not np.isclose(
                cover.cost,
                row.expected_control_cover,
                rtol=1e-9,
                atol=1e-10,
            ):
                raise RuntimeError(
                    f"{row.case_id}: expected control cover "
                    f"{row.expected_control_cover}, found {cover.cost}"
                )

        floors = []
        for d in (1e-4, 5e-5):
            lower = control_replay_information_lower_bound(
                graph,
                row.groups,
                row.costs,
                high,
                p=0.20,
                shared_patch=0.10,
                fairness_tolerance=0.10,
                d=d,
                beta=0.05,
            )
            if not lower.success:
                raise RuntimeError(
                    f"{row.case_id}: information lower program failed: "
                    f"{lower.message}"
                )
            floors.append(lower.expected_cost_floor)

        ratio = floors[1] / floors[0]
        expected_ratio = (
            2.0 if row.expected_small_d_regime == "linear" else 4.0
        )
        tolerance = 5e-3 if expected_ratio == 2.0 else 1e-2
        if not np.isclose(ratio, expected_ratio, rtol=tolerance):
            raise RuntimeError(
                f"{row.case_id}: expected halving-d ratio "
                f"{expected_ratio}, found {ratio}"
            )

        summaries.append(
            {
                "case_id": row.case_id,
                "control_feasible": cover.success,
                "control_cover": (
                    cover.cost if cover.success else None
                ),
                "expected_small_d_regime": row.expected_small_d_regime,
                "lower_floor_halving_d_ratio": ratio,
            }
        )

    print(
        json.dumps(
            {
                "status": "passed",
                "rows": len(rows),
                "cases": summaries,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
