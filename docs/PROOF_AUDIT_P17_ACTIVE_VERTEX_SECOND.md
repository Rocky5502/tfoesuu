# P17 active-vertex attainability — independent second audit

**Audit status: independent derivation completed; literature collision remains a
novelty gate. This note checks correctness, not originality.**

This audit deliberately does not reuse the first proof's "heterogeneity witness"
argument as its starting point. Instead it derives the one-query probability
laws, their KL divergence, the adaptive transcript lower bound, and the exact
finite deterministic design problem from first principles.

## 1. One-query atoms

Fix a legal replay group S containing a candidate changed endpoint x. Let
m=|S|>=2. Every group member uses the same U~Unif[0,1].

Under H0:

- U <= p, probability p:
  old=(1,...,1), new=(1,...,1);
- p < U <= p+s, probability s:
  old=(0,...,0), new=(1,...,1);
- U > p+s, probability r=1-p-s:
  old=(0,...,0), new=(0,...,0).

Under H_x:

- U <= p, probability p: same first atom;
- p < U <= p+s, probability s: same second atom;
- p+s < U <= p+s+d, probability d:
  old=(0,...,0), new has a 1 only at coordinate x;
- U > p+s+d, probability r-d:
  old=(0,...,0), new=(0,...,0).

The only new alternative atom is the one-coordinate discordance interval of mass
d. If x is not in S, the entire group law is identical under H0 and H_x.

## 2. One-query KL

For x in S, H0 has masses (p,s,r) on its three support atoms. H_x assigns
(p,s,r-d) to those same atoms and additionally assigns d to the new discordance
atom. Therefore

  D_KL(P_0^S || P_x^S)
    = p log(p/p) + s log(s/s) + r log(r/(r-d))
    = K_sync,

where

  K_sync = r log(r/(r-d)).

If x is not in S, the KL is zero.

This independently recovers the active-vertex/group information matrix

  K[i,x] = K_sync B[x,i],
  B[x,i] = 1{x in S_i}.

Group size and the identity of the synchronized reference do not appear in the
KL as long as the legal group contains x and at least one unchanged reference.

## 3. Adaptive transcript KL

Consider an arbitrary adaptive tester. Let A_t be the chosen replay group at
time t, predictable from the past transcript and internal randomization, and let
N_i be the number of times group i is queried before stopping.

By the chain rule for KL under adaptive experiment selection,

  D_KL(P_0^T || P_x^T)
    = sum_i E_0[N_i] D_KL(P_0^{S_i} || P_x^{S_i})
    = K_sync sum_{i:x in S_i} E_0[N_i].

Let Accept be the terminal decision event. A beta-correct tester has

  P_0(Accept) >= 1-beta,
  P_x(Accept) <= beta.

Data processing through the terminal decision gives

  D_KL(P_0^T || P_x^T)
    >= kl(1-beta,beta).

Hence, writing q_i=E_0[N_i],

  K_sync B q >= kl(1-beta,beta) 1.

Minimizing c^T q gives

  E_0[cost]
    >= [kl(1-beta,beta)/K_sync] C_vert,

where

  C_vert = min{c^T q : Bq>=1, q>=0}.

This lower bound applies even to adaptive testers.

## 4. Compressing the raw observation to one bit

Define the statistic

  H(S) = 1{the old/new patch-delta vector is non-constant on S}.

From the atoms above:

- under H0, H(S)=0 almost surely;
- under H_x with x in S, H(S)~Bernoulli(d);
- under H_x with x not in S, H(S)=0 almost surely.

Thus the full raw group observation contains a particularly simple one-sided
detection channel. The achievability argument can be performed entirely on this
compressed bit; no likelihood-ratio calculation is needed for the upper bound.

## 5. Exact deterministic nonadaptive design

For a deterministic schedule n in Z_+^k, endpoint x receives

  t_x = sum_{i:x in S_i} n_i = (Bn)_x

independent Bernoulli(d) detection opportunities.

The tester rejects if any H(S_i)=1. Therefore

  P_0(reject)=0,

and under H_x,

  P_x(accept)=(1-d)^{t_x}.

Let

  L = ceil(log(beta)/log(1-d)).

Then the schedule is beta-correct for every active endpoint iff

  Bn >= L 1.

Consequently, among deterministic nonadaptive schedules using this decision
rule, the exact minimum declared cost is the integer multicover

  M_L(B,c)
    = min{c^T n : Bn>=L1, n in Z_+^k}.

This is implemented by minimum_active_vertex_multicover.

## 6. Fractional relaxation and rounding

The LP relaxation of the multicover is exactly L C_vert:

  min{c^T z : Bz>=L1, z>=0}
    = L C_vert.

If b* solves the unit-cover LP, setting

  n_i=ceil(L b_i*)

is feasible and gives

  L C_vert
    <= M_L(B,c)
    <= sum_i c_i ceil(L b_i*)
    <= L C_vert + sum_{i:b_i*>0} c_i.

Thus the integer scheduling overhead is additive and does not alter the
first-order small-d scaling for a fixed finite instance.

## 7. Combined correctness statement

The independently derived sandwich is

  [kl(1-beta,beta)/K_sync] C_vert
      <= Q*
      <= M_L(B,c)
      <= L C_vert + rounding overhead,

with

  K_sync = r log(r/(r-d)),
  L = ceil(log(beta)/log(1-d)).

For fixed interior r>0,

  K_sync = d + d^2/(2r) + O(d^3).

For beta bounded away from 1/2,

  kl(1-beta,beta)=Theta(log(1/beta)),

and

  L=Theta(log(1/beta)/d).

Therefore, for a fixed replay instance as d->0,

  Q* = Theta(C_vert log(1/beta)/d)

up to the finite additive integer-rounding term.

## 8. Scope audit

Every step above uses all of the following:

1. homogeneous old threshold p on every queryable vertex;
2. homogeneous null patch s on every queryable vertex;
3. exactly one changed active endpoint x under each alternative;
4. additional shift d>0 at x;
5. per-vertex raw old/new outputs are visible;
6. all members of one legal group share exactly the same random tape;
7. legal groups have size at least two;
8. different group queries use independent tapes.

Dropping any of these assumptions requires a new proof. In particular,
multi-endpoint changes can make a group move uniformly and defeat the
heterogeneity statistic.

## 9. Independent audit verdict

No mathematical contradiction was found between the atom law, the adaptive KL
lower bound, and the deterministic multicover upper construction.

The original P17 edge-witness upper bound remains correct but is not the sharpest
known use of the raw-output oracle in this homogeneous single-endpoint family.
The active-vertex construction strictly improves it on valid instances such as
the K4 triple fixture.

**Correctness verdict:** candidate theorem appears internally sound.

**Promotion verdict:** do not yet label the result PROVED + AUDITED in the main
ledger until the controlled-sensing / active-hypothesis-testing collision audit
is closed and the manuscript theorem wording is reviewed against that prior art.
