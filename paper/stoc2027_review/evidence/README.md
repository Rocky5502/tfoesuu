# Frozen P12/P15 oracle-validation evidence

These files are the complete admitted 100,000-trial-per-configuration P12/P15
records used by the manuscript. They validate sufficient-statistic simulators
against exact finite Bernoulli laws; they do not measure executable-software
runtime and do not prove the paper's theorems.

- `p12_100k_results.jsonl`: 54 configurations; SHA-256
  `f00458f50d225c8c5bde5cb235c6f67fbc67102157768369df8cd350956f1035`.
- `p15_100k_results.jsonl`: 144 configurations; SHA-256
  `e0750e5d46215909aa710d83bca8ad748877e66f786aa9106e883ce94da274ab`.
- `p12_p15_100k_preview_manifest_v1.json`: source commit, specification and
  runner identities, expected row counts, and admission policy.
- `p12_p15_100k_preview_validation_v1.json`: independent exact-law validation;
  SHA-256
  `32ea2d88d6475c4880d607e13023151e3f84c4a78eac05ee5e0be64b37d5c9c5`.
- `replay_benchmark_v1.jsonl` and `counterfactual_replay_benchmark_v1.jsonl`:
  frozen P12/P15 specifications.
- `gpu_replay_sweep_source_snapshot.py` and
  `gpu_counterfactual_sweep_source_snapshot.py`: byte-identical snapshots of
  the admitted runners; their SHA-256 hashes match the manifest.
- `validate_preview_results.py`: a convenience copy of the repository
  validator. Run it from the full repository, where it imports the versioned
  `tfoesuu.preview_results` module; this evidence folder is archival rather
  than a standalone Python environment.

The manifest binds the runs to source revision
`149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`. The repository validator is
`scripts/validate_preview_results.py`; raw result paths can be overridden when
the files are stored outside the source tree.
