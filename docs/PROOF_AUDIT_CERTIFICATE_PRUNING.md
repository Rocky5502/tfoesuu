# Proof audit — sound patch envelopes and promise-aware residual testing (P14)

## Status

**P14 deterministic certificate carryover: PROVED + AUDITED.**

**P14 separated-promise alternative pruning: DERIVED + IMPLEMENTED + TESTED;
final promotion pending synchronized manuscript and real LaTeX gates.**

The two statements below have different semantics and must not be conflated.

## 1. Frozen quantities

For every fairness edge e=(u,v), let

- old gap: g0_e = mu0_u - mu0_v;
- fairness threshold: tau_e >= 0;
- sound patch-effect envelope:
  b_e >= |(mu1_u-mu0_u) - (mu1_v-mu0_v)|;
- separation margin gamma > 0 for the testing promise.

Write

  M_e = |g0_e| + b_e.

By the triangle inequality,

  |g1_e|
    = |g0_e + theta_u - theta_v|
    <= |g0_e| + |theta_u-theta_v|
    <= M_e.

This single deterministic upper bound supports two different pruning rules.

## 2. Strong zero-query fairness certificate

If

  M_e <= tau_e,

then |g1_e| <= tau_e for every patch consistent with the envelope. The edge is
therefore deterministically certified fair and requires no stochastic execution.
This statement does not rely on a separated testing promise.

The original prune_with_patch_envelopes API implements exactly this rule.

## 3. Promise-aware alternative pruning

The full regression tester uses the separated promise

  H0: |g1_e| <= tau_e for every edge,

versus

  H1: |g1_e| >= tau_e + gamma for at least one edge.

Define the alternative-capable edge set

  E_gamma = {e : M_e >= tau_e + gamma},

and let H_gamma=(V,E_gamma).

If an edge e satisfies

  M_e < tau_e + gamma,

then soundness of the envelope implies

  |g1_e| <= M_e < tau_e + gamma,

so e cannot be the H1 witness. Consequently every H1 instance has at least one
violating edge in E_gamma.

The boundary is intentionally non-strict in E_gamma. If
M_e = tau_e + gamma, the envelope still permits an alternative exactly on the
separated boundary, so the edge must remain testable.

## 4. Three semantic categories

The implementation keeps three disjoint categories:

1. **certified safe**
   M_e <= tau_e.
   These edges are proved fair from side information alone.

2. **promise-gap only**
   tau_e < M_e < tau_e + gamma.
   These edges are not deterministically certified fair. They are omitted only
   because they cannot realize the promised H1 boundary. An actual outcome in
   (tau_e, tau_e+gamma) would lie outside the testing promise.

3. **alternative-capable**
   M_e >= tau_e + gamma.
   These are the only edges on which stochastic search is necessary.

Calling category 2 "safe" would be mathematically wrong; the API and result
object therefore expose it separately.

## 5. Sharpened Gaussian separated-test upper bound

Let m_gamma=|E_gamma|. If m_gamma=0, the H1 class is empty under the supplied
sound envelopes. A zero-query test that accepts is therefore correct on all
promised instances.

If m_gamma>0, run the P4 Gaussian allocation only on H_gamma:

  n_v
    = ceil(
        8 log(2 m_gamma / delta) q_v / gamma^2
      ),

where q is an optimal solution for Psi(H_gamma,nu). Estimate
theta_u-theta_v on every edge in E_gamma, add the known old gap g0_e, and reject
at the same separated midpoint threshold used by the existing full-regression
tester.

On H0, simultaneous Gaussian concentration over E_gamma controls false
rejection by delta. On H1, Section 3 guarantees that at least one H1 witness
belongs to E_gamma, and the same estimation event detects it. Therefore the
declared paired-oracle cost is at most

  [8 log(2 m_gamma/delta)/gamma^2] Psi(H_gamma,nu)
  + |V(H_gamma)|,

up to the existing integer-rounding convention. If m_gamma=0 the cost is zero.

## 6. Strict improvement over the fairness-certificate residual

The original residual graph

  H_star = {e : M_e > tau_e}

contains every edge that is not deterministically certified fair. Promise-aware
testing uses only

  H_gamma = {e : M_e >= tau_e + gamma}.

Hence E_gamma is always a subset of E(H_star), and the inclusion can be strict.
For example, with g0=0, tau=0.10, b=0.15, gamma=0.10,

  tau < M=0.15 < tau+gamma=0.20.

The edge is not certified fair, so it belongs to H_star, but it cannot satisfy
H1 and is absent from H_gamma. The new bound can therefore reduce both the
number of union-bound comparisons and the graph-allocation quantity Psi.

This is a sharper **upper bound** under the separated promise. No matching
instance-dependent lower characterization is claimed.

## 7. Relationship to P11

P11 says old certificate slack alone cannot improve unrestricted minimax
complexity. P14 does not contradict it. The improvement here uses additional
sound structural information b_e that constrains the patch. The separation
margin gamma is then used to identify which envelope-consistent edges can
actually realize H1.

## 8. Implementation correspondence

- prune_with_patch_envelopes implements the unconditional fairness certificate.
- prune_for_separated_regression implements the three-way promise-aware
  partition.
- run_gaussian_full_regression_test allocates samples only on the
  alternative-capable graph while returning certified-safe and promise-gap edges
  separately.
- tests/test_certificate.py checks the three categories, strict boundary, and
  invalid gamma.
- tests/test_full_regression.py checks zero-sampling of promise-gap edges and
  retention of the exact alternative boundary.

## 9. Promotion gates

Before the sharpened P14 statement is promoted to **PROVED + AUDITED**:

1. full CI is green on the synchronized theorem branch;
2. the manuscript distinguishes certified-fair and promise-gap-only edges;
3. the theorem/algorithm matrix and proof ledger use H_gamma consistently;
4. the real LaTeX build is green;
5. no text claims that promise-gap edges are fair outside the separated promise.
