param([switch]$Update, [switch]$Check)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Runtime = Join-Path $Root ".runtime"

$AppPidFile = Join-Path $Runtime "pockettrack.pid"
$AppLog = Join-Path $Runtime "pockettrack.log"

$HostnameLocal = "my-pocket-track"

New-Item -ItemType Directory -Force -Path $Runtime | Out-Null

# Make the package importable regardless of the venv's .pth state. A checkout in
# a cloud-synced folder can end up with a hidden .pth, which Python skips - the
# venv looks installed but "import cardbudget" fails. Every command below, and
# the server we launch, inherits this.
$SrcPath = Join-Path $Root "src"
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$SrcPath;$env:PYTHONPATH" } else { $SrcPath }

function Say {
    param([string]$Message)
    Write-Host ""
    Write-Host "PocketTrack  $Message" -ForegroundColor Blue
}

function Fail {
    param([string]$Message)
    Write-Host ""
    Write-Host "ERROR  $Message" -ForegroundColor Red
    exit 1
}

Say "Preparing system dependencies"

$Python = $null

if (Get-Command py -ErrorAction SilentlyContinue) {
    try {
        & py -3.12 --version | Out-Null
        $Python = "py"
    } catch {}
}

if (-not $Python -and (Get-Command python -ErrorAction SilentlyContinue)) {
    try {
        $version = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        if ([version]$version -ge [version]"3.12") {
            $Python = "python"
        }
    } catch {}
}

if (-not $Python) {
    Say "Installing Python 3.12"

    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install `
            --id Python.Python.3.12 `
            --exact `
            --accept-package-agreements `
            --accept-source-agreements
    } else {
        Fail "Python 3.12 is required. Install Python 3.12 and rerun .\start.ps1."
    }

    if (Get-Command py -ErrorAction SilentlyContinue) {
        $Python = "py"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $Python = "python"
    } else {
        Fail "Python installation completed but Python is not yet available in PATH. Reopen PowerShell and rerun .\start.ps1."
    }
}

Say "Preparing Python environment"

$Venv = Join-Path $Root ".venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"
$VenvPocketTrack = Join-Path $Venv "Scripts\pockettrack.exe"

function Create-Venv {
    Say "Creating fresh Python virtual environment"

    if (Test-Path $Venv) {
        Remove-Item -Recurse -Force $Venv
    }

    if ($Python -eq "py") {
        & py -3.12 -m venv $Venv
    } else {
        & python -m venv $Venv
    }

    & $VenvPython -m pip install --upgrade pip setuptools wheel
    & $VenvPython -m pip install -e "${Root}[dev]"
}

function Install-Project {
    & $VenvPython -m pip install --upgrade pip setuptools wheel
    & $VenvPython -m pip install -e "${Root}[dev]"
}

function Test-Venv {
    if (-not (Test-Path $VenvPython)) { return $false }
    if (-not (Test-Path $VenvPocketTrack)) { return $false }

    try {
        & $VenvPython -c @"
import cardbudget
import fastapi
import uvicorn
from cardbudget.cli import main
"@
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

if (-not (Test-Path $VenvPython)) {
    Create-Venv
} elseif ($Update) {
    Say "Updating PocketTrack dependencies"
    Install-Project
}

if (-not (Test-Venv)) {
    Say "Existing virtual environment is unhealthy; rebuilding automatically"
    Create-Venv
}

if (-not (Test-Venv)) {
    Fail "PocketTrack Python environment could not be initialized."
}

Say "Python environment ready"

& $VenvPython -c @"
import sys
import cardbudget
from cardbudget.cli import main

print(f"Python:      {sys.executable}")
print(f"PocketTrack: {cardbudget.__file__}")
print("Package:     OK")
print("CLI:         OK")
"@

$Provider = & $VenvPocketTrack categorization-provider
if ($LASTEXITCODE -ne 0) { Fail "PocketTrack could not read its categorization settings." }
if ($Provider -eq "ollama") {
    $Model = & $VenvPocketTrack categorization-provider --model
    if ($LASTEXITCODE -ne 0) { Fail "PocketTrack could not read its Ollama model." }
    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        try {
            Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 | Out-Null
        } catch {
            Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
            for ($i = 0; $i -lt 10; $i++) {
                Start-Sleep -Seconds 1
                try {
                    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 | Out-Null
                    break
                } catch {}
            }
        }
        & ollama show $Model 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) {
            if ($Update) {
                & ollama pull $Model
                if ($LASTEXITCODE -ne 0) { Write-Warning "Model download failed." }
            } else {
                Write-Warning "Run ollama pull $Model or restart with -Update."
            }
        }
    } else {
        Write-Warning "Install Ollama from ollama.com and run ollama pull $Model to enable local AI."
    }
}
if ($Check) {
    & $VenvPython -m pytest -q -p no:cacheprovider (Join-Path $Root "tests")
    if ($LASTEXITCODE -ne 0) { Fail "PocketTrack tests failed." }
    & $VenvPocketTrack doctor
    if ($LASTEXITCODE -ne 0) { Fail "PocketTrack diagnostics failed." }
}

Say "Preparing private local hostname"

$HostsFile = "$env:SystemRoot\System32\drivers\etc\hosts"
$HostsContent = Get-Content $HostsFile -ErrorAction SilentlyContinue

if (-not ($HostsContent -match "(^|\s)$HostnameLocal(\s|$)")) {
    $IsAdmin = (
        [Security.Principal.WindowsPrincipal]
        [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator
    )

    if (-not $IsAdmin) {
        Write-Warning @"
Administrator permission is required once to register:
127.0.0.1 $HostnameLocal

For this run PocketTrack will remain available on:
http://127.0.0.1:8000
"@
    } else {
        Add-Content -Path $HostsFile -Value "`n127.0.0.1 $HostnameLocal"
        ipconfig /flushdns | Out-Null
    }
}

Say "Starting PocketTrack application"

if (-not $env:POCKETTRACK_PLAID_ENVIRONMENT) {
    $env:POCKETTRACK_PLAID_ENVIRONMENT = "production"
}

$Running = $false

if (Test-Path $AppPidFile) {
    $ExistingPid = Get-Content $AppPidFile
    if (Get-Process -Id $ExistingPid -ErrorAction SilentlyContinue) {
        $Running = $true
        Write-Host "PocketTrack is already running (PID $ExistingPid)."
    }
}

if (-not $Running) {
    $StdoutLog = Join-Path $Runtime "pockettrack.stdout.log"
    $StderrLog = Join-Path $Runtime "pockettrack.stderr.log"

    $Process = Start-Process `
        -FilePath $VenvPocketTrack `
        -ArgumentList "serve" `
        -RedirectStandardOutput $StdoutLog `
        -RedirectStandardError $StderrLog `
        -WindowStyle Hidden `
        -PassThru

    Set-Content -Path $AppPidFile -Value $Process.Id
}

$BackendReady = $false

for ($i = 0; $i -lt 30; $i++) {
    try {
        Invoke-WebRequest `
            -Uri "http://127.0.0.1:8000/" `
            -TimeoutSec 2 `
            -UseBasicParsing | Out-Null

        $BackendReady = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $BackendReady) {
    $StdoutLog = Join-Path $Runtime "pockettrack.stdout.log"
    $StderrLog = Join-Path $Runtime "pockettrack.stderr.log"

    if (Test-Path $StdoutLog) {
        Get-Content $StdoutLog -Tail 80
    }

    if (Test-Path $StderrLog) {
        Get-Content $StderrLog -Tail 80
    }

    Fail "PocketTrack backend did not become ready."
}

Say "Installing automatic refresh (8:00 AM and 8:00 PM)"

try {
    & $VenvPocketTrack install-scheduler --hours 8,20
    & $VenvPocketTrack scheduler-status
} catch {
    Write-Warning "The sync scheduler could not be installed automatically. Retry with: pockettrack install-scheduler --hours 8,20"
}

Say "Ready"

Write-Host ""
Write-Host "Open:  http://127.0.0.1:8000"
Write-Host "Stop:  .\stop.ps1"
Write-Host "Logs:  $Runtime"
