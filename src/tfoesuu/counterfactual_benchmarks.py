from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class CounterfactualReplayBenchmarkSpec:
    benchmark_id: str
    p: float
    shared_patch: float
    d: float
    beta: float
    seed: int


def counterfactual_replay_benchmark_v1() -> list[CounterfactualReplayBenchmarkSpec]:
    """Frozen theorem-stress grid for P15 four-way replay."""

    rows: list[CounterfactualReplayBenchmarkSpec] = []
    i = 0
    for p in (0.20, 0.35, 0.50):
        for shared in (0.05, 0.10, 0.20, 0.30):
            for d in (0.05, 0.02, 0.01, 0.005, 0.002, 0.001):
                if p + shared + d >= 0.95:
                    continue
                for beta in (0.05, 0.01):
                    i += 1
                    rows.append(
                        CounterfactualReplayBenchmarkSpec(
                            benchmark_id=f"c{i:04d}",
                            p=p,
                            shared_patch=shared,
                            d=d,
                            beta=beta,
                            seed=40_000 + i,
                        )
                    )
    return rows


def write_counterfactual_replay_jsonl(
    rows: Iterable[CounterfactualReplayBenchmarkSpec],
    path: str | Path,
) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_counterfactual_replay_jsonl(
    path: str | Path,
) -> list[CounterfactualReplayBenchmarkSpec]:
    rows: list[CounterfactualReplayBenchmarkSpec] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(CounterfactualReplayBenchmarkSpec(**json.loads(line)))
    return rows
