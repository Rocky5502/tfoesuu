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
| G4 experiment | runner now fails closed on the complete prepared-input contract | PARTIAL: protocol and cost audit continues |
| G5 smoke | prior CUDA kernel/preflight evidence only; no new experiment launched | OPEN |
| G6 scale | publication-scale runs require approval | BLOCKED BY APPROVAL GATE |
| G7 manuscript | static consistency passed; no public result matrix exists | OPEN |
| G8 artifact | reproducibility material exists but external replication closure is incomplete | OPEN |

## Active risk register

1. Prepared data are source-commit-bound; work-branch code is incompatible until re-prepared or
   covered by an explicit validated compatibility contract.
2. Narrow theorem scopes can drift into broader fairness/null claims, especially around P17.
3. The v1 public graph uses synthetic duplicated-probability endpoints, not materialized empirical
   protected-attribute counterfactuals; all claims must retain that limitation.
4. Publication experiments, figures, and PDF admission evidence remain incomplete.
5. Repository-wide Ruff still has pre-existing findings outside the touched public-integrity files.

Resolved during this session: raw frozen-manifest SHA-256 values were not comparable across PC1 and
PC2 because Git checkout line endings differed. Future provenance records retain exact byte hashes
and add LF-normalized SHA-256 plus Git blob identity.

## Current task

Audit the public evaluator's statistical/cost contract and maintain
`docs/CODEX_CLAIM_LEDGER.md` as the theorem-to-code-to-test/manuscript crosswalk. The strict
prepared-subject validator, dual-GPU exploratory smoke, and portable provenance repair are complete.
