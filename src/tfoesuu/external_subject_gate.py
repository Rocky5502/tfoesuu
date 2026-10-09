from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass


def semantic_python_hash(source: str) -> str:
    """Hash Python syntax while ignoring comments and formatting.

    This is a source-screening aid, not a proof of behavioral equivalence.
    Parse failures are intentionally propagated so callers fail closed.
    """

    tree = ast.parse(source)
    canonical = ast.dump(tree, annotate_fields=True, include_attributes=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ThemisGateEvidence:
    """Auditable facts used by the external-subject admission gate."""

    commit_matches: bool
    checkout_clean: bool
    license_matches: bool
    dependency_locks: tuple[str, ...]
    current_scripts_parse: bool
    same_path_semantic_revisions: int
    same_schema_pair_verified: bool
    variants_introduced_together: bool
    random_tape_exposed: bool


@dataclass(frozen=True)
class ThemisGateDecision:
    """Three-level admission decision for Themis-derived subjects."""

    deterministic_baseline_ready: bool
    evolving_pair_ready: bool
    replay_theorem_ready: bool
    reasons: tuple[str, ...]


def evaluate_themis_gate(evidence: ThemisGateEvidence) -> ThemisGateDecision:
    """Fail closed unless provenance, evolution, and replay gates are explicit.

    ``deterministic_baseline_ready`` means source-eligible for further
    environment work, not authorized to execute or admit results.  Evolution
    additionally requires a dependency lock, two semantic revisions of one
    executable path, and an independently verified stable input schema.
    Replay-theorem readiness further requires an actual subject random tape.
    """

    if evidence.same_path_semantic_revisions < 0:
        raise ValueError("same_path_semantic_revisions must be nonnegative")

    reasons: list[str] = []
    if not evidence.commit_matches:
        reasons.append("pinned commit mismatch")
    if not evidence.checkout_clean:
        reasons.append("checkout is dirty")
    if not evidence.license_matches:
        reasons.append("license hash mismatch")
    if not evidence.current_scripts_parse:
        reasons.append("selected scripts do not parse in the declared runtime")
    if not evidence.dependency_locks:
        reasons.append("no dependency lock")
    if evidence.same_path_semantic_revisions < 2:
        reasons.append("no two semantic revisions of one executable path")
    if not evidence.same_schema_pair_verified:
        reasons.append("same-schema old/new pair not verified")
    if evidence.variants_introduced_together:
        reasons.append("demo variants were introduced together")
    if not evidence.random_tape_exposed:
        reasons.append("no audited subject random tape")

    baseline = (
        evidence.commit_matches
        and evidence.checkout_clean
        and evidence.license_matches
        and evidence.current_scripts_parse
    )
    evolving = (
        baseline
        and bool(evidence.dependency_locks)
        and evidence.same_path_semantic_revisions >= 2
        and evidence.same_schema_pair_verified
        and not evidence.variants_introduced_together
    )
    replay = evolving and evidence.random_tape_exposed
    return ThemisGateDecision(
        deterministic_baseline_ready=baseline,
        evolving_pair_ready=evolving,
        replay_theorem_ready=replay,
        reasons=tuple(reasons),
    )
