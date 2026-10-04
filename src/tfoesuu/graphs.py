from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx
import numpy as np

Edge = tuple[int, int]


@dataclass(frozen=True)
class GraphSpec:
    """Small immutable representation used by theorem and experiment code."""

    n: int
    edges: tuple[Edge, ...]
    family: str
    metadata: dict[str, object]

    def __post_init__(self) -> None:
        if self.n < 0:
            raise ValueError("n must be nonnegative")
        seen: set[Edge] = set()
        normalized: list[Edge] = []
        for u, v in self.edges:
            if not (0 <= u < self.n and 0 <= v < self.n):
                raise ValueError(f"edge {(u, v)} outside vertex range")
            if u == v:
                raise ValueError("self-loops are not used in the fairness graph")
            e = (u, v) if u < v else (v, u)
            if e not in seen:
                seen.add(e)
                normalized.append(e)
        object.__setattr__(self, "edges", tuple(sorted(normalized)))

    @property
    def m(self) -> int:
        return len(self.edges)

    def to_networkx(self) -> nx.Graph:
        g = nx.Graph()
        g.add_nodes_from(range(self.n))
        g.add_edges_from(self.edges)
        return g


def edge_graph() -> GraphSpec:
    return GraphSpec(2, ((0, 1),), "edge", {})


def matching_graph(k: int) -> GraphSpec:
    if k < 1:
        raise ValueError("k must be >= 1")
    return GraphSpec(2 * k, tuple((2 * i, 2 * i + 1) for i in range(k)), "matching", {"k": k})


def star_graph(k: int) -> GraphSpec:
    if k < 1:
        raise ValueError("k must be >= 1")
    return GraphSpec(k + 1, tuple((0, i) for i in range(1, k + 1)), "star", {"leaves": k})


def path_graph(n: int) -> GraphSpec:
    if n < 2:
        raise ValueError("n must be >= 2")
    return GraphSpec(n, tuple((i, i + 1) for i in range(n - 1)), "path", {})


def clique_graph(n: int) -> GraphSpec:
    if n < 2:
        raise ValueError("n must be >= 2")
    return GraphSpec(n, tuple((i, j) for i in range(n) for j in range(i + 1, n)), "clique", {})


def complete_bipartite_graph(a: int, b: int) -> GraphSpec:
    if a < 1 or b < 1:
        raise ValueError("a and b must be >= 1")
    edges = tuple((i, a + j) for i in range(a) for j in range(b))
    return GraphSpec(a + b, edges, "complete_bipartite", {"a": a, "b": b})


def erdos_renyi_graph(n: int, p: float, seed: int) -> GraphSpec:
    if n < 2:
        raise ValueError("n must be >= 2")
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must lie in [0,1]")
    rng = np.random.default_rng(seed)
    edges = tuple((i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p)
    if not edges:
        edges = ((0, 1),)
    return GraphSpec(n, edges, "erdos_renyi", {"p": p, "seed": seed})


def from_edges(n: int, edges: Iterable[Edge], family: str = "custom") -> GraphSpec:
    return GraphSpec(n, tuple(edges), family, {})
