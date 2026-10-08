# P19 mixed-control information LP: second-order candidate (NOT PROMOTED)

Scope: finite legal replay groups, fixed positive costs, bipartite two-class
P19 null, fixed tolerance tau>0, and positive residual probability r.
This is an information-allocation LP statement, not a minimax testing theorem.

Partition high candidates into C (some group contains a second high control)
and U (no matched-high group). Define C_U as the minimum boundary-group
fractional cover cost on U and C_C as the minimum matched-control cover cost
on C. Set ell=kl(1-beta,beta), Kc=-r log(1-d/r), and
Kb=tau log(tau/(tau+d))+r log(r/(r-d)).

Any group containing x in U has no other high vertex. Hence the U-only
boundary subproblem separates exactly from the C subproblem. Let lambda be
an optimal dual for the control cover on C. If every boundary group g
containing x in C satisfies (Kb/Kc)*lambda[x] <= cost[g], a scaled
control-cover primal and dual certify

    Q_LP(d) = ell * (C_U/Kb(d) + C_C/Kc(d)).

Since Kb/Kc = Theta(d) at fixed tau>0, this sufficient condition holds
for all sufficiently small d with finite fixed positive costs.

Writing b2=(1/tau+1/r)/2 and b3=(1/r^2-1/tau^2)/3 gives the candidate
two-term expansion

    Q_LP(d) = ell*C_U/(b2*d^2)
              + ell*(C_C - b3*C_U/b2^2)/d + O(1).

The boundary-KL cubic correction is necessary in the d^-1 coefficient.
The exact decomposition is not asserted at arbitrary finite d: very cheap
boundary groups can dominate until d becomes sufficiently small.

Deterministic independent falsification checks: 318 eligible seeded
finite-action cases (162 mixed, 68 controlled, 88 boundary-only), all
satisfying the dual sufficient condition and objective identity at
d=1e-6, with maximum relative LP discrepancy 3.89e-16.
These are synthetic LP checks, NOT empirical results or proof audits.

Required gates: independent proof audit, nearest-prior-work collision check,
actual repository regression tests, full CI and paper build. P19 retains its
frozen two-class scope; P20 remains conjectural. No theorem promotion.
