# Preregistration: Fairlearn repair on public V2 contexts

Status: **analysis design frozen; score companion and outcome approval still required**.

## Question and scope

This protocol asks a software-conformance question: on seven fixed public data
contexts, does Fairlearn's repaired multi-column protected-group path agree
with an injective one-column encoding of the same ordered protected tuples?
It does not estimate a causal effect, reinterpret protected attributes, or
claim that the selected populations represent deployment populations.

The machine-readable contract is
`configs/fairlearn_public_v2_analysis.json`. Its validator rejects dataset,
source-pair, transformation, support, estimand, seed, or authorization drift.
The prepared input is the immutable V2.1 manifest with SHA-256
`b07bf1aa17e37bc02971e200fb7c7e6eed14584d8920573f966fc56399acaf39`.
The executable pair remains old `e8cc63784de5410805c156715175fc60e2cd5653`
and direct-child repair `0cf59eccfdd364417787fe2c368a1c77c3f378b8`.

## Frozen protected transformations

- Adult keeps the source-defined sex and race categories.
- COMPAS keeps source-defined race and sex.
- Law School keeps source-defined race and gender.
- German and Default Credit keep sex and map numeric age to `age<25` or
  `age>=25`.
- Bank uses the same age threshold and is a single-attribute negative control.
- MEPS keeps source-defined race and is a single-attribute negative control.

The age threshold is fixed before subject outcomes and agrees with the earlier
binary-age benchmark convention. No group may be merged, removed, or relabeled
after an old/new result is observed.

## Support gate

Every transformed group must contain at least 40 training rows, at least two
training rows from each binary label, and at least five evaluation rows; every
evaluation group must occur in training. A read-only pre-outcome audit of V2.1
passes this gate for all seven datasets. The transformed group counts are 10,
2, 4, 4, 4, 4, and 2 for Adult, Bank, COMPAS, Default Credit, German, Law
School, and MEPS respectively. The limiting group is German male/age<25 with
45 training rows; the original provisional threshold of 50 was therefore
rejected before any subject execution and replaced by the frozen threshold 40.

## Estimands and controls

For each dataset and revision, the primary estimand is both the maximum and the
mean row-wise absolute difference between the exact randomized prediction PMF
from native protected columns and from an injective length-prefixed encoding of
the same ordered tuple. The repaired revision must have exactly zero difference
before serialization tolerance. The paired old-minus-new discrepancy is the
evolution effect; it is reported for every dataset, including zero effects.

Bank and MEPS test the unchanged single-attribute path. Their old and new PMFs
must agree exactly. Four frozen common-tape seeds are correspondence checks
only; the primary result uses exact PMFs and therefore needs no sampling
confidence interval. No significance filtering or dataset deletion is allowed.

## Score-model gate and newly found blocker

Fairlearn runs in the pinned historical Python 3.8 environment with a prefit
score estimator. Before entering that environment, a companion artifact must
store aligned training and evaluation scores from the V2.1 logistic-regression
pipeline. Its evaluation scores must reproduce V2.1
`baseline_probabilities` exactly, and both subject revisions must receive the
same immutable score arrays.

A hostile reconstruction audit decoded the stored raw features and inferred
column types from their scalar values. This reproduced all evaluation scores
bit-for-bit for Adult, Bank, COMPAS, Default Credit, German, and Law School.
It failed for MEPS (maximum absolute probability difference
`0.4504382489762433`) because scalar tokens do not retain source dataframe
dtypes. Consequently V2.1 remains a valid protected-context representation,
but it is not by itself an exact score-model replay artifact. The remedy is a
separate non-overwriting score companion generated with the original frozen
loader and environment; silently accepting inferred MEPS types is forbidden.

No public Fairlearn outcome may run until that companion has its own schema,
hashes, corruption tests, independent validation, and exact evaluation-score
reproduction. Creating the companion is preprocessing, not authorization for
the publication campaign.

## Release fences

- The configuration retains `outcome_authorized=false` until fresh approval.
- Failure of a support, score, source, runtime, common-tape, or canonical-key
  gate aborts the affected run without adaptive repair.
- Exact PMF discrepancies are software behavior, not population fairness or
  causal-effect estimates.
- All seven datasets and all zero/negative findings must be reported together.
- GPU use is scientifically inappropriate for the historical Fairlearn subject
  and cannot substitute for exact CPU execution.
