#!/usr/bin/env python3
"""Run the theorem-facing TFOESUU publication validation suite.

The suite is intentionally model-free and network-free.  It executes existing
synthetic theorem audits under frozen seeds and writes every stdout payload,
command, and repository state to a run directory.  GPU sweeps are opt-in because
they can be large; deterministic manifests and CPU sanity experiments always run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Iterable


def command_output(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.STDOUT, timeout=15
        ).strip()
    except Exception:
        return None


def cpu_plan(trials: int) -> list[tuple[str, list[str]]]:
    py = sys.executable
    jobs: list[tuple[str, list[str]]] = [
        (
            "p17_manifest_validation",
            [
                py,
                "experiments/validate_partial_replay_manifest.py",
                "--benchmark",
                "data/partial_replay_benchmark_v1.jsonl",
            ],
        ),
        (
            "p19_manifest_validation",
            [
                py,
                "experiments/validate_control_replay_manifest.py",
                "--benchmark",
                "data/control_replay_structural_cases_v1.jsonl",
            ],
        ),
        (
            "replay_phase_contract",
            [py, "experiments/validate_replay_phase_contract.py"],
        ),
        (
            "mixed_control_geometry_search",
            [
                py,
                "experiments/search_control_replay_mixed_geometry.py",
                "--top",
                "20",
            ],
        ),
    ]

    for graph in ("matching", "star", "path", "clique"):
        n = "8" if graph != "clique" else "6"
        jobs.append(
            (
                f"gaussian_{graph}",
                [
                    py,
                    "experiments/run_gaussian_core.py",
                    "--graph",
                    graph,
                    "--n",
                    n,
                    "--gamma",
                    "0.5",
                    "--beta",
                    "0.05",
                    "--trials",
                    str(trials),
                    "--seed",
                    "20271008",
                ],
            )
        )

    for d in ("0.10", "0.05", "0.02", "0.01"):
        tag = d.replace(".", "p")
        jobs.append(
            (
                f"paired_replay_d{tag}",
                [
                    py,
                    "experiments/run_replay_separation.py",
                    "--p",
                    "0.50",
                    "--d",
                    d,
                    "--beta",
                    "0.05",
                    "--trials",
                    str(trials),
                    "--seed",
                    "20271008",
                ],
            )
        )
        jobs.append(
            (
                f"four_way_replay_d{tag}",
                [
                    py,
                    "experiments/run_counterfactual_replay.py",
                    "--p",
                    "0.35",
                    "--shared-patch",
                    "0.20",
                    "--d",
                    d,
                    "--beta",
                    "0.05",
                    "--trials",
                    str(trials),
                    "--seed",
                    "20271008",
                ],
            )
        )

    for tau in ("0.0", "0.01", "0.05", "0.10"):
        tag = tau.replace(".", "p")
        jobs.append(
            (
                f"threshold_phase_tau{tag}",
                [
                    py,
                    "experiments/run_threshold_replay_phase.py",
                    "--p",
                    "0.20",
                    "--shared-patch",
                    "0.10",
                    "--tau",
                    tau,
                    "--d",
                    "0.01",
                    "--beta",
                    "0.05",
                    "--trials",
                    str(trials),
                    "--seed",
                    "20271008",
                ],
            )
        )

    jobs.extend(
        [
            (
                "location_replay",
                [
                    py,
                    "experiments/run_location_replay.py",
                    "--candidates",
                    "16",
                    "--p",
                    "0.50",
                    "--d",
                    "0.05",
                    "--beta",
                    "0.05",
                    "--trials",
                    str(trials),
                ],
            ),
            (
                "software_subject",
                [
                    py,
                    "experiments/run_allocator_subject.py",
                    "--contexts",
                    "16",
                    "--changed-context",
                    "3",
                    "--delta",
                    "0.05",
                    "--beta",
                    "0.05",
                    "--trials",
                    str(trials),
                ],
            ),
        ]
    )
    return jobs


def gpu_plan(
    devices: str,
    trials: int,
    output_dir: Path,
) -> list[tuple[str, list[str]]]:
    py = sys.executable
    return [
        (
            "gpu_gaussian_sweep",
            [
                py,
                "experiments/gpu_sweep.py",
                "--devices",
                devices,
                "--trials",
                str(trials),
                "--benchmark",
                "data/benchmark_v1.jsonl",
                "--output",
                str(output_dir / "gpu_gaussian.jsonl"),
            ],
        ),
        (
            "gpu_paired_replay_sweep",
            [
                py,
                "experiments/gpu_replay_sweep.py",
                "--devices",
                devices,
                "--trials",
                str(trials),
                "--benchmark",
                "data/replay_benchmark_v1.jsonl",
                "--output",
                str(output_dir / "gpu_paired_replay.jsonl"),
            ],
        ),
        (
            "gpu_four_way_replay_sweep",
            [
                py,
                "experiments/gpu_counterfactual_sweep.py",
                "--devices",
                devices,
                "--trials",
                str(trials),
                "--benchmark",
                "data/counterfactual_replay_benchmark_v1.jsonl",
                "--output",
                str(output_dir / "gpu_four_way_replay.jsonl"),
            ],
        ),
    ]


def run_jobs(
    jobs: Iterable[tuple[str, list[str]]],
    output_dir: Path,
) -> list[dict]:
    records: list[dict] = []
    for name, cmd in jobs:
        proc = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log_path = output_dir / f"{name}.log"
        log_path.write_text(proc.stdout, encoding="utf-8")
        record = {
            "name": name,
            "command": cmd,
            "returncode": proc.returncode,
            "log": str(log_path),
        }
        records.append(record)
        if proc.returncode != 0:
            raise RuntimeError(
                f"{name} failed with exit code {proc.returncode}; "
                f"see {log_path}"
            )
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--mode",
        choices=["smoke", "publication"],
        default="smoke",
        help="smoke uses 1k CPU trials; publication uses 100k CPU trials",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/publication_suite"),
    )
    ap.add_argument(
        "--gpu-devices",
        help="optional comma-separated CUDA ids; omitted means CPU-only",
    )
    ap.add_argument(
        "--gpu-trials",
        type=int,
        default=1_000_000,
    )
    args = ap.parse_args()

    cpu_trials = 1_000 if args.mode == "smoke" else 100_000
    args.output_dir.mkdir(parents=True, exist_ok=True)

    repo_state = {
        "git_commit": command_output(["git", "rev-parse", "HEAD"]),
        "git_status_porcelain": command_output(["git", "status", "--porcelain"]),
        "mode": args.mode,
        "cpu_trials_per_stochastic_job": cpu_trials,
        "gpu_devices": args.gpu_devices,
        "gpu_trials_per_manifest_row": (
            args.gpu_trials if args.gpu_devices else None
        ),
    }
    (args.output_dir / "run_state.json").write_text(
        json.dumps(repo_state, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    evidence = subprocess.run(
        [
            sys.executable,
            "scripts/summarize_submission_evidence.py",
            "--output",
            str(args.output_dir / "deterministic_evidence.json"),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if evidence.returncode != 0:
        raise RuntimeError(
            "deterministic evidence summary failed:\n" + evidence.stdout
        )

    jobs = cpu_plan(cpu_trials)
    if args.gpu_devices:
        jobs.extend(
            gpu_plan(
                args.gpu_devices,
                args.gpu_trials,
                args.output_dir,
            )
        )

    records = run_jobs(jobs, args.output_dir)
    (args.output_dir / "commands.json").write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "passed",
                "jobs": len(records),
                "output_dir": str(args.output_dir),
                **repo_state,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
