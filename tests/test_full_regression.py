import numpy as np

from tfoesuu.graphs import matching_graph
from tfoesuu.oracles import GaussianVersionPair
from tfoesuu.testers import run_gaussian_full_regression_test


def test_full_regression_uses_zero_samples_when_all_edges_pruned():
    graph = matching_graph(2)
    old = {edge: 0.0 for edge in graph.edges}
    tau = {edge: 0.20 for edge in graph.edges}
    bound = {edge: 0.05 for edge in graph.edges}

    oracle = GaussianVersionPair.from_sequences(
        mu0=[0.0] * graph.n,
        mu1=[0.01, 0.0, 0.0, 0.0],
        sigma0=1.0,
        sigma1=1.0,
        rho=0.9,
    )
    out = run_gaussian_full_regression_test(
        graph,
        oracle,
        old,
        tau,
        bound,
        gamma=0.05,
        beta=0.05,
        seed=7,
    )
    assert not out.reject
    assert out.residual_edges == ()
    assert int(np.sum(out.sample_counts)) == 0


def test_full_regression_detects_obvious_residual_violation():
    graph = matching_graph(1)
    edge = graph.edges[0]
    old = {edge: 0.0}
    tau = {edge: 0.10}
    bound = {edge: 1.0}

    oracle = GaussianVersionPair.from_sequences(
        mu0=[0.0, 0.0],
        mu1=[1.0, -1.0],
        sigma0=1.0,
        sigma1=1.0,
        rho=0.95,
    )
    out = run_gaussian_full_regression_test(
        graph,
        oracle,
        old,
        tau,
        bound,
        gamma=0.20,
        beta=0.01,
        seed=42,
    )
    assert out.reject
    assert out.residual_edges == (edge,)
    assert int(np.sum(out.sample_counts)) > 0


def test_pruning_reduces_sampled_vertex_set():
    graph = matching_graph(3)
    old = {edge: 0.0 for edge in graph.edges}
    tau = {edge: 0.10 for edge in graph.edges}
    bound = {
        graph.edges[0]: 0.0,
        graph.edges[1]: 0.0,
        graph.edges[2]: 0.30,
    }

    oracle = GaussianVersionPair.from_sequences(
        mu0=[0.0] * graph.n,
        mu1=[0.0] * graph.n,
        sigma0=1.0,
        sigma1=1.0,
        rho=0.5,
    )
    out = run_gaussian_full_regression_test(
        graph,
        oracle,
        old,
        tau,
        bound,
        gamma=0.10,
        beta=0.05,
        seed=3,
    )
    active = set(np.flatnonzero(out.sample_counts))
    assert active == set(graph.edges[2])



def test_full_regression_skips_promise_gap_edge_without_calling_it_safe():
    graph = matching_graph(1)
    edge = graph.edges[0]
    old = {edge: 0.0}
    tau = {edge: 0.10}
    bound = {edge: 0.15}

    oracle = GaussianVersionPair.from_sequences(
        mu0=[0.0, 0.0],
        mu1=[0.0, 0.0],
        sigma0=1.0,
        sigma1=1.0,
        rho=0.5,
    )
    out = run_gaussian_full_regression_test(
        graph,
        oracle,
        old,
        tau,
        bound,
        gamma=0.10,
        beta=0.05,
        seed=11,
    )

    assert not out.reject
    assert out.safe_edges == ()
    assert out.promise_gap_edges == (edge,)
    assert out.residual_edges == ()
    assert int(np.sum(out.sample_counts)) == 0


def test_full_regression_keeps_exact_alternative_boundary():
    graph = matching_graph(1)
    edge = graph.edges[0]
    old = {edge: 0.0}
    tau = {edge: 0.10}
    bound = {edge: 0.20}

    oracle = GaussianVersionPair.from_sequences(
        mu0=[0.0, 0.0],
        mu1=[0.0, 0.0],
        sigma0=1.0,
        sigma1=1.0,
        rho=0.5,
    )
    out = run_gaussian_full_regression_test(
        graph,
        oracle,
        old,
        tau,
        bound,
        gamma=0.10,
        beta=0.05,
        seed=13,
    )

    assert out.promise_gap_edges == ()
    assert out.residual_edges == (edge,)
    assert int(np.sum(out.sample_counts)) > 0
