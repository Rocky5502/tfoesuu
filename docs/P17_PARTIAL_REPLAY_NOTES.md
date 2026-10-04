# P17 candidate — partial synchronized replay

**Status: UPPER BOUND PROVED IN THE FROZEN HOMOGENEOUS WITNESS MODEL; minimax
optimality OPEN. Do not promote P17 to the abstract.**

## Oracle

Let H=(V,E) be the fairness graph and let S be a declared family of legal replay
groups. A query chooses one group S in the family, draws one random tape U, and
executes both P0 and P1 on every vertex in S using that same tape.

An edge e=(u,v) is observable by this query only when {u,v} is a subset of S.
This condition is essential: P15's four-way witness needs both counterfactual
endpoints under the same tape. Observing only u or only v is not a legal P15
edge witness.

Let c(S)>0 be the cost of one replay-group query. Define the integral replay cover

  C(H,S,c) = min sum_S c(S) x_S

subject to

  sum_{S: e subset S} x_S >= 1  for every e in E,
  x_S in {0,1}.

## Safe fixed-design upper bound

Choose an optimal integral cover. One macro-round queries every selected replay
group once, using independent tapes between groups and a shared tape within each
group. In the homogeneous P16/P15 Bernoulli family, under the null every
within-group edge differential is zero pathwise. Under a single-edge alternative,
at least one selected group contains the changed edge, and its witness appears
with probability d in each macro-round.

Therefore

  T = ceil(log(beta) / log(1-d))

macro-rounds give zero type-I error and type-II error at most beta for every
single-edge alternative. Total declared cost is C(H,S,c) T.

This is a theorem-level upper bound once the oracle and homogeneous family above
are frozen. It is NOT yet a minimax characterization.

## Boundary checks

- If the only legal groups are individual fairness edges, C is the sum of their
  costs and the construction recovers edgewise four-way replay.
- If V+ itself is one legal group, one group covers every edge and the construction
  recovers the P16 whole-suite mechanism after choosing c(V+) to equal its
  concrete execution cost.
- Compatibility clusters and bounded-size replay groups interpolate between
  these extremes.
- A fairness edge contained in no legal group is not testable by this oracle.

## Why the old fractional vertex-cover candidate is not P17

The old T3 LP used q_u+q_v >= 1. That model treats endpoint observations as
substitutes. Under P15, however, the sparse pathwise differential is produced
only when u and v are co-observed with the same random tape. The correct static
coverage object for the partial-synchronization oracle is therefore an
edge-by-group incidence matrix, not a vertex-cover incidence matrix.

## Lower-bound problem still open

A matching lower bound cannot simply assert that every selected group must be
queried T times. One group may cover many alternative edges, groups may overlap,
and an adaptive tester may allocate repetitions nonuniformly. The correct lower
bound should start from transcript KL constraints indexed by edge alternatives:

  sum_{S: e subset S} E_0[N_S] K_{S,e} >= kl(1-beta,beta).

In the homogeneous witness family K_{S,e} is the P15 null-to-alternative KL when
S contains e and zero otherwise. The resulting fractional allocation LP is a
candidate *lower-bound relaxation*. Whether its value is tight, whether an
integrality gap is inherent for nonadaptive fixed designs, and whether adaptive
scheduling closes that gap are all open.

## Collision boundary

Classical common-random-number literature already studies simultaneous
comparisons among several stochastic systems; group testing studies subset
queries and feedback. Those ingredients are prior art. Any eventual novelty
claim must concern this software-version/fairness-regression replay oracle and
its proved complexity, not CRN, set cover, or subset querying themselves.
