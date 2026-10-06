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
6. **Replay hierarchy:** edgewise, partial-group, and full-suite synchronization expose different graph/information geometries.
7. **Generalization:** retained certificates, unknown variance, imperfect impact information, and multiple patches.

## Work order

### Phase A — theorem core
- Keep P1--P16 frozen unless a genuine audit issue appears.
- Freeze the audited homogeneous P17 result: the raw-output lower program and
  executable raw-contrast schedule are both governed by C_vert, while C_edge is
  a valid witness-scheduling upper geometry that can be arbitrarily larger or
  infeasible.
- Treat P17 attainability as solved for the homogeneous
  single-changed-endpoint family and for the audited group-coherent/d-detectable
  sufficient-condition class.  The latter allows different null patch effects
  across disconnected replay components while requiring pathwise coherence
  inside each legal replay group.
- The remaining P17 frontier is arbitrary heterogeneous/composite-null replay
  beyond group coherence: identify extra control structure, a baseline-adjusted
  statistic, or a sharper decision geometry.
- Generalize only where the theorem exposes new evolving-software structure,
  rather than adding decorative graph algebra.

### Phase B — full fairness regression
- Carry forward old edge certificates rather than only testing patch neutrality.
- Introduce edge headroom and directionality.
- Seek an instance-dependent information allocation problem.

### Phase C — software-evolution structure
- Formalize distributionally sound vs replay-sound impact sets.
- Quantify false positives in impact analysis.
- Add sentinel sampling for controlled unsoundness.
- Study a sequence of patches and amortized certificate reuse.

### Phase D — computational falsification campaign
- Exhaust graph families, legal replay-group families, and heterogeneous cost/variance profiles.
- For the homogeneous family, use the proved C_vert result as a regression test;
  search heterogeneous/composite-null instances for failures of raw contrast and
  candidate replacement decision geometries.
- Estimate rare error rates only for theorem-backed executable testers.
- Search for candidate adaptivity/separation instances; treat every computational pattern as a conjecture until proved.

### Phase E — paper hardening
- Keep the first 10–12 pages theorem/story dense.
- Move routine calculations and extended experiments to appendices.
- Keep all literature claims backed by peer-reviewed sources.
- Maintain explicit AI-methodology disclosure required by the STOC 2027 CFP.

## Kill criteria

We should pivot rather than force the idea if any of these occurs:

- the final complexity theorem reduces immediately to a known experimental-design theorem with no new regression structure;
- the replay hierarchy collapses to generic CRN/set-cover facts with no theorem that depends on evolving-software fairness access;
- the full fairness problem cannot exploit old-version information beyond ordinary two-sample testing;
- lower bounds do not distinguish the evolving-software access model from static auditing.

The repository is designed to expose these failures early.
