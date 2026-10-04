from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SoftwareSubjectBenchmarkSpec:
    benchmark_id: str
    contexts: int
    affected_contexts: tuple[int, ...]
    delta: float
    beta: float
    baseline_low: float
    baseline_high: float
    seed: int


def software_subject_benchmark_v1() -> list[SoftwareSubjectBenchmarkSpec]:
    """Deterministic executable-software benchmark specifications."""

    rows: list[SoftwareSubjectBenchmarkSpec] = []
    i = 0
    for contexts in (16, 64, 256, 1024):
        single = (contexts // 3,)
        multi = tuple(sorted({contexts // 5, contexts // 2, (4 * contexts) // 5}))
        for affected in (single, multi):
            for delta in (0.05, 0.02, 0.01, 0.005):
                i += 1
                rows.append(
                    SoftwareSubjectBenchmarkSpec(
                        benchmark_id=f"s{i:04d}",
                        contexts=contexts,
                        affected_contexts=affected,
                        delta=delta,
                        beta=0.05,
                        baseline_low=0.25,
                        baseline_high=0.70,
                        seed=30_000 + i,
                    )
                )
    return rows


def write_software_subject_jsonl(
    rows: Iterable[SoftwareSubjectBenchmarkSpec],
    path: str | Path,
) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for row in rows:
            payload = asdict(row)
            payload["affected_contexts"] = list(row.affected_contexts)
            fh.write(json.dumps(payload, sort_keys=True) + "\n")


def read_software_subject_jsonl(
    path: str | Path,
) -> list[SoftwareSubjectBenchmarkSpec]:
    out: list[SoftwareSubjectBenchmarkSpec] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            payload = json.loads(line)
            payload["affected_contexts"] = tuple(payload["affected_contexts"])
            out.append(SoftwareSubjectBenchmarkSpec(**payload))
    return out
