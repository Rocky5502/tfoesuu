# Repository maintenance and publication separation

This repository is an executable research software workspace, not a published
paper archive. The root README presents its code, limitations, and reproducibility.

## Branches

- `main`: maintained integration branch. Do not force-push or silently rewrite
  previously reported scientific experiments.
- `research/*`: theorem proposals, assumptions, proof attacks, and controlled
  experiments. Not automatically a validated result.
- `docs/*`: documentation and repository maintenance changes. Review with a
  pull request prior to merge.

## Paper separation

At the October 2026 checkpoint, **tracked `paper/` sources and some validation
scripts still exist** because the scientific freeze, exact evidence, and CI
checks depend on them. This maintenance change intentionally does not delete
those files or reconfigure their integrity checks.

For a future code-only public repository, perform an independent separation:
(1) preserve the existing freeze and hashes in an access-controlled archive,
(2) identify imports, tests and workflows that reference `paper/`,
(3) move manuscript-specific source/validation to the archival workspace,
(4) update code-only CI, (5) run the full local test and reproducibility checks,
and (6) remove manuscript files in a separately reviewed PR. **Do not assume
`.gitignore` removes already tracked files or old Git history.**

If manuscript details must remain confidential, maintain private visibility
until a properly reviewed redaction and history audit is complete. A deletion
commit cannot erase previously accessible Git blobs or forks.

## Release gate

Review licenses, dependency security, source hashes, historical datasets,
reproducibility constraints, and coauthor publication rights before any public
release. The software MIT license does not supersede manuscript or dataset terms.
