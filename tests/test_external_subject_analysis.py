import numpy as np
import pytest

from tfoesuu.external_subject_analysis import bernoulli_disagreement_laws


def test_bernoulli_disagreement_laws_match_exact_couplings():
    old = np.array([0.0, 0.25, 0.75, 1.0])
    new = np.array([0.5, 0.75, 0.25, 1.0])

    laws = bernoulli_disagreement_laws(old, new)

    np.testing.assert_allclose(laws.common_uniform, [0.5, 0.5, 0.5, 0.0])
    np.testing.assert_allclose(laws.independent, [0.5, 0.625, 0.625, 0.0])
    assert np.all(laws.common_uniform <= laws.independent)


@pytest.mark.parametrize(
    ("old", "new"),
    [([0.1], [0.1, 0.2]), ([-0.1], [0.2]), ([0.1], [1.1]), ([np.nan], [0.2])],
)
def test_bernoulli_disagreement_laws_reject_invalid_probabilities(old, new):
    with pytest.raises(ValueError):
        bernoulli_disagreement_laws(old, new)
