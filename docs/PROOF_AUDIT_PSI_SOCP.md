# Audit: rotated-cone representation of Psi(H,nu)

**Status: SUPPORTING PROPOSITION PROVED + AUDITED.**

This is a computational representation of the existing Gaussian allocation
quantity. It is not a novelty claim about second-order cone programming.

## 1. Starting program

For active graph vertices and positive paired-delta variances
s_v = nu_v^2, the Gaussian allocation is

  Psi(H,nu) = min sum_v q_v

subject to

  s_u/q_u + s_v/q_v <= 1     for every edge e=(u,v),
  q_v > 0                     for every active v.

Isolated vertices may be assigned q_v=0 because they occur in no constraint.

## 2. Rotated-cone formulation

For each edge e=(u,v), introduce nonnegative incidence variables
t_{e,u}, t_{e,v}. Consider

  minimize   sum_v q_v

  subject to t_{e,u} + t_{e,v} <= 1                   for every e=(u,v)
             q_u t_{e,u} >= s_u
             q_v t_{e,v} >= s_v
             q_v >= 0, t_{e,v} >= 0.

Each hyperbolic inequality q_v t_{e,v} >= s_v is a rotated second-order-cone
constraint because

  2 q_v t_{e,v} >= (sqrt(2) nu_v)^2.

Thus the program is SOCP-representable.

## 3. Equivalence: original -> conic

Take any feasible original allocation q. For every edge incidence set

  t_{e,v} = s_v/q_v.

Then q_v t_{e,v}=s_v, and for e=(u,v),

  t_{e,u}+t_{e,v}
    = s_u/q_u + s_v/q_v
    <= 1.

Hence every original feasible point extends to a conic feasible point with the
same objective.

## 4. Equivalence: conic -> original

Take any conic feasible (q,t). Because s_v>0 on every active incidence,
q_v t_{e,v} >= s_v implies q_v>0 and

  t_{e,v} >= s_v/q_v.

For e=(u,v),

  s_u/q_u + s_v/q_v
  <= t_{e,u}+t_{e,v}
  <= 1.

Therefore q is feasible for the original Psi program, again with the same
objective. The two optimal values are exactly equal.

## 5. Computational interpretation

The result means the main Gaussian allocation is an explicit standard conic
optimization problem, not only an abstract information quantity. Standard
conic-optimization methods can approximate its optimum to arbitrary numerical
precision. We do **not** make a separate novelty claim for this fact, nor do we
state a fine-grained bit-complexity theorem here.

The P17 quantities C_edge and C_vert are ordinary linear programs, so all
submission-facing fixed-design schedules arise from standard convex or linear
optimization plus deterministic rounding.

## 6. Executable correspondence

`psi_conic_certificate` in `src/tfoesuu/allocation.py` maps a candidate original
allocation q to the incidence variables t_{e,v}=s_v/q_v and reports:

- maximum edge-sum violation;
- maximum hyperbolic-product violation.

Tests apply the map to solved heterogeneous instances and require both residuals
to be at numerical tolerance.

## 7. Novelty fence

Rotated second-order-cone representations of hyperbolic constraints are standard
convex-optimization machinery. The contribution of TFOESUU remains the
fairness-regression access model and its query-complexity characterizations, not
the use of SOCP.