"""Regression tests for P17/P19 canonical replay-group execution accounting."""

import pytest

from tfoesuu.graphs import complete_bipartite_graph, path_graph
from tfoesuu.planner import plan_bernoulli_replay


def test_p17_duplicate_and_reordered_group_members_do_not_change_cost():
    graph = path_graph(3)
    canonical = ((0, 2), (1, 2))
    noncanonical = ((2, 0, 0), (2, 1, 1))
    kwargs = dict(
        p=0.20,
        shared_patch=0.10,
        d=0.05,
        beta=0.05,
        costs=(1.0, 1.0),
        homogeneous_single_changed_endpoint=True,
    )
    expected = plan_bernoulli_replay(
        graph, "partial-homogeneous", groups=canonical, **kwargs
    )
    actual = plan_bernoulli_replay(
        graph, "partial-homogeneous", groups=noncanonical, **kwargs
    )
    assert actual.group_counts == expected.group_counts
    assert actual.rounds == expected.rounds
    assert actual.normalized_geometry == pytest.approx(expected.normalized_geometry)
    assert actual.concrete_program_executions == expected.concrete_program_executions
    assert actual.concrete_program_executions == sum(
        2 * count * len(group)
        for count, group in zip(actual.group_counts, canonical)
    )


def test_p19_duplicate_and_reordered_group_members_do_not_change_cost():
    graph = complete_bipartite_graph(3, 2)
    canonical = ((0, 1), (1, 2), (0, 2))
    noncanonical = ((1, 0, 0), (2, 1, 1), (2, 0, 0))
    kwargs = dict(
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=0.01,
        beta=0.05,
        costs=(1.0, 1.0, 1.0),
        high_vertices=(0, 1, 2),
        bipartite_control_family=True,
    )
    expected = plan_bernoulli_replay(
        graph, "partial-bipartite-control", groups=canonical, **kwargs
    )
    actual = plan_bernoulli_replay(
        graph, "partial-bipartite-control", groups=noncanonical, **kwargs
    )
    assert actual.group_counts == expected.group_counts
    assert actual.rounds == expected.rounds
    assert actual.normalized_geometry == pytest.approx(expected.normalized_geometry)
    assert actual.concrete_program_executions == expected.concrete_program_executions
    assert actual.concrete_program_executions == sum(
        2 * count * len(group)
        for count, group in zip(actual.group_counts, canonical)
    )


@pytest.mark.parametrize(
    "mode",
    ["partial-homogeneous", "partial-bipartite-control"],
)
def test_group_with_only_one_unique_vertex_is_rejected(mode):
    graph = (
        path_graph(3)
        if mode == "partial-homogeneous"
        else complete_bipartite_graph(3, 2)
    )
    kwargs = (
        dict(
            p=0.20,
            shared_patch=0.10,
            d=0.05,
            beta=0.05,
            homogeneous_single_changed_endpoint=True,
        )
        if mode == "partial-homogeneous"
        else dict(
            p=0.20,
            shared_patch=0.10,
            fairness_tolerance=0.10,
            d=0.01,
            beta=0.05,
            high_vertices=(0, 1, 2),
            bipartite_control_family=True,
        )
    )
    with pytest.raises(ValueError, match="at least two vertices"):
        plan_bernoulli_replay(
            graph,
            mode,
            groups=((0, 0), (1, 2)),
            costs=(1.0, 1.0),
            **kwargs,
        )
