# Proof Attack: Is the Gaussian log |E| Factor Necessary?

Status: **OPEN PROOF ATTACK / NOT A THEOREM**

The audited Gaussian core currently has an upper bound with
`log(|E|/delta)` and an adaptive null lower bound with `log(1/delta)`. This
note freezes a candidate multiplicity lower-bound route without promoting it.

## 1. Candidate hard family

Take a star with center 0 and m leaves. Under the null all means are zero.
Alternative i shifts only leaf i by gamma; the center and all other leaves
remain zero. Every alternative therefore violates exactly one star edge.

For unit-independent Gaussian calls with leaf variance nu^2, suppose first that
a fixed nonadaptive design takes exactly t samples from every leaf. The
likelihood ratio L_i for alternative i satisfies

    E_0[L_i] = 1,
    E_0[L_i^2] = exp(t gamma^2 / nu^2),

and, because different leaf likelihood ratios depend on independent data,

    E_0[L_i L_j] = 1  for i != j.

For the uniform mixture L = (1/m) sum_i L_i,

    chi^2(P_mix || P_0)
      = (exp(t gamma^2 / nu^2) - 1) / m.

Thus a constant-error lower bound for this *symmetric fixed allocation* requires

    t = Omega((nu^2/gamma^2) log m),

and hence total leaf samples

    m t = Omega((m nu^2/gamma^2) log m).

For equal variances the audited star value satisfies

    Psi(K_{1,m},nu) = nu^2 (1 + sqrt(m))^2 = Theta(m nu^2),

so the symmetric calculation has the desired order

    Omega((Psi/gamma^2) log |E|).

## 2. Why this is not yet a proof of the desired theorem

The calculation above assumes equal fixed allocation to the leaves. The actual
Gaussian lower-bound target should cover the model claimed in the paper, which
allows adaptive allocation and expected stopping.

A naive mixture argument with arbitrary fixed counts n_i gives

    chi^2(P_mix || P_0)
      = (1/m^2) sum_i (exp(n_i gamma^2/nu^2) - 1).

Convexity alone does **not** turn a constant lower bound on this expression into
a lower bound of order m log m on sum_i n_i: a highly concentrated allocation
can make the mixture chi-square large while leaving many individual alternatives
poorly tested. Therefore the symmetric calculation cannot be promoted without
an additional minimax/symmetrization or many-alternative argument.

## 3. Exact obligations before promotion

1. Prove that one may restrict to a permutation-symmetric strategy without
   weakening the minimax lower bound, or use an alternative argument that
   directly enforces correctness for every leaf alternative.
2. Handle adaptive sampling and random stopping, not just deterministic counts.
3. Keep center samples in the accounting even though they carry no information
   for the leaf-only alternative family.
4. Combine any multiplicity lower bound with the existing binary
   fixed-confidence `log(1/delta)` term without double counting.
5. Verify the final statement against the exact definition of Psi and concrete
   paired-oracle cost units.

## 4. Candidate routes

- permutation symmetrization plus Yao/minimax;
- Fano or generalized testing inequalities over m+1 hypotheses;
- change-of-measure constraints for every leaf combined through an optimization
  dual rather than a single uniform mixture;
- Gaussian maxima / multiple-testing lower bounds specialized to the shared-center
  graph structure.

## 5. Promotion rule

Do not change P5 or the abstract until an adaptive lower bound is independently
derived and audited. A valid outcome may also be that the union-bound
`log |E|` factor is removable for some graph classes but necessary for others.
