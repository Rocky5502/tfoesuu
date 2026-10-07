# Proof Attack: P18 Nuisance-Aware Replay Information Geometry

Status: **CONJECTURE / RESEARCH ATTACK ONLY**

This note is intentionally separate from the audited P15 and P17 results. It does
not promote a new theorem. Its purpose is to freeze the next non-overlapping
question and prevent the project from rediscovering results already proved.

## 1. Non-overlap with existing results

- **P15 already proves** the one-edge nonzero-common-patch separation:
  vertex-paired replay has quadratic small-gap complexity while four-way
  counterfactual replay has linear small-gap complexity in the audited Bernoulli
  threshold family.
- **P17 already proves** an active-vertex fractional-cover characterization for
  the frozen homogeneous single-changed-endpoint partial-replay family.

P18 must therefore be graph-level and nuisance-aware. Re-proving the P15
two-endpoint separation under new notation would be duplication, not progress.

## 2. Candidate general model

Let H=(V,E) be the residual fairness graph after deterministic certificate
pruning. Let S be a family of legal replay actions and c(S)>0 their declared
costs. Let N denote a frozen class of fairness-preserving nuisance patch effects.
For each alternative a (for example, an oriented violating edge) and legal action
S, define an information coefficient

    I[a,S]

from the exact null-to-alternative observation law induced by the replay
semantics and the least-favourable nuisance allowed by N.

The candidate optimization is

    minimize    sum_S c(S) x_S
    subject to  sum_S I[a,S] x_S >= K_beta   for every alternative a,
                x_S >= 0.

Here K_beta is an information requirement such as kl(1-beta,beta), but the exact
right-hand side and KL orientation must be derived from the frozen testing model.

## 3. Candidate specialization checks

Any acceptable P18 theorem must recover already-audited results rather than
contradict them.

### 3.1 Homogeneous partial replay

For the frozen P17 family, the exact raw-output transcript KL depends on whether
a legal group contains the changed active vertex. The general information
program should reduce to the audited active-vertex geometry after factoring out
the common per-informative-query KL.

### 3.2 One-edge common benign patch

For the P15 family, endpoint-separated vertex replay and four-way co-replay have
different exact KL orders. P18 should reproduce P15 as a one-edge special case,
not introduce a second theorem with the same content.

### 3.3 Endpoint-containing replay under nuisance

The main new conjectural phenomenon is that some nuisance classes make
endpoint-containing same-tape actions first-order informative (order d) while
actions that cannot cancel the nuisance are only second-order informative
(order d^2). This must be proved from exact observation laws; asymptotic labels
alone are not a theorem.

## 4. Required proof obligations

Before promotion, establish all of the following:

1. Freeze the null nuisance class N and alternative family.
2. Freeze legal replay semantics and concrete cost units.
3. Derive exact action-by-alternative observation laws.
4. Compute the correct KL orientation used by the transcript lower bound.
5. Prove a lower bound for adaptive strategies; do not assume nonadaptive
   additivity without justification.
6. Construct an upper procedure whose allocation is tied to the same structural
   quantity, including integer rounding and stopping semantics.
7. Check unknown orientation of the changed endpoint.
8. Check whether actions overlap or reuse the same random tape across time.
9. Produce finite counterexamples for every proposed generalization beyond the
   frozen nuisance class.
10. Perform a fresh archival collision audit against controlled sensing and
    active sequential hypothesis testing.

## 5. Failure modes to search deliberately

- Composite nulls for which separated observations can estimate the nuisance
  cheaply enough to beat a naive C_edge/d claim.
- Legal replay families where the least-favourable nuisance depends on the
  allocation itself.
- Actions whose KL is not captured by a scalar endpoint-incidence coefficient.
- Adaptive policies that learn nuisance parameters and change the optimal
  exponent or combinatorial geometry.
- Nonidentifiable alternatives even though every fairness edge is covered in a
  purely combinatorial sense.

## 6. Implementation scaffold

`src/tfoesuu/replay_information.py` solves a generic linear information-cover
program once an information matrix has already been justified mathematically.
`tests/test_replay_information.py` contains optimization fixtures, including
a mixed linear-versus-quadratic information tradeoff.

These files are **not proof artifacts** and must never be cited as evidence that
P18 is true. Their role is to make candidate finite instances and reductions
auditable once exact coefficients are derived.

## 7. Collision boundary

Classical common random numbers, controlled sensing, active hypothesis testing,
and cost-sensitive experiment selection already establish that shared randomness
and KL-driven action allocation are not new. The only defensible P18 novelty
would be a theorem showing that software replay semantics induce a specific
structured action-information geometry for fairness-regression certification,
with matching lower and upper complexity under a precisely stated nuisance class.
