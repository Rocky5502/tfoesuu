# Proof status ledger

This file is the source of truth for mathematical claims. A result is not promoted to the abstract or contribution list unless its status is **PROVED + AUDITED**.

| ID | Statement | Status | Notes |
|---|---|---|---|
| P1 | Sound change-impact localization of newly introduced fairness violations | PROVED + AUDITED | Elementary reuse argument. |
| P2 | No uniform finite-query sharp-threshold certification under stochastic execution | PROVED + AUDITED | Two-point KL/TV argument. |
| P3 | Differential variance identity under paired old/new replay | PROVED + AUDITED | Variance expansion. |
| P4 | Gaussian static-allocation upper bound using `Psi(H,nu)` | PROVED + AUDITED | Union bound + Gaussian tails. |
| P5 | Adaptive Gaussian lower bound using the same `Psi(H,nu)` | PROVED + AUDITED | Adaptive transcript KL + edgewise alternatives. |
| P6 | Lagrange dual representation of `Psi` | PROVED + AUDITED | Slater condition + separable minimization over q. |
| P6-C | Exact rotated-SOC representation of `Psi` | PROVED + AUDITED (SUPPORTING) | Standard hyperbolic-to-rotated-cone reformulation; executable certificate test; not a novelty claim. |
| P7 | Unit-variance exact values: edge, matching, clique, star, complete bipartite | PROVED + AUDITED | Symmetry/convexity; star is `K_{1,k}`. |
| P8 | Homogeneous variance scaling: `Psi(H,lambda nu^2)=lambda Psi(H,nu^2)` | PROVED + AUDITED | Direct rescaling. |
| P9 | Common-uniform Bernoulli delta variance `d(1-d)` | PROVED + AUDITED | Delta is signed Bernoulli on interval between probabilities. |
| P10 | Linear patch-locality separation on an M-edge matching | PROVED + AUDITED | Re-derived from P4/P5; matched execution oracle; exact matching `Psi`. |
| P11 | Old certificate slack alone gives no minimax speedup under unrestricted patches | PROVED + AUDITED | Independent boundary-null reduction; lower bound is slack-independent. |
| P12 | Common-uniform Bernoulli replay gives linear-vs-quadratic small-patch query complexity | PROVED + AUDITED | One-edge fairness regression; paired KL is Theta(d), independent KL is Theta(d^2). |
| P13 | Unknown-location Bernoulli replay on an M-edge matching has Theta(M/d) fixed-confidence scaling | PROVED + AUDITED | Edgewise transcript KL sums under the common null; active anomaly-search collision boundary documented. |
| P14 | Sound patch-effect envelopes prune certified-safe edges; Gaussian testing runs only on the residual graph | PROVED + AUDITED | Triangle-inequality carryover plus P4 allocation on residual graph. |
| P15 | Four-way counterfactual replay cancels a nonzero common patch effect and changes differential-gap complexity from Theta(d^-2) to Theta(d^-1) | PROVED + AUDITED | Four-output KL versus vertex-paired KL; CRN/coupling prior art explicitly fenced. |
| P16 | Synchronized suite replay tests all fairness edges at once; rounds are Theta(log(1/delta)/d) and concrete executions Theta(n_active log(1/delta)/d), independent of edge count | PROVED + AUDITED | Fixed-alternative KL lower bound + pathwise common-patch cancellation; stronger suite-replay access model stated explicitly. |
| P17 | Partial synchronized replay: witness scheduling, raw-information floor, structural geometry, and homogeneous raw-contrast attainability | PROVED + AUDITED FOR THE FROZEN HOMOGENEOUS SINGLE-CHANGED-ENDPOINT FAMILY; HETEROGENEOUS/COMPOSITE-NULL EXTENSION OPEN | The edge-witness upper uses C_edge, but raw-output transcript information and the audited raw-contrast schedule are both governed by C_vert in the frozen homogeneous family. Thus [kl(1-beta,beta)/K_sync] C_vert <= Q*_hom <= L C_vert + rounding support cost. Structural fixtures also show C_edge/C_vert can be n-1 or infinite. A frozen heterogeneous fair-null counterexample shows the homogeneous raw-contrast predicate can false-positive outside its scope. Do not extend the C_vert attainability theorem to heterogeneous/composite fairness-preserving nulls. |
| P18 | Thresholded one-edge synchronized replay has complexity Theta((tau+d)d^-2 log(1/delta)); tau=0 gives d^-1 while fixed tau>0 gives d^-2 | PROVED + AUDITED | Exact four-way transcript KL + matching Bernstein/Chernoff upper order; interior-margin constant for lower bound; paired-Bernoulli/common-random-number tools are prior art and explicitly fenced. |
| P19 | Matched-background controls restore linear partial-replay complexity under a two-class heterogeneous fair null; mixed topologies combine quadratic boundary and linear control blocks | PROVED + AUDITED FOR THE BIPARTITE TWO-CLASS THRESHOLD FAMILY | Exact mixed transcript-KL LP + fractional control-cover construction + P18/P19 hybrid upper. Nonadaptive fixed boundary allocations require Omega(|U| log |U|/d^2); adaptive LR allocation attains Theta(|U|/d^2) topology scaling at fixed confidence, both in expected null cost and after deterministic Markov truncation. Its untruncated leading null constant is within log(1/beta)/kl(1-beta,beta) of the information floor (1.1305 at beta=.05). Exact adaptive constants and optimal beta dependence remain open. |
| P20 | General nuisance-aware replay information geometry beyond P19: legal replay actions induce an action-by-alternative information matrix whose minimum-cost information cover is conjectured to characterize graph-level certification cost | CONJECTURE; FINITE-NUISANCE QUANTIFIER AUDIT + LP FIXTURES ONLY | P18/P19 remain audited scoped results. For each fixed null nuisance eta, stopped-transcript KL gives a necessary pointwise allocation floor. The maximum of these floors can be strictly smaller than a single shared fixed-information allocation; do not substitute the latter as an adaptive minimax bound. Abstract LP fixtures and P19 single-nuisance consistency are not a replay-realizable generalization or achievability proof. See docs/P20_NUISANCE_QUANTIFIER_AUDIT.md. Independent second audit, replay-law realization, and matching tester OPEN. |
| T1 | Full thresholded fairness regression with retained old-version headroom | PARTIAL | P11 gives minimax no-free-lunch; P14 gives a sound envelope-pruned upper bound. Tight instance-dependent lower characterization remains open. |
| T2 | Unknown-variance anytime-valid tester | OPEN | Avoid optional-stopping mistakes. |
| T3 | Tight graph-level bounded/Bernoulli complexity | PARTIAL | P16 handles homogeneous full-suite replay; P18 gives the one-edge tolerance phase; P19 gives a heterogeneous partial-replay control-cover characterization. A general graph-level theorem remains open. |
| T4 | Sound-but-imprecise and mildly unsound impact analysis | OPEN | Separate deterministic soundness from sentinel model. |
| T5 | Adaptive instance-dependent stopping advantage | OPEN | Need matching lower bound or separation. |
| T6 | Version-aware patch-locality separation vs fresh auditing | OPEN | P10 settles location information on a matching; broader fresh-audit comparison remains open. |
| T7 | Multi-patch amortized complexity | OPEN | Potential dynamic graph/certificate theorem. |

## Audit protocol

For each theorem:

1. freeze definitions and quantifiers;
2. derive the proof independently at least twice;
3. search nearest theorem literature for collision;
4. build finite-instance numerical checks where meaningful;
5. add adversarial tests designed to break assumptions;
6. only then mark **PROVED + AUDITED**.
