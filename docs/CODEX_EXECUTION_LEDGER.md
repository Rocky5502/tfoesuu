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
| G2 data | seven nonzero NPZ/JSON pairs and manifest pass strict schema/content/hash validation | PASS for frozen prepared artifacts |
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

Run the bounded no-outcome V2 preparation/validation on PC2 from a clean commit
and the frozen seven-source map. The separate
V2 schema, non-overwriting preparer, validator, and 15-test corruption suite are
implemented. Six datasets already had retained raw bytes; the missing Default
Credit archive was reacquired from the registered UCI HTTPS endpoint under CC
BY 4.0 with TLS verification, stored at a new path, and hashed. No complete V2
output exists yet and readiness remains false. Do not infer it from V1 probabilities, manufacture a second protected
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
