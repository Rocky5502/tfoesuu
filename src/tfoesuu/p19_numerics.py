from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class CertifiedP19Allocation:
    cost: float
    counts: np.ndarray
    success: bool
    message: str
    primal_violation: float
    relative_dual_violation: float
    relative_gap: float


def _positive_log1p_remainder(x: float) -> float:
    """Return x-log(1+x), avoiding cancellation when x is tiny."""
    if x < 1e-3:
        return x*x*(0.5 + x*(-1.0/3.0 + x*(0.25 + x*(-0.2 + x*(1.0/6.0 + x*(-1.0/7.0 + x/8.0))))))
    return x - math.log1p(x)


def _negative_log1p_remainder(x: float) -> float:
    """Return -log(1-x)-x for 0<x<1, without subtracting tiny terms."""
    if x < 1e-3:
        return x*x*(0.5 + x*(1.0/3.0 + x*(0.25 + x*(0.2 + x*(1.0/6.0 + x*(1.0/7.0 + x/8.0))))))
    return -math.log1p(-x) - x


def stable_p19_information_rates(r: float, tau: float, d: float) -> tuple[float, float]:
    """Null-to-alternative transcript KL for matched controls and boundaries."""
    if not (math.isfinite(r) and math.isfinite(tau) and math.isfinite(d)
            and r > 0 and tau >= 0 and 0 < d < r):
        raise ValueError("require finite r>0, tau>=0 and 0<d<r")
    control = -r * math.log1p(-d/r)
    if tau == 0:
        return control, control
    ratio = d / tau
    if math.isinf(ratio):
        # The limit tau -> 0 is continuous. Avoid inf * tau for subnormal tau.
        positive_part = d - tau * (
            math.log(d) - math.log(tau) + math.log1p(tau / d)
        )
    else:
        positive_part = tau * _positive_log1p_remainder(ratio)
    boundary = positive_part + r * _negative_log1p_remainder(d/r)
    if not (math.isfinite(boundary) and boundary > 0):
        raise ArithmeticError("boundary KL underflowed or became nonfinite")
    return control, boundary


def certified_p19_information_allocation(
    information: np.ndarray, costs: np.ndarray, target: float,
) -> CertifiedP19Allocation:
    """Solve the P19 single-nuisance information LP in normalized cover coordinates.

    Each legal group carries the same nonzero KL for every high candidate it
    contains. Setting z_g = K_g q_g / target reduces the constraint matrix to
    binary incidence. Reject solver output without a primal-dual certificate.
    """
    K = np.asarray(information, dtype=float)
    c = np.asarray(costs, dtype=float)
    if (K.ndim != 2 or K.shape[1] == 0 or c.shape != (K.shape[0],)
            or np.any(~np.isfinite(K)) or np.any(K < 0)
            or np.any(~np.isfinite(c)) or np.any(c <= 0)
            or not math.isfinite(target) or target <= 0):
        raise ValueError("invalid P19 information matrix, costs, or target")
    zero = np.zeros(len(c))
    if np.any(np.max(K, axis=0) == 0):
        return CertifiedP19Allocation(float("inf"), zero, False,
            "some alternative has no informative legal group", float("inf"), float("inf"), float("inf"))
    active = np.flatnonzero(np.max(K, axis=1) > 0)
    h = np.max(K[active], axis=1)
    # Exact within-row equality is a structural premise of the binary-cover
    # reduction, not a numerical tolerance: accepting an almost-equal row
    # would certify the wrong optimization problem.
    if np.any((K[active] > 0) & (K[active] != h[:, None])):
        raise ValueError("P19 requires identical nonzero information within each group")
    A = (K[active] > 0).astype(float).T
    per_unit = c[active] / h
    if np.any(~np.isfinite(per_unit)):
        return CertifiedP19Allocation(float("inf"), zero, False,
            "P19 normalized costs overflowed", float("inf"), float("inf"), float("inf"))
    scale = float(per_unit.min())
    weights = per_unit / scale
    if np.any(~np.isfinite(weights)):
        return CertifiedP19Allocation(float("inf"), zero, False,
            "P19 relative normalized costs overflowed", float("inf"), float("inf"), float("inf"))
    result = linprog(weights, A_ub=-A, b_ub=-np.ones(K.shape[1]),
                     bounds=[(0.0, None)] * len(active), method="highs")
    if not result.success:
        return CertifiedP19Allocation(float("inf"), zero, False, str(result.message),
            float("inf"), float("inf"), float("inf"))
    z = np.asarray(result.x)
    dual = -np.asarray(result.ineqlin.marginals)
    primal_violation = float(max(0.0, 1.0 - np.min(A @ z), -np.min(z)))
    dual_violation = float(max(0.0, -np.min(dual),
        np.max((A.T @ dual - weights) / np.maximum(1.0, weights))))
    objective = float(weights @ z)
    gap = float(abs(objective - np.sum(dual)) / max(1.0, abs(objective)))
    counts = zero.copy()
    counts[active] = target * z / h
    cost = float(c @ counts)
    original_information = K.T @ counts
    certified = (primal_violation <= 1e-8 and dual_violation <= 1e-8
                 and gap <= 1e-7 and np.all(np.isfinite(counts))
                 and math.isfinite(cost) and
                 np.min(original_information) >= target * (1.0 - 1e-8))
    if not certified:
        return CertifiedP19Allocation(float("inf"), zero, False,
            f"P19 LP primal-dual certificate failed: primal={primal_violation:.3g}, "
            f"dual={dual_violation:.3g}, gap={gap:.3g}",
            primal_violation, dual_violation, gap)
    return CertifiedP19Allocation(cost, counts, True,
        "certified normalized P19 fractional information cover",
        primal_violation, dual_violation, gap)
