# Reviewer quick start

TFOESUU is a **research-software artifact**, not a paper or fairness certification service. The code studies how prior certification, sound change bounds, and legal random-tape replay affect the **concrete execution cost** of scoped fairness-regression tests.

## Requirements

- Python 3.10 or newer, `pip`, and Git. A clean Python 3.12 environment is the CI target.
- CPU validation uses `numpy`, `scipy`, `networkx`, `matplotlib`, `tqdm`, and test dependencies declared in `pyproject.toml`.
- No GPU, paid API, pre-trained model, or external dataset download is required for the smoke checks.
- Historical-source audits also require the original Git commit ancestry. Do not use a shallow clone for the P12/P15 source-identity audit.

```bash
git clone https://github.com/Rocky5502/tfoesuu.git
cd tfoesuu
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/validate_benchmark_inventory.py
```

**Access:** the connected repository was private at the last verified checkpoint. The clone command works only for users granted access; it is not evidence that the code is already public.

## Ten-minute CPU review

Run these independently; they use small synthetic examples rather than long publication sweeps.

```bash
python experiments/run_gaussian_core.py --graph star --n 8 --trials 500 --gamma 0.7 --beta 0.05
python experiments/run_replay_separation.py --p 0.5 --d 0.05 --beta 0.05 --trials 1000
python experiments/validate_partial_replay_manifest.py --benchmark data/partial_replay_benchmark_v1.jsonl
python experiments/validate_control_replay_manifest.py --benchmark data/control_replay_structural_cases_v1.jsonl
```

## Reproduce the three archived evidence layers

| Layer | What the code verifies | What it does **not** establish |
| --- | --- | --- |
| P12/P15 | 198 frozen Monte Carlo configurations and 594 comparisons against exact finite laws | Executable-software runtime or a measured optimal scaling exponent |
| P19 simple null | 57,600 deterministic seeded synthetic trajectories with legal four-execution replay rounds | General composite-nuisance optimality or speedups on arbitrary software |
| Unknown shared nuisance | 24 exact rational transcript laws and a shifted-support counterexample | Robustness to unrestricted nuisance or approximate synchronization |

```bash
python scripts/validate_preview_results.py reproducibility/p12_p15/evidence/p12_p15_100k_preview_manifest_v1.json --base-dir reproducibility/p12_p15
python -m pytest -q reproducibility/p19_simple_null/test_p19_audit.py
(cd reproducibility/unknown_shared_nuisance && python -m unittest -q test_exact_witness_audit.py)
```

The P12/P15 manifest binds artifacts to an earlier commit and requires full history. Archived files are retained at their original byte hashes. The P19 renderer additionally checks the CSV hash before rendering.

## Code navigation

- `src/tfoesuu/certificate.py` and `planner.py`: sound edge-pruning and residual obligations
- `src/tfoesuu/graphs.py` and `allocation.py`: Gaussian graph allocation
- `src/tfoesuu/oracles.py` and `testers.py`: explicitly charged test observations
- `src/tfoesuu/control_replay.py`, `partial_replay.py`: legal coupling families and covers
- `src/tfoesuu/preview_results.py`: exact-law validation and provenance admission
- `data/`: specification datasets and aggregate historical software census (not raw private rows)
- `reproducibility/`: frozen independent simulations, executable audit scripts, and results
- `tests/`: falsification, scope guards, and regression checks

## Limitations and interpretation

Do not interpret a zero-witness result as unconditional fairness certification. Each theorem assumes its own null family, margin, independence/tape semantics, legal replay groups, and cost units. Dataset discrepancies in the historical Fairlearn reproduction concern **software grouping behavior**, not measured causal discrimination. Consult [proof-status scopes](PROOF_STATUS.md), [reproducibility protocol](REPRODUCIBILITY.md), and [license boundaries](../THIRD_PARTY_NOTICES.md).

## Integrity and release state

Original frozen results must not be hand-edited. Tests and simulations cannot replace independent mathematical proof review. A GitHub workflow file or a historical local pass does not imply CI passed on the current commit. This repository intentionally excludes compiled and source manuscript files from its current tree; earlier Git history may still contain them.
