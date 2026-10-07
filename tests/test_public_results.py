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
        impacted_edges=5,
        replay_rounds=20.0,
        concrete_program_executions=executions,
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