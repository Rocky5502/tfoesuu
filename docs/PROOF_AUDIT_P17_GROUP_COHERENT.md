# Proof audit — P17 group-coherent composite-null extension

**Status: PROVED + AUDITED.  The pre-promotion candidate commit
`012d0bdc44c761073f5a7f3e9e912e50e2af7192` passed full CI, adversarial
tests, manifest regeneration, bibliography/manuscript consistency, artifact
freeze validation, and both push- and PR-triggered real LaTeX builds before
manuscript promotion.**

## 1. Model and scope

Let H=(V,E) be the fairness graph and G={S_1,...,S_k} the legal replay groups,
each of size at least two, with positive query costs c_i. A query to S_i draws a
fresh random tape U and executes both program versions on every v in S_i using
that same tape. Distinct group queries use independent tapes.

For one query define the patch delta

  D_v(U)=P1(v;U)-P0(v;U).

The null class is **group-coherent** when, for every legal group S_i, there is a
measurable function h_i such that

  D_v(U)=h_i(U)  almost surely for every v in S_i.

Different replay components may have different h_i. If two legal groups overlap,
their common vertex forces the corresponding h_i functions to agree almost
surely on the overlap, so heterogeneity can persist across disconnected replay
components without requiring global homogeneity.

An alternative indexed by fairness-active endpoint x is d-detectable when every
legal group containing x satisfies

  P_x( (D_v(U):v in S_i) is nonconstant ) >= d.

No claim is made for arbitrary heterogeneous fairness-preserving nulls that fail
group coherence.

## 2. Theorem

Let

  B[x,i]=1{x in S_i}

for fairness-active x and define

  C_vert=min c^T q
         subject to Bq>=1,
                    q>=0.

Assume C_vert<infinity and let q* be optimal. For beta in (0,1/2) and d in
(0,1), set

  L=ceil(log(beta)/log(1-d)),
  n_i=ceil(L q_i*).

Query S_i exactly n_i times with independent tapes and reject on the first
nonconstant within-group patch-delta vector.

Then:

1. every group-coherent null has type-I error exactly zero;
2. every d-detectable alternative x has type-II error at most beta; and
3. declared query cost satisfies

     c^T n <= L C_vert + sum_{i:q_i*>0} c_i.

## 3. Proof

Under any group-coherent null, every queried group has a constant patch-delta
vector almost surely. The rejection predicate is therefore false on every query,
so type-I error is zero.

For any active endpoint x, feasibility of q* and upward rounding give

  sum_{i:x in S_i} n_i
    >= L sum_{i:x in S_i} q_i*
    >= L.

Under a d-detectable alternative x, each independent query to a group containing
x misses the contrast event with probability at most 1-d. Fresh tapes make the
query-level miss events independent. Hence the probability that every query
containing x misses is at most

  (1-d)^{sum_{i:x in S_i} n_i}
    <= (1-d)^L
    <= beta.

Finally, ceil(L q_i*) <= L q_i*+1 on the positive support of q*, yielding

  c^T n <= L c^T q* + sum_{i:q_i*>0} c_i.

This proves all three claims.

## 4. Strict extension beyond global homogeneity

Take a four-vertex matching with legal groups {0,1} and {2,3}. Under the null,
vertices 0 and 1 use old threshold 0.20 and new threshold 0.30, while vertices 2
and 3 use old threshold 0.40 and new threshold 0.45. The program is globally
heterogeneous, but each legal replay group has pathwise-identical patch deltas.

If alternative x=0 changes only vertex 0's new threshold to 0.35, then each query
to {0,1} exposes a contrast exactly on U in (0.30,0.35], probability d=0.05.
The group {2,3} remains contrast-free. Thus the theorem strictly contains the
globally homogeneous Bernoulli family.

The deterministic specification is stored in
data/partial_replay_group_coherent_cases_v1.jsonl.

## 5. Information lower bound inherited from the homogeneous subfamily

The group-coherent class contains the already-audited homogeneous Bernoulli P17
family. Therefore every tester uniformly valid for the broader class must also
be valid on that homogeneous subfamily. The existing transcript-KL argument
hence remains a necessary lower bound:

  [kl(1-beta,beta)/K_sync] C_vert <= Q*_gc,

for the embedded homogeneous thresholds, where

  K_sync=(1-p-s) log((1-p-s)/(1-p-s-d)).

Combining this inherited lower bound with the group-coherent schedule gives the
same active-vertex combinatorial geometry on both certified sides. For fixed
interior p,s and fixed confidence, K_sync=d+O(d^2) and
L=Theta(log(1/beta)/d), so the small-d order is Theta(C_vert/d) up to constants
and rounding support cost.

This is a scoped minimax sandwich for the group-coherent/d-detectable class. It
does not characterize arbitrary heterogeneous composite nulls.

## 6. Adversarial boundary

The frozen scope counterexample with tau=0.20, old thresholds (0.20,0.40), and
new thresholds (0.30,0.45) violates group coherence inside its legal two-vertex
group: at U=0.25 the patch deltas are (1,0) even though the new fairness gap is
only 0.15. The theorem therefore excludes exactly the failure mode already
encoded by the P17 scope-falsification manifest.

## 7. Executable correspondence

- raw_group_contrast_witness implements the observation-level rejection event;
- active_vertex_contrast_schedule implements the C_vert fixed design;
- tests/test_partial_replay_lower.py checks a globally heterogeneous but
  group-coherent null and its single-endpoint alternative;
- tests/test_partial_replay_benchmarks.py checks the frozen coherent-case
  manifest and exact C_vert geometry;
- data/partial_replay_group_coherent_cases_v1.jsonl is deterministic
  specification data, not empirical evidence.

## 8. Promotion gate result

The gate was executed before promotion on candidate commit
`012d0bdc44c761073f5a7f3e9e912e50e2af7192`.

1. theorem/code/data definitions were synchronized on the candidate branch;
2. full pytest and adversarial tests passed;
3. the committed coherent-case manifest round-tripped exactly;
4. bibliography, manuscript consistency, and submission-manifest checks passed;
5. push CI and PR CI passed; and
6. both push- and PR-triggered real LaTeX builds passed.

The promotion commit adds the manuscript proposition and flips the ledger only
after those gates.  The promoted commit is itself required to rerun CI and the
paper build before merge.
