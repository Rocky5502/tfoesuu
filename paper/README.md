# Overleaf manuscript

Upload the contents of this directory to Overleaf with `main.tex` as the root document.

The submission draft uses an 11pt single-column letter-paper layout with one-inch margins, matching the STOC 2027 submission guidance. The title/abstract occupy a dedicated title page, followed by an optional table-of-contents page; the official CFP states that the merits, prior-work context, and central technical ideas must be clear within the first twelve pages following the title page, while a TOC immediately after the title page does not count toward those twelve pages. The accepted-paper proceedings format is a different later-stage format.

The bibliography intentionally contains archival peer-reviewed sources only.


For a submission candidate, compile the PDF from the frozen commit and attach
`paper/main.pdf` to the repository-wide submission checksum manifest using
`scripts/freeze_submission_artifacts.py --require-clean --extra-file paper/main.pdf`.
The PDF is intentionally git-ignored; the manifest records its SHA-256 digest.
