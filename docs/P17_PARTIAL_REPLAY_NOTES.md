# P17 — partial synchronized replay

**Status: FRACTIONAL WITNESS-SCHEDULING UPPER BOUND PROVED; RAW-OUTPUT LOWER
PROGRAM CORRECTED; MATCHING MINIMAX CHARACTERIZATION OPEN.**

## Frozen oracle

Let H=(V,E) be the fairness graph and let G={S_1,...,S_k} be the legal replay
groups. Every legal replay group has at least two vertices. Querying S_i draws a
fresh random tape and runs both software versions on every vertex in S_i with
that shared tape. Different group queries use independent tapes.

Two geometries must be kept separate:

- a four-way fairness witness for edge e=(u,v) requires both endpoints in the
  same group;
- raw-output information about an oriented alternative only requires the changed
  endpoint to appear in a legal synchronized group.

## Matrix A: witness scheduling

Define

  A[e,i] = 1{ e subset S_i }.

The fractional witness-cover value is

  C_edge = min c^T a
           subject to A a >= 1,
                      a >= 0.

For

  L = ceil(log(beta)/log(1-d)),
  n_i = ceil(L a_i*),

the fixed schedule queries group i exactly n_i times and rejects when any legal
four-way witness appears.

For every alternative edge e,

  sum_i A[e,i] n_i >= L,

so its miss probability is at most (1-d)^L <= beta. The null has zero type-I
error because the witness is pathwise impossible. The declared cost obeys

  c^T n <= L C_edge + sum_{i:a_i*>0} c_i.

This is the proved P17 theorem-level upper construction.

## Matrix B: raw information

Let V_+ be the non-isolated fairness vertices and define

  B[x,i] = 1{ x in S_i },  x in V_+.

For an oriented fairness alternative a=(u,v;x), where x is the changed endpoint,
set

  r = 1-p-s,
  K_sync = r log(r/(r-d)).

Because all legal groups have size at least two,

  K[i,a] = K_sync * 1{x in S_i}.

The synchronized reference need not be the fairness partner. Therefore all
oriented alternatives changing the same x have identical information columns.

The transcript-KL constraints reduce exactly to

  K_sync B q >= kl(1-beta,beta) 1.

Define

  C_vert = min c^T q
           subject to B q >= 1,
                      q >= 0.

Then the corrected necessary raw-information floor is

  Q_info
    = [kl(1-beta,beta)/K_sync] C_vert.

This is a necessary lower program, not an achievability theorem.

## Two-geometry sandwich

Every feasible edge-cover vector is feasible for the active-vertex cover, so

  C_vert <= C_edge.

Hence the currently certified P17 bounds are

  [kl(1-beta,beta)/K_sync] C_vert
      <= Q*
      <= L C_edge + sum_{i:a_i*>0} c_i.

The left and right combinatorial objects are different. No matching equality is
claimed.

For fixed interior p,s,r and d -> 0,

  K_sync = d + d^2/(2r) + O(d^3),
  L = Theta(log(1/beta)/d).

Thus both sides have first-order d^{-1} dependence for fixed confidence, while
the remaining difficulty is the geometry/attainability gap between C_vert and
C_edge.

## Algorithmic correspondence

Algorithm A — witness scheduler:
1. construct A;
2. solve the fractional edge-cover LP;
3. set L=ceil(log(beta)/log(1-d));
4. round n_i=ceil(L a_i*);
5. query each group n_i times using independent tapes across queries;
6. reject on the first legal four-way witness.

Algorithm B — information-floor calculator:
1. construct B from active-vertex/group incidence;
2. compute K_sync;
3. solve the fractional active-vertex cover;
4. multiply its optimum by kl(1-beta,beta)/K_sync;
5. report the value only as a necessary expected-cost floor.

## Code correspondence

- minimum_fractional_replay_cover -> C_edge;
- fractional_replay_schedule -> Algorithm A;
- raw_output_information_lower_bound -> Algorithm B / transcript-KL floor;
- fractional_group_replay_lower_bound -> withdrawn and fails closed;
- search_partial_replay_gap.py -> witness-scheduling gap search only.

## Adversarial checks

The test suite checks:

- all informative legal groups have the same raw KL in the frozen oracle;
- an unrelated synchronized reference is as informative as the fairness partner
  for a fixed changed endpoint;
- absence of an active endpoint from every legal group makes the corresponding
  information constraint infeasible;
- oriented-edge columns collapse by changed vertex;
- rewiring the fairness graph while preserving the active vertex set preserves
  the raw-information LP;
- the K4 triple fixture retains the strict fractional-vs-integral witness-cover
  gap.

## What remains open

The main mathematical question is no longer whether the obsolete edge-cover
lower bound can be repaired. It cannot for the raw oracle. The right question is:

  When is the active-vertex information floor attainable by a uniformly valid
  fairness-regression tester, and when is the stronger edge-witness geometry
  fundamentally necessary?

A proof of equality under structural conditions, or a rigorous separation family,
would be a stronger P17 result than the withdrawn matching-cover claim.

## Novelty fence

Common random numbers, coupling, linear programming, set/fractional cover,
change-of-measure lower bounds, and group queries are established tools. Any
eventual novelty claim must be tied to a proved theorem for the evolving-software
fairness-regression replay model.
