# Local NVIDIA GPU runbook

The GPUs are for **our own simulation and optimization only**. No pretrained model, model API, or model inference is used.

## 1. Verify the machine first

```powershell
nvidia-smi
python scripts/verify_environment.py
```

For Blackwell-generation GeForce RTX 50-series hardware, use a recent NVIDIA driver and a PyTorch build with Blackwell support. Do not begin a month-scale sweep until `verify_environment.py` reports all intended devices.

## 2. Install CPU research dependencies

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Install the current CUDA-enabled PyTorch wheel recommended by the official PyTorch selector for the installed driver, then:

```powershell
pip install -r requirements-gpu.txt
python scripts/verify_environment.py
```

## 3. Smoke test before burning GPU

```powershell
pytest -q
python scripts/generate_benchmark.py --output data/benchmark_v1.jsonl
python experiments/gpu_sweep.py --devices 0 --trials 10000 --benchmark data/benchmark_v1.jsonl --output results/smoke.jsonl
```

Inspect error rates and logs before increasing the budget.

## 4. Two-GPU run

```powershell
python experiments/gpu_sweep.py --devices 0,1 --trials 1000000 --benchmark data/benchmark_v1.jsonl --output results/gpu_sweep_1m.jsonl
```

Each GPU writes an independent shard and the launcher merges them deterministically. Completed benchmark IDs are skipped on restart, so interrupted runs resume rather than overwrite completed work.

## 5. Month-scale policy

Do **not** simply run one configuration for a month. Use staged budgets:

- Gate 0: 10^3 trials/config — detect code errors.
- Gate 1: 10^4 — reject obviously wrong conjectures.
- Gate 2: 10^5 — stabilize curves and identify hard regimes.
- Gate 3: 10^6–10^7 — rare-error and constant-factor checks for frozen theorems.
- Gate 4: only after theorem freeze, run publication-quality sweeps.

Record:

- git commit SHA;
- GPU names and driver;
- PyTorch/CUDA versions;
- command line;
- benchmark manifest checksum;
- result checksum.

## 6. What the GPUs should search for

High-value computation:

- heterogeneous variance patterns that break guessed closed forms;
- graph families that maximize `Psi` under fixed `n,m`;
- cases where a proposed adaptive heuristic loses badly;
- coupled-vs-independent replay ratios under varying correlation;
- Bernoulli small-patch regimes where delta variance collapses;
- numerical counterexamples to any proposed simplification of the dual.

Low-value computation:

- decorative large sweeps with no theorem question;
- training or running AI models;
- repeating already-settled curves only to obtain more points.
