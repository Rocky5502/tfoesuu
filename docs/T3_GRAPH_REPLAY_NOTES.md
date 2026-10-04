# T3 graph-level Bernoulli replay — theorem-search notes

**Status: OPEN / CONJECTURE HUNTING. Nothing in this file is a paper result.**

## Candidate mechanism

P15 suggests that four-way replay can turn a differential fairness regression of
size d into a sparse witness with probability d per suitable replay round. On a
general fairness graph, a query design can potentially share work across incident
edges. This makes vertex coverage a natural object to test.

A first LP candidate is the fractional vertex-cover number

tau*(H) = min sum_v q_v
subject to q_u + q_v >= 1 for every edge (u,v), q_v >= 0.

This is not yet claimed to be the correct T3 complexity. The access model must
specify whether one replay round is vertex-local, edge-local, or can reuse a
random tape across several endpoints. Those choices change what sharing is legal.

## Why this is promising

- Matching: tau*=M, agreeing with the M independent-location structure in P13.
- Star: tau*=1, predicting that a shared center may cover all fairness obligations.
- Clique K_n: tau*=n/2, showing fractional sharing distinct from an integral cover.
- Complete bipartite K_{a,b}: tau*=min(a,b).

The triangle is an immediate diagnostic: tau*=3/2 while the integral minimum
vertex cover is 2. Any proposed tester whose legal replay primitive can only select
whole vertices may expose an integrality issue; randomized allocations may realize
the fractional value in expectation.

## Required proof gates

1. Freeze the general-graph replay oracle precisely.
2. Derive the observation law under a null with nonzero common patch effects.
3. Define an adversarial alternative family for every fairness edge.
4. Prove a fixed-allocation upper bound without silently assuming independence
   across edge tests.
5. Derive transcript-KL constraints for adaptive testers.
6. Determine whether the resulting primal is fractional vertex cover, a weighted
   cover, an edge cover, Psi-like reciprocal allocation, or another quantity.
7. Collision-check against graph property testing, graph experimental design,
   active anomaly detection, and stochastic network monitoring.
8. Only after independent proof audit update docs/PROOF_STATUS.md.

## Computational falsification

Run:

    python experiments/search_graph_replay_complexity.py --max-n 7

The graph-atlas sweep enumerates unlabeled graphs through seven vertices and
reports the largest fractional/integral cover gaps. Its purpose is to find hard
proof cases, not to produce empirical evidence for the paper.
