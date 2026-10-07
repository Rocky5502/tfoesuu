from pathlib import Path

from tfoesuu.replay_phase_benchmarks import (
    read_replay_phase_jsonl,
    replay_phase_cases_v1,
    write_replay_phase_jsonl,
)


def test_replay_phase_grid_is_unique_and_roundtrips(tmp_path: Path):
    rows = replay_phase_cases_v1()
    assert rows
    assert len({row.case_id for row in rows}) == len(rows)

    out = tmp_path / "phase.jsonl"
    write_replay_phase_jsonl(rows, out)
    assert read_replay_phase_jsonl(out) == rows


def test_phase_grid_does_not_overclaim_mixed_control_regime():
    rows = replay_phase_cases_v1()
    p19 = [row for row in rows if row.family == "p19-control-topology"]
    assert p19
    assert {row.control_coverage for row in p19} == {0.0, 1.0}
    assert all(row.expected_regime in {"linear", "quadratic"} for row in p19)


def test_p18_grid_separates_local_and_fixed_tolerance_questions():
    rows = replay_phase_cases_v1()
    local = [row for row in rows if row.family == "p18-threshold-local"]
    fixed = [row for row in rows if row.family == "p18-threshold-fixed"]

    assert local and fixed
    assert all(row.expected_regime == "local-linear-order" for row in local)
    assert all(row.expected_regime == "quadratic" for row in fixed)
    assert len({row.tau for row in fixed}) == 1
    assert len({row.tau_over_d for row in fixed}) == len(fixed)
