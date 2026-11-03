# P12/P15 archived finite-law evidence

The `evidence/` directory is a byte-for-byte copy of the original manifest, validation report, source snapshots, results, and specifications. For reproducible validation, the same blobs also appear at their historical relative paths under `data/`, `experiments/`, and `results/` in this bundle. This is intentional: the original admission manifest identifies those paths and historic Git blob IDs.

```bash
python scripts/validate_preview_results.py reproducibility/p12_p15/evidence/p12_p15_100k_preview_manifest_v1.json --base-dir reproducibility/p12_p15
```

**Prerequisites:** run from a full Git clone with access to original source commit `149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b`. Shallow clones may fail the historical ancestry check. The source/runners/results are a frozen 2026 campaign; its result rows are not executable-program timing measurements. Do not rebrand these finite-law audits as observed complexity exponents. All original SHA-256 and Git blob identities remain in the manifest.

Readers who only want a quick smoke can skip this full historical verification and run the small tests in [the reviewer guide](../../docs/REVIEWER_GUIDE.md).
