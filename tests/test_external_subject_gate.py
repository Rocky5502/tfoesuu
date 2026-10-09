from tfoesuu.external_subject_gate import (
    ExternalEvolutionEvidence,
    ThemisGateEvidence,
    evaluate_external_evolution_gate,
    evaluate_themis_gate,
    semantic_python_hash,
)


def _valid_evidence(**overrides):
    values = {
        "commit_matches": True,
        "checkout_clean": True,
        "license_matches": True,
        "dependency_locks": ("requirements.txt",),
        "current_scripts_parse": True,
        "same_path_semantic_revisions": 2,
        "same_schema_pair_verified": True,
        "variants_introduced_together": False,
        "random_tape_exposed": True,
    }
    values.update(overrides)
    return ThemisGateEvidence(**values)


def test_semantic_python_hash_ignores_comments_but_detects_behavior_changes():
    first = "x = 1\n# old comment\nprint(x)\n"
    comment_only = "x = 1\n# new comment\nprint(x)\n"
    changed = "x = 2\n# new comment\nprint(x)\n"

    assert semantic_python_hash(first) == semantic_python_hash(comment_only)
    assert semantic_python_hash(first) != semantic_python_hash(changed)


def test_themis_gate_rejects_cointroduced_demo_variants_as_evolution():
    decision = evaluate_themis_gate(
        _valid_evidence(
            dependency_locks=(),
            same_path_semantic_revisions=1,
            same_schema_pair_verified=False,
            variants_introduced_together=True,
            random_tape_exposed=False,
        )
    )

    assert decision.deterministic_baseline_ready
    assert not decision.evolving_pair_ready
    assert not decision.replay_theorem_ready
    assert "no dependency lock" in decision.reasons
    assert "demo variants were introduced together" in decision.reasons
    assert "no audited subject random tape" in decision.reasons


def test_themis_gate_fails_closed_on_identity_or_provenance_mismatch():
    decision = evaluate_themis_gate(
        _valid_evidence(
            commit_matches=False,
            checkout_clean=False,
            license_matches=False,
        )
    )

    assert not decision.deterministic_baseline_ready
    assert not decision.evolving_pair_ready
    assert not decision.replay_theorem_ready
    assert "pinned commit mismatch" in decision.reasons
    assert "checkout is dirty" in decision.reasons
    assert "license hash mismatch" in decision.reasons


def test_themis_gate_distinguishes_evolution_from_replay_readiness():
    evolving = evaluate_themis_gate(_valid_evidence(random_tape_exposed=False))
    replay = evaluate_themis_gate(_valid_evidence())

    assert evolving.deterministic_baseline_ready
    assert evolving.evolving_pair_ready
    assert not evolving.replay_theorem_ready
    assert replay.replay_theorem_ready


def _valid_external_evolution(**overrides):
    values = {
        "old_commit_matches": True,
        "new_commit_matches": True,
        "both_checkouts_clean": True,
        "new_is_direct_child": True,
        "license_unchanged": True,
        "dependency_manifest_unchanged": True,
        "public_schema_unchanged": True,
        "random_draw_path_unchanged": True,
        "target_semantics_changed": True,
        "upstream_bugfix_documented": True,
        "environment_locked": True,
        "runtime_preflight_passed": True,
        "shared_tape_verified": True,
    }
    values.update(overrides)
    return ExternalEvolutionEvidence(**values)


def test_external_evolution_gate_separates_source_execution_and_replay():
    source_only = evaluate_external_evolution_gate(
        _valid_external_evolution(
            environment_locked=False,
            runtime_preflight_passed=False,
            shared_tape_verified=False,
        )
    )
    executable = evaluate_external_evolution_gate(
        _valid_external_evolution(shared_tape_verified=False)
    )
    replay = evaluate_external_evolution_gate(_valid_external_evolution())

    assert source_only.source_pair_ready
    assert not source_only.execution_ready
    assert not source_only.replay_ready
    assert executable.execution_ready
    assert not executable.replay_ready
    assert replay.replay_ready


def test_external_evolution_gate_rejects_unrelated_or_schema_changing_pair():
    decision = evaluate_external_evolution_gate(
        _valid_external_evolution(
            new_is_direct_child=False,
            public_schema_unchanged=False,
            random_draw_path_unchanged=False,
        )
    )

    assert not decision.source_pair_ready
    assert not decision.execution_ready
    assert not decision.replay_ready
    assert "new revision is not the direct child of old" in decision.reasons
    assert "public execution schema changed" in decision.reasons
    assert "random draw path changed across revisions" in decision.reasons


def test_external_evolution_gate_requires_documented_semantic_change():
    decision = evaluate_external_evolution_gate(
        _valid_external_evolution(
            target_semantics_changed=False,
            upstream_bugfix_documented=False,
        )
    )

    assert not decision.source_pair_ready
    assert "target semantics are unchanged" in decision.reasons
    assert "upstream bugfix is not documented" in decision.reasons
