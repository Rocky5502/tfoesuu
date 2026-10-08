# Local NVIDIA GPU runbook

The GPUs are for **our own simulation and optimization only**. No pretrained model, model API, or model inference is used.

## 0. Single-Blackwell-GPU launch gate (October 2026)

**Decision: ready to attempt a local 1,000-trial smoke, not yet cleared for
unattended publication sweeps.** GitHub CI has repeatedly failed before
runner assignment, so local tests and the full LaTeX build are unverified.
Do not interpret a GPU successfully running a script as evidence that all
theorems, benchmarks and publication claims pass.

Confirm the **actual GPU name and VRAM with `nvidia-smi`**; do not infer it
from a colloquial product name. NVIDIA's current GeForce 50-series public
lineup lists the RTX 5080 and RTX 5070 Ti separately. Use `--devices 0`
for one GPU; only use `--devices 0,1` if there really are two distinct
CUDA devices reported by PyTorch.

From a clean Windows PowerShell clone:

```powershell
git switch main
git pull --ff-only
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
# Install CUDA-enabled torch using the command from https://pytorch.org/get-started/locally/
# Choose Windows, Pip, Python, Stable, and a driver-compatible CUDA build.
python -m pip install -r requirements-gpu.txt
nvidia-smi
python scripts/verify_environment.py
python -c "import torch; assert torch.cuda.is_available(); x=torch.randn(1024,device='cuda:0'); print(torch.cuda.get_device_name(0),float(x.sum()))"
python -m compileall -q src scripts experiments tests
python scripts/validate_benchmark_inventory.py
python -m pytest -q
```

**Gate 0:** Verify CUDA is available, the installed device identity matches
`nvidia-smi`, the CUDA tensor smoke runs, and all CPU tests/inventory checks
pass. Resolve failing tests before GPU experiments. The CUDA `torch.binomial`
kernel is important for the existing Bernoulli sweeps and should be exercised
by a small replay smoke before increasing trial counts.

**Gate 1:** Run 1,000-trial one-GPU theorem-aligned smoke experiments, all from
the frozen checked-in manifests. These outputs are exploratory only:

```powershell
python experiments/gpu_replay_sweep.py --devices 0 --trials 1000 --benchmark data/replay_benchmark_v1.jsonl --output results/smoke_p12_1k.jsonl
python experiments/gpu_counterfactual_sweep.py --devices 0 --trials 1000 --benchmark data/counterfactual_replay_benchmark_v1.jsonl --output results/smoke_p15_1k.jsonl
python experiments/gpu_sweep.py --devices 0 --trials 1000 --benchmark data/benchmark_v1.jsonl --output results/smoke_gaussian_1k.jsonl
```

**Gate 2:** Check exact row counts, errors, file integrity, and provenance.
Record the source SHA, driver, CUDA/PyTorch versions, manifest checksums,
raw job logs and output checksums. Increase to 10,000, then 100,000 trials
only if the previous stage is sound. Never append a different trial budget
to an existing resumable `*.gpu0.jsonl` shard: choose a NEW output basename
when changing trials, code, manifest or seed. Otherwise the resume logic
will silently mix old and new experiment configurations.

The separate **seven-public-dataset** sweep is not launch-ready until
datasets are locally prepared, the registry and SHA-256s are verified,
the trial-count/method-grid release gates pass, and the GPU smoke succeeds.
A prepared manifest row is not a measured result.

**Do not regenerate a checked-in frozen manifest in-place as a prerequisite.**
A regeneration audit should write to a temporary/results path and compare
it to the frozen source without modifying the checkout. The former examples
below target two GPUs and should be used only when two devices are present.

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
pip install -r requirements-dev.txt
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
python scripts/generate_replay_benchmark.py --output data/replay_benchmark_v1.jsonl
python scripts/generate_counterfactual_benchmark.py --output data/counterfactual_replay_benchmark_v1.jsonl
python scripts/generate_partial_replay_benchmark.py --output data/partial_replay_benchmark_v1.jsonl
python scripts/generate_partial_replay_structural_cases.py --output data/partial_replay_structural_cases_v1.jsonl
python experiments/validate_partial_replay_manifest.py --benchmark data/partial_replay_benchmark_v1.jsonl
python experiments/gpu_sweep.py --devices 0 --trials 10000 --benchmark data/benchmark_v1.jsonl --output results/smoke_gaussian.jsonl
python experiments/gpu_replay_sweep.py --devices 0 --trials 10000 --benchmark data/replay_benchmark_v1.jsonl --output results/smoke_replay.jsonl
```

Inspect error rates and logs before increasing the budget.

## 4. Two-GPU theorem-stress runs

Gaussian graph allocation:

```powershell
python experiments/gpu_sweep.py --devices 0,1 --trials 1000000 --benchmark data/benchmark_v1.jsonl --output results/gpu_sweep_1m.jsonl
```

Bernoulli replay separation:

```powershell
python experiments/gpu_replay_sweep.py --devices 0,1 --trials 1000000 --benchmark data/replay_benchmark_v1.jsonl --output results/replay_gpu_sweep_1m.jsonl
```

Four-way counterfactual replay with nonzero shared patch effects (P15):

```powershell
python experiments/gpu_counterfactual_sweep.py --devices 0,1 --trials 1000000 --benchmark data/counterfactual_replay_benchmark_v1.jsonl --output results/counterfactual_gpu_sweep_1m.jsonl
```

Each launcher writes one shard per GPU and merges them deterministically. Completed benchmark IDs are skipped on restart, so interrupted runs resume rather than overwrite completed work.

### P17 partial replay does not need Monte Carlo for the scoped theorem

For the frozen homogeneous single-changed-endpoint P17 family, the rounded
raw-contrast schedule has an **exact** endpoint-wise miss probability:
`(1-d)^N_x`.  The 168-row CPU validator computes this quantity directly for
every active endpoint and verifies it is at most `beta`.  Do not spend GPU
budget estimating this exact probability by Monte Carlo merely to reproduce the
theorem.

GPU work related to P17 should instead target questions that are genuinely
unresolved: heterogeneous/composite fairness-preserving nulls, candidate
contrast-safe control structures, and counterexamples to proposed broader
decision geometries.

## 5. Month-scale policy

Do **not** simply run one configuration for a month. Use staged budgets:

- Gate 0: (10^3) trials/config — detect code errors.
- Gate 1: (10^4) — reject obviously wrong conjectures.
- Gate 2: (10^5) — stabilize curves and identify hard regimes.
- Gate 3: (10^6)–(10^7) — rare-error and constant-factor checks for frozen theorems.
- Gate 4: only after theorem freeze, run publication-quality sweeps.

For the replay theorem, prioritize shrinking patch sizes `d` before merely increasing trial counts. The key falsification target is the predicted exponent gap:

- paired replay: cost proportional to `d^-1`;
- independent replay: cost proportional to `d^-2`.

The original replay grid spans `d=0.1` down to `d=0.002`. The frozen P15 counterfactual grid adds 144 configurations over multiple baselines, shared-patch sizes, `d` down to `0.001`, and two confidence levels.

Record:

- git commit SHA;
- GPU names and driver;
- PyTorch/CUDA versions;
- command line;
- benchmark manifest checksum;
- result checksum.

## 6. What the GPUs should search for

High-value computation:

- heterogeneous variance patterns that break guessed Gaussian closed forms;
- graph families that maximize `Psi` under fixed `n,m`;
- cases where a proposed adaptive heuristic loses badly;
- coupled-vs-independent replay ratios under varying correlation;
- Bernoulli small-patch regimes where the predicted linear-vs-quadratic exponents fail;
- finite-`d` regimes where asymptotic constants are misleading;
- numerical counterexamples to any proposed simplification of the dual;
- candidate graph-level Bernoulli constructions for the next theorem;
- heterogeneous/composite-null P17 instances that break naive raw-contrast extensions or suggest a sharper decision geometry.

Low-value computation:

- decorative large sweeps with no theorem question;
- training or running AI models;
- repeating already-settled curves only to obtain more points;
- Monte Carlo estimation of the scoped homogeneous P17 miss probability, which is available exactly from the rounded schedule.

## 7. Publication gate

Do not treat a GPU curve as evidence of a theorem. A publication figure may illustrate a statement only after:

1. the theorem statement is frozen;
2. the proof is audited;
3. the exact repository commit is recorded;
4. the sweep manifest is frozen;
5. reruns on both GPUs agree within Monte Carlo uncertainty;
6. each publication result has a `record_publication_run.py` provenance record;
7. the final bundle is hashed with `scripts/freeze_submission_artifacts.py --require-clean`, attaching the compiled PDF and real result/provenance files with `--extra-file`.


## Public benchmark publication run

Install the optional public-data layer after the core environment is green:

```powershell
pip install -r requirements-public.txt
```

Prepare the seven registered datasets. MEPS requires explicit acceptance of the AHRQ terms and is never accepted silently by the script:

```powershell
python scripts/prepare_public_benchmarks.py --max-contexts 4096 --accept-meps-terms
```

Validate the complete prepared directory and capture its read-only byte-hash report before execution:

```powershell
python scripts/validate_prepared_public_benchmarks.py `
  'D:\Rocky Work\TFOESUU\datasets\prepared' `
  --expected-source-commit (git rev-parse HEAD)
```

The GPU runner invokes the same strict validator and fails before CUDA work if any registered
dataset, manifest row, metadata field, probability vector, label vector, or source commit is
incoherent.

Run a single-GPU smoke test before the full sweep:

```powershell
python experiments/gpu_public_replay_sweep.py --device cuda:0 --trials 1000 --patch-size 0.05 --output results/public_smoke.jsonl
```

If the smoke result validates, run the frozen publication preview:

```powershell
python experiments/gpu_public_replay_sweep.py --device cuda:0 --trials 100000 --patch-size 0.05 --patch-size 0.02 --patch-size 0.01 --output results/public_replay_100k.jsonl
python scripts/render_public_results.py --results results/public_replay_100k.jsonl --output paper/figures/public_results.pdf --png-output paper/figures/public_results.png
```

The public sweep compares execution-access regimes, not predictive models. The base predictor is local and uses non-protected features only. Each scalar evaluation probability is duplicated into a synthetic two-endpoint edge; v1 does not materialize protected-attribute counterfactual pairs. The patch is injected in the executable stochastic decision wrapper so the old/new replay semantics remain controlled. Do not add a dataset, seed, or patch size after seeing results without recording the change as a new protocol version.
