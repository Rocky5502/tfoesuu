#!/usr/bin/env bash
# Safe, reproducible PC2 WSL2 bootstrap (RTX 5070 Ti).
# Runs only when explicitly invoked by the user. Never changes drivers.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd -P)"
store="/mnt/d/Rocky Work/TFOESUU"
cd "$root"

say() { printf '[pc2 setup] %s\n' "$*"; }
die() { printf '[pc2 setup] ERROR: %s\n' "$*" >&2; exit 2; }

[[ -d .git ]] || die "run from the Git checkout; .git not found"
[[ -d "$store" ]] || die "missing PC2 Windows data directory $store"
[[ "$(git branch --show-current)" == "main" ]] || die "checkout main first"
[[ -z "$(git status --porcelain --untracked-files=normal)" ]] ||
  die "working tree contains uncommitted/untracked changes"
command -v python3 >/dev/null || die "python3 missing"
command -v git >/dev/null || die "git missing"
command -v /usr/lib/wsl/lib/nvidia-smi >/dev/null ||
  say "nvidia-smi not found at canonical WSL path; verify PC2 driver"

say "Host $(hostname), user $(id -un), Python $(python3 --version 2>&1)"
say "Git $(git rev-parse HEAD)"
say "Data store: $store"
mkdir -p "$store/results" "$store/logs" "$store/datasets"

if [[ ! -x .venv/bin/python ]]; then
  say "Creating isolated Python virtual environment"
  if ! python3 -m venv .venv; then
    die "Python venv unavailable: install python3-venv (or matching Python version) then retry"
  fi
else
  say "Reusing existing .venv"
fi

python="$root/.venv/bin/python"
"$python" -m pip install --upgrade pip
"$python" -m pip install -r requirements-dev.txt
"$python" -m pip install -e .

# Driver 591.86 / WSL CUDA 13.1 supports the official cu130 wheel.
# Use an explicit reviewed version rather than an unbounded nightly.
"$python" -m pip install 'torch==2.12.1' --index-url https://download.pytorch.org/whl/cu130
"$python" -m pip install -r requirements-gpu.txt

say "Checking GPU, CUDA runtime and PyTorch binomial kernel"
"$python" scripts/verify_environment.py
"$python" - <<'PY'
import torch
assert torch.cuda.is_available(), "CUDA unavailable in PyTorch"
assert torch.cuda.device_count() >= 1, "No CUDA devices"
print("GPU:", torch.cuda.get_device_name(0))
print("PyTorch:", torch.__version__, "wheel CUDA:", torch.version.cuda)
print("Compute capability:", torch.cuda.get_device_capability(0))
total = torch.full((16,), 3.0, device="cuda:0")
prob = torch.full((16,), 0.25, device="cuda:0")
observed = torch.binomial(total, prob)
torch.cuda.synchronize()
print("CUDA binomial smoke:", observed.cpu().tolist())
PY
say "Checking Python syntax, frozen manifests and unit tests"
"$python" -m compileall -q src scripts experiments tests
"$python" scripts/validate_benchmark_inventory.py
"$python" -m pytest -q

say "PC2 setup and local preflight PASSED for $(git rev-parse HEAD)"
say "Next, configure the PC1 checkout and use the status-only SSH dispatcher."
