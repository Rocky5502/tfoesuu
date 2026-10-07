from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ThresholdReplayPhaseSpec:
    """Deterministic P18 phase-transition stress specification."""

    benchmark_id: str
    p: float
    shared_patch: float
    fairness_tau: float
    d: float
    beta: float
    seed: int


def threshold_replay_phase_benchmark_v1() -> list[ThresholdReplayPhaseSpec]:
    """Frozen grid spanning sparse, matched-scale, and positive-tolerance regimes.

    These rows are theorem-falsification specifications, not empirical results.
    The common baseline and patch shift are fixed so that the grid isolates the
    interaction between the fairness tolerance tau and separated margin d.
    """

    rows: list[ThresholdReplayPhaseSpec] = []
    i = 0
    p = 0.20
    shared_patch = 0.10
    beta = 0.05
    for fairness_tau in (0.0, 0.005, 0.01, 0.05, 0.10, 0.20):
        for d in (0.05, 0.02, 0.01, 0.005):
            if p + shared_patch + fairness_tau + d >= 1.0:
                continue
            i += 1
            rows.append(
                ThresholdReplayPhaseSpec(
                    benchmark_id=f"p18-{i:04d}",
                    p=p,
                    shared_patch=shared_patch,
                    fairness_tau=fairness_tau,
                    d=d,
                    beta=beta,
                    seed=60_000 + i,
                )
            )
    return rows


def write_threshold_replay_phase_jsonl(
    rows: Iterable[ThresholdReplayPhaseSpec],
    path: str | Path,
) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_threshold_replay_phase_jsonl(
    path: str | Path,
) -> list[ThresholdReplayPhaseSpec]:
    rows: list[ThresholdReplayPhaseSpec] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(ThresholdReplayPhaseSpec(**json.loads(line)))
    return rows
