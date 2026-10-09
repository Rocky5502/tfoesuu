# Mixed-control singular asymptotics

Status: **PROVED + AUDITED for the exact P19 information lower program;
ORDER-MATCHING HYBRID UPPER; FIXED/SEQUENTIAL FAMILYWISE GAP RESOLVED**.

For fixed \(\tau>0\), let \(r=1-p-s-\tau\). The exact P19 information
channels expand as

    K_ctrl(d) = d + d^2/(2r) + d^3/(3r^2) + O(d^4),

    K_bnd(d) = b2 d^2 + b3 d^3 + O(d^4),

where

    b2 = (1/2)(1/tau + 1/r),
    b3 = (1/3)(1/r^2 - 1/tau^2).

The cancellation of the linear boundary terms explains the quadratic P18/P19
penalty. The cubic term determines part of the next coefficient.

## Exact two-term lower-program expansion

Let \(U\) contain the high-side alternatives with no control-compatible legal
group. Such a candidate cannot share a legal group with any other high
candidate: otherwise that group would itself be control-compatible. Therefore
the boundary-only blocks for \(U\) separate exactly. If

    cbar_x = min {c_i : x in S_i},

then their exact combined contribution is

    ell * sum_{x in U} cbar_x / K_bnd(d).

Let \(C_{\rm ctrl}(A\setminus U)\) be the fractional matched-control cover cost
of the remaining covered candidates, with value zero when none remain. For

    ell = kl(1-beta,beta),

the exact mixed-information LP value obeys

    Q(d) = A0/d^2 + B0/d + O(1),

where

    A0 = ell * sum_{x in U} cbar_x / b2,

    B0 = ell * C_ctrl(A\U)
         - ell * b3 * sum_{x in U} cbar_x / b2^2.

Equivalently, the leading coefficient is the value of

    minimize    c^T m
    subject to  b2 R_U^T m >= ell 1,
                m >= 0.

This is the exact lower-program expansion. The upper construction below matches
its finite-topology orders and cost functionals up to constants, not these exact
two-term coefficients.

## Hybrid achievable tester

Assume every unmatched candidate is observable and let \(m=|U|>0\). For each
\(x\in U\), query its cheapest containing group and compare it with any low
member. Under the frozen P19 null the new-version mismatch indicator is
Bernoulli(tau); under singleton alternative x it is Bernoulli(tau+d). Allocate
error beta/m to each such P18 test. Apply the zero-type-I matched-control
schedule to the residual candidates in \(A\setminus U\), then reject if either
block rejects. The declared cost is at most

    ceil(8 (tau+d) log(m/beta) / d^2) * sum_{x in U} cbar_x
    + L * C_ctrl(A\U) + control-rounding-support-cost,

where `L=ceil(log(beta)/log(1-d))`. Thus fixed finite mixed topologies attain the
same d^-2 leading order and residual d^-1 control order as the lower program,
with the same boundary-minimum and residual-cover geometry up to constants.

This construction is valid only for P19's equal-high two-class null and
singleton alternatives. It can false-positive under an arbitrary heterogeneous
fair composite null, and simultaneous changes to matched controls can hide from
the contrast.

## Proof audit

A group is boundary-only for an unmatched high candidate precisely because it
contains no second high vertex. It therefore cannot contain, or provide
information about, another high candidate. This rules out the cross-coverage
interaction conjectured in the earlier discovery note.

For the covered block, scale by \(K_{\rm ctrl}\). Its perturbed cover LP has
matrix \(C+\epsilon R\), where
\(\epsilon=K_{\rm bnd}/K_{\rm ctrl}=O(d)\). Positive fixed group costs bound
all optimizer coordinates, so the perturbed value is
\(C_{\rm ctrl}(A\setminus U)+O(d)\). Combining this with
\(1/K_{\rm ctrl}=d^{-1}+O(1)\) and the expansion of
\(1/K_{\rm bnd}\) gives the formula above.

The executable coefficient and hybrid-schedule implementations are checked against the exact LP for
positive, zero, and negative values of \(b_3\), diverse positive group costs,
fully controlled and fully boundary-only extremes, and an unobservable
candidate. A frozen counterexample test prevents accidental extension of the
matched-control predicate to an arbitrary composite null.

## Fixed allocation versus sequential expected cost

For `m=|U|` disjoint unit-cost boundary channels, any nonadaptive deterministic
allocation with familywise type-I and pointwise type-II errors at most beta has

    sum_x n_x >= sum_{k=1}^m log(1 + D_beta k) / rho2,

with `D_beta=(1-2 beta)^2/[beta(1-beta)]` and
`rho2=log(1+d^2(1/tau+1/r))`. This is `Omega(m log m/d^2)` at fixed interior
parameters, so the fixed hybrid's multiplicity penalty is not just a loose
union bound.

For the exact P19 simple null, a two-sided sequential likelihood-ratio tester
with upper boundary `m/beta` and lower boundary `beta` has global type-I and
pointwise type-II error at most beta. Its expected null rounds per boundary
channel are at most

    [log(1/beta) + log(r/(r-d))] / K_bnd,

independent of `m`. The alternative channel uses at most

    [log(m/beta) + log(1+d/tau)] / KL(P1||P0)

expected rounds. The stopping horizon is unbounded; these statements do not
extend to arbitrary composite nulls.

## Remaining target

Close exact adaptive minimax constants and audit bounded-horizon adaptive
allocations. The hybrid theorem does not promote the general P20 conjecture or
cover unknown background levels, nonexchangeable controls, or simultaneous
alternatives.
