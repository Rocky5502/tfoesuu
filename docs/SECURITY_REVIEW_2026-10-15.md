# TFOESUU repository security and publication-readiness audit — 15 October 2026

**Scope:** source-tree hygiene and selected remote-file inspection. This is not a
penetration test, transitive dependency CVE scan, Git history secret scan, or
production security certification.

## Observations verified from the current GitHub repository

- The branch was based on audited `main` commit
  `695007fba0c7d78e3361c60671fd37da7e3a642e`.
- The root initially lacked a `LICENSE`, `SECURITY.md`, dependency-update
  configuration, and a purpose-built README illustration.
- Eleven security-relevant files were read (PC1/PC2 shell scripts, public
  benchmark preparation/loaders, robust nuisance module, both workflows and
  the historical-subject Dockerfile).
- A targeted search in those eleven found **no matches** for embedded PEM
  private-key markers, common GitHub/AWS/token shapes, quoted hardcoded
  credential assignments, disabled TLS/SSH verification, `shell=True`,
  `os.system(`, or `eval(`. This is *not* evidence those risks cannot exist in
  other source files, Git history or third-party dependencies.
- The PC1 dispatcher references a **user-managed** SSH private-key path; the
  inspected source did not contain private-key contents.
- The historical-subject Docker image is pinned by SHA-256, but dependency
  advisory status, image integrity beyond its declared digest, and patch
  freshness have **not** been externally verified.
- CI uses version tags of third-party Actions rather than pinned commit
  digests; GitHub Actions execution was previously reported blocked by account
  billing. Neither workflow was rerun here.

## Hardening introduced on the maintenance branch

- Added MIT for original files, with explicit third-party rights exclusions.
- Added responsible security disclosure instructions.
- Expanded `.gitignore` to protect local credentials and private keys.
- Set workflow `permissions: contents: read`.
- Disabled checkout credential persistence where Git auth is unnecessary.
- Added timeouts to both CI workflows.
- Added monthly Dependabot PR configuration for Python and GitHub Actions.
- Added maintenance and review templates and accessible architecture graphic.

## Mandatory checks before public release

1. Run a full history-aware secret scan, e.g. an organization-approved
   Gitleaks/detect-secrets workflow, and **revoke any exposed credentials**.
2. Run a dependency CVE audit on every supported Python profile, including
   GPU/public-benchmark extras; check container base and runtime packages.
3. Pin GitHub Actions to reviewed full commit SHAs and document update policy.
4. Verify all contributor/institutional copyright rights before granting MIT.
5. Audit `paper/` contents, cached datasets, and historical commits before
   changing repository visibility. Removing tracked files does not erase history.
6. Restore functioning CI and obtain a passing run on the exact release SHA.
7. Validate `pip install -e '.[dev]'`, `pytest -q`, and reproducibility
   validators on a clean checkout after any code-only/paper split.
8. Review external fetchers for redirects, source pins, SHA checks and
   archive-extraction traversal safety before accepting untrusted inputs.

**Release verdict:** the maintenance branch improves hygiene and documentation,
but a full security clearance or permission to make the repository public has
not been established. Keep the publication/submission freeze separate.
