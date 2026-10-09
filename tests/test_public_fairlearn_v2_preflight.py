from __future__ import annotations

import numpy as np
import pytest

from tfoesuu.public_fairlearn_v2_preflight import (
    audit_group_support,
    canonical_tuple_key,
    transform_protected_rows,
)


def test_canonical_tuple_key_is_injective_for_concatenation_collision():
    assert canonical_tuple_key(("a", "bc")) != canonical_tuple_key(("ab", "c"))
    assert canonical_tuple_key(("é", "x")) == canonical_tuple_key(("é", "x"))


def test_transform_protected_rows_applies_frozen_age_threshold():
    rows = np.array([["female", 24], ["male", 25]], dtype=object)
    transformed = transform_protected_rows(
        rows,
        ("sex", "age"),
        {
            "sex": {"kind": "identity"},
            "age": {
                "kind": "threshold",
                "cut": 25,
                "lower_label": "age<25",
                "upper_label": "age>=25",
            },
        },
    )

    assert transformed == (("female", "age<25"), ("male", "age>=25"))


def test_support_audit_checks_rows_labels_and_evaluation_coverage():
    train_groups = (("a",),) * 4 + (("b",),) * 4
    labels = np.array([0, 0, 1, 1, 0, 0, 1, 1])
    evaluation_groups = (("a",), ("b",))
    report = audit_group_support(
        train_groups,
        labels,
        evaluation_groups,
        minimum_training_rows=4,
        minimum_training_per_label=2,
        minimum_evaluation_rows=1,
    )

    assert report["group_count"] == 2
    assert report["minimum_training_rows"] == 4
    assert report["minimum_training_rows_per_label"] == 2


def test_support_audit_fails_closed_without_both_labels():
    with pytest.raises(ValueError, match="support gate failed"):
        audit_group_support(
            (("a",),) * 4,
            np.array([0, 0, 0, 1]),
            (("a",),),
            minimum_training_rows=4,
            minimum_training_per_label=2,
            minimum_evaluation_rows=1,
        )
