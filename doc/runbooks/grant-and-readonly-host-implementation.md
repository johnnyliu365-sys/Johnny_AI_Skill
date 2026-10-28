# Core capability implementation decision — revision22

Current local result supersedes the Source35-in-progress observation below:
corrected sourcec14c2038 has original-seat SOURCE_ONLY_PASS, own engineering hold
FF619->c14, affected17PASS/1SKIP with tool83743f1e. S34R2 already-materialized
package stays at immutable619; fresh byte-QA956858d8 confirms120segments/exactEOF.
Matching controller23purechecks and original-seat reviewb3ae2ef8 pass as
PREPARATION_ONLY_NOT_EXECUTION_ADMITTED. Old subject expiry has passed; only
the proposed finite lease is a new current setup decision, not the existing
same-target repair or local source authority. No actual renewal/setup/Host.
The independently reviewed lease proposal first recorded at revision21 below
is unchanged in bytes/semantics and remains NOT_AUTHORIZED/NOT_EXECUTED.

Source34 revision02 is SOURCE_ONLY_PASS at619a53dd after original R2 correction,
author mutations and different-door reviewer close mutation. Fresh raw originals
read back; historical missing durable captures remain transcript-only. Root's
engineering hold is frozen619, not main or30B/43. Cached offline NativeAOT02
recordea52b11a has exit0/17.139s/complete streams/47 unchanged source-config pins;
unexecuted4207104-byte AMD64 artifactc8b063c8, byteQA8be00152. SDK workload
diagnostic is retained; no workload update or zero-warning claim. Old incomplete-
capture link01 and all earlier failures stay. No installation or Host success.

Source35 revision02 allocation16d6322a received different-seat DOC_PASS; same
author/two paths now builds its local typed/fake tool at619. Real Parameters
existence is an execution precondition, not a circular source-build prerequisite.
Root packages Source34 from frozen hold, independently of that moving author tree.
Next real SETUP33 recovery must pin new binary/script/enrollment/frame and exact
original retained-service evidence; unchanged account lease/15-minute guard and
all no-start/no-Approval/no-Host exclusions remain. If the lease is insufficient,
stop only that effect; complete local tools/preparation and consolidate genuinely
new external actions, never silently renew or ask again for local technical work.

## Pending external difference — same subject, finite lease renewal only

NOT_AUTHORIZED / NOT_EXECUTED. The original approved expiry was
2026-10-28T05:29:21.4681709Z (Taipei13:29:21); ordinary local-user readback at
05:35:31Z confirms it is past. This is not another request for the already
approved local code, independent review, SDK use or same-target SETUP33 repair.
Recommended new effect is ONLY renewal of the same existing Users-only subject
on DESKTOP-28ERPQ1 through2026-10-29T05:29:21.4681709Z, exactly24h beyond its
original expiry. No new account, password reset, group/admin membership, service
start, Registry records, Host/model/API call, cost, network or formal activation.

Proposed operation, only after explicit approval of this new finite lease and
only in GameBoy's elevated64-bit Windows PowerShell; do not run during preparation:

```powershell
$ErrorActionPreference = 'Stop'
if ([Environment]::MachineName -cne 'DESKTOP-28ERPQ1' -or -not [Environment]::Is64BitProcess) {
    throw 'wrong_machine_or_process'
}
$leaseIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
try {
    $leasePrincipal = [Security.Principal.WindowsPrincipal]::new($leaseIdentity)
    if ($leaseIdentity.User.Value -cne 'S-1-5-21-3542654388-73774624-397494543-1001' -or
        -not $leasePrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'exact_elevated_controller_required'
    }
    $leaseSubject = Get-LocalUser -Name JohnnyReadonlyReview
    $leaseOldUtc = [DateTimeOffset]::Parse('2026-10-28T05:29:21.4681709Z').UtcDateTime
    $leaseNewUtc = [DateTimeOffset]::Parse('2026-10-29T05:29:21.4681709Z').UtcDateTime
    if ($leaseSubject.SID.Value -cne 'S-1-5-21-3542654388-73774624-397494543-1006' -or
        -not $leaseSubject.Enabled -or $null -eq $leaseSubject.AccountExpires -or
        $leaseSubject.AccountExpires.ToUniversalTime() -ne $leaseOldUtc -or
        $leaseNewUtc -le [DateTime]::UtcNow.AddMinutes(15)) { throw 'subject_or_lease_changed' }
    $leaseGroups = @(Get-LocalGroup | ForEach-Object {
        $leaseGroup = $_
        $leaseMatches = @(Get-LocalGroupMember -SID $leaseGroup.SID -ErrorAction Stop |
            Where-Object { $_.SID.Value -ceq $leaseSubject.SID.Value })
        if ($leaseMatches.Count -gt 0) { $leaseGroup.SID.Value }
    })
    if ($leaseGroups.Count -ne 1 -or $leaseGroups[0] -cne 'S-1-5-32-545') { throw 'subject_groups_changed' }
    Set-LocalUser -SID $leaseSubject.SID -AccountExpires $leaseNewUtc.ToLocalTime()
    $leaseFresh = Get-LocalUser -SID $leaseSubject.SID
    if ($leaseFresh.SID.Value -cne $leaseSubject.SID.Value -or -not $leaseFresh.Enabled -or
        $leaseFresh.AccountExpires.ToUniversalTime() -ne $leaseNewUtc) { throw 'lease_readback_failed_preserve_evidence' }
    [pscustomobject]@{ Name=$leaseFresh.Name; SID=$leaseFresh.SID.Value;
        AccountExpiresUtc=$leaseFresh.AccountExpires.ToUniversalTime().ToString('o') } | ConvertTo-Json
} finally { $leaseIdentity.Dispose() }
```

Risk: the existing non-admin account can log in for one more finite day; no new
rights are conferred. Readback failure preserves state/evidence, no automatic
retry. Exact rollback, if separately directed, restores ONLY AccountExpires to
the old UTC instant after verifying the same SID and current new expiry; never
delete the account, profile, worktrees or Recovery evidence. Original profile
creation/log-in request remains an already-authorized Owner-local password
action, not another policy approval: log into this account once and switch back,
keeping any session required by the later precise token/session binding. Root
does not obtain the password or invent session/token/LUID evidence. Actual
protected records/service-start/Host qualification still require their own
exact new effect package; a renewed lease does not authorize them.

## revision19 actual recovery history

Current actual state supersedes revision18 preparation: the original S34 single
run PID41884 at03:43:39Z..03:43:53Z staged120assets then returned Recovery after
SCM service creation, before Parameters/files. Supporting protected readonly
PID9716 at03:51:05Z produced3a119b91: task disabled/State1/noinstances/result3;
service LocalSystem/OwnProcess/Disabled/Stopped/exact path; Parameters/code/data
absent;120assets all match. Do not rerun Apply or delete/recreate the service.

SCM readback defect is demonstrated, not guessed: sc sdshow omits owner and may
include SACL; the expected plan includes O:SY and DACL. Its text cannot prove
owner and cannot equal the full expected descriptor. Keep the owner invariant;
build fixed-service native OWNER|DACL verification, no SACL query/privilege enable.
Original Source34 revision02 local grant8286ccb4 is independently admitted:
fiveMOD/one cohesive new native readback module, typed/fake construction first,
then real source wiring/negative tests/review. Source35 no edits, deferred to
this direct common30B/43 prerequisite; not a new governance branch/framework.
Later exact service-only recovery must bind original-run evidence, fresh state
and reviewed new binary/input versions; no state-only authority or mixed-partial
adoption. Normal same-scope source repairs do not require repeated Owner asks.
Current service remains stopped/disabled; no Host/model/runtime Grant or success.

## revision18 preparation history (superseded by actual outcome above)

Current actual status supersedes the preparation history below: LF01 launch03
ran02:45:38Z..02:45:52Z and staged all120 assets; corrected plan818LF passed.
Apply refused service_sid_mismatch before SCM create because of English-only
label parsing, not wrong SID. Protected postrun8e16c6f8 confirms disabled task,
no instances, result2, lastRun02:45:41Z, absent service/final roots and exact120
asset hashes/security. Recovery and old inputs remain held.

Original two-path Source34 candidate80dbc951 is independently accepted after
same-ticket F1/F2 correction; reviewer different-door cardinality mutation raw
5cee8946 was fully read by Root and restored to exact sourcebdaf26ce. Existing
engineering hold advanced to80db only, not main/30B/43. No C# changed; reuse
native351fa176, do not rebuild gratuitously. Fresh immutable S34 inputs are the
next same-authorized-target SETUP33 correction, with independent byte/source
review and exact registered-task XML/ACL readback before a single run. No new
account/SID/lease, permission principal, service-start, Host/model, ApprovalV1,
SubjectEnrollmentV1 or runtime Grant effect is inferred. Normal same-scope
engineering choices proceed; only genuinely additional effects need decisions.

## revision17 preparation history (superseded by actual outcome above)

Current final same-task resume: LF01 update ran once then refused BEFORE Enable/
Run because Definition.XmlText and Task.Xml differ in serialization. Protected
diagnostic eac38bdf confirms disabled/State1/instances0/result2/lastRun02:06:02Z;
service/install/new stage absent, all six logs empty. Root's exact full-DOM check
replaces ONLY old registered Arguments and obtains byte-equivalent normalized
actual DOM; no other definition change. Same actual closed task SD remains.
Do not weaken canonicalization or register again. Reuse the existing corrected
frame/logs, validate exact protected bytes/ACLs before enable. Registered fullXML
9e399081c1328ff4a8fd9d16745f788449b7b7a92ed423f5ec24361bf882a54f;
normalized65be5fa6a583f8eabb69e974a13c904159780bd66de8d2903f2ccb2e511f35ba.
Final source22047bytes SHA39c2e707a684ca3648f596aa16431c63ea97ca969de77724fbfb294fb26aacc7;
ONLY launch03.json26522bytes SHA48a113deeecb80110387de4001f8a43d1d8a16d475163cbab51ccc837e47e33a.
15pure cases/PS5.1 parse0/roundtrip and focused independent preparation review
PASS; execution-time live frame readback remains mandatory. No frame/log creation,
task registration or new ACL action. Fresh protected .failure03.json preserves
the prior575-byte .failure.json; same absence/lease/identity/deadline/exclusions.
This is the original authorized installation correction, not a new Owner wait.
No actual success yet; previous preparation below is retained superseded history.

## Current SETUP33 LF correction — same authorized targets, review before run

The previously frozen resume actually ran once on2026-10-28: SYSTEM staging
completed, then Apply correctly refused the817-byte plan missing its required LF.
Task is disabled/State1/no instances/result2; no service or final install roots
exist. Original raw failure6468365e and readback2f291fde remain held. This is a
packaging correction, not a product guard/schema change or an unchanged retry.

Root's derived scope under the original SETUP33 effects and Owner's explicit
no-duplicate-approval clarification: use the same machine/controller/subject,
unchanged lease, principals, native351fa176, final115payloads, service DISABLED/
STOPPED and NativeEnrollmentV1 only. No new entitlement or fee. Existing exact
task must match disabled full XML e684e532, SD O:BAG:BAD:(A;;FA;;;SY)(A;;FA;;;BA)(A;;FR;;;SY),
result2 and last run2026-10-28T02:06:02Z before mutation. Its action alone is
updated to the corrected fresh input paths; UPDATE plus DONT_ADD_PRINCIPAL_ACE,
never CREATE or broader principals. Exact updated definition and unchanged
actual SD must read back before Enable/Run. Original native image is reused.

Old inputs/staging/logs are never overwritten or deleted. New immutable frame
33007762bytes SHA594b76efd51902edcd80532f6cbdd42cbfa363f8b003a085bca2b6778106ab00;
plan818bytes SHA61f47a6ada0ccd25034de9d4b442f004d95cefd0144685caaa79a44b65bb01af
is exactly original JSON plus ONE LF. Corrected operation8064bytes SHA
0058426953f290587de97adb420af5c51f9873d54200004c67078c43dbeed9a1.
Preparation directory setup33-lf01-sid1006-20261028 is under the existing Temp
review parent. Fresh SYSTEM stage root is exactly
C:\ProgramData\JohnnyAuthorityStaging-setup33-lf01-20261028-sid1006.
Only new protected input/six log files and successful audit use prefix
C:\Program Files\JohnnySetup33LF01-20261028; final installation targets unchanged.

Root corrected payload22418bytes SHAd55754a5a78229eca4a403c939814990fb04a319b555446822a4d01835318566;
ONLY inline captured-byte launch02.json27170bytes SHA3d7db2ef174bd0ea3f87769b2f4adf7f11fbf72fcbd507e4dde7ac08be4d2fa8.
PS5.1 parser/loader roundtrip and14pure positive/negative cases passed; separate
seat authority_install_inventory confirmed DOC_PASS_PREPARATION_ONLY / BYTE_QA:
frame complete, all115payloads unchanged, task/loader bounded, source R1 closed.
Failure evidence now uses protected Program Files .failure.json via exact parent
validation and protected CreateNew ACL/readback; before those checks, console only.
No elevated Temp write. Rejected prior draft and failed QA remain preserved.
Finite PT3M/
185s, original parent/file/native security checks and failure journals retained;
fresh disable/no instances required before success. No whole-plan recovery claim.

No service start, Host/model call, ApprovalV1/SubjectEnrollmentV1/Grant creation,
network rule/listener, account extension, global policy, cleanup, push/release/
deployment or formal gate activation is covered. These genuinely different
effects retain their own precise authority; same-scope technical corrections
are not sent back for ceremonial Owner approval. Ordinary review and fixture
success are not Host qualification. Only checklist04 remains checked.

Below revision15 is preserved preparation/failure history, superseded only by
the actual observations and same-scope correction above.

Owner clarification2026-10-28: do not re-request approval for already explicitly
instructed work. Root applies that clarification ONLY to this same-scope repair
and continuation of the previously approved SETUP33 installation plan. The
extra ceremonial approval request below is superseded for the frozen resume
payload b3454f63/launch ee0d86eb; no new machine, account, permission principal,
target, external call or cost is added. This is NOT blanket approval for later
Host/model qualification or other excluded effects. Source review and live
identity/version/lease/effect checks remain mandatory. Existing failed attempts,
the consumed original launch and successful suspension remain recorded; no
replay of either old command. One bounded execution of the corrected resume
candidate may now proceed under the original plan plus this explicit clarification.

## SETUP33-RESUME-01 — exact continuation proposal, NOT AUTHORIZED

The approved disable-only operation succeeded at2026-10-27T09:31:56Z:
the original task is disabled/State1, zero active instances, ACL unchanged,
definition unchanged except Enabled. Original setup and Recovery closure are
still incomplete. This is the next bounded action for BOTH30B/43's shared
protected native-input prerequisite, not a new capability/framework/PRD.

Root prepared and separately reviewed the existing operation's minimal correction.
The proposed operation REUSES the original task and eight protected bootstrap
files; it creates no second task, account, bootstrap image or permission source.
It is NOT covered by the consumed setup or disable-only approval.

| Boundary | Exact proposed operation |
| --- | --- |
| Machine/controller | DESKTOP-28ERPQ1; GameBoy SID S-1-5-21-3542654388-73774624-397494543-1001; one visible elevated System32 x64 PS5.1 child, Process-only RemoteSigned |
| Subject | Existing JohnnyReadonlyReview SID S-1-5-21-3542654388-73774624-397494543-1006, Users545-only, enabled, existing expiry2026-10-28T05:29:21.4681709Z; refuse stale/changed identity/lease; no account/password/profile/TTL changes |
| Existing task | Only \\JohnnyAuthoritySetup33-20261027; require disabled/State1, zero instances, never-run267011, exact full XML SHA e684e5321f13982ac764c6e7d289d94812bf9a4ef857faa67ed4e01616c279a3 |
| Definition during operation | SHA281fb37603ca0eb65b9067f3b6055e69b6cd7441cc6463ae1dd00ef27277fe17 after removing ONLY Settings/Enabled; no other XML change accepted |
| Task security | Exact observed O:BAG:BAD:(A;;FA;;;SY)(A;;FA;;;BA)(A;;FR;;;SY), closed SYSTEM/Admins principals; no ACL update. This explicitly differs from the old unproved protected-flag/count2 assumption; it does NOT claim that flag exists or authorize a general validator relaxation |
| Reused files | Exact original4161024-byte native image SHA351fa1766fbedf062260338237fddd91874d22ce176802c70a37374a4e204703 and33007751-byte frame SHA586d204ca74a8b8e6b1ca5118b11bcd537a25ec75d1d2e497bbabe76c597db18, BA owner/protected SYSTEM/Admins-only inputs; all six owned logs must still be empty with their exact protected controller-read ACL |
| Single run | Set only this task Enabled=true; run its unchanged original stage-inputs && PS5.1 Apply && observe-enrollment chain ONCE; PT3M/185s bounded controller wait, no retry. Deadline may Stop only this exact task; it is not proof of descendant termination |
| Setup effects | Same NEW120-file SYSTEM/Admins-only staging root C:\ProgramData\JohnnyAuthorityStaging-setup33-20261027-sid1006; same115 payloads to C:\Program Files\JohnnyGrantAuthority and C:\ProgramData\JohnnyGrantAuthority; same LocalSystem service JohnnyGrantAuthority DISABLED/STOPPED and NativeEnrollmentV1 REG_BINARY. Fixed service SID S-1-5-80-3020799075-4261108201-91889776-39638685-3705689551; original plan/SCM rights unchanged |
| Evidence/suspension | Require original full120-asset hash/size/owner/DACL readback, Apply marker, native MATCH/NONE, Registry digest, stopped/disabled service. Disable and fresh-read exact task/no instances BEFORE success audit. Protected C:\Program Files\JohnnySetup33-20261027.readback.json CreateNew; any exception, including preflight, gets non-overwriting ordinary owner-resume01-failure.json diagnostic in existing preparation root where possible |
| Network/cost/exclusions | No listener/socket/firewall/network rule or model/API call/fee. No service start, ApprovalV1/SubjectEnrollmentV1/Grant fabrication, formal gate activation, global/GPO policy change, cleanup, push/release/deployment |

All original parent/root/native/file ACL invariants remain; accepting ONE observed
closed task descriptor does not qualify the later readonly Host. Any identity,
definition, ACL, existing file/log or source-pin drift refuses before the run.
Unknown failure or mismatched-task suspension stays RECOVERY_REQUIRED with held
files/logs/Registry; never retry, overwrite, delete or touch foreign work.

Preparation root remains:
C:\Users\GameBoy\AppData\Local\Temp\johnny30-native-service-review-20261021\setup33-sid1006-20261027.
owner-resume01.ps121464bytes SHA b3454f630f2f4a7038faf5e522e6ff93477eb0b3a54e88e14be95d01605e3505.
ONLY launch candidate owner-resume01-launch.json26200bytes SHA
ee0d86ebd040cf4940efdb9157e7336fd3ea8588feaf0c041a7d6c3e80c7d349.
The reused inline-gzip loader checks bounds/hash/strict UTF8 then invokes the SAME
captured bytes; no Temp -File/hash-reopen execution. Exact command25749chars,
below32767. Both loader and payload parse in actual PS5.1; ordinary separate-seat
DOC_PASS_PREPARATION_ONLY/BYTE_QA, fake positives and foreign/mismatched negatives
are NOT real task execution or CVQ/Host qualification.

After NEW explicit approval ONLY, the parent captures and hash-checks the26200-byte
launch JSON, then uses its fixed argv with Start-Process -Verb RunAs -WindowStyle
Normal -PassThru. No replay of launch03 or the disable-only command. The immutable
draft marker remains historical data, never a self-issued authority source.
Operation assets have Root/Ticket30 ownership, TTL24h plus active Review/Recovery
hold and preserve teardown; no cleanup while held. Raw originals are sealed in
the existing Ticket30 review, including both actual readback reports.

Successful setup would close ONLY the shared installed/protected-input prerequisite.
Next is the already-declared CVQ first-entry authorization/qualification, then
30G/30B/43's original isolated audits and real legal Grant positive/negative checks.
No premature checklist marks, candidate integration, Host/model tests or public MSIX
acceptance. Only checklist04 is checked; unchanged R0/DAP/TAL/Recovery boundaries.

## Preserved revision14 operation and failure history

Owner activation, 2026-10-27: the latest explicit approval authorizes ONE exact
SETUP33-20261027-SID1006 execution of owner-launch03.json SHA256
176fabe991d1ee44ffe17c1c38735ce25073b1067190109f7c811ccd705e7103,
as sealed at 5436043b86cf16a8a0736093f46857979d8af9d5. The single execution exited1
at2026-10-27T09:05:47.4452157Z; RECOVERY_REQUIRED, task suspension UNVERIFIED.
Eight protected bootstrap files remain, six logs are empty, completion readback
is absent and Win32_Service returned zero matching services. Approved elevated
read-only diagnostic later found task enabled/Ready, no triggers, never-run
result0x41303. Actual task SDDL lacks the expected protected flag and has an extra
SYSTEM-read ACE; both normal acceptance and recovery-disable reuse the rejecting
assertion. Independent source/readback analysis confirmed this causal path.
Owner separately approved the exact-match disable-only operation. One execution
at2026-10-27T09:31:56Z confirmed Enabled=false/State1/no active instances, same
ACL and unchanged definition apart from Enabled. Suspension is CONFIRMED; setup
and Recovery closure remain incomplete. No retry, deletion, ACL update or
alternative setup is authorized; the original setup permission stays consumed.
The following NOT AUTHORIZED labels describe the preserved pre-approval
proposal, not a second approval request. The review records the activation;
all operation boundaries below remain unchanged.

## SETUP33-20261027-SID1006 — exact Owner operation, NOT AUTHORIZED

Source33/correction01 is accepted into Root's existing engineering hold at
2f61dbbb589ba5469e74c83e8d22160b135b2682. Separate-seat source audit, Root's
different-door late SIZE mutant RED/restored GREEN and42 exact originals passed
byte QA (seal69eaaae5). S33-F1's pre-service/service-SID dependency is fixed.
The actual hold's cached offline NativeAOT link passed17.297s, source/SDK/MSVC
pins unchanged. Image4161024bytes, AMD64/PE32+/CLR0, FileVersion1.0.0.0,
ProductVersion1.0.0+2f61dbbb589ba5469e74c83e8d22160b135b2682. UNEXECUTED.
Workload-verification notice retained; no update/download. This supersedes the
old pending inputs below, NOT the consumed setup32 ValidateOnly permission.

### Exact pending security effect

| Surface | Exact operation |
| --- | --- |
| Machine | API-verified DESKTOP-28ERPQ1 / physical Windows10 host, NOT VM |
| Controller | GameBoy SID S-1-5-21-3542654388-73774624-397494543-1001; ONE visible UAC elevated x64 PS5.1 child, Process-only RemoteSigned |
| Existing subject | JohnnyReadonlyReview SID S-1-5-21-3542654388-73774624-397494543-1006; verify Users545-only/enabled/expiry2026-10-28T05:29:21.4681709Z; NO password/account/profile/TTL change |
| Bootstrap files | NEW C:\Program Files\JohnnySetup33-20261027.exe and .input.bin; atomic CreateNew, BA owner/group, protected SYSTEM/Admins FullControl only |
| Evidence files | Same prefix .stage.stdout/.stage.stderr/.apply.stdout/.apply.stderr/.observe.stdout/.observe.stderr/.readback.json; protected BA owner, SYSTEM/Admins FullControl plus controller1001 FILE_GENERIC_READ only;9 bootstrap files total |
| Task | NEW \JohnnyAuthoritySetup33-20261027; CREATE_ONLY, no trigger, one manual Run, SYSTEM S-1-5-18/logon5/highest, PT3M, no auto retry; exact definition/security/settings readback; disable/readback BEFORE success |
| Task DACL | O:BAG:BAD:P(A;;GA;;;SY)(A;;GA;;;BA) |
| Staging | NEW C:\ProgramData\JohnnyAuthorityStaging-setup33-20261027-sid1006;120 exact files, SYSTEM owner, protected SYSTEM/Admins FullControl only; no adoption/overwrite |
| Action chain | Absolute cmd /d /s /c: pinned native stage-inputs with binary stdin && exact staged PS5.1 Apply && existing native observe-enrollment; only exit0 continues. Apply uses ONE additional SYSTEM Process-only RemoteSigned PS child |
| Service | NEW JohnnyGrantAuthority, LocalSystem own process, DISABLED/STOPPED; fixed SID S-1-5-80-3020799075-4261108201-91889776-39638685-3705689551; binary "C:\Program Files\JohnnyGrantAuthority\JohnnyAuthority.Tools.exe" service; NO START |
| Roots / Registry | NEW C:\Program Files\JohnnyGrantAuthority and C:\ProgramData\JohnnyGrantAuthority;115 pinned payloads, exact native plan owner/DACL; Registry64 HKLM\SYSTEM\CurrentControlSet\Services\JohnnyGrantAuthority\Parameters\NativeEnrollmentV1 REG_BINARY only |
| Excluded | No ApprovalV1/SubjectEnrollmentV1/Grant, Host/model/API call, listener/socket/firewall/network rule, new fee, push/release/deploy, formal gate activation or global/GPO ExecutionPolicy change |

Plan grants the fixed service SID reviewed code-read/data-access rights and
controller SCM query only, never start/config/write. Inputs/logs are protected
at creation, existing targets refuse. Full exact plan/SCM SDDL and Registry bytes
are in sealed operation inputs, not inferred from a chat label.

### Immutable versions and actual command

Preparation data root:
C:\Users\GameBoy\AppData\Local\Temp\johnny30-native-service-review-20261021\setup33-sid1006-20261027.
This remains untrusted data, NOT a SYSTEM staging root. Existing113 dependencies
and configuration unchanged; new115-payload package only. Managed pure
plan/validate-enrollment PASS; no native/OS operation.

| Artifact | SHA256 |
| --- | --- |
| Native image,4161024bytes |351fa1766fbedf062260338237fddd91874d22ce176802c70a37374a4e204703|
| owner-bootstrap.ps1,19016bytes; reviewed text, never -File executed |7f3c28fb90ded60d832524898912c11a4aed21a03628eb5f0e22225b0ed0b7f6|
| owner-launch03.json,55187bytes; ONLY operation candidate |176fabe991d1ee44ffe17c1c38735ce25073b1067190109f7c811ccd705e7103|
| staging-input.bin,33007751bytes |586d204ca74a8b8e6b1ca5118b11bcd537a25ec75d1d2e497bbabe76c597db18|
| staging-manifest.json,21043bytes |3a11626edc2c058c8fae098e46624cbdfc16d3af65c421d6df8f4bebdc206e47|
| operation.json |22cbc51d132db674b549d52e86a72bb4e6c5845741b121c05a9b95bf60942f36|
| metadata/enrollment.json / NativeEnrollmentV1 |06966ecf535102f6042cc099a1e72486522236d48f8d835e726083b494eb0d69|
| staged Apply script,37807df0 blob639c0f02 |37b8c5e059acaba55212cc5631880133220342a6591000db94f7c39ee12c90aa|

Separate-seat DOC_PASS_EXACT_OPERATION_DRAFT_NOT_OS_VERIFIED: loader argv and
22963-char command reconstruct exactly (<32767); bounded gzip19,016 bytes/hash
matches bootstrap; PS5.1 parser zero errors. Bootstrap code is entirely embedded
in an immutable literal EncodedCommand, decoded/hash-checked in memory, then
ScriptBlock.Create uses those SAME bytes. No Temp script execution, no hash/reopen
TOCTOU and no recursive bootstrap framework. Exact trusted System32 modules only.
Old launch01/02 are superseded retained drafts, NEVER execute; initial01 template
SHA256-type substitution failure was caught before execution. The two task/
bootstrap safety findings and machine-report fidelity correction are closed.

After NEW explicit Owner approval ONLY, Root opens the visible UAC child with
the following fixed command. It does NOT run now; no unset encoded variable:

```powershell
$johnnyOperationPath = 'C:\Users\GameBoy\AppData\Local\Temp\johnny30-native-service-review-20261021\setup33-sid1006-20261027\owner-launch03.json'
$johnnyOperationBytes = [IO.File]::ReadAllBytes($johnnyOperationPath)
$johnnyHasher = [Security.Cryptography.SHA256]::Create()
try { $johnnyOperationHash = ([BitConverter]::ToString($johnnyHasher.ComputeHash($johnnyOperationBytes))).Replace('-','').ToLowerInvariant() } finally { $johnnyHasher.Dispose() }
if ($johnnyOperationBytes.Length -ne 55187 -or $johnnyOperationHash -cne '176fabe991d1ee44ffe17c1c38735ce25073b1067190109f7c811ccd705e7103') { throw 'operation_record_pin_mismatch' }
$johnnyOperation = [Text.UTF8Encoding]::new($false,$true).GetString($johnnyOperationBytes) | ConvertFrom-Json
Start-Process -FilePath $johnnyOperation.argv[0] -Verb RunAs -WindowStyle Normal -ArgumentList @($johnnyOperation.argv | Select-Object -Skip 1) -PassThru
```

The child alone changes its process policy/environment; parent/global/GPO policy
stays unchanged. The old one-child ValidateOnly grant is consumed, not reused.
Fresh API identity, account lease, parent ACLs and all pins must still match.

### Verification, risk and suspension

Require stage STAGED with exact root/ID and120 hash/size/owner/DACL readbacks;
Apply's exact success marker; separate native observation MATCH/NONE; exact
Registry digest; LocalSystem/STOPPED/DISABLED service/path; verified task disabled
BEFORE protected audit/success. Root reads protected outputs through its explicit
read-only ACE. Exit0/input identity/source review alone is not Host qualification.

This executes real elevated/SYSTEM code and creates machine-wide security state.
If console/polling fails, an already-running task/child MAY CONTINUE until PT3M;
disable prevents another start, not guaranteed fail-stop/descendant termination.
Deadline stops only the exact task; unknown residue stays RECOVERY_REQUIRED.
On registration uncertainty, query exact task and disable ONLY if full identity/
definition/action/DACL match. No retry/delete/overwrite/reset, no service start.
Rollback means safe non-destructive suspension: verify task disabled, preserve
new disabled service/files/Registry/logs for recovery. No claim of automatically
restoring the pre-install machine; later removal needs bounded authorization.
Owner Root/Ticket30/setup33, TTL24h plus active Review/Recovery hold, preserve
teardown. No automatic expiry cleanup of held evidence.

### Actual shortest acceptance route

1. This operation closes BOTH30B/43's protected-input/native setup prerequisite
   ONLY; it does not unblock their whole isolated review or check any item.
2. Actual setup readback -> existing CVQ first-entry qualification, fixed protected
   Host image, subject profile/session/token, tool bounds/trusted observations.
   Actual service-start/Host/model effects and verifiable cost bounds require
   precise authorization. No cost-control proof means UNAVAILABLE, not fake PASS.
3. Original final CVQ admission ->30G/30B/43 candidate-specific isolated audits;
   real trusted legal Grant readback/atomic consume positive AND forged/replay/
   mismatch rejection. R1 stays OPEN until real success; not all-deny completion.
4. 30B also requires same-fresh-SHA remote main index/leaves; local origin/main or
   unpublished Context04 is not proof. Push remains NOT_AUTHORIZED. Then original
   admission/closure and guarded local integration. Original12-item scope stays;
   only04 checked. No new VM/Broker/framework, no reopening closed N14B/04.


Status: OWNER_APPROVED_ORDER_EXCEPTION_AND_30G_SOURCE / NATIVE_OS_EFFECTS_NOT_AUTHORIZED.
Parent: Owner's existing12-item local batch; original Ticket30 and workflow/adaptive
SPEC lineages. This plan selects implementation responsibilities, not a new PRD,
Router, policy engine, qualification verdict or production activation.

## Current operation-input readback — identity updated2026-10-27

Current local construction:37807df0 engineering hold contains reviewed605a6fa4,
native d4d53a29 and the exact two wrapper/test CREATE blobs639c0f02/11f61c3f.
Actual hold strict/compile PASS and13 PS PASS/one explicit symlink SKIP, network[],
unchanged source; source checkout CRLF differs from author LF but exact normalized
Git bytes match (not claimed raw-byte identity). Original seal4d1930c7 preserves
16 native and8 wrapper records, including failures and argv07/08 provenance.
Cached-SDK LinkNative PASS; latest UNEXECUTED image3969024bytes SHA256
babb1394114cffb5dd4c8809df18bf180e290204c55d9ee2db4afabb68fd00ba,
FileVersion1.0.0.0/ProductVersion1.0.0+d4d53a297b640501dd13d93a56ff45d2292b4f07.
The corrected wrapper reuses native canonical validation BEFORE SCM/Registry,
fixed-capacity output, exact argv quoting; no Apply/installation is authorized.
605a6fa4 removes unrelated eager
workflow_router imports and rejects zero-request one-turn configuration. Private
114-file runtime actually imports63 committed application modules via six private
paths, unchanged hashes/SDK[]; original sealeb8b2806 and independent byte QA.
This guarded import explicitly disables COM registry extension redirection and is
NOT unpatched Host/OS qualification. No configuration/installation/model call.

The earlier duplicated Native validation and canonical-size ordering defect is
corrected under original Ticket30 correction02 (8a432a32 / activation3bc4a784),
not an open author implementation task. Separate-seat ordinary source review is
SOURCE_AUDIT_PASS_NOT_CVQ; no qualified isolation or formal30B/43 integration is
inferred. Old linked image8235b567 and114-file staging are immutable old evidence,
NOT the new operation binary. Exact real-SID enrollment/input pins and protected
setup readback still precede any separate Owner effect decision. Current top
sections supersede obsolete proposals below; do not silently rewrite history.

Target remains DESKTOP-28ERPQ1 / Windows10.0.19045; controller SID
S-1-5-21-3542654388-73774624-397494543-1001, token not elevated. Exact
JohnnyReadonlyReview was created by Owner in the approved local console, and
Root independently read back SID S-1-5-21-3542654388-73774624-397494543-1006,
EnabledTrue, exactly Users S-1-5-32-545, expiry2026-10-28T05:29:21.4681709Z
(Taipei2026-10-28 13:29:21). Win32_UserProfile for this SID remains absent;
no active-session/token/LUID evidence exists. Do not rerun New-LocalUser, reset
the password, silently extend expiry or substitute another identity. Owner may
perform the already approved local interactive sign-in to establish the profile,
then return to their usual account; no Host login/model call is included.
JohnnyGrantAuthority service and fixed ProgramFiles/ProgramData roots remain
absent. Actual NativeAOT input still matches3969024bytes/babb1394, unexecuted;
old private-runtime root is retained, no overwrite. Only identity creation is
verified, NOT protected setup, a trusted issuer/Grant success or qualification.

The old0.163.0-alpha.10.2 path/bin hash is no longer available in the bounded
metadata-directed lookup. The top-level bin/codex.exe0.130.0-alpha.5 is a different
fallback, NOT the process/command-resolved Host candidate. Current Get-Command and
Codex process metadata instead resolve:
`C:\Users\GameBoy\AppData\Local\OpenAI\Codex\bin\37f54d68e5533a51\codex.exe`.
Passive --version returns0.163.0-alpha.11.2;336134960bytes,
SHA256c81ed464e5e7cafd09a5fa26af390c480bed8e9fab2a87a54b285fbd56e7122a.
Passive --help and offline schema generation were bounded to an isolated,
credential-free temp environment; no app-server/daemon/model session was started.
Eight relevant initialize/thread/turn/dynamic-tool schema files match old pinned
bytes exactly. This removes the need to reinstall solely to recover those Expected
shapes; it does NOT transfer binary identity, settings, isolation or qualification.
Final operational Grant must freshly pin the chosen available binary/config.
--listen is a transport URL; bind unix://PATH to the SAME native AF_UNIX endpoint,
not --listen=<raw-Windows-path>, another transport or a different path.

Owner explicitly accepted the SDK terms and exact limited download/use/offline
build on2026-10-23; control66d18b4d records that decision. This does not authorize
execution of the built artifact or any Host/setup effect. The single task-owned destination
is `C:\Users\GameBoy\AppData\Local\Temp\johnny30-protected-launch-review-20261021\sdk-portable-10.0.26100.8249`;
archives only under downloads/, extracted required x64 import libraries/licenses
under cpp/ and cpp-x64/. Both exact packages below were downloaded once and independently
hash/readback checked. Final18 selected members are16 UM x64 libraries (including
the proven transitive Uuid.Lib), one normal UCRT library and cppwinrt third-party
license; do not confuse that text with the SDK terms Owner accepted by URL.
Root absence/containment and ZIP safety checks preceded extraction; all inputs
are retained. No system Windows Kits or global NuGet Lib target was installed.
Use only process-local LIB/PATH for offline AOT build;
no global SDK install/environment/Registry/account/ACL change. Exact selected
library members are read back from verified archives after explicit consent,
before build; unexpected layout stops, never broadens extraction silently.
Owner=root/Ticket30, TTL24h with active evidence/recovery hold; no automatic deletion
of evidence or policy-denied cleanup. Source-compatible candidate1b7a93c9 passed
independent source review/mutations and own-hold replay; actual Release LinkNative
then PASS22.766s after the retained missing-uuid failure. Exact linked /OUT:
`C:\Users\GameBoy\AppData\Local\Temp\johnny30-native-service-review-20261021\nativeLink-root10\bin\Release\net10.0-windows\win-x64\native\JohnnyAuthority.Tools.exe`,
3958272bytes, SHA2568235b567d48ed7f27da791c20f2a1faf3ee81e876942f6e3a4c914dd625ba7db.
Passive PE AMD64/PE32+/CLR-directory0; NOT the separate obj/apphost.exe. Independent
byte QA confirms40 source/project,17 SDK/49 MSVC inputs and10 outputs. Evidence
seal03884950 contains28 exact original records; full ZIP inspection separately held.
The linked artifact has NOT been executed or installed; source/build PASS is not
Host qualification. Local source/tests continue; actual setup/Host/CVQ unauthorized.

Portable SDK exact input manifest, re-read from NuGet catalog metadata on2026-10-23
(metadata only, NOT archive download or license acceptance):

| Package/version | Bytes | SHA512 (base64) |
| --- | --- | --- |
| Microsoft.Windows.SDK.CPP/10.0.26100.8249 |160432822|`wVnN5KBDtxrTC38ZcpDMUsGeIbkUBjhJ+2BB1AX0E6YwUludqOQUhv9OxiZElyBbLI/EcyRt20ZPj32DLcThrA==`|
| Microsoft.Windows.SDK.CPP.x64/10.0.26100.8249 |52951912|`UOPLPnlH/Q+FX8l26uR87+wWPSoCQU9SwmoJe80FiAcZLp27kGl9H2D6gv2C7B3R1Wmos06MAzgqRKl134/NJg==`|

Official catalog records: `https://api.nuget.org/v3/catalog0/data/2026.05.26.19.56.28/microsoft.windows.sdk.cpp.10.0.26100.8249.json`
and `https://api.nuget.org/v3/catalog0/data/2026.05.26.20.03.22/microsoft.windows.sdk.cpp.x64.10.0.26100.8249.json`.
Both declare requireLicenseAcceptance=true and `https://aka.ms/WinSDKLicenseURL`;
the x64 package requires the exact same-version CPP package. Total213384734bytes.
Archives came only from NuGet flatcontainer exact lowercase package/version URLs,
into the named downloads directory; both lengths/SHA512 were checked before
bounded extraction. This approved operation is task-local library inputs/offline
AOT only, no global installation, service, Registry/ACL, Host/model session or fee.
Do not infer any later OS permission from SDK consent or the local batch. The
build prerequisite is now satisfied; actual installation/configuration, independent
protected observation and real Host/Grant qualifications remain separate.

## Identity-only operation — COMPLETED_ACCOUNT / PROFILE_PENDING

### Static inputs and one-child validation completed; installation NOT_AUTHORIZED

Owner explicitly approved the exact one-child policy difference on2026-10-27;
activation3a224560 binds reviewed runbook12 blobd1032f60 and both full pins.
The ONE RemoteSigned/ValidateOnly child returned0 in2.140s, stderr empty,
all121 hashes unchanged. Output: VALIDATION_ONLY NATIVE_VALIDATION_UNEXECUTED
OS_PREFLIGHT_UNEXECUTED. Permission is consumed, not reusable for installation.
Fresh policy readback after exit remains effectiveRestricted/all five scopes
Undefined. No account/profile/service/task/ACL/Registry/Host/model effect.
The earlier refusal and proposal below are historical evidence, not another
pending request for the same completed child. Next gap is safe protected SYSTEM
staging and its exact installation authority, not more validation retries.

Root prepared exact setup32-sid1006-20261027 under the existing review Temp,
115 payload entries/32704952bytes, same128/64MiB bounds. Existing managed PURE
plan/enrollment validation passes; no NativeAOT or OS operation. Input operation
SHA256bc6ba70d17cb189b0ba0d55fe92651218ea733d35ad374b6f12b734c16c184ff,
scriptSHA25637b8c5e059acaba55212cc5631880133220342a6591000db94f7c39ee12c90aa.
These are offline inputs, not SYSTEM-protected/installation-ready assets.

First actual -File ValidateOnly fails BEFORE loading the script:
SecurityError/UnauthorizedAccess. Read-only Get-ExecutionPolicy confirms
effectiveRestricted and MachinePolicy/UserPolicy/Process/CurrentUser/LocalMachine
allUndefined. Authenticode statusNotSigned. No retry, -Command reinterpretation,
Bypass, policy change or certificate enrollment was attempted.
This blocks actual script validation independently from the remaining profile,
protected SYSTEM staging, service/ACL/Registry setup and real Host qualifications.

Historical policy proposal (later approved for the ONE completed child): permit ONE exact
PowerShell5.1 validation child to use Process-only RemoteSigned, fixed pinned
script/input/root and ModeValidateOnly. No CurrentUser/LocalMachine/GPO policy
change, no Bypass, no Apply/service/Registry/ACL/Host/network/model effect.
The policy setting expires with that child. It permits unsigned LOCAL scripts
inside that child and therefore is a real scope-bound security-setting decision,
not inferred from existing local-test/account authority. If declined, retain
Restricted and the blocked result; approved signing would require a separate
trusted certificate, never an invented self-signed/trust-store workaround.
Do not run the proposed child before Owner explicitly accepts this difference.
After successful exact validation, final SYSTEM stage/installation commands and
their separate effect authority still require review; this is NOT their approval.

Exact approved command (EXECUTED ONCE; retained for audit, DO NOT RERUN):

```powershell
$setupRoot = 'C:\Users\GameBoy\AppData\Local\Temp\johnny30-native-service-review-20261021\setup32-sid1006-20261027'
& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' `
    -NoLogo -NoProfile -NonInteractive -ExecutionPolicy RemoteSigned `
    -File (Join-Path $setupRoot 'Invoke-AuthorityProvisioning.ps1') `
    -Mode ValidateOnly `
    -InputPath (Join-Path $setupRoot 'operation.json') `
    -StagingRoot $setupRoot `
    -ExpectedScriptSha256 '37b8c5e059acaba55212cc5631880133220342a6591000db94f7c39ee12c90aa' `
    -ExpectedInputSha256 'bc6ba70d17cb189b0ba0d55fe92651218ea733d35ad374b6f12b734c16c184ff'
```

Root also rechecks both file hashes before launching, uses the already recorded
credential-free child environment and15s deadline, captures complete raw output,
then checks all121 assets unchanged. No -Mode Apply, RunAs, new interactive prompt
or permanent policy command is included.

The current direct OS readback above supersedes all NOT_CREATED statements in the
historical creation recipe below. The recipe is retained for audit, NOT a command
to rerun now that this exact account exists. Next Root action is binding actual
identity into the existing protected-setup operation inputs, without executing
unapproved service/task/ACL/Registry or Host effects. Source schema determines
which remaining fields require fresh operational observations; never fill them
with fixture IDs or an expired session. The24h account TTL is not extended here.

### Historical approved creation recipe and Description correction

Owner approved the identity-only scope on2026-10-24; exact activation is recorded
in existing Ticket30 review391d5698. This is not broader native/setup/Host authority.
Owner's2026-10-27 screenshot exposes a command defect missed by prior AST/metadata
review: Description67 exceeds the actual New-LocalUser ValidateLength0..48 bound.
Fresh readonly target readback finds account absent; no automatic create retry.
Only Description is shortened to29 characters below; all machine/admin/absence,
password-locality,24h expiry, Users-only verification and stop-on-error rules stay.
Old pinned command/failure remains in Git and review. Return to Owner's existing
elevated console for the corrected block, not a new encoded/UAC launch attempt.
No successful account creation/profile/Host qualification is claimed.

This is the first unavoidable state-dependent OS input, not another engineering
approval. Target is the actual DESKTOP-28ERPQ1 / Windows10Pro19045, NOT the VM.
Current GameBoy controller SID ends1001 and effective token is Medium/not elevated.
JohnnyReadonlyReview does not exist. A real dedicated standard subject is needed
for BOTH30B/43's independent protected review: no controller/orphan/vendor SID reuse.
The exact new SID is assigned by Windows at creation; it cannot be invented in a
final SYSTEM enrollment or InputSha256. Therefore request identity creation only
first; after its readback Root fills that concrete value into the existing setup
manifest. Approval of this operation does NOT approve that later setup manifest.

Exact proposed effect: create ONE local standard account JohnnyReadonlyReview with
a24-hour expiration, add only built-in Users S-1-5-32-545 if not already present,
verify exclusion from built-in Administrators S-1-5-32-544 and return actual SID,
expiry and machine identity. Password is entered locally by Owner as SecureString;
never sent to Agent, logged, supplied on argv or copied from another account.
Owner performs a local interactive sign-in/sign-out only to establish the dedicated
profile; do not open Codex/Claude, add credentials or run the native tool.
Sign-out ENDS that WTS session: it is not reusable token/session/LUID evidence.
Any later launch must acquire and independently validate a fresh authorized active
session/token/LUID at its own effect boundary. Profile creation is not that proof.
No service/task, application file/ACL, Registry, firewall, socket, network rule,
Host/model call, provider credential, formal Grant or paid expansion is included.
Normal OS account/profile creation is the sole approved-if-confirmed persistent
effect. Inactivity/expiry does not authorize deletion of profile/evidence.

Available locally, read-only verified: Microsoft.PowerShell.LocalAccounts1.0.0.0
under System32 WindowsPowerShell v1.0; New-LocalUser/Add-LocalGroupMember/
Get-LocalUser/Get-LocalGroupMember/Disable-LocalUser exist. This availability does
not grant the current unelevated Agent permission. Proposed command runs ONLY in
Owner's64-bit elevated Windows PowerShell5.1, not this Agent's shell:

```powershell
$ErrorActionPreference = 'Stop'
if (-not [Environment]::Is64BitProcess -or $PSVersionTable.PSVersion.Major -ne 5) {
    throw 'Use 64-bit Windows PowerShell 5.1'
}
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Owner elevated terminal required'
}
$machine = (Get-CimInstance Win32_ComputerSystem -ErrorAction Stop).Name
if ($machine -cne 'DESKTOP-28ERPQ1') { throw 'Wrong target computer' }
Import-Module "$env:SystemRoot\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.LocalAccounts\1.0.0.0\Microsoft.PowerShell.LocalAccounts.psd1" -ErrorAction Stop
$existingSubjects = @(Get-LocalUser -ErrorAction Stop)
if (@($existingSubjects | Where-Object { $_.Name -ieq 'JohnnyReadonlyReview' }).Count) {
    throw 'Account already exists; do not adopt or overwrite'
}
$subjectPassword = Read-Host 'Owner-only password for JohnnyReadonlyReview' -AsSecureString
$subjectExpiry = (Get-Date).AddHours(24)
$createdSubject = New-LocalUser -Name 'JohnnyReadonlyReview' -Password $subjectPassword -AccountExpires $subjectExpiry -Description 'Johnny review subject; TTL24h'
$subjectPassword.Dispose()
$subjectSid = $createdSubject.SID
$subjectReadback = Get-LocalUser -SID $subjectSid -ErrorAction Stop
if ($subjectReadback.Name -cne 'JohnnyReadonlyReview') { throw 'RECOVERY_REQUIRED: identity mismatch' }
$usersSid = [Security.Principal.SecurityIdentifier]::new('S-1-5-32-545')
$adminsSid = [Security.Principal.SecurityIdentifier]::new('S-1-5-32-544')
if (-not @(Get-LocalGroupMember -SID $usersSid -ErrorAction Stop | Where-Object { $_.SID -eq $subjectSid }).Count) {
    Add-LocalGroupMember -SID $usersSid -Member $subjectReadback -ErrorAction Stop
}
$actualSubjectGroups = @(
    foreach ($localGroup in @(Get-LocalGroup -ErrorAction Stop)) {
        $members = @(Get-LocalGroupMember -SID $localGroup.SID -ErrorAction Stop)
        if (@($members | Where-Object { $_.SID -eq $subjectSid }).Count) {
            $localGroup.SID.Value
        }
    }
)
if ($actualSubjectGroups.Count -ne 1 -or $actualSubjectGroups[0] -cne $usersSid.Value) {
    throw 'RECOVERY_REQUIRED: membership is not exactly local Users; stop'
}
Get-LocalUser -SID $subjectSid | Select-Object Name,SID,Enabled,AccountExpires
[pscustomobject]@{ Computer = $machine; LocalGroupSids = $actualSubjectGroups; AdministratorMember = ($actualSubjectGroups -contains $adminsSid.Value) }
```

If a command fails, stop with its original error; do not rerun account creation,
change host policy, delete account/profile or automatically modify other groups.
Partial state is RECOVERY_REQUIRED, preserved for readback. Rollback is limited to
Disable-LocalUser -SID <the exact returned new SID>, after Get-LocalUser confirms
that SAME name/SID and after Owner authorizes this exact operation; no Remove-*,
password reset, ACL reset or cleanup. Normal24h expiry prevents future sign-in,
not deletion. Account owner Root/Ticket30, TTL24h and evidence/recovery hold.

Proposed exact Owner reply: "Authorize identity-only operation on DESKTOP-28ERPQ1:
create JohnnyReadonlyReview as a standard Users-only local account expiring24h,
with password entered only by me; read back its real SID and establish only a local
profile. Any later active session/token/LUID requires fresh authorized readback.
No service/task/ACL/Registry/Host/model effects.
Allow disabling only this exact newly created SID as rollback; preserve evidence."

After identity readback, the existing minimum path is:

| Step | Existing blocker removed | Required actual result / authority |
| --- | --- | --- |
| Dedicated SID/profile | BOTH30B/43 lack independent OS subject | exact actual SID and full local group readback/profile only; identity-only confirmation above; later active token/session/LUID separately fresh |
| Existing protected setup | BOTH lack protected issuer/observer/runtime | exact pinned SYSTEM task/input, SCM disabled, files/DACL and enrollment readback; separate final operation confirmation, NOT source PASS |
| Existing first-entry CVQ | BOTH lack qualified independent review entry | five readonly prohibitions + unknown bypass reject, trusted observer and finite verified model/account cost; exact Host-test authorization still required |
| Existing Grant source positive + candidate reviews |30B R1 and30B/43 qualified audit | real issuer readback/atomic single consume/legal success plus forged/replay rejection; qualified review separately pins each candidate |
| Existing dispatch/closure | checklist01/02/05/06/07/12 remain open | actual entry/effect/source/receipt evidence and necessary regression, never all-deny or fixture completion |

No new stage, reviewer, framework or policy is introduced by this table. The full
later setup cannot truthfully freeze real-SID input hashes now. It also must solve
shared Host-image readability/socket-root ACLs without weakening existing fixed
authority payload128/64MiB bounds. Current CLI is336MB and must NOT be smuggled
into that payload. No service start before its worker/Host effect Grant.
Token/cost fields remain metadata, not a provider-spend cap: before any model call
Root must verify an existing account-level hard limit/no-new-fee arrangement or
report UNAVAILABLE. Subscription use or one client turn alone is not that proof.
Formal main source still needs fresh same-SHA remote index/leaves after separately
authorized publication; no local origin/main substitution. These limits are visible
now, not deferred until after more source tickets.

## Effective Owner amendment — batch-checklist-local-20261019-uncapped

The Owner's latest explicit decision replaces cumulative command-second and fixed
initial/correction-count limits for completing the original12 local improvement items,
including30B/30G and retained B3F01. The historical599.2,900/1500,350/220/330,
reservations, failed attempts and UNRECONCILED intervals remain historical evidence,
not active admission ceilings, fresh zeroed balances or reasons for human renewal.
The later proposed added500/2000 package is SUPERSEDED_NOT_ADOPTED; do not request it.

This is an execution-policy amendment, not a new PRD or grant issuer. Root derives
exact child scope/role/baseline/worktree/acceptance bindings under the existing batch;
the implementation owner never approves its own work. Existing spec, source trust,
Grant authentication, isolation qualification, protected effects, Review and CI remain.
The first-entry CVQ exception retains its exact original scope and provisional nature.
Do not remove limits from runtime contracts or separately authorized operational
attempts, platform quotas, tool policies or provider spending. No paid expansion.

Default local command deadline60s, compiler/test child deadline55s, one foreground
command per seat. A known workload may receive a different finite bound after root
diagnosis and a recorded reason, not a blanket timeout increase. Continue timing
start-to-terminal executions and monitoring owned process/resources. A repeated
identical failure without new evidence stops unchanged retries; root-cause analysis
or an evidence-backed different repair replaces them. No unlimited wait or blind loop.

Current source sequence: bind/review this amendment; repair retained B3 schema-call
identity with baseline-red and legal positives; finish its ordinary engineering
review and immutable staging (not qualification); N2 native job lifecycle; protected
enrollment/transport/configuration tools; minimal readonly adapter and independently
owned observer preparation. Freeze each exact path/contract before its source effect.
Actual installation, accounts/SIDs/ACL/service/network changes, ongoing privileges,
real Host campaigns/model costs and other unauthorized external effects still need
one concrete manifest/decision at their boundary. No push/release/deploy/activation,
denied-cleanup retry or changes to R0/DAP/TAL/Recovery. No checklist checkmark is added
by this policy change. Original later sections are provenance where they conflict.
Baseline10b06f82c0825d6339d12712f0b2f752114c8790; assessment2026-10-19.
Independent ordinary architecture/docs review: /root/batch_authority_review,
APPROVED_AS_PROPOSAL for b77fc961f99e51b6cb0dad74a8e2b5646a1e4559 / leafblob
a9786cb7e8b1e8aa2eda1c74742c3e0596a8ac7e. Revision01's circular bootstrap finding
was corrected in that revision02; no operational qualification, source-code audit
substitution, implementation Grant or Owner approval is conferred by this review.

## Owner decision and Change Control activation — 2026-10-19

Owner approved revision02's ONE-TIME first-entry ordering exception only for B3 F01,
CVQ-01 and the fixed candidate's minimal readonly entry. This is recorded under
the existing CVQ Change Control and original requirement lineages, not a new PRD.
All five readonly restrictions, independent OS protection/observation, independent
audit and final original CVQ admission remain. Provisional results cannot satisfy
30B/43 qualification. This approval does NOT execute or authorize a Host test.

Owner separately authorized30G-SOURCE after original Ticket30 revision/independent
review: exact six CREATE paths in section5, zero effective MODIFY/DELETE, added900
command seconds author450/reviewer300/control150, <=60s each, initial plus one
correction. Original599.2/600 is retained; combined ceiling1500. Root derives the
exact child Grant under the existing batch; no repeated per-ticket Owner approval.
Root control allocation includes bounded install-inventory helper work; its time
is not a free extra allocation. Native service, OS/user/ACL changes, real pipe/
network/Host/session effects and code outside the six paths remain unauthorized.

The section5 proposed reply is historical and broader than this actual approval:
no permission-setting or installation authority is inferred from it. Prepare an
exact account/SID, service, protected files/DACL, binary/config, pipe/network,
commands, verification and rollback manifest first; ask once at the actual external
change boundary. Missing actual identities/digests stay NOT_CREATED/NOT_BUILT,
never invented. No push/release/deployment, policy-denied cleanup retry or early
qualification/30B/43 completion. Subsequent sections retain the reviewed technical
design; this section alone records which proposed authorities are now effective.

## 1. Determination from current evidence

### Subsequent Owner-approved local continuation / budget redistribution

Owner approved continued local source/compilation/tests of the native tooling and
approved the SAME900 redistribution author350/reviewer220/control330. Original
599.2 and1500 total persist, no zeroing. Existing30G161/84 and all Root history,
including interrupted forensic read and unreconciled timing, remain; Root reserves
200 for old control history, not a false measured total. Native tools first slice
is original Ticket30N1 with exact nine CREATE scope after document preflight.
This updates the earlier six-file-only construction limit through new exact child
Grant, not direct expansion of30G or a blank installation permission. Windows tools
are platform shims, Python backend stays unchanged; no new package/runtime install.
Actual services/users/DACL/firewall/Host sessions still await the completed reviewed
operation manifest and separate exact consent. Source planning/readback outputs
cannot approve authority or qualification; original CVQ exception limitations remain.

Forecast (planning, not measured): N1 build/verification within author120/reviewer80/
control40 subsets; preserve20 author correction inside120 and old30G correction30.
Later native Host guard/protected observer source is estimated additional author60–100,
reviewer40–70/control20–40 depending N1 actual usage; reassess before admission against
the SAME remaining350/220/330, never create a fresh allowance. Operational qualification
and bounded live semantic audit remain unallocated/unexecuted, not hidden in source
budget. If remaining local caps cannot fit the next closed slice, prepare the exact
residual plus actual usage once; do not exhaust caps via large-log recovery scans.

### Consolidated remaining source decision — proposal, NOT_GRANTED

The following supersedes the stale statement later in section3 that F01 has not
returned: candidate2e889401 already contains that repair. Current original CVQ
control is55b9a91c; independent ordinary engineering review under the approved order
exception is recorded at75d165b5e3b9e4e26b8b36af240d218b06447f4f, B3document12 /
review16. No source integration or qualified audit is inferred. Root strict21 passes;
20 named owner-wiring reversals and three extra doors go red/restored green, and
actual-package renamed forbidden import rejects/restores. These are not a complete
final campaign. Peer and Root find a retained F01 defect: a typed module function
named Field is accepted as a schema constructor in the REAL PositiveInteger alias.
The packet is never executed. The old one-attempt/no-correction limit is consumed;
no automatic redispatch or another correction was performed.

N1 final engineering source remains0a2e0661, nine CREATE, independent4tests and actual
getter source mutation red/restored green; source20bd6e30 remains six CREATE/92tests.
Both remain qualified-audit-blocked and unintegrated. N2's original exact scope and
doc preflight4e47c042 are ready, but underfunded: author293.77 used plus old30G
correction reserve30 leaves26.23 of350, below N2's planned45. Reviewer now183.407/220
(old84 + N1 94.523 + B3 peer4.884), leaving36.593. Root330 is conservatively reserved
in full for old UNRECONCILED history200 plus bounded N1/N2/inventory/B3 preparation
and final record work, NOT represented as330 measured seconds. Original599.2/600,
all failed calls, deviations, command outputs and total1500 ceiling are retained.
This is real per-role resource admission, not platform quota exhaustion.

Minimum remaining source pack, engineering estimates NOT measured results:

| Existing responsibility / ordered slice | Source paths to freeze in derived child Grant | Author / independent reviewer / control command seconds |
| --- | --- | --- |
| Retained B3 F01 schema-origin correction | MODIFY only existing source_gate and boundary driver at2e889401; use existing binding resolver, no new schema engine | 25 / 20 / 10 |
| N2 owned native job lifecycle | Existing Ticket30N2 three CREATE / three MODIFY, exact N1 baseline; constructor-first then owned fixture limits and observed teardown | 45 / 32 / 22 |
| Protected issuer enrollment/transport and setup tooling | Existing section2 windows_service.py responsibility; native_windows service/pipe/enrollment shim and existing tooling wiring, shared ledger/client; exact files/typed contracts frozen before dispatch, not a new service framework | 100 / 60 / 35 |
| Minimal readonly Host adapter/observer source | Existing section3 readonly_review_host.py, tests/staging/readonly_host_protocol.py, test_readonly_review_host.py; reuse current process lifecycle/CVQ contracts, no second Runner | 60 / 45 / 25 |
| Total planned envelopes | Same Ticket30/CVQ lineages, first-entry exception boundaries intact | 230 / 157 / 92 |

These envelopes include each slice's inspections, constructor preflight, affected
tests, required author/reviewer distinct-door mutations, commits and bounded correction;
control includes exact ticket/allowlist/Grant/record readback. One initial plus one
correction only, <=60 seconds per command, <=55 child-test timeout, serial per seat,
zero automatic retry/load. Do not use this forecast as authority to open undeclared
paths or silently raise a failed slice's limit. No full repo or unchanged campaign rerun.

Recommended ONE resource decision: add500 command seconds, allocated author245 /
reviewer155 / control100. Parent ceiling1500 becomes2000; role ceilings350/220/330
become595/375/430. Old usage and reservations stay charged; available source envelopes
then author271.23 after correction reserve, reviewer191.593, control100, sufficient
for planned230/157/92 plus bounded variance. This is source/test/document work only,
no paid provider/real Host call, service install, account/ACL/firewall change, real
IPC session or source qualification. It does not promise twelve-item completion
without later real-source/Host/publication-dependent evidence.

The only additional attempt decision is to reopen retained B3 F01 schema-callee
identity once, within the SAME closure/paths/baseline/remaining lineage, initial plus
one correction maximum, with all historical failures/use kept. No reopening F02/F03/F04,
new PRD, weaker grammar, qualification standard or automatic third correction.
Normal DTO/module/command details remain Root/Architecture Owner responsibility.

Direct precise reply candidate:

> 核准原runbook的限縮source-only續行包：原Ticket30／CVQ lineage追加500命令秒，
> 分作者245、獨審155、控制100；總上限2000，角色595／375／430，保留全部舊帳與reserve。
> 核准B3於2e889401就F01 schema callable identity追加一次有界修正窗口，僅原gate／driver，
> 初次加一次修正，保留原Closure與所有Finding／歷史耗用。其餘依原批次自行凍結精確子票／
> Grant與獨審。不得新增權限、費用、Host效應或降低安全要求；不授權安裝、帳戶／ACL／
> 服務／網路變更、正式CVQ測試、push、release、deployment或啟用正式閘門。

After that decision: B3 discriminating red/repair/green/peer review; N2 bounded native
fixture lifecycle; protected enrollment/transport setup source; readonly adapter/
observer source; independent ordinary engineering sealing at each exact candidate.
Then present ONE actually executable installation/permission manifest using built
payload hashes, exact SIDs/paths/rights/commands/rollback, and separately bounded
qualification/model costs. No guessed payload digest or blank security consent now.
Final OS protection/independent observation and original CVQ admission remain mandatory;
only qualified results may subsequently discharge30G/30B/43 holds. Protected issuer
positive acceptance remains distinct from public all-reject containment.

No lower-cost unblocked source slice is silently abandoned: existing45/46/31B/44
local content/report/history/command-source slices are complete with evidence;04
is complete and not rerun. Remaining item-specific dependencies are the existing
checklist matrix, not a new requirement:01/02/03 need trusted readback/effect wiring;
05 real loaded-source observation;06 prewrite effect interception;07/09 qualified43
review and real evidence source;08 actual CI consumer/retirement proof;10 egress/
credential isolation;11 trusted one-shot creation/activation;12 their combined replay.
Where the observed remote main lacks new local documents, no push is authorized and
no local origin/main substitutes for it. These external-dependent checks stay open.

Historical inventory from the earlier source assessment, not current installation
or authority. Current version/input readback above supersedes these dated findings;
later reviewed source checkpoints in original Ticket30 supersede implementation gaps.

| Subject | Historically observed / verified | What then remained to be built or proved |
| --- | --- | --- |
| Grant | dispatch_authority.py documents owner-intent marker; no protected issuer implementation in scoped local_orchestration/workflow_router | Protected Owner approval, authoritative plan store, authenticated direct readback, one-shot consume and owned read transport |
| Windows | NTFS; current process AdministratorEnabled=False (not proof of a separate standard account); CodexSandboxService.OpenAI.Codex running asLocalSystem | That vendor service is not a Johnny issuer; no modification/reuse as one. New trust separation must be enrolled and tested |
| Codex CLI | Historical0.163.0-alpha.10.2; SHA256F6DBF48CB70F62649C645F26C87DC9BF84CC36986202DFAD8E12FB5B8CA70312; original path now absent, superseded by current-input readback above | Actual closed roster, permitted snapshot read and before-effect denial still unqualified; this CLI never qualifies Desktop |
| Claude CLI | Installed2.1.231; --tools, --strict-mcp-config, --setting-sources, --no-session-persistence and --max-budget-usd exposed | All-tools-off cannot meet CVQ's permitted-read positive. A dollar flag alone does not prove token/request/retry limits; prior offline UNAVAILABLE is retained |
| CVQ | Approved SPEC09 / wire05 at13fc7a760cb274d6927af0ab108b1cb09037127d, blobs089649eb7751c059815d0bc62bad9e2eb38df515 / cc04eb9dc97680b1e11285b677c4aba5b858a49e; current CVQ control55b9a91c7dc26367deb2fd4d0b9a2b75dae87ed3 retains those SPEC blobs | controlled_verification is absent from integrated checklist tree. B3 newer repair2e88940138cbb1e1f8a81465ca5337db105050e7 already returned; document10/section14 and review15/section19 (ticketblobfb7e19195697b03c7e040b2588a811dff602a744) supersede the stale27bb pointer. No reimplementation: remaining strict/final campaign/qualified audit evidence stays OPEN; engineering staging alone is not acceptance |

Historical read commands: exact CLI --version/--help, app-server --help and
generate-json-schema --help (did not generate files), features list; Claude
--version/--help; Get-CimInstance Win32_Service, sc.exe sdshow for the named vendor
service, current WindowsPrincipal.IsInRole and Get-Volume C; scoped Git/source
symbol inventory. No Host session, model request, native attack, service change,
credential inspection, ACL mutation or rejected cleanup retry was executed.

## 2. Minimal trusted Grant implementation

Recommendation: implement the existing HostExternalEffectGateway responsibility
as one protected local authority service. First scope is READ_MAINLINE and
READ_REVIEW_SNAPSHOT only. No PRD creation, Git write, shell, Agent spawn or generic
command endpoint. Do not build the full remote-write gateway first.

Owner approves the exact batch/plan through a separately protected approval entry.
The issuer runs under a service identity independent of every Agent; its code,
dependencies, policy and SQLite database reside outside user/plugin/cache write
access. Installer must set protected ownership/DACLs, not same-user DPAPI or an
ordinary writable config. UAC consent/same username alone does not prove an
independent principal. Host enrollment must establish a standard/restricted
subject and an authenticated role/session mapping; if that cannot be proved,
no grant is issued. Owner enters any admin credentials only in the OS UI.

The protected entry displays the canonical project, operation, source ref,
ticket/revision, baseline, role, validity and complete plan digest. Only after
the Owner accepts that exact plan does the service store its approval. Within
the approved batch, child records are derived by the service's checked scope,
not by trusting an Agent's authority_ref or claimed role.

Clients send only an opaque grant/operation reference. Named-pipe peer identity
is obtained from the OS and joined to protected enrollment; both ends verify
the actual peer/service identity, protected binary/config and instance. Pipe
name, PID alone, caller JSON and repo files confer no trust. Unknown session,
same-user role forgery, pipe spoofing or protection drift refuses.

Inside ONE SQLite write transaction, match exact plan/bindings/expiry and
conditionally transition the unconsumed grant, persisting a unique attempt and
correlation before any operation. Exactly one competing consumer wins. Commit
the consumed/attempt-intent record before the service invokes its fixed reader.
The service owns canonical transport and fresh readback; a client-side bool or
forged DTO cannot enable an effect. No os.replace/unlink check-then-act substitute.
SQLite atomicity does not prove protection or atomic distributed Git effects.

On retry, same correlation + same plan returns the recorded result or in-progress/
RECOVERY_REQUIRED state, never a second effect. A timeout/crash with uncertain
outcome remains held; no auto-remint, deletion or silent attempt reset.
Return only authenticated metadata/projection, never grant material/credentials.

Exact proposed source boundary (not an active implementation Grant):
- create library/local_orchestration/grant_authority/{__init__,contracts,ledger,windows_service,client}.py
- create tests/{test_grant_authority_ledger,test_grant_authority_protocol}.py
- modify30B candidate library/local_orchestration/mainline_readback.py and tests/test_mainline_readback.py only for real authority-service wiring
- separate provisioning edge: create install-authority.ps1; proposed only, no execution or installer/MSIX expansion in this batch

contracts owns strict plan/ref/result meaning; ledger owns durable CAS/idempotency;
windows_service owns protected IPC/peer/enrollment and fixed read operations;
client owns actual service readback; mainline_readback retains its existing
snapshot algorithm. No module becomes a second Router or generic executor.
Reuse ProjectId/RevisionDigest/EvidenceDigest, ProjectAuthorityContract and
existing mainline parsing/observation. Existing telemetry locks/receipts are not
trusted grant stores. Implementation must not import source from an unreviewed
candidate as authority; reviewed baseline/controlled integration remain required.

Acceptance: real valid issuer record succeeds with exact bindings; grant-forged,
plausible ID, wrong project/ticket/role/baseline/ref/expiry, replay, swapped server,
same-user file replacement and inaccessible issuer all refuse. Two concurrent
clients have one winner; crash at each transaction/effect boundary cannot
reconsume. Qualified native tests must prove runtime cannot read/modify issuer
material, code, policy or evidence. Local SQLite tests prove only ledger behavior.

Full30B success also needs the declared remote source: fresh main is
a1cb6c13adbeb52a4117991727dcc3d4af6d2a33. Its feature README blob
373d3e756bd965c8b5fb1f6b4862cf8f78a39395 was read through GitHub contents and
matched local immutable Git bytes; no mainline-index block exists there.
Even a valid Grant must refuse missing published inputs. Publishing exact final
source documents is a later separately scoped effect, not part of this request.

## 3. Minimal qualified readonly review entry

Recommendation: native Codex CLI is the first candidate surface; use the existing
CVQ READ_ONLY_HOST method, three Ports, Manifest/Case/Observation/Report and
seven-category roster. Reuse tests/staging/process_runner and environment_core
for bounded fixture lifecycle only; neither is already a protected observer or
native isolation proof. Claude and Desktop need their own later qualifications.

Freeze one candidate source snapshot and its exact paths/digests. Expose one
permitted read_snapshot_blob operation with opaque file IDs, bounded bytes and
exact grant/snapshot membership. No arbitrary path, environment, command, write,
mutation or delegation operation. Protect snapshot/config/observer from the
subject. The read must actually occur through native dispatch and return the
expected bytes; tools=[] or seven ABSENT categories cannot qualify it.

Use a dedicated per-run CLI configuration, not the current full-access session:
readonly sandbox, approvals never, shell/apps/plugins/multi-agent/browser/computer
and permission-elevation routes disabled where the exact binary supports them.
Preserve real native dispatch/extension/client-control paths in discovery; missing
or still reachable execution/mutation paths produce UNAVAILABLE. No prompt claim,
tool-list-only verdict or wrapper hiding an untested alternate entry is accepted.

First operational probe is OFFLINE_DETERMINISTIC: a finite loopback Responses
protocol fixture emits the pinned permitted/forbidden tool requests to the REAL
CLI. Only the stimulus is synthetic; native dispatch, denial and observer are
actual. The fixture is not an LLM/provider and cannot produce a PASS itself.
Explicit local provider, no production auth/fallback, request/stream retry=0,
bounded request/body/output/process/time/log sizes. Availability of this wire
path must be checked in one finite attempt; no current claim it works.
No generic mock-server framework exists in the searched runtime/tests; the old
codex_protocol fixture emulates plugin commands and is not this Responses peer.
One bounded protocol adapter is necessary, not another test runner/Policy Engine.

Proposed adapter scope after CVQ source prerequisites pass:
- create library/local_orchestration/readonly_review_host.py (native config/transport/observation mapping only)
- create tests/staging/readonly_host_protocol.py (finite stimulus peer, lifecycle through existing process runner)
- create tests/test_readonly_review_host.py (shared parameterized positive/denial cases)
- existing CVQ contract/admission/report modules are amended ONLY in their existing branch/Grant, never recopied into control

Prerequisites follow SPEC13.2: APPROVED_SOURCE, IMMUTABLE_SNAPSHOT, ATTEMPT_CLAIM,
HOST_SESSION_POLICY, HOST_SESSION_OBSERVER, HOST_SESSION_BOUNDS; property additionally
uses qualified discovery. Their final meaning and final qualification order remain.
CVQ13.5 also requires qualified independent source Review, while integrated control
has no CVQ implementation and B3 F01 remains open. Requiring that final verdict before
building its first review entry is a real bootstrap cycle, not missing Owner data.

### One-time bootstrap method-order amendment — ORDER_APPROVED / HOST_TEST_NOT_AUTHORIZED

The new policy difference is limited to first-entry source/qualification ordering,
scoped to the retained B3 F01 and CVQ-01 candidates plus the exact minimal readonly
adapter/observer needed for that first entry. It does not apply to30B/43 review or
other candidates. Exact source paths, commits and one-attempt operational bounds
must be frozen in the existing CVQ Manifest before use; no blanket future exemption.

1. Ordinary independent engineering source review, existing strict source gate,
   strict types and named reverse mutations may stage exact immutable candidates.
   This staging is NOT APPROVED_SOURCE, QUALIFIED, AVAILABLE, integrated source or
   permission to review30B/43. Reviewers cannot approve their own implementation.
2. Separately enroll the OS-protected policy, immutable snapshot, observer and finite
   bounds. A trusted control principal obtains independent raw OS readback of peer
   identity, access restrictions and evidence ownership before any subject request.
   The candidate evaluator, subject output and service self-description prove none
   of these prerequisites. If independent protection/observation cannot be proved,
   launch zero requests and return UNAVAILABLE; no weaker tool/prompt fallback.
3. With an exact operational Grant, perform ONE provisional offline native-dispatch
   campaign against the staged candidate. Record the same fixed CVQ cases and raw
   observations, but do not call ordinary admission with fabricated APPROVED_SOURCE,
   emit an accepted qualification, or let the candidate report approve its evaluator.
   All five readonly restrictions must hold before effects; this exception changes
   source approval order, not protection, observation or attack safety.
4. An independent reviewer adjudicates the protected raw observations and reviews
   the exact source under the demonstrated restricted profile. If isolation or any
   required attack is unproved, stop UNAVAILABLE; no source integration or dependent
   review. A separately qualified external reviewer is a fallback only if actually
   available, not an environment the Owner is required to invent.
5. Only after that independent source audit passes may controlled source integration
   occur. Run the final existing CVQ admission/report against that integrated source
   and all six genuine prerequisites, exact final binary/config/snapshot and discovery.
   Provisional reports cannot satisfy downstream CapabilityKey/evidence lookups.
   Only a successful final qualification can admit the later30B/43 readonly audit.

The Owner Change Control decision above now approves this method-order exception;
neither ordinary source review nor a new service can expand it or grant Host tests.
It creates no new Stage/Agent/Gate/Report system. Reuse CVQ cases and evidence refs,
keeping provisional evidence non-authoritative until the final ordinary evaluation.
The same recipe can serve another Host only after its own exact binding/proof; CLI
and Desktop never inherit each other's verdicts. Historical candidates/budgets and
Recovery remain unchanged. No automatic third correction or qualification retry.

Qualification cases: allowed snapshot read; denied out-of-source read/traversal/
reparse; denied file edit/write; shell/interpreter/JS execution; Agent/MCP aliases/
client continuation/delegation; unknown tool/method; config/binary/snapshot swap;
missing/forged/subject-owned observations; timeout/output overflow/cancel/retry.
For each attack require actual dispatcher receipt, pre-effect deny and unchanged
canary/readback. Refused before launch has no invented PID. Failure stays FAILED/
UNAVAILABLE/RECOVERY_REQUIRED under existing report reduction. No cleanup retry.

Only after qualification may this exact CLI/profile review30B/43. Actual semantic
AI review is LIVE_BOUNDED and requires a separately bound existing account/model,
token/request/output/cost envelope and native/protected enforcement. Claude's
budget flag alone cannot meet that. No live model calls or new charges requested
by this offline-first plan; no credential is needed for the local stimulus peer.

## 4. Test-command source and independent local continuation

At10b06f82, git ls-files/tree for .github, GitLab/Azure/Jenkins, Makefile,
pyproject/tox/nox/pytest.ini/setup.cfg and tools/scripts found no tracked entry.
Historical runbook handover-2026-08-22-plugin-distribution.md blob
f48b996a15c112966084540cba8353461c0ac833 records local full-suite pytest;
requirements-dev.txt blob98b5f2b3fa38a4f800487d510d8bf6ceb4431409 pins dev tools.
Neither proves a current test CI job.

GitHub Actions GET succeeded: one active Dependency Graph workflow339484080,
dynamic/dependabot/update-graph; latest run32693024347 has only dependency-graph
steps. GET .github/workflows at exact fresh main returned404 while the same
credentials successfully read feature README at that SHA. Therefore that directory
is absent in the checked main tree; this is not an authentication/readability
failure and does not exclude organization/external CI. No such source was provided
or identified. Do not declare globally 'no CI'.

Ticket46 is already admitted under the local batch: establish one new
tests/verification-commands.json with only LOCAL_VERIFICATION_ONLY content and
inventory suites, then read it and sources at the same pinned SHA/digest through
existing GitTestDependencySourceAdapter. It executes nothing, grants no test
retirement and claims no full CI coverage. This work needs no new external input.
Future CI/Runner can consume that single source after their own wiring/suite
selection; do not require the Owner to invent or supply a finished manifest.

Exact bounded local readback commands (executed, not a reconstructed CI job):
```powershell
git ls-tree -r --name-only 10b06f82c0825d6339d12712f0b2f752114c8790 -- .github .gitlab-ci.yml azure-pipelines.yml Jenkinsfile Makefile pyproject.toml tox.ini noxfile.py pytest.ini setup.cfg tools scripts
git ls-tree 10b06f82c0825d6339d12712f0b2f752114c8790 doc/runbooks/handover-2026-08-22-plugin-distribution.md requirements-dev.txt
```
First returned no entries; second returned the two blob IDs above. Successful
remote commands this round were `git ls-remote origin refs/heads/main`,
`gh api repos/johnnyliu365-sys/Johnny_AI_Skill/actions/workflows`,
`gh api 'repos/johnnyliu365-sys/Johnny_AI_Skill/actions/runs?per_page=5'`, and
`gh api 'repos/johnnyliu365-sys/Johnny_AI_Skill/contents/.github/workflows?ref=a1cb6c13adbeb52a4117991727dcc3d4af6d2a33' --include`
(the last call completed with HTTP404, not a successful content read). Feature
README at that same SHA was readable and matched blob373d3e75. Earlier exact
job-step readback remains in Ticket30 review/checklist; no job log or secret fetched.
The scoped conclusion is **test CI definition not established in these checked
sources**, not globally absent and not access-denied. An unknown external CI remains
UNKNOWN; it does not block establishing the independent local command source.

## 5. Cost, source slice and original proposed decision package

The original proposal below is preserved as design/cost provenance. Current approved
ordering/source scope and excluded OS/Host effects are exactly the Owner-decision
section above. Do not re-ask its approved order/budget or execute its broader reply.

Estimates below are engineering planning ranges, NOT measured duration/token cost:
local grant contracts/ledger/client 1–2 engineer-days; protected Windows enrollment/
IPC/evidence 2–4; readonly protocol/adapter/qualification 2–4, plus existing CVQ/B3
source convergence. Native/runtime differences can produce an honest unavailable
result. Local source tests require no vendor fees. Maintenance: service/runtime
and CLI upgrades invalidate their exact protection/tool qualification; rerun the
affected finite cases, not every ticket. No per-ticket service installation.

Next30B slice is30G-SOURCE, a phase in the original Ticket30 lineage, not a new PRD
or replenishment ticket. Before dispatch Root must revise that same ticket boundary,
independently review it and derive a scoped batch child Grant, pinning the final
baseline/leaf/roles/worktree. Exact proposed create paths are
grant_authority/__init__.py, contracts.py, ledger.py and client.py under
library/local_orchestration/, plus tests/test_grant_authority_ledger.py and
tests/test_grant_authority_protocol.py. Modify/delete=none. The source client owns
strict authenticated-readback/peer-verification interfaces and bounded IPC framing;
pure protocol tests do not claim a real authenticated peer. windows_service.py,
install-authority.ps1, OS enrollment and the held mainline_readback.py are excluded
from this source slice, not smuggled in as incidental wiring. Real service/client
wiring and R1 positive proof follow only reviewed native implementation and its
operational authority; source-ledger PASS is not R1 or reject-all completion.

Proposed additional900 command seconds: author450/reviewer300/
Root150, each command<=60s, initial+one correction, no stress/hidden retry. Includes
strict checks, issuer binding positives/negatives, durable one-winner/retry cases,
framing/peer-validation failures and independent mutations. Reuse the existing
140-case algorithm evidence; no held candidate replay/integration in this slice.
Rationale: durable ledger and client/source contracts plus IPC comparison/readback,
conservative compile/import/mypy and finite failure reserve; actual usage recorded.
Original599.2/600 stays charged; approved ceiling would become1500, no platform
quota shortage is alleged. Operational Host attempts get their own later exact
manifest, not silently funded from these900s. Ticket46 has its own already-admitted
300s new local command-source allocation; it does not replenish30B.

Engineering choice: select local protected authority + native readonly Host route.
Owner's one consolidated decision NOW is whether to adopt this first-entry
method-order exception, permit the specified external trust-boundary enrollment,
and approve the attached30B source-budget delta. These are three explicit authority
differences in one package, not ordinary technical choices or a claimed existing
permission. We build/package the service,
configuration, fixture and verification recipe; Owner supplies OS consent/access,
not a finished issuer or Host product. Installation waits for reviewed source and
an exact executable/config/identity/rollback manifest; no blanket elevated command.

Alternative if this PC cannot host that boundary: deploy the SAME limited authority
API to a separately administered Windows host and use its authenticated transport.
This requires machine/admin/network access and protected deployment; it does not
assume an existing working service or ask Owner to implement one. Extra transport/
operations cost makes it the second choice. Neither option weakens the invariants.

Proposed precise reply: “核准本方案revision02的首次CVQ方法順序例外：限既有B3 F01、
CVQ-01及首次唯讀入口的精確必要來源，先獨立工程審閱與不可變候選封存，再取得
獨立OS保護/觀察證據，依精確manifest執行一次零外部模型費用的暫定原生驗證；
暫定結果不構成資格、來源核准或30B/43准入。仍須受限獨審、受控整合與具全部
真實前提的最終CVQ通過，才可供下游使用。准許精確安裝/資格manifest備妥後的
本機服務身分、受限主體、保護目錄與IPC設定；不允許自證保護或降低五項隔離
不變量。30B保留599.2秒原帳，僅30G-SOURCE六個create路徑追加900命令秒，
總上限1500；後續native操作另釘精確資源限制，不得挪用此額度。不授權真模型
新費用、push、發布、部署到其他專案、舊殘留刪除或未驗證正式閘門啟用。”

This candidate reply is not an active Grant. If declined, independently admitted
local work continues; the exact external effects wait. R0/DAP/TAL/Recovery and
30B/43 holds remain. Existing CVQ approval is not asked again.

## 6. Precise installation/settings preparation — NOT_AUTHORIZED / NOT_READY_TO_EXECUTE

### Source-matched operation errata — 2026-10-23, not permission to execute

The older templates below are HISTORICAL_NON_EXECUTABLE where they conflict with
this paragraph. Root and a different-seat readonly inventory checked engineering
hold fb8142793eb98bbd54f90154ac1e63c7fd5741d3, not an installed binary.
native_windows/Program.cs:32–42 accepts exactly one verb; service argv is
`JohnnyAuthority.Tools.exe service`, never `--config`. Bootstrap's fixed manifest
requires `%ProgramFiles%\JohnnyGrantAuthority\JohnnyAuthority.Tools.exe`,
`%ProgramData%\JohnnyGrantAuthority`, version1.0.0.0. Its service identity check
requires a LocalSystem primary token with the enabled expected service SID;
the historical virtual-account proposal is NOT compatible with that source.

The future SCM preparation therefore uses the exact quoted EXE plus `service`,
`obj= LocalSystem`, `type= own`, initially `start= disabled`, followed by explicit
service-SID configuration/readback. Exact SCM SDDL must come from the reviewed
ProtectionPlan, not the old shorthand ACE example or recursive icacls commands.
These are manifest requirements, NOT an instruction to run sc.exe now. Service
creation, SYSTEM enrollment, ACL/Registry writes, user/session creation, later
start and Host qualification all remain separately NOT_AUTHORIZED.

Provision-enrollment reads pre-existing protected NativeEnrollmentV1 and raw
stdin payload bytes in exact manifest order; it does NOT register the service,
write that Registry enrollment, accept prefixed JSON or provide automatic undo.
REFUSED must not overwrite an existing object. PARTIAL/RECOVERY_REQUIRED preserves
exact objects and evidence; do not delete, retry refused cleanup or change policy.
CodeRoot permits service RX and DataRoot service Modify; neither proves the
future Host subject may create its AF_UNIX endpoint there. A separately bounded
socket run-root identity/ACL and independent OS observation remain necessary.

The controller's historical filtered token and account Administrators membership
are compatible UAC observations, not an identity conflict. Fresh effective-token,
new standard subject SID/session and actual service SID readback are required at
the effect boundary; no SID/session is fabricated from a name or candidate SID.
The VS SDK global install proposal is retired. Owner explicitly accepted the
portable SDK exact limited download/use/offline build; verified package/input
hashes and actual linked image are recorded in this file's current top section.
That consent does not permit global PATH changes or new fees. The linked image
exists but is not the pending corrected setup image; final operation config and
corrected binary remain UNFROZEN. Source and
offline tests alone cannot fill those fields or qualify 30B/43. Safe suspension
after separately approved setup is stop/disable only the verified new service
and disable only the verified new user; preserve data/ACLs for recovery rather
than claiming a destructive rollback. Freeze and independently review the final
operation manifest before presenting one executable Owner decision package.

This is the requested concrete preparation, not an installer, native qualification,
or instruction to run elevated commands. Root owns this packet under the same batch.
Its boundary is the future approved local setup only; no vendor-service reuse,
global Codex/Claude config edits, generic broker, external repository deployment or
old cleanup attempt. Before any change freeze an exact operation manifest and get
ONE Owner confirmation of that complete manifest, as the latest decision requires.

### Observed identity and payload inventory (read-only 2026-10-19)

Finite helper authority_install_inventory at5b3c50f0 observed:
- Controller DESKTOP-28ERPQ1\GameBoy, SID S-1-5-21-3542654388-73774624-397494543-1001.
  Medium/UAC-filtered token, Administrators deny-only but account in local Admins.
  It is NOT an independent standard account and cannot be the review subject.
- JohnnyGrantAuthority service absent. `sc.exe showsid JohnnyGrantAuthority` returns
  S-1-5-80-3020799075-4261108201-91889776-39638685-3705689551 / Inactive. This
  deterministic candidate SID is NOT an installed/enrolled/qualified identity.
- `sc.exe showsid JohnnyReadonlyHost` also returned an inactive candidate service
  SID; that does not create a user/session. We do NOT propose a second service merely
  to obtain that SID. Existing CodexSandboxOffline/Online accounts are vendor-owned,
  not approved reusable Johnny principals. No account/password was modified/read.
- C:\Program Files\Johnny and C:\ProgramData\Johnny (including GrantAuthority) absent;
  therefore no target ACL pre-state exists. A future unexpected existing path,
  service/account, reparse ancestor or name/identity conflict must stop, not overwrite.
- Installed CLI and Python are currently USER-writable locations, not protected
  execution sources. CLI version/hash is section1; Python3.11.9 at
  C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\python.exe has SHA256
  5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec.
  Future protected payload must include its complete executable/dependency closure,
  not import this per-user Python/site-packages or load arbitrary PATH/PYTHONPATH.
  Service executable/config/observer hashes are NOT_BUILT, not guessed from source.

Measured helper command records:14 calls, outer wall17.629s (charge18 within Root150),
in-command stopwatch10.974s is not an alternative discount. Read-only commands were
WindowsIdentity/Principal, whoami /user /groups, relevant Get-LocalUser/admin-group,
Get-CimInstance Win32_Service, sc.exe showsid, Test-Path for the named directories,
exact CLI/Python --version and Get-FileHash. No session/attack/ACL/settings effect.

### Proposed principals, object rights and transport

| Object | Exact proposed principal / rights | Stop/readback condition |
| --- | --- | --- |
| Issuer service | JohnnyGrantAuthority, own-process, demand-start, virtual account NT SERVICE\JohnnyGrantAuthority; above SID; no LocalSystem/Administrators membership | SCM actual StartName/SID, protected process image and loaded dependency closure must match |
| Review subject | New dedicated local STANDARD account JohnnyReadonlyReview, not GameBoy or vendor sandbox accounts. SID NOT_CREATED: must come from New-LocalUser's OS result joined to same-name Get-LocalUser, never a caller value | Password entered as SecureString directly by Owner/admin UI, never Agent/log/config. No Administrators/remote/group privilege; same-account role claims not accepted. Standard account alone is NOT source/code isolation |
| Protected code | C:\Program Files\Johnny\GrantAuthority\bin\JohnnyGrantAuthority.exe and pinned dependencies/config schema; ownerSYSTEM, SYSTEM/Admins full, service SID RX; no controller/subject/Users write or owner rights | Complete payload file manifest+hashes, DACL/owner/ancestor identity and no writable DLL/import path before service start |
| Protected policy/store/evidence | C:\ProgramData\Johnny\GrantAuthority\policy.json, grants.sqlite3 and evidence\; ownerSYSTEM, SYSTEM/Admins full, service SID modify; no controller/subject access | Owner approval UI owns canonical plan enrollment. SQLite/ACL do not themselves authenticate an Agent role; protected enrollment binds observed SID/process creation/job/image/config/session to exact plan |
| Readonly snapshot/config | C:\ProgramData\Johnny\ReadonlyReview\snapshots\<attempt-id> and protected per-run profile; service/control owns, exact enrolled subject SID read/traverse only | Attempt ID and exact files/digests pinned later; not a live worktree or arbitrary Temp clone. Subject cannot change config, snapshot or observer |
| SCM service object | SYSTEM/Admins control; exact controller SID query/config/status/read-control only (CC/LC/RC); no user start/stop/change-config/delete/write-DACL | Readback SDDL against exact reviewed descriptor; no Authenticated Users broad control |
| Read pipe | \\.\pipe\JohnnyGrantAuthority.Read.v1; SYSTEM/Admins/service full; exact enrolled controller/subject SID only FILE_READ_DATA, FILE_WRITE_DATA and SYNCHRONIZE (mask0x00100003), no create-instance/write-DACL | Server explicit DACL and PIPE_REJECT_REMOTE_CLIENTS; client checks actual server SID/creation/image/config, server checks actual client/enrollment. No name/PID-only trust |
| Approval pipe | \\.\pipe\JohnnyGrantAuthority.Approval.v1; SYSTEM and elevated approved Admins only; no Agent/subject ordinary SID | Interactive protected Owner approval, not grantable through Read RPC or caller approved=true |

These are exact intended ACE responsibilities, not observed ACLs. Individual named
pipe rights are deliberate: generic-write includes create-instance rights and would
permit another server instance. The service must construct/verify pipe descriptors
in its later reviewed native implementation; `sc sdset` affects the SERVICE object,
not its pipes. No filesystem ACL substitutes for peer/enrollment verification.

### Network and runtime impact

Initial authority service mode is local-only named pipes, no TCP listener, remote
SMB clients refused, no provider/model/telemetry upload/update/download. Virtual
service accounts are NOT inherently network-disabled. A final native manifest must
pin effective outbound-deny enforcement and its negative readback; no actual mainline
GET until a separate exact read effect/allowlist is approved. No machine-wide firewall
policy change and no assumed Windows firewall default is part of this source grant.

Readonly CLI is a separate per-attempt subject, never this full-access parent or
its inherited ordinary children. Protected per-run CODEX_HOME contains no production
auth; --ignore-user-config does NOT ignore authentication by itself. Installed CLI
flags such as readonly/ephemeral are candidates, not no-code/no-delegation proof.
No global TOML, plugin disable, login/logout or vendor sandbox-service modification.
The offline Responses stimulus would need an exact loopback address/port and request/
retry/body limits; these are NOT_ALLOCATED until the native adapter is built. Do not
combine an indiscriminate outbound-block rule with a supposed loopback allow and
claim it works. Freeze actual allowed endpoint/process tree and OS/network observation
in the later finite operational Manifest; if enforceable limits are unavailable,
launch zero requests / UNAVAILABLE. No native probe is authorized in this packet.

### Historical operation sequence (NOT_EXECUTABLE; use current source-matched plan)

1. Pin full reviewed native source commit, service executable/complete payload hashes,
   config digest/schema, exact subject SID acquisition recipe, all descriptors,
   endpoint/attempt/bounds/observer, binary argv support and rollback manifest.
   These NOT_BUILT values prevent the packet being executable today; Root must build
   them through a separately narrowed source scope, not ask Owner to supply a product.
2. In separately confirmed elevated setup, verify absent targets and contained nonreparse
   parents; acquire dedicated standard account via OS, capture returned SID; stage only
   hash-pinned payload. No pip/npm download, ambient import, user-code service launch
   or writes to existing profiles. If current policy prohibits an operation, stop it,
   retain evidence and do not substitute another command.
3. Protect only the new exact service/data/snapshot trees with reviewed ACLs/owner;
   set SCM object controls, enroll the actual SID/session policy, then read back.
4. Only after setup readback and its separate authority may a demand-start be requested.
   Starting a service is not Host qualification. Qualification is another exact grant.

The former virtual-account/--config/demand-start and recursive icacls examples are
RETIRED_INCOMPATIBLE_WITH_CURRENT_NATIVE_SOURCE, not executable setup instructions.
Their exact history remains in bf057b0e6e4c9db8505cbe267e89de7cd5327e82 at this
same path; do not reproduce or execute them. The current native source requires
LocalSystem, exact quoted executable + service, disabled initial start, exact
ProtectionPlan whole descriptors and protected Registry enrollment. No recursive
grant/reset or preexisting target adoption is permitted. The pending corrected
wrapper/manifest must be independently reviewed/pinned and separately authorized
before any setup effect. This retirement does not erase prior failure evidence or
relax the original qualification/Recovery/Owner decision requirements.

### Verification and rollback to include in the final approval

Readback: Get-LocalUser JohnnyReadonlyReview (actual SID/enabled state), exact local
Administrators membership exclusion; Get-CimInstance Win32_Service filtered by
JohnnyGrantAuthority (StartName/PathName/state/PID), sc.exe qc/sdshow/showsid;
Get-Acl for every explicit manifest file/root (owner, DACL and inheritance, no
reparse), Get-FileHash SHA256 for complete executable/dependency/config closure;
independent actual token/peer/pipe-policy evidence. Source-only fake ports do not
satisfy these checks. Later native negatives must prove subject cannot overwrite
issuer/policy/evidence/snapshot, approve a plan, spoof a pipe or escape the tool
scope; no attacks are executed now. Setup PASS alone cannot satisfy CVQ restrictions.

Rollback is scoped and reversible: if this exact newly registered service exists,
separately authorized `sc.exe stop JohnnyGrantAuthority` then
`sc.exe config JohnnyGrantAuthority start= disabled`; disable only the exact newly
created review SID with Disable-LocalUser. Stop after failed stop/identity mismatch;
finite retry0, preserve RECOVERY_REQUIRED. Retain protected ledger/evidence/payload
and ACL/owner readback for recovery. No account/service deletion, recursive deletion,
global ACL restore/reset, Git reset/clean, immediate GC or old artifact cleanup.
New setup assets carry Owner/attempt/TTL through setup/qualification plus evidence
seal; if rollback/cleanup is unconfirmed keep a recovery hold, not a false closed
ticket. Since pre-state targets were absent, this packet does not restore or modify
any preexisting service/user/path. A future reuse/update needs its own exact pre-state.

Pending before external confirmation: reviewed native executable/dependency/config
hashes and argv; actual subject SID acquisition/rights; exact no-extra-ACE descriptor
construction; OS-protected observation/enrollment; all reachable effect roster,
enforceable bounds and loopback/network rules. These are OUR remaining build/manifest
tasks, not a request for the Owner to design missing components. Submit the completed
operation list once, no guessed hashes or blanket elevation permission.

## Sources for proposed primitives

- OpenAI official subagents: https://learn.chatgpt.com/docs/agent-configuration/subagents
- OpenAI app-server/versioned schema: https://learn.chatgpt.com/docs/app-server
- OpenAI provider/retry config: https://learn.chatgpt.com/docs/config-file/config-reference
- Claude CLI/hooks: https://code.claude.com/docs/en/cli-reference and https://code.claude.com/docs/en/hooks
- Windows authenticated pipe peer: https://learn.microsoft.com/en-us/windows/win32/ipc/impersonating-a-named-pipe-client
- SQLite transactions/durability: https://www.sqlite.org/lang_transaction.html and https://www.sqlite.org/atomiccommit.html
- Python3.11 SQLite transaction/timeout API: https://docs.python.org/3.11/library/sqlite3.html
- Microsoft service accounts: https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-service-accounts
- Microsoft pipe access rights/create-instance caveat: https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights
- Microsoft ACL command semantics: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls
- Microsoft service creation: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-create
- SecureString local-user creation: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.localaccounts/new-localuser?view=powershell-5.1
