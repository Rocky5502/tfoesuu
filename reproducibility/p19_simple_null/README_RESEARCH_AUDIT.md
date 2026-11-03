# TFOESUU P19 independent sequential replay audit

**Date:** 2026-10-14. **Authority:** independent stand-alone CPU experiment written from the definitions in the user-provided 45-page manuscript; NOT the frozen PC1/PC2 P12/P15 campaign, and NOT a patch of an authenticated newest LaTeX source tree.

## Scientific question and preregistered contrast

Hold fixed a single simple null, a singleton alternative, and every four-call round's unit cost. Only change legal control access:

- Candidate high vertex `x` and high control `h` (matched group). Both old thresholds `p`; both new null thresholds `p+s+tau`; alternative increments only `x` by `d`. The old/new patch-delta contrast is pathwise zero under the null. A nonzero witness has probability `d` under the alternative; stop at first witness or `L=ceil(log(delta)/log(1-d))` rounds.
- Candidate high vertex `x` and low reference `l` (boundary-only group). Old thresholds `p`; high new null threshold `p+s+tau`, low new threshold `p+s`. The alternative increments high `x` by `d`. The ordered four-output transcript has atom probabilities changed from `(tau,r)` to `(tau+d,r-d)`, with `r=1-p-s-tau`. Use the **raw ordered four-output transcript** for the sequential log likelihood ratio, stopping on either logLR >= log(1/delta) or logLR <= log(delta). These thresholds provide one-sided risk bounds by Ville's inequality for the declared pair of simple hypotheses.

Both modes count four synthetic program evaluations per legal-group query. The physical execution count is **not** measured wall time. Distinct random streams were generated for each experimental condition.

Frozen before execution: `p=.30, s=.11, tau=.16, delta=.05`, patch sizes `[.025,.035,.05,.07,.10,.14]`, 2,400 independent trajectories for each of 2 group topologies and each truth assignment (24 cells; 57,600 trajectories), seed `20261014`. There is an 80,000-round fail-closed cap in the boundary test; all runs terminated before the cap. The example is a **synthetic common-uniform threshold program**, not a historical executable Fairlearn runtime.

## Results: observed average concrete executions on the null

| d | Matched controls | Boundary-only | Boundary / matched |
|---:|---:|---:|---:|
| 0.025 | 476.0 | 4292.1 | 9.02 |
| 0.035 | 340.0 | 2311.0 | 6.80 |
| 0.050 | 236.0 | 1186.7 | 5.03 |
| 0.070 | 168.0 | 625.2 | 3.72 |
| 0.100 | 116.0 | 326.9 | 2.82 |
| 0.140 | 80.0 | 169.5 | 2.12 |

Ordinary least-squares log-log fit to these **six observed finite-grid null means**: slope `-1.0316` (matched group), `-1.8731` (boundary-only group). They are not inferred theorem exponents. The within-configuration standard errors of the sample means appear in the CSV; the chart uses approximate 95% intervals for means. All 24 empirical error counts are in the CSV; the largest observed fraction was **125/2400 = 0.052083**, with Clopper-Pearson 95% CI approximately `[0.0435,0.0617]`. That value is just above the design target in one cell, consistent with Monte Carlo variability and not evidence of a risk guarantee violation. Bounds arise from test mathematics, not a finite frequency table.

## Exact mathematical checks and scope

- Six stand-alone tests passed, validating pathwise matched null equality, witness interval length, full boundary three-atom law and null-to-alternative KL, correct witness horizon, terminated sequential tests, and the `K_control ~ d` / `K_boundary ~ d^2` small-effect expansions.
- Neither this experiment nor the existing fixed-budget 198-configuration campaign proves the theorem, novelty, or performance on deployed software. This experiment does provide an **independently recorded variable-stopping-time concrete-execution measurement** on the exact simple P19 model.
- The matched control has a stronger legal access channel; equality of execution charges does **not** imply equal observation laws. Comparing the two is a controlled counterfactual about legal group topology, not a generic algorithmic speedup claim.
- Simultaneous alternatives, heterogeneous composite nulls, arbitrary control groups, unknown `d`, changing baseline or sample dependence remain outside scope.

## Reproduction and provenance

```bash
python -m pip install numpy scipy reportlab pymupdf pytest
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q test_p19_audit.py
python p19_sequential_audit.py --out results
python render_audit_figures.py
```

The SHA-256 of `p19_sequential_audit.py`, the recorded CSV, model parameters, seeds and all 24 results are frozen in `results/p19_audit_manifest.json`. The figure renderer refuses to proceed if the CSV hash does not match. Confirm that the current source SHA matches the manifest before claiming reproduction. This bundle makes no GitHub push, local PC1/PC2 changes, paid GPU call or Overleaf overwrite.

## Source authority and manuscript caveats

- New user-supplied PDF: `main(20261014-144546).pdf`; 45 pages; SHA-256 `bfb9a006c00fc4e760e13baceae02cf2e5f2f19aba5df1921d93f2328c662cc8`.
- GitHub private repository `Rocky5502/tfoesuu` main checked on 2026-10-14 and still pointed to `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b` (2026-10-08). The newer source appears local and is **not** available as the final Oct 13 ZIP in the inspected library. Never overwrite the newer PC1 local tree with GitHub main or an Oct 11 ZIP.
- The four-way differential in current PDF Eq. (38) is **correctly parenthesized** as `(P1(u)-P0(u))-(P1(v)-P0(v))`; the earlier concern was PDF text extraction ambiguity.
- A Table 3 appendix caption calls public benchmark populations `planned`. Distinguish unexecuted *theorem-aligned public-data wrapper* studies from the completed *historical Fairlearn seven-population census*, instead of globally changing tense.
- Fairlearn issue #728 (opened April 2021) and merged PR #763 (May 2021) establish that the protected-group name truncation was a known historical bug. Its recreation is valid engineering evidence, **not new defect discovery**. A source-level ancestry/hash check against the manuscript's exact pinned parent/child revisions remains necessary.
- **Outstanding release gates:** decisive theorem novelty vs controlled sensing, closest graph design, sequential sparse testing and CRN literature; full proof adversarial review of P19; access to the actual Oct 13 newest source ZIP; source/record revalidation; human author sign-off. Submission not authorized.

Reference URLs:
- https://acm-stoc.org/stoc2027/stoc2027-cfp.html
- https://github.com/fairlearn/fairlearn/issues/728
- https://github.com/fairlearn/fairlearn/pull/763
- https://doi.org/10.1111/sjos.12757
