#Requires -Version 5.1
<#
.SYNOPSIS
Johnny AI Skill bundle bootstrap: verify, present the exact dependency plan,
and require explicit user confirmation before any install effect.

.DESCRIPTION
This entry performs read-only verification only. The live install effect is
owned by library/local_orchestration/plugin_install_transaction.py and stays
unauthorized until the approved 0.4.0 bundle passes Tickets 14 and 15. Running
this script never modifies a company repository, PATH, global Python or Git.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BundleZip
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-TypedResult {
    param(
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$Code
    )
    Write-Output ('{{"status":"{0}","code":"{1}"}}' -f $Status, $Code)
}

# P0 boundary: never bootstrap from inside any Git repository checkout.
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if ($null -ne $gitCommand) {
    $insideRepository = ''
    try {
        $insideRepository = (& git rev-parse --is-inside-work-tree 2>$null)
    } catch {
        $insideRepository = ''
    }
    if ("$insideRepository".Trim() -eq 'true') {
        Write-TypedResult -Status 'BLOCKED' -Code 'INSTALL_BLOCKED_INSIDE_REPOSITORY'
        exit 2
    }
} else {
    Write-TypedResult -Status 'BLOCKED' -Code 'GIT_UNAVAILABLE'
    exit 2
}

if (-not (Test-Path -LiteralPath $BundleZip -PathType Leaf)) {
    Write-TypedResult -Status 'BLOCKED' -Code 'BUNDLE_NOT_FOUND'
    exit 2
}

$archiveHash = (Get-FileHash -LiteralPath $BundleZip -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Output ("Bundle archive SHA-256: {0}" -f $archiveHash)
Write-Output 'Compare this digest with the approved release digest before continuing.'

$pythonProbe = $null
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($null -ne $pyLauncher) {
    try {
        $pythonProbe = (& py -3.11 --version 2>$null)
    } catch {
        $pythonProbe = $null
    }
}
if ([string]::IsNullOrWhiteSpace("$pythonProbe")) {
    Write-TypedResult -Status 'BLOCKED' -Code 'PYTHON_311_UNAVAILABLE'
    exit 2
}
Write-Output ("Control Python probe: {0}" -f "$pythonProbe".Trim())

# Present the exact dependency plan from the bundled runtime lock (read-only).
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $BundleZip).Path)
try {
    $lockEntry = $archive.Entries | Where-Object { $_.FullName -eq 'requirements-runtime.lock' }
    if ($null -eq $lockEntry) {
        Write-TypedResult -Status 'BLOCKED' -Code 'RUNTIME_LOCK_MISSING'
        exit 2
    }
    $reader = New-Object System.IO.StreamReader($lockEntry.Open())
    try {
        $lockJson = $reader.ReadToEnd() | ConvertFrom-Json
    } finally {
        $reader.Dispose()
    }
    Write-Output ("Python constraint: {0}" -f $lockJson.python_constraint)
    Write-Output 'Exact dependency plan (name / version / artifact SHA-256):'
    foreach ($dependency in $lockJson.dependencies) {
        foreach ($artifact in $dependency.artifacts) {
            Write-Output ("  {0} {1} {2}" -f $dependency.normalized_name, $dependency.exact_version, $artifact.sha256)
        }
    }
} finally {
    $archive.Dispose()
}

$confirmation = Read-Host 'Type INSTALL to confirm this exact plan'
if ($confirmation -cne 'INSTALL') {
    Write-TypedResult -Status 'BLOCKED' -Code 'USER_DECLINED'
    exit 2
}

# The live per-user install effect binds through PluginInstallTransaction only
# after the approved bundle passes scripted and owner-run Vita qualification.
Write-TypedResult -Status 'BLOCKED' -Code 'LIVE_INSTALL_NOT_AUTHORIZED'
exit 3
