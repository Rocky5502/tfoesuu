# Research blueprint

## North-star question

What is the optimal execution complexity of certifying that a software patch has not introduced a fairness regression when program executions are stochastic and earlier-version evidence can be reused?

## Contribution ladder

The project should not become a broad empirical fairness paper. The intended STOC structure is:

1. **New access model:** evolving stochastic software with counterfactual fairness graph, old/new versions, impact information, and replayable randomness.
2. **Impossibility:** sharp threshold certification is statistically impossible without separation.
3. **Core characterization:** a graph-and-uncertainty complexity quantity with upper and lower bounds.
4. **Regression advantage:** paired old/new execution can reduce uncertainty from outcome variance to patch-delta variance.
5. **Patch advantage:** sound change information removes unaffected comparisons from the query problem.
6. **Generalization:** bounded outputs, retained certificates, unknown variance, and multiple patches.

## Work order

### Phase A — theorem core
- Re-audit Gaussian lower bound under adaptive stopping.
- Add rigorous dual theorem and strong-duality proof.
- Generalize exact `Psi` families where they reveal structure rather than decorative algebra.
- Derive the Bernoulli coupled-delta analogue.

### Phase B — full fairness regression
- Carry forward old edge certificates rather than only testing patch neutrality.
- Introduce edge headroom and directionality.
- Seek an instance-dependent information allocation problem.

### Phase C — software-evolution structure
- Formalize distributionally sound vs replay-sound impact sets.
- Quantify false positives in impact analysis.
- Add sentinel sampling for controlled unsoundness.
- Study a sequence of patches and amortized certificate reuse.

### Phase D — GPU falsification campaign
- Exhaust graph families and heterogeneous variance profiles.
- Search for gaps between primal/dual/numerical conjectures.
- Estimate rare error rates at theorem constants.
- Search for candidate adaptivity-separation instances.

### Phase E — paper hardening
- Keep the first 10–12 pages theorem/story dense.
- Move routine calculations and extended experiments to appendices.
- Keep all literature claims backed by peer-reviewed sources.
- Maintain explicit AI-methodology disclosure required by the STOC 2027 CFP.

## Kill criteria

We should pivot rather than force the idea if any of these occurs:

- the final complexity theorem reduces immediately to a known experimental-design theorem with no new regression structure;
- coupled replay adds only a trivial implementation observation and no new query result;
- the full fairness problem cannot exploit old-version information beyond ordinary two-sample testing;
- lower bounds do not distinguish the evolving-software access model from static auditing.

The repository is designed to expose these failures early.
