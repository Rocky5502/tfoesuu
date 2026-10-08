# Tomorrow GPU checklist — TFOESUU STOC 2027

Use this checklist from a clean checkout of the frozen experiment commit. Use the live consolidated `main` branch (P1--P19 audited, P20 conjectural).
Do not edit code between public-data preparation and the corresponding result run. If code must change, commit it first and re-prepare the datasets so the preparation SHA matches the run SHA.

## 0. Freeze the source

```powershell
git switch main
git pull --ff-only origin main
git status --short
git rev-parse HEAD
```

`git status --short` must be empty before continuing.

## 1. Core CPU gates

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
python scripts/validate_benchmark_inventory.py
pytest -q
python scripts/check_bibliography.py
python scripts/check_paper_consistency.py
python scripts/summarize_submission_evidence.py --output results/submission_evidence.json
```

Stop on the first failure. Do not start a GPU run around a red CPU gate.

## 2. Verify CUDA

Install the CUDA-enabled PyTorch build recommended by the current PyTorch selector for the installed NVIDIA driver, then:

```powershell
pip install -r requirements-gpu.txt
python scripts/verify_environment.py
nvidia-smi
```

Record GPU model, driver, CUDA/PyTorch versions, and the source SHA.

## 3. Install the optional public-data layer

```powershell
pip install -r requirements-public.txt
```

Before using MEPS, read the AHRQ/MEPS access terms. The preparation script requires the explicit `--accept-meps-terms` flag and will not silently accept them.

## 4. Prepare the seven public datasets from the frozen commit

Start with 1024 evaluation contexts for the smoke/publication-preview ladder:

```powershell
python scripts/prepare_public_benchmarks.py --max-contexts 1024 --accept-meps-terms
```

Inspect `data/public_prepared/prepared_manifest.json`. It must contain seven dataset entries and each entry must record the current `preparation_source_commit`.

## 5. Gate A — 1,000 trials, one patch size

```powershell
python experiments/gpu_public_replay_sweep.py --device cuda:0 --trials 1000 --patch-size 0.05 --output results/public_smoke_1k.jsonl
python scripts/validate_public_results.py --results results/public_smoke_1k.jsonl --require-datasets 7
```

Check that every dataset has all five access regimes and that no error rate obviously violates the intended confidence behavior. This is a code/protocol smoke test, not publication evidence.

## 6. Gate B — 10,000 trials, three patch sizes

```powershell
python experiments/gpu_public_replay_sweep.py --device cuda:0 --trials 10000 --patch-size 0.05 --patch-size 0.02 --patch-size 0.01 --output results/public_preview_10k.jsonl
python scripts/validate_public_results.py --results results/public_preview_10k.jsonl --require-datasets 7
python scripts/render_public_results.py --results results/public_preview_10k.jsonl --output results/public_preview_10k.pdf --png-output results/public_preview_10k.png
python scripts/render_public_results_table.py --results results/public_preview_10k.jsonl --output results/public_preview_table.tex --patch-size 0.01
```

Use this stage to inspect finite-instance behavior, plot legibility, GPU memory, and runtime. Do not copy preview numbers into the manuscript.

## 7. Gate C — 100,000-trial frozen publication preview

Only if Gates A and B pass without source changes:

```powershell
python experiments/gpu_public_replay_sweep.py --device cuda:0 --trials 100000 --patch-size 0.05 --patch-size 0.02 --patch-size 0.01 --output results/public_replay_100k.jsonl
python scripts/validate_public_results.py --results results/public_replay_100k.jsonl --require-datasets 7
python scripts/render_public_results.py --results results/public_replay_100k.jsonl --output paper/figures/public_results.pdf --png-output paper/figures/public_results.png
python scripts/render_public_results_table.py --results results/public_replay_100k.jsonl --output paper/generated/public_results_table.tex --patch-size 0.01
```

The manuscript automatically uses `paper/figures/public_results.pdf` when it exists and always inputs `paper/generated/public_results_table.tex`.

## 8. Rebuild and inspect the paper

```powershell
python scripts/check_bibliography.py
python scripts/check_paper_consistency.py
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
cd ..
```

Inspect the PDF at 100% size. Check the overview figure, gray algorithm box, seven-dataset table, main result table, 4-panel result figure, captions, theorem cross-references, and bibliography. Result figures must remain legible in grayscale.

## 9. Freeze provenance

Record the public result run with the repository provenance tooling and hash the final bundle. At minimum preserve:

- source git SHA and clean/dirty status;
- prepared dataset SHA-256 values;
- split/preparation seed;
- exact commands;
- trial count and patch sizes;
- GPU/driver/CUDA/PyTorch versions;
- result JSONL SHA-256;
- generated table/figure hashes;
- compiled PDF hash.

Do not change the theorem status because an experiment looks good. P17 heterogeneous/composite-null replay remains OPEN until a separate proof/audit gate succeeds.

## 10. Escalation after the 100k preview

Increase to 4096 contexts and/or 1e6 trials only if the 100k results show that additional resolution is scientifically necessary (for example, rare-error confidence intervals are still too wide). Re-prepare from the same frozen source commit when changing the context cap, and archive the new prepared-data hashes as a distinct protocol version.