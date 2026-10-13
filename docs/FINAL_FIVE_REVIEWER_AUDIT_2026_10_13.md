# Final five-reviewer audit — 2026-10-13

This record separates independent reviewer findings from authoring changes.
The five reviews were read-only; the principal research agent implemented and
validated all accepted repairs.

## R1 — Gaussian graph theory: GO

Verified the active-vertex domain of `Psi`, existence of the minimum, the
`|V_+(H)|` rounding term, dual, canonical graph domains, homogeneous scaling,
and zero calls for an edgeless residual graph. The numerical runner now rejects
failed or infeasible optimizer outputs. Final targeted audit: 12 tests passed.

## R2 — Bernoulli/replay theory: GO

Verified that Gaussian delta observations and raw pair/edge/suite/group
transcripts are distinct primitives. P12, P15, P16, P18, and P19 now state
their probability domains, independent-round assumptions, fixed-parameter
asymptotics, null classes, and execution units explicitly. P16's homogeneous
single-changed-endpoint family is self-contained. Final focused audit: 91 tests
passed.

## R3 — experiments and reproducibility: GO for scoped evidence

Independently recomputed all 198 P12/P15 records and 594 exact finite-law
comparisons: zero familywise-Bonferroni outliers, minimum exact p-value
`0.00046475515380564977`, and maximum absolute deviation
`0.002427090218361183`. Raw hashes and all four frozen runner/spec Git blobs
match source commit `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`.
The release now contains raw records, frozen specs, admitted runner snapshots,
manifest, report, and README. Claims remain implementation/oracle-law
validation only, not proof, runtime, or software-benchmark evidence.

## R4 — novelty and closest work: GO

Added and explicitly contrasted Yan--Zhang (fixed-model active fairness
auditing), Buselli et al. (group-level unfair regression after model updates),
and Ajarra--Basu (SP dimension for auditing statistical parity after strategic
updates). The Gaussian design contribution is contrasted with prior max--min
graph design. Removed the unsupported phrase “new control-cover geometry” and
fixed the malformed Gießing author escape. Closest-work positioning appears
within the first twelve content pages.

## R5 — holistic STOC exposition/compliance: conditional findings resolved

Removed duplicate Gaussian/Bernoulli proof inclusions, reducing the review PDF
from 58 to 44 pages while preserving complete formal proofs once. The opening
now identifies principal theorem groups and adds the mixed-topology row. The
100k evidence language is synchronized, the AI methodology remains at the end,
and stale two-column entry points were removed from the review-only release.

## Final mechanical gate

- Full Python suite: 324 passed.
- Ruff on all touched Python files: passed.
- `git diff --check`: passed.
- Bundled Tectonic: 44-page US Letter PDF; no undefined citation/reference,
  duplicate-label, or overfull-box warning.
- Visual inspection: all 44 rendered pages checked; no clipping, overlap,
  blank internal page, or unreadable figure/table.
- PDF SHA-256:
  `1197c6b14a57f567b680916cdb67510459517dedccf669917f1052ef8e355b79`.

These reviews do not replace human-author and coauthor responsibility or venue
submission checks.
