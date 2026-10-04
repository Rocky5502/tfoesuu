# Testing Fairness of Evolving Software under Uncertainty (TFOESUU)

STOC 2027 research project on **fairness regression testing for evolving stochastic software**.

## Research question

Given a previously certified program P0, a patched version P1, a counterfactual fairness graph, and stochastic execution access, how many executions are fundamentally necessary to decide whether the patch introduced a fairness regression?

This project is intentionally **model-free**: no proprietary model API, pretrained model, or open-source model is an experimental subject or component.

## Central mechanism

Replay old and new versions with the same random tape and observe the behavioral delta:

    Z_v = P1(v; R) - P0(v; R)

Then

    Var(Z_v) = Var(P1) + Var(P0) - 2 Cov(P1,P0).

For positively correlated versions, the uncertainty of the change can be far below the uncertainty of either absolute behavior.

## Repository

- src/tfoesuu/ — mathematical and algorithmic implementation.
- experiments/ — CPU/GPU reproducible experiments.
- data/ — deterministic benchmark specifications.
- tests/ — mathematical/implementation checks.
- paper/ — Overleaf-ready manuscript.
- docs/ — theorem ledger, protocol, roadmap, provenance.
- .github/workflows/ — CPU CI.

## Setup

    python -m venv .venv
    pip install -r requirements.txt
    pip install -e .
    pytest -q
    python experiments/run_graph_sweep.py --output results/graph_sweep.csv

For NVIDIA simulation, first install the PyTorch build matching the local CUDA stack, then:

    pip install -r requirements-gpu.txt
    python experiments/run_gpu_monte_carlo.py --device cuda --trials 100000

## Integrity rules

No invented results. Conjectures stay conjectures. Synthetic benchmarks are identified as synthetic. Every long experiment must record configuration, seed, environment and source commit. External datasets/software require provenance and license records.

See docs/THEOREM_LEDGER.md and docs/ROADMAP.md.
