#!/usr/bin/env python3
"""Validate the theorem-facing replay phase-transition benchmark contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.replay_phase_benchmarks import (
    read_replay_phase_jsonl,
    replay_phase_cases_v1,
)


def validate(rows):
    if not rows:
        raise ValueError("phase benchmark must contain at least one row")

    case_ids = [row.case_id for row in rows]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("case_id values must be unique")

    for row in rows:
        if not (row.d > 0.0):
            raise ValueError(f"{row.case_id}: d must be positive")
        if row.tau_over_d < 0.0:
            raise ValueError(f"{row.case_id}: tau_over_d must be nonnegative")
        if not (0.0 <= row.control_coverage <= 1.0):
            raise ValueError(f"{row.case_id}: control_coverage must lie in [0,1]")
        if row.replay_fidelity != 1.0:
            raise ValueError(
                f"{row.case_id}: v1 freezes replay_fidelity=1.0; "
                "partial replay fidelity has no promoted theorem"
            )

    local = [r for r in rows if r.family == "p18-threshold-local"]
    fixed = [r for r in rows if r.family == "p18-threshold-fixed"]
    p19 = [r for r in rows if r.family == "p19-control-topology"]

    if not local or not fixed or not p19:
        raise ValueError("phase grid must include P18 local/fixed and P19 topology families")

    if any(r.expected_regime != "local-linear-order" for r in local):
        raise ValueError("P18 local rows must remain labeled local-linear-order")
    if any(r.expected_regime != "quadratic" for r in fixed):
        raise ValueError("P18 fixed-tolerance rows must remain quadratic")

    fixed_taus = {round(r.tau, 12) for r in fixed}
    if len(fixed_taus) != 1:
        raise ValueError("P18 fixed-tolerance family must hold tau fixed while d shrinks")

    coverages = {r.control_coverage for r in p19}
    if coverages != {0.0, 1.0}:
        raise ValueError(
            "P19 v1 may contain only topology-complete control-coverage extremes 0 and 1; "
            "mixed coefficients require an explicit replay topology"
        )
    for r in p19:
        expected = "linear" if r.control_coverage == 1.0 else "quadratic"
        if r.expected_regime != expected:
            raise ValueError(f"{r.case_id}: inconsistent P19 regime label")

    return {
        "rows": len(rows),
        "families": sorted({r.family for r in rows}),
        "p19_control_coverages": sorted(coverages),
        "replay_fidelity": 1.0,
        "status": "valid",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--benchmark",
        type=Path,
        help="optional JSONL to validate; omitted validates the in-code frozen v1 grid",
    )
    args = ap.parse_args()

    rows = (
        read_replay_phase_jsonl(args.benchmark)
        if args.benchmark
        else replay_phase_cases_v1()
    )
    print(json.dumps(validate(rows), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
