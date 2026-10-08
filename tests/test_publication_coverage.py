"""Strict publication-release coverage tests (synthetic rows, not empirical data)."""

from dataclasses import replace

import pytest

from tfoesuu.public_results import (
    PUBLIC_METHODS,
    PublicResultRow,
    validate_publication_coverage,
)


SHA = "0123456789abcdef0123456789abcdef01234567"
DATASETS = ("public-adult", "public-bank")
PATCHES = (0.10, 0.05, 0.02, 0.01)


def _row(dataset: str, patch: float, method: str, seed: int = 17) -> PublicResultRow:
    return PublicResultRow(
        dataset_id=dataset,
        dataset_name=dataset,
        method=method,
        patch_size=patch,
        common_shift=0.05,
        confidence_target=0.05,
        trials=100_000,
        graph_vertices=100,
        graph_edges=50,
        affected_fraction=0.1,
        impacted_edges=5,
        replay_rounds=100.0,
        concrete_program_executions=400.0,
        type_i_error_count=100,
        type_ii_error_count=200,
        type_i_error=0.001,
        type_ii_error=0.002,
        seed=seed,
        dataset_sha256=("a" if dataset == "public-adult" else "b") * 64,
        source_commit=SHA,
    )


def _matrix():
    return [
        _row(dataset, patch, method)
        for dataset in DATASETS
        for patch in PATCHES
        for method in PUBLIC_METHODS
    ]


def test_complete_matched_publication_grid_is_accepted():
    validate_publication_coverage(_matrix(), DATASETS)


def test_same_number_of_method_rows_does_not_hide_missing_method():
    rows = _matrix()
    removed = next(row for row in rows if row.dataset_id == DATASETS[0]
                   and row.patch_size == PATCHES[0] and row.method == "tfoesuu")
    rows.remove(removed)
    # Old count-only validator could accept this: still five rows in the cell.
    rows.append(_row(DATASETS[0], PATCHES[0], "independent", seed=18))
    with pytest.raises(ValueError, match="incomplete method coverage"):
        validate_publication_coverage(rows, DATASETS)


def test_unmatched_seeds_are_rejected():
    rows = _matrix()
    rows[0] = replace(rows[0], seed=29)
    with pytest.raises(ValueError, match="unmatched publication seeds"):
        validate_publication_coverage(rows, DATASETS)


def test_missing_patch_cell_is_rejected():
    rows = [row for row in _matrix() if not (
        row.dataset_id == DATASETS[1] and row.patch_size == PATCHES[1])]
    with pytest.raises(ValueError, match="missing publication patch sizes"):
        validate_publication_coverage(rows, DATASETS)


def test_registry_mismatch_is_rejected():
    with pytest.raises(ValueError, match="publication dataset registry mismatch"):
        validate_publication_coverage(_matrix(), ("public-adult", "public-compas"))


def test_short_source_commit_is_rejected():
    rows = [replace(row, source_commit="0123456789abcdef") for row in _matrix()]
    with pytest.raises(ValueError, match="full 40-hex"):
        validate_publication_coverage(rows, DATASETS)


def test_insufficient_trials_are_rejected():
    rows = [
        replace(row, trials=1000, type_i_error_count=1, type_ii_error_count=2)
        for row in _matrix()
    ]
    with pytest.raises(ValueError, match="insufficient trials"):
        validate_publication_coverage(rows, DATASETS)


def test_method_specific_graph_drift_is_rejected():
    rows = _matrix()
    rows[0] = replace(rows[0], graph_edges=60)
    with pytest.raises(ValueError, match="graph metadata drift"):
        validate_publication_coverage(rows, DATASETS)



def test_multiple_seed_specific_rows_require_aggregation_before_release():
    rows = _matrix()
    # Every method has the same two-seed set, so this is matched but is not
    # one aggregate result per manuscript-table cell.
    for method in PUBLIC_METHODS:
        rows.append(_row(DATASETS[0], PATCHES[0], method, seed=18))
    with pytest.raises(ValueError, match="nonaggregated method rows"):
        validate_publication_coverage(rows, DATASETS)
