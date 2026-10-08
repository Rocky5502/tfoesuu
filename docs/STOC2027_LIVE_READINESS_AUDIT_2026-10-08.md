# TFOESUU STOC 2027: Live Submission-Readiness Audit

Audit date: **2026-10-08**. Branch: **main**. This document records
a GitHub source/inventory inspection, not an independent proof certificate or
a clean local full-repository build. Revalidate it after subsequent commits.

## Bottom line

**Submission readiness: NOT YET.** The deterministic benchmark specifications,
source code, tests, theorem-ledger documentation and manuscript sources exist.
There is no verified publication-scale result bundle or clean full-manuscript
build at the inspected HEAD. P20 is conjectural. The present external Overleaf
project state has not been established.

## Checked source/inventory facts

- Nine frozen theorem-specification JSONL artifacts contain **821 rows in
  total**: Gaussian 384; paired replay 54; executable subject 32;
  four-way counterfactual 144; threshold phase 24; matched controls 6;
  partial-replay stress 168; structural cases 8; heterogeneous scope 1.
  Each JSONL was parsed via the connected GitHub repository and checked for
  duplicate identifiers within that file on 2026-10-08.
- The separate `data/public_benchmark_registry_v1.jsonl` contains **7 public
  populations**, all marked `planned`: Adult, Bank Marketing, German Credit,
  COMPAS, Law School GPA, MEPS Panel 21, Default Credit.
- `results/` has only `.gitkeep` in Git. Large run outputs are deliberately
  excluded; their absence from Git alone does not prove they were never run
  elsewhere. No result bundle was provided/verified for this audit.
- `paper/generated/public_results_table.tex` contains intentionally unfilled
  `TBD` cells; it is not an empirical results table for submission.
- `paper/main.tex` references the monochrome editable TikZ overview, theorem
  sections, code-facing algorithm, experimental *protocol*, and peer-reviewed
  related-work sources. This inspection does not certify a clean full PDF build.
- `docs/PROOF_STATUS.md` marks P1--P19 as audited **within their frozen
  models**. This is a project ledger claim, not a substitute for an independent
  human proof audit. P20 remains **CONJECTURE** and must not enter the abstract
  as an established theorem.

## Explicit statistical and software-scope caveats

The public sweep in `experiments/gpu_public_replay_sweep.py` constructs
synthetic old/new Bernoulli oracles from locally derived baseline probabilities.
Some method outcomes are simulated directly from their exact Bernoulli witness
law rather than replaying a general nondeterministic software system. These
results can validate the *frozen threshold-coupled model* if actually run and
audited, but cannot establish practical record/replay feasibility for arbitrary
real software, or prove P20.

The original source and the ingestion loader must remain distinct. The
frozen registry now records AIF360 as the preparation loader for Adult, Bank,
German, COMPAS, Law School, and MEPS, and UCI (`ucimlrepo`) for Default
Credit. Archival source names/URLs remain the original dataset provenance.
Prepare all datasets from one frozen clean commit and report the resulting
data hashes.

## Build and validation status

The latest inspected GitHub Actions jobs were failing **before an assigned
runner or reported execution steps**. No passing evidence for pytest, benchmark
regeneration, bibliography checks, or `latexmk` was obtained. Do not describe
the CI or manuscript build as green.

To run locally on an environment with Python, dependencies, and TeX Live:

```bash
git switch main
git pull --ff-only origin main
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m compileall -q src scripts experiments tests
python scripts/validate_benchmark_inventory.py
pytest -q
make paper-check
make paper-pdf
python scripts/summarize_submission_evidence.py --output results/submission_evidence.json
```

If a full PDF has errors or unreadable content, fix and re-run before submission.
For publication experiments, follow `docs/TOMORROW_GPU_CHECKLIST.md` from the
same clean frozen commit after reading any dataset access terms.

## Open blockers in recommended priority

1. **Obtain a working CI runner and a clean local/CI pytest run.** The recorded
   workflow startup failures do not establish downstream code quality.
2. **Compile and inspect the full manuscript PDF.** Verify captions, label and
   equation references, bibliography metadata, page count and legibility of the
   overview at final 11-pt physical size.
3. **Run a CPU smoke and freeze a publication execution ledger.** Record source
   SHA, seeds, commands, environment, error denominators and result hashes.
4. **Prepare and validate all seven public subjects.** These are currently
   registered populations, not completed downloadable datasets or results.
   Include explicit MEPS access-term acknowledgement when applicable.
5. **Run reproducible theorem-facing simulation sweeps.** Report actual type-I
   and type-II counts with binomial intervals; do not label deterministic
   manifest rows as stochastic results. Avoid unneeded GPU spending on P17
   exact miss probabilities that can be computed analytically.
6. **Do not conflate theorem scopes.** P17 homogeneous and P19 two-class
   controls are special cases. P20 composite-null information geometry needs
   a replay-realizable observation law, independent proof, and matching sound
   adaptive/finite-sample upper algorithm before promotion.
7. **Finalize authorship, independent human mathematical and bibliographic
   audit, and STOC 2027 video/consent requirements.** Follow
   `docs/STOC2027_SUBMISSION_CHECKLIST.md`.

## Overleaf status

The GitHub `paper/*.tex` source is updated. This audit found no authenticated
Overleaf project write/preview integration and did not verify any automatic
GitHub-to-Overleaf synchronization. A GitHub update is **not** confirmation
that the separate Overleaf project already has the same commit. Verify the
Overleaf-side commit/import and build before claiming synchronized status.

## Change hygiene and preparation

The immediate local workflow was strengthened so `make paper-check`
runs both bibliography and complete-manuscript consistency checks, and
`make paper-pdf` invokes `latexmk`. The GPU checklist has been corrected
to use `main` rather than the stale automation branch. Public benchmark
`loader_family` metadata is being aligned to the actual preparation code;
the underlying source names and DOI provenance are unchanged.
