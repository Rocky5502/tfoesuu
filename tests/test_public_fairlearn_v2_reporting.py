from __future__ import annotations

import copy

import pytest

from tfoesuu.public_fairlearn_v2_reporting import (
    render_results_table,
    render_row_audit_table,
)

REGISTRY = [
    {"benchmark_id": "public-adult", "name": "Adult Census Income"},
    {"benchmark_id": "public-bank", "name": "Bank Marketing"},
]

REPORT = {
    "schema": "tfoesuu-fairlearn-public-v2-validation-v1",
    "record_count": 4,
    "campaign_provenance_valid": True,
    "new_repair_conformance": True,
    "single_attribute_negative_controls": True,
    "datasets": [
        {
            "dataset_id": "public-bank",
            "old_max_abs_pmf_difference": 0.0,
            "old_mean_abs_pmf_difference": 0.0,
            "new_max_abs_pmf_difference": 0.0,
            "new_mean_abs_pmf_difference": 0.0,
        },
        {
            "dataset_id": "public-adult",
            "old_max_abs_pmf_difference": 1.0,
            "old_mean_abs_pmf_difference": 0.05521976534594683,
            "new_max_abs_pmf_difference": 0.0,
            "new_mean_abs_pmf_difference": 0.0,
        },
    ],
}

ADMISSION = {
    "source_artifacts": {
        "old_sha256": "a" * 64,
        "new_sha256": "b" * 64,
        "protocol_sha256": "c" * 64,
    },
    "validation": REPORT,
}

ROW_AUDIT = {
    "schema": "tfoesuu-fairlearn-public-v2-row-audit-v1",
    "source_artifacts": ADMISSION["source_artifacts"],
    "validation": {
        "campaign_provenance_valid": True,
        "new_repair_conformance": True,
        "scope": "paired-software-behavior-only",
    },
    "datasets": [
        {
            "dataset_id": "public-adult",
            "evaluation_rows": 100,
            "parent_affected_rows": 6,
            "parent_affected_fraction": 0.06,
            "parent_max_abs_pmf_difference": 1.0,
            "parent_mean_abs_pmf_difference": 0.05521976534594683,
            "repair_affected_rows": 0,
        },
        {
            "dataset_id": "public-bank",
            "evaluation_rows": 50,
            "parent_affected_rows": 0,
            "parent_affected_fraction": 0.0,
            "parent_max_abs_pmf_difference": 0.0,
            "parent_mean_abs_pmf_difference": 0.0,
            "repair_affected_rows": 0,
        },
    ],
}


def test_results_table_is_complete_registry_ordered_and_booktabs_only():
    table = render_results_table(REPORT, REGISTRY)

    assert table.index("Adult Census Income") < table.index("Bank Marketing")
    assert "1.0000" in table
    assert "0.0552" in table
    assert "0.0000" in table
    assert "\\toprule" in table and "\\bottomrule" in table
    assert "{|" not in table and "|}" not in table
    assert "No confidence interval applies" in table


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("missing", "complete registry census"),
        ("extra", "complete registry census"),
        ("provenance", "validated campaign provenance"),
        ("repair", "repair conformance"),
    ],
)
def test_results_table_fails_closed_on_incomplete_or_invalid_report(mutation, message):
    report = copy.deepcopy(REPORT)
    if mutation == "missing":
        report["datasets"].pop()
    elif mutation == "extra":
        report["datasets"].append(
            {**report["datasets"][0], "dataset_id": "public-unregistered"}
        )
    elif mutation == "provenance":
        report["campaign_provenance_valid"] = False
    else:
        report["new_repair_conformance"] = False

    with pytest.raises(ValueError, match=message):
        render_results_table(report, REGISTRY)


def test_row_audit_table_reports_counts_and_fails_closed_on_hash_drift():
    table = render_row_audit_table(ADMISSION, ROW_AUDIT, REGISTRY)

    assert "6/100 (6.00\\%)" in table
    assert "0/50 (0.00\\%)" in table
    assert "Repair affected" in table
    assert "not causal or population-fairness estimates" in table

    corrupted = copy.deepcopy(ROW_AUDIT)
    corrupted["source_artifacts"]["old_sha256"] = "d" * 64
    with pytest.raises(ValueError, match="does not match admitted results"):
        render_row_audit_table(ADMISSION, corrupted, REGISTRY)
