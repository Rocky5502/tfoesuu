#!/usr/bin/env python3
from __future__ import annotations

import json
import platform
import sys


def main():
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "torch_available": False,
        "cuda_available": False,
        "cuda_device_count": 0,
        "devices": [],
    }
    try:
        import torch

        report["torch_available"] = True
        report["torch_version"] = torch.__version__
        report["torch_cuda_version"] = torch.version.cuda
        report["cuda_available"] = bool(torch.cuda.is_available())
        report["cuda_device_count"] = int(torch.cuda.device_count())
        for i in range(torch.cuda.device_count()):
            p = torch.cuda.get_device_properties(i)
            report["devices"].append(
                {
                    "id": i,
                    "name": p.name,
                    "total_memory_gib": round(p.total_memory / (1024**3), 3),
                    "compute_capability": f"{p.major}.{p.minor}",
                }
            )
    except Exception as exc:
        report["torch_error"] = repr(exc)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
