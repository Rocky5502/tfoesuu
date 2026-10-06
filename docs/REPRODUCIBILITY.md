# Reproducibility protocol

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
python scripts/generate_partial_replay_benchmark.py --output data/partial_replay_benchmark_v1.jsonl
python scripts/generate_partial_replay_structural_cases.py --output data/partial_replay_structural_cases_v1.jsonl
python scripts/generate_partial_replay_scope_cases.py --output data/partial_replay_scope_cases_v1.jsonl
python scripts/generate_partial_replay_group_coherent_cases.py --output data/partial_replay_group_coherent_cases_v1.jsonl
```

The generator is deterministic. The manifest contains parameter specifications rather than giant sampled arrays.

## CPU theorem sanity check

```bash
python experiments/run_gaussian_core.py --graph star --n 10 --gamma 0.5 --beta 0.05 --trials 100000
python experiments/run_bernoulli_coupling.py --p0 0.5 --delta 0.01 --samples 1000000
```

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
raw-contrast predicate fires. Regenerate it with
`scripts/generate_partial_replay_scope_cases.py`; it is specification data,
not an empirical false-positive estimate.

The group-coherent extension manifest
`data/partial_replay_group_coherent_cases_v1.jsonl` records a globally
heterogeneous but replay-group-coherent null together with a single changed
endpoint.  Its v1 matching instance uses null patch intervals (0.20,0.30] and
(0.40,0.45] in different replay components, d=0.05, and an exact witness tape
u=0.325.  Tests require zero null contrast within each group, positive
alternative contrast in the changed group, and agreement with the C_vert
schedule.  Regenerate it with
`scripts/generate_partial_replay_group_coherent_cases.py`.


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
