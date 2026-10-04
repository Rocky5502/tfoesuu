# Proof audit — patch location × replay hierarchy

## Family

Counterfactual graph: a matching of M edges `e_i=(u_i,v_i)`.

Old version and null new version:
- every vertex has Bernoulli parameter `p`.

Alternative `i`:
- only `u_i` changes to `p+d`;
- every other vertex remains at `p`.

Common-uniform replay is used at queried vertices.

## Upper bound

Sample each candidate `u_i` for

`n = ceil(log(delta)/log(1-d))`

paired-oracle calls. Reject if any old/new discordance appears.

Under the null, a paired old/new observation is identical almost surely, so the
type-I error is exactly zero regardless of M.

Under alternative i, each paired observation at `u_i` is discordant with
probability d, so the miss probability is `(1-d)^n <= delta`.

Total paired-oracle calls: `M n`.

## Adaptive lower bound

For each alternative i, the only informative query location is `u_i`. Its
null-to-alternative per-call KL is

`K_pair = (1-p) log((1-p)/(1-p-d))`.

For a delta-correct adaptive tester with finite expected stopping time, transcript
change of measure and data processing imply

`E0[N_{u_i}] K_pair >= kl(1-delta,delta)`.

Summing over the M distinct candidate vertices gives

`E0[T] >= M kl(1-delta,delta)/K_pair`.

For fixed interior p, `K_pair=d+O(d^2)`; for delta <= 1/4,
`kl(1-delta,delta)=Theta(log(1/delta))`. Therefore the upper and lower bounds
match in order:

`Theta(M log(1/delta)/d)`.

## Interpretation

This result combines two information axes:
1. patch-location information contributes/removes an M factor;
2. paired replay contributes/removes one power of d relative to independent fresh
   Bernoulli observations.

## Collision boundary

Sequential search for an anomalous process among many stochastic processes is
established theory; see Cohen and Zhao, IEEE Transactions on Information Theory,
2015. We do not claim to invent multi-source anomaly search. The result is used as
a regression-specific corollary tying a sound software impact set to the replay
oracle.

Status: **PROVED + AUDITED** for the stated matching family.
