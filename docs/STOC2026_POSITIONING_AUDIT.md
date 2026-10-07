# STOC 2026 positioning audit for TFOESUU

Inspected sources (2026-10-08):

- STOC 2026 official accepted-paper list:
  https://acm-stoc.org/stoc2026/accepted-papers.html
- STOC 2026 proceedings table of contents / abstracts:
  https://acm-stoc.org/stoc2026/toc.html
- STOC 2026 call for papers:
  https://acm-stoc.org/stoc2026/stoc2026-cfp.html

This document is a positioning aid, not evidence about the STOC review process
and not a claim that title/abstract style causes acceptance.

## Patterns worth emulating

The accepted list contains many papers whose titles or abstracts expose one of
the following immediately:

1. a sharp lower or upper bound ("requires", "optimal", "near-optimal");
2. a new access/oracle model and its query complexity;
3. a unified structural quantity or framework that controls several regimes;
4. a clean separation between two computational/information models;
5. a precise resolution of an open question.

Representative 2026 examples include:

- *Boolean Function Monotonicity Testing Requires (Almost) n^{1/2} Queries*;
- *Testing Distributions against Bounded Distinguishers*;
- *Combinatorial Optimization using Comparison Oracles*;
- *A Unified Approach to Memory-Sample Tradeoffs for Detecting Planted Structures*;
- *The Sample Complexity of Agnostic Multiclass Classification: Natarajan
  Dimension Strikes Back*.

Their abstracts typically define the formal problem quickly, state the main
bound/separation numerically, and only then give broader motivation.

## Implications for this manuscript

### Keep the locked title, sharpen everything below it

The title *Testing Fairness of Evolving Software under Uncertainty* is broad, so
the abstract and first page must compensate by saying immediately that this is
a query-complexity paper about version-aware replay oracles.

### Treat replay as the access model

The paper's clean theoretical spine is not "we test seven datasets." It is:

- old certificate + sound patch information are side information;
- paired/four-way/suite/partial replay are distinct observation primitives;
- query/execution complexity changes with the primitive;
- Psi(H,nu), C_edge, and C_vert are the structural complexity quantities.

The model therefore needs a compact oracle-access table and must distinguish
replay rounds from concrete executions.

### Lead with paired upper/lower statements

The Gaussian result should be presented as one characterization:

  lower: Omega(Psi * gamma^-2 * log(1/delta))
  upper: O(Psi * gamma^-2 * log(|E|/delta))

The Bernoulli story should be presented as an access separation:

  weaker access: Theta(d^-2 log(1/delta))
  stronger synchronized replay: Theta(d^-1 log(1/delta))

P17 should be presented as a geometry result plus a scope boundary, not as a
long chronological debugging story.

### Experiments are validation, not the contribution

STOC 2026 includes many papers with no benchmark-style empirical section. For
TFOESUU, deterministic theorem fixtures and synthetic stress tests are useful
for falsification and artifact review, but the manuscript must not make "815
rows" sound like the scientific contribution. Public datasets can demonstrate
that the execution model is realizable, but they cannot rescue a weak theorem
story and should remain secondary.

### Separate query complexity from computation time

Recent SODA 2026 work explicitly studies the gap between query and computational
complexity in property testing. TFOESUU currently characterizes execution/query
complexity and solves its allocation programs numerically. A worthwhile
supporting result is to expose the conic/LP structure of these allocations so
reviewers know the schedules are computationally obtainable rather than merely
information-theoretic optima.

## Manuscript changes triggered by this audit

- rewrite abstract around the formal query-complexity problem;
- add a replay-access/cost table to the model;
- keep a front-of-paper theorem-results table;
- keep the overview figure theorem-centric;
- update related work with 2026 property-testing and active-auditing neighbors;
- explore an exact conic representation of Psi(H,nu);
- keep public benchmark results out of the main PDF until frozen and validated.

## Discovery queue

1. **Completed supporting result: Psi conic representation.** The exact rotated-SOC formulation is proved, independently audited, executable-certified, and manuscript-synchronized; it is explicitly not a novelty claim.
2. **Completed scoped discovery: P18 thresholded replay phase.** One-edge synchronized replay has `Theta((tau+d)d^-2 log(1/delta))` complexity under an interior condition, explaining the `d^-1` to `d^-2` boundary.
3. **Next: heterogeneous P17 graph/group composite null.** Use P18 as the one-edge boundary condition and search for a baseline-adjusted statistic or new group geometry rather than reusing raw contrast.
4. **Multi-version amortization.** Look for a dynamic potential depending on cumulative changed structure rather than T fresh audits.
5. **Query/time separation.** Decide whether a genuine computational complexity question remains after the conic/LP computability facts are made explicit.
