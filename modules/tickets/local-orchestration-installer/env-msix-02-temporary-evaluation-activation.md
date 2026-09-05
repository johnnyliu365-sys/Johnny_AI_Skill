# ENV-MSIX-02 — Temporary evaluation activation network

| Field | Value |
| --- | --- |
| Kind / revision / state | `OPERATIONAL_ENVIRONMENT_ACTION` / `02` / `AUTHORIZED / CORRECTION_REVIEW_PENDING` |
| Owner / baseline | Current-session operator/reviewer; `b140e5bf3d47d0e1a3736dd87340c1e693ff70de`, clean local main; no push. |
| Authority | Owner's 2026-09-06 explicit authorization to temporarily connect this VM, attempt official evaluation activation, read status/expiry, then disconnect. |
| Environment / correlation | `ENV-MSIX-01-20260905` / `EVAL-ACTIVATE-20260906-01` |
| Profile / allocation | POC / HIGH_ASSURANCE: privileged network effect; zero implementers, one existing read-only adversarial helper. |
| Exact VM | `7701b26b-5b5a-42c0-b1e1-36d34dfdaa46` / `Johnny-MSIX-Lab-20260905` |
| Exact adapter | `Microsoft:7701B26B-5B5A-42C0-B1E1-36D34DFDAA46\6BF8439D-9DE5-48C6-83E2-A368C38F8648` |
| Observed existing switch | `c08cb7b8-9b3c-408e-8e30-5e16a3aeb444` / `Default Switch`; never select WSL or an external switch. |
| Prior provisioning | [ENV-MSIX-01](env-msix-01-disposable-hyper-v.md), revision 06; creation and its correction budget remain closed. This is a distinct owner-authorized operational action, not another provisioning correction. |

## Observations and scope

The owner supplied guest screenshots of Windows 11 EnterpriseEval 25H2 build
26200.6584 and `slmgr.vbs /xpr` reporting notification mode. These are owner-provided
diagnostics, not implementation/release evidence, proof of activation or of the
evaluation period being exhausted. Guest activation and MSIX lifecycle are unproved.

Native preflight `ACTIVATION-NETWORK-PREFLIGHT-20260906-02` exited 0 and observed the
exact VM Running, one disconnected adapter, Default Switch and WSL, and zero enabled
integration services. Its sanitized native result is
`C:\ProgramData\JohnnyActivationPreflight-20260906-8056c424.json`.
An earlier read-only probe exited 46 at its strict VM-root ACL check, before any VM
command or output write. The subsequent read-only probe recorded extra VM-root ACEs;
their provenance is not proved. This action neither relaxes that ACL nor writes in
the VM root. Its result files are separate fresh protected ProgramData files.

Only the exact existing adapter may be connected/disconnected. No switch/NAT creation,
host firewall or ACL change, shared drives, guest/host integration, host activation,
company account, key purchase, credential capture, `rearm`, license bypass, VM recreation,
package installation, certificate trust, source implementation, push or release.
Connecting an ordinary switch is not an activation-endpoint allowlist: guest background
network traffic is possible during this brief owner-controlled window. Do not claim
that only Microsoft activation traffic was technically permitted.

## Closure CLOSURE-ENV-MSIX-02/01

1. Resolve the exact VM/adapter and existing switch by IDs with fresh name/type checks.
   CONNECT requires Running, initially disconnected, and zero enabled integrations.
   Missing/mismatched state refuses before network effect; no fallback selection.
2. Reuse only the trusted-module bootstrap at commit
   `f3e77eed6da2fa85b2e115508776f1b3dc311c74`, ENV-MSIX-01 PowerShell block through
   `# ENV_F2_BOOTSTRAP_END`. Never execute its provisioning body. Append the one block
   below and exactly one terminal call `Invoke-LabNetworkAction CONNECT` or
   `Invoke-LabNetworkAction -Action DISCONNECT -DisconnectAttempt <fresh-guid>`.
   The operator binds the fresh nonempty report GUID before each DISCONNECT and
   reads only its exact derived result path. This GUID identifies an observation,
   not a new grant or permission to reconnect.
3. Use the absolute System32 Windows PowerShell 5.1 executable, normal UAC,
   `-NoLogo -NoProfile -NonInteractive -EncodedCommand`, System32 working directory,
   hidden window. No privileged process loads a writable external script.
4. Result files use CreateNew and an atomic protected file ACL after parent checks.
   No VM-root ACL is changed. Exit 0 and fresh exact result readback are both required.
   A failed CONNECT after requesting effect attempts one exact-adapter disconnect.
   Unproved restoration/reporting is RECOVERY_REQUIRED, never a success or retry.
5. Owner runs the guest activation in its basic console: an elevated guest command
   prompt may run `cscript.exe //nologo C:\Windows\System32\slmgr.vbs /ato`, followed
   by `slmgr.vbs /xpr`. Do not run these commands on the host. An error is returned as
   a sanitized code; do not ask for keys, passwords or full licensing dumps.
6. Parent does not have guest credentials or an admitted guest command channel.
   After CONNECT, hand the one guest command step to the owner. No poller, background
   watchdog, scheduled task, gateway or promised asynchronous disconnect is created.
   Owner returns success/failure immediately; either result routes to DISCONNECT.
   If abandoning the attempt, disconnect first. The owner can also set this VM's
   network adapter to Not connected in Hyper-V Manager. Do not leave it online as a
   completed action or infer activation from network connectivity.
7. DISCONNECT is exact-adapter and idempotent, including an already disconnected or
   stopped VM; it does not depend on switch existence or guest authentication.
   Each invocation has a fresh report GUID, so earlier records remain immutable
   without blocking a new observation. Reusing a report GUID refuses before effect.
   Read back Connected=false and absent SwitchId. Failure/unknown state is
   RECOVERY_REQUIRED. Package readiness remains unproved after successful activation.

## AdversarialReviewPlan

Exact candidate: commit containing this revision and matching direct index digest.
Closure `CLOSURE-ENV-MSIX-02/01`; requirement `REQUIRED`; helper
`/root/wa01_adversarial_review`, existing Terra/xhigh, fresh view
`ENVMSIX02-AUDIT-20260906-02`; all previous helper views closed.
`READ_ONLY_INTENT_ONLY`, `NO_EXTERNAL_EFFECT`; no writes, native host commands,
secret/config access or fan-out. Attack AUTHORIZATION, STATE_TRANSITION,
ERROR_PARTIAL_FAILURE, CONSISTENCY, IDEMPOTENCY and OBSERVABILITY. Return finite
findings only; parent alone reviews and operates. Same-lifetime wait, no receipt.
Reviewer parse-checks exact composed bytes and tests rejection/cleanup paths with
in-memory fake cmdlets (never elevated); no VM mutation is used as a negative test.

## Exact native action block

The bootstrap named in closure 2 precedes this block. Only the terminal action and
the DISCONNECT observation GUID vary. Revision 02 is the one bounded correction of
revision 01 / `15eedd726e3fa1d23f80170b6381498ecf4fa2c0`: fresh disconnect carriers
repair its replay/recovery defect without broadening any network authority.
The threat anchor is the protected OS and administrator; concurrent malicious
administrator/system changes are outside this one-shot operational threat model.

```powershell
function Invoke-LabNetworkAction {
    param([Parameter(Mandatory=$true)][ValidateSet('CONNECT','DISCONNECT')][string]$Action,
          [guid]$DisconnectAttempt = [guid]::Empty)
    $ErrorActionPreference = 'Stop'
    [string]$vmId = '7701b26b-5b5a-42c0-b1e1-36d34dfdaa46'
    [string]$adapterId = 'Microsoft:7701B26B-5B5A-42C0-B1E1-36D34DFDAA46\6BF8439D-9DE5-48C6-83E2-A368C38F8648'
    [guid]$switchId = 'c08cb7b8-9b3c-408e-8e30-5e16a3aeb444'
    [string]$reportPath = 'C:\ProgramData\JohnnyActivationNetwork-20260906-' + $Action.ToLowerInvariant() + '-01.json'
    if ($Action -ceq 'DISCONNECT') {
        if ($DisconnectAttempt -eq [guid]::Empty) { throw 'DISCONNECT_ATTEMPT_REQUIRED' }
        $reportPath = 'C:\ProgramData\JohnnyActivationNetwork-20260906-disconnect-' + $DisconnectAttempt.ToString('D') + '.json'
    }
    $stream = $null
    [bool]$effectRequested = $false
    [int]$code = 42
    $result = [ordered]@{Action=$Action;Correlation='EVAL-ACTIVATE-20260906-01';DisconnectAttempt=$DisconnectAttempt.ToString('D');VMId=$vmId;Status='BLOCKED';Connected=$null;Failure=$null;TimestampUtc=[DateTime]::UtcNow.ToString('o')}
    function Get-BoundAdapter {
        $boundVm = Get-VM -Id $vmId
        if ($boundVm.Name -cne 'Johnny-MSIX-Lab-20260905') { throw 'VM_IDENTITY_MISMATCH' }
        $items = @(Get-VMNetworkAdapter -VM $boundVm)
        if ($items.Count -ne 1 -or $items[0].Id -cne $adapterId) { throw 'ADAPTER_IDENTITY_MISMATCH' }
        return $items[0]
    }
    try {
        [string[]]$trusted = @('S-1-5-18','S-1-5-32-544','S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464')
        foreach ($parent in @('C:\','C:\ProgramData')) {
            if (([IO.File]::GetAttributes($parent) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'RESULT_PARENT_REPARSE' }
            $parentAcl = Get-Acl -LiteralPath $parent
            if ($parentAcl.GetOwner([Security.Principal.SecurityIdentifier]).Value -notin $trusted) { throw 'RESULT_PARENT_OWNER' }
            foreach ($rule in $parentAcl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])) {
                if (($rule.PropagationFlags -band [Security.AccessControl.PropagationFlags]::InheritOnly) -ne 0) { continue }
                if ($rule.AccessControlType.ToString() -eq 'Allow' -and ([long]$rule.FileSystemRights -band 0x500D0040) -ne 0 -and $rule.IdentityReference.Value -notin $trusted) { throw 'RESULT_PARENT_WRITER' }
            }
        }
        $fileSecurity = [Security.AccessControl.FileSecurity]::new()
        $fileSecurity.SetAccessRuleProtection($true,$false)
        $fileSecurity.SetOwner([Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'))
        foreach ($sid in @('S-1-5-18','S-1-5-32-544')) { $fileSecurity.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new($sid),'FullControl','Allow')) }
        $fileSecurity.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new('S-1-5-32-545'),'Read','Allow'))
        $stream = [IO.FileStream]::new($reportPath,[IO.FileMode]::CreateNew,[Security.AccessControl.FileSystemRights]::Write,[IO.FileShare]::None,4096,[IO.FileOptions]::WriteThrough,$fileSecurity)
        $adapter = Get-BoundAdapter
        if ($Action -ceq 'CONNECT') {
            $vm = Get-VM -Id $vmId
            if ($vm.State.ToString() -ne 'Running' -or $adapter.Connected -or $adapter.SwitchId) { throw 'INITIAL_STATE_MISMATCH' }
            if (@(Get-VMIntegrationService -VM $vm | Where-Object {$_.Enabled}).Count -ne 0) { throw 'INTEGRATION_STATE_MISMATCH' }
            $switch = Get-VMSwitch -Id $switchId
            if ($switch.Name -cne 'Default Switch' -or $switch.SwitchType.ToString() -ne 'Internal') { throw 'SWITCH_IDENTITY_MISMATCH' }
            $effectRequested = $true
            Connect-VMNetworkAdapter -VMNetworkAdapter $adapter -VMSwitch $switch -Confirm:$false
            $fresh = Get-BoundAdapter
            if (-not $fresh.Connected -or $fresh.SwitchId -ne $switchId) { throw 'CONNECT_READBACK_MISMATCH' }
            $result.Status = 'CONNECTED_OWNER_ACTIVATION_REQUIRED'
        } else {
            $effectRequested = $true
            Disconnect-VMNetworkAdapter -VMNetworkAdapter $adapter -Confirm:$false
            $fresh = Get-BoundAdapter
            if ($fresh.Connected -or $fresh.SwitchId) { throw 'DISCONNECT_READBACK_MISMATCH' }
            $result.Status = 'DISCONNECTED_ACTIVATION_SEPARATE'
        }
        $result.Connected = [bool]$fresh.Connected
        $code = 0
    } catch {
        if ($_.Exception.Message -cmatch '^[A-Z_]{1,64}$') { $result.Failure=$_.Exception.Message } else { $result.Failure='NATIVE_OPERATION_FAILED' }
        if ($effectRequested) {
            $result.Status = 'RECOVERY_REQUIRED'
            if ($Action -ceq 'CONNECT') {
                try {
                    $ownedAdapter = Get-BoundAdapter
                    Disconnect-VMNetworkAdapter -VMNetworkAdapter $ownedAdapter -Confirm:$false
                    $after = Get-BoundAdapter
                    if ($after.Connected -or $after.SwitchId) { throw 'ROLLBACK_UNCONFIRMED' }
                    $result.Status = 'BLOCKED_DISCONNECTED'
                    $result.Connected = $false
                } catch { $result.Status='RECOVERY_REQUIRED' }
            }
        }
    }
    if ($null -ne $stream) {
        try {
            $bytes = [Text.Encoding]::UTF8.GetBytes(($result | ConvertTo-Json))
            $stream.Write($bytes,0,$bytes.Length)
            $stream.Flush($true)
        } catch { $code=44 } finally { $stream.Dispose() }
    }
    exit $code
}
```

Exit 44 is a failed output carrier, not proof of network restoration. After CONNECT
exit 44, use DISCONNECT immediately; after DISCONNECT exit 44, one bounded retry uses
a fresh DisconnectAttempt GUID. Both retain earlier records and require exact result
readback. If that single recovery attempt fails, stop other work as RECOVERY_REQUIRED
and have the owner disconnect the exact adapter through Hyper-V Manager, then inspect
native state. No automatic loop, report overwrite or CONNECT retry is authorized.

Official references: [evaluation activation](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise),
[slmgr options](https://learn.microsoft.com/en-us/windows-server/get-started/activation-slmgr-vbs-options),
[Connect-VMNetworkAdapter](https://learn.microsoft.com/en-us/powershell/module/hyper-v/connect-vmnetworkadapter).
