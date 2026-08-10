$ErrorActionPreference = "SilentlyContinue"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Runtime = Join-Path $Root ".runtime"
$AppPidFile = Join-Path $Runtime "pockettrack.pid"

Write-Host ""
Write-Host "PocketTrack  Stopping PocketTrack" -ForegroundColor Blue

if (Test-Path $AppPidFile) {
    $AppPid = Get-Content $AppPidFile

    Stop-Process `
        -Id $AppPid `
        -Force `
        -ErrorAction SilentlyContinue

    Remove-Item $AppPidFile -Force
}

Write-Host "PocketTrack stopped."
