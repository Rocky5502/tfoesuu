import pytest

from tfoesuu.separations import (
    counterfactual_replay_bounds,
    edge_coupled_common_patch_kl,
    vertex_paired_common_patch_kl,
)


def test_counterfactual_replay_small_d_exponents():
    p, s, beta = 0.35, 0.20, 0.05
    d1, d2 = 1e-4, 5e-5

    e_ratio = (
        edge_coupled_common_patch_kl(p, s, d1)
        / edge_coupled_common_patch_kl(p, s, d2)
    )
    v_ratio = (
        vertex_paired_common_patch_kl(p, s, d1)
        / vertex_paired_common_patch_kl(p, s, d2)
    )

    assert e_ratio == pytest.approx(2.0, rel=5e-4)
    assert v_ratio == pytest.approx(4.0, rel=2e-3)


def test_edge_coupled_exact_upper_miss():
    b = counterfactual_replay_bounds(0.3, 0.2, 0.01, 0.05)
    n = b.edge_coupled_upper_rounds
    assert (1.0 - 0.01) ** n <= 0.05
    if n > 1:
        assert (1.0 - 0.01) ** (n - 1) > 0.05


def test_four_way_replay_beats_vertex_pairing_for_small_d():
    b = counterfactual_replay_bounds(0.3, 0.2, 0.005, 0.05)
    assert b.edge_coupled_upper_rounds < b.vertex_paired_upper_rounds
    assert b.edge_coupled_null_expected_lower < b.vertex_paired_null_expected_lower


def test_common_patch_parameter_validation():
    with pytest.raises(ValueError):
        counterfactual_replay_bounds(0.4, 0.0, 0.01, 0.05)
    with pytest.raises(ValueError):
        counterfactual_replay_bounds(0.7, 0.2, 0.11, 0.05)
