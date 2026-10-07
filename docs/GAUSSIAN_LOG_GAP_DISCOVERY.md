# Gaussian log-gap discovery audit

Status: **OPEN / COLLISION-CHECKED.** No new theorem is promoted by this file.

## Problem

The current Gaussian patch-neutrality upper bound is

    O(Psi(H,nu) gamma^-2 log(|E(H)|/delta)),

whereas the adaptive null lower bound is

    Omega(Psi(H,nu) gamma^-2 log(1/delta)).

The missing question is whether the edge-count logarithm is a proof artifact,
an unavoidable structural term on some graph family, or removable by adaptive
sampling.

## Collision result

A generic statement that "adaptive sampling removes the log dimension factor"
would not be novel. Malloy and Nowak, *Sequential Testing for Sparse Recovery*,
IEEE Transactions on Information Theory 60(12), 2014,
DOI 10.1109/TIT.2014.2363846, proves sharp sequential/nonsequential differences
for sparse coordinate-wise testing. Related adaptive sensing literature makes
the same high-level phenomenon well established.

Therefore TFOESUU must not claim novelty for sequential elimination itself.

## TFOESUU-specific question

The unresolved structure is different from independent coordinates:

- one vertex execution supports every incident fairness edge;
- heterogeneous paired-delta variances enter through Psi(H,nu);
- change-impact pruning changes the residual graph before stochastic testing;
- cost may be measured in paired calls, replay rounds, or concrete executions;
- correctness is null equality on every residual edge versus a separated
  violation on at least one edge.

A meaningful strengthening must exploit or lower-bound this shared-vertex graph
incidence.

## Candidate directions

1. **Adaptive graph filtering.** Construct a multistage tester that eliminates
   edges/components while reusing vertex samples, and prove its expected null
   cost in terms of Psi rather than |E| times a per-edge budget.
2. **Structural lower family.** Search stars, cliques, complete bipartite graphs,
   and variance-skewed graphs for a necessary logarithm that survives adaptive
   vertex sampling.
3. **Separate cost notions.** A log factor might disappear for expected null
   cost while remaining in worst-case alternative cost or deterministic
   fixed-design cost. Do not conflate them.
4. **Nonadaptive lower bound.** If useful, first prove a clean fixed-design
   log-cardinality lower bound on a matching, but label it as a nonadaptive
   phenomenon and collision-check it against sparse normal-means detection.

## Promotion gate

No statement about removing or requiring log|E| enters the abstract, theorem
table, or contribution list until it has:
proof -> independent derivation -> adversarial finite checks -> archival
collision audit -> executable correspondence -> real CI/LaTeX validation.
