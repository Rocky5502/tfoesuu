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
