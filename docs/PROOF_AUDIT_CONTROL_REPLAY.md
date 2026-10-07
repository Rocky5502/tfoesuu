# Proof audit: matched-background controls under heterogeneous fairness nulls

**Status: P19 PROVED + AUDITED for the frozen two-class bipartite threshold family.**

The statistical ingredients (common random numbers, matched controls, Bernoulli
change of measure, fractional covering) are established tools. The result here
is their exact query-complexity consequence for partial replay in version-aware
fairness regression.

## 1. Frozen heterogeneous null family

Let H=(A union B,E) be bipartite, with every fairness edge crossing from high
class A to low class B. Every old-version threshold equals p. Fix s>=0,
tau>0, d>0, and p+s+tau+d<1.

Under the common null:

  low vertices:  new threshold p+s,
  high vertices: new threshold p+s+tau.

Thus every fairness edge has new-version gap exactly tau and is fair at
tolerance tau.

Alternative x for x in A increases only x to threshold p+s+tau+d. Every edge
incident to x then has gap tau+d, so the alternative is a fairness regression.

A legal replay group S_i has size at least two, cost c_i>0, and one fresh
uniform tape shared across both versions and every group member.

## 2. Two exact per-query information rates

Write

  h = p+s+tau,
  r = 1-h.

Fix alternative x in A.

### Control-compatible group

If S_i contains x and at least one other high vertex, then under the null all
high vertices in the group have identical old/new threshold pairs. The
alternative creates a new transcript state only on U in (h,h+d]. Under the
null the all-zero-above-h transcript atom has mass r; under the alternative it
has mass r-d and the new x-only state has mass d. Therefore

  K_control(d) = r log(r/(r-d)) = d + O(d^2).

### Boundary-only group

If S_i contains x but no other high vertex, all its other members are low.
The null already has a high-vs-low transcript interval of mass tau. Under the
alternative this mass becomes tau+d while the all-zero mass becomes r-d. Hence

  K_boundary(tau,d)
    = tau log(tau/(tau+d)) + r log(r/(r-d))
    = (d^2/2)(1/tau + 1/r) + O(d^3)

for fixed tau,r>0.

If S_i omits x, its transcript law is identical under the null and alternative
x and its KL is zero.

These formulas remain exact when groups contain additional duplicate high or
low vertices: duplicate outputs do not introduce a new tape boundary.

## 3. Exact adaptive mixed-information lower program

Let A_ctrl[x,i]=1 when group i contains x and another high vertex. Let
B[x,i]=1 when group i contains x. Then B-A_ctrl identifies boundary-only
queries for alternative x.

Under the common null, let n_i=E_0[N_i] be expected adaptive query counts.
Transcript chain rule and data processing through a beta-correct final decision
give, for every x in A,

  K_control * sum_i A_ctrl[x,i] n_i
  + K_boundary * sum_i (B[x,i]-A_ctrl[x,i]) n_i
  >= kl(1-beta,beta).

Therefore every adaptive tester with finite null expected cost obeys the exact
LP lower bound

  min c^T n
  subject to
    [K_control A_ctrl + K_boundary(B-A_ctrl)] n
      >= kl(1-beta,beta) * 1,
    n >= 0.

`control_replay_information_lower_bound` solves exactly this program.

## 4. Matched-control upper construction

Define the fractional control cover

  C_ctrl = min c^T q
           subject to A_ctrl q >= 1, q>=0.

Assume C_ctrl is finite. Let

  L = ceil(log(beta)/log(1-d)),
  n_i = ceil(L q_i*).

Query group i exactly n_i times with independent tapes. Within each group
compare old-to-new patch deltas only among high-class members. Reject if those
high-class deltas are nonconstant.

Under the null all high vertices have identical old/new threshold pairs, so
their patch deltas are identical pathwise. Type-I error is exactly zero despite
the benign tau disparity between high and low classes.

Under alternative x, every control-compatible query containing x produces a
nonconstant high-class delta vector exactly when U in (h,h+d], with probability
d. The rounded schedule gives x at least L such opportunities, so its pointwise
miss probability is at most (1-d)^L <= beta.

The declared cost is at most

  L C_ctrl + sum_{i:q_i*>0} c_i.

## 5. Small-effect geometry

For fixed p,s,tau>0 with p+s+tau<1,

  K_control/d -> 1,
  K_boundary/d -> 0

as d->0.

Scale the exact lower LP by z_i = d n_i / kl(1-beta,beta). Its constraints
become

  (K_control/d) A_ctrl z
  + (K_boundary/d)(B-A_ctrl) z >= 1.

If C_ctrl is finite, finite-dimensional LP continuity (or compactness using
positive costs) gives

  lim_{d->0} d * Q_lower(d) / kl(1-beta,beta) = C_ctrl.

The upper schedule has L ~ log(1/beta)/d. Thus at fixed confidence the lower
and upper bounds have matching leading combinatorial geometry C_ctrl and
linear 1/d dependence, up to rounding and the standard kl-versus-log constant.

## 6. Absence of matched controls forces the quadratic regime

If some high candidate x has no control-compatible group, then its lower-bound
constraint contains only K_boundary. Let c_min be the minimum positive group
cost. Any tester must satisfy

  expected cost >= c_min * kl(1-beta,beta) / K_boundary(tau,d).

For fixed tau>0 this is Omega(d^-2 log(1/beta)). If x is absent from every
legal group, the alternative is unobservable and the cost is infinite.

Hence positive fairness tolerance alone does not determine the exponent:
matched-background replay controls restore the sparse linear regime; without
such controls, the same heterogeneous null contains the P18 quadratic regime.

## 7. Relationship to P17 and P18

- P17-A is recovered conceptually when all replay-eligible vertices belong to
  one homogeneous control class: every legal group containing x has a matched
  control and C_ctrl collapses to the active-vertex cover C_vert.
- P18 is recovered on a high-low group with no matched high control: the
  per-query information is K_boundary and fixed positive tau gives d^-2.
- P19 therefore supplies the extra control structure that the frozen P17
  heterogeneous counterexample showed was missing.

## 8. Prior-art fence

Common random numbers, matched comparisons, blocking, and multiple-comparison
simulation methods are not novelty claims. Fractional covering is also standard.
The submission-level claim is the exact mixed-information lower program and the
control-cover characterization induced by legal replay groups for evolving
software under a heterogeneous fairness-preserving null.

## 9. Executable correspondence

- `minimum_fractional_control_cover` computes C_ctrl;
- `control_replay_information_lower_bound` solves the exact mixed-KL LP;
- `matched_control_replay_schedule` constructs the zero-type-I upper schedule;
- `matched_control_contrast_witness` implements the within-high-class patch-delta
  predicate;
- `tests/test_control_replay.py` checks exact KL collision with P15/P18,
  linear-vs-quadratic asymptotics, cover rounding, heterogeneous-null type-I
  protection, and bipartite-scope rejection.