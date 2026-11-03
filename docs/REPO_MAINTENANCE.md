# Repository maintenance and source archive boundary

The current working tree is a **code-only research artifact**: packages, tests,
synthetic benchmark specifications, reproducibility evidence, and reviewer guidance.
The manuscript/Overleaf source is intentionally maintained separately.

## Scientific immutability

Do not silently edit frozen JSONL/CSV result rows, original source snapshots,
manifest identities, or declared theorem assumptions. Changes to these require
a new independently labeled release and a verified provenance comparison.

The archived manuscript remains retrievable from the history of the private
research repository. **Deleting `paper/` from the current tree does not erase
historical Git blobs.** A public release with a clean history is a separate,
permission-gated operation. Third-party datasets, Fairlearn software, and ACM
publisher templates have their own rights and terms; the root MIT license does
not override them.

## Code review and release branch policy

- `main`: reviewed working tree with the current implementation and frozen inputs.
- `research/*`: proposed theory, falsification tests, and bounded experiments.
- `release/*`: documentation, artifact relocation, and reviewer-readiness changes.

Reviewers should start with [REVIEWER_GUIDE.md](REVIEWER_GUIDE.md). CI must run
the code-only tests and independent evidence checks; no paper compilation
belongs in the code-release workflow. A new public repository must be
constructed from a verified allowlist and a fresh Git history, after full
license, secret-history, and dependency scanning.

## Prohibited release shortcuts

Never claim that paper deletion rewrites history, that a configured CI
workflow passed, that fixed-budget simulations measure sample-complexity
slopes, or that historical Fairlearn grouping differences measure causal
discrimination. Code-only maintenance must not silently revise the research
claims or the submission archive.
