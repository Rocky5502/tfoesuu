from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


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
