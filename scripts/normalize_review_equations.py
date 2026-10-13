r"""Normalize display mathematics in the STOC review source.

The review manuscript uses numbered displays throughout.  This script converts
legacy ``\[ ... \]`` blocks in the compiled source closure into numbered
``equation`` environments with deterministic, unique labels.  Existing
equation/align environments and their semantic labels are left untouched.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "stoc2027_review"
TARGETS = (
    PAPER / "formal_results.tex",
    PAPER / "appendix" / "03_localization.tex",
    PAPER / "appendix" / "04_coupled_execution.tex",
    PAPER / "appendix" / "07_regression_consequences.tex",
    PAPER / "appendix" / "07_open_problems.tex",
)
DISPLAY = re.compile(r"(?<!\\)\\\[(.*?)(?<!\\)\\\]", re.DOTALL)


def label_prefix(path: Path) -> str:
    relative = path.relative_to(PAPER).with_suffix("").as_posix()
    return re.sub(r"[^a-z0-9]+", "-", relative.lower()).strip("-")


def normalize(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    prefix = label_prefix(path)
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        body = match.group(1).strip("\n")
        return (
            f"\\begin{{equation}}\\label{{eq:{prefix}-{count:03d}}}\n"
            f"{body}\n"
            "\\end{equation}"
        )

    normalized = DISPLAY.sub(replace, source)
    path.write_text(normalized, encoding="utf-8", newline="\n")
    return count


def main() -> None:
    total = 0
    for path in TARGETS:
        changed = normalize(path)
        total += changed
        print(f"{path.relative_to(ROOT)}: normalized {changed} displays")
    print(f"normalized {total} displays")


if __name__ == "__main__":
    main()
