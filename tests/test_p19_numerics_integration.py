"""P19 cancellation-resistant KL and normalized LP regression checks."""
import math
import numpy as np
import pytest
from tfoesuu.control_replay import control_replay_information_lower_bound
from tfoesuu.graphs import complete_bipartite_graph
from tfoesuu.p19_numerics import (
    certified_p19_information_allocation,
    stable_p19_information_rates,
)

@pytest.mark.parametrize("d", [1e-4, 1e-6, 1e-9, 1e-12])
def test_exact_mixed_control_small_effect(d):
    graph = complete_bipartite_graph(3, 2)
    lower = control_replay_information_lower_bound(
        graph, [(0, 1), (2, 3)], [1.0, 1.0], (0, 1, 2),
        p=0.2, shared_patch=0.1, fairness_tolerance=0.1,
        d=d, beta=0.05,
    )
    kc, kb = stable_p19_information_rates(0.6, 0.1, d)
    assert lower.success, lower.message
    assert lower.control_kl == pytest.approx(kc)
    assert lower.boundary_kl == pytest.approx(kb)
    assert lower.expected_cost_floor == pytest.approx(
        (1.0/kc + 1.0/kb)*math.log(19.0)*0.9, rel=1e-8
    )
    assert np.min(lower.information_matrix.T @ lower.expected_query_counts) >= (
        math.log(19.0)*0.9*(1-1e-8)
    )

def test_negative_kl_cancellation_reproducer():
    kc, kb = stable_p19_information_rates(0.6, 0.1, 1e-9)
    assert kc > 0 and kb > 0
    assert kb == pytest.approx((1e-9)**2 * (1/0.1 + 1/0.6)/2, rel=1e-7)

def test_subnormal_tolerance_no_overflow():
    kc, kb = stable_p19_information_rates(0.6, 5e-324, 1e-5)
    assert math.isfinite(kc) and math.isfinite(kb)
    assert kb > 0

def test_unobservable_alternative_fails_closed():
    sol = certified_p19_information_allocation(
        np.array([[0.1, 0.0]]), np.array([1.0]), 1.0)
    assert not sol.success and math.isinf(sol.cost)

def test_nonuniform_group_information_rejected():
    with pytest.raises(ValueError, match="identical nonzero"):
        certified_p19_information_allocation(
            np.array([[0.1, 0.1*(1+1e-12)]]), np.array([1.0]), 1.0)

def test_seeded_fractional_incidence_certificates():
    rng = np.random.default_rng(1729)
    for n in range(1, 8):
        for _ in range(75):
            g = int(rng.integers(n, 3*n+4))
            incidence = rng.integers(0, 2, size=(g, n))
            for j in range(n):
                incidence[j, j] = 1
            rates = 10.0**rng.uniform(-22, -3, size=g)
            K = incidence * rates[:, None]
            costs = 10.0**rng.uniform(-1, 1, size=g)
            sol = certified_p19_information_allocation(K, costs, 0.9*math.log(19))
            assert sol.success, sol.message
            assert sol.primal_violation <= 1e-8
            assert sol.relative_dual_violation <= 1e-8
            assert sol.relative_gap <= 1e-7
            assert np.min(K.T @ sol.counts) >= 0.9*math.log(19)*(1-1e-8)

def test_empty_information_matrix_fails_closed():
    result = certified_p19_information_allocation(
        np.empty((0, 2)), np.empty(0), 1.0
    )
    assert not result.success
    assert math.isinf(result.cost)
    assert "no informative legal replay groups" in result.message
