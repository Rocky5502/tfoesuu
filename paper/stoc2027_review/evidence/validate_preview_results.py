"""Validate the frozen P12/P15 100k preview campaign."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.preview_results import validate_preview_campaign


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--base-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = validate_preview_campaign(args.manifest, base_dir=args.base_dir)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
        return
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite existing report: {args.output}")
    args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
