# STOC 2027 theorem/novelty matrix — 2026-10-15

Status: automated adversarial literature audit. **Human theorem-by-theorem
originality sign-off remains mandatory.** “Not located” is not proof of
priority.

| Our claim | Complete assumptions | Oracle / transcript | Cost model | Precise cited old theorem or mechanism | Implication / non-implication | New statement retained | Overlap risk | Evidence link | Human auditor verdict |
|---|---|---|---|---|---|---|---|---|---|
| P12 one-edge replay | Interior common-uniform Bernoulli threshold family; known `d`; simple paired null/alternative | Raw old/new pair under one tape, versus fresh independent samples | Two executions per vertex-paired round | Connor's matched proportions and McNemar-type discordance; Glasserman--Yao CRN | Classical pairing explains rare discordance, but does not state the exact versioned-program oracle comparison and concrete cost | Exact software-access separation `d^-1` versus `d^-2` in the frozen family | High | `HOSTILE_NOVELTY_AUDIT_P12_P19.md`; DOI `10.2307/2531961` | Pending |
| P13 unknown changed matching edge | Common null; exactly one changed edge among `M`; fixed confidence | Per-edge raw replay | Concrete executions from queried edges | Cohen--Zhao anomaly testing; Malloy--Nowak sparse sequential recovery | Prior work supplies search/information machinery; no direct versioned fairness-edge statement | Software-replay specialization and cost translation | High | DOI `10.1109/TIT.2014.2387857`; DOI `10.1109/TIT.2014.2363846` | Pending |
| P14 certificate pruning | Sound change-impact and deterministic effect envelopes | No stochastic query for certified-safe edges; declared residual oracle | Zero for pruned edges, theorem cost on residual graph | Regression-test selection and deterministic change-impact analysis | Standard pruning does not prove the fairness identity connecting envelope and residual test | Sound deterministic/stochastic interface | High; not marketed as novelty | `docs/THEOREM_ALGORITHM_MATRIX.md` | Pending |
| P15 four-way nuisance cancellation | One edge; common-uniform tape across both versions/endpoints; common shift; one endpoint gets extra `d` | Ordered four-output transcript | Four executions per round | Glasserman--Yao CRN; classical paired inference and KL change of measure | CRN implies coupling is established; precise executable transcript and access comparison are specialized | Scoped four-way software-replay separation | Medium-high | DOI `10.1287/mnsc.38.6.884`; manuscript theorem | Pending |
| P16 suite replay | Homogeneous one-changed-endpoint family; one tape across full active suite | Entire raw old/new suite vector | `2 n_+` executions per round | CRN multiple comparisons and group testing/property testing | Edge-count-free rounds do not imply edge-count-free execution cost | Exact round/execution separation for the suite oracle | High | Claim ledger P16 and suite tests | Pending |
| P17 edge/vertex covers | Legal groups of at least two vertices; homogeneous singleton change for achievability; heterogeneous counterexample outside scope | Ordered raw group transcript | Declared `c(S)`, or `2|S|` executions when instantiated | Classical fractional covering; Singh--Singh--Davidov graph design | Classical LP theory does not identify the two transcript-dependent incidence matrices or their scope mismatch | `C_edge` versus `C_vert` replay geometry, attainability fence, unbounded gaps | Medium | DOI `10.1111/sjos.12757`; 168+8+1 fixtures | Pending |
| P18 tolerance phase | One synchronized edge; interior thresholds; tolerance `tau`; gap increment `d` | Ordered four-output threshold transcript | Four executions per round | Bernoulli testing, exact KL, tolerant-testing analogies | Classical KL gives the calculation; not a universal phase diagram | Exact replay-specific transition from first- to second-order information | High | P18 proof and 24-row exact grid | Pending |
| P19 mixed control topology | Equal-high two-class simple null; declared matched controls; singleton alternatives; fresh tapes | Legal group raw transcripts with first-order control and second-order boundary channels | Positive group costs; explicit conversion to concrete executions | Nitinawarat--Atia--Veeravalli controlled sensing; Naghshvar--Javidi active sequential testing; Deshmukh--Veeravalli--Bhashyam composite sensing; Malek et al. and Malloy--Nowak sequential dimension effects | Prior theory contains action-KL allocation and adaptive stopping. It does not directly derive the first-/second-order information matrix from legal old/new software replay | Scoped mixed information law, cover geometry, and matching-order hybrid under exact null/alternative | Medium; strongest candidate contribution | DOI `10.1109/TAC.2013.2261188`; DOI `10.1214/13-AOS1144`; DOI `10.1080/07474946.2021.1912525`; P19 audits | Pending |
| N1 exactly shared unknown threshold | `0<p<h<h+d<1`; nuisance shared exactly across endpoints; known `d`; independent rounds | Ordered four-way common-tape transcript | Four executions per round | Glasserman--Yao CRN; standard stopped-KL/Wald argument | The nuisance is annihilated pathwise rather than statistically estimated; this is not composite controlled sensing | Uniform nuisance-invariant witness plus pointwise null-side converse | Very high; elementary corollary | `STOC2027_P19_COMPOSITE_NUISANCE_PROOF_AUDIT_20261015.md` | Pending |
| N2 equal-mean obstruction | `0<p<p+eta<p+s<p+s+eta<1`; fair old/new gaps `eta<=tau` | Same four-output tape transcript | Four executions per round | Elementary coupling/symmetric-difference calculation | Equal expected effects do not determine the coupling; no general impossibility follows | Exact false-witness probability `2 eta` and scope counterexample | Very high; fence, not novelty | Same proof audit; nine exact tests | Pending |
| N3 uncalibrated marginal overlap | Candidate-only Bernoulli channel; nuisance interval width at least `d`; valid probabilities | One marginal output, no matched control | Any number of samples | Elementary Le Cam/hypothesis-set intersection | Identical induced distributions preclude testing, but richer matched transcripts can separate | Explicit reduced-channel nonidentifiability fence | Complete overlap with standard identifiability logic | Same proof audit | Pending |
| P20 general nuisance/action geometry | Globally consistent nuisance; action-dependent exact laws; adaptive action counts may depend on nuisance | General declared replay actions | Positive action/group costs | Deshmukh--Veeravalli--Bhashyam composite controlled sensing and later controlled-sensing work | Pointwise nuisance LP and one shared fixed allocation do not commute; current abstract LP is not achievability | No theorem promoted; open realizability/achievability question | Critical | `docs/P20_NUISANCE_QUANTIFIER_AUDIT.md` | Pending |

## Primary-source boundary checked on 2026-10-15

- Glasserman and Yao, *Management Science* 38(6):884--908 (1992), DOI
  `10.1287/mnsc.38.6.884`: CRN comparison is established prior art.
- Nitinawarat, Atia and Veeravalli, *IEEE Transactions on Automatic Control*
  (2013), DOI `10.1109/TAC.2013.2261188`: fixed and sequential controlled
  sensing, causal/open-loop distinctions, and asymptotic testing policies are
  prior art.
- Naghshvar and Javidi, *Annals of Statistics* (2013), DOI
  `10.1214/13-AOS1144`: active sequential hypothesis testing and information
  acquisition are prior art.
- Deshmukh, Veeravalli and Bhashyam, *Sequential Analysis* 40(2):259--289
  (2021), DOI `10.1080/07474946.2021.1912525`: controlled sensing with
  composite hypotheses and unknown parameters is prior art.
- Malek et al., AISTATS 2017, and Malloy--Nowak 2014 establish adaptive
  sequential allocation/dimension effects; generic removal of a multiplicity
  penalty is not claimed here.
- Fairlearn issue 728 and merged PR 763 document the 2021 protected-group bug;
  the seven-population census is a reproduction, not a new defect discovery.

## Release rule

The manuscript may call P17/P19 “scoped replay-derived extensions” only with
their complete oracle, null, alternative and cost qualifiers. N1--N3 are
parameter-invariant consequences and counterexamples, not headline novelty.
P20 remains open. Any stronger wording is a release blocker.
