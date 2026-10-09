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


@dataclass(frozen=True)
class ExternalEvolutionEvidence:
    """Evidence for admitting a chronological external software pair."""

    old_commit_matches: bool
    new_commit_matches: bool
    both_checkouts_clean: bool
    new_is_direct_child: bool
    license_unchanged: bool
    dependency_manifest_unchanged: bool
    public_schema_unchanged: bool
    random_draw_path_unchanged: bool
    target_semantics_changed: bool
    upstream_bugfix_documented: bool
    environment_locked: bool
    runtime_preflight_passed: bool
    shared_tape_verified: bool


@dataclass(frozen=True)
class ExternalEvolutionDecision:
    """Source, execution, and replay admission levels for an external pair."""

    source_pair_ready: bool
    execution_ready: bool
    replay_ready: bool
    reasons: tuple[str, ...]


def evaluate_external_evolution_gate(
    evidence: ExternalEvolutionEvidence,
) -> ExternalEvolutionDecision:
    """Fail closed when chronology, schema, semantics, or replay is unverified."""

    source_checks = (
        (evidence.old_commit_matches, "old commit mismatch"),
        (evidence.new_commit_matches, "new commit mismatch"),
        (evidence.both_checkouts_clean, "an external checkout is dirty"),
        (evidence.new_is_direct_child, "new revision is not the direct child of old"),
        (evidence.license_unchanged, "license changed across revisions"),
        (
            evidence.dependency_manifest_unchanged,
            "dependency manifest changed across revisions",
        ),
        (evidence.public_schema_unchanged, "public execution schema changed"),
        (
            evidence.random_draw_path_unchanged,
            "random draw path changed across revisions",
        ),
        (evidence.target_semantics_changed, "target semantics are unchanged"),
        (evidence.upstream_bugfix_documented, "upstream bugfix is not documented"),
    )
    reasons = [message for passed, message in source_checks if not passed]
    if not evidence.environment_locked:
        reasons.append("compatibility environment is not locked")
    if not evidence.runtime_preflight_passed:
        reasons.append("runtime preflight has not passed")
    if not evidence.shared_tape_verified:
        reasons.append("shared random tape has not been verified")

    source_ready = all(passed for passed, _ in source_checks)
    execution_ready = (
        source_ready and evidence.environment_locked and evidence.runtime_preflight_passed
    )
    replay_ready = execution_ready and evidence.shared_tape_verified
    return ExternalEvolutionDecision(
        source_pair_ready=source_ready,
        execution_ready=execution_ready,
        replay_ready=replay_ready,
        reasons=tuple(reasons),
    )


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
