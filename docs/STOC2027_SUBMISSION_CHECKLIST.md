# STOC 2027 submission compliance checklist

Source of truth: the [official STOC 2027 Call for Papers](https://acm-stoc.org/stoc2027/stoc2027-cfp.html).
Re-check the live CFP before submission in case instructions change. Last
live-CFP verification: **2026-10-14**.

## Dates

- [ ] Paper submitted by **November 2, 2026, 11:59 p.m. AoE**.
- [ ] Required author video submitted by **November 16, 2026, 11:59 p.m. AoE**.
- [ ] If accepted, camera-ready prepared by **April 1, 2027**.

## Authorship and public posting

- [x] Title page lists the three human authors, affiliations, contact details,
  and ORCIDs. STOC 2027 is non-anonymous.
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
- [x] Title page contains the final title, human authors/affiliations, and a contribution-focused abstract.
- [x] Dedicated title/abstract page is separated from the technical manuscript.
- [x] Reviewer-navigation table of contents appears immediately after the title page; the official CFP says this page does not count toward the first twelve pages.
- [x] First **12 content pages following the title/optional contents pages** explain importance, prior-work context, central technical ideas, theorem statements, and proof architecture. Human-author sign-off remains required.
- [x] Main mathematical claims have complete proofs in the compiled review source. Human proof certification remains required.
- [x] The mandatory AI Methodology disclosure is placed at the end of the paper body immediately before the final bibliography.
- [x] Audited local PDF has no security restrictions on copying or printing.
- [x] Final manuscript consistency, equation-label, cross-reference, and bibliography checks pass.
- [x] Final LaTeX build passed from a clean extraction of the Overleaf package.
  The pushed branch matches locally; GitHub-hosted CI is externally blocked by
  the account spending limit, so the complete local gate is the current
  machine-verifiable release evidence.

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

- [ ] Freeze the final submission Git SHA after human-author sign-off; the current audited research branch is recorded in the execution ledger.
- [ ] Generate the whole-submission checksum manifest with `scripts/freeze_submission_artifacts.py --require-clean`.
- [x] Freeze benchmark manifests and SHA-256 hashes, including the 24-row P18 phase grid, the 168-row P17 stress grid, the separate 8-row P17 structural-case manifest, and the deterministic P17 scope-falsification manifest.
  Their SHA-256 values are respectively `d73c9e8d065ae2e5efe617fd31900d70d8cf7eae858d17498b5ceb8741bf8ff9`,
  `fa61d7820dd5d911ae6c9bcd506ad5b26e7313f63b048e2b6db148318c585942`,
  `78d4ddf3514528bc54a6c99481ad8d02830516dd80f7730d493d4774b9a349c3`, and
  `9759ad422d50bb8477280b1901020d5095f3d8f1d50f0a2d788c612a4acf2442`.
- [x] Run the complete local CPU suite and manuscript static gates; 336 tests passed at the latest repository release gate. GitHub-hosted CI remains blocked by the external account spending limit.
- [x] Run the 168-row P17 executable manifest validator and archive its deterministic validation summary. The checked-in theorem tests re-execute every row; `scripts/summarize_submission_evidence.py` reports the 821-row theorem-facing inventory and exact scope counterexample.
- [x] Run the authorized frozen P12/P15 campaigns through 100,000 trials per configuration; do not infer authorization for larger campaigns.
- [ ] Complete the historical GPU environment record. GPU names,
  CUDA/PyTorch versions, exact commands, benchmark/output hashes, worker
  assignment, and frozen Git SHA are recorded; the driver-version field was
  not captured in the immutable 100k result manifest and must not be inferred
  retrospectively from the current machines.
- [x] Archive the exact Overleaf-ready source and compiled PDF outside Git; generated manuscript artifacts are intentionally not pushed to the repository.
- [x] Verify submission-facing result tables/figures against immutable admission manifests and source hashes.

## Proceedings note

The STOC submission itself has no page limit, but the accepted proceedings
version is limited to 12 pages and uses ACM acmart sigconf formatting.
Do not prematurely force the submission manuscript into proceedings format.
