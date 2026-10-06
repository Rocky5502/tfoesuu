import pytest

from tfoesuu.certificate import prune_for_separated_regression, prune_with_patch_envelopes
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



def test_separated_promise_pruning_tracks_three_edge_categories():
    graph = matching_graph(3)
    old = {edge: 0.0 for edge in graph.edges}
    tau = {edge: 0.10 for edge in graph.edges}
    bound = {
        graph.edges[0]: 0.05,  # certified safe
        graph.edges[1]: 0.15,  # not certified, but cannot reach tau+gamma=0.20
        graph.edges[2]: 0.30,  # alternative-capable
    }

    out = prune_for_separated_regression(
        graph, old, tau, bound, gamma=0.10
    )

    assert out.certified_safe_edges == (graph.edges[0],)
    assert out.promise_gap_edges == (graph.edges[1],)
    assert out.alternative_graph.edges == (graph.edges[2],)


def test_separated_promise_boundary_remains_alternative_capable():
    graph = matching_graph(1)
    edge = graph.edges[0]
    out = prune_for_separated_regression(
        graph,
        {edge: 0.0},
        {edge: 0.10},
        {edge: 0.20},
        gamma=0.10,
    )
    assert out.certified_safe_edges == ()
    assert out.promise_gap_edges == ()
    assert out.alternative_graph.edges == (edge,)


def test_separated_promise_pruning_can_remove_all_h1_witnesses_without_certifying_fairness():
    graph = matching_graph(1)
    edge = graph.edges[0]
    out = prune_for_separated_regression(
        graph,
        {edge: 0.0},
        {edge: 0.10},
        {edge: 0.15},
        gamma=0.10,
    )
    assert out.certified_safe_edges == ()
    assert out.promise_gap_edges == (edge,)
    assert out.alternative_graph.m == 0


def test_separated_promise_pruning_validates_gamma():
    graph = matching_graph(1)
    edge = graph.edges[0]
    with pytest.raises(ValueError, match="gamma must be positive"):
        prune_for_separated_regression(
            graph,
            {edge: 0.0},
            {edge: 0.10},
            {edge: 0.15},
            gamma=0.0,
        )
