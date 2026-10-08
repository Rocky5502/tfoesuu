# TFOESUU — Research / Code / Experiment Readiness Audit

Audit date: **2026-10-08**
Live source inspected: `main` at `83c754114050769c043442b2b2f96b470c858fc8`
This file reports what is **present**, not a claim of a clean end-to-end run.

## 1. Scientific gates

- P1--P19: the proof ledger records audited **scoped** mathematical results.
  Final independent human checking remains required before STOC submission.
- P20: **CONJECTURE**. Finite-nuisance action-information LP fixtures and a
  necessary pointwise-null KL floor exist; no graph-level adaptive
  achievability or general replay-oracle theorem is established.
- The monochrome STOC overview and algorithm are in the GitHub LaTeX
  source. A separately connected Overleaf project is not verified as synced.

## 2. Code / data inventory

- Nine checked-in deterministic theorem/specification JSONL manifests:
  **821 frozen configurations**. These are **not** measured GPU trials.
- Seven public dataset populations: frozen registry and preparation/loader
  scripts. Raw public data and full-result matrix are not in the tracked repo.
- `results/` at audit time contains only `.gitkeep`. Therefore no local
  publication sweep or seven-dataset benchmark is established as completed.
- The public GPU benchmark has an explicit four-way old/new common-tape
  threshold simulation for its single-changed-edge witness. Unchanged edges
  are eliminated by a distributionally sufficient reduction. Independent and
  vertex-paired methods still use binomial sufficient-statistic simulation.
- The three synchronized methods deliberately share a matched witness trace.
  Their reported `concrete_program_executions` are planned oracle-work
  counts, not independently profiled wall-clock execution totals.
- The default public patch grid now has four values and matches the strict
  manuscript release gate.

## 3. Hardening landed in this pass

1. Reject NaN/Infinity, nonnumeric measurements, fractional counts, and
   boolean counts in publication-result rows.
2. Require exact dataset, method, patch, aggregate-row, and matched-seed
   coverage, with a 40-character source commit and enough trials.
3. Use a Bonferroni-simultaneous Clopper--Pearson interval for the larger of
   type-I/type-II empirical errors, avoiding post-selection undercoverage.
4. Persist publication job commands and failure logs incrementally.
5. Replace injected binomial witness hits with explicit four-way common-tape
   threshold simulations; add deterministic oracle and optional CPU torch
   smoke tests. Retain model-based cost accounting disclosure.
6. Update the manuscript and public-benchmark protocol to distinguish
   simulation from executed system timings.
7. Check the GPU runner's default patch grid against the publication gate.

Tests were **added**; a green full-repository run has **not** been observed.

## 4. Current release blockers

- GitHub Actions CI is **red before runner assignment** on the inspected
  source: job metadata report no runner and no steps. This is not a pytest or
  LaTeX failure log; their results remain unknown.
- A clean Python/pytest/static-bibliography run and a complete
  `paper/main.tex` LaTeX build must be obtained on the final HEAD.
- The public seven-dataset preparation and staged CPU/GPU experiments must
  actually be run, with raw logs, exact commands, data hashes, frozen seeds
  and environment metadata.
- Generated result tables and plots must be produced from the validated
  frozen output; do not turn the tracked `TBD` template into pretend results.
- Every result claim must be linked to the software implementation's
  *statistical observation model* and to honest execution-cost units.
- Confirm final human authors/affiliations, AI disclosure, first-12-page STOC
  technical navigation, and required video/policy steps.

## 5. Exact next execution gate

On a clean checkout with a working Python environment:

```bash
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m compileall -q src scripts experiments tests
python scripts/validate_benchmark_inventory.py
pytest -q
python scripts/check_bibliography.py
python scripts/check_paper_consistency.py
```

After these are green, do the **CPU smoke**, then a one-dataset GPU smoke,
then the full seven-dataset run using a frozen source SHA.
Only the strict release gate may promote a public-results matrix to
publication-facing LaTeX.

**Do not claim submission readiness, empirical performance, or a P20 theorem
from manifest existence or generic LP code.**
