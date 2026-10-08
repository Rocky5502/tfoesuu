# Public benchmark loader metadata consistency audit — 2026-10-08

## Scope and diagnosis

The two-PC setup at base revision `2622f3e879b9a6f04fc548e298b8ce1f41348c45` independently reported `193 passed, 1 failed` in pytest. The sole failure was `tests/test_public_benchmarks.py::test_public_benchmark_registry_roundtrip`, caused by disagreement between four `loader_family` values in the committed `data/public_benchmark_registry_v1.jsonl` and the Python registry function.

The authoritative implementation in `scripts/prepare_public_benchmarks.py` uses `aif360.sklearn.datasets.fetch_adult`, `fetch_bank`, `fetch_german`, and `fetch_compas` for the corresponding datasets; it uses `ucimlrepo.fetch_ucirepo(id=350)` for Default Credit. The `loader_family` field denotes the **actual software fetcher**, not the source organization of the archived dataset. Thus the committed file's old `uci` / `propublica` loader labels were stale.

## Controlled metadata-only correction

- `public-adult`: `uci` → `aif360`
- `public-bank`: `uci` → `aif360`
- `public-german`: `uci` → `aif360`
- `public-compas`: `propublica` → `aif360`

No other field or row is changed. Dataset identities, seven-row inventory, source names, source URLs, DOIs, protected attributes, status, and experiment data remain identical. This is an explicit amendment to a previously committed `v1` metadata registry, **not a fresh benchmark experiment or evidence of publication readiness**. The Git blob SHA and any recorded registry file checksum change; re-freeze the manifest checksum and source commit for future experiment provenance after review/merge.

## Verification gates

Before merging or launching experiments, review this diff. After merge, synchronize PC1 and PC2 to the same resulting commit and re-run on **both**:

```bash
python scripts/validate_benchmark_inventory.py
python -m pytest -q
```

Do not assert a green 194-test suite until actual machine output confirms it. This audit does not address the separate PC2 Git HTTPS CA trust failure (the original checkout was recovered by an SSH-transferred Git bundle).
