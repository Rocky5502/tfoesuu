"""Fail-closed validation for resumable JSONL experiment shards."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def load_compatible_shard(
    path: str | Path,
    specs: Iterable[Any],
    *,
    trials: int,
    device: str,
) -> dict[str, dict[str, Any]]:
    """Load a shard only if every row matches its full frozen run identity."""

    expected: dict[str, dict[str, Any]] = {}
    for spec in specs:
        if not is_dataclass(spec):
            raise TypeError("sweep specifications must be dataclass instances")
        fields = asdict(spec)
        benchmark_id = fields.get("benchmark_id")
        if not isinstance(benchmark_id, str) or benchmark_id in expected:
            raise ValueError("specification benchmark IDs must be unique strings")
        expected[benchmark_id] = fields

    shard = Path(path)
    if not shard.exists():
        return {}

    loaded: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(shard.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        benchmark_id = row.get("benchmark_id")
        if benchmark_id not in expected:
            raise ValueError(f"unexpected benchmark ID in {shard.name}:{line_number}")
        if benchmark_id in loaded:
            raise ValueError(f"duplicate benchmark ID in {shard.name}: {benchmark_id}")
        if row.get("trials") != trials or row.get("device") != device:
            raise ValueError(f"incompatible run identity in {shard.name}: {benchmark_id}")
        for field, value in expected[benchmark_id].items():
            if row.get(field) != value:
                raise ValueError(
                    f"specification mismatch in {shard.name}: {benchmark_id}.{field}"
                )
        loaded[benchmark_id] = row
    return loaded
