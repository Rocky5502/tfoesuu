# Proof audit: thresholded fairness replay phase transition

**Status: PROVED + AUDITED AS A SCOPED ONE-EDGE RESULT.**

The statistical ingredients are standard Bernoulli testing and transcript KL.
The useful paper-level consequence is the interpolation between the sparse-witness
replay regime and a nonzero fairness-tolerance boundary.

## 1. Frozen family

Consider one fairness edge (u,v) and one common-uniform replay tape U~Unif[0,1].
Old thresholds are (p,p). Let s>=0 be a common patch effect, tau>=0 the allowed
new-version fairness gap, and d>0 the separated alternative margin.

Boundary null H0:

  new thresholds = (p+s+tau, p+s).

Boundary alternative H1:

  new thresholds = (p+s+tau+d, p+s).

Assume p>0 and p+s+tau+d<1.

This pair is contained in the composite testing problem

  H0: new-version gap <= tau
  H1: new-version gap >= tau+d.

## 2. Exact one-round transcript KL

Let r=1-p-s-tau. Under H0 the only transcript atoms whose probabilities change
under H1 have masses

  tau  and  r.

Under H1 these become

  tau+d  and  r-d.

All other transcript atoms have the same probabilities under the two hypotheses.
Therefore

  K_tau(d)
    = tau log(tau/(tau+d))
      + r log(r/(r-d)),

where the first term is interpreted as zero at tau=0.

At tau=0 this reduces exactly to the P15 four-way common-patch KL

  r log(r/(r-d)),

which is d+O(d^2).

For fixed tau>0 and fixed r>0, Taylor expansion gives

  K_tau(d)
    = (d^2/2)(1/tau + 1/r) + O(d^3).

Thus the per-round information changes from first order in d at tau=0 to
second order in d at any fixed positive interior tolerance.

## 3. Adaptive lower bound

Let an adaptive beta-correct tester have finite expected stopping time under the
boundary null. Standard transcript change of measure and data processing through
the final decision give

  E_0[T] K_tau(d) >= kl(1-beta,beta).

Hence

  E_0[T] >= kl(1-beta,beta) / K_tau(d).

For a uniform order statement, assume the alternative remains at least rho>0
away from the upper threshold boundary:

  r-d >= rho.

Because KL is upper-bounded by chi-square divergence for this categorical pair,

  K_tau(d)
  <= d^2/(tau+d) + d^2/(r-d)
  <= (1+1/rho) d^2/(tau+d),

using tau+d<=1 in the last step. Therefore

  E_0[T]
  >= [1/(1+1/rho)]
     [(tau+d)/d^2] kl(1-beta,beta).

For beta bounded below 1/2, kl(1-beta,beta)=Theta(log(1/beta)) in the usual
fixed-confidence regime.

## 4. Matching fixed-design upper order

In one synchronized edge replay define

  W = 1{P1(u;U) != P1(v;U)}.

For threshold Bernoulli outputs under a common uniform tape, W is Bernoulli with
mean equal to the absolute new-version threshold gap.

Use n independent replay rounds and reject when

  mean(W) >= tau + d/2.

The worst null is the boundary mean tau, and the worst alternative is the
boundary mean tau+d by stochastic ordering of binomial tails.

For the null upper tail, Bernstein gives

  Pr_0(reject)
  <= exp(- n d^2 / [8(tau+d/6)])
  <= exp(- n d^2 / [8(tau+d)]).

For the alternative lower tail, the standard lower-tail Chernoff bound gives

  Pr_1(accept)
  <= exp(- n d^2 / [8(tau+d)]).

Thus

  n = ceil(8 (tau+d) log(1/beta) / d^2)

suffices for both errors to be at most beta.

Combined with the lower bound, the minimax replay-round complexity in this
scoped one-edge family is

  Theta((tau+d) d^{-2} log(1/beta))

up to constants depending on the interior margin rho.

## 5. Phase interpretation

- tau=0: Theta(d^{-1} log(1/beta));
- tau=Theta(d): Theta(d^{-1} log(1/beta));
- fixed tau>0: Theta(d^{-2} log(1/beta)).

This explains why a zero-background-contrast replay witness can be linearly
sensitive in d, while a fixed nonzero fairness tolerance restores ordinary
quadratic local testing behavior.

## 6. Relation to P17 scope failure

The P17 heterogeneous counterexample is not merely an implementation accident.
Once benign null behavior can create a nonzero within-group contrast, the sparse
zero-type-I witness structure disappears. The exact theorem above is one-edge
and does not solve general partial-group composite-null geometry, but it rules out
a universal claim that synchronized replay should retain d^{-1} dependence at
fixed positive background disparity.

## 7. Prior-art fence

Testing paired Bernoulli proportions, common-random-number comparisons, and
Bernoulli concentration are classical. No novelty is claimed for those tools.
The paper-level claim is their consequence for the version-aware replay access
model and the resulting transition between zero-background and thresholded
fairness-regression regimes.

## 8. Executable correspondence

- `threshold_fairness_replay_kl` implements the exact one-round KL;
- `threshold_fairness_replay_bounds` implements the fixed-confidence upper and
  transcript-KL lower schedules;
- `tests/test_threshold_replay_phase.py` checks the tau=0 reduction to P15,
  linear-vs-quadratic asymptotics, schedule interpolation, and parameter guards.

## 9. Independent conditional-Bernoulli cross-check

There is a second derivation of the one-round information that does not enumerate
the four-output transcript atom by atom. Let

  a = 1-p-s.

The event U>p+s has probability a under both hypotheses. Conditional on this
event, the only relevant distinction is whether U falls in the differential
interval. Under the boundary null its conditional probability is

  x = tau/a,

and under the alternative it is

  x + epsilon = (tau+d)/a,

where epsilon=d/a. Because the conditioning event itself has identical
probability under H0 and H1, the full one-round KL is

  a * kl(x, x+epsilon).

Expanding this Bernoulli KL gives exactly

  tau log(tau/(tau+d))
  + (a-tau) log((a-tau)/(a-tau-d)),

which matches K_tau(d) with r=a-tau. This independently confirms both the exact
KL formula and its linear/quadratic transition. It also makes the statistical
boundary clear: the theorem is a thresholded paired-Bernoulli problem embedded
inside the version-aware replay transcript.
