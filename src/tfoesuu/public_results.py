from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from numbers import Real
from pathlib import Path

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
    affected_fraction: float
    impacted_edges: int
    replay_rounds: float
    concrete_program_executions: float
    type_i_error_count: int
    type_ii_error_count: int
    type_i_error: float
    type_ii_error: float
    seed: int
    dataset_sha256: str
    source_commit: str
    preparation_source_commit: str | None = None
    preparation_contract_sha256: str | None = None


def _validate_finite_measure(name: str, value: object) -> None:
    """Reject nonnumeric, boolean, NaN and infinite experimental measurements."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")  # noqa: TRY004
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite real number")


def _validate_integer_measure(name: str, value: object) -> None:
    """Counts, seeds and graph sizes cannot be floating point measurements."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")  # noqa: TRY004


def validate_public_result_row(row: PublicResultRow) -> None:
    for name in (
        "patch_size",
        "common_shift",
        "confidence_target",
        "affected_fraction",
        "replay_rounds",
        "concrete_program_executions",
        "type_i_error",
        "type_ii_error",
    ):
        _validate_finite_measure(name, getattr(row, name))
    for name in (
        "trials",
        "graph_vertices",
        "graph_edges",
        "impacted_edges",
        "type_i_error_count",
        "type_ii_error_count",
        "seed",
    ):
        _validate_integer_measure(name, getattr(row, name))
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
    if not (0.0 < row.affected_fraction <= 1.0):
        raise ValueError("affected_fraction must lie in (0,1]")
    if not (0 < row.impacted_edges <= row.graph_edges):
        raise ValueError("impacted_edges must lie in [1, graph_edges]")
    if row.replay_rounds <= 0:
        raise ValueError("replay_rounds must be positive")
    if row.concrete_program_executions <= 0:
        raise ValueError("concrete_program_executions must be positive")
    for name, count in (
        ("type_i_error_count", row.type_i_error_count),
        ("type_ii_error_count", row.type_ii_error_count),
    ):
        if not (0 <= count <= row.trials):
            raise ValueError(f"{name} must lie in [0,trials]")
    for name, value in (
        ("type_i_error", row.type_i_error),
        ("type_ii_error", row.type_ii_error),
    ):
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"{name} must lie in [0,1]")
    if abs(row.type_i_error - row.type_i_error_count / row.trials) > 1e-12:
        raise ValueError("type_i_error does not match count/trials")
    if abs(row.type_ii_error - row.type_ii_error_count / row.trials) > 1e-12:
        raise ValueError("type_ii_error does not match count/trials")
    if len(row.dataset_sha256) != 64:
        raise ValueError("dataset_sha256 must be a 64-character hex digest")
    int(row.dataset_sha256, 16)
    if len(row.source_commit) < 7:
        raise ValueError("source_commit must identify a git commit")
    prep_present = row.preparation_source_commit is not None
    contract_present = row.preparation_contract_sha256 is not None
    if prep_present != contract_present:
        raise ValueError(
            "preparation_source_commit and preparation_contract_sha256 must be provided together"
        )
    if prep_present:
        if not re.fullmatch(r"[0-9a-f]{40}", row.preparation_source_commit or ""):
            raise ValueError("preparation_source_commit must be a full lowercase Git SHA")
        if not re.fullmatch(r"[0-9a-f]{64}", row.preparation_contract_sha256 or ""):
            raise ValueError("preparation_contract_sha256 must be a lowercase SHA-256")


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
        (
            row.dataset_id,
            row.method,
            row.patch_size,
            row.common_shift,
            row.confidence_target,
            row.affected_fraction,
            row.seed,
        )
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate dataset/method/patch-size/seed result rows")
    commit_set = {row.source_commit for row in rows}
    if len(commit_set) != 1:
        raise ValueError("all publication rows must come from one source commit")
    preparation_set = {
        (row.preparation_source_commit, row.preparation_contract_sha256)
        for row in rows
    }
    if len(preparation_set) != 1:
        raise ValueError("all publication rows must share preparation provenance")
    confidence_set = {row.confidence_target for row in rows}
    if len(confidence_set) != 1:
        raise ValueError("one publication matrix must use one confidence target")
    shift_set = {row.common_shift for row in rows}
    if len(shift_set) != 1:
        raise ValueError("one publication matrix must use one common shift")
    fraction_set = {row.affected_fraction for row in rows}
    if len(fraction_set) != 1:
        raise ValueError("one publication matrix must use one affected fraction")
    hashes_by_dataset: dict[str, set[str]] = {}
    for row in rows:
        hashes_by_dataset.setdefault(row.dataset_id, set()).add(
            row.dataset_sha256
        )
    bad = [name for name, hashes in hashes_by_dataset.items() if len(hashes) != 1]
    if bad:
        raise ValueError(f"dataset hashes changed within result matrix: {bad}")


def validate_publication_coverage(
    rows: Iterable[PublicResultRow],
    expected_dataset_ids: Iterable[str],
    *,
    minimum_patch_sizes: int = 4,
    minimum_trials: int = 100_000,
) -> None:
    """Fail closed unless a publication matrix covers a matched experiment grid.

    Unlike the permissive result-schema validator, this is a *release gate*.
    It rejects missing/extra registry datasets, incomplete method cells,
    inconsistent patch grids, mismatched seeds across methods, unverifiable
    source-commit tokens, and insufficient trial counts. It cannot establish
    that underlying trials were truly executed; immutable raw logs and run
    provenance must still be independently audited.
    """

    observed = list(rows)
    validate_public_result_matrix(observed)

    required = set(expected_dataset_ids)
    if not required or any(not name for name in required):
        raise ValueError("expected dataset IDs must be nonempty")
    seen = {row.dataset_id for row in observed}
    if seen != required:
        raise ValueError(
            f"publication dataset registry mismatch: missing={sorted(required-seen)} "
            f"extra={sorted(seen-required)}"
        )
    if minimum_patch_sizes < 1 or minimum_trials < 1:
        raise ValueError("minimum patch sizes and trials must be positive")
    grid = {row.patch_size for row in observed}
    if len(grid) < minimum_patch_sizes:
        raise ValueError(
            f"publication patch grid incomplete: {len(grid)} < {minimum_patch_sizes}"
        )

    groups: dict[tuple[str, float], dict[str, list[PublicResultRow]]] = {}
    for row in observed:
        if row.trials < minimum_trials:
            raise ValueError(
                f"insufficient trials for {row.dataset_id}/{row.method}: "
                f"{row.trials} < {minimum_trials}"
            )
        if not re.fullmatch(r"[0-9a-fA-F]{40}", row.source_commit):
            raise ValueError("publication source_commit must be a full 40-hex git SHA")
        if row.preparation_source_commit is None or row.preparation_contract_sha256 is None:
            raise ValueError("publication rows require preparation compatibility provenance")
        if not re.fullmatch(r"[0-9a-f]{40}", row.preparation_source_commit):
            raise ValueError("publication preparation_source_commit must be a full 40-hex Git SHA")
        if not re.fullmatch(r"[0-9a-f]{64}", row.preparation_contract_sha256):
            raise ValueError("publication preparation contract must be a SHA-256 digest")
        methods = groups.setdefault((row.dataset_id, row.patch_size), {})
        methods.setdefault(row.method, []).append(row)

    required_methods = set(PUBLIC_METHODS)
    for dataset_id in sorted(required):
        dataset_grid = {patch for (dataset, patch) in groups if dataset == dataset_id}
        if dataset_grid != grid:
            raise ValueError(
                f"missing publication patch sizes for {dataset_id}: "
                f"{sorted(grid-dataset_grid)}"
            )
        for patch in sorted(grid):
            cohort = groups[(dataset_id, patch)]
            if set(cohort) != required_methods:
                raise ValueError(
                    f"incomplete method coverage for {dataset_id}/d={patch}: "
                    f"missing={sorted(required_methods-set(cohort))}"
                )
            if any(len(values) != 1 for values in cohort.values()):
                raise ValueError(
                    f"nonaggregated method rows for {dataset_id}/d={patch}: "
                    "aggregate independent seeds before the publication release gate"
                )
            seed_sets = {name: {row.seed for row in values}
                         for name, values in cohort.items()}
            if len({frozenset(ids) for ids in seed_sets.values()}) != 1:
                raise ValueError(
                    f"unmatched publication seeds for {dataset_id}/d={patch}: "
                    f"{seed_sets}"
                )
            # Graph/counterfactual structure is a property of the frozen
            # dataset+patch, not a method-specific tuning parameter.
            cohort_rows = [row for values in cohort.values() for row in values]
            graph_meta = {
                (row.dataset_name, row.graph_vertices, row.graph_edges,
                 row.impacted_edges)
                for row in cohort_rows
            }
            if len(graph_meta) != 1:
                raise ValueError(
                    f"graph metadata drift across methods for {dataset_id}/d={patch}"
                )
