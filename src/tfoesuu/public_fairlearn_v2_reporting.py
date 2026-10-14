from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .public_fairlearn_v2_results import validate_public_fairlearn_v2_campaign_outputs


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _validated_rows(report: dict, registry: list[dict]) -> list[tuple[dict, dict]]:
    if report.get("campaign_provenance_valid") is not True:
        raise ValueError("results table requires validated campaign provenance")
    if report.get("new_repair_conformance") is not True:
        raise ValueError("results table requires validated repair conformance")
    by_id = {row.get("dataset_id"): row for row in report.get("datasets", [])}
    registry_by_id = {row.get("benchmark_id"): row for row in registry}
    if (
        len(by_id) != len(report.get("datasets", []))
        or len(registry_by_id) != len(registry)
        or set(by_id) != set(registry_by_id)
    ):
        raise ValueError("results table requires the complete registry census")
    return [(registry_row, by_id[registry_row["benchmark_id"]]) for registry_row in registry]


def render_results_table(report: dict, registry: list[dict]) -> str:
    """Render the complete exact-PMF census as a compact booktabs table."""

    rows = _validated_rows(report, registry)
    body = []
    for registry_row, result in rows:
        values = (
            result["old_max_abs_pmf_difference"],
            result["old_mean_abs_pmf_difference"],
            result["new_max_abs_pmf_difference"],
            result["new_mean_abs_pmf_difference"],
        )
        if any(not isinstance(value, (int, float)) for value in values):
            raise ValueError(f"{result['dataset_id']}: nonnumeric PMF discrepancy")
        body.append(
            f"{registry_row['name']} & " + " & ".join(f"{value:.4f}" for value in values) + r" \\"
        )
    return "\n".join(
        [
            r"\begin{table}[H]",
            r"\centering",
            (
                r"\caption{The repair eliminates every observed native-versus-canonical PMF "
                r"discrepancy. Entries are exact row-wise absolute probability-mass differences "
                r"under the frozen seven-dataset census; lower is conformance.}"
            ),
            r"\label{tab:fairlearn-v2-results}",
            r"\small",
            r"\begin{tabular}{@{}lrrrr@{}}",
            r"\toprule",
            (
                r"& \multicolumn{2}{c}{Parent $|\Delta\mathrm{PMF}|$} "
                r"& \multicolumn{2}{c}{Repaired $|\Delta\mathrm{PMF}|$} \\"
            ),
            r"\cmidrule(lr){2-3}\cmidrule(l){4-5}",
            r"Dataset & Max & Mean & Max & Mean \\",
            r"\midrule",
            *body,
            r"\bottomrule",
            r"\end{tabular}",
            r"\vspace{2pt}",
            r"\begin{minipage}{0.98\linewidth}\footnotesize",
            (
                r"The primary analysis uses deterministic exact PMFs. No confidence interval "
                r"applies; four frozen common-tape seeds serve only as implementation-correspondence "
                r"checks. All datasets, including exact zeros, are reported."
            ),
            r"\end{minipage}",
            r"\end{table}",
            "",
        ]
    )


def render_row_audit_table(admission: dict, row_audit: dict, registry: list[dict]) -> str:
    """Render the provenance-bound row-count extension of the complete census."""

    if row_audit.get("schema") != "tfoesuu-fairlearn-public-v2-row-audit-v1":
        raise ValueError("row audit schema mismatch")
    admitted_sources = admission.get("source_artifacts", {})
    audit_sources = row_audit.get("source_artifacts", {})
    for name in ("old_sha256", "new_sha256", "protocol_sha256"):
        if admitted_sources.get(name) != audit_sources.get(name):
            raise ValueError(f"row audit {name} does not match admitted results")
    validation = row_audit.get("validation", {})
    if (
        validation.get("campaign_provenance_valid") is not True
        or validation.get("new_repair_conformance") is not True
        or validation.get("scope") != "paired-software-behavior-only"
    ):
        raise ValueError("row audit validation boundary is incomplete")

    admitted = admission.get("validation", {})
    admitted_by_id = {row.get("dataset_id"): row for row in admitted.get("datasets", [])}
    audit_by_id = {row.get("dataset_id"): row for row in row_audit.get("datasets", [])}
    registry_by_id = {row.get("benchmark_id"): row for row in registry}
    if not registry_by_id or set(admitted_by_id) != set(audit_by_id) or set(audit_by_id) != set(
        registry_by_id
    ):
        raise ValueError("row audit requires the complete admitted registry census")

    body = []
    for registry_row in registry:
        dataset_id = registry_row["benchmark_id"]
        result = audit_by_id[dataset_id]
        admitted_result = admitted_by_id[dataset_id]
        rows = result.get("evaluation_rows")
        affected = result.get("parent_affected_rows")
        fraction = result.get("parent_affected_fraction")
        repair_affected = result.get("repair_affected_rows")
        if (
            isinstance(rows, bool)
            or not isinstance(rows, int)
            or rows <= 0
            or isinstance(affected, bool)
            or not isinstance(affected, int)
            or not 0 <= affected <= rows
            or fraction != affected / rows
            or repair_affected != 0
            or result.get("parent_max_abs_pmf_difference")
            != admitted_result.get("old_max_abs_pmf_difference")
            or result.get("parent_mean_abs_pmf_difference")
            != admitted_result.get("old_mean_abs_pmf_difference")
        ):
            raise ValueError(f"{dataset_id}: row audit disagrees with admitted estimands")
        body.append(
            f"{registry_row['name']} & {affected}/{rows} ({100 * fraction:.2f}\\%) & "
            f"{result['parent_max_abs_pmf_difference']:.4f} & "
            f"{result['parent_mean_abs_pmf_difference']:.4f} & {repair_affected}/{rows} \\\\"
        )
    return "\n".join(
        [
            r"\begin{table}[H]",
            r"\centering",
            (
                r"\caption{Historical protected-group encoding comparison. Affected rows have "
                r"nonzero exact native-versus-canonical randomized-prediction PMF discrepancy; "
                r"the full seven-population census, including zeros, is retained.}"
            ),
            r"\label{tab:historical-census}",
            r"\small",
            r"\begin{tabular}{@{}lrrrr@{}}",
            r"\toprule",
            r"Dataset & Parent affected & Parent max & Parent mean & Repair affected \\",
            r"\midrule",
            *body,
            r"\bottomrule",
            r"\end{tabular}",
            r"\vspace{2pt}",
            r"\begin{minipage}{0.98\linewidth}\footnotesize",
            (
                r"The comparison uses deterministic exact PMFs on frozen evaluation rows, so no "
                r"sampling confidence interval applies. Counts are descriptive software-behavior "
                r"results, not causal or population-fairness estimates."
            ),
            r"\end{minipage}",
            r"\end{table}",
            "",
        ]
    )


def admit_campaign_outputs(
    *,
    old_path: Path,
    new_path: Path,
    protocol_path: Path,
    registry_path: Path,
    expected_runner_commit: str,
    expected_input_bundle_manifest_sha256: str,
) -> tuple[dict, str]:
    """Validate raw campaign outputs and return reproducible JSON and TeX artifacts."""

    old = json.loads(old_path.read_text(encoding="utf-8"))
    new = json.loads(new_path.read_text(encoding="utf-8"))
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    registry = load_jsonl(registry_path)
    protocol_sha256 = sha256_file(protocol_path)
    report = validate_public_fairlearn_v2_campaign_outputs(
        old,
        new,
        protocol,
        expected_protocol_sha256=protocol_sha256,
        expected_runner_commit=expected_runner_commit,
        expected_input_bundle_manifest_sha256=expected_input_bundle_manifest_sha256,
    )
    _validated_rows(report, registry)
    admission = {
        "schema": "tfoesuu-fairlearn-public-v2-admission-v1",
        "source_artifacts": {
            "old_sha256": sha256_file(old_path),
            "new_sha256": sha256_file(new_path),
            "protocol_sha256": protocol_sha256,
            "registry_sha256": sha256_file(registry_path),
        },
        "validation": report,
    }
    return admission, render_results_table(report, registry)
