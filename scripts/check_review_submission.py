#!/usr/bin/env python3
"""Static gates specific to the STOC 2027 review-submission source."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

PAPER = Path("paper/stoc2027_review")
MAIN = PAPER / "main.tex"
INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
RAW_DISPLAY_RE = re.compile(r"(?<!\\)\\\[")
NUMBERED_DISPLAY_RE = re.compile(
    r"\\begin\{(equation|align|gather|multline)\}(.*?)\\end\{\1\}", re.DOTALL
)


def resolve_input(parent: Path, raw: str) -> Path:
    for candidate in (PAPER / raw, parent.parent / raw):
        resolved = candidate if candidate.suffix else candidate.with_suffix(".tex")
        if resolved.exists():
            return resolved
    raise FileNotFoundError(raw)


def collect(path: Path, seen: set[Path]) -> list[tuple[Path, str]]:
    resolved = path.resolve()
    if resolved in seen:
        return []
    seen.add(resolved)
    text = resolved.read_text(encoding="utf-8")
    docs = [(resolved, text)]
    for raw in INPUT_RE.findall(text):
        docs.extend(collect(resolve_input(resolved, raw), seen))
    return docs


def main() -> None:
    errors: list[str] = []
    try:
        docs = collect(MAIN, set())
    except FileNotFoundError as exc:
        raise SystemExit(f"missing review input: {exc}") from exc

    labels = [label for _, text in docs for label in LABEL_RE.findall(text)]
    duplicates = sorted(label for label, count in Counter(labels).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate labels: {duplicates}")

    equation_count = 0
    for path, text in docs:
        if RAW_DISPLAY_RE.search(text):
            errors.append(f"unnumbered display math remains in {path}")
        for match in NUMBERED_DISPLAY_RE.finditer(text):
            equation_count += 1
            if not LABEL_RE.search(match.group(2)):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"unlabeled {match.group(1)} environment at {path}:{line}")

    preamble = (PAPER / "review_preamble.tex").read_text(encoding="utf-8")
    required_format = {
        r"\documentclass[11pt,letterpaper,oneside]{article}": "11-point letter article",
        r"\usepackage[margin=1in,letterpaper]{geometry}": "one-inch letter geometry",
        r"\bibliographystyle{alpha}": "alphanumeric bibliography",
    }
    combined = "\n".join(text for _, text in docs)
    if re.search(r"\bet\s+al\.", combined, re.IGNORECASE):
        errors.append("review source uses 'et al.' contrary to the STOC reference guidance")
    for marker, description in required_format.items():
        source = preamble if "documentclass" in marker or "geometry" in marker else combined
        if marker not in source:
            errors.append(f"missing review-format gate: {description}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

    print(
        "review submission check passed: "
        f"{len(docs)} TeX files, {equation_count} numbered/labeled displays, "
        f"{len(labels)} total labels"
    )


if __name__ == "__main__":
    main()
