#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.public_fairlearn_v2_results import validate_public_fairlearn_v2_transcripts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcripts")
    parser.add_argument("--protocol", required=True)
    args = parser.parse_args()
    protocol = json.loads(Path(args.protocol).read_text(encoding="utf-8"))
    records = [
        json.loads(line)
        for line in Path(args.transcripts).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    report = validate_public_fairlearn_v2_transcripts(records, protocol)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
