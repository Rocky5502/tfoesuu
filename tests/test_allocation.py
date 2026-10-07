import math

import numpy as np

from tfoesuu.allocation import (
    exact_unit_variance_psi,
    psi_conic_certificate,
    solve_psi,
    solve_psi_dual,
)
from tfoesuu.graphs import (
    clique_graph,
    complete_bipartite_graph,
    edge_graph,
    matching_graph,
    star_graph,
)


def assert_close(a, b, tol=1e-6):
    assert abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def test_closed_forms_unit_variance():
    graphs = [
        edge_graph(),
        matching_graph(5),
        clique_graph(8),
        star_graph(9),
        complete_bipartite_graph(3, 7),
    ]
    for graph in graphs:
        primal = solve_psi(graph, np.ones(graph.n))
        expected = exact_unit_variance_psi(graph)
        assert primal.success
        assert primal.max_constraint_violation < 1e-7
        assert expected is not None
        assert_close(primal.objective, expected, 1e-5)


def test_primal_dual_agree():
    for graph in [star_graph(7), clique_graph(6), complete_bipartite_graph(2, 5)]:
        variances = np.linspace(0.5, 2.0, graph.n)
        primal = solve_psi(graph, variances)
        dual = solve_psi_dual(graph, variances)
        assert primal.success
        assert dual.success
        assert_close(primal.objective, dual.objective, 2e-5)


def test_homogeneous_variance_scaling():
    graph = star_graph(10)
    base = solve_psi(graph, np.ones(graph.n)).objective
    for lam in [0.1, 0.5, 2.0, 10.0]:
        scaled = solve_psi(graph, np.full(graph.n, lam)).objective
        assert_close(scaled, lam * base, 1e-5)


def test_star_optimizer_shape():
    k = 16
    graph = star_graph(k)
    result = solve_psi(graph, np.ones(graph.n))
    assert_close(result.q[0], 1 + math.sqrt(k), 1e-5)
    for leaf in result.q[1:]:
        assert_close(leaf, 1 + 1 / math.sqrt(k), 1e-5)


def test_primal_solution_has_rotated_cone_certificate():
    for graph in [
        star_graph(7),
        clique_graph(6),
        complete_bipartite_graph(2, 5),
    ]:
        variances = np.linspace(0.4, 2.1, graph.n)
        primal = solve_psi(graph, variances)
        assert primal.success

        cert = psi_conic_certificate(graph, variances, primal.q)
        assert cert.incidence_weights.shape == (graph.m, 2)
        assert cert.max_edge_sum_violation < 1e-7
        assert cert.max_product_violation < 1e-10

        for (u, v), (tu, tv) in zip(graph.edges, cert.incidence_weights):
            assert 2.0 * primal.q[u] * tu + 1e-12 >= 2.0 * variances[u]
            assert 2.0 * primal.q[v] * tv + 1e-12 >= 2.0 * variances[v]
            assert tu + tv <= 1.0 + 1e-7
