# P17 partial synchronized replay — proof audit

**Status: CORRECTION IN PROGRESS. The fractional replay-cover construction is a
proved fixed-design upper bound in the frozen homogeneous witness model. The
previous matching fractional-cover lower bound is withdrawn for the raw-output
oracle. Do not promote P17 to the abstract or theorem list until the raw-output
lower bound and attainability gap pass independent audit.**

## Frozen oracle

Let H=(V,E) be the fairness graph and let G={S_1,...,S_k} be the legal replay
groups. A query to S_i draws a fresh tape U and executes both software versions
on every v in S_i with that tape. Different queries use independent tapes.

For the P15 four-way *witness*, an edge e=(u,v) is witnessed only by a query
containing both u and v. This edge-incidence condition is sufficient for the
zero-type-I construction below. It is **not** a statement that raw observations
from other groups have zero information about an alternative.

## Proved fractional scheduling upper bound

Let c_i>0 and define

  C_frac = min sum_i c_i a_i
           s.t. sum_{i: e subset S_i} a_i >= 1 for every e,
                a_i >= 0.

Let

  L = ceil(log(beta)/log(1-d)),
  n_i = ceil(L a_i*),

for an optimal fractional cover a*. Query group i exactly n_i times and reject
when any legal within-group four-way witness appears. Under H0 the witness is
pathwise impossible. Under any frozen single-edge alternative e,

  sum_{i: e subset S_i} n_i >= L,

so independent misses have probability at most (1-d)^L <= beta. The declared
cost obeys

  sum_i c_i n_i <= L C_frac + sum_{i: a_i*>0} c_i.

This upper bound survives the correction.

## Withdrawal of the old matching lower bound

The earlier audit asserted that, for edge alternative e=(u,v), only groups
containing both u and v have changed observation law. That premise is false for
the **raw-output oracle**. A group containing the changed endpoint can carry KL
information even when it omits the fairness partner. Therefore the old step

  K(d) sum_{i: e subset S_i} E_0[N_i] >= kl(1-beta,beta)

is not a valid transcript-KL characterization of the raw oracle, and the claimed
sandwich

  C_frac kl(1-beta,beta)/K(d) <= Q* <= ...

is withdrawn. No minimax equality or Theta(C_frac/d) theorem is currently
certified for P17.

## Correct raw-output information lower program

Index alternatives by oriented fairness edges a=(u,v,x), where x in {u,v} is
the changed endpoint. In the homogeneous threshold family set

  r = 1-p-s,
  K_joint = r log(r/(r-d)),
  K_single = s log(s/(s+d)) + r log(r/(r-d)).

For a legal group S,

  K_{S,a} = 0          if x notin S,
            K_single   if S={x},
            K_joint    if x in S and |S|>=2.

The second vertex in the final case need not be the fairness partner. Transcript
change of measure therefore yields the necessary allocation program

  minimize   sum_S c(S) q_S
  subject to sum_S q_S K_{S,a} >= kl(1-beta,beta)  for every a,
             q_S >= 0.

This is implemented by raw_output_information_lower_bound(). It is a necessary
information floor; the repository does not claim that it is attainable.

### Constraint reduction

For the frozen homogeneous family, K_{S,a} depends on an oriented alternative
only through its changed endpoint x. Thus alternatives sharing x produce
identical information columns. The 2|E| constraints reduce exactly to one
constraint per non-isolated fairness vertex x:

  K_single q_{ {x} }
  + K_joint sum_{S contains x, |S|>=2} q_S
  >= kl(1-beta,beta).

This is an algebraic reduction of the lower program, not a new minimax theorem.
It also shows why the raw-information geometry is vertex/group incidence while
the certified witness upper construction is edge/group incidence.

## Exact information separation

For d>0 in the valid interior parameter range,

  K_joint - K_single = s log(1+d/s) > 0.

As d -> 0 with p,s,r fixed,

  K_single = (d^2/2)(1/s + 1/r) + O(d^3),
  K_joint  = d + d^2/(2r) + O(d^3).

Hence singleton raw observations are second-order in d, while synchronizing the
changed endpoint with any unchanged reference produces first-order information.
This does not by itself prove an achievable tester at the information-LP cost.

## Promotion gates

P17 stays out of the manuscript theorem list until all of the following pass:

1. adversarial unit tests independently verify the raw KL cases;
2. an independent derivation checks the group laws and transcript-KL direction;
3. the active-vertex constraint reduction is tested against edge rewiring;
4. the attainability/adaptivity gap between the raw-information floor and
   edge-witness schedule is resolved or stated as a proved separation;
5. literature collision review is refreshed;
6. paper and proof-status text are synchronized and the complete CI/paper build
   is green.

## Novelty fence

Fractional cover, common random numbers, coupling, change of measure, and subset
queries are prior art. Any eventual claim must be restricted to a proved
complexity statement for this software-version/fairness-regression replay oracle.
