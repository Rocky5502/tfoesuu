"""Approval-gated historical Fairlearn public-context campaign runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from external_subjects.fairlearn_public_v2.runner_core import (
    NEW_COMMIT,
    OLD_COMMIT,
    load_runner_input_bundle,
    run_dataset_transcript,
    validate_campaign_approval,
    validate_runner_checkout,
    validate_subject_checkout,
)


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=("old", "new"), required=True)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--input-bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    # Authority is checked before the subject checkout is mounted or imported.
    approval = validate_campaign_approval(args.protocol, args.approval)
    inputs = load_runner_input_bundle(args.input_bundle, args.protocol)
    source = validate_subject_checkout(args.checkout, args.version)
    runner = validate_runner_checkout(Path(__file__).resolve().parents[2])
    input_bundle_manifest_sha256 = _sha256(
        args.input_bundle / "input_bundle_manifest.json"
    )
    if args.output.exists() or not args.output.parent.is_dir():
        raise ValueError("output must be a new file in an existing directory")

    sys.path.insert(0, str(args.checkout.resolve()))
    import fairlearn
    import numpy as np
    import pandas as pd
    import scipy
    import sklearn
    from fairlearn.postprocessing import ThresholdOptimizer

    commit = OLD_COMMIT if args.version == "old" else NEW_COMMIT
    started_at = datetime.now(timezone.utc)
    started = time.perf_counter()
    records = [
        run_dataset_transcript(
            threshold_optimizer_cls=ThresholdOptimizer,
            version=args.version,
            commit=commit,
            **dataset,
        )
        for dataset in inputs
    ]
    finished_at = datetime.now(timezone.utc)
    result = {
        "schema": "tfoesuu-fairlearn-public-v2-campaign-output-v2",
        "version": args.version,
        "commit": commit,
        "protocol_sha256": approval["protocol_sha256"],
        "input_bundle_manifest_sha256": input_bundle_manifest_sha256,
        "runner": runner,
        "approval": approval,
        "source": source,
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "packages": {
                "fairlearn": fairlearn.__version__,
                "numpy": np.__version__,
                "pandas": pd.__version__,
                "scipy": scipy.__version__,
                "scikit_learn": sklearn.__version__,
            },
        },
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "elapsed_seconds": time.perf_counter() - started,
        "records": records,
    }
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
