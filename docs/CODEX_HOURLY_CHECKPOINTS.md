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

## 2026-10-08T17:05:41Z — session `codex-20261009-hourly-a`

- Self-check: research branch clean at `1e1490e2fe08e6ebd07c8d234262538ea66a49ba`;
  isolated PC1 execution worktree and PC2 clean `main` both at frozen
  `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`; both RTX 5070 Ti devices idle and
  CUDA-visible before launch; PC2 D: had 1.3 TiB free.
- Authorized 10,000-trial stage completed with unique output names and no overwrite:
  PC1 P15, 144 rows, UTC 17:05:10--17:05:15, result SHA-256
  `a6f4fece81ed06d579edb9c297c3375ff64dc55a429ca64f3d1bfda4d3f8e9d7`;
  PC2 P12, 54 rows, UTC 17:05:20--17:05:23, result SHA-256
  `2c9f46906eacd67b987ef2ecb5a58bda345d9fbc78b1b0b7999961769eb224a7`.
- Exact validation recomputed every analytic schedule and finite binomial law: 594 comparisons,
  Bonferroni familywise threshold `8.417508417508418e-05`, zero outliers. Largest absolute
  empirical-minus-exact deviation across the six metric families was `0.005136753812386062`
  (P15 edge-coupled alternative miss); this is exploratory Monte Carlo variation, not a theorem
  discrepancy.
- GPU jobs are finished; no process remains authorized to continue. No public-dataset GPU sweep,
  100,000-trial run, or manuscript result admission was attempted.
- Approval gate reached: YES for 100,000 trials or larger; fresh approval required.
- Next independent task: continue formal/statistical audit and repair the local PDF toolchain while
  keeping frozen data/source compatibility explicit.

### Checkpoint update — authorized 100,000-trial dual-GPU preview

- Fresh preflight: both frozen execution trees clean at `149baf36`; both GPUs idle, CUDA-visible,
  and had more than 14 GiB free. The research branch remained clean at `f9128c5` before logging.
- PC1 P15: 144 frozen configurations at 100,000 trials, UTC 17:06:40--17:06:44, result
  SHA-256 `e0750e5d46215909aa710d83bca8ad748877e66f786aa9106e883ce94da274ab`.
- PC2 P12: 54 frozen configurations at 100,000 trials, UTC 17:06:50--17:06:53, result
  SHA-256 `f00458f50d225c8c5bde5cb235c6f67fbc67102157768369df8cd350956f1035`.
- Exact audit: all IDs unique/complete, every recomputed schedule matched, and 0 of 594 exact
  binomial tests crossed the Bonferroni threshold `8.417508417508418e-05`. Minimum exact p-value
  was `0.00046475515380564977`; largest absolute empirical/exact difference was
  `0.002427090218361183` (P12 paired alternative miss, row `r0019`).
- These remain controlled sufficient-statistic previews, not measured service runtime and not a
  seven-public-dataset publication matrix. Both GPU jobs finished; no background job remains.
- Approval gate reached: YES for million-trial or public-dataset publication campaigns.

### Checkpoint update — preparation/execution compatibility contract

- Falsification tests were added first: unrelated execution-code changes must remain compatible;
  any change to a preparation-contract file must fail closed.
- Implemented `tfoesuu-public-preparation-compatibility-v1` over the exact Git blobs for the public
  preparation script, frozen registry, and public dependency contract. Public result rows now carry
  preparation SHA, execution SHA, and contract SHA-256; the publication release gate requires all
  three and rejects mixed or partial provenance.
- Real baseline-to-research-branch check passed before the compatibility commit: preparation SHA
  `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`, execution SHA
  `b6ee17d233702915dfe6774e532ea02b7671245d`, contract SHA-256
  `b12985f536e2465e67300d62b76b59a8196a0b91dd1167287bfabe08613a7e13`.
- Validation: 39 focused tests and 208 full tests passed; changed-file Ruff, compileall,
  bibliography, and manuscript static checks passed.
- Dataset decision: retain the preregistered seven populations. No post-outcome dataset was added
  without a specific scientific coverage gap and a new protocol version.

## 2026-10-09 — dual-GPU public smoke and P19 sharpening

- PC2 received commit `087f64fb06be0eaaddc1ee5106ec567854751593` through a verified Git bundle
  and created an isolated detached worktree; its baseline checkout stayed at `149baf36`.
- Both machines independently validated all 15 prepared artifacts and the preparation/execution
  contract `b12985f536e2465e67300d62b76b59a8196a0b91dd1167287bfabe08613a7e13`.
- Complete 1,000-trial public smoke: PC1 ran Adult, German, MEPS, and COMPAS (80 rows; SHA-256
  `8d7ce8817264186e1b0701b7375ec7e5c846e4e8b7d5b87bcb9e4c6b91c84f33`); PC2 ran Bank,
  Law School, and Default Credit (60 rows; SHA-256
  `8d082247de450f93e73cf518bd2d07a5fe35e2e2a34d895790e5371d1f44621c`).
- The merged 140-row matrix covers seven datasets, four patch sizes, and five methods; SHA-256
  `d10dfea15e9ded19f645d5e7a719aaa4d1e8e194ba025e633d677478c123da25`. All type-I counts
  were zero. Across the 28 distinct synchronized-witness configurations, exact binomial auditing
  found zero Bonferroni outliers (minimum p-value `0.08532118556935754`). This is exploratory,
  not publication evidence.
- Formal audit found that an unmatched P19 candidate cannot share a group with another high
  candidate. This removes a false cross-coverage concern and yields exact d^-2 and d^-1
  coefficients for the finite mixed-topology information lower LP. Adversarial tests cover all
  curvature signs, extreme topologies, diverse costs, and unobservability.
- Validation: 213 tests passed from an isolated task-specific pytest temp root; touched-file Ruff,
  compileall, the 828-row benchmark inventory, bibliography policy, and full manuscript static
  consistency passed. The LaTeX compile wrapper first exposed a Windows code-page bug and then
  hung silently in the installed TeX toolchain after UTF-8 correction; it was terminated after a
  bounded wait, so no fresh local PDF is claimed.
- Official STOC 2027 CFP was rechecked: non-anonymous submission; first twelve pages following the
  title page carry the exposition burden; mandatory public posting; 20--30 minute author video;
  substantive AI methodology disclosure. The local compliance checklist is current as of
  2026-10-09.
- Overleaf account inspection found no project matching TFOESUU, the paper title, or STOC. A new
  import was staged from `TFOESUU_STOC2027_26383fa_overleaf.zip` (SHA-256
  `41c8ac87107104e3da8dbe4d6f0df3fe806591e1b653f0ab4114529b5d48fce5`), but Chrome blocked the
  file transfer because the ChatGPT browser extension lacks file-URL access. No Overleaf project
  was created or modified; the upload dialog remains open for user handoff.
- Approval gate reached: YES for a 100,000-trial public publication campaign. It was not launched.
