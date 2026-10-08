# TFOESUU PC1 Windows bootstrap for one RTX 5070 Ti GPU.
# Explicitly invoked only; no remote jobs, driver changes, or long sweeps.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if (-not (Test-Path ".git")) {
        throw "Run from a real Git clone of TFOESUU"
    }
    $branch = (& git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or $branch -ne "main") {
        throw "Checkout main before running the PC1 bootstrap"
    }
    $dirty = & git status --porcelain
    if ($LASTEXITCODE -ne 0 -or $dirty) {
        throw "The repository contains uncommitted changes; review them first"
    }
    $sha = (& git rev-parse HEAD).Trim()
    Write-Host "[PC1] Source commit: $sha"
    Write-Host "[PC1] Workspace: $repoRoot"
    & nvidia-smi
    if ($LASTEXITCODE -ne 0) { throw "nvidia-smi failed" }

    if (-not (Test-Path ".venv\Scripts\python.exe")) {
        Write-Host "[PC1] Creating isolated Python 3.11 environment"
        & py -3.11 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Cannot create Python 3.11 virtual environment" }
    }
    $python = Join-Path $repoRoot ".venv\Scripts\python.exe"
    & $python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
    & $python -m pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) { throw "Development dependencies failed" }
    & $python -m pip install -e .
    if ($LASTEXITCODE -ne 0) { throw "Editable project installation failed" }

    # Official Blackwell-compatible PyTorch CUDA 13.0 wheel.
    & $python -m pip install "torch==2.12.1" --index-url "https://download.pytorch.org/whl/cu130"
    if ($LASTEXITCODE -ne 0) { throw "CUDA PyTorch installation failed" }
    & $python -m pip install -r requirements-gpu.txt
    if ($LASTEXITCODE -ne 0) { throw "GPU requirements failed" }

    & $python scripts/verify_environment.py
    if ($LASTEXITCODE -ne 0) { throw "Environment report failed" }
    $torchSmoke = @'
import torch
assert torch.cuda.is_available(), "PyTorch CUDA is unavailable"
print("GPU:", torch.cuda.get_device_name(0))
print("PyTorch:", torch.__version__, "CUDA wheel:", torch.version.cuda)
x = torch.binomial(torch.full((8,), 2.0, device="cuda:0"), torch.full((8,), 0.5, device="cuda:0"))
torch.cuda.synchronize()
print("CUDA binomial smoke:", x.cpu().tolist())
'@
    $torchSmoke | & $python -
    if ($LASTEXITCODE -ne 0) { throw "CUDA kernel smoke failed" }

    & $python -m compileall -q src scripts experiments tests
    if ($LASTEXITCODE -ne 0) { throw "Python compilation failed" }
    & $python scripts/validate_benchmark_inventory.py
    if ($LASTEXITCODE -ne 0) { throw "Frozen benchmark inventory failed" }
    & $python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw "TFOESUU tests failed" }
    Write-Host "[PC1] SETUP/PREFLIGHT PASSED for $sha"
    Write-Host "[PC1] No GPU sweep or PC2 job was started"
}
finally {
    Pop-Location
}
