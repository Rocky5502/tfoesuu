# P17 candidate audit — active-vertex attainability by raw group heterogeneity

**Status: CANDIDATE PROOF. NOT YET PROMOTED.**

This note records a stronger construction discovered after the corrected two-matrix
audit. It must pass an independent derivation, adversarial tests, literature
collision review, complete CI, and manuscript consistency before it can replace
the current P17 open-gap wording.

## 1. Frozen model

Let H=(V,E) be the fairness graph and V_+ its non-isolated vertices. Let
G={S_1,...,S_k} be legal replay groups, each containing at least two vertices,
with costs c_i>0.

A group query to S_i draws a fresh U~Unif[0,1] and returns both program versions
at every v in S_i under that same U. Different group queries use independent
tapes.

The homogeneous Bernoulli family is:

- old version: threshold p at every active vertex;
- null new version: threshold p+s at every active vertex;
- alternative indexed by active endpoint x: threshold p+s+d at x and p+s at
  every other active vertex;

with p>0, s>0, d>0, and p+s+d<1.

Every active endpoint x is a legal alternative because x is incident to at least
one fairness edge, and increasing only x by d introduces differential gap d on
each incident fairness edge.

## 2. Patch-delta heterogeneity statistic

For one synchronized group query define

  D_v(U) = P_1(v;U) - P_0(v;U),  v in S_i.

Reject that group observation when the vector (D_v : v in S_i) is not constant.

### Null law

Under the homogeneous null,

  D_v(U) = 1{ p < U <= p+s }

for every active vertex v. Therefore every legal group has a constant delta
vector pathwise, and the heterogeneity rule has exactly zero type-I error.

### Alternative law

Fix a changed endpoint x. For x,

  D_x(U) = 1{ p < U <= p+s+d },

whereas every unchanged y satisfies

  D_y(U) = 1{ p < U <= p+s }.

If a legal group contains x, it also contains at least one other vertex because
legal groups have size at least two. The frozen alternative changes only x, so
that other vertex is unchanged. Consequently the group delta vector is
heterogeneous exactly when

  U in (p+s, p+s+d],

an event of probability d.

Thus **any legal synchronized group containing x is a valid zero-type-I
d-probability detection opportunity**. The fairness partner is not special for
this decision rule.

## 3. Active-vertex fractional cover

Define the active-vertex/group incidence matrix

  B[x,i] = 1{ x in S_i },  x in V_+.

Let

  C_vert = min c^T b
           subject to B b >= 1,
                      b >= 0.

Assume C_vert is finite and let b* be an optimum.

For beta in (0,1/2), set

  L = ceil(log(beta) / log(1-d)),
  n_i = ceil(L b_i*).

Because Bb*>=1, every active endpoint x receives

  sum_{i:x in S_i} n_i
    >= L sum_{i:x in S_i} b_i*
    >= L

independent detection opportunities.

## 4. Candidate upper theorem

**Candidate theorem (active-vertex partial-replay tester).**
In the frozen model above, the fixed schedule n_i=ceil(L b_i*) with the
within-group patch-delta heterogeneity rule has

  P_0(reject) = 0

and, for every single-endpoint alternative x,

  P_x(accept) <= (1-d)^L <= beta.

Its declared query cost satisfies

  sum_i c_i n_i
    <= L C_vert + sum_{i:b_i*>0} c_i.

### Proof

The type-I statement follows pathwise from Section 2. Under alternative x, every
query of a group containing x detects with probability d, and independent group
queries use independent tapes. The total number of such queries is at least L,
so missing all detections has probability at most (1-d)^L. The cost inequality
uses ceil(z)<=z+1 on the support of b*.

No union bound over alternatives is needed: fixed-confidence correctness is
pointwise in the unknown alternative.

## 5. Existing information lower bound

For an oriented alternative changing endpoint x, a legal group query has
null-to-alternative KL

  K_sync = r log(r/(r-d)),
  r = 1-p-s,

when x is in the group and zero otherwise. Therefore adaptive transcript
change-of-measure yields

  K_sync B q >= kl(1-beta,beta) 1

for q_i=E_0[N_i]. Minimizing expected cost gives

  Q* >= [kl(1-beta,beta)/K_sync] C_vert.

This is the already corrected raw-information lower program.

## 6. Candidate matching characterization

Combining Sections 4 and 5 gives the finite-sample sandwich

  [kl(1-beta,beta)/K_sync] C_vert
      <= Q*
      <= L C_vert + R(b*),

where

  R(b*) = sum_{i:b_i*>0} c_i.

This removes C_edge from the best known upper bound for the frozen raw-output
testing problem. C_edge remains relevant only to the stricter decision rule that
insists on witnessing the actual fairness edge in the queried group.

For a fixed finite replay instance and fixed interior p,s,r,

  K_sync = d + d^2/(2r) + O(d^3)

and

  L = Theta(log(1/beta)/d).

Also

  kl(1-beta,beta)
    = (1-2 beta) log((1-beta)/beta).

Hence for beta bounded away from 1/2 and d->0,

  Q* = Theta(C_vert log(1/beta)/d)

up to the additive rounding term, which is independent of d for a fixed LP
instance.

A basic optimal solution can be chosen with support at most |V_+|, so the
rounding term needs at most |V_+| group costs; this support statement should be
independently checked before being used in a polished theorem.

## 7. Why this does not contradict P15

P15 studies the information gain from synchronizing the two endpoints of one
fairness edge relative to vertex-paired old/new replay. Here each legal group
already contains at least two synchronized vertices. Under the frozen homogeneous
single-endpoint family, any unchanged synchronized vertex acts as a reference for
the changed endpoint. The new decision rule exploits the *raw group output* rather
than insisting that the reference be the fairness partner.

Thus:

- C_edge characterizes one conservative four-way-edge-witness schedule;
- C_vert may characterize the stronger raw-output P17 oracle in the homogeneous
  single-endpoint family.

## 8. Adversarial obligations before promotion

1. Verify pathwise null constancy for every tape region.
2. Verify alternative heterogeneity occurs iff U is in (p+s,p+s+d].
3. Verify the reference need not be adjacent to x.
4. Verify every legal group has an unchanged reference under the single-endpoint
   alternative.
5. Verify the rounded schedule gives every active endpoint at least L queries.
6. Test the strict K4-triple improvement C_vert=4/3 versus C_edge=2.
7. Check heterogeneous query costs.
8. Check duplicated/dominated legal groups.
9. Check d approaching the interior boundary p+s+d<1.
10. Independently re-derive the transcript KL direction and terminal-decision
    data processing.
11. Refresh nearest prior-art collision search.
12. Keep the result scoped to the homogeneous single-endpoint alternative family;
    do not silently generalize to multiple changed endpoints or heterogeneous
    null patch effects.

## 9. Potential failure boundaries

The construction can fail outside the frozen family.

- If several vertices in the same group change identically, raw heterogeneity may
  disappear.
- If null patch effects differ by vertex, the rule can have false positives.
- If group outputs are aggregated and per-vertex old/new outcomes are hidden, the
  rule may be unavailable.
- If tapes are not aligned across vertices, pathwise cancellation disappears.

Any promoted theorem must state these boundaries explicitly.
