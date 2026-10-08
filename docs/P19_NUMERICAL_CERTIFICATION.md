# P19 numerical certificate — implementation-only

The exact frozen P19 information-allocation LP is
minimize c^T q subject to K^T q >= ell * 1, q >= 0,
where ell = kl(1-beta,beta). For each legal group g, all its
nonzero information coefficients are identical to h_g.
Writing z_g = h_g*q_g/ell gives the equivalent fractional cover:
minimize sum_g (c_g/h_g) z_g subject to A z >= 1,
A[x,g] = 1{K[g,x]>0}. We normalize the objective coefficients
and verify primal feasibility, dual feasibility, the primal-dual
gap, and recovered information constraints before returning success.

Directly subtracting two O(d) terms to evaluate the boundary
KL can produce a negative number. The stable formula is

K_boundary = tau * [u - log1p(u)] + r * [-log1p(-v)-v],
u = d/tau, v = d/r, r = 1-p-s-tau.

Positive log remainders use Taylor expansions near zero; the
subnormal-tau path avoids overflowing d/tau. K_control =
-r*log1p(-d/r). For tau=0, K_boundary=K_control.

These are deterministic numerical safeguards, not new empirical
results or a new theorem. P19's two-class bipartite scope and
P20's conjecture status remain unchanged. Run the full repository
pytest suite and paper consistency/LaTeX build before publication.
