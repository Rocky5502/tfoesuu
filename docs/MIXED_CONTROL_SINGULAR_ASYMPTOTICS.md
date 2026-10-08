# Mixed-control singular asymptotics

Status: **PROVED + AUDITED for the exact P19 information lower program**.
This is not a matching mixed-topology tester.

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

This is a lower-program theorem, not a matching minimax theorem when \(U\) is
nonempty.

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

The executable coefficient implementation is checked against the exact LP for
positive, zero, and negative values of \(b_3\), diverse positive group costs,
fully controlled and fully boundary-only extremes, and an unobservable
candidate.

## Remaining target

Derive or refute a matching achievable tester for mixed topologies with
\(U\ne\varnothing\). The exact information floor alone does not establish
minimax attainability or promote the general P20 conjecture.
