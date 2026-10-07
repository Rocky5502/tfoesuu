from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ControlReplayStructuralCase:
    case_id: str
    high_count: int
    low_count: int
    groups: tuple[tuple[int, ...], ...]
    costs: tuple[float, ...]
    expected_control_feasible: bool
    expected_control_cover: float | None
    expected_small_d_regime: str


def control_replay_structural_cases_v1() -> list[ControlReplayStructuralCase]:
    """Exact P19 geometry fixtures; these are specifications, not results."""

    return [
        ControlReplayStructuralCase(
            case_id="p19-triangle-controls",
            high_count=3,
            low_count=2,
            groups=((0, 1), (1, 2), (0, 2)),
            costs=(1.0, 1.0, 1.0),
            expected_control_feasible=True,
            expected_control_cover=1.5,
            expected_small_d_regime="linear",
        ),
        ControlReplayStructuralCase(
            case_id="p19-boundary-only",
            high_count=3,
            low_count=2,
            groups=((0, 3), (1, 3), (2, 3)),
            costs=(1.0, 1.0, 1.0),
            expected_control_feasible=False,
            expected_control_cover=None,
            expected_small_d_regime="quadratic",
        ),
        ControlReplayStructuralCase(
            case_id="p19-all-high-control",
            high_count=4,
            low_count=1,
            groups=((0, 1, 2, 3),),
            costs=(1.0,),
            expected_control_feasible=True,
            expected_control_cover=1.0,
            expected_small_d_regime="linear",
        ),
        ControlReplayStructuralCase(
            case_id="p19-cycle-controls",
            high_count=4,
            low_count=2,
            groups=((0, 1), (1, 2), (2, 3), (0, 3)),
            costs=(1.0, 1.0, 1.0, 1.0),
            expected_control_feasible=True,
            expected_control_cover=2.0,
            expected_small_d_regime="linear",
        ),
        ControlReplayStructuralCase(
            case_id="p19-paired-controls",
            high_count=4,
            low_count=1,
            groups=((0, 1), (2, 3)),
            costs=(1.0, 1.0),
            expected_control_feasible=True,
            expected_control_cover=2.0,
            expected_small_d_regime="linear",
        ),
        ControlReplayStructuralCase(
            case_id="p19-weighted-triangle",
            high_count=3,
            low_count=1,
            groups=((0, 1), (1, 2), (0, 2)),
            costs=(1.0, 1.0, 2.0),
            expected_control_feasible=True,
            expected_control_cover=2.0,
            expected_small_d_regime="linear",
        ),
    ]


def write_control_replay_structural_jsonl(
    rows: Iterable[ControlReplayStructuralCase],
    path: str | Path,
) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            payload = asdict(row)
            fh.write(json.dumps(payload, sort_keys=True) + "\n")


def read_control_replay_structural_jsonl(
    path: str | Path,
) -> list[ControlReplayStructuralCase]:
    rows: list[ControlReplayStructuralCase] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            payload = json.loads(line)
            payload["groups"] = tuple(tuple(g) for g in payload["groups"])
            payload["costs"] = tuple(float(x) for x in payload["costs"])
            rows.append(ControlReplayStructuralCase(**payload))
    return rows
