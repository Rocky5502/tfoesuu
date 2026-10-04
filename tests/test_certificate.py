import pytest

from tfoesuu.certificate import prune_with_patch_envelopes
from tfoesuu.graphs import matching_graph


def test_sound_patch_envelopes_prune_safe_edges():
    graph = matching_graph(3)
    old = {edge: 0.01 for edge in graph.edges}
    tau = {edge: 0.10 for edge in graph.edges}
    bound = {
        graph.edges[0]: 0.02,
        graph.edges[1]: 0.09,
        graph.edges[2]: 0.20,
    }

    out = prune_with_patch_envelopes(graph, old, tau, bound)

    assert out.safe_edges == (graph.edges[0], graph.edges[1])
    assert out.residual_graph.edges == (graph.edges[2],)


def test_boundary_is_safe_by_non_strict_fairness_definition():
    graph = matching_graph(1)
    edge = graph.edges[0]
    out = prune_with_patch_envelopes(
        graph,
        {edge: -0.04},
        {edge: 0.10},
        {edge: 0.06},
    )
    assert out.residual_graph.m == 0


def test_invalid_negative_patch_bound_rejected():
    graph = matching_graph(1)
    edge = graph.edges[0]
    with pytest.raises(ValueError):
        prune_with_patch_envelopes(
            graph,
            {edge: 0.0},
            {edge: 0.1},
            {edge: -0.01},
        )
