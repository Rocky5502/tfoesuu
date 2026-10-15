# TFOESUU — STOC 2027 independently audited review release (2026-10-15)

## What to compile

**Overleaf main file: `main.tex`**. This builds the STOC 2027 *review-submission* manuscript, with human author information on the title page, a separate contents page, single-column US Letter layout, 11-point main text and 1-inch margins. The complete formal results and technical appendix are included; references are at the end. No review-submission page limit applies under the official CFP.

Stale two-column post-acceptance entry points have been removed from this
review-only release so that every shipped compilable source has one observation
taxonomy and one set of theorem statements. Camera-ready formatting is a
separate post-acceptance task.

## Source reconciliation and editorial changes

This release was reconciled with the research branch rather than replacing it.
It separates Gaussian delta observations from raw Bernoulli replay transcripts,
repairs the active-vertex domain of the Gaussian allocation, preserves the
scoped P12--P19 hypotheses, and removes duplicated theorem/proof inclusions.
The 2026-10-15 audit also adds a narrowly scoped exact shared-nuisance witness,
its shifted-support counterexample, and a reproduced P19 stopping-time check.
These additions do not promote the open P20 composite-nuisance conjecture.
No experimental value was inferred from a PDF, log message, or unit-test count.

## Verified mechanical checks in the editorial environment

- The final local build command and PDF hash are recorded in the repository's
  execution ledger and release manifest.
- Citation keys, referenced labels, duplicate labels, and bibliography output
  are checked on the final TeX closure.
- All 136 displayed equations are numbered and uniquely labeled; the review
  static gate rejects raw unnumbered display blocks and unlabeled numbered
  environments.
- Every final PDF page is rendered for visual inspection before packaging.

If local latexmk cannot invoke BibTeX, check that the BibTeX executable is
installed and on PATH. The only compiled input is the source-backed P19 PDF
figure under `figures/`; the manuscript PDF itself is not bundled. The exact
figure data, generator, seeds, and tests are under
`supplemental/p19_simple_null_20261014/`. The dependency-free nuisance audit is
under `supplemental/unknown_shared_nuisance/`.

## Scientific conditions not certified by this package

The `evidence/` directory includes the complete 54-row P12 and 144-row P15
100k records, admission manifest, exact-law validation report, and hashes. The
594 comparisons produced zero familywise-Bonferroni outliers at level 0.05.
This is oracle-model validation, not a hardware-speedup result, proof, or
real-software benchmark. The seven-population historical PMF census is a
software-behavior result, not causal fairness. Coauthor sign-off and final
human verification of every substantive claim remain mandatory.

Current venue details must be rechecked at https://acm-stoc.org/stoc2027/stoc2027-cfp.html immediately before submission.
