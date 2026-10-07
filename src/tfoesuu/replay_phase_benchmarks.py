from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ReplayPhaseCase:
    """Deterministic specification for a theorem-validation phase experiment."""

    case_id: str
    family: str
    d: float
    tau_over_d: float
    control_coverage: float
    replay_fidelity: float
    expected_regime: str
    theorem_scope: str

    @property
    def tau(self) -> float:
        return self.tau_over_d * self.d


def replay_phase_cases_v1() -> list[ReplayPhaseCase]:
    """Frozen phase-grid specifications; these rows are not empirical results."""

    rows: list[ReplayPhaseCase] = []
    ds = (0.04, 0.02, 0.01)
    ratios = (0.0, 0.25, 1.0, 4.0, 16.0)

    # P18 one-edge threshold family.  tau=O(d) retains the linear order while
    # fixed-positive tau is represented separately below.
    for d in ds:
        for ratio in ratios:
            rows.append(
                ReplayPhaseCase(
                    case_id=f"p18-local-d{d:g}-r{ratio:g}",
                    family="p18-threshold-local",
                    d=d,
                    tau_over_d=ratio,
                    control_coverage=0.0,
                    replay_fidelity=1.0,
                    expected_regime="local-linear-order",
                    theorem_scope="P18 tau=O(d)",
                )
            )

    # Fixed positive tolerance: as d shrinks, tau/d diverges and P18 predicts
    # the quadratic boundary regime.
    for d in ds:
        tau = 0.10
        rows.append(
            ReplayPhaseCase(
                case_id=f"p18-fixed-tau-d{d:g}",
                family="p18-threshold-fixed",
                d=d,
                tau_over_d=tau / d,
                control_coverage=0.0,
                replay_fidelity=1.0,
                expected_regime="quadratic",
                theorem_scope="P18 fixed tau>0",
            )
        )

    # P19 extremes only. Intermediate control coverage is intentionally not
    # assigned a theorem-predicted exponent until the mixed-control extension
    # is proved or refuted.
    for d in ds:
        rows.extend(
            [
                ReplayPhaseCase(
                    case_id=f"p19-boundary-d{d:g}",
                    family="p19-control-topology",
                    d=d,
                    tau_over_d=0.10 / d,
                    control_coverage=0.0,
                    replay_fidelity=1.0,
                    expected_regime="quadratic",
                    theorem_scope="P19 boundary-only",
                ),
                ReplayPhaseCase(
                    case_id=f"p19-covered-d{d:g}",
                    family="p19-control-topology",
                    d=d,
                    tau_over_d=0.10 / d,
                    control_coverage=1.0,
                    replay_fidelity=1.0,
                    expected_regime="linear",
                    theorem_scope="P19 complete matched-control coverage",
                ),
            ]
        )

    return rows


def write_replay_phase_jsonl(rows: Iterable[ReplayPhaseCase], path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_replay_phase_jsonl(path: str | Path) -> list[ReplayPhaseCase]:
    rows: list[ReplayPhaseCase] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(ReplayPhaseCase(**json.loads(line)))
    return rows
