# ENV-MSIX-05 — Python packaging qualification blocked before execution

| Field | Value |
| --- | --- |
| Artifact ID / revision | `REVIEW-ENV-MSIX-05-20260907` / `02` |
| State | `OWNER_RESUMED / CAPABILITY_RECHECK / NOT_EXECUTED` |
| Admitted baseline | `275858692716b2ed06d7f76e1adb6cc114728466`, ENV-MSIX-05 document revision 01 |
| Ticket | [ENV-MSIX-05](../../../modules/tickets/local-orchestration-installer/env-msix-05-clean-python-packaging.md) |
| Result | No native execution, download, root creation, extraction, pip or packaging result; no qualification verdict |

## Blocker and actual observations — 2026-09-07

The first command-construction invocation failed JavaScript parsing before any
shell call (`SyntaxError: Unexpected token '^'`). After correcting that local
construction syntax, the acquisition/preflight command below was submitted once.
The execution tool **rejected process creation** with:

```text
exec_command failed: CreateProcess { message: "Rejected(... rejected: blocked by policy)" }
```

This is a concise excerpt, not an untruncated process log. The tool's own displayed
error truncated the echoed command; the exact submitted command is preserved
below. There is no native exit code or stdout/stderr to reconstruct. The tool
did not provide a more specific policy rule, so no cause such as network failure,
hash mismatch, missing package or owner's lack of authorization is inferred.

A subsequent read-only observation at the same baseline confirmed clean tracked
worktree and the exact ENV-MSIX-05 root absent. No alternative shell/channel,
privilege change, policy bypass or acquisition retry was attempted. SDK closure
at `0de3fae7473dff907c7c5f3ae0707cb90b62e286` remains valid and independent.

PY1–PY6 are **not executed / not qualified**, not red or green native tests.
The root's absence is evidence of no created action workspace, not a substitute
for the proposed transfer/verifier evidence. This is an operational blocker
record, not a completed code-review cycle; no adversarial helper was dispatched
to approve unexecuted work. Parent owns this halt.

Continuation requires resolving the execution-tool capability/policy issue
through its authorized controls, then Router admission/readback of this exact
ticket. Owner's prior authorization is recorded; asking for the same authorization
again does not establish executable capability. Do not silently change pins,
security policy or route effects through a different tool to evade the denial.
No push/release or product/VM/host effect has occurred in this action.

## Read-only post-denial readback

```powershell
git rev-parse HEAD
git status --short
Test-Path -LiteralPath 'C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\tests\.johnny-runtime\env-msix-05-python-20260907'

```

```json
{
  "chunk_id": "3ae28a",
  "wall_time_seconds": 0.9538563,
  "exit_code": 0,
  "original_token_count": 12,
  "output": "275858692716b2ed06d7f76e1adb6cc114728466\nFalse\r\n"
}
```

## Owner-requested diagnosis and bounded resumption — 2026-09-07

The owner requested immediate continuation. Parent performed read-only diagnostics:
PowerShell ParseInput returned 0 errors for the 7,782-character command; official
`codex execpolicy check` against the existing user rule file returned
`{"matchedRules":[]}` / exit 0. That rule file has 46 allow decisions and no
forbidden/prompt decisions. Local config reports danger-full-access and never.
These observations exclude those specific explanations, not all host policies.
No safety configuration was edited. The actual hidden rejection cause is unknown.

The same readback found the wrapper's absolute-path Join-Path bug, independently
of policy: joining repo cwd to the absolute CAP review path yielded a doubled
drive path and Test-Path=False. The corrected submission passes its canonical
relative path into Get-LfDigest, preserving the hash predicate. The action root
remains absent. Ticket revision 03 records a single owner-requested submission
through the same tool/security boundary; no alternative-channel execution.
Historical command/result below remain unchanged. No qualification is inferred
until a new actual execution capture and review exist.

Official [rules documentation](https://learn.chatgpt.com/docs/agent-configuration/rules)
defines the read-only checker; its local-file result is not complete host admission.

## Exact historical submitted command — NOT EXECUTED

Retained solely as evidence of the rejected request, not a replay instruction.

```powershell
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$repo='C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest'
$root=Join-Path $repo 'tests\.johnny-runtime\env-msix-05-python-20260907'
function ByteHash([string]$path) {
  $h=[Security.Cryptography.SHA256]::Create(); $s=[IO.File]::OpenRead($path)
  try { return [BitConverter]::ToString($h.ComputeHash($s)).Replace('-','').ToLowerInvariant() }
  finally { $s.Dispose(); $h.Dispose() }
}
function CheckPath([string]$path) {
 $n=Get-Item -LiteralPath $path -Force
 while ($null -ne $n) {
  Write-Output "PATH=$($n.FullName) ATTRIBUTES=$($n.Attributes)"
  if (($n.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_PATH' }
  if ($n -is [IO.DirectoryInfo]) { $n=$n.Parent } else { $n=$n.Directory }
 }
}
function NativeProbe([string]$label,[string]$exe,[string[]]$argv,[int]$expected) {
 $i=[Diagnostics.ProcessStartInfo]::new()
 $i.FileName=$exe
 $i.Arguments=($argv | ForEach-Object { if ($_ -match '["\r\n]') { throw 'UNSAFE_ARG' }; '"'+$_+'"' }) -join ' '
 $i.WorkingDirectory=Join-Path $root 'cwd'
 $i.UseShellExecute=$false; $i.CreateNoWindow=$true
 $i.RedirectStandardOutput=$true; $i.RedirectStandardError=$true
 $i.EnvironmentVariables.Clear()
 foreach ($pair in @(@('SystemRoot','C:\Windows'),@('WINDIR','C:\Windows'),@('COMSPEC','C:\Windows\System32\cmd.exe'),@('PATH','C:\Windows\System32;C:\Windows'),@('TEMP',(Join-Path $root 'temp')),@('TMP',(Join-Path $root 'temp')),@('USERPROFILE',(Join-Path $root 'user')),@('APPDATA',(Join-Path $root 'appdata')),@('LOCALAPPDATA',(Join-Path $root 'localappdata')),@('DOTNET_CLI_HOME',(Join-Path $root 'dotnet-home')),@('DOTNET_SKIP_FIRST_TIME_EXPERIENCE','1'),@('DOTNET_CLI_TELEMETRY_OPTOUT','1'),@('DOTNET_NOLOGO','1'),@('NUGET_PACKAGES',(Join-Path $root 'nuget-packages')),@('NUGET_HTTP_CACHE_PATH',(Join-Path $root 'nuget-http')),@('PIP_CONFIG_FILE','NUL'),@('PYINSTALLER_CONFIG_DIR',(Join-Path $root 'pyinstaller-cache')))) {
  $i.EnvironmentVariables[$pair[0]]=$pair[1]
 }
 Write-Output "NATIVE_BEGIN=$label UTC=$([DateTime]::UtcNow.ToString('o'))"
 Write-Output "EXE=$exe ARGS=$($i.Arguments) CWD=$($i.WorkingDirectory) ENVIRONMENT=EXACT_DECLARED_ALLOWLIST"
 $p=[Diagnostics.Process]::new(); $p.StartInfo=$i
 try {
  if (-not $p.Start()) { throw 'NOT_STARTED' }
  $out=$p.StandardOutput.ReadToEndAsync(); $err=$p.StandardError.ReadToEndAsync()
  if (-not $p.WaitForExit(60000)) { $p.Kill(); throw "OWNED_PROCESS_TIMEOUT=$label" }
  $stdout=$out.GetAwaiter().GetResult(); $stderr=$err.GetAwaiter().GetResult()
  Write-Output 'STDOUT_BEGIN'; Write-Output $stdout; Write-Output 'STDOUT_END'
  Write-Output 'STDERR_BEGIN'; Write-Output $stderr; Write-Output 'STDERR_END'
  Write-Output "NATIVE_EXIT=$($p.ExitCode) LABEL=$label UTC=$([DateTime]::UtcNow.ToString('o'))"
  if ($expected -eq 0 -and $p.ExitCode -ne 0) { throw "EXPECTED_SUCCESS_FAILED=$label" }
  if ($expected -eq 1 -and $p.ExitCode -eq 0) { throw "ZERO_RED_FINDING=$label" }
  if ($label -ceq 'VERIFIER_VERSION' -and $stdout.Trim() -cne '10.0.302') { throw 'SDK_VERSION_MISMATCH' }
 } finally { $p.Dispose() }
}
function Get-LfDigest([string]$Path) {
  $normalized = [IO.File]::ReadAllText((Join-Path (Get-Location) $Path)).Replace("`r`n", "`n")
  $hasher = [Security.Cryptography.SHA256]::Create()
  try { return [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($normalized))).Replace('-', '').ToLowerInvariant() } finally { $hasher.Dispose() }
}
Add-Type -AssemblyName System.Net.Http
$head=(& git rev-parse HEAD).Trim()
if ($head -cne '275858692716b2ed06d7f76e1adb6cc114728466' -or @(& git status --porcelain).Count -ne 0) { throw 'BASELINE_DIRTY_OR_MISMATCH' }
Write-Output "START_UTC=$([DateTime]::UtcNow.ToString('o')) EXECUTION_AUTHORITY=$head"
$capPath=Join-Path $repo 'doc\reviews\local-orchestration-installer\cap-msix-02-build-input-review.md'
if ((Get-LfDigest $capPath) -cne 'bf2c0419372b5962d30753237c60bc5eba9beb7699bfadbe96eb5deb44461222') { throw 'CAP_DIGEST_CHANGED' }
$dotnet='C:\Program Files\dotnet\dotnet.exe'
$dh=ByteHash $dotnet; $ds=Get-AuthenticodeSignature -LiteralPath $dotnet
Write-Output "VERIFIER=$dotnet SHA256=$dh SIGNATURE=$($ds.Status) SUBJECT=$($ds.SignerCertificate.Subject)"
if ($dh -cne '4377f10c78400f0370b88156773de9843c07f14e65b3232005ec3179ef38d463' -or $ds.Status.ToString() -cne 'Valid' -or $ds.SignerCertificate.Subject -notmatch 'Microsoft') { throw 'VERIFIER_INVALID' }
if (Test-Path -LiteralPath $root) { throw 'ROOT_EXISTS' }
CheckPath (Split-Path -Parent $root)
Write-Output "FRESH_ROOT_ABSENT=$root"
New-Item -ItemType Directory -Path $root | Out-Null
foreach ($d in @('wheels','cwd','temp','user','appdata','localappdata','dotnet-home','nuget-packages','nuget-http','pyinstaller-cache')) { New-Item -ItemType Directory -Path (Join-Path $root $d) | Out-Null }
NativeProbe 'VERIFIER_VERSION' $dotnet @('--version') 0
function Acquire([string]$url,[string]$dest,[string]$algorithm,[string]$expected,[long]$expectedSize) {
 $handler=[Net.Http.HttpClientHandler]::new()
 $handler.AllowAutoRedirect=$false; $handler.UseProxy=$false; $handler.UseCookies=$false; $handler.UseDefaultCredentials=$false
 $c=[Net.Http.HttpClient]::new($handler); $c.Timeout=[TimeSpan]::FromSeconds(60); $c.MaxResponseContentBufferSize=67108864
 try {
  Write-Output "HTTP_BEGIN=$url UTC=$([DateTime]::UtcNow.ToString('o')) MAX_BYTES=67108864 TIMEOUT_SECONDS=60 REDIRECT=False PROXY=False DEFAULT_CREDENTIALS=False COOKIES=False"
  $r=$c.GetAsync($url).GetAwaiter().GetResult()
  try {
   Write-Output "HTTP_STATUS=$([int]$r.StatusCode) URI=$($r.RequestMessage.RequestUri.AbsoluteUri)"
   if ([int]$r.StatusCode -ne 200 -or $r.RequestMessage.RequestUri.AbsoluteUri -cne $url) { throw 'HTTP_SOURCE_FAILED' }
   $bytes=$r.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
   if ($bytes.LongLength -gt 67108864 -or ($expectedSize -gt 0 -and $bytes.LongLength -ne $expectedSize)) { throw 'HTTP_SIZE_FAILED' }
   $h=[Security.Cryptography.HashAlgorithm]::Create($algorithm)
   try {
    $digestBytes=$h.ComputeHash($bytes)
    $digest=if ($algorithm -ceq 'SHA512') { [Convert]::ToBase64String($digestBytes) } else { [BitConverter]::ToString($digestBytes).Replace('-','').ToLowerInvariant() }
    Write-Output "HTTP_BYTES=$($bytes.LongLength) $algorithm=$digest"
    if ($digest -cne $expected) { throw 'DOWNLOAD_DIGEST_MISMATCH' }
    $f=[IO.FileStream]::new($dest,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $f.Write($bytes,0,$bytes.Length); $f.Flush($true) } finally { $f.Dispose() }
    $f=[IO.File]::OpenRead($dest)
    try { $disk=$h.ComputeHash($f) } finally { $f.Dispose() }
    if ([Convert]::ToBase64String($disk) -cne [Convert]::ToBase64String($digestBytes)) { throw 'DISK_DIGEST_MISMATCH' }
   } finally { $h.Dispose() }
   Write-Output "STORED=$dest SHA256=$(ByteHash $dest) UTC=$([DateTime]::UtcNow.ToString('o'))"
  } finally { $r.Dispose() }
 } finally { $c.Dispose(); $handler.Dispose() }
}
Acquire 'https://api.nuget.org/v3-flatcontainer/python/3.11.9/python.3.11.9.nupkg' (Join-Path $root 'python.nupkg') 'SHA512' '41On79FZ75irnOEBGFSjDV13j1nZb8m7EbB87SmQs1XwMEhrBwf3mMc8RCAXOrERh2qW6tWYFxi2BMTN1xxVjQ==' 17478009
$rows=(Get-Content -LiteralPath $capPath -Raw) -split [char]10 | Where-Object { $_ -match '^\| [^|]+==[^|]+\|' }
if (@($rows).Count -ne 7) { throw 'WHEEL_COUNT' }
foreach ($row in $rows) {
 $m=[regex]::Match($row,'\]\((https://files[.]pythonhosted[.]org/[^)]+)\).*?([a-f0-9]{64})')
 if (-not $m.Success) { throw 'WHEEL_ROW_INVALID' }
 $url=$m.Groups[1].Value; $pin=$m.Groups[2].Value
 $name=[IO.Path]::GetFileName(([uri]$url).AbsolutePath)
 Acquire $url (Join-Path (Join-Path $root 'wheels') $name) 'SHA256' $pin 0
}
Write-Output 'PY1_EIGHT_ARTIFACTS_ACQUIRED=PASS'

```
