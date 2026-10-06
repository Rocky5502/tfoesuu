# P17 partial synchronized replay — corrected proof audit

**Status: EDGE-WITNESS UPPER PROVED; RAW-OUTPUT INFORMATION FLOOR CORRECTED;
ACTIVE-VERTEX RAW-CONTRAST UPPER PROVED + AUDITED FOR THE FROZEN HOMOGENEOUS
SINGLE-ENDPOINT FAMILY; BROADER HETEROGENEOUS/COMPOSITE-NULL PARTIAL REPLAY
REMAINS OPEN.**

## 1. Frozen oracle

Let H=(V,E) be the fairness graph and let G={S_1,...,S_k} be the legal replay
groups. Every legal replay group contains at least two vertices. A query to S_i
draws a fresh random tape U and executes both software versions on every v in
S_i using that same tape. Different group queries use independent tapes.

For a P15 four-way fairness witness on edge e=(u,v), a query is witness-legal
only when {u,v} is a subset of S_i. Raw-output information is different: a group
containing the perturbed endpoint can have a changed distribution even when it
omits that endpoint's fairness partner.

That distinction is the central correction to the earlier P17 lower-bound
attempt.

## 2. Edge-by-group witness matrix

Define the witness-incidence matrix

  A in {0,1}^{|E| x k},
  A[e,i] = 1{ e subset S_i }.

For positive query costs c, define

  C_edge = min c^T a
           subject to A a >= 1,
                      a >= 0.

This is a fractional scheduling object for legal four-way witnesses. It is not a
raw-information lower bound.

## 3. Proved fixed-design scheduling theorem

Let

  L = ceil(log(beta)/log(1-d)),
  n_i = ceil(L a_i*),

where a* is an optimal solution of the edge-cover LP.

Query group S_i exactly n_i times with independent tapes across queries and
reject when any legal within-group four-way witness appears.

For every fairness edge e,

  sum_i A[e,i] n_i
  >= L sum_i A[e,i] a_i*
  >= L.

Under the frozen homogeneous single-edge alternative, each legal witness
opportunity misses with probability 1-d; under the null, the witness is pathwise
impossible. Therefore

  P_0(reject) = 0,
  sup_e P_e(accept) <= (1-d)^L <= beta.

The total declared cost satisfies

  c^T n <= L C_edge + sum_{i:a_i*>0} c_i.

This is the theorem-level P17 upper bound.

## 4. Why the previous matching lower bound was invalid

The withdrawn proof assumed that, under an oriented edge alternative a=(u,v;x),
only groups containing both u and v changed law. That is false for the raw-output
oracle. A legal group containing x and any second synchronized vertex can carry
nonzero KL even if the second vertex is not the fairness partner.

Therefore the old edge-incidence transcript constraint

  K(d) sum_{i:e subset S_i} E_0[N_i] >= kl(1-beta,beta)

is not valid for the raw-output oracle, and the claimed matching fractional-cover
minimax lower bound is withdrawn.

## 5. Correct raw-output information matrix

Index alternatives by oriented fairness edges a=(u,v;x), where x is in {u,v} and
is the changed endpoint. Let

  r = 1-p-s,
  K_sync = r log(r/(r-d)).

Because every legal replay group has size at least two, the exact
null-to-alternative KL is

  K[i,a] = K_sync * 1{x in S_i}.

The synchronized reference need not be the fairness partner.

Transcript change of measure gives the necessary information-allocation program

  minimize c^T q
  subject to K^T q >= B_beta 1,
             q >= 0,

where B_beta = kl(1-beta,beta).

This program is a necessary expected-cost floor. It is not automatically
attainable by a uniformly valid fairness-regression tester.

## 6. Exact reduction to the active-vertex matrix

Let

  V_+ = {x in V : degree_H(x) > 0}

and define the active-vertex incidence matrix

  B in {0,1}^{|V_+| x k},
  B[x,i] = 1{x in S_i}.

All oriented alternatives that perturb the same active vertex have identical
columns in K. Hence the 2|E| transcript constraints reduce exactly to

  K_sync B q >= B_beta 1.

Define

  C_vert = min c^T q
           subject to B q >= 1,
                      q >= 0.

Then the corrected information lower program has exact value

  Q_info = (B_beta / K_sync) C_vert.

This is an exact simplification of the necessary information LP, not a matching
minimax theorem.

## 7. Relation between the two geometries

Every feasible edge-cover vector is also feasible for the active-vertex cover.
For any x in V_+, choose an incident edge e=(x,y). Then

  sum_{i:x in S_i} a_i
  >= sum_{i:e subset S_i} a_i
  >= 1.

Therefore

  C_vert <= C_edge.

The corrected P17 picture is a two-geometry sandwich:

  [kl(1-beta,beta)/K_sync] C_vert
      <= Q*
      <= L C_edge + sum_{i:a_i*>0} c_i.

The left side is a valid information-theoretic necessary bound and the right
side is the proved fixed-design witness schedule. No equality between the two
sides is claimed.

## 7a. Exact structural regimes

The two LP geometries are not universally equivalent.  Three exact regimes are
now encoded in deterministic regression fixtures.

**Group-coherent equality.**  Give each active vertex its legal-group incidence
signature sigma(x)=(1{x in S_i})_i.  If every fairness edge (u,v) satisfies
sigma(u)=sigma(v), then for every group i,

  1{{u,v} subset S_i} = 1{u in S_i} = 1{v in S_i}.

Equality propagates through each connected fairness component, so after duplicate
constraints are removed the relevant edge-cover and active-vertex-cover rows
coincide.  Therefore C_edge=C_vert.

**Unbounded finite separation.**  Let H=K_n, let the legal replay groups be
exactly the two-vertex fairness edges, and give every group unit cost.  Each group
covers only its own fairness edge, hence

  C_edge = |E(K_n)| = n(n-1)/2.

For the active-vertex LP, summing all n vertex constraints counts each pair
variable twice and gives C_vert >= n/2.  The uniform assignment
q_e=1/(n-1) attains n/2, so

  C_vert = n/2,
  C_edge/C_vert = n-1.

**Finite information with infeasible witness geometry.**  Let H be the path
0-1-2 and let the only legal groups be {0,2} and {1,2}, both with unit cost.
Every active vertex occurs in a legal group, and the active-vertex LP has value
C_vert=2.  However edge {0,1} is contained in no legal group, so the witness LP
is infeasible and C_edge=+infinity.

Consequently there is no universal finite constant alpha satisfying
C_edge <= alpha C_vert over the frozen P17 oracle class.  This is a theorem
about the two LP geometries only.  It does not prove a testing-complexity or
minimax separation, and it does not close the attainability question.

## 7b. Active-vertex raw-contrast attainability theorem

The raw-output oracle exposes more than four-way fairness-edge witnesses. In
the **frozen homogeneous threshold family**, let every vertex eligible for a
legal replay group have old threshold p. Under the null every such vertex has
new threshold p+s. Under an oriented alternative exactly one fairness-active
endpoint x has new threshold p+s+d; every other vertex remains at p+s. Assume
p>0, s>0, d>0, and p+s+d<1.

For one synchronized group query S_i with tape U, define the patch delta

  D_v(U) = P1(v;U) - P0(v;U).

Under the null, D_v(U) is identical for every member of every legal group,
pathwise. Hence a test that rejects only when the vector (D_v(U): v in S_i)
is nonconstant has zero type-I error.

Under an oriented alternative changing x, every legal group S_i containing x
also contains at least one distinct vertex y because legal groups have size at
least two. Since x is the unique changed endpoint, y remains at the common
threshold p+s. Therefore

  D_x(U) != D_y(U)
    iff U is in (p+s, p+s+d],

an event of probability d. Thus every independently replayed group query
containing x provides a raw contrast witness with probability d, even when the
group contains no fairness edge incident to x.

Let q* solve the active-vertex cover and set

  L = ceil(log(beta)/log(1-d)),
  n_i = ceil(L q_i*).

For every active vertex x,

  sum_{i:x in S_i} n_i
    >= L sum_{i:x in S_i} q_i*
    >= L.

Query each S_i exactly n_i times with independent tapes across queries and
reject on the first nonconstant within-group patch-delta vector. The null
rejection probability is zero. For any oriented single-endpoint alternative x,
the miss probability is at most

  (1-d)^{sum_{i:x in S_i} n_i}
    <= (1-d)^L
    <= beta.

The declared cost satisfies

  c^T n <= L C_vert + sum_{i:q_i*>0} c_i.

Consequently, for this frozen homogeneous family, the corrected information
floor and the raw-contrast construction use the **same combinatorial geometry**:

  [kl(1-beta,beta)/K_sync] C_vert
      <= Q*_hom
      <= L C_vert + sum_{i:q_i*>0} c_i.

This does not prove an exact finite-sample constant, and it does not extend to
an arbitrary heterogeneous fairness-preserving null. The failure is
constructive: with tau=0.20, old thresholds (0.20,0.40), new thresholds
(0.30,0.45), and shared tape U=0.25, the new-version fairness gap is only 0.15
but the patch-delta vector equals (1,0), so the homogeneous raw-contrast
predicate rejects. The frozen scope-falsification manifest records this case.
Thus within-group patch deltas may differ without any fairness violation, and
the zero-type-I argument genuinely fails beyond the stated scope.

The executable theorem correspondence is active_vertex_contrast_schedule; the
observation predicate is raw_group_contrast_witness. Deterministic tests check
active-vertex exposure, the no-joint-edge path case, and the threshold intervals
of the Bernoulli construction. Full CI, bibliography/manuscript checks, and the
real LaTeX build passed before promotion.

## 7c. Candidate group-coherent extension (not yet promoted)

A sufficient-condition extension is under audit.  Under every null, require the
patch-delta vector to be pathwise constant inside each legal replay group; the
common function may differ across disconnected replay components.  Under an
alternative indexed by active endpoint x, require every legal group containing
x to produce a nonconstant patch-delta vector with probability at least d.
With fresh independent tapes, the existing C_vert schedule then has zero
type-I error and pointwise type-II error at most beta by the same exposure
argument.  A four-vertex matching fixture demonstrates strict global
heterogeneity across two disconnected replay components.

The homogeneous Bernoulli family is a subfamily of this group-coherent class,
so its existing transcript-KL lower bound remains a necessary minimax floor for
the broader class.  This candidate therefore preserves C_vert on both certified
combinatorial sides, but it is **not PROVED + AUDITED yet**.  The dedicated
audit is docs/PROOF_AUDIT_P17_GROUP_COHERENT.md.  Promotion requires green
candidate CI and a real LaTeX build, followed by a separate synchronized
manuscript/status commit.

## 8. Small-d scaling

For fixed interior p,s,r,

  K_sync
    = r log(r/(r-d))
    = d + d^2/(2r) + O(d^3),

while

  L
    = ceil(log(beta)/log(1-d))
    = Theta(log(1/beta)/d).

Thus both certified sides have first-order d^{-1} dependence for fixed
confidence, but they can differ in the combinatorial factors C_vert and C_edge,
as well as finite-sample constants and rounding overhead.

## 9. Algorithm/proof correspondence

The repository mapping is:

- minimum_fractional_replay_cover solves the edge-by-group witness LP C_edge;
- fractional_replay_schedule implements n_i = ceil(L a_i*);
- raw_output_information_lower_bound implements the corrected raw-output
  transcript-KL floor;
- fractional_group_replay_lower_bound intentionally fails closed because its
  former interpretation was invalid;
- search_partial_replay_gap.py searches only witness-scheduling
  integral/fractional cover gaps and makes no lower-bound claim.

## 10. Promotion gates

For any extension beyond the frozen homogeneous theorem, all of the following must hold:

1. complete CI and paper build are green;
2. the edge and active-vertex matrix derivations are independently checked;
3. adversarial tests cover missing endpoints, unrelated synchronized references,
   active-vertex column collapse, and graph rewiring;
4. the raw-contrast attainability proof is independently rechecked for the
   frozen homogeneous family, and broader heterogeneous/composite-null scope is
   kept explicitly outside the claim;
5. nearest prior-art collision review is refreshed;
6. manuscript, proof ledger, code, experiments, and reproducibility notes use the
   same oracle and matrix definitions.

## 11. Novelty fence

Common random numbers, coupling, fractional covers, subset/group querying,
change of measure, and linear programming are prior art. Any eventual novelty
claim must concern a proved complexity result for the specific evolving-software
fairness-regression replay oracle, not the generic use of these tools.
