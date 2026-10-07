from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .graphs import Edge, GraphSpec


@dataclass(frozen=True)
class CertificatePruningResult:
    """Result of deterministic old-certificate / patch-envelope pruning."""

    safe_edges: tuple[Edge, ...]
    residual_graph: GraphSpec


@dataclass(frozen=True)
class ResidualEdgeMargins:
    """Directional threshold headroom retained from an old fair certificate."""

    edge: Edge
    old_signed_gap: float
    threshold: float
    positive_headroom: float
    negative_headroom: float


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


def threshold_residual_margins(
    graph: GraphSpec,
    old_signed_gaps: Mapping[Edge, float],
    thresholds: Mapping[Edge, float],
) -> tuple[ResidualEdgeMargins, ...]:
    """Return directional patch-contrast boundaries for thresholded fairness.

    For an oriented edge e=(u,v), let g0 = mu0_u - mu0_v and let
    theta_vtx = mu1 - mu0. The new signed gap is

        g1 = g0 + theta_u - theta_v.

    Fairness requires |g1| <= tau. Hence the patch contrast theta_u-theta_v
    may increase by at most tau-g0 in the positive direction and by at most
    tau+g0 in the negative direction before crossing the fairness boundary.

    This helper only exposes retained certificate geometry; it is not a
    statistical testing theorem.
    """

    out: list[ResidualEdgeMargins] = []
    for edge in graph.edges:
        if edge in old_signed_gaps:
            gap = float(old_signed_gaps[edge])
        elif (edge[1], edge[0]) in old_signed_gaps:
            gap = -float(old_signed_gaps[(edge[1], edge[0])])
        else:
            raise KeyError(f"missing old signed gap for edge {edge}")

        tau = _edge_map_value(thresholds, edge, "threshold")
        if tau < 0:
            raise ValueError(f"threshold must be nonnegative on edge {edge}")
        if abs(gap) > tau + 1e-12:
            raise ValueError(
                f"old certificate is not fair on edge {edge}: |{gap}| > {tau}"
            )

        out.append(
            ResidualEdgeMargins(
                edge=edge,
                old_signed_gap=gap,
                threshold=tau,
                positive_headroom=tau - gap,
                negative_headroom=tau + gap,
            )
        )
    return tuple(out)
