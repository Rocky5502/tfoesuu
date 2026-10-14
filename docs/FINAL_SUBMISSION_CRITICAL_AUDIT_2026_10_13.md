# Final-submission critical audit — 2026-10-13

This is a private release-control checklist, not manuscript text. Rankings reflect
submission risk, not presentation order.

| Rank | Risk and evidence | Required resolution | Verification |
|---:|---|---|---|
| 1 | **P12/P15 100k evidence lacked an independent admission boundary.** The raw 54-row P12 and 144-row P15 files were recovered with the checkpointed hashes, but a reader could not previously prove complete-census identity, frozen schedules, or exact finite laws from one command. | Closed on this branch: add a fail-closed manifest/validator and corruption-first tests. Preserve the interpretation as sufficient-statistic validation, not instrumented software runtime. | `python scripts/validate_preview_results.py data/p12_p15_100k_preview_manifest_v1.json --base-dir .`; current report SHA-256 `cd6b4394bb87c42bb58861892b6eb1f05e7ef6ac084de50ebd6d864b8f5a20bb`; 198 rows, 594 exact binomial comparisons, zero Bonferroni outliers, and a machine-readable no-scaling-fit fence. |
| 2 | **CLOSED mechanically.** The editorial tree was reconciled into the tracked `paper/stoc2027_review` source without replacing the authoritative research sources. | Preserve the review tree and package only tracked source/evidence files. | Source-only ZIP: 31 entries, SHA-256 `dea6d44778c64ad827a3f02cc5cdb0b7e494c0fe78e25eb650a61d46ed9d618b`; clean extraction rebuilt successfully. |
| 3 | **CLOSED for automated adversarial review; human sign-off remains required.** P19's fixed-design `log m` factor, adaptive expected-null cost, deterministic cap, and singleton-alternative scope are separated in the theorem and claim ledger. | Human authors must independently verify every theorem before submission. | Five-reviewer audit, claim/proof-status consistency gates, exact absorbing-chain oracle, and full local test suite. |
| 4 | **CLOSED for recorded literature/policy audit; human originality sign-off remains required.** Generic conic, coupling, and sequential-testing ingredients are not claimed as new. | Recheck the live CFP immediately before upload and obtain author citation/originality approval. | Hostile P12--P19 novelty audit; official CFP reverified 2026-10-14; bibliography and first-12-content-page gates pass. |
| 5 | **CLOSED mechanically.** The source-only Overleaf ZIP was extracted into a clean temporary directory and compiled independently. | Preserve the immutable ZIP and rebuild after any later source edit. | 45 US-Letter, unencrypted pages; no overfull or unresolved-reference warnings; representative edited pages visually inspected; clean-extract PDF SHA-256 `b196c2aa4aade56b2d24edbfcefc02ef4846ca82fb7a24d72e35be1f526fedb0`. |

## Closed risk 1 evidence

- Frozen source commit: `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`.
- P12 result SHA-256: `f00458f50d225c8c5bde5cb235c6f67fbc67102157768369df8cd350956f1035`.
- P15 result SHA-256: `e0750e5d46215909aa710d83bca8ad748877e66f786aa9106e883ce94da274ab`.
- Validation result: all 198 rows present; all frozen schedules and specification fields exact; all empirical rates are trial-count proportions; 594 exact two-sided binomial checks; familywise threshold `8.417508417508418e-05`; minimum exact p-value `0.00046475515380564977`; maximum absolute deviation `0.002427090218361183`; zero outliers.
- Falsification tests reject result/spec/runner hash drift, wrong trial budgets,
  schedule drift, duplicate identifiers, and incomplete censuses.

This closes artifact admissibility for bounded validation evidence. It does not
turn the simulations into wall-clock, end-to-end, or public-dataset evidence.
