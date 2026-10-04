from __future__ import annotations

from dataclasses import dataclass
import math

from .graphs import GraphSpec
from .separations import binary_decision_kl


@dataclass(frozen=True)
class SuiteReplayBounds:
    """Finite-sample bounds for synchronized suite replay on a fairness graph."""

    active_vertices: int
    replay_rounds_upper: int
    concrete_executions_upper: int
    null_expected_rounds_lower: float
    null_expected_concrete_executions_lower: float
    per_round_kl: float


def active_vertex_count(graph: GraphSpec) -> int:
    """Number of vertices incident to at least one fairness edge."""

    return len({v for edge in graph.edges for v in edge})


def synchronized_suite_replay_bounds(
    graph: GraphSpec,
    p: float,
    s: float,
    d: float,
    beta: float,
) -> SuiteReplayBounds:
    """Bounds for a one-unknown-edge differential under synchronized suite replay.

    Null:
      every active vertex has old threshold p and new threshold p+s.

    Alternative:
      one endpoint of one fairness edge receives an additional differential d.

    One suite-replay round draws one uniform tape and executes both software
    versions on every active vertex.  It therefore costs 2*n_active concrete
    program executions and exposes every edge differential simultaneously.
    """

    if graph.m < 1:
        return SuiteReplayBounds(0, 0, 0, 0.0, 0.0, 0.0)
    if not (0.0 < p < 1.0):
        raise ValueError("p must lie in (0,1)")
    if not (0.0 < s < 1.0 - p):
        raise ValueError("s must lie in (0,1-p)")
    if not (0.0 < d < 1.0 - p - s):
        raise ValueError("d must lie in (0,1-p-s)")
    if not (0.0 < beta < 0.5):
        raise ValueError("beta must lie in (0,1/2)")

    n_active = active_vertex_count(graph)
    r = 1.0 - p - s
    per_round_kl = r * math.log(r / (r - d))
    rounds = math.ceil(math.log(beta) / math.log1p(-d))
    lower_rounds = binary_decision_kl(beta) / per_round_kl

    return SuiteReplayBounds(
        active_vertices=n_active,
        replay_rounds_upper=rounds,
        concrete_executions_upper=2 * n_active * rounds,
        null_expected_rounds_lower=lower_rounds,
        null_expected_concrete_executions_lower=2 * n_active * lower_rounds,
        per_round_kl=per_round_kl,
    )
