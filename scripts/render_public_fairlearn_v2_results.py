#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.public_fairlearn_v2_reporting import admit_campaign_outputs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the frozen Fairlearn V2 campaign and render submission artifacts."
    )
    parser.add_argument("--old", type=Path, required=True)
    parser.add_argument("--new", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--runner-commit", required=True)
    parser.add_argument("--input-bundle-manifest-sha256", required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--tex-output", type=Path, required=True)
    args = parser.parse_args()

    admission, table = admit_campaign_outputs(
        old_path=args.old,
        new_path=args.new,
        protocol_path=args.protocol,
        registry_path=args.registry,
        expected_runner_commit=args.runner_commit,
        expected_input_bundle_manifest_sha256=args.input_bundle_manifest_sha256,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.tex_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(admission, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.tex_output.write_text(table, encoding="utf-8")
    print(
        json.dumps(
            {
                "json_output": str(args.json_output),
                "tex_output": str(args.tex_output),
                "record_count": admission["validation"]["record_count"],
                "new_repair_conformance": admission["validation"][
                    "new_repair_conformance"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
