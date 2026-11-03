# Reproduction bundles

This directory preserves executable evidence for TFOESUU without storing the manuscript or its publisher templates.

- [P12/P15 finite-law validation](p12_p15/evidence/README.md): 198 frozen configurations, two sets of 100,000 trials per configuration, and 594 exact-law comparisons. The manifest records original runner/spec paths and historical source identities; a complete Git history is required.
- [P19 independent synthetic replay](p19_simple_null/README_RESEARCH_AUDIT.md): 57,600 deterministic trajectories, measured numbers of four-execution tape rounds, and explicit null/alternative contracts.
- [Unknown shared-nuisance exact audit](unknown_shared_nuisance/README.md): exact rational transcript calculations, strict-domain guards, and a shifted-support counterexample.

**Do not infer:** measured general software speedup, a proof of theorem optimality, a causal fairness claim, or validation of unrestricted composite nuisance. The exact reference laws and observed outcomes are distinct types of evidence.

## Commands from repository root

```bash
python -m pip install -e ".[dev]"
python scripts/validate_preview_results.py reproducibility/p12_p15/evidence/p12_p15_100k_preview_manifest_v1.json --base-dir reproducibility/p12_p15
python -m pytest -q reproducibility/p19_simple_null/test_p19_audit.py
(cd reproducibility/unknown_shared_nuisance && python -m unittest -q test_exact_witness_audit.py)
```

The archived result/spec/script blobs are referenced by their original Git object IDs, preserving content identity. They were not regenerated, manually edited, or silently relabeled as new experiments. Some historical metadata refer to the earlier execution machines; these are provenance records, not paths expected to exist on a reviewer's machine.

The manuscript is stored separately. Deleting it from this working tree **does not erase historical Git blobs** from the private source repository.
