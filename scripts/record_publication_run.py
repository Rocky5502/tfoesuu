#!/usr/bin/env python3
"""Create an immutable provenance record for a local publication experiment."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from tfoesuu.provenance import sha256_file, sha256_lf_normalized_text


def command_output(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.STDOUT, timeout=15
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", type=Path, required=True)
    ap.add_argument("--result", type=Path, required=True)
    ap.add_argument("--command", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if not args.benchmark.is_file():
        raise FileNotFoundError(args.benchmark)
    if not args.result.is_file():
        raise FileNotFoundError(args.result)

    torch_info = None
    try:
        import torch
        torch_info = {
            "version": torch.__version__,
            "cuda_runtime": torch.version.cuda,
            "cuda_available": torch.cuda.is_available(),
            "devices": [
                {
                    "index": i,
                    "name": torch.cuda.get_device_name(i),
                    "capability": list(torch.cuda.get_device_capability(i)),
                }
                for i in range(torch.cuda.device_count())
            ],
        }
    except (ImportError, OSError, RuntimeError) as exc:
        torch_info = {"available": False, "error": type(exc).__name__}

    record = {
        "schema": "tfoesuu-publication-run-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": command_output(["git", "rev-parse", "HEAD"]),
        "git_status_porcelain": command_output(["git", "status", "--porcelain"]),
        "command": args.command,
        "benchmark": {
            "path": str(args.benchmark),
            "sha256": sha256_file(args.benchmark),
            "sha256_lf_normalized": sha256_lf_normalized_text(args.benchmark),
            "bytes": args.benchmark.stat().st_size,
        },
        "result": {
            "path": str(args.result),
            "sha256": sha256_file(args.result),
            "sha256_lf_normalized": sha256_lf_normalized_text(args.result),
            "bytes": args.result.stat().st_size,
        },
        "python": platform.python_version(),
        "platform": platform.platform(),
        "nvidia_smi": command_output(["nvidia-smi"]),
        "torch": torch_info,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()
