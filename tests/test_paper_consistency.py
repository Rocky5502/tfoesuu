from pathlib import Path
import subprocess
import sys


def test_paper_static_checker_passes_on_repository():
    proc = subprocess.run(
        [sys.executable, "scripts/check_paper_consistency.py"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "paper static check passed" in proc.stdout
