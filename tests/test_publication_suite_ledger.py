"""Publication suite ledger failure-path tests (no external data or GPU needed)."""

import json
import sys

import pytest

from scripts.run_publication_suite import run_jobs


def test_publication_job_failure_preserves_partial_command_ledger(tmp_path):
    jobs = [
        ("ok", [sys.executable, "-c", "print('verified step')"]),
        (
            "broken",
            [sys.executable, "-c", "import sys; print('deliberate failure'); sys.exit(7)"],
        ),
        ("not_started", [sys.executable, "-c", "print('must not execute')"]),
    ]
    with pytest.raises(RuntimeError, match="broken failed with exit code 7"):
        run_jobs(jobs, tmp_path)

    records = json.loads((tmp_path / "commands.json").read_text(encoding="utf-8"))
    assert [item["name"] for item in records] == ["ok", "broken"]
    assert [item["status"] for item in records] == ["passed", "failed"]
    assert [item["returncode"] for item in records] == [0, 7]
    assert (tmp_path / "ok.log").read_text(encoding="utf-8").strip() == "verified step"
    assert "deliberate failure" in (tmp_path / "broken.log").read_text(
        encoding="utf-8"
    )
    assert not (tmp_path / "not_started.log").exists()


def test_successful_publication_jobs_leave_complete_command_ledger(tmp_path):
    jobs = [
        ("first", [sys.executable, "-c", "print('first')"]),
        ("second", [sys.executable, "-c", "print('second')"]),
    ]
    completed = run_jobs(jobs, tmp_path)
    records = json.loads((tmp_path / "commands.json").read_text(encoding="utf-8"))
    assert records == completed
    assert len(records) == 2
    assert all(item["status"] == "passed" for item in records)
