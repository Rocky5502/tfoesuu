#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

EXPECTED = {
    "data/benchmark_v1.jsonl": {"min_rows": 384, "id_key": "benchmark_id", "role": "Gaussian allocation stress"},
    "data/replay_benchmark_v1.jsonl": {"min_rows": 54, "id_key": "benchmark_id", "role": "paired replay separation"},
    "data/software_subject_benchmark_v1.jsonl": {"min_rows": 32, "id_key": "benchmark_id", "role": "executable stochastic software subject"},
    "data/counterfactual_replay_benchmark_v1.jsonl": {"min_rows": 144, "id_key": "benchmark_id", "role": "four-way replay stress"},
    "data/partial_replay_benchmark_v1.jsonl": {"min_rows": 168, "id_key": "benchmark_id", "role": "partial-replay parameter stress"},
    "data/partial_replay_structural_cases_v1.jsonl": {"min_rows": 8, "id_key": "case_id", "role": "exact structural theorem fixtures"},
    "data/partial_replay_scope_cases_v1.jsonl": {"min_rows": 1, "id_key": "case_id", "role": "scope/counterexample guard"},
}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise SystemExit(f"{path}:{lineno}: expected JSON object")
            rows.append(row)
    return rows


def main() -> None:
    total = 0
    global_ids: set[tuple[str, str]] = set()
    for name, spec in EXPECTED.items():
        path = Path(name)
        if not path.exists():
            raise SystemExit(f"missing frozen benchmark artifact: {name}")
        rows = read_jsonl(path)
        if len(rows) < int(spec["min_rows"]):
            raise SystemExit(
                f"{name}: expected at least {spec['min_rows']} rows, found {len(rows)}"
            )
        key = str(spec["id_key"])
        ids = []
        for i, row in enumerate(rows, start=1):
            if key not in row or not isinstance(row[key], str) or not row[key].strip():
                raise SystemExit(f"{name}: row {i} missing non-empty {key}")
            ids.append(row[key])
        if len(ids) != len(set(ids)):
            raise SystemExit(f"{name}: duplicate {key} values")
        for item in ids:
            token = (name, item)
            if token in global_ids:
                raise SystemExit(f"{name}: duplicate inventory token {item}")
            global_ids.add(token)
        total += len(rows)
        print(f"ok {name}: {len(rows)} rows - {spec['role']}")
    print(f"benchmark inventory ok: {len(EXPECTED)} frozen artifacts, {total} rows")


if __name__ == "__main__":
    main()
