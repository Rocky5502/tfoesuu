"""Replay-law tests for the explicit old/new four-way threshold oracle.

These are small synthetic oracle fixtures, not publication GPU results.
"""

import numpy as np
import pytest

from experiments.gpu_public_replay_sweep import (
    four_way_witness_on_tape,
    simulate_four_way_pathwise_counts,
)


def test_four_way_null_cancels_and_alternative_exposes_exact_interval():
    # Old endpoints have threshold 0.20; fair patch shifts both to 0.30.
    # Alternative changes exactly one endpoint to 0.35. Witness interval
    # is (0.30, 0.35], not an injected Bernoulli(d) random variable.
    tape = np.array([0.10, 0.20, 0.25, 0.29, 0.31, 0.34, 0.36, 0.50, 0.90])
    null, alt = four_way_witness_on_tape(tape, p=0.20, s=0.10, d=0.05)
    assert not np.any(null)
    np.testing.assert_array_equal(
        alt,
        np.array([False, False, False, False, True, True, False, False, False]),
    )


def test_four_way_null_cancels_under_nonzero_common_benign_shift():
    tape = np.linspace(0.0, 1.0, 4097)
    null, alt = four_way_witness_on_tape(tape, p=0.25, s=0.20, d=0.04)
    assert np.count_nonzero(null) == 0
    expected = (tape > 0.45) & (tape <= 0.49)
    np.testing.assert_array_equal(alt, expected)


def test_four_way_oracle_rejects_invalid_tape_or_noninterior_probabilities():
    with pytest.raises(ValueError):
        four_way_witness_on_tape(np.array([float("nan")]), p=0.2, s=0.1, d=0.05)
    with pytest.raises(ValueError):
        four_way_witness_on_tape(np.array([1.1]), p=0.2, s=0.1, d=0.05)
    with pytest.raises(ValueError):
        four_way_witness_on_tape(np.array([0.5]), p=0.5, s=0.4, d=0.2)


def test_four_way_torch_cpu_smoke_follows_declared_model():
    pytest.importorskip("torch")
    false_rejects, misses = simulate_four_way_pathwise_counts(
        p=0.2, s=0.1, d=0.10,
        rounds=30, trials=4000, device="cpu", seed=20271008,
    )
    assert false_rejects == 0
    assert 0 <= misses <= 4000
    # P(no mismatch after 30 independent tapes) = (1-d)^30.
    expected_miss_rate = (1.0 - 0.10) ** 30
    assert (misses / 4000) == pytest.approx(expected_miss_rate, abs=0.025)
