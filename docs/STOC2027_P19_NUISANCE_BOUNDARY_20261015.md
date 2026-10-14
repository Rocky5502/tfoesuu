# STOC 2027 P19: Unknown Shared-Nuisance Boundary (15 Oct 2026)

**Status:** independently derived narrow result and exact-law audit; **not** a claim of unrestricted composite-nuisance optimality or STOC acceptance. This note is deliberately separate from the current release manuscripts and frozen data.

## Exact legal observation model
Each round draws an independent U~Unif[0,1] and returns all four ordered binary program outputs (old candidate, new candidate, old control, new control) under the **same** U. Each round costs four concrete program executions. Let d>0 be known and delta in (0,1/2).

### Shared unknown-background witness
Null thresholds: old (p,p), new (h,h) for **unknown** 0<p<h<h+d<1. Singleton alternative: old (p,p), new (h+d,h). The observed difference between endpoint old/new patch deltas has null probability 0 and alternative probability exactly d, uniformly in the unknown p,h.

After L=ceil(log(delta)/log(1-d)) independent rounds, rejecting on any discrepancy has type-I error 0, type-II error <=delta, and cost 4L concrete executions. Under any fixed admissible p,h, the **full four-output transcript** null-to-alternative KL per round equals (1-h)*log((1-h)/(1-h-d)). Therefore any sequential delta-correct tester limited to this four-way oracle with finite expected null stopping requires at least kl(1-delta,delta)/KL expected null rounds (data processing/chain rule). For fixed interior h, this is order 1/d. The upper guarantee is uniform in unknown shared p,h; the lower comparison is pointwise. This DOES NOT cover unequal endpoint nuisance, approximate replay, unknown d, multiple changed candidates, or unrestricted composite alternative classes.

### Fair null that falsifies mean-only matching
Take old thresholds (p,p+eta), new thresholds (p+s,p+s+eta), 0<eta<s and p+s+eta<1. Both expected patch effects equal s; old and new edge disparities each equal eta and satisfy fairness tolerance tau>=eta. Yet common-tape patch-delta indicators differ on a symmetric-difference interval of mass **2 eta**. Naively running the zero-witness rule for L(d,delta) rounds rejects this valid null with probability 1-(1-2 eta)^L. For d=0.01, eta=0.005, delta=0.05, L=299 and false rejection ~0.9504637433623376. As d->0 with fixed eta, false rejection tends to one.

This demonstrates why **pathwise replay matching cannot be replaced by equality of mean patch effects**. It is not a universal impossibility result for all composite tests.

### Scoped reduced-channel overlap
If the only observation is Bernoulli(h) with completely unknown null h in [a,b], while an alternative is Bernoulli(h+d) for the same nuisance interval, the two distribution families intersect whenever 0<d<=b-a. A uniformly delta-correct test (delta<1/2) is then impossible on that **marginal-only channel**. Do not transfer this to richer four-way transcript access.

## Validation and integration gates
- An independent local Fraction-based enumeration checked 24 exact four-output transcript laws with normalized probability vectors, witness probabilities, and KL. Six deterministic unit tests passed.
- A separate editable Overleaf ZIP carries the fully stated proposition, two individually numbered/labeled equations, proof, main-text scoped reference, and test source. This GitHub note is not the Overleaf source or an upload to Overleaf.
- Independent human proof audit and detailed comparison to Chernoff sequential design; Nitinawarat/Atia/Veeravalli controlled sensing; Deshmukh/Veeravalli/Bhashyam 2021; Glasserman/Yao 1992 remain required before any novelty claim.
- Preserve the 198 original P12/P15 configuration records, seven-population Fairlearn census, and already released work unchanged. No new GPU run, paid API, GitHub main merge, public release, or HotCRP submission is authorized by this note.

**GitHub base:** codex/final-submission-audit-20261012 at e64b781eeeddd5b1c37f750ce13164c761671aa5. This branch intentionally isolates research changes.