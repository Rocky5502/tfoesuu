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
import json
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

FROZEN_DATA_ROWS = {
    "benchmark_v1.jsonl": 384,
    "replay_benchmark_v1.jsonl": 54,
    "software_subject_benchmark_v1.jsonl": 32,
    "counterfactual_replay_benchmark_v1.jsonl": 144,
    "threshold_replay_phase_v1.jsonl": 24,
    "control_replay_structural_cases_v1.jsonl": 6,
    "partial_replay_benchmark_v1.jsonl": 168,
    "partial_replay_structural_cases_v1.jsonl": 8,
    "partial_replay_scope_cases_v1.jsonl": 1,
}
REQUIRED_PAPER_MARKERS = {
    r"\tableofcontents": "reviewer navigation TOC",
    r"\label{fig:overview}": "overview figure",
    r"\label{alg:tfoesuu}": "algorithmic framework",
    r"\label{sec:evaluation}": "evaluation section",
    r"\textbf{RQ1}": "RQ1",
    r"\textbf{RQ2}": "RQ2",
    r"\textbf{RQ3}": "RQ3",
    r"\textbf{RQ4}": "RQ4",
    r"\label{tab:main-results}": "main theorem results table",
    r"\label{thm:threshold-replay-phase}": "P18 thresholded replay theorem",
    r"\label{fig:threshold-replay-phase}": "P18--P19 replay phase figure",
    r"\label{thm:control-replay}": "P19 matched-control replay theorem",
    r"\label{tab:benchmark-inventory}": "benchmark inventory table",
    r"\label{tab:deterministic-evidence}": "deterministic evidence table",
}


def resolve_input(parent: Path, raw: str) -> Path:
    candidates = [PAPER / raw, parent.parent / raw]
    normalized = []
    for candidate in candidates:
        if candidate.suffix == "":
            candidate = candidate.with_suffix(".tex")
        normalized.append(candidate)
    for candidate in normalized:
        if candidate.exists():
            return candidate
    return normalized[0]


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
    missing_cites = sorted(set(cites) - set(bibkeys))

    errors: list[str] = []
    if duplicate_labels:
        errors.append(f"duplicate labels: {duplicate_labels}")
    if missing_refs:
        errors.append(f"unresolved references: {missing_refs}")
    if duplicate_bib:
        errors.append(f"duplicate BibTeX keys: {duplicate_bib}")
    if missing_cites:
        errors.append(f"missing BibTeX keys: {missing_cites}")


    manuscript_text = "\n".join(text for _, text in docs)
    for marker, name in REQUIRED_PAPER_MARKERS.items():
        if marker not in manuscript_text:
            errors.append(f"missing required manuscript component: {name}")

    if r"\textsc{TBD}" in manuscript_text or "Values Pending" in manuscript_text:
        errors.append(
            "compiled manuscript contains TBD placeholders; preregistered public "
            "result templates must remain outside the submission-facing closure"
        )

    data_dir = Path("data")
    observed_total = 0
    for filename, expected_rows in FROZEN_DATA_ROWS.items():
        path = data_dir / filename
        if not path.is_file():
            errors.append(f"missing frozen data artifact: {path}")
            continue
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        observed_total += len(rows)
        if len(rows) != expected_rows:
            errors.append(
                f"{path}: expected {expected_rows} frozen rows, found {len(rows)}"
            )
        ids = [
            row.get("benchmark_id")
            or row.get("case_id")
            or row.get("subject_id")
            or row.get("id")
            for row in rows
        ]
        ids = [value for value in ids if value is not None]
        if ids and len(set(ids)) != len(ids):
            errors.append(f"{path}: duplicate frozen row identifiers")

    if observed_total != 821:
        errors.append(
            f"frozen benchmark inventory total drift: expected 821, found {observed_total}"
        )

    public_registry = data_dir / "public_benchmark_registry_v1.jsonl"
    if not public_registry.is_file():
        errors.append(f"missing public benchmark registry: {public_registry}")
    else:
        public_rows = [
            json.loads(line)
            for line in public_registry.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(public_rows) != 7:
            errors.append(
                f"{public_registry}: expected 7 public benchmark entries, "
                f"found {len(public_rows)}"
            )
        public_ids = [row.get("benchmark_id") for row in public_rows]
        if any(not value for value in public_ids) or len(set(public_ids)) != len(public_ids):
            errors.append(f"{public_registry}: public benchmark IDs must be unique and non-empty")

    scope_path = data_dir / "partial_replay_scope_cases_v1.jsonl"
    if scope_path.is_file():
        scope_rows = [
            json.loads(line)
            for line in scope_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(scope_rows) == 1:
            row = scope_rows[0]
            cuts = sorted({
                0.0,
                float(row["old_threshold_0"]),
                float(row["old_threshold_1"]),
                float(row["new_threshold_0"]),
                float(row["new_threshold_1"]),
                1.0,
            })
            measure = 0.0
            for left, right in zip(cuts, cuts[1:]):
                if right <= left:
                    continue
                u = (left + right) / 2.0
                old = [
                    int(u <= float(row["old_threshold_0"])),
                    int(u <= float(row["old_threshold_1"])),
                ]
                new = [
                    int(u <= float(row["new_threshold_0"])),
                    int(u <= float(row["new_threshold_1"])),
                ]
                deltas = [new_i - old_i for old_i, new_i in zip(old, new)]
                if len(set(deltas)) > 1:
                    measure += right - left
            expected_measure = float(row["expected_false_positive_measure"])
            if abs(measure - expected_measure) > 1e-12:
                errors.append(
                    "P17 scope measure drift between executable threshold geometry "
                    "and frozen scope manifest"
                )

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
