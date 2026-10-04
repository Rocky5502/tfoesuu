import pytest

from tfoesuu.graphs import clique_graph, matching_graph, star_graph
from tfoesuu.suite_replay import (
    active_vertex_count,
    synchronized_suite_replay_bounds,
)


@pytest.mark.parametrize(
    "graph,expected",
    [
        (matching_graph(5), 10),
        (star_graph(9), 9),
        (clique_graph(8), 8),
    ],
)
def test_active_vertex_count(graph, expected):
    assert active_vertex_count(graph) == expected


def test_suite_replay_rounds_do_not_depend_on_edge_count():
    star = synchronized_suite_replay_bounds(
        star_graph(20), 0.3, 0.2, 0.01, 0.05
    )
    clique = synchronized_suite_replay_bounds(
        clique_graph(20), 0.3, 0.2, 0.01, 0.05
    )
    assert star.replay_rounds_upper == clique.replay_rounds_upper
    assert star.concrete_executions_upper == clique.concrete_executions_upper


def test_suite_replay_small_d_is_linear():
    b1 = synchronized_suite_replay_bounds(
        clique_graph(10), 0.3, 0.2, 1e-4, 0.05
    )
    b2 = synchronized_suite_replay_bounds(
        clique_graph(10), 0.3, 0.2, 5e-5, 0.05
    )
    assert (
        b2.null_expected_rounds_lower / b1.null_expected_rounds_lower
    ) == pytest.approx(2.0, rel=5e-4)


def test_dense_graph_suite_replay_beats_edgewise_execution_count():
    n = 20
    graph = clique_graph(n)
    b = synchronized_suite_replay_bounds(graph, 0.3, 0.2, 0.01, 0.05)
    edgewise_concrete = 4 * graph.m * b.replay_rounds_upper
    assert edgewise_concrete / b.concrete_executions_upper == pytest.approx(
        2 * graph.m / n
    )
