from __future__ import annotations

from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass
from itertools import pairwise
from typing import TypeVar

import numpy as np

Transcript = tuple[int, ...]
T = TypeVar("T", bound=Hashable)


def common_uniform_transcript_pmf(
    thresholds: Sequence[float],
) -> dict[Transcript, float]:
    """Exact raw-output law for thresholds sharing one uniform tape.

    The returned key is the complete ordered binary output tuple. This raw
    transcript is intentionally distinct from a delta-only observation.
    """

    values = tuple(float(value) for value in thresholds)
    if not values:
        raise ValueError("at least one threshold is required")
    if any(not np.isfinite(value) or not 0.0 <= value <= 1.0 for value in values):
        raise ValueError("thresholds must be finite and lie in [0,1]")
    cuts = sorted({0.0, 1.0, *values})
    pmf: dict[Transcript, float] = {}
    for left, right in pairwise(cuts):
        mass = right - left
        if mass <= 0.0:
            continue
        probe = (left + right) / 2.0
        outcome = tuple(int(probe <= threshold) for threshold in values)
        pmf[outcome] = pmf.get(outcome, 0.0) + mass
    return pmf


def pushforward_pmf(
    pmf: dict[Transcript, float], mapping: Callable[[Transcript], T]
) -> dict[T, float]:
    """Push an exact finite transcript law through a deterministic statistic."""

    result: dict[T, float] = {}
    for outcome, mass in pmf.items():
        image = mapping(outcome)
        result[image] = result.get(image, 0.0) + mass
    return result


@dataclass(frozen=True)
class GaussianVersionPair:
    """Two stochastic software versions with controllable old/new correlation.

    For vertex v:
      Y0 = mu0 + sigma0 * U
      Y1 = mu1 + sigma1 * (rho * U + sqrt(1-rho^2) * V)
    where U,V are iid standard Gaussian under a shared random tape.
    """

    mu0: np.ndarray
    mu1: np.ndarray
    sigma0: np.ndarray
    sigma1: np.ndarray
    rho: np.ndarray

    @classmethod
    def from_sequences(
        cls,
        mu0: Sequence[float],
        mu1: Sequence[float],
        sigma0: Sequence[float] | float = 1.0,
        sigma1: Sequence[float] | float = 1.0,
        rho: Sequence[float] | float = 0.0,
    ) -> GaussianVersionPair:
        a = np.asarray(mu0, dtype=float)
        b = np.asarray(mu1, dtype=float)
        if a.shape != b.shape or a.ndim != 1:
            raise ValueError("mu0 and mu1 must be one-dimensional with equal shape")
        n = len(a)
        s0 = np.broadcast_to(np.asarray(sigma0, dtype=float), (n,)).copy()
        s1 = np.broadcast_to(np.asarray(sigma1, dtype=float), (n,)).copy()
        rr = np.broadcast_to(np.asarray(rho, dtype=float), (n,)).copy()
        if np.any(s0 <= 0) or np.any(s1 <= 0):
            raise ValueError("standard deviations must be positive")
        if np.any(np.abs(rr) > 1):
            raise ValueError("rho must lie in [-1,1]")
        return cls(a, b, s0, s1, rr)

    @property
    def n(self) -> int:
        return len(self.mu0)

    @property
    def theta(self) -> np.ndarray:
        return self.mu1 - self.mu0

    @property
    def paired_delta_variance(self) -> np.ndarray:
        return self.sigma1**2 + self.sigma0**2 - 2.0 * self.rho * self.sigma0 * self.sigma1

    @property
    def independent_delta_variance(self) -> np.ndarray:
        return self.sigma1**2 + self.sigma0**2

    def sample_delta(self, vertex: int, count: int, rng: np.random.Generator, paired: bool = True) -> np.ndarray:
        if count < 1:
            raise ValueError("count must be >= 1")
        if paired:
            u = rng.standard_normal(count)
            v = rng.standard_normal(count)
            old = self.mu0[vertex] + self.sigma0[vertex] * u
            new_noise = self.rho[vertex] * u + np.sqrt(max(0.0, 1.0 - self.rho[vertex] ** 2)) * v
            new = self.mu1[vertex] + self.sigma1[vertex] * new_noise
        else:
            old = self.mu0[vertex] + self.sigma0[vertex] * rng.standard_normal(count)
            new = self.mu1[vertex] + self.sigma1[vertex] * rng.standard_normal(count)
        return new - old


@dataclass(frozen=True)
class BernoulliCommonUniformPair:
    """Bernoulli versions coupled by the same uniform random tape.

    Y_j(v) = 1{U <= p_j(v)}. This monotone coupling gives a sparse patch delta:
    |Z|=1 only when U falls between p0 and p1.
    """

    p0: np.ndarray
    p1: np.ndarray

    @classmethod
    def from_sequences(cls, p0: Sequence[float], p1: Sequence[float]) -> BernoulliCommonUniformPair:
        a = np.asarray(p0, dtype=float)
        b = np.asarray(p1, dtype=float)
        if a.shape != b.shape or a.ndim != 1:
            raise ValueError("p0 and p1 must be one-dimensional with equal shape")
        if np.any((a < 0) | (a > 1)) or np.any((b < 0) | (b > 1)):
            raise ValueError("Bernoulli probabilities must lie in [0,1]")
        return cls(a, b)

    @property
    def theta(self) -> np.ndarray:
        return self.p1 - self.p0

    @property
    def paired_delta_variance(self) -> np.ndarray:
        d = np.abs(self.theta)
        return d * (1.0 - d)

    @property
    def independent_delta_variance(self) -> np.ndarray:
        return self.p0 * (1.0 - self.p0) + self.p1 * (1.0 - self.p1)

    def sample_delta(self, vertex: int, count: int, rng: np.random.Generator, paired: bool = True) -> np.ndarray:
        if count < 1:
            raise ValueError("count must be >= 1")
        if paired:
            u = rng.random(count)
            old = (u <= self.p0[vertex]).astype(float)
            new = (u <= self.p1[vertex]).astype(float)
        else:
            old = (rng.random(count) <= self.p0[vertex]).astype(float)
            new = (rng.random(count) <= self.p1[vertex]).astype(float)
        return new - old
