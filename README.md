# Testing Fairness of Evolving Software under Uncertainty (TFOESUU)

**STOC 2027 theory-first research project on fairness regression testing for evolving stochastic software.**

## Research question

Given a previously certified program P0, a patched version P1, a counterfactual fairness graph, and stochastic execution access, **how many executions are fundamentally necessary to determine whether the patch introduced a fairness regression?**

This project is deliberately model-free:

- no proprietary model API;
- no pretrained model;
- no open-source model;
- no LLM/model as an experimental subject.

GPU computation is used only for our own stochastic simulation, convex/graph optimization, theorem stress-testing, and counterexample search.

## Central mechanism: replay the change, not the whole system

When old and new software can be executed with the same random tape R, a paired-oracle call observes

    Z_v = P1(v; R) - P0(v; R).

Its uncertainty is

    Var(Z_v) = Var(P1) + Var(P0) - 2 Cov(P1,P0).

A **paired-oracle call evaluates both versions once**, so it corresponds to exactly two concrete program executions. The paper states query bounds in paired-oracle calls unless noted otherwise.

## Validated theoretical spine

The live source of truth is [docs/PROOF_STATUS.md](docs/PROOF_STATUS.md). Current audited results include:

- localization of new fairness violations to sound patch-impact edges;
- impossibility of sharp-threshold finite-sample certification under stochastic execution without a margin;
- Gaussian graph-allocation upper/lower bounds governed by Psi(H,nu);
- exact Psi values on several graph families and a primal/dual characterization;
- an Omega(M) patch-location advantage on matching instances;
- no minimax gain from old certificate slack alone under unrestricted patches;
- a Bernoulli **linear-vs-quadratic small-patch separation**: paired replay scales as Theta(d^-1 log(1/delta)), while independent/fresh replay scales as Theta(d^-2 log(1/delta));
- unknown patch location on an M-edge matching costs Theta(M d^-1 log(1/delta)) under common-uniform replay;
- sound patch-effect envelopes can prune already-safe fairness edges with **zero new executions**, leaving only a residual graph for stochastic testing;
- four-way counterfactual replay cancels a nonzero fairness-neutral common patch and changes the differential-gap exponent from quadratic to linear;
- a thresholded replay phase transition shows the limit of that advantage: one-edge synchronized replay costs `Theta((tau+d) log(1/delta)/d^2)`, so `tau=O(d)` remains linear in `1/d` while fixed positive `tau` returns to quadratic scaling;
- matched-background controls restore the linear regime under a scoped heterogeneous two-class null: the exact lower program mixes `Theta(d)` control-compatible information with `Theta(d^2)` boundary-only information, and the upper schedule is governed by a new fractional control cover `C_ctrl`;
- synchronized suite replay tests all fairness edges from one shared-seed suite execution, giving `Theta(n_active log(1/delta)/d)` concrete-execution scaling in the audited Bernoulli family, independent of edge count.
- partial synchronized replay has a corrected two-matrix formulation. The edge-by-group LP gives a four-way-witness schedule, while the raw transcript-information floor reduces to an active-vertex/group cover. Exact structural fixtures separate those LPs. An audited raw-output contrast theorem attains the same active-vertex C_vert geometry in the frozen homogeneous single-changed-endpoint family, including instances where the edge-witness LP is infeasible. A deterministic heterogeneous fair-null counterexample now guards the scope boundary: naive raw-contrast extension can false-positive, so broader heterogeneous/composite-null partial replay remains open.

Claims enter the abstract only after proof/audit gates.

## Repository map

```text
src/tfoesuu/
  allocation.py              Psi primal/dual optimization
  certificate.py             Static patch-envelope certificate pruning
  graphs.py                  Counterfactual graph families
  oracles.py                 Coupled Gaussian/Bernoulli version oracles
  separations.py             Replay and patch-location finite-sample bounds
  software_subjects.py       Executable randomized software subject
  benchmarks.py              Gaussian theorem benchmark specifications
  replay_benchmarks.py       Bernoulli replay benchmark specifications
  subject_benchmarks.py      Executable-subject benchmark specifications
  testers.py                 Gaussian patch-neutrality/full-regression testers
  counterfactual_benchmarks.py  Frozen P15 four-way replay benchmark grid
  control_replay.py           P19 matched-control geometry, exact information LP, schedule
  control_replay_benchmarks.py Exact P19 structural theorem fixtures
  replay_phase_benchmarks.py  Theorem-driven P18/P19 phase-transition specifications
  suite_replay.py             P16 synchronized-suite replay bounds
  partial_replay.py           Legal replay groups + integral P17 upper constructions
  partial_replay_lower.py     Fractional witness schedule + active-vertex information floor
  partial_replay_benchmarks.py Deterministic P17 theorem-falsification specifications
  preview_results.py         Fail-closed P12/P15 100k campaign admission
  public_benchmarks_v2.py    Protected-context V2 preparation and validation
  public_fairlearn_v2_*.py   Historical Fairlearn execution/provenance boundary
  planner.py                 Fail-closed theorem-backed TFOESUU execution planner

experiments/
  run_gaussian_core.py
  run_bernoulli_coupling.py
  run_replay_separation.py
  run_location_replay.py
  run_allocator_subject.py
  gpu_sweep.py
  gpu_replay_sweep.py
  gpu_counterfactual_sweep.py  Two-GPU P15 shared-patch stress sweep
  search_partial_replay_gap.py P17 witness-cover gap / counterexample search
  search_control_replay_mixed_geometry.py Mixed-control singular-LP falsification search
  validate_replay_phase_contract.py Phase-grid theorem-claim validator

scripts/
  generate_benchmark.py
  generate_replay_benchmark.py
  generate_subject_benchmark.py
  generate_counterfactual_benchmark.py
  generate_threshold_replay_phase.py
  generate_control_replay_structural_cases.py
  generate_partial_replay_benchmark.py
  generate_partial_replay_structural_cases.py
  generate_partial_replay_scope_cases.py
  generate_public_benchmark_registry.py
  generate_replay_phase_benchmark.py
  summarize_submission_evidence.py
  run_publication_suite.py      Integrated CPU/GPU theorem-facing publication runner
  check_bibliography.py
  check_paper_consistency.py
  check_review_submission.py  STOC review-format/equation-label gate
  validate_preview_results.py P12/P15 exact finite-law admission
  render_public_fairlearn_v2_results.py  Provenance-locked V2 result renderer
  audit_public_fairlearn_v2_rows.py      Exact row/group audit of frozen V2 outputs
  render_public_fairlearn_v2_row_audit.py  Provenance-locked affected-row table
  freeze_submission_artifacts.py Whole-repository submission checksum manifest
  record_publication_run.py      Per-run benchmark/result provenance
  verify_environment.py

data/
  benchmark_v1.jsonl
  replay_benchmark_v1.jsonl
  software_subject_benchmark_v1.jsonl
  counterfactual_replay_benchmark_v1.jsonl  144 frozen P15 configurations
  threshold_replay_phase_v1.jsonl            24 frozen P18 tolerance/effect specifications
  partial_replay_benchmark_v1.jsonl          168 frozen P17 parameter-stress rows
  partial_replay_structural_cases_v1.jsonl   8 exact P17 structural theorem fixtures
  partial_replay_scope_cases_v1.jsonl        deterministic P17 scope counterexamples
  public_benchmark_registry_v1.jsonl            7 frozen public evaluation datasets
  p12_p15_100k_preview_manifest_v1.json         admitted 198-configuration campaign
  p12_p15_100k_preview_validation_v1.json       594 exact-law comparisons
  fairlearn_public_v2_results_v1.json           admitted seven-population census
  fairlearn_public_v2_row_audit_v1.json         affected-row/group aggregate audit

paper/stoc2027_review/       Authoritative STOC review-submission LaTeX source
docs/                        proof audits, novelty matrix, roadmap, GPU runbook
tests/                       deterministic unit/theorem sanity tests
.github/workflows/           CPU CI + real LaTeX/PDF build CI
```

## Dependency profiles

The repository separates dependency surfaces so theorem/CPU validation remains lightweight.

- `requirements.txt`: core runtime dependencies only;
- `requirements-dev.txt`: core + pytest/ruff for local development and CI;
- `requirements-gpu.txt`: core + PyTorch for local GPU simulation sweeps;
- `requirements-public.txt`: optional V1 public-benchmark dependencies;
- `requirements-public-v2.txt`: V1 dependencies plus deterministic legacy-XLS
  support required by the protected-context V2 preparation.

The package metadata in `pyproject.toml` is the canonical installable-project definition. Keep lower bounds synchronized when dependencies change.

Equivalent editable installs are `pip install -e ".[dev]"`,
`pip install -e ".[gpu]"`, `pip install -e ".[public]"`, and
`pip install -e ".[public-v2]"`.

## CPU setup and validation

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .

pytest -q
python scripts/check_bibliography.py
python scripts/check_paper_consistency.py
python scripts/check_review_submission.py

python scripts/generate_benchmark.py --output data/benchmark_v1.jsonl
python scripts/generate_replay_benchmark.py --output data/replay_benchmark_v1.jsonl
python scripts/generate_subject_benchmark.py --output data/software_subject_benchmark_v1.jsonl
python scripts/generate_counterfactual_benchmark.py --output data/counterfactual_replay_benchmark_v1.jsonl
python scripts/generate_threshold_replay_phase.py --output data/threshold_replay_phase_v1.jsonl
python scripts/generate_control_replay_structural_cases.py --output data/control_replay_structural_cases_v1.jsonl
python scripts/generate_partial_replay_benchmark.py --output data/partial_replay_benchmark_v1.jsonl
python scripts/generate_partial_replay_structural_cases.py --output data/partial_replay_structural_cases_v1.jsonl
python scripts/generate_partial_replay_scope_cases.py --output data/partial_replay_scope_cases_v1.jsonl

python experiments/run_gaussian_core.py --graph star --n 10 --trials 10000
python experiments/run_replay_separation.py --p 0.5 --d 0.01 --trials 100000
python experiments/run_location_replay.py --candidates 64 --p 0.5 --d 0.01 --trials 100000
python experiments/run_allocator_subject.py --contexts 64 --changed-context 17 --delta 0.01 --trials 100000
python experiments/run_counterfactual_replay.py --p 0.35 --shared-patch 0.20 --d 0.01 --trials 100000
python experiments/run_threshold_replay_phase.py --p 0.20 --shared-patch 0.10 --tau 0.10 --d 0.01 --trials 100000
python experiments/search_partial_replay_gap.py --n 5 --max-group-size 3
python experiments/validate_partial_replay_manifest.py --benchmark data/partial_replay_benchmark_v1.jsonl
python experiments/validate_control_replay_manifest.py --benchmark data/control_replay_structural_cases_v1.jsonl
python experiments/validate_replay_phase_contract.py --benchmark /tmp/replay_phase_benchmark_v1.jsonl
python experiments/search_control_replay_mixed_geometry.py --top 20
```

## One-command theorem-facing publication validation

The repository now exposes a single orchestrator for the paper-facing CPU checks
and optional GPU sweeps. It records the repository state, derives the deterministic
evidence summary, validates all P17 manifest rows, and runs the Gaussian, replay,
counterfactual-replay, location, and executable-software-subject experiments.

```bash
# Fast CPU smoke validation
python scripts/run_publication_suite.py --mode smoke \
  --output-dir results/publication_smoke

# Larger CPU publication run
python scripts/run_publication_suite.py --mode publication \
  --output-dir results/publication_cpu

# Bounded publication run plus frozen GPU sweeps (through 100k only)
python scripts/run_publication_suite.py --mode publication \
  --gpu-devices 0,1 --gpu-trials 100000 \
  --output-dir results/publication_full
```

No paper number should be copied from these runs by hand. Result rows become
submission-facing only after their source commit, benchmark hash, seed/environment
metadata, and output checksums are frozen.

## Submission-facing manuscript structure

The Overleaf-ready paper now contains, in the main compiled closure:

- an evidence-reuse/replay overview figure;
- a front-of-paper theorem/results-at-a-glance table;
- an executable high-level TFOESUU algorithm;
- explicit RQ1--RQ4;
- the complete 821-row deterministic specification inventory;
- a deterministic audit-results table;
- an exact P17 structural/scope figure;
- the admitted P12/P15 campaign: 198 configurations at 100,000 trials each and
  594 exact-law comparisons with zero familywise-Bonferroni outliers;
- a complete seven-population historical Fairlearn census. The parent differs
  from the canonical protected-tuple control on Adult and Default Credit, the
  other five parent populations are exact zeros, and the repair agrees exactly
  on all seven. This is software-behavior evidence, not causal fairness.

## Two local NVIDIA GPUs

Install the CUDA-enabled PyTorch build appropriate for the installed NVIDIA driver using the official PyTorch selector, then install the remaining GPU extras.

```bash
pip install -r requirements-gpu.txt
python scripts/verify_environment.py
```

Smoke first:

```bash
python experiments/gpu_sweep.py --devices 0 --trials 10000 --benchmark data/benchmark_v1.jsonl --output results/smoke_gaussian.jsonl
python experiments/gpu_replay_sweep.py --devices 0 --trials 10000 --benchmark data/replay_benchmark_v1.jsonl --output results/smoke_replay.jsonl
```

Then use both GPUs for an authorized bounded stage:

```bash
python experiments/gpu_sweep.py --devices 0,1 --trials 100000 --benchmark data/benchmark_v1.jsonl --output results/gpu_sweep_100k.jsonl
python experiments/gpu_replay_sweep.py --devices 0,1 --trials 100000 --benchmark data/replay_benchmark_v1.jsonl --output results/replay_gpu_sweep_100k.jsonl
python experiments/gpu_counterfactual_sweep.py --devices 0,1 --trials 100000 --benchmark data/counterfactual_replay_benchmark_v1.jsonl --output results/counterfactual_gpu_sweep_100k.jsonl
```

See [docs/GPU_RUNBOOK.md](docs/GPU_RUNBOOK.md) before any long run. The approved
frozen P12/P15 evidence stops at $10^5$ trials per configuration. Million-trial
or larger campaigns require fresh authorization and a demonstrated scientific
need; completed admitted campaigns must not be rerun merely to consume GPUs.

## Data policy

This project does not need a scraped observational dataset to establish its theorems. The committed JSONL files are deterministic **synthetic specification datasets** with exact ground truth and immutable seeds. They are designed to:

1. falsify conjectures;
2. verify theorem constants and scaling;
3. expose adversarial graph/variance regimes;
4. reproduce executable software-subject cases.

Large raw Monte Carlo outputs belong in `results/` and are git-ignored.

## Paper and Overleaf

The authoritative review source is `paper/stoc2027_review/main.tex`. CI applies
the general manuscript checker and the STOC-specific review gate, then builds
that entry point as an 11-point, single-column US-Letter manuscript. Generated
PDFs, Overleaf ZIPs, and local build directories are release artifacts: they
are not committed or pushed to GitHub.

## Theorem-driven phase benchmark

The replay phase grid is a deterministic specification layer, not an empirical result table. It is designed to test predicted complexity transitions rather than increase dataset count.

- P18 local rows vary `tau/d` while keeping `tau=O(d)` and are labeled only at the proved local linear order.
- P18 fixed-tolerance rows hold positive `tau` fixed while shrinking `d`, targeting the proved quadratic boundary regime.
- P19 v1 contains only the topology-complete control-coverage extremes `rho=0` and `rho=1`.
- The mixed P19 lower program has proved two-term asymptotics, and a boundary/control hybrid matches its `d`-orders. Fixed boundary allocations require an `|U| log |U|/d^2` familywise cost, while adaptive likelihood-ratio allocation achieves `Theta(|U|/d^2)` topology scaling at fixed confidence even with a deterministic truncated cost cap. Its untruncated leading null constant is within `log(1/beta)/kl(1-beta,beta)` of the information floor (1.1305 at beta=.05); exact adaptive constants and optimal confidence dependence remain open. A scalar `rho` still does not determine the topology. Replay fidelity below 1 remains a falsification domain until corresponding theory is proved or refuted.

The mixed-control singular analysis is documented in `docs/MIXED_CONTROL_SINGULAR_ASYMPTOTICS.md`. It is intentionally not promoted to P20.

## Integrity rules

- No invented results.
- Conjectures stay labeled conjectures/open.
- Computational checks never substitute for proof.
- Peer-reviewed archival references are preferred.
- Known adjacent theories—fairness testing, paired binary inference, common random numbers, active anomaly search, pairwise experimental design—are cited explicitly instead of being relabeled as novel.
- Every long experiment records configuration, seed, environment, source commit, and output checksum.

See [docs/THEOREM_ALGORITHM_MATRIX.md](docs/THEOREM_ALGORITHM_MATRIX.md), [docs/ROADMAP.md](docs/ROADMAP.md), [docs/NOVELTY_MATRIX.md](docs/NOVELTY_MATRIX.md), the claim-level [docs/HOSTILE_NOVELTY_AUDIT_P12_P19.md](docs/HOSTILE_NOVELTY_AUDIT_P12_P19.md), [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md), and [docs/ARTIFACT_FREEZE.md](docs/ARTIFACT_FREEZE.md).


## Public benchmark layer

A separate seven-dataset registry is frozen for the submission-facing finite-instance evaluation: Adult, Bank Marketing, German Credit, COMPAS, Law School GPA, MEPS Panel 21, and Default Credit.  The raw datasets are not committed.  Each publication run must freeze source/preprocessing hashes and construct old/new stochastic software versions locally so the benchmark exercises the replay model rather than merely reporting generic classifier fairness metrics.


## Public benchmark commands and admitted status

V1 remains a deliberately failing negative control for executable multi-column
Fairlearn contexts: protected names are metadata only. Inspect it with
`scripts/audit_fairlearn_public_contexts.py <prepared-dir> --require-ready`; the
gate must fail rather than reinterpret V1 as row-level protected data.

For V2 work, install `requirements-public-v2.txt`. The non-overwriting
preparer and validator are `scripts/prepare_public_benchmarks_v2.py` and
`scripts/validate_prepared_public_benchmarks_v2.py`; the immutable protocol is
documented in [docs/PUBLIC_BENCHMARK_V2_PROTOCOL.md](docs/PUBLIC_BENCHMARK_V2_PROTOCOL.md).
V2 preserves aligned train/evaluation protected values, non-protected features,
source bytes, and split identities. Raw datasets remain external and must never
be added to Git.

The authorized historical Fairlearn campaign is complete. Its admitted summary
is `data/fairlearn_public_v2_results_v1.json`, produced only after validation of
the 14 old/new records, source identities, input-bundle manifest, approval
record, common-tape correspondence, and single-attribute controls. Do not infer
causal or population-fairness conclusions from this finite-row software census.

The P12/P15 GPU campaign can be revalidated without rerunning it:

```bash
python scripts/validate_preview_results.py \
  data/p12_p15_100k_preview_manifest_v1.json \
  --base-dir . --output /tmp/p12_p15_validation.json
```

This checks all 198 configurations and 594 exact-law comparisons against the
frozen result records and source/specification hashes.
