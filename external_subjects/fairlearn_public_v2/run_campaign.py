"""Approval-gated historical Fairlearn public-context campaign runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from external_subjects.fairlearn_public_v2.runner_core import (
    NEW_COMMIT,
    OLD_COMMIT,
    load_runner_input_bundle,
    run_dataset_transcript,
    validate_campaign_approval,
    validate_subject_checkout,
)


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
    if args.output.exists() or not args.output.parent.is_dir():
        raise ValueError("output must be a new file in an existing directory")

    sys.path.insert(0, str(args.checkout.resolve()))
    from fairlearn.postprocessing import ThresholdOptimizer

    commit = OLD_COMMIT if args.version == "old" else NEW_COMMIT
    records = [
        run_dataset_transcript(
            threshold_optimizer_cls=ThresholdOptimizer,
            version=args.version,
            commit=commit,
            **dataset,
        )
        for dataset in inputs
    ]
    result = {
        "schema": "tfoesuu-fairlearn-public-v2-campaign-output-v1",
        "version": args.version,
        "commit": commit,
        "approval": approval,
        "source": source,
        "records": records,
    }
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
