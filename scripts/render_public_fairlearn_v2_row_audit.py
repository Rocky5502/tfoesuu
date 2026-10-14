#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tfoesuu.public_fairlearn_v2_reporting import (
    load_jsonl,
    render_row_audit_table,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render the provenance-bound Fairlearn V2 affected-row census."
    )
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--row-audit", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--tex-output", type=Path, required=True)
    args = parser.parse_args()

    admission = json.loads(args.admission.read_text(encoding="utf-8"))
    row_audit = json.loads(args.row_audit.read_text(encoding="utf-8"))
    registry = load_jsonl(args.registry)
    table = render_row_audit_table(admission, row_audit, registry)
    args.tex_output.parent.mkdir(parents=True, exist_ok=True)
    args.tex_output.write_bytes(table.encode("utf-8"))
    print(
        json.dumps(
            {
                "tex_output": str(args.tex_output),
                "dataset_count": len(row_audit["datasets"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
