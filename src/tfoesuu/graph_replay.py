from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import networkx as nx
import numpy as np
from scipy.optimize import linprog

from .graphs import GraphSpec
from .separations import binary_decision_kl


@dataclass(frozen=True)
class EdgeReplayCover:
    """Fractional vertex-cover allocation for sparse one-endpoint replay witnesses.

    For edge e=(u,v), an adversarial regression may occur at either endpoint.
    If vertex v is queried q_v times and a changed endpoint emits an observable
    replay witness with probability d_v per call, then a simple fixed allocation
    needs q_u+q_v large enough on every edge.  The normalized LP below is the
    fractional vertex-cover relaxation min sum q_v subject to q_u+q_v >= 1.

    This module is a CONJECTURE-HUNTING utility for T3, not a promoted theorem.
    """

    objective: float
    weights: np.ndarray
    success: bool
    message: str


def fractional_vertex_cover(graph: GraphSpec, costs: Sequence[float] | None = None) -> EdgeReplayCover:
    n=graph.n
    c=np.ones(n,dtype=float) if costs is None else np.asarray(costs,dtype=float)
    if c.shape!=(n,) or np.any(c<=0) or np.any(~np.isfinite(c)):
        raise ValueError("costs must be finite, positive, and length n")
    if graph.m==0:
        return EdgeReplayCover(0.0,np.zeros(n),True,"edgeless graph")
    # scipy linprog uses A_ub x <= b_ub, hence -(x_u+x_v) <= -1.
    A=np.zeros((graph.m,n),dtype=float)
    for i,(u,v) in enumerate(graph.edges):
        A[i,u]=-1.0; A[i,v]=-1.0
    res=linprog(c,A_ub=A,b_ub=-np.ones(graph.m),bounds=[(0,None)]*n,method="highs")
    return EdgeReplayCover(float(res.fun),np.asarray(res.x),bool(res.success),str(res.message))


def integral_vertex_cover_size(graph: GraphSpec) -> int:
    """Exact minimum vertex cover size for small graphs via NetworkX complement."""
    g=graph.to_networkx()
    # min vertex cover = n - max independent set = n - max clique(complement).
    comp=nx.complement(g)
    omega=max((len(c) for c in nx.find_cliques(comp)),default=0)
    return graph.n-omega


def edgewise_union_bound_rounds(graph: GraphSpec, d: float, beta: float) -> tuple[int,np.ndarray]:
    """A conservative T3 candidate allocation based on fractional cover weights.

    This is intentionally labelled computational/conjectural.  It allocates
    ceil(L*w_v) calls with L chosen so that an edge receiving total normalized
    weight at least one has miss probability at most beta/|E| under a stylized
    sparse-witness model with per-call witness probability d.
    """
    if graph.m<1: return 0,np.zeros(graph.n,dtype=int)
    if not 0<d<1: raise ValueError("d must lie in (0,1)")
    if not 0<beta<0.5: raise ValueError("beta must lie in (0,1/2)")
    cover=fractional_vertex_cover(graph)
    if not cover.success: raise RuntimeError(cover.message)
    L=math.log(beta/graph.m)/math.log1p(-d)
    counts=np.ceil(L*cover.weights).astype(int)
    return int(counts.sum()),counts


def edgewise_change_of_measure_floor(graph: GraphSpec, per_call_kl: float, beta: float) -> float:
    """LP lower-bound candidate from edgewise transcript constraints.

    If every edge alternative can place its informative change at an endpoint and
    a query to either endpoint contributes at most per_call_kl, change of measure
    yields E[N_u]+E[N_v] >= kl(1-beta,beta)/per_call_kl for each edge.
    Solving those constraints gives a fractional-cover lower-bound candidate.

    The premise must be proved for the final T3 access model before this can be
    promoted beyond a theorem-search utility.
    """
    if per_call_kl<=0: raise ValueError("per_call_kl must be positive")
    cover=fractional_vertex_cover(graph)
    return cover.objective*binary_decision_kl(beta)/per_call_kl
