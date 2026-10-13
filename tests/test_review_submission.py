import subprocess
import sys


def test_review_submission_static_gates():
    proc = subprocess.run(
        [sys.executable, "scripts/check_review_submission.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "review submission check passed" in proc.stdout
