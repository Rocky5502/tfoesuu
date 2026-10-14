# Hostile novelty audit: P12--P19

Status: **automated archival collision audit complete; independent human
literature sign-off still required before submission.**  This document is a
claim-control artifact, not an assertion that an automated search proves
novelty.

## Method and verdict vocabulary

The audit compares mathematical mechanism, observation sigma-algebra, null and
alternative classes, cost unit, and lower-bound quantifiers.  It uses primary
publisher or proceedings records where available.  A **specialized
instantiation** derives a sharp consequence of established machinery in the
paper's software-replay model.  A **scoped extension** adds a theorem statement
not found in the checked sources but remains assembled from established tools.
"Potentially distinct" means only that this search found no identical theorem;
it is not a priority or novelty certification.

## Claim-by-claim matrix

| Claim | TFOESUU statement and frozen scope | Closest checked primary work | Mathematical overlap | Distinguishing oracle/null/cost feature | Hostile verdict and permitted wording |
|---|---|---|---|---|---|
| P12 | One interior Bernoulli edge under common-uniform old/new raw-pair replay has `Theta(d^-1 log(1/delta))`, versus `Theta(d^-2 log(1/delta))` under independent new-version samples. | Connor, paired proportions, DOI [10.2307/2531961](https://doi.org/10.2307/2531961); McNemar's matched-pair test; classical common-random-number work. | Paired binary inference and discordant-pair efficiency are established; the rare discordance probability is order `d`. | The theorem freezes executable old/new threshold programs, the retained baseline, two legal software oracles, and concrete execution accounting, with matching transcript-KL converses. | **Specialized instantiation.** Claim an exact access-model separation for fairness regression; never claim invention of paired testing, coupling, or the `d^-1` rare-event mechanism in isolation. |
| P13 | Unknown changed edge on an `M`-edge matching costs `Theta(M/d)` at fixed confidence in the frozen replay family. | Cohen and Zhao, active anomaly testing, DOI [10.1109/TIT.2014.2387857](https://doi.org/10.1109/TIT.2014.2387857); Malloy and Nowak, sequential sparse recovery, DOI [10.1109/TIT.2014.2363846](https://doi.org/10.1109/TIT.2014.2363846). | Searching for a rare anomalous coordinate by sequential tests and transcript KL is established. | A coordinate is a counterfactual software edge whose observation is an old/new common-tape transcript; the theorem is fixed-confidence and explicitly records the active anomaly-search boundary. | **Specialized instantiation.** Use as a software-oracle consequence, not as a new anomaly-search theorem. |
| P14 | Sound effect envelopes remove certified-safe edges before applying the Gaussian allocation to the residual graph. | Regression-test selection and change-impact analysis; established graph-based pairwise design below. | Safe pruning followed by testing is a standard reuse pattern. | The envelope is a version-delta bound tied by the fairness identity to a stochastic residual test. | **Specialized instantiation; not a novelty claim** for impact analysis or pruning. Its value is the sound interface between deterministic reuse and the declared stochastic theorem. |
| P15 | Four raw outputs sharing one tape cancel a nonzero common patch pathwise; the scoped family changes from vertex-paired `Theta(d^-2)` to four-way `Theta(d^-1)`. | Common random numbers/control variates and paired designs; Naghshvar and Javidi, DOI [10.1214/13-AOS1144](https://doi.org/10.1214/13-AOS1144), for active sequential testing. | Nuisance cancellation by shared randomness and KL lower bounds are classical. | The observation is the ordered four-output old/new-by-endpoint transcript; the comparison holds one executable patch family fixed and separates two replay sigma-algebras at explicit execution cost. | **Scoped extension.** Defend the four-way software-replay separation, not common-random-number variance reduction or nuisance cancellation generally. |
| P16 | Full-suite replay has `Theta(d^-1 log(1/delta))` rounds in the homogeneous one-changed-endpoint family, while each round costs `2 n_active` executions. | Common-random-number multiple comparisons and group-query/property-testing traditions. | One shared random input can support many comparisons; batching is established. | All active old/new executions share the identical random tape and retain the raw vector; the theorem separates replay rounds from program executions. | **Specialized instantiation.** The edge-count-free round bound is conditional on a stronger oracle and must never be advertised as edge-count-free execution cost. |
| P17 | Legal replay groups induce edge-witness cover `C_edge` and raw active-vertex information cover `C_vert`; `C_vert` is attainable only in the frozen homogeneous single-changed-endpoint family, and a heterogeneous fair-null counterexample blocks silent extension. | Fractional covering is classical; Singh, Singh, and Davidov's graph-based max--min pairwise design, DOI [10.1111/sjos.12757](https://doi.org/10.1111/sjos.12757). | LP covering, graph allocation, and pairwise experimental design are established. | Two different incidence matrices arise from what a raw old/new group transcript reveals versus what a witness-only planner requires. The positive theorem and counterexample name incompatible null scopes. | **Scoped extension, potentially distinct subject to human literature sign-off.** Claim the replay-induced separation and its exact scope boundary; fractional cover, LP duality, and graph design are not a novelty claim. |
| P18 | A one-edge thresholded synchronized transcript has `Theta((tau+d)d^-2 log(1/delta))` complexity under the stated interior condition. | Paired-proportion inference and classical Bernoulli concentration; tolerant property testing supplies a broader hardness analogy. | The exact KL expansion changes from first to second order when a positive boundary mass is present; the testing tools are standard. | The exact four-output threshold transcript and composite fairness-boundary law connect tolerance to executable replay. | **Specialized instantiation.** Present an exact replay/tolerance boundary, not a universal phase transition or new concentration inequality. |
| P19 | In a bipartite equal-high two-class null, legal matched-background controls contribute first-order KL, boundary-only groups second-order KL, giving a mixed information LP and scoped hybrid upper bound; fixed nonadaptive disjoint boundary allocations pay `Omega(m log m/d^2)`, while sequential stopping has `Theta(m/d^2)` expected-null topology scaling at fixed confidence. | Nitinawarat, Atia, and Veeravalli, controlled sensing, DOI [10.1109/TAC.2013.2261188](https://doi.org/10.1109/TAC.2013.2261188); Nitinawarat and Veeravalli, nonuniform control cost, DOI [10.1080/07474946.2014.961864](https://doi.org/10.1080/07474946.2014.961864); Deshmukh, Veeravalli, and Bhashyam, composite controlled sensing, DOI [10.1080/07474946.2021.1912525](https://doi.org/10.1080/07474946.2021.1912525); Malloy and Nowak above; Malek et al., [AISTATS 2017](https://proceedings.mlr.press/v54/malek17a.html). | Action-dependent KL allocation, adaptive sensing, likelihood-ratio stopping, sequential multiple testing, and removal of nonadaptive dimension penalties are established. | The columns of the information matrix are derived from legal old/new replay groups under one fairness-preserving heterogeneous null: matched controls have order-`d` information and boundary actions order-`d^2`. The upper result uses this control topology and explicit group costs. | **Scoped extension, potentially distinct subject to human literature sign-off.** Claim the replay-derived mixed information law/control-cover theorem. Do not claim invention of action-information LPs, matched controls, sequential testing, or generic removal of multiplicity penalties. |

## Adjacent fairness and software work

Yan and Zhang's fixed-model active demographic-parity audit
([ICML 2022](https://proceedings.mlr.press/v162/yan22c.html)) establishes that
query-efficient fairness auditing itself is prior art.  Ajarra and Basu study
property auditing after strategic updates.  Regression-test selection,
incremental verification, probabilistic program coupling, and fairness testing
are likewise established.  The defensible paper-level distinction is therefore
the explicit hierarchy of executable old/new transcript laws, fairness-null
families, and program-execution costs--not any one generic ingredient.

## Submission constraints produced by this audit

1. The abstract and contribution list may describe proved exponent separations,
   but must attach them to the exact replay oracle and null class.
2. `P12`, `P13`, `P14`, `P16`, and `P18` are not standalone broad novelty
   claims; they support the access-model hierarchy.
3. `P15`, `P17`, and `P19` are the most defensible scoped increments.  Even for
   them, the paper must say what is established machinery and what is derived
   from the software transcript.
4. The `P19` sequential/nonadaptive comparison cannot be described as the
   first removal of a multiplicity or dimension penalty.
5. No use of "first-ever," "unprecedented," or equivalent priority language is
   permitted without an independent human search and sign-off.
6. The checked literature does not establish a collision with the exact
   replay-derived `P17`/`P19` statements, but absence of a found collision is not
   proof of novelty.

## Residual reviewer risk

The strongest hostile reading is that the paper is a careful specialized
instantiation of paired inference and controlled sensing.  The manuscript must
answer that objection through the exact observation laws, opposing scope
counterexamples, and the mixed first-/second-order replay geometry.  If those
features are not viewed as a substantive theorem contribution after human
literature review, the honest fallback is to narrow the claim rather than add
experiments.
