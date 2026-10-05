# P17 — partial synchronized replay

**Status: FRACTIONAL WITNESS-SCHEDULING UPPER BOUND PROVED; RAW-OUTPUT MATCHING LOWER BOUND WITHDRAWN; MINIMAX CHARACTERIZATION OPEN. Do not promote P17 to the abstract or theorem list as a matching result.**

## Frozen oracle

Let H=(V,E) be the fairness graph and let S be a declared family of legal replay
groups. A query chooses one legal group S, draws one random tape U, and executes
both P0 and P1 on every vertex in S using that same tape. Different group queries
use independent tapes.

There are two distinct observation notions and they must not be conflated.

1. **Four-way fairness witness.** For edge e=(u,v), P15's pathwise witness requires
   both u and v in the same replay group.
2. **Raw-output information.** A group containing a perturbed endpoint can have a
   changed raw-output law even when it omits that endpoint's fairness partner.

The earlier P17 lower-bound attempt incorrectly treated (1) as if it implied zero
raw-output KL in case (2). That matching lower bound is withdrawn.

## Proved fixed-design upper bound

For legal groups S with costs c(S)>0, solve the fractional edge-by-group cover

  minimize    sum_S c(S) a_S
  subject to  sum_{S: e subset S} a_S >= 1  for every e in E,
              a_S >= 0.

Let C_frac be its optimum and choose

  L = ceil(log(beta) / log(1-d)),
  n_S = ceil(L a_S).

Every fairness edge then receives at least L independent legal four-way witness
opportunities. In the frozen homogeneous single-edge witness family, each such
opportunity misses the sparse witness with probability 1-d. Therefore the
fixed-design tester has zero type-I error and pointwise type-II error at most
beta, with declared cost

  sum_S c(S) n_S
    <= L C_frac + sum_{S: a_S>0} c(S).

This is the current theorem-level P17 statement. It is an upper bound only.

## Correct raw-output information lower program

Alternatives are oriented fairness edges (u,v;x), where x is the endpoint that
receives the additional differential shift d. Let

  B_beta = kl(1-beta,beta).

For a legal group S define the exact null-to-alternative raw-output KL K_{S,a}.
Any uniformly valid tester must satisfy the transcript change-of-measure
constraints

  sum_S E_0[N_S] K_{S,a} >= B_beta

for every oriented alternative a. Hence a necessary expected-cost floor is

  minimize    sum_S c(S) q_S
  subject to  sum_S q_S K_{S,a} >= B_beta  for every a,
              q_S >= 0.

For the frozen homogeneous family, write s for the shared-patch mass and
r=1-p-s. The implementation uses

  K_single
    = s log(s/(s+d)) + r log(r/(r-d))

when S is the singleton changed endpoint, and

  K_sync
    = r log(r/(r-d))

when S contains the changed endpoint and at least one additional unchanged
synchronized vertex. Groups omitting the changed endpoint have zero KL.

The synchronized reference need not be the fairness partner. This is the key
reason the old edge-incidence lower bound is invalid.

## Exact structural reduction

For fixed changed endpoint x, every oriented edge alternative incident to x has
the same information column. Thus the nominal 2|E| information constraints
collapse to one constraint for each non-isolated fairness vertex x in V+:

  K_single q_{ {x} }
    + K_sync sum_{S: x in S, |S|>=2} q_S
    >= B_beta.

Consequently, in this frozen homogeneous family the raw-information floor sees
the fairness graph only through its active vertex set V+. Rewiring edges while
holding V+ and the legal replay groups/costs fixed leaves this lower LP
unchanged. The four-way witness upper bound can still change because it depends
on edge/group incidence.

This exposes two different geometries:

  raw-information floor          -> vertex/group incidence
  certified four-way upper bound -> edge/group incidence.

Whether their gap is fundamental, or whether a different uniformly valid tester
attains the information floor, is open.

## Information amplification

The exact difference is

  K_sync - K_single = s log(1+d/s) > 0.

For d -> 0,

  K_single
    = (d^2/2)(1/s + 1/r) + O(d^3),

while

  K_sync
    = d + d^2/(2r) + O(d^3).

Thus singleton endpoint observations carry Theta(d^2) information per query,
whereas synchronizing the changed endpoint with any unchanged reference carries
Theta(d) information. This is an information statement, not yet a matching
minimax theorem.

## Boundary checks

- If a fairness edge is contained in no legal group, the P15 four-way witness
  scheduler cannot certify that edge through the proved upper construction.
- Raw-output testing can nevertheless have positive information about an
  oriented alternative if legal groups contain its changed endpoint.
- If some oriented alternative's changed endpoint appears in no legal group,
  the raw-information LP is infeasible.
- If V+ itself is one legal group, one synchronized group supplies joint
  information for every active endpoint and a legal four-way witness for every
  fairness edge.
- The K4 triple fixture retains the strict fractional-vs-integral witness-cover
  gap: fractional cost 2 versus integral cost 3 at unit group costs.

## Implementation guardrails

- minimum_fractional_replay_cover and fractional_replay_schedule are
  witness-scheduling objects.
- fractional_group_replay_lower_bound is withdrawn for the raw-output oracle and
  intentionally fails closed so old scripts cannot silently report the invalid
  quantity.
- raw_output_information_lower_bound implements the necessary raw-output
  transcript-KL allocation floor.
- Adversarial tests must cover singleton-vs-synchronized KL, unrelated reference
  equivalence, unobservable oriented alternatives, active-vertex column
  collapse, and edge-rewiring invariance.

## Promotion gates

P17 must not be promoted to a matching theorem until all of the following pass:

1. corrected implementation and adversarial tests are green;
2. the KL matrix and active-vertex reduction are independently re-derived;
3. the lower program is clearly labeled necessary, not automatically attainable;
4. a uniformly valid tester matching the information floor is proved, or a
   rigorous separation is proved instead;
5. nearest prior-art collision search is refreshed;
6. manuscript, proof ledger, notes, references, reproducibility artifacts, and
   generated paper are mutually consistent.

## Collision boundary

Common random numbers, coupling, subset/group querying, fractional set cover, and
information-allocation LPs are established prior art. Any eventual novelty claim
must concern the precise evolving-software fairness-regression replay oracle and
a proved complexity statement. No novelty claim should be based merely on using
CRN, fractional covers, or KL allocation.
