#!/usr/bin/env python3
"""Static archival-reference policy checks for the STOC manuscript.

This is intentionally offline.  It prevents common metadata regressions after
the external archival metadata audit, but it does not replace independent human
verification against publishers/proceedings.
"""
from pathlib import Path
import re

path = Path("paper/references.bib")
text = path.read_text(encoding="utf-8")

forbidden = [
    r"arXiv preprint",
    r"@misc\s*\{",
    r"url\s*=\s*\{https?://(?:www\.)?arxiv\.org/",
]
hits = [pattern for pattern in forbidden if re.search(pattern, text, re.IGNORECASE)]
if hits:
    raise SystemExit(f"bibliography policy violation: {hits}")

entries = [
    block for block in re.split(r"(?=^@)", text, flags=re.MULTILINE)
    if block.lstrip().startswith("@")
]
if not entries:
    raise SystemExit("bibliography contains no entries")

keys: list[str] = []
missing_archival_id: list[str] = []
dois: list[tuple[str, str]] = []

for entry in entries:
    match = re.match(r"@\w+\s*\{\s*([^,]+),", entry)
    if not match:
        raise SystemExit("could not parse bibliography entry key")
    key = match.group(1).strip()
    keys.append(key)

    doi_match = re.search(r"^\s*doi\s*=\s*\{([^}]+)\}", entry, re.MULTILINE | re.IGNORECASE)
    url_match = re.search(r"^\s*url\s*=\s*\{([^}]+)\}", entry, re.MULTILINE | re.IGNORECASE)
    if not doi_match and not url_match:
        missing_archival_id.append(key)
    if doi_match:
        doi = doi_match.group(1).strip().lower()
        if any(ch.isspace() for ch in doi):
            raise SystemExit(f"bibliography DOI contains whitespace: {key}: {doi}")
        dois.append((key, doi))

duplicates = sorted({key for key in keys if keys.count(key) > 1})
if duplicates:
    raise SystemExit(f"duplicate bibliography keys: {duplicates}")

doi_values = [doi for _, doi in dois]
duplicate_dois = sorted({doi for doi in doi_values if doi_values.count(doi) > 1})
if duplicate_dois:
    raise SystemExit(f"duplicate bibliography DOIs: {duplicate_dois}")

if missing_archival_id:
    raise SystemExit(
        "bibliography entries missing DOI or canonical archival URL: "
        + ", ".join(missing_archival_id)
    )

# Regression guard for a metadata error found in the 2026-10-06 archival audit.
wrong_stoc_title = "Optimal Monotonicity and Lipschitz Testers over Hypercubes and Hypergrids"
correct_stoc_title = "Optimal Bounds for Monotonicity and Lipschitz Testing over Hypercubes and Hypergrids"
if wrong_stoc_title in text:
    raise SystemExit("stale Chakrabarty--Seshadhri STOC title reintroduced")
if correct_stoc_title not in text:
    raise SystemExit("canonical Chakrabarty--Seshadhri STOC title missing")

print(
    f"bibliography policy check passed: {len(entries)} archival entries, "
    f"{len(dois)} DOI-tagged"
)
