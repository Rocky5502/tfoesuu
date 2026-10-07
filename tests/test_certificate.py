import pytest

from tfoesuu.certificate import prune_with_patch_envelopes, threshold_residual_margins
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


def test_threshold_residual_margins_preserve_directional_headroom():
    graph = matching_graph(1)
    edge = graph.edges[0]
    margins = threshold_residual_margins(
        graph,
        {edge: 0.03},
        {edge: 0.10},
    )

    assert len(margins) == 1
    assert margins[0].positive_headroom == pytest.approx(0.07)
    assert margins[0].negative_headroom == pytest.approx(0.13)


def test_threshold_residual_margins_flip_reversed_signed_gap():
    graph = matching_graph(1)
    u, v = graph.edges[0]
    margins = threshold_residual_margins(
        graph,
        {(v, u): 0.04},
        {(u, v): 0.10},
    )

    assert margins[0].old_signed_gap == pytest.approx(-0.04)
    assert margins[0].positive_headroom == pytest.approx(0.14)
    assert margins[0].negative_headroom == pytest.approx(0.06)


def test_threshold_residual_margins_reject_old_unfair_edge():
    graph = matching_graph(1)
    edge = graph.edges[0]
    with pytest.raises(ValueError):
        threshold_residual_margins(
            graph,
            {edge: 0.11},
            {edge: 0.10},
        )
