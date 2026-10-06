#!/usr/bin/env python3
"""Build a machine-readable submission artifact manifest.

The manifest hashes every tracked repository file and any explicitly supplied
extra artifacts (for example the compiled PDF or frozen publication results).
It never creates or infers empirical results.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from tfoesuu.provenance import sha256_file


def git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=root,
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def tracked_files(root: Path) -> list[Path]:
    raw = subprocess.check_output(
        ["git", "ls-files", "-z"],
        cwd=root,
    ).decode("utf-8")
    return sorted(
        (root / rel)
        for rel in raw.split("\0")
        if rel and (root / rel).is_file()
    )


def file_record(path: Path, root: Path, kind: str) -> dict[str, object]:
    resolved = path.resolve()
    try:
        display = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        display = str(resolved)
    return {
        "path": display,
        "kind": kind,
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def tree_digest(records: list[dict[str, object]]) -> str:
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument(
        "--extra-file",
        action="append",
        type=Path,
        default=[],
        help="Additional untracked/ignored artifact to hash; may be repeated.",
    )
    ap.add_argument(
        "--require-clean",
        action="store_true",
        help="Fail unless git status --porcelain is empty before writing output.",
    )
    args = ap.parse_args()

    root = args.root.resolve()
    commit = git_output(root, "rev-parse", "HEAD")
    status = git_output(root, "status", "--porcelain")
    clean = status == ""
    if args.require_clean and not clean:
        raise SystemExit("refusing submission freeze from a dirty git worktree")

    records = [file_record(path, root, "tracked") for path in tracked_files(root)]
    tracked_paths = {str(Path(record["path"])) for record in records}

    extras: list[dict[str, object]] = []
    for raw in args.extra_file:
        path = raw if raw.is_absolute() else root / raw
        if not path.is_file():
            raise FileNotFoundError(path)
        rec = file_record(path, root, "extra")
        if str(Path(rec["path"])) in tracked_paths:
            raise SystemExit(
                f"--extra-file is already tracked and automatically included: {rec['path']}"
            )
        extras.append(rec)
    extras.sort(key=lambda item: str(item["path"]))

    manifest = {
        "schema": "tfoesuu-submission-freeze-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "git_clean_before_manifest": clean,
        "git_status_porcelain": status,
        "tracked_file_count": len(records),
        "tracked_tree_sha256": tree_digest(records),
        "tracked_files": records,
        "extra_files": extras,
    }

    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"manifest: {output}")
    print(f"manifest_sha256: {sha256_file(output)}")
    print(f"git_commit: {commit}")
    print(f"tracked_files: {len(records)}")
    print(f"extra_files: {len(extras)}")


if __name__ == "__main__":
    main()
