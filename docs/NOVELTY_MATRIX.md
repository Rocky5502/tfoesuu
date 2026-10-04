# Novelty matrix

| Ingredient | Established literature | What we must *not* claim | Our research question |
|---|---|---|---|
| Regression test selection | IEEE TSE; STVR survey | Inventing regression selection | Query complexity of a fairness property after a stochastic patch |
| Change-impact analysis | STVR survey and extensive SE work | Inventing impact analysis | Treating sound impact as information that changes statistical testing complexity |
| Fairness testing | ESEC/FSE Themis | Inventing fairness testing | Fairness **regression** under stochastic execution and reusable prior certificates |
| Query-efficient fairness auditing | ICML active fairness auditing | First query-efficient fairness audit | Version-aware old/new coupled execution and patch-local information |
| Property testing | STOC/CCC/ToC literature | First graph/property tester | New evolving-software oracle/property pair |
| Common random numbers | Management Science and simulation literature | Inventing common-random-number variance reduction | Using replay coupling as an information primitive for software fairness regression |
| Probabilistic coupling | POPL and probability/program logics | Inventing coupling | Query complexity consequences of executable old/new coupling |
| Pairwise graph design | Scandinavian Journal of Statistics and older design literature | Inventing graph allocation | Regression-specific `Psi` plus lower bounds in the coupled software oracle |
| Incremental verification | ISSTA/PACMSE and prior verification literature | Inventing incremental verification | Statistical rather than proof-reuse complexity for fairness under execution noise |

## Submission-level novelty test

The paper is strong only if the final theorem package makes at least one statement that cannot be obtained by simply substituting “software inputs” into a known pairwise experimental-design theorem. The high-value targets are:

1. a full fairness-regression complexity using old-certificate headroom;
2. a separation between version-aware coupled testing and fresh auditing;
3. a separation caused by patch locality under a matched oracle;
4. an amortized theorem across multiple software versions;
5. a bounded/Bernoulli result where small patch size itself collapses uncertainty.
