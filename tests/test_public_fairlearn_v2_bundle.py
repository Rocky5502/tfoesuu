from __future__ import annotations

import numpy as np
import pytest

from tfoesuu.public_fairlearn_v2_bundle import build_dataset_input_payload


def test_dataset_input_payload_preserves_score_bits_and_group_shapes():
    payload = build_dataset_input_payload(
        dataset_id="toy",
        training_positions=np.array([1, 2]),
        training_scores=np.array([0.2, 0.8]),
        training_labels=np.array([0, 1]),
        evaluation_positions=np.array([3]),
        evaluation_scores=np.array([0.1 + 0.2]),
        training_groups=(("a", 1), ("b", 2)),
        evaluation_groups=(("a", 1),),
    )

    assert float.fromhex(payload["evaluation_score_hex"][0]) == 0.1 + 0.2
    assert payload["native_training_groups"] == [["a", 1], ["b", 2]]
    assert payload["canonical_training_groups"][0] != payload["canonical_training_groups"][1]


def test_dataset_input_payload_keeps_single_attribute_native_vector():
    payload = build_dataset_input_payload(
        dataset_id="single",
        training_positions=np.array([1, 2]),
        training_scores=np.array([0.2, 0.8]),
        training_labels=np.array([0, 1]),
        evaluation_positions=np.array([3]),
        evaluation_scores=np.array([0.5]),
        training_groups=(("a",), ("b",)),
        evaluation_groups=(("a",),),
    )

    assert payload["native_training_groups"] == ["a", "b"]
    assert payload["native_evaluation_groups"] == ["a"]


def test_dataset_input_payload_rejects_alignment_or_width_drift():
    with pytest.raises(ValueError, match="misaligned"):
        build_dataset_input_payload(
            dataset_id="toy",
            training_positions=np.array([1, 2]),
            training_scores=np.array([0.2]),
            training_labels=np.array([0, 1]),
            evaluation_positions=np.array([3]),
            evaluation_scores=np.array([0.5]),
            training_groups=(("a",), ("b",)),
            evaluation_groups=(("a",),),
        )
