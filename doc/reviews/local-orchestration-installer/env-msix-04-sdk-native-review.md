# ENV-MSIX-04 — SDK native operation review

| Field | Value |
| --- | --- |
| Artifact ID / revision | `REVIEW-ENV-MSIX-04-20260907` / `01` |
| State | `EXECUTED / REVIEW_PENDING` |
| Execution authority | `c6b9ad1a10acae3d542584a49e7b2e3061c6b810`, ENV-MSIX-04 document revision 01 / closure revision 01 |
| Ticket | [ENV-MSIX-04](../../../modules/tickets/local-orchestration-installer/env-msix-04-sdk-native-qualification.md) |
| Result boundary | SDK operations on this build host only; no Johnny application, installation, registration, signing, host activation or release claim |
| Reviewer | Current-session parent owns final adjudication; existing read-only adversarial helper supplies findings only |

## Observed result and parent preliminary evaluation

The parent personally executed the admitted extraction and six finite native calls
on 2026-09-07, preserving their complete commands and returned outputs below.
The execution host was Windows 10 build 19045 x64, **not** the Windows 11 lab VM.
Only the exact ignored ENV-MSIX-04 root was created/used. The inherited trusted
OS/native DLL and OS-managed trust/cache assumptions remain explicit; this does
not certify an uncompromised machine or zero OS cache activity.

| Cell | Actual observation | Preliminary disposition |
| --- | --- | --- |
| NT1 | Exact authenticated archive SHA, fresh non-reparse root; 37 selected members / 6,710,968 bytes; all seven exe/DLL Authenticode Valid/Microsoft; complete hashes/versions | Satisfied |
| NT2 | Native validated pack exit 0; unpack exit 0; manifest/logo/text hashes identical; generated AppxBlockMap.xml separately recorded | Satisfied |
| NT3 | Separate missing.png Logo fixture exit 1, intended 0x80080204 missing-file validation; positive input bytes preserved | Satisfied |
| NT4 | Repack with /no exit 1, intended 0x80070050 existing output; original package SHA unchanged | Satisfied |
| NT5 | SignTool signed MakeAppx verification exit 0; unsigned test package exit 1, explicit No signature found | Satisfied |
| NT6 | Complete capture, unchanged archive and zero tracked changes during native phase; consumed execution metadata recorded before helper; final review still pending | Pending helper + final parent outcome |

SDK MakeAppx reports version 10.0.28000.2705. SignTool file-version metadata is
4.00 (WinBuild.160101.0800); it is not relabeled as MakeAppx's version.
SignTool's printed Authenticode image digest is not the whole-file SHA256:
the native file's whole-byte hash is preserved in NT1. These are distinct hashes,
not an unexplained mismatch.

Test package whole-file SHA256:
`c258fca73d190cb9e102d2fba97f1f1740805345c410cc6479c2a271117c41fe`.
The positive fixture is a data-only unsigned **framework** package. There was no
application executable or install/launch probe. Framework pack success does not
prove the future full-trust application's identity, dependency closure or lifecycle.
The SDK itself removed its newly failed missing-logo output, as printed; no
material user artifact was deleted and no cleanup command was run.

## Review plan

REQUIRED adversarial review by the same existing helper, exact committed evidence
candidate plus execution authority above. Categories: SPEC_GAP, AUTHORIZATION,
ERROR_PARTIAL_FAILURE, CONSISTENCY, IDEMPOTENCY, OBSERVABILITY.
Isolation: READ_ONLY_INTENT_ONLY. Effects: NO_EXTERNAL_EFFECT. Read the complete
ticket/report and their direct index rows; compare claimed cells with actual output,
negative cause, path/supply-chain boundaries, fixture identity and lifecycle state.
Do not execute captured commands, SDK tools, mutate files/refs, acquire anything,
or touch VM/trust/host state. Return finite findings, not approval. The parent alone
decides closure under the existing one-correction bound.

## Complete execution capture

Each command body below is the actual tool input, not a reconstructed shorthand.
Each JSON result is the complete tool-return object, with its unfiltered output
string and native stdout/stderr boundaries. JSON escape decoding preserves all
returned characters/newlines, including doubled CR and terminal encoding question
marks in localized OS messages. This is lossless capture of **returned text**, not
a claim that raw native output bytes were captured. Intended negative causes are
also present as English text and HRESULTs, independent of the localized message.
No further native call is authorized merely because its command is recorded here.

### NT1 extraction and signatures

```powershell
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
Add-Type -AssemblyName System.IO.Compression.FileSystem
$repo='C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest'
$root=Join-Path $repo 'tests\.johnny-runtime\env-msix-04-sdk-native-20260907'
$archive=Join-Path $repo 'tests\.johnny-runtime\env-msix-03-sdk-replay-20260907-01\sdk.nupkg'
function ByteHash([string]$path) {
  $h=[Security.Cryptography.SHA256]::Create()
  $s=[IO.File]::OpenRead($path)
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
Set-Location $repo
$head=(& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -cne 'c6b9ad1a10acae3d542584a49e7b2e3061c6b810') { throw 'BASELINE_MISMATCH' }
if (@(& git status --porcelain).Count -ne 0) { throw 'DIRTY_WORKTREE' }
Write-Output "START_UTC=$([DateTime]::UtcNow.ToString('o')) EXECUTION_CANDIDATE=$head"
Write-Output "OS_VERSION=$([Environment]::OSVersion.VersionString) IS_64BIT_OS=$([Environment]::Is64BitOperatingSystem) IS_64BIT_PROCESS=$([Environment]::Is64BitProcess)"
Write-Output "KERNEL32_VERSION=$((Get-Item -LiteralPath 'C:\Windows\System32\kernel32.dll').VersionInfo.FileVersion)"
if (-not [Environment]::Is64BitProcess) { throw 'X64_HOST_REQUIRED' }
CheckPath $archive
$archiveHash=ByteHash $archive
Write-Output "ARCHIVE_SHA256=$archiveHash"
if ($archiveHash -cne '8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed') { throw 'ARCHIVE_HASH_MISMATCH' }
$review=[IO.File]::ReadAllText((Join-Path $repo 'doc\reviews\local-orchestration-installer\env-msix-03-sdk-archive-review.md')).Replace(([string][char]13+[char]10),[string][char]10)
$hash=[Security.Cryptography.SHA256]::Create()
try { $reviewHash=[BitConverter]::ToString($hash.ComputeHash([Text.Encoding]::UTF8.GetBytes($review))).Replace('-','').ToLowerInvariant() } finally { $hash.Dispose() }
if ($reviewHash -cne '96bbda5f1dd3642eec5336705f6d7fee0ab95d37566c2f5d55a9fdfd7133b4d6') { throw 'REVIEW_CHANGED' }
Write-Output "ENV3_REVIEW_LF_SHA256=$reviewHash"
$index=Get-Content -LiteralPath (Join-Path $repo 'doc\reviews\local-orchestration-installer\README.md') -Raw
if (-not $index.Contains($reviewHash)) { throw 'REVIEW_INDEX_MISMATCH' }
if (Test-Path -LiteralPath $root) { throw 'ROOT_ALREADY_EXISTS' }
CheckPath (Split-Path -Parent $root)
Write-Output "NEW_ROOT_ABSENT=$root"
$names=@('makeappx.exe','signtool.exe','appxpackaging.dll','appxsip.dll','opcservices.dll','mssign32.dll','wintrust.dll','signtool.exe.manifest','wintrust.dll.ini','Microsoft.Windows.Build.Appx.AppxPackaging.dll.manifest','Microsoft.Windows.Build.Appx.AppxSip.dll.manifest','Microsoft.Windows.Build.Appx.OpcServices.dll.manifest','Microsoft.Windows.Build.Signing.mssign32.dll.manifest','Microsoft.Windows.Build.Signing.wintrust.dll.manifest','en-US/AppxPackaging.dll.mui')
$prefix='bin/10.0.28000.0/x64/'
$zip=[IO.Compression.ZipFile]::OpenRead($archive)
try {
  $selected=@($zip.Entries | Where-Object { ($_.FullName.StartsWith($prefix,[StringComparison]::Ordinal) -and $names -ccontains $_.FullName.Substring($prefix.Length)) -or $_.FullName -cmatch '^schemas/10[.]0[.]28000[.]0/winrt/[^/]+[.]xsd$' })
  if ($selected.Count -gt 128 -or $selected.Count -le $names.Count) { throw 'ENTRY_COUNT_INVALID' }
  foreach ($name in $names) { if (@($selected | Where-Object { $_.FullName -ceq ($prefix+$name) }).Count -ne 1) { throw 'REQUIRED_ENTRY_MISSING_OR_DUPLICATE' } }
  $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
  [long]$total=0
  foreach ($entry in $selected) {
    if (-not $seen.Add($entry.FullName) -or $entry.FullName -match '(^/|\\|:|(^|/)[.][.]?(/|$)|[. ](/|$))') { throw 'ENTRY_PATH_INVALID' }
    if ((($entry.ExternalAttributes -shr 16) -band 61440) -eq 40960 -or ($entry.ExternalAttributes -band 1024) -ne 0) { throw 'LINK_ENTRY_REJECTED' }
    if ($entry.Length -gt 16777216 -or $entry.Length -lt 0) { throw 'ENTRY_TOO_LARGE' }
    $total += $entry.Length
  }
  if ($total -gt 67108864) { throw 'EXTRACTION_TOO_LARGE' }
  Write-Output "SELECTED_COUNT=$($selected.Count) TOTAL_UNCOMPRESSED=$total"
  New-Item -ItemType Directory -Path $root | Out-Null
  $tools=Join-Path $root 'tools'
  New-Item -ItemType Directory -Path $tools | Out-Null
  foreach ($entry in $selected) {
    $dest=[IO.Path]::GetFullPath((Join-Path $tools $entry.FullName))
    if (-not $dest.StartsWith(($tools+'\'),[StringComparison]::OrdinalIgnoreCase)) { throw 'EXTRACTION_ESCAPE' }
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($dest)) | Out-Null
    $source=$entry.Open()
    $target=[IO.FileStream]::new($dest,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $source.CopyTo($target); $target.Flush($true) } finally { $target.Dispose(); $source.Dispose() }
    if ((Get-Item -LiteralPath $dest).Length -ne $entry.Length) { throw 'EXTRACTION_LENGTH_MISMATCH' }
    Write-Output "EXTRACTED=$($entry.FullName) BYTES=$($entry.Length) SHA256=$(ByteHash $dest)"
  }
} finally { $zip.Dispose() }
$bin=Join-Path $root 'tools\bin\10.0.28000.0\x64'
foreach ($name in @('makeappx.exe','signtool.exe','appxpackaging.dll','appxsip.dll','opcservices.dll','mssign32.dll','wintrust.dll')) {
  $path=Join-Path $bin $name
  $sig=Get-AuthenticodeSignature -LiteralPath $path
  Write-Output "NATIVE=$name VERSION=$((Get-Item -LiteralPath $path).VersionInfo.FileVersion) SIGNATURE=$($sig.Status) SUBJECT=$($sig.SignerCertificate.Subject)"
  if ($sig.Status.ToString() -cne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'Microsoft') { throw 'NATIVE_SIGNATURE_INVALID' }
}
if ((ByteHash $archive) -cne $archiveHash) { throw 'ARCHIVE_CHANGED' }
CheckPath $root
foreach ($child in @('positive','missing-logo','temp')) { New-Item -ItemType Directory -Path (Join-Path $root $child) | Out-Null }
Write-Output 'NT1_EXTRACTION_SIGNATURE=PASS'
Write-Output "END_UTC=$([DateTime]::UtcNow.ToString('o'))"
```

```json
{
  "chunk_id": "47772b",
  "wall_time_seconds": 4.9052973,
  "exit_code": 0,
  "original_token_count": 2255,
  "output": "START_UTC=2026-09-07T07:14:02.1635662Z EXECUTION_CANDIDATE=c6b9ad1a10acae3d542584a49e7b2e3061c6b810\r\nOS_VERSION=Microsoft Windows NT 10.0.19045.0 IS_64BIT_OS=True IS_64BIT_PROCESS=True\r\nKERNEL32_VERSION=10.0.19041.4842 (WinBuild.160101.0800)\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01\\sdk.nupkg ATTRIBUTES=Archive\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-03-sdk-replay-20260907-01 ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop ATTRIBUTES=ReadOnly, Directory\r\nPATH=C:\\Users\\GameBoy ATTRIBUTES=Directory\r\nPATH=C:\\Users ATTRIBUTES=ReadOnly, Directory\r\nPATH=C:\\ ATTRIBUTES=Hidden, System, Directory\r\nARCHIVE_SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed\r\nENV3_REVIEW_LF_SHA256=96bbda5f1dd3642eec5336705f6d7fee0ab95d37566c2f5d55a9fdfd7133b4d6\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop ATTRIBUTES=ReadOnly, Directory\r\nPATH=C:\\Users\\GameBoy ATTRIBUTES=Directory\r\nPATH=C:\\Users ATTRIBUTES=ReadOnly, Directory\r\nPATH=C:\\ ATTRIBUTES=Hidden, System, Directory\r\nNEW_ROOT_ABSENT=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\r\nSELECTED_COUNT=37 TOTAL_UNCOMPRESSED=6710968\r\nEXTRACTED=bin/10.0.28000.0/x64/appxpackaging.dll BYTES=2443720 SHA256=3437f43e925cdf3af77ffba2e85a97d0413644b35428335f0f8b1f52fcd1ba12\r\nEXTRACTED=bin/10.0.28000.0/x64/appxsip.dll BYTES=465392 SHA256=9ec9ce1865851b01dec2ea702e57b827993e41c90c81146d3b0390839764c330\r\nEXTRACTED=bin/10.0.28000.0/x64/en-US/AppxPackaging.dll.mui BYTES=97224 SHA256=faf1505fb4a8ca5518808841801c6ff9f9e97de65feb0a77aa2b41c3e34501a0\r\nEXTRACTED=schemas/10.0.28000.0/winrt/AppxManifestSchema.xsd BYTES=35530 SHA256=b2f322fb4552bc6365e54699ab6b4491c9015db2785f4b58f936b6536a6e08e0\r\nEXTRACTED=schemas/10.0.28000.0/winrt/AppxManifestSchema2010_v2.xsd BYTES=36908 SHA256=9c5534d4542982713ecc5051a4c783fd4ab2b6b2e48aad690da41dd3d710c0b4\r\nEXTRACTED=schemas/10.0.28000.0/winrt/AppxManifestSchema2013.xsd BYTES=12335 SHA256=5f4d752fbda7e0f7cb99d5e7c31fc640b9af6ef4ec9ee5404de375532fd7422b\r\nEXTRACTED=schemas/10.0.28000.0/winrt/FoundationManifestSchema.xsd BYTES=31062 SHA256=1e20f352da120946a490ca97f427bcbe5216ccbe57bb0cdc5b579b22e1b3b820\r\nEXTRACTED=schemas/10.0.28000.0/winrt/FoundationManifestSchema_v2.xsd BYTES=1200 SHA256=f326bcaeef69cb884a76bf2f27d62fd720b8318e4c8ace693aa71ee174020fb5\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema.xsd BYTES=17538 SHA256=b9bc778d6c7bb96432e76f2bea67f969bc572bc793f693db8cb2785a715ed5d9\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v10.xsd BYTES=8362 SHA256=7af086c3b8e1a6bfcda01098aea3299f2ed9130fb84049ae9b929c10b6bc67c4\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v11.xsd BYTES=2536 SHA256=08d8bc9f317d26157acdacf258575ed04ad16f0c69d465a45c0668f2a035cc9c\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v12.xsd BYTES=1728 SHA256=819d6d516586786745083326aad48df43e6f49bcb7e10f8c64082fbc154f9f1c\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v13.xsd BYTES=2817 SHA256=e3303cd0a7fce2f25df791d9591baebfec421d0b572df8716e1db1116aad3456\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v15.xsd BYTES=833 SHA256=3c1915b184b1b1025dcbad9b2a69f89e356214d785827145392af52f51b0cf27\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v15a.xsd BYTES=924 SHA256=93440fe5d80ea633062db69da82651adef4fcfefee4d015a72d4df1535e570b9\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v16.xsd BYTES=867 SHA256=4fb245dbf7f4dd702ab258220ab7239b8a1af2a4f92d70ca9b1e7b413fcfafd1\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v17.xsd BYTES=3889 SHA256=e04fdb88bee37a74e7c968518fac25a2c48a44d10d8c9e09e1daabd4959dd591\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v18.xsd BYTES=994 SHA256=403e90ad3df82f9a4a22a52aa18bc795aef874372a7f13bf3354c3f54ca097f9\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v2.xsd BYTES=4665 SHA256=1b0ccfb95c35a4dc9309780365878f907f1d3748ade61497cec76578848245c0\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v3.xsd BYTES=8469 SHA256=9c7369a354dae05bc975d8520d9dbffe62443c8e49403c987f032de5f61e9cb9\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v4.xsd BYTES=10080 SHA256=3ae40452a840933b0637f642dd011ed1889d0e3157c78cb9b0537fca690c5697\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v5.xsd BYTES=10460 SHA256=8c76e442d169b96225b17e99b75f54353ba240af6b406f6de49e89abb2bdc7b3\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v6.xsd BYTES=4232 SHA256=45d52be6a0e9ce37e8004970888a54a020ff89729c7e6791403a08c8122caff2\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v7.xsd BYTES=3590 SHA256=8354916aefae694876d5a8391578996e048bfbba14b7cc5e4551e83b3a9f8deb\r\nEXTRACTED=schemas/10.0.28000.0/winrt/UapManifestSchema_v8.xsd BYTES=5063 SHA256=58c48d7a4827076d600c0105825794a2210ba17245c624423d7bf19e20482476\r\nEXTRACTED=bin/10.0.28000.0/x64/makeappx.exe BYTES=588272 SHA256=98ddf5a4fdb38a1d32c2ca7b350a2012ed430d277baa1bf03ac91ef82365f1d3\r\nEXTRACTED=bin/10.0.28000.0/x64/Microsoft.Windows.Build.Appx.AppxPackaging.dll.manifest BYTES=1924 SHA256=b50d228857d9cd6509854feacdc153a78804be4312bf699298dbf6a5bd846ddd\r\nEXTRACTED=bin/10.0.28000.0/x64/Microsoft.Windows.Build.Appx.AppxSip.dll.manifest BYTES=491 SHA256=bf9dadc2a05e46f479f8bdc4ebda515682449cfe04794afb9b8a9cf12edf7f4e\r\nEXTRACTED=bin/10.0.28000.0/x64/Microsoft.Windows.Build.Appx.OpcServices.dll.manifest BYTES=450 SHA256=7babce6a576b434c71b93797ac6968963a9c23feea56d8d45faeeaa8175907ec\r\nEXTRACTED=bin/10.0.28000.0/x64/Microsoft.Windows.Build.Signing.mssign32.dll.manifest BYTES=238 SHA256=e0c65f5b5f5ae116abbb566dc7ddf95b666fc9a7f327afa67502100954d8d713\r\nEXTRACTED=bin/10.0.28000.0/x64/Microsoft.Windows.Build.Signing.wintrust.dll.manifest BYTES=238 SHA256=9a6e1a316f4148eaace69326f5f99a6a7ac4e9b58b5c22082f6603dd964bfad9\r\nEXTRACTED=bin/10.0.28000.0/x64/mssign32.dll BYTES=149960 SHA256=04a203bf583d4bb664b0b9c570150c243be22a061a81cf69ccfe27efc90132d7\r\nEXTRACTED=bin/10.0.28000.0/x64/opcservices.dll BYTES=1743304 SHA256=11e20c4673d403c6aa2ee2f7ea85194c2e430e5d4245fcbaba207a6a80e48f24\r\nEXTRACTED=bin/10.0.28000.0/x64/signtool.exe BYTES=551368 SHA256=d6c04707c59a67fce9fa4bb5fe76c79445b60e1e326d8b500a2f2ba8707c590a\r\nEXTRACTED=bin/10.0.28000.0/x64/signtool.exe.manifest BYTES=968 SHA256=c1a768e47b3d054eee0d8ab9027eba122a52bf6a058ae1c02e4ddcb96cf4b09f\r\nEXTRACTED=bin/10.0.28000.0/x64/wintrust.dll BYTES=461256 SHA256=0ae34a731e4ce6ba394fb294f079884cafbccfa9ff3ac899455d4a9758136cf2\r\nEXTRACTED=bin/10.0.28000.0/x64/wintrust.dll.ini BYTES=2081 SHA256=ca458c3ff25d27a7c61674ee9547f13fc70c7208583cbfba75ca39b4098fa21c\r\nNATIVE=makeappx.exe VERSION=10.0.28000.2705 (WinBuild.160101.0800) SIGNATURE=Valid SUBJECT=CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US\r\nNATIVE=signtool.exe VERSION=4.00 (WinBuild.160101.0800) SIGNATURE=Valid SUBJECT=CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US\r\nNATIVE=appxpackaging.dll VERSION=10.0.28000.2705 (WinBuild.160101.0800) SIGNATURE=Valid SUBJECT=CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US\r\nNATIVE=appxsip.dll VERSION=10.0.28000.2705 (WinBuild.160101.0800) SIGNATURE=Valid SUBJECT=CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US\r\nNATIVE=opcservices.dll VERSION=10.0.28000.2705 (WinBuild.160101.0800) SIGNATURE=Valid SUBJECT=CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US\r\nNATIVE=mssign32.dll VERSION=10.0.28000.2705 (WinBuild.160101.0800) SIGNATURE=Valid SUBJECT=CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US\r\nNATIVE=wintrust.dll VERSION=10.0.28000.2705 (WinBuild.160101.0800) SIGNATURE=Valid SUBJECT=CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907 ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest ATTRIBUTES=Directory\r\nPATH=C:\\Users\\GameBoy\\Desktop ATTRIBUTES=ReadOnly, Directory\r\nPATH=C:\\Users\\GameBoy ATTRIBUTES=Directory\r\nPATH=C:\\Users ATTRIBUTES=ReadOnly, Directory\r\nPATH=C:\\ ATTRIBUTES=Hidden, System, Directory\r\nNT1_EXTRACTION_SIGNATURE=PASS\r\nEND_UTC=2026-09-07T07:14:05.7821529Z\r\n"
}
```

### Data-only fixture creation

```diff
*** Begin Patch
*** Add File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/tests/.johnny-runtime/env-msix-04-sdk-native-20260907/positive/AppxManifest.xml
+<?xml version="1.0" encoding="utf-8"?>
+<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10">
+  <Identity Name="Johnny.Toolchain.Probe" Publisher="CN=JohnnyToolchainProbe" Version="0.0.0.1" ProcessorArchitecture="x64" />
+  <Properties>
+    <DisplayName>Johnny Toolchain Probe</DisplayName>
+    <PublisherDisplayName>Johnny Toolchain Probe</PublisherDisplayName>
+    <Logo>logo.png</Logo>
+    <Framework>true</Framework>
+  </Properties>
+  <Resources><Resource Language="en-US" /></Resources>
+  <Dependencies>
+    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.26200.0" />
+  </Dependencies>
+</Package>
*** Add File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/tests/.johnny-runtime/env-msix-04-sdk-native-20260907/positive/probe.txt
+ENV-MSIX-04 data-only native toolchain probe. Not an installable Johnny application.
*** Add File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/tests/.johnny-runtime/env-msix-04-sdk-native-20260907/missing-logo/AppxManifest.xml
+<?xml version="1.0" encoding="utf-8"?>
+<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10">
+  <Identity Name="Johnny.Toolchain.Probe" Publisher="CN=JohnnyToolchainProbe" Version="0.0.0.1" ProcessorArchitecture="x64" />
+  <Properties>
+    <DisplayName>Johnny Toolchain Probe</DisplayName>
+    <PublisherDisplayName>Johnny Toolchain Probe</PublisherDisplayName>
+    <Logo>missing.png</Logo>
+    <Framework>true</Framework>
+  </Properties>
+  <Resources><Resource Language="en-US" /></Resources>
+  <Dependencies>
+    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.26200.0" />
+  </Dependencies>
+</Package>
*** Add File: C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/tests/.johnny-runtime/env-msix-04-sdk-native-20260907/missing-logo/probe.txt
+ENV-MSIX-04 data-only native toolchain probe. Not an installable Johnny application.
*** End Patch
```

```json
{}
```

### NT2 native positive pack/unpack

```powershell
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$repo='C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest'
$root=Join-Path $repo 'tests\.johnny-runtime\env-msix-04-sdk-native-20260907'
$bin=Join-Path $root 'tools\bin\10.0.28000.0\x64'
function ByteHash([string]$path) {
  $h=[Security.Cryptography.SHA256]::Create(); $s=[IO.File]::OpenRead($path)
  try { return [BitConverter]::ToString($h.ComputeHash($s)).Replace('-','').ToLowerInvariant() }
  finally { $s.Dispose(); $h.Dispose() }
}
function NativeProbe([string]$label,[string]$exe,[string[]]$argv,[int]$expected) {
  $info=[Diagnostics.ProcessStartInfo]::new()
  $info.FileName=$exe
  $info.Arguments=($argv | ForEach-Object { if ($_ -match '["\r\n]') { throw 'UNSAFE_ARG' }; '"'+$_+'"' }) -join ' '
  $info.WorkingDirectory=$root
  $info.UseShellExecute=$false
  $info.CreateNoWindow=$true
  $info.RedirectStandardOutput=$true
  $info.RedirectStandardError=$true
  $info.EnvironmentVariables['PATH']='C:\Windows\System32;C:\Windows'
  $info.EnvironmentVariables['TEMP']=Join-Path $root 'temp'
  $info.EnvironmentVariables['TMP']=Join-Path $root 'temp'
  Write-Output "NATIVE_BEGIN=$label UTC=$([DateTime]::UtcNow.ToString('o'))"
  Write-Output "EXE=$exe ARGUMENTS=$($info.Arguments) CWD=$root"
  $p=[Diagnostics.Process]::new(); $p.StartInfo=$info
  try {
    if (-not $p.Start()) { throw 'PROCESS_NOT_STARTED' }
    $out=$p.StandardOutput.ReadToEndAsync()
    $err=$p.StandardError.ReadToEndAsync()
    if (-not $p.WaitForExit(60000)) { $p.Kill(); throw "OWNED_PROCESS_TIMEOUT=$label" }
    $stdout=$out.GetAwaiter().GetResult(); $stderr=$err.GetAwaiter().GetResult()
    Write-Output 'STDOUT_BEGIN'; Write-Output $stdout; Write-Output 'STDOUT_END'
    Write-Output 'STDERR_BEGIN'; Write-Output $stderr; Write-Output 'STDERR_END'
    Write-Output "NATIVE_EXIT=$($p.ExitCode) LABEL=$label UTC=$([DateTime]::UtcNow.ToString('o'))"
    if ($expected -eq 0 -and $p.ExitCode -ne 0) { throw "EXPECTED_SUCCESS_FAILED=$label" }
    if ($expected -eq 1 -and $p.ExitCode -eq 0) { throw "ZERO_RED_FINDING=$label" }
  } finally { $p.Dispose() }
}

if ((& git rev-parse HEAD).Trim() -cne 'c6b9ad1a10acae3d542584a49e7b2e3061c6b810') { throw 'BASELINE_MISMATCH' }
Add-Type -AssemblyName System.Drawing
foreach ($fixture in @('positive','missing-logo')) {
  $dir=Join-Path $root $fixture
  $logo=Join-Path $dir 'logo.png'
  if (Test-Path -LiteralPath $logo) { throw 'LOGO_EXISTS' }
  $bmp=[Drawing.Bitmap]::new(50,50)
  $graphics=[Drawing.Graphics]::FromImage($bmp)
  $stream=[IO.FileStream]::new($logo,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  try {
    $graphics.Clear([Drawing.Color]::FromArgb(255,20,70,130))
    $bmp.Save($stream,[Drawing.Imaging.ImageFormat]::Png)
    $stream.Flush($true)
  } finally { $stream.Dispose(); $graphics.Dispose(); $bmp.Dispose() }
  foreach ($name in @('AppxManifest.xml','probe.txt','logo.png')) {
    Write-Output "INPUT=$fixture/$name SHA256=$(ByteHash (Join-Path $dir $name))"
  }
}
if ((ByteHash (Join-Path $root 'positive\logo.png')) -cne (ByteHash (Join-Path $root 'missing-logo\logo.png'))) { throw 'LOGO_BYTES_DIFFER' }
NativeProbe 'NT2_PACK' (Join-Path $bin 'makeappx.exe') @('pack','/v','/no','/h','SHA256','/d',(Join-Path $root 'positive'),'/p',(Join-Path $root 'positive.msix')) 0
NativeProbe 'NT2_UNPACK' (Join-Path $bin 'makeappx.exe') @('unpack','/v','/no','/p',(Join-Path $root 'positive.msix'),'/d',(Join-Path $root 'unpacked')) 0
foreach ($name in @('AppxManifest.xml','probe.txt','logo.png')) {
  $a=ByteHash (Join-Path (Join-Path $root 'positive') $name)
  $b=ByteHash (Join-Path (Join-Path $root 'unpacked') $name)
  Write-Output "ROUNDTRIP=$name INPUT_SHA256=$a OUTPUT_SHA256=$b"
  if ($a -cne $b) { throw "ROUNDTRIP_BYTES_DIFFER=$name" }
}
Get-ChildItem -LiteralPath (Join-Path $root 'unpacked') -File -Recurse | ForEach-Object { Write-Output "UNPACKED=$($_.FullName.Substring($root.Length+1)) SHA256=$(ByteHash $_.FullName)" }
Write-Output "PACKAGE_SHA256=$(ByteHash (Join-Path $root 'positive.msix'))"
Write-Output 'NT2_PACK_UNPACK=PASS'

```

```json
{
  "chunk_id": "3f9293",
  "wall_time_seconds": 1.9306922,
  "exit_code": 0,
  "original_token_count": 1607,
  "output": "INPUT=positive/AppxManifest.xml SHA256=f1dac3cf6532ba27c73670566c60ff902c070fa8da651635bc683b332cef428a\r\nINPUT=positive/probe.txt SHA256=7279571882f7cbe5b070fc4e8e9c06e9b84176439ee9492ae0e7c2e4fea75e0e\r\nINPUT=positive/logo.png SHA256=ef5fdf2c53dfeb2cb409f84bbefe4d1b7b611b6d8eb142bb9319780aea9b393a\r\nINPUT=missing-logo/AppxManifest.xml SHA256=dac51f6d893d317d965a7a30acdc932c8a7ece3e37cce4c2d8e7869f02e69c16\r\nINPUT=missing-logo/probe.txt SHA256=7279571882f7cbe5b070fc4e8e9c06e9b84176439ee9492ae0e7c2e4fea75e0e\r\nINPUT=missing-logo/logo.png SHA256=ef5fdf2c53dfeb2cb409f84bbefe4d1b7b611b6d8eb142bb9319780aea9b393a\r\nNATIVE_BEGIN=NT2_PACK UTC=2026-09-07T07:18:41.9796953Z\r\nEXE=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\tools\\bin\\10.0.28000.0\\x64\\makeappx.exe ARGUMENTS=\"pack\" \"/v\" \"/no\" \"/h\" \"SHA256\" \"/d\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\" \"/p\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\" CWD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\r\nSTDOUT_BEGIN\r\nMicrosoft (R) MakeAppx Tool\r\r\nVersion 10.0.28000.2705\r\r\nCopyright (C) Microsoft. All rights reserved.\r\r\n\r\r\nOption /v specified, switching to verbose output.\r\r\nOption /no specified, existing files will be preserved.\r\r\nOption /h specified, using custom hash method: SHA256.\r\r\nThe path (/p) parameter is: \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\"\r\r\nThe content directory (/d) parameter is: \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\"\r\r\nEnumerating files from directory \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\"\r\r\nPacking 3 file(s) in \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\" (content directory) to \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\" (output file name).\r\r\nMemory limit defaulting to 17095639040 bytes.\r\r\nUsing \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\\AppxManifest.xml\" as the manifest for the package.\r\r\nSettings for extension txt: Type = text/plain, Compression = Normal.\r\r\nProcessing \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\\probe.txt\" as a payload file.  Its path in the package will be \"probe.txt\".\r\r\nSettings for extension png: Type = image/png, Compression = None.\r\r\nProcessing \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\\logo.png\" as a payload file.  Its path in the package will be \"logo.png\".\r\r\nPackage creation succeeded.\r\r\n\r\nSTDOUT_END\r\nSTDERR_BEGIN\r\n\r\nSTDERR_END\r\nNATIVE_EXIT=0 LABEL=NT2_PACK UTC=2026-09-07T07:18:42.2924249Z\r\nNATIVE_BEGIN=NT2_UNPACK UTC=2026-09-07T07:18:42.2979499Z\r\nEXE=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\tools\\bin\\10.0.28000.0\\x64\\makeappx.exe ARGUMENTS=\"unpack\" \"/v\" \"/no\" \"/p\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\" \"/d\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\unpacked\" CWD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\r\nSTDOUT_BEGIN\r\nMicrosoft (R) MakeAppx Tool\r\r\nVersion 10.0.28000.2705\r\r\nCopyright (C) Microsoft. All rights reserved.\r\r\n\r\r\nOption /v specified, switching to verbose output.\r\r\nOption /no specified, existing files will be preserved.\r\r\nThe path (/p) parameter is: \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\"\r\r\nThe output directory (/d) parameter is: \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\unpacked\"\r\r\nUnpacking \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\" (package name) to \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\unpacked\" (output directory).\r\r\nExtracting file AppxManifest.xml to \\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\unpacked\\AppxManifest.xml\r\r\nExtracting file AppxBlockMap.xml to \\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\unpacked\\AppxBlockMap.xml\r\r\nExtracting file logo.png to \\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\unpacked\\logo.png\r\r\nExtracting file probe.txt to \\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\unpacked\\probe.txt\r\r\nPackage extraction succeeded.\r\r\n\r\nSTDOUT_END\r\nSTDERR_BEGIN\r\n\r\nSTDERR_END\r\nNATIVE_EXIT=0 LABEL=NT2_UNPACK UTC=2026-09-07T07:18:42.6327218Z\r\nROUNDTRIP=AppxManifest.xml INPUT_SHA256=f1dac3cf6532ba27c73670566c60ff902c070fa8da651635bc683b332cef428a OUTPUT_SHA256=f1dac3cf6532ba27c73670566c60ff902c070fa8da651635bc683b332cef428a\r\nROUNDTRIP=probe.txt INPUT_SHA256=7279571882f7cbe5b070fc4e8e9c06e9b84176439ee9492ae0e7c2e4fea75e0e OUTPUT_SHA256=7279571882f7cbe5b070fc4e8e9c06e9b84176439ee9492ae0e7c2e4fea75e0e\r\nROUNDTRIP=logo.png INPUT_SHA256=ef5fdf2c53dfeb2cb409f84bbefe4d1b7b611b6d8eb142bb9319780aea9b393a OUTPUT_SHA256=ef5fdf2c53dfeb2cb409f84bbefe4d1b7b611b6d8eb142bb9319780aea9b393a\r\nUNPACKED=unpacked\\AppxBlockMap.xml SHA256=c6ca0cfac331412e3e8aadf8e9d62a6d22adb22260fa140484e5d3f7f30c1316\r\nUNPACKED=unpacked\\AppxManifest.xml SHA256=f1dac3cf6532ba27c73670566c60ff902c070fa8da651635bc683b332cef428a\r\nUNPACKED=unpacked\\logo.png SHA256=ef5fdf2c53dfeb2cb409f84bbefe4d1b7b611b6d8eb142bb9319780aea9b393a\r\nUNPACKED=unpacked\\probe.txt SHA256=7279571882f7cbe5b070fc4e8e9c06e9b84176439ee9492ae0e7c2e4fea75e0e\r\nPACKAGE_SHA256=c258fca73d190cb9e102d2fba97f1f1740805345c410cc6479c2a271117c41fe\r\nNT2_PACK_UNPACK=PASS\r\n"
}
```

### NT3–NT5 native negative/positive controls and preservation

```powershell
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$repo='C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest'
$root=Join-Path $repo 'tests\.johnny-runtime\env-msix-04-sdk-native-20260907'
$bin=Join-Path $root 'tools\bin\10.0.28000.0\x64'
function ByteHash([string]$path) {
  $h=[Security.Cryptography.SHA256]::Create(); $s=[IO.File]::OpenRead($path)
  try { return [BitConverter]::ToString($h.ComputeHash($s)).Replace('-','').ToLowerInvariant() }
  finally { $s.Dispose(); $h.Dispose() }
}
function NativeProbe([string]$label,[string]$exe,[string[]]$argv,[int]$expected) {
  $info=[Diagnostics.ProcessStartInfo]::new()
  $info.FileName=$exe
  $info.Arguments=($argv | ForEach-Object { if ($_ -match '["\r\n]') { throw 'UNSAFE_ARG' }; '"'+$_+'"' }) -join ' '
  $info.WorkingDirectory=$root
  $info.UseShellExecute=$false
  $info.CreateNoWindow=$true
  $info.RedirectStandardOutput=$true
  $info.RedirectStandardError=$true
  $info.EnvironmentVariables['PATH']='C:\Windows\System32;C:\Windows'
  $info.EnvironmentVariables['TEMP']=Join-Path $root 'temp'
  $info.EnvironmentVariables['TMP']=Join-Path $root 'temp'
  Write-Output "NATIVE_BEGIN=$label UTC=$([DateTime]::UtcNow.ToString('o'))"
  Write-Output "EXE=$exe ARGUMENTS=$($info.Arguments) CWD=$root"
  $p=[Diagnostics.Process]::new(); $p.StartInfo=$info
  try {
    if (-not $p.Start()) { throw 'PROCESS_NOT_STARTED' }
    $out=$p.StandardOutput.ReadToEndAsync()
    $err=$p.StandardError.ReadToEndAsync()
    if (-not $p.WaitForExit(60000)) { $p.Kill(); throw "OWNED_PROCESS_TIMEOUT=$label" }
    $stdout=$out.GetAwaiter().GetResult(); $stderr=$err.GetAwaiter().GetResult()
    Write-Output 'STDOUT_BEGIN'; Write-Output $stdout; Write-Output 'STDOUT_END'
    Write-Output 'STDERR_BEGIN'; Write-Output $stderr; Write-Output 'STDERR_END'
    Write-Output "NATIVE_EXIT=$($p.ExitCode) LABEL=$label UTC=$([DateTime]::UtcNow.ToString('o'))"
    if ($expected -eq 0 -and $p.ExitCode -ne 0) { throw "EXPECTED_SUCCESS_FAILED=$label" }
    if ($expected -eq 1 -and $p.ExitCode -eq 0) { throw "ZERO_RED_FINDING=$label" }
  } finally { $p.Dispose() }
}

$pkg=Join-Path $root 'positive.msix'
$before=ByteHash $pkg
NativeProbe 'NT3_MISSING_LOGO' (Join-Path $bin 'makeappx.exe') @('pack','/v','/no','/h','SHA256','/d',(Join-Path $root 'missing-logo'),'/p',(Join-Path $root 'missing-logo.msix')) 1
NativeProbe 'NT4_NO_OVERWRITE' (Join-Path $bin 'makeappx.exe') @('pack','/v','/no','/h','SHA256','/d',(Join-Path $root 'positive'),'/p',$pkg) 1
$after=ByteHash $pkg
Write-Output "NT4_PACKAGE_BEFORE=$before AFTER=$after"
if ($before -cne $after) { throw 'PACKAGE_OVERWRITTEN' }
NativeProbe 'NT5_SIGNED_EXE' (Join-Path $bin 'signtool.exe') @('verify','/pa','/v',(Join-Path $bin 'makeappx.exe')) 0
NativeProbe 'NT5_UNSIGNED_PACKAGE' (Join-Path $bin 'signtool.exe') @('verify','/pa','/v',$pkg) 1
foreach ($fixture in @('positive','missing-logo')) {
 foreach ($name in @('AppxManifest.xml','probe.txt','logo.png')) {
   Write-Output "PRESERVED=$fixture/$name SHA256=$(ByteHash (Join-Path (Join-Path $root $fixture) $name))"
 }
}
$archive=Join-Path $repo 'tests\.johnny-runtime\env-msix-03-sdk-replay-20260907-01\sdk.nupkg'
$archiveHash=ByteHash $archive
Write-Output "ORIGINAL_ARCHIVE_SHA256=$archiveHash"
if ($archiveHash -cne '8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed') { throw 'ARCHIVE_CHANGED' }
Write-Output "NEGATIVE_PACKAGE_EXISTS=$(Test-Path -LiteralPath (Join-Path $root 'missing-logo.msix'))"
Write-Output "HEAD=$((& git rev-parse HEAD).Trim())"
& git diff --check
if ($LASTEXITCODE -ne 0) { throw 'DIFF_CHECK_FAILED' }
$status=@(& git status --porcelain)
Write-Output "TRACKED_WORKTREE_STATUS_COUNT=$($status.Count)"
if ($status.Count -ne 0) { throw 'TRACKED_MUTATION' }
Write-Output 'NT3_NT4_NT5_NATIVE_CONTROLS=OBSERVED'

```

```json
{
  "chunk_id": "51d38b",
  "wall_time_seconds": 2.4502163,
  "exit_code": 0,
  "original_token_count": 2688,
  "output": "NATIVE_BEGIN=NT3_MISSING_LOGO UTC=2026-09-07T07:19:07.8322530Z\r\nEXE=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\tools\\bin\\10.0.28000.0\\x64\\makeappx.exe ARGUMENTS=\"pack\" \"/v\" \"/no\" \"/h\" \"SHA256\" \"/d\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\missing-logo\" \"/p\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\missing-logo.msix\" CWD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\r\nSTDOUT_BEGIN\r\nMicrosoft (R) MakeAppx Tool\r\r\nVersion 10.0.28000.2705\r\r\nCopyright (C) Microsoft. All rights reserved.\r\r\n\r\r\nOption /v specified, switching to verbose output.\r\r\nOption /no specified, existing files will be preserved.\r\r\nOption /h specified, using custom hash method: SHA256.\r\r\nThe path (/p) parameter is: \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\missing-logo.msix\"\r\r\nThe content directory (/d) parameter is: \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\missing-logo\"\r\r\nEnumerating files from directory \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\missing-logo\"\r\r\nPacking 3 file(s) in \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\missing-logo\" (content directory) to \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\missing-logo.msix\" (output file name).\r\r\nMemory limit defaulting to 17095639040 bytes.\r\r\nUsing \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\missing-logo\\AppxManifest.xml\" as the manifest for the package.\r\r\nMakeAppx : error: Manifest validation error: Line 7, Column 6, Reason: The file name \"missing.png\" declared for element \"*[local-name()='Properties']/*[local-name()='Logo']\" doesn't exist in the package.\r\r\nMakeAppx : error: Failure at (ValidateFilesInManifest( manifestReaderInternal.Get(), rootNode.Get(), payloadFiles, Manifest::FileNameXPaths, (sizeof(*RtlpNumberOf(Manifest::FileNameXPaths))), !localized && !isNonQualifiedResourcePackage)) - 0x80080204 - The specified package format is not valid: The package manifest is not valid.\r\r\nMakeAppx : error: Failure at (PackageValidator::Validate(manifestReader.Get(), localized, *(fileList->GetMap()))) - 0x80080204 - The specified package format is not valid: The package manifest is not valid.\r\r\nCleaning up output file \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\missing-logo.msix\".\r\r\nMakeAppx : error: Failure at (CreatePackage( overwrite, hashAlgorithm, fileList, outputPath, manifestStream.Get(), forceCompressionNone, performanceOptions, encryptPackage, encryptionOptions, cgmPath, mainPackagePathForResourceExemption, makepriExeFullPath, publisherBridgingList)) - 0x80080204 - The specified package format is not valid: The package manifest is not valid.\r\r\nMakeAppx : error: Package creation failed.\r\r\nMakeAppx : error: 0x80080204 - The specified package format is not valid: The package manifest is not valid.\r\r\n\r\nSTDOUT_END\r\nSTDERR_BEGIN\r\n\r\nSTDERR_END\r\nNATIVE_EXIT=1 LABEL=NT3_MISSING_LOGO UTC=2026-09-07T07:19:08.0738004Z\r\nNATIVE_BEGIN=NT4_NO_OVERWRITE UTC=2026-09-07T07:19:08.0805118Z\r\nEXE=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\tools\\bin\\10.0.28000.0\\x64\\makeappx.exe ARGUMENTS=\"pack\" \"/v\" \"/no\" \"/h\" \"SHA256\" \"/d\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\" \"/p\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\" CWD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\r\nSTDOUT_BEGIN\r\nMicrosoft (R) MakeAppx Tool\r\r\nVersion 10.0.28000.2705\r\r\nCopyright (C) Microsoft. All rights reserved.\r\r\n\r\r\nOption /v specified, switching to verbose output.\r\r\nOption /no specified, existing files will be preserved.\r\r\nOption /h specified, using custom hash method: SHA256.\r\r\nThe path (/p) parameter is: \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\"\r\r\nThe content directory (/d) parameter is: \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\"\r\r\nEnumerating files from directory \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\"\r\r\nPacking 3 file(s) in \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\" (content directory) to \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\" (output file name).\r\r\nMemory limit defaulting to 17095639040 bytes.\r\r\nUsing \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive\\AppxManifest.xml\" as the manifest for the package.\r\r\nMakeAppx : error: Can't overwrite existing file \"\\\\?\\C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\".\r\r\nMakeAppx : error: Failure at (CanOverwrite(outputPath, overwrite, &canOverwrite)) - 0x80070050 - ?????\r\r\nMakeAppx : error: Failure at (ResolveOutputPath(overwrite, outputPath, &tempOutputPath)) - 0x80070050 - ?????\r\r\nMakeAppx : error: Failure at (CreatePackage( overwrite, hashAlgorithm, fileList, outputPath, manifestStream.Get(), forceCompressionNone, performanceOptions, encryptPackage, encryptionOptions, cgmPath, mainPackagePathForResourceExemption, makepriExeFullPath, publisherBridgingList)) - 0x80070050 - ?????\r\r\nMakeAppx : error: Package creation failed.\r\r\nMakeAppx : error: 0x80070050 - ?????\r\r\n\r\nSTDOUT_END\r\nSTDERR_BEGIN\r\n\r\nSTDERR_END\r\nNATIVE_EXIT=1 LABEL=NT4_NO_OVERWRITE UTC=2026-09-07T07:19:08.1364094Z\r\nNT4_PACKAGE_BEFORE=c258fca73d190cb9e102d2fba97f1f1740805345c410cc6479c2a271117c41fe AFTER=c258fca73d190cb9e102d2fba97f1f1740805345c410cc6479c2a271117c41fe\r\nNATIVE_BEGIN=NT5_SIGNED_EXE UTC=2026-09-07T07:19:08.1422197Z\r\nEXE=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\tools\\bin\\10.0.28000.0\\x64\\signtool.exe ARGUMENTS=\"verify\" \"/pa\" \"/v\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\tools\\bin\\10.0.28000.0\\x64\\makeappx.exe\" CWD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\r\nSTDOUT_BEGIN\r\n\r\r\nVerifying: C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\tools\\bin\\10.0.28000.0\\x64\\makeappx.exe\r\r\n\r\nSignature Index: 0 (Primary Signature)\r\nHash of file (sha256): C310D55285CA4E81C156767C037B9AE0EE91F542EA7A58439276FBEFD44D42A4\r\n\r\nSigning Certificate Chain:\r\n    Issued to: Microsoft Root Certificate Authority 2010\r\r\n    Issued by: Microsoft Root Certificate Authority 2010\r\r\n    Expires:   Sun Jun 24 06:04:01 2035\r\r\n    SHA1 hash: 3B1EFD3A66EA28B16697394703A72CA340A05BD5\r\r\n\r\n        Issued to: Microsoft Windows Code Signing PCA 2024\r\r\n        Issued by: Microsoft Root Certificate Authority 2010\r\r\n        Expires:   Sun Jun 24 06:04:01 2035\r\r\n        SHA1 hash: D30F05F637E605239C0070D1EA9860D434AC2A94\r\r\n\r\n            Issued to: Microsoft Corporation\r\r\n            Issued by: Microsoft Windows Code Signing PCA 2024\r\r\n            Expires:   Thu Mar 04 03:58:24 2027\r\r\n            SHA1 hash: 0A24A6CC7DDDD7F637BCF9578B6CE274A7AF132A\r\r\n\r\nThe signature is timestamped: Wed Aug 12 10:20:23 2026\r\r\nTimestamp Verified by:\r\n    Issued to: Microsoft Root Certificate Authority 2010\r\r\n    Issued by: Microsoft Root Certificate Authority 2010\r\r\n    Expires:   Sun Jun 24 06:04:01 2035\r\r\n    SHA1 hash: 3B1EFD3A66EA28B16697394703A72CA340A05BD5\r\r\n\r\n        Issued to: Microsoft Time-Stamp PCA 2010\r\r\n        Issued by: Microsoft Root Certificate Authority 2010\r\r\n        Expires:   Tue Oct 01 02:32:25 2030\r\r\n        SHA1 hash: 36056A5662DCADECF82CC14C8B80EC5E0BCC59A6\r\r\n\r\n            Issued to: Microsoft Time-Stamp Service\r\r\n            Issued by: Microsoft Time-Stamp PCA 2010\r\r\n            Expires:   Sat Nov 14 02:48:31 2026\r\r\n            SHA1 hash: 5A64E2034D6EE66C6AFE757189124B30EB245467\r\r\n\r\n\r\nSuccessfully verified: C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\tools\\bin\\10.0.28000.0\\x64\\makeappx.exe\r\r\n\r\nNumber of files successfully Verified: 1\r\r\nNumber of warnings: 0\r\r\nNumber of errors: 0\r\r\n\r\nSTDOUT_END\r\nSTDERR_BEGIN\r\n\r\nSTDERR_END\r\nNATIVE_EXIT=0 LABEL=NT5_SIGNED_EXE UTC=2026-09-07T07:19:08.4002530Z\r\nNATIVE_BEGIN=NT5_UNSIGNED_PACKAGE UTC=2026-09-07T07:19:08.4041228Z\r\nEXE=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\tools\\bin\\10.0.28000.0\\x64\\signtool.exe ARGUMENTS=\"verify\" \"/pa\" \"/v\" \"C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\" CWD=C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\r\nSTDOUT_BEGIN\r\n\r\r\nVerifying: C:\\Users\\GameBoy\\Desktop\\Johnny_AI_Skill_latest\\tests\\.johnny-runtime\\env-msix-04-sdk-native-20260907\\positive.msix\r\r\n\r\nNumber of files successfully Verified: 0\r\r\nNumber of warnings: 0\r\r\nNumber of errors: 1\r\r\n\r\nSTDOUT_END\r\nSTDERR_BEGIN\r\nSignTool Error: No signature found.\r\n\r\nSTDERR_END\r\nNATIVE_EXIT=1 LABEL=NT5_UNSIGNED_PACKAGE UTC=2026-09-07T07:19:08.5788889Z\r\nPRESERVED=positive/AppxManifest.xml SHA256=f1dac3cf6532ba27c73670566c60ff902c070fa8da651635bc683b332cef428a\r\nPRESERVED=positive/probe.txt SHA256=7279571882f7cbe5b070fc4e8e9c06e9b84176439ee9492ae0e7c2e4fea75e0e\r\nPRESERVED=positive/logo.png SHA256=ef5fdf2c53dfeb2cb409f84bbefe4d1b7b611b6d8eb142bb9319780aea9b393a\r\nPRESERVED=missing-logo/AppxManifest.xml SHA256=dac51f6d893d317d965a7a30acdc932c8a7ece3e37cce4c2d8e7869f02e69c16\r\nPRESERVED=missing-logo/probe.txt SHA256=7279571882f7cbe5b070fc4e8e9c06e9b84176439ee9492ae0e7c2e4fea75e0e\r\nPRESERVED=missing-logo/logo.png SHA256=ef5fdf2c53dfeb2cb409f84bbefe4d1b7b611b6d8eb142bb9319780aea9b393a\r\nORIGINAL_ARCHIVE_SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed\r\nNEGATIVE_PACKAGE_EXISTS=False\r\nHEAD=c6b9ad1a10acae3d542584a49e7b2e3061c6b810\r\nTRACKED_WORKTREE_STATUS_COUNT=0\r\nNT3_NT4_NT5_NATIVE_CONTROLS=OBSERVED\r\n"
}
```
