# PC1 Windows PowerShell dispatcher for PC2's WSL2 TFOESUU worker.
# Uses the pre-existing Windows OpenSSH connection. No passwords or keys stored.
param(
    [ValidateSet("status", "preflight", "smoke-p12", "smoke-p15", "smoke-gaussian")]
    [string]$Mode = "status",
    [string]$PC2Host = $env:TFOESUU_PC2_HOST,
    [string]$RemoteUser = $env:TFOESUU_PC2_USER,
    [string]$KeyFile = "$env:USERPROFILE\.ssh\id_ed25519"
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($PC2Host) -or [string]::IsNullOrWhiteSpace($RemoteUser)) {
    throw "Set TFOESUU_PC2_HOST and TFOESUU_PC2_USER or pass -PC2Host and -RemoteUser explicitly"
}
if ($PC2Host -notmatch "^[A-Za-z0-9][A-Za-z0-9.:-]*$" -or $RemoteUser -notmatch "^[A-Za-z_][A-Za-z0-9_.-]*$") {
    throw "Invalid PC2 host or remote user argument"
}
if (-not (Test-Path -LiteralPath $KeyFile)) {
    throw "SSH private key not found at $KeyFile"
}
if (-not (Get-Command ssh.exe -ErrorAction SilentlyContinue)) {
    throw "Windows OpenSSH client ssh.exe not available"
}
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    $sourceSha = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $sourceSha -notmatch '^[0-9a-f]{40}$') {
        throw "Cannot determine PC1 source commit"
    }
    $branch = (& git branch --show-current).Trim()
    if ($Mode -ne "status" -and $branch -ne "main") {
        throw "PC1 must use main for execution dispatch"
    }
    if ($Mode -ne "status") {
        $dirty = (& git status --porcelain)
        if ($dirty) { throw "PC1 working tree must be clean before dispatch" }
    }
    Write-Host "[pc1] mode=$Mode expected_commit=$sourceSha PC2=$PC2Host"
    $command = "wsl.exe -e bash /home/zbq/work/tfoesuu/scripts/pc2_wsl_worker.sh $Mode $sourceSha"
    & ssh.exe -i $KeyFile -o BatchMode=yes -o ConnectTimeout=10 "$RemoteUser@$PC2Host" $command
    if ($LASTEXITCODE -ne 0) {
        throw "Remote worker command failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
