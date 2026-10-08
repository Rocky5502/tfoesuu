import subprocess
from pathlib import Path

import pytest

from tfoesuu.public_benchmarks import validate_preparation_source_compatibility

CONTRACT_PATHS = ("prepare.py", "registry.jsonl", "requirements.txt")


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo, text=True, stderr=subprocess.STDOUT
    ).strip()


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", ".")
    _git(
        repo,
        "-c",
        "user.name=TFOESUU Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        message,
    )
    return _git(repo, "rev-parse", "HEAD")


def test_preparation_compatibility_allows_unrelated_code_changes(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    for path in CONTRACT_PATHS:
        (repo / path).write_text(f"frozen {path}\n", encoding="utf-8")
    preparation_commit = _commit(repo, "prepare baseline")

    (repo / "unrelated.py").write_text("VALIDATOR = True\n", encoding="utf-8")
    execution_commit = _commit(repo, "add unrelated validator")

    report = validate_preparation_source_compatibility(
        preparation_commit,
        execution_commit,
        repo=repo,
        contract_paths=CONTRACT_PATHS,
    )
    assert report["preparation_source_commit"] == preparation_commit
    assert report["execution_source_commit"] == execution_commit
    assert report["compatible"] is True
    assert len(report["contract_sha256"]) == 64
    assert set(report["git_blobs"]) == set(CONTRACT_PATHS)


def test_preparation_compatibility_rejects_changed_contract_file(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    for path in CONTRACT_PATHS:
        (repo / path).write_text(f"frozen {path}\n", encoding="utf-8")
    preparation_commit = _commit(repo, "prepare baseline")

    (repo / "prepare.py").write_text("changed preparation semantics\n", encoding="utf-8")
    execution_commit = _commit(repo, "change preparation")

    with pytest.raises(ValueError, match="preparation contract mismatch.*prepare.py"):
        validate_preparation_source_compatibility(
            preparation_commit,
            execution_commit,
            repo=repo,
            contract_paths=CONTRACT_PATHS,
        )
