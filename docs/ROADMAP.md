# Research roadmap

The project is theory-first. GPU computation attacks conjectures and constants; it never substitutes for proof.

## Frozen validated spine

P1-P3 establish localization, the need for a statistical margin, and paired-delta variance.
P4-P8 establish the Gaussian graph-allocation core around Psi(H,nu).
P9-P12 establish the Bernoulli replay mechanism and the one-edge linear-vs-quadratic small-patch separation.
P13 combines unknown patch location with replay on a matching: fixed-confidence cost scales as Theta(M log(1/delta)/d).
P14 shows how sound static patch-effect envelopes prune fairness edges with zero new executions.
P15 shows that four-way replay across both versions and both counterfactual endpoints cancels a nonzero common patch effect and changes differential-gap complexity from Theta(d^-2) to Theta(d^-1).
P16 lifts synchronized replay to the full active fairness suite: round complexity is independent of edge count and concrete execution complexity is Theta(n_active log(1/delta)/d) in the audited homogeneous Bernoulli family.
P17 now has a corrected two-matrix formulation for partial synchronized replay: an edge-by-group matrix governs the proved witness-scheduling upper bound, while an active-vertex/group matrix governs the necessary raw-information floor. The LP geometries are now structurally separated by exact fixtures: equality under coherent group signatures, ratio n-1 on K_n pair groups, and finite C_vert with infeasible C_edge. These do not resolve minimax attainability.

See docs/PROOF_STATUS.md and docs/PROOF_AUDIT_P17_FRACTIONAL_REPLAY.md for exact audit status.

## Immediate theorem queue

### A. Partial synchronized replay: close the two-geometry gap
The intermediate access model is now frozen. Legal replay groups have size at least two and may have heterogeneous costs. The proved fixed-design upper construction is governed by the edge-by-group fractional cover

  C_edge = min c^T a  subject to A a >= 1, a >= 0,

while raw transcript change-of-measure reduces exactly to the active-vertex/group cover

  C_vert = min c^T q  subject to B q >= 1, q >= 0.

The corrected necessary lower floor is [kl(1-beta,beta)/K_sync] C_vert and C_vert <= C_edge. There is no universal finite-factor equivalence between the two LP geometries: deterministic structural cases include equality, an n-1 finite ratio, and finite C_vert with C_edge=+infinity. The highest-value theorem target is therefore no longer to compare the two LPs by a constant factor. It is to prove either:
1. structural conditions under which the active-vertex information floor is attainable;
2. a rigorous family separating achievable cost from C_vert; or
3. a sharper oracle-dependent parameter that interpolates between the two matrices.

Keep the current manuscript claim scoped to the proved upper construction and necessary information floor until one of these attainability questions is closed.

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
2. Materialize deterministic Gaussian, replay, counterfactual, and partial-replay benchmark manifests.
3. Run 10^4-trial single-GPU smoke tests.
4. Stress the replay exponent at shrinking d.
5. Search heterogeneous variance profiles and partial-replay group families for counterexamples to candidate graph-level formulas and C_vert/C_edge attainability conjectures.
6. Only after theorem freeze, run 10^6-10^7 publication sweeps on both GPUs.

## Paper gate

A contribution enters the abstract only when it is PROVED + AUDITED in docs/PROOF_STATUS.md. Computationally checked observations remain labeled empirical.
