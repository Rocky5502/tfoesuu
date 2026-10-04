# P17 fractional replay-cover proof audit

**Status: FIRST DERIVATION COMPLETE. Independent second audit and literature
collision check remain mandatory before promotion.**

## Frozen model

Let H=(V,E) be a fairness graph and let G={S_1,...,S_k} be legal replay groups.
A query to S_i draws a fresh tape U and executes both software versions on every
v in S_i with that same tape. Different group queries use independent tapes.

An edge e=(u,v) is informative in a group query iff {u,v} is a subset of S_i.
In the homogeneous Bernoulli family, an informative query has zero pathwise
differential under H0 and reveals the single-edge alternative with probability d.
Its null-to-alternative KL is

  K(d)=r log(r/(r-d)),  r=1-p-s.

Let c_i>0 be the declared cost of querying group S_i.

Define the fractional replay cover

  C* = min sum_i c_i a_i
       s.t. sum_{i: e subset S_i} a_i >= 1 for every e,
            a_i >= 0.

## Lower bound

For any adaptive beta-correct tester with finite null expected cost, fix an edge
alternative e. Transcript KL and data processing imply

  K(d) sum_{i: e subset S_i} E_0[N_i]
      >= kl(1-beta,beta).

Set

  a_i = E_0[N_i] K(d) / kl(1-beta,beta).

Then a is feasible for the fractional cover LP. Therefore

  E_0[cost]
  = sum_i c_i E_0[N_i]
  >= C* kl(1-beta,beta)/K(d).

This argument does not require a union bound and permits adaptive group choice.

## Upper bound

Let a* be an optimal fractional cover and define

  L = ceil(log(beta)/log(1-d)),
  n_i = ceil(L a_i*).

Run group i exactly n_i times, independently across queries, and reject on any
within-group fairness witness.

For every edge alternative e,

  sum_{i: e subset S_i} n_i
  >= L sum_{i: e subset S_i} a_i*
  >= L.

Each informative query misses independently with probability 1-d, hence the
probability of missing alternative e is at most

  (1-d)^L <= beta.

Under H0 a witness is pathwise impossible, so type-I error is zero.

The concrete declared cost satisfies

  sum_i c_i n_i
  <= L C* + sum_{i: a_i*>0} c_i.

Thus the finite upper/lower sandwich is

  C* kl(1-beta,beta)/K(d)
  <= Q*
  <= L C* + R(a*),

where R(a*) is the explicit support-weighted rounding overhead.

For fixed beta and fixed interior p,s,r, as d->0,

  K(d)=d+O(d^2),
  L=Theta(log(1/beta)/d),

so, when the replay instance is fixed,

  Q* = Theta(C* log(1/beta)/d)

up to beta-dependent constant conventions and vanishing relative rounding cost.

## Adversarial checks still required

- infeasible edge not contained in any legal group;
- one legal full-suite group recovers P16;
- edge-only groups recover edgewise P15 scheduling;
- overlapping groups with a strict fractional/integral gap;
- heterogeneous positive costs;
- duplicate/dominated groups;
- support-size and rounding-overhead control;
- beta and d boundary validation;
- explicit test that endpoint-only groups cannot observe an edge.

## Novelty fence

Set cover/fractional cover, common random numbers, couplings, and subset queries
are established concepts. Any claim must be limited to the proved complexity
characterization induced by this software-version/fairness-regression replay
oracle.
