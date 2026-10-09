# Reproducibility protocol

## Portable and byte-exact hashes

Publication provenance records both `sha256` (the exact local bytes) and
`sha256_lf_normalized` for text manifests and JSONL results. The latter normalizes CRLF and legacy CR
line endings to LF before hashing, so it identifies the same logical text across Windows and Linux
checkouts. Frozen `data/*.jsonl` files are declared `eol=lf` in `.gitattributes`; the Git blob ID is
also recorded by the PC2 worker. Never compare a Windows raw-byte digest with a Linux raw-byte digest
as if a mismatch alone implied different benchmark rows.

## Immutable inputs

Every experiment is determined by:

- repository commit SHA;
- benchmark JSONL row;
- explicit random seed;
- implementation version;
- CPU/GPU environment report.

## Generated benchmark

```bash
python scripts/generate_benchmark.py --output data/benchmark_v1.jsonl
python scripts/generate_replay_benchmark.py --output data/replay_benchmark_v1.jsonl
python scripts/generate_counterfactual_benchmark.py --output data/counterfactual_replay_benchmark_v1.jsonl
python scripts/generate_threshold_replay_phase.py --output data/threshold_replay_phase_v1.jsonl
python scripts/generate_control_replay_structural_cases.py --output data/control_replay_structural_cases_v1.jsonl
python scripts/generate_partial_replay_benchmark.py --output data/partial_replay_benchmark_v1.jsonl
python scripts/generate_partial_replay_structural_cases.py --output data/partial_replay_structural_cases_v1.jsonl
python scripts/generate_partial_replay_scope_cases.py --output data/partial_replay_scope_cases_v1.jsonl
python scripts/generate_replay_phase_benchmark.py --output /tmp/replay_phase_benchmark_v1.jsonl
```

The generator is deterministic. The manifest contains parameter specifications rather than giant sampled arrays.

## CPU theorem sanity check

```bash
python experiments/run_gaussian_core.py --graph star --n 10 --gamma 0.5 --beta 0.05 --trials 100000
python experiments/run_bernoulli_coupling.py --p0 0.5 --delta 0.01 --samples 1000000
```

## Integrated publication suite

For a single theorem-facing run directory:

```bash
python scripts/run_publication_suite.py --mode smoke \
  --output-dir results/publication_smoke

python scripts/run_publication_suite.py --mode publication \
  --output-dir results/publication_cpu
```

To add the frozen GPU sweeps, pass `--gpu-devices` and `--gpu-trials`.
The suite writes the exact repository state, deterministic evidence summary,
executed command list, and per-job logs into the selected result directory.
Those generated result directories remain non-source artifacts until explicitly
frozen with hashes and provenance.

## GPU stress sweep

```bash
python experiments/gpu_sweep.py --devices 0,1 --trials 1000000 --benchmark data/benchmark_v1.jsonl --output results/gpu_sweep.jsonl
```

## Artifact freeze

When a figure/table becomes submission-facing:

1. create a frozen config/manifest;
2. rerun from a clean environment;
3. save environment report;
4. save command line and seed;
5. compute SHA-256 checksums;
6. never hand-edit result rows.


## Publication-run provenance

After each frozen long run, create a machine-readable provenance record with
scripts/record_publication_run.py. For the P15 publication sweep, pass the frozen
counterfactual benchmark JSONL, the merged result JSONL, the exact command string,
and a provenance JSON output path.

The record captures the source commit, dirty-tree status, benchmark and result
SHA-256 hashes, platform/Python metadata, NVIDIA environment, and PyTorch/CUDA
device information. Publication artifacts should be generated only from runs
whose provenance records show a clean source tree and the intended frozen commit.


## P17 partial-replay theorem checks

The P17 manifest is deterministic specification data. It spans graph family,
legal replay-group size, cost scale, and small differential effects. Every one of
its 168 rows is now materialized into a canonical graph, all legal groups up to
the row's size cap, and per-group costs. The validator executes both LP
geometries, the raw-information floor, and the homogeneous raw-contrast schedule
for every row. For every possible changed active endpoint, it also computes the
actual rounded exposure and verifies the exact miss probability
`(1-d)^exposure <= beta`. These are deterministic theorem checks, not empirical
evidence.

Use:

```bash
python experiments/search_partial_replay_gap.py --n 5 --max-group-size 3
python experiments/validate_partial_replay_manifest.py --benchmark data/partial_replay_benchmark_v1.jsonl
pytest -q tests/test_partial_replay_lower.py tests/test_partial_replay_benchmarks.py
```

The witness-scheduling LP and raw-information LP have different meanings and
must not be merged in reporting. The former uses edge-by-group incidence; the
latter reduces to active-vertex/group incidence under the frozen P17 oracle.

The separate structural-case manifest
`data/partial_replay_structural_cases_v1.jsonl` contains exact theorem fixtures,
not empirical outcomes: one coherent-equality case, six K_n pair-group cases
(n=3,...,8) with exact ratio n-1, and one finite-information/infeasible-witness
case. Regenerate it with `scripts/generate_partial_replay_structural_cases.py`.
The test suite requires the committed manifest to equal the deterministic
in-code specification exactly.

The separate scope-falsification manifest
`data/partial_replay_scope_cases_v1.jsonl` records deterministic counterexamples
to invalid theorem generalizations. Its v1 case fixes a heterogeneous
fairness-preserving null with tau=0.20, old Bernoulli thresholds (0.20,0.40),
new thresholds (0.30,0.45), and shared tape u=0.25. The new-version gap is
0.15 <= tau, yet the patch-delta vector is nonconstant and the homogeneous
raw-contrast predicate fires. The executable scope audit partitions the full
common-uniform tape at the four thresholds and derives the complete rejection
set `(0.20,0.30] U (0.40,0.45]`, whose exact uniform-tape measure is 0.15.
This quantity is analytic specification evidence, not an empirical false-positive
rate. Regenerate the manifest with
`scripts/generate_partial_replay_scope_cases.py`; it is specification data,
not an empirical false-positive estimate.


## Whole-submission checksum manifest

For a candidate submission commit, create a full tracked-source checksum manifest:

```bash
python scripts/freeze_submission_artifacts.py \
  --require-clean \
  --output results/submission_manifest.json
```

The manifest hashes every tracked repository file and records the exact git SHA.
Use repeated `--extra-file` arguments to attach the compiled PDF and only those
publication result/provenance files that actually exist. See
`docs/ARTIFACT_FREEZE.md`. This mechanism records artifacts; it never creates or
infers empirical results.

### P17 raw-contrast theorem checks

The P17 test suite exercises `active_vertex_contrast_schedule` and
`raw_group_contrast_witness` for the frozen homogeneous single-changed-endpoint
family. Deterministic checks cover active-vertex exposure, a finite-C_vert case
with infeasible C_edge, and representative common-uniform threshold regions.
These checks validate implementation correspondence to the audited theorem; they
do not replace the proof or extend the claim to heterogeneous/composite
fairness-preserving nulls.


## Public benchmark reproducibility

The public-data layer is separate from the 821 deterministic theorem/specification rows. Its source registry is `data/public_benchmark_registry_v1.jsonl`. Preparation is performed with `scripts/prepare_public_benchmarks.py`, which records a canonical loaded-data SHA-256, deterministic split seed, evaluation-context count, local base-predictor metadata, and the probability clipping range used to keep additive replay patches in the Bernoulli interior.

Publication rows are validated by `tfoesuu.public_results.PublicResultRow`. A publication matrix must come from one source commit, use one content hash per dataset, and contain no duplicate dataset/method/patch-size/seed keys. The plotting script `scripts/render_public_results.py` consumes only this validated JSONL. Raw third-party datasets and generated result files remain outside git; provenance and hashes are frozen with the publication bundle.


## P18 thresholded-replay phase checks

`data/threshold_replay_phase_v1.jsonl` contains 24 deterministic parameter
specifications spanning zero tolerance, `tau` on the same scale as `d`, and
fixed positive tolerance.  Every row is checked against
`threshold_fairness_replay_bounds`; the manifest stores no observed error rate
or performance result.

Regenerate and test with:

```bash
python scripts/generate_threshold_replay_phase.py \
  --output data/threshold_replay_phase_v1.jsonl
pytest -q tests/test_threshold_replay_phase.py \
  tests/test_threshold_replay_benchmarks.py
```


## P19 matched-control structural checks

`data/control_replay_structural_cases_v1.jsonl` contains six exact geometry
fixtures for the bipartite two-class theorem. They cover fractional
control-cover values 1, 1.5, and 2, weighted controls, paired controls, and a
boundary-only instance where the control cover is infeasible but the exact
mixed-information lower program remains finite and quadratic in the small
effect.

```bash
python scripts/generate_control_replay_structural_cases.py \
  --output data/control_replay_structural_cases_v1.jsonl
pytest -q tests/test_control_replay.py \
  tests/test_control_replay_benchmarks.py
```

## Theorem-driven replay phase contract

The additional replay phase grid is generated on demand and is not counted as a
new submission-evidence dataset. It is a deterministic experiment contract used
to guard theorem-facing GPU/CPU sweeps against post-hoc regime labeling.

```bash
python scripts/generate_replay_phase_benchmark.py \\
  --output /tmp/replay_phase_benchmark_v1.jsonl
python experiments/validate_replay_phase_contract.py \\
  --benchmark /tmp/replay_phase_benchmark_v1.jsonl
python experiments/search_control_replay_mixed_geometry.py --top 20
```

Version 1 freezes replay fidelity at 1.0. It labels only theorem-backed P19
control-coverage extremes (0 and 1). The exact mixed lower program now has
proved two-term coefficients, but intermediate topologies cannot be represented
by one scalar coverage fraction. A hybrid upper matches their finite-topology
`d`-orders but still requires the explicit groups and costs and does not close
exact constants. `boundary_familywise_fixed_design_lower_bound` reproduces the
rankwise chi-square lower floors for disjoint boundary channels, while
`boundary_familywise_sequential_bounds` reproduces the exact two-sided-SPRT KL,
overshoot, and expected-cost bounds. The fixed allocation has a necessary
`log |U|` factor; the unbounded sequential design removes it from expected null
cost. Mixed fixtures remain in the topology search rather than the v1 rho-only
grid. Generated rows are parameter specifications, never observed performance values.
