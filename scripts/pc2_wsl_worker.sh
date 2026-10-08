#!/usr/bin/env bash
# TFOESUU PC2 WSL worker. Run interactively or via Windows OpenSSH.
# Never installs drivers, pulls code, or silently starts long GPU runs.
set -euo pipefail

mode="$1"
expected_sha="${2:-}"
repo="$HOME/work/tfoesuu"
store="/mnt/d/Rocky Work/TFOESUU"

say() { printf '[pc2] %s\n' "$*"; }
die() { printf '[pc2] ERROR: %s\n' "$*" >&2; exit 2; }

[[ -d "$repo/.git" ]] || die "clone repo into $repo first"
[[ -d "$store" ]] || die "missing data folder: $store"
cd "$repo"

sha="$(git rev-parse HEAD)"
short="$(git rev-parse --short=12 HEAD)"
say "mode=$mode host=$(hostname) user=$(id -un)"
say "repository=$repo"
say "source_commit=$sha"
say "data_store=$store"

if [[ -n "$expected_sha" && "$expected_sha" != "$sha" ]]; then
  die "PC1 requested $expected_sha but PC2 has $sha; synchronize main first"
fi

case "$mode" in
  status)
    git status --short
    df -h "$store"
    if [[ -x /usr/lib/wsl/lib/nvidia-smi ]]; then
      /usr/lib/wsl/lib/nvidia-smi
    elif command -v nvidia-smi >/dev/null 2>&1; then
      nvidia-smi
    else
      say "nvidia-smi missing; verify Windows driver and WSL CUDA"
    fi
    if [[ -x .venv/bin/python ]]; then
      .venv/bin/python scripts/verify_environment.py
    else
      say "Python virtual environment not configured at $repo/.venv"
    fi
    ;;
  preflight|smoke-p12|smoke-p15|smoke-gaussian)
    [[ "$(git branch --show-current)" == "main" ]] || die "worker requires branch main"
    [[ -z "$(git status --porcelain --untracked-files=normal)" ]] || die "worktree is dirty"
    python="$repo/.venv/bin/python"
    [[ -x "$python" ]] || die "missing .venv; install Python dependencies first"
    "$python" -c 'import torch; assert torch.cuda.is_available(), "CUDA unavailable"; x=torch.binomial(torch.full((8,), 2.0, device="cuda:0"), torch.full((8,), 0.5, device="cuda:0")); print("CUDA binomial OK:", x.tolist())'
    if [[ "$mode" == preflight ]]; then
      "$python" -m compileall -q src scripts experiments tests
      "$python" scripts/validate_benchmark_inventory.py
      "$python" -m pytest -q
      say "preflight passed for $sha"
      exit 0
    fi

    mkdir -p "$store/results" "$store/logs"
    stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    name="$mode-$short-$stamp"
    output="$store/results/$name.jsonl"
    log="$store/logs/$name.log"

    case "$mode" in
      smoke-p12)
        manifest="data/replay_benchmark_v1.jsonl"
        script="experiments/gpu_replay_sweep.py"
        ;;
      smoke-p15)
        manifest="data/counterfactual_replay_benchmark_v1.jsonl"
        script="experiments/gpu_counterfactual_sweep.py"
        ;;
      smoke-gaussian)
        manifest="data/benchmark_v1.jsonl"
        script="experiments/gpu_sweep.py"
        ;;
    esac
    {
      say "UTC_start=$stamp source=$sha"
      say "manifest=$manifest manifest_sha256=$(sha256sum "$manifest" | cut -d ' ' -f1)"
      "$python" scripts/verify_environment.py
      say "launching 1000 exploratory trials per frozen configuration"
      "$python" "$script" --devices 0 --trials 1000 --benchmark "$manifest" --output "$output"
      sha256sum "$output" "$manifest"
    } 2>&1 | tee "$log"
    say "finished result=$output log=$log"
    ;;
  *)
    die "usage: $0 {status|preflight|smoke-p12|smoke-p15|smoke-gaussian} [expected_git_sha]"
    ;;
esac
