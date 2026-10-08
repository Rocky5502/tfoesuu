"""Testing Fairness of Evolving Software under Uncertainty."""

from .allocation import (
    AllocationResult,
    PsiConicCertificate,
    psi_conic_certificate,
    solve_psi,
    solve_psi_dual,
)
from .certificate import (
    CertificatePruningResult,
    ResidualEdgeMargins,
    prune_with_patch_envelopes,
    threshold_residual_margins,
)
from .graphs import GraphSpec
from .oracles import BernoulliCommonUniformPair, GaussianVersionPair
from .replay_benchmarks import ReplayBenchmarkSpec, replay_benchmark_v1
from .replay_information import ReplayInformationSolution, minimum_information_cover
from .nuisance_information import FiniteNuisanceInformationAudit, audit_finite_nuisance_information
from .separations import (
    CounterfactualReplayBounds,
    LocationReplayBounds,
    ReplaySeparationBounds,
    ThresholdFairnessReplayBounds,
    counterfactual_replay_bounds,
    location_replay_bounds,
    replay_separation_bounds,
    threshold_fairness_replay_bounds,
    threshold_fairness_replay_kl,
)
from .software_subjects import RandomizedResourceAllocatorPair, linear_baseline
from .suite_replay import SuiteReplayBounds, active_vertex_count, synchronized_suite_replay_bounds
from .partial_replay import (
    GroupReplayUpperBound,
    ReplayGroupCover,
    minimum_replay_group_cover,
    partial_synchronized_replay_upper_bound,
)
from .partial_replay_benchmarks import (
    PartialReplayBenchmarkSpec,
    partial_replay_benchmark_v1,
)
from .control_replay_benchmarks import (
    ControlReplayStructuralCase,
    control_replay_structural_cases_v1,
)
from .control_replay import (
    ControlReplayInformationLowerBound,
    ControlReplaySchedule,
    FractionalControlCover,
    control_replay_information_lower_bound,
    matched_control_contrast_witness,
    matched_control_replay_schedule,
    minimum_fractional_control_cover,
)
from .partial_replay_lower import (
    FractionalActiveVertexCover,
    FractionalReplayCover,
    FractionalReplaySchedule,
    RawOutputInformationLowerBound,
    fractional_replay_schedule,
    minimum_fractional_active_vertex_cover,
    minimum_fractional_replay_cover,
    raw_output_information_lower_bound,
)
from .threshold_replay_benchmarks import (
    ThresholdReplayPhaseSpec,
    threshold_replay_phase_benchmark_v1,
)
from .subject_benchmarks import (
    SoftwareSubjectBenchmarkSpec,
    software_subject_benchmark_v1,
)
from .testers import FullRegressionTestResult, run_gaussian_full_regression_test
from .planner import TFOESUUPlan, plan_bernoulli_replay, plan_gaussian_regression

__all__ = [
    "AllocationResult",
    "PsiConicCertificate",
    "psi_conic_certificate",
    "solve_psi",
    "solve_psi_dual",
    "CertificatePruningResult",
    "ResidualEdgeMargins",
    "threshold_residual_margins",
    "prune_with_patch_envelopes",
    "GraphSpec",
    "GaussianVersionPair",
    "BernoulliCommonUniformPair",
    "ReplayBenchmarkSpec",
    "ReplayInformationSolution",
    "FiniteNuisanceInformationAudit",
    "audit_finite_nuisance_information",
    "minimum_information_cover",
    "replay_benchmark_v1",
    "ReplaySeparationBounds",
    "ThresholdFairnessReplayBounds",
    "LocationReplayBounds",
    "CounterfactualReplayBounds",
    "replay_separation_bounds",
    "threshold_fairness_replay_bounds",
    "threshold_fairness_replay_kl",
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
    "PartialReplayBenchmarkSpec",
    "partial_replay_benchmark_v1",
    "FractionalActiveVertexCover",
    "ControlReplayStructuralCase",
    "control_replay_structural_cases_v1",
    "FractionalControlCover",
    "ControlReplayInformationLowerBound",
    "ControlReplaySchedule",
    "minimum_fractional_control_cover",
    "control_replay_information_lower_bound",
    "matched_control_replay_schedule",
    "matched_control_contrast_witness",
    "FractionalReplayCover",
    "FractionalReplaySchedule",
    "RawOutputInformationLowerBound",
    "minimum_fractional_active_vertex_cover",
    "minimum_fractional_replay_cover",
    "fractional_replay_schedule",
    "raw_output_information_lower_bound",
    "linear_baseline",
    "ThresholdReplayPhaseSpec",
    "threshold_replay_phase_benchmark_v1",
    "SoftwareSubjectBenchmarkSpec",
    "software_subject_benchmark_v1",
    "FullRegressionTestResult",
    "run_gaussian_full_regression_test",
    "TFOESUUPlan",
    "plan_gaussian_regression",
    "plan_bernoulli_replay",
]

__version__ = "0.1.0"
