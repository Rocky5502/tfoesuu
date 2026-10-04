# Numerical sanity checks

These checks validate implementation and constants; they are **not empirical scientific claims**.

## Gaussian star

Command:

```bash
PYTHONPATH=src python experiments/run_gaussian_core.py --graph star --n 10 --gamma 0.6 --beta 0.05 --trials 20000 --seed 11
```

Observed in the development environment:

- analytic `Psi = 16`;
- primal `Psi = 15.999999999999977`;
- dual `Psi = 15.999999999150091`;
- primal-dual gap `8.50e-10`;
- theorem allocation: center about `4`, each of nine leaves about `4/3`;
- 20,000-trial null error estimate: `0.00545` for target `beta=0.05`;
- 20,000-trial planted-alternative miss estimate: `0.0001`.

The theorem is deliberately conservative; the simulation is only a consistency check.

## Bernoulli common-uniform patch

Command:

```bash
PYTHONPATH=src python experiments/run_bernoulli_coupling.py --p0 0.5 --delta 0.01 --samples 500000 --seed 11
```

Theory:

- paired delta variance: `0.01 * 0.99 = 0.0099`;
- independent replay variance: `0.5*0.5 + 0.51*0.49 = 0.4999`;
- variance ratio: about `0.019804`.

The development run returned empirical variances about `0.0098961` and `0.4991623`, respectively.
