# TFOESUU two-PC GPU architecture (PC1 Windows + PC2 Windows/WSL2)

Created: 2026-10-08. **Status: setup instructions only; no local hardware was accessed from ChatGPT.**

## Verified user-supplied facts

- PC1 is the controller. Windows project folder: G:\TFOESUU Project.
- PC1 already reaches PC2 through Windows OpenSSH with the existing local SSH key, over a private LAN at 192.168.103.117.
- The current remote Windows account is Administrator. Interactive entry into WSL launches Ubuntu 22.04.5 as user zbq.
- PC2 has an existing storage folder: D:\Rocky Work\TFOESUU.
- Claimed devices are two GeForce 50-series cards, one per PC. Confirm the **exact** names, VRAM, driver, and CUDA visibility on each host with nvidia-smi and PyTorch; do not infer hardware identity from a nickname.
- These are TWO SEPARATE CUDA workers. Their memories are NOT pooled, and CUDA device 1 on PC1 does not refer to the PC2 GPU.

## Recommended layout

PC1 Windows (develop and orchestrate; local GPU worker):
    G:\TFOESUU Project\tfoesuu\   (if G: root is not already a Git repository)

PC2 Ubuntu WSL2 (fast Linux working tree, venv, CUDA worker):
    /home/zbq/work/tfoesuu/

PC2 Windows D: (persistent bulk outputs, logs, prepared data):
    D:\Rocky Work\TFOESUU\
    /mnt/d/Rocky Work/TFOESUU/

Microsoft recommends keeping a Linux Git checkout and virtual environment in the WSL ext4 filesystem instead of /mnt/d for good small-file/build performance. Large result JSONL, datasets, and logs can go on D:. Keep source synchronized by Git, not live network-mounted .git.

## Step 1: run NOW in existing PC2 Ubuntu terminal

    whoami
    pwd
    ls -ld "/mnt/d/Rocky Work/TFOESUU"
    df -h /mnt/d
    /usr/lib/wsl/lib/nvidia-smi
    python3 --version
    git --version

If /usr/lib/wsl/lib/nvidia-smi is missing, try nvidia-smi and check the Windows driver first. In WSL2 the Windows NVIDIA driver supplies CUDA; **do not install a Linux display driver**. If D: is not mounted, stop and troubleshoot the WSL mount before creating paths.

## Step 2: prepare WSL2 worker checkout (PC2 Ubuntu)

    cd ~
    sudo apt-get update
    sudo apt-get install -y git python3-venv python3-pip
    mkdir -p "$HOME/work"
    cd "$HOME/work"
    git clone https://github.com/Rocky5502/tfoesuu.git
    cd tfoesuu
    git switch main
    git pull --ff-only
    mkdir -p "/mnt/d/Rocky Work/TFOESUU/results"
    mkdir -p "/mnt/d/Rocky Work/TFOESUU/logs"
    mkdir -p "/mnt/d/Rocky Work/TFOESUU/datasets"
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements-dev.txt
    python -m pip install -e .

If the repository already exists under ~/work/tfoesuu, do NOT clone a second copy: cd there, inspect git status, then fast-forward main if clean.

Install a CUDA-enabled PyTorch build from the **official PyTorch selector** for Linux/Pip and the Windows GPU driver's compatible CUDA wheel (https://pytorch.org/get-started/locally/). Then install remaining GPU requirements:

    python -m pip install -r requirements-gpu.txt
    python scripts/verify_environment.py
    python -c "import torch; assert torch.cuda.is_available(); x=torch.binomial(torch.full((8,),2.,device='cuda:0'),torch.full((8,),0.5,device='cuda:0')); print(torch.cuda.get_device_name(0), x.tolist())"

The GPU identity, CUDA detection, and CUDA binomial kernel must pass before running large experiments.

## Step 3: prepare PC1 Windows checkout

Open a NEW PC1 Windows PowerShell terminal (outside the existing SSH/WSL session).

    Set-Location 'G:\TFOESUU Project'
    git status --short

If G:\TFOESUU Project already IS the TFOESUU Git checkout, run git switch main and git pull --ff-only there. Otherwise clone into a NEW subdirectory, leaving existing files undisturbed:

    git clone https://github.com/Rocky5502/tfoesuu.git tfoesuu
    Set-Location .\tfoesuu
    git switch main
    git pull --ff-only

Install Python/torch locally on PC1 separately using the GPU runbook. A working Python environment on PC2 does not install anything on PC1.

## Step 4: verify remote command dispatch

After BOTH checkouts have the SAME commit:

    .\scripts\pc1_dispatch_pc2.ps1 -Mode status
    .\scripts\pc1_dispatch_pc2.ps1 -Mode preflight

The PowerShell launcher invokes PC2's existing Windows OpenSSH service, then runs an Ubuntu script using Windows wsl.exe. It uses your local key at USERPROFILE\.ssh\id_ed25519, does not require a second Linux SSH server, and checks the full source commit before running. If PowerShell execution policy blocks scripts, inspect policy with Get-ExecutionPolicy -List and use a PROCESS-scoped RemoteSigned policy if appropriate.

Without the dispatcher, basic direct SSH still works:

    ssh -i "$env:USERPROFILE\.ssh\id_ed25519" Administrator@192.168.103.117

On PC2 Windows, run wsl to enter Ubuntu again.

After successful preflight, a PC1-authorized PC2 GPU smoke can be dispatched by:

    .\scripts\pc1_dispatch_pc2.ps1 -Mode smoke-p12

Other allowed modes: smoke-p15, smoke-gaussian. Each is limited to 1,000 trials/config and saves results and logs in the designated PC2 D: folder. NO long sweep is auto-launched.

## Step 5: make both PC source revisions match before experiments

On PC1, finish edits/tests; review and commit source deliberately, then push the agreed branch to GitHub.

On PC2 WSL2:

    cd ~/work/tfoesuu
    git status --short
    git switch main
    git pull --ff-only
    git rev-parse HEAD

On PC1, compare:

    git rev-parse HEAD

The dispatcher rejects mismatches. NEVER silently git-pull while a GPU job is running, rewrite a tracked benchmark fixture, or resume a shard with a different trial budget/seed/source SHA.

## How to use Codex safely

Codex on PC1 is recommended for local code navigation, unit tests, data validation, artifact generation, Git synchronization and SSH dispatch. It is optional for the SSH setup itself. Run Codex within the Git checkout (not the entire user profile). Prefer approvals for remote commands, installs, Git writes and GPU jobs. Give it the root AGENTS.md and this runbook. Codex is a development assistant, **not** an LLM used as a TFOESUU experimental subject.

Theoretical P20 conjectures, statistical claims, peer-reviewed citations and results remain subject to independent human/proof validation. Do not give Codex permission to launch 100k/1m jobs, install drivers, modify firewall settings, or delete D: data without explicit separate approval. Consider replacing the temporary Administrator SSH login with a dedicated restricted PC2 account for ongoing automation. Keep SSH limited to trusted LAN/VPN and never commit private keys, passwords, tokens or personal data.

## Architecture boundaries

- PC1 GPU and PC2 GPU process independent job shards, not a shared-memory CUDA device.
- Each machine owns its Python environment, CUDA availability and Git checkout.
- Experiment outputs must record source SHA, manifest hash, parameters, device and environment; merge only equivalent configurations.
- The PC2 worker currently supports status, preflight and three 1,000-trial theorem smokes, nothing more.
- This runbook makes no claim that either machine has passed pytest, GPU kernels, or a complete paper build; hardware checks and scripts have to be run by the user/Codex with permission.
