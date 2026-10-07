from pathlib import Path

import pytest

from scripts.summarize_submission_evidence import summarize


def test_submission_evidence_summary_matches_frozen_repository():
    summary = summarize(Path("."))

    assert summary["total_frozen_specification_rows"] == 821

    scope = summary["p17_scope"]
    assert scope["fairness_gap"] == pytest.approx(0.15)
    assert scope["fairness_tau"] == pytest.approx(0.20)
    assert len(scope["rejecting_intervals"]) == 2
    for actual, expected in zip(
        scope["rejecting_intervals"], [[0.20, 0.30], [0.40, 0.45]]
    ):
        assert actual[0] == pytest.approx(expected[0])
        assert actual[1] == pytest.approx(expected[1])
    assert scope["exact_uniform_tape_measure"] == pytest.approx(0.15)
