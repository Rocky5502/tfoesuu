"""Finite-nuisance information-cover audit for P20 (not a testing theorem).

A nuisance parameter is fixed across all observations in one experiment.
It must not be minimized independently for each replay action.  This module
compares pointwise-null information floors with a single fixed allocation
meeting all *necessary* information inequalities on a finite nuisance grid.

A KL budget alone is not a sufficient hypothesis-test construction.  In
particular, the shared-allocation LP is NOT an adaptive minimax lower bound
or an achievability certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .replay_information import ReplayInformationSolution, minimum_information_cover


@dataclass(frozen=True)
class FiniteNuisanceInformationAudit:
    """Compare nuisance-dependent floors with a shared fixed information cover."""

    pointwise_solutions: tuple[ReplayInformationSolution, ...]
    worst_pointwise_cost: float
    shared_fixed_information_solution: ReplayInformationSolution
    shared_to_pointwise_ratio: float


def audit_finite_nuisance_information(
    information: Sequence[Sequence[Sequence[float]]],
    costs: Sequence[float],
    requirements: Sequence[float],
) -> FiniteNuisanceInformationAudit:
    """Audit an array shaped (nuisance, action, alternative).

    For a correctly specified sequential test, and an exact null/alternative
    action KL matrix for each fixed nuisance eta, transcript KL implies
    E_{0,eta}[cost] >= minimum_information_cover(I_eta, costs, requirements).
    This is conditional on the test's risk bounds and the transcript
    change-of-measure assumptions.

    Taking the maximum of these floors is a necessary uniform-null cost
    bound.  The *single shared* allocation LP instead applies the same x to
    every nuisance and alternative.  Its objective is a fixed-design
    information-budget calculation only: neither an adaptive lower bound nor
    a sufficient finite-sample testing guarantee.

    Nuisance scenarios are fixed globally, never separately per action.
    """

    I = np.asarray(information, dtype=float)
    if I.ndim != 3 or I.shape[0] == 0:
        raise ValueError(
            "information must have shape (positive nuisance count, actions, alternatives)"
        )
    n_nuisance, n_actions, n_alternatives = I.shape
    c = np.asarray(costs, dtype=float)
    b = np.asarray(requirements, dtype=float)
    if c.shape != (n_actions,):
        raise ValueError("costs must have one entry per action")
    if b.shape != (n_alternatives,):
        raise ValueError("requirements must have one entry per alternative")
    if not np.all(np.isfinite(I)) or np.any(I < 0.0):
        raise ValueError("information coefficients must be finite and nonnegative")
    if not np.all(np.isfinite(c)) or np.any(c <= 0.0):
        raise ValueError("costs must be finite and strictly positive")
    if not np.all(np.isfinite(b)) or np.any(b < 0.0):
        raise ValueError("requirements must be finite and nonnegative")

    pointwise = tuple(
        minimum_information_cover(I[j], c, b) for j in range(n_nuisance)
    )
    worst_pointwise = max(sol.cost for sol in pointwise)

    # Each (eta, alternative) is a separate constraint, but every row of
    # the flattened matrix refers to the SAME action allocation variable.
    shared_matrix = I.transpose(1, 0, 2).reshape(
        n_actions, n_nuisance * n_alternatives
    )
    shared = minimum_information_cover(
        shared_matrix, c, np.tile(b, n_nuisance)
    )
    if np.isfinite(worst_pointwise) and worst_pointwise > 0.0:
        ratio = shared.cost / worst_pointwise
    elif worst_pointwise == 0.0 and shared.cost == 0.0:
        ratio = 1.0
    else:
        ratio = float("nan")

    return FiniteNuisanceInformationAudit(
        pointwise_solutions=pointwise,
        worst_pointwise_cost=float(worst_pointwise),
        shared_fixed_information_solution=shared,
        shared_to_pointwise_ratio=float(ratio),
    )
