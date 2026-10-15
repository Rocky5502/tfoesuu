# Exact shared-nuisance audit

This dependency-free supplement checks the distributional identities used in
Appendix `09_robust_matched_nuisance.tex`.  It is an exact rational-law audit,
not a Monte Carlo experiment.

Run from this directory:

```text
python -m unittest -v test_exact_witness_audit.py
python exact_witness_audit.py
```

The transcript order is `(old candidate, new candidate, old control, new
control)`.  The audit checks the complete null and alternative laws, both KL
directions (including the infinite reverse divergence), the 299-round shifted
support counterexample, the repaired strict domain
`0 < p < p+eta < p+s < p+s+eta < 1`, and candidate-only marginal overlap.
The result is deliberately scoped to exactly shared thresholds and one common
uniform tape; it is not a general composite-nuisance theorem.
