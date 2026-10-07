from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


PUBLIC_METHODS = ("independent", "vertex-paired", "four-way", "suite", "tfoesuu")


@dataclass(frozen=True)
class PublicResultRow:
    """One frozen aggregate row for the public benchmark experiment."""

    dataset_id: str
    dataset_name: str
    method: str
    patch_size: float
    common_shift: float
    confidence_target: float
    trials: int
    graph_vertices: int
    graph_edges: int
    impacted_edges: int
    replay_rounds: float
    concrete_program_executions: float
    type_i_error: float
    type_ii_error: float
    seed: int
    dataset_sha256: str
    source_commit: str


def validate_public_result_row(row: PublicResultRow) -> None:
    if row.method not in PUBLIC_METHODS:
        raise ValueError(f"unsupported method: {row.method}")
    if not row.dataset_id or not row.dataset_name:
        raise ValueError("dataset identifiers must be non-empty")
    if not (0.0 < row.patch_size < 1.0):
        raise ValueError("patch_size must lie in (0,1)")
    if not (0.0 <= row.common_shift < 1.0):
        raise ValueError("common_shift must lie in [0,1)")
    if not (0.0 < row.confidence_target < 0.5):
        raise ValueError("confidence_target must lie in (0,0.5)")
    if row.trials <= 0:
        raise ValueError("trials must be positive")
    if row.graph_vertices <= 0 or row.graph_edges < 0:
        raise ValueError("invalid graph size")
    if not (0 < row.impacted_edges <= row.graph_edges):
        raise ValueError("impacted_edges must lie in [1, graph_edges]")
    if row.replay_rounds <= 0:
        raise ValueError("replay_rounds must be positive")
    if row.concrete_program_executions <= 0:
        raise ValueError("concrete_program_executions must be positive")
    for name, value in (
        ("type_i_error", row.type_i_error),
        ("type_ii_error", row.type_ii_error),
    ):
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"{name} must lie in [0,1]")
    if len(row.dataset_sha256) != 64:
        raise ValueError("dataset_sha256 must be a 64-character hex digest")
    int(row.dataset_sha256, 16)
    if len(row.source_commit) < 7:
        raise ValueError("source_commit must identify a git commit")


def write_public_results(
    rows: Iterable[PublicResultRow],
    path: str | Path,
) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            validate_public_result_row(row)
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")


def read_public_results(path: str | Path) -> list[PublicResultRow]:
    rows: list[PublicResultRow] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = PublicResultRow(**json.loads(line))
            validate_public_result_row(row)
            rows.append(row)
    return rows


def validate_public_result_matrix(rows: Iterable[PublicResultRow]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError("public result matrix is empty")
    keys = [
        (row.dataset_id, row.method, row.patch_size, row.seed)
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate dataset/method/patch-size/seed result rows")
    commit_set = {row.source_commit for row in rows}
    if len(commit_set) != 1:
        raise ValueError("all publication rows must come from one source commit")
    hashes_by_dataset: dict[str, set[str]] = {}
    for row in rows:
        hashes_by_dataset.setdefault(row.dataset_id, set()).add(
            row.dataset_sha256
        )
    bad = [name for name, hashes in hashes_by_dataset.items() if len(hashes) != 1]
    if bad:
        raise ValueError(f"dataset hashes changed within result matrix: {bad}")