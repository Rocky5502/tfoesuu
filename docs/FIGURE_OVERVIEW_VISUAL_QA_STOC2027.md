# STOC 2027 Overview Figure: Design and Evidence Audit

Date: 2026-10-08
File: `paper/figures/overview_pipeline.tex`
Placement: `paper/main.tex` immediately after the introduction.
Format: editable vector TikZ; 11 pt single-column STOC submission.
Figure width: 15.95 cm, below the 16.51 cm text block.

## Scientific message

TFOESUU is an evidence-reuse / oracle-access testing theory:
archived certificates and sound patch envelopes prune safe edges; the
remaining statistical testing problem depends on which versions and inputs
can share a replayed random tape. Theorems P4–P19 supply different, scoped
allocations and testing results. P20 is conjectural and must not be
visually presented as a proved algorithm.

## Visual constraints and corrective action

The previous diagram placed five wide text panels on one horizontal line
inside a `\\resizebox{\\textwidth}{!}{...}`, introduced teal/red styling,
and included a dense colored scope-warning panel. That structure reduced
type size at final print width and mixed proposed and proved claims.

The replacement:
- uses only black, white, and grayscale;
- has no `resizebox`, colored emphasis, or embedded bitmap;
- separates deterministic certificate reuse from stochastic replay access;
- aligns exactly three replay primitives with three scoped theorem families;
- reports concrete execution accounting next to replay capabilities;
- places P20 in a dashed, clearly conjectural footer;
- keeps the explanation in the manuscript caption and source text.

The formula `h_e^+=tau_e-g_{0,e}`,
`h_e^-=tau_e+g_{0,e}` is directional headroom, not a
claim that headroom alone yields a new minimax theorem. Gaussian `Psi`,
the homogeneous `C_vert`, and P19 matched-control `C_ctrl` are scoped
according to `docs/PROOF_STATUS.md`.

## Prior STOC work and venue-facing lessons

Consulted archival proceedings, not unreviewed preprints:

1. **STOC 2025, Cameron Seth, _A Tolerant Independent Set Tester_.**
   The accepted proceedings study tolerant graph testing and explicitly
   separate access model, tolerance promises, statistical guarantees and
   complexity. This is contextual precedent for exact model/guarantee
   statements, *not* a theorem being reused in the figure.
   Proceedings: https://acm-stoc.org/stoc2025/toc.html

2. **STOC 2026, Mark Chen, Xi Chen, Hao Cui, William Pires, Jonah
   Stockwell, _Boolean Function Monotonicity Testing Requires (Almost)
   n^{1/2} Queries_.** ACM STOC 2026, pp. 584–594,
   DOI: 10.1145/3798129.3800775.
   Its adaptive-query lower-bound framing reinforces the need to distinguish
   information access, exact model and proved bound. It is *not* a direct
   fairness-regression theorem or novelty collision.
   Publisher: https://doi.org/10.1145/3798129.3800775

3. **STOC 2026 proceedings** were checked for recent theorem-first
   presentation practices: https://acm-stoc.org/stoc2026/toc.html.

These were used to guide *presentation and scope discipline*. No
theorem or experimental result was imported from them.

## Rendering and QA

A standalone figure preview was compiled locally using
`latexmk -pdf -interaction=nonstopmode -halt-on-error` with system
TeX Live, then rasterized for manual visual inspection at final-size
figure width. The final preview shows separated panels, legible
footnotes and equations, no compression, monochrome-compatible structure,
and no overlapping text. The figure remains editable TikZ.

The isolated preview is not a replacement for a clean build of the
complete `paper/main.tex`. The full manuscript, bibliography and
cross-references must be compiled and visually audited at the final
source SHA before submission.

## Remaining research/publishing gates

- Independently recheck claims P4–P19 against proofs.
- Keep P20 as an open conjecture; no empirical/result icon is permitted.
- Compile full `paper/main.tex` from a clean checkout.
- Confirm the overview remains inside the first 12 technical pages,
  and its caption does not displace the main theorem narrative.
- Confirm the synchronized source appears in any external Overleaf project
  if the GitHub/Overleaf sync is enabled. No separate Overleaf write
  was performed in this work session.
