from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from tfoesuu.external_subject_gate import (
    ExternalEvolutionEvidence,
    evaluate_external_evolution_gate,
)

OLD_COMMIT = "e8cc63784de5410805c156715175fc60e2cd5653"
NEW_COMMIT = "0cf59eccfdd364417787fe2c368a1c77c3f378b8"
EXPECTED_BLOBS = {
    "LICENSE": ("abef27e17206c6dbe20de33fb24f7c7ce3ae490d",) * 2,
    "requirements.txt": ("e28efe081a00d8b1b978c499add874045c8ef84a",) * 2,
    "fairlearn/postprocessing/_threshold_optimizer.py": (
        "67d443feb59d036cf5aeb2a47485cec6f2b7d42f",
    )
    * 2,
    "fairlearn/postprocessing/_interpolated_thresholder.py": (
        "1eaa15f9b496038fa4b85bb58d8594cbd511c6f0",
    )
    * 2,
    "fairlearn/_input_validation.py": (
        "03d5fe963f00ca644701691f15814c7c499f8a6f",
        "962b348e9850ad3bc0b9dd9bd95535dfa6267c08",
    ),
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


def audit(old_checkout: Path, new_checkout: Path) -> dict[str, object]:
    old_checkout = old_checkout.resolve()
    new_checkout = new_checkout.resolve()
    old_commit = _git(old_checkout, "rev-parse", "HEAD")
    new_commit = _git(new_checkout, "rev-parse", "HEAD")
    old_clean = not _git(old_checkout, "status", "--porcelain")
    new_clean = not _git(new_checkout, "status", "--porcelain")
    new_parent = _git(new_checkout, "rev-parse", f"{new_commit}^")

    blobs: dict[str, dict[str, str]] = {}
    for path in EXPECTED_BLOBS:
        blobs[path] = {
            "old": _git(old_checkout, "rev-parse", f"{old_commit}:{path}"),
            "new": _git(new_checkout, "rev-parse", f"{new_commit}:{path}"),
        }

    def blobs_match(path: str) -> bool:
        expected_old, expected_new = EXPECTED_BLOBS[path]
        return blobs[path] == {"old": expected_old, "new": expected_new}

    license_unchanged = blobs_match("LICENSE") and (
        blobs["LICENSE"]["old"] == blobs["LICENSE"]["new"]
    )
    requirements_unchanged = blobs_match("requirements.txt") and (
        blobs["requirements.txt"]["old"] == blobs["requirements.txt"]["new"]
    )
    schema_unchanged = blobs_match(
        "fairlearn/postprocessing/_threshold_optimizer.py"
    )
    rng_unchanged = blobs_match(
        "fairlearn/postprocessing/_interpolated_thresholder.py"
    )
    target_changed = blobs_match("fairlearn/_input_validation.py") and (
        blobs["fairlearn/_input_validation.py"]["old"]
        != blobs["fairlearn/_input_validation.py"]["new"]
    )
    commit_subject = _git(new_checkout, "show", "-s", "--format=%s", new_commit)
    documented = commit_subject == (
        "Fix _merge_columns when using multiple sensitive features with long names (#763)"
    )

    evidence = ExternalEvolutionEvidence(
        old_commit_matches=old_commit == OLD_COMMIT,
        new_commit_matches=new_commit == NEW_COMMIT,
        both_checkouts_clean=old_clean and new_clean,
        new_is_direct_child=new_parent == old_commit,
        license_unchanged=license_unchanged,
        dependency_manifest_unchanged=requirements_unchanged,
        public_schema_unchanged=schema_unchanged,
        random_draw_path_unchanged=rng_unchanged,
        target_semantics_changed=target_changed,
        upstream_bugfix_documented=documented,
        environment_locked=False,
        runtime_preflight_passed=False,
        shared_tape_verified=False,
    )
    decision = evaluate_external_evolution_gate(evidence)
    return {
        "schema_version": 1,
        "old_checkout": str(old_checkout),
        "new_checkout": str(new_checkout),
        "old_commit": old_commit,
        "new_commit": new_commit,
        "new_parent": new_parent,
        "old_clean": old_clean,
        "new_clean": new_clean,
        "commit_subject": commit_subject,
        "blobs": blobs,
        "decision": {
            "source_pair_ready": decision.source_pair_ready,
            "execution_ready": decision.execution_ready,
            "replay_ready": decision.replay_ready,
            "reasons": list(decision.reasons),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("old_checkout", type=Path)
    parser.add_argument("new_checkout", type=Path)
    parser.add_argument("--require", choices=("audit", "source"), default="audit")
    args = parser.parse_args()
    report = audit(args.old_checkout, args.new_checkout)
    print(json.dumps(report, indent=2, sort_keys=True))
    decision = report["decision"]
    assert isinstance(decision, dict)
    required = {"audit": True, "source": decision["source_pair_ready"]}
    return 0 if required[args.require] else 2


if __name__ == "__main__":
    raise SystemExit(main())
