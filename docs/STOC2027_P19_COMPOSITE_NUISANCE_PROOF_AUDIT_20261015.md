# P19 composite-nuisance proof audit — 2026-10-15

Status: **SCOPED ADVANCE VERIFIED after one domain repair.** This audit does
not promote P20, certify originality, or replace human proof review.

## Audited observation model

One legal four-way round observes the ordered raw transcript

`X = (old candidate, new candidate, old control, new control)`

from threshold programs driven by one common `U ~ Uniform[0,1]`. Tapes are
independent between rounds and all four coordinates are retained. Each round
costs four concrete program executions. The patch magnitude `d` is known.

For nuisance `(p,h)` with `0 < p < h < h+d < 1`, the matched null is
`(p,p) -> (h,h)` and its paired singleton alternative is
`(p,p) -> (h+d,h)`. The null and alternative are sets of distributions indexed
by the same nuisance set; correctness is uniform, while the converse fixes one
same-nuisance null/alternative pair.

## Exact atoms and KL directions

In coordinate order `(oc,nc,ot,nt)`, the complete laws are:

| State | Null mass | Alternative mass |
|---|---:|---:|
| `1111` | `p` | `p` |
| `0101` | `h-p` | `h-p` |
| `0100` | `0` | `d` |
| `0000` | `1-h` | `1-h-d` |

Therefore the discrepancy witness `0100` has null probability zero and
alternative probability exactly `d`. The support inclusion is strict:
`supp(P0) ⊊ supp(P1)`. Consequently,

`KL(P0 || P1) = (1-h) log((1-h)/(1-h-d))`,

while `KL(P1 || P0) = infinity`. Only the forward direction supports the
claimed expected-null converse.

For a tester adapted to independent-round transcripts, terminating with a
decision, with both uniform errors at most `delta < 1/2` and finite null
expected stopping time, the null log-likelihood increment is bounded. The
stopped chain rule and decision data processing give

`E_0[T] KL(P0 || P1) >= kl(1-delta,delta)`.

On every fixed interior nuisance set with `1-h` bounded below,
`KL(P0 || P1) = d + d^2/(2(1-h)) + O(d^3)`. The deterministic witness horizon
`ceil(log(delta)/log(1-d))` is also order `d^-1`, giving the claimed fixed-error
minimax null-expected order. No expected-alternative lower bound is inferred
from reverse KL.

## Counterexample found and repaired

The incoming Candidate B assumed only `0 < eta < s` and `p+s+eta < 1`.
That admitted negative thresholds. For example,
`p=-0.05, s=0.10, eta=0.02` satisfies those displayed inequalities, but
threshold clipping changes the two mean effects and the witness mass; the
claimed `2 eta` identity fails. The manuscript now requires

`0 < p < p+eta < p+s < p+s+eta < 1`.

Under this repaired domain the complete fair-null law is:

| State | Mass |
|---|---:|
| `1111` | `p` |
| `0111` | `eta` |
| `0101` | `s-eta` |
| `0001` | `eta` |
| `0000` | `1-p-s-eta` |

The two witness atoms have total mass `2 eta`; after `L` independent rounds the
false-rejection probability is exactly `1-(1-2 eta)^L`. At
`d=.01, eta=.005, delta=.05`, `L=299` and the value is
`0.9504637433623376`. Equal mean effects therefore do not imply pathwise
matching.

## Reduced-channel nonidentifiability

For candidate-only observations, let the null family be `Bernoulli(h0)` and the
alternative family `Bernoulli(h1+d)`, with nuisance values in `[a,b]` and valid
probabilities. If `d <= b-a`, choose admissible `h1` and `h0=h1+d`. The induced
laws are identical, both KL directions are zero, and type-I plus type-II error
is at least one. No uniformly `delta`-correct test exists for `delta<1/2`.
This elementary intersection argument does not apply to the matched four-way
channel, whose alternative-only witness atom prevents overlap.

## Executable falsification evidence

- New canonical module: `src/tfoesuu/robust_matched_nuisance.py`.
- Nine deterministic tests verify complete atom maps, witness masses, both KL
  directions, exact horizon/counterexample value, invalid-domain rejection,
  and reduced-channel overlap.
- The incoming 24-case rational enumerator and its six tests passed before
  integration. The canonical tests strictly strengthen it by checking reverse
  support failure and the previously omitted probability domain.
- No GPU or Monte Carlo run is needed for these exact finite laws.

## Remaining open problem

This result handles only an exactly shared nuisance annihilated pathwise. It
does not handle nonidentical, approximately matched, corrupted, or action-wise
unknown backgrounds; multiple simultaneous changes; unknown `d`; imperfect
tape synchronization; arbitrary positive-tolerance nulls; or a general
composite minimax allocation. P20 remains open.

## Adversarial-review verdict

Three read-only theory reviews independently agreed that Candidate A is valid
under the stated channel and that Candidate B is valid after the domain repair.
They also agreed that the ingredients are classical common-random-number,
support-splitting, stopped-KL, and hypothesis-set intersection arguments. The
paper therefore presents this as a nuisance-invariant special case plus a scope
counterexample, not as a standalone STOC novelty claim.
