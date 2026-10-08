# Preregistration: executable counterfactual-subject benchmark v2

Status: **design frozen; no outcomes collected; not manuscript evidence**

## Scientific decision

Do not add five or six more ordinary tabular populations.  The seven-population
v1 matrix already varies realistic covariates, but its evaluator duplicates each
scalar baseline probability into two synthetic endpoints.  More rows of the same
kind would not repair the main semantic gap: execution on genuine inputs that
differ in a protected attribute, with measured software invocations rather than
declared oracle-work counts.

The single next candidate is the Themis executable subject suite:

- upstream: <https://github.com/LASER-UMASS/Themis>;
- pinned candidate commit: `a70f12a6a8f34cdd8b170b4dc59a78674c9e8950`;
- pin verification: `git ls-remote ... HEAD`, 2026-10-09;
- upstream scope: command-line subject systems with declared input schemas and
  binary outputs, including eight named systems and twenty reported instances;
- licensing gate: upstream states academic-use-only distribution.  No vendoring
  or redistribution is permitted until the exact license obligations are recorded.

This choice is motivated by counterfactual execution semantics, not benchmark
count or expected favorable outcomes.

## Read-only feasibility audit (2026-10-09)

The pinned commit was cloned outside the project repository at
`G:\TFOESUU Project\external_sources\themis-a70f12a` and checked out detached
and clean.  No upstream file was modified and no subject was executed.

- Top-level license SHA-256:
  `30572d228ee9914fa381ea0997325627300e6cd976e738c327115af32a957ab8`.
- No `requirements.txt`, `setup.py`, environment file, or other dependency lock
  is present. The Themis 2.0 README requires Anaconda 2 and names matplotlib,
  scikit-learn, and NumPy; the core also imports SciPy.
- Themis 1.0 and the replication scripts use Python-2-only interfaces such as
  `commands`, `urllib2`, `map` list semantics, and print statements. Other
  subject families include C++ and a large Java/Weka tree. A silent Python 3
  port is therefore forbidden.
- The harness exposes a seed for its own test-input sampling, but the inspected
  command-line subjects return deterministic binary decisions and expose no
  software random tape. Harness sampling randomness is not replayable subject
  randomness.
- The most compact external baseline candidate is replication system G's
  command-line linear-regression wrapper. Its source SHA-256 is
  `fcbb5c6b22f12857353b3077ad573d6475d03e7a73c07794ac77d80400a33f96`;
  the bundled Census training file SHA-256 is
  `096c67159231feb8d8e40c76906e10d63a5a74cd07b11fdd39f9f235b2f619d2`.
- Git history contains only the initial addition for that wrapper, not a
  documented old/new version pair.

Gate outcome: **eligible only as a deterministic executable fairness-testing
baseline at present**. It is a no-go for replay-theorem evidence and for the
primary evolving-software experiment until a legitimate, same-schema old/new
change is identified and a behavior-preserving compatibility environment is
locked. This negative feasibility result is retained rather than manufacturing
versions or wrapping deterministic outputs in synthetic randomness.

## Frozen v2 question

Can the version-aware procedures operate on real executable input pairs that
differ in exactly one declared protected attribute, and what are their measured
subprocess and wall-clock costs?  A result answers this empirical question only.
It becomes replay-theorem evidence only if the subject also exposes a seedable
random tape and satisfies the relevant Bernoulli/interiority assumptions.

## Pre-outcome acceptance gates

Before any result is inspected:

1. Record the upstream commit, license text hash, dependency lock, selected
   subject/model hashes, wrapper hash, and local environment manifest.
2. Select exactly one model family for the first bounded smoke.  Freeze an old/new
   pair with the same input schema; do not select versions after viewing fairness
   outcomes.
3. Materialize input pairs that differ in exactly one protected attribute.
   Reject pairs outside the declared input domain and record every exclusion.
4. Capture the complete old/new by endpoint transcript.  Verify repeated
   deterministic executions and, where available, same-tape and independent-tape
   controls.
5. Count actual subprocess invocations and measure wall time.  Do not substitute
   the v1 evaluator's declared planned execution count.
6. Freeze pair sampling, tolerance, alternative size, seeds, stopping rules, and
   exclusions before the smoke.  Preserve raw stdout, stderr, return codes, and
   per-invocation timing.
7. Store v2 outputs separately from the seven-dataset v1 artifacts.  A failed or
   incompatible subject remains in the audit trail.

## Interpretation fences

- A deterministic binary-only subject is a fairness-testing baseline, not
  evidence for common-random-number replay gains.
- A randomized wrapper counts as theorem-facing only if it exercises the actual
  external executable and injects auditable randomness; merely wrapping a fixed
  prediction in the existing synthetic Bernoulli model is insufficient.
- Themis configurations need not be chronological software revisions.  The
  old/new pair must represent a documented code/model/configuration change.
- Dependency rehabilitation may alter behavior.  Any compatibility patch must be
  isolated, hashed, and reported rather than silently editing upstream code.
- No v2 result enters the paper until provenance, schema, transcript, and
  statistical validation pass independently.

## Go/no-go order

1. License and dependency audit.
2. Read-only source inventory and wrapper feasibility check.
3. CPU-only one-pair smoke with zero manuscript claims.
4. Preregister the bounded matrix.
5. Request publication-scale approval only after the smoke passes.
