# Independent proof audit: P19 mixed boundary/control hybrid

Status: **PASS for the frozen equal-high two-class null and singleton
alternatives; FAIL outside that scope**.

## Claim audited

Let (U) be the high candidates with no legal group containing a second high
control. Assume every candidate is observable, (m=|U|>0), and define

    cbar_x = min {c_i : x in S_i}.

For the P19 null (all low new thresholds (p+s), all high new thresholds
(p+s+	au)) and alternatives that raise exactly one high candidate by (d),
a fixed-design tester has declared cost at most

    N_U * sum_{x in U} cbar_x
    + L * C_ctrl(A\U) + sum_{i:q_i*>0} c_i,

where

    N_U = ceil(8 (tau+d) log(m/delta) / d^2),
    L   = ceil(log(delta) / log(1-d)).

Both the type-I error and every pointwise type-II error are at most delta.

## First derivation

An unmatched candidate cannot share a legal group with another high vertex;
otherwise that group would be a matched control. Its cheapest containing group
therefore includes at least one low reference. On fresh common-uniform tapes,
the new-version mismatch between that high and low is Bernoulli(tau) under the
P19 null and Bernoulli(tau+d) under its singleton alternative. P18 with error
delta/m gives (N_U) rounds. A union bound controls false rejection over U.

The remaining candidates use the residual P19 fractional control cover. Its
contrast is pathwise zero under the P19 null and misses any covered singleton
alternative with probability at most delta. OR-combining the blocks proves the
claim. Distinct unmatched candidates cannot share their selected groups, and an
unmatched group cannot participate in a high-control query, so costs add without
hidden cross-coverage.

## Independent adversarial derivation

Re-derive the construction by partitioning alternatives, not observations:

1. For (x\in U), the P19 experiment restricted to a cheapest containing group
   reduces exactly to P18's Bernoulli mismatch experiment.
2. For (x\in A\setminus U), the rounded residual control cover supplies at
   least L independent sparse-witness opportunities.
3. Pointwise type-II control requires no union over alternatives. Only the
   boundary block contributes type-I error, hence delta/m is sufficient.

This independently yields the same schedule and declared-cost expression.

## Scope attacks that succeed

The hybrid is not a theorem for the full fairness composite null. In
(K_{2,1}), take old thresholds 0.20, low-new threshold 0.30, and high-new
thresholds 0.40 and 0.39 at tolerance 0.10. Both fairness edges are null-valid,
but the matched-high contrast fires with probability 0.01 per round.

It is also not valid for unrestricted simultaneous alternatives. Starting from
the exact P19 null with both highs at 0.40 and the low at 0.30, raising both highs
to 0.41 violates both edges but leaves their patch deltas identical, so a
matched-control-only block misses surely.

Therefore the theorem must retain:

- pathwise-equal high controls under every allowed null;
- exactly one raised high candidate per alternative (or a certified unchanged
  anchor);
- fresh independent tapes between rounds and a common tape within each group;
- global type-I allocation over all boundary tests;
- observability of every unmatched candidate.

## Familywise gap resolution

The fixed-design `log m` factor is real. For deterministic boundary-channel
counts `n_(1) <= ... <= n_(m)`, a uniform mixture over the `k` least-sampled
singleton alternatives and exact transcript chi-square give

    n_(k) >= log(1 + D_beta k) / rho2,

where `D_beta=(1-2 beta)^2/[beta(1-beta)]` and
`rho2=log(1+d^2(1/tau+1/r))`. Summing proves an
`Omega(m log m/d^2)` unit-cost lower bound for nonadaptive fixed allocations.

An unbounded-horizon sequential construction separates this from expected null
cost. Process exact per-candidate likelihood ratios with upper boundary
`m/beta` and lower boundary `beta`. Ville's inequality controls global type I;
the reciprocal likelihood-ratio martingale controls each pointwise miss. Wald
bounds give null rounds per channel

    [log(1/beta) + log(r/(r-d))] / K_bnd,

independent of `m`; only the changed channel retains additive `log m` delay.
Thus topology-size dependence is resolved for these two regimes. Exact adaptive
minimax constants and bounded-horizon adaptive allocations remain open. The
exact lower-program coefficient and this upper bound bracket the leading null
constant within `log(1/beta)/kl(1-beta,beta)`, a topology- and cost-independent
factor equal to `1.1304671072` at `beta=0.05`.

The unbounded horizon is not essential for the topology-size improvement.
Running at internal error `eta<beta` and accepting if the next query would cross
`max_i E_i[cost]/(beta-eta)` adds at most `beta-eta` pointwise miss probability
by Markov's inequality and cannot increase type I. At fixed beta and unit costs,
this deterministic adaptive cap is `O((m+log m)/d^2)=O(m/d^2)`. Part (i)'s null
information floor is `Omega(m/d^2)`, so the adaptive deterministic-cap topology
order is tight. Only exact constants and beta dependence remain open.

## Executable guards

- `mixed_control_replay_schedule` constructs both schedule blocks and fails on
  unobservable candidates.
- `test_mixed_control_hybrid_schedule_combines_boundary_and_control_blocks`
  checks a genuinely mixed topology.
- `test_mixed_control_hybrid_schedule_splits_familywise_boundary_error` checks
  the all-boundary extreme and the `delta/m` allocation.
- familywise fixed-design tests verify the exact one-round chi-square and every
  rankwise lower floor; sequential-bound tests verify both KL orientations,
  cost aggregation, and null per-channel independence from `m`.
- `test_matched_control_statistic_is_not_valid_for_arbitrary_composite_null`
  freezes the successful null-scope attack.
- planner tests ensure the public API now emits boundary schedules rather than
  falsely rejecting observable mixed topologies or manufacturing linear cost.
