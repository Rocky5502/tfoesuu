from __future__ import annotations

import copy

import pytest

from tfoesuu.public_fairlearn_v2_reporting import render_results_table

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
