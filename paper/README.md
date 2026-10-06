# Overleaf manuscript

Upload the contents of this directory to Overleaf with `main.tex` as the root document.

The submission draft uses an 11pt single-column letter-paper layout with one-inch margins to keep the first 10--12 pages readable, matching the STOC 2027 submission guidance. The accepted-paper proceedings format is a different later-stage format.

The bibliography intentionally contains archival peer-reviewed sources only.


For a submission candidate, compile the PDF from the frozen commit and attach
`paper/main.pdf` to the repository-wide submission checksum manifest using
`scripts/freeze_submission_artifacts.py --require-clean --extra-file paper/main.pdf`.
The PDF is intentionally git-ignored; the manifest records its SHA-256 digest.


## Group-coherent P17 promotion note

The group-coherent P17 extension was kept outside the manuscript until candidate
commit `012d0bdc44c761073f5a7f3e9e912e50e2af7192` passed full CI and both
push- and PR-triggered real LaTeX builds.  The subsequent promotion commit
synchronizes the audited proposition with the proof ledger, code, deterministic
specification data, and submission manuscript.  Arbitrary heterogeneous
fairness-preserving nulls remain explicitly outside the claim.
