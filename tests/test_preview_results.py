from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from tfoesuu import preview_results
from tfoesuu.counterfactual_benchmarks import CounterfactualReplayBenchmarkSpec
from tfoesuu.preview_results import validate_preview_campaign
from tfoesuu.replay_benchmarks import ReplayBenchmarkSpec
from tfoesuu.separations import (
    counterfactual_replay_bounds,
    replay_separation_bounds,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _campaign(tmp_path: Path) -> tuple[Path, Path]:
    replay_spec = ReplayBenchmarkSpec("r0001", 0.25, 0.1, 0.05, 20001)
    counter_spec = CounterfactualReplayBenchmarkSpec("c0001", 0.2, 0.05, 0.05, 0.05, 40001)
    replay_bounds = replay_separation_bounds(replay_spec.p, replay_spec.d, replay_spec.beta)
    counter_bounds = counterfactual_replay_bounds(
        counter_spec.p,
        counter_spec.shared_patch,
        counter_spec.d,
        counter_spec.beta,
    )

    replay_specs = tmp_path / "replay_specs.jsonl"
    counter_specs = tmp_path / "counter_specs.jsonl"
    replay_results = tmp_path / "replay_results.jsonl"
    counter_results = tmp_path / "counter_results.jsonl"
    _write_jsonl(replay_specs, [replay_spec.__dict__])
    _write_jsonl(counter_specs, [counter_spec.__dict__])
    _write_jsonl(
        replay_results,
        [
            {
                **replay_spec.__dict__,
                "device": "cuda:0",
                "trials": 100_000,
                "paired_upper_rounds": replay_bounds.paired_upper_rounds,
                "paired_null_expected_lower": replay_bounds.paired_null_expected_lower,
                "paired_per_round_kl": replay_bounds.paired_per_round_kl,
                "paired_alt_miss_empirical": 0.05,
                "independent_upper_rounds": replay_bounds.independent_upper_rounds,
                "independent_null_expected_lower": (replay_bounds.independent_null_expected_lower),
                "independent_per_round_kl": replay_bounds.independent_per_round_kl,
                "independent_null_error_empirical": 0.02,
                "independent_alt_miss_empirical": 0.03,
                "upper_round_ratio_ind_over_pair": (
                    replay_bounds.independent_upper_rounds / replay_bounds.paired_upper_rounds
                ),
                "lower_round_ratio_ind_over_pair": (
                    replay_bounds.independent_null_expected_lower
                    / replay_bounds.paired_null_expected_lower
                ),
            }
        ],
    )
    _write_jsonl(
        counter_results,
        [
            {
                **counter_spec.__dict__,
                "device": "cuda:0",
                "trials": 100_000,
                "edge_coupled_upper_rounds": (counter_bounds.edge_coupled_upper_rounds),
                "edge_coupled_concrete_executions": (4 * counter_bounds.edge_coupled_upper_rounds),
                "edge_coupled_null_expected_lower": (
                    counter_bounds.edge_coupled_null_expected_lower
                ),
                "edge_coupled_per_round_kl": (counter_bounds.edge_coupled_per_round_kl),
                "edge_coupled_alt_miss_empirical": 0.05,
                "vertex_paired_upper_rounds": (counter_bounds.vertex_paired_upper_rounds),
                "vertex_paired_concrete_executions": (
                    2 * counter_bounds.vertex_paired_upper_rounds
                ),
                "vertex_paired_null_expected_lower": (
                    counter_bounds.vertex_paired_null_expected_lower
                ),
                "vertex_paired_per_round_kl": (counter_bounds.vertex_paired_per_round_kl),
                "vertex_paired_null_error_empirical": 0.02,
                "vertex_paired_alt_miss_empirical": 0.03,
                "upper_round_ratio_vertex_over_edge": (
                    counter_bounds.vertex_paired_upper_rounds
                    / counter_bounds.edge_coupled_upper_rounds
                ),
                "lower_round_ratio_vertex_over_edge": (
                    counter_bounds.vertex_paired_null_expected_lower
                    / counter_bounds.edge_coupled_null_expected_lower
                ),
            }
        ],
    )

    manifest = {
        "schema": "tfoesuu-p12-p15-preview-admission-v1",
        "source_commit": "149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b",
        "trials_per_configuration": 100_000,
        "familywise_alpha": 0.05,
        "artifacts": {
            "p12": {
                "spec_path": replay_specs.name,
                "spec_sha256": _sha256(replay_specs),
                "result_path": replay_results.name,
                "result_sha256": _sha256(replay_results),
                "expected_rows": 1,
            },
            "p15": {
                "spec_path": counter_specs.name,
                "spec_sha256": _sha256(counter_specs),
                "result_path": counter_results.name,
                "result_sha256": _sha256(counter_results),
                "expected_rows": 1,
            },
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path, replay_results


def test_preview_campaign_accepts_complete_formula_consistent_census(tmp_path):
    manifest, _ = _campaign(tmp_path)

    report = validate_preview_campaign(manifest, base_dir=tmp_path)

    assert report["record_count"] == 2
    assert report["comparison_count"] == 6
    assert report["all_schedules_exact"] is True
    assert report["all_empirical_rates_valid"] is True


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("hash", "SHA-256"),
        ("trials", "trial budget"),
        ("schedule", "formula mismatch"),
        ("duplicate", "unique benchmark IDs"),
        ("missing", "complete specification census"),
    ],
)
def test_preview_campaign_fails_closed_on_corruption(tmp_path, mutation, message):
    manifest_path, replay_results = _campaign(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in replay_results.read_text().splitlines()]

    if mutation == "hash":
        manifest["artifacts"]["p12"]["result_sha256"] = "0" * 64
    elif mutation == "trials":
        rows[0]["trials"] = 99_999
    elif mutation == "schedule":
        rows[0]["paired_upper_rounds"] += 1
    elif mutation == "duplicate":
        rows.append(copy.deepcopy(rows[0]))
    else:
        rows.clear()

    if mutation != "hash":
        _write_jsonl(replay_results, rows)
        manifest["artifacts"]["p12"]["result_sha256"] = _sha256(replay_results)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        validate_preview_campaign(manifest_path, base_dir=tmp_path)


def test_preview_campaign_rejects_mismatched_declared_git_blob(tmp_path, monkeypatch):
    manifest_path, _ = _campaign(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"]["p12"]["spec_git_blob"] = "1" * 40
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(preview_results, "_git_blob_at_commit", lambda *_: "2" * 40)

    with pytest.raises(ValueError, match="Git blob mismatch"):
        validate_preview_campaign(manifest_path, base_dir=tmp_path)
