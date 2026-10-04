# Testing Fairness of Evolving Software under Uncertainty

**STOC 2027 theory-first research repository.**

This repository studies **fairness regression testing for evolving stochastic software**. The central question is:

> Given a previously certified software version, a patch, and stochastic execution access to the old and new versions, how many executions are fundamentally necessary to determine whether the patch introduced a fairness violation?

The project is deliberately **model-free**. It uses no proprietary AI API, no pretrained model, no open-source model, and no LLM as an experimental subject. GPU computation is used only for our own stochastic simulation, graph optimization, counterexample search, and reproducibility experiments.

## Core idea

A fairness specification is represented by a counterfactual graph `G=(V,E)`. Vertices are valid software inputs; an edge `(u,v)` means that the two inputs should receive sufficiently similar outcomes. Software can be stochastic, so repeated executions return samples from input-dependent distributions.

The regression setting provides two important sources of information:

1. **Change impact:** a sound impact set localizes where a patch can have changed behavior.
2. **Coupled old/new execution:** if both versions can be replayed under the same random tape or seed, we can observe the patch-induced delta directly,

   `Z_v = P1(v; R) - P0(v; R)`.

The relevant uncertainty is then the variance of the change rather than the variance of either version in isolation:

`Var(Z_v) = Var(P1) + Var(P0) - 2 Cov(P1,P0)`.

For the Gaussian core problem, the repository studies the graph allocation quantity

`Psi(H,nu) = min sum_v q_v`

subject to

`nu_u^2/q_u + nu_v^2/q_v <= 1` for every fairness edge `(u,v)`.

The current manuscript proves an upper bound and an adaptive lower bound matching in their dependence on `Psi(H,nu)` and the separation margin `gamma`, up to confidence/logarithmic factors.

## Repository map

```text
src/tfoesuu/                 Reusable research code
  allocation.py              Psi primal/dual solvers and exact special cases
  graphs.py                  Counterfactual graph generators
  oracles.py                 Coupled Gaussian/Bernoulli version oracles
  testers.py                 Static Gaussian patch-neutrality tester
  benchmarks.py              Reproducible synthetic benchmark specifications
experiments/
  run_gaussian_core.py       CPU/GPU Monte Carlo validation
  run_bernoulli_coupling.py  Coupled-vs-independent variance experiment
  gpu_sweep.py               Multi-GPU, resumable theorem-stress sweep
scripts/
  generate_benchmark.py      Materialize benchmark manifest
  verify_environment.py      CPU/GPU environment check
paper/                       Overleaf-ready STOC manuscript sources
docs/
  PROOF_STATUS.md            Theorem ledger: proved / conjecture / open
  RESEARCH_BLUEPRINT.md      Research program and milestone order
  GPU_RUNBOOK.md             Long-run local NVIDIA workflow
  REPRODUCIBILITY.md         Exact reproduction protocol
  LITERATURE_POLICY.md       Citation-quality and novelty-audit policy
tests/                       Deterministic unit and theorem sanity tests
```

## Quick start

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
python scripts/generate_benchmark.py --output data/benchmark_v1.jsonl
python experiments/run_gaussian_core.py --graph star --n 10 --trials 10000
```

For GPU runs, install the current NVIDIA-compatible PyTorch build first, then:

```bash
pip install -r requirements-gpu.txt
python scripts/verify_environment.py
python experiments/gpu_sweep.py --devices 0,1 --trials 1000000 --output results/gpu_sweep.jsonl
```

See `docs/GPU_RUNBOOK.md` before month-scale execution.

## Mathematical guardrails

This repository keeps three categories separate:

- **PROVED:** a statement has a written proof in the manuscript and a proof-audit note.
- **COMPUTATIONALLY CHECKED:** numerical experiments agree with the statement on tested instances; this is not a proof.
- **CONJECTURE / OPEN:** a research target that must not be described as a result.

See `docs/PROOF_STATUS.md` for the live ledger.

## Current validated core

- Localization of newly introduced fairness violations to impacted edges under a sound change-impact set.
- Impossibility of uniform finite-query sharp-threshold certification under stochastic execution without a positive separation margin.
- Differential variance identity for paired old/new execution.
- Gaussian fixed-allocation upper bound parameterized by `Psi(H,nu)`.
- Adaptive information-theoretic lower bound parameterized by the same `Psi(H,nu)`.
- Exact `Psi` values for a single edge, matchings, cliques, stars, and complete bipartite graphs under unit variance.
- A primal/dual characterization of `Psi` implemented and numerically cross-checked.
- Common-uniform Bernoulli coupling formula showing that a small behavioral patch can have much lower differential variance than independent replay.

## Reproducibility philosophy

The paper is theory-first. Experiments are used to:

1. falsify conjectures before proof effort is invested;
2. check constants and special cases;
3. find adversarial graph/variance structures;
4. demonstrate scaling of proved quantities;
5. stress-test implementation correctness.

Empirical curves never substitute for theorem statements.

## Paper

The `paper/` directory is Overleaf-ready. Upload that directory as a project or connect it through your preferred Git workflow.

## Citation

A citation file is provided in `CITATION.cff`. Bibliography entries in `paper/references.bib` are restricted to peer-reviewed or otherwise essential canonical sources; the live policy is in `docs/LITERATURE_POLICY.md`.
