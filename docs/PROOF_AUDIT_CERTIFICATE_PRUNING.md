# Proof audit — sound patch envelopes and residual testing (P14)

## Deterministic carryover

For each fairness edge e=(u,v):

- old gap: g0_e = mu0_u - mu0_v;
- threshold: tau_e;
- sound patch-effect envelope:
  b_e >= |(mu1_u-mu0_u) - (mu1_v-mu0_v)|.

Then

|g1_e|
= |g0_e + theta_u - theta_v|
<= |g0_e| + |theta_u-theta_v|
<= |g0_e| + b_e.

Therefore |g0_e| + b_e <= tau_e is a sufficient zero-query certificate that the
edge remains fair.

## Residual graph

H* contains only edges not discharged by the inequality above.  Safe edges need
no new execution.  If H* is empty, zero paired-oracle calls suffice.

## Gaussian separated test on H*

For every residual edge, estimate theta_u-theta_v using the same allocation as P4:

n_v = ceil(8 log(2m*/delta) q_v / gamma^2).

The Psi constraints imply every residual edge-difference estimate has Gaussian
variance at most gamma^2/[8 log(2m*/delta)].

Use the decision threshold

|g0_e + hat(theta_u-theta_v)| >= tau_e + gamma/2.

On the simultaneous good estimation event:
- if the new edge is fair, true magnitude <= tau_e, so estimated magnitude is
  <= tau_e + gamma/2;
- if it is an alternative with true magnitude >= tau_e+gamma, estimated magnitude
  is >= tau_e + gamma/2.

The same Gaussian tail plus union-bound calculation as P4 controls the failure
event by delta.

## Relationship to P11

P11 says old certificate slack alone cannot improve unrestricted minimax
complexity. P14 does not contradict it: P14 adds new structural information, a
sound deterministic envelope constraining the patch. The computational gain is
created by the combination of headroom and that envelope.

## Implementation audit

- src/tfoesuu/certificate.py implements the deterministic pruning rule.
- src/tfoesuu/testers.py runs the Gaussian allocation only on the residual graph.
- tests/test_certificate.py covers safe/boundary/invalid cases.
- tests/test_full_regression.py checks zero-query pruning, residual detection, and
  sampled-vertex reduction.

Status: **PROVED + AUDITED** under the stated exact-old-gap and sound-envelope
assumptions.
