# Proof Attack: P20 General Nuisance-Aware Replay Information Geometry

Status: **CONJECTURE / RESEARCH ATTACK ONLY**

This note is intentionally separate from the audited P15--P19 results. It does
not promote a theorem. Its purpose is to freeze the next non-overlapping
graph-level question.

## 1. Non-overlap with existing results

- **P15** already proves the one-edge nonzero-common-patch exponent separation.
- **P17** already proves the homogeneous active-vertex partial-replay geometry.
- **P18** already proves the one-edge threshold/tolerance phase transition.
- **P19** already proves a matched-background control-cover result for the
  bipartite two-class heterogeneous threshold family.

P20 must therefore be strictly broader than each of these scoped theorems.

## 2. Candidate general model

Let H=(V,E) be the residual fairness graph after deterministic certificate
pruning. Let S be a family of legal replay actions with costs c(S), and let N be
a frozen class of fairness-preserving nuisance patch effects.

Index active alternatives by a. For every legal action S and alternative a,
derive the exact observation law under the null nuisance class and the
alternative, then define an information coefficient I[a,S] from the justified
change-of-measure quantity.

The candidate optimization is

    minimize    sum_S c(S) x_S
    subject to  sum_S I[a,S] x_S >= K_a   for every active alternative a,
                x_S >= 0.

The right-hand side K_a, KL orientation, and least-favourable nuisance are part
of the theorem and must not be inserted heuristically.

## 3. Required specialization checks

Any acceptable P20 theorem must recover, rather than duplicate, the validated
spine:

1. the P17 active-vertex geometry under the frozen homogeneous family;
2. the P15 one-edge common-patch linear-vs-quadratic separation;
3. the P18 threshold phase transition;
4. the P19 mixed first-order/second-order control geometry.

## 4. Required proof obligations

Before promotion:

1. freeze the composite null and alternative family;
2. freeze legal replay semantics and cost units;
3. derive exact action-by-alternative transcript laws;
4. prove the adaptive lower bound rather than assume nonadaptive additivity;
5. construct an attainable upper procedure tied to the same structural object;
6. audit unknown orientation, stopping, tape reuse, and nuisance learning;
7. search for nonidentifiability and degenerate-cost counterexamples;
8. perform a fresh archival collision audit against controlled sensing, active
   sequential hypothesis testing, experimental design, and combinatorial
   pure-exploration literature;
9. synchronize code, tests, proof ledger, and manuscript only after the proof
   gates pass.

## 5. Failure modes to attack deliberately

- nuisance estimation may make an apparently quadratic action effectively useful;
- the least-favourable nuisance may depend on the allocation;
- one scalar information coefficient may fail to capture the relevant joint law;
- adaptive policies may alter the optimal structural geometry;
- purely combinatorial coverage may not imply statistical identifiability.

## 6. Implementation scaffold

`src/tfoesuu/replay_information.py` solves a generic linear information-cover
program once a valid information matrix has already been justified.
`tests/test_replay_information.py` contains deterministic optimization
fixtures, including mixed first-order/second-order tradeoffs.

These files are **not proof artifacts** and must never be cited as evidence that
P20 is true.

## 7. Novelty boundary

Common random numbers, paired testing, matched controls, controlled sensing,
KL-driven action selection, fractional covering, and graph experimental design
are established prior art. The only defensible P20 novelty would be a theorem
showing that executable software replay semantics induce a particular structured
information geometry for fairness-regression certification, with matching lower
and upper complexity under a precisely stated nuisance class.
