# Ten-perspective internal meta-review — 2026-10-15

This is an adversarial internal review exercise, not ten independent peer
reviews.  Each perspective was asked to identify a reason to reject or narrow
the new nuisance material.  The evidence record is
`STOC2027_P19_COMPOSITE_NUISANCE_PROOF_AUDIT_20261015.md`; theorem status is
controlled by `PROOF_STATUS.md`.

## 1. Information-theoretic lower bounds

The forward null-to-alternative divergence is finite only because the null
support is contained in the alternative support.  The reverse divergence is
infinite.  Any symmetric-KL statement would be false.  The appendix now gives
both directions and states the null-side stopping assumptions explicitly.

## 2. Sequential testing

The witness stopping rule has geometric alternative cost and null cost equal
to its deterministic horizon.  Consequently the useful `1/d` conclusion is a
null-expected or fixed-confidence minimax statement on an interior nuisance
set, not a two-sided expected-sample equivalence with identical constants.
The manuscript uses only the scoped conclusion.

## 3. Composite hypotheses

The shared nuisance cancels only because both endpoints and both versions use
one common uniform tape with exactly aligned thresholds.  The shifted-interval
counterexample assigns witness mass `2 eta` under a fairness-preserving null.
Thus the result is not a solution of the heterogeneous composite-null problem.

## 4. Formal specification

The incoming shifted-interval conditions omitted `p>0`.  Negative `p` values
could satisfy the displayed inequalities while silently invoking clipped
thresholds and invalidating the atom calculation.  The repaired hypothesis is
`0<p<p+eta<p+s<p+s+eta<1`, and a regression test rejects the old loophole.

## 5. Algorithmic access model

The conclusion depends on observing the raw four-way replay transcript.  It
does not follow from candidate-only marginals, independent tapes, or merely
matched means.  The code and appendix name the tape coupling and charge four
concrete executions per replay round.

## 6. Graph and topology scope

The new witness is a one-edge special case.  It supplies neither the mixed
quadratic/linear topology of P19 nor a graph-level allocation theorem.  P20
therefore remains a conjecture; no headline or abstract claim was expanded.

## 7. Numerical reproducibility

The attached P19 sequential study was rerun from source.  Its 57,600 trials
reproduced the canonical CSV byte-for-byte (SHA-256
`3d59d674928bd93aab69dbb519ef2920aecc5c923afda43ec322a3c212089546`).
The slopes are descriptive checks of this frozen grid, not fitted universal
exponents.  Exact-law tests, rather than additional Monte Carlo, are the
decisive evidence for the new witness.

## 8. Systems and executable-subject relevance

The exact threshold family validates the oracle mathematics but is not itself
a new evolving executable-software subject.  The historical Fairlearn census
remains observational supporting evidence.  A stochastic executable subject
with a legally replayable random tape is still an evidence gap and is not
hidden by the new appendix.

## 9. Novelty and prior art

Support-revealing events, geometric stopping, KL change of measure, and
composite-hypothesis overlap are classical.  The new material is positioned as
a nuisance-invariant special case and a scope obstruction.  Its value is to
clarify exactly when the paper's replay witness survives nuisance, not to claim
a new general testing theory.  Independent human literature sign-off remains
required.

## 10. STOC presentation and release control

The main text gives the result one short scoped paragraph; complete algebra is
in the appendix.  The first-twelve-content-page contribution narrative remains
centered on the previously audited replay topology results.  The paper must
not be called submission-ready until author proof/citation sign-off, authorship
and conflict checks, required video, and the external submission actions are
complete.

## Meta-verdict

**Scoped advance verified; no general composite-nuisance advance.**  The
mathematics and executable exact checks support N1--N3 after the domain repair.
The strongest remaining scientific blockers are (i) independent human audit
of the novelty boundary and complete proofs, (ii) the open P20 achievability
problem, and (iii) the absence of a stochastic executable subject realizing
the general replay setting.  None can be closed by additional GPU simulation
of the exact threshold family.
