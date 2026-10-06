# Theorem–algorithm–matrix crosswalk

This document connects the mathematical spine of TFOESUU to the executable
repository. It is a navigation and audit artifact, not an additional source of
theorem claims. The authoritative claim status remains docs/PROOF_STATUS.md.

## Core notation

- H=(V,E): counterfactual fairness graph.
- V_+: non-isolated fairness-active vertices.
- Psi(H,nu): Gaussian graph-allocation complexity.
- A: P17 edge-by-group witness-incidence matrix.
- B: P17 active-vertex/group information-incidence matrix.
- c: replay-group query-cost vector.
- beta or delta: target testing error.
- d: differential fairness effect in the homogeneous Bernoulli replay family.

## Theorem crosswalk

| ID | Mathematical object / statement | Algorithmic object | Main code | Audit state |
|---|---|---|---|---|
| P1 | Sound change-impact localization | Remove edges outside the sound impact closure | certificate.py / graph utilities | Proved + audited |
| P2 | No finite sharp-threshold certification without separation | Impossibility / no executable tester promised | proof only | Proved + audited |
| P3 | Paired-delta variance identity | Estimate patch delta under common randomness | oracles.py | Proved + audited |
| P4 | Gaussian static-allocation upper bound via Psi(H,nu) | Solve allocation and sample each active vertex | allocation.py, testers.py | Proved + audited |
| P5 | Adaptive Gaussian lower bound via the same Psi | Transcript-KL lower program | allocation.py + proof audit | Proved + audited |
| P6 | Lagrange dual representation of Psi | Primal/dual numerical agreement | allocation.py | Proved + audited |
| P7 | Exact Psi values for canonical graph families | Closed-form sanity fixtures | graphs.py, tests | Proved + audited |
| P8 | Homogeneous variance scaling of Psi | Rescaling sanity check | allocation.py | Proved + audited |
| P9 | Common-uniform Bernoulli delta variance d(1-d) | Coupled Bernoulli replay | oracles.py, separations.py | Proved + audited |
| P10 | Linear patch-locality separation on a matching | Patch-aware vs location-unaware allocation | separations.py | Proved + audited |
| P11 | Old slack alone gives no minimax speedup | Boundary-null adversary | proof only | Proved + audited |
| P12 | Paired replay d^-1 vs independent d^-2 | Replay-separation bound calculator | separations.py | Proved + audited |
| P13 | Unknown-location matching complexity Theta(M/d) | Location replay tester/bounds | separations.py | Proved + audited |
| P14 | Patch-effect envelopes prune safe edges | Residual graph construction | certificate.py | Proved + audited |
| P15 | Four-way replay cancels a common patch | Counterfactual replay tester/bounds | separations.py, counterfactual benchmark | Proved + audited |
| P16 | Synchronized suite replay removes edge-count dependence | Full active-suite shared-tape replay | suite_replay.py | Proved + audited |
| P17-U | Partial replay fractional witness-scheduling upper construction | Edge/group LP + deterministic rounding | partial_replay_lower.py | Upper bound proved; valid but generally nonmatching for the homogeneous raw-output oracle |
| P17-I | Raw-output necessary information floor | Active-vertex/group LP scaled by transcript KL | partial_replay_lower.py | Corrected/derived/tested; attained by P17-A in the frozen homogeneous family |
| P17-G | Structural relation between information and witness LP geometries | Deterministic equality/finite-gap/infinite-gap fixtures | partial_replay_lower.py + tests + structural specification data | LP geometry proved + tested; not a minimax result |
| P17-A | Active-vertex raw-contrast schedule in the frozen homogeneous single-endpoint family | Active-vertex LP + deterministic rounding + within-group patch-delta contrast | partial_replay_lower.py + tests | PROVED + AUDITED for frozen homogeneous family; broader composite-null extension open |
| P17-S | Scope counterexample for naive heterogeneous raw contrast | Heterogeneous fair-null deterministic witness | tests + partial_replay_scope_cases_v1.jsonl | Counterexample proved + tested; rules out silent generalization of P17-A |
| P17-M | Broader heterogeneous/composite-null partial-replay complexity | Open: needs controls/baseline adjustment/new geometry | none yet | Open |

## P17 matrix package

Let the legal replay groups be G={S_1,...,S_k}, each of size at least two.

### Matrix A — witness geometry

For e in E and group i,

  A[e,i] = 1{ e subset S_i }.

The fractional witness-cover LP is

  C_edge = min c^T a
           subject to A a >= 1,
                      a >= 0.

For

  L = ceil(log(beta)/log(1-d)),

the proved fixed schedule is

  n_i = ceil(L a_i*).

Each edge receives at least L independent legal four-way witness
opportunities. The total declared cost satisfies

  c^T n <= L C_edge + sum_{i:a_i*>0} c_i.

Executable correspondence:

- minimum_fractional_replay_cover
- fractional_replay_schedule
- experiments/search_partial_replay_gap.py

### Matrix B — information geometry

For x in V_+ and group i,

  B[x,i] = 1{ x in S_i }.

In the frozen homogeneous raw-output family,

  r = 1-p-s,
  K_sync = r log(r/(r-d)).

Every legal group containing the changed endpoint contributes K_sync
null-to-alternative KL, regardless of whether the other synchronized vertex is
the fairness partner.

Define

  C_vert = min c^T q
           subject to B q >= 1,
                      q >= 0.

The necessary transcript-information floor is

  Q_info = [kl(1-beta,beta)/K_sync] C_vert.

Executable correspondence:

- minimum_fractional_active_vertex_cover
- raw_output_information_lower_bound

### Relation

Every edge-cover feasible vector is active-vertex-cover feasible, so

  C_vert <= C_edge.

The edge-witness construction remains valid and gives

  [kl(1-beta,beta)/K_sync] C_vert
      <= Q*_hom
      <= L C_edge + rounding overhead.

For the frozen homogeneous single-changed-endpoint family, the audited
raw-contrast construction sharpens the upper side to the same active-vertex
geometry:

  [kl(1-beta,beta)/K_sync] C_vert
      <= Q*_hom
      <= L C_vert + raw-contrast rounding support cost.

This is a matching combinatorial/minimax-order characterization for the scoped
homogeneous family, not an exact finite-sample equality and not a theorem for
heterogeneous/composite fairness-preserving nulls.

The LP geometries themselves are now sharply separated.  Under coherent endpoint
group signatures their duplicate constraint rows coincide and C_vert=C_edge. For
K_n with legal groups equal to its unit-cost edges, C_vert=n/2 and
C_edge=n(n-1)/2, giving ratio n-1. For the path 0-1-2 with legal groups {0,2}
and {1,2}, C_vert=2 while the witness LP is infeasible. Thus no universal finite
factor compares C_edge to C_vert over the frozen oracle class. This separation
alone does not identify achievable testing complexity; P17-A supplies the
achievable C_vert construction only for the scoped homogeneous family.

## Algorithm A — fractional partial-replay witness scheduler

Input: H, legal groups G, costs c, effect d, confidence beta.

1. Construct A[e,i]=1{e subset S_i}.
2. Solve min c^T a subject to A a >= 1 and a >= 0.
3. Set L=ceil(log(beta)/log(1-d)).
4. Set n_i=ceil(L a_i*).
5. Query group S_i exactly n_i times using fresh tapes across queries.
6. Within each group query, share the tape across both program versions and all
   vertices in the group.
7. Reject on the first legal four-way fairness witness; otherwise accept.

Guarantee in the frozen homogeneous single-edge family: zero type-I error and
pointwise type-II error at most beta.

## Algorithm B — raw-information floor calculator

Input: H, legal groups G, costs c, p, shared patch s, effect d, confidence beta.

1. Construct V_+.
2. Construct B[x,i]=1{x in S_i}.
3. If an active vertex is absent from every legal group, report infeasible.
4. Solve C_vert=min c^T q subject to Bq>=1 and q>=0.
5. Compute K_sync=(1-p-s) log((1-p-s)/(1-p-s-d)).
6. Return [kl(1-beta,beta)/K_sync] C_vert and the correspondingly scaled query
   weights.
7. Report this value only as a necessary information floor.

## P17 adversarial test matrix

| Failure mode | Required check |
|---|---|
| Old invalid edge-only KL assumption | Withdrawn legacy lower-bound API fails closed |
| Illegal singleton replay group | Canonical group validation rejects it |
| Fairness partner incorrectly treated as special | Unrelated synchronized reference gives the same KL |
| Hidden oriented-edge dependence | Columns collapse by changed endpoint |
| Hidden edge-topology dependence in raw LP | Rewiring with fixed V_+ preserves the raw-information floor |
| Missing information channel | Active vertex absent from all groups makes the lower LP infeasible |
| Edge-vs-vertex geometry conflation | K4 triples exhibit C_vert=4/3 and C_edge=2 at unit group cost |
| Hidden finite-factor assumption | K_n pair groups verify C_vert=n/2 and C_edge=n(n-1)/2 for n=3,...,8 |
| Witness feasibility confused with information feasibility | Path-3 reference fixture verifies finite C_vert with infeasible C_edge |
| Equality condition regression | Group-coherent matching fixture verifies C_vert=C_edge |
| Fractional schedule rounding bug | Every edge receives at least L integer witness opportunities |
| Full 168-row stress-manifest drift | Every parameter row materializes and passes the LP/information/raw-contrast/rounding validator, including exact endpoint-wise miss probability <= beta |

## Specification-data correspondence

The checked-in data/partial_replay_benchmark_v1.jsonl manifest contains 168
deterministic specification rows spanning:

- clique, path, and matching graph families;
- legal group-size caps 2--4 where valid;
- two query-cost scales;
- d in {0.05, 0.02, 0.01};
- fixed interior p=0.20 and shared patch s=0.10;
- immutable row seeds.

These rows are theorem-falsification specifications, not empirical findings.
The generator is scripts/generate_partial_replay_benchmark.py. CI both regenerates
the manifest and executes every one of its 168 rows through
experiments/validate_partial_replay_manifest.py: canonical graph/group/cost
materialization, C_vert and C_edge feasibility, C_vert <= C_edge, raw-information
floor feasibility, C_vert raw-contrast correspondence, and the deterministic
rounding-cost bound.

## Promotion rule

Promotion of the scoped homogeneous P17 theorem is complete: proof audit,
executable correspondence, adversarial tests, the 168-row exact-risk validator,
prior-art fence, CI, paper build, and manuscript synchronization all passed.
Any broader heterogeneous/composite-null P17 theorem must independently pass the
same gates before entering the abstract or contribution list.


## P17 structural specification data

`data/partial_replay_structural_cases_v1.jsonl` is a deterministic
8-row theorem-fixture manifest separate from the 168-row P17 parameter stress
grid.  It records the exact expected LP values for coherent equality, the
K_n pair-group finite-gap family for n=3,...,8, and the
finite-information/infeasible-witness path case.  These rows are mathematical
specifications, not empirical measurements.

## Algorithm C — active-vertex raw-contrast scheduler

Scope: frozen homogeneous threshold family only. Every replay-eligible vertex
has old threshold p and null-new threshold p+s; one active endpoint may instead
have p+s+d.

1. Solve C_vert=min c^T q subject to Bq>=1 and q>=0.
2. Set L=ceil(log(beta)/log(1-d)).
3. Set n_i=ceil(L q_i*).
4. Query each legal group S_i exactly n_i times with a fresh shared tape per query.
5. In each query compute D_v=P1(v;U)-P0(v;U) for every group member.
6. Reject if the within-group D_v vector is nonconstant; otherwise continue.

Under the homogeneous null every D_v is identical pathwise, so type-I error is
zero. Under a single-changed-endpoint alternative x, every query containing x
produces a contrast with probability d. Active-vertex exposure is at least L,
so the pointwise miss probability is at most beta. The declared cost is at most

  L C_vert + sum_{i:q_i*>0} c_i.

This audited construction matches the lower program's combinatorial geometry in
the frozen family. It is not a theorem for arbitrary heterogeneous
fairness-preserving nulls.
