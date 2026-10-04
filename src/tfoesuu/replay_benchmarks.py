from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ReplayBenchmarkSpec:
    benchmark_id: str
    p: float
    d: float
    beta: float
    seed: int


def replay_benchmark_v1() -> list[ReplayBenchmarkSpec]:
    """Deterministic grid for the Bernoulli replay-separation theorem.

    The grid spans interior baselines, patch sizes over two orders of magnitude,
    and multiple fixed-confidence targets.  It is a theorem-stress specification,
    not an observational dataset.
    """

    rows: list[ReplayBenchmarkSpec] = []
    i = 0
    for p in (0.25, 0.50, 0.75):
        for d in (0.10, 0.05, 0.02, 0.01, 0.005, 0.002):
            if p + d >= 1.0:
                continue
            for beta in (0.10, 0.05, 0.01):
                i += 1
                rows.append(
                    ReplayBenchmarkSpec(
                        benchmark_id=f"r{i:04d}",
                        p=p,
                        d=d,
                        beta=beta,
                        seed=20_000 + i,
                    )
                )
    return rows


def write_replay_jsonl(rows: Iterable[ReplayBenchmarkSpec], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_replay_jsonl(path: str | Path) -> list[ReplayBenchmarkSpec]:
    out: list[ReplayBenchmarkSpec] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(ReplayBenchmarkSpec(**json.loads(line)))
    return out
