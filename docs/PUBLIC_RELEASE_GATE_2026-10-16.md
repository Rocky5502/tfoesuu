# Public-release gate — TFOESUU (16 October 2026)

## Status

**Code and documentation can be prepared for open source, but changing this
existing private repository's visibility is not yet an approved, audited action.**
The GitHub Git history and tracked `paper/` source are part of the risk
assessment. This is not a claim of a completed public release.

Current base audited: `main` at `59135236a2d0e5824dcef435885fe6ef60e23ade`.
Source inventory: 332 Git-tracked files, including 67 under `paper/`.
Original code/docs have a root MIT license; **third-party components are not
relicensed**, including the ACM class/BST and source datasets. Consult
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Changes staged on security/public-release-preflight-20261016

- Remove the remote-install `curl | sh` fallback from the historical PC2
  replication script. If Docker is unavailable, the script now *requires* an
  already installed, manually checksum-verified `uv 0.12.20` at the prescribed
  local path, and fails on version mismatch. The user must inspect the binary
  source and pin its SHA-256 before running; this repository does not assert a
  binary hash it did not independently capture.
- PC1 SSH dispatch no longer embeds a particular private LAN address or
  Windows account name. On the local controller, set
  `TFOESUU_PC2_HOST` and `TFOESUU_PC2_USER` (or pass the existing
  `-PC2Host` and `-RemoteUser` flags) before invoking. Do not commit
  environment-specific endpoints.
- Two static regression tests guard those defaults.

## Verified and unverified checks

- Read GitHub metadata, tracked-file tree, root MIT/third-party notices,
  Python packaging, both workflows, and selected execution surfaces.
- Previously reported full test counts and GitHub Actions billing failures
  are **historical Codex assertions**, not a fresh green CI run.
- This review searched 12 selected sensitive source files for obvious private-key,
  credential assignment, dynamic-execution and disabled-verification patterns;
  no matching direct secret was observed. This does NOT cover all files, prior
  Git commits or dependencies.
- No live CVE audit, full Git-history secrets scan, clean checkout test, cloud
  runner execution, or complete legal review has been performed in this session.
- The 2026 paper remains a submission-stage asset and has not been separated
  from the Git history.

## Release policy and safe path

1. **Approve rights**: all contributors/coauthors and their institutions must
   authorize open-source distribution of their original code and descriptions.
   Dataset, upstream Fairlearn and ACM files retain separate terms.
2. **Choose disclosure scope**: for a code-only repository, create a **new
   repository with fresh Git history** and copy a strictly reviewed allowlist
   from a locally tested checkout. Removing `paper/` in a new commit of the
   existing Git history is NOT sufficient to prevent historical exposure.
3. **Keep reproducible evidence**: archive research/manuscript sources, result
   hashes and their exact original commit privately; copy only redistributable
   synthetic manifests/aggregated data with necessary provenance to the
   code-only public repository.
4. **Run a full scan**: offline history-aware secret scanning, package
   vulnerability/advisory audit for every relevant Python profile, dependency
   licensing review, upstream source-license checks, and container scanning.
   Rotate/revoke any leaked secret before publishing.
5. **Run clean-build tests**: create a fresh virtualenv and run `pip install
   -e '.[dev]'`, `python -m pytest -q`, inventory/manifest checks and safe
   publication demos; resolve hosted GitHub Actions billing and require a
   completed green workflow on the released commit.
6. **Review communication and STOC policy**: confirm public posting,
   authorship and submission policy with all coauthors before associating
   the repository with the manuscript.
7. **Publish** only after steps 1–6 are signed off. Assign an immutable
   release tag, archive hash, source citation metadata and verified version
   identifier. No fictitious DOI, venue acceptance or green CI badges.

## Operations that are deliberately not performed

- No recursive deletion of `paper/` or rewrite of protected Git history.
- No overwriting original experimental results, manifests or validated proofs.
- No release/tag minted without a fresh test and provenance receipt.
- No visibility change from private to public while licensing/secret and
  submission gates remain unresolved.
