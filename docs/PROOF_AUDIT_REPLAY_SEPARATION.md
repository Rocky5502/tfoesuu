# Proof audit — Bernoulli replay separation

## Statement family

Use one counterfactual edge `(u,v)` with fairness threshold zero.

Old version:

- `p0(u)=p0(v)=p`.

Null:

- `p1(u)=p1(v)=p`.

Alternative:

- `p1(u)=p+d`,
- `p1(v)=p`,

with `p in (0,1)` and `d in (0,1-p)`.

The old version is fair in both worlds.  The alternative introduces a fairness
regression of magnitude exactly `d`.

## Paired common-uniform replay

At `u`, use the same `U~Unif[0,1]` for both versions.

Under the null the observed pair is:

- `(1,1)` with probability `p`;
- `(0,0)` with probability `1-p`.

Under the alternative:

- `(1,1)` with probability `p`;
- `(0,0)` with probability `1-p-d`;
- `(0,1)` with probability `d`.

### Upper bound

Reject on the first discordant `(0,1)` pair.

- Type-I error is exactly zero.
- Alternative miss probability after `n` paired rounds is `(1-d)^n`.

Thus
`n = ceil(log(beta)/log(1-d))`
is sufficient, which is
`Theta(d^{-1} log(1/beta))`
for small `d`.

### Adaptive lower bound

The null-to-alternative KL of one informative paired query is

`K_pair = (1-p) log((1-p)/(1-p-d))`.

Queries to `v` have zero KL.  For any adaptive beta-correct test with finite
expected stopping time, transcript change of measure and data processing through
the terminal decision give

`E0[N_u] K_pair >= kl(1-beta,beta)`.

Therefore

`E0[T] >= kl(1-beta,beta) / K_pair`.

As `d -> 0`,

`K_pair = d + O(d^2)`,

so the lower bound is
`Omega(d^{-1} log(1/beta))`
for fixed interior `p`.

## Independent/fresh replay

If old and new randomness are independent, the old observation has the same law
under both hypotheses and contributes zero information.  The new observation at
`u` is Bernoulli(p) under the null and Bernoulli(p+d) under the alternative.

### Upper bound

If the old baseline `p` is retained exactly, sample the new version at `u`
and reject when the empirical mean is at least `p+d/2`.

Hoeffding gives each one-sided error at most

`exp(-n d^2/2)`.

Hence
`ceil(2 log(1/beta)/d^2)`
samples suffice.

Giving the independent tester the exact old baseline only strengthens it, so the
comparison is conservative in favor of fresh auditing.

### Adaptive lower bound

One informative independent query has null-to-alternative KL

`K_ind = kl(Bern(p), Bern(p+d))`.

Therefore

`E0[T] >= kl(1-beta,beta)/K_ind`.

For fixed `p in (0,1)`,

`K_ind = d^2/[2p(1-p)] + O(d^3)`.

Thus independent replay has
`Theta(d^{-2} log(1/beta))`
small-patch complexity.

## Novelty boundary

This proof does **not** claim that paired Bernoulli inference, matched-pair tests,
or common random numbers are new.  Classical matched-pairs statistics and CRN
already study efficiency gains from pairing.

The paper-level claim is the use of replayable old/new software versions as an
information-access primitive for **fairness regression testing**, together with
the resulting linear-vs-quadratic small-patch separation and its later extension
to graph-structured fairness constraints.

## Audit status

- algebra independently re-derived twice;
- exact finite-sample paired upper bound checked;
- KL asymptotics checked numerically;
- classical matched-pair and common-random-number literature collision checked;
- implementation tests added.

Status: **PROVED + AUDITED** for the stated one-edge family.
