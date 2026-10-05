#!/usr/bin/env python3
"""Search small partial-replay instances for witness-scheduling cover gaps.

This is theorem-falsification infrastructure, not empirical evidence.  It
compares the integral replay-group cover with its fractional relaxation for the
*proved P17 witness-scheduling upper construction*.  It deliberately does not
interpret the fractional cover as a raw-output information lower bound.
"""

from __future__ import annotations

import argparse
import itertools

from tfoesuu.graphs import clique_graph
from tfoesuu.partial_replay import minimum_replay_group_cover
from tfoesuu.partial_replay_lower import minimum_fractional_replay_cover


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

    integral = minimum_replay_group_cover(graph, groups, costs)
    fractional = minimum_fractional_replay_cover(graph, groups, costs)
    if not integral.success or not fractional.success:
        raise RuntimeError(
            integral.message if not integral.success else fractional.message
        )

    gap = integral.objective / fractional.cost
    print(
        {
            "n": args.n,
            "max_group_size": args.max_group_size,
            "groups": len(groups),
            "fractional_witness_cover": fractional.cost,
            "integral_witness_cover": integral.objective,
            "integrality_gap": gap,
            "interpretation": "witness-scheduling upper construction only",
        }
    )


if __name__ == "__main__":
    main()
