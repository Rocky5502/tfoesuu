# Proof audit — four-way counterfactual replay (P15)

## Family

One counterfactual edge (u,v).

Old version:
- p0_u = p0_v = p.

Null:
- p1_u = p1_v = p+s.

Alternative:
- p1_u = p+s+d;
- p1_v = p+s.

Assume p>0, s>0, d>0, p+s+d<1.

The common patch effect s is fairness-neutral. The differential d is exactly the
new fairness gap.

## Four-way replay upper bound

Use one U~Uniform[0,1] for all four evaluations:
P0(u;U), P1(u;U), P0(v;U), P1(v;U).

Define

W = [P1(u)-P0(u)] - [P1(v)-P0(v)].

Under H0, W=0 pathwise.
Under H1, W=1 exactly for U in (p+s,p+s+d], probability d.

Reject on first W=1.

- type-I error: exactly zero;
- type-II error after n rounds: (1-d)^n.

Thus
n = ceil(log(delta)/log(1-d))
suffices.

## Four-way replay lower bound

Let r=1-p-s.

Under H0 the only states with positive mass have probabilities p, s, r.
Under H1, the p and s states retain their masses; d mass is split from the
all-zero r state into a new differential-witness state.

Therefore

K_edge = KL(H0 || H1)
       = r log(r/(r-d))
       = d + O(d^2).

Transcript change of measure gives

E0[T] K_edge >= kl(1-delta,delta).

Hence fixed-confidence complexity is Theta(log(1/delta)/d).

## Vertex-paired replay

A call at u shares randomness only between old and new versions at u.

H0 pair distribution on (1,1),(0,1),(0,0):
(p, s, r).

H1:
(p, s+d, r-d).

Thus

K_vertex
= s log(s/(s+d)) + r log(r/(r-d))
= d^2/2 * (1/s + 1/r) + O(d^3).

The first-order terms cancel.

Lower bound:
E0[T] >= kl(1-delta,delta)/K_vertex.

Upper bound:
retain only the old/new discordance indicator, which is Bernoulli(s) under H0
and Bernoulli(s+d) under H1. Threshold at s+d/2; Hoeffding yields
ceil(2 log(1/delta)/d^2) calls.

Hence vertex-paired replay is Theta(log(1/delta)/d^2) for fixed interior s,r.

## Execution units

- one vertex-paired call = two concrete executions;
- one four-way edge-coupled call = four concrete executions.

The constant conversion does not affect the d exponent.

## Novelty boundary

Common random numbers for stochastic-system comparison are classical (Glasserman
and Yao, Management Science 1992). Probabilistic couplings for relational program
reasoning are also established (Barthe et al., POPL 2017).

P15 does not claim either technique. The theorem claim is the query-complexity
separation induced by a four-way replay access mechanism for fairness regression:
fairness-neutral common patch effects cancel pathwise, while a differential
fairness regression remains a sparse witness.

A broader literature collision audit remains part of the submission gate.

Status: **PROVED + AUDITED** for the stated Bernoulli threshold-program family.
