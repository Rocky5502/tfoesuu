from __future__ import annotations

import pytest

from tfoesuu.oracles import common_uniform_transcript_pmf, pushforward_pmf
from tfoesuu.separations import (
    discrete_kl,
    edge_coupled_common_patch_kl,
    paired_per_round_kl,
    threshold_fairness_replay_kl,
    vertex_paired_common_patch_kl,
)


def test_p12_kl_is_exact_for_named_raw_pair_transcript():
    p, d = 0.2, 0.01
    null = common_uniform_transcript_pmf((p, p))
    alternative = common_uniform_transcript_pmf((p, p + d))

    assert discrete_kl(null, alternative) == pytest.approx(paired_per_round_kl(p, d))
    delta_null = pushforward_pmf(null, lambda y: y[1] - y[0])
    delta_alternative = pushforward_pmf(alternative, lambda y: y[1] - y[0])
    assert discrete_kl(delta_null, delta_alternative) != pytest.approx(
        paired_per_round_kl(p, d)
    )


def test_p15_kls_are_exact_for_raw_vertex_and_four_way_transcripts():
    p, s, d = 0.2, 0.1, 0.01
    vertex_null = common_uniform_transcript_pmf((p, p + s))
    vertex_alternative = common_uniform_transcript_pmf((p, p + s + d))
    edge_null = common_uniform_transcript_pmf((p, p + s, p, p + s))
    edge_alternative = common_uniform_transcript_pmf(
        (p, p + s + d, p, p + s)
    )

    assert discrete_kl(vertex_null, vertex_alternative) == pytest.approx(
        vertex_paired_common_patch_kl(p, s, d)
    )
    assert discrete_kl(edge_null, edge_alternative) == pytest.approx(
        edge_coupled_common_patch_kl(p, s, d)
    )


def test_p18_kl_is_exact_for_raw_four_way_transcript():
    p, s, tau, d = 0.2, 0.1, 0.1, 0.01
    null = common_uniform_transcript_pmf((p, p + s + tau, p, p + s))
    alternative = common_uniform_transcript_pmf(
        (p, p + s + tau + d, p, p + s)
    )

    assert discrete_kl(null, alternative) == pytest.approx(
        threshold_fairness_replay_kl(p, s, tau, d)
    )
