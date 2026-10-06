from __future__ import annotations

from dataclasses import asdict, dataclass
import itertools
import json
from pathlib import Path
from typing import Iterable

from .graphs import GraphSpec, clique_graph, matching_graph, path_graph


@dataclass(frozen=True)
class PartialReplayBenchmarkSpec:
    """Deterministic specification for P17 theorem-falsification runs."""

    benchmark_id: str
    graph_family: str
    n: int
    max_group_size: int
    cost_per_vertex: float
    p: float
    shared_patch: float
    d: float
    beta: float
    seed: int


def partial_replay_benchmark_v1() -> list[PartialReplayBenchmarkSpec]:
    """Frozen stress grid for partial synchronized replay.

    These rows are specification data, not empirical results. They span graph
    structure, legal replay-group size, cost scale, and small differential
    effects while keeping the homogeneous Bernoulli parameters in the valid
    interior range.
    """
    graph_specs = [
        ("clique", 3), ("clique", 4), ("clique", 5), ("clique", 6),
        ("path", 3), ("path", 4), ("path", 5), ("path", 6),
        ("matching", 4), ("matching", 6),
    ]
    rows: list[PartialReplayBenchmarkSpec] = []
    i = 0
    for family, n in graph_specs:
        group_sizes = sorted({2, min(3, n), min(4, n)})
        for max_group_size in group_sizes:
            for cost_per_vertex in (1.0, 2.0):
                for d in (0.05, 0.02, 0.01):
                    i += 1
                    rows.append(
                        PartialReplayBenchmarkSpec(
                            benchmark_id=f"p17-{i:04d}",
                            graph_family=family,
                            n=n,
                            max_group_size=max_group_size,
                            cost_per_vertex=cost_per_vertex,
                            p=0.20,
                            shared_patch=0.10,
                            d=d,
                            beta=0.05,
                            seed=50_000 + i,
                        )
                    )
    return rows


def materialize_partial_replay_spec(
    spec: PartialReplayBenchmarkSpec,
) -> tuple[GraphSpec, tuple[tuple[int, ...], ...], tuple[float, ...]]:
    """Materialize one frozen P17 stress specification.

    The v1 manifest semantics are:
      * graph_family selects the canonical graph constructor;
      * every vertex subset of size 2..max_group_size is a legal replay group;
      * one group query costs cost_per_vertex times the group cardinality.

    The seed belongs to downstream stochastic simulations; materialization of the
    graph/group/cost geometry itself is deterministic.
    """
    if spec.graph_family == "clique":
        graph = clique_graph(spec.n)
    elif spec.graph_family == "path":
        graph = path_graph(spec.n)
    elif spec.graph_family == "matching":
        if spec.n % 2:
            raise ValueError("matching benchmark n must be even")
        graph = matching_graph(spec.n // 2)
    else:
        raise ValueError(f"unsupported partial-replay graph family: {spec.graph_family}")

    if not (2 <= spec.max_group_size <= spec.n):
        raise ValueError("max_group_size must lie in [2,n]")
    if not (spec.cost_per_vertex > 0.0):
        raise ValueError("cost_per_vertex must be positive")

    groups = tuple(
        group
        for size in range(2, spec.max_group_size + 1)
        for group in itertools.combinations(range(spec.n), size)
    )
    costs = tuple(spec.cost_per_vertex * len(group) for group in groups)
    return graph, groups, costs


def write_partial_replay_jsonl(
    rows: Iterable[PartialReplayBenchmarkSpec],
    path: str | Path,
) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_partial_replay_jsonl(
    path: str | Path,
) -> list[PartialReplayBenchmarkSpec]:
    rows: list[PartialReplayBenchmarkSpec] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(PartialReplayBenchmarkSpec(**json.loads(line)))
    return rows


@dataclass(frozen=True)
class PartialReplayStructuralCase:
    """Deterministic P17 structural-geometry falsification case."""

    case_id: str
    regime: str
    graph_family: str
    n: int
    group_rule: str
    expected_c_vert: float
    expected_raw_contrast_cost: float
    expected_c_edge: float | None
    expected_ratio: float | None


def partial_replay_structural_cases_v1() -> list[PartialReplayStructuralCase]:
    """Audited specification cases for equality, finite gap, and infinite gap.

    These rows encode exact mathematical expectations.  They are not empirical
    observations and must remain synchronized with the P17 regression tests and
    proof audit.
    """
    rows = [
        PartialReplayStructuralCase(
            case_id="p17-struct-equality-matching",
            regime="coherent-equality",
            graph_family="matching",
            n=4,
            group_rule="fairness_edges",
            expected_c_vert=2.0,
            expected_raw_contrast_cost=2.0,
            expected_c_edge=2.0,
            expected_ratio=1.0,
        )
    ]
    for n in range(3, 9):
        rows.append(
            PartialReplayStructuralCase(
                case_id=f"p17-struct-clique-pairs-n{n}",
                regime="finite-linear-gap",
                graph_family="clique",
                n=n,
                group_rule="fairness_edges",
                expected_c_vert=n / 2.0,
                expected_raw_contrast_cost=n / 2.0,
                expected_c_edge=n * (n - 1) / 2.0,
                expected_ratio=n - 1.0,
            )
        )
    rows.append(
        PartialReplayStructuralCase(
            case_id="p17-struct-finite-info-infinite-witness",
            regime="infinite-witness-gap",
            graph_family="path",
            n=3,
            group_rule="reference_pairs_02_12",
            expected_c_vert=2.0,
            expected_raw_contrast_cost=2.0,
            expected_c_edge=None,
            expected_ratio=None,
        )
    )
    return rows


def write_partial_replay_structural_jsonl(
    rows: Iterable[PartialReplayStructuralCase],
    path: str | Path,
) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_partial_replay_structural_jsonl(
    path: str | Path,
) -> list[PartialReplayStructuralCase]:
    rows: list[PartialReplayStructuralCase] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(PartialReplayStructuralCase(**json.loads(line)))
    return rows


@dataclass(frozen=True)
class PartialReplayScopeCase:
    """Deterministic falsification case for the scope of a P17 tester."""

    case_id: str
    regime: str
    fairness_tau: float
    old_threshold_0: float
    old_threshold_1: float
    new_threshold_0: float
    new_threshold_1: float
    tape_u: float
    expected_fair_null: bool
    expected_raw_contrast: bool
    expected_false_positive_measure: float


def partial_replay_scope_cases_v1() -> list[PartialReplayScopeCase]:
    """Frozen counterexample showing why P17-A needs a homogeneous null."""
    return [
        PartialReplayScopeCase(
            case_id="p17-scope-heterogeneous-fair-null-raw-contrast",
            regime="heterogeneous-null-false-positive",
            fairness_tau=0.20,
            old_threshold_0=0.20,
            old_threshold_1=0.40,
            new_threshold_0=0.30,
            new_threshold_1=0.45,
            tape_u=0.25,
            expected_fair_null=True,
            expected_raw_contrast=True,
            expected_false_positive_measure=0.15,
        )
    ]


def write_partial_replay_scope_jsonl(
    rows: Iterable[PartialReplayScopeCase],
    path: str | Path,
) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_partial_replay_scope_jsonl(
    path: str | Path,
) -> list[PartialReplayScopeCase]:
    rows: list[PartialReplayScopeCase] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(PartialReplayScopeCase(**json.loads(line)))
    return rows
