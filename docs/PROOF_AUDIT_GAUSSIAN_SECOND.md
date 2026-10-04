# Gaussian core — independent second audit

This audit re-derives P4-P7 from the mathematical definitions rather than from
the implementation.

## P4 static upper bound

For a feasible allocation q and
n_v = ceil(8 log(2m/delta) q_v / gamma^2), every edge estimator has variance at
most gamma^2/[8 log(2m/delta)]. A centered Gaussian exceeds gamma/2 in absolute
value with probability at most 2 exp(-log(2m/delta)) = delta/m. A union bound
controls all null edges. On an alternative edge with gap at least gamma, missing
the gamma/2 threshold requires estimation error at least gamma/2, so the same
tail calculation is sufficient. Ceilings cost at most one call per active
vertex (and therefore at most |V|).

## P5 adaptive lower bound

Under the common null theta=0 let n_v=E_0[N_v]. For edge (u,v), compare against
the legal alternative theta_u=a, theta_v=-b with a+b=gamma. Transcript KL is

  n_u a^2/(2 nu_u^2) + n_v b^2/(2 nu_v^2).

Data processing through a delta-correct terminal decision gives at least
kl(1-delta,delta). Direct Lagrange minimization over a+b=gamma gives

  gamma^2 / {2 [nu_u^2/n_u + nu_v^2/n_v]}.

Hence every edge satisfies

  nu_u^2/n_u + nu_v^2/n_v
  <= gamma^2/[2 kl(1-delta,delta)].

Scaling n by gamma^2/[2 kl] produces a feasible Psi allocation and yields

  E_0[T] >= 2 kl(1-delta,delta) Psi / gamma^2.

The finite-null-mean assumption is necessary for this transcript accounting.

## P6 dual

With lambda_e>=0, the Lagrangian vertex term is

  q_v + nu_v^2 Lambda_v/q_v,

where Lambda_v=sum_{e incident v} lambda_e. Its infimum over q_v>0 is
2 nu_v sqrt(Lambda_v). Strict feasibility follows by taking all active q_v
large, so Slater gives strong duality.

## P7 exact unit-variance families

- edge: symmetry gives q_u=q_v=2, Psi=4;
- k-edge matching: add k disjoint edge optima, Psi=4k;
- clique K_n: averaging over vertex permutations preserves feasibility and cannot
  increase the convex objective, so q_v=2 and Psi=2n;
- K_{a,b}: symmetry reduces to min ax+by subject to 1/x+1/y<=1. The optimum is
  on equality with x=1+sqrt(b/a), y=1+sqrt(a/b), giving
  (sqrt(a)+sqrt(b))^2;
- a k-leaf star is K_{1,k}, hence (1+sqrt(k))^2.

## Implementation cross-check

The existing unit tests independently solve the convex primal, compare it with
the Lagrange dual under heterogeneous variances, and check all stated closed
forms and homogeneous scaling.

Status after this independent derivation:

- P4: PROVED + AUDITED
- P5: PROVED + AUDITED
- P6: PROVED + AUDITED
- P7: PROVED + AUDITED

No empirical result is used as a substitute for these derivations.
