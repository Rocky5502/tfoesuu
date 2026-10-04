"""Testing Fairness of Evolving Software under Uncertainty."""

from .allocation import AllocationResult, solve_psi, solve_psi_dual
from .graphs import GraphSpec
from .oracles import BernoulliCommonUniformPair, GaussianVersionPair
from .replay_benchmarks import ReplayBenchmarkSpec, replay_benchmark_v1
from .separations import ReplaySeparationBounds, replay_separation_bounds

__all__ = [
    "AllocationResult",
    "solve_psi",
    "solve_psi_dual",
    "GraphSpec",
    "GaussianVersionPair",
    "BernoulliCommonUniformPair",
    "ReplayBenchmarkSpec",
    "replay_benchmark_v1",
    "ReplaySeparationBounds",
    "replay_separation_bounds",
]

__version__ = "0.1.0"
