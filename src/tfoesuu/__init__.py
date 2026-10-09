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
from .control_replay import (
    BoundaryFamilywiseFixedDesignLowerBound,
    BoundaryFamilywiseSequentialBounds,
    ControlReplayInformationLowerBound,
    ControlReplaySchedule,
    FractionalControlCover,
    MixedControlReplaySchedule,
    boundary_familywise_fixed_design_lower_bound,
    boundary_familywise_sequential_bounds,
    control_replay_information_lower_bound,
    matched_control_contrast_witness,
    matched_control_replay_schedule,
    minimum_fractional_control_cover,
    mixed_control_replay_schedule,
)
from .control_replay_benchmarks import (
    ControlReplayStructuralCase,
    control_replay_structural_cases_v1,
)
from .graphs import GraphSpec
from .nuisance_information import FiniteNuisanceInformationAudit, audit_finite_nuisance_information
from .oracles import BernoulliCommonUniformPair, GaussianVersionPair
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
from .planner import TFOESUUPlan, plan_bernoulli_replay, plan_gaussian_regression
from .replay_benchmarks import ReplayBenchmarkSpec, replay_benchmark_v1
from .replay_information import ReplayInformationSolution, minimum_information_cover
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
from .subject_benchmarks import (
    SoftwareSubjectBenchmarkSpec,
    software_subject_benchmark_v1,
)
from .suite_replay import SuiteReplayBounds, active_vertex_count, synchronized_suite_replay_bounds
from .testers import FullRegressionTestResult, run_gaussian_full_regression_test
from .threshold_replay_benchmarks import (
    ThresholdReplayPhaseSpec,
    threshold_replay_phase_benchmark_v1,
)

__all__ = [
    "AllocationResult",
    "BernoulliCommonUniformPair",
    "BoundaryFamilywiseFixedDesignLowerBound",
    "BoundaryFamilywiseSequentialBounds",
    "CertificatePruningResult",
    "ControlReplayInformationLowerBound",
    "ControlReplaySchedule",
    "ControlReplayStructuralCase",
    "CounterfactualReplayBounds",
    "FiniteNuisanceInformationAudit",
    "FractionalActiveVertexCover",
    "FractionalControlCover",
    "FractionalReplayCover",
    "FractionalReplaySchedule",
    "FullRegressionTestResult",
    "GaussianVersionPair",
    "GraphSpec",
    "GroupReplayUpperBound",
    "LocationReplayBounds",
    "MixedControlReplaySchedule",
    "PartialReplayBenchmarkSpec",
    "PsiConicCertificate",
    "RandomizedResourceAllocatorPair",
    "RawOutputInformationLowerBound",
    "ReplayBenchmarkSpec",
    "ReplayGroupCover",
    "ReplayInformationSolution",
    "ReplaySeparationBounds",
    "ResidualEdgeMargins",
    "SoftwareSubjectBenchmarkSpec",
    "SuiteReplayBounds",
    "TFOESUUPlan",
    "ThresholdFairnessReplayBounds",
    "ThresholdReplayPhaseSpec",
    "active_vertex_count",
    "audit_finite_nuisance_information",
    "boundary_familywise_fixed_design_lower_bound",
    "boundary_familywise_sequential_bounds",
    "control_replay_information_lower_bound",
    "control_replay_structural_cases_v1",
    "counterfactual_replay_bounds",
    "fractional_replay_schedule",
    "linear_baseline",
    "location_replay_bounds",
    "matched_control_contrast_witness",
    "matched_control_replay_schedule",
    "minimum_fractional_active_vertex_cover",
    "minimum_fractional_control_cover",
    "minimum_fractional_replay_cover",
    "minimum_information_cover",
    "minimum_replay_group_cover",
    "mixed_control_replay_schedule",
    "partial_replay_benchmark_v1",
    "partial_synchronized_replay_upper_bound",
    "plan_bernoulli_replay",
    "plan_gaussian_regression",
    "prune_with_patch_envelopes",
    "psi_conic_certificate",
    "raw_output_information_lower_bound",
    "replay_benchmark_v1",
    "replay_separation_bounds",
    "run_gaussian_full_regression_test",
    "software_subject_benchmark_v1",
    "solve_psi",
    "solve_psi_dual",
    "synchronized_suite_replay_bounds",
    "threshold_fairness_replay_bounds",
    "threshold_fairness_replay_kl",
    "threshold_replay_phase_benchmark_v1",
    "threshold_residual_margins",
]

__version__ = "0.1.0"
