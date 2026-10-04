import numpy as np

from tfoesuu.graphs import edge_graph, star_graph
from tfoesuu.oracles import GaussianVersionPair
from tfoesuu.testers import gaussian_static_counts, run_gaussian_static_test


def test_counts_are_feasible_and_positive_on_active_vertices():
    graph = star_graph(5)
    counts, allocation = gaussian_static_counts(graph, np.ones(graph.n), gamma=0.5, beta=0.05)
    assert allocation.success
    assert np.all(counts > 0)


def test_obvious_alternative_rejects_with_fixed_seed():
    graph = edge_graph()
    oracle = GaussianVersionPair.from_sequences(
        mu0=[0.0, 0.0],
        mu1=[2.0, -2.0],
        sigma0=1.0,
        sigma1=1.0,
        rho=0.9,
    )
    out = run_gaussian_static_test(graph, oracle, gamma=0.5, beta=0.01, seed=42, paired=True)
    assert out.reject
