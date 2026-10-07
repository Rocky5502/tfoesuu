from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class ReplayInformationSolution:
    """Minimum-cost allocation for an action-by-alternative information matrix.

    Rows of information are legal replay actions. Columns are alternatives
    that must each accumulate a required amount of information. This is a generic
    optimization primitive only; theorem-level meaning depends on how the
    information coefficients are derived for a frozen statistical model.
    """

    cost: float
    action_weights: np.ndarray
    achieved_information: np.ndarray
    success: bool
    message: str


def minimum_information_cover(
    information: Sequence[Sequence[float]],
    costs: Sequence[float],
    requirements: Sequence[float],
) -> ReplayInformationSolution:
    """Solve min c^T x subject to I^T x >= b and x >= 0.

    This routine intentionally makes no claim that KL information is additive
    for an arbitrary adaptive experiment. It is only a reusable LP primitive
    for models where a proof/audit has justified linear information constraints.
    """

    I = np.asarray(information, dtype=float)
    c = np.asarray(costs, dtype=float)
    b = np.asarray(requirements, dtype=float)

    if I.ndim != 2:
        raise ValueError("information must be a 2D action-by-alternative matrix")
    n_actions, n_alternatives = I.shape
    if c.shape != (n_actions,):
        raise ValueError("costs must have one entry per action")
    if b.shape != (n_alternatives,):
        raise ValueError("requirements must have one entry per alternative")
    if np.any(~np.isfinite(I)) or np.any(I < 0):
        raise ValueError("information coefficients must be finite and nonnegative")
    if np.any(~np.isfinite(c)) or np.any(c <= 0):
        raise ValueError("costs must be finite and strictly positive")
    if np.any(~np.isfinite(b)) or np.any(b < 0):
        raise ValueError("requirements must be finite and nonnegative")

    if n_alternatives == 0:
        return ReplayInformationSolution(
            0.0, np.zeros(n_actions), np.zeros(0), True, "no alternatives"
        )

    positive = b > 0
    if np.any(positive & (I.sum(axis=0) <= 0)):
        return ReplayInformationSolution(
            float("inf"),
            np.zeros(n_actions),
            np.zeros(n_alternatives),
            False,
            "some required alternative receives zero information from every action",
        )

    res = linprog(
        c,
        A_ub=-I.T,
        b_ub=-b,
        bounds=[(0.0, None)] * n_actions,
        method="highs",
    )
    if not res.success:
        return ReplayInformationSolution(
            float("inf"),
            np.zeros(n_actions),
            np.zeros(n_alternatives),
            False,
            str(res.message),
        )

    weights = np.asarray(res.x, dtype=float)
    achieved = I.T @ weights
    return ReplayInformationSolution(
        float(c @ weights), weights, achieved, True, str(res.message)
    )
