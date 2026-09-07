# ENV-MSIX-03 — Single-use SDK replay execution evidence

| Field | Value |
| --- | --- |
| Artifact ID / revision | `EVIDENCE-ENV-MSIX-03-REPLAY-20260907-01` / `01` |
| State | `CAPTURED / REVIEW_PENDING` |
| Execution candidate | `4e8746817bd25f9a7813acd7de60aa7af640da48` |
| Authority | ENV-MSIX-03 document revision 04, closure revision 02; owner single-use evidence-only replay |
| Parent review | [Archive correction review](env-msix-03-sdk-archive-review.md) |
| Scope | New archive verification observations; no SDK extraction/execution, installation, VM, certificate trust, host, push or release effects |

## Capture and interpretation

These are the actual three sequential PowerShell command bodies passed to the shell
with `login=false`, followed by their complete returned output and shell exit code.
No output-reducing wrapper was used. Native negative exits were checked separately
from shell success. Output is losslessly encoded as a JSON array of lines:
join entries with LF to recover the whole output after CRLF-to-LF normalization.
Trailing spaces and the final newline are preserved by this representation.
The parent read the unfiltered outputs before forming any conclusion.

The new quarantine is `tests/.johnny-runtime/env-msix-03-sdk-replay-20260907-01`.
The original `env-msix-03-sdk-20260906` archive and three named fixtures are read
before/after, not rewritten. Working-host OS/.NET trust is the admitted boundary;
this is not a defense against compromised same-user/admin/system processes.
OS-managed certificate revocation/cache activity is not asserted absent.

The exact XML template comes from the committed ticket. Generated config fixtures
are written with FileMode.CreateNew; their complete readback and byte hashes appear
below. The wrong policy changes only the fixed fingerprint to 64 zeroes. Neither
candidate certificate nor ambient private-feed configuration supplies trust.

One orchestration JavaScript payload had a syntax error before any nested shell
call executed while preparing phase 3. That pre-execution failure neither downloaded
again nor ran verification. Phase 3 below is the single actual shell invocation;
there was exactly one SDK HTTP acquisition in this replay.

| Cell | Observed result, pending independent review |
| --- | --- |
| EV1 | Fresh absent root, non-reparse ancestry; absolute verifier hash and valid Microsoft .NET signature; SDK 10.0.302 |
| EV2 | HTTP 200, exact unchanged URI, 22,297,017 buffered and written bytes, admitted hash; one request with bounded no-redirect handler |
| EV3 | Positive exit 0; wrong signer exit 1 / NU3034; actual package ID/version readback |
| EV4 | One-byte sibling corruption exit 1 / NU3008; original hash unchanged; original reverify exit 0; old quarantine named files unchanged |
| EV5 | Separate parent/helper review of the committed record still required |

## EV1 — root, verifier and preserved original

Exact command:

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repo = 'C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest'
$root = Join-Path $repo 'tests\.johnny-runtime\env-msix-03-sdk-replay-20260907-01'
$oldRoot = Join-Path $repo 'tests\.johnny-runtime\env-msix-03-sdk-20260906'
function Read-ByteHash([string]$path) {
  $sha = [Security.Cryptography.SHA256]::Create()
  $stream = [IO.File]::OpenRead($path)
  try { return [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
  finally { $stream.Dispose(); $sha.Dispose() }
}
function Assert-NoReparse([string]$path) {
  $entry = Get-Item -LiteralPath $path -Force
  while ($null -ne $entry) {
    Write-Output ("PATH_CHECK={0} ATTRIBUTES={1}" -f $entry.FullName, $entry.Attributes)
    if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_PATH' }
    if ($entry -is [IO.DirectoryInfo]) { $entry = $entry.Parent } else { $entry = $entry.Directory }
  }
}
Write-Output ('START_UTC=' + [DateTime]::UtcNow.ToString('o'))
Set-Location $repo
$head = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -cne '4e8746817bd25f9a7813acd7de60aa7af640da48') { throw 'CANDIDATE_MISMATCH' }
$status = @(& git status --porcelain)
if ($LASTEXITCODE -ne 0 -or $status.Count -ne 0) { throw 'DIRTY_WORKTREE' }
Write-Output "CANDIDATE=$head TRACKED_WORKTREE=CLEAN"
$parent = Join-Path $repo 'tests\.johnny-runtime'
if ([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($root)) -cne $parent) { throw 'OUTSIDE_OWNED_PARENT' }
Assert-NoReparse $parent
if (Test-Path -LiteralPath $root) { throw 'REPLAY_ROOT_ALREADY_EXISTS' }
Write-Output "FRESH_ROOT_ABSENT=$root"
Assert-NoReparse (Join-Path $oldRoot 'sdk.nupkg')
foreach ($pair in @(
  @('sdk.nupkg','8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed'),
  @('sdk-tampered.nupkg','06add73b37945dae1488b34dcc8c92c8bd0acfded7af01c4ce14ff83544faae2'),
  @('nuget.config','f297aae534f103b2572d56f9a973f824779afa952aa447ba72b32f3687c2679e'),
  @('nuget-wrong-signer.config','776c18560e1f814b78d9d8a26c807168c49f599cb630cc013c120cc6748fe364')
)) {
  $path = Join-Path $oldRoot $pair[0]
  if (((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'OLD_FILE_REPARSE' }
  $digest = Read-ByteHash $path
  Write-Output ("OLD_BEFORE={0} SHA256={1}" -f $pair[0], $digest)
  if ($digest -cne $pair[1]) { throw 'OLD_FILE_CHANGED' }
}
$dotnet = 'C:\Program Files\dotnet\dotnet.exe'
Assert-NoReparse $dotnet
$dotnetHash = Read-ByteHash $dotnet
Write-Output "VERIFIER_PATH=$dotnet SHA256=$dotnetHash"
if ($dotnetHash -cne '4377f10c78400f0370b88156773de9843c07f14e65b3232005ec3179ef38d463') { throw 'VERIFIER_HASH_MISMATCH' }
$signature = Get-AuthenticodeSignature -LiteralPath $dotnet
Write-Output ("VERIFIER_AUTHENTICODE_STATUS={0} SUBJECT={1} THUMBPRINT={2}" -f $signature.Status, $signature.SignerCertificate.Subject, $signature.SignerCertificate.Thumbprint)
if ($signature.Status.ToString() -cne 'Valid' -or $signature.SignerCertificate.Subject -cne 'CN=.NET, O=Microsoft Corporation, L=Redmond, S=Washington, C=US') { throw 'VERIFIER_SIGNATURE_MISMATCH' }
New-Item -ItemType Directory -Path $root -ErrorAction Stop | ForEach-Object { Write-Output ('CREATED_ROOT=' + $_.FullName) }
Assert-NoReparse $root
foreach ($child in @('dotnet-home','cache','temp')) {
  New-Item -ItemType Directory -Path (Join-Path $root $child) -ErrorAction Stop | ForEach-Object { Write-Output ('CREATED_CHILD=' + $_.FullName) }
}
$env:DOTNET_CLI_HOME = Join-Path $root 'dotnet-home'
$env:NUGET_PACKAGES = Join-Path $root 'cache'
$env:TEMP = Join-Path $root 'temp'
$env:TMP = Join-Path $root 'temp'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:DOTNET_NOLOGO = '1'
Set-Location $root
Write-Output "CWD=$((Get-Location).Path)"
Write-Output "PROCESS_HOME=$env:DOTNET_CLI_HOME PACKAGES=$env:NUGET_PACKAGES TEMP=$env:TEMP TMP=$env:TMP"
$version = & 'C:\Program Files\dotnet\dotnet.exe' --version
$versionExit = $LASTEXITCODE
$version | Write-Output
Write-Output "VERIFIER_VERSION_EXIT=$versionExit"
if ($versionExit -ne 0 -or $version.Trim() -cne '10.0.302') { throw 'VERIFIER_VERSION_MISMATCH' }
Write-Output 'EV1_PREFLIGHT=PASS'
Write-Output ('END_UTC=' + [DateTime]::UtcNow.ToString('o'))
```

Execution metadata:

```json
{
  "chunk_id": "2f62c0",
  "exit_code": 0,
  "wall_time_seconds": 2.3554303
}
```

Complete output (JSON lines, lossless):

```json
[
  "START_UTC=2026-09-07T06:22:08.7466713Z",
  "CANDIDATE=4e8746817bd25f9a7813acd7de60aa7af640da48 TRACKED_WORKTREE=CLEAN",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop ATTRIBUTES=ReadOnly, Directory",
  "PATH_CHECK=C:\\Users\\GameBoy ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users ATTRIBUTES=ReadOnly, Directory",
  "PATH_CHECK=C:\\ ATTRIBUTES=Hidden, System, Directory",
  "FRESH_ROOT_ABSENT=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-20260906\\sdk.nupkg ATTRIBUTES=Archive",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-20260906 ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop ATTRIBUTES=ReadOnly, Directory",
  "PATH_CHECK=C:\\Users\\GameBoy ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users ATTRIBUTES=ReadOnly, Directory",
  "PATH_CHECK=C:\\ ATTRIBUTES=Hidden, System, Directory",
  "OLD_BEFORE=sdk.nupkg SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed",
  "OLD_BEFORE=sdk-tampered.nupkg SHA256=06add73b37945dae1488b34dcc8c92c8bd0acfded7af01c4ce14ff83544faae2",
  "OLD_BEFORE=nuget.config SHA256=f297aae534f103b2572d56f9a973f824779afa952aa447ba72b32f3687c2679e",
  "OLD_BEFORE=nuget-wrong-signer.config SHA256=776c18560e1f814b78d9d8a26c807168c49f599cb630cc013c120cc6748fe364",
  "PATH_CHECK=C:\\Program Files\\dotnet\\dotnet.exe ATTRIBUTES=Archive",
  "PATH_CHECK=C:\\Program Files\\dotnet ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Program Files ATTRIBUTES=ReadOnly, Directory",
  "PATH_CHECK=C:\\ ATTRIBUTES=Hidden, System, Directory",
  "VERIFIER_PATH=C:\\Program Files\\dotnet\\dotnet.exe SHA256=4377f10c78400f0370b88156773de9843c07f14e65b3232005ec3179ef38d463",
  "VERIFIER_AUTHENTICODE_STATUS=Valid SUBJECT=CN=.NET, O=Microsoft Corporation, L=Redmond, S=Washington, C=US THUMBPRINT=BB793DB742624269BB5F4515BBE9A3DF418F588D",
  "CREATED_ROOT=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01 ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users\\GameBoy\\Desktop ATTRIBUTES=ReadOnly, Directory",
  "PATH_CHECK=C:\\Users\\GameBoy ATTRIBUTES=Directory",
  "PATH_CHECK=C:\\Users ATTRIBUTES=ReadOnly, Directory",
  "PATH_CHECK=C:\\ ATTRIBUTES=Hidden, System, Directory",
  "CREATED_CHILD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\dotnet-home",
  "CREATED_CHILD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\cache",
  "CREATED_CHILD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\temp",
  "CWD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01",
  "PROCESS_HOME=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\dotnet-home PACKAGES=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\cache TEMP=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\temp TMP=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\temp",
  "10.0.302",
  "VERIFIER_VERSION_EXIT=0",
  "EV1_PREFLIGHT=PASS",
  "END_UTC=2026-09-07T06:22:10.3051468Z",
  ""
]
```

## EV2 — bounded one-shot acquisition

Exact command:

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Add-Type -AssemblyName System.Net.Http
$root = 'C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\tests\.johnny-runtime\env-msix-03-sdk-replay-20260907-01'
$destination = Join-Path $root 'sdk.nupkg'
$uri = [Uri]'https://api.nuget.org/v3-flatcontainer/microsoft.windows.sdk.buildtools/10.0.28000.2705/microsoft.windows.sdk.buildtools.10.0.28000.2705.nupkg'
$node = Get-Item -LiteralPath $root -Force
while ($null -ne $node) {
  if (($node.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_ROOT' }
  $node = $node.Parent
}
if (Test-Path -LiteralPath $destination) { throw 'ARCHIVE_ALREADY_EXISTS' }
$handler = [Net.Http.HttpClientHandler]::new()
$handler.AllowAutoRedirect = $false
$handler.UseDefaultCredentials = $false
$handler.Credentials = $null
$handler.UseProxy = $false
$handler.UseCookies = $false
$handler.AutomaticDecompression = [Net.DecompressionMethods]::None
$client = [Net.Http.HttpClient]::new($handler)
$client.Timeout = [TimeSpan]::FromSeconds(180)
$client.MaxResponseContentBufferSize = 536870912
$response = $null
$watch = [Diagnostics.Stopwatch]::StartNew()
try {
  Write-Output ('HTTP_START_UTC=' + [DateTime]::UtcNow.ToString('o'))
  Write-Output "REQUEST_URI=$($uri.AbsoluteUri)"
  Write-Output ("HANDLER_REDIRECT={0} DEFAULT_CREDENTIALS={1} CREDENTIALS_NULL={2} PROXY={3} COOKIES={4} DECOMPRESSION={5}" -f $handler.AllowAutoRedirect, $handler.UseDefaultCredentials, ($null -eq $handler.Credentials), $handler.UseProxy, $handler.UseCookies, $handler.AutomaticDecompression)
  Write-Output "TIMEOUT_SECONDS=$($client.Timeout.TotalSeconds) BUFFER_LIMIT_BYTES=$($client.MaxResponseContentBufferSize)"
  Write-Output 'SDK_GET_ATTEMPT=1'
  $response = $client.GetAsync($uri, [Net.Http.HttpCompletionOption]::ResponseContentRead).GetAwaiter().GetResult()
  $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
  $watch.Stop()
  $declaredLength = $response.Content.Headers.ContentLength
  Write-Output ("HTTP_STATUS={0} RESPONSE_URI={1} DECLARED_LENGTH={2} BUFFERED_BYTES={3} ELAPSED_MS={4}" -f [int]$response.StatusCode, $response.RequestMessage.RequestUri.AbsoluteUri, $declaredLength, $bytes.LongLength, $watch.ElapsedMilliseconds)
  if ([int]$response.StatusCode -ne 200 -or $response.RequestMessage.RequestUri.AbsoluteUri -cne $uri.AbsoluteUri) { throw 'HTTP_OR_ORIGIN_MISMATCH' }
  if ($bytes.LongLength -gt 536870912 -or $bytes.LongLength -le 0) { throw 'ARCHIVE_SIZE_INVALID' }
  if ($null -ne $declaredLength -and [long]$declaredLength -ne $bytes.LongLength) { throw 'HTTP_LENGTH_MISMATCH' }
  $sha = [Security.Cryptography.SHA256]::Create()
  try { $digest = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant() } finally { $sha.Dispose() }
  Write-Output "DOWNLOAD_SHA256=$digest"
  if ($digest -cne '8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed') { throw 'EXACT_ARCHIVE_HASH_MISMATCH' }
  $file = [IO.FileStream]::new($destination, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
  try { $file.Write($bytes,0,$bytes.Length); $file.Flush($true) } finally { $file.Dispose() }
  $sha = [Security.Cryptography.SHA256]::Create()
  $readback = [IO.File]::OpenRead($destination)
  try { $diskDigest = [BitConverter]::ToString($sha.ComputeHash($readback)).Replace('-', '').ToLowerInvariant() } finally { $readback.Dispose(); $sha.Dispose() }
  Write-Output "CREATENEW_DESTINATION=$destination DISK_BYTES=$((Get-Item -LiteralPath $destination).Length) DISK_SHA256=$diskDigest"
  if ($diskDigest -cne $digest) { throw 'DISK_HASH_MISMATCH' }
  Write-Output 'EV2_ACQUISITION=PASS'
  Write-Output ('HTTP_END_UTC=' + [DateTime]::UtcNow.ToString('o'))
} finally {
  if ($null -ne $response) { $response.Dispose() }
  $client.Dispose()
  $handler.Dispose()
}
```

Execution metadata:

```json
{
  "chunk_id": "3bf317",
  "exit_code": 0,
  "wall_time_seconds": 3.17281
}
```

Complete output (JSON lines, lossless):

```json
[
  "HTTP_START_UTC=2026-09-07T06:23:00.0298323Z",
  "REQUEST_URI=https://api.nuget.org/v3-flatcontainer/microsoft.windows.sdk.buildtools/10.0.28000.2705/microsoft.windows.sdk.buildtools.10.0.28000.2705.nupkg",
  "HANDLER_REDIRECT=False DEFAULT_CREDENTIALS=False CREDENTIALS_NULL=True PROXY=False COOKIES=False DECOMPRESSION=None",
  "TIMEOUT_SECONDS=180 BUFFER_LIMIT_BYTES=536870912",
  "SDK_GET_ATTEMPT=1",
  "HTTP_STATUS=200 RESPONSE_URI=https://api.nuget.org/v3-flatcontainer/microsoft.windows.sdk.buildtools/10.0.28000.2705/microsoft.windows.sdk.buildtools.10.0.28000.2705.nupkg DECLARED_LENGTH=22297017 BUFFERED_BYTES=22297017 ELAPSED_MS=1773",
  "DOWNLOAD_SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed",
  "CREATENEW_DESTINATION=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\sdk.nupkg DISK_BYTES=22297017 DISK_SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed",
  "EV2_ACQUISITION=PASS",
  "HTTP_END_UTC=2026-09-07T06:23:02.2748905Z",
  ""
]
```

## EV3/EV4 — generated policy, native verification and identity

Exact command:

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repo = 'C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest'
$root = Join-Path $repo 'tests\.johnny-runtime\env-msix-03-sdk-replay-20260907-01'
$oldRoot = Join-Path $repo 'tests\.johnny-runtime\env-msix-03-sdk-20260906'
function Read-ByteHash([string]$path) {
  $sha = [Security.Cryptography.SHA256]::Create()
  $stream = [IO.File]::OpenRead($path)
  try { return [BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
  finally { $stream.Dispose(); $sha.Dispose() }
}
function Write-NewFixture([string]$path, [byte[]]$bytes) {
  $stream = [IO.FileStream]::new($path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
  try { $stream.Write($bytes,0,$bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
}
Set-Location $repo
$head = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -cne '4e8746817bd25f9a7813acd7de60aa7af640da48') { throw 'CANDIDATE_MISMATCH' }
if (@(& git status --porcelain).Count -ne 0) { throw 'DIRTY_WORKTREE' }
Write-Output "EXECUTION_CANDIDATE=$head"
$node = Get-Item -LiteralPath $root -Force
while ($null -ne $node) {
  Write-Output ("PATH_RECHECK={0} ATTRIBUTES={1}" -f $node.FullName, $node.Attributes)
  if (($node.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_ROOT' }
  $node = $node.Parent
}
$archive = Join-Path $root 'sdk.nupkg'
if (((Get-Item -LiteralPath $archive -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'ARCHIVE_REPARSE' }
$originalDigest = Read-ByteHash $archive
Write-Output "PRE_VERIFY_ARCHIVE_SHA256=$originalDigest"
if ($originalDigest -cne '8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed') { throw 'ARCHIVE_CHANGED' }
$dotnet = 'C:\Program Files\dotnet\dotnet.exe'
$verifierHash = Read-ByteHash $dotnet
$signature = Get-AuthenticodeSignature -LiteralPath $dotnet
Write-Output "VERIFIER_PATH=$dotnet SHA256=$verifierHash"
Write-Output ("VERIFIER_SIGNATURE={0} SUBJECT={1}" -f $signature.Status,$signature.SignerCertificate.Subject)
if ($verifierHash -cne '4377f10c78400f0370b88156773de9843c07f14e65b3232005ec3179ef38d463' -or $signature.Status.ToString() -cne 'Valid' -or $signature.SignerCertificate.Subject -cne 'CN=.NET, O=Microsoft Corporation, L=Redmond, S=Washington, C=US') { throw 'VERIFIER_CHANGED' }
$ticketLines = & git show '4e8746817bd25f9a7813acd7de60aa7af640da48:modules/tickets/local-orchestration-installer/env-msix-03-sdk-archive-verification.md'
if ($LASTEXITCODE -ne 0) { throw 'COMMITTED_TEMPLATE_UNREADABLE' }
$lf = [string][char]10
$fence = ([string][char]96) * 3
$ticketText = $ticketLines -join $lf
$templatePattern = '(?s)' + $fence + 'xml\n(.*?)\n' + $fence
$templateMatches = [regex]::Matches($ticketText, $templatePattern)
if ($templateMatches.Count -ne 1) { throw 'TEMPLATE_AMBIGUOUS' }
$configText = $templateMatches[0].Groups[1].Value + $lf
$repoFingerprint = '1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d'
if ([regex]::Matches($configText, [regex]::Escape($repoFingerprint)).Count -ne 1) { throw 'TEMPLATE_SIGNER_AMBIGUOUS' }
$wrongConfigText = $configText.Replace($repoFingerprint, ('0' * 64))
Write-NewFixture (Join-Path $root 'nuget.config') ([Text.Encoding]::UTF8.GetBytes($configText))
Write-NewFixture (Join-Path $root 'nuget-wrong-signer.config') ([Text.Encoding]::UTF8.GetBytes($wrongConfigText))
foreach ($name in @('nuget.config','nuget-wrong-signer.config')) {
  $path = Join-Path $root $name
  Write-Output ("GENERATED_FROM_COMMITTED_TEMPLATE_CREATENEW={0} BYTES={1} SHA256={2}" -f $path,(Get-Item -LiteralPath $path).Length,(Read-ByteHash $path))
  Get-Content -LiteralPath $path
}
$env:DOTNET_CLI_HOME = Join-Path $root 'dotnet-home'
$env:NUGET_PACKAGES = Join-Path $root 'cache'
$env:TEMP = Join-Path $root 'temp'
$env:TMP = Join-Path $root 'temp'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:DOTNET_NOLOGO = '1'
Set-Location $root
Write-Output "CWD=$((Get-Location).Path) PROCESS_HOME=$env:DOTNET_CLI_HOME PACKAGES=$env:NUGET_PACKAGES TEMP=$env:TEMP TMP=$env:TMP"
$version = & 'C:\Program Files\dotnet\dotnet.exe' --version
$versionExit = $LASTEXITCODE
$version | Write-Output
Write-Output "VERIFIER_VERSION_EXIT=$versionExit"
if ($versionExit -ne 0 -or $version.Trim() -cne '10.0.302') { throw 'SDK_VERSION_CHANGED' }
Write-Output ('EV3_POSITIVE_START_UTC=' + [DateTime]::UtcNow.ToString('o'))
& 'C:\Program Files\dotnet\dotnet.exe' nuget verify sdk.nupkg --all --configfile nuget.config --verbosity normal
$positiveExit = $LASTEXITCODE
Write-Output "EV3_POSITIVE_EXIT=$positiveExit"
if ($positiveExit -ne 0) { throw 'POSITIVE_VERIFICATION_FAILED' }
Write-Output ('EV3_WRONG_SIGNER_START_UTC=' + [DateTime]::UtcNow.ToString('o'))
$wrongOutput = & 'C:\Program Files\dotnet\dotnet.exe' nuget verify sdk.nupkg --all --configfile nuget-wrong-signer.config --verbosity normal
$wrongExit = $LASTEXITCODE
$wrongOutput | Write-Output
Write-Output "EV3_WRONG_SIGNER_EXIT=$wrongExit"
if ($wrongExit -eq 0 -or ($wrongOutput -join $lf) -notmatch 'NU3034') { throw 'WRONG_SIGNER_NOT_REJECTED_AS_EXPECTED' }
$mutatedBytes = [IO.File]::ReadAllBytes($archive)
$offset = [int][Math]::Floor($mutatedBytes.Length / 2)
$before = $mutatedBytes[$offset]
$mutatedBytes[$offset] = $mutatedBytes[$offset] -bxor 1
Write-Output "TAMPER_OFFSET=$offset BEFORE=$before AFTER=$($mutatedBytes[$offset])"
Write-NewFixture (Join-Path $root 'sdk-tampered.nupkg') $mutatedBytes
Write-Output ('EV4_TAMPER_START_UTC=' + [DateTime]::UtcNow.ToString('o'))
$tamperedOutput = & 'C:\Program Files\dotnet\dotnet.exe' nuget verify sdk-tampered.nupkg --all --configfile nuget.config --verbosity normal
$tamperedExit = $LASTEXITCODE
$tamperedOutput | Write-Output
Write-Output "EV4_TAMPERED_EXIT=$tamperedExit"
if ($tamperedExit -eq 0 -or ($tamperedOutput -join $lf) -notmatch 'NU3008') { throw 'TAMPER_NOT_REJECTED_AS_EXPECTED' }
$afterDigest = Read-ByteHash $archive
Write-Output "ORIGINAL_AFTER_SHA256=$afterDigest"
if ($afterDigest -cne $originalDigest) { throw 'ORIGINAL_CHANGED' }
& 'C:\Program Files\dotnet\dotnet.exe' nuget verify sdk.nupkg --all --configfile nuget.config --verbosity normal
$reverifyExit = $LASTEXITCODE
Write-Output "EV4_ORIGINAL_REVERIFY_EXIT=$reverifyExit"
if ($reverifyExit -ne 0) { throw 'ORIGINAL_REVERIFY_FAILED' }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [IO.Compression.ZipFile]::OpenRead($archive)
try {
  $entries = @($zip.Entries | Where-Object { $_.FullName -ceq 'Microsoft.Windows.SDK.BuildTools.nuspec' })
  if ($entries.Count -ne 1 -or $entries[0].Length -gt 1048576) { throw 'NUSPEC_IDENTITY_ENTRY_INVALID' }
  $settings = [Xml.XmlReaderSettings]::new()
  $settings.DtdProcessing = [Xml.DtdProcessing]::Prohibit
  $settings.XmlResolver = $null
  $settings.MaxCharactersInDocument = 1048576
  $stream = $entries[0].Open()
  $reader = [Xml.XmlReader]::Create($stream,$settings)
  try {
    $document = [Xml.XmlDocument]::new()
    $document.XmlResolver = $null
    $document.Load($reader)
    $idNodes = $document.SelectNodes('/*[local-name()="package"]/*[local-name()="metadata"]/*[local-name()="id"]')
    $versionNodes = $document.SelectNodes('/*[local-name()="package"]/*[local-name()="metadata"]/*[local-name()="version"]')
    if ($idNodes.Count -ne 1 -or $versionNodes.Count -ne 1) { throw 'NUSPEC_FIELDS_AMBIGUOUS' }
    Write-Output ("NUSPEC_ID={0} VERSION={1} ENTRY_LENGTH={2}" -f $idNodes[0].InnerText,$versionNodes[0].InnerText,$entries[0].Length)
    if ($idNodes[0].InnerText -cne 'Microsoft.Windows.SDK.BuildTools' -or $versionNodes[0].InnerText -cne '10.0.28000.2705') { throw 'NUSPEC_IDENTITY_MISMATCH' }
  } finally { $reader.Dispose(); $stream.Dispose() }
} finally { $zip.Dispose() }
foreach ($name in @('sdk.nupkg','sdk-tampered.nupkg','nuget.config','nuget-wrong-signer.config')) {
  $path = Join-Path $root $name
  Write-Output ("RETAINED_FILE={0} BYTES={1} SHA256={2}" -f $name,(Get-Item -LiteralPath $path).Length,(Read-ByteHash $path))
}
foreach ($pair in @(
  @('sdk.nupkg','8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed'),
  @('sdk-tampered.nupkg','06add73b37945dae1488b34dcc8c92c8bd0acfded7af01c4ce14ff83544faae2'),
  @('nuget.config','f297aae534f103b2572d56f9a973f824779afa952aa447ba72b32f3687c2679e'),
  @('nuget-wrong-signer.config','776c18560e1f814b78d9d8a26c807168c49f599cb630cc013c120cc6748fe364')
)) {
  $digest = Read-ByteHash (Join-Path $oldRoot $pair[0])
  Write-Output ("OLD_AFTER={0} SHA256={1}" -f $pair[0],$digest)
  if ($digest -cne $pair[1]) { throw 'OLD_QUARANTINE_CHANGED' }
}
Set-Location $repo
git status --short --branch
if ($LASTEXITCODE -ne 0 -or @(& git status --porcelain).Count -ne 0) { throw 'TRACKED_WORKTREE_CHANGED' }
git rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'HEAD_READBACK_FAILED' }
Write-Output ('EV1_TO_EV4_REPLAY_END_UTC=' + [DateTime]::UtcNow.ToString('o'))
Write-Output 'REPLAY_NATIVE_CHECKS=PASS REVIEW_REQUIRED=EV5'
```

Execution metadata:

```json
{
  "chunk_id": "0502ba",
  "exit_code": 0,
  "wall_time_seconds": 9.4989115
}
```

Complete output (JSON lines, lossless):

```json
[
  "EXECUTION_CANDIDATE=4e8746817bd25f9a7813acd7de60aa7af640da48",
  "PATH_RECHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01 ATTRIBUTES=Directory",
  "PATH_RECHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime ATTRIBUTES=Directory",
  "PATH_RECHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests ATTRIBUTES=Directory",
  "PATH_RECHECK=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest ATTRIBUTES=Directory",
  "PATH_RECHECK=C:\\Users\\GameBoy\\Desktop ATTRIBUTES=ReadOnly, Directory",
  "PATH_RECHECK=C:\\Users\\GameBoy ATTRIBUTES=Directory",
  "PATH_RECHECK=C:\\Users ATTRIBUTES=ReadOnly, Directory",
  "PATH_RECHECK=C:\\ ATTRIBUTES=Hidden, System, Directory",
  "PRE_VERIFY_ARCHIVE_SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed",
  "VERIFIER_PATH=C:\\Program Files\\dotnet\\dotnet.exe SHA256=4377f10c78400f0370b88156773de9843c07f14e65b3232005ec3179ef38d463",
  "VERIFIER_SIGNATURE=Valid SUBJECT=CN=.NET, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
  "GENERATED_FROM_COMMITTED_TEMPLATE_CREATENEW=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\nuget.config BYTES=497 SHA256=f297aae534f103b2572d56f9a973f824779afa952aa447ba72b32f3687c2679e",
  "<?xml version=\"1.0\" encoding=\"utf-8\"?>",
  "<configuration>",
  "  <config><add key=\"signatureValidationMode\" value=\"require\" /></config>",
  "  <packageSources><clear /></packageSources>",
  "  <trustedSigners>",
  "    <clear />",
  "    <repository name=\"nuget.org\" serviceIndex=\"https://api.nuget.org/v3/index.json\">",
  "      <certificate fingerprint=\"1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d\" hashAlgorithm=\"SHA256\" allowUntrustedRoot=\"false\" />",
  "    </repository>",
  "  </trustedSigners>",
  "</configuration>",
  "GENERATED_FROM_COMMITTED_TEMPLATE_CREATENEW=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\nuget-wrong-signer.config BYTES=497 SHA256=776c18560e1f814b78d9d8a26c807168c49f599cb630cc013c120cc6748fe364",
  "<?xml version=\"1.0\" encoding=\"utf-8\"?>",
  "<configuration>",
  "  <config><add key=\"signatureValidationMode\" value=\"require\" /></config>",
  "  <packageSources><clear /></packageSources>",
  "  <trustedSigners>",
  "    <clear />",
  "    <repository name=\"nuget.org\" serviceIndex=\"https://api.nuget.org/v3/index.json\">",
  "      <certificate fingerprint=\"0000000000000000000000000000000000000000000000000000000000000000\" hashAlgorithm=\"SHA256\" allowUntrustedRoot=\"false\" />",
  "    </repository>",
  "  </trustedSigners>",
  "</configuration>",
  "CWD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01 PROCESS_HOME=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\dotnet-home PACKAGES=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\cache TEMP=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\temp TMP=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\temp",
  "10.0.302",
  "VERIFIER_VERSION_EXIT=0",
  "EV3_POSITIVE_START_UTC=2026-09-07T06:26:57.1248178Z",
  "X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行程式碼簽署。",
  "X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行時間戳記。",
  "",
  "正在驗證 Microsoft.Windows.SDK.BuildTools.10.0.28000.2705",
  "內容雜湊: TZQ96xtu7+fyFsyJCgj6Hazru0H8G1kiE1CeZLGpsqT4xKQmkxWu9yRuxYLeHJECjqEHN7duZUTcdbt8zlQ8OQ==",
  "C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\sdk.nupkg",
  "簽章雜湊演算法: SHA256",
  "",
  "簽章類型: Author",
  "正在利用以下憑證驗證 作者主要簽章: ",
  "  主體名稱: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
  "  SHA1 雜湊: F25C45D17C53D4E0D1DC9FB9DFD0731FCF904B77",
  "  SHA256 雜湊: 566A31882BE208BE4422F7CFD66ED09F5D4524A5994F50CCC8B05EC0528C1353",
  "  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2023/7/27 上午 08:00:00 至 2026/10/18 上午 07:59:59",
  "時間戳記: 2026/8/15 上午 04:35:41",
  "正在利用以下時間戳記服務憑證，驗證 作者主要簽章 的時間戳記: ",
  "  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O=\"DigiCert, Inc.\", C=US",
  "  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E",
  "  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33",
  "  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59",
  "",
  "簽章類型: Repository",
  "服務索引: https://api.nuget.org/v3/index.json",
  "擁有者: Microsoft, WindowsSDK",
  "正在利用以下憑證驗證 存放庫副署: ",
  "  主體名稱: CN=NuGet.org Repository by Microsoft, O=NuGet.org Repository by Microsoft, L=Redmond, S=Washington, C=US",
  "  SHA1 雜湊: C72FE7739A9EECB8EC1E4F596DB3BB74039B1DE2",
  "  SHA256 雜湊: 1F4B311D9ACC115C8DC8018B5A49E00FCE6DA8E2855F9F014CA6F34570BC482D",
  "  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2024/2/23 上午 08:00:00 至 2027/5/19 上午 07:59:59",
  "時間戳記: 2026/8/26 下午 12:54:00",
  "正在利用以下時間戳記服務憑證，驗證 存放庫副署 的時間戳記: ",
  "  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O=\"DigiCert, Inc.\", C=US",
  "  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E",
  "  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33",
  "  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59",
  "",
  "已成功驗證套件 'Microsoft.Windows.SDK.BuildTools.10.0.28000.2705'。",
  "EV3_POSITIVE_EXIT=0",
  "EV3_WRONG_SIGNER_START_UTC=2026-09-07T06:26:58.9677963Z",
  "X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行程式碼簽署。",
  "X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行時間戳記。",
  "",
  "正在驗證 Microsoft.Windows.SDK.BuildTools.10.0.28000.2705",
  "內容雜湊: TZQ96xtu7+fyFsyJCgj6Hazru0H8G1kiE1CeZLGpsqT4xKQmkxWu9yRuxYLeHJECjqEHN7duZUTcdbt8zlQ8OQ==",
  "C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\sdk.nupkg",
  "簽章雜湊演算法: SHA256",
  "",
  "簽章類型: Author",
  "正在利用以下憑證驗證 作者主要簽章: ",
  "  主體名稱: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
  "  SHA1 雜湊: F25C45D17C53D4E0D1DC9FB9DFD0731FCF904B77",
  "  SHA256 雜湊: 566A31882BE208BE4422F7CFD66ED09F5D4524A5994F50CCC8B05EC0528C1353",
  "  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2023/7/27 上午 08:00:00 至 2026/10/18 上午 07:59:59",
  "時間戳記: 2026/8/15 上午 04:35:41",
  "正在利用以下時間戳記服務憑證，驗證 作者主要簽章 的時間戳記: ",
  "  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O=\"DigiCert, Inc.\", C=US",
  "  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E",
  "  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33",
  "  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59",
  "",
  "簽章類型: Repository",
  "服務索引: https://api.nuget.org/v3/index.json",
  "擁有者: Microsoft, WindowsSDK",
  "正在利用以下憑證驗證 存放庫副署: ",
  "  主體名稱: CN=NuGet.org Repository by Microsoft, O=NuGet.org Repository by Microsoft, L=Redmond, S=Washington, C=US",
  "  SHA1 雜湊: C72FE7739A9EECB8EC1E4F596DB3BB74039B1DE2",
  "  SHA256 雜湊: 1F4B311D9ACC115C8DC8018B5A49E00FCE6DA8E2855F9F014CA6F34570BC482D",
  "  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2024/2/23 上午 08:00:00 至 2027/5/19 上午 07:59:59",
  "時間戳記: 2026/8/26 下午 12:54:00",
  "正在利用以下時間戳記服務憑證，驗證 存放庫副署 的時間戳記: ",
  "  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O=\"DigiCert, Inc.\", C=US",
  "  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E",
  "  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33",
  "  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59",
  "",
  "已完成，有 1 個錯誤和 0 個警告。",
  "error: NU3034: 此套件已簽署，但不是由受信任簽署者所簽署。",
  "",
  "套件特徵標記驗證失敗。",
  "EV3_WRONG_SIGNER_EXIT=1",
  "TAMPER_OFFSET=11148508 BEFORE=162 AFTER=163",
  "EV4_TAMPER_START_UTC=2026-09-07T06:27:00.2330711Z",
  "X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行程式碼簽署。",
  "X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行時間戳記。",
  "",
  "正在驗證 Microsoft.Windows.SDK.BuildTools.10.0.28000.2705",
  "內容雜湊: mZ5bE870O3M8HcsV09GggAINNAeoIOqygIxbvKYhr0B2C3+k/n8Ubq5IWZ2exIvHGLjtY2T/G7eRXhRjj9qFOQ==",
  "C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\sdk-tampered.nupkg",
  "簽章雜湊演算法: SHA256",
  "",
  "簽章類型: Author",
  "正在利用以下憑證驗證 作者主要簽章: ",
  "  主體名稱: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
  "  SHA1 雜湊: F25C45D17C53D4E0D1DC9FB9DFD0731FCF904B77",
  "  SHA256 雜湊: 566A31882BE208BE4422F7CFD66ED09F5D4524A5994F50CCC8B05EC0528C1353",
  "  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2023/7/27 上午 08:00:00 至 2026/10/18 上午 07:59:59",
  "時間戳記: 2026/8/15 上午 04:35:41",
  "正在利用以下時間戳記服務憑證，驗證 作者主要簽章 的時間戳記: ",
  "  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O=\"DigiCert, Inc.\", C=US",
  "  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E",
  "  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33",
  "  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59",
  "",
  "簽章類型: Repository",
  "服務索引: https://api.nuget.org/v3/index.json",
  "擁有者: Microsoft, WindowsSDK",
  "正在利用以下憑證驗證 存放庫副署: ",
  "  主體名稱: CN=NuGet.org Repository by Microsoft, O=NuGet.org Repository by Microsoft, L=Redmond, S=Washington, C=US",
  "  SHA1 雜湊: C72FE7739A9EECB8EC1E4F596DB3BB74039B1DE2",
  "  SHA256 雜湊: 1F4B311D9ACC115C8DC8018B5A49E00FCE6DA8E2855F9F014CA6F34570BC482D",
  "  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2024/2/23 上午 08:00:00 至 2027/5/19 上午 07:59:59",
  "時間戳記: 2026/8/26 下午 12:54:00",
  "正在利用以下時間戳記服務憑證，驗證 存放庫副署 的時間戳記: ",
  "  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O=\"DigiCert, Inc.\", C=US",
  "  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E",
  "  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33",
  "  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59",
  "",
  "已完成，有 1 個錯誤和 0 個警告。",
  "error: NU3008: 套件完整性檢查失敗。套件在簽署後已變更。嘗試清除本機 HTTP 快取，然後再次執行 NuGet 作業。",
  "",
  "套件特徵標記驗證失敗。",
  "EV4_TAMPERED_EXIT=1",
  "ORIGINAL_AFTER_SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed",
  "X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行程式碼簽署。",
  "X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行時間戳記。",
  "",
  "正在驗證 Microsoft.Windows.SDK.BuildTools.10.0.28000.2705",
  "內容雜湊: TZQ96xtu7+fyFsyJCgj6Hazru0H8G1kiE1CeZLGpsqT4xKQmkxWu9yRuxYLeHJECjqEHN7duZUTcdbt8zlQ8OQ==",
  "C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\sdk.nupkg",
  "簽章雜湊演算法: SHA256",
  "",
  "簽章類型: Author",
  "正在利用以下憑證驗證 作者主要簽章: ",
  "  主體名稱: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US",
  "  SHA1 雜湊: F25C45D17C53D4E0D1DC9FB9DFD0731FCF904B77",
  "  SHA256 雜湊: 566A31882BE208BE4422F7CFD66ED09F5D4524A5994F50CCC8B05EC0528C1353",
  "  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2023/7/27 上午 08:00:00 至 2026/10/18 上午 07:59:59",
  "時間戳記: 2026/8/15 上午 04:35:41",
  "正在利用以下時間戳記服務憑證，驗證 作者主要簽章 的時間戳記: ",
  "  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O=\"DigiCert, Inc.\", C=US",
  "  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E",
  "  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33",
  "  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59",
  "",
  "簽章類型: Repository",
  "服務索引: https://api.nuget.org/v3/index.json",
  "擁有者: Microsoft, WindowsSDK",
  "正在利用以下憑證驗證 存放庫副署: ",
  "  主體名稱: CN=NuGet.org Repository by Microsoft, O=NuGet.org Repository by Microsoft, L=Redmond, S=Washington, C=US",
  "  SHA1 雜湊: C72FE7739A9EECB8EC1E4F596DB3BB74039B1DE2",
  "  SHA256 雜湊: 1F4B311D9ACC115C8DC8018B5A49E00FCE6DA8E2855F9F014CA6F34570BC482D",
  "  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2024/2/23 上午 08:00:00 至 2027/5/19 上午 07:59:59",
  "時間戳記: 2026/8/26 下午 12:54:00",
  "正在利用以下時間戳記服務憑證，驗證 存放庫副署 的時間戳記: ",
  "  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O=\"DigiCert, Inc.\", C=US",
  "  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E",
  "  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33",
  "  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O=\"DigiCert, Inc.\", C=US",
  "  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59",
  "",
  "已成功驗證套件 'Microsoft.Windows.SDK.BuildTools.10.0.28000.2705'。",
  "EV4_ORIGINAL_REVERIFY_EXIT=0",
  "NUSPEC_ID=Microsoft.Windows.SDK.BuildTools VERSION=10.0.28000.2705 ENTRY_LENGTH=914",
  "RETAINED_FILE=sdk.nupkg BYTES=22297017 SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed",
  "RETAINED_FILE=sdk-tampered.nupkg BYTES=22297017 SHA256=06add73b37945dae1488b34dcc8c92c8bd0acfded7af01c4ce14ff83544faae2",
  "RETAINED_FILE=nuget.config BYTES=497 SHA256=f297aae534f103b2572d56f9a973f824779afa952aa447ba72b32f3687c2679e",
  "RETAINED_FILE=nuget-wrong-signer.config BYTES=497 SHA256=776c18560e1f814b78d9d8a26c807168c49f599cb630cc013c120cc6748fe364",
  "OLD_AFTER=sdk.nupkg SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed",
  "OLD_AFTER=sdk-tampered.nupkg SHA256=06add73b37945dae1488b34dcc8c92c8bd0acfded7af01c4ce14ff83544faae2",
  "OLD_AFTER=nuget.config SHA256=f297aae534f103b2572d56f9a973f824779afa952aa447ba72b32f3687c2679e",
  "OLD_AFTER=nuget-wrong-signer.config SHA256=776c18560e1f814b78d9d8a26c807168c49f599cb630cc013c120cc6748fe364",
  "## main...origin/main [ahead 4]",
  "4e8746817bd25f9a7813acd7de60aa7af640da48",
  "EV1_TO_EV4_REPLAY_END_UTC=2026-09-07T06:27:04.5050098Z",
  "REPLAY_NATIVE_CHECKS=PASS REVIEW_REQUIRED=EV5",
  ""
]
```


