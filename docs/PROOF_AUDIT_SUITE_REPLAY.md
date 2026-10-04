# Proof audit — synchronized suite replay (P16)

## Access model

One suite-replay round:
1. draw one U~Uniform[0,1];
2. execute P0(v;U) and P1(v;U) for every fairness-active vertex v;
3. observe all old/new deltas and therefore every edge differential.

Cost:
- one suite round as the oracle unit;
- 2*n_active concrete software executions per round.

This is stronger than vertex-local or edge-local replay and is only appropriate
when the test harness can replay the same seed across the affected input suite.

## Hard family

Every active vertex:
- old threshold p.

Null:
- every active vertex new threshold p+s.

Alternative:
- one endpoint of one fairness edge has new threshold p+s+d;
- every other active vertex remains p+s.

Assume p>0, s>0, d>0, p+s+d<1.

## Upper bound

Under the null, every old/new delta is identical pathwise, so no edge ever
witnesses a difference.

Under any alternative, for U in (p+s,p+s+d], probability d:
- the differential endpoint has old/new delta 1;
- all ordinary endpoints have delta 0;
- every incident fairness edge exposes the regression.

Reject on first differential edge.

Miss probability after T rounds: (1-d)^T.

Thus ceil(log(delta)/log(1-d)) rounds suffice, independently of |E|.

## Lower bound

Fix any one legal alternative. Let r=1-p-s.

Under H0, one suite state has mass r.
Under the fixed alternative, d mass is split from that state into a new
differential-endpoint state.

Per-round null-to-alternative KL:

K = r log(r/(r-d)) = d + O(d^2).

For any adaptive delta-correct finite-mean stopping rule:

E0[T] K >= kl(1-delta,delta).

Hence round complexity is Theta(log(1/delta)/d).

Because each round executes both versions at every active vertex, concrete
execution complexity is Theta(n_active log(1/delta)/d).

## Edge-count consequence

The theorem cost is independent of m=|E|. Compared with naively running a
four-execution P15 replay separately on each edge for the same number of rounds:

- edgewise concrete cost = 4mT;
- suite concrete cost = 2 n_active T;
- ratio = 2m/n_active.

For K_n this ratio is n-1.

This comparison is an algorithmic consequence, not a lower bound against every
possible weaker-access algorithm.

## Prior-art boundary

Common random numbers and simultaneous multiple comparisons are classical.
P16 does not claim the CRN mechanism. The theorem concerns the query/execution
complexity of fairness-regression certification under a synchronized software
test-suite replay primitive.

Status: **PROVED + AUDITED** under the homogeneous Bernoulli threshold family and
the explicit suite-replay access model.
