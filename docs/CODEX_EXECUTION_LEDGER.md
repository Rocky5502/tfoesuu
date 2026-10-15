# Codex execution ledger

## Session 2026-10-08

- Work branch: `codex/research-audit-20261008`
- Observed baseline: `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`
- Baseline relationship: local `main`, `origin/main`, and PC2 `/home/zbq/work/tfoesuu` matched.
- PC1 environment: Windows 10 build 26200, Python 3.11.9, PyTorch 2.12.1+cu130,
  one NVIDIA GeForce RTX 5070 Ti (16,303 MiB reported by `nvidia-smi`).
- PC2 environment: WSL2 Ubuntu, Python 3.12.2, PyTorch 2.12.1+cu130, one NVIDIA
  GeForce RTX 5070 Ti (15.92 GiB reported by PyTorch), 1.3 TiB free on the D: data volume.
- Frozen public registry SHA-256:
  `b15ec8d941d16b7b2c8101b91704ee383131d904665e5864ef224cbf3c53a273`.
- Prepared manifest SHA-256 observed read-only on PC2:
  `c8a0b3419322627cc3660f8d9e8e5095234644b7ce54036cd3b4f27a5ecdfc89`.
- Prepared population counts observed on PC2: Adult 45,222; Bank 7,842; German 1,000;
  COMPAS 5,273; Law School 22,342; MEPS 15,831; Default Credit 30,000.

## Acceptance matrix

| Gate | Current evidence | State |
|---|---|---|
| G0 identity | PC1 and PC2 both at baseline SHA; PC1 baseline was clean | PASS |
| G1 software | compileall; 194 PC1 tests; 194 PC2 tests; inventory; bibliography and paper static checks | PASS, with 107 pre-existing Ruff findings |
| G2 data | V1 seven-subject schema passes its narrow validator; V2.1 separately preserves and validates complete aligned train/evaluation protected contexts and source bytes | PASS for representation; no outcome protocol implied |
| G3 math | frozen proof-status documents and P17 negative boundary present | OPEN: claim-level crosswalk audit required |
| G4 experiment | runner fails closed on prepared inputs and records a three-Git-object preparation compatibility contract | PASS for bounded public smoke; publication cost audit remains |
| G5 smoke | complete P12/P15 staged grids plus a complete seven-dataset 1k public matrix on two GPUs; exact finite-law audits green | PASS for bounded exploratory gates |
| G6 scale | publication-scale runs require approval | BLOCKED BY APPROVAL GATE |
| G7 manuscript | static consistency passed; no public result matrix exists | OPEN |
| G8 artifact | reproducibility material exists but external replication closure is incomplete | OPEN |

## Active risk register

1. Narrow theorem scopes can drift into broader fairness/null claims, especially around P17/P20.
2. The v1 public graph uses synthetic duplicated-probability endpoints, not materialized empirical
   protected-attribute counterfactuals; all claims must retain that limitation.
   A strict audit now also proves that protected names in v1 metadata cannot substitute for
   row-level protected values: five registry entries are multi-column candidates, but zero frozen
   prepared subjects are executable multi-column Fairlearn contexts.
3. Publication experiments, figures, and PDF admission evidence remain incomplete.
4. P19's nonadaptive fixed boundary block provably needs `|U| log |U|/d^2`, while sequential LR
   stopping removes the multiplicative log from expected null cost and is within the confidence-only
   factor `log(1/beta)/kl(1-beta,beta)` of the leading information constant. Markov truncation retains
   `Theta(|U|/d^2)` topology scaling under a deterministic adaptive cost cap at fixed confidence.
   Exact adaptive constants and optimal confidence dependence remain open; no arbitrary composite-null
   extension is valid.
5. Repository-wide Ruff still has pre-existing findings outside the touched files.

Resolved during this session: raw frozen-manifest SHA-256 values were not comparable across PC1 and
PC2 because Git checkout line endings differed. Future provenance records retain exact byte hashes
and add LF-normalized SHA-256 plus Git blob identity.

## Current task

Freeze the V2.1 Fairlearn analysis question before any outcome: decide and
preregister protected-group transformations, support exclusions, estimand, and
old/new training/evaluation procedure. The complete bounded no-outcome V2.1
preparation now exists at immutable PC2 path `datasets/prepared_v2/d0790b3` and
passes independent source-byte and alignment validation. The earlier V2.0 path
remains preserved but preliminary because it omitted training contexts. The separate
V2.1 schema, non-overwriting preparer, validator, and 17-test corruption suite are
implemented. Six datasets already had retained raw bytes; the missing Default
Credit archive was reacquired from the registered UCI HTTPS endpoint under CC
BY 4.0 with TLS verification, stored at a new path, and hashed. V2.1 readiness
means representation only, not outcome authorization. Do not infer groups from
V1 probabilities, manufacture a second protected
attribute, or reinterpret metadata as data. The direct
parent/child pair `e8cc637` -> `0cf59ec` passes source, locked-runtime, and
common-tape gates on PC1. The preregistered smoke isolated the documented
protected-group merge defect: old collapsed four groups to three and differed
from its canonical control, while new retained four groups and matched the
control for every frozen seed. This remains exploratory and outside manuscript
results. The Themis candidate remains rejected for evolution/replay. The strict
prepared-subject validator, dual-GPU public exploratory smoke, portable
provenance repair, P19 mixed lower expansion, and bounded-horizon adaptive
closure are complete. The public publication matrix remains behind its explicit
approval gate.

PC2 independently reproduced the exact scientific summary in an isolated uv
0.12.20-managed CPython 3.8.20 runtime with the same dependency freeze. Git
bundles were used after its existing HTTPS CA failure; certificate verification
was never bypassed. The protected PC2 baseline remains unchanged. Independent
host replication is therefore closed; manuscript admission and any larger
matrix remain gated on a frozen statistical question and approval where needed.
The exact PMF audit closes the seed-count question for the 24-row fixture:
common-tape and independent-tape disagreement laws are available analytically,
so more seeds would add noise rather than evidence.

Independent P19 verification is now closed for theorem parts (vi)--(vii).
The audit re-derived both likelihood-ratio orientations, conditional
familywise Ville bounds, Wald overshoot constants and integrability, arbitrary
serial-order cost charging, and the Markov truncation coupling. An exact
finite absorbing-chain oracle with log-likelihood increments
{-log 2, 0, +log 2} found no counterexample and is now a regression test.
No extension beyond the frozen equal-high null and singleton alternatives was
admitted. The next safe task remains freezing the V2.1 analysis estimand,
protected transformations, support rules, and old/new protocol before any
public outcome run.

The seven-dataset Fairlearn analysis question is now preregistered in a
machine-validated, no-outcome contract. Protected transformations, group
support, exact-PMF estimands, controls, common tapes, multiplicity handling,
and fail-closed policies are frozen. A read-only support audit passes all seven
datasets after selecting the pre-outcome minimum of 40 training rows per
transformed group; German male/age<25 is limiting at 45 rows.

A second hostile gate found that refitting the score model from V2.1 scalar
tokens reproduces stored evaluation probabilities bit-for-bit on six datasets
but not MEPS (maximum absolute difference 0.4504382489762433), because the
tokens do not retain source dataframe dtype semantics. Do not infer those
types. The highest-value safe next task is a non-overwriting score companion
containing aligned training/evaluation probabilities generated under the
original V2.1 loader and environment, with exact reproduction, hashes,
corruption tests, and independent validation. Public subject outcomes remain
unauthorized.

The V2.2 score companion is now complete. Clean commit
`b35c0b0d5b997afd50f154d15effffc0ac371345` was bundled with SHA-256
`db2a962cd8cf589015b4e03d1c62ef3430b42e9f8269c6b4f3dd94279da21779`,
cloned into an isolated PC2 checkout, and tested under the exact V2.1
environment (272 passed, one expected Torch-only skip). PC2 wrote only the new
800 KiB path `datasets/score_companion_v2/b35c0b0`; the protected baseline and
V2.0/V2.1 artifacts remain unchanged. Every evaluation vector exactly matches
V2.1. Manifest SHA-256:
`52ee136f3754b2f02860d07ba1a8bde3236279cd92200540a163cb47abf0a19e`;
external validation JSON SHA-256:
`56aee3a55b1214bef36b1867ca8a77dd9ad91c6ae1ce54fe9927987c62925049`.
This closes preprocessing reproducibility, not the public-outcome approval
gate. Next: independently audit the subject runner against the frozen protocol
without executing outcomes, then request approval for the bounded public
campaign if every source/runtime/common-tape/output gate passes.

The non-executing subject-runner preflight is now implemented and reproduced
on PC2. It validates the V2.1/V2.2 identities, protocol authorization fence,
protected transforms, label/row support, canonical-key injectivity, and
complete dataset census without importing Fairlearn. PC2 passed 276 tests with
one expected Torch-only skip and produced plan SHA-256
fa07b09ea675a44025ef923f28307ef2d6b1a98aa91354788cf9c5859c839a94;
preflight report SHA-256
fbb15b8b21dda43f0cbb08cb86d355e0a8d26eb2cfa692559b1bc763916b48b8.
The report says runner-preflight-only and outcome_authorized=false.
No subject outcome was observed. Next: implement the separately gated historical
runtime executor and its transcript validator using synthetic fixtures only;
the genuine seven-dataset execution remains approval-blocked.

The historical-runtime runner core is now independently gated. It provides an
immutable source-row score lookup estimator and validates a separate external
approval record bound to the exact protocol hash, old/new commits, four seeds,
bounded scope, explicit user authority, and timestamp. Missing or drifted
approval fails before any Fairlearn import. Four falsifying tests pass, the
full suite is 281 passed, and PC2's exact historical Python 3.8.20 / NumPy
1.20.3 runtime passed a synthetic lookup plus missing-approval fail-closed
check. Commit 3c5acec1573325a4b29851e89c5f7e00141d0cf8; bundle SHA-256
8e60e1b6efc6cf89b4a41bbf3d1a952f75fe0c6d213ffe36f1753de7aba86b69.
No genuine context or subject outcome was executed. Next: finish the
transcript schema/validator and exercise it only on synthetic records.

The transcript validator is now complete at commit
855e467251e730247bf273f9d832e18c1d4f70c0. It requires the full fourteen-record
old/new census and independently checks every pinned identity, PMF validity,
row/group cardinality, seed set, repeated determinism, exact PMF-threshold
predictions, four-way common tapes, repaired canonical conformance, and
single-attribute negative controls. It reports both maximum and mean exact PMF
discrepancies for every dataset, including zeros. Four synthetic attacks pass
and the complete suite is 285 passed. No public transcript exists or was
generated. Next: connect the approval-gated historical executor to this schema
and validate only synthetic subject runs; genuine execution remains blocked.

The historical executor now emits that frozen transcript schema at commit
`655abe5956dd3c12d5438bc0d3e8f8d37df0a5e5`. It rejects source-pair drift,
invalid provenance hashes, split overlap, duplicate positions, group-cardinality
drift, malformed seeds, and invalid PMFs before admitting a transcript. Eight
focused tests and all 289 repository tests pass. In PC2's pinned Python 3.8.20
runtime, the actual old and new Fairlearn classes both passed a synthetic-only
end-to-end gate: two common tapes, repeated determinism, exact threshold
correspondence, and native/canonical execution all succeeded. Canonical JSON
SHA-256 values were `03f303fabc81c557d34fe601b89fc4d82be7bdc79679bae042dae142f83740df`
(old) and `af31a5083b8eca463c83b621b854716ac21b77bd1f475c9a6dfd686b78b115e7`
(new). These differ in pinned version identity and are not public results.
No public context or outcome was loaded. The engineering blocker is closed;
fresh user approval is now the sole gate before the bounded seven-dataset
campaign.

A final hostile readiness audit found that the transcript executor still
accepted only in-memory arrays: there was no immutable bridge from V2.1/V2.2
into Python 3.8, and no last-mile clean-checkout check in the campaign entry
point. Commit `e73b6fda243b93e3b1c406f75d8daa09e28544c0` closes both gaps. Scores
cross the runtime boundary as exact hexadecimal IEEE-754 strings; every bundle
file is byte-counted and hashed against the protocol/prepared/companion/plan
identities. The runner verifies a clean pinned Git commit plus five critical
source hashes before importing Fairlearn, writes only a new output, and checks
fresh approval before any subject mount or import. All 295 local tests pass;
PC2 independently passed 294 with one expected Torch-only skip. PC2 created the
new 13,597,580-byte outcome-free bundle at
`datasets/fairlearn_public_v2_inputs/e73b6fd`, manifest SHA-256
`2435e006a8a445e0e94e7248745f5ce9b1349361d4b49b7ffd18488bcebc686e`.
The historical runtime loaded all seven exact row censuses and validated both
source trees. A missing-approval launch failed before output creation. No
Fairlearn public outcome was executed; fresh approval remains the only campaign
gate.

The manuscript evaluation section is synchronized with this boundary. It now
separates the theorem-aligned V1 GPU simulation from the V2 direct executable
software comparison, states the exact-PMF estimand and single-attribute
controls, and explicitly excludes causal or population-fairness interpretation.
It also records that the historical subject is CPU-only. The 45-page manuscript
compiled successfully with bundled Tectonic; targeted visual inspection of the
four affected pages found no clipping, overlap, or broken flow.

Fresh user authorization opened the bounded, frozen seven-dataset Fairlearn V2
campaign. The provenance-complete rerun used clean runner commit
`ade8ff3d8b764a4cbda7d06bbf062650542c5530`, immutable input-bundle manifest
SHA-256 `2435e006a8a445e0e94e7248745f5ce9b1349361d4b49b7ffd18488bcebc686e`,
and approval SHA-256
`56fc7b2cb93b1503c0ac7bcfee984ec3155eaaae82d2a0179ca96c07cc34a106`.
The old/new output SHA-256 values are respectively
`3965581b561d689b7c537781646d73e6a6ea12f147308d598f404478710d32ab`
and `6a47d03fe207adf8683eace7cd11514a27bf076ce2b34147fce3e094730e1c9d`;
the independent validation report SHA-256 is
`cc07642b3d643b046de946023a8b373affb9697c0153c2f7abbbf545a2afd6f4`.
All fourteen records passed. The parent differed from its canonical control on
Adult (max 1, mean 0.05521976534594683) and Default Credit (max 1, mean
0.10234294181034484), while COMPAS, German, Law School, Bank, and MEPS were
exact zeros. The repair was exact on all seven datasets. These are deterministic
software-behavior discrepancies, not causal or population-fairness estimates.

A new fail-closed admission renderer revalidates raw campaign provenance before
creating the complete-census JSON and booktabs table. Five new falsification
tests bring the full suite to 304 passing tests. The manuscript now reports all
seven datasets, including null findings; final-size color and grayscale review
placed the table beside its claim on page 33. The final 45-page PDF SHA-256 is
`dcf8e8a919d647da05fa76eb64544aaf000078f9249f2716713eeb0a6b97e251`.

The manuscript release audit at starting SHA
`1514af31dbd8f0fb7c37e967b2e909c50a01f48f` repaired three severe overfull
boxes and a submission-critical float-order defect: the three principal
evaluation tables and P17 audit figure had drifted to pages 42--45. The final
46-page bundled-Tectonic build reports zero overfull boxes; evidence now appears
beside its discussion on pages 32--36, Figure 4 remains with Table 6 on page 36,
and related work begins on page 37. Color, grayscale, and first-page renders
passed visual review. All 304 tests passed in 14.37 s and `git diff --check`
passed. The stable PDF is 322,376 bytes with SHA-256
`aa5e15be13d30cc40987d741f7b7a4c96436ddd446bc845aad68f7de0325720b`.

## 2026-10-13 — final-submission evidence admission

Resumed on `codex/final-submission-audit-20261012` at
`5c115824e63caed23674f6cae93f30a53bfadcb1`. The recovered P12/P15 100k
outputs matched the checkpointed SHA-256 values, but there was no executable
admission boundary. A corruption-first validator now binds the complete 198-row
census to the frozen source commit, specification and runner hashes, exact
schedules, CUDA labels, trial counts, and exact finite binomial laws.

The generated validation report has SHA-256
`32ea2d88d6475c4880d607e13023151e3f84c4a78eac05ee5e0be64b37d5c9c5`.
It confirms 594 comparisons, zero Bonferroni outliers, minimum exact p-value
`0.00046475515380564977`, and maximum absolute empirical deviation
`0.002427090218361183`. Six targeted corruption tests and all 310 repository
tests pass; Ruff and `git diff --check` pass. These remain theorem-family
sufficient-statistic simulations, not instrumented runtime or public-software
evidence. Neither GPU was used: no scientifically valid rerun was needed.

## 2026-10-13 — final five-reviewer manuscript and reproducibility gate

Independent R1--R5 audits exposed and resolved three submission-critical
issues: the Gaussian allocation incorrectly optimized over isolated vertices;
the Bernoulli results conflated delta-only and raw replay transcripts; and the
editorial package duplicated full proof blocks. The final review source now
uses active vertices, fail-closed allocation and resume guards, explicit oracle
sigma-algebras and theorem domains, and one authoritative copy of every proof.

The release includes the complete frozen 100k P12/P15 records, specs, admitted
runner snapshots, manifest, exact-law report, and hashes. Closest-work
positioning now explicitly covers Yan--Zhang 2022, Buselli et al. 2024, and
Ajarra--Basu 2026 without priority overclaims. All 324 tests passed; touched-file
Ruff and `git diff --check` passed. Bundled Tectonic produced a 44-page US
Letter review PDF with no unresolved citations/references or overfull boxes.
All 44 rendered pages passed visual inspection. PDF SHA-256:
`1197c6b14a57f567b680916cdb67510459517dedccf669917f1052ef8e355b79`.

## 2026-10-13 — final equation, CFP, and Figure 1 polish

At starting SHA `381e9c8556fc95425fa092a854eea6de6cf401c5`, the official STOC 2027 CFP
was rechecked against the review source. The manuscript remains an 11-point,
single-column, US-Letter full version with one-inch margins; the title page and
optional contents page precede the first twelve content pages, and the main
merits, technical ideas, and proof architecture occur in that initial window.
The later 12-page `acmart` rule applies to the accepted camera-ready version,
not this review submission.

The compiled source closure contained 117 legacy unnumbered displays. They
were converted mechanically to stable numbered `equation` environments with
unique labels, yielding 130 numbered/labeled displays and no duplicate labels.
A new fail-closed static checker rejects raw display math, unlabeled numbered
environments, duplicate labels, format drift, and use of ``et al.'' contrary
to the CFP's reference guidance. Figure 1 was rebuilt as editable TikZ with a
four-stage evidence-reuse path, three explicitly noninterchangeable replay-law
branches, a restrained teal/gray system, and accessible alt text.

Validation: 325 tests passed in 13.42 s; review and general paper static gates
passed; touched Python Ruff passed after correction; `git diff --check` passed.
Bundled Tectonic produced 44 US-Letter pages with zero overfull boxes and zero
unresolved citations/references. All 44 pages were rerendered; Figure 1 passed
full-size color and grayscale inspection. The pre-release PDF SHA-256 is
`69affbdf03ab1607857b232fd62c1e9c67b2f83227459b5e971246b661c2c349`.
No GPU job was launched because every experiment admitted by the manuscript is
already complete and another run would add no scientific information.

The coherent source change was committed as
`8271457701cf581363f4794299e3d53c1d1aa88f`. A source-only Overleaf ZIP was
then rebuilt without generated TeX artifacts and compiled again from a fresh
extraction. The clean-extract build passed at 44 pages with no overfull boxes
or unresolved citations/references. Final artifacts:

- ZIP SHA-256 `796f637d6ae10c587bcc401128a0d1478392c37fa53f9ac29701e5ae1763c13e`
  (135,563 bytes; 31 entries).
- PDF SHA-256 `e27195241f3260e5426e9cf2ba4e421b75216bda3f8b0839f6b3aa7f29a4179f`
  (287,719 bytes; 44 US-Letter pages).

## 2026-10-14 — repository and GitHub release-surface audit

Resumed on `codex/final-submission-audit-20261012` at
`82a2b4caa37ce5216b70f1fff274c6682cfce363`. The audit found five material
release risks: stale README claims about the completed public V2 census; an
ambiguous manuscript-source pointer; undocumented V2 dependencies; CI that did
not enforce the final review-format/equation gate or compile the authoritative
review tree; and a research branch not yet published to the remote.

A red-first release-surface test exposed the documentation, dependency-extra,
and CI gaps (three expected failures). The repaired surface now identifies
`paper/stoc2027_review/main.tex` as the authoritative source, documents the
complete 198-configuration P12/P15 campaign and fourteen-record Fairlearn V2
census, exposes reproducible `public` and `public-v2` package extras, and makes
both static manuscript gates part of CI. Generated PDFs, Overleaf ZIPs, build
directories, and experiment scratch output are excluded from Git; tracked TeX
source is retained for reproducibility.

The frozen 100k evidence revalidated independently: 198 records, 594 exact-law
comparisons, zero Bonferroni outliers, minimum exact p-value
`0.00046475515380564977`, and maximum absolute empirical deviation
`0.002427090218361183`. The report SHA-256 is
`32ea2d88d6475c4880d607e13023151e3f84c4a78eac05ee5e0be64b37d5c9c5`.
The full suite passed 329 tests in 16.25 s; the new targeted test passed 4/4;
touched-file Ruff, both manuscript static gates, the benchmark inventory, and
`git diff --check` passed. The existing final PDF is 44-page US Letter and
unencrypted. No GPU job was launched because all authorized evidence was
complete and a rerun would be scientifically redundant. A repository-wide
Ruff scan still reports 63 legacy findings outside this change and is not
misrepresented as passing.

The coherent repository release surface was committed as
`b79169e14164d506f33f912c378c214524d99d72`, frozen from a clean tree into a
299-file manifest with SHA-256
`7b6354e7901f3533cc1bb780c158dec0a12257c78f853f9e4d8bd4d07539871c`, and
pushed to `origin/codex/final-submission-audit-20261012`; the remote SHA matched
exactly. GitHub accepted both workflow dispatches but did not start either job:
the service reported failed account payments or an insufficient spending
limit. This is an external CI-infrastructure blocker, not a test failure; the
complete local gates above remain the available verification evidence.

## 2026-10-14 — historical Fairlearn row-level adversarial audit

Resumed clean on `codex/final-submission-audit-20261012` at
`7465b246dff45e65ea6927b1c45a9f735695ee4e`. The active risk review prioritized
the missing row counts, protected-tuple strata, exact-zero mechanism, and
issue-history comparison in the admitted Fairlearn case study. PC2's frozen raw
old/new outputs remained intact at the recorded SHA-256 values
`3965581b561d689b7c537781646d73e6a6ea12f147308d598f404478710d32ab`
and `6a47d03fe207adf8683eace7cd11514a27bf076ce2b34147fce3e094730e1c9d`.
They and the immutable input bundle were copied read-only to a temporary audit
directory; no dataset or result was overwritten.

A red-first test failed on the intentionally absent row-audit function. The new
fail-closed audit validates the original campaign, input-bundle file census and
hashes, source-row order, complete old/new census, and protected support before
joining exact PMFs to protected tuples. The resulting aggregate has SHA-256
`bce7829545445bb77ca874469c6fe71a2c1bd2759b607e4dc57ae0d24e56fd34`.
The parent affects 244/4,096 Adult rows (5.95703125%) and 443/4,096 Default
Credit rows (10.8154296875%); the repair affects zero rows. All 687 nonzero rows
lie in the seven Adult and two Default Credit tuples whose parent string keys
differ between the frozen training and evaluation splits.

The mechanism was independently reproduced from the pinned parent code and
checked against the official Fairlearn issue #728, direct-child repair commit
`0cf59eccfdd364417787fe2c368a1c77c3f378b8`, and PR #763. This is a
multi-population reproduction of a known fixed-width NumPy string-merge defect,
not a new bug discovery. Bank and MEPS bypass the merge as single-column
controls; COMPAS, German, and Law School have identical parent encodings across
the frozen splits, explaining their exact zeros without implying general parent
correctness.

Validation: 334 tests passed in 13.75 s; six touched Python files passed Ruff;
bibliography, general-paper, review-format, equation-label, and diff gates
passed. Bundled Tectonic produced a 45-page US-Letter, unencrypted PDF with no
overfull boxes or unresolved references. Page 38 passed full-resolution visual
inspection; PDF SHA-256 is
`74990d6bf9805a74f0cca8530605bd8a38aab5c4cbedfb961ca4d44289268012`.
Neither GPU was used: PC1 and PC2 reported 22%/1% utilization from existing
desktop workloads, and this exact-PMF audit is CPU-only.

## 2026-10-14 — hostile P12--P19 novelty audit

Resumed clean on `codex/final-submission-audit-20261012` at
`8573adaff1a53e628f3b201b024d149910281a43`. The five highest-impact remaining
risks were (1) a topic-level rather than theorem-level collision audit, (2)
overreading the P19 sequential/nonadaptive comparison as a generic discovery,
(3) absent independent human literature sign-off, (4) simulator-law evidence
that must not be presented as real-software scaling, and (5) unavailable
GitHub-hosted CI because of the account billing/spending-limit block.

A red-first release test failed on the absent claim-level audit and absent
manuscript novelty fence. The new
`docs/HOSTILE_NOVELTY_AUDIT_P12_P19.md` compares P12--P19 against primary
paired-proportion, controlled-sensing, sequential-testing, graph-design, and
active-fairness sources by mathematical overlap, transcript law, null scope,
and cost unit. It classifies P12/P13/P14/P16/P18 as specialized access-model
instantiations and P15/P17/P19 as scoped extensions. It explicitly forbids
claims to common random numbers, paired inference, fractional cover, generic
action-information LPs, or generic removal of multiplicity penalties. No
automated search is represented as independent human novelty certification.

The review manuscript now cites Malek et al. (AISTATS 2017) and Malloy--Nowak
at the P19 sequential comparison and states that this part is a specialized
instantiation whose possible increment is the replay-derived first-/second-order
mixed channel. A fail-closed test requires every P12--P19 replay claim, the
principal primary-source identifiers, the verdict vocabulary, and narrow
manuscript wording.

Validation: the red test first failed 2/6 as intended, then passed 6/6. The
first full run encountered only a Windows global pytest-temp permission error;
rerunning with repository-local `--basetemp=.pytest_tmp_novelty_full_20261014`
passed **336 tests in 12.72 s**. Touched Python Ruff, bibliography, general
paper, review-format/equation-label, and diff gates passed. Direct bundled
Tectonic compilation produced a 45-page, US-Letter, unencrypted PDF with no
overfull boxes, unresolved references, or `??` markers. The edited page 8
passed full-resolution visual inspection; validation PDF SHA-256 is
`126384a613d815b717ee092b87044f105eedfad54a2599b5e704ef132fa8f4c8`.
PC1 reported 2% utilization and 7,949/16,303 MiB; PC2 reported 1% and
7,911/16,303 MiB. No GPU job was launched because this literature/manuscript
audit has no scientifically valid GPU workload and the authorized campaigns
are complete.

## 2026-10-14 — P12/P15 empirical-scaling evidence audit

Continued from clean, pushed commit
`b3d24bc973113beb9625df3335c1b8c3ae744fe5`. A falsifying release test first
failed because the 100k validator did not state whether its records could
support an empirical sample-complexity fit. Direct schema inspection showed
that every row contains one theorem-prescribed schedule for each law; the
round/execution count therefore changes with `d` by construction. The records
contain empirical decision rates but no independent sample-budget axis,
per-trial stopping time, instrumented wall time, or executable-software
runtime. A log--log fit of those schedules would regress the formula on its own
input and falsely label a theoretical curve as an observed exponent.

The validator now emits three fail-closed interpretation fields:
`schedule_counts_are_formula_derived=true`,
`instrumented_runtime_present=false`, and
`supports_empirical_sample_complexity_fit=false`. The portable report writer
uses explicit LF bytes; the repository and Overleaf evidence copies regenerate
byte-for-byte with SHA-256
`cd6b4394bb87c42bb58861892b6eb1f05e7ef6ac084de50ebd6d864b8f5a20bb`.
`docs/P12_P15_SCALING_EVIDENCE_AUDIT.md` records the negative result and the
smallest valid future design: independently preregistered budget grids with
confidence intervals around target-error crossings, only after a stochastic
executable subject satisfies the replay-oracle gate.

The main text and appendix now state that the admitted campaign cannot
independently estimate a scaling exponent, so no empirical-complexity figure
is reported. This preserves the 100k campaign's valid role--594 exact-law
simulator checks--without overstating it. Another GPU run would reproduce
already-known binomial power curves and add no scientific information, so none
was launched.

Validation: the focused red test failed on the missing fields, then all seven
preview tests passed; the complete suite passed **336 tests in 12.76 s**.
Touched-file Ruff, bibliography, paper static, review/equation, and diff gates
passed. Bundled Tectonic produced 45 US-Letter pages with no overfull or
unresolved-reference warning. The edited main-text and appendix pages passed
full-resolution visual inspection. Validation PDF SHA-256 is
`bfb9a006c00fc4e760e13baceae02cf2e5f2f19aba5df1921d93f2328c662cc8`.

A source-only Overleaf ZIP was then frozen from the tracked
`paper/stoc2027_review` tree at commit
`92d3288df697b65efaf88fc239b853db62d26146`. It contains 31 entries and no
PDF, build directory, or extracted text. The immutable external artifact is
`TFOESUU_STOC2027_FINAL_AUDITED_OVERLEAF_2026-10-14.zip`, 136,687 bytes,
SHA-256
`dea6d44778c64ad827a3f02cc5cdb0b7e494c0fe78e25eb650a61d46ed9d618b`.
The first extraction-check command used the wrong working directory and failed
before TeX execution; rerunning from the extracted root succeeded. The fresh
extraction compiled to 45 US-Letter, unencrypted pages, and the two edited
pages passed full-resolution visual inspection. Clean-extract PDF SHA-256 was
`b196c2aa4aade56b2d24edbfcefc02ef4846ca82fb7a24d72e35be1f526fedb0`.
Temporary staging, extraction, and rendered-page files were removed after
verification; the ZIP and prior release artifacts were preserved.

## 2026-10-14 — release-acceptance reconciliation

The live official STOC 2027 call was rechecked on October 14. Its deadline,
non-anonymous authorship, public-posting consent, 11-point single-column Letter
format, one-inch margins, first-twelve-content-page rule, complete-proof rule,
video requirement, and substantive-AI disclosure language remain consistent
with the submission checklist and review source. No venue-rule drift was found.

The final checklist had stale open boxes for already completed machine gates.
The 168-row P17 executable validator, the 24-row P18 inventory, the 8-row P17
structural fixtures, and the one-row deterministic P17 scope counterexample all
revalidated. Their hashes are now recorded in the checklist. Focused release
checks passed 17 tests; review-format/equation-label, manuscript consistency,
bibliography, and diff gates passed. The review tree still has 130 numbered,
uniquely labeled displayed equations and 170 total labels.

No scientific result changed. Remaining gates are deliberately human or
external: author theorem/citation/reproduction sign-off, authorship and COI
confirmations, HotCRP consent/upload, the required author video, the final
post-sign-off Git/artifact freeze, and the missing historical NVIDIA driver
field. The driver version was not recorded in the immutable 100k manifest and
will not be reconstructed from current-machine telemetry. GitHub-hosted CI
remains blocked by the account spending limit; the complete local gates are
the current machine-verifiable evidence. No GPU run was scientifically needed.

## 2026-10-15 — ten-perspective nuisance-theory sprint

Started from clean commit `e64b781eeeddd5b1c37f750ce13164c761671aa5`
and preserved every newer local commit on feature branch
`research/stoc2027-composite-nuisance-20261015`. The supplied Overleaf ZIP
SHA-256 is
`e16f0febf989957e24155e9fb49ce41e7a9e37073b5d40f12f61e22c4a52f67b`;
a complete immutable intake backup is stored outside the repository under
`Oct 15 overleaf/intake-backup-20261015-144346-complete`.

The adversarial proof audit found one material draft defect: the proposed
shifted-support counterexample omitted `p>0`, so clipped negative thresholds
could satisfy the displayed conditions while invalidating the atom law. The
hypothesis is now `0<p<p+eta<p+s<p+s+eta<1`, guarded by a negative-domain
regression test. The exact shared-nuisance theorem was independently reduced
to complete transcript laws. Its null support is a strict subset of the
alternative support, the forward KL is
`(1-h) log((1-h)/(1-h-d))`, and the reverse KL is infinite. The result is
therefore recorded only as supporting N1; N2 is the shifted-support scope
counterexample and N3 is candidate-only marginal nonidentifiability. P20
remains open and no abstract/headline claim was enlarged.

Added the canonical exact-law implementation and adversarial tests, a
dependency-free Overleaf supplement, a theorem/novelty matrix, a detailed
proof audit, and a ten-role internal meta-review explicitly distinguished from
independent peer review. The attached P19 sequential CPU study was rerun from
source: all 57,600 trials reproduced its canonical CSV byte-for-byte, SHA-256
`3d59d674928bd93aab69dbb519ef2920aecc5c923afda43ec322a3c212089546`.
Its six-point slopes remain descriptive checks rather than theorem estimates.

The first full-suite invocation used pytest's global Windows temporary root
and produced 64 setup `PermissionError`s after 283 passing tests. The
established repository-local `--basetemp` rerun passed all **347 tests in
13.65 s**. Ruff, bibliography, paper consistency, review-format/equation, and
diff checks passed. Direct bundled Tectonic produced 47 unencrypted US-Letter
pages, with no undefined reference, missing citation, overfull box, or TeX
error; PDF SHA-256 is
`347a0a481543bec69061852e7963b6b7ee685f64553bbeb4257ca0f9a9eaee3f`.
Main-text pages containing the scope paragraph and P19 plot and appendix pages
containing the complete proposition were visually inspected at 144 dpi.

No GPU experiment was launched. PC1 and PC2 both expose RTX 5070 Ti devices,
but the new identities are exact and the supplied stochastic check already
reproduces. Additional Monte Carlo would consume GPU-hours without resolving
P20, novelty, or the executable-subject gap.

### Definitive Overleaf release freeze

The first clean-root supplement invocation exposed an import-path packaging
defect: the exact nuisance test only ran from its own directory. Commit
`37a9197` made the supplement root-runnable, and `d9d963c` refreshed the
Overleaf instructions and equation count. The definitive source-only release
contains 45 tracked inputs:

- ZIP: `TFOESUU_STOC2027_OVERLEAF_P19_NUISANCE_RELEASE_2026-10-15.zip`
- bytes: `163783`
- SHA-256: `badca88ce9204ed5bbf9cd9d211d51e3021913a209657117a16e75c6be082e7f`

A fresh extraction compiled successfully and both embedded supplements passed
from the extraction root (3 exact-nuisance tests and 6 P19 tests). The extracted
PDF has 47 unencrypted US-Letter pages, no fatal/undefined/overfull log match,
and SHA-256
`578766a2fc52e3983fecf971b2669e14dca3656c198506698c79ab95d41fcec4`.
All 47 pages were rendered; the changed main-text and appendix pages received
full-resolution visual inspection. A convenience copy is
`TFOESUU_STOC2027_AUDITED_RELEASE_2026-10-15.pdf` beside the ZIP.

The feature branch was pushed with local/remote equality at
`b5de2d481b7b659a571bbb5097be1de16ca25e6f`. The GitHub `ci` and `paper`
workflows created failed records but ran zero steps. Their check annotations
state that recent account payments failed or the spending limit must be
increased. This is an external billing gate, not a test or compilation failure;
the complete local and clean-extraction gates above remain the executed
evidence.
