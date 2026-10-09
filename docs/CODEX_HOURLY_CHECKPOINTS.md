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

## 2026-10-09 01:30 +08:00 — benchmark semantics checkpoint

- Corrected a stale replay-phase contract statement: mixed P19 lower-program asymptotics are
  proved, but a scalar control-coverage fraction does not determine the topology-dependent
  coefficients and no matching mixed-topology upper tester is known. The frozen v1 grid therefore
  keeps only topology-complete extremes for the correct reason.
- Re-ran the finite mixed-topology falsification search at `d=10^-4`. A representative topology
  with one unmatched candidate had exact `A0=0.4542848710713936`,
  `B0=5.173799920535316`, half-step cost ratio `3.997725336698979`, and two-term scaled residual
  error `-0.000771774831642702`; no counterexample was exposed by this bounded search.
- Rejected count-driven addition of five or six ordinary datasets. Preregistered one targeted v2
  candidate instead: the Themis executable subject suite at upstream commit
  `a70f12a6a8f34cdd8b170b4dc59a78674c9e8950`, with license, dependency, genuine protected-input,
  transcript, random-tape, and measured-subprocess gates. No external subject outcome was run or
  admitted.
- Validation: 214 tests passed from an isolated task-specific pytest temp root; touched-file Ruff,
  compileall, manuscript static consistency, bibliography policy, and the 828-row benchmark
  inventory all passed.
- Read-only Themis feasibility gate: exact commit cloned detached/clean outside the repository;
  license hash recorded; no dependency lock found; Python-2-only interfaces and mixed Python/C++/
  Java subject stacks identified. The compact system-G wrapper is deterministic and has no
  historical old/new pair, so it is admitted only as a possible external baseline, not a replay or
  evolving-software result. No dependency was installed and no subject outcome was executed.
- GPU/status audit: no PC2 WSL compute process was reported; PC2's protected main checkout remains
  at frozen baseline `149baf36`. PC1 reported desktop graphics processes only and no identifiable
  experiment process. No GPU job was launched because the next authorized work was proof/contract
  auditing, not another compute sweep.

## 2026-10-09 07:16 +08:00 — mixed P19 achievability checkpoint

- Started from clean branch `codex/research-audit-20261008` at
  `c13cfb837ee1064fb576dab6461989e5cc2c1e8a`.
- Closed the finite-topology mixed-order gap inside the frozen P19 family. For each unmatched but
  observable candidate, a P18 boundary test runs on its cheapest containing group with error budget
  `delta/|U|`; the remaining candidates use the residual P19 matched-control cover. The hybrid
  matches the lower program's `d^-2`/`d^-1` orders and boundary-minimum/control-cover geometry for
  fixed finite topologies, but not exact two-term constants or the possible `log |U|` gap.
- Two independent derivations agreed on the construction and cost. An adversarial audit produced
  successful counterexamples outside scope: unequal but fairness-valid high null thresholds can
  false-trigger the control contrast, and simultaneous equal changes to both controls can be
  invisible. The theorem and API therefore retain the equal-high null and singleton-alternative
  fences.
- Implemented `mixed_control_replay_schedule`, exported it, and upgraded the unified P19 planner to
  emit hybrid boundary/control schedules instead of rejecting observable mixed topologies. Added
  mixed, all-boundary, unobservable, familywise-error, and composite-null counterexample tests.
- Manuscript theorem, proof, abstract, introduction, phase figure, open-problem scope, claim ledger,
  proof status, roadmap, reproducibility guide, novelty matrix, and theorem/algorithm crosswalk were
  synchronized. Independent audit is recorded in
  `docs/PROOF_AUDIT_CONTROL_REPLAY_HYBRID.md`.
- Extended the mixed-topology enumeration to compute the achievable hybrid cost. At `d=10^-3`,
  representative one-unmatched fixtures had lower half-step ratio `3.9775288000006923`, hybrid
  ratio `3.9777503799183593`, and hybrid/lower cost ratio `5.274876575653486`: matching the
  quadratic exponent while visibly not claiming exact constants.
- Exact validation commands: `.venv\\Scripts\\python.exe -m pytest --basetemp
  "G:\\TFOESUU Project\\.tmp-pytest-codex-20261009\\full-mixed-upper" -q` -> **218 passed**;
  touched-file Ruff -> pass; `python -m compileall -q src experiments scripts` -> pass;
  manuscript static check -> 47 labels/50 citations; bibliography policy -> pass; benchmark
  inventory -> 10 artifacts/828 rows.
- GPU state remained idle for research workloads on both PCs. No new numerical sweep was warranted
  by this theorem/proof task. Next scientific target: close or lower-bound the `log |U|` dependence
  and exact constants without weakening the composite-null scope fence.

## 2026-10-09 08:20 +08:00 — P19 familywise fixed/sequential resolution

- Started from clean branch `codex/research-audit-20261008` at
  `33fefcee4a7bf2d77f2547fe759a8eedeed79254`. PC1's compute-process query showed only desktop/UI
  processes; the read-only PC2 WSL command `/usr/lib/wsl/lib/nvidia-smi
  --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader` returned no rows.
  No GPU sweep was scientifically warranted for an exact proof/API task.
- Resolved the apparent P19 `log |U|` gap by separating design classes. For `m` disjoint boundary
  channels, deterministic nonadaptive counts satisfy the exact rankwise floors
  `n_(k) >= log(1+D_beta k)/rho2`, proving `Omega(m log m/d^2)` unit-cost complexity. A two-sided
  sequential LR test with thresholds `m/beta` and `beta` has familywise type-I and pointwise
  type-II error at most `beta`; its expected null rounds per channel are independent of `m`, while
  the changed channel retains additive `log m` delay and the stopping horizon is unbounded.
- Implemented exact chi-square, both KL orientations, bounded-overshoot expected-cost formulas,
  and public API exports. Added five falsifying/identity tests. At `p=.2,s=.1,tau=.1,d=.01,beta=.05`,
  the certified null per-channel sequential bound stayed `5445.138735274` for `m=1,4,16,64`, while
  the changed-channel bound rose from `5442.743003918` to `12765.752036510`.
- Manuscript theorem part (vi), fixed-allocation proposition and proof, abstract, introduction,
  results table, open-problem scope, proof/claim ledgers, roadmap, crosswalk, and reproducibility
  guide now state the fixed-versus-sequential distinction and retain the exact P19 scope fence.
- Exact validation: `.venv\\Scripts\\python.exe -m pytest --basetemp
  "G:\\TFOESUU Project\\.tmp-pytest-codex-20261009\\full-familywise" -q` -> **223 passed**;
  touched-file Ruff -> pass; `python -m compileall -q src experiments scripts` -> pass; manuscript
  static check -> 48 labels/50 citations; bibliography policy -> pass; inventory -> 10 frozen
  artifacts/828 rows. The LaTeX auto path first hit the known Windows decoding/toolchain problem;
  explicit bundled Tectonic compiled a 43-page PDF successfully, temporary PDF SHA-256
  `06f2851c2afa6efd08b4a851fd6f874ed5d655544c94b39d0311d37c48d8f930`.
- No dataset or experiment-result artifact was created or overwritten. Next target: exact adaptive
  constants or bounded-horizon adaptive lower bounds, then the genuine executable-subject gate.
- Validated theorem/code/manuscript change committed as
  `2509be2ea7eab5efdfe9c85a14c4741adf599a42`.

## 2026-10-09 09:13 +08:00 — P19 sequential constant bracket

- Started clean on `codex/research-audit-20261008` at
  `d376a57877b18cbf9eb8094130f57f0237ea73e0`. PC1's process query again showed only desktop/UI
  clients; the direct read-only PC2 WSL compute-process query returned no rows. No GPU work was
  launched because this checkpoint tightened exact information constants rather than estimating a
  numerical law.
- Added two falsifying tests first. They failed with missing lower-bound and small-gap coefficient
  fields, then passed after implementing the exact summed null information floor and asymptotic
  coefficients in `boundary_familywise_sequential_bounds`.
- Combining P19's lower program with the sequential upper proves the explicit leading-null bracket
  `[kl(1-beta,beta)/b2] sum cbar <= liminf d^2 Q0* <= limsup d^2 Q0* <=
  [log(1/beta)/b2] sum cbar`. The remaining ratio is independent of `|U|`, topology, and costs;
  it equals `1.1304671071846433` at `beta=0.05`. The manuscript and claim/proof/reproducibility
  ledgers now replace an unspecified constant gap with this certified 13.05% bracket.
- Exact validation: the deliberate red run produced 2 expected `AttributeError` failures; focused
  green run -> 30 passed; full isolated run -> **225 passed**; touched-file Ruff, compileall,
  manuscript static consistency (48 labels/50 citations), bibliography policy, and frozen inventory
  (10 artifacts/828 rows) all passed. Bundled Tectonic compiled a 44-page temporary PDF with
  SHA-256 `c4438b00d1d99e979d4db4a1a625a0dc0953c7d926065239a2930657978a19b1`.
- No data or result artifact was changed. Validated scientific commit:
  `f5e6ae7f837490817961237efe5cb3bd29c4296d`. Next target: determine whether bounded-horizon
  adaptive allocation can avoid the fixed-allocation `|U| log |U|` penalty, without claiming more
  than the available lower bounds support.

## 2026-10-09 10:13 +08:00 — P19 bounded-horizon adaptive closure

- Started clean on `codex/research-audit-20261008` at
  `cd52041fe8db97835e79cbfe9e6237e537f88e61`. PC1 again showed only desktop/UI GPU clients;
  PC2's direct WSL compute-process query returned no rows. No GPU job was launched because the
  target was a closed-form stopping/error argument, not an empirical quantity.
- Added four falsifying tests before implementation; the red run failed at import as expected.
  Implemented `boundary_familywise_truncated_sequential_bounds`, which runs the exact P19
  sequential block at internal error `eta<beta`, reserves `beta-eta` for truncation, and caps
  declared cost at `max_i E_i[cost]/(beta-eta)`. Truncation-to-accept cannot increase type I;
  Markov's inequality limits each added miss probability to the reserved budget.
- This closes the bounded-horizon topology-order question. At unit costs and fixed confidence,
  the deterministic adaptive cap is `O((|U|+log |U|)/d^2)=O(|U|/d^2)`, while the null information
  floor is `Omega(|U|/d^2)`. Nonadaptive fixed allocations remain
  `Theta(|U| log |U|/d^2)`. The theorem explicitly leaves exact constants and optimal beta
  dependence open; the Markov cap is a certificate, not a claim of practical finite-m optimality.
- Exact executable checks cover error-budget accounting, heterogeneous worst alternatives,
  invalid internal errors, and size growth. For `|U|=16,64,256`, the certified small-gap cap
  coefficient per arm was `26.4834257092`, `25.7407680157`, and `25.4437049383`, respectively,
  rather than growing like `log |U|`.
- Validation: focused green run -> 4 passed; full isolated run -> **229 passed**; touched-file Ruff,
  compileall, manuscript static consistency (48 labels/50 citations), bibliography policy, and
  frozen inventory (10 artifacts/828 rows) all passed. Bundled Tectonic compiled a 44-page PDF;
  temporary PDF SHA-256 `6486b9016fb9d20d506914723e32704c808e9cba019d3cce1bb9025d08fc34ed`.
- No dataset or result artifact was changed. Validated scientific commit:
  `956f7aee60608be05eb9a67a05109318639c8e4a`. Next target: optimize or sharpen the truncation
  confidence allocation, then resume the genuine evolving executable-subject gate.

## 2026-10-09 11:13 +08:00 — optimized P19 truncation certificate

- Started clean on `codex/research-audit-20261008` at
  `9b0851a63d3f0fc3ddbfc813bbd79e3f2f687dac`. PC1 again showed desktop/UI GPU clients only;
  PC2's WSL compute-process query returned no rows. The task was a deterministic scalar
  optimization of a proved bound, so no GPU run was scientifically indicated.
- Added two falsifying tests first. The red run showed that the default still used the arbitrary
  `eta=beta/2` split and missed a dense-grid cap by 34.8%. The implementation now minimizes the
  exact certified cap over `eta in (0,beta)` and retains the half split as a mandatory fallback;
  optimizer failure therefore cannot weaken the previous guarantee. Explicit `internal_error`
  continues to bypass optimization for reproducibility.
- At `p=.2,s=.1,tau=.1,d=.01,beta=.05`, optimized unit-cost caps improved over half splitting by
  factors `1.2917`, `1.2989`, `1.2907`, and `1.2874` for `|U|=1,16,64,256` (22.3--23.0% smaller).
  The heterogeneous `[1,3,11]` fixture improved by factor `1.3451` (25.7% smaller), selecting
  `eta=0.0073699458883` and preserving candidate 2 as the worst alternative.
- Validation: deliberate red run -> 2 expected failures; focused green run -> 6 passed; full
  isolated run -> **231 passed**; touched-file Ruff, compileall, manuscript static consistency
  (48 labels/50 citations), bibliography policy, and frozen inventory (10 artifacts/828 rows) all
  passed. Bundled Tectonic compiled a 44-page PDF; temporary PDF SHA-256
  `9fb1b4be4443f33ca1d44a439812d3d6b426bbfcdd691267749ed238b2ecb7dd`.
- No data or result artifact was changed. Validated scientific commit:
  `9efb7a5b228a87dfc4b2b1c9c4e5d5326fc3944e`. Next target: resume the genuine evolving
  executable-subject gate without contaminating frozen v1 evidence.

## 2026-10-09 11:58 +08:00 — fail-closed Themis evolution gate

- Started clean on `codex/research-audit-20261008` at
  `512e4722abcf3cefc00220ee677e9b9e0c0a580c`. PC1's compute-process query showed only
  desktop/UI clients; PC2's `Ubuntu-24.04` compute-process query returned no rows. No GPU job was
  launched because the candidate failed the pre-outcome scientific gates.
- Added four falsifying admission tests and implemented a three-level external-subject gate:
  deterministic baseline, evolving pair, and replay-theorem readiness. The read-only auditor
  verifies the pinned commit, clean tree, license hash, dependency manifests, exact Git source
  bytes, normalized Python AST history, variant introduction commits, schema evidence, and subject
  random-tape evidence. It never invokes the external subject.
- On pinned Themis commit `a70f12a6a8f34cdd8b170b4dc59a78674c9e8950`, identity, cleanliness,
  and license hash passed. `loan.py` has two Git blobs but one semantic AST hash
  `2cd3bc94e1bcb5a2760e95345f6eae6c69c5813307deb2c31f238054258ed50c`;
  `loan_2.py` and `loan_3.py` were co-introduced at `92432c77bbdada0838c8f924e37f5cd78016db4e`;
  system G has one revision; no dependency lock or audited subject random tape exists.
  `--require evolving` therefore exited 2. No fairness outcome was collected.
- Validation commands: focused gate tests -> 4 passed; touched-file Ruff -> pass; compileall ->
  pass. The first full run reached 207 passed plus 28 setup errors caused solely by a denied host
  temp directory; rerunning with explicit `--basetemp` produced **235 passed**. Manuscript static
  consistency (48 labels/50 citations), bibliography policy, and frozen inventory
  (10 artifacts/828 rows) passed.
- No dataset or result artifact changed. Validated scientific commit:
  `769ca33e8037f75ca1a4f2e288ca8a7d06bd8483`. Next target: identify a legitimate chronological,
  same-schema, seedable executable subject and preregister it before any outcome run.

## 2026-10-09 12:18 +08:00 — genuine Fairlearn evolving subject admitted

- Started clean at `87ff45e44ca5675a2f8e8551338fded96aacbed1`. Screened documented external
  candidates and froze Fairlearn's direct repair pair `e8cc63784de5410805c156715175fc60e2cd5653`
  -> `0cf59eccfdd364417787fe2c368a1c77c3f378b8` before local execution. The pair
  preserves the MIT license, dependency manifest, public `ThresholdOptimizer.predict` schema, and
  random-draw implementation while changing only the documented long protected-group-name merge
  defect from issue #728 / PR #763.
- Added three falsifying generic admission tests; the deliberate red run failed at import, then the
  seven-test gate suite passed. Built a digest-pinned Python 3.8.20 container with exact 2021
  dependencies and verified both source revisions import as `0.6.2.dev0` with identical prediction
  signatures. Frozen probe SHA-256:
  `c4d5a27c7d7e4bd54e31e1cd04599a10450e5d0e958e5c40629d2f69033918d3`.
- Ran the preregistered four-seed CPU smoke once. Old multi-column handling collapsed four groups to
  three and failed its canonical-combined control for every seed; new retained four groups and
  passed every control. Old/new disagreements in the affected path were 8, 7, 7, and 8 of 24 rows;
  the canonical control path had zero disagreements at every seed. All repeated calls were bitwise
  identical and all outputs matched the recorded shared uniforms and probability mass functions.
- External evidence hashes: old `c22a17c62f3411499a51793e2c3705e49e778a1bd661a26b28a4f7d1a2f0eeda`;
  new `dcc9c129cc51d6be130351e6abab15fd4d6d85b24835711e4df46821c80d1a19`;
  validator `20df213d6c9540b96ab380680b6469f90dc287fdec1a2b4cf4ea1e220acb0a05`.
  These are exploratory, external-to-Git artifacts and are not admitted manuscript results.
- Validation: touched-file Ruff and compileall passed; full isolated suite -> **238 passed**;
  manuscript static consistency (48 labels/50 citations), bibliography policy, and frozen inventory
  (10 artifacts/828 rows) passed. Scientific commit:
  `19c2ec629f5ebe9f1a07ab0dfce2d91338ca5db6`; isolated PC2 replication launcher commit:
  `ccb69fc90ce20621b2e829bf078d7e39a021e608`.
- PC2 replication stopped before checkout or execution because PC2 WSL has no Docker or other
  Python 3.8 runtime (system Python is 3.10.12). The protected baseline was untouched. PC1 and PC2
  GPU process queries showed no scientific compute jobs; the actual Fairlearn subject is CPU-only,
  so no scientifically invalid GPU surrogate was launched. Next action: review an isolated PC2
  runtime provision or retain independent-host replication as an explicit blocker, then freeze a
  statistical question before any larger experiment.
- Same-hour resolution: the GitHub clone then failed closed on PC2's existing CA trust problem;
  certificate verification was not bypassed. Exact project and Fairlearn Git bundles were verified
  on PC1 and transferred over the established SSH path. An isolated uv 0.12.20-managed CPython
  3.8.20 runtime with the exact package freeze completed the PC2 run without changing the protected
  baseline or system packages. PC2 reproduced the full scientific summary exactly (3/4 old groups,
  4/4 new groups, old control failure and new control pass for all seeds, 8/7/7/8 affected-path and
  0/0/0/0 control-path disagreements). PC2 transcript/validator/runtime hashes are frozen in
  `docs/FAIRLEARN_EXECUTABLE_V2_PREREGISTRATION.md`. Independent-host replication is now closed;
  the next gate is a frozen statistical question, not more unprincipled compute.
