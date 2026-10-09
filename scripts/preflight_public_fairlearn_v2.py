#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from tfoesuu.public_fairlearn_v2_preflight import build_public_fairlearn_v2_preflight


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared-dir", required=True)
    parser.add_argument("--companion-dir", required=True)
    parser.add_argument("--protocol", required=True)
    args = parser.parse_args()
    report = build_public_fairlearn_v2_preflight(
        args.prepared_dir, args.companion_dir, args.protocol
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
