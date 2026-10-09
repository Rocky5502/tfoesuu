# Public protected-context V2 protocol

## Scope and status

V2 repairs the representation defect in public V1 without changing V1. It is a
data and provenance contract for observed protected-group contexts; it is not a
fairness outcome, a causal counterfactual construction, or publication evidence.

Implementation is complete and tested. Production preparation is **blocked**
until exact raw bytes for all seven registered sources are frozen and the
committed V2 source map is validated. PC2 initially retained source bytes for
six datasets. The missing Default Credit archive was then reacquired from the
registered UCI HTTPS endpoint under its CC BY 4.0 license, without disabling
certificate verification, and frozen separately from V1.

## Artifact schema

Each `<dataset-id>.npz` contains exactly:

- `baseline_probabilities`: finite interior evaluation probabilities;
- `evaluation_labels`: aligned binary targets;
- `source_row_positions`: unique positions in the canonical loaded population;
- `protected_attribute_values`: a two-dimensional matrix in declared column order;
- `non_protected_feature_values`: the aligned raw evaluation feature matrix.

Heterogeneous table values use canonical JSON scalar tokens, never pickle.
Metadata records the exact loaded protected columns, registry semantics,
category catalog, joint-group counts, minimum support, feature columns, split
counts and seed, source-file byte hashes, preparation Git SHA, exact Python and
loader-package versions, and a row-wise alignment SHA-256 over every stored
array.

The contract fixes `counterfactual_semantics` to `observational-context-only`,
sets the counterfactual transform status to `not-defined`, and limits
identifiability to observed joint-group comparisons. Protected attributes may
not be inferred from aggregate probabilities or relabeled as causal worlds.

## Fail-closed properties

The validator rejects:

- any dataset set other than the complete frozen seven-entry registry;
- absent or case-ambiguous protected columns;
- protected columns leaking into the predictor feature matrix;
- row-count, row-position, shape, alignment-digest, or split drift;
- pickle/object arrays, malformed scalar encodings, category-catalog drift, or
  joint-group count drift;
- fewer than two joint groups meeting the preregistered support threshold;
- missing, size-mismatched, or SHA-256-mismatched source artifacts;
- incomplete environment locks, mixed preparation commits,
  metadata/manifest divergence, or an existing
  destination directory.

Preparation uses a new staging directory and renames it only after complete
validation. It never edits or replaces `datasets/prepared/` or its V1 manifest.

## Commands after the seventh source is frozen

The frozen path map is `configs/public_source_map_v2.json`; every path is
relative to the immutable raw-source root. From a clean committed tree:

```bash
python -m pip install -r requirements-public-v2.txt

python scripts/prepare_public_benchmarks_v2.py \
  --data-home /path/to/raw \
  --source-root /path/to/raw \
  --source-map /path/to/source-map-v2.json \
  --output-dir /path/to/prepared_v2 \
  --accept-meps-terms

python scripts/validate_prepared_public_benchmarks_v2.py \
  /path/to/prepared_v2 \
  --source-root /path/to/raw \
  --expected-source-commit <full-clean-sha> \
  --require-ready
```

The first command refuses dirty source, partial registries, and existing output
paths. The second verifies source bytes again. No outcome experiment is
authorized by either command.

## Current PC2 source evidence

The read-only PC2 raw directory contains 15 files: three direct source files
(COMPAS CSV, Law School SAS, MEPS ZIP) and twelve OpenML cache objects covering
Adult, Bank, and German. The SHA-256 of the lexicographically ordered
`sha256sum` listing is
`73edce410b52b132befc77a10a2ed23fd77dbeebb395222e082c20c4bd500e3e`.
Loading those six cached populations read-only confirmed the declared protected
columns are present in every frame; the canonical loader shape/index/column
schema digest is
`5d69a1a723144733ae88858a492b0eed3bb56b5c1f61bb86200c786a45dcb0ad`.
The official UCI Default Credit ZIP was downloaded to a new path (never
overwriting V1 or another raw file); SHA-256
`56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602`.
It contains exactly one 5,539,328-byte XLS member. After this addition, the
ordered 16-file raw-source listing digest is
`92a3fddd48155e527ee549b705026e1063823d34f6e00f1bb2bb44d3dd341e2e`.
No prepared V2 artifact or
outcome is claimed until a clean committed preparer reproduces and validates
all seven populations.
