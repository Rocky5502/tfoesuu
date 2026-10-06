# P17 — partial synchronized replay

**Status: PROVED + AUDITED FOR THE HOMOGENEOUS SINGLE-CHANGED-ENDPOINT FAMILY
AND FOR THE GROUP-COHERENT/d-DETECTABLE SUFFICIENT-CONDITION EXTENSION.  The
active-vertex geometry C_vert is attainable in both scoped settings; arbitrary
heterogeneous/composite-null partial replay remains open.**

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

## Two geometries, and the homogeneous-family sharpening

Every feasible edge-cover vector is feasible for the active-vertex cover, so

  C_vert <= C_edge.

The four-way witness scheduler remains a valid general upper construction:

  [kl(1-beta,beta)/K_sync] C_vert
      <= Q*_hom
      <= L C_edge + sum_{i:a_i*>0} c_i.

For the frozen homogeneous single-changed-endpoint family, the audited
raw-contrast scheduler sharpens the upper side to

  [kl(1-beta,beta)/K_sync] C_vert
      <= Q*_hom
      <= L C_vert + sum_{i:q_i*>0} c_i.

Thus C_edge and C_vert remain genuinely different LP geometries, but C_vert is
the necessary and achievable combinatorial geometry for the scoped homogeneous
raw-output family. The broader heterogeneous/composite-null problem is still
open.

For fixed interior p,s,r and d -> 0,

  K_sync = d + d^2/(2r) + O(d^3),
  L = Theta(log(1/beta)/d).

Hence the scoped lower and upper costs have the same first-order d^{-1}
dependence governed by C_vert, up to finite-sample constants and rounding
support cost.

## Exact structural regimes

The corrected geometries admit three exact, deterministic regimes:

- **coherent equality:** if every fairness edge has identical endpoint
  legal-group incidence signatures, duplicate LP rows coincide and
  C_vert=C_edge;
- **unbounded finite gap:** for K_n with legal groups equal to its edges and
  unit costs, C_vert=n/2 while C_edge=n(n-1)/2, so the ratio is n-1;
- **infinite witness gap:** for the path 0-1-2 with legal groups {0,2} and
  {1,2}, C_vert=2 but C_edge is infeasible because edge {0,1} is never jointly
  replayable.

Hence no finite universal factor compares C_edge to C_vert in the frozen oracle
class.  These are LP-geometry statements only; they do not establish minimax
testing separation or attainability of the information floor.

The exact cases are checked in tests/test_partial_replay_lower.py and recorded
as deterministic specification data in
data/partial_replay_structural_cases_v1.jsonl.

The separate deterministic scope manifest
data/partial_replay_scope_cases_v1.jsonl records the explicit heterogeneous
fair-null counterexample used to prevent Algorithm C from being reported
outside its homogeneous assumptions. Scope cases are logical falsification
witnesses, not empirical error-rate measurements.

## Audited raw-contrast attainability

For the frozen homogeneous threshold family, every replay-eligible vertex has
old threshold p and null-new threshold p+s. An alternative changes exactly one
fairness-active endpoint x to p+s+d.

A legal group containing x has at least one other, unchanged synchronized member.
For a shared tape U, compare the patch deltas D_v=P1(v;U)-P0(v;U) within the
group. Under the null they are identical pathwise. Under the alternative, a
group containing x has a nonconstant delta vector exactly when U lies in
(p+s,p+s+d], probability d.

Thus the active-vertex LP can schedule an executable raw-output contrast test:
if q* minimizes C_vert, take L=ceil(log(beta)/log(1-d)) and
n_i=ceil(L q_i*). Reject on the first nonconstant within-group delta vector.
This gives zero type-I error and pointwise type-II error at most beta in the
frozen family, with cost

  c^T n <= L C_vert + sum_{i:q_i*>0} c_i.

Combined with the corrected transcript-KL lower floor, both certified sides use
C_vert in this restricted family. The claim does **not** extend automatically
to heterogeneous fairness-preserving nulls. A frozen counterexample sets
tau=0.20, old thresholds (0.20,0.40), new thresholds (0.30,0.45), and shared
tape U=0.25. The new gap 0.15 is fair, but the patch deltas are (1,0), so the
homogeneous raw-contrast predicate fires. The broader theorem therefore needs
additional controls or a different decision geometry rather than a relabeling
of Algorithm C.

## Group-coherent composite-null extension

The homogeneous theorem can be broadened without allowing arbitrary
heterogeneity.  Say the null is group-coherent when, for every legal replay
group S_i, all members have the same pathwise patch delta D_v(U) almost surely.
Different disconnected replay components may use different common patch-delta
functions.  Suppose further that under an alternative indexed by active endpoint
x, every legal group containing x produces a nonconstant patch-delta vector with
probability at least d.

Under these assumptions Algorithm C is still valid.  The null contrast
probability is zero in every queried group, active-vertex rounding supplies at
least L independent opportunities for every x, and the alternative miss
probability is at most (1-d)^L <= beta.  The cost remains

  L C_vert + sum_{i:q_i*>0} c_i.

The extension is strict: in a four-vertex matching with replay groups {0,1} and
{2,3}, one null component may use patch interval (0.20,0.30] while the other
uses (0.40,0.45].  This is globally heterogeneous but group-coherent.  A
single-endpoint extension of vertex 0 to threshold 0.35 yields contrast
probability 0.05 in {0,1}.  The exact fixture is stored in
data/partial_replay_group_coherent_cases_v1.jsonl.

Because this broader class contains the homogeneous Bernoulli subfamily, the
existing C_vert transcript-KL lower bound remains necessary for its minimax
problem.  Thus C_vert appears on both certified combinatorial sides for the
group-coherent/d-detectable class.  Arbitrary heterogeneous fair nulls that fail
group coherence remain open and are not covered by Algorithm C.

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
5. report the value as the necessary expected-cost floor.

Algorithm C — homogeneous raw-contrast scheduler:
1. solve the same active-vertex LP for q*;
2. set L=ceil(log(beta)/log(1-d)) and n_i=ceil(L q_i*);
3. replay each group S_i exactly n_i times with fresh shared tapes;
4. compute D_v=P1(v;U)-P0(v;U) within the group;
5. reject on the first nonconstant within-group D vector.

## Code correspondence

- minimum_fractional_replay_cover -> C_edge;
- fractional_replay_schedule -> Algorithm A;
- raw_output_information_lower_bound -> Algorithm B / transcript-KL floor;
- active_vertex_contrast_schedule + raw_group_contrast_witness -> Algorithm C;
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

The active-vertex raw-contrast construction is now audited for the homogeneous
single-changed-endpoint family and for the strictly broader group-coherent,
d-detectable class.  The remaining P17 question is arbitrary heterogeneous or
otherwise composite fairness-preserving nulls that violate group coherence,
where within-group patch-delta disagreement cannot be treated as a zero-type-I
witness.  Candidate routes are additional synchronized controls,
baseline-adjusted contrasts, or a new decision geometry.

## Novelty fence

Common random numbers, coupling, linear programming, set/fractional cover,
change-of-measure lower bounds, and group queries are established tools. Any
eventual novelty claim must be tied to a proved theorem for the evolving-software
fairness-regression replay model.
