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

See docs/PROOF_STATUS.md and docs/PROOF_AUDIT_P17_FRACTIONAL_REPLAY.md for exact audit status.

## Immediate theorem queue

### A. P18 nuisance-aware replay information geometry
The next theorem target is the graph-level composite-null problem frozen in
`docs/PROOF_ATTACK_P18_INFORMATION_GEOMETRY.md`. It must not duplicate P15's
one-edge common-patch separation or P17's homogeneous active-vertex theorem.
Derive exact action-by-alternative information under legal replay semantics,
then determine whether a matching lower/upper information-cover
characterization exists. See S1 below for the full promotion and failure-mode
checklist.

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

### S1 — P18 nuisance-aware replay information geometry (highest priority)

Do **not** duplicate P15. P15 already proves the one-edge nonzero-common-patch
separation between vertex-paired and four-way replay. Do **not** relabel the
audited homogeneous P17 theorem as a new result either.

The next non-overlapping target is graph-level and nuisance-aware:

1. freeze a composite class of fairness-preserving patch nuisances;
2. derive the exact observation law for every legal replay action and every
   oriented violating alternative;
3. construct the resulting action-by-alternative information matrix;
4. determine whether the minimum-cost information cover gives a valid adaptive
   lower bound and whether a matching allocation/test can attain it;
5. recover P15 and the homogeneous P17 geometry as special cases;
6. search for a genuine phase transition in which endpoint-containing co-replay
   is first-order informative in d while nuisance-contaminated separated replay
   is only second-order informative;
7. explicitly test whether nuisance learning or adaptation defeats any naive
   C_edge/d characterization.

The implementation in `src/tfoesuu/replay_information.py` is only a generic LP
scaffold. It is not theorem evidence. The proof attack and failure modes are
frozen in `docs/PROOF_ATTACK_P18_INFORMATION_GEOMETRY.md`.

A successful result may be a positive characterization, a phase-transition
theorem, or a clean impossibility theorem showing that no single unweighted cover
captures the composite-null problem.

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
null lower bound contains log(1/delta). Determine whether log|E| is:

- removable by a sharper correlated simultaneous test;
- necessary on an explicit graph/alternative family; or
- replaceable by a structural complexity smaller than |E|.

Do not hide the gap behind big-O notation.

### S5 — Replay feasibility and software semantics

Formalize which software randomness is controllable:

- seeded pseudorandomness;
- deterministic record/replay;
- partially replayable groups;
- external or non-replayable nondeterminism.

Connect these categories to the oracle hierarchy. The theory should expose the
price of weaker replay rather than assume universal synchronization.

### S6 — Final archival collision audit

Before strengthening abstract/contribution language, collision-check P15--P17
against peer-reviewed work on controlled sensing, active hypothesis testing,
restricted group testing, combinatorial pure exploration, graph-constrained
experimental design, fractional covering/sampling designs, CRN ranking and
selection, and stochastic monitoring. Fractional cover, CRN, coupling, and
subset queries are established ingredients and must never be claimed novel.

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

