# Public benchmark protocol for STOC 2027

## Purpose

The public-data layer is a finite-instance stress test of the version-aware execution model. It does not establish any theorem and it must never be used to extend P17 beyond its audited scope. Public datasets supply realistic input populations and protected attributes; the stochastic old/new software versions are constructed locally and reproducibly.

## Frozen benchmark populations

| ID | Dataset | Task | Protected attributes | Source family |
|---|---|---|---|---|
| `public-adult` | Adult Census Income | binary classification | sex, race | UCI |
| `public-bank` | Bank Marketing | binary classification | age | UCI |
| `public-german` | Statlog German Credit | binary classification | sex, age | UCI |
| `public-compas` | ProPublica COMPAS | binary classification | race, sex | ProPublica |
| `public-lawschool` | Law School GPA | regression to thresholded decision | race, gender | AIF360 |
| `public-meps21` | MEPS Panel 21 | binary classification | race | AIF360/AHRQ |
| `public-default-credit` | Default of Credit Card Clients | binary classification | sex, age | UCI |

The authoritative URLs and DOIs where available are frozen in `data/public_benchmark_registry_v1.jsonl`.

## Version construction

1. Split each dataset deterministically into training and evaluation partitions using a frozen seed.
2. Fit a simple local baseline predictor using only non-protected features. No pretrained model or external model API is permitted.
3. Convert the baseline score into an interior Bernoulli probability `p0(x)` with clipping away from 0 and 1.
4. Define the old executable software as `P0(x;U)=1{U <= p0(x)}` for a common-uniform random tape `U`.
5. Construct the new version from a frozen patch specification. The theorem-aligned controlled patch uses a common probability shift `s` and an endpoint-specific differential shift `d` on a counterfactual pair, with clipping configurations excluded from theorem-comparison plots.
6. In the v1 evaluator, construct one controlled two-endpoint edge per evaluation context by
   duplicating its scalar `p0(x)` at both old endpoints. The prepared NPZ does not store or mutate
   protected-attribute values, and therefore does not materialize an empirical counterfactual pair.
   Protected attributes identify the fairness-relevant source population and are excluded from the
   local predictor; the experimental graph itself is a synthetic theorem-aligned wrapper.
7. Run independent execution, old/new vertex pairing, four-way replay, suite replay where executable, and TFOESUU using identical confidence targets.

## Why this construction is appropriate

The local predictor supplies heterogeneous base probabilities from public covariates, while the
software wrapper gives exact control of stochastic execution and the common random tape. Duplicating
each scalar probability makes the two old endpoints equal by construction before the injected patch.
This is a controlled finite-instance replay experiment, not evidence that the source dataset supplies
valid causal counterfactual worlds or that its fairness assumptions hold.

## Prepared-input integrity gate

Before any public smoke or publication run, validate the complete directory read-only:

```bash
python scripts/validate_prepared_public_benchmarks.py \
  /path/to/datasets/prepared \
  --expected-source-commit <40-character-clean-release-SHA>
```

The validator requires exactly the seven registered IDs; coherent manifest and per-dataset metadata;
the frozen NPZ schema; matching probability/label lengths; finite interior probabilities within the
declared clip; binary labels; one source commit; and valid metadata/count fields. Its JSON report
records byte hashes for the 15 prepared artifacts. These byte hashes are distinct from each
dataset's `canonical_loaded_data_sha256`, which fingerprints the loader's canonical feature/target
population before splitting.

The protected-attribute names in v1 metadata are not row-level protected data. The fail-closed
Fairlearn readiness audit is documented in `docs/FAIRLEARN_PUBLIC_CONTEXT_AUDIT.md`; it classifies
five registry entries as candidates but zero frozen prepared artifacts as executable multi-column
contexts. Any such experiment requires a separate v2 artifact contract and new preparation in a
non-overwriting directory.

Prepared artifacts may be evaluated by a later clean execution commit only through the explicit
`tfoesuu-public-preparation-compatibility-v1` contract. The contract compares the Git blob IDs of:

- `scripts/prepare_public_benchmarks.py`;
- `data/public_benchmark_registry_v1.jsonl`;
- `requirements-public.txt`.

Any mismatch fails closed and requires re-preparation. A compatible result row records the original
`preparation_source_commit`, the later execution `source_commit`, and the SHA-256 of the exact
contract blob map. This exception does not permit metadata editing and does not claim that
unrecorded loader package versions were reconstructed; the canonical population hashes and strict
prepared-artifact byte hashes remain part of the release evidence.

## Primary factors

- patch size `d`: freeze at least four logarithmically separated values after CPU smoke validation;
- common patch size `s`: include zero and nonzero regimes;
- confidence target: primary `delta=0.05`, with at least one sensitivity value;
- replay regime: independent, vertex paired, four-way, suite where valid, TFOESUU;
- dataset: all seven registered public populations;
- seeds: freeze before the publication run; do not add seeds after inspecting outcomes.

## Primary outcomes

- concrete program executions to reach the fixed-confidence decision;
- replay rounds where meaningful;
- empirical type-I and type-II error with trial count and binomial interval;
- speedup relative to independent execution at matched confidence;
- graph vertices/edges and residual graph size after deterministic pruning;
- theorem-predicted schedule cost versus observed finite-instance cost.

Classifier predictive accuracy is secondary metadata, not the main outcome.

## Run ladder

1. `10^3` trials/configuration CPU smoke.
2. `10^4` trials/configuration single-GPU smoke.
3. `10^5` trials/configuration publication preview.
4. `10^6` or more trials/configuration only for configurations whose rare-error resolution requires it.

Escalate only after the previous stage passes schema, error-control, and provenance checks.

## Result admission gate

A public result may enter the manuscript only if:

- the dataset source and local content SHA-256 are recorded;
- preprocessing and split seed are frozen;
- the repository SHA is clean and recorded;
- the result validates against `PublicResultRow`;
- all rows in a publication matrix come from one source commit;
- repeated rows do not change the dataset hash;
- the requested confidence/error semantics match the theorem or are clearly labeled empirical;
- the figure/table is generated from immutable result JSONL rather than edited by hand.

## P17 fence

The public-data suite is not a vehicle for claiming the P17 heterogeneous/composite-null theorem. The P17 raw-contrast result remains restricted to the frozen homogeneous family. The public suite can evaluate safe witness-based or general version-aware procedures and can be used to search for failures of invalid generalizations.

## Observation and cost semantics of the GPU evaluator

`experiments/gpu_public_replay_sweep.py` evaluates the frozen *threshold-
coupled Bernoulli software model* with heterogeneous prepared input
probabilities. It is not an external-service replay or measured program-runtime
study. Independent and vertex-paired baselines draw exact binomial sufficient
statistics. Synchronized replay now uses explicit four-way old/new threshold
operations on common random tapes, rather than injecting a Binomial(d)
witness count.

Under the **single-changed-edge** experimental alternative, the remaining
fairness edges carry no differential patch signal. Therefore the four-way,
suite, and localized TFOESUU methods may reuse one matched changed-edge
witness trace; this is statistically sufficient within that frozen model.
Their error estimates are intentionally correlated and should not be
reported as independent replicated findings.

The `concrete_program_executions` field is a *declared planned oracle-work
count* (e.g., 4mT for edgewise four-way replay and 4kT for impact-localized
replay), not the number of PyTorch kernels dispatched. Do not interpret
these results as an independently observed wall-clock speedup or a test of
uncontrolled operating-system nondeterminism. Such claims require actual
instrumented multi-input software execution and separate timing/provenance.

The deterministic NumPy tape-partition fixture and optional CPU PyTorch
smoke tests in `tests/test_public_four_way_pathwise.py` guard the
common-tape cancellation law. No simulated run is publication evidence
until it has been executed on the frozen evaluation inputs and independently
validated against the strict result-matrix gate.

## Publication release gate (October 2026)

Preparation is not an experiment result. The repository contains **821 frozen
theorem/specification rows** and a registry of **7 planned public populations**.
Neither count is evidence that GPU sweeps or a seven-dataset publication
evaluation have finished. The `paper/generated/public_results_table.tex` file
still contains a deliberately non-evidential template until an actual result
matrix is frozen and verified.

After running the seven-dataset protocol, validate the actual aggregated
result JSONL from a clean source commit:

```bash
python scripts/validate_public_results.py \
  --registry data/public_benchmark_registry_v1.jsonl \
  --results results/public/public_results.jsonl \
  --require-datasets 7 \
  --min-patch-sizes 4 \
  --min-trials 100000
```

This stricter release gate requires:
- the **exact** seven registered dataset IDs (no missing or extra data);
- at least four patch sizes and the **same patch-size grid** for every dataset;
- all five methods (independent, vertex-paired, four-way, suite, TFOESUU)
  for each dataset/patch-size cell;
- a **single aggregated result per method** in each dataset/patch-size cell; distinct seed-specific rows must be aggregated with independently preserved run provenance before release;
- **matched seed identifiers across methods** for every dataset/patch-size cell;
- identical graph metadata across methods for each cell;
- 100,000 or more actual trials per aggregate row, with integer trial counts and error counts;
- finite, numeric execution costs, replay rounds, patch sizes, and empirical error rates (no NaN, Infinity, boolean counts, or fractional trial counts);
- one 40-character hexadecimal source-commit ID;
- consistent frozen dataset SHA-256, source commit, confidence target, and
  common patch shift in the matrix.

These are validation constraints, **not evidence** that trials ran.
Independently verify the raw execution logs, data hashes, environment metadata,
result provenance, and the exact code revision before paper admission. Only
after the release gate passes should the manuscript-facing public-results
table be generated from the frozen result file.

For the table's maximum of empirical type-I and type-II errors, report an
**exact Bonferroni-simultaneous 95% Clopper--Pearson interval**, not the
unadjusted interval for whichever error rate happened to be larger.
`scripts/render_public_results_table.py` implements this correction.

For theorem-only CPU work, `scripts/run_publication_suite.py` now writes
`commands.json` incrementally. When a job fails, its log and failed status
survive for diagnosis; downstream jobs are not recorded as completed.

**Do not copy or fabricate results into the PDF to satisfy a deadline.**
