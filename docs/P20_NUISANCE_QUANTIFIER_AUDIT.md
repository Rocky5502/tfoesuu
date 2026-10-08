# P20: Composite-Nuisance Quantifier Audit and Information-LP Separation

**Status:** exact finite LP result and conditional transcript-KL derivation;
independent statistical audit **OPEN**. This is not a new headline theorem and
does not promote P20 beyond **CONJECTURE**.

## 1. Why the current P20 candidate needs more than one information matrix

A nuisance parameter `eta` describes a single fairness-preserving null
program. The value is fixed throughout one experiment, not independently
selected for every legal replay action. Action choices may depend on previous
observations, so their expected counts can themselves depend on `eta`.

Freeze: (i) legal actions S with positive concrete costs c_S; (ii) a finite
nuisance set N; (iii) alternatives a with exact conditional observation laws
P_{0,eta}^{S} and P_{a,eta}^{S}; (iv) independent fresh tapes across queries
and a shared tape within each action, as prescribed by its replay semantics;
(v) one common history-adapted action policy and a stopping rule; and
(vi) type-I and pointwise type-II errors at most beta, where 0<beta<1/2.

Let

    I_{a,S}(eta) = KL(P_{0,eta}^{S} || P_{a,eta}^{S})

be a finite null-to-alternative one-query KL. For the policy's action count
N_S, the stopped-transcript KL chain rule, when the usual integrability and
stopping assumptions hold, gives

    KL(P_{0,eta}^{transcript} || P_{a,eta}^{transcript})
      = sum_S E_{0,eta}[N_S] I_{a,S}(eta).

The algorithm's adaptive choice probabilities cancel from the likelihood
ratio because its action rule is identical under the null and alternative
conditioned on the observed history. Data processing to the final accept/reject
decision implies, for every a and eta,

    sum_S E_{0,eta}[N_S] I_{a,S}(eta)
      >= kl(1-beta,beta).

Define the **pointwise-null information LP**

    L(eta) = min_{x_S>=0} sum_S c_S x_S
             s.t. sum_S I_{a,S}(eta) x_S >= kl(1-beta,beta)
                  for each alternative a.

Then every admissible policy satisfies

    sup_eta E_{0,eta}[cost] >= sup_eta L(eta).

This is a *necessary* lower bound for a uniform null-error criterion, not
a theorem of asymptotic tightness or achievability. On a finite nuisance grid,
the maximum is only a lower bound for the full continuous nuisance class.

## 2. The dangerous noncommutation

The quantity

    L_shared = min_{x_S>=0} sum_S c_S x_S
               s.t. sum_S I_{a,S}(eta) x_S >= K
                    for ALL (a,eta)

uses a **single fixed allocation vector** x for every null nuisance state.
It is not generally equal to sup_eta L(eta) and must NOT be used as a
lower bound for arbitrary adaptive testing, since E_{0,eta}[N_S] need
not be independent of eta.

For every finite nuisance family:

    sup_eta L(eta) <= L_shared,

but the inequality may be strict.

Take one alternative, two equal-cost actions, K=1, and two nuisance states:

                  action 1    action 2
    eta = 0          1        epsilon
    eta = 1       epsilon        1

with 0<epsilon<1. Each pointwise LP costs exactly 1. The shared
fixed-information allocation costs exactly

    L_shared = 2/(1+epsilon) > 1.

For m nuisance states and m equal-cost actions with information matrix
the m-by-m identity, sup_eta L(eta)=1 while L_shared=m.

**The matrices here are abstract nonnegative information coefficients.**
No claim is made that every such matrix is realizable by the frozen
four-way Bernoulli software oracle. A separate replay-law derivation and
compatibility check are mandatory before making a software theorem.

## 3. What the generic LP actually does

`src/tfoesuu/replay_information.py` solves a generic fixed
action-information cover.

`src/tfoesuu/nuisance_information.py` computes:
1. the minimum cost for each fixed nuisance information matrix;
2. the maximum of these necessary pointwise budgets; and
3. the cost of one shared fixed-information allocation subject to all
   scenario-alternative inequalities.

The third quantity is **not** a guaranteed practical testing cost and
**not** an adaptive minimax lower bound. KL requirements alone do not
imply a finite-sample level-beta test exists at those sample counts.

`tests/test_nuisance_information.py` pins exact algebraic examples,
zero-information nonidentifiability, and input rejection.

## 4. Consequences for any future P20 theorem

A future P20 must distinguish all of:
- a *fixed* null nuisance eta;
- a *single* alternative a compared against that eta;
- action-dependent, but history-selected, replay observations;
- nuisance-dependent expected action counts under adaptive policies;
- one nuisance-independent, fixed, predeclared schedule;
- least-favourable nuisance selections that must remain globally
  consistent across the actions in one experiment.

Do not minimize I_{a,S}(eta) separately over eta for each action and call
the result an exact adaptive information floor. Such an entrywise-inf
matrix represents a stronger adversary that can change eta between actions,
unless independently justified. Inserting it into an LP may produce a
**more demanding fixed-design constraint** and is not automatically a
valid adaptive lower bound.

## 5. Archival collision boundary, verified October 8, 2026

This distinction is closely connected to established controlled sensing,
sequential composite testing, and action/error-exponent allocation. Treat
the following publications as prior art, not as sources of new P20 theorems:

- Deshmukh, Veeravalli and Bhashyam, *Sequential controlled sensing for
  composite multihypothesis testing*, **Sequential Analysis** 40(2):
  259–289 (2021), DOI 10.1080/07474946.2021.1912525.
- Hsu and Wang, *Tradeoffs Among Action Taking Policies Matter in Active
  Sequential Multi-Hypothesis Testing: The Optimal Error Exponent Region*,
  **IEEE Transactions on Information Theory** 71(9):6546–6565 (2025),
  DOI 10.1109/TIT.2025.3588527.
- Gan, Jia, Li and Tayur, *Toward a Liquid Biopsy: Greedy Approximation
  Algorithms for Active Sequential Hypothesis Testing*,
  **Management Science**, DOI 10.1287/mnsc.2023.00829,
  published online August 19, 2025 (archival).

The 2026 hypergraph and property-testing literature is useful framing,
but does not validate or replace the composite-null transcript argument.
Do not cite arXiv-only papers, future-status preprints, or unverifiable
paper metadata merely to enlarge the reference list.

## 6. Remaining research obligations

- Derive I_{a,S}(eta) from EXACT old/new threshold observation partitions
  for a controlled multi-class replay family.
- Construct a finite replay-realizable crossing-nuisance example or prove
  that the replay oracle prevents such a crossing.
- Study whether calibration/control actions let an adaptive policy identify
  the nuisance cheaply enough to beat every shared fixed-design cover.
- Prove or refute a matching achievability result with its actual testing
  statistic, type-I control, finite-sample error and rounding cost.
- Independently audit the stopped-transcript measure-change argument.
- Update the manuscript's theorem statements only after these gates close.
