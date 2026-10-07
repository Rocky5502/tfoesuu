from __future__ import annotations

import argparse
import json
from pathlib import Path


FROZEN_ARTIFACTS = {
    "data/benchmark_v1.jsonl": 384,
    "data/replay_benchmark_v1.jsonl": 54,
    "data/software_subject_benchmark_v1.jsonl": 32,
    "data/counterfactual_replay_benchmark_v1.jsonl": 144,
    "data/threshold_replay_phase_v1.jsonl": 24,
    "data/partial_replay_benchmark_v1.jsonl": 168,
    "data/partial_replay_structural_cases_v1.jsonl": 8,
    "data/partial_replay_scope_cases_v1.jsonl": 1,
}


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def scope_false_positive_measure(
    row: dict,
) -> tuple[float, list[tuple[float, float]]]:
    cuts = sorted({
        0.0,
        float(row["old_threshold_0"]),
        float(row["old_threshold_1"]),
        float(row["new_threshold_0"]),
        float(row["new_threshold_1"]),
        1.0,
    })
    rejecting: list[tuple[float, float]] = []
    total = 0.0
    for left, right in zip(cuts, cuts[1:]):
        if right <= left:
            continue
        u = (left + right) / 2.0
        old = [
            int(u <= float(row["old_threshold_0"])),
            int(u <= float(row["old_threshold_1"])),
        ]
        new = [
            int(u <= float(row["new_threshold_0"])),
            int(u <= float(row["new_threshold_1"])),
        ]
        deltas = [new_i - old_i for old_i, new_i in zip(old, new)]
        if len(set(deltas)) > 1:
            rejecting.append((left, right))
            total += right - left
    return total, rejecting


def summarize(root: Path) -> dict:
    artifact_rows = {}
    for rel, expected in FROZEN_ARTIFACTS.items():
        rows = read_jsonl(root / rel)
        artifact_rows[rel] = len(rows)
        if len(rows) != expected:
            raise ValueError(
                f"{rel}: expected {expected} rows, found {len(rows)}"
            )

    scope_rows = read_jsonl(root / "data/partial_replay_scope_cases_v1.jsonl")
    if len(scope_rows) != 1:
        raise ValueError("scope manifest must contain exactly one v1 row")
    scope = scope_rows[0]
    measure, intervals = scope_false_positive_measure(scope)
    expected_measure = float(scope["expected_false_positive_measure"])
    if abs(measure - expected_measure) > 1e-12:
        raise ValueError(
            "scope false-positive measure disagrees with manifest"
        )

    return {
        "artifact_rows": artifact_rows,
        "total_frozen_specification_rows": sum(artifact_rows.values()),
        "p17_scope": {
            "case_id": scope["case_id"],
            "fairness_gap": abs(
                float(scope["new_threshold_0"])
                - float(scope["new_threshold_1"])
            ),
            "fairness_tau": float(scope["fairness_tau"]),
            "rejecting_intervals": [
                [left, right] for left, right in intervals
            ],
            "exact_uniform_tape_measure": measure,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize frozen STOC evidence artifacts."
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    summary = summarize(args.root)
    payload = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
