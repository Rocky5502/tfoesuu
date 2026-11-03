# TFOESUU

**Testing Fairness of Evolving Software under Uncertainty**

[![MIT License](https://img.shields.io/badge/license-MIT-0f766e.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-254e72.svg)](pyproject.toml)
[![Research software](https://img.shields.io/badge/status-research%20software-64748b.svg)](docs/PROOF_STATUS.md)

TFOESUU is an executable Python research toolkit for **version-aware fairness regression testing** of stochastic software. Its emphasis is on what an auditor may legitimately observe, which obligations can be soundly eliminated, and how the available replay mechanism changes the testing budget.

![TFOESUU scientific architecture: certified context, sound reduction, replay-law contract, and scope-matched statistical tests](docs/assets/tfoesuu-architecture.svg)

> **Scope:** Results apply to explicitly declared Gaussian and common-uniform threshold families. This software does not provide universal fairness certification or causal-discrimination estimates.

## Start here

**Reviewers:** [10-minute setup and exact reproduction commands](docs/REVIEWER_GUIDE.md) · [Theorem-to-code map](docs/THEOREM_ALGORITHM_MATRIX.md) · [Scientific scope](docs/PROOF_STATUS.md) · [Data inventory](data/README.md)

Requires Python 3.10+ and Git. No model API, GPU, or dataset download is needed for the CPU checks.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/validate_benchmark_inventory.py
```

A bounded synthetic smoke experiment:

```bash
python experiments/run_gaussian_core.py --graph star --n 8 --trials 500 --gamma 0.7 --beta 0.05
python experiments/run_replay_separation.py --p 0.5 --d 0.05 --beta 0.05 --trials 1000
```

These examples exercise declared mathematical oracles. They are **not** benchmark evidence of improved speed on arbitrary deployed software.

## How the toolkit works

| Component | Implementation | Scientific role |
| --- | --- | --- |
| Change and certificate handling | `certificate.py`, `planner.py` | Eliminate only provably safe comparisons |
| Counterfactual graph and allocation | `graphs.py`, `allocation.py` | Gaussian graph allocation and residual-obligation geometry |
| Observation oracles and tests | `oracles.py`, `testers.py` | State legal observations, type-I/II risks, and concrete call charges |
| Restricted replay and covers | `control_replay.py`, `partial_replay.py` | Distinguish legal groups, shared-tape access, and fractional covers |
| Exact-law evidence | `preview_results.py` | Fail-closed admission of frozen Bernoulli experiments |
| Historical software audit | `public_fairlearn_v2_results.py` | Validate grouping-behavior discrepancies, not causal fairness |

All modules are in [`src/tfoesuu/`](src/tfoesuu). The research intentionally distinguishes a theoretical oracle query, a shared-tape round, and an actual execution of a program.

## Reproduce the evidence

- **P12/P15:** 198 archived configurations, 100,000 trials per configuration, and 594 exact-law checks. [Frozen data and source identities](reproducibility/p12_p15/evidence/README.md).
- **P19:** 57,600 synthetic trajectories studying legal control topology and measured stopping-time executions, not generalized empirical speedups. [Independent CPU audit](reproducibility/p19_simple_null/README_RESEARCH_AUDIT.md).
- **Shared nuisance:** exact rational-law audit and counterexample under a deliberately restricted matched-control model. [Audit notes](reproducibility/unknown_shared_nuisance/README.md).
- **Public-data layer:** specifications and aggregate historical Fairlearn grouping results; raw third-party datasets are not redistributed. [Data guide](data/README.md).

Commands, scope conditions, and interpretation are in the [reviewer guide](docs/REVIEWER_GUIDE.md) and [reproducibility protocol](docs/REPRODUCIBILITY.md).

## Directory map

```text
src/tfoesuu/        Algorithms, legal oracle interfaces, and exact-law validators
tests/              CPU unit, adversarial, and scope regression tests
experiments/        Reproducible synthetic experiments and validation scripts
data/               Frozen specifications and aggregate public-software evidence
reproducibility/    Archived raw results, source snapshots, and independent audits
configs/            Explicit experiment protocols
external_subjects/  Version-pinned third-party software-subject interfaces
scripts/            Non-destructive generators, checks, and provenance utilities
docs/               Reviewer guide, validity boundaries, and maintenance records
```

## Development, citation, and security

Install optional profiles only when needed: `pip install -e ".[gpu]"` (CUDA setup is machine-specific) or `pip install -e ".[public-v2]"` (may require upstream data licenses). Dependency declarations are in [`pyproject.toml`](pyproject.toml), with matching `requirements*.txt` profiles for scripted environments. See [contributing](CONTRIBUTING.md) and [security reporting](SECURITY.md).

Original code and documentation are distributed under the [MIT License](LICENSE), subject to [third-party notices](THIRD_PARTY_NOTICES.md) and contributor rights. [CITATION.cff](CITATION.cff) records the software citation; no conference acceptance or DOI is asserted.

**Access note:** the repository was private at the last verified checkpoint. Reviewers must be granted access before the code/data link is usable. CI must be judged from an **executed** run, not a configured workflow. Manuscript files are maintained separately from this code-focused working tree; deleting them from the current tree does not erase older Git history.
