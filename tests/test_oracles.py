import numpy as np

from tfoesuu.oracles import BernoulliCommonUniformPair, GaussianVersionPair


def test_gaussian_variance_identity():
    oracle = GaussianVersionPair.from_sequences(
        mu0=[0.0, 1.0],
        mu1=[0.1, 0.8],
        sigma0=[1.0, 2.0],
        sigma1=[1.5, 1.0],
        rho=[0.8, -0.25],
    )
    expected = np.array([
        1.5**2 + 1.0**2 - 2 * 0.8 * 1.5 * 1.0,
        1.0**2 + 2.0**2 - 2 * (-0.25) * 1.0 * 2.0,
    ])
    np.testing.assert_allclose(oracle.paired_delta_variance, expected)
    np.testing.assert_allclose(oracle.independent_delta_variance, [3.25, 5.0])


def test_bernoulli_common_uniform_formula():
    p0 = np.array([0.1, 0.5, 0.8])
    p1 = np.array([0.2, 0.49, 0.3])
    oracle = BernoulliCommonUniformPair.from_sequences(p0, p1)
    d = np.abs(p1 - p0)
    np.testing.assert_allclose(oracle.paired_delta_variance, d * (1 - d))
    np.testing.assert_allclose(
        oracle.independent_delta_variance,
        p0 * (1 - p0) + p1 * (1 - p1),
    )


def test_common_uniform_sampling_mean_and_variance():
    oracle = BernoulliCommonUniformPair.from_sequences([0.4], [0.43])
    rng = np.random.default_rng(123)
    z = oracle.sample_delta(0, 400_000, rng, paired=True)
    assert abs(z.mean() - 0.03) < 0.002
    assert abs(z.var() - 0.03 * 0.97) < 0.002
