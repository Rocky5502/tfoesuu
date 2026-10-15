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

## 2026-10-09 12:26 +08:00 — exact Fairlearn distributional law

- Started clean on `codex/research-audit-20261008` at
  `8e9277dfa44a2cb645bd2fd2bf35891f930fd44c`. PC1 showed desktop/UI GPU clients only;
  PC2's compute-process query returned no rows. No GPU job was launched because the preserved
  Fairlearn PMFs determine the target quantities exactly.
- Added five falsifying tests first; the red run failed at import as expected. Implemented exact
  per-row Bernoulli disagreement laws: `|p-q|` for a common uniform tape and
  `p(1-q)+(1-p)q` for independent tapes, with strict shape/finiteness/probability validation.
- The strengthened transcript validator proves that the repaired multi-column PMF equals its
  canonical control exactly and that the old/new canonical control PMFs are identical. The affected
  PMFs differ on 17/24 rows. Exact expected disagreements are `7.083333333333334` per 24-row pass
  under common replay and `8.083333333333334` independently, ratio `1.1411764705882352`.
- This closes the same-fixture seed-count question negatively: more seeds would add sampling noise,
  not information. A larger experiment is warranted only if it adds genuine contexts or protected
  structure; synthesizing a second protected attribute is forbidden. PC1 exact-law validation
  SHA-256: `0c62bbc79e91c55366f1884907d0f28e302d6af2ee47ca7264593f33e91c26a4`.
- Validation: focused suite -> 12 passed; full isolated suite -> **243 passed**; touched-file Ruff,
  compileall, manuscript static consistency (48 labels/50 citations), bibliography policy, and
  frozen inventory (10 artifacts/828 rows) passed. No dataset or raw transcript changed. Validated
  scientific commit: `a3b1f92121c7c1a5ed4e839dcecc795eb0c8ef33`. Next target: audit whether
  the frozen public sources contain genuine multi-column protected contexts before proposing any
  larger Fairlearn protocol.

## 2026-10-09 16:24 +08:00 — public-v1 Fairlearn context gap closed negatively

- Verified branch `codex/research-audit-20261008` at clean starting SHA
  `d869599341572709902590bbc34f8ba12973c08b`. PC1 showed desktop/UI GPU clients only; PC2's WSL
  compute-process query returned no rows. No GPU job was launched because the input gate failed and
  a surrogate would not answer the scientific question.
- Audited the preparer, strict validator, frozen registry, and all seven PC2 artifacts read-only.
  Five registry entries name two protected attributes, but every NPZ has exactly
  `baseline_probabilities` and `evaluation_labels`. Protected names survive only in JSON metadata;
  row-level values and held-out indices do not. The compact seven-artifact schema payload SHA-256 is
  `9154f1cd625be433bcae77f543e085949acec8f813ac4af29656d3b049a36558`.
- Found a second provenance limitation: the v1 preparer silently drops only protected columns that
  happen to exist, then records the registry declaration. Thus metadata alone does not prove that
  all declared columns were loaded. The five datasets are registry candidates, not source-verified
  executable contexts.
- Added two falsifying regressions, a strict code/CLI readiness gate, and a separately versioned v2
  contract specification. The gate validates v1 first and reports **0/7 executable-ready**; with
  `--require-ready` it exits 2. No dataset, frozen result, or external subject transcript changed.
- Commands: read-only PC2 `numpy.load(..., allow_pickle=False)`/JSON schema inspection; focused
  `pytest -q tests/test_prepared_public_validation.py --basetemp .pytest_tmp_fairlearn_context`;
  full `pytest -q --basetemp .pytest_tmp_full_context`; touched-file Ruff; compileall; paper,
  bibliography, and inventory checks; explicit CLI fail-closed check. Results: **11 focused and
  245 full tests passed**, CLI exit 2 as required, Ruff/compileall/paper/bibliography green, and
  inventory unchanged at 10 artifacts/828 rows. Next action: implement a
  non-overwriting v2 preparer/validator with exact protected-column presence and row-alignment
  corruption tests before any outcome run.
- Validated scientific commit: `71f3a32938b9e3516b7cf6837616deafcedafd88`.

## 2026-10-09 17:19 +08:00 (09:19Z) — separate public-context V2 contract

- Started clean on branch `codex/research-audit-20261008` at full SHA
  `583190edf7fe238331dd5123525b168f8a87c6bd`. The branch is local/untracked by a remote branch;
  `main`/`origin/main` remain at frozen baseline `149baf36`. PC1 had 13.7 GiB free VRAM with only
  desktop/UI clients; PC2 had 14.9 GiB free, no compute process, a clean baseline checkout, and
  1.3 TiB free. Completed P12/P15 1k/10k/100k outputs were not rerun.
- Added seven falsifying V2 validator tests first; the deliberate red run failed at import. Added
  eight preparer/source-map tests before that implementation; its red run also failed at import.
  The new separate contract stores aligned source row positions, protected values, raw
  non-protected evaluation features, labels, probabilities, joint-group support, exact source
  hashes, environment versions, and a row-wise alignment digest. It explicitly declares
  observational contexts only and no identified counterfactual transform.
- The preparer requires every protected column, forbids case aliases and protected-feature
  leakage, refuses dirty source/partial registries/existing destinations, stages into a new
  directory, and renames only after complete validation. V1 code, data, manifests, and results are
  untouched. Corruption tests reject missing columns, row reorder, category drift, insufficient
  support, incomplete environments, and source-byte mismatch.
- Read-only PC2 audit: the raw directory has 15 files covering Adult, Bank, German, COMPAS, Law
  School, and MEPS; ordered source-list digest
  `73edce410b52b132befc77a10a2ed23fd77dbeebb395222e082c20c4bd500e3e`. Loading those six cached
  populations confirmed all declared protected columns; loader schema digest
  `5d69a1a723144733ae88858a492b0eed3bb56b5c1f61bb86200c786a45dcb0ad`.
  Default Credit raw bytes were not retained by the original `ucimlrepo` call. Complete V2
  preparation therefore failed closed at provenance; no V2 data or outcome was generated.
- Validation: 15 focused tests and **260 full tests passed**; touched-file Ruff, compileall, paper
  static consistency (48 labels/50 citations), bibliography policy, and frozen inventory
  (10 artifacts/828 rows) passed. GPU work was not scientifically indicated. Next action: obtain
  and hash the registered UCI Default Credit source without bypassing TLS, freeze a complete source
  map, then run bounded CPU-only V2 preparation/validation on PC2. Public outcome runs remain gated.

### Same-cycle update — seventh raw source frozen

- Verified the official UCI dataset page, DOI `10.24432/C55S3H`, 30,000-row/23-feature metadata,
  and CC BY 4.0 license. Downloaded its official ZIP on PC2 over HTTPS with normal certificate
  verification to the previously absent new path `datasets/raw/uci-350-default-credit.zip`.
  No existing file was overwritten. ZIP SHA-256:
  `56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602`; it contains exactly one
  5,539,328-byte XLS member. Updated ordered 16-file raw-source listing digest:
  `92a3fddd48155e527ee549b705026e1063823d34f6e00f1bb2bb44d3dd341e2e`.
- Added a frozen seven-dataset source map and a local-source Default Credit reader, avoiding the
  original ephemeral `ucimlrepo` response. V2 dependencies are separate from the V1 preparation
  contract. One new falsifying archive-selection test failed at import before implementation.
- Focused V2 suite: **16 passed**. Full isolated suite: **261 passed**; touched-file Ruff,
  compileall, manuscript static consistency, bibliography policy, and inventory passed. Next:
  commit this source-reader increment, transfer the exact commit to an isolated PC2 worktree, and
  run the no-outcome V2 preparation/validator after environment and source-map gates pass.

### Same-cycle update — preliminary V2.0 prepared, then scope gap found

- Verified bundle SHA-256 `efd01144585cfc166755f87317f3be594789c1cf0fe74a12605a83e0592c7cb6`
  and cloned clean commit `18442ac113903f21df4f2845e1868cf791ee238e` into an isolated PC2 checkout;
  protected baseline `main` stayed clean at `149baf36`. An isolated uv/CPython 3.12.14 environment
  installed exact resolved versions, including `xlrd==2.0.2`, over verified package channels.
- PC2 preflight: 260 passed, one Torch-only test skipped because the CPU V2 environment does not
  install Torch; touched-file Ruff and compileall passed. The bounded no-outcome preparation wrote
  a new directory `datasets/prepared_v2/18442ac` and its built-in plus independent validators passed
  all seven source-byte, schema, alignment, support, and manifest checks. External validation JSON
  SHA-256 `3bf959c990df34772da787c01e2d6eb017b425e28ed81ff5e28e332cae4259a3`;
  manifest SHA-256 `4cd3af97283ec7a327fac14791d90e5e5eeaddc1a166ef33ea8bdc56e69d0161`.
- A subsequent hostile protocol audit found V2.0 preserves only evaluation protected contexts.
  Genuine Fairlearn fitting also requires aligned training-side protected values and features.
  V2.0 is therefore preserved but downgraded to preliminary/non-executable; no outcome was run.
- Added a falsifying training-row reorder test first; it failed at import. V2.1 now includes complete
  aligned training labels, positions, protected matrices, raw non-protected matrices, independent
  training alignment hashes, train/evaluation group counts, split-disjointness checks, and support
  coverage. Focused V2.1 suite: **17 passed**. Next: commit, transfer, and prepare V2.1 to a new path;
  never overwrite V2.0.

### Same-cycle update — V2.1 representation completed

- Committed V2.1 as `d0790b30d09fcc22721dfd5942ec9ef0db76cb35`; verified bundle SHA-256
  `2497b8471e032fe50de7b794009887a08575898f80a9c17178191e5fbd21024a` and cloned it into a second
  clean isolated PC2 checkout. Reused the isolated resolved CPU environment read-only via explicit
  `PYTHONPATH`; no baseline source or V1 artifact changed.
- PC2 V2.1 preflight: 261 passed and one Torch-only pathwise test skipped; Ruff/compileall passed.
  Bounded CPU preparation wrote only `datasets/prepared_v2/d0790b3` (6.2 MiB), then built-in and
  independent validators rechecked all seven raw sources, complete training/evaluation arrays,
  disjoint positions, support counts, manifests, and hashes. Validation JSON SHA-256
  `652a4299461a7ba58d5443f67b81a899ea529e5c9abe87eccf429fedb3cb8723`; manifest SHA-256
  `b07bf1aa17e37bc02971e200fb7c7e6eed14584d8920573f966fc56399acaf39`.
- Scientific limitation found before outcomes: supported raw training joint-group counts are Adult
  10, COMPAS 4, Law School 4, German 83, and Default Credit 102; Bank has 68 raw age groups and
  MEPS has 2 race groups. Thus V2.1 closes representation but not analysis design. German/Default
  age transformations and support rules must be preregistered; no post-outcome binning is allowed.
- Added an explicit report scope (`representation-only`) and `outcome_ready=false`, with a red/green
  regression preventing data-contract readiness from being mislabeled experimental readiness.
  Next task: freeze a support/age-transform/estimand protocol, then audit it before any Fairlearn
  run. Public outcome campaigns remain approval-gated.

## 2026-10-09 22:01 +08:00 (14:01Z) — independent P19 sequential audit

- Verified branch codex/research-audit-20261008 at full SHA
  c1236c2f147f34479bd7aa8fb16cdf7dfdbaee48 before edits. PC1 had no scientific
  GPU compute process; PC2 baseline remained clean on main at
  149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b with no reported GPU compute process.
  Completed frozen P12/P15 stages were not rerun.
- Hostile re-derivation found no counterexample to P19 parts (vi)--(vii) within
  the declared equal-high null and singleton-alternative scope. It checked LR
  orientation, conditional serial-channel Ville bounds, reciprocal-martingale
  misses, overshoot signs, Wald integrability, order-independent cost upper
  charging, and the pre-query Markov truncation coupling.
- Added a deterministic absorbing-chain oracle for the exact lattice case with
  increments {-log 2, 0, +log 2} and boundaries {-2,+3}. Exact values are null
  upper crossing 3/31, changed lower crossing 7/31, null mean time 470/31, and
  changed mean time 580/31; all satisfy the beta/m, beta, H0, and H1
  certificates. This is an exact computation, not a stochastic simulation.
- Strengthened the manuscript proof with the conditional-history,
  integrability, serial-order, and truncation-coupling arguments. Commands:
  focused test_control_replay.py (37 passed), full pytest with isolated
  basetemp (263 passed), touched-file Ruff, compileall, paper consistency
  (16 TeX, 48 labels, 50 citations), bibliography policy, and frozen inventory
  (10 artifacts, 828 rows); all passed. No dataset, result, or GPU artifact
  changed. Next: preregister and adversarially audit the V2.1 analysis protocol
  before any public outcome execution.

## 2026-10-09 23:08 +08:00 (15:08Z) — public V2 analysis preregistration

- Verified branch codex/research-audit-20261008 at clean full SHA
  a281ed0f258e2c793dd6d0d825b01413ab2de1dc. PC1 and PC2 reported no scientific
  GPU compute process; PC2 protected baseline remained clean on main at
  149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b. No result or dataset was changed.
- Added a machine-readable seven-dataset Fairlearn protocol and fail-closed
  validator. It freezes the source pair, prepared-manifest identity, protected
  transforms, support gates, score-model gate, exact-PMF estimands, injective
  canonical control, four correspondence seeds, complete reporting, and
  outcome_authorized=false. Six scope-drift tests were red first at missing
  implementation, then passed.
- Read-only PC2 support audit before subject execution: transformed group
  counts Adult/Bank/COMPAS/Default/German/Law/MEPS = 10/2/4/4/4/4/2. All groups
  pass at least 40 training rows, two rows per label, five evaluation rows, and
  train/evaluation coverage. German male/age<25 is limiting at 45 training
  rows, so a provisional threshold of 50 was rejected before outcomes.
- Hostile score replay found an additional reproducibility blocker: decoding
  V2.1 features and inferring dataframe types reproduced stored evaluation
  probabilities exactly for six datasets, but MEPS differed by as much as
  0.4504382489762433. V2.1 intentionally stores scalar values, not source
  dataframe dtypes. The protocol therefore forbids inferred-type execution and
  requires a separate immutable training/evaluation score companion generated
  with the frozen loader/environment before any Fairlearn outcome.
- Validation: 6 focused and 269 full tests passed; touched-file Ruff,
  compileall, paper consistency (16 TeX, 48 labels, 50 citations), bibliography
  policy, and frozen inventory (10 artifacts, 828 rows) all passed. GPUs were
  not used because the historical Fairlearn subject and preprocessing are CPU
  tasks. Next: implement and independently validate the non-overwriting score
  companion; outcome execution remains approval-gated.

## 2026-10-10 00:08 +08:00 (2026-10-09 16:08Z) — V2.2 score companion

- Started clean on branch codex/research-audit-20261008 at full SHA
  8abd9bb32494262a8e8f0ee24259b87846f9c391. PC1 had no scientific GPU
  process; PC2 baseline remained clean at 149baf36 and no GPU process was
  reported. The task is CPU-only preprocessing, so no GPU time was spent.
- Added four falsifying companion tests first; their red run failed at missing
  module import. Implemented a non-overwriting V2.2 schema, normalized
  row/score alignment hash, strict seven-dataset validator, raw-loader score
  preparer, and standalone validator. It rejects score reorder, evaluation
  drift, prepared-manifest drift, incomplete sets, position mismatch, clip
  violations, and metadata/manifest divergence. Local focused tests passed and
  the full suite reached 273 passed before remote preparation.
- Committed implementation at b35c0b0d5b997afd50f154d15effffc0ac371345;
  bundle SHA-256
  db2a962cd8cf589015b4e03d1c62ef3430b42e9f8269c6b4f3dd94279da21779.
  Isolated PC2 preflight under the exact V2.1 Python 3.12.14 environment:
  272 passed, one expected Torch-only skip. No source or prepared artifact was
  modified.
- PC2 generated only the new 800 KiB directory
  datasets/score_companion_v2/b35c0b0 from the original loaders and frozen raw
  bytes. Built-in and separate CLI validation passed; all seven evaluation
  score vectors reproduce V2.1 bit-for-bit. Companion manifest SHA-256
  52ee136f3754b2f02860d07ba1a8bde3236279cd92200540a163cb47abf0a19e;
  external validation JSON SHA-256
  56aee3a55b1214bef36b1867ca8a77dd9ad91c6ae1ce54fe9927987c62925049.
- The machine-readable analysis contract now pins those hashes. No Fairlearn
  old/new outcome was executed and outcome_authorized remains false. Next:
  implement/audit the fail-closed subject runner without running the public
  campaign, then stop at the explicit approval gate.

## 2026-10-10 01:08 +08:00 (2026-10-09 17:08Z) — fail-closed runner preflight

- Verified branch codex/research-audit-20261008 clean at full SHA
  3413ac3e31bf8f4dc496c9e51550126164c713cd. PC1 reported no scientific GPU
  process. No datasets or existing results were edited; this CPU-only gate did
  not warrant GPU use.
- Added four falsifying preflight tests first; the red run failed at missing
  module import. Implemented canonical length-prefixed tuple keys, exact
  protected transformations, binary-label/group support auditing, and a
  complete seven-dataset plan builder that validates V2.1, V2.2, and the
  machine-readable protocol without importing or running Fairlearn.
- Local validation reached 277 passed. Committed the preflight implementation
  as 5c9f23717211b3e59b1e42aa43cb0b374233c54f; bundle SHA-256
  5326c3a896d5ba0d024b2cd70bec8944e18a245fbb196cf229b17ecaa3ea9537.
  The first remote shell gate failed safely because command substitution was
  interpreted outside WSL; no output existed. The corrected explicit-path
  command used the already isolated clone and did not weaken any check.
- PC2 isolated preflight: 276 passed, one expected Torch-only skip. All seven
  datasets passed frozen support, row alignment, and canonical-key injectivity.
  Plan SHA-256 fa07b09ea675a44025ef923f28307ef2d6b1a98aa91354788cf9c5859c839a94;
  report SHA-256 fbb15b8b21dda43f0cbb08cb86d355e0a8d26eb2cfa692559b1bc763916b48b8.
  The report remains runner-preflight-only with outcome_authorized=false.
- Next: build and falsify the historical-runtime executor/transcript validator
  on synthetic fixtures only. Do not execute the seven-dataset old/new campaign
  without fresh approval.

## 2026-10-10 02:09 +08:00 (2026-10-09 18:09Z) — approval-gated runtime core

- Verified branch codex/research-audit-20261008 clean at full SHA
  dcd4692abdfc811efc18ecbda3e297d1f7c22a25. PC1 and PC2 reported no
  scientific GPU compute process; PC2 protected baseline remained clean at
  149baf36. GPU use is invalid for this historical CPU subject.
- Added four falsifying runner-core tests first; the red run failed at missing
  package import. Implemented a Python-3.8-compatible immutable source-row
  score lookup and external approval validator. Approval must bind the exact
  protocol SHA-256, source pair, four seeds, bounded seven-dataset scope,
  explicit user authority, and timestamp. Missing, duplicate-row, unknown-row,
  scope-drift, or protocol-drift cases fail closed.
- Local focused tests passed; full suite 281 passed, Ruff and compileall green.
  Commit 3c5acec1573325a4b29851e89c5f7e00141d0cf8; bundle SHA-256
  8e60e1b6efc6cf89b4a41bbf3d1a952f75fe0c6d213ffe36f1753de7aba86b69.
- PC2 isolated clone ran the synthetic lookup and missing-approval rejection
  under the exact historical runtime: Python 3.8.20, NumPy 1.20.3. No approval
  record was created, no Fairlearn subject was imported, and no public outcome
  was observed. Next: transcript schema and independent validator on synthetic
  records only; genuine execution remains approval-gated.

## 2026-10-10 03:09 +08:00 (2026-10-09 19:09Z) — transcript validator

- Verified branch codex/research-audit-20261008 clean at full SHA
  4770358b6a9de305af3eeb71862a37afb08d7195. PC1 and PC2 reported no scientific
  GPU compute process; PC2 baseline remained clean at 149baf36. No source,
  dataset, prepared artifact, or result changed.
- Added four transcript attacks first; the red run failed at missing module
  import. Implemented a strict fourteen-record validator for the complete
  seven-dataset old/new census. It checks source/prepared/companion/plan
  identities, source positions, group cardinality, probability-simplex PMFs,
  full seeds, repeated determinism, exact threshold correspondence, common
  tapes across two versions and two modes, repaired canonical conformance, and
  single-attribute negative controls.
- The first repaired-mismatch test exposed aliasing in the synthetic fixture
  itself: native and canonical modes shared one mutable PMF list. The fixture
  was repaired with a deep copy before the validator was accepted. This was a
  test-harness defect, not subject evidence.
- Focused synthetic attacks pass; full suite 285 passed, touched-file Ruff and
  compileall green. Commit 855e467251e730247bf273f9d832e18c1d4f70c0. No
  public transcript was created and no subject outcome was observed. Next:
  connect the historical executor to the frozen schema using synthetic inputs
  only; genuine execution remains approval-gated.

## 2026-10-10 04:12 +08:00 (2026-10-09 20:12Z) — synthetic subject executor closure

- Verified branch `codex/research-audit-20261008` clean at
  `e8623a4b6c672bf7512f2cd144043e8910c7e7e4` before work. PC2's protected
  baseline remained clean at `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`.
  PC1 and PC2 GPUs were at 1% utilization; the listed processes were desktop
  services, not research jobs. This historical Fairlearn gate is CPU-only.
- Added executor falsification tests first; the red run failed at the missing
  `run_dataset_transcript` import. Implemented pinned old/new source identity,
  immutable lookup, split/alignment/cardinality/seed/PMF checks, two protected
  modes, common tapes, repeated seeded calls, and exact threshold
  correspondence. Focused tests: 8 passed; full suite: 289 passed; Ruff and
  diff checks passed.
- Committed code as `655abe5956dd3c12d5438bc0d3e8f8d37df0a5e5`.
  Git bundle SHA-256:
  `0d4537dfaa334176b371d290b25db6ecafea37562039078a78c16b820755260b`.
  PC2 cloned it into an isolated checkout and ran the actual pinned old and new
  `ThresholdOptimizer` classes under Python 3.8.20 on synthetic inputs only.
  Both versions passed repeated determinism and exact threshold checks for both
  modes and both tapes. Transcript hashes: old
  `03f303fabc81c557d34fe601b89fc4d82be7bdc79679bae042dae142f83740df`;
  new `af31a5083b8eca463c83b621b854716ac21b77bd1f475c9a6dfd686b78b115e7`.
- No V2.1/V2.2 public context was loaded and no public outcome exists. The
  executor/validator path is ready; fresh explicit user approval remains
  required for the bounded seven-dataset campaign.

## 2026-10-10 14:14 +08:00 (2026-10-10 06:14Z) — immutable campaign input bridge

- Resumed clean on `codex/research-audit-20261008` at
  `7c3ba09b59ae9d8e8bd12b2af32506d68988a475`. PC2's protected baseline was
  still clean at `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`; neither host had a research
  GPU process. This historical subject remains CPU-only.
- A hostile audit found a last-mile gap: the tested executor had no immutable
  V2.1/V2.2-to-Python-3.8 input bridge and the final entry point did not itself
  prove the source checkout clean. Added falsifying corruption, alignment,
  shape, source-dirty, and exact-float tests before completing the bridge.
- Commit `e73b6fda243b93e3b1c406f75d8daa09e28544c0` adds an outcome-free bundle
  builder, exact hexadecimal score serialization, strict file census and
  hashes, historical-runtime loader, clean Git/source-hash gate, approval-first
  campaign entry point, and non-overwriting output. Local: 295 passed. Ruff,
  compileall, and diff checks passed. Bundle-transfer SHA-256:
  `6cf7354e437d6ddadd0ae21286a5e40984a23e16d5f41620c0678f10e99718cb`.
- PC2 isolated verification under the exact V2.1 environment: 294 passed and
  one expected Torch-only skip. It created only the new 13,597,580-byte input
  directory `datasets/fairlearn_public_v2_inputs/e73b6fd`; manifest SHA-256
  `2435e006a8a445e0e94e7248745f5ce9b1349361d4b49b7ffd18488bcebc686e`.
  Python 3.8 loaded all seven datasets with train/evaluation row counts:
  Adult 33916/4096, Bank 5881/1961, COMPAS 3954/1319, Default 22500/4096,
  German 750/250, Law School 16756/4096, and MEPS 11873/3958. Both pinned
  source trees passed clean-commit and critical-file hashes.
- The exact command path with a nonexistent approval returned
  `fresh campaign approval file is missing` and created no output. No public
  subject outcome was computed. Next action is the bounded seven-dataset run
  only after fresh explicit approval.
- Audited the manuscript against the two distinct public protocols. The old
  prose conflated the V1 theorem-aligned GPU simulation with V2 executable
  Fairlearn behavior. Revised the evaluation section to separate them, freeze
  the exact-PMF/software-behavior interpretation, retain the causal-fairness
  exclusion, and identify the CPU-only historical runtime. Bibliography and
  paper consistency checks passed. Bundled Tectonic produced a 45-page PDF;
  visual inspection of pages 31--34 found no clipping, overlap, or broken
  section flow. Existing narrow-table underfull/overfull warnings were
  unchanged and do not originate in the new prose.

## 2026-10-10 14:58 +08:00 (2026-10-10 06:58Z) — V2 campaign admission

- Started on `codex/research-audit-20261008` at full SHA
  `ade8ff3d8b764a4cbda7d06bbf062650542c5530`. The local GPU process census
  contained desktop/UI processes only. The pinned Python 3.8 Fairlearn subject
  is CPU-only, so GPU execution would not be scientifically valid.
- Recorded fresh user authorization in an external approval object (SHA-256
  `56fc7b2cb93b1503c0ac7bcfee984ec3155eaaae82d2a0179ca96c07cc34a106`).
  PC2 ran the complete bounded seven-dataset old/new census from the immutable
  input manifest `2435e006a8a445e0e94e7248745f5ce9b1349361d4b49b7ffd18488bcebc686e`.
  Old/new outputs hash to `3965581b561d689b7c537781646d73e6a6ea12f147308d598f404478710d32ab`
  and `6a47d03fe207adf8683eace7cd11514a27bf076ce2b34147fce3e094730e1c9d`.
  Independent validation SHA-256:
  `cc07642b3d643b046de946023a8b373affb9697c0153c2f7abbbf545a2afd6f4`.
- Exact primary results: Adult parent max/mean discrepancy 1/0.05521976534594683;
  Default Credit 1/0.10234294181034484; every other parent dataset was zero.
  The repaired revision was exactly zero on all seven. Both single-attribute
  controls passed. All fourteen records and all four common-tape correspondence
  checks passed; no confidence interval applies to deterministic exact PMFs.
- Added five falsification tests and a provenance-locked result renderer. Full
  suite: 304 passed in 12.23 s using a repository-local pytest root. Touched-file
  Ruff, paper consistency, benchmark inventory, and bundled-Tectonic compilation
  passed. The generated admission JSON SHA-256 is
  `93609c26a4abb7da84bcc9de44186cf5ed8886d3060bfdcbe31ce1302f59f048`.
- Admitted the full census to manuscript Table 5, including every null result and
  the causal/population exclusion. Adversarial PDF review caught an initial
  twelve-page float deferral; fixed placement now keeps the table beside the
  claim on page 33. Color and grayscale renders passed. Final 45-page PDF
  SHA-256: `dcf8e8a919d647da05fa76eb64544aaf000078f9249f2716713eeb0a6b97e251`.
- Next: commit this coherent admission layer, then audit the remaining paper-wide
  overfull boxes and release-language consistency. No million-trial, public
  expansion, publication, or submission action is authorized.

## 2026-10-11 09:15 +08:00 (2026-10-11 01:15Z) — manuscript layout release gate

- Verified branch `codex/research-audit-20261008` at full SHA
  `1514af31dbd8f0fb7c37e967b2e909c50a01f48f` before work. The local RTX 5070
  Ti reported 5% utilization, 2,098/16,303 MiB, and 40 C; the compute census
  contained desktop/UI processes only and no scientific GPU job. The admitted
  V2 campaign was already complete, so launching another run had no scientific
  value.
- A paper-wide release audit found three severe overfull boxes (85.14 pt in the
  planner path, 30.68 pt in the Gaussian variance sentence, and 119.03 pt in
  the P17 figure) and deferred the evaluation tables/figure to pages 42--45,
  far from their claims. Reflowed the affected prose, made code paths breakable,
  repaired the P17 annotation/ticks, and pinned the submission-facing evidence
  objects to their evaluation context.
- Built with bundled Tectonic using
  `tectonic --keep-logs --keep-intermediates --outdir build-layout-release5-20261011 main.tex`.
  The final artifact has 46 pages and zero `Overfull \\hbox` warnings. The
  inventory, public-benchmark, V2-result, and deterministic-evidence objects now
  appear on pages 32, 33, 34, and 36; Figure 4 shares page 36 with its evidence
  table, and related work begins on page 37. Full-size page 1 and pages 36--37,
  plus grayscale page 36, passed visual inspection without clipping, overlap,
  or illegible encoding.
- Validation command
  `.venv\\Scripts\\python.exe -m pytest -q --basetemp .pytest_tmp_layout_20261011`
  passed all 304 tests in 14.37 s; `git diff --check` passed. Stable PDF:
  `output/pdf/tfoesuu_stoc2027_v2_admission.pdf`, 322,376 bytes, SHA-256
  `aa5e15be13d30cc40987d741f7b7a4c96436ddd446bc845aad68f7de0325720b`.
- Next: commit the coherent layout repair and retain the existing approval gate
  for any million-trial, dataset-expansion, publication, or submission action.

## 2026-10-13 14:42 +08:00 — 100k preview admission gate

- Branch/SHA at start: `codex/final-submission-audit-20261012` /
  `5c115824e63caed23674f6cae93f30a53bfadcb1`; only the new validator worktree
  changes were present. PC1 reported RTX 5070 Ti utilization 25%, 2,568/16,303
  MiB, 43 C with desktop/UI processes only. PC2 reported 1%, 6,248/16,303 MiB,
  55 C and no identified TFOESUU job. No GPU run was launched because the
  authorized 100k evidence already existed and a rerun would add no scientific
  information.
- Falsifying command before implementation:
  `.venv\\Scripts\\python.exe -m pytest -q tests\\test_preview_results.py --basetemp .pytest_tmp_preview_red`
  failed on the intentionally missing `tfoesuu.preview_results` module.
- Added the fail-closed validator, CLI, immutable manifest, and six corruption
  regressions. The real validation command was
  `.venv\\Scripts\\python.exe scripts\\validate_preview_results.py data\\p12_p15_100k_preview_manifest_v1.json --base-dir . --output data\\p12_p15_100k_preview_validation_v1.json`.
- Result: 198/198 rows, 594 comparisons, zero Bonferroni outliers; validation
  report SHA-256
  `32ea2d88d6475c4880d607e13023151e3f84c4a78eac05ee5e0be64b37d5c9c5`.
  P12/P15 result hashes are respectively `f00458f5...1035` and
  `e0750e5d...74ab`.
- Checks: targeted tests 6 passed; full suite 310 passed in 14.79 s; touched-file
  Ruff and `git diff --check` passed. Next: commit this evidence boundary, then
  reconcile and compile the supplied editorial Overleaf tree without
  overwriting the authoritative research source.

## 2026-10-13 18:55 +08:00 — final audited Overleaf release gate

- Branch: `codex/final-submission-audit-20261012`; starting checkpoint SHA
  `f879b6d482fc9a584a469ff372025139aa3620df`. No GPU job was launched: the
  admitted 100k evidence was complete and another run had no scientific value.
- R1--R5 reviews completed. Final R1 Gaussian and R2 Bernoulli verdicts are GO;
  R3 accepts the scoped oracle-law evidence; R4 accepts novelty positioning;
  R5's duplication, evidence, and first-12-page issues were resolved.
- Added Git-blob verification for the frozen source binding and fail-closed
  resume checks for trial budget, device, seed, full spec, unexpected IDs, and
  duplicate IDs. The release carries both raw JSONLs, both specs, admitted
  runner snapshots, manifest, report, and evidence README.
- Validation: `PYTHONPATH=.;src .venv\\Scripts\\pytest.exe -q` with a local
  base temp passed 324 tests in 13.52 s; touched-file Ruff passed; the immutable
  campaign revalidated 198 rows and 594 finite laws with zero Bonferroni
  outliers; `git diff --check` passed.
- Manuscript: direct bundled-Tectonic build succeeded, 44 US-Letter pages,
  zero undefined citations/references and zero overfull boxes. Every rendered
  page was visually inspected. Stable PDF:
  `output/stoc2027_final_2026-10-13/TFOESUU_STOC2027_REVIEW_AUDITED_2026-10-13.pdf`,
  SHA-256 `1197c6b14a57f567b680916cdb67510459517dedccf669917f1052ef8e355b79`.
- Next: create a source-only Overleaf ZIP from the reconciled repository tree,
  verify archive contents/hashes and clean build, then commit the coherent
  final-audit changes. No upload or submission is authorized.

## 2026-10-13 19:24 +08:00 — pre-submission typography and visual gate

- Start: `codex/final-submission-audit-20261012` at
  `381e9c8556fc95425fa092a854eea6de6cf401c5`; preserved the existing final
  release artifacts. PC1 was idle for research purposes (RTX 5070 Ti: 1%,
  3,012/16,303 MiB, 45 C). No scientifically redundant GPU rerun was started.
- CFP audit: official review format is nonanonymous, 11-point or larger,
  single-column, single-spaced, US Letter with one-inch margins and no review
  page limit. The merits/key ideas remain within content pages 1--12; the
  12-page `acmart` limit is camera-ready-only.
- Source audit/fix: normalized 117 legacy display blocks. The compiled closure
  now has 130 sequentially numbered, uniquely labeled equations and a static
  regression gate. Removed the two remaining ``et al.'' prose constructions.
- Figure 1: replaced the dense inline diagram with editable TikZ emphasizing
  evidence reuse, sound pruning, replay-law declaration, and scope-matched
  certification. Full-size color and grayscale renders passed.
- Checks: 325 tests passed (13.42 s); review/general static gates passed; Ruff
  and `git diff --check` passed. Tectonic: 44 pages, no overfull boxes or
  unresolved citations/references. Every page was rerendered and inspected.
- Next: commit the coherent source changes, rebuild from the packaged Overleaf
  source, and issue a new immutable ZIP/PDF/manifest without overwriting the
  earlier audited release.
- Completed: source commit `8271457701cf581363f4794299e3d53c1d1aa88f`;
  clean-extract Overleaf build passed. Final ZIP SHA-256
  `796f637d6ae10c587bcc401128a0d1478392c37fa53f9ac29701e5ae1763c13e`;
  final PDF SHA-256
  `e27195241f3260e5426e9cf2ba4e421b75216bda3f8b0839f6b3aa7f29a4179f`.
  No submission/upload action was taken.

## 2026-10-14 15:45 +08:00 — repository release and remote-sync gate

- Start: branch `codex/final-submission-audit-20261012`, full SHA
  `82a2b4caa37ce5216b70f1fff274c6682cfce363`; `origin/main` remained at the
  verified baseline `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`.
- Five highest-impact risks were stale V2 README claims, an ambiguous paper
  source pointer, undocumented V2 dependencies, incomplete manuscript CI, and
  the absence of the final research branch on GitHub. Added a red-first
  release-surface regression (three expected failures), then repaired README,
  dependency extras, Make targets, CI workflows, ignore rules, public-protocol
  status, and the submission checklist. Generated paper/output artifacts are
  ignored and will not be committed or pushed.
- Evidence command:
  `.venv\Scripts\python.exe scripts\validate_preview_results.py data\p12_p15_100k_preview_manifest_v1.json --base-dir . --output %TEMP%\tfoesuu_p12_p15_validation_20261014.json`.
  Result: 198 records, 594 comparisons, zero Bonferroni outliers; report
  SHA-256 `32ea2d88d6475c4880d607e13023151e3f84c4a78eac05ee5e0be64b37d5c9c5`.
- Verification: new release-surface test 4 passed; full suite 329 passed in
  16.25 s; touched-file Ruff passed; bibliography, general-paper, review-format,
  equation-label, and benchmark-inventory gates passed. `pdfinfo` confirms the
  final artifact is 44-page US Letter and unencrypted. Repository-wide Ruff
  still has 63 pre-existing findings outside this patch; no unrelated mass
  rewrite was attempted.
- GPUs: no experiment launched. The authorized P12/P15 and Fairlearn V2
  campaigns are complete, so additional use would not produce valid new
  evidence. Next: commit this coherent release surface, validate from a clean
  commit, push the research branch (never `main`), and verify the remote SHA.
- Completed release commit `b79169e14164d506f33f912c378c214524d99d72`.
  Clean-tree freeze: 299 tracked files, zero extras, manifest SHA-256
  `7b6354e7901f3533cc1bb780c158dec0a12257c78f853f9e4d8bd4d07539871c`.
  The branch was pushed and `git ls-remote` returned the identical SHA.
- GitHub runs `38530588063` (CI) and `38530588034` (paper) were created but
  GitHub did not start their jobs, reporting failed account payments or an
  insufficient spending limit. No runner executed repository code; resolving
  GitHub billing/spending is the remaining external CI gate.

## 2026-10-14 17:51 +08:00 — Fairlearn exact row/group audit

- Start: clean branch `codex/final-submission-audit-20261012` at full SHA
  `7465b246dff45e65ea6927b1c45a9f735695ee4e`. Five live risks were incomplete
  claim-level literature comparison, missing Fairlearn row/group evidence,
  simulator-versus-scaling ambiguity, claim/source-tree drift, and unavailable
  GitHub-hosted CI. The row/group validity gap was the highest-value locally
  falsifiable task.
- PC1 reported RTX 5070 Ti utilization 22%, 8,065/16,303 MiB, 43 C; PC2
  reported 1%, 7,910/16,303 MiB, 53 C. No TFOESUU GPU job was launched because
  the historical subject and exact-PMF audit are CPU-only.
- Recovered the preserved PC2 raw outputs and immutable input bundle read-only.
  Hash gates matched old `3965581b...d32ab`, new `6a47d03f...e1c9d`, and bundle
  manifest `2435e006...686e`. The initial falsifying test failed at the missing
  `summarize_public_fairlearn_v2_rows` import, as intended.
- Implemented exact row alignment, affected counts/fractions, full
  protected-tuple strata, and a reproduction of the pinned parent's
  split-dependent fixed-width NumPy merge. Results: Adult 244/4,096 (5.96%),
  Default Credit 443/4,096 (10.82%), all other parent populations zero, repair
  0 across every row. Parent keys mismatch for seven Adult and two Default
  Credit tuples; this exactly localizes all 687 affected rows.
- Verified against official Fairlearn issue #728, PR #763, and direct-child
  commit `0cf59ecc...`: the case study reproduces a known defect and is now
  labeled accordingly. Bank/MEPS bypass the multi-column merge; the other three
  zero multi-column datasets retain identical parent keys across frozen splits.
- Aggregate row-audit SHA-256:
  `bce7829545445bb77ca874469c6fe71a2c1bd2759b607e4dc57ae0d24e56fd34`.
  Checks: 334 tests passed in 13.75 s; touched-file Ruff and all static paper
  gates passed. The LaTeX skill's Windows TeX-Live probe hit a GBK decoding bug,
  so its documented bundled-Tectonic fallback was invoked directly. Final build:
  45 US-Letter pages, no overfull/undefined-reference findings; page 38 passed
  visual inspection. PDF SHA-256:
  `74990d6bf9805a74f0cca8530605bd8a38aab5c4cbedfb961ca4d44289268012`.
- Next: commit this coherent evidence repair, then begin the hostile
  claim-by-claim novelty audit using primary published sources. Human proof and
  author sign-off remain explicitly outside automated certification.

## 2026-10-14 17:59 +08:00 — hostile novelty and wording gate

- Start: clean branch `codex/final-submission-audit-20261012` at full SHA
  `8573adaff1a53e628f3b201b024d149910281a43`. Highest risks: theorem-level
  literature collision, generic interpretation of P19 adaptivity, missing
  human novelty sign-off, simulator/real-software evidence confusion, and the
  external GitHub CI billing block.
- Red-first command:
  `.venv\Scripts\python.exe -m pytest tests/test_release_surface.py -q` ->
  expected 2 failures for the absent audit and absent narrow manuscript fence.
- Added `docs/HOSTILE_NOVELTY_AUDIT_P12_P19.md`, primary-source identifiers,
  exact overlap/oracle/null/cost comparisons, a durable verdict for every
  P12--P19 claim, README/claim-ledger links, and a regression test. Manuscript
  wording now cites sequential multiple-testing prior art and limits P19's
  increment to the replay-derived mixed information channels.
- Verification: targeted 6 passed; full suite with local isolated temp base
  **336 passed in 12.72 s**; Ruff, bibliography, general-paper,
  review-submission/equation-label, and diff gates passed. The first full run's
  64 setup errors were solely the inaccessible global Windows pytest temp root;
  no assertion failed, and the isolated rerun resolved the environment issue.
- PDF: bundled Tectonic built 45 US-Letter pages, unencrypted, with no overfull
  boxes, unresolved references, or `??` markers. Page 8 visual inspection
  passed. SHA-256:
  `126384a613d815b717ee092b87044f105eedfad54a2599b5e704ef132fa8f4c8`.
- GPUs: PC1 2%, 7,949/16,303 MiB, 42 C; PC2 1%, 7,911/16,303 MiB, 49 C. No
  research GPU job was running or warranted. Next: commit and push this coherent
  novelty repair, then audit whether the preserved 100k records support a
  genuinely measured scaling figure without conflating exact-law simulator
  validation with executable-software evidence.

## 2026-10-14 18:07 +08:00 — P12/P15 scaling-evidence falsification

- Start: clean/pushed research branch at
  `b3d24bc973113beb9625df3335c1b8c3ae744fe5`. The frozen 198-row campaign and
  594 exact-law comparisons were re-read without modifying raw results.
- Negative finding: every recorded sample count is the theorem-prescribed
  schedule for that `(law,d,beta)` and each law has only one evaluated budget.
  There is no independent budget axis, stopping-time trace, instrumented
  runtime, or real-software execution. Consequently, the campaign cannot
  estimate an observed `d` exponent; fitting its schedules would be circular.
- Red-first test: the validation report initially lacked interpretation fields
  and failed on `schedule_counts_are_formula_derived`. Implemented a
  machine-readable three-field fence, portable LF report output, a complete
  scientific audit, and synchronized main/appendix wording. No empirical
  scaling figure was added.
- Current validation-report SHA-256:
  `cd6b4394bb87c42bb58861892b6eb1f05e7ef6ac084de50ebd6d864b8f5a20bb`;
  repository and Overleaf evidence copies match byte-for-byte.
- Verification: preview tests 7 passed; full suite **336 passed in 12.76 s**;
  touched Ruff, bibliography, paper, review/equation, and diff gates passed.
  Tectonic: 45 US-Letter pages, no overfull or unresolved-reference warning;
  edited pages 7 and 39 visually passed. PDF SHA-256
  `bfb9a006c00fc4e760e13baceae02cf2e5f2f19aba5df1921d93f2328c662cc8`.
- GPU decision: no run. Additional Monte Carlo under exactly known binomial
  laws is scientifically redundant. A new empirical scaling campaign is
  justified only after a stochastic executable old/new subject passes the
  declared replay-oracle gate. Next: commit/push this evidence boundary, then
  continue the remaining human-sign-off and external-CI release blockers.

### Same-checkpoint source-only Overleaf freeze

- Committed and pushed the evidence boundary as
  `92d3288df697b65efaf88fc239b853db62d26146`, with remote SHA equality.
- Packaged exactly the 31 tracked review-source entries; rejected generated
  PDF/text/build content. ZIP size 136,687 bytes; SHA-256
  `dea6d44778c64ad827a3f02cc5cdb0b7e494c0fe78e25eb650a61d46ed9d618b`.
- A first extraction compile invocation used the repository working directory
  and failed before TeX execution. The corrected fresh-extraction build passed:
  45 US-Letter pages, unencrypted, no overfull or unresolved-reference warning;
  PDF SHA-256
  `b196c2aa4aade56b2d24edbfcefc02ef4846ca82fb7a24d72e35be1f526fedb0`.
  Main-text page 7 and appendix page 39 passed visual inspection. Temporary
  release work directories were removed; the external ZIP was retained.

## 2026-10-14 22:40 +08:00 — release-acceptance reconciliation

- Start: clean, pushed branch `codex/final-submission-audit-20261012` at
  `21b0e308cc0d2fb8e224f75cfd67eaae886f79f5`.
- Rechecked the live official STOC 2027 CFP. The recorded deadline and review
  format, first-twelve-content-page, public-posting, video, authorship, and AI
  disclosure requirements remain current; no policy drift was found.
- Re-executed the frozen inventory and P17/P18 theorem-facing validators. The
  inventory contains 10 artifacts/828 rows overall; the theorem-facing summary
  contains 821 rows. The P17/P18 focused tests passed 10/10.
- Recorded the four previously omitted release hashes: P18 phase grid
  `d73c9e8...ff9`, P17 stress grid `fa61d782...942`, P17 structural fixtures
  `78d4ddf3...49c3`, and P17 scope counterexample `9759ad42...2442`.
- Corrected the critical audit's stale preview-validation hash to
  `cd6b4394...20bb`, and separated closed automated gates from required human
  sign-off and external service gates. The missing historical NVIDIA driver
  field remains open rather than being inferred from current telemetry.
- Validation: 17 focused release tests passed; review gate reports 15 TeX
  files, 130 numbered/labeled displays, and 170 total labels; manuscript,
  bibliography, and diff gates passed. No scientific claim or manuscript
  source changed, so a redundant PDF or GPU rerun was not performed.
- Remaining action: commit/push this release-control correction, then generate
  a clean release-candidate checksum manifest. A final submission freeze still
  requires human-author sign-off.

## 2026-10-15 20:45 +08:00 — composite-nuisance proof sprint

- Branch/start: `research/stoc2027-composite-nuisance-20261015` from
  `e64b781eeeddd5b1c37f750ce13164c761671aa5`; intake ZIP SHA-256
  `e16f0feb...2f67b`; complete external backup verified.
- Scientific result: exact shared-threshold witness N1 proved from the full
  four-output law; forward KL finite and reverse KL infinite. Incoming N2
  domain was falsified at negative `p` and repaired to require
  `0<p<p+eta<p+s<p+s+eta<1`. N2 now gives exact false-witness mass `2 eta`;
  N3 records candidate-only overlap. P20 and the stochastic executable-subject
  gap remain open.
- Reproduction: attached P19 CPU study reran 57,600 trials and reproduced the
  canonical CSV byte-for-byte (`3d59d674...9546`). The manuscript labels its
  six-point slopes descriptive and not measured software-runtime scaling.
- Tests/checks: 26 focused tests passed; full suite **347 passed in 13.65 s**
  with repository-local `--basetemp`; Ruff, bibliography, paper static,
  review/equation-label, and diff checks passed. An earlier default-temp run
  had 283 passes and 64 setup errors solely because the global pytest temp root
  was inaccessible.
- Paper: Tectonic built 47 unencrypted US-Letter pages; no undefined
  reference/citation, overfull box, or TeX error. PDF SHA-256
  `347a0a481543bec69061852e7963b6b7ee685f64553bbeb4257ca0f9a9eaee3f`;
  edited main and appendix pages passed 144-dpi visual inspection.
- GPU state/decision: PC1 and PC2 RTX 5070 Ti devices were reachable during
  intake; no scientifically justified GPU job was launched. Exact-law checks
  and the reproducible CPU study dominate additional Monte Carlo evidence.
- Next: freeze the source ZIP, compile it from a clean extraction, commit and
  push the feature branch, then report human/external submission blockers.
