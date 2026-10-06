# Submission artifact freeze

This procedure creates a machine-readable checksum manifest for a candidate STOC
submission. It does not create empirical results and must not be used to imply
that publication sweeps were run when they were not.

## Clean-source freeze

From the exact candidate commit:

```bash
pytest -q
python scripts/check_bibliography.py
python scripts/check_paper_consistency.py
python scripts/freeze_submission_artifacts.py \
  --require-clean \
  --output results/submission_manifest.json
```

The manifest records:

- exact git commit;
- whether the worktree was clean before the manifest was written;
- every tracked repository file, byte count, and SHA-256 digest;
- a canonical SHA-256 digest over the full tracked-file record;
- any explicitly attached untracked/ignored artifacts.

The manifest itself is written after the cleanliness check, so placing it under
the git-ignored `results/` directory does not invalidate the frozen source
state.

## Attach compiled PDF and real publication artifacts

Only include files that actually exist and were generated from the frozen
commit. For example:

```bash
python scripts/freeze_submission_artifacts.py \
  --require-clean \
  --extra-file paper/main.pdf \
  --extra-file results/gpu_sweep_1m.jsonl \
  --extra-file results/gpu_sweep_1m.provenance.json \
  --output results/submission_manifest.json
```

Repeat `--extra-file` for every submission-facing result, provenance record,
or compiled artifact. Tracked benchmark JSONL files and paper sources are
already included automatically.

## Integrity rules

- Never add a missing result merely to satisfy the manifest.
- Never hand-edit a result after its provenance record is created.
- A dirty worktree is not submission-frozen.
- Re-running this tool at a different commit creates a different source identity.
- The final archived bundle should contain the manifest and the exact files it
  references.
- Human authors must still verify theorem proofs, citations, authorship,
  conflicts, and STOC submission metadata.
