import math

import numpy as np
import pytest

from tfoesuu.graphs import complete_bipartite_graph, edge_graph, path_graph
from tfoesuu.planner import plan_bernoulli_replay, plan_gaussian_regression


def test_gaussian_planner_prunes_safe_edge_to_zero_executions():
    graph = edge_graph()
    edge = graph.edges[0]

    plan = plan_gaussian_regression(
        graph,
        old_edge_gaps={edge: 0.02},
        thresholds={edge: 0.20},
        patch_effect_bounds={edge: 0.10},
        variances=np.ones(graph.n),
        gamma=0.10,
        beta=0.05,
    )

    assert plan.safe_edges == (edge,)
    assert plan.residual_edges == ()
    assert plan.concrete_program_executions == 0
    assert plan.vertex_counts == (0, 0)


def test_one_edge_replay_plans_keep_theorem_scope_explicit():
    graph = edge_graph()

    paired = plan_bernoulli_replay(
        graph,
        "vertex-paired-one-edge",
        p=0.50,
        d=0.05,
        beta=0.05,
    )
    assert paired.rounds is not None and paired.rounds > 0
    assert paired.concrete_program_executions == 2 * paired.rounds
    assert "P12" in paired.theorem_scope

    four_way = plan_bernoulli_replay(
        graph,
        "four-way-one-edge",
        p=0.35,
        shared_patch=0.20,
        d=0.05,
        beta=0.05,
    )
    assert four_way.rounds is not None and four_way.rounds > 0
    assert four_way.concrete_program_executions == 4 * four_way.rounds
    assert "P15" in four_way.theorem_scope


def test_one_edge_modes_reject_multiedge_generalization():
    graph = path_graph(3)

    with pytest.raises(ValueError, match="one-edge theorem"):
        plan_bernoulli_replay(
            graph,
            "vertex-paired-one-edge",
            p=0.50,
            d=0.05,
            beta=0.05,
        )

    with pytest.raises(ValueError, match="one-edge theorem"):
        plan_bernoulli_replay(
            graph,
            "four-way-one-edge",
            p=0.35,
            shared_patch=0.20,
            d=0.05,
            beta=0.05,
        )


def test_suite_plan_counts_active_vertex_executions():
    graph = path_graph(3)
    plan = plan_bernoulli_replay(
        graph,
        "suite-homogeneous",
        p=0.30,
        shared_patch=0.10,
        d=0.05,
        beta=0.05,
    )

    assert plan.rounds is not None and plan.rounds > 0
    assert plan.concrete_program_executions == 2 * 3 * plan.rounds
    assert plan.normalized_geometry == pytest.approx(3.0)
    assert "P16" in plan.theorem_scope


def test_partial_plan_requires_explicit_homogeneous_scope_acknowledgement():
    graph = path_graph(3)
    groups = [(0, 2), (1, 2)]
    costs = [1.0, 1.0]

    with pytest.raises(ValueError, match="explicit acknowledgement"):
        plan_bernoulli_replay(
            graph,
            "partial-homogeneous",
            p=0.20,
            shared_patch=0.10,
            d=0.05,
            beta=0.05,
            groups=groups,
            costs=costs,
        )

    plan = plan_bernoulli_replay(
        graph,
        "partial-homogeneous",
        p=0.20,
        shared_patch=0.10,
        d=0.05,
        beta=0.05,
        groups=groups,
        costs=costs,
        homogeneous_single_changed_endpoint=True,
    )

    assert plan.group_counts is not None
    assert plan.normalized_geometry == pytest.approx(2.0)
    assert plan.concrete_program_executions is not None
    assert plan.concrete_program_executions > 0
    assert "P17" in plan.theorem_scope


def test_partial_plan_rejects_invalid_homogeneous_parameters():
    graph = path_graph(3)
    with pytest.raises(ValueError, match=r"p\+shared_patch\+d<1"):
        plan_bernoulli_replay(
            graph,
            "partial-homogeneous",
            p=0.80,
            shared_patch=0.15,
            d=0.10,
            beta=0.05,
            groups=[(0, 2), (1, 2)],
            costs=[1.0, 1.0],
            homogeneous_single_changed_endpoint=True,
        )


def test_thresholded_four_way_plan_tracks_p18_and_execution_cost():
    graph = edge_graph()
    plan = plan_bernoulli_replay(
        graph,
        "four-way-thresholded-one-edge",
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=0.01,
        beta=0.05,
    )

    assert "P18" in plan.theorem_scope
    assert plan.rounds is not None and plan.rounds > 0
    assert plan.concrete_program_executions == 4 * plan.rounds


def test_thresholded_four_way_plan_rejects_multiedge_scope():
    with pytest.raises(ValueError, match="P18.*one-edge"):
        plan_bernoulli_replay(
            path_graph(3),
            "four-way-thresholded-one-edge",
            p=0.20,
            shared_patch=0.10,
            fairness_tolerance=0.10,
            d=0.01,
            beta=0.05,
        )


def test_p19_control_plan_requires_explicit_scope_and_tracks_execution_cost():
    graph = complete_bipartite_graph(3, 2)
    groups = [(0, 1), (1, 2), (0, 2)]
    costs = [1.0, 1.0, 1.0]

    with pytest.raises(ValueError, match="explicit acknowledgement"):
        plan_bernoulli_replay(
            graph,
            "partial-bipartite-control",
            p=0.20,
            shared_patch=0.10,
            fairness_tolerance=0.10,
            d=0.01,
            beta=0.05,
            groups=groups,
            costs=costs,
            high_vertices=(0, 1, 2),
        )

    plan = plan_bernoulli_replay(
        graph,
        "partial-bipartite-control",
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=0.01,
        beta=0.05,
        groups=groups,
        costs=costs,
        high_vertices=(0, 1, 2),
        bipartite_control_family=True,
    )

    assert "P19" in plan.theorem_scope
    assert plan.normalized_geometry == pytest.approx(1.5)
    assert plan.group_counts is not None
    expected = sum(
        2 * count * len(group)
        for count, group in zip(plan.group_counts, groups)
    )
    assert plan.concrete_program_executions == expected



def test_p19_planner_uses_boundary_tests_without_matched_controls():
    graph = complete_bipartite_graph(3, 2)
    # Every legal group contains exactly one high vertex, so the hybrid planner
    # must use the proved quadratic P18 boundary block rather than manufacture
    # a linear matched-control schedule.
    groups = [(0, 3), (1, 3), (2, 4)]
    costs = [1.0, 1.0, 1.0]

    plan = plan_bernoulli_replay(
        graph,
        "partial-bipartite-control",
        p=0.20,
        shared_patch=0.10,
        fairness_tolerance=0.10,
        d=0.01,
        beta=0.05,
        groups=groups,
        costs=costs,
        high_vertices=(0, 1, 2),
        bipartite_control_family=True,
    )

    expected_rounds_per_group = math.ceil(
        8.0 * 0.11 * math.log(3.0 / 0.05) / (0.01**2)
    )
    assert plan.group_counts == (expected_rounds_per_group,) * 3
    assert plan.normalized_geometry is None
    assert plan.rounds == 3 * expected_rounds_per_group

def test_p19_control_plan_rejects_nonpositive_tolerance():
    graph = complete_bipartite_graph(2, 1)
    with pytest.raises(ValueError, match="tau>0"):
        plan_bernoulli_replay(
            graph,
            "partial-bipartite-control",
            p=0.20,
            shared_patch=0.10,
            fairness_tolerance=0.0,
            d=0.01,
            beta=0.05,
            groups=[(0, 1)],
            costs=[1.0],
            high_vertices=(0, 1),
            bipartite_control_family=True,
        )
