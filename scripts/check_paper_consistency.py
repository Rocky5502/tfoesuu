#!/usr/bin/env python3
"""Static consistency checks for the STOC manuscript.

Checks the complete main.tex input closure for:
- missing \input files;
- duplicate labels;
- unresolved \ref/\cref/\Cref targets;
- missing bibliography keys used by \cite commands;
- duplicate BibTeX keys;
- forbidden explicit preprint-only bibliography patterns.

This complements, rather than replaces, a real LaTeX compile.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys


PAPER = Path("paper")
MAIN = PAPER / "main.tex"

INPUT_RE = re.compile(r"\\input\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|pageref|eqref|cref|Cref)\{([^}]+)\}")
CITE_RE = re.compile(r"\\(?:cite|citep|citet)\{([^}]+)\}")
BIBKEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)


def resolve_input(parent: Path, raw: str) -> Path:
    p = parent.parent / raw
    if p.suffix == "":
        p = p.with_suffix(".tex")
    return p


def collect_tex(path: Path, seen: set[Path]) -> list[tuple[Path, str]]:
    path = path.resolve()
    if path in seen:
        return []
    if not path.exists():
        raise FileNotFoundError(path)
    seen.add(path)

    text = path.read_text(encoding="utf-8")
    out = [(path, text)]
    for raw in INPUT_RE.findall(text):
        child = resolve_input(path, raw)
        out.extend(collect_tex(child, seen))
    return out


def main() -> None:
    try:
        docs = collect_tex(MAIN, set())
    except FileNotFoundError as exc:
        raise SystemExit(f"missing manuscript input: {exc}") from exc

    labels: list[str] = []
    refs: list[str] = []
    cites: list[str] = []
    for _, text in docs:
        labels.extend(LABEL_RE.findall(text))
        refs.extend(REF_RE.findall(text))
        for group in CITE_RE.findall(text):
            cites.extend(k.strip() for k in group.split(",") if k.strip())

    label_counts = Counter(labels)
    duplicate_labels = sorted(k for k, n in label_counts.items() if n > 1)
    missing_refs = sorted(set(refs) - set(labels))

    bib_path = PAPER / "references.bib"
    bib = bib_path.read_text(encoding="utf-8")
    bibkeys = BIBKEY_RE.findall(bib)
    bib_counts = Counter(bibkeys)
    duplicate_bib = sorted(k for k, n in bib_counts.items() if n > 1)
    missing_cites = sorted(set(cites) - set(bibkeys))\n    bib_entries = BIBENTRY_RE.findall(bib)\n    missing_doi = sorted(key for _, key, body in bib_entries if not re.search(r"\\bdoi\\s*=", body, re.IGNORECASE))

    errors: list[str] = []
    if duplicate_labels:
        errors.append(f"duplicate labels: {duplicate_labels}")
    if missing_refs:
        errors.append(f"unresolved references: {missing_refs}")
    if duplicate_bib:
        errors.append(f"duplicate BibTeX keys: {duplicate_bib}")
    if missing_cites:
        errors.append(f"missing BibTeX keys: {missing_cites}")

    forbidden = {
        "arXiv preprint": re.compile(r"arXiv\s+preprint", re.IGNORECASE),
        "@misc entry": re.compile(r"@misc\s*\{", re.IGNORECASE),
    }
    hits = [name for name, pat in forbidden.items() if pat.search(bib)]
    if hits:
        errors.append(f"bibliography policy violations: {hits}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        raise SystemExit(1)

    print(
        "paper static check passed: "
        f"{len(docs)} TeX files, {len(labels)} labels, "
        f"{len(set(cites))} cited keys, {len(bibkeys)} bibliography entries"
    )


if __name__ == "__main__":
    main()
