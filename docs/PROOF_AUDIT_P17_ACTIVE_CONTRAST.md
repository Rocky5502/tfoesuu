# Proof audit — P17 active-vertex raw contrast

**Status: PROVED + AUDITED for the frozen homogeneous single-changed-endpoint
family.** Full CI and the real LaTeX build are green on the synchronized proof
branch. This audit remains the homogeneous specialization. A separate audited
result, docs/PROOF_AUDIT_P17_GROUP_COHERENT.md, extends the same schedule to
group-coherent/d-detectable null/alternative classes; arbitrary heterogeneous
fairness-preserving nulls remain outside both claims.

## 1. Exact family

Let H=(V,E) contain at least one fairness edge and let G={S_1,...,S_k} be legal
replay groups, each of size at least two, with positive query costs c_i.

Every vertex that appears in a legal replay group has old threshold p. Under the
null every such vertex has new threshold p+s. Under an oriented alternative,
exactly one fairness-active endpoint x has new threshold p+s+d; every other
vertex remains at p+s. Assume p>0, s>0, d>0, and p+s+d<1.

A query to S_i draws one fresh U~Uniform[0,1] and executes both versions at every
member of S_i using that same U. Different group queries use independent tapes.

## 2. Observation-level contrast

For v in S_i define

  D_v(U)=P1(v;U)-P0(v;U).

The executable predicate `raw_group_contrast_witness` returns true iff the
within-group D_v vector is nonconstant.

Under H0, for every replay-eligible v,

  D_v(U)=1{U in (p,p+s]},

so all group members have identical deltas pathwise. The predicate is therefore
false almost surely and the test has exactly zero type-I error.

Under alternative x, if x is in S_i, then S_i contains a distinct y because
|S_i|>=2. The alternative changes only x, hence

  D_x(U) != D_y(U)
    iff U in (p+s,p+s+d].

The event has probability d. If x is not in S_i, the group law is unchanged and
cannot create a contrast.

## 3. Active-vertex schedule

Let B[x,i]=1{x in S_i} for fairness-active x and let

  C_vert=min c^T q subject to Bq>=1, q>=0.

If C_vert is finite, let q* be optimal and define

  L=ceil(log(beta)/log(1-d)),
  n_i=ceil(L q_i*).

For every active x,

  sum_{i:x in S_i} n_i
    >= L sum_{i:x in S_i} q_i*
    >= L.

Each query containing the changed endpoint uses an independent tape and exposes
a contrast with probability d. Thus the pointwise miss probability is

  (1-d)^{sum_{i:x in S_i} n_i} <= (1-d)^L <= beta.

The declared cost obeys

  c^T n
    <= L c^T q* + sum_{i:q_i*>0} c_i
    = L C_vert + sum_{i:q_i*>0} c_i.

## 4. Matching combinatorial geometry with the lower program

The already-audited raw-output transcript lower program has exact value

  [kl(1-beta,beta)/K_sync] C_vert,

where

  K_sync=(1-p-s) log((1-p-s)/(1-p-s-d)).

Therefore both the necessary information floor and the executable fixed design
use C_vert for this family. This is a matching **combinatorial geometry** and
small-d order statement, not an equality of finite-sample constants.

On every fixed replay instance with fixed interior p,s and beta,
K_sync=d+O(d^2) and L=Theta(1/d), so the lower and upper costs have the same
first-order d^{-1} dependence governed by C_vert, up to rounding support cost.

## 5. Why the scope cannot be silently generalized

The zero-type-I argument requires a homogeneous pathwise null across all group
members, not merely that the fairness graph has no violating edge.

A concrete two-vertex counterexample already suffices. Let the fairness graph
contain only edge (0,1), let the fairness tolerance be tau=0.20, take old
Bernoulli thresholds (0.20,0.40), and new thresholds (0.30,0.45). The new
fairness gap is 0.15 <= tau, so this is a fairness-preserving null. At shared
tape U=0.25 the old outputs are (0,1), the new outputs are (1,1), and therefore
the patch deltas are (1,0). The raw-group contrast predicate fires even though
the fairness null is true.

This deterministic witness is encoded in
data/partial_replay_scope_cases_v1.jsonl and exercised by both the direct
scope-guard regression and the manifest round-trip test. It proves only that
the naive homogeneous contrast rule is not uniformly valid for arbitrary
heterogeneous/composite fairness-preserving nulls; it does not characterize the
optimal broader tester. A fully arbitrary heterogeneous/composite-null extension remains open.  The
separate group-coherent theorem covers the sufficient-condition subclass where
null patch deltas are pathwise equal inside every legal replay group.

## 6. Adversarial implementation checks

- all active vertices receive at least L rounded exposure;
- the path 0-1-2 with groups {0,2},{1,2} is testable although C_edge is
  infeasible;
- four representative common-uniform threshold regions verify the pathwise
  contrast event;
- an unrelated synchronized reference triggers the alternative contrast;
- malformed/singleton observation vectors fail closed;
- a frozen heterogeneous fair-null scope case provably triggers the homogeneous
  raw-contrast predicate, preventing silent theorem generalization;
- raw lower and raw-contrast upper recompute the same C_vert optimum;
- the 8-row structural specification manifest records and checks the exact
  normalized raw-contrast cost;
- all 168 parameter-stress rows materialize their rounded schedules and verify,
  for every active endpoint, both exposure at least L and the exact finite-sample
  miss bound `(1-d)^N_x <= beta`.

## 7. Prior-art fence

Common random numbers, multiple-system simulation comparison, control variates,
and multiple-comparison procedures are established. The theorem does not claim
those techniques. The research claim is the active-vertex fractional-cover query
geometry induced by version-aware fairness-regression access in the frozen family.

## 8. Completed promotion audit

The synchronized branch passed all deterministic tests and full CI, bibliography
and manuscript consistency checks, and the real LaTeX build. The status ledger,
theorem/algorithm matrix, roadmap, novelty fence, README, data documentation,
and manuscript use the same homogeneous-family scope for P17-A.  P17-C was
audited separately before promotion and extends only to group-coherent,
d-detectable settings; arbitrary within-group heterogeneous fair nulls remain
open.
