from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.public_fairlearn_v2_bundle import build_public_fairlearn_v2_input_bundle


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build an outcome-free input bundle for the pinned Fairlearn runtime."
    )
    parser.add_argument("--prepared-dir", type=Path, required=True)
    parser.add_argument("--companion-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = build_public_fairlearn_v2_input_bundle(
        args.prepared_dir,
        args.companion_dir,
        args.protocol,
        args.output_dir,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
