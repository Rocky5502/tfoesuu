# STOC 2027 submission compliance checklist

Source of truth: official STOC 2027 Call for Papers. Policy snapshot re-checked
on 2026-10-06; re-check the live CFP again immediately before submission in case
instructions change.

## Dates

- [ ] Paper submitted by **November 2, 2026, 11:59 p.m. AoE**.
- [ ] Required author video submitted by **November 16, 2026, 11:59 p.m. AoE**.
- [ ] If accepted, camera-ready prepared by **April 1, 2027**.

## Authorship and public posting

- [ ] Replace the manuscript author placeholder with all human author names and affiliations. STOC 2027 is non-anonymous.
- [ ] Confirm every listed author is human and accepts responsibility for the complete submission.
- [ ] Check that no author appears on more than five STOC 2027 submissions.
- [ ] All authors consent to STOC publicly posting the submitted paper through the conference submission process.
- [ ] All authors explicitly consent to PC members/sub-reviewers using LLMs to assist with reviewing the public submission, as required by STOC 2027.
- [ ] Check prior/simultaneous-submission compliance immediately before upload.
- [ ] Record all required conflicts of interest accurately.
- [ ] Ensure authors have ORCID IDs for the ACM publication process.

## Submission channel and manuscript

- [ ] Submit the final PDF through the official STOC 2027 HotCRP site by the deadline.
- [ ] Confirm the uploaded PDF is the exact version approved by all authors for mandatory public posting.
- External repository posting (for example arXiv, ECCC, or IACR ePrint) is **recommended but not required** by the current STOC 2027 CFP.


- [x] 11-point type.
- [x] Single-column submission format.
- [x] Letter paper.
- [x] One-inch margins.
- [x] Hyperlinked cross-references via hyperref/cleveref.
- [x] Alphanumeric bibliography style.
- [ ] Title page contains final title, human authors/affiliations, and a contribution-focused abstract.
- [ ] First 10–12 pages clearly explain importance, prior-work context, central technical ideas, theorem statements, and proof intuition to a broad TCS audience.
- [ ] Main mathematical claims have proofs sufficient for verification.
- [ ] References are placed at the end of the full submission.
- [ ] Final PDF has no security restrictions on copying or printing.
- [ ] Final manuscript consistency and bibliography checks pass.
- [ ] Final LaTeX CI build passes from a clean checkout.

## Generative-AI disclosure

Substantive generative-AI use must be disclosed. This project uses ChatGPT for
research ideation, literature triage, proof exploration, code drafting, and
manuscript structuring, so the disclosure is mandatory.

Before submission:

- [ ] AI Methodology statement identifies ChatGPT/OpenAI.
- [ ] It states which manuscript/research components were materially influenced.
- [ ] Every theorem and proof has been independently checked by the human authors.
- [ ] Every citation has been independently verified against an archival source.
- [ ] Every implementation/result used in the paper has been reproduced by the human authors from the frozen repository commit.
- [ ] No AI system is listed as an author.
- [x] No pretrained model, open-source model, proprietary model API, or LLM is an experimental subject or research oracle.

## Required video

- [ ] Prepare a 20–30 minute recording presented by at least one listed author.
- [ ] Explain context, innovations relative to prior work, intuition, and proof structure.
- [ ] Do not introduce claims or missing proofs that are absent from the paper.
- [ ] Submit by the video deadline.

## Artifact/reproducibility gate

- [ ] Freeze submission git SHA.
- [ ] Generate the whole-submission checksum manifest with `scripts/freeze_submission_artifacts.py --require-clean`.
- [ ] Freeze benchmark manifests and SHA-256 hashes, including the 168-row P17 stress grid and the separate 8-row P17 structural-case manifest.
- [ ] Run CPU CI from a clean checkout.
- [ ] Run staged GPU publication sweeps only on frozen theorem configurations.
- [ ] Record GPU names, NVIDIA driver, CUDA/PyTorch versions, exact commands, benchmark hashes, output hashes, and git SHA.
- [ ] Archive the exact Overleaf-ready paper source and compiled PDF.
- [ ] Verify all result tables/figures trace to immutable result manifests.

## Proceedings note

The STOC submission itself has no page limit, but the accepted proceedings
version is limited to 12 pages and uses ACM acmart sigconf formatting.
Do not prematurely force the submission manuscript into proceedings format.
