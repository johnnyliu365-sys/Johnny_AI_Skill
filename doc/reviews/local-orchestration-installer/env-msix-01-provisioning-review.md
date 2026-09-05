# ENV-MSIX-01 — Provisioning convergence review

| Field | Value |
| --- | --- |
| Artifact ID / kind / revision | `REVIEW-ENV-MSIX-01-20260905` / `OPERATIONAL_READINESS_REVIEW` / `03` |
| Date / current conclusion | `2026-09-06 (Asia/Taipei)` / `APPROVED / VM_BOOTED_SETUP_PENDING`; original convergence history below retained |
| Action / closure | [ENV-MSIX-01](../../../modules/tickets/local-orchestration-installer/env-msix-01-disposable-hyper-v.md) / `CLOSURE-ENV-MSIX-01/01` |
| Initial candidate | `15ca43c29307850b8037ff9c11fcc983b3826fb0` |
| Correction candidate / leaf digest | `7e249dcfc5d722c79f6c1a4f3a1109229ccc4484` / `4f9936c518cd7a05015f724096e4fd2f3d539530d3524182067ff13709b3340c` |
| Final reviewer / helper | Current-session operator / reused Terra-xhigh read-only adversarial helper; no implementation lane or delegated verdict |
| Effect result | Exact reviewed VM recipe executed once, exit 0 and bound result readback; no test certificate creation/import, host trust change, package operation, host registration, push or release |

## Original bounded reviews — historical findings and disposition

| Finding | Closure binding / category | Evidence and disposition |
| --- | --- | --- |
| ENV-F1: unobservable partial root admission | Item 5, `ERROR_PARTIAL_FAILURE / OBSERVABILITY`; operational recipe defect | Initial candidate could create the root then fail ACL admission before acquiring result-write authority. Correction introduced pre-creation phase tracking, parent-observed exit 43 for unproved ownership, and exit 44 for failed result delivery. Reviewer inspected those branches: CLOSED by correction, static evidence only; no privileged fault injection was performed. |
| ENV-F2: elevated module search includes user-writable locations | Items 1–2 and the recipe's explicit no-writable-script elevation boundary, `AUTHORIZATION / DEPLOYMENT_READINESS`; operational recipe defect | Correction candidate line 84 imports `Hyper-V` by name, before `try` and before admission checks. A competing user module can therefore be selected by inherited module discovery; failures also precede the declared result handling. Reviewer independently confirmed the search-path premise below. OPEN / BLOCKING; no hostile module was created or executed. |

Both helper returns were received in the existing session. The operator accepts
ENV-F2 as a flaw in the operator-authored recipe, not insufficient owner VM authority,
a missing runner, a product MSIX limitation or an implementer's performance problem.
The second review does not retroactively become approval because ENV-F1 closed.

## Independent read-only evidence

The fresh Windows PowerShell process was invoked without a profile:

```powershell
& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo -NoProfile -NonInteractive -Command '$env:PSModulePath -split ";"'
```

Unfiltered output:

```text
C:\Users\GameBoy\Documents\WindowsPowerShell\Modules
C:\Program Files\WindowsPowerShell\Modules
C:\Windows\system32\WindowsPowerShell\v1.0\Modules
```

Microsoft documents CurrentUser search paths and name-based module discovery in
[about_PSModulePath](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_psmodulepath?view=powershell-7.4),
including Windows PowerShell 5.1's locations. The risk conclusion is an inference
from that behavior and this recipe, not a claim that this workstation is compromised.
The earlier administrator `Get-VMHost` probe's exit 0 proves access, not trusted
module identity; it must not be promoted into provenance evidence.

Read-only filesystem discovery found these Windows manifests:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Hyper-V\1.1\Hyper-V.psd1
C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Hyper-V\2.0.0.0\Hyper-V.psd1
```

Their presence is not yet admission of either version or its transitive executable
dependencies. No system/user module, module search path, profile, group membership
or certificate store was modified. The exact correction recipe passed a parse-only
Windows PowerShell 5.1 check (`WINDOWS_POWERSHELL_51_PARSE_PASS`, exit 0); parsing is
neither execution nor security qualification.

## Media disposition before provisioning

The official Windows evaluation ISO download completed independently of VM admission.
The downloader exited 0 after checking the full file against the size and the
independently read official Microsoft hash bound in the action. Unfiltered output:

```text
ISO_VERIFIED_SHA256=89626da8fdfdd8d03c31bc911bc525145c9e07e3a5f1c299e0645f0ab7e38096
ISO_VERIFIED_BYTES=7335473152
```

The verified media remains in the declared user-local cache. This is acquisition
evidence only; the protected-copy check is still required before future attachment.
No media is attached and no VM was started by this action.

## Original convergence and proposed decision — historical

[CodeReview section 5](../../../CodeReview.md#5-結論與收斂) allows one initial plus
one correction review for a Closure revision. Both are exhausted with ENV-F2 open.
No third correction, new helper, silent alternative provisioning method or automatic
cleanup is admitted. Preserve both candidate commits and the rejected recipe.

The smallest proposed continuation is an **owner-scoped single-use override** for
ENV-F2 only, as allowed by the ticket-set continuation rule: bind the protected OS
PowerShell/module identity, eliminate writable-location discovery and implicit
autoload across the elevated command's dependencies, and include bootstrap failures
in the independent failure carrier. Prove rejection of an untrusted resolution
without running hostile code elevated, then perform one complete bounded review.
This is a proposal, not a corrected recipe or an approved executable closure. Do not
split this small operational fix into a new product framework or weaken isolation.

The existing authorization for exactly one disposable VM and guest-only test trust
remains valid. The additional owner decision concerns this single review-limit
exception, not renewed permission for the same VM. Only an approved corrected
recipe and verified media may resume the original effect. Another blocking return
stops again; it does not start an indefinite correction loop.

Return: `ACTION_COMPLETED` for evidence recording; VM provisioning remains
`BLOCKED / CONVERGENCE_REVIEW_REQUIRED`. Continuation: `WAIT_FOR_HUMAN` for the
named single-use override. No Windows or MSIX lifecycle qualification is claimed.

## Owner-approved single-use ENV-F2 correction

The owner explicitly approved the preceding proposal on 2026-09-05. This grants one
additional correction/review for ENV-F2 only, then continuation of the existing VM
authority after approval. It does not grant another automatic correction, host
trust changes, a product rewrite, push or release. The current candidate is
`f3e77eed6da2fa85b2e115508776f1b3dc311c74`, action revision 04, LF SHA-256
`c339a50c82a18067a945ead4c586f3027e9fe72e2d9ad64255c4fab24f9d0541`.

The reviewer inspected the exact bootstrap and unchanged VM/result body. Fixed OS
manifests, disabled autoload, child-local search paths, ACL/reparse admission and
native module name/version/GUID/base readback close ENV-F2 under the declared
standard-user module-shadowing threat model. Bootstrap rejection exits 45 before
root creation. Existing ENV-F1 exit-43/44 recovery behavior remains intact.
No persistent environment setting, profile or system module was changed.

Actual Windows readback corrected a draft assumption before candidate freeze:
the three built-in Microsoft.PowerShell modules report PSHOME as ModuleBase, not
their manifest directory. The frozen recipe binds those exact native values;
CimCmdlets and Hyper-V retain their observed module directories. This is not a
generic path fallback. Hyper-V is exactly version 2.0.0.0 with GUID
`af4bddd0-8583-4ff2-84b2-a33f5c8de8a7`.

### Reproducible reviewer counter-mutation

Run this in the control checkout **without elevation**. It extracts only the marked
bootstrap from the immutable candidate; none of the variants contains VM operations
or file writes. The mutations exist only in process memory, not in the candidate.

```powershell
$candidate = 'f3e77eed6da2fa85b2e115508776f1b3dc311c74'
$body = (git show ($candidate+':modules/tickets/local-orchestration-installer/env-msix-01-disposable-hyper-v.md')) -join "`n"
$fence = [string]::new([char]96,3)
$recipe = [regex]::Match($body,'(?s)'+$fence+'powershell\n(.*?)\n'+$fence).Groups[1].Value
$bootstrap = $recipe.Substring(0,$recipe.IndexOf('# ENV_F2_BOOTSTRAP_END'))
$wrongGuid = $bootstrap.Replace('af4bddd0-8583-4ff2-84b2-a33f5c8de8a7','00000000-0000-0000-0000-000000000000')
$userManifest = $bootstrap.Replace('Assert-ProtectedOsPath $manifest','if ($spec[1] -eq ''Hyper-V'') { $manifest = ''C:\Users\GameBoy\Documents\WindowsPowerShell\Modules\Hyper-V\Hyper-V.psd1'' }; Assert-ProtectedOsPath $manifest')
$cases = @(
    [pscustomobject]@{Name='F2_INHERITED_USER_PATH';Code=('$env:PSModulePath=''C:\Users\GameBoy\Documents\WindowsPowerShell\Modules'''+"`n"+$bootstrap);Expected=0;Observed=0},
    [pscustomobject]@{Name='F2_REJECT_USER_MANIFEST';Code=$userManifest;Expected=45;Observed=45},
    [pscustomobject]@{Name='F2_REJECT_WRONG_GUID';Code=$wrongGuid;Expected=45;Observed=45},
    [pscustomobject]@{Name='F2_COUNTER_MUTATION_REMOVE_GUID_GUARD';Code=$wrongGuid.Replace(' -or $loaded[0].Guid -ne [guid]$spec[3]','');Expected=45;Observed=0},
    [pscustomobject]@{Name='F2_RESTORE_GUID_GUARD';Code=$wrongGuid;Expected=45;Observed=45}
)
foreach ($case in $cases) {
    'CELL='+$case.Name
    $suffix = 'if ($PSModuleAutoLoadingPreference -ne "None" -or $env:PSModulePath -cne $osModules) { exit 90 }; [Console]::WriteLine("BOOTSTRAP_ONLY_PASS"); exit 0'
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($case.Code+"`n"+$suffix))
    & 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo -NoProfile -NonInteractive -EncodedCommand $encoded
    $result = $LASTEXITCODE
    'EXPECTED='+$case.Expected+' ACTUAL='+$result
    if ($result -eq $case.Expected) { 'ASSERTION=GREEN' } else { 'ASSERTION=RED' }
    if ($result -ne $case.Observed) { throw 'UNEXPECTED_COUNTER_MUTATION_RESULT' }
}
'PINNED_COUNTER_MUTATION_SEQUENCE_PASS'
```

Direct unfiltered stdout/stderr, no output-reducing wrapper:

```text
CELL=F2_INHERITED_USER_PATH
BOOTSTRAP_ONLY_PASS
EXPECTED=0 ACTUAL=0
ASSERTION=GREEN
CELL=F2_REJECT_USER_MANIFEST
MODULE_PATH_UNTRUSTED
EXPECTED=45 ACTUAL=45
ASSERTION=GREEN
CELL=F2_REJECT_WRONG_GUID
MODULE_IDENTITY_MISMATCH
EXPECTED=45 ACTUAL=45
ASSERTION=GREEN
CELL=F2_COUNTER_MUTATION_REMOVE_GUID_GUARD
BOOTSTRAP_ONLY_PASS
EXPECTED=45 ACTUAL=0
ASSERTION=RED
CELL=F2_RESTORE_GUID_GUARD
MODULE_IDENTITY_MISMATCH
EXPECTED=45 ACTUAL=45
ASSERTION=GREEN
PINNED_COUNTER_MUTATION_SEQUENCE_PASS
```

The first input refusal and the separate removed-GUID-check mutation enter different
guards. The mutation passes real native loading with a wrong expected identity,
making the rejection assertion red; restoring the exact guard returns it green.
This proves the bootstrap's identity check, not a live elevated attack or VM failure
recovery. No hostile module or fixture was installed. Full recipe parsing in Windows
PowerShell 5.1 returned `WINDOWS_POWERSHELL_51_PARSE_PASS`, exit 0. Its actual encoded
command length is 28,980 characters. AST-derived `Get-Command` discovery in the
bootstrap-only child resolved all 33 referenced native commands from Core or the
five admitted modules and returned `COMMAND_DISCOVERY_PASS`; no VM cmdlet was invoked.

### Additional audit and final operator conclusion

The reused Terra/xhigh helper returned `NO_FINDINGS` for the exact candidate and
digest, without executing the bootstrap or native effects. The operator independently
checked the evidence and retains the final verdict. One wording error in that return
was corrected: `f3e77ee` is a **descendant**, not an ancestor, of `a193b0e`.
`git merge-base --is-ancestor a193b0e f3e77ee` exited 0; the reverse exited 1.

ENV-F2 is CLOSED for this bound action. Final verdict: `APPROVED` for the exact
native provisioning recipe only. `ACTION_COMPLETED -> AUTO_CONTINUE` selects the
single originally authorized VM creation. The helper's return is not effect
authority or proof of execution. The original ISO/copy, owned-root, offline isolation,
partial-failure and no-host-trust constraints remain mandatory. SQL/tenant/schema/
production-account and release vectors are outside this VM-only action; guest test
trust remains authorized but deferred, and MSIX package lifecycle remains UNPROVED.

## Actual owner-authorized provisioning result

After approval commit `6ec58eb04f70f88af2dc1d97236bd8681bffe3da`, the operator
verified clean HEAD and submitted only the unchanged PowerShell block from
`f3e77eed6da2fa85b2e115508776f1b3dc311c74` to the literal System32 executable via
normal UAC, `-NoLogo -NoProfile -NonInteractive -EncodedCommand`, hidden process
window and System32 working directory. The parent waited for the process; it did
not create a background automation, retry, feature toggle or second VM.

Independent process return and complete result-file readback:

```text
ENV_MSIX01_PROVISION_PROCESS_EXIT=0
{
    "Environment":  "ENV-MSIX-01-20260905",
    "Status":  "VM_BOOTED_SETUP_PENDING",
    "Phase":  "BOOT_READBACK_COMPLETE",
    "VMId":  "7701b26b-5b5a-42c0-b1e1-36d34dfdaa46",
    "Failure":  null,
    "Name":  "Johnny-MSIX-Lab-20260905",
    "Generation":  2,
    "MemoryBytes":  4294967296,
    "Processors":  4,
    "VhdCapacityBytes":  85899345920,
    "NetworkConnected":  false,
    "IntegrationServicesEnabled":  0,
    "SecureBoot":  "On",
    "TpmEnabled":  true,
    "IsoSha256":  "89626da8fdfdd8d03c31bc911bc525145c9e07e3a5f1c299e0645f0ab7e38096"
}
```

The actual result is
`C:\ProgramData\JohnnyMsixLab-ENV-MSIX-01-20260905\provision-result.json`, raw
SHA-256 `90df7bf5d1d6264411f1f09bd007d4845d4e838fb092548760f6a7826c482726`.
Its native creation timestamp is `2026-09-05T23:56:12.7970718+08:00`; this report
was finalized after midnight without renaming the already bound environment/VM.
The non-elevated parent read it by exact path and checked environment, state, VM ID,
name, disconnected network, Secure Boot and vTPM against the admitted identity.
The recipe had freshly queried native resources and Running state before emitting
that result. This is observed creation/boot evidence, not a guest setup assertion.

The operator launched `C:\Windows\System32\vmconnect.exe` through normal UAC for
the basic console of `localhost / Johnny-MSIX-Lab-20260905`; process ID 45052 and
window title `在 localhost 上的 Johnny-MSIX-Lab-20260905 - 虛擬機器連線` were read
back. Opening a console is not evidence that Windows is installed, an account
is configured, networking is connected or a package is installable. No credentials
were requested, captured or persisted by the operator.

Return: `ENVIRONMENT_BOOTSTRAP_RETURN.VM_BOOTED_SETUP_PENDING -> ACTION_COMPLETED`.
Continuation: `WAIT_FOR_HUMAN / OWNER_GUEST_SETUP_REQUIRED` for Windows installation
and initial setup in that exact VM. Do not rerun create, change the working host's
trust, silently connect networking/shared drives or claim MSIX qualification. Guest
test trust remains deferred until the guest is usable. No cleanup/deletion occurred;
the media, protected VM root and VHDX are retained for this authorized test environment.
