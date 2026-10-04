import pytest

from tfoesuu.graphs import clique_graph, matching_graph, path_graph
from tfoesuu.partial_replay import (
    minimum_replay_group_cover,
    partial_synchronized_replay_upper_bound,
)


def test_edge_groups_recover_edgewise_cover():
    g = matching_graph(4)
    groups = list(g.edges)
    r = minimum_replay_group_cover(g, groups)
    assert r.success
    assert r.objective == pytest.approx(4.0)
    assert len(r.selected) == 4


def test_full_suite_group_covers_clique_once():
    g = clique_graph(8)
    r = minimum_replay_group_cover(g, [range(g.n)])
    assert r.success
    assert r.objective == pytest.approx(1.0)
    assert r.selected == (0,)


def test_overlapping_groups_choose_cheapest_valid_cover():
    g = path_graph(4)
    groups = [(0, 1, 2), (1, 2, 3), (0, 1), (2, 3)]
    r = minimum_replay_group_cover(g, groups, costs=[2.0, 2.0, 1.5, 1.5])
    assert r.success
    assert r.objective == pytest.approx(3.0)
    assert set(r.selected) == {2, 3}


def test_uncovered_edge_is_rejected():
    g = path_graph(4)
    r = minimum_replay_group_cover(g, [(0, 1), (1, 2)])
    assert not r.success
    assert r.objective == pytest.approx(float("inf"))


def test_upper_bound_uses_exact_cover_cost():
    g = clique_graph(5)
    r = partial_synchronized_replay_upper_bound(
        g, [range(g.n)], d=0.05, beta=0.01, costs=[10.0]
    )
    assert r.cover_cost_per_round == pytest.approx(10.0)
    assert r.total_cost == pytest.approx(10.0 * r.rounds)
    assert r.rounds > 0
