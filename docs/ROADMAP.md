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
P17 has a corrected two-matrix formulation for partial synchronized replay. The LP geometries are structurally separated by exact fixtures, and an audited raw-output contrast construction attains the active-vertex C_vert geometry in the frozen homogeneous single-changed-endpoint family. Broader heterogeneous/composite-null partial replay remains open.

See docs/PROOF_STATUS.md and docs/PROOF_AUDIT_P17_FRACTIONAL_REPLAY.md for exact audit status.

## Immediate theorem queue

### A. Partial synchronized replay: extend beyond the homogeneous theorem
The intermediate access model is now frozen. Legal replay groups have size at least two and may have heterogeneous costs. The proved fixed-design upper construction is governed by the edge-by-group fractional cover

  C_edge = min c^T a  subject to A a >= 1, a >= 0,

while raw transcript change-of-measure reduces exactly to the active-vertex/group cover

  C_vert = min c^T q  subject to B q >= 1, q >= 0.

The corrected lower floor is [kl(1-beta,beta)/K_sync] C_vert. The audited active-vertex raw-contrast theorem uses q* from the same LP, L=ceil(log(beta)/log(1-d)), and n_i=ceil(L q_i*) to obtain zero type-I error and pointwise type-II error at most beta in the frozen homogeneous family, at cost at most L C_vert plus rounding support cost.

A deterministic heterogeneous-null counterexample now closes off the naive
generalization route: for tau=0.20, old thresholds (0.20,0.40), new thresholds
(0.30,0.45), and U=0.25, the new program remains fair (gap 0.15) while the raw
patch-delta contrast fires. The next theorem target is therefore not "reuse the
same contrast under heterogeneity." It is to identify extra replay/control
structure, a baseline-adjusted statistic, or a sharper decision geometry that
restores uniform validity under the composite null.

A candidate sufficient-condition extension is now under audit: **group-coherent
composite nulls**, where every legal replay group has a pathwise-constant null
patch-delta vector, while different disconnected replay components may have
different patch effects.  If every alternative indexed by active endpoint x
creates a within-group contrast with probability at least d in every legal
group containing x, the same C_vert rounding argument gives zero type-I error
and type-II error at most beta.  The candidate has proof, adversarial code, and
deterministic specification data, but it must remain outside the manuscript
theorem set until CI and the real paper build pass.

Arbitrary heterogeneous/composite nulls that violate group coherence remain
open; the frozen scope counterexample proves that Algorithm C cannot simply be
used there.

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
5. Search heterogeneous variance profiles and partial-replay group families for counterexamples to broader composite-null graph formulas and candidate extensions beyond the audited homogeneous C_vert theorem.
6. Only after theorem freeze, run 10^6-10^7 publication sweeps on both GPUs.

## Paper gate

A contribution enters the abstract only when it is PROVED + AUDITED in docs/PROOF_STATUS.md. Computationally checked observations remain labeled empirical.
