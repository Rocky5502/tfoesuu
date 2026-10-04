import pytest

from tfoesuu.graph_replay import fractional_vertex_cover, integral_vertex_cover_size
from tfoesuu.graphs import (
    clique_graph,
    complete_bipartite_graph,
    edge_graph,
    matching_graph,
    path_graph,
    star_graph,
)


@pytest.mark.parametrize(
    "graph,expected",
    [
        (edge_graph(),1.0),
        (matching_graph(5),5.0),
        (star_graph(9),1.0),
        (complete_bipartite_graph(3,7),3.0),
        (clique_graph(8),4.0),
    ],
)
def test_fractional_cover_known_values(graph,expected):
    r=fractional_vertex_cover(graph)
    assert r.success
    assert r.objective==pytest.approx(expected,abs=1e-8)
    for u,v in graph.edges:
        assert r.weights[u]+r.weights[v]>=1-1e-8


def test_triangle_has_fractional_integral_gap():
    tri=clique_graph(3)
    assert fractional_vertex_cover(tri).objective==pytest.approx(1.5)
    assert integral_vertex_cover_size(tri)==2


def test_bipartite_integrality_on_star():
    g=star_graph(20)
    assert fractional_vertex_cover(g).objective==pytest.approx(integral_vertex_cover_size(g))
