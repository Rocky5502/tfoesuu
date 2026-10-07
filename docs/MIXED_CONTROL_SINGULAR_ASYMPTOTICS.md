# Mixed-control singular asymptotics

Status: discovery note only; not a promoted theorem.

For fixed tau>0 let r=1-p-s-tau. The exact P19 information channels expand as

    K_ctrl(d) = d + d^2/(2r) + d^3/(3r^2) + O(d^4),

    K_bnd(d) = b2 d^2 + b3 d^3 + O(d^4),

where

    b2 = (1/2)(1/tau + 1/r),
    b3 = (1/3)(1/r^2 - 1/tau^2).

The cancellation of the linear boundary terms explains the quadratic P18/P19
penalty. The cubic term matters for any claimed next coefficient.

## Leading singular program

Let U contain the high-side alternatives with no control-compatible legal group.
If n(d) has order d^-2, set m(d)=d^2 n(d). For x in U, the leading constraints
suggest

    A0 = min c^T m
         subject to b2 R_U^T m >= ell 1,
                    m >= 0,

with ell=kl(1-beta,beta).

When U is empty, A0=0, consistent with the all-control-covered linear P19
regime. When U is nonempty and every member is observable, positive costs imply
A0>0, so the exact information lower program retains a quadratic leading term.

This is a lower-program asymptotic target, not yet a matching minimax theorem.

## Correction to the naive second coefficient

The earlier heuristic

    Q*(d) = A*/d^2 + B*/d + o(d^-1)

may still admit an expansion, but B* cannot generally be interpreted as an
independent residual control-cover cost.

First, a leading boundary allocation n=m/d^2 gives

    K_bnd(d)n = b2 m + b3 d m + O(d^2),

so boundary curvature changes next-order feasibility.

Second, a group used at order d^-2 for a boundary-only alternative can be
control-compatible for another candidate. For that candidate,

    K_ctrl(d)n = m/d + O(1),

which diverges. Such a candidate is already oversatisfied and needs no separate
order-d^-1 control allocation.

Therefore the next coefficient is a lexicographic optimal-face perturbation
problem with curvature. It depends on which A0-optimal support is chosen and
which control alternatives that support already covers.

## Correct next target

1. Prove the leading coefficient A0 for the exact P19 lower LP.
2. Characterize the A0-optimal face.
3. Derive the first perturbation on that face, including b3.
4. Identify control alternatives oversatisfied by leading allocations.
5. Optimize any remaining order-d^-1 allocation jointly with the leading face.
6. Determine whether a stable B0 exists and how to express it.
7. Separately derive or refute a matching achievable tester.

The exponent-level boundary remains plausible: complete control coverage permits
the linear P19 regime; any observable candidate with no control-compatible group
forces a quadratic leading information floor. The stronger interpretation
"quadratic boundary cost plus an independent linear control cover" is withdrawn
until proved.

The computational audit should next compare d^2 Q(d) with A0, inspect the scaled
residual d[Q(d)-A0/d^2], record leading optimal supports, vary positive group
costs, and test cases with positive, zero, and negative b3.
