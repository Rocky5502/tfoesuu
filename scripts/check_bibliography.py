#!/usr/bin/env python3
"""Fail on bibliography entries that are explicitly tagged as preprints."""
from pathlib import Path
import re

path = Path("paper/references.bib")
text = path.read_text(encoding="utf-8")
forbidden = [r"arXiv preprint", r"@misc\s*\{"]
hits = [pattern for pattern in forbidden if re.search(pattern, text, re.IGNORECASE)]
if hits:
    raise SystemExit(f"bibliography policy violation: {hits}")
print("bibliography policy check passed")
