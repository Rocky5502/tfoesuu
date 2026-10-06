# Benchmark and specification matrix

The project uses deterministic specification data rather than scraped observational
datasets for theorem validation.  Each artifact has a distinct falsification or
reproducibility role; row count is not treated as scientific evidence.

| Artifact | Frozen rows | Primary role |
|---|---:|---|
| `benchmark_v1.jsonl` | 384 | Gaussian graph-allocation scaling and variance profiles |
| `replay_benchmark_v1.jsonl` | 54 | Bernoulli paired-replay separation |
| `software_subject_benchmark_v1.jsonl` | 32 | Executable randomized software-subject cases |
| `counterfactual_replay_benchmark_v1.jsonl` | 144 | Four-way counterfactual replay across `p,s,d,beta` regimes |
| `partial_replay_benchmark_v1.jsonl` | 168 | Partial-replay graph/group/cost/small-effect stress |
| `partial_replay_structural_cases_v1.jsonl` | 8 | Exact equality, finite-gap, and infeasible-witness fixtures |
| `partial_replay_scope_cases_v1.jsonl` | 1 | Deterministic heterogeneous-null counterexample |

Total frozen specification rows: **791**.

## Coverage principles

The benchmark suite is designed to attack theorems, not to imitate an ML benchmark leaderboard.

1. **Graph structure:** matching, star, path, clique, and structurally exact P17 fixtures.
2. **Uncertainty structure:** homogeneous, degree-weighted, and lognormal Gaussian variance profiles.
3. **Coupling strength:** multiple old/new correlations and replay-access regimes.
4. **Effect size:** large through small `gamma` or `d` values, including the regime where asymptotic exponents matter.
5. **Execution semantics:** pure mathematical oracles plus an executable randomized software subject.
6. **Positive and negative evidence:** theorem-conforming rows coexist with explicit scope-breaking counterexamples.
7. **Reproducibility:** deterministic IDs/seeds, regenerators, CI checks, and publication provenance.

## CI inventory gate

Run:

```bash
python scripts/validate_benchmark_inventory.py
```

The gate verifies that every frozen artifact exists, meets its frozen minimum row
count, contains valid unique identifiers, and remains discoverable by the
reproducibility pipeline.

## Expansion policy

New benchmark artifacts are added only when they probe a new proof obligation,
oracle assumption, graph geometry, cost model, or counterexample regime.  We do
not add unrelated public datasets merely to increase a dataset count.  External
datasets may be added later only where they can instantiate the paper's executable
old/new-version and replay assumptions without changing the estimand.
