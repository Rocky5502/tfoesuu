from pathlib import Path

import pytest

from tfoesuu.public_results import (
    PublicResultRow,
    read_public_results,
    validate_public_result_matrix,
    validate_public_result_row,
    write_public_results,
)


def _row(method: str, *, executions: float, seed: int = 0) -> PublicResultRow:
    return PublicResultRow(
        dataset_id="public-adult",
        dataset_name="Adult Census Income",
        method=method,
        patch_size=0.05,
        common_shift=0.05,
        confidence_target=0.05,
        trials=1000,
        graph_vertices=100,
        graph_edges=50,
        affected_fraction=0.10,
        impacted_edges=5,
        replay_rounds=20.0,
        concrete_program_executions=executions,
        type_i_error_count=10,
        type_ii_error_count=20,
        type_i_error=0.01,
        type_ii_error=0.02,
        seed=seed,
        dataset_sha256="a" * 64,
        source_commit="0123456789abcdef",
    )


def test_public_result_roundtrip_and_matrix(tmp_path: Path):
    rows = [_row("independent", executions=1000.0), _row("tfoesuu", executions=100.0)]
    for row in rows:
        validate_public_result_row(row)
    validate_public_result_matrix(rows)

    out = tmp_path / "results.jsonl"
    write_public_results(rows, out)
    assert read_public_results(out) == rows


def test_public_result_matrix_rejects_mixed_commits():
    a = _row("independent", executions=1000.0)
    b = _row("tfoesuu", executions=100.0)
    b = PublicResultRow(**{**b.__dict__, "source_commit": "fedcba9876543210"})
    with pytest.raises(ValueError, match="one source commit"):
        validate_public_result_matrix([a, b])


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("concrete_program_executions", float("nan")),
        ("concrete_program_executions", float("inf")),
        ("replay_rounds", float("nan")),
        ("replay_rounds", float("-inf")),
        ("patch_size", float("nan")),
        ("type_i_error", float("inf")),
        ("common_shift", "0.05"),
        ("confidence_target", True),
    ],
)
def test_nonfinite_public_result_metrics_are_rejected(field, bad_value):
    row = _row("tfoesuu", executions=100.0)
    altered = PublicResultRow(**{**row.__dict__, field: bad_value})
    with pytest.raises(ValueError, match="finite real number"):
        validate_public_result_row(altered)


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("trials", 1000.5),
        ("trials", True),
        ("graph_vertices", 100.0),
        ("graph_edges", 50.5),
        ("type_i_error_count", 10.5),
        ("type_ii_error_count", 20.0),
        ("seed", 3.14),
    ],
)
def test_fractional_or_boolean_public_result_counts_are_rejected(field, bad_value):
    row = _row("tfoesuu", executions=100.0)
    altered = PublicResultRow(**{**row.__dict__, field: bad_value})
    with pytest.raises(ValueError, match="must be an integer"):
        validate_public_result_row(altered)
