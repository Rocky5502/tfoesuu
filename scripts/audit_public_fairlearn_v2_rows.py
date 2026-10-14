#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from external_subjects.fairlearn_public_v2.runner_core import load_runner_input_bundle
from tfoesuu.public_fairlearn_v2_reporting import sha256_file
from tfoesuu.public_fairlearn_v2_results import (
    summarize_public_fairlearn_v2_rows,
    validate_public_fairlearn_v2_campaign_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate frozen Fairlearn V2 outputs and audit exact row/group discrepancies."
        )
    )
    parser.add_argument("--old", type=Path, required=True)
    parser.add_argument("--new", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--input-bundle", type=Path, required=True)
    parser.add_argument("--runner-commit", required=True)
    parser.add_argument("--input-bundle-manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    old = json.loads(args.old.read_text(encoding="utf-8"))
    new = json.loads(args.new.read_text(encoding="utf-8"))
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    protocol_sha256 = sha256_file(args.protocol)
    manifest_path = args.input_bundle / "input_bundle_manifest.json"
    if sha256_file(manifest_path) != args.input_bundle_manifest_sha256:
        raise ValueError("input bundle manifest SHA-256 mismatch")

    validation = validate_public_fairlearn_v2_campaign_outputs(
        old,
        new,
        protocol,
        expected_protocol_sha256=protocol_sha256,
        expected_runner_commit=args.runner_commit,
        expected_input_bundle_manifest_sha256=args.input_bundle_manifest_sha256,
    )
    contexts = {
        row["dataset_id"]: row
        for row in load_runner_input_bundle(args.input_bundle, args.protocol)
    }
    records = [*old["records"], *new["records"]]
    datasets = summarize_public_fairlearn_v2_rows(records, contexts)
    report = {
        "schema": "tfoesuu-fairlearn-public-v2-row-audit-v1",
        "source_artifacts": {
            "old_sha256": sha256_file(args.old),
            "new_sha256": sha256_file(args.new),
            "protocol_sha256": protocol_sha256,
            "input_bundle_manifest_sha256": sha256_file(manifest_path),
        },
        "validation": {
            "campaign_provenance_valid": validation["campaign_provenance_valid"],
            "record_count": validation["record_count"],
            "runner_commit": validation["runner_commit"],
            "new_repair_conformance": validation["new_repair_conformance"],
            "scope": validation["scope"],
        },
        "datasets": datasets,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "datasets": len(datasets),
                "parent_affected_rows": sum(
                    row["parent_affected_rows"] for row in datasets
                ),
                "repair_affected_rows": sum(
                    row["repair_affected_rows"] for row in datasets
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
