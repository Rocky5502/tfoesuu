import numpy as np
import pytest

from tfoesuu.software_subjects import (
    RandomizedResourceAllocatorPair,
    linear_baseline,
)


def test_old_version_is_counterfactually_fair():
    subject = RandomizedResourceAllocatorPair.from_sequences(
        linear_baseline(8),
        affected_contexts=[3],
        delta=0.02,
    )
    for u, v in subject.fairness_graph.edges:
        assert subject.probability(0, u) == subject.probability(0, v)


def test_patch_impact_and_new_fairness_regression():
    subject = RandomizedResourceAllocatorPair.from_sequences(
        linear_baseline(8),
        affected_contexts=[2, 6],
        delta=0.03,
    )
    expected_vertices = (
        subject.encode_vertex(2, 1),
        subject.encode_vertex(6, 1),
    )
    assert subject.replay_sound_impact_vertices == expected_vertices
    assert len(subject.impacted_edges) == 2

    for context in [2, 6]:
        u = subject.encode_vertex(context, 0)
        v = subject.encode_vertex(context, 1)
        assert abs(subject.probability(1, u) - subject.probability(1, v)) == pytest.approx(0.03)


def test_unaffected_vertex_has_zero_paired_delta():
    subject = RandomizedResourceAllocatorPair.from_sequences(
        linear_baseline(5),
        affected_contexts=[1],
        delta=0.05,
    )
    vertex = subject.encode_vertex(4, 1)
    rng = np.random.default_rng(7)
    z = subject.sample_paired_delta(vertex, 10000, rng)
    assert np.all(z == 0)


def test_affected_vertex_matches_sparse_delta_formula():
    d = 0.02
    subject = RandomizedResourceAllocatorPair.from_sequences(
        [0.4, 0.5, 0.6],
        affected_contexts=[1],
        delta=d,
    )
    vertex = subject.encode_vertex(1, 1)
    rng = np.random.default_rng(11)
    z = subject.sample_paired_delta(vertex, 500_000, rng)
    assert abs(float(z.mean()) - d) < 0.001
    assert abs(float(z.var()) - d * (1.0 - d)) < 0.001
