from pathlib import Path
import math

from tfoesuu.separations import threshold_fairness_replay_bounds
from tfoesuu.threshold_replay_benchmarks import (
    read_threshold_replay_phase_jsonl,
    threshold_replay_phase_benchmark_v1,
    write_threshold_replay_phase_jsonl,
)


def test_threshold_replay_phase_grid_roundtrip(tmp_path: Path):
    rows = threshold_replay_phase_benchmark_v1()

    assert len(rows) == 24
    assert len({row.benchmark_id for row in rows}) == 24
    assert {row.fairness_tau for row in rows} == {
        0.0, 0.005, 0.01, 0.05, 0.10, 0.20
    }
    assert {row.d for row in rows} == {0.05, 0.02, 0.01, 0.005}

    out = tmp_path / "threshold_replay_phase.jsonl"
    write_threshold_replay_phase_jsonl(rows, out)
    assert read_threshold_replay_phase_jsonl(out) == rows

    committed = read_threshold_replay_phase_jsonl(
        "data/threshold_replay_phase_v1.jsonl"
    )
    assert committed == rows


def test_every_threshold_replay_phase_row_executes_theorem_bounds():
    for row in threshold_replay_phase_benchmark_v1():
        bounds = threshold_fairness_replay_bounds(
            row.p,
            row.shared_patch,
            row.fairness_tau,
            row.d,
            row.beta,
        )
        assert bounds.per_round_kl > 0.0
        assert bounds.null_expected_rounds_lower > 0.0
        assert bounds.replay_upper_rounds > 0
        assert (
            bounds.replay_upper_concrete_executions
            == 4 * bounds.replay_upper_rounds
        )


def test_zero_tolerance_rows_have_linear_upper_schedule():
    for row in threshold_replay_phase_benchmark_v1():
        if row.fairness_tau != 0.0:
            continue
        bounds = threshold_fairness_replay_bounds(
            row.p,
            row.shared_patch,
            row.fairness_tau,
            row.d,
            row.beta,
        )
        target = 8.0 * math.log(1.0 / row.beta) / row.d
        assert bounds.replay_upper_rounds <= target + 1.0
