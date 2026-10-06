# Overleaf manuscript

Upload the contents of this directory to Overleaf with `main.tex` as the root document.

The submission draft uses an 11pt single-column letter-paper layout with one-inch margins to keep the first 10--12 pages readable, matching the STOC 2027 submission guidance. The accepted-paper proceedings format is a different later-stage format.

The bibliography intentionally contains archival peer-reviewed sources only.


For a submission candidate, compile the PDF from the frozen commit and attach
`paper/main.pdf` to the repository-wide submission checksum manifest using
`scripts/freeze_submission_artifacts.py --require-clean --extra-file paper/main.pdf`.
The PDF is intentionally git-ignored; the manifest records its SHA-256 digest.


## Candidate-theorem audit note

The group-coherent P17 extension is being audited outside the submission
manuscript first.  Its proof, tests, and deterministic specification data live
in the repository, but the theorem is intentionally not inserted into
`main.tex` until candidate CI and a real LaTeX build pass.  This README change
also ensures the paper workflow compiles the unchanged manuscript on the
candidate branch as an explicit audit gate.
