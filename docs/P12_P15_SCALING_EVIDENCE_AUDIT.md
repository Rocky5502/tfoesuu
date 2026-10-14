# P12/P15 scaling-evidence audit

Status: **existing campaign validates finite simulator laws; it does not
identify empirical sample-complexity exponents.**

## Audited design

The admitted campaign has 54 P12 and 144 P15 configurations, with 100,000
Monte Carlo trials per configuration. Each row contains empirical decision
rates at the theorem-prescribed schedule, and the validator recomputes that
schedule exactly from `(p, shared_patch, d, beta)`. It also verifies 594
empirical rates against their exact binomial laws.

The recorded round and concrete-execution counts are therefore deterministic
outputs of the proved formulas. They are not measured stopping times. The
records contain no instrumented wall-clock or GPU-kernel duration and execute
sufficient-statistic samplers rather than an external software subject.

## Falsification question

Can the existing rows support a log--log fit claiming an *observed* `d^-1`
versus `d^-2` sample-complexity separation?

**No.** Each `(method, p, shared_patch, d, beta)` is evaluated at one sample
budget chosen by the corresponding analytical upper bound. As `d` varies, the
budget varies by construction. Regressing those prescribed budgets on `d`
would merely fit the input formula back to itself. Empirical error rates near
their exact probabilities establish sampler fidelity at those budgets; they do
not estimate the number of samples needed to cross a target error.

Consequently:

- a figure of schedule versus `d` may be labeled only as a theoretical or
  formula-derived curve;
- the campaign cannot support a caption such as "measured execution
  complexity" or "observed scaling exponent";
- GPU elapsed time would still not be program-execution complexity, even if it
  had been instrumented;
- the current manuscript correctly reports the campaign as exact-law simulator
  validation and does not add the requested empirical-complexity figure.

## Smallest scientifically valid follow-up

An empirical power-curve study would preregister independent sample budgets for
each fixed law rather than derive one budget from the theorem. For each method
and `d`, it would evaluate several budgets bracketing the target miss
probability, estimate the crossing budget with binomial confidence intervals,
and fit slopes only after freezing the fitting range and exclusion rules. It
would report replay rounds and concrete executions separately.

Such a campaign is not useful for the present sufficient-statistic models:
their entire finite power curves are already known exactly, so additional GPU
Monte Carlo would add noise rather than scientific information. A genuinely
new empirical scaling study becomes informative only after identifying an
executable stochastic old/new subject whose legal random-tape replay matches
the theorem oracle. The deterministic Fairlearn PMF census is valuable
historical software evidence but does not supply that oracle. No new GPU run is
warranted until this subject gate is met and the experiment is separately
preregistered.

## Machine-readable release fence

`validate_preview_campaign` emits:

- `schedule_counts_are_formula_derived: true`;
- `instrumented_runtime_present: false` for the frozen records; and
- `supports_empirical_sample_complexity_fit: false`.

These fields prevent downstream reporting from silently promoting a simulator
conformance campaign into empirical complexity evidence.
