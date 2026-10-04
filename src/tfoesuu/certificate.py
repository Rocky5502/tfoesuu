from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .graphs import Edge, GraphSpec


@dataclass(frozen=True)
class CertificatePruningResult:
    """Result of deterministic old-certificate / patch-envelope pruning."""

    safe_edges: tuple[Edge, ...]
    residual_graph: GraphSpec


def _edge_map_value(values: Mapping[Edge, float], edge: Edge, name: str) -> float:
    if edge in values:
        return float(values[edge])
    rev = (edge[1], edge[0])
    if rev in values:
        # Thresholds and absolute patch bounds are orientation invariant. Old gaps
        # are only used through absolute value in pruning, so reversal is safe.
        return float(values[rev])
    raise KeyError(f"missing {name} for edge {edge}")


def prune_with_patch_envelopes(
    graph: GraphSpec,
    old_edge_gaps: Mapping[Edge, float],
    thresholds: Mapping[Edge, float],
    patch_effect_bounds: Mapping[Edge, float],
) -> CertificatePruningResult:
    """Prune edges certified safe without executing the new version.

    For edge e=(u,v), let g0_e be the old expected gap and let b_e be a sound
    deterministic envelope satisfying

        |(mu1_u-mu0_u) - (mu1_v-mu0_v)| <= b_e.

    Triangle inequality gives |g1_e| <= |g0_e| + b_e.  Therefore an edge is
    reusable without stochastic testing whenever |g0_e| + b_e <= tau_e.
    """

    safe: list[Edge] = []
    residual: list[Edge] = []

    for edge in graph.edges:
        gap = _edge_map_value(old_edge_gaps, edge, "old gap")
        tau = _edge_map_value(thresholds, edge, "threshold")
        bound = _edge_map_value(patch_effect_bounds, edge, "patch-effect bound")

        if tau < 0:
            raise ValueError(f"threshold must be nonnegative on edge {edge}")
        if bound < 0:
            raise ValueError(f"patch-effect bound must be nonnegative on edge {edge}")

        if abs(gap) + bound <= tau:
            safe.append(edge)
        else:
            residual.append(edge)

    residual_graph = GraphSpec(
        graph.n,
        tuple(residual),
        f"{graph.family}_residual",
        {
            **graph.metadata,
            "original_edges": graph.m,
            "safe_edges": len(safe),
            "residual_edges": len(residual),
        },
    )
    return CertificatePruningResult(tuple(safe), residual_graph)
