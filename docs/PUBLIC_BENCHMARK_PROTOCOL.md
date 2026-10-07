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

1. Split each dataset deterministically into train/validation/evaluation partitions using frozen seeds.
2. Fit a simple local baseline predictor using only non-protected features. No pretrained model or external model API is permitted.
3. Convert the baseline score into an interior Bernoulli probability `p0(x)` with clipping away from 0 and 1.
4. Define the old executable software as `P0(x;U)=1{U <= p0(x)}` for a common-uniform random tape `U`.
5. Construct the new version from a frozen patch specification. The theorem-aligned controlled patch uses a common probability shift `s` and an endpoint-specific differential shift `d` on a counterfactual pair, with clipping configurations excluded from theorem-comparison plots.
6. Construct counterfactual fairness edges by changing only the designated protected attribute while holding all non-protected features fixed. Store the resulting graph size and pair-construction audit.
7. Run independent execution, old/new vertex pairing, four-way replay, suite replay where executable, and TFOESUU using identical confidence targets.

## Why this construction is appropriate

The local predictor supplies realistic heterogeneous base probabilities from public data, while the software wrapper gives exact control of the stochastic execution and common random tape. By training the base score without protected attributes, a counterfactual pair shares the same old probability before the injected patch. This allows theorem-aligned replay experiments without claiming that the original public dataset itself satisfies the theorem assumptions.

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