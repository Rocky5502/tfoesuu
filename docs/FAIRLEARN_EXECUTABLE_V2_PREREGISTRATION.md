# Preregistration: Fairlearn executable evolving-subject benchmark v2

Status: **source, runtime, and replay gates passed; bounded exploratory smoke only**

## Scientific purpose

This candidate addresses the executable-subject gap with an actual fairness
software defect and repair. It does not add another synthetic tabular row.
Fairlearn issue <https://github.com/fairlearn/fairlearn/issues/728> reports that
`ThresholdOptimizer` produced incorrect group results for multiple protected
features. Pull request <https://github.com/fairlearn/fairlearn/pull/763> fixes
truncation of long merged group names and explicitly notes that the defect can
affect users.

The frozen chronological pair is:

- upstream: <https://github.com/fairlearn/fairlearn>;
- old: `e8cc63784de5410805c156715175fc60e2cd5653`;
- new: `0cf59eccfdd364417787fe2c368a1c77c3f378b8`;
- relation: new is the direct child of old;
- upstream release containing the fix: `v0.6.2`;
- license Git blob in both revisions:
  `abef27e17206c6dbe20de33fb24f7c7ce3ae490d` (MIT);
- dependency-manifest Git blob in both revisions:
  `e28efe081a00d8b1b978c499add874045c8ef84a` (`requirements.txt`).

Both detached source trees are kept outside this repository and must be clean.
No upstream source may be edited.

## Source-level gate

The following facts were frozen before local execution:

1. `fairlearn/postprocessing/_threshold_optimizer.py` is identical across the
   pair (Git blob `67d443feb59d036cf5aeb2a47485cec6f2b7d42f`). Its public
   `predict(X, *, sensitive_features, random_state=None)` schema is unchanged.
2. `fairlearn/postprocessing/_interpolated_thresholder.py` is identical across
   the pair (Git blob `1eaa15f9b496038fa4b85bb58d8594cbd511c6f0`). Both versions
   use `check_random_state(random_state).rand(n)`, so the same integer seed and
   row order generate the same uniform tape.
3. The target file changes from Git blob
   `03d5fe963f00ca644701691f15814c7c499f8a6f` to
   `962b348e9850ad3bc0b9dd9bd95535dfa6267c08`. The semantic change replaces
   fixed-width NumPy row merging with pandas row merging to prevent truncation
   of long protected-group names.
4. The upstream regression fixture was added in the same repair commit. The
   benchmark input below is frozen from that fixture rather than selected after
   observing our outputs.

This establishes a legitimate same-schema evolving source pair. It does not by
itself authorize an experiment or establish replay readiness.

## Frozen compatibility environment

The bounded smoke will use one digest-pinned Linux container and these exact
packages for both revisions:

- base image: `python@sha256:e191a71397fd61fbddb6712cd43ef9a2c17df0b5e7ba67607128554cd6bff267`
  (`python:3.8.20-slim-bullseye`, Linux amd64);
- Python 3.8.20;
- NumPy 1.20.3;
- pandas 1.2.4;
- SciPy 1.6.3;
- scikit-learn 0.24.2.

The container digest, `pip freeze`, Python/platform manifest, and hashes of the
probe and both source trees must be captured before results are admitted. The
upstream `rai-core-flask==0.0.2` dependency is not needed by the postprocessing
execution path; the probe imports directly from the pinned source tree. If that
assumption fails, the smoke fails rather than silently changing versions.

Resolved local image identity:
`sha256:6afe6f54f95c63fd79c70d4db4e1820c093b186db99e855405d4323b7bcc6e87`.
The probe SHA-256 is
`c4d5a27c7d7e4bd54e31e1cd04599a10450e5d0e958e5c40629d2f69033918d3`.

## Frozen bounded CPU smoke

The first smoke uses the exact 16-row training fixture and 24-row evaluation
fixture added by upstream PR #763. It fits the same prefitted linear regressor
and two demographic-parity `ThresholdOptimizer` instances per revision:

- one receives the two protected columns separately;
- one receives their canonical combined representation.

The long strings, commas, and backslashes in the four protected groups are
retained exactly. Predictions use seeds `1`, `104729`, `130363`, and `155921`,
fixed here before local execution. For every version and seed, preserve the
probability mass function, generated uniform tape, predictions, interpolation
dictionary, group cardinality, stdout/stderr, return code, and wall time.

The runtime/replay gate passes only if:

1. both exact revisions import and execute in the same locked environment;
2. repeated calls at a fixed seed are bitwise identical;
3. for each call, predictions equal the recorded probability thresholded by
   `numpy.random.RandomState(seed).rand(n)` in the frozen row order;
4. old and new consume equal-length, elementwise-identical uniform tapes; and
5. the new revision's two-column result equals its canonical-combined control
   for every frozen seed, as specified by the upstream regression test.

The documented old-version mismatch is an expected defect reproduction, not a
gate condition and not a paper claim. Record it whether present or absent. No
seed, string length, row, metric, or exclusion may be changed after the smoke.

## Interpretation and compute fences

- This pair tests evolution of protected-group handling under an unchanged
  randomized prediction interface. It is not evidence that arbitrary software
  versions can share random tapes.
- Identical integer seeds count as a common tape here only because the entire
  random-draw implementation is byte-identical and the emitted uniforms are
  checked explicitly.
- The actual Fairlearn subject is CPU code. A GPU reimplementation would not be
  the external executable and is scientifically inadmissible for this smoke.
- A four-seed smoke is environment and correspondence evidence, not a
  publication-scale statistical result.
- No public-dataset campaign, large trial matrix, paper admission, or external
  release follows without a separate frozen protocol and explicit approval.

## Go/no-go order

1. Reproduce source identity, clean-tree, chronology, license, manifest, API,
   semantic-change, and unchanged-RNG checks automatically.
2. Resolve and record the container digest and exact environment manifest.
3. Run import-only preflight for both revisions.
4. Run the frozen four-seed CPU smoke once and retain all outcomes.
5. Independently validate transcript hashes and common-tape correspondence.
6. Decide whether a larger preregistered matrix is scientifically warranted.

## Bounded smoke outcome (2026-10-09)

The protocol above was executed once after source audit, container resolution,
and import-only preflight. Both revisions imported as `0.6.2.dev0` with the
frozen public signature and exact dependency lock. The independent validator
passed every runtime and common-tape condition.

- The old multi-column path collapsed four protected groups to three. Its
  predictions disagreed with its canonical-combined control for all four frozen
  seeds.
- The repaired multi-column path retained four groups and exactly matched its
  canonical-combined control for all four seeds.
- Old/new predictions disagreed on 8, 7, 7, and 8 of 24 rows in the multi-column
  path for seeds `1`, `104729`, `130363`, and `155921`, respectively.
- Old/new predictions had zero disagreements for every seed in the canonical
  combined control path. This isolates the observed change to the documented
  group-merging defect rather than the estimator, tape, or row order.
- Every repeated prediction was bitwise identical and every prediction matched
  the recorded probability thresholded by the recorded common uniform tape.
- Subject execution took 0.293 seconds old and 0.317 seconds new in the bounded
  container smoke; these are single-run engineering timings, not performance
  claims.

Evidence directory (outside Git):
`G:\TFOESUU Project\external_results\fairlearn_v2_20261009T1230`.
Key SHA-256 values are:

- old transcript: `c22a17c62f3411499a51793e2c3705e49e778a1bd661a26b28a4f7d1a2f0eeda`;
- new transcript: `dcc9c129cc51d6be130351e6abab15fd4d6d85b24835711e4df46821c80d1a19`;
- independent validation summary:
  `20df213d6c9540b96ab380680b6469f90dc287fdec1a2b4cf4ea1e220acb0a05`;
- source audit: `e01e127a97b706b4d6af575787b54ba6d98318d987222f4f139735c835db8a4e`;
- environment image inspection:
  `35fe8b50d18b87c39100222341238883928a95cfc2bfd55bc829a9e2c27e1815`;
- `pip freeze`: `18f12df17d479da0107d8907c8b5b811c1cbf285388aae39b244f33b4ae737d0`.

This is a genuine positive resolution of the executable evolving-subject gap at
smoke scale. It remains excluded from manuscript results until independent-host
replication, a frozen statistical question, and any required approval pass.
