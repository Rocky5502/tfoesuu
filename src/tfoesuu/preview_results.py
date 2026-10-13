"""Fail-closed admission checks for the frozen P12/P15 100k previews."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from scipy.stats import binom, binomtest

from .counterfactual_benchmarks import (
    CounterfactualReplayBenchmarkSpec,
    read_counterfactual_replay_jsonl,
)
from .replay_benchmarks import ReplayBenchmarkSpec, read_replay_jsonl
from .separations import counterfactual_replay_bounds, replay_separation_bounds

SCHEMA = "tfoesuu-p12-p15-preview-admission-v1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _lf_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def _read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise TypeError(f"JSONL row {line_number} is not an object")
            rows.append(row)
    return rows


def _assert_close(row: dict[str, Any], field: str, expected: float) -> None:
    observed = row.get(field)
    if isinstance(expected, int):
        if observed != expected:
            raise ValueError(
                f"formula mismatch for {row.get('benchmark_id')} field {field}: "
                f"expected {expected}, observed {observed}"
            )
        return
    if not isinstance(observed, (int, float)) or not math.isclose(
        float(observed), expected, rel_tol=1e-12, abs_tol=1e-12
    ):
        raise ValueError(
            f"formula mismatch for {row.get('benchmark_id')} field {field}: "
            f"expected {expected!r}, observed {observed!r}"
        )


def _validate_identity(
    rows: list[dict[str, Any]],
    specs: Iterable[ReplayBenchmarkSpec | CounterfactualReplayBenchmarkSpec],
    *,
    expected_rows: int,
    trials: int,
) -> dict[str, ReplayBenchmarkSpec | CounterfactualReplayBenchmarkSpec]:
    ids = [row.get("benchmark_id") for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("result rows must have unique benchmark IDs")
    if len(rows) != expected_rows:
        raise ValueError(
            f"complete specification census required: expected {expected_rows} rows, "
            f"observed {len(rows)}"
        )
    spec_by_id = {spec.benchmark_id: spec for spec in specs}
    if set(ids) != set(spec_by_id):
        raise ValueError("complete specification census required: result/spec IDs differ")
    for row in rows:
        if row.get("trials") != trials:
            raise ValueError(
                f"trial budget mismatch for {row.get('benchmark_id')}: "
                f"expected {trials}, observed {row.get('trials')}"
            )
        if not isinstance(row.get("device"), str) or not row["device"].startswith("cuda:"):
            raise ValueError(f"invalid CUDA device for {row.get('benchmark_id')}")
        spec = spec_by_id[row["benchmark_id"]]
        for field, expected in spec.__dict__.items():
            if row.get(field) != expected:
                raise ValueError(f"specification mismatch for {row['benchmark_id']} field {field}")
    return spec_by_id


def _empirical_count(row: dict[str, Any], field: str, trials: int) -> int:
    rate = row.get(field)
    if not isinstance(rate, (int, float)) or not 0.0 <= float(rate) <= 1.0:
        raise ValueError(f"invalid empirical rate {field} for {row.get('benchmark_id')}")
    count = round(float(rate) * trials)
    if not math.isclose(float(rate), count / trials, abs_tol=1e-6 / trials + 5e-8):
        raise ValueError(
            f"empirical rate {field} for {row.get('benchmark_id')} is not a trial-count proportion"
        )
    return count


def _audit_rate(
    row: dict[str, Any], field: str, trials: int, probability: float
) -> tuple[float, float]:
    count = _empirical_count(row, field, trials)
    p_value = float(binomtest(count, trials, probability).pvalue)
    return p_value, abs(count / trials - probability)


def _validate_p12(
    rows: list[dict[str, Any]],
    specs: list[ReplayBenchmarkSpec],
    *,
    expected_rows: int,
    trials: int,
) -> list[tuple[float, float]]:
    by_id = _validate_identity(rows, specs, expected_rows=expected_rows, trials=trials)
    audits: list[tuple[float, float]] = []
    for row in rows:
        spec = by_id[row["benchmark_id"]]
        assert isinstance(spec, ReplayBenchmarkSpec)
        bounds = replay_separation_bounds(spec.p, spec.d, spec.beta)
        for field, expected in {
            "paired_upper_rounds": bounds.paired_upper_rounds,
            "paired_null_expected_lower": bounds.paired_null_expected_lower,
            "paired_per_round_kl": bounds.paired_per_round_kl,
            "independent_upper_rounds": bounds.independent_upper_rounds,
            "independent_null_expected_lower": bounds.independent_null_expected_lower,
            "independent_per_round_kl": bounds.independent_per_round_kl,
            "upper_round_ratio_ind_over_pair": (
                bounds.independent_upper_rounds / bounds.paired_upper_rounds
            ),
            "lower_round_ratio_ind_over_pair": (
                bounds.independent_null_expected_lower / bounds.paired_null_expected_lower
            ),
        }.items():
            _assert_close(row, field, expected)
        cutoff_count = math.ceil(bounds.independent_upper_rounds * (spec.p + spec.d / 2.0))
        audits.extend(
            [
                _audit_rate(
                    row,
                    "paired_alt_miss_empirical",
                    trials,
                    (1.0 - spec.d) ** bounds.paired_upper_rounds,
                ),
                _audit_rate(
                    row,
                    "independent_null_error_empirical",
                    trials,
                    float(
                        binom.sf(
                            cutoff_count - 1,
                            bounds.independent_upper_rounds,
                            spec.p,
                        )
                    ),
                ),
                _audit_rate(
                    row,
                    "independent_alt_miss_empirical",
                    trials,
                    float(
                        binom.cdf(
                            cutoff_count - 1,
                            bounds.independent_upper_rounds,
                            spec.p + spec.d,
                        )
                    ),
                ),
            ]
        )
    return audits


def _validate_p15(
    rows: list[dict[str, Any]],
    specs: list[CounterfactualReplayBenchmarkSpec],
    *,
    expected_rows: int,
    trials: int,
) -> list[tuple[float, float]]:
    by_id = _validate_identity(rows, specs, expected_rows=expected_rows, trials=trials)
    audits: list[tuple[float, float]] = []
    for row in rows:
        spec = by_id[row["benchmark_id"]]
        assert isinstance(spec, CounterfactualReplayBenchmarkSpec)
        bounds = counterfactual_replay_bounds(spec.p, spec.shared_patch, spec.d, spec.beta)
        for field, expected in {
            "edge_coupled_upper_rounds": bounds.edge_coupled_upper_rounds,
            "edge_coupled_concrete_executions": 4 * bounds.edge_coupled_upper_rounds,
            "edge_coupled_null_expected_lower": (bounds.edge_coupled_null_expected_lower),
            "edge_coupled_per_round_kl": bounds.edge_coupled_per_round_kl,
            "vertex_paired_upper_rounds": bounds.vertex_paired_upper_rounds,
            "vertex_paired_concrete_executions": 2 * bounds.vertex_paired_upper_rounds,
            "vertex_paired_null_expected_lower": (bounds.vertex_paired_null_expected_lower),
            "vertex_paired_per_round_kl": bounds.vertex_paired_per_round_kl,
            "upper_round_ratio_vertex_over_edge": (
                bounds.vertex_paired_upper_rounds / bounds.edge_coupled_upper_rounds
            ),
            "lower_round_ratio_vertex_over_edge": (
                bounds.vertex_paired_null_expected_lower / bounds.edge_coupled_null_expected_lower
            ),
        }.items():
            _assert_close(row, field, expected)
        cutoff_count = math.ceil(
            bounds.vertex_paired_upper_rounds * (spec.shared_patch + spec.d / 2.0)
        )
        audits.extend(
            [
                _audit_rate(
                    row,
                    "edge_coupled_alt_miss_empirical",
                    trials,
                    (1.0 - spec.d) ** bounds.edge_coupled_upper_rounds,
                ),
                _audit_rate(
                    row,
                    "vertex_paired_null_error_empirical",
                    trials,
                    float(
                        binom.sf(
                            cutoff_count - 1,
                            bounds.vertex_paired_upper_rounds,
                            spec.shared_patch,
                        )
                    ),
                ),
                _audit_rate(
                    row,
                    "vertex_paired_alt_miss_empirical",
                    trials,
                    float(
                        binom.cdf(
                            cutoff_count - 1,
                            bounds.vertex_paired_upper_rounds,
                            spec.shared_patch + spec.d,
                        )
                    ),
                ),
            ]
        )
    return audits


def _git_blob_at_commit(base_dir: Path, commit: str, path: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(base_dir), "rev-parse", f"{commit}:{path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    blob = completed.stdout.strip()
    if completed.returncode != 0 or len(blob) != 40:
        raise ValueError(f"cannot resolve Git blob {commit}:{path}")
    return blob


def _resolve_and_hash(
    base_dir: Path,
    record: dict[str, Any],
    kind: str,
    *,
    source_commit: str,
) -> tuple[Path, Path]:
    spec_path = (base_dir / record["spec_path"]).resolve()
    result_path = (base_dir / record["result_path"]).resolve()
    for path, field in (
        (spec_path, "spec_sha256"),
        (result_path, "result_sha256"),
    ):
        if not path.is_file():
            raise ValueError(f"missing {kind} artifact: {path}")
        expected = record.get(field)
        observed = _sha256(path)
        if observed != expected:
            raise ValueError(
                f"SHA-256 mismatch for {kind} {path.name}: expected {expected}, observed {observed}"
            )
    if "spec_lf_sha256" in record:
        observed_lf = _lf_sha256(spec_path)
        if observed_lf != record["spec_lf_sha256"]:
            raise ValueError(f"LF-normalized SHA-256 mismatch for {kind} specification")
    if "runner_path" in record:
        runner = (base_dir / record["runner_path"]).resolve()
        if not runner.is_file():
            raise ValueError(f"missing {kind} runner: {runner}")
        if "runner_git_blob" not in record and _sha256(runner) != record.get("runner_sha256"):
            raise ValueError(f"SHA-256 mismatch for {kind} runner")
    for path_field, blob_field in (
        ("spec_path", "spec_git_blob"),
        ("runner_path", "runner_git_blob"),
    ):
        if blob_field in record:
            observed_blob = _git_blob_at_commit(base_dir, source_commit, record[path_field])
            if observed_blob != record[blob_field]:
                raise ValueError(
                    f"Git blob mismatch for {kind} {path_field}: "
                    f"expected {record[blob_field]}, observed {observed_blob}"
                )
    return spec_path, result_path


def validate_preview_campaign(
    manifest_path: str | Path, *, base_dir: str | Path | None = None
) -> dict[str, Any]:
    """Validate immutable P12/P15 artifacts and recompute all finite laws."""

    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError(f"unsupported preview manifest schema: {manifest.get('schema')}")
    source_commit = manifest.get("source_commit")
    if not isinstance(source_commit, str) or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None:
        raise ValueError("source_commit must be a full 40-character Git SHA")
    trials = manifest.get("trials_per_configuration")
    if not isinstance(trials, int) or trials <= 0:
        raise ValueError("trials_per_configuration must be positive")
    alpha = manifest.get("familywise_alpha")
    if not isinstance(alpha, (int, float)) or not 0.0 < float(alpha) < 1.0:
        raise ValueError("familywise_alpha must lie in (0,1)")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != {"p12", "p15"}:
        raise ValueError("manifest must contain exactly the P12 and P15 artifacts")
    root = Path(base_dir) if base_dir is not None else manifest_file.parent

    p12_spec_path, p12_result_path = _resolve_and_hash(
        root, artifacts["p12"], "P12", source_commit=source_commit
    )
    p15_spec_path, p15_result_path = _resolve_and_hash(
        root, artifacts["p15"], "P15", source_commit=source_commit
    )
    p12_rows = _read_rows(p12_result_path)
    p15_rows = _read_rows(p15_result_path)
    audits = _validate_p12(
        p12_rows,
        read_replay_jsonl(p12_spec_path),
        expected_rows=artifacts["p12"]["expected_rows"],
        trials=trials,
    )
    audits.extend(
        _validate_p15(
            p15_rows,
            read_counterfactual_replay_jsonl(p15_spec_path),
            expected_rows=artifacts["p15"]["expected_rows"],
            trials=trials,
        )
    )
    threshold = float(alpha) / len(audits)
    outliers = sum(p_value < threshold for p_value, _ in audits)
    if manifest.get("require_no_bonferroni_outliers") and outliers:
        raise ValueError(f"observed {outliers} Bonferroni finite-law outliers")
    return {
        "schema": "tfoesuu-p12-p15-preview-validation-v1",
        "source_commit": source_commit,
        "record_count": len(p12_rows) + len(p15_rows),
        "p12_record_count": len(p12_rows),
        "p15_record_count": len(p15_rows),
        "trials_per_configuration": trials,
        "comparison_count": len(audits),
        "bonferroni_threshold": threshold,
        "bonferroni_outlier_count": outliers,
        "minimum_exact_p_value": min(p_value for p_value, _ in audits),
        "maximum_absolute_empirical_deviation": max(difference for _, difference in audits),
        "all_schedules_exact": True,
        "all_empirical_rates_valid": True,
        "result_sha256": {
            "p12": _sha256(p12_result_path),
            "p15": _sha256(p15_result_path),
        },
    }
