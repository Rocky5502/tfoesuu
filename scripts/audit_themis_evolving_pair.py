from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from tfoesuu.external_subject_gate import (
    ThemisGateEvidence,
    evaluate_themis_gate,
    semantic_python_hash,
)

EXPECTED_COMMIT = "a70f12a6a8f34cdd8b170b4dc59a78674c9e8950"
EXPECTED_LICENSE_SHA256 = "30572d228ee9914fa381ea0997325627300e6cd976e738c327115af32a957ab8"
LOAN_PATHS = (
    "Themis2.0/loan.py",
    "Themis2.0/loan_2.py",
    "Themis2.0/loan_3.py",
)
WRAPPER_PATH = "ESEC.FSE.2017.Experimental.Replication/Figure2/G/Gtest.py"
LOCK_NAMES = {
    "environment.yml",
    "environment.yaml",
    "pipfile.lock",
    "poetry.lock",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "uv.lock",
}


def _git(checkout: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=checkout,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    return completed.stdout.strip()


def _git_bytes(checkout: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=checkout,
        check=True,
        capture_output=True,
    )
    return completed.stdout


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _history(checkout: Path, path: str) -> list[dict[str, str]]:
    commits = _git(checkout, "log", "--all", "--format=%H", "--", path).splitlines()
    revisions: list[dict[str, str]] = []
    for commit in commits:
        source_bytes = _git_bytes(checkout, "show", f"{commit}:{path}")
        source = source_bytes.decode("utf-8", errors="strict")
        revision = {
            "commit": commit,
            "git_blob": _git(checkout, "rev-parse", f"{commit}:{path}"),
            "source_sha256": _sha256(source_bytes),
        }
        try:
            revision["semantic_python_sha256"] = semantic_python_hash(source)
        except SyntaxError:
            revision["semantic_python_sha256"] = "unavailable-python-runtime-mismatch"
        revisions.append(revision)
    return revisions


def _introduction_commit(checkout: Path, path: str) -> str:
    return _git(
        checkout,
        "log",
        "--all",
        "--diff-filter=A",
        "--format=%H",
        "-1",
        "--",
        path,
    )


def audit(checkout: Path) -> dict[str, object]:
    checkout = checkout.resolve()
    if not (checkout / ".git").exists():
        raise ValueError(f"not a Git checkout: {checkout}")

    commit = _git(checkout, "rev-parse", "HEAD")
    status = _git(checkout, "status", "--porcelain", "--untracked-files=normal")
    license_path = checkout / "LICENSE.md"
    license_sha256 = _sha256(license_path.read_bytes()) if license_path.is_file() else None
    locks = sorted(
        str(path.relative_to(checkout)).replace("\\", "/")
        for path in checkout.rglob("*")
        if ".git" not in path.parts
        and path.is_file()
        and (
            path.name.lower() in LOCK_NAMES
            or path.name.lower().startswith("requirements-")
        )
    )

    loan_histories = {path: _history(checkout, path) for path in LOAN_PATHS}
    current_sources = {path: (checkout / path).read_text(encoding="utf-8") for path in LOAN_PATHS}
    try:
        for source in current_sources.values():
            semantic_python_hash(source)
        current_scripts_parse = True
    except SyntaxError:
        current_scripts_parse = False

    loan_semantic_hashes = {
        revision["semantic_python_sha256"] for revision in loan_histories[LOAN_PATHS[0]]
    }
    introductions = {path: _introduction_commit(checkout, path) for path in LOAN_PATHS[1:]}
    variants_introduced_together = len(set(introductions.values())) == 1
    wrapper_history = _history(checkout, WRAPPER_PATH)
    checkout_source_sha256 = {
        path: _sha256((checkout / path).read_bytes())
        for path in (*LOAN_PATHS, WRAPPER_PATH)
    }

    evidence = ThemisGateEvidence(
        commit_matches=commit == EXPECTED_COMMIT,
        checkout_clean=not status,
        license_matches=license_sha256 == EXPECTED_LICENSE_SHA256,
        dependency_locks=tuple(locks),
        current_scripts_parse=current_scripts_parse,
        same_path_semantic_revisions=len(loan_semantic_hashes),
        same_schema_pair_verified=False,
        variants_introduced_together=variants_introduced_together,
        random_tape_exposed=False,
    )
    decision = evaluate_themis_gate(evidence)
    return {
        "schema_version": 1,
        "history_source_hash_basis": "exact Git object content bytes",
        "checkout": str(checkout),
        "commit": commit,
        "commit_matches": evidence.commit_matches,
        "checkout_clean": evidence.checkout_clean,
        "license_sha256": license_sha256,
        "license_matches": evidence.license_matches,
        "dependency_locks": locks,
        "loan_histories": loan_histories,
        "loan_semantic_revision_count": evidence.same_path_semantic_revisions,
        "loan_variant_introduction_commits": introductions,
        "loan_variants_introduced_together": variants_introduced_together,
        "wrapper_history": wrapper_history,
        "checkout_source_sha256": checkout_source_sha256,
        "wrapper_semantic_revision_count": len(
            {revision["semantic_python_sha256"] for revision in wrapper_history}
        ),
        "decision": {
            "deterministic_baseline_ready": decision.deterministic_baseline_ready,
            "evolving_pair_ready": decision.evolving_pair_ready,
            "replay_theorem_ready": decision.replay_theorem_ready,
            "reasons": list(decision.reasons),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument(
        "--require",
        choices=("audit", "baseline", "evolving", "replay"),
        default="audit",
    )
    args = parser.parse_args()
    report = audit(args.checkout)
    print(json.dumps(report, indent=2, sort_keys=True))

    decision = report["decision"]
    assert isinstance(decision, dict)
    required = {
        "audit": True,
        "baseline": decision["deterministic_baseline_ready"],
        "evolving": decision["evolving_pair_ready"],
        "replay": decision["replay_theorem_ready"],
    }
    return 0 if required[args.require] else 2


if __name__ == "__main__":
    raise SystemExit(main())
