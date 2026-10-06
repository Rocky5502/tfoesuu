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
5. **proved upper / necessary lower program:** partial synchronized replay separates an edge-by-group witness cover C_edge from an active-vertex/group information cover C_vert, with C_vert <= C_edge;
6. **proved LP-geometry structure:** coherent group signatures give equality, K_n pair groups give C_edge/C_vert=n-1, and a path/reference construction gives finite C_vert with infeasible C_edge; these are not minimax statements;
7. **proved + audited:** a within-group raw patch-delta contrast schedule attains the C_vert geometry in the frozen homogeneous single-changed-endpoint family, yielding matching lower/upper combinatorial geometry and d^-1 fixed-confidence order; CRN/multiple-comparison techniques themselves are established prior art;
8. **candidate under audit:** a group-coherent composite-null sufficient condition allows globally heterogeneous patch effects across disconnected replay components while preserving the C_vert schedule; this must not be called audited or manuscript-promoted until its gates pass;
9. **open:** characterize arbitrary heterogeneous/composite fairness-preserving nulls that violate group coherence, where the frozen scope counterexample rules out naive raw contrast;
10. **open:** full fairness-regression complexity with instance-dependent old-certificate headroom;
11. **open:** graph-level bounded/Bernoulli complexity that combines sparse deltas with shared vertices;
12. **open:** amortized complexity across multiple software versions.

A reviewer should be able to remove every generic ingredient above and still identify a theorem whose statement fundamentally depends on **software evolution and version-aware access**.
