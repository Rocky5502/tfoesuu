# Research roadmap

The project is theory-first. GPU computation attacks conjectures and constants; it never substitutes for proof.

## Frozen validated spine

P1-P3 establish localization, the need for a statistical margin, and paired-delta variance.
P4-P8 establish the Gaussian graph-allocation core around Psi(H,nu).
P9-P12 establish the Bernoulli replay mechanism and the one-edge linear-vs-quadratic small-patch separation.
P13 combines unknown patch location with replay on a matching: fixed-confidence cost scales as Theta(M log(1/delta)/d).
P14 shows how sound static patch-effect envelopes prune fairness edges with zero new executions.
P15 shows that four-way replay across both versions and both counterfactual endpoints cancels a nonzero common patch effect and changes differential-gap complexity from Theta(d^-2) to Theta(d^-1).
P16 lifts synchronized replay to the full active fairness suite: round complexity is independent of edge count and concrete execution complexity is Theta(n_active log(1/delta)/d) in the audited homogeneous Bernoulli family.
P17 has a corrected two-matrix formulation for partial synchronized replay. The LP geometries are structurally separated by exact fixtures, and an audited raw-output contrast construction attains the active-vertex C_vert geometry in the frozen homogeneous single-changed-endpoint family. Broader heterogeneous/composite-null partial replay remains open.
P18 characterizes the one-edge thresholded composite-null boundary: synchronized replay costs Theta((tau+d)d^-2 log(1/delta)), so tau=O(d) retains the linear d^-1 regime while any fixed positive tolerance restores d^-2 scaling.
P19 identifies matched-background replay controls as a sufficient heterogeneous extension: an exact mixed-information LP separates Theta(d) control-compatible queries from Theta(d^2) boundary-only queries, and a fractional control cover C_ctrl restores the linear regime in the two-class bipartite family.

See docs/PROOF_STATUS.md and docs/PROOF_AUDIT_P17_FRACTIONAL_REPLAY.md for exact audit status.

## Immediate theorem queue

### A. Partial synchronized replay: extend beyond the solved two-class control family
The intermediate access model is now frozen. Legal replay groups have size at least two and may have heterogeneous costs. The proved fixed-design upper construction is governed by the edge-by-group fractional cover

  C_edge = min c^T a  subject to A a >= 1, a >= 0,

while raw transcript change-of-measure reduces exactly to the active-vertex/group cover

  C_vert = min c^T q  subject to B q >= 1, q >= 0.

The corrected lower floor is [kl(1-beta,beta)/K_sync] C_vert. The audited active-vertex raw-contrast theorem uses q* from the same LP, L=ceil(log(beta)/log(1-d)), and n_i=ceil(L q_i*) to obtain zero type-I error and pointwise type-II error at most beta in the frozen homogeneous family, at cost at most L C_vert plus rounding support cost.

A deterministic heterogeneous-null counterexample closes off the naive
generalization route: for tau=0.20, old thresholds (0.20,0.40), new thresholds
(0.30,0.45), and U=0.25, the new program remains fair (gap 0.15) while the raw
patch-delta contrast fires. P18 resolves the one-edge thresholded analogue. P19 then shows that declared
matched-background controls can restore first-order information and linear
small-effect scaling in a bipartite two-class heterogeneous null. The remaining
target is arbitrary heterogeneous/composite nulls with multiple background
levels, imperfect control classes, or unknown control membership.

Keep the raw-contrast claim explicitly scoped to the homogeneous single-changed-endpoint family until a broader composite-null theorem passes its own proof/audit gates.

### B. Retained certificate headroom
Old-version slack cannot improve unrestricted minimax complexity by itself (P11). Seek an instance-dependent theorem where patch restrictions and certified headroom interact nontrivially.

### C. Unknown variance and sequential validity
Replace known Gaussian delta variances with confidence sequences or another anytime-valid construction. Every stopping rule must be audited for optional-stopping validity.

### D. Imperfect impact analysis
Separate two models: sound-but-imprecise impact sets, and explicitly probabilistic unsoundness with sentinel checks. Never blur them.

### E. Multi-version amortization
Study P0 -> P1 -> ... -> PT with reusable certificates. Target a dynamic complexity depending on cumulative changed structure rather than T times a fresh audit.

## Experiment queue

1. Run all CPU CI and theorem checks.
2. Materialize deterministic Gaussian, replay, counterfactual, and partial-replay benchmark manifests.
3. Run 10^4-trial single-GPU smoke tests.
4. Stress the replay exponent at shrinking d.
5. Search heterogeneous variance profiles and partial-replay group families for counterexamples to broader composite-null graph formulas and candidate extensions beyond the audited homogeneous C_vert theorem.
6. Only after theorem freeze, run 10^6-10^7 publication sweeps on both GPUs.

## Paper gate

A contribution enters the abstract only when it is PROVED + AUDITED in docs/PROOF_STATUS.md. Computationally checked observations remain labeled empirical.

## STOC-strengthening sprint: highest-value open weaknesses

This sprint is deliberately narrow. Do not add new RQs, arbitrary datasets, or
headline claims until these items are resolved or explicitly bounded.

### S1 — Beyond the solved P19 matched-control family (highest priority)

P17 remains homogeneous, while P18 and P19 now establish two rigorous boundaries:
fixed positive tolerance without a sparse control channel is quadratic, and a
declared matched-background control can restore first-order information in the
two-class bipartite family. The next target is strictly broader:

1. characterize multiple background levels and partially overlapping control classes;
2. quantify imperfect or unknown control membership rather than assuming it;
3. derive the corresponding mixed-information geometry or an impossibility result;
4. state all quantifiers over legal replay groups, orientations, costs, and nuisance
   parameters explicitly and add counterexamples before promotion.

A rigorous impossibility/boundary theorem remains a successful outcome.

### S1b — Mixed-control asymptotic stratification (finite-topology orders resolved)

Keep the broader nuisance-aware minimax claim at P20-CONJECTURE status; the P19
hybrid does not promote it. P19's exact lower LP implies a sharper question than
the binary all-controls/no-controls split. In a partially
controlled topology, some alternatives have a first-order control-compatible
channel while others are observable only through the second-order boundary
channel.  For fixed positive tau,

  K_ctrl(d) = Theta(d),    K_bnd(tau,d) = Theta(d^2).

The exact finite P19 information lower program now has a proved two-term
expansion. Boundary-only alternatives determine the d^-2 coefficient; boundary
KL curvature and the residual control cover determine the d^-1 coefficient.
A group containing an unmatched high candidate cannot contain another high
candidate, so the previously suspected cross-coverage interaction is impossible
in this model. If every candidate is control-covered, the leading regime
collapses to P19's d^-1 control-cover geometry. If even one observable candidate
lacks every control-compatible group, the information floor retains a d^-2
leading term.

Repository falsification support:
- experiments/search_control_replay_mixed_geometry.py enumerates small legal
  pair-group families and measures exact LP scaling under d -> d/2;
- tests pin one mixed topology to the quadratic leading regime and an
  all-covered topology to the linear leading regime.

Completed: exact lower-program d^-2 and d^-1 coefficients plus a hybrid upper
that matches the finite-topology d-orders and boundary-minimum/residual-cover
geometry up to constants. Tests cover positive/zero/negative boundary curvature,
multiple unmatched candidates, unobservable extremes, and a composite-null
counterexample. Remaining: exact two-term minimax constants and `|U|` dependence.


### S1c — P20 unified replay information geometry (conjecture)

P18 and P19 establish two scoped phase-transition/control results. P20 asks
whether a single graph-level action-by-alternative information geometry can
characterize the broader nuisance-aware problem without relabeling those scoped
theorems as generic controlled sensing.

The candidate program is

  minimize    sum_S c(S) x_S
  subject to  sum_S I[a,S] x_S >= K_a   for every active alternative a,
              x_S >= 0.

The matrix I must be derived from exact replay semantics and the frozen nuisance
class. A composite null has one globally fixed nuisance value per experiment:
an adaptive policy may have different expected action counts under different
nulls. Do not replace the valid necessary floor
  sup_eta min_x {c^T x : I(eta)^T x >= K}
by the generally larger shared-fixed-allocation program
  min_x {c^T x : I(eta)^T x >= K for every eta}.
The latter is a fixed-information design objective, not an adaptive minimax
lower bound or a finite-sample achievability certificate. See
`docs/P20_NUISANCE_QUANTIFIER_AUDIT.md` and the exact finite fixtures in
`tests/test_nuisance_information.py`. The generic solver in `src/tfoesuu/replay_information.py` is only an
implementation scaffold. Promotion requires an adaptive lower bound, a matching
attainable procedure, counterexamples outside scope, and a fresh archival
collision audit.

See `docs/PROOF_ATTACK_P20_INFORMATION_GEOMETRY.md`.

### S2 — Full thresholded fairness with retained certificate headroom

Bridge the gap between patch-neutrality tests and the motivating thresholded
fairness-regression question. Seek an instance-dependent characterization using
old edge slack/headroom plus sound patch envelopes. P11 and P14 are boundary
results; the missing target is a tight or near-tight statistical complexity
statement after deterministic pruning.

### S3 — Formal replay-oracle hierarchy

Define comparable access models for fresh sampling, vertex-paired old/new replay,
four-way edge replay, legal partial group replay, and synchronized full-suite
replay. Prove strict separations only where the cost units and information
available to each oracle are matched fairly. Separate replay rounds, group-query
cost, and concrete program executions.

### S4 — Close or explain the Gaussian logarithmic gap

P4 has a simultaneous-testing factor log(|E|/delta), whereas the current adaptive
null lower bound contains log(1/delta). The first archival collision audit is
complete: generic adaptive elimination of dimension penalties is established in
sequential sparse testing (see docs/GAUSSIAN_LOG_GAP_DISCOVERY.md and
Malloy--Nowak 2014). Therefore a TFOESUU result must use the shared-vertex graph
structure rather than merely rediscover sequential thresholding.

Determine whether the extra logarithm is:

- removable by an adaptive graph-filtering scheme whose expected cost is
  controlled by Psi(H,nu);
- necessary on an explicit graph/variance family even with adaptive vertex
  sampling; or
- replaceable by a structural complexity smaller than |E|.

Keep expected null cost, worst-case alternative cost, fixed-design cost, replay
rounds, and concrete executions separate. Do not hide the gap behind big-O
notation.

### S5 — Replay feasibility and software semantics

Formalize which software randomness is controllable:

- seeded pseudorandomness;
- deterministic record/replay;
- partially replayable groups;
- external or non-replayable nondeterminism.

Connect these categories to the oracle hierarchy. The theory should expose the
price of weaker replay rather than assume universal synchronization.

The next executable-subject candidate is preregistered in
`docs/THEMIS_EXECUTABLE_V2_PREREGISTRATION.md`.  It targets genuine protected-
input mutation and measured subprocess cost; it must remain separate from the
synthetic-endpoint public v1 matrix and cannot become replay-theorem evidence
without auditable random-tape control.

### S6 — Final archival collision audit

Before strengthening abstract/contribution language, collision-check P15--P17
against peer-reviewed work on controlled sensing, active hypothesis testing,
restricted group testing, combinatorial pure exploration, graph-constrained
experimental design, fractional covering/sampling designs, CRN ranking and
selection, and stochastic monitoring. Fractional cover, CRN, coupling, and
subset queries are established ingredients and must never be claimed novel.

### S5b — Replay phase-transition benchmark contract

Before GPU execution, maintain a deterministic phase-grid specification rather
than adding public datasets for count.  The grid varies d and tau/d for P18 and
uses only the theorem-backed P19 control-coverage extremes rho=0 and rho=1.
The mixed-control singular LP now has proved two-term coefficients, but an
intermediate scalar coverage fraction does not identify the replay topology,
costs, or coefficients. The hybrid upper also requires that explicit topology
and does not close exact constants. Mixed fixtures therefore remain in the
topology search rather than a misleading rho-only sweep. The v1 specification lives in
`src/tfoesuu/replay_phase_benchmarks.py` and is guarded against accidental
claim expansion by `tests/test_replay_phase_benchmarks.py`.

The apparent familywise `log |U|` gap is now split by design class: exact
chi-square mixtures prove it necessary for nonadaptive fixed boundary
allocations, while a two-sided sequential LR construction removes the
multiplicative log from expected null cost. Exact adaptive constants and
bounded-horizon adaptive allocation remain research targets.

Replay fidelity is recorded as a field but is frozen at 1.0 in v1.  No theorem
currently supports a partial-fidelity exponent, so gamma-like replay-quality
sweeps must not be interpreted as predicted phase transitions until a formal
access model exists.

### S7 — Compact theorem-validation experiments

Keep experiments subordinate to proofs. Validate predicted scaling and structural
ratios with deterministic manifests and executable stochastic subjects:

- d^-2 versus d^-1 small-effect scaling;
- edgewise four-way versus synchronized-suite execution cost;
- exact P17 structural fixtures and integrality gaps;
- heterogeneous-null counterexamples;
- Gaussian Psi scaling and any resolution of the log|E| question.

Do not add public datasets merely to increase a dataset count.

### Promotion gate

A new headline claim enters the abstract only after:
PROVED -> independent second derivation -> adversarial finite checks -> archival
collision audit -> code/test synchronization -> green CI and paper build.
