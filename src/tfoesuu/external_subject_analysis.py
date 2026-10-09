from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class BernoulliDisagreementLaws:
    """Exact disagreement probabilities for two Bernoulli marginals."""

    common_uniform: NDArray[np.float64]
    independent: NDArray[np.float64]


def bernoulli_disagreement_laws(
    old: Sequence[float] | NDArray[np.float64],
    new: Sequence[float] | NDArray[np.float64],
) -> BernoulliDisagreementLaws:
    """Return exact per-row disagreement laws under paired and fresh tapes.

    Common-uniform thresholding disagrees with probability ``abs(old-new)``.
    Independent Bernoulli draws disagree with probability
    ``old*(1-new) + (1-old)*new``. These are distributional identities, not
    Monte Carlo estimates.
    """

    p = np.asarray(old, dtype=float)
    q = np.asarray(new, dtype=float)
    if p.shape != q.shape:
        raise ValueError("old and new probabilities must have the same shape")
    if p.ndim != 1:
        raise ValueError("probabilities must be one-dimensional")
    if not np.all(np.isfinite(p)) or not np.all(np.isfinite(q)):
        raise ValueError("probabilities must be finite")
    if np.any((p < 0.0) | (p > 1.0)) or np.any((q < 0.0) | (q > 1.0)):
        raise ValueError("probabilities must lie in [0, 1]")
    return BernoulliDisagreementLaws(
        common_uniform=np.abs(p - q),
        independent=p * (1.0 - q) + (1.0 - p) * q,
    )
