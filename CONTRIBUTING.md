# Contributing to TFOESUU

TFOESUU is a theory-first research repository. Contributions are evaluated for
scientific correctness and reproducibility before convenience or feature count.

## Development setup

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
pytest -q
```

Optional GPU and public-benchmark dependencies remain separate in
`requirements-gpu.txt`, `requirements-public.txt`, and
`requirements-public-v2.txt`.

## Claim lifecycle

Do not promote a conjecture directly into the manuscript. A headline claim must
pass:

1. exact statement and assumptions;
2. independent derivation;
3. counterexample search;
4. finite deterministic checks where meaningful;
5. proof audit;
6. prior-art collision audit;
7. implementation correspondence;
8. tests;
9. manuscript synchronization.

The authoritative claim ledger is `docs/PROOF_STATUS.md`.

## Code changes

Theorem-backed code must:

- validate dimensions, parameter domains, and theorem scope;
- fail closed outside proved assumptions;
- distinguish query cost, concrete executions, and wall-clock/GPU cost;
- include positive, boundary, adversarial, and failure tests;
- avoid hidden heuristic fallbacks;
- keep deterministic specification data separate from empirical results.

Prefer small pure functions and explicit immutable data structures.

## Experiments

Every experiment must be tied to a scientific question. Do not add datasets or
sweeps only to increase counts.

Submission-facing empirical artifacts require:

- exact source commit;
- frozen benchmark/configuration;
- explicit seed;
- environment report;
- command line;
- metric definition;
- output checksum.

Generated result rows must never be hand-edited.

The publication pipeline is staged: CPU theorem checks -> G1 smoke/falsification
runs -> G2 frozen publication runs. A failed prediction is investigated as a
possible bug, violated assumption, or scientific discovery; it is not tuned away.

## Documentation

When a mathematical object changes, inspect and synchronize:

- `docs/PROOF_STATUS.md`;
- `docs/THEOREM_ALGORITHM_MATRIX.md`;
- relevant proof-audit notes;
- README/reproducibility documentation;
- code and tests;
- manuscript text only after the promotion gate passes.

Do not claim CI passed unless an actual workflow run executed successfully.

## Commit scope

Keep commits small and scientifically coherent. Useful prefixes include:

- `theory:` mathematical implementation/audit support;
- `test:` deterministic/adversarial checks;
- `experiment:` runners, validators, and frozen experiment contracts;
- `docs:` scientific/reproducibility documentation;
- `build:` dependency and packaging changes;
- `ci:` automated validation.

A smaller correct change is preferred to a broad change that mixes theorem,
experiment, and manuscript assumptions.
