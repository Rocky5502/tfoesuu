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
