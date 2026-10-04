# Executable stochastic software subjects

The project is theory-first. Its primary experimental objects are deterministic
theorem-stress specifications, not a large observational dataset. To ensure that
the execution oracle corresponds to executable software rather than notation
alone, the repository also includes small versioned software subjects.

## Randomized resource allocator

RandomizedResourceAllocatorPair models a service that returns a binary resource
allocation decision.

- A context is a non-protected application state such as a need tier.
- Every context has group-0 and group-1 counterfactual inputs.
- The old version uses the same allocation probability for both groups.
- A patch changes group 1 at a selected subset of contexts.
- A caller supplies the uniform random tape, so the old and new versions can be
  replayed under identical randomness.

The induced fairness graph is a matching with one counterfactual edge per
context. The replay-sound impact set is available exactly from the patch
specification. This directly instantiates the Bernoulli theory while remaining
genuine executable program logic.

Smoke command:

    python experiments/run_allocator_subject.py --contexts 64 --changed-context 17 --delta 0.01 --trials 100000

The output reports paired-oracle calls and concrete program executions separately.

## Why the subject suite stays small

A new software subject should be added only if it changes a theorem-relevant
structural property, for example:

- non-matching counterfactual graph topology;
- heterogeneous execution cost;
- partially replayable randomness;
- multiple simultaneous changed contexts;
- imperfect static change-impact information.

We do not add software subjects merely to increase benchmark count. This keeps the
artifact aligned with a STOC contribution: computation probes the theory rather
than substituting for it.
