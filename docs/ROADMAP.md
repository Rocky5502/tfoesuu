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
P17 has a corrected two-matrix formulation for partial synchronized replay. The LP geometries are structurally separated by exact fixtures, and a new gated raw-output contrast construction attains the active-vertex C_vert geometry in the frozen homogeneous single-changed-endpoint family. Broader heterogeneous/composite-null partial replay remains open.

See docs/PROOF_STATUS.md and docs/PROOF_AUDIT_P17_FRACTIONAL_REPLAY.md for exact audit status.

## Immediate theorem queue

### A. Partial synchronized replay: close the two-geometry gap
The intermediate access model is now frozen. Legal replay groups have size at least two and may have heterogeneous costs. The proved fixed-design upper construction is governed by the edge-by-group fractional cover

  C_edge = min c^T a  subject to A a >= 1, a >= 0,

while raw transcript change-of-measure reduces exactly to the active-vertex/group cover

  C_vert = min c^T q  subject to B q >= 1, q >= 0.

The corrected lower floor is [kl(1-beta,beta)/K_sync] C_vert. The active-vertex raw-contrast candidate uses q* from the same LP, L=ceil(log(beta)/log(1-d)), and n_i=ceil(L q_i*) to obtain zero type-I error and pointwise type-II error at most beta in the frozen homogeneous family, at cost at most L C_vert plus rounding support cost. After final promotion, the next theorem target is the genuinely broader problem: heterogeneous/composite fairness-preserving nulls, where within-group patch-delta disagreement need not imply unfairness.

Keep the raw-contrast claim explicitly scoped to the homogeneous single-changed-endpoint family until a broader composite-null theorem is proved.

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
