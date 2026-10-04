"""Testing Fairness of Evolving Software under Uncertainty."""

from .allocation import AllocationResult, solve_psi, solve_psi_dual
from .certificate import CertificatePruningResult, prune_with_patch_envelopes
from .graphs import GraphSpec
from .oracles import BernoulliCommonUniformPair, GaussianVersionPair
from .replay_benchmarks import ReplayBenchmarkSpec, replay_benchmark_v1
from .separations import (
    CounterfactualReplayBounds,
    LocationReplayBounds,
    ReplaySeparationBounds,
    counterfactual_replay_bounds,
    location_replay_bounds,
    replay_separation_bounds,
)
from .software_subjects import RandomizedResourceAllocatorPair, linear_baseline
from .suite_replay import SuiteReplayBounds, active_vertex_count, synchronized_suite_replay_bounds
from .partial_replay import ReplayGroupCover, GroupReplayUpperBound, minimum_replay_group_cover, partial_synchronized_replay_upper_bound
from .subject_benchmarks import (
    SoftwareSubjectBenchmarkSpec,
    software_subject_benchmark_v1,
)
from .testers import FullRegressionTestResult, run_gaussian_full_regression_test

__all__ = [
    "AllocationResult",
    "solve_psi",
    "solve_psi_dual",
    "CertificatePruningResult",
    "prune_with_patch_envelopes",
    "GraphSpec",
    "GaussianVersionPair",
    "BernoulliCommonUniformPair",
    "ReplayBenchmarkSpec",
    "replay_benchmark_v1",
    "ReplaySeparationBounds",
    "LocationReplayBounds",
    "CounterfactualReplayBounds",
    "replay_separation_bounds",
    "counterfactual_replay_bounds",
    "location_replay_bounds",
    "RandomizedResourceAllocatorPair",
    "SuiteReplayBounds",
    "active_vertex_count",
    "synchronized_suite_replay_bounds",
    "ReplayGroupCover",
    "GroupReplayUpperBound",
    "minimum_replay_group_cover",
    "partial_synchronized_replay_upper_bound",
    "linear_baseline",
    "SoftwareSubjectBenchmarkSpec",
    "software_subject_benchmark_v1",
    "FullRegressionTestResult",
    "run_gaussian_full_regression_test",
]

__version__ = "0.1.0"
