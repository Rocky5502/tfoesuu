# Public protected-context V2 protocol

## Scope and status

V2.1 repairs the representation defect in public V1 without changing V1. It is a
data and provenance contract for observed protected-group contexts; it is not a
fairness outcome, a causal counterfactual construction, or publication evidence.

Implementation is complete and tested. Exact raw bytes and a committed source
map now exist for all seven datasets. A first immutable V2.0 preparation at
commit `18442ac` validated the evaluation-side representation, then an
independent audit correctly rejected it as insufficient for an executable
Fairlearn subject because it omitted training-side protected contexts. V2.1
therefore adds the complete aligned training split; V2.0 remains preserved as a
preliminary artifact and is not outcome-ready.

## Artifact schema

Each V2.1 `<dataset-id>.npz` contains exactly:

- `baseline_probabilities`: finite interior evaluation probabilities;
- `evaluation_labels`: aligned binary targets;
- `source_row_positions`: unique positions in the canonical loaded population;
- `protected_attribute_values`: a two-dimensional matrix in declared column order;
- `non_protected_feature_values`: the aligned raw evaluation feature matrix;
- `training_labels`: the complete aligned training targets;
- `training_source_row_positions`: unique canonical training positions;
- `training_protected_attribute_values`: the complete training protected matrix;
- `training_non_protected_feature_values`: the complete raw training feature matrix.

Heterogeneous table values use canonical JSON scalar tokens, never pickle.
Metadata records separate training/evaluation group counts and alignment
digests, plus the exact loaded protected columns, registry semantics,
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
- overlap between training and evaluation source positions, or omission of the
  complete training split;
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
The preliminary V2.0 manifest and external validation hashes are recorded in
the hourly ledger. V2.1 was then prepared under clean commit
`d0790b30d09fcc22721dfd5942ec9ef0db76cb35` at the distinct immutable PC2 path
`datasets/prepared_v2/d0790b3`. Independent validation rechecked all source
bytes and arrays. Validation JSON SHA-256:
`652a4299461a7ba58d5443f67b81a899ea529e5c9abe87eccf429fedb3cb8723`;
manifest SHA-256:
`b07bf1aa17e37bc02971e200fb7c7e6eed14584d8920573f966fc56399acaf39`.
The directory occupies 6.2 MiB.

Representation readiness is not outcome readiness. Adult, COMPAS, and Law
School expose low-cardinality categorical joint groups (10, 4, and 4 supported
training groups under the raw representation). German and Default Credit expose
83 and 102 supported raw joint groups because age is retained numerically;
Bank similarly has 68 single-attribute age groups. Any analysis must freeze a
semantically justified age transformation and support rule before observing
old/new Fairlearn outcomes. The validator now reports
`readiness_scope=representation-only` and `outcome_ready=false` explicitly.

The downstream analysis question and transforms are now frozen separately in
`docs/FAIRLEARN_PUBLIC_V2_ANALYSIS_PREREGISTRATION.md` and its machine-readable
configuration. A pre-outcome audit found that V2.1 feature tokens reproduce the
stored score model exactly on six datasets but not MEPS because dataframe dtype
semantics are not preserved. Therefore a separately versioned, non-overwriting
training/evaluation score companion is required before any executable-subject
outcome. This does not weaken V2.1's representation claim and does prevent an
unreproducible model refit from entering the evidence chain.

That companion is now complete as schema
`tfoesuu-public-score-companion-v2.2`. Its seven evaluation score vectors
reproduce V2.1 exactly, including MEPS because generation uses the original
source dataframe dtypes rather than inferred token types. The manifest and
external validation hashes are frozen in the downstream preregistration.
Readiness remains score-replay-only and does not authorize subject outcomes.

## Subsequent authorized outcome and admission

After the protocol, source identities, score companion, approval record, and
historical runtimes were frozen, the bounded seven-dataset old/new campaign was
explicitly authorized and completed. The admitted, repository-facing summary
is `data/fairlearn_public_v2_results_v1.json`. Its validation object binds 14
old/new records to runner commit
`ade8ff3d8b764a4cbda7d06bbf062650542c5530`, input-bundle manifest SHA-256
`2435e006a8a445e0e94e7248745f5ce9b1349361d4b49b7ffd18488bcebc686e`,
and the frozen protocol/registry artifacts. The repair matches the canonical
protected-tuple control on all seven populations. The parent differs on Adult
and Default Credit and is exactly zero on the remaining five.

This completion does not retroactively make V1 executable, authorize a larger
campaign, or turn the result into a causal-fairness estimate. The raw datasets
and historical runtime outputs remain external frozen evidence rather than Git
content.
