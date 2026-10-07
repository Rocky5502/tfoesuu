# P19 independent audit: tape-partition derivation

**Conclusion: the first proof audit is reproduced independently.**

## A. Direct transcript reconstruction

For any synchronized replay group, the complete observation is constant on the
intervals induced by the distinct old/new thresholds. The probability of a
transcript state is therefore exactly the length of the corresponding tape
interval.

Use p=old threshold, l=p+s, h=p+s+tau, and alternative h+d.

### Group containing x, one matched high control, and any number of low vertices

Under the null, the top tape interval (h,1] has one transcript state of mass
r=1-h. Under alternative x, the interval (h,h+d] becomes a new x-specific
state while the old top state shrinks to mass r-d. Every lower interval keeps
the same transcript and mass. Therefore

  KL(Q0||Q1) = r log(r/(r-d)).

No Taylor argument is used in this derivation.

### Group containing x and low vertices but no matched high control

Under the null, interval (l,h] has the x-high/low-low transcript of mass tau
and (h,1] has the all-zero transcript of mass r. Under alternative x these
masses become tau+d and r-d. Thus

  KL(Q0||Q1)
  = tau log(tau/(tau+d)) + r log(r/(r-d)).

Again this follows from the exact categorical transcript law.

`tests/test_control_replay.py` independently reconstructs both categorical laws
from tape partitions and checks the two formulas numerically.

## B. Small-d asymptotics

Expanding the exact formulas gives

  K_control = d + d^2/(2r) + O(d^3),

and, for fixed tau>0,

  K_boundary
  = (d^2/2)(1/tau + 1/r) + O(d^3).

Hence a matched high control creates first-order information, while a low-only
reference carries only second-order local information.

## C. Lower-program derivation

The common null is the same for every alternative x in the high class. Adaptive
transcript chain rule therefore sums the exact group KL chosen on each round.
Taking null expectations yields one linear information constraint per x. The
minimum expected declared cost satisfying all constraints is exactly the mixed
LP implemented by `control_replay_information_lower_bound`.

## D. Upper construction cross-check

The upper statistic ignores cross-class high/low differences and compares only
patch deltas among high-class members. Under the null these are identical for
every tape value. Under alternative x they differ precisely on (h,h+d], so
each matched-control exposure is an independent Bernoulli(d) witness. Scaling a
fractional control cover by ceil(log(beta)/log(1-d)) therefore gives zero
type-I error and pointwise miss probability at most beta.

## E. Scope

The result is not claimed for arbitrary heterogeneous nulls. It requires the
two-class bipartite threshold family and declared high-class controls. The
purpose of P19 is to show exactly what extra control structure is sufficient
to recover the linear replay regime that P18 loses at fixed positive tolerance.