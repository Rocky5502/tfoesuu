#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from tfoesuu.public_score_companion_v2 import validate_public_score_companion_v2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("companion_dir")
    parser.add_argument("prepared_v2_dir")
    args = parser.parse_args()
    report = validate_public_score_companion_v2(
        args.companion_dir, args.prepared_v2_dir
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
