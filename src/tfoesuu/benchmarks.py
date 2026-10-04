from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class BenchmarkSpec:
    benchmark_id: str
    graph_family: str
    n: int
    graph_parameter: float | int | None
    variance_profile: str
    correlation: float
    gamma: float
    beta: float
    seed: int


def benchmark_v1() -> list[BenchmarkSpec]:
    """Deterministic benchmark matrix for theorem stress-testing.

    This is not an observational dataset. It is a synthetic specification suite
    whose role is to falsify conjectures and check predicted scaling laws.
    """

    rows: list[BenchmarkSpec] = []
    i = 0
    for family in ("matching", "star", "path", "clique"):
        for n in (8, 16, 32, 64):
            if family == "matching" and n % 2:
                continue
            for profile in ("homogeneous", "degree_weighted", "lognormal"):
                for rho in (0.0, 0.5, 0.9, 0.99):
                    for gamma in (0.2, 0.5):
                        i += 1
                        rows.append(
                            BenchmarkSpec(
                                benchmark_id=f"b{i:04d}",
                                graph_family=family,
                                n=n,
                                graph_parameter=None,
                                variance_profile=profile,
                                correlation=rho,
                                gamma=gamma,
                                beta=0.05,
                                seed=10_000 + i,
                            )
                        )
    return rows


def write_jsonl(rows: Iterable[BenchmarkSpec], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_jsonl(path: str | Path) -> list[BenchmarkSpec]:
    out: list[BenchmarkSpec] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(BenchmarkSpec(**json.loads(line)))
    return out
