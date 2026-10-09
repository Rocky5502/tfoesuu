# Fairlearn public-context audit

## Decision

The frozen public-v1 artifacts are **not executable multi-column Fairlearn
contexts**.  No larger Fairlearn matrix may use them as if they contained
row-level protected values.

Five registry entries name two protected attributes: Adult, German Credit,
COMPAS, Law School, and Default Credit.  This makes them candidates for a new
preparation audit, not validated contexts.  The other two entries name only one
protected attribute.

## Evidence

The preparation code removes the declared protected columns before fitting the
predictor.  It then writes only `baseline_probabilities` and
`evaluation_labels` to each NPZ.  Protected *names* survive in JSON metadata,
but protected values and the held-out row indices do not.  Consequently the
values cannot be reconstructed from the prepared artifacts without reloading
the source population and reproducing the split.

A read-only inspection on PC2 confirmed this exact two-key schema for all seven
frozen NPZ files.  Its canonical compact payload has SHA-256
`9154f1cd625be433bcae77f543e085949acec8f813ac4af29656d3b049a36558`.
No source or prepared artifact was modified.

The current preparer also treats a declared protected column as optional when
dropping predictors: it records the registry declaration even if the loaded
frame does not contain every named column.  Therefore the five registry rows
are only multi-column candidates; their metadata does not prove that both
columns were present at preparation time.

## Enforced gate

`audit_prepared_v1_fairlearn_contexts` first runs the complete strict v1
validator, then reports registry candidates separately from executable-ready
subjects.  For the v1 contract the executable-ready set is necessarily empty.
The command-line wrapper can be run with `--require-ready` and exits with status
2, preventing a metadata-only declaration from passing the gate.

## Requirements for a separately versioned v2 preparation

A genuine-context artifact must be created in a new output directory and must
not mutate v1.  Before any outcome run it must:

1. require every declared protected column to exist, with exact recorded names;
2. preserve held-out row indices and the aligned row-level protected matrix;
3. record categorical encodings and missing-value handling without collapsing
   distinct joint groups;
4. prove alignment among probabilities, labels, indices, and protected rows;
5. record source bytes, loader versions, split seed, preparation Git SHA, and
   artifact hashes;
6. freeze a Fairlearn estimand and test protocol before observing outcomes; and
7. pass a corruption suite covering absent columns, reordered rows, truncated
   group labels, unknown categories, and schema drift.

The separate V2 schema, non-overwriting preparer, validator, and corruption
suite are now implemented in `docs/PUBLIC_BENCHMARK_V2_PROTOCOL.md`. A read-only
PC2 inventory found retained source bytes for Adult, Bank, German, COMPAS, Law
School, and MEPS, but initially not for Default Credit: its original
`ucimlrepo` call did not preserve a raw file. The official UCI ZIP has now been
reacquired over verified HTTPS under CC BY 4.0 and frozen at a new path with
SHA-256 `56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602`.
The complete training/evaluation V2.1 representation has now been prepared and
independently validated under clean commit `d0790b3`; hashes are in
`docs/PUBLIC_BENCHMARK_V2_PROTOCOL.md`. This closes the representation gap, not
the experiment-design gate: age is high-cardinality in German and Default
Credit, and no old/new Fairlearn outcome has been run.

A seven-dataset outcome campaign and manuscript admission remain behind the
explicit publication-scale approval gate.
