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

& $ownedPython -X utf8 $ownedEntry @RouterArguments
exit $LASTEXITCODE
