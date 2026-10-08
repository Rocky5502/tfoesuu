# Codex hourly checkpoints

## 2026-10-08T09:42:20Z — session `codex-20261008-a`

- Actual SHA/state: PC1 and PC2 both
  `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`; PC1 baseline clean before creating
  `codex/research-audit-20261008`.
- Completed: read master directive and required project documents; inventoried source/tests/CI;
  verified local/remote environments; captured read-only prepared file list, byte sizes, SHA-256s,
  manifest metadata, and seven population counts.
- Commands and outcomes: `compileall` exit 0; PC1 `pytest` 194 passed in 8.31s;
  benchmark inventory 828 rows exit 0; bibliography exit 0; paper static check exit 0;
  Ruff exit 1 with 107 pre-existing findings; PC2 preflight exit 0 with 194 tests in 4.66s;
  PC2 CUDA binomial kernel passed. No GPU experiment was launched.
- Prepared manifest SHA-256:
  `c8a0b3419322627cc3660f8d9e8e5095234644b7ce54036cd3b4f27a5ecdfc89`.
- Prepared NPZ SHA-256s: Adult `848a098c...e50d71`; Bank `f37ec608...7d9b`;
  COMPAS `62e35ea1...266a`; Default Credit `7c24e5d4...b36f`; German
  `4be96354...d7cf`; Law School `c9b905fa...c041`; MEPS `e0f4fb94...3090`.
- Claim status: no theorem status changed. The prepared-input validation weakness is
  `COMPUTATIONALLY_CHECKED` by source inspection; regression tests are being added before repair.
- Risks/next task: make public execution fail closed with a strict read-only prepared-data validator,
  then run focused and full tests and validate the PC2 snapshot through the new code.
- Approval gate reached: NO. Publication-scale computation remains gated and was not attempted.

### Checkpoint update — prepared-input repair

- Added a strict read-only validator and CLI; the public GPU runner now invokes it before CUDA work.
- Red test: new test module initially failed collection because the validator was absent.
- Green evidence: 15 focused tests passed; then 203 full tests passed in 7.90s. Changed-file Ruff,
  compileall, bibliography, and paper static checks pass.
- The validator was streamed read-only to PC2 and accepted exactly seven IDs, 15 artifacts, one
  frozen source commit, finite clipped probabilities, binary aligned labels, coherent metadata, and
  the manifest. It reproduced the previously captured artifact SHA-256 values.
- Scientific correction: code inspection falsified the documented claim that v1 materializes pairs
  by changing protected attributes. The actual runner duplicates each scalar `p0` into a synthetic
  two-endpoint edge. Protocol, runbook, README, and manuscript now state this limitation explicitly.
- GPU jobs: none. Approval gate reached: NO.
- PDF closure: static manuscript consistency passes. The LaTeX skill wrapper and direct MiKTeX
  `latexmk` both produced no output and were terminated after bounded waits; no PDF result is
  claimed. This is an environment/toolchain blocker, not a manuscript compile diagnostic.

### Checkpoint update — dual-GPU exploratory smoke

- PC1 ran all 144 frozen P15 configurations at 1,000 trials on CUDA from isolated baseline
  `149baf36`; result SHA-256 `256a11155bfb8faf42c5be1cb18b03fd9458434a1577bb69f17feff5db573527`.
- PC2 ran all 54 frozen P12 configurations at 1,000 trials on CUDA from clean baseline `149baf36`;
  result SHA-256 `6d38a3e103908a42d37bf0274ea658cf2873ecd667cb2117ec07d8233c097d2d`.
- Exact finite-law audit: 594 binomial comparisons, Bonferroni threshold
  `8.417508417508418e-05`, zero outliers. These are exploratory smokes, not publication evidence.
- Cross-platform provenance finding: P12's committed Git blob was identical on both PCs
  (`fd8b653879e2958059738cb842f2bf76bc73a7b8`), but raw SHA-256 differed because PC1 checked out
  CRLF and PC2 LF. Added portable LF-normalized hashing, Git-blob logging, and an LF attribute for
  frozen JSONL manifests.
- GPU jobs: complete; no larger trial budget launched. Approval gate reached: NO.
