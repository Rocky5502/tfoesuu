# Research roadmap

The project is theory-first. GPU computation attacks conjectures and constants; it never substitutes for proof.

## Frozen validated spine

P1-P3 establish localization, the need for a statistical margin, and paired-delta variance.
P4-P8 establish the Gaussian graph-allocation core around Psi(H,nu).
P9-P12 establish the Bernoulli replay mechanism and the one-edge linear-vs-quadratic small-patch separation.
P13 combines unknown patch location with replay on a matching: fixed-confidence cost scales as Theta(M log(1/delta)/d).
P14 shows how sound static patch-effect envelopes prune fairness edges with zero new executions.
P15 shows that four-way replay across both versions and both counterfactual endpoints cancels a nonzero common patch effect and changes differential-gap complexity from Theta(d^-2) to Theta(d^-1).

See docs/PROOF_STATUS.md for exact audit status.

## Immediate theorem queue

### A. Graph-level four-way counterfactual replay
Lift P15 from one fairness edge to general counterfactual graphs. The current `graph_replay.py` fractional-cover construction is a conjecture-hunting harness only. The next theorem must derive the correct graph quantity from the exact replay access model and prove matching upper/lower bounds before any formula is promoted.

### B. Retained certificate headroom
Old-version slack cannot improve unrestricted minimax complexity by itself (P11). Seek an instance-dependent theorem where patch restrictions and certified headroom interact nontrivially.

### C. Unknown variance and sequential validity
Replace known Gaussian delta variances with confidence sequences or another anytime-valid construction. Every stopping rule must be audited for optional-stopping validity.

### D. Imperfect impact analysis
Separate two models: sound-but-imprecise impact sets, and explicitly probabilistic unsoundness with sentinel checks. Never blur them.

### E. Multi-version amortization
Study P0 -> P1 -> ... -> PT with reusable certificates. Target a dynamic complexity depending on cumulative changed structure rather than T times a fresh audit.

## Experiment queue

1. Run all CPU CI and theorem checks.
2. Materialize deterministic Gaussian and replay benchmark manifests.
3. Run 10^4-trial single-GPU smoke tests.
4. Stress the replay exponent at shrinking d.
5. Search heterogeneous variance profiles and graph families for counterexamples to candidate graph-level formulas.
6. Only after theorem freeze, run 10^6-10^7 publication sweeps on both GPUs.

## Paper gate

A contribution enters the abstract only when it is PROVED + AUDITED in docs/PROOF_STATUS.md. Computationally checked observations remain labeled empirical.
