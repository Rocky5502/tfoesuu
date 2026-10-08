#!/usr/bin/env python3
"""GPU finite-instance sweep over prepared public benchmark populations.

The comparison is between execution-access regimes, not between predictive
models.  Prepared datasets provide heterogeneous baseline probabilities.  Each
context induces one counterfactual fairness edge whose old endpoints have the
same probability.  A deterministic uncertainty-band patch applies a common
shift to an impacted subset; one impacted edge additionally receives a
differential shift under the alternative.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

import numpy as np

from tfoesuu.public_benchmarks import (
    validate_preparation_source_compatibility,
    validate_prepared_public_directory,
)
from tfoesuu.public_results import PublicResultRow, write_public_results

METHODS = ("independent", "vertex-paired", "four-way", "suite", "tfoesuu")
DEFAULT_PATCH_SIZES = (0.10, 0.05, 0.02, 0.01)


def git_state() -> tuple[str, bool]:
    sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain"], text=True
        ).strip()
    )
    return sha, dirty


def load_subject(prepared_dir: Path, dataset_id: str) -> tuple[np.ndarray, dict]:
    npz_path = prepared_dir / f"{dataset_id}.npz"
    meta_path = prepared_dir / f"{dataset_id}.json"
    if not npz_path.exists() or not meta_path.exists():
        raise FileNotFoundError(
            f"missing prepared subject for {dataset_id}; run "
            "scripts/prepare_public_benchmarks.py first"
        )
    arr = np.load(npz_path)
    p0 = np.asarray(arr["baseline_probabilities"], dtype=float)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if "preparation_source_commit" not in meta:
        raise ValueError(f"{dataset_id}: prepared metadata lacks source commit")
    if p0.ndim != 1 or len(p0) < 1:
        raise ValueError(f"{dataset_id}: invalid baseline probability vector")
    return p0, meta


def impacted_mask(p0: np.ndarray, fraction: float) -> np.ndarray:
    if not (0.0 < fraction <= 1.0):
        raise ValueError("affected_fraction must lie in (0,1]")
    k = max(1, math.ceil(fraction * len(p0)))
    order = np.argsort(np.abs(p0 - 0.5), kind="stable")
    mask = np.zeros(len(p0), dtype=bool)
    mask[order[:k]] = True
    return mask


def hoeffding_pair_rounds(edges: int, d: float, beta: float) -> int:
    # Two empirical means per edge.  Requiring both means to be within d/4
    # and union-bounding over all edges gives 4M exp(-n d^2 / 8) <= beta.
    return math.ceil(8.0 * math.log(4.0 * edges / beta) / (d * d))


def witness_rounds(d: float, beta: float) -> int:
    return math.ceil(math.log(beta) / math.log1p(-d))


def _batch_size(edges: int, target_elements: int = 1_500_000) -> int:
    return max(1, min(4096, target_elements // max(1, edges)))


def simulate_independent(
    p0: np.ndarray,
    impact: np.ndarray,
    *,
    s: float,
    d: float,
    n: int,
    trials: int,
    changed_edge: int,
    device: str,
    seed: int,
) -> tuple[float, float]:
    import torch

    dev = torch.device(device)
    gen = torch.Generator(device=dev)
    gen.manual_seed(seed)
    p_null = p0 + impact.astype(float) * s
    p_alt_right = p_null.copy()
    p_alt_right[changed_edge] += d
    if np.any((p_null <= 0.0) | (p_null >= 1.0)) or np.any(
        (p_alt_right <= 0.0) | (p_alt_right >= 1.0)
    ):
        raise ValueError("public patch leaves Bernoulli interior")

    left_p = torch.tensor(p_null, dtype=torch.float32, device=dev)
    alt_right_p = torch.tensor(p_alt_right, dtype=torch.float32, device=dev)
    bsz = _batch_size(len(p0))
    null_errors = 0
    alt_misses = 0
    done = 0
    threshold = d / 2.0
    while done < trials:
        b = min(bsz, trials - done)
        totals = torch.full((b, len(p0)), float(n), device=dev)
        lp = left_p.unsqueeze(0).expand(b, -1)
        null_left = torch.binomial(totals, lp, generator=gen)
        null_right = torch.binomial(totals, lp, generator=gen)
        null_diff = torch.abs(null_right - null_left) / float(n)
        null_reject = torch.any(null_diff >= threshold, dim=1)
        null_errors += int(null_reject.sum().item())

        alt_left = torch.binomial(totals, lp, generator=gen)
        arp = alt_right_p.unsqueeze(0).expand(b, -1)
        alt_right = torch.binomial(totals, arp, generator=gen)
        alt_diff = torch.abs(alt_right - alt_left) / float(n)
        alt_reject = torch.any(alt_diff >= threshold, dim=1)
        alt_misses += int((~alt_reject).sum().item())
        done += b
    return null_errors / trials, alt_misses / trials


def simulate_vertex_paired(
    edges: int,
    impact: np.ndarray,
    *,
    s: float,
    d: float,
    n: int,
    trials: int,
    changed_edge: int,
    device: str,
    seed: int,
) -> tuple[float, float]:
    import torch

    dev = torch.device(device)
    gen = torch.Generator(device=dev)
    gen.manual_seed(seed)
    base = impact.astype(float) * s
    alt_right = base.copy()
    alt_right[changed_edge] += d
    left_p = torch.tensor(base, dtype=torch.float32, device=dev)
    alt_right_p = torch.tensor(alt_right, dtype=torch.float32, device=dev)
    bsz = _batch_size(edges)
    threshold = d / 2.0
    null_errors = 0
    alt_misses = 0
    done = 0
    while done < trials:
        b = min(bsz, trials - done)
        totals = torch.full((b, edges), float(n), device=dev)
        lp = left_p.unsqueeze(0).expand(b, -1)
        null_left = torch.binomial(totals, lp, generator=gen)
        null_right = torch.binomial(totals, lp, generator=gen)
        null_diff = torch.abs(null_right - null_left) / float(n)
        null_errors += int(torch.any(null_diff >= threshold, dim=1).sum().item())

        alt_left = torch.binomial(totals, lp, generator=gen)
        arp = alt_right_p.unsqueeze(0).expand(b, -1)
        alt_r = torch.binomial(totals, arp, generator=gen)
        alt_diff = torch.abs(alt_r - alt_left) / float(n)
        alt_misses += int((~torch.any(alt_diff >= threshold, dim=1)).sum().item())
        done += b
    return null_errors / trials, alt_misses / trials


def four_way_witness_on_tape(
    tape: np.ndarray, *, p: float, s: float, d: float
) -> tuple[np.ndarray, np.ndarray]:
    """Explicit four-execution same-tape contrast on frozen one-edge family.

    The returned masks indicate which individual random tapes reveal a
    *differential patch* under the fair null and the one-endpoint alternative.
    This is a pure NumPy test oracle for finite deterministic tape partitions;
    the GPU runner performs the same threshold evaluations using PyTorch.
    """

    u = np.asarray(tape, dtype=float)
    if np.any(~np.isfinite(u)) or np.any((u < 0.0) | (u > 1.0)):
        raise ValueError("random tape values must be finite and in [0,1]")
    if not (0.0 < p < 1.0 and 0.0 <= s < 1.0 - p and 0.0 < d < 1.0 - p - s):
        raise ValueError("require interior p, nonnegative shift s and p+s+d<1")

    old_u = u <= p
    old_v = u <= p
    null_new_u = u <= p + s
    null_new_v = u <= p + s
    alt_new_u = u <= p + s + d
    alt_new_v = u <= p + s
    null_contrast = (null_new_u.astype(np.int8) - old_u.astype(np.int8)) - (
        null_new_v.astype(np.int8) - old_v.astype(np.int8)
    )
    alt_contrast = (alt_new_u.astype(np.int8) - old_u.astype(np.int8)) - (
        alt_new_v.astype(np.int8) - old_v.astype(np.int8)
    )
    return null_contrast != 0, alt_contrast != 0


def simulate_four_way_pathwise_counts(
    *, p: float, s: float, d: float, rounds: int,
    trials: int, device: str, seed: int
) -> tuple[int, int]:
    """Count *simulated executable* same-tape witnesses and misses.

    Uses the actual threshold implementations P0(x;U) and P1(x;U) on
    fresh uniform tapes, rather than injecting a Binomial(d) hit count.
    For the frozen homogeneous single-changed-edge family, only one edge
    can witness a regression; evaluating that edge's sufficient contrast is
    distributionally equivalent to evaluating all unaffected edges.

    Concrete execution counts for full group/suite policies are **planned
    accounting**, not measured program runtime or GPU kernel calls.
    All synchronized methods reuse this matched random-tape trace because
    they have the same observable witness under this frozen model.
    """

    import torch

    if rounds < 1 or trials < 1:
        raise ValueError("rounds and trials must be positive")
    if not (0.0 < p < 1.0 and 0.0 <= s < 1.0 - p and 0.0 < d < 1.0 - p - s):
        raise ValueError("require interior p, nonnegative shift s and p+s+d<1")

    dev = torch.device(device)
    gen = torch.Generator(device=dev)
    gen.manual_seed(seed)
    batch = max(1, min(4096, 1_000_000 // rounds))
    false_rejects = 0
    misses = 0
    done = 0
    while done < trials:
        count = min(batch, trials - done)
        tape = torch.rand((count, rounds), generator=gen, device=dev)
        old_u = tape <= p
        old_v = tape <= p
        null_u = tape <= p + s
        null_v = tape <= p + s
        alt_u = tape <= p + s + d
        alt_v = tape <= p + s
        # Integer arithmetic (rather than XOR) also handles non-monotone
        # threshold changes if the oracle is generalized in the future.
        null_delta = (null_u.to(torch.int8) - old_u.to(torch.int8)) - (
            null_v.to(torch.int8) - old_v.to(torch.int8)
        )
        alt_delta = (alt_u.to(torch.int8) - old_u.to(torch.int8)) - (
            alt_v.to(torch.int8) - old_v.to(torch.int8)
        )
        false_rejects += int(torch.any(null_delta != 0, dim=1).sum().item())
        misses += int((~torch.any(alt_delta != 0, dim=1)).sum().item())
        done += count
    return false_rejects, misses


def run_dataset(
    dataset_id: str,
    p0: np.ndarray,
    meta: dict,
    *,
    d: float,
    s: float,
    beta: float,
    affected_fraction: float,
    trials: int,
    device: str,
    seed: int,
    source_commit: str,
    preparation_source_commit: str,
    preparation_contract_sha256: str,
) -> list[PublicResultRow]:
    if not (0.0 < d < 1.0 and 0.0 <= s < 1.0):
        raise ValueError("invalid patch parameters")
    if float(np.max(p0)) + s + d >= 1.0:
        raise ValueError(
            f"{dataset_id}: p0+s+d must stay below 1; "
            "reduce patch sizes or tighten preparation clipping"
        )
    m = len(p0)
    impact = impacted_mask(p0, affected_fraction)
    k = int(impact.sum())
    changed_edge = int(np.flatnonzero(impact)[0])

    n_quad = hoeffding_pair_rounds(m, d, beta)
    n_linear = witness_rounds(d, beta)

    independent_i, independent_ii = simulate_independent(
        p0, impact, s=s, d=d, n=n_quad, trials=trials,
        changed_edge=changed_edge, device=device, seed=seed + 11
    )
    paired_i, paired_ii = simulate_vertex_paired(
        m, impact, s=s, d=d, n=n_quad, trials=trials,
        changed_edge=changed_edge, device=device, seed=seed + 23
    )
    witness_false_reject_count, witness_miss_count = simulate_four_way_pathwise_counts(
        p=float(p0[changed_edge]), s=s, d=d,
        rounds=n_linear, trials=trials, device=device, seed=seed + 37
    )
    independent_i_count = round(independent_i * trials)
    independent_ii_count = round(independent_ii * trials)
    paired_i_count = round(paired_i * trials)
    paired_ii_count = round(paired_ii * trials)

    common = {
        "dataset_id": dataset_id,
        "dataset_name": str(meta["dataset_name"]),
        "patch_size": d,
        "common_shift": s,
        "confidence_target": beta,
        "trials": trials,
        "graph_vertices": 2 * m,
        "graph_edges": m,
        "affected_fraction": affected_fraction,
        "impacted_edges": k,
        "seed": seed,
        "dataset_sha256": str(meta["canonical_loaded_data_sha256"]),
        "source_commit": source_commit,
        "preparation_source_commit": preparation_source_commit,
        "preparation_contract_sha256": preparation_contract_sha256,
    }

    return [
        PublicResultRow(
            method="independent",
            replay_rounds=float(m * n_quad),
            concrete_program_executions=float(2 * m * n_quad),
            type_i_error_count=independent_i_count,
            type_ii_error_count=independent_ii_count,
            type_i_error=independent_i_count / trials,
            type_ii_error=independent_ii_count / trials,
            **common,
        ),
        PublicResultRow(
            method="vertex-paired",
            replay_rounds=float(m * n_quad),
            concrete_program_executions=float(4 * m * n_quad),
            type_i_error_count=paired_i_count,
            type_ii_error_count=paired_ii_count,
            type_i_error=paired_i_count / trials,
            type_ii_error=paired_ii_count / trials,
            **common,
        ),
        PublicResultRow(
            method="four-way",
            replay_rounds=float(m * n_linear),
            concrete_program_executions=float(4 * m * n_linear),
            type_i_error_count=witness_false_reject_count,
            type_ii_error_count=witness_miss_count,
            type_i_error=witness_false_reject_count / trials,
            type_ii_error=witness_miss_count / trials,
            **common,
        ),
        PublicResultRow(
            method="suite",
            replay_rounds=float(n_linear),
            concrete_program_executions=float(4 * m * n_linear),
            type_i_error_count=witness_false_reject_count,
            type_ii_error_count=witness_miss_count,
            type_i_error=witness_false_reject_count / trials,
            type_ii_error=witness_miss_count / trials,
            **common,
        ),
        PublicResultRow(
            method="tfoesuu",
            replay_rounds=float(k * n_linear),
            concrete_program_executions=float(4 * k * n_linear),
            type_i_error_count=witness_false_reject_count,
            type_ii_error_count=witness_miss_count,
            type_i_error=witness_false_reject_count / trials,
            type_ii_error=witness_miss_count / trials,
            **common,
        ),
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepared-dir", type=Path, default=Path("data/public_prepared"))
    ap.add_argument("--dataset", action="append", help="prepared dataset ID; repeatable")
    ap.add_argument("--patch-size", action="append", type=float)
    ap.add_argument("--common-shift", type=float, default=0.05)
    ap.add_argument("--affected-fraction", type=float, default=0.10)
    ap.add_argument("--beta", type=float, default=0.05)
    ap.add_argument("--trials", type=int, default=10_000)
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--seed", type=int, default=20271008)
    ap.add_argument("--output", type=Path, default=Path("results/public_replay_gpu.jsonl"))
    ap.add_argument("--allow-dirty", action="store_true")
    args = ap.parse_args()

    sha, dirty = git_state()
    if dirty and not args.allow_dirty:
        raise SystemExit("working tree is dirty; commit/freeze before publication runs")

    prepared_report = validate_prepared_public_directory(args.prepared_dir)
    compatibility = validate_preparation_source_compatibility(
        prepared_report["source_commit"],
        sha,
    )
    print(
        "validated preparation compatibility: "
        f"prepared={prepared_report['source_commit']} execution={sha} "
        f"contract={compatibility['contract_sha256']}",
        flush=True,
    )

    patch_sizes = args.patch_size or list(DEFAULT_PATCH_SIZES)
    if args.dataset:
        dataset_ids = args.dataset
    else:
        dataset_ids = sorted(
            path.stem for path in args.prepared_dir.glob("public-*.npz")
        )
    if not dataset_ids:
        raise SystemExit("no prepared public datasets found")

    rows: list[PublicResultRow] = []
    for dataset_index, dataset_id in enumerate(dataset_ids):
        p0, meta = load_subject(args.prepared_dir, dataset_id)
        prep_commit = str(meta["preparation_source_commit"])
        if prep_commit != prepared_report["source_commit"]:
            raise SystemExit(f"{dataset_id}: inconsistent preparation source commit")
        for d_index, d in enumerate(patch_sizes):
            run_seed = args.seed + 1000 * dataset_index + 100 * d_index
            print(
                f"running {dataset_id}: d={d}, trials={args.trials}, "
                f"device={args.device}",
                flush=True,
            )
            rows.extend(
                run_dataset(
                    dataset_id,
                    p0,
                    meta,
                    d=d,
                    s=args.common_shift,
                    beta=args.beta,
                    affected_fraction=args.affected_fraction,
                    trials=args.trials,
                    device=args.device,
                    seed=run_seed,
                    source_commit=sha,
                    preparation_source_commit=prep_commit,
                    preparation_contract_sha256=compatibility["contract_sha256"],
                )
            )

    write_public_results(rows, args.output)
    print(f"wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
