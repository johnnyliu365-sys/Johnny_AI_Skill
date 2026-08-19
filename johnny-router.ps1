#Requires -Version 5.1
<#
.SYNOPSIS
Johnny Router launcher: forward one command to the Johnny-owned control-plane
Python without touching project or global interpreters.

.DESCRIPTION
The launcher only resolves the per-user Johnny root and forwards arguments.
When the owned runtime does not exist it reports a typed capability result and
performs no effect; it never installs, repairs or modifies anything itself.
#>
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RouterArguments = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$johnnyRoot = $env:JOHNNY_ROOT
if ([string]::IsNullOrWhiteSpace($johnnyRoot)) {
    $johnnyRoot = Join-Path $env:LOCALAPPDATA 'JohnnyRouter'
}

$ownedPython = Join-Path $johnnyRoot 'venv\Scripts\python.exe'
$ownedEntry = Join-Path $johnnyRoot 'runtime\johnny_router_entry.py'

if (-not (Test-Path -LiteralPath $ownedPython -PathType Leaf) -or
    -not (Test-Path -LiteralPath $ownedEntry -PathType Leaf)) {
    Write-Output '{"status":"CAPABILITY_UNAVAILABLE","code":"JOHNNY_RUNTIME_NOT_INSTALLED"}'
    exit 3
}

if ($RouterArguments.Count -ge 1 -and $RouterArguments[0] -eq 'uninstall') {
    # Self-deletion guard: a python running from the owned venv locks its own
    # executable and loaded native modules, so the owned venv can never delete
    # itself. Uninstall therefore executes from a disposable copy of the venv;
    # the owned venv stays unlocked and fully removable, and the copy is
    # deleted afterwards.
    $uninstallStage = Join-Path ([System.IO.Path]::GetTempPath()) ('johnny-uninstall-' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $uninstallStage | Out-Null
    $exitCode = 3
    try {
        Copy-Item -Recurse -LiteralPath (Join-Path $johnnyRoot 'venv') -Destination (Join-Path $uninstallStage 'venv')
        $stagePython = Join-Path $uninstallStage 'venv\Scripts\python.exe'
        & $stagePython -X utf8 $ownedEntry @RouterArguments
        $exitCode = $LASTEXITCODE
    } finally {
        Remove-Item -Recurse -Force $uninstallStage -ErrorAction SilentlyContinue
    }
    exit $exitCode
}

& $ownedPython -X utf8 $ownedEntry @RouterArguments
exit $LASTEXITCODE
