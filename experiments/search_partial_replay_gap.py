#!/usr/bin/env python3
"""Search small partial-replay instances for integral/fractional cover gaps.

This is theorem-falsification infrastructure, not empirical evidence.
"""

from __future__ import annotations

import argparse
import itertools

from tfoesuu.graphs import clique_graph
from tfoesuu.partial_replay import minimum_replay_group_cover
from tfoesuu.partial_replay_lower import fractional_group_replay_lower_bound


def all_groups(n: int, max_group_size: int):
    for k in range(2, min(n, max_group_size) + 1):
        yield from itertools.combinations(range(n), k)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--max-group-size", type=int, default=3)
    args = ap.parse_args()

    graph = clique_graph(args.n)
    groups = list(all_groups(args.n, args.max_group_size))
    costs = [2.0 * len(g) for g in groups]

    upper = minimum_replay_group_cover(graph, groups, costs)
    lower = fractional_group_replay_lower_bound(
        graph, groups, costs, per_informative_query_kl=1.0, beta=0.05
    )
    if not upper.success or not lower.success:
        raise RuntimeError(upper.message if not upper.success else lower.message)

    gap = upper.objective / lower.normalized_cost
    print(
        {
            "n": args.n,
            "max_group_size": args.max_group_size,
            "groups": len(groups),
            "fractional_normalized": lower.normalized_cost,
            "integral": upper.objective,
            "integrality_gap": gap,
        }
    )


if __name__ == "__main__":
    main()
