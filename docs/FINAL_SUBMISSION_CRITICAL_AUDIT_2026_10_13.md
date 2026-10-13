# Final-submission critical audit — 2026-10-13

This is a private release-control checklist, not manuscript text. Rankings reflect
submission risk, not presentation order.

| Rank | Risk and evidence | Required resolution | Verification |
|---:|---|---|---|
| 1 | **P12/P15 100k evidence lacked an independent admission boundary.** The raw 54-row P12 and 144-row P15 files were recovered with the checkpointed hashes, but a reader could not previously prove complete-census identity, frozen schedules, or exact finite laws from one command. | Closed on this branch: add a fail-closed manifest/validator and corruption-first tests. Preserve the interpretation as sufficient-statistic validation, not instrumented software runtime. | `python scripts/validate_preview_results.py data/p12_p15_100k_preview_manifest_v1.json --base-dir .`; report SHA-256 `32ea2d88d6475c4880d607e13023151e3f84c4a78eac05ee5e0be64b37d5c9c5`; 198 rows, 594 exact binomial comparisons, zero Bonferroni outliers. |
| 2 | **The supplied editorial Overleaf tree is external to Git.** Its archival source matches commit `5c115824`, but several review-facing section files and the source organization differ. | Reconcile into a separate submission tree without overwriting the authoritative research sources; compile and compare claims before packaging. | Clean Git diff, source inventory, bibliography check, deterministic build, and ZIP hash. |
| 3 | **Final independent theorem sign-off is incomplete.** Earlier audits found that P19's fixed-design `log m` factor and adaptive expected-cost behavior must be separated, and the hybrid upper bound is valid only for the scoped singleton-alternative family. | Audit the final theorem statements against those quantifiers and complete independent Gaussian/Bernoulli reviewer passes. | Claim-by-claim reviewer records plus proof-status consistency tests. |
| 4 | **Novelty/citation and current STOC-policy review is not yet closed.** The final prose must not promote standard conic machinery or generic coupling as novelty, and venue rules can change. | Check all central positioning claims against primary sources and verify the official STOC 2027 call directly. | Private citation audit with URLs/access dates; bibliography and first-12-content-page checks. |
| 5 | **A clean final review build has not yet been reproduced from the supplied ZIP.** The generic helper selected `preamble.tex`, while a direct bundled-Tectonic attempt stalled before producing output. | Use the installed TeX Live toolchain on the reconciled submission tree; render and inspect every page in color and representative grayscale. | Zero fatal errors/overfull boxes, page inventory, visual QA record, PDF and ZIP SHA-256 values. |

## Closed risk 1 evidence

- Frozen source commit: `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`.
- P12 result SHA-256: `f00458f50d225c8c5bde5cb235c6f67fbc67102157768369df8cd350956f1035`.
- P15 result SHA-256: `e0750e5d46215909aa710d83bca8ad748877e66f786aa9106e883ce94da274ab`.
- Validation result: all 198 rows present; all frozen schedules and specification fields exact; all empirical rates are trial-count proportions; 594 exact two-sided binomial checks; familywise threshold `8.417508417508418e-05`; minimum exact p-value `0.00046475515380564977`; maximum absolute deviation `0.002427090218361183`; zero outliers.
- Falsification tests reject result/spec/runner hash drift, wrong trial budgets,
  schedule drift, duplicate identifiers, and incomplete censuses.

This closes artifact admissibility for bounded validation evidence. It does not
turn the simulations into wall-clock, end-to-end, or public-dataset evidence.
