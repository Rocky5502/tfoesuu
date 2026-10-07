# STOC 2027 submission compliance checklist

Source of truth: official STOC 2027 Call for Papers. Re-check the live CFP before
submission in case instructions change. Last live-CFP verification: **2026-10-08**.

## Dates

- [ ] Paper submitted by **November 2, 2026, 11:59 p.m. AoE**.
- [ ] Required author video submitted by **November 16, 2026, 11:59 p.m. AoE**.
- [ ] If accepted, camera-ready prepared by **April 1, 2027**.

## Authorship and public posting

- [ ] Replace the manuscript author placeholder with all human author names and affiliations. STOC 2027 is non-anonymous.
- [ ] Confirm every listed author is human and accepts responsibility for the complete submission.
- [ ] Check that no author appears on more than five STOC 2027 submissions.
- [ ] All authors consent to STOC publicly posting the submitted paper.
- [ ] All authors explicitly consent in HotCRP to PC members/sub-reviewers using LLMs to assist with evaluation of the publicly posted paper.
- [ ] Check prior/simultaneous-submission compliance immediately before upload.
- [ ] Record all required conflicts of interest accurately.
- [ ] Ensure authors have ORCID IDs for the ACM publication process.
- [ ] Decide whether to mirror the public STOC submission in an established repository (e.g., arXiv/ECCC); this is recommended by STOC but not required.

## Submission manuscript

- [x] 11-point type.
- [x] Single-column submission format.
- [x] Letter paper.
- [x] One-inch margins.
- [x] Hyperlinked cross-references via hyperref/cleveref.
- [x] Alphanumeric bibliography style.
- [ ] Title page contains final title, human authors/affiliations, and a contribution-focused abstract.
- [x] Dedicated title/abstract page is separated from the technical manuscript.
- [x] Reviewer-navigation table of contents appears immediately after the title page; the official CFP says this page does not count toward the first twelve pages.
- [ ] First **12 pages following the title page** clearly explain importance, prior-work context, central technical ideas, theorem statements, and proof intuition to a broad TCS audience.
- [ ] Main mathematical claims have proofs sufficient for verification.
- [x] Bibliographic references are at the end of the technical manuscript; the mandatory AI Methodology disclosure follows them as the final paper statement.
- [ ] Final PDF has no security restrictions on copying or printing.
- [ ] Final manuscript consistency and bibliography checks pass.
- [ ] Final LaTeX CI build passes from a clean checkout.

## Generative-AI disclosure

Substantive generative-AI use must be disclosed. This project uses ChatGPT for
research ideation, literature triage, proof exploration, code drafting, and
manuscript structuring, so the disclosure is mandatory.

Before submission:

- [x] AI Methodology statement identifies ChatGPT/OpenAI.
- [x] It states that research ideation, literature triage, proof exploration, implementation/test drafting, and manuscript drafting/structuring were materially influenced, and identifies the affected manuscript/artifact scope.
- [ ] Every theorem and proof has been independently checked by the human authors.
- [ ] Every citation has been independently verified against an archival source.
- [ ] Every implementation/result used in the paper has been reproduced by the human authors from the frozen repository commit.
- [x] No AI system is listed as an author.
- [x] No pretrained model, open-source model, proprietary model API, or LLM is an experimental subject or research oracle.

## Required video

- [ ] Prepare a 20–30 minute recording presented by at least one listed author.
- [ ] Explain context, innovations relative to prior work, intuition, and proof structure.
- [ ] Do not introduce claims or missing proofs that are absent from the paper.
- [ ] Submit by the video deadline.

## Artifact/reproducibility gate

- [ ] Freeze submission git SHA.
- [ ] Generate the whole-submission checksum manifest with `scripts/freeze_submission_artifacts.py --require-clean`.
- [ ] Freeze benchmark manifests and SHA-256 hashes, including the 24-row P18 phase grid, the 168-row P17 stress grid, the separate 8-row P17 structural-case manifest, and the deterministic P17 scope-falsification manifest.
- [ ] Run CPU CI from a clean checkout.
- [ ] Run the 168-row P17 executable manifest validator and archive its deterministic validation summary.
- [ ] Run staged GPU publication sweeps only on frozen theorem configurations.
- [ ] Record GPU names, NVIDIA driver, CUDA/PyTorch versions, exact commands, benchmark hashes, output hashes, and git SHA.
- [ ] Archive the exact Overleaf-ready paper source and compiled PDF.
- [ ] Verify all result tables/figures trace to immutable result manifests.

## Proceedings note

The STOC submission itself has no page limit, but the accepted proceedings
version is limited to 12 pages and uses ACM acmart sigconf formatting.
Do not prematurely force the submission manuscript into proceedings format.
