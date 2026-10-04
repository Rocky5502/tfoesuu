from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .graphs import GraphSpec


@dataclass(frozen=True)
class AllocationPatch:
    """A small group-specific patch to a randomized resource allocator."""

    affected_contexts: tuple[int, ...]
    delta: float
    common_shift: float = 0.0

    def __post_init__(self) -> None:
        if self.delta == 0.0:
            raise ValueError("delta must be nonzero")
        if len(set(self.affected_contexts)) != len(self.affected_contexts):
            raise ValueError("affected_contexts must be unique")


@dataclass(frozen=True)
class RandomizedResourceAllocatorPair:
    """Executable old/new software pair with replayable uniform randomness.

    Vertex encoding is vertex = 2 * context + group, with group in {0,1}.
    The old version ignores group. The new version applies patch.delta only to
    group 1 at selected contexts. An execution returns a binary allocation
    decision using a caller-supplied random tape value U in [0,1).

    This subject intentionally has no learned component.
    """

    baseline_probabilities: np.ndarray
    patch: AllocationPatch

    @classmethod
    def from_sequences(
        cls,
        baseline_probabilities: Sequence[float],
        affected_contexts: Iterable[int],
        delta: float,
        common_shift: float = 0.0,
    ) -> "RandomizedResourceAllocatorPair":
        p = np.asarray(baseline_probabilities, dtype=float)
        if p.ndim != 1 or len(p) < 1:
            raise ValueError("baseline_probabilities must be a nonempty vector")
        if np.any((p <= 0.0) | (p >= 1.0)):
            raise ValueError("baseline probabilities must lie strictly in (0,1)")
        affected = tuple(sorted(int(c) for c in affected_contexts))
        if any(c < 0 or c >= len(p) for c in affected):
            raise ValueError("affected context outside range")
        patch = AllocationPatch(
            affected,
            float(delta),
            float(common_shift),
        )
        for c in affected:
            q0 = p[c] + common_shift
            q1 = p[c] + common_shift + delta
            if not (0.0 < q0 < 1.0 and 0.0 < q1 < 1.0):
                raise ValueError("patched probabilities must remain in (0,1)")
        return cls(p.copy(), patch)

    @property
    def contexts(self) -> int:
        return len(self.baseline_probabilities)

    @property
    def n_vertices(self) -> int:
        return 2 * self.contexts

    @staticmethod
    def encode_vertex(context: int, group: int) -> int:
        if context < 0 or group not in (0, 1):
            raise ValueError("invalid context/group")
        return 2 * context + group

    def decode_vertex(self, vertex: int) -> tuple[int, int]:
        if not (0 <= vertex < self.n_vertices):
            raise ValueError("vertex outside subject domain")
        return vertex // 2, vertex % 2

    @property
    def fairness_graph(self) -> GraphSpec:
        edges = tuple(
            (self.encode_vertex(c, 0), self.encode_vertex(c, 1))
            for c in range(self.contexts)
        )
        return GraphSpec(
            self.n_vertices,
            edges,
            "resource_allocator_counterfactual_matching",
            {"contexts": self.contexts},
        )

    @property
    def replay_sound_impact_vertices(self) -> tuple[int, ...]:
        if self.patch.common_shift != 0.0:
            return tuple(
                self.encode_vertex(c, group)
                for c in self.patch.affected_contexts
                for group in (0, 1)
            )
        return tuple(
            self.encode_vertex(c, 1) for c in self.patch.affected_contexts
        )

    @property
    def impacted_edges(self) -> tuple[tuple[int, int], ...]:
        impacted = set(self.replay_sound_impact_vertices)
        return tuple(
            (u, v)
            for u, v in self.fairness_graph.edges
            if u in impacted or v in impacted
        )

    def probability(self, version: int, vertex: int) -> float:
        if version not in (0, 1):
            raise ValueError("version must be 0 or 1")
        context, group = self.decode_vertex(vertex)
        p = float(self.baseline_probabilities[context])
        if version == 1 and context in self.patch.affected_contexts:
            p += self.patch.common_shift
            if group == 1:
                p += self.patch.delta
        return p

    def execute(self, version: int, vertex: int, random_tape: float) -> int:
        if not (0.0 <= random_tape < 1.0):
            raise ValueError("random_tape must lie in [0,1)")
        return int(random_tape <= self.probability(version, vertex))

    def paired_delta(self, vertex: int, random_tape: float) -> int:
        return self.execute(1, vertex, random_tape) - self.execute(
            0, vertex, random_tape
        )

    def sample_paired_delta(
        self,
        vertex: int,
        count: int,
        rng: np.random.Generator,
    ) -> np.ndarray:
        if count < 1:
            raise ValueError("count must be >= 1")
        u = rng.random(count)
        p0 = self.probability(0, vertex)
        p1 = self.probability(1, vertex)
        return (u <= p1).astype(np.int8) - (u <= p0).astype(np.int8)



    def sample_edge_coupled_fairness_delta(
        self,
        context: int,
        count: int,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """Sample the four-way replay differential on one counterfactual edge.

        The same uniform random tape is used for:
          old group 0, new group 0, old group 1, new group 1.

        The returned value is
          (new-old)_group1 - (new-old)_group0.

        A common shift therefore cancels pathwise.
        """

        if not (0 <= context < self.contexts):
            raise ValueError("context outside subject domain")
        if count < 1:
            raise ValueError("count must be >= 1")

        u = rng.random(count)
        v0 = self.encode_vertex(context, 0)
        v1 = self.encode_vertex(context, 1)

        z0 = (
            (u <= self.probability(1, v0)).astype(np.int8)
            - (u <= self.probability(0, v0)).astype(np.int8)
        )
        z1 = (
            (u <= self.probability(1, v1)).astype(np.int8)
            - (u <= self.probability(0, v1)).astype(np.int8)
        )
        return z1 - z0


def linear_baseline(
    contexts: int,
    low: float = 0.25,
    high: float = 0.75,
) -> np.ndarray:
    """Deterministic baseline profile used by reproducibility experiments."""

    if contexts < 1:
        raise ValueError("contexts must be >= 1")
    if not (0.0 < low <= high < 1.0):
        raise ValueError("require 0 < low <= high < 1")
    if contexts == 1:
        return np.asarray([(low + high) / 2.0])
    return np.linspace(low, high, contexts, dtype=float)
