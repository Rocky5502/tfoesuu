from tfoesuu.external_subject_gate import (
    ThemisGateEvidence,
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
