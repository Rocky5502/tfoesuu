# Gaussian core proof audit

## A. Primal definition

For impacted graph `H=(V,E)` and paired-delta variances `s_v = nu_v^2 > 0`, define

`Psi = min sum_v q_v`

subject to

`s_u/q_u + s_v/q_v <= 1` for every edge `(u,v)`.

The feasible set is convex because `1/q` is convex on `q>0`, and Slater holds by taking all `q` sufficiently large.

## B. Static upper bound audit

Set

`n_v = ceil(8 log(2m/delta) q_v / gamma^2)`.

For edge `(u,v)`, Gaussian sample means give

`Var(hat_theta_u-hat_theta_v) = s_u/n_u + s_v/n_v <= gamma^2/[8 log(2m/delta)]`.

Threshold at `gamma/2`.

Under the null, each edge false-reject probability is at most `delta/m`; union bound gives at most `delta`.

Under an alternative with one true gap at least `gamma`, failure to reject requires estimation error at least `gamma/2`, again bounded by `delta/m <= delta`.

Integer ceilings add at most one query per active vertex.

## C. Adaptive lower bound audit

Use the common null `theta=0`. Let `n_v=E_0[N_v]` for a finite-expected-stopping-time algorithm.

For each edge `(u,v)`, define an alternative with `theta_u=a`, `theta_v=-b`, `a,b>=0`, `a+b=gamma`. Other coordinates remain zero. This is a valid alternative because the selected edge has gap exactly `gamma`; additional violated incident edges do not hurt validity.

Adaptive transcript KL under the null is

`n_u a^2/(2 s_u) + n_v b^2/(2 s_v)`.

Data processing through the terminal accept/reject event yields at least `kl(1-delta,delta)`.

Minimizing the quadratic subject to `a+b=gamma` gives

`gamma^2 / [2(s_u/n_u + s_v/n_v)]`.

Therefore each edge satisfies

`s_u/n_u + s_v/n_v <= gamma^2/[2 kl(1-delta,delta)]`.

Scaling expected counts gives a feasible primal solution, hence

`E_0[T] >= 2 kl(1-delta,delta) Psi / gamma^2`.

### Caveat to preserve in the theorem statement

The expected stopping time under the null must be finite. If it is infinite, the lower bound is vacuous but still true. Any later anytime-valid extension must recheck change-of-measure and optional-stopping assumptions rather than copying this proof mechanically.

## D. Dual audit

Lagrangian:

`L(q,lambda) = sum_v q_v + sum_e lambda_e(s_u/q_u+s_v/q_v-1)`.

Collecting vertex terms gives

`q_v + s_v Lambda_v/q_v`, where `Lambda_v=sum_{e incident v} lambda_e`.

The infimum over `q_v>0` is `2 sqrt(s_v Lambda_v) = 2 nu_v sqrt(Lambda_v)`.

Thus

`Psi = max_{lambda>=0} 2 sum_v nu_v sqrt(Lambda_v) - sum_e lambda_e`.

Strong duality follows from Slater.

## E. Numerical audit

The implementation compares primal and dual values for exact graph families and heterogeneous variance vectors. Unit tests require small relative duality gaps. A 10-vertex, 9-edge unit-variance star gives `Psi=16` analytically and numerically to machine precision.
