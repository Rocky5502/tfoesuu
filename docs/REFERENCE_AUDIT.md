# Reference metadata audit

**Audit date:** 2026-10-06  
**Scope:** machine-assisted archival metadata verification of the references
currently used by the STOC manuscript.

This file is an engineering/audit artifact, not a substitute for the STOC
requirement that the human authors independently verify every citation before
submission.  The human-verification checkbox therefore remains open in
`docs/STOC2027_SUBMISSION_CHECKLIST.md`.

## Policy

- Prefer publisher/proceedings/journal records and DOI metadata.
- PMLR and JMLR records without a DOI use their canonical archival article URL.
- Do not cite an arXiv/preprint record when an archival version is available.
- The offline CI check requires every BibTeX entry to contain either a DOI or a
  canonical archival URL.
- Any metadata discrepancy found by the audit is corrected in
  `paper/references.bib` and guarded when practical.

## Audited references

| Key | Archival identity | Machine-assisted audit |
|---|---|---|
| GalhotraBrunMeliou2017 | DOI 10.1145/3106237.3106277 | title/authors/venue/pages matched |
| RothermelHarrold1996 | DOI 10.1109/32.536955 | title/authors/volume/issue/pages matched |
| YooHarman2012 | DOI 10.1002/stvr.430 | publisher record matched volume 22(2), 67--120, 2012 |
| LiSunLeungZhang2013 | DOI 10.1002/stvr.1475 | title/authors/volume/issue/pages matched |
| YanZhang2022 | PMLR v162 canonical article URL | title/authors/pages 24929--24962 matched |
| ChakrabartySeshadhri2013 | DOI 10.1145/2488608.2488661 | title/authors/STOC pages 419--428 matched after correction |
| FischerFortnow2006 | DOI 10.4086/toc.2006.v002a009 | title/journal/volume/pages matched |
| CanonneGur2018 | DOI 10.1007/s00037-018-0168-4 | title/authors/volume/pages matched |
| Hurwitz2011 | DOI 10.1007/978-3-642-25591-5_54 | title/ISAAC LNCS 7074/pages matched |
| GlassermanYao1992 | DOI 10.1287/mnsc.38.6.884 | title/authors/volume/pages matched |
| BartheEtAl2017 | DOI 10.1145/3009837.3009896 | title/authors/POPL pages matched |
| YinEtAl2025 | DOI 10.1145/3728976 | title/authors/PACMSE volume/pages matched |
| YuanLinShi2026 | DOI 10.1145/3798265 | title/authors/PACMPL 10(OOPSLA1)/pages matched |
| SinghSinghDavidov2025 | DOI 10.1111/sjos.12757 | title/authors/SJS 52(2)/pages matched |
| KaufmannCappeGarivier2016 | JMLR v17 article 1 canonical URL | title/authors/pages 1--42 matched |
| AlbarghouthiEtAl2017 | DOI 10.1145/3133904 | title/authors/PACMPL 1(OOPSLA), article 80 matched |
| Connor1987 | DOI 10.2307/2531961 | title/author/Biometrics 43(1), 207--211 matched |
| CohenZhao2015 | DOI 10.1109/TIT.2014.2387857 | title/authors/TIT 61(3), 1432--1450 matched |
| YangNelson1991 | DOI 10.1287/opre.39.4.583 | title/authors/Operations Research 39(4), 583--591 matched |
| NelsonMatejcik1995 | DOI 10.1287/mnsc.41.12.1935 | title/authors/Management Science 41(12), 1935--1945 matched |

## Correction made in this audit

The Chakrabarty--Seshadhri STOC 2013 record previously used the non-archival
title wording

> Optimal Monotonicity and Lipschitz Testers over Hypercubes and Hypergrids

The archival STOC/DBLP record is

> Optimal Bounds for Monotonicity and Lipschitz Testing over Hypercubes and
> Hypergrids

The BibTeX entry has been corrected while retaining the verified DOI
`10.1145/2488608.2488661` and pages 419--428.

## Remaining human gate

Before submission, a human author must independently open each archival record
(or DOI target), verify title/authors/venue/year/pages and that the cited paper
actually supports the manuscript statement where it is used.  Only then should
the human-verification checkbox be marked complete.
