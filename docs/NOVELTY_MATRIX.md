# Novelty matrix

| Ingredient | Established literature | What we must *not* claim | Our research question |
|---|---|---|---|
| Regression test selection | IEEE TSE; STVR survey | Inventing regression selection | Query complexity of a fairness property after a stochastic patch |
| Change-impact analysis | STVR survey and extensive SE work | Inventing impact analysis | Treating sound impact as information that changes statistical testing complexity |
| Fairness testing | ESEC/FSE Themis | Inventing fairness testing | Fairness **regression** under stochastic execution and reusable prior certificates |
| Probabilistic fairness verification | OOPSLA/PACMPL FairSquare | First verification of program fairness | Statistical re-certification of an evolving version rather than whole-program probabilistic verification |
| Query-efficient fairness auditing | ICML active fairness auditing | First query-efficient fairness audit | Version-aware old/new coupled execution and patch-local information |
| Property testing | STOC/CCC/ToC literature | First graph/property tester | New evolving-software oracle/property pair |
| Common random numbers | Management Science and simulation literature | Inventing common-random-number variance reduction | Using replay coupling as an information primitive for software fairness regression |
| Paired Bernoulli / matched proportions | Biometrics and classical matched-pairs statistics | Inventing paired binary inference or McNemar-style efficiency | Linear-vs-quadratic small-patch complexity under two software execution oracles |
| Probabilistic coupling | POPL and probability/program logics | Inventing coupling | Query complexity consequences of executable old/new coupling |
| Pairwise graph design | Scandinavian Journal of Statistics and older design literature | Inventing graph allocation | Regression-specific `Psi` plus lower bounds in the coupled software oracle |
| Fractional set/group cover | Classical combinatorial optimization | Inventing fractional cover or LP rounding | How legal replay-group structure controls fairness-regression witness scheduling after software evolution |
| Group/subset querying | Group testing, active search, and simulation design | Inventing subset queries | Distinguishing edge-witness geometry from raw endpoint-information geometry under replay-compatible software groups |
| Incremental verification | ISSTA/PACMSE and prior verification literature | Inventing incremental verification | Statistical rather than proof-reuse complexity for fairness under execution noise |

## Submission-level novelty test

The paper is strong only if the final theorem package makes statements that cannot be obtained by simply substituting “software inputs” into a known pairwise experimental-design theorem.

Current high-value results/targets:

1. **proved:** sound patch location gives an Omega(M) advantage on an M-edge matching under a matched execution oracle;
2. **proved:** common-uniform old/new replay yields Theta(d^-1) rather than Theta(d^-2) small-patch complexity on a Bernoulli fairness-regression family;
3. **proved:** four-way replay cancels a nonzero fairness-neutral common patch and changes the small-gap exponent from d^-2 to d^-1;
4. **proved:** synchronized suite replay removes explicit edge-count dependence in the audited homogeneous family;
5. **proved upper / necessary lower program:** partial synchronized replay separates an edge-by-group witness cover C_edge from an active-vertex/group information cover C_vert, with C_vert <= C_edge; a matching minimax theorem is not claimed;
6. **open:** characterize when the P17 active-vertex information floor is attainable, or prove a separation;
7. **open:** full fairness-regression complexity with instance-dependent old-certificate headroom;
8. **open:** graph-level bounded/Bernoulli complexity that combines sparse deltas with shared vertices;
9. **open:** amortized complexity across multiple software versions.

A reviewer should be able to remove every generic ingredient above and still identify a theorem whose statement fundamentally depends on **software evolution and version-aware access**.
