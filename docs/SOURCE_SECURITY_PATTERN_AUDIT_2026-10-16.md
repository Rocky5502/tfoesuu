# Source security pattern audit — 16 October 2026

**Repository:** `Rocky5502/tfoesuu`
**Audited commit:** `14f518c0c62905b98327efcb4bc9eb14b5184bb1` on `main`.
**Status:** scoped source-pattern review completed; public-release gate remains **blocked**.

## Coverage and outcome

- Enumerated the full Git tree, and targeted all **107 tracked executable source files**
  with `.py`, `.sh` or `.ps1` extensions under `src/`, `scripts/`,
  `experiments/`, and `external_subjects/`.
- Retrieved and inspected every one of those files through the authenticated
  GitHub connector at the exact audited SHA; **107/107 readable**.
- Searched for embedded PEM/SSH private-key markers, common GitHub/AWS
  credential-token patterns, simple quoted hardcoded-secret assignments,
  `shell=True`, `os.system`, `eval`, `exec`, disabled transport-verification
  patterns, `pickle.load` / `yaml.load` / `tarfile.extractall`, and
  obvious network-to-shell pipelines.
- **Zero matches in these selected pattern families** after the security
  changes merged in PR #19. This does *not* mean these categories are
  impossible or that the overall code is vulnerability-free.

## Actual remediation

1. The historical PC2 replication script no longer downloads an external
   installer and feeds it to a shell. Its non-Docker fallback now requires a
   manually installed and checksum-verified pinned `uv 0.12.20` binary and
   aborts on version mismatch.
2. The Windows SSH dispatcher now requires a configured host and username
   from `TFOESUU_PC2_HOST`, `TFOESUU_PC2_USER`, or its explicit flags.
   No workstation-specific defaults remain in its current source.
3. Added two static regression tests to enforce those decisions.
4. Original scientific algorithms, frozen evidence, and manuscript source
   were not modified by that PR.

## CI facts as checked on GitHub

- Latest `main` run at
  https://github.com/Rocky5502/tfoesuu/actions/runs/38879124401 is marked
  `failure`, but its sole job reported **zero steps**.
- Downloading the job logs returned a missing-blob error, so no specific
  failure explanation could be independently confirmed in this review.
- A billing/spending-limit block was reported earlier by the research team,
  but is not independently established from the unavailable current logs.
- Historical reported 347 passing local tests remain historical evidence;
  **the full suite was not independently rerun on this new HEAD**.

## Out-of-scope / mandatory next gates

This check did not analyze Git history, scanned all non-code data/docs,
execute dynamic taint analysis or a dependency CVE checker, verify the legal
rights to all files, or run a clean-install CI. The Docker image has a declared
SHA-256 base digest; its actual contents/dependency advisories were not
audited. GitHub Actions are still not passing.

Before making a public release: review every historical commit for secrets
and restricted content; audit third-party licenses, datasets, publisher
templates and manuscript/publication rights; run clean end-to-end local
tests and hosted CI on the exact released source; and preferably create a
**new code-only repository with a fresh Git history** rather than change this
research archive's visibility. Removing `paper/` in a new commit does not
remove the older copies from Git history.

See [release gate](PUBLIC_RELEASE_GATE_2026-10-16.md),
[third-party notices](../THIRD_PARTY_NOTICES.md), and
[paper separation issue](https://github.com/Rocky5502/tfoesuu/issues/15).
