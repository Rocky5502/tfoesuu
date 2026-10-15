# Third-party components and licensing boundaries

The repository's root [MIT LICENSE](LICENSE) covers original TFOESUU code and
documentation for which contributors have the authority to grant that license.
It **does not relicense external content**.

| Component or source | Treatment |
| --- | --- |
| Python dependencies (NumPy, SciPy, NetworkX, Matplotlib, pandas, PyTorch, etc.) | Separate third-party licenses; review package metadata at the installed versions |
| Historical Fairlearn source and software behavior | Upstream copyright and license remain applicable; research reproduction is not original ownership |
| Public benchmark input populations | Original dataset terms, attribution, redistribution and privacy conditions apply; see `data/README.md` |
| ACM `acmart.cls`, `ACM-Reference-Format.bst` and publisher-provided files | Retain their upstream licensing and author/publisher notices; do not assume MIT coverage |
| LaTeX and statistical literature | Citations are not a license to redistribute third-party text or figures |

Before redistributing a release, audit actual vendored files for their own
copyright notices and reproduce them as required. Do not infer permission to
publish entire benchmark datasets simply because scripts can download them.

**Contributor-rights check:** people contributing code must ensure they have
authority to distribute it under MIT. The license does not replace any
coauthor, institutional, employer or publisher permissions that may be needed.
