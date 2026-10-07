from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Mapping, Sequence

import numpy as np

from .certificate import prune_with_patch_envelopes
from .graphs import Edge, GraphSpec
from .partial_replay_lower import active_vertex_contrast_schedule
from .separations import (
    counterfactual_replay_bounds,
    replay_separation_bounds,
    threshold_fairness_replay_bounds,
)
from .suite_replay import synchronized_suite_replay_bounds
from .testers import gaussian_static_counts


ReplayMode = Literal[
    "vertex-paired-one-edge",
    "four-way-one-edge",
    "four-way-thresholded-one-edge",
    "suite-homogeneous",
    "partial-homogeneous",
]


@dataclass(frozen=True)
class TFOESUUPlan:
    """Theorem-backed execution plan for one frozen access model.

    This object is deliberately a planning artifact, not a generic guarantee
    wrapper.  Each constructor below rejects requests that fall outside the
    theorem scope encoded in the repository.
    """

    mode: str
    theorem_scope: str
    safe_edges: tuple[Edge, ...]
    residual_edges: tuple[Edge, ...]
    rounds: int | None
    concrete_program_executions: int | None
    vertex_counts: tuple[int, ...] | None
    group_counts: tuple[int, ...] | None
    normalized_geometry: float | None
    notes: tuple[str, ...]


def plan_gaussian_regression(
    graph: GraphSpec,
    old_edge_gaps: Mapping[Edge, float],
    thresholds: Mapping[Edge, float],
    patch_effect_bounds: Mapping[Edge, float],
    variances: Sequence[float],
    gamma: float,
    beta: float,
) -> TFOESUUPlan:
    """Plan the proved envelope-pruned Gaussian regression tester."""

    pruning = prune_with_patch_envelopes(
        graph,
        old_edge_gaps,
        thresholds,
        patch_effect_bounds,
    )
    residual = pruning.residual_graph
    variance = np.asarray(variances, dtype=float)
    counts, allocation = gaussian_static_counts(
        residual,
        variance,
        gamma,
        beta,
    )
    if not allocation.success or allocation.max_constraint_violation > 1e-7:
        raise RuntimeError(
            f"Gaussian allocation failed: {allocation.message}"
        )

    paired_calls = int(counts.sum())
    return TFOESUUPlan(
        mode="gaussian-paired-regression",
        theorem_scope=(
            "P14 envelope-pruned Gaussian separated-threshold regression"
        ),
        safe_edges=pruning.safe_edges,
        residual_edges=residual.edges,
        rounds=None,
        concrete_program_executions=2 * paired_calls,
        vertex_counts=tuple(int(x) for x in counts),
        group_counts=None,
        normalized_geometry=float(allocation.objective),
        notes=(
            "Each paired-oracle call executes P0 and P1 once.",
            "Patch-effect envelopes must be sound; the planner cannot infer soundness.",
        ),
    )


def plan_bernoulli_replay(
    graph: GraphSpec,
    mode: ReplayMode,
    *,
    p: float,
    d: float,
    beta: float,
    shared_patch: float = 0.0,
    fairness_tolerance: float = 0.0,
    groups: Iterable[Iterable[int]] | None = None,
    costs: Sequence[float] | None = None,
    homogeneous_single_changed_endpoint: bool = False,
) -> TFOESUUPlan:
    """Plan one proved Bernoulli replay schedule and fail closed otherwise."""

    if graph.m == 0:
        return TFOESUUPlan(
            mode=mode,
            theorem_scope="edgeless graph",
            safe_edges=(),
            residual_edges=(),
            rounds=0,
            concrete_program_executions=0,
            vertex_counts=None,
            group_counts=None,
            normalized_geometry=0.0,
            notes=("No fairness edges require stochastic testing.",),
        )

    if mode == "vertex-paired-one-edge":
        if graph.m != 1:
            raise ValueError(
                "P12 vertex-paired planner is restricted to the one-edge theorem"
            )
        if shared_patch != 0.0:
            raise ValueError(
                "vertex-paired-one-edge uses the P12 zero-common-patch family; "
                "use four-way-one-edge for the P15 common-patch comparison"
            )
        bounds = replay_separation_bounds(p, d, beta)
        rounds = bounds.paired_upper_rounds
        return TFOESUUPlan(
            mode=mode,
            theorem_scope="P12 one-edge common-uniform old/new replay",
            safe_edges=(),
            residual_edges=graph.edges,
            rounds=rounds,
            concrete_program_executions=2 * rounds,
            vertex_counts=None,
            group_counts=None,
            normalized_geometry=None,
            notes=(
                "The schedule is the proved one-edge paired upper construction.",
            ),
        )

    if mode == "four-way-one-edge":
        if graph.m != 1:
            raise ValueError(
                "P15 four-way planner is restricted to the one-edge theorem"
            )
        bounds = counterfactual_replay_bounds(
            p,
            shared_patch,
            d,
            beta,
        )
        rounds = bounds.edge_coupled_upper_rounds
        return TFOESUUPlan(
            mode=mode,
            theorem_scope="P15 one-edge four-way counterfactual replay",
            safe_edges=(),
            residual_edges=graph.edges,
            rounds=rounds,
            concrete_program_executions=4 * rounds,
            vertex_counts=None,
            group_counts=None,
            normalized_geometry=None,
            notes=(
                "Each replay round executes two versions at both fairness endpoints.",
            ),
        )

    if mode == "four-way-thresholded-one-edge":
        if graph.m != 1:
            raise ValueError(
                "P18 thresholded replay planner is restricted to the one-edge theorem"
            )
        bounds = threshold_fairness_replay_bounds(
            p,
            shared_patch,
            fairness_tolerance,
            d,
            beta,
        )
        return TFOESUUPlan(
            mode=mode,
            theorem_scope="P18 one-edge thresholded four-way replay",
            safe_edges=(),
            residual_edges=graph.edges,
            rounds=bounds.replay_upper_rounds,
            concrete_program_executions=(
                bounds.replay_upper_concrete_executions
            ),
            vertex_counts=None,
            group_counts=None,
            normalized_geometry=None,
            notes=(
                "Complexity interpolates with the allowed fairness tolerance.",
                "The proved phase transition is scoped to one threshold-Bernoulli edge.",
            ),
        )

    if mode == "suite-homogeneous":
        bounds = synchronized_suite_replay_bounds(
            graph,
            p,
            shared_patch,
            d,
            beta,
        )
        return TFOESUUPlan(
            mode=mode,
            theorem_scope="P16 homogeneous synchronized-suite family",
            safe_edges=(),
            residual_edges=graph.edges,
            rounds=bounds.replay_rounds_upper,
            concrete_program_executions=bounds.concrete_executions_upper,
            vertex_counts=None,
            group_counts=None,
            normalized_geometry=float(bounds.active_vertices),
            notes=(
                "One tape is shared across both versions at every active vertex.",
                "Round complexity is independent of fairness-edge count only in the audited family.",
            ),
        )

    if mode == "partial-homogeneous":
        if not (
            0.0 < p < 1.0
            and 0.0 < shared_patch < 1.0 - p
            and 0.0 < d < 1.0 - p - shared_patch
        ):
            raise ValueError(
                "partial-homogeneous requires p>0, shared_patch>0, d>0, "
                "and p+shared_patch+d<1"
            )
        if not homogeneous_single_changed_endpoint:
            raise ValueError(
                "P17 partial raw-contrast scheduling requires explicit acknowledgement "
                "of the homogeneous single-changed-endpoint theorem scope"
            )
        if groups is None or costs is None:
            raise ValueError(
                "partial-homogeneous planning requires legal replay groups and costs"
            )
        group_list = tuple(tuple(int(v) for v in group) for group in groups)
        schedule = active_vertex_contrast_schedule(
            graph,
            group_list,
            costs,
            d=d,
            beta=beta,
        )
        executions = 0
        for count, group in zip(schedule.counts, group_list):
            executions += 2 * int(count) * len(group)
        return TFOESUUPlan(
            mode=mode,
            theorem_scope=(
                "P17 homogeneous single-changed-endpoint active-vertex contrast"
            ),
            safe_edges=(),
            residual_edges=graph.edges,
            rounds=int(schedule.counts.sum()),
            concrete_program_executions=executions,
            vertex_counts=None,
            group_counts=tuple(int(x) for x in schedule.counts),
            normalized_geometry=float(
                schedule.normalized_fractional_cost
            ),
            notes=(
                "Do not use this plan for heterogeneous/composite fairness-preserving nulls.",
                "Group-query costs and concrete program executions are distinct accounting units.",
            ),
        )

    raise ValueError(f"unsupported replay mode: {mode}")
