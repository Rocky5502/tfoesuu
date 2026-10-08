#!/usr/bin/env python3
"""Enumerate small P19 replay topologies and expose mixed asymptotic regimes.

This is a theorem-falsification search, not an empirical benchmark.  For each
legal replay-group family we compare the exact mixed-KL information LP at d and
d/2.  Ratios near 2 indicate first-order (d^-1) cost; ratios near 4 indicate
second-order (d^-2) cost.  Mixed topologies are retained explicitly so a future
P20 statement must explain them rather than silently collapsing to the two
extreme fixtures.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations

from tfoesuu.control_replay import (
    control_replay_information_lower_bound,
    minimum_fractional_control_cover,
    mixed_control_asymptotic_coefficients,
    mixed_control_leading_coefficient,
)
from tfoesuu.graphs import complete_bipartite_graph


def candidate_groups(high_count: int, low_count: int) -> tuple[tuple[int, ...], ...]:
    """Pairs only: high-high controls and high-low boundary observations."""
    high = range(high_count)
    low = range(high_count, high_count + low_count)
    return tuple(combinations(high, 2)) + tuple((h, l) for h in high for l in low)


def enumerate_families(high_count: int, low_count: int, max_groups: int):
    graph = complete_bipartite_graph(high_count, low_count)
    high = tuple(range(high_count))
    universe = candidate_groups(high_count, low_count)
    for size in range(1, min(max_groups, len(universe)) + 1):
        for groups in combinations(universe, size):
            # Every alternative must at least be observable.
            if any(not any(x in group for group in groups) for x in high):
                continue
            costs = (1.0,) * len(groups)
            cover = minimum_fractional_control_cover(graph, groups, costs, high)
            yield graph, high, groups, costs, cover


def exact_floor(graph, high, groups, costs, d: float) -> float:
    out = control_replay_information_lower_bound(
        graph,
        groups,
        costs,
        high,
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=d,
        beta=0.05,
    )
    if not out.success:
        raise RuntimeError(out.message)
    return out.expected_cost_floor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--high", type=int, default=3)
    parser.add_argument("--low", type=int, default=2)
    parser.add_argument("--max-groups", type=int, default=4)
    parser.add_argument("--d", type=float, default=1e-4)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    rows = []
    for graph, high, groups, costs, cover in enumerate_families(
        args.high, args.low, args.max_groups
    ):
        qd = exact_floor(graph, high, groups, costs, args.d)
        qh = exact_floor(graph, high, groups, costs, args.d / 2.0)
        leading = mixed_control_leading_coefficient(
            graph, groups, costs, high,
            p=0.20, shared_patch=0.10, fairness_tolerance=0.10, beta=0.05,
        )
        if not leading.success:
            raise RuntimeError(leading.message)
        two_term = mixed_control_asymptotic_coefficients(
            graph, groups, costs, high,
            p=0.20, shared_patch=0.10, fairness_tolerance=0.10, beta=0.05,
        )
        if not two_term.success:
            raise RuntimeError(two_term.message)
        a0 = leading.coefficient
        leading_weights = leading.scaled_query_weights
        leading_uncovered = leading.uncovered_high_vertices
        ratio = qh / qd
        control_degree = {
            x: sum(
                x in g and sum(v in high for v in g) >= 2
                for g in groups
            )
            for x in high
        }
        uncovered = tuple(x for x, deg in control_degree.items() if deg == 0)
        rows.append(
            {
                "groups": groups,
                "control_cover_feasible": cover.success,
                "control_cover": cover.cost if cover.success else None,
                "control_uncovered": uncovered,
                "floor_d": qd,
                "floor_half_d": qh,
                "ratio_half_over_full": ratio,
                "apparent_exponent": 1 if ratio < 3.0 else 2,
                "exact_A0": a0,
                "exact_B0": two_term.inverse_linear_coefficient,
                "d2_floor": args.d * args.d * qd,
                "d2_floor_error": args.d * args.d * qd - a0,
                "scaled_residual": args.d * (
                    qd - a0 / (args.d * args.d)
                ),
                "scaled_residual_error": args.d * (
                    qd - a0 / (args.d * args.d)
                ) - two_term.inverse_linear_coefficient,
                "leading_boundary_weights": leading_weights.tolist(),
                "leading_uncovered": leading_uncovered,
            }
        )

    rows.sort(
        key=lambda row: (
            len(row["control_uncovered"]),
            abs(row["ratio_half_over_full"] - (2 if row["control_cover_feasible"] else 4)),
            len(row["groups"]),
        )
    )
    print(json.dumps(rows[: args.top], indent=2))


if __name__ == "__main__":
    main()
