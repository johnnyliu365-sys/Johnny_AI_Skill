# ENV-MSIX-01 — Disposable Windows MSIX test environment

| Field | Value |
| --- | --- |
| Kind / revision / state | `OPERATIONAL_ENVIRONMENT_ACTION` / `02` / `OWNER_AUTHORIZED / CORRECTION_REVIEW_REQUIRED` |
| Authority | Owner's 2026-09-05 authorization to create a disposable Windows test VM; test-certificate trust only inside that VM, never on the working host. |
| Requirement / findings | CHG-20260905-050 revision 02; [CAP-MSIX-01 review](../../../doc/reviews/local-orchestration-installer/cap-msix-01-capability-review.md) at `5d7906e5f8cb5dd64ccf94a2d0c05fa11477133e` |
| Scope / owner | Environment provisioning only, current-session operator/reviewer. No product implementation, host plugin registration, push or release. |
| Profile | POC / HIGH_ASSURANCE: privileged Hyper-V and downloaded OS supply chain; one mandatory read-only adversarial helper, no implementation lane. |
| Environment / correlation | `ENV-MSIX-01-20260905` / `VM-PROVISION-20260905-01` |
| VM / resources | `Johnny-MSIX-Lab-20260905`; Generation 2; 4 vCPU; 4 GiB fixed startup RAM; 80 GiB dynamic VHDX; Secure Boot and vTPM. |
| Host data root | `C:\ProgramData\JohnnyMsixLab-ENV-MSIX-01-20260905`; new, administrator/SYSTEM-only directory. Existing path or VM name blocks; no reuse or deletion. |
| Download cache | `C:\Users\GameBoy\AppData\Local\JohnnyMsixLab`; downloaded media and PDF only, no scripts/secrets. |
| Expected return | `ENVIRONMENT_BOOTSTRAP_RETURN`: `VM_BOOTED_SETUP_PENDING`, `BLOCKED` or `RECOVERY_REQUIRED`; not Windows/MSIX qualification. |

## Bound media and user boundary

Use the public [Microsoft evaluation download page][download], Traditional Chinese
Enterprise x64 (not LTSC), 90-day evaluation. Do not purchase a license, invent
registration data, bypass Windows account/setup requirements or activate using a
workstation/company account. Any required login is performed by the owner in Windows.

The page's official link resolved to:

`https://software-static.download.prss.microsoft.com/dbazure/888969d5-f34g-4e03-ac9d-1f9786c66749/26200.6584.250915-1905.25h2_ge_release_svc_refresh_CLIENTENTERPRISEEVAL_OEMRET_x64FRE_zh-tw.iso`

Expected length: `7335473152` bytes. Expected SHA-256:
`89626da8fdfdd8d03c31bc911bc525145c9e07e3a5f1c299e0645f0ab7e38096`.
The reviewer extracted and visually checked page 3, `Enterprise Eval x64 Eval ZH-TW
DVD9`, of the [official hash PDF][hashes]. Verify after download and again on the
protected copy before attachment. A mismatch blocks; never replace the expected hash
with a digest derived solely from the download.

## Finite closure CLOSURE-ENV-MSIX-01 revision 01

1. Observe host capacity, running Hyper-V and successful administrator `Get-VMHost`.
   The actual host has about 32 GiB RAM and 195 GiB free C: space; normal-token access
   was denied and the owner-scoped UAC read-only probe exited 0. Do not change group
   membership, enable features, restart the host or change its certificate trust.
2. Bound the exact VM name, fresh protected data root and verified media. All writes
   stay in that root/cache; no existing VM, physical disk or target repository effect.
3. Create one VM with no virtual switch. Disable its integration services for this
   initial offline setup. No enhanced-session clipboard/drive sharing, shared folders,
   passthrough disk, NAT/switch creation or external host registration is admitted.
4. Independently read back resources, VM ID, disk/DVD paths, Secure Boot, vTPM,
   disconnected adapters and disabled integrations before boot; then read Running.
   A Running VM is **setup pending**, not installed/activated Windows or MSIX proof.
5. A failed partial operation preserves its exact created artifacts and VM ID with
   `RECOVERY_REQUIRED`. No automatic recursive cleanup, fallback, overwrite or retry.
   Retry requires the operator to inspect exact owned state, not run create again.
   When root ownership cannot be proved, do not write a result into that root: the
   elevated process returns code `43`, an independent parent-observed recovery
   carrier binding this exact action/root and the pre-VM root-admission failure.
   The parent persists that result and performs read-only inspection before retry.
6. Open the basic VM console only for the owner's installation/account interaction.
   No password, key, plaintext secret or host account is captured in artifacts.
   Test signing/guest trust waits for a qualified guest; this action creates neither.

## AdversarialReviewPlan

`candidate_commit`: the exact commit containing this revision and its digest index.
`closure_revision`: `CLOSURE-ENV-MSIX-01/01`; `profile_requirement`: `REQUIRED`.
Helper: reuse `/root/wa01_adversarial_review` (Terra/xhigh), read-only/no-code;
ContextView `ENVMSIX01-AUDIT-20260905`. Prior UIX/CAP views remain closed.
`isolation_disposition`: `READ_ONLY_INTENT_ONLY` (tool surface is not a sandbox);
`effect_scope`: `NO_EXTERNAL_EFFECT`. No helper file writes, native effects or fan-out.
Attack `BOUNDARY_DATA`, `AUTHORIZATION`, `ERROR_PARTIAL_FAILURE`, `STATE_TRANSITION`,
`IDEMPOTENCY`, `CONSISTENCY`, `OBSERVABILITY`, `DEPLOYMENT_READINESS` against the exact
native command recipe below. Return finite findings only. Operator alone executes
after review; same-lifetime wait requires no runner/receipt/descriptor. The environment
ID/result evidence is an effect binding, not a fabricated runtime dispatch receipt.

## Exact elevated native-command recipe

This is an owner-authorized operational command record, not a new installer script,
production API or permission to create a privileged helper/service. The operator
submits these exact committed bytes to Windows PowerShell through normal UAC. Native
Hyper-V cmdlets perform creation. A read-only result file is the observation carrier,
not authority. No script is loaded from a writable external location by elevation.

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Import-Module Hyper-V
[string]$phase = 'PREFLIGHT'
[string]$root = 'C:\ProgramData\JohnnyMsixLab-ENV-MSIX-01-20260905'
[string]$name = 'Johnny-MSIX-Lab-20260905'
[string]$sourceIso = 'C:\Users\GameBoy\AppData\Local\JohnnyMsixLab\Windows11-Enterprise-25H2-zh-tw.iso'
[string]$expectedHash = '89626da8fdfdd8d03c31bc911bc525145c9e07e3a5f1c299e0645f0ab7e38096'
$vm = $null
[bool]$ownsRoot = $false
[bool]$resultWritten = $false
$result = [ordered]@{Environment='ENV-MSIX-01-20260905';Status='BLOCKED';Phase=$phase;VMId=$null;Failure=$null}
try {
    Get-VMHost -ErrorAction Stop | Out-Null
    if ([IO.DriveInfo]::new('C').AvailableFreeSpace -lt 100GB) { throw 'INSUFFICIENT_FREE_DISK' }
    if ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory * 1KB -lt 6GB) { throw 'INSUFFICIENT_FREE_MEMORY' }
    if (Get-VM -Name $name -ErrorAction SilentlyContinue) { throw 'VM_NAME_EXISTS' }
    if (Test-Path -LiteralPath $root) { throw 'ROOT_EXISTS' }
    $parent = Get-Item -LiteralPath 'C:\ProgramData' -Force
    if (($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'REPARSE_PARENT' }
    $acl = [Security.AccessControl.DirectorySecurity]::new()
    $acl.SetAccessRuleProtection($true,$false)
    foreach ($sid in @('S-1-5-18','S-1-5-32-544')) {
        $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new($sid),'FullControl','ContainerInherit,ObjectInherit','None','Allow'))
    }
    $acl.SetOwner([Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'))
    $phase = 'ROOT_CREATION_REQUESTED'
    [IO.Directory]::CreateDirectory($root,$acl) | Out-Null
    $phase = 'ROOT_CREATED'
    $actualAcl = Get-Acl -LiteralPath $root
    if (-not $actualAcl.AreAccessRulesProtected -or $actualAcl.GetOwner([Security.Principal.SecurityIdentifier]).Value -ne 'S-1-5-32-544') { throw 'ROOT_ACL_MISMATCH' }
    $rules = @($actualAcl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]))
    if ($rules.Count -ne 2 -or @($rules | Where-Object {$_.IdentityReference.Value -notin @('S-1-5-18','S-1-5-32-544') -or $_.AccessControlType.ToString() -ne 'Allow' -or $_.FileSystemRights.ToString() -ne 'FullControl'}).Count -ne 0) { throw 'ROOT_RULES_MISMATCH' }
    $ownsRoot = $true
    [string]$iso = Join-Path $root 'Windows11-Enterprise-25H2-zh-tw.iso'
    $inputStream = [IO.File]::Open($sourceIso,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
    try {
        if ($inputStream.Length -ne 7335473152) { throw 'ISO_LENGTH_MISMATCH' }
        $outputStream = [IO.File]::Open($iso,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
        try { $inputStream.CopyTo($outputStream); $outputStream.Flush($true) } finally { $outputStream.Dispose() }
    } finally { $inputStream.Dispose() }
    if ((Get-FileHash -LiteralPath $iso -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) { throw 'ISO_HASH_MISMATCH' }
    $phase = 'MEDIA_VERIFIED'
    [string]$disk = Join-Path $root 'disk.vhdx'
    $vm = New-VM -Name $name -Generation 2 -MemoryStartupBytes 4GB -Path $root -NewVHDPath $disk -NewVHDSizeBytes 80GB -ErrorAction Stop
    $phase = 'VM_CREATED'
    Set-VM -VM $vm -ProcessorCount 4 -AutomaticStartAction Nothing -AutomaticStopAction Save -AutomaticCheckpointsEnabled $false
    Set-VMMemory -VM $vm -DynamicMemoryEnabled $false
    Set-VMFirmware -VM $vm -EnableSecureBoot On -SecureBootTemplate MicrosoftWindows
    Set-VMKeyProtector -VM $vm -NewLocalKeyProtector
    Enable-VMTPM -VM $vm
    Get-VMNetworkAdapter -VM $vm | Disconnect-VMNetworkAdapter
    Get-VMIntegrationService -VM $vm | Disable-VMIntegrationService
    $dvd = Add-VMDvdDrive -VM $vm -Path $iso -Passthru
    Set-VMFirmware -VM $vm -FirstBootDevice $dvd
    $fresh = Get-VM -Id $vm.Id
    $memory = Get-VMMemory -VM $fresh
    $security = Get-VMSecurity -VM $fresh
    $firmware = Get-VMFirmware -VM $fresh
    $disks = @(Get-VMHardDiskDrive -VM $fresh)
    $media = @(Get-VMDvdDrive -VM $fresh)
    if ($fresh.Generation -ne 2 -or $fresh.ProcessorCount -ne 4 -or $fresh.MemoryStartup -ne 4GB -or $memory.DynamicMemoryEnabled) { throw 'RESOURCE_READBACK_MISMATCH' }
    if ($security.TpmEnabled -ne $true -or $firmware.SecureBoot.ToString() -ne 'On') { throw 'SECURITY_READBACK_MISMATCH' }
    if ($disks.Count -ne 1 -or $disks[0].Path -ne $disk -or (Get-VHD -Path $disk).Size -ne 80GB) { throw 'DISK_READBACK_MISMATCH' }
    if ($media.Count -ne 1 -or $media[0].Path -ne $iso) { throw 'MEDIA_READBACK_MISMATCH' }
    if (@(Get-VMNetworkAdapter -VM $fresh | Where-Object {$_.SwitchName}).Count -ne 0) { throw 'NETWORK_CONNECTED' }
    if (@(Get-VMIntegrationService -VM $fresh | Where-Object {$_.Enabled}).Count -ne 0) { throw 'INTEGRATION_ENABLED' }
    $phase = 'CONFIGURATION_VERIFIED'
    Start-VM -VM $fresh
    $fresh = Get-VM -Id $vm.Id
    if ($fresh.State.ToString() -ne 'Running') { throw 'NOT_RUNNING' }
    $result.Status = 'VM_BOOTED_SETUP_PENDING'
    $result.VMId = $fresh.Id.ToString()
    $result['Name'] = $name
    $result['Generation'] = 2
    $result['MemoryBytes'] = $fresh.MemoryStartup
    $result['Processors'] = $fresh.ProcessorCount
    $result['VhdCapacityBytes'] = (Get-VHD -Path $disk).Size
    $result['NetworkConnected'] = $false
    $result['IntegrationServicesEnabled'] = 0
    $result['SecureBoot'] = $firmware.SecureBoot.ToString()
    $result['TpmEnabled'] = $security.TpmEnabled
    $result['IsoSha256'] = $expectedHash
    $phase = 'BOOT_READBACK_COMPLETE'
} catch {
    if ($phase -ne 'PREFLIGHT') { $result.Status = 'RECOVERY_REQUIRED' }
    if ($null -ne $vm) { $result.VMId = $vm.Id.ToString() }
    if ($_.Exception.Message -cmatch '^[A-Z_]{1,64}$') { $result.Failure = $_.Exception.Message } else { $result.Failure = 'NATIVE_OPERATION_FAILED' }
} finally {
    $result.Phase = $phase
    if ($ownsRoot) {
        try {
            [string]$report = Join-Path $root 'provision-result.json'
            $reportStream = [IO.File]::Open($report,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
            try {
                [byte[]]$reportBytes = [Text.Encoding]::UTF8.GetBytes(($result | ConvertTo-Json))
                $reportStream.Write($reportBytes,0,$reportBytes.Length)
                $reportStream.Flush($true)
            } finally { $reportStream.Dispose() }
            $reportAcl = Get-Acl -LiteralPath $report
            $reportAcl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new('S-1-5-32-545'),'Read','Allow'))
            Set-Acl -LiteralPath $report -AclObject $reportAcl
            $resultWritten = $true
        } catch { $resultWritten = $false }
    }
}
if (-not $ownsRoot -and $phase -ne 'PREFLIGHT') { exit 43 }
if ($ownsRoot -and -not $resultWritten) { exit 44 }
if ($result.Status -eq 'VM_BOOTED_SETUP_PENDING' -and $resultWritten) { exit 0 } else { exit 42 }
```

`RECOVERY_REQUIRED` is not authorization to reset/remove another VM or recursively
delete the host directory. Future cleanup requires the exact VM ID and this action's
owned-root readback. A normal user may read the sanitized result file through its
explicit read ACL; VM disks/private guest state remain administrator/SYSTEM-only.

The operator independently captures the elevated process exit code. `43` means
`RECOVERY_REQUIRED / ROOT_ADMISSION_UNCONFIRMED` before any VM command; `44` means
`RECOVERY_REQUIRED / RESULT_CARRIER_FAILED` and requires exact root/VM inspection.
`42` means preflight rejection or a non-success result file; absence of that file
never becomes success. Only `0` plus the expected result-file readback permits the
setup-pending claim. No recovery branch writes to a root whose ownership is unproved.

Revision 02 is the single bounded correction to revision 01 / candidate `15ca43c`:
it closes the helper's root-ACL failure observation gap without authorizing any
additional VM, certificate, deletion, feature change or automatic cleanup.

[download]: https://www.microsoft.com/en-us/evalcenter/download-windows-11-enterprise
[hashes]: https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/bade/documents/products-and-services/en-us/owned-and-operated/Verify-Download-Win11-Enterprise.pdf
