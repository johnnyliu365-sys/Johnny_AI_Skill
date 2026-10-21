# 30｜可信的獨立票接續與主線保持開放

| 欄位 | 內容 |
| --- | --- |
| State | `30G_ENGINEERING_PASS / QUALIFIED_AUDIT_BLOCKED / 30B_REVIEW_BLOCKED / R2_CLOSED / R1_SOURCE_UNVERIFIED`；30G候選20bd6e30與30B候選0f6d467a均未整合；30A／30M證據保留，完整Ticket30與01／02未完成 |
| Requirement lineage | 沿用 `PRD-20260805-009`／`CHG-20260805-009` 與原 Ticket 30；不建立新 PRD、平行 Ticket 或第二套 authority |
| Effective authority | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` 的既有有效 AC 1–8 |
| Design evidence only | Owner-authorized、獨審通過的 SPEC design baseline `76d1f942e24975da28889c8b6ecee904c8ef3da0`，SPEC blob `6fd8c3098f48be40c2cf05a03f8284c186163c08`；它允許受控拆票規劃，不是 Ticket 30A implementation Grant 或 runtime activation |
| Prior candidate | `76f6f32771e80add10c499db2c7479377b079c0c` 的初審為 `BLOCKED`：錯把一般 owner 指示寫成 ticket-scoped Grant，並自創未獲核准的 API、source grammar 與硬預算 |
| Roles / worktree | Root＝Architecture Owner（本次文件修訂）及唯一 reviewer orchestrator；實作者 `/root/ticket30a_fixture_impl`，獨審 `/root/ticket30a_fixture_review`；repo-contained `.worktrees/skill-improvement-30a-fixture`／`codex/skill-improvement-30a-fixture`；文件獨審 `/root/ticket30_docs_review` 已在 `35b25d60` PASS，分配時再讀回 Git identity |
| Profile | Current30G=`HIGH_ASSURANCE`, exact scope below；historical30A=`STANDARD` fixture only；均不授予真實Host/source/effect資格 |
| Implementation language | Python3.11 strict；current30G checker／constructor順序依下節；原30A命令為歷史證據不重跑 |

## Effective local batch resource / convergence amendment — 2026-10-19

Authority `batch-checklist-local-20261019-uncapped`: Owner explicitly removes all
per-ticket/per-role cumulative command-second ceilings and fixed initial-plus-one
correction attempt ceilings for the original12 local items, including30B/30G/B3F01.
Historical usage, failures, findings, reservations and UNRECONCILED timing remain;
none are reset or presented as measurement. Older numeric ceilings/attempt locks
below are SUPERSEDED_FOR_THIS_LOCAL_BATCH, not reasons for another renewal request.
The proposed500 package is SUPERSEDED_NOT_ADOPTED. Scope/qualification/external-effect
boundaries do not change. Implementation-authority's explicit resource amendment
rule is canonical; this is the project-specific authority/child-Grant binding.

Root may derive precise local child Grants, including N2 after its reviewed exact
baseline/paths/constructors, under this parent without a fresh resource approval.
Existing field allowlists and type/source/review admission must still pass; this
section does not automatically authorize a new path or operational trusted Grant.
Actual issuer/Host positive acceptance remains OPEN,30B/43 remain REVIEW_BLOCKED,
and ordinary engineering preparation remains distinct from qualified source review.

Retain command60s / compiler-test child55s as initial defaults and resource tracking;
adjust an individual bound only after diagnosis with workload/reason recorded. A
repeat of the same failure without new evidence stops unchanged retries, not other
independent work. No unbounded wait/load, tool-policy bypass, paid expansion, installation,
permission change, live Host campaign, push/release/deploy or formal activation.
This amendment becomes effective after independent consistency review of its exact
committed rules/ticket/index/runbook versions; subsequent exact child bindings refer
to that reviewed revision. Current N1 immutable source/evidence hold is unchanged.



## 30N14B — retained protected launch provenance / closure54 engineering accepted

Original30/PRD-20260805-009/CHG-20260805-009/Context04/runbook03 sections3/6;
parent batch-checklist-local-20261019-uncapped/first-CVQ construction exception.
State ENGINEERING_SOURCE_ACCEPTED_NOT_HOST_QUALIFIED; exact DOC_PASS, N14A stage QA,
child Grants13a..13f and independent source review completed. Baseline7606a21df3cbda10d401b3458c3e0ee9e07594a3 is an
engineering source hold, NOT remote authority or qualified Host. No new PRD/SPEC.
AO actual FINAL CutB plus limits-anchor refinement; Root independently reads
existing lease/token/launch/preparation/N10 signatures at that exact source.
One result: protected enrollment determines existing launch, retaining ORIGINAL
token/job/process/thread provenance for future peer matching. No actual launch.

Exact no-DELETE/no-dependency scope:
MODIFY library/local_orchestration/grant_authority/windows_subject_lease.py
MODIFY tests/test_grant_authority_windows_subject_preparation.py
MODIFY tests/test_grant_authority_windows_subject_launch.py
CREATE library/local_orchestration/grant_authority/windows_protected_subject_launch.py
CREATE tests/test_grant_authority_windows_protected_subject_launch.py
No export/service/SCM/Registry/ledger/N14A/launch-ABI edits. The two existing tests
may ONLY pass limits=the original job._limits to their existing derived-job
constructor; preserve all negative assertions. Initial exact-name inventory missed
these subclass constructors. Root strict diagnostic found both missing arguments;
the corrected base-and-derived inventory is retained with the original failure.
This necessary bounded caller migration uses the existing batch, not new authority.
Other unmigratable caller/contract conflict ->BLOCKED, not silent scope expansion.

Reuse existing _SubjectJobLimits/_PrimarySubjectTokenLease/_PrimarySubjectIdentity,
_SubjectJobLease, _SubjectLaunchPlan, _launch_verified_subject, _SuspendedProcessCreation,
_ObservedEnrollmentMatch, _SnapshotSourceFile/_SnapshotBlobMember/_SnapshotBlobReader
and original recovery/poison/lock/teardown mechanisms. No new error enum/DTO tree/
reader/handle protocol/Runner/permission source. Private module __all__=().

Job lease constructor adds exact limits:_SubjectJobLimits parameter, same factory
passes keyword limits=validated_limits (validated before native create/readback).
Exact type check before assignments; retain _limits and _original_limits as the
same original normal-model object. require_live and _borrow_native_owner require
both exact types and identity _limits is _original_limits before returning/borrowing.
Mismatch uses existing owner/alias drift recovery/poison path, no auto-close/retry/
fallback/getter. Same-class equal-value replacement must fail. Existing behavior
and factory return type unchanged; no unrelated lifecycle refactor.

New private entry:
_launch_protected_subject(enrollment:_ProtectedInstalledSubjectEnrollment,
token:_PrimarySubjectTokenLease,job:_SubjectJobLease,
cancellation:threading.Event,deadline:float)->_RetainedProtectedSubjectLaunch.
No caller plan/SID/session/owner_ref/PID/path/config/args/env/limits/trust flag.
Output strongly retains exact enrollment/token/job/creation/actual identity and
record-derived owner_ref/original job_ref in private slots _enrollment/_token/_job/
_creation/_identity/_owner_ref/_job_ref. Ordinary assignment-only construction,
no serialization/raw handle getter/PID reopen/adopt/auto-GC/native teardown.
Private source trust only, not resistance to arbitrary same-process private writes.

Order before ANY N10/process effect:
1 exact enrollment/token/job/controller types, finite float now<deadline<=now+60s,
   issuing thread and controller, exact retained approval/record and all five N14A
   approval links. Binding comes from record, never caller assertions.
2 owner_ref=record.operation_ref; capture original token owner/alias/identity/thread
   and job owner/alias/ref/limits/thread. Require exact PRIMARY identity SID/session
   match record, owner refs match, original aliases/threads intact, leases live,
   not close/borrow/poison/recovery/launch-attempted. job.require_live(owner_ref),
   original limits identity and job._original_limits==record.job_limits.
3 build two existing normal _SnapshotBlobMember values in executable/configuration
   order from record.launch_plan.files: copy path/sha256/size_bytes/owner/
   descriptor_sha256/volume_serial/file_id exactly into _SnapshotSourceFile;
   blob_ref=record.approval_ref, offset=length=0, sha256=_EMPTY_SHA256.
4 each _SnapshotBlobReader(member,cancellation,deadline).read() must return exact
   empty bytes. Existing N10 still reads/hashes full files and checks protected
   path/owner/descriptor/volume/file-id/stability; zero range is not skip-validation.
5 after both proofs recheck controller and ALL original lease/owner/alias/thread/
   identity/limits/lifecycle/binding facts; no substitution between proof and launch.
6 call existing _launch_verified_subject(record.launch_plan,token,job,owner_ref)
   exactly once. Reuse existing borrowed-owner/ref/thread/lock checks; do not
   substitute/reopen a handle or accept a composed caller plan.
7 successful launch then assignment-only retained wrapper; NO further model,
   clock/cancel/peer/file/native rejection check after effect. If construction
   unexpectedly raises, exact existing _retain_failed_preparation(token,token_owner,
   job,job_owner,job_alias,creation) retains/poisons original owners; raise existing
   _ProcessCreationError(RECOVERY_REQUIRED,creation), no close/retry/resume.
No new enrollment Recovery hold: no authenticated output/legitimate resume exists
on failure; enrollment is immutable evidence, not new native ownership.

Finite existing failures: plain invalid arguments/binding/known refusal before child
-> _ProcessCreationError(INVALID_INPUT). Pre-child lease uncertainty propagates the
original _SubjectJobError with retained owner/recovery_hold or _SubjectTokenError
with its existing poison/retention; never remap uncertainty to INVALID_INPUT, never
construct _ProcessCreationError(RECOVERY_REQUIRED,None). Limits-anchor failure uses
existing _retain_recovery_resource(RECOVERY_REQUIRED,original owner,job_ref,alias),
sets lease recovery flag and raises existing _SubjectJobError with that hold.
N10 failure propagates existing _SnapshotReadError, child count0. Original launch
errors propagate unchanged; its own InvalidInput mapping does not certify safe
cleanup or clear preexisting holds. Post-launch uncertainty ->existing
_ProcessCreationError(RECOVERY_REQUIRED,original creation). No raw native/path/SID/
OS details or invented success. No issue/claim/read/settle/pipe/Host.

Preflight source construction: new output need not exist before SOURCE_EDIT_ONLY.
Normal constructors/type imports first, Root strict5/memorycompile then separately
reviewed SDK-deny import/fake admission before any test execution. No Any/cast/
model_construct/model_copy(update)/reexport bypass. Defining module imports only.

N14BT1 constructor/factory preserves exact original limits; bool/derived/wrong
limits and equal-value substitution refuse via original lifecycle/retention path;
ordinary valid job success remains. Existing constructor caller inventory exact.
N14BT2 executable/configuration member full-field mapping/order/zero bounds and
empty digest, controller passed unchanged; both before single real launch seam.
Tracking typed N10 fake reused for composition, existing whole-file zero-range N10
suite retained; no duplicate browser/SDK/native/file harness.
N14BT3 intact enrollment/approval five-links/token PRIMARY SID/session/owner/job
limits and original refs ->success, exact original owners/creation strongly held.
Wrong types/subclasses/unsealed/direct record, each link/SID/session/owner/alias/
thread/limits drift/closed/borrowed/poisoned/launch-attempted ->zero child creation.
N14BT4 cancellation/deadline/N10 mismatch, second-proof owner/limits substitution ->
zero child. Successful launch construction exception ->exact six-argument retention,
original owners held, no close/reopen/retry; repeat launch refuses before new effect.
N14BT5 named memory reverse mutations: remove limits identity; remove limits-value
binding; skip configuration proof; move proof after launch; omit retained owner;
drop postlaunch retention; accept derived enrollment. RED call at intended cell,
exact restoredGREEN. Root independently different door; all unfiltered raw retained.
No ceremonial first-red for new behavior; no all-refusal substitute for legal pass.

Reuse tests/test_grant_authority_windows_subject_preparation.py _CompositionFakes,
existing subject-launch resume seam and snapshot-reader fake/assertions. One new
focused matrix only, no copied native harness. Constructor/limits tests included
before launch composition, not deferred followup test ticket. Run new suite plus
affected subject lease/preparation/launch and snapshot reader/contracts, N14A source
bindings as necessary; strict5 lease/new app/newtest/two migrated old tests,
memorycompile/import/diffcheck. No weakened checker or skipped old assertion.
Root must inspect actual fakes/ABI/guard and exact source before test admission.
No old test retired; local commands not proof of external test CI.

Profile HIGH_ASSURANCE/source-only first-entry build, Python3.11 strict. Root AO/
sole reviewer/orchestrator; retained /root/ticket30n4_peer_impl current Luna/xhigh
capability, separate retained source-audit helper not qualified Host reviewer.
Prospective owner/review worktrees .worktrees/skill-improvement-30g-protected-launch
and matching -review, branches codex/same, exact baseline7606a21d; registration/
containment/Git identity required before allocation. Temp under LOCALAPPDATA/Temp/
johnny30-protected-launch-owner-20261021 and matching-review-20261021; ownerauthor/
Root, TTLthroughreviewseal, evidence/Recovery holds overrideexpiry; teardown only
after exact safe authorization. Uncapped cumulative/count, preserve history;
initial child55/outer60s, diagnose repeated unchanged failures. Growth forecast
lease25..45 lines, app220..300, test350..470; >500effective structural review signal,
not forced split/minify. Reuse limits/ownership code, no monolithic catch-all script.
XSS/UI N/A, no product responsibility move; bounded source application composition.

Return exact baseline/candidate/fiveblobs/files/checks/findings/deviations/holds.
Author initially SOURCE_EDIT_ONLY, no import/test/checker/SDK/SQLite/commit/Agent/
cleanup until separately admitted. Normal local construction sub-Grants derived
from original batch, not operational trusted Grants. No live Host campaign,
account/SID/config/security/ACL/SCM/service install/launch, network/models/newfees,
push/release/deploy/formalactivation. 30B43/TAL/R0/DAP/E01/Recovery remain unchanged.

### Shortest acceptance continuation / external boundary — 2026-10-21

N14B result: immutable650f1c37ebef9741ec1691e0e5f22fe7f60e8c85, exact five paths;
strict5 and449 affected tests pass, eight named memory RED/exact restoredGREEN
pairs include Root independent final-controller door. Full failures/successes and
passive Host inventory preserved in original review N14B_SOURCE_ORIGINALS_V1 seal.
Independent source helper actual FINAL ENGINEERING_SOURCE_PASS_NOT_QUALIFICATION;
Root engineering acceptance only. Own engineering hold exactFF to650f1c37, main
unchangeda1cb6c13. No real subject launched, Host/Grant positive not yet accepted;
30B/43 REVIEW_BLOCKED. No checklist item newly checked. Next is step2 below, not
another provenance abstraction or new framework. Normal local child allocation
comes from existing uncapped batch; no operational trusted Grant is implied.

No new planning branch/framework or unrelated governance slice. This sequence is
recorded in original30 and does not grant installation or a native campaign:

1. Finish N14B exact source, strict checks, affected fake-only behavior, named
   red/restored-green mutations and independent engineering review. Result must
   prove protected enrollment reaches the existing launch once with original
   owners retained; this builds the missing subject-provenance prerequisite of
   the common entry blocking both30B and43. It is NOT Host qualification.
2. Reuse the existing protected-store/pipe/message-identity/retained-process/
   approved-issue/claim/snapshot/settle modules in the smallest executable service
   composition. Actual windows_service currently decodes observations; it is not
   an SCM ServiceFramework composition root. No caller observation may substitute
   for OS-derived peer facts. Acceptance: bounded legitimate read plus forged/
   mismatched/replayed inputs rejected by that real wiring in offline tests;
   freeze executable/dependency/config payload and operation manifest. This
   prepares30B trusted-Grant positive and43 protected observation, not either PASS.
3. Obtain ONE exact operational confirmation for independently protected service/
   subject/observer setup and the bounded first-entry native campaign. Read back
   actual OS protections before any subject request. Initial provisional evidence
   is not CVQ qualification; finish the original CVQ with genuine prerequisites,
   then use its exact capability for each held candidate's independent audit.
   This removes the shared qualified-entry dependency of30B/43 only after PASS.
4.30B additionally requires trusted issuer positive AND same fresh observed remote
   main SHA index/leaves. Local origin/main or source tests cannot supply this;
   unpushed Context04/mainline source remains a separate publication dependency.
   43 still needs its own qualified candidate review/evidence, not N14B test counts.

Fresh passive inventory: DESKTOP-28ERPQ1, DESKTOP-28ERPQ1\\GameBoy,
SID S-1-5-21-3542654388-73774624-397494543-1001; admin-enabled=false,
Windows10.0.19045.0, PowerShell7.6.5. Get-VM -Name
'Johnny-MSIX-Lab-20260905' -ErrorAction Stop was denied with
Unspecified,Microsoft.HyperV.PowerShell.Commands.GetVM and message
「您沒有完成此工作的必要權限。請連絡電腦 'DESKTOP-28ERPQ1' 的授權原則系統管理員。」
No VM identity/state was established; no retry/elevation/policy bypass. Exact raw
is retained in first_host_exact_permission_inventory_raw pending evidence seal.

External changes NOT authorized: create dedicated standard review account and
read back its actual SID/session; install demand-start JohnnyGrantAuthority with
reviewed service identity and protected executable/dependency closure; exact
whole-DACL/owner/Registry/store/pipe protection; independent observation; finite
zero-external-model offline Host campaign. Earlier runbook03 virtual-account and
unbuilt EXE examples are historical proposal, NOT runnable permission: later
source requires LocalSystem plus exact service SID, and NativeTools CLI is not
an SCM service. Do not approve guessed hashes or treat service-account RX as a
restriction of LocalSystem. Final manifest must resolve these exact runtime facts.
Network: local named pipes and only explicitly bounded loopback stimulus; no
provider credentials/model fees/remote source effect or global firewall change.
Rollback proposal: identity-checked stop then demand-service disable, disable only
the newly created review SID, retain protected ledger/evidence and recovery holds;
no delete/reset/clean/GC/global ACL rollback. Failed stop keeps RECOVERY_REQUIRED.
Complete local wiring/build before asking Owner to approve the concrete manifest;
Owner supplies OS consent, not a missing executable. No checklist box changes.


## 30N14A — protected subject enrollment source / proposed closure53

Original30/PRD-20260805-009/CHG-20260805-009/Context04/runbook03 sections3/6,
same local batch/first-CVQ construction exception. This source prerequisite fills
protected expected subject provenance; caller launch plan/SID/session is not
authorization. Status PROPOSED_NOT_DISPATCHABLE until exact DOC_PASS, final N13
source-stage baseline and child Grant binding. No new PRD/SPEC/authority engine.
Architecture actual FINAL CUT_A_CONTRACT_READY and DOC_PASS3e58897e; Root reads
existing contracts at a081906f6b3f7e34f8cad9ce96d510f86a446d07. Final source baseline
is86be3e340d4b95dd37f054a4024ae7ada5affbd7 after reviewed N13-only deltas; Registry
and all direct N14A contracts unchanged. N13 source/stage originals QA passed at
a2ccc40a/8ad53fac;110prior paths unchanged,114total. Not Host/authority integration.
Root child Grant/allocation binding below is the remaining dispatch prerequisite;
other contract drift requires rebind. No new Owner technical approval required.

Exact no-DELETE/no-dependency scope:
MODIFY library/local_orchestration/grant_authority/windows_approval_registry.py
CREATE library/local_orchestration/grant_authority/windows_installed_subject_enrollment.py
CREATE tests/test_grant_authority_windows_installed_subject_enrollment.py

Reuse N11 Registry traversal/owners/ACL/Current/lastwrite/query/lock/poison/recovery
and existing strict models/JSON rejection. No second native reader, general
selector/callback, duplicate SDK fake/JSON parser/Runner/public DTO/export.
Old read_installed_approval_payload(cancellation:threading.Event,deadline:float)->bytes remains ApprovalV1-only,
even if SubjectEnrollmentV1 absent. New fixed read_installed_subject_bundle_payloads
(cancellation:threading.Event,deadline:float)->tuple[bytes,bytes] returns ApprovalV1 then
SubjectEnrollmentV1. One retained key/ancestor traversal and private fixed branch,
no caller path/key/value selector. Approval cap262144, subject cap131072 bytes.
Read both, recheck Current/all descriptors/lastwrite, reread both, exact compare,
known owners checked-close once, terminal controller check then return. Never
partial payload success. Unknown native output/close/alias retains owners/buffers,
poisons RECOVERY_REQUIRED; known refusal with certain close finite refusal. Old
reader behavior/regression byte semantics unchanged; no SDK/Registry run authorized.

One private _InstalledSubjectEnrollmentRecord(_StrictModel):
schema_revision exact Literal[1]; scope Literal["SOURCE_ONLY_UNQUALIFIED"];
enrollment_ref/session_ref/grant_ref/operation_ref existing OpaqueMetadataId;
native_enrollment_id bounded1..128 canonical lowercase ASCII letters/digits with
single internal hyphens, starts letter (existing C# NativeEnrollment grammar);
native_enrollment_revision exact Literal[1];
native_setup_manifest_sha256 existing _ObservedSha256;
approval_ref existing CVQ OpaqueMetadataId; plan_digest EvidenceDigest with existing
exact sha256_ plus64lowerhex grammar; actor_role existing ModelRole;
expected_subject_sid existing _CanonicalSid; expected_windows_session_id existing
_PositiveUint32; launch_plan existing _SubjectLaunchPlan; job_limits existing
_SubjectJobLimits. No cloned args/environment/files/peer/token schema.
Reject exact-type/coercion/subclass/bool/null/extra/duplicate/depth/nonfinite/invalid
UTF8/bounds failures, not normalize; nested ordinary strict constructors/validators.
C# link fields are source-only producer/consumer links, NOT independent readback
proof of installed NativeEnrollment. Future installer must generate and read back
same canonical values. LUID only future actual WTS token, never fixture enrollment.

Private _decode_installed_subject_enrollment(payload:bytes)->record|None and
_read_installed_subject_enrollment(expected_approval:_InstalledApprovalRecord,
cancellation:threading.Event,deadline:float)->_ProtectedInstalledSubjectEnrollment.
Before native: exact inputs/finite admitted <=60s deadline/issuing thread. After
one fixed bundle read: controller/poison, decode Approval using existing decoder,
require exact equality with expected_approval, strict decode subject, require exact
approval_ref/grant_ref/operation_ref/plan_digest/actor_role == approval corresponding
values, terminal controller/poison, ordinary sealed-wrapper constructor. Strong
refs to exact approval/record; exact typed singleton seal, no serialization/raw
getter or caller trust flag. Seal is local-source provenance, NOT OS isolation or
authority against arbitrary same-process code. No operation issue/claim/read/settle.
Finite failures INVALID_INPUT/INVALID_RECORD/APPROVAL_MISMATCH/WRONG_THREAD/CANCELLED/
DEADLINE_EXCEEDED/SOURCE_UNAVAILABLE/RECOVERY_REQUIRED. Existing Registry failures
map identically where same; native/data/protection/value unavailable ->SOURCE_UNAVAILABLE.
Malformed/mismatched bundle approval ->APPROVAL_MISMATCH; subject ->INVALID_RECORD.
Sanitized enum-only errors, no payload/path/SID/ACL/OS text.

Preflight build order: constructor/decoder tests for new private types first,
Root strict3+memorycompile under reviewed SDK-deny guard, then fake-native regression.
New private output need not already exist before source-only construction dispatch;
operational qualification remains separate. Reuse existing approval_tests._FakeRegistryApi,
_FakeAdvapiDll/_install_fake/descriptors/literal approval; thin bundle subclass only.
No copied native harness, nominal fakes must satisfy real declared types/signatures;
no Any/cast/model_construct/model_copy(update)/implicit reexport bypass.

N14AT1 ordinary constructor/roundtrip minimal/max/Unicode launch; exact grammar
1/128, SID/session1/max,0/overflow/bool/extra/null/coercion/depth/size rejection.
N14AT2 stable one-traversal bundle reads both twice; old ApprovalV1-only still green;
missing/type/size/either-value drift/Current/ACL/owner/ancestor/link/lastwrite reject.
N14AT3 interruption/cancel/deadline/close uncertainty retain/no partialbytes/no retry.
N14AT4 bundled approval and each subject link exact mismatch refused; sealed wrapper
exact owners/record refs, wrong-type/unsealed/direct record refused.
N14AT5 named reverse mutations skip approval equality, skip subject reread, oldentry
require newvalue, seal identity relaxed, grammar/coercion/extra relaxed: named RED,
exact restoredGREEN. Root at leastone different door, all raw unfiltered output.
Test actual candidate modules/source binding; fake-native evidence not Host proof.
Existing N11 suite plus affected downstream N12/N13 consumers, strict3 including
newtest/registry/application, memorycompile/import and diffcheck. No old test retired.
XSS/UI N/A; no responsibility move TEST->A->B, only bounded existing adapter reuse.

Forecast registry70..110new/120affected; app260..340; tests360..470 via shared fakes.
>500effective triggers reuse/responsibility review, not forced split/minify/newfile.
Root AO/sole reviewer/orchestrator; retained Luna/xhigh author after N13 allocation
release, distinct retained native-tools helper source-only evidence, not qualified.
Prospective repo-contained worktrees skill-improvement-30g-subject-enrollment and
matching -review, branches codex/same; Temp johnny30-subject-enrollment-owner-20261021
and matching-review-20261021 under LOCALAPPDATA/Temp. Register before creation after
baseline/grant activation, owner author/Root, TTLthroughreviewseal, holds override
expiry, teardown exact safe authorization only, no denied-cleanup retry.
Initial55child/60outer, uncapped cumulative/count/evidence-progress, old failures
retained. Source-edit-only initial author; Root guard review before any test/native
stub import. SubjectEnrollmentV1 actual install/write/approval, account/SID/session
selection, SCM/ACL/service/network/SDK/SQLite/models/newfees/Host tests/push/release/
deploy/formal activation not authorized. 30B43/TAL/R0/DAP/Recovery unchanged.

## 30N13 — installed approval single-claim snapshot composition / closure52

Original30/PRD-20260805-009/CHG-20260805-009/Context04/runbook03 section2,
batch-checklist-local-20261019-uncapped and first-CVQ source construction order.
Baseline a081906f6b3f7e34f8cad9ce96d510f86a446d07 now in Root source-stage,
N12 originals23/23 and stage QA PASS at27d49dd1/7df4e9e2. Only source-engineering
hold, not qualified Host/Grant or final-main source. Prior failures/UNKNOWN/Recovery
are retained; checklist04 not redone. No PRD, SPEC change, new authority engine,
public Grant DTO, export, generic callback or caller authority/path/plan override.

Exact scope, no DELETE/dependency:
MODIFY library/local_orchestration/grant_authority/windows_protected_store.py
CREATE library/local_orchestration/grant_authority/windows_installed_snapshot.py
CREATE tests/test_grant_authority_windows_installed_snapshot.py

Closure52 same-ticket corrective delta, no requirement/SPEC expansion:
MODIFY tests/test_grant_authority_windows_snapshot_reader.py only the existing
test_controller_is_checked_between_prefix_metadata_steps and directly necessary
typed deterministic clock fixture. Existing product reader/native and old fake
SDK/handle grammar remain unchanged; no new test framework or timing threshold.
Candidate ce49780dfab4ee7a0742345cd15b5ea53b6dd24c is correction baseline.
Root actual guarded formal run448PASS/1FAIL: old deadline cell used5ms wall time,
possibly expiring before constructor; exact actual failure enum was not emitted,
so constructor-race cause remains source-backed diagnosis, not observed enum.
Replace scheduler/sleep dependence with clock advancement keyed to first fake
metadata query; retain exact root-only open/no read/no event/knownclose assertions.
No unchanged whole-suite retry just to seek green. Preserve full failure original.

N13F1/T1/T3 Root boundary probe actual RED: final pins_open getter sets cancellation
after final native verification; existing store returns verified bytes with Event
set, ledger COMPLETE and retained0. Add controller check after terminal pins/poison
read and immediately before return, so controller loss retains exact backing and
returns no bytes. Add permanent deterministic cancel/deadline boundary regression,
preexisting primary legal route remains green. Root's distinct getter-side door
is not substituted by rerunning author mutations. Preserve baseline raw/probe.
Original final51 remains readable;52 supersedes only these narrow correction cells.

Reuse before create: existing GrantPlan/Record/LedgerResult, private installed
approval, SQLiteGrantLedger issue/claim/settle, N12 pins/controller/busy/retention
and C13 issuer check, N10 exact-member one-use reader. One new application leaf
owns ordered member reading/evidence framing; existing store owns ledger lifecycle.
One parameterized test module reuses applicable prior test builders/fakes, no copied
native/ACL/JSON parser, fixture framework or standalone test runner. Existing ledger,
native readers, installed approval and old tests remain byte-identical.
New private result DTO unnecessary: ordered tuple[bytes,...], position maps exactly
to retained immutable approval.members. Scope remains SOURCE_ONLY_UNQUALIFIED.
No existing behavior moved or test retired: TEST->A->B N/A, source composition only.

Private APIs:
- store._read_installed_snapshot(self)->tuple[bytes,...]
- application._read_ordered_members(approval:_InstalledApprovalRecord,
  cancellation:threading.Event,deadline:float)->tuple[bytes,...]
- application._derive_snapshot_evidence(approval:_InstalledApprovalRecord,
  payloads:tuple[bytes,...])->EvidenceDigest
No raw ledger/approval getter or arbitrary operation forwarding. Existing private
finite error may add GRANT_NOT_YET_VALID/GRANT_EXPIRED/GRANT_ALREADY_CLAIMED/
GRANT_ALREADY_TERMINAL, no parallel error/state engine. Public existing constructor
preflight is unchanged and reused from exact N11/N12 evidence; new private methods
are candidate output and ordinary constructors/negative forms checked before review,
not a circular operational qualification prerequisite.

N13T1 legal real store method at actual application/reader seam, fake SDK/ledger:
existing busy lock, controller/thread/cancel/deadline/closed/poison checks; live pins
and native.verify_after; exact retained approval.peer C13 recheck. Internal
time.time_ns exact nonnegative int -> integer epoch seconds, require
not_before <= observed_at < expires_at BEFORE any ledger.issue. Check controller
before/after every bounded operation and before final return. Reject caller time/
plan/approval/ref/path injection, no env/config/remote fallback.

Issue exact fixed approval.grant_ref/plan. Accept only exact ISSUED+UNCONSUMED or
EXISTING+UNCONSUMED record, matching full original plan/ref and no correlation/
evidence. Existing CLAIMED -> finite ALREADY_CLAIMED; terminal -> ALREADY_TERMINAL,
no reader. After issue/result/controller checks, sample internal time.time_ns a
SECOND time immediately before claim; exact nonnegative int -> epoch seconds.
Pass this fresh value, NOT the pre-issue sample, to existing ledger.claim, whose
same transaction matches expiry and conditionally consumes UNCONSUMED.
EXPIRED -> GRANT_EXPIRED, no reader/settle; issued record remains UNCONSUMED.
No continuous post-claim wall-clock expiry policy is added: admission occurs
at durable claim-before-operation. Claim exact grant/plan/approval.operation_ref/
fresh observed_at, only exact
CLAIMED_NEW+CLAIMED record/full binding/correlation/no evidence permits construction
of any _SnapshotBlobReader. Existing claim (even same operation) is NOT a crash/
lease/resume authorization. Ledger remains unchanged, no lease subsystem.

N13T2 exactly each immutable approval.members entry once in original tuple order
through actual N10 _SnapshotBlobReader(member,cancel,deadline).read(). Hold all bytes
until completion, no generator/callback/partial tuple escape. Existing caps remain
1..256 members, <=32768bytes/member, <=64MiB source; validate actual bytes count/
hash against approved member at composition boundary even when fake is used.
Actual reader remains sole native handle owner, coordinator cannot adopt/close it.

Evidence: fixed domain bytes johnny-installed-snapshot-evidence-v1 followed by NUL;
8-byte big-endian byte-length + UTF8 approval.model_dump_json(); 4-byte big-endian
member count; for every exact payload 8-byte big-endian length + exact bytes in order.
sha256_ + SHA256 hex, ordinary strict EvidenceDigest validator. Tests independently
derive Expected framing, do not call product helper to form Expected.
Settle exact COMPLETE/correlation/evidence. Require exact SETTLED+COMPLETE record
matching full plan/ref/correlation/evidence; EXISTING is not success for a fresh
attempt. Then controller/native.verify_after/controller, only then return allbytes.
Existing checked close remains separate same-thread caller responsibility.

N13T3 before issue known validity/C13/controller denial -> zero ledger/reader effect.
Unknown ledger outcome, mismatched returned record, reader failure, settle refusal/
exception, postcheck drift or interruption -> retain exact ledger/approval and
native backing, poison terminal RECOVERY_REQUIRED, no bytes/retry/cleanup/fabricated
rollback. Do not re-settle an unknown outcome or rewrite terminal COMPLETE as if
rollback occurred. Known existing CLAIMED/terminal never rereads. Controller or
pins loss at intermediate/final boundary cannot yield success. Busy/close reentry,
wrong-thread/closed/reuse and interrupted outcome finite; successful close once.
Protected store constructor/close defaults preserved for all existing consumers.
Finite errors never include raw bytes/paths/approval/native details.

N13T4 discrimination: first clock expires_at-1 then second expires_at: issue may
happen, claim receives fresh expired value and refuses; reader/settle0. Mutating
second sample to first must turn this named cell RED then exact-restored GREEN.
Also legal not_before and expires_at-1 (and zero-length member),
max256 members and32768length, exact ordered multi-member+complete evidence. Reject
not-yet/expiry before issue; same-operation CLAIMED/terminal, claimEXISTING, wrong
grant/plan/correlation/lifecycle/evidence, missing/extra/reordered/wronglength/hash
payload, second-member failure no partialbytes, settleEXISTING/refusal/unknown,
pre/post pin drift, cancellation/timeouts/interruption and no postpoison retry.
Required named memory reverse mutations: move validity check after issue; accept
claimEXISTING; omit/reorder member; return before settle; accept settleEXISTING;
remove recovery retention; skip pre/post pin verification. Each RED/exactGREEN,
no bare assertion of names. Root independent different legal boundary mutation.

Execution ownership: retained /root/ticket30n4_peer_impl Luna/xhigh is source author
only, no Agent orchestration. Root AO/sole reviewer/orchestrator; distinct retained
ticket30_native_tools_review helper source evidence NOT qualified audit.
Initial author SOURCE_EDIT_ONLY after exact DOC/readback/Grant, no pytest/checker/
import/SDK/SQLite/commit until separately permitted. Root executes strict3 (modified
store/application/newtest), memory compile/import and focused fake test + N12six
suites under reviewed pre-import SDK/KnownFolder/SQLite/file/token/SCM/network/
process/ctypes/HANDLE/owner-init-before-property guard. Shared prior test-module
identity and owner guards remain; inspect any new fake class BEFORE allowlisting.
Do not interpret Python guard as OS isolation or qualified no-code review.
New behavior needs no ceremonial stub-first-red; all named mutation evidence required.
Root WIP checks diagnostic only; formal review/merge source must be committed.
Do not read active author worktree or statuspoll; await actual FINAL.

Forecast product180new+180modified/test450effective lines, docs only this ticket/
registry/review/checklist; no screenshots/dependencies. Growth>500effective triggers
responsibility/reuse structural review, not minify/arbitrary split or silent
permission to create files. No extra framework or unregistered output.
Initial command55child/60outer finite, uncapped cumulative/count but all historic
time/failures retained and identical unexplained failures not retried unchanged.

Fresh author allocation .worktrees/skill-improvement-30g-installed-snapshot,
branch codex/skill-improvement-30g-installed-snapshot; matching -review ownedRoot.
Context ctx-ticket30n13-installed-snapshot-20261021, bridgeNOT_REQUIRED same-lifetime.
Register both worktrees now before create, author/Root owners; Temp exact
LOCALAPPDATA/Temp/johnny30-installed-snapshot-owner-20261021 and
LOCALAPPDATA/Temp/johnny30-installed-snapshot-review-20261021; owner+purpose=N13,
TTL through final review/seal, teardown only after exact safe clearance, references/
Recovery override expiry and no denied-cleanup retry. Prior N12 allocation released
as immutable referenced hold, no deletion. Precise childGrant candidate
grant-ticket30n13-installed-snapshot-20261021 revision02 NOT_ACTIVE until committed
leaf/index DOC_PASS+Root exact baseline/roles/worktree/preflight readback.
Parent original localbatch, never an installed operational issuer Grant.

No actual Host/native campaign/SDK/SQLite file/SCM/account/ACL/service/config/
Registry/network/model/newfees/target/remote/push/release/deploy/formal activation/
receipt/admit_dispatch/native spawn effect. Only ordinary controlled local test/
compiler processes approved after guard review. First-CVQ order exception not
widened; Host qualification/30B43/TAL/R0/DAP/Recovery/checklist completion unchanged.
Return actual FINAL typed status/candidate/files/full check originals/deviations;
Root routes source review, same-ticket repair, exact local stage and next item.


## 30N12 — closure49 bounded source correction supplement

Same original30/PRD009/CHG009/Context04/uncapped batch and first-CVQ source-only
construction exception. Closure48 behavior/safety remains; this supplement only
corrects reuse applicability and adds missing discriminating cells, not a new
requirement, PRD, Host permission or budget. Source baseline is immutable candidate
ae9d195522069c94c8214f6e3cfb87609790e915; old a607 and failed evidence retained.
Root engineering review CHANGES_REQUESTED F1/F2/F3 independently reproduced all
three baseline probes RED (no Python denial), originals in registered RootTemp
n12-immutable-review-originals.json. E01 UNKNOWN/rawmissing remains independent.

Supersede closure48 CREATE-only correction scope for this additive repair:
MODIFY exactly:
- library/local_orchestration/grant_authority/windows_protected_store_native.py
- library/local_orchestration/grant_authority/windows_snapshot_native.py
- tests/test_grant_authority_windows_protected_store.py
CREATE/DELETE/export/dependency0. Composition file and all other old consumers/
tests unchanged. Same retained author/worktree/Context; reviewer Root, distinct
retained helper source evidence only. No author execution or commit until separately
bound after Root checks; independent ticket consistency review precedes Grant11.

F1: descriptor structural checks must not globally reject AUTO_INHERITED on a safe
unmanaged ancestor. Allow it only for ANCESTOR after existing owner/effective ACE
checks; managed root/state/DB remain protected exact two-ACE policy and explicitly
reject AUTO_INHERITED. Other defaulted/pending control restrictions unchanged.

F2: reuse the existing facts parser, not copy it. Add exact-bool keyword-only
allow_oversized_directory_metadata=False to _Win32SnapshotApi.query_facts.
Default preserves N10 behavior. Opt-in skips size cap ONLY for observed directory
metadata, never files. N12 opts in only for expected directory entries; its local
size check is DB-only. Expected-kind mismatch still refuses, so a directory flag
cannot disguise DB. All DB/read-size/controller/identity limits remain.

F3: distinguish explicit local malformed-return checks from unknown SDK execution.
One private local sentinel may map proven malformed structure/control/SID/ACE to
finite known protection refusal before constructor, reverse-close known owners,
no poison. SDK getter/conversion/copy exceptions (including ValueError and
interruptions) remain unknown/recovery; do not catch all ValueError as known.
Post-constructor any malformed/unknown outcome remains retained terminal recovery.
The existing bounded descriptor-copy helper's exceptions have no proven local
provenance and therefore stay recovery, including non-buffer descriptor objects.

Extend shared parameterized fakes/tests, no new script/framework: legal inherited
ancestor through actual composition; same flag managed/DB rejects; old shared
default rejects oversized directory; explicit directory opt-in accepts metadata;
opt-in cannot uncap files; N12 directory metadata above DB cap passes while exact
DB cap passes/cap+1 refuses; local malformed validity/control/null DACL/ACE refuses
without poison; SDK ValueError/interruption and postcheck-malformed retain/poison.
Keep Root baseline probes and replay after repair. Preserve original four mutation
groups plus Root different legal boundary; old ae9d mutation plan is NOT_EXECUTED
and must be rebound. No all-reject or weakened assertion as a substitute.

Root strict4 includes both protected-store sources, shared snapshot native and new
test; memory compile/import and original four fake suites remain. Add necessary
N10 reader/contracts consumer regression with exact fake-owner guard review before
execution; no real Native/SQLite stores or ledger suite. Preserve source identity,
module collection identity and full RED/exactGREEN output. Shared API default
compatibility must be shown, not inferred from unchanged consumers. Original P0,
resource/lifecycle/effect/cleanup/Host prohibitions and evidence holds all remain.

## 30N12 — fixed protected-store admission / closure48 historical baseline

Original30/PRD009/CHG009/Context04/runbook03 section2 and same uncapped
batch/first-CVQ source-construction order. Source baseline
a6071d5f2734091934a8645884c7db2068f62569 is engineeringhold only.
N11 final1d72c996/sealc1d875ec and independent43-original QA retained;
N10/N11/C13/ledger and all old consumers/tests remain unchanged.

CREATE ONLY:
- library/local_orchestration/grant_authority/windows_protected_store_native.py
- library/local_orchestration/grant_authority/windows_protected_store.py
- tests/test_grant_authority_windows_protected_store.py
MODIFY/DELETE/export/dependency0. AO bounded review selects three cohesive
responsibilities: platform file protection/ownership, fixed-source composition,
shared parameterized tests. No security helper framework, copied binary ACL
parser, ledger, generic factory, service loop, public Grant DTO or new engine.
Reuse installed pywin32 structured descriptor APIs, N10 _OwnedHandle/facts
where exact, N11 actual reader and C13 actual issuer check.

Private _open_protected_grant_store(cancellation:threading.Event,
deadline:float)->_ProtectedGrantStore has NO caller path/approval/peer/plan/
hash/marker. Imports and ordinary private constructors perform no native IO.
Exact Event, finite future float monotonic deadline <=60s, same issuing thread,
check before/after bounded operations, cancellation/deadline cannot return success.
Fixed order: actual N11 _read_installed_approval -> actual C13
_verify_current_wts_issuer_identity(approval.peer) -> native pre-admission ->
existing SQLiteGrantLedger(fixed_database_path) -> native post-readback ->
private lifetime-bound store. N11/C13 failure means zero later native/store calls.
Keep exact approval/peer/member binding private; no raw ledger getter or
issue/read/claim/settle forwarding, export, target/remote read, dispatch or receipt.
This is SOURCE_ONLY_UNQUALIFIED construction, not operational Grant issuance.

Resolve only native KnownFolder ProgramData through existing SDK bounded string
boundary; no env/cwd/caller/registry fallback. Exact local canonical drive path,
bounded UTF16, no UNC/device/relative/dot/ADS/reparse route. Derive only
JohnnyGrantAuthority/state/grants.sqlite3. Pre-created DB and managed directories
must exist; OPEN_EXISTING only, never let SQLite create a missing DB or change ACL.
Managed root must later be protected-at-creation by separately approved installer;
source fake evidence cannot prove no pre-existing dangerous native handle exists.

Retain volume root and every prefix through ProgramData/managed root/state/DB:
READ_CONTROL|FILE_READ_ATTRIBUTES, FILE_SHARE_READ|FILE_SHARE_WRITE, no SHARE_DELETE,
OPEN_EXISTING/OPEN_REPARSE_POINT; directory BACKUP_SEMANTICS, noninheritable owner.
Do not reuse N10 SHARE_READ-only open. Reuse _OwnedHandle once-close/alias checks
and query_facts(include_security=False) where exact; N10 finite64MiB DB admission
cap retained explicitly, never truncate/read DB contents or weaken N10 policy.
Actual path/volume/file-ID/disk/nonreparse checks before construction. Every opened
owner distinct, no raw/borrowed/invalid/pseudo alias, native owner uncertainty
retains original wrappers/backing and poisons; no raw close fallback or GC cleanup.

Protection via bounded valid immutable self-relative descriptor and existing SDK
ACL/GetAce getters; no copied registry binary parser or process/pipe-specific policy.
Managed root/state: protected nonnull DACL, exact SYSTEM/Admin full file access
ordinary allows with directory inheritance; DB same principals/full access with
no inheritance flags. No extra principal/object/conditional/unknown ACE, null DACL,
untrusted owner or mutable/unproven descriptor. SYSTEM/Admin are trusted TCB;
service SID RX does not constrain SYSTEM and no restricted SID policy is added.
Unmanaged ancestors are NOT forced into managed two-ACE/protected policy and
no OS ACL change is allowed. Still reject effective untrusted authority capable
of replacing/deleting/reparsing the retained child or changing parent owner/DACL;
identity pins alone do not prove safety. Ordinary ancestor allow/deny grammar and
effective-vs-inherit-only flags bounded; unsupported actual descriptors fail closed
UNAVAILABLE, not blanket ACL rewrite. Descriptor checks use the retained handles.

Before constructor, fixed -journal/-wal/-shm must all be absent. Presence or unknown
status refuses before constructor; never read/delete/rename/recover them. Do not
pin auxiliary files (would block legitimate SQLite journal cleanup). After constructor
check their absence again: residue/unknown means RECOVERY_REQUIRED. Pins for main
DB/parents remain alive throughout constructor and store lifetime, not check-drop-open.
Postcheck compares exact path/volume/file-ID/nonreparse/protection; DB size/time may
legitimately change due schema creation, but size must remain <=64MiB. Managed
parent metadata time need not remain unchanged when journal creation is legitimate.

Before constructor, known refusal closes known owners in reverse once; close
uncertainty retains exact owners/backing and poisons. Once constructor invoked,
exception/post-drift/aux residue/cancellation or ownership uncertainty implies
possible schema/journal effect: retain pins, any produced ledger/native backing,
return finite RECOVERY_REQUIRED; no fabricated rollback, close/retry/delete.
Successful private store holds pins and exact approval, exposes only checked
same-thread finite close; no auto destructor/finalizer or raw ledger escape.
Unknown close retains/poisons; known close releases each once. Errors/log/public
outputs contain no raw paths/approval/bytes/SID/ACL/native exception.
No grant state machine or second authorization source is introduced.

N12T1 real composition entry+real admission over shared fake native/ledger boundary:
N11->C13->pre->constructor->post exact trace; pins alive; exact64MiB legal DB,
empty DB, canonical Unicode paths, valid inherited ancestor versus managed policy.
No Actual->Expected copying. Record actual loaded source/candidate/exact3blobs.
N12T2 N11/C13 failure, caller argument/env fallback, missing DB, bad canonical
path/identity/owner/reparse/DACL/ACE/mask, cap+1, preexisting/unknown auxiliary:
constructor0, finite sanitized refusal, no hidden effect. Ancestor replacement
rights must fail; legal ordinary ancestor/managed policy must still pass.
N12T3 constructor exception, post identity/protection drift/aux residue,
deadline/cancel between operations/final return, alias/unknown ownership/close,
wrong-thread/reuse: exact retention+terminal poison, no retry/fallback/cleanup;
successful close once. Include interrupted native outcome, not Exception-only.
N12T4 author four groups RED/exactrestoredGREEN on final candidate:
protection/share-delete, preconstructor admission order, postcheck/residue,
ownership/recovery. Root different legitimate positive boundary door. A mutation
that merely changes failure classification is labelled as such, not escaped effect.

Newtest + existing N11 installed-approval, C13 issuer-identity and grant protocol
tests; strict3. Existing ledger test file creates real SQLite stores and is NOT
in this fake-only execution set; ledger/contracts remain unmodified, actual
signature and pure protocol constructor evidence are reused instead.
--strict --disallow-any-unimported --explicit-package-bases, memorycompile/import,
actual-loaded-source check, Native/file/registry/token/SCM/SQLite/process/network
denyguards. Test only approved fake boundaries; no real SQLite file/constructor
or SDK/native effect even in temporary directories. Existing native models/
normal constructors are preflight sources; new private constructors checked on
candidate before source approval, no fictional operational qualification
prerequisite to build this first capability. No public typed contract migration.
Forecast native400/composition180/tests450 effective lines: >500 is structural
review signal, not forced split/minify or permission for duplicate scripts.
TEST->A->B N/A: no old behavior moved/retired, old tests unchanged.

Execution allocation after E01: original Grant01 execution is suspended. Proposed
corrective Grant binds retained owner SOURCE_STATIC_ONLY (source edits, strict
checker and memory compile only; no pytest/candidate import/SDK execution).
Root owns pinned pre-import/fake-owner guarded child test execution, after owner
actualFINAL and exact source/ABI/fake-class inspection. Owner proposes four named
mutation groups; Root executes their RED/exactGREEN plus independent different
door on committed final candidate. Temporary WIP diagnostics never become review
authority or merge source. Original raw/effect UNKNOWN hold remains independent;
no retroactive permission, risk acceptance or qualification from this allocation.

Root AO/sole reviewer/orchestrator; retained /root/ticket30n4_peer_impl Luna/xhigh,
Root independent source review plus distinct retained sourcehelper evidence only.
Fresh owner .worktrees/skill-improvement-30g-protected-store / codex/same;
Root -review same baseline; Context ctx-ticket30n12-protected-store-20261021.
Reserve exact LOCALAPPDATA/Temp johnny30-protected-store-owner-20261021 and
johnny30-protected-store-review-20261021 before create, owner-specific TTL through
seal/hold; references/Recovery override expiry, no automatic deletion. N11 prior
allocations immutable-held, not reused. ChildGrant candidate
grant-ticket30n12-protected-store-20261021 revision01 NOT_ACTIVE until exact DOC,
preflight/allocation/readback; direct same-lifetime bridgeNOT_REQUIRED.
Batch uncapped historical accounting retained; child55/outer60 initial finitebounds.
No actual Host/Native campaign/install/security/account/ACL/service/config/registry/
remote/model/network/newfees/push/release/deploy/formalactivation/deniedcleanupretry.
30B43/TAL/R0/DAP/Recovery and unchecked checklist states unchanged.

## 30N11 — fixed installed-approval registry source / closure47 proposal

Original30/PRD009/CHG009/Context04/runbook03 section2, same uncapped local batch
and first-CVQ source-construction order, no new PRD/authority engine. Baseline
43abc3cc81ee2c162d95035dd5f2e62cfd60745b is engineeringhold only. N10 exact
source/archive seals1c9cc2df/2660b9ae and QA a9436988 retained, not Host qualification.

CREATE ONLY:
- library/local_orchestration/grant_authority/windows_approval_registry.py
- library/local_orchestration/grant_authority/windows_installed_approval.py
- tests/test_grant_authority_windows_installed_approval.py
MODIFY/DELETE/export/dependency0. Native registry handle/security/buffer boundary
is distinct from N10 file IO; decoder only composes existing GrantPlan,
AuthorityPeer, N9 _SnapshotBlobMember and existing bounded duplicate/depth JSON
helpers. No copied ledger, file reader, generic registry API, service loop,
new Router/Gate/public Grant DTO or arbitrary commands. Existing tests unchanged.

Private entry _read_installed_approval(cancellation:threading.Event,
deadline:float) returns one private immutable validated record or raises a finite
sanitized error. Imports/constructors perform no native IO. Exact Event, finite
positive future monotonic deadline at most60s, single issuing thread, single-use
native read, check controller between all bounded operations. The caller supplies
NO path, expected digest, plan, approval marker, registry hive, service name,
Grant ID or observation. Private decoded values remain SOURCE_ONLY_UNQUALIFIED
and confer no permission; there is no production consumer/export in this slice.

Compiled product namespace JohnnyGrantAuthority, no project/model/ticket literal.
The fixed bootstrap value is a REG_BINARY UTF8 JSON value named ApprovalV1 below
HKLM SYSTEM/current selected ControlSet/Services/JohnnyGrantAuthority/Parameters.
This is construction data only: no real key/value/service/account exists by
assertion, and its actual creation/approval/protection needs the later exact
Owner install package. Never choose a caller/environment/DataRoot/root-relative
fallback. Resolve SYSTEM Select Current as a bounded native REG_DWORD1..999;
retain opened key handles and derive ControlSetNNN without trusting environment
or a transparent CurrentControlSet link. Explicit registry64 view. Open existing
keys read-only, no create/set/delete/flush/connect/remote-registry or impersonation.
Reject registry links at each actual opened component; do not follow them.

Read protection before reading approval contents: same retained native handles,
owner SYSTEM or BuiltinAdministrators, present nonnull DACL. Every fixed ancestor
must deny effective write/owner/DACL/delete/link/subkey-creation authority to
untrusted principals; native unknown/conditional/object ACE shape fails closed.
Allow only known ordinary ACE grammar, preserve deny semantics conservatively;
inherited-only entries do not count as effective grants. Owner/protection/native
metadata absence refuses. Leaf Parameters carrying ApprovalV1 requires protected
DACL, only SYSTEM/Admin full-control ordinary allow entries, no Agent/controller/
Users/readable service-data grant. Do NOT infer service-self-write prevention:
LocalSystem issuer is trusted TCB under existing AC17R14. Never add a restricted
service SID policy or weaken C13. Fixed ancestors with a genuine unsupported
descriptor return finite UNAVAILABLE; no broad HKLM ACL change is authorized.

Registry Native boundary uses fixed preallocated buffers, not unbounded SDK
RegQueryValueEx allocation/retry loops: ApprovalV1 max262144 bytes; value type
REG_BINARY only; Select Current exact DWORD4 bytes; security descriptor bounded
<=65536; opened prefixes bounded by fixed namespace. Validate exact native status,
type, actual returned byte count and tuple/buffer/handle shapes before decoding;
no capacity-as-length, truncation or value-to-string transform. MORE_DATA refuses,
never allocate supplied size/retry. Native APIs remain fake in tests, not executed.
Capture native key lastwrite raw FILETIME/protection before/after, re-read Select
Current under its retained handle, and refuse selection/protection/value/metadata
movement; do not claim multi-object atomicity or operational race qualification.

Close ONLY exact owned HKEYs once using their proper native close operation,
never CloseHandle/raw fallback/GC. Unknown return/close/alias/exception retains
original owners/native output holders+buffer in an explicit bounded recovery hold
and poisons further use. Cancellation/deadline/invalid input refuse before next
effect; incomplete/unknown outcome cannot return payload. Retain existing Recovery
and evidence, no cleanup retry/expiry deletion or clearing poison to rerun.
Failure/error/log/public output contains no paths, bytes, SID/DACL text or native
exception. The private success record alone retains its exact validated path/SID
fields for later issuer binding; no raw registry bytes/SDDL/exception is exposed.

One private strict record schema_revision1 / approval_ref / grant_ref /
operation_ref / plan:GrantPlan / peer:AuthorityPeer /
members:tuple[_SnapshotBlobMember,...] / plan_digest and literal source scope.
Reuse existing metadata types; no new role/public result statuses/Grant lifecycle.
Normal constructors and JSON validation, reject bypass/subclasses/extra/duplicate/
nonfinite/depth/invalid UTF8 and missing fields, no normalize/transform.
1..256 members, unique blob_ref, same-path expected source identity must agree;
no first-match-wins. plan_digest must equal existing grant_plan_digest(plan);
only READ_REVIEW_SNAPSHOT in this initial fixed read plan. Other valid enum values
are unsupported here, not silently activated or removed from old enums. No
caller-provided self-consistency is provenance: only this factory's fixed native
read supplies bytes, and even its result is unqualified private construction.
Future issuer must independently verify C13/current service, exact SCM/PythonClass/
startup/runtime/import/code/config protection, protected Owner acceptance,
peer/session membership and durable claim-before-read before any real operation.
This slice does not issue/read/claim/settle SQLite, invoke N10, run a service,
read target/remote, dispatch a tool/Agent or generate receipt/approval UI.

N11T1 real entry+real decode over fake native boundary: independent literal valid
protected record reconstructs exact plan/peer/member values unchanged; min/max
source sizes/members, Unicode and empty N9 ranges, legal exact262144-byte payload,
normal cancellation/deadline/close once. Expected independently pinned fixtures.
N11T2 forged caller argument/API route, caller-root/env fallback, missing/wrong/
mutable/extra-principal leaf protection, owner/null/unprotected DACL, link/view/
Select drift, invalid native count/type/status/handle/descriptor, payload overcap
and malformed JSON all refuse BEFORE exposing bytes/record; assert exact order
and no issue/claim/read/dispatch/process/network/OS mutation.
N11T3 duplicate/mismatched blob/source identity, wrong digest/operation/scope,
pre/post key/protection/selection drift, close/alias/owner uncertainty and
same-thread/reuse/deadline negatives preserve exact holds+poison and no payload.
N11T4 author named source-protection, byte-count cap, exact membership/digest and
recovery mutation RED/exactrestoredGREEN on finalcandidate; Root different legal
positive door. Read original unfiltered outputs, bind actual loaded source/3blobs.

Focused newtest + existing N9 snapshot-contract and C8 service-wire tests; strict3
--strict --disallow-any-unimported --explicit-package-bases, memorycompile/
import under native registry/file/SCM/token/ctypes/process/network denyguards.
No actual Registry/SCM/Host API or SDK constructor; fake boundary must model actual
native return/count/owner semantics, not generated-stub assumptions. Forecast
native450/decoder180/test500 effective lines is structural-review signal, not
minification/forced splitting. Shared fake/parameterized cases, no permanent
one-off probe pile/source prompt/work-order narratives. TEST->A->B N/A no old
behavior moved/retired; no existing consumer or public gate is changed.

Root AO/sole reviewer/orchestrator; retained /root/ticket30n4_peer_impl approved
Luna/xhigh, distinct retained sourcehelper evidence only. Proposed owner allocation
.worktrees/skill-improvement-30g-installed-approval / codex/same, Root matching
-review; Context ctx-ticket30n11-installed-approval-20261021. Reserve exact owned
Temp johnny30-installed-approval-owner-20261021 and -review-20261021 under
LOCALAPPDATA/Temp beforecreate, TTL through reviewseal, active holds overrideexpiry.
Prior N10 allocations immutable-held, no reuse/deletion. Grant candidate
grant-ticket30n11-installed-approval-20261021 revision01 NOT_ACTIVE until exact
DOC/constructor/preflight/allocation; bridgeNOT_REQUIRED same-lifetime direct.
Uncapped historical accounting preserved; child55/outer60 initial finitebounds.
No real Native/Host campaign, install/service/registry/security/account/ACL changes,
remote/model/network/newcost/push/release/deploy/formalactivation/deniedcleanupretry.
30B43/TAL/R0/DAP/Recovery and unchecked checklist states unchanged.

## 30N10 — same-process bounded snapshot reader / closure46 proposal

Original30/PRD009/CHG009/Context04/runbook03 sections2/3, uncapped local batch
batch-checklist-local-20261019-uncapped and unchanged first-CVQ minimalreadonly
source construction order. Baseline fcb373a680b21397bf0e22d7ec8b8894c0eb00c5,
engineeringhold only. N9 exact constructors7cafff9a/e9092823, N7/N8 codecs,
H11 readcomposition and all old tests/source remain unchanged. No new PRD/Grant
protocol/result envelope/Router/authority source or engine. This does NOT authorize
actual Native calls: tests replace native boundaries; Host qualification remainsOPEN.

CREATE ONLY:
- library/local_orchestration/grant_authority/windows_snapshot_native.py
- library/local_orchestration/grant_authority/windows_snapshot_reader.py
- tests/test_grant_authority_windows_snapshot_reader.py
MODIFY/DELETE/export/dependency0. Three responsibilities are justified by bounded
Architecture review: no existing checked same-process Python file-read ABI exists.
Do not copy the600line message-pipe class or C# reader into orchestration.
Reuse N9 ordinary models/scalar meanings, existing _FILETIME rawlayout and retained
owner/thread/deadline/completion semantics; no second ownership/policy framework.
Private native file facts/finite errors are implementation details, not new public
authorization DTOs. They must be typed, bounded and tested, not dynamicdict/Any.

Internal operation _SnapshotBlobReader(member:_SnapshotBlobMember,
cancellation:threading.Event, deadline:float).read()->bytes. Constructors/imports
perform no Native IO. Exact normalN9 member revalidation before IO; reject invalid,
subclass/bypass-built or mutated values, invalid event, nonfinite/nonpositive/expired
monotonicdeadline and wrong thread; deadline at most60seconds ahead at admission.
Reader single-use/nonreentrant; failure or success cannot reopen/read again.
No incoming external path/offset/hash/handle/approval field. Member is an internal
issuer-resolved expected value, NOT read authority. This unexposed primitive cannot
prove provenance and has no production caller in this slice; later protected
issuer membership resolution must occur BEFORE it is called, with no caller DTO
shortcut. Do not claim this construction has enabled a trusted source entry.

Native leaf alone owns exact file/directory/event handles, OS ABI and completion.
All imports/constructors no-effect. Open only requested canonical localdrive path,
OPEN_EXISTING, noninheritable, OPEN_REPARSE_POINT/BACKUP_SEMANTICS; final file
READ_CONTROL|FILE_READ_DATA, shareREAD only (no write/delete share), OVERLAPPED.
Retain and check every opened directory prefix with no delete sharing through
the entire operation, reject reparse/alias/type escape and wrong finalpath; do
not reopen by pathname to hash. Bound prefixcount<=256 before effects; deeper
paths explicitly unsupported in this construction, not silently truncated.
Regular disk file only. Internal Win32 extended-prefix handling is exact and
explicit, not Unicode normalization/casefold/firstmatch of caller paths.
Compare exact expected canonical spelling after documented extendedprefix removal;
a differently spelled actual path fails closed, not silently normalized.
No protected-ancestry claim without observations.

Capture before/after on retained final handle: attributes, creation/write raw100ns
FILETIME (no PyDateTime rounding), size, volumeSerial, fileID, finalpath, ownerSID,
owner+DACL descriptor digest. Reuse _FILETIME layout and validate native integer/
tuple/buffer/handle shapes at boundary. Owner/DACL required(non-null DACL);
descriptor SHA256 is exact UTF8 of native OWNER|DACL SDDL text from
ConvertSecurityDescriptorToStringSecurityDescriptor revision1; no normalization.
This is explicitly its serialization, not proof the old .NET formatter is byte
equivalent. Cross-formatter qualification remainsUNVERIFIED; don't reuse a digest
by assuming SDDL text equivalence. Compare initial facts to all N9 expected fields,
and complete before/after stablefacts (access time is not a stable invariant).
Identity/owner/descriptor/size/path mismatch refuses, even matching content hash.

Reader streams entire source<=67108864 through the SAME retained file handle,
fixedchunks<=32768, hashes complete file and captures ONLY pinned memberrange
<=32768. Actual approved inventory/sizes remainUNKNOWN, no assumption every source
fits one frame. Check trueEOF with extra1byte including emptyfile; detect premature
EOF/truncation/growth and wholefile changes outside capturedrange. Wholefile digest
AND member digest AND exact returnedlength AND all postfacts must match before
any bytes escape. Emptyfile/member SHA rules preserve valid N9 constructor cases.

Preallocate and retain exact overlapped readbuffer/OVERLAPPED until completion.
ReadFile status/capacity are not bytes transferred: use GetOverlappedResult actual
count (0..requested); exactpositive shortreads may advance, premature0 refuses.
Check one controller cancellation event/finite monotonicdeadline before/after each
bounded step and during pending polling. Each wait bounded, no sleep/unboundedjoin.
Same-issuing-thread CancelIo is a request only. Cancel/drain bounded<=1000ms and
separate completion observation required; knowncompleted abort can teardown once,
unknown/incomplete/exception retains original file/event/ancestor owners+buffer+
OVERLAPPED in explicit recovery hold, poisons future reads. Close only ORIGINAL
owners exactlyonce after completion; closeexception/aliasdrift also retained and
no rawhandle fallback/retry/GC/policy change. Finite sanitized failure, no paths/
contents/SDDL/nativeexception text in result/error/log. No nonempty bytes success
or empty-success fallback on failure. No claim synchronous metadata syscalls have
qualified hard wall bounds; actual Native qualification is still required.

N10T1 positive fake-native endtoend REAL leaf+reader: normal/full/internalrange,
emptyfile/member, maximumslice, Unicode path exact, immediate/pending and shortread.
Expected hashes come independently from pinned fixturebytes, not Actual.
N10T2 malformed/bypass input shapes, wrongthread/reuse, bad native tuples/status/
count/bufferidentity, reparse/path/disk/directory/owner/DACL/volume/fileID/size/
attribute/rawcreation/rawlastwrite mismatch before/after and deadline/cancellation.
N10T3 wholefile tamper OUTSIDE capturedrange, rangehash/length mismatch,
prematureEOF/growth and partial/pending timeout, observedabort vs unknowndrain,
close/alias uncertainty. Assert no bytes escape, exact effects/order, original
owners/buffer/overlap retained and refused reuse; user/unowned assets neverdeleted.
N10T4 named author reverse mutations for wholehash, identity/postfacts, exact
completioncount and recovery hold RED/exactGREEN; Root different legitimate door.
Tests must reach native-boundary leaf, not merely stub reader to expectedfixture.
Use shared parameterization/helper in this suite, no external repo/clone/process/
browser/container/server/OS calls or newframework/permanent probe artifacts.

Existing typed input constructors are reviewed and exercised before delegation;
new private ABI internals are built/tested under that established N9 input contract,
not asserted to preexist. Constructor-only source ordering does not waive final
readbehavior gates. Strict3 --disallow-any-unimported --explicit-package-bases,
newtest + N9 tests + existing C8 tests, memorycompile/actualsource/import under
Native/socket/subprocess deny guards; normal unreduced pytest, short caseIDs.
Forecast native<=400effective/reader<=220/test<=480; signal not forcedsplit/minify.
Over500 triggers existing structuralreview, not newGate. No gratuitous source
narrative/prompt/ticket identifiers, dependency or baseline test edits.
TEST->A->B N/A: no old behavior moved/retired; inherited behavior untouched.

Root AO/solefinalreviewer/orchestrator; retained /root/ticket30n4_peer_impl uses
approvedLuna/xhigh in a fresh owner allocation after N9 immutablehold; distinct
sourcehelper. ctx-ticket30n10-snapshot-reader-20261021.
Proposed author .worktrees/skill-improvement-30g-snapshot-reader codex/same and Root
matching -review; registered Temp johnny30-snapshot-reader-owner-20261021 and
-review-20261021 to reserve beforecreate. Exactowners+TTLthroughreviewseal, active
Recovery/evidenceholds overrideexpiry; no cleanupclaim/expirydeletion.
Grant candidate grant-ticket30n10-snapshot-reader-20261021 revision01 NOT_ACTIVE
until DOC/D8/asset/actualexistingconstructor preflight. Bridge NOT_REQUIRED direct,
no queue/receipt/gateway invented. Return candidate/files/checks/findings/deviations
and original raw commands/terminal outputs; preserve uncapped historical failures.
Child55/outer60 finite commandbounds, diagnose no-progress repeatedfailures.
No Host/nativecampaign/SCM/service/account/security/ACL/install/model/provider/
network/newcost/push/release/deploy/formalactivation, no refusedcleanupretry,
30B43/TAL/R0/DAP/Recovery statechange or checklist/fullTicket30completion.

## 30N9 — bounded snapshot membership values / closure45 proposal

Original30/PRD009/CHG009/Context04/runbook03 sections2/3 and existing12localbatch
batch-checklist-local-20261019-uncapped; first-CVQ minimalreadonly source-order
exception unchanged. Baseline f6e6b946b916afa60e0eaef9808527b2fa4f3635 is
engineeringhold only, not main/qualified source. N8 wire seal d5b099b5/452a4bbd
and N7 codec are reused unchanged; do not alter their cap/fields or oldtests.

Necessary gap from bounded query56ed1491: native same-process file reader needs
fixed wholefile identity plus opaque blob/range membership; C8 JSON/GrantRecord
and caller markers confer no provenance. GrantPlan/readprotocol has no snapshot
blobfield; do NOT expand that public wire or pass32KiB through16KiB pipeframe.
Native tool callback will later resolve opaqueID inside protected ownership;
no request accepts caller path/offset/hash/content or mints authority.
This slice ONLY constructs its reusable immutable value contracts, not a reader,
approvalstore/service/Grantissuer/Host effect or positive trustedGrant evidence.

CREATE ONLY library/local_orchestration/grant_authority/windows_snapshot_contracts.py
and tests/test_grant_authority_windows_snapshot_contracts.py.
MODIFY/DELETE/export/dependency0; no ABI/reader stubs or duplicate parser/runner.
Two private named models, reusing _StrictModel, _CanonicalSid, C8
_ObservedSha256, windows_peer _CanonicalWindowsPath/_Uint32/_Uint64 and
existing CVQ OpaqueMetadataId. C8 _ObservedEnrollmentFile is deliberately NOT
subclassed/copied as another C8 observation: its file size1..64MiB excludes
empty sourcefiles, while snapshot membership must represent size0..64MiB.
Reuse its scalar meanings; distinguish expected facts from OS observations.
No new observation/qualification/result/Grant model or state machine.

_SnapshotSourceFile(_StrictModel) EXACT fields:
path:_CanonicalWindowsPath; sha256:_ObservedSha256;
size_bytes:strict exactbuilt-in int0..67108864;
owner:_CanonicalSid; descriptor_sha256:_ObservedSha256;
volume_serial:_Uint32; file_id:_Uint64.
All string/int inputs require exact builtin before existing adapters; reject
bool/subclasses/coercion, preserve exactcodepoints/path/digest with no transform.
For size0, sha256 must be SHA256(emptybytes), intrinsic content consistency.
Frozen/extra-forbid/revalidatealways inherited, ordinary constructors only.

_SnapshotBlobMember(_StrictModel) EXACT fields:
blob_ref:CVQOpaqueMetadataId; source_file:_SnapshotSourceFile;
offset:strict exactbuiltin int0..67108864;
length:strict exactbuiltin int0..32768; sha256:_ObservedSha256;
scope:Literal SOURCE_ONLY_UNQUALIFIED default samevalue.
blobref/digest/scope exactbuiltinstr, source_file exactnormal model instance
or exactdict validated by its ordinary constructor; no bypass/create/update/cast.
offset+length must be <=source_file.size_bytes; zero-length blob SHA256(empty).
When offset0 and length==source_file.size_bytes, blobsha==sourcefilesha.
A bounded blob is allowed to be one pinned range of a larger sourcefile; exact
wholefile identity/digest and fixedrange/digest must both survive later native
read. This does not infer any actual approved snapshot inventory or filesizes.
No normalization/partialhash-as-wholehash/path-from-caller/implicit membership.
No claimed approved/source-only boolean can authorize a read; all values remain
SOURCE_ONLY_UNQUALIFIED. Actual issuer-owned binding/native proof laterrequired.

N9T1 ordinary constructor/roundtrip exactempty/full/range and32768 boundary,
source file up to64MiB with in-range pinned slice, genericfictional values only.
N9T2 reject each invalidfield shape/null/bool/subclass/overflow, wrongdigest/
path/SID/opaqueid per reused grammar, extra/mutability and nested badfacts;
malformed bypass inputs are rejection evidence only.
N9T3 crossfield negative range end/zero digest/fullrange digest and legal
neighbors, frozen source binding, no policy/authority promotion by values.
N9T4 named bounded reverse mutations for source-size/builtin check/range/digest
conditions RED/exactGREEN, plus Root different legitimate-case counter.
No ceremonial nonexistent-newmodel Stub-red requirement. Constructor-only
first construction follows same admitted N7 source-order method; Root verifies
new ordinary constructors before any later reader logic is admitted.
No public effect port in this slice, TEST->A->B N/A(no responsibilitytransfer).

Focused pytest newtest + existing windows_service C8 value tests if applicable;
strict2 --disallow-any-unimported --explicit-package-bases, memorycompile/import
under denied Native/socket/subprocess guards, actualloadedsource/Gitblobs.
Use default normal unfiltered pytest output; verbose only for a diagnosed
small namedcell, not verboseentiresuites. ExplicitparameterIDs/fullraw preserve
errors without massive binaryassertion dumps. No permanent duplicate helper.
Forecast product<=160effective/test<=260; structural signal not forcedsplit.

Root AO/solefinalreviewer/orchestrator; retained /root/ticket30n4_peer_impl
approvedLuna/xhigh, existing distinct sourcehelper. PriorN8 allocation/context
immutableheld; fresh ctx-ticket30n9-snapshot-contracts-20261021, author
.worktrees/skill-improvement-30g-snapshot-contracts codex/same, Root matching
-review. Registered fresh Temp roots to reserve before creation:
johnny30-snapshot-contracts-owner-20261021 and -review-20261021; exactowners,
TTLthroughreviewseal/holds, no expiration deletion or refusedcleanupretry.
Grant candidate grant-ticket30n9-snapshot-contracts-20261021 revision01
NOT_ACTIVE until exact DOC/D8/asset/ordinaryexisting-base constructor admission.
Original batch uncapped history, failures/UNKNOWN unchanged, child55/outer60
finite bounds; no new fees/blank privileges. Return typed result with candidate/
files/checks/findings/deviations/raw refs; author cannot approve/integrate.

No actual file/nativeapi/Host/process/pipe/service/account/security/ACL/rights/
install/network/model/Provider/cleanup effects. Local compiler/test control
children only. No push/release/deployment/activation or qualifiedCVQ/30B43/TAL/
Recovery relief/checklistcompletion. After reviewed contracts, freeze a bounded
same-process native reader/cancel/drain/retainedowner failure seam in original
Ticket30 and derive precise nextscope, not an additional authority system.


## 30N8 — native control-wire request builders / closure44 proposal

Same original30/PRD009/CHG009/Context04/runbook03 minimalreadonly entry and
batch-checklist-local-20261019-uncapped; first-CVQ source-order exception only.
Baseline9c999a1ea3d819c3454f36ab39b9fddb1192ff5f engineeringhold, not main/
trustedissuer/Host source. N7 finalc3ff3fb1 codec is reused; do not rewrite it.
Native exactgenerated controlschemas sealed3bd6495a, originally same offline
binaryf6dbf48c/version0.163.0-alpha.10.2, DATA_MAPPING_PASS; no liveHosttested.
Schema supported initialization clientInfo(name/version), capability
experimentalApi; DynamicToolSpec function(name/description/inputSchema/type),
thread SandboxMode read-only; initialized notification methodONLY; turn input
text with text_elements. Root actual source span read, no guessed currentdocs.

Necessary gap: currentcodec only handles incoming tool calls/results; minimal
native adapter still lacks its fixed initialization/thread/turn outgoing frames.
Build these as same nativewire responsibility, not another Runner/state-machine/
configuration loader. No new Grant issuer or independent policy engine.

MODIFY ONLY library/local_orchestration/readonly_review_host.py:
bounded imports/adapters/private serialization helper and append four private
builders below. Existing _SnapshotToolCall, decoder/encoder bodies/constants
must remain semantically/AST unchanged; existing605-effective test file remains
EXACT41223d3f34d8b3b19e58e2f1e157e321ff51a429, not modified.
CREATE ONLY tests/test_readonly_review_control_wire.py, separate outgoing
control-request AC from existing incoming tool/result matrices; no helper/
browser/server/PNG fixture duplicate, exports/dependencies/DELETE0.
Reuse _SnapshotRequestId/_validated_native_identifier, existing CVQBoundedText
(1..128characters) and OpaqueMetadataId TypeAdapter.json_schema for fileID.
Exact builtin int/str checks before adapters; no Any/cast/model_construct/
normalization/ambient model/profile/config reads. Model/provider/version are
bounded opaque inputdata, not fixed vendor names or capability/authority proof.
No new typed model/DTO needed; real existing scalar constructor preflight first.

_encode_initialize_request(request_id:_SnapshotRequestId,
client_version:CVQBoundedText)->bytes|None:
id/method initialize/params clientInfo{name:johnny-readonly-source,
version:exactvalue},capabilities{experimentalApi:true}. No otherfields.
_encode_initialized_notification()->bytes:
exact {"method":"initialized"} plus LF, no id/params/auth.
_encode_thread_start_request(request_id:_SnapshotRequestId,
model_id:CVQBoundedText,provider_id:CVQBoundedText)->bytes|None:
id/method thread/start/params exact model/modelProvider values,
allowProviderModelFallback:false, ephemeral:true, approvalPolicy:never,
sandbox:read-only, environments:[], experimentalRawEvents:false,
dynamicTools exactly one function read_snapshot_blob with technicaldescription
"Read a bounded immutable snapshot blob by opaque identifier." and inputSchema
object with file_id existingCVQschema, required[file_id],additionalProperties:false.
Do not add config/cwd/permissions/capabilityRoots or guessed feature flags.
_encode_turn_start_request(request_id:_SnapshotRequestId,
thread_id:bounded_native_identifier,input_text:CVQBoundedText)->bytes|None:
id/method turn/start/params threadId exactvalidated, input exactly one
{type:text,text:exactvalue,text_elements:[]}, approvalPolicy:never,environments:[].
No model/sandbox/permissions/config/path/role override. Text is callerdata,
not source-code Owner instruction or policy. Unicode preserved, no normalization.
Each frame compact UTF8JSON+singleLF <=existing65536 limit; invalid values incl
subclasses/bool/null/overflow/empty/overlong returnNone, no truncation.
Only byte construction, no init/session/model action. These readonly/fallback
fields are requested metadata, NOT proof nativeHost honors them or closes tools;
actualconfig/roster/OS protection/observer/native mediation remain UNVERIFIED.

N8T1 independent literal initialize/initialized frames, exactunicode version and
signed64/stringIDs/validlimits; literalExpected not derived from functionActual.
N8T2 independent thread/turn frame/schema/field checks, fileID schema matches
existingCVQ contract; caller cannot inject alternate method/tools/permissions/
config or silently enablefallback/write; legitimateprofile values stillaccepted.
N8T3 negative primitive/subclass/bound/input matrix, preservedUnicode/newlines,
deterministic exactbytes, import effectguards; no native calls/paidAPI/network.
N8T4 discriminating method/policy/tool/boundary reverse mutations -> namedRED/
exactrestoredGREEN plus Rootdifferent legitimate gate. Preserve fullraw, use
bounded pytest formatting/explicitparameterIDs; do not emit massive binary
failure values or diagnostic outputs outside registeredTemp. No evidence hiding:
original raw failures retained even if displayed output is bounded.
Focusednewtest plus existingN7/protocol219 affectedcells, strictproduct+newtest
(no Any/skippedimports), compile/loadedsource/Gitblob and oldfunctionAST/source
identity checks. Newfeature no invented defective-baseline stub-red claim.
TEST->A->B N/A(no responsibility transfer or testretirement).

Root architecture/solefinalreviewer; retained /root/ticket30n4_peer_impl
approvedLuna/xhigh implementer after N7 immutablehold, different existing
sourcehelper. Fresh .worktrees/skill-improvement-30g-readonly-control-wire
codex/same, Root matching -review; freshContext
ctx-ticket30n8-readonly-control-wire-20261021. Temp roots
johnny30-readonly-control-wire-owner-20261021 and -review-20261021; namedowners,
TTLthroughreview/seal, evidence/Recovery holds overrideTTL, no deletion.
Forecast product+<=130effective/test<=320; review structural/reuse signal
without forcedsplit/minification. Entire originalbatchhistory/uncappedpolicy,
child55/outer60/resources/raw/diagnose unchangedfail preserved, no reset.
Grant candidate grant-ticket30n8-readonly-control-wire-20261021 revision01
NOT_ACTIVE pending DOC_PASS/D8/fresh Gitcontainment/baseconstructor preflight.
No neednewOwner approval for this necessary bounded source-only construction.
No actual Host/server/thread/turn/model/process/pipe/security/SCM/account/ACL/
install/rights/network/cleanup/push/release/deploy/activation, qualification,
30B43/TAL/Recovery relief or checklistcompletion.


## 30N7 — bounded native snapshot-tool wire codec / closure43 proposal

Original30/runbook03 minimal readonly adapter, existing12 local batch and first
CVQ source-order exception; originalPRD/CHG/SPEC/Context references unchanged.
Baseline7e3c12197bb127313813f7e968c12d3ba5658088 engineeringhold includes exact
CVQ24c package; not qualified/integrated source. ActiveH10I closure42/ticket14e05a54/
correctiond60f27c4 remain bound to own immutable inputs; this independent additive
source slice does not revoke/redefine that scope or alter its authorworktree.

Reuse determination: N6 owns finite Responses HTTP stimulus, not native dynamic
tool request/result wire. tests/staging narrow search tools/list/tools/call/jsonrpc/
Streamable/MCP found no existing matchingcodec; do not build anotherMCPserver/
HTTPframework. Native app-server dynamic tools are already supported in exact
offline-generated0.163.0-alpha.10.2 schema, executableSHAf6dbf48c... . Root seal
af639057 / prior d9e7c527 contains original ServerRequest,DynamicToolCallParams/
Response,RequestId data/digests; official docs URLs there. This is versioned wire
design evidence only, not trusted/enrolledbinary, native dispatch or Host proof.
Prefer that native protocol over duplicate MCP/broker; later stdio/launch/control
channel and restriction qualification remain separate necessary boundaries.

CREATE EXACT library/local_orchestration/readonly_review_host.py
and tests/test_readonly_review_host_wire.py. MODIFY/DELETE0, exports/deps0.
New module is originalplanned readonly adapter wire boundary ONLY; no process/
filesystem/socket/provider/CLI/config loading/runner/qualification invocation.
New test file separates native request/result codec from N6 Responses HTTPfixture;
reuse common production grant_authority.client _unique_object,
_reject_json_constant,_check_json_depth (generic JSON validation only), existing
CVQ QualificationModel/Digest/OpaqueMetadataId, hashlib/base64/json/Pydantic.
No copied JSONdepth/duplicate parsers, browser/mock/PNG helpers or framework.

Private immutable _SnapshotToolCall(QualificationModel) fields:
request_id = exact strict signedint64 or bounded_native_identifier;
thread_id,turn_id,call_id = bounded_native_identifier;
file_id = existing CVQOpaqueMetadataId;
scope Literal SOURCE_ONLY_UNQUALIFIED defaultsame.
bounded_native_identifier is exactstr1..128 ASCII letters/digits/underscore/
dot/colon/hyphen only; native IDs may startdigit, unlike CVQfile IDs. No coercion,
normalization, Any/cast/model_construct or ambientrole. Unknownfields reject.
This is a bounded native wire profile, not all arbitrary JSONRPC implementation
conformance. Actual CLI response compatibility remains UNVERIFIED until qualified.

PhaseA CONSTRUCTOR_ONLY: only these private aliases/model with ordinary validators
and pure constructor/roundtrip/negative tests, no JSONcodec/effect/functionstub.
No publicsuccessDTO changes. Root must independently construct/strict/mutate
private bounds and seal exactPhaseA before the same Grant may rebind PhaseB.
This is restricted construction order using existing localbatch precedent, not
waiving complete typed preflight, new authority or stage. No fake first-red
claim for absent new code, budget/history unchanged.

PhaseB private functions, after reviewed constructorbaseline:
_decode_snapshot_tool_call(frame:bytes,expected_thread_id:str,
expected_turn_id:str)->_SnapshotToolCall|None.
Accept exactly one complete UTF8 JSON object <=65536bytes; optional one terminal
LF delimiter only, no secondobject/trailingdata. StrictJSON commonhelpers reject
duplicates/nonfinite/depth; all structural/domain input validated at boundary.
Exact topkeys id/method/params; method item/tool/call only. Params exact required
arguments/callId/threadId/tool/turnId, optionalnamespace; namespace absent/null only,
tool read_snapshot_blob only; arguments exactly {file_id: CVQOpaqueMetadataId}.
Reject method/tool/namespace/unknownkeys/wrongthread/turn/invalidRPCid orshape,
invalidUTF8/control/oversize/exception with None. Native IDs validated before
exact expected comparisons. No arbitrarypath, command, callback, permission or
actual refusal evidence: decoder refusal is NOT proof Host denied anything.

_encode_snapshot_tool_result(call:_SnapshotToolCall,expected_file_id:OpaqueMetadataId,
expected_digest:Digest,content:bytes)->bytes|None.
Revalidate exactcall class/ordinary constructor, fileID and digest; source content
exactbytes0..32768, sha256 must equal expectedDigest and requestedfileID exact.
No truncation/retry/normalization. Valid output canonical compact UTF8 JSON+LF,
top id/result; result contentItems=[{type:inputText,text:<compactJSON>}],success=true.
Innertext exact {file_id,sha256,encoding:base64,data:<base64 originalbytes>}.
Return None for mismatch/invalidinput, never filesystemread or successauthority.
success only native wirecontent flag, not Grant/readapproval/CVQReport/admission.
ExpectedIDs/digests are assertions until genuine protected source provides them;
codec neither authenticates nor consumes/approves grants. Replaycount/ownership/
Native denial/actual loadedsource observed by later existinghost mechanisms.

N7T1 ordinary model constructors/roundtrip exactsigned64/string IDs, immutability,
scope/unknownfield/boolean/null/whitespace/control/Unicode/boundary rejects;
PhaseA focusedpytest/strict2/memorycompile/sourceblobs and one independent bound
reverse gate before PhaseB.
N7T2 phaseB valid exact native frame -> typedcall -> digestbound rawbytes result,
independent literal expectedwire (not Expected derived from Actual), zero-byte/
Unicode rawsource and maxbyte legal positives. ExistingJSONhelpers really invoked.
N7T3 malformed/duplicate/nonfinite/deep/oversize/secondframe, tool/namespace/
method/key/ID/context/file/digest/body mismatch, subclasses/null/booleans/integer
edges; no read/effect/callback, no blanketdenial of valid fixtures.
N7T4 remove contextbinding, filebinding, digest or limit check -> namedRED/
exactrestoredGREEN; Root different valid-positive boundary. Final guarded
focused plus affectedexisting commonclient/protocol consumers, strict2(noAny/
skippedimports), compile/import/Git exacttwo sourceblobs. TEST->A->B N/A,
no moved responsibility/testretirement. No arbitrary Host/model/version literals
in generic policy; exactnative schema identity is projectdata, not claimedglobal.

Profile HIGH_ASSURANCE source-only, Python3.11 strict, XSS_NOT_APPLICABLE (data
codec no renderer). Forecast product<=230/test<=360effective, no screenshots/
persistent executable evidence. >500effective triggers structural/reuse review,
not forcedsplitting/minifying/deletion. No prompts/Owner or ticketnarrative in code.
Root architecture/control/finalreviewer; original released C13 implementation
owner /root/ticket30n4_peer_impl (allocationheldcc46a184), Luna/xhigh existing
approved profile; distinct existing native-tools sourcehelper. Oneactive lane.
Fresh author .worktrees/skill-improvement-30g-readonly-wire codex/same and Root
-review; Context ctx-ticket30n7-readonly-wire-20261021. Temps
johnny30-readonly-wire-owner-20261021 and -review-20261021; owner+TTLthrough
review/seal/holdoverride, freshperrunbasetemp no reuse/cleanup. Grant candidate
grant-ticket30n7-readonly-wire-20261021 revision01 NOT_ACTIVE until DOC_PASS/D8/
fresh containment/Gitbaseline/commonconstructors. Root may bind PhaseA only,
PhaseB conditional on reviewedactual model, no new Ownerquestion.
Uncapped localhistoricalpolicy, percommand60/child55, resources/raw records;
diagnose no-evidence repeat, no hard platform/policylimitbypass. No actualsubject
Native/Host/server/thread/turn/model/socket/pipe/SCM/service/account/ACL/security/
install/rights/network/cleanup/push/release/deploy/activation. No qualifiedsource/
30B43/TAL/Recovery relief or newcheckmark. This is not fullHostadaptercompletion.


## 30N4-H10I — one owned verified subject launch / closure42 proposal

Original30/runbook03 section3 minimum readonly entry, same parent
batch-checklist-local-20261019-uncapped and sealed Context04/SPEC lineage.
No PRD/SPEC change or new authority source. Baseline
801af02174ba9bc1b752b70c7ee58f4777482472 engineeringhold.
Actual source inventory: Python H10H only returns a suspended B2-owned process;
C# NativeJobGuard already resumes its own SafeHandle-owned fixture process.
Reuse C# behavior as native-contract reference, not a second unmanaged owner;
C# fixture ownership/JSON cannot safely replace the retained Python B2 pair.
No existing card claims a protected readonly launch. Reuse actual private
H10H/H9/H8/B2/H6/H10G owners/validators/recovery and shared composition_fakes.
No new process runner, DTO, policy engine, parser, service or general fixture.

CREATE EXACT
library/local_orchestration/grant_authority/windows_subject_launch.py
tests/test_grant_authority_windows_subject_launch.py.
MODIFY ONLY library/local_orchestration/grant_authority/windows_subject_lease.py:
one private bool _subject_launch_attempted=False in existing lease constructor.
No other lease behavior/limits changes; DELETE0/export0/dependency0.
The private bit is an owning-lifecycle reservation, not a Grant or public trust
claim. It lives on the existing original job owner, not a new global owner map.

One private _launch_verified_subject(plan:_SubjectLaunchPlan,
token:_PrimarySubjectTokenLease,job:_SubjectJobLease,
owner_ref:OpaqueMetadataId)->_SuspendedProcessCreation.
Use existing exact constructor/validator paths and finite errors. Reject
wrong exact types/owner/thread/expired/recovery before creation. Under existing
RECOVERY_LOCK -> LIFECYCLE_LOCK -> CREATION_LOCK, require exact false reservation;
one launch attempt claims it before child creation, never resets even on failure.
Reject repeat/reentry on same original job before another create or resume.
Job native active-process-limit1 remains necessary, not replaced by this bit.

Call real _prepare_suspended_subject once itself; never accept caller-supplied
creation as proof of preparation. Reuse its original input/pair checks, job
membership/image/session observations and installed protection checks. Capture
original owners/aliases/identity, recheck after preparation and immediately
before native resume. Re-borrow original token/job as needed only AFTER H10H
borrow exits; do not nest an active borrow around H10H. Reuse original check
helpers and existing Recovery retention; do not copy token/ACL/job parsers.
Bind only kernel32 ResumeThread with exact HANDLE/DWORD ABI, retain DLL owner,
call once on original primary thread; exact integer previous suspend count1
alone succeeds. 0,>1,0xffffffff,bool/other type, exception, alias/owner/thread/
identity/job drift or uncertain borrow exit refuses. Check original owner pair,
leases and observation identity at final return. Preserve creation SUCCEEDED
for H6 teardown compatibility; no invented RESUMED enum or second state machine.
No close/terminate/cleanup fallback. Any post-child uncertainty retains original
process/thread/token/job owners and RECOVERY_REQUIRED through existing helpers;
no false success, retry/reset or clearing previous recovery. Known pre-child
refusal creates no fictional process record. Actual Host/token/job/process/
ResumeThread effects are forbidden this source phase: every Win32 seam is fake.

H10IT1 use real ordinary plan/token/job constructors and existing
tests.test_grant_authority_windows_subject_preparation composition_fakes via
pytest plugin/import. Real H10H through actual source dependencies + fake native
edges, ordered prepare/verify/assign/readback/resume once; exact original record
returned, both original handles stay owned/open, legal finite input passes.
H10IT2 owner/type/thread/expiry/poison/recovery and repeat/reentry negative
cells prove zero extra create/resume; marker not reset after failed attempt.
H10IT3 parameterize resume ABI/results/exceptions and pre/post boundary drift,
silent borrow-exit mutation, wrong retained pair/identity/membership/image,
uncertain native result. Assert exact original resources retained/recovery,
no close/terminate/native retry. Malformed bypasses rejection evidence only.
H10IT4 reverse weaken reservation, pre-resume check, strict count1 and final
post-borrow check -> namedRED/exactrestoredGREEN; Root different legal-positive
door. Guarded affected launch/preparation/joblease suite, strict3 exact(no skip/
Any), memorycompile/import/load/Gitblob and single oldconstructor-line diff.
No ceremonial first-red for new behavior. TEST->A->B N/A: new composition,
no old responsibility/test retirement. Shared fixtures reused, not duplicated.

Forecast product<=240/test<=420effective, oldlease oneconstructorline, docs only
original30/registry/review/context metadata, screenshot0. >500effective triggers
structural/reuse review, not line compression/forcedsplits/delete. No ownerprompt
or ticket narrative in code. Per-run fresh registered basetemp, no old-rootclean.
Assets owner+TTLthroughreview/seal; candidate/evidence/Recovery holds overrideTTL.

Root Architecture Owner/control/finalreviewer. Implementation owner
/root/grant_transport_impl after H11 allocation RELEASED_TO_IMMUTABLE_REFERENCED_HOLD
c60a5026; distinct existing /root/ticket30_native_tools_review source helper.
Fresh author .worktrees/skill-improvement-30g-subject-launch, branch codex/same;
Root review matching -review. Context ctx-ticket30g-subject-launch-20261021.
Temps johnny30g-subject-launch-owner-20261021 / -review-20261021.
Grant candidate grant-ticket30g-subject-launch-20261021 revision01 NOT_ACTIVE
until distinct DOC_PASS, D8, exact baseline/nonreparse/containment/Git allocation
and ordinary constructors preflight. Existing types only, no typed bootstrap.
Same uncapped batch/history; command60/child55, resources tracked, raw results
saved before output, no identical failed retry. No native subject/Host/model/
network/pipe/SCM/service/security/account/ACL/install/rights/cleanup/push/release/
deploy/activation. No actual protection, qualified/main/30B43 or checklist pass.


## 30N4-H11 — one source-only bound read dispatcher / closure41 proposal

Original30/runbook03 section2, parent batch-checklist-local-20261019-uncapped.
No new PRD, SPEC semantics, authority source, Router, host or policy engine.
Source baseline3279f52e1d36751489054d617e364742df1c3d2d (engineeringhold only).
Independent bounded handoff confirms client accepts an injected channel, transport
owns bounded server I/O, windows_service.py is pure enrollment decoding, and no
caller joins peer match -> strict request -> exact existing ledger read -> response.
N5/N6 codec/HTTP already exist and are reused, never rebuilt. C13 issuer-identity
correction is separate; this value/read composition does not depend on it or
declare an actual protected issuer. All existing qualification holds remain.

CREATE EXACT
library/local_orchestration/grant_authority/windows_read_dispatch.py
tests/test_grant_authority_windows_read_dispatch.py.
MODIFY ONLY tests/test_grant_authority_windows_peer.py: qualify its single existing
import of _peer/_plan as tests.test_grant_authority_protocol; no fixture/assertion/
behavior change. This bounded test-import migration enables reuse of its existing
_matching_enrollment/_observation instead of duplicating the peer fixture.
DELETE0/export0/dependency0. windows_service.py remains pure wire decoding:
the separate new product owns ONLY ordered read composition, not another service
framework or production policy. All other files readonly, no unrelated UI/API fix.

One private function _read_bound_grant_frame(request_frame: bytes,
enrollment: _ProtectedPeerEnrollment, observation: _ProtectedPeerObservation,
ledger: SQLiteGrantLedger) -> bytes | None. These exact input/value constructors,
LedgerResult, GrantRecord and GrantReadRequest already exist; no new DTO/Protocol/
enum/state machine. Output None is explicit refusal; bytes are existing
encode_read_response wire only, never a success/qualification/approval receipt.
Reuse _match_protected_peer, decode_read_request, _bind_existing_record and
encode_read_response, real SQLiteGrantLedger.read. No copied validators/parsers.

Revalidate exact enrollment/observation through existing helpers before read;
peer mismatch/malformed input refuses. Decode bounded frame and verify both exact
request identifiers against enrollment.request_binding BEFORE any ledger read.
Only then call read exactly once for that grant_ref, bind existing record/plan
through _bind_existing_record, and encode matching bytes. Invalid/missing/refused/
malformed stored result, mismatch, exception or encode failure returns None,
no issue/claim/settle/fallback/retry. No arbitrary command/path/source/Grant minting.
This function assumes no native provenance from its arguments: it is explicitly
SOURCE_ONLY_UNQUALIFIED ordered composition, not authentication. Actual server
must later supply independently observed/enrolled inputs and qualify OS protection.
Read does not consume or authorize the underlying operation; existing lifecycle/
expiry/CAS semantics are NOT silently changed by this source-only metadata read.

H11T1 reuse ordinary real peer/plan constructors and existing test factories.
One actual disposable SQLite ledger prepopulated by fixture before call returns
a record response accepted by existing GrantAuthorityClient through a fake channel;
assert exact request IDs/plan/record and SOURCE_ONLY_UNQUALIFIED. No trustedissuer/
operationalGrant/real30B success claim. Known healthy path must not be blanket denied.
H11T2 parameterize peer/session/SID/creation/job/image/config mismatch, malformed/
oversize/duplicate-key request and wrong request identifiers: assert no ledger
read. Missing grant/refused/error result/record grant or plan mismatch refuse;
exact one legitimate read; spy on real read rather than substitute all expected
values for Actual. No source authority by caller self-report.
H11T3 forbid issue/claim/settle during dispatch, repeat calls remain read-only,
ledger exception/encoding refusal finite, no socket/process/native/Host/Git/
provider/log/credential effect. SQLite access only under registered disposable
fixture roots, no real data. Reuse existing peer/plan/codec/SQLite test seams,
no new general fake/runner. Preserve all unknown Recovery/current user artifacts.
H11T4 weaken peer ordering, pre-read request binding, post-read plan binding,
or response operation binding -> namedRED/restoredGREEN; Root must use a
different legitimate-positive counter. Guarded focused+direct peer/protocol/
ledger tests, strict exact3(no skipped imports/Any), memorycompile/import and
actual source/test blob readback; fixture import is the only allowed olddiff.
TEST->A->B N/A: no responsibility moved; existing entry/helpers unchanged.

Expected increment product<=90/test<=240effective, oldfixture1line; docs limited
this existing ticket/registry/review/context metadata, screenshots0. >500lines
triggers structure/reuse review, not minify/split/deletion. Test output in registered
ownerTemp, per-run fresh basetemp child registered before run and retained to
review/seal (no pytest cleanup of previous roots); owner+TTLthroughreview/seal,
holds override TTL. No evidence deletion or denied-cleanup retry.

Root Architecture Owner/control/finalreviewer; implementation owner
/root/grant_transport_impl only after H10H allocation released/sealed4302a155 and
advisory final returned. Distinct /root/ticket30_native_tools_review sourcehelper.
Preregister author .worktrees/skill-improvement-30g-read-dispatch and matching
-review, branches codex/same; Context ctx-ticket30g-read-dispatch-20261021;
Temps johnny30g-read-dispatch-owner-20261021 and -review-20261021.
Conditional grant-ticket30g-read-dispatch-20261021 revision01 NOT_ACTIVE until
distinct DOC_PASS, D8, fresh exactbaseline/containment/nonreparse Git and ordinary
shared constructor preflight. No new private type constructor bootstrap needed.
Same cumulative uncapped policy/history, child55/outer60, resource monitoring,
raw before display and no unchanged failing retry. Only offline source/tests/
bounded control processes/registered passive outputs. No actual native pipe/
token/job/process/SCM/service/Host/model/network/security/install/rights/cleanup/
push/release/deploy/activation; no qualifiedsource/main/30B43/checklist completion.

## 30N4-H10H correction / closure40 limited fixture-import migration — 2026-10-21


Same original30/H10H requirement, source baseline23113241, returned candidate
a247600007bfd1c1dd7651fbac1e7bded89d26e9; retain closure38 C13-independent T1-4,
original context/worktree/owner/remaining history and uncapped local batch.
Root CHANGES_REQUESTED, not a new PRD or new security/functional requirement:
H10H-F01 initial job-borrow exit can silently drift captured token before B2;
Root guarded actual dependency wrap produced create_calls1 instead of required0.
H10H-F02 final token-borrow exit can silently change identity and return success;
Root guarded exact-candidate probe DID_NOT_RAISE. Both are existing before/final
boundary checks in closure38. Revalidate captured token/job/identity and original
process pair immediately after applicable borrow exits and before create/return.
Use existing finite refusals/Recovery/original-owner retention, no reset/close/
terminate/resume, no new DTO/framework/parser. Add parameterized corresponding
baseline-red regressions including valid unchanged positive, exact originals/
no-child vs post-child outcome. Do not replace tests with blanket refusals.

H10H-E01 strict evidence: ordinary exacttwofile mypy fails on old retained test's
unqualified ABI fixture import. The reported alternative skips that imported
retained module; _FakeKernel32 consequently becomes Any (Root diagnostic
disallow-any-unimported produces3target errors). Do not use skip/ignore/stub or
casts to hide fixture typing. Smallest reuse repair is one existing fixture's
import identity, not another fake/helper or new test framework:
tests/test_grant_authority_windows_retained_process.py ONLY change the import
of fake_native/launch_plan from top-level test_grant_authority_windows_subject_process_abi
to tests.test_grant_authority_windows_subject_process_abi.
No fixture/assertion/behavior rewrite, deletion or extra paths. Demonstrate
duplicate-import-safe strict checking without fixture skip, including new target
test and this affected fixture, and run focused+direct affected regressions.

Exact overall allowlist vs23113241: originaltwo CREATE
library/local_orchestration/grant_authority/windows_subject_preparation.py
tests/test_grant_authority_windows_subject_preparation.py
plus ONLY above one-line existing retained-test import MODIFY; DELETE0/export0.
Relative additive correction baselinea2476000: same2newfiles may MODIFY and exact
one oldimport MODIFY; no other source/test/CLI/dependency edits.
This is a local child-scope amendment under the Owner batch, not operational
authority or an expansion of final AC. Conditioned on distinct DOCpreflight/D8
and Root derived revision02 Grant before author writes the extra path.
One shared fake composition fixture/parameterized cells remain; >500effective
test lines trigger responsibility/reuse review, not forced split/minify/deletion.
Current425/1141physicalfiles reviewed as one create-to-check responsibility,
reusing H8/B2/H6 fixtures, no duplicate runner/server/pixel/browser framework.
Correctness/type fixes must not grow a parallel lifecycle system.

Root initial raw h10h-root-initial-review-20261021.json SHA256
81e7739e0a332e437619aaf8500646cb8414eb88655e908b25abf28d0d82d66a:
591guardedPASS7.07s/effects[] does not discharge two silent-exit probes.
Distinct existinghelper independently found both source gaps and Any gap.
Seven author mutation pairs remain source evidence with exact final restores;
two intermediate inverse misplacements/nonbaselineGREEN remain invalid history.
No claim of initial strict proof/complete source review/Host qualification.
All closure38 operational restrictions continue unchanged: no actual Native/
Host/token/process/job/SD/pipe/SCM/service/security/rights/install/network/model/
provider/newcost/cleanup/push/release/deploy/activation. Only bounded offline
fake/control tests and registered passive outputs. C13 PhaseB unaffected.

## 30N4-C13 — distinguish issuer account from service SID / closure39 proposal

Original30/runbook03 source-only protectedissuer preparation, existing uncapped
batch/first-entry source-order bounds; baseline
2311324147c93fa463ce6e1566a148ce78f0c793. H10H closure38/Grantbec453bd remains
separate at exactly this unchanged source baseline and two disjoint paths.
Architecture readback /root/ticket30n4_peer_impl confirms a single issuer may
have LocalSystem TokenUser plus its independent NT SERVICE service-SID group;
there is no need for a new broker/Agent/service/VM. This fixes identity meaning,
NOT an approved LocalSystem installation/account/privilege setting.
AuthorityPeer.service_sid remains the S-1-5-80 service identity; pipe's existing
SYSTEM/BA collision rejection and H9 nonstandard-subject rejection stay unchanged.
Do not change any effective operational security settings or claim service trust.

One private source precondition:
_verify_current_wts_issuer_identity(peer: AuthorityPeer) -> None.
Existing AuthorityPeer is revalidated before native acquisition; service_sid must
be an exact canonical S-1-5-80 identifier with five uint32 subauthorities, never
SYSTEM/BA/ordinary user SID. The function owns one current PROCESS primary-token
query-only acquisition, not an incoming client/thread/WTS subject token or caller
supplied observation/owner. Current-process pseudohandle is borrowed, never closed.
Reuse H5 token USER/TYPE/SID decoders/query/close-owner tools, H9 raw GROUPS query
wrapper (not its subject-specific administrator rejection), original alias
validation/recovery lock/hold helpers, and H10E raw query-only process-token open.
Obtain only the current-process pseudohandle from GetCurrentProcess, never a
caller-supplied alias; this one thin native producer is allowed and its borrowed
pseudohandle must not be closed or duplicated. Pass its checked alias to H10E's
existing query-only open; do not use its positive-session record reader for issuer
facts. Do not hard-code the pseudohandle value in place of the native producer.
Only issuer-specific GROUPS tuple/pair/attribute/full-scan validation is allowed
locally: H9's existing group validator rejects the SYSTEM/BA entries this role
must permit and provides no neutral parsed entries. Reuse H5 SID conversion and
CanonicalSid validation; do not duplicate native query/open, USER/TYPE/SID decoding
or copy the subject-policy rejection. No parallel general token parser, owner
lifecycle, native process launcher, new public DTO or permission engine.

Read actual TokenUser == S-1-5-18 and PRIMARY; read GROUPS using existing strict
native tuple/pair/SID/uint32 grammar. Validate the entire returned tuple, no
first-match wins. Require exactly one matching peer.service_sid group with actual
SE_GROUP_ENABLED and without SE_GROUP_USE_FOR_DENY_ONLY. ENABLED_BY_DEFAULT alone
does not qualify. Other canonical groups including SYSTEM/BA are not mistaken for
a forbidden subject token; H9's separate WTS subject checks do not change.
Wrong/missing/disabled/deny-only/duplicate group, wrong account/token type or
malformed later entry refuse, not transform or normalize values.
Capture original native token owner/alias/issuing thread and revalidate before/
after each boundary and close. Use finite typed private failures, no raw OS text.
No SeTcb assertion/enablement, no clean-thread/SCM/code-protection/approved-owner/
Grant/Host qualification claim; this only observes current process token fields.

Known nativequery/identity mismatch with a stable known owner closes exactly
that owner through existing checked close, then refuses. Invalid/changed/unknown
native owner, alias/thread drift, interrupted or uncertain close retains original
resource/evidence under existing H9 recovery hold/poison; no second close, native
retry, unknown-object Close, reset or Recoveryclear. Native open failure cannot
invent an acquired owner. Nothing starts/stops a service or changes impersonation.
Existing resources and healthy old user-token semantics remain unchanged.

CREATE EXACT:
library/local_orchestration/grant_authority/windows_issuer_identity.py
tests/test_grant_authority_windows_issuer_identity.py
MODIFY0/DELETE0/export0; windows_service.py stays its current decoder responsibility,
no issuer/process-token behavior piled into wire decoding. Existing sources/tests
readonly. One independent token-observation responsibility warrants the two files;
first reuse existing fake PyHANDLE/SID/native-query fixtures before adding only
small issuer-specific cases locally. Not a new test harness or security framework.
Inputs/normal AuthorityPeer constructor already exist; output None uses no new DTO.
If private finite error constructors need bootstrap, first implement pure private
error definitions/constructor tests only, review that commit before native-query
body under the SAME ticket/Grant, no additional Owner decision or budget reset.

C13T1 normal AuthorityPeer/actual dependency-through-fake path: exact current
process token QUERY-only, SYSTEM primary + one enabled service group succeeds;
known token closes once, pseudohandle never closes. Subject role values cannot
stand in for issuer; no all-reject completion.
C13T2 invalid peer/SID before open; wrong account/type; absent/disabled/deny-only/
enabled-by-default-only/duplicate group, valid first followed by malformed entry,
noncanonical SID/attributes/shape fail before success. H9/pipe guard behavior intact.
C13T3 native fail/unknown return/query exception/owner or alias/thread drift/
close false/throw/interruption preserve exact required holds and poison, no
retry/secondclose/privilege effect; stable known refusal can close without poison.
C13T4 guarded focused + directly affected H5/H9/pipe tests, strict exacttwofiles,
memorycompile/import/actualloadedsource/blobs. Final-byte reverse mutations pin
TokenUser, enabled vsdefault flag, deny-only, later duplicate/malformed inspection
and recovery/close confirmation; namedRED and exactrestoreGREEN. Root differentdoor.
Do not bypass actual helper behavior by replacing every function with PASS.

Profile HIGH_ASSURANCE source-only; proposedauthor /root/ticket30n4_peer_impl
C12 allocation/context releasedaee411f4; subsequent architecture reads are complete,
no source edits. Root sole finalreviewer/orchestrator; existing distincthelper.
Freshctx-ticket30g-issuer-identity-20261020, proposed contained
.worktrees/skill-improvement-30g-issuer-identity and matching-review, codex/same.
OwnedTemp johnny30g-issuer-identity-20261020 and -review-20261020 author/Root,
raw/typecache TTLreviewseal then protectedreferencedhold, no expirycleanup.
Conditional grant-ticket30g-issuer-identity-20261020 revision01 NOT_ACTIVE until
DOCreview/D8/normalconstructorpreflight/exactallocation/role/baseline readback.
Forecast product<=200/test<=350 effective lines, not compression/split targets;
>500 structural responsibility/reuse review. All historicaluse/failures retained;
uncapped local cumulative/count policy, child55/outer60 initialfinite deadlines.
No actual native/token/process/job/Host/SD/pipe/SCM/service/account/ACL/privilege/
security/install/network/model/provider/newcost/cleanup/push/release/deploy/
activation. Only bounded offline fake tests/control children/passiveownedoutputs.
Return COMPLETED/BLOCKED/CHANGE_DETECTED exactcandidate/files/checks/findings/
deviations; technicalcomments only, no ownerprompt/ticketstory, no selfapproval.
Actual protected approval/service entry/client/observation and ultimate setup
manifest/Owner effect approval remain necessary, not supplied by this check.

## 30N4-H10H — bind suspended creation to existing leases / closure38 proposal

Original30/runbook03 source-only construction under batch-checklist-local-20261019-uncapped
and the approved first-entry ordering exception. Baseline
2311324147c93fa463ce6e1566a148ce78f0c793 (H10G source composition only).
Architecture narrow readback /root/ticket30n4_peer_impl at fixedf227430c found that
B2 accepts a raw token alias and an unrelated caller plan cannot bind an existing
record to that token/plan. Root selects owning the create-to-check call, NOT
adding DTOs, ready flags, mutable binding fields or accepting a caller-supplied
record. H10G source review is now closed and composed; its original native/
qualification restrictions remain. No new PRD/SPEC/security policy or resume right.

One outcome: private _prepare_suspended_subject(plan, token, job, owner_ref)
-> existing _SuspendedProcessCreation. Exact typed inputs existing
_SubjectLaunchPlan, _PrimarySubjectTokenLease, _SubjectJobLease, OpaqueMetadataId.
No supplied existing process record/rawtokenalias/proof boolean/callback injection.
The function itself passes the exact borrowed token alias and validated immutable
plan to existing B2 once, then joins existing H10D/E/F/G/H6 observations.
Returned record remains SUSPENDED_SOURCE_ONLY, not a new runtime state or authority,
not a permission-to-resume object. No ResumeThread, shell, arbitrary endpoint,
account/token acquisition, new Job, runtime activation, issuer or effect API.

CREATE EXACT:
library/local_orchestration/grant_authority/windows_subject_preparation.py
tests/test_grant_authority_windows_subject_preparation.py
MODIFY0/DELETE0/export0; existing sources, tests, __init__, CLI and dependencies
readonly. Reuse H9 lease/identity/recovery, H8 lease/limits/recovery, B2 checked
ABI/record, H10D pair guards, H10E child identity, H10F installedprotection,
H10G assignment and H6 retained-process reader. No parallel native parser, DTO,
fixture server, owner lifecycle, job policy, runner or ready-state machine.
Tests first search existing H8/B2/H6/H9/H10E/H10F/G fakes/fixtures; only missing
small composition-specific assertions/hooks may live in this exact test file.

Freeze internal lock order H9 _RECOVERY_LOCK -> H8 _LIFECYCLE_LOCK ->
B2 _CREATION_LOCK across the whole synchronous composition, including borrow
exit and uncertainty retention. Existing locks are RLocks; no inverse acquisition
or asynchronous wait/delegation. Token borrow spans creation and all checks.
Validate exact lease/plan types, owner/thread/poison and initial job borrow
admission BEFORE create. End that initial job borrow before H10G's own borrow;
never nest H8 job borrows. Keep outer locks to serialize lifecycle through the
existing source seams; no claim these locks exclude another OS principal.

Capture original token owner/alias/identity and job owner/alias; validate identity
through existing model, use existing alias/pair guards before and after dependency
boundaries. Require token owner object and alias remain the originals, not merely
same-number replacement. Call B2 with exact captured token alias and validated
plan once. Verify the returned exact live registered original pair using H10D,
read child primary identity via H10E and compare all existing SID/session/LUID/
PRIMARY fields with the captured token identity; verify both installed process/
thread descriptors via H10F. Assign/readback via H10G; no raw Assign copy.
Borrow exact job only for H6 reader after assignment. Observe twice, with actual
reader validation, and require identical five facts, PID==creation.process_id,
session==captured token identity, MEMBER, and full image path exact spelling
==validated_plan.files.executable.path (existing windows_peer equality semantics,
not suffix/casefold/new normalization). Creation time is positive and stable,
not an invented expected OS creation timestamp. Revalidate original resources,
identity and job lifetime at the final boundary/borrow exit before return.
No false claim that identity tuple proves exact token object/restrictions, file
bytes/provenance, continuing OS suspension or absencefromalljobs.

Before any child creation, known invalid input/lease refusal remains finite with
zero create/query/assignment/close and no invented process record. Existing B2
known no-child failure remains its finite refusal. Once a valid child exists,
any failure/unknown/alias/identity/protection/observation/borrow-exit mismatch must
retain that exact creation record plus original token+job owners using existing
recovery holds/poison; never return SUCCEEDED as a completed preparation. Preserve
B2 exception.creation_record when creation outcome is uncertain; if unknown
creation outcome lacks an identifiable child, retain known original leases and
existing native recovery evidence, do not invent a PID/record. No automatic
close/terminate/rollback/retry/replacement/Recoveryclear; failure handling cannot
resume or discard owners. Technical sanitizer errors use existing finite enums.

H10HT1 actual normal constructors + fake creation-to-check path: exact alias/
plan/owners, order of child identity/protection/assignment/readback, same returned
registered record, no Resume/Close/Terminate calls. Actual dependency functions
execute through patched native boundaries, not all helpers replaced by PASS.
H10HT2 wrong type/owner/thread/closed/expired/poisoned/nested token/job borrow,
invalid plan and pre-create refusal; no child effects, no blanket rejectall.
H10HT3 child identity mismatch each existing field, installed protection mismatch,
PID/session/image/membership mismatch, changed creation time or other five facts,
process/thread/token/job owner/alias drift and dependency/borrow-exit exceptions:
finite failure, exact retained originals and Recovery, no duplicate create.
Known no-child B2 refusal is distinguished from post-create uncertainty.
H10HT4 focused+direct affected tests, strict twofiles, memorycompile/import and
actual loaded-source paths/blobs; guarded native/SD/network/subprocess boundaries.
Final-byte reverse mutations independently pin token-to-B2 alias binding,
child identity comparison, installed protection, H10G assignment connection,
actual observed image/stability and recovery retention, namedRED/exactrestoreGREEN.
Root uses a different door, including a legitimate-work positive. Zero RED finding.
No source/model self-description counts as authority or actual OS isolation.

Profile HIGH_ASSURANCE source-only; final CVQ and protected issuer requirements
stay mandatory and unfulfilled. Author /root/grant_transport_impl H10G allocation/
Context RELEASED e2e554cc; Root sole reviewer/orchestrator, existing distinct helper.
Fresh ctx-ticket30g-subject-preparation-20261020; proposed contained
.worktrees/skill-improvement-30g-subject-preparation and matching-review,
codex/same. Temps johnny30g-subject-preparation-20261020 and -review-20261020
for bounded fake outputs/typecache, author/Root respectively; TTLreviewseal then
immutable referencedhold, no expirycleanup/Recoveryrelease.
Conditional grant-ticket30g-subject-preparation-20261020 revision01 NOT_ACTIVE
until exact DOC review/D8/contained allocation/current baseline/constructor
preflight; same batch usage and failures retained, no count/cumulative cap.
Initial child55/outer60 finite deadline; diagnose timeout and stagnant failures.
Forecast product<=250/test<=400 effective lines, not compression targets or a
license for newfiles; >500 triggers actual responsibility/reuse structure review.
No owner prompts/ticket narratives in source; no unrelated interface changes.
Return COMPLETED/BLOCKED/CHANGE_DETECTED candidate/files/checks/findings/deviations.

No actual subject token/process/job/native/SD/pipe/SCM/Host effect, service/account/
ACL/security/install/network/model/provider/newcost/cleanup/push/release/deploy/
formal activation. Only registered ordinary bounded control test/build children.
Source composition cannot satisfy trusted Grant issuance/readback, readonly/
no-code/no-delegation/egress evidence, 30B43 qualification or checklist closure.

## 30N4-C12 — reuse existing component-name admission / closure37 proposal

Original30/runbook03 source-only construction, existing uncapped batch and
C10 recorded shared-grammar followup, baseline
f8754baabc13196e1f8974201737daf30f0a3982. No new PRD/SPEC/policy/Host capability.
Current C9 NativeOwnedDirectoryTargets.ValidateComponent127-144 and C10
NativeOwnedPayloadFileCreator.HasValidLeaf152-170 implement the SAME bounded
component/device-name predicate twice. NativeManifest.cs InputRules already
owns common pure input predicates. Reuse it, no newfile/framework/parser.
H10G Python assignment lane is disjoint, remains bound to unchanged closure36
atd485ff3b/Grant72cb001e; this source-only docs revision does not change its
committed input/AC/paths or issue any effect authority.

One outcome: C9 directory components and C10 payload leaf admission use ONE
existing InputRules predicate with unchanged accepted/rejected values.
CREATE0/DELETE0. MODIFY EXACT library/local_orchestration/native_windows/
NativeManifest.cs, NativeOwnedDirectoryCreation.cs,
NativeOwnedPayloadFileCreation.cs, NativeOwnedDirectoryCreationSelfTests.cs,
NativeOwnedPayloadFileCreationSelfTests.cs. Other ports, checkedrelease,
ProtectionPlan/enrollment/WindowsReadback/SelfTests.cs/csproj/CLI readonly.
NativeManifest change ONLY shared internal InputRules component predicate;
do not change public AbsoluteWindowsPath or manifest/source/SD validation.
Directory derivation/exception/result classification and file uniqueness/
hash/size/role/root/ProtectionPlan rules stay unchanged. No new public DTO,
enum, port, configurable grammar or duplicated third implementation.

Freeze predicate already present: .NET UTF16Length1..255, no trailing space/dot;
stem beforefirstdot rejects OrdinalIgnoreCase CON/PRN/AUX/NUL/CONIN$/CONOUT$ and
exactfour-character COM1..9/LPT1..9. Preserve legal Unicode/codepoints/case and
non-device COM0/COM10/LPT0/LPT10 and ordinary dotted stems. No normalization or
new Unicode/OS security policy. Whole-path syntax/control/invalidcharacter
admission remains existing AbsoluteWindowsPath, not copied into this helper.
Keep totalpath32767/directories1024 where each existing caller owns those
distinct boundaries; do not merge unrelated file/directory result contracts.

TEST -> A freeze actual NativeOwnedDirectoryTargets.Derive/Create and
NativeOwnedPayloadFileCreator.Create paths with existing enrollment/fake ports.
Shared InputRules method is private source infrastructure, need not preexist
before this source-only transfer. Tests invoke real creators/derivation,
not a second expected predicate or only helper/direct delegation assertions.
Move both checks to existing InputRules, remove both old device-rule bodies.
B=N/A no second responsibility split or retired test/entry; preserve coverage.

C12T1 ordinary existing enrollment/ProtectionPlan/C9/C10 constructors and legal
directory/file primary paths; normal and inclusive255 componentlength,
legal Unicode/COM0/COM10 values still accepted where original contracts allow.
C12T2 both real consumers reject reserved devicecase/extension variants,
length0/256/trailingdot/space before nativecreation; exact root/entry/bytes/hash/
status boundaries preserved, no native/SD/actualfilesystemeffect.
C12T3 final-source reverse mutations: loosen shared predicate reservedname/
bounds so corresponding directory AND file consumer cells red, then exact
restoreGREEN; bypass each consumer's shared check separately, that consumer
namedRED/restoreGREEN. Zero red is finding; tests must discriminate transfer,
not just helper callcounts/testmirror. Root own differentdoor.
C12T4 offline SDK10.0.302 build0W/E/fake self-test plus actual fivefile blobs/
diff/import; unchanged C11release and C9/C10 matrices staygreen, no unrelated
old campaigns rerun. Persist full argv/stdout/stderr/actualpatch/blobs before
display, exactrestore green required. No ceremonial newfeature first-red;
this behavior-preserving split follows TEST->A and negative finalmutations.

Profile HIGH_ASSURANCE source-only, original CVQ stillmandatory later.
Proposedauthor /root/ticket30n4_peer_impl, C11allocation/context RELEASED
d7350c9f; bounded architecture query completed no sourcechanges.
Freshctx-ticket30g-native-component-reuse-20261020, proposed contained
.worktrees/skill-improvement-30g-native-component-reuse and matching-review,
codex/same. OwnedTemp johnny30g-native-component-reuse-20261020 and
-review-20261020 author/Root for offlineobj/bin/cache/raw, TTLreviewseal then
protected referencedhold; no expirydelete/Recoveryclear.
Root sole reviewer/orchestrator, existing distinctsourcehelper. Conditional
grant-ticket30g-native-component-reuse-20261020 revision01 NOT_ACTIVE until
DOCreview/D8/normalpreflight/exactallocation/baseline/roles readback.
Forecast netproductreduction, tests bounded expansion~100lines each in existing
coherent matrices; >500 effective triggers actualstructure review, not forced
split/minify. Prior usage/failures kept, no cumulative/countcap; child55/outer60,
diagnose beforeadjusting and no unchangedfailure retry.
No realnative/SD/Host/job/process/pipe/SCM/service/account/security/ACL/install/
network/model/provider/newcost/cleanup/push/release/deploy/activation.
Only ordinaryboundedcontrolbuild/test and registeredpassiveoutputs.
Return COMPLETED/BLOCKED/CHANGE_DETECTED with exactcandidate/files/checks/
findings/deviations; technicalcomments only. Source-only evidence, no whole12/
Host/30B43/issuerpositive or general Windows-path security completion claim.

## 30N4-H10G — original suspended process to owned job / closure36 proposal

Original30/runbook03 bounded native construction under existing uncapped batch/
first-entry source-order exception. Baseline f8754baabc13196e1f8974201737daf30f0a3982
contains source-reviewed H8 lease, B2 creation, H6 observation, H10D original pair,
H10E identity and H10F installed protection. Context04, originalPRD/CHG/SPEC,
no new requirement or safety policy. No claim any producer/Host is qualified.

One observable result: one exact live suspended B2 record assigned once to one
exact live owned H8 job, with actual specific-job membership readback; noresume.
CREATE ONLY library/local_orchestration/grant_authority/windows_created_process_job.py
and tests/test_grant_authority_windows_created_process_job.py. MODIFY0/DELETE0/
exports0. Existing H6/H8/B2/H10D/H10E/H10F/nativeWindows files readonly.
New product file owns only job assignment/readback lifetime, not another launcher,
lease, policy engine, DTO/parser or authorization source. Reuse existing H6
_read_job_membership(nativeKernel32, originalprocessalias, originaljobalias)
and _JobMembership; do not duplicate IsProcessInJob ctypes/output parser.
Use B2 record._kernel32, not newloader or PID/path-based reopening.
Reuse existing H8 normal constructor/limits/borrow/recovery and H10D exactrecord
sameoriginalpair checks, existing fake job+ABI support where safe; no copied
large standalone harness. Product forecast200effective/test450, >500 triggers
actual structural review, not forcedsplit/compactcode. Full-round oldusage and
findings retained; no renewed cumulative/countcaps.

Private input contract _assign_created_process_to_job(creation: B2
_SuspendedProcessCreation, job: H8 _SubjectJobLease, owner_ref: existing
OpaqueMetadataId)->None. No callerexpectedmembership, rawalias, admissionflag,
grantrecord, arbitrary nativecall or close callback as success authority.
Exact actual types, ordinary constructors; no new public DTO bootstrap cycle.
Finite errors reuse B2 _ProcessCreationError/_CreationFailureReason and existing
H8 _SubjectJobError for pre-borrow owner/lifetime refusals, no raw exceptions.
Later issuer/launch composition must still prove H10E/F/source/Grant/standardness;
this seam does not substitute for those obligations or executeactualqualification.
H8 owner_ref does not bind a B2 creation to a subject authorization; specific-job
membership is not proof of absence from all other jobs. No such claim is made.

Acquire outer H8 _LIFECYCLE_LOCK, then B2 _CREATION_LOCK, and enter
job._borrow_native_owner(owner_ref) while BOTH outer locks remain held. Catch
borrow-exit failure and retain originals BEFORE releasing either outer lock;
never allow kill-on-close between borrow failure and recovery publication.
This first composite entry freezes H8-before-B2 order; neither existing source
has an inverse composite consumer. Bind ORIGINAL job owner+originalalias
for the entire operation; require job.require_live and H10D live original
registeredSUCCEEDED/same-issuing-thread OPEN process/thread pair before/after
each membership and assignment boundary. A fixed private active-record guard
refuses reentrant samecreation/differentjob before another query/assign.
Pre-read specificjob must be NOT_MEMBER; MEMBER is known refusal beforeAssign,
never repeatAssign/idempotent authorization. Query failure/malformed data refuses
without Assign. Native AssignProcessToJobObject uses exact original aliases,
fixed pywin32 wrapper result must be None; no truthiness/expected flag.
After attempt, actual same specific-job readback must be MEMBER; before/after
guards include job lease identity/expiry and both B2 owners. Return None only
after borrow exit also completes. Do not query nulljob/globalmembership instead.

A native assignment failure/throw/non-None/unknown does NOT prove no effect
(Windows may terminate on job limit failure). Once attemptbegins, any bad return,
missing/notmember/malformed postread, alias/thread/record/lifetime drift, reentry
effect or borrow-exit failure retains BOTH original B2 record and original job
owner+alias via existing _retain_recovery_record/_retain_recovery_resource;
job._recovery_required prevents laterclose/reborrow, globalexistingpoison applies.
Never close/resume/terminate/retry/replace/move either resource or clearRecovery.
Beforeattempt known wrongowner/closed/expired/preexistingmembership refusal
must not be falsely reported as assignment happened; retain any existing drift
Recovery truthfully. Existing unrelated Recovery state remains untouched.

H10GT1 ordinary H8 limits/B2 constructors preflight; legal fake originalpair/
ownedlease performs NOT_MEMBER -> exactAssign(None) -> MEMBER, preserves owners,
zero nativeClose/resume, expectedcallorder and exactborrowifetime. Tests reach
real production boundary and existing actual membership parser, not testcopy.
H10GT2 wrongrecord/type/role/thread/registration/readiness/alias, wrongjob/owner,
closed/expired/poisoned/nestedborrow, MEMBER or invalid/unavailableprequery:
zero Assign/effect and no success. Legitimate normal path must remain green.
H10GT3 failed/throw/non-None Assign, postquery missing/failure/notmember/invalid,
job/process/threadalias drift at each nativeboundary and borrowexitexpiry:
both original owners/aliases strongly held, finiteRecovery, no cleanup/retry;
reentrant samecreation/differentjob cannot issue secondAssign.
H10GT4 guarded focused+affected H8/B2/H6/H10D tests (no unrelated campaigns),
strict new2, memorycompile/import+actual loadedsource/hash, finite smoke.
Final-byte reverse mutations must discriminate pre-membership refusal, fixed
originalAssignargs/return, postMEMBER check and bothowner recovery retention;
each actualnamedRED/exactrestoredGREEN with complete captured argv/stdout/stderr,
patchtext and product/test blobs. Store results BEFORE display; no retrospective
transcription as original output. Root differentdoor and distinctsourcehelper.
Responsibility transfer/retirement B=N/A; no oldcoverage deleted.

Profile HIGH_ASSURANCE source-only, original finalCVQ stillrequired. Proposed
author /root/grant_transport_impl; H10F allocation/context RELEASED immutablehold
6ff7292f; fresh ctx-ticket30g-created-process-job-20261020. Root sole reviewer/
orchestrator, existing distinctsourcehelper. Proposed contained
.worktrees/skill-improvement-30g-created-process-job and matching-review,
codex/same. Registered ownedTemp johnny30g-created-process-job-20261020 and
-review-20261020 author/Root, fakechecks/raw/typecache TTLreviewseal then held
while referenced; no automatic expirydelete or Recoveryclear.
Conditional grant-ticket30g-created-process-job-20261020 revision01 NOT_ACTIVE
until exactcommittedDOCreview/D8/preflight/allocation/baseline/roles readback.
No true nativejob/process/token/SD/pipe/Host/SCM/service/account/security/ACL/
install/network/model/provider/newcost/cleanup/push/release/deploy/activation.
Only ordinary boundedcontroltest/build processes/passiveregisteredoutputs,
child55/outer60 initialdeadline, timeoutdiagnosis/nounchangedretry, historical
usage retained. Return COMPLETED/BLOCKED/CHANGE_DETECTED exactcandidate/files/
checks/findings/deviations, technicalcomments only no ownerprompt/ticketstory.
All formal30B43/issuer/Host/checklist/Recovery obligations remain open.

## 30N4-C11 — shared checked setup-handle release / closure35 proposal

Original30/runbook03 source-only construction under existing uncapped batch/
first-entry order exception. Baseline77a8cb4b59fa19dd06cd7bc4d4891adbd202b5b5
contains reviewed C9 and C10 source. C10 F2 closed only its file path; C9 still
uses SafeFileHandle.Dispose without native release proof. Root managed-runtime
false-release reproduction05f230a4 and C9 finally source confirm affected
shared invariant. Do not claim existing qualified native cleanup or reopen
unrelated accepted C9 behavior. H10F Python lane is independent.

One observable outcome: directory and payload-file setup share ONE checked
release lifetime, preserving normal behavior and refusing uncertain cleanup.
CREATE EXACT library/local_orchestration/native_windows/NativeOwnedHandleRelease.cs,
a small internal owned-handle release component extracted from C10, not a new
Policy/Owner/cleanup framework. MODIFY EXACT same-directory
Win32OwnedDirectoryCreationPort.cs, Win32OwnedPayloadFileCreationPort.cs,
NativeOwnedDirectoryCreationSelfTests.cs, NativeOwnedPayloadFileCreationSelfTests.cs,
JohnnyAuthority.Tools.csproj. DELETE0. No domain/manifest/ProtectionPlan/parser/
SelfTests.cs/CLI/SCM/WindowsReadback contract changes. Newfile has one responsibility
and both named consumers; no new independent test harness or screenshot/artifact.

Move, do not copy, C10's original SafeFileHandle+rawalias retention and explicit
checked native close into the shared component. Reuse the existing finite close
delegate seam (or bounded internal rename within allowed files), one actual
CloseHandle binding, no new public DTO/enum/Grant or configurable policy. Exact
original owner/lifetime must be strongly retained before native entry. Normal
knownsuccess unregisters after disabling automatic duplicate release. False/
throw/unknown stops native cleanup, keeps exact remaining owners+aliases strongly
held with finalizer suppressed, no retry/alternateClose/GC teardown. Previously
retained/closed/ambiguous owners cannot be reissued for close. No actualnative
calls in tests. Caller supplies only its original owned SafeFileHandle, not
arbitrary rawalias adoption, PID, path or issuer authority.

Both creators close in reverse lifetime order only after their full proof.
Once close uncertainty occurs, stop later closes and retain remaining originals
through the SAME component. Preserve C10 exit/recovery behavior and unchanged
normal/negative file-creation matrix. C9 normal success remains Created/None;
close uncertainty becomes failureUnavailable, keeps truthful Created boolean
but TargetAlreadyExists=false even after knownexists, so high-level creator
cannot mask recovery as TARGET_EXISTS_REFUSED. No target delete/rollback/adoption,
no changes to directory admission, ACLs, derivation or existing-object refusal.
The existing C9 constructor fake seam may gain the same checked-close injection;
update all bounded callers, never let old fakehandles fall through to realclose.
No default fake-alwayssuccess in production or optional ignored check.

TEST -> A: freeze existing C9/C10 real creator->port->owned-release paths and
reusable FakeNativeApi assertions before transfer. B:N/A, no test retirement.
C11T1 ordinary existing enrollment/ProtectionPlan constructors and both existing
fake self-test primary paths; legal directory and multichunk file outcomes,
actual explicitclose once per original handle, reverse order after lastproof,
no recoveryhold onknownsuccess. Shared helper is private infrastructure, not a
new public contract whose absence blocks its own construction.
C11T2 directory nativeclose false/throw at first and later ancestor, knownexists
plus uncertainclose, partial success and missing observation: exact remaining
owners/aliases retained, no subsequentclose/retry/finalizer, highlevel recovery
not success/exists/ordinaryrefusal. Keep all C9 existing error cases and C10 F1/F2.
C11T3 shared resource release normal/invalid/alreadyretained/closed boundaries,
duplicate/reentry refusal and no release of unrelated/foreign owners; fake
ownsHandle:false, injected close delegate, no OS SafeFileHandle finalization.
C11T4 offline SDK10.0.302 restore/build0warnings0errors/fake self-test, exact
source/artifact mapping/diff. Record C9 defectbaseline evidence honestly: native
false-close semantics corroborated by existing puremanagedprobe; new test seam
wiring is not present in originalC9, so never call compilefailure a behavioral
baseline-red. Where a normal existing release-call-count cell can execute on
oldC9, capture it before correction with exactsource/test/wiring identities;
state any instrumentation change, do not claim unchanged testbytes. Final-byte
reverse mutations MUST independently show directory closefailure masking,
shared remaining-owner retention and file consumer still reaching checked close
each namedRED/exactrestoreGREEN. Root differentdoor; oldC10 campaigns remain
on their actual oldbytes, not rerun wholesale or relabeled asnewproofs.

Profile HIGH_ASSURANCE source-only, eventual originalCVQ stillrequired. Proposed
author /root/ticket30n4_peer_impl, oldC10allocation/context RELEASEDimmutablehold
8827753b; Root sole reviewer/orchestrator, existing distinctsourcehelper.
Fresh ctx-ticket30g-shared-handle-release-20261020; proposed contained
.worktrees/skill-improvement-30g-shared-handle-release and matching-review,
codex/same. OwnedTemp johnny30g-shared-handle-release-20261020 and -review-20261020,
respective author/Root, offline obj/bin/cache/raw, TTLreviewseal thenreferencedhold,
noexpirydelete. Forecast extractedshared100effective lines, originalC10shrinks,
C9smallwiringdelta/testmatrix expansion; >500 triggers real structural review,
not forcedsplit/minification. Conditional grant-ticket30g-shared-handle-release-
20261020 revision01 NOT_ACTIVE until committedDOCreview/normalpreflight/
exactallocation/roles/baseline readback. No new public type-preexistence cycle.
No actualnative/SD/Host/CLI/SCM/service/account/security/ACL/install/network/
model/provider/cost/cleanup/push/release/deploy/formalactivation. Only bounded
controlbuild/test processes and registeredpassiveoutputs, child55/outer60
initialdeadline; usage/failures retained, no cumulative/countcaps/unchangedretry.
Return exact COMPLETED/BLOCKED/CHANGE_DETECTED+candidate/files/checks/findings/
deviations. Technicalcomments only, no ownerprompt/ticket narrative. Allformal
issuer/Host/30B43/checklist/Recovery qualifications andholds remain unchanged.

## 30N4-H10F — installed created-object protection readback / closure34 proposal

Original30/runbook03, uncapped local batch/first-entry source-order exception.
Architecture Root narrows the next missing prerequisite before future assign/
resume: desired B2 SDDL is not installed process/thread protection. No new
product requirement, security policy, operational Grant, public effect or DTO.
Baseline6f563a7bfd0b8ff71fb6f913cd68db7b687cf883 (52path source engineering
stage, H10E source approved). C10 native-file correction is disjoint and not
an implementation dependency. Original PRD/CHG/SPEC/Context04 unchanged.

CREATE EXACT library/local_orchestration/grant_authority/windows_created_process_protection.py
and tests/test_grant_authority_windows_created_process_protection.py.
MODIFY EXACT library/local_orchestration/grant_authority/windows_subject_process_abi.py
and tests/test_grant_authority_windows_subject_process_abi.py, only minimal
shared fixed-descriptor validator extraction and existing/new mask regression.
DELETE0/export0. H9/H10C/H10D/H10E/nativeWindows/peer/service files readonly.
Reuse B2 SD semantic/buffer checker, H10D exact original-record/pair checks and
B2 recovery registry. Do not copy the ACE parser or build a permissions engine.

Private _verify_created_process_protection(creation:_SuspendedProcessCreation)
returns None only after both actual object descriptors validate. Only new
native wrapper win32security.GetSecurityInfo(originalalias,SE_KERNEL_OBJECT=6,
OWNER_SECURITY_INFORMATION|DACL_SECURITY_INFORMATION=5), exactly process then
thread. No caller-supplied descriptor/mask/expectedSD/trust flag/PID/path, no
SetSecurityInfo, CloseHandle, token/process creation, assign/resume or new
authority source. Actual standardness/Grant/Host qualification not inferred.

B2 original _verify_security_descriptor entry retains its fixed GENERIC_ALL
creation semantics and signature. Extract its existing grammar into one
private shared validator; new fixed installed-kernel wrapper selects modern
PROCESS_ALL_ACCESS/THREAD_ALL_ACCESS0x001fffff, never caller-selected mask.
Microsoft current winnt.h and process/thread rights document modern Windows
mapping; win32con.PROCESS_ALL_ACCESS currently contains old0xFFF, do not use
it as observed-policy truth. New wrapper rejects generic0x10000000 and weak/
extra masks for installed descriptors. Both wrappers retain exact valid
self-relative readonly bounded buffer, control0x9004/revision1, ownerSYSTEM,
two unflagged ACCESS_ALLOWED ACEs for SYSTEM/Admins only, no missing/extra/
duplicate/deny/NULL ACE acceptance, no normalization/observed-data rewriting.
Do not weaken existing constructor to admit installed forms. Source helpers
are not a new untrusted authorization API.

Hold B2 _CREATION_LOCK through read/validation, check exact registered SUCCEEDED
same-issuing-thread original OPEN process/thread owners via H10D before first
native entry and before/after each query/descriptor validation. Private active
record set rejects same-thread reentry before extra query; no new owner engine.
Original wrong type/thread/parent/role/registry/readiness/alias/recovery refuses
before any native calls. Recheck after native exception as well; known read
failure with unchanged original pair yields sanitized NATIVE_CALL_FAILED and
keeps successful record for separate teardown. Unknown/malformed/protection
mismatch or pair drift retains B2 record as RECOVERY_REQUIRED; no unsafe close,
retry, rollback, hold release or automatic teardown. Descriptor wrapper owns
its Python copied buffer; do not fabricate a native object/LocalFree owner.
GetSecurityInfo is not atomic against concurrent ACL changes: do not claim a
permanent protection proof, replace final admission or real CVQ qualification.

TEST reuses decorated B2 fake_native/launch_plan/_FakeSecurityDescriptor/_FakeAcl/
_FakeAce and original successful record, adding only exact GetSecurityInfo
fake seam. No second SD/ABI harness or real SD converter. Preserve B2 existing
constructor success and negative matrix unchanged. A:new actual-readback seam,
B:N/A; no test retirement or existing behavior refactor beyond shared predicate.
H10FT1 normal B2 constructor + fixed installed validator through ordinary native
fake descriptors, both aliases/flags/order, no borrowed closes, success None;
valid mapped descriptor passes while original generic creation still passes,
original creation must reject mapped mask and installed must reject generic.
H10FT2 null/absolute/invalid/short/long/writable buffer/control/revision/owner,
missing/bad/extra/duplicate/deny/flagged ACE, weak/extra/noninteger masks and
SID mismatch -> exact refused/recovery, never transformed into a legal result.
H10FT3 wrong original record/type/thread/role/parent/registry/state/alias before
query, native throw/BaseException, callback drift before/after each read and
validation, reentry and bounded thread case -> finite refusal, no extra query,
no borrow close/GC/teardown or lost recovery record. Legal reader remains usable
when a nested call is refused before effects.
H10FT4 guarded focused+affected ABI/H10D/H10E only, strictnew2+modified2, actual
memorycompile/import/LF/blob/diff, new-first/ABI-first fresh order; final-byte
mutations independently pin actual-read vs desired-copy, both-role queries,
fixed objecttype/info/mask, pre/post original identity and recovery retention.
One named cell per distinct obligation; Root different door, full unfiltered
red/exactrestoregreen/raw patch+source/test identities, no ceremonial firstred.
No new checklist completion or claim of actual OS evidence from fakes.

Profile HIGH_ASSURANCE source construction; final original CVQ still required.
Proposed author /root/grant_transport_impl (H10E released to immutablehold by
9c0f3267), Root sole reviewer/orchestrator, existing distinct source helper.
Fresh ctx-ticket30g-created-process-protection-20261020; proposed contained
.worktrees/skill-improvement-30g-created-process-protection and matching-review,
codex/same. Owned Temp johnny30g-created-process-protection-20261020 and
-review-20261020, respective author/Root, fakechecks/raw/onecache; TTLreviewseal
thenreferencedhold, noexpirydelete. Forecast newproduct100/test220 effective,
minimal existing shared-validator delta; >500 is actual structure review only.
Conditional grant-ticket30g-created-process-protection-20261020 revision01
NOT_ACTIVE until committed independent DOCreview, normal existing constructor
preflight, exact allocation/roles/baseline readback. No new-type preexistence loop.
Child55/outer60 initial deadline, no cumulative/countcap or unchangedretry.
No actual native/Host/CLI/model/provider/security/ACL/account/service/install/
network/cost/cleanup/push/release/deploy/formalactivation. Only ordinary bounded
control verification processes and registered passive outputs. Return exact
COMPLETED/BLOCKED/CHANGE_DETECTED with candidate/files/checks/findings/deviations;
comments technicalonly, no ownerprompt/ticket narrative. 30B/43/R0/DAP/TAL/
Recovery and unfinished checklist items unchanged.

## 30N4-H10E — created-process primary-token facts / closure33 proposal

Original30/runbook03, same uncapped batch and first-CVQ source-order exception.
Root Architecture identifies next missing producer before any future assign/
resume: H9 observes source token, H6 observes five process facts; neither reads
the created child's token SID/Session/LUID/PRIMARY type. This is an observation
primitive, not Grant/standard-account qualification or resume permission.
Baseline21ddef2a4ed274a68725576bfd981f2c8c213ff7 contains approved B2/H10C/H10D,
independent of active native C10. Original SPEC/PRD/CHG/Context04 unchanged.

CREATE EXACT library/local_orchestration/grant_authority/windows_created_process_identity.py
and tests/test_grant_authority_windows_created_process_identity.py.
MODIFY0/DELETE0/export0. Existing B2/H6/H9/H10D/peer/message/native files readonly.
Private _read_created_process_primary_identity(creation:_SuspendedProcessCreation)
returns existing H9 _PrimarySubjectIdentity. No new DTO/enum/error/rolepolicy,
expected SID/session/LUID argument, PID reopen, caller trust flag, process launch/
assign/resume, DACL proof or effect interface. Reuse H9 namespace
_query_base_identity/_require_subject_handle_owner/_require_subject_alias/
_close_known_owner/_retain_and_poison, existing _SubjectTokenError/Failure and
message identity parsers; do not copy token-query grammar or weaken shared
native-only helpers. H10D namespace _require_live_pair/_require_same_open_pair
and B2 registry/checked owners supply exact process record identity.

Fixed lock order H9 _RECOVERY_LOCK THEN B2 _CREATION_LOCK, held through whole read/
cleanup, matching existing token-borrow->B2 creation order; never inverse B2->H9.
Exact registered SUCCEEDED creation, same issuing thread, both original OPEN
owners and original aliases required before token open. Use checked original
process handle only. A private active-record set prevents same-thread recursive
read before a second open; existing BORROW_IN_USE refusal, no new owner engine.
Such refused reentry need not poison the valid outer read when no effect began.
Existing H9 RECOVERY_POISONED refuses before native open. No rawPI fallback.

Only new fixed native wrapper win32security.OpenProcessToken(originalprocessalias,
TOKEN_QUERY0x0008). Runtime return must be exact current native PyHANDLE via
existing H9 validation; not structural/duck object, int, None or token lease.
Reject token alias equal to process/thread alias without closing foreign alias.
Unknown exception/malformed open retains identifiable raw output through H9
existing recovery hold/poison; never invent unknown handle. Original valid B2
record stays retained; successful-process teardown remains a separate caller
action, never implicit. Do not auto-adopt B2 recovery/partial/foreign record.

Read USER/SESSION_ID/STATISTICS/TYPE through actual existing H9 _query_base_identity,
which checks token's original alias before each query and uses normal strict
DTO constructor; canonical SID, positive uint32 session, signed-native64 LUID
converted existing uint64 including0, PRIMARY only. No values filled from source
token, plan, expectation or fixture equality. These are observed values only:
SYSTEM-like SID may be observed, but no standard-subject/expected match is claimed.
Recheck original B2 pair after open, after identity reads and before/after owned
token close; callback drift stops result. Wrong owner/thread/registry/closed/
recovery/alias before open => zero native calls. After original record drift,
retain exact token through H9 hold and original B2 recovery, no unsafe close.
Known original token on ordinary query/validation failure closes exactly once
through existing H9 original-alias helper before propagating sanitized error.
Close uncertainty/alias drift => retain/poison, no retry/alternate Close/GC.
Native-open BaseException handled finitely, unknown owner not fabricated.
Return identity only AFTER confirmed token Close and final B2 identity check.
Never close borrowed process/thread/job/source-token owners, or release holds.

TEST real new reader over ordinary B2 fake successful record, actual H9 query
path + existing _PrimarySubjectIdentity constructors. Reuse B2 decorated
fake_native/launch_plan, H9 native_surface/_FakeHandle/_FakeNativeSurface; arrange
B2 creation BEFORE installing H9 query fake (its sys.modules/WinDLL swap).
One thin fixture adds OpenProcessToken to existing fake surface, no copied
SD/ABI/token-parser harness. Both new-first/ABI-first fresh collection orders.
A:new private observation seam, B:N/A; no test retirement.
H10ET1 ordinary existing H9 DTO and B2 constructors preflight, legal child facts
different from launch/source expectation returned unchanged inclLUID0/boundaries,
TOKEN_QUERYexact/processoriginalalias, four native queries, ownedtokenCloseonce
BEFORE result, borrowedowners untouched. No grant/provenance/installedDACL claim.
H10ET2 wrong record/type/parent/role/thread/registry/readiness/alias and existing
recoverypoison refuse beforeopen; malformed native owner/foreign alias retained
without structural Close, unknown open/interrupt finite and no retries.
H10ET3 malformed SID/session/LUID/type, ordinaryquery failure, token/process alias
or parent drift at each native phase, closeexception/KBI/nonNone, reentrant read
and bounded two-thread lock order retain/refuse safely; no return after failed
cleanup, no duplicateopen/Close/deadlock, known queryfailure cleans onlyownedtoken.
H10ET4 guarded focused+affected B2/H9/H10D (not unrelatedoldcampaigns), strict new2/
directimports, memorycompile/actualimport/LF/blob/diffcheck; final-byte named
mutations pin source-handle query, actualfact return vs expectedcopy, pre-open
identity, tokenclose-before-return, drift/poison refusal and reentry. One cell
perdistinct obligation; Rootdifferentdoor. Capture actualpatchhash/currentproduct+
test identities/argv/nonsecret whitelistenv/elapsed/exit/fullunreduced output,
exactrestore andGREEN. No ceremonialfirstred for new behavior.

Profile HIGH_ASSURANCE source construction only, eventual originalqualifiedCVQ
stillrequired. Proposed author /root/grant_transport_impl, H10D allocation closed
to immutablehold3a4572ba; Root sole reviewer, distinct source-evidence helper.
Fresh ctx-ticket30g-created-process-identity-20261020; contained WT
.worktrees/skill-improvement-30g-created-process-identity and matching-review,
codex/same. Owned Temp johnny30g-created-process-identity-20261020 and
-review-20261020, respectiveauthor/Root, fakechecks/raw/onecache, TTLreviewseal
thenreferencedhold, noexpirydelete. Forecast product180/test250 effective lines,
>500actualstructuralreview signal not forcedsplit. Conditional
grant-ticket30g-created-process-identity-20261020 revision01 NOT_ACTIVE until
committedDOCreview, existingnormalconstructorpreflight and exactallocation
identity/baseline/roles readback. Newfunction reuses existingDTO, no newtype cycle.
Child55/outer60 initial bounds; retain usage/failures, no cumulative/countcaps or
unchanged retries. No live native/Host/CLI/model/provider/SD/security/ACL/account/
service/install/network/cost/cleanup/push/release/deploy/formalactivation. Only
ordinary controlverificationprocesses and registeredpassiveoutputs.
Sourceapproval is not actual child-token, installedDACL or Host qualification.
30B/43/R0/DAP/TAL/Recovery/checklistcompletion unchanged. Return typed
COMPLETED/BLOCKED/CHANGE_DETECTED with exactcandidate/files/checks/findings/
deviations; sourcecomments technicalonly, no ownerprompt/ticketnarrative.


## 30N4-C10 — new protected enrolled payload file / closure32 proposal

Original30/runbook03 protected payload setup, existing uncapped local batch and
first-entry source-order exception; necessary construction, not installer/CLI/
authority effect. Architecture Root accepts bounded topology helper's file
analogue of C9. Baseline63d44d47ad984a75f513ce20fb10da5803c94d8c, independent
of H10D Python teardown. B2/C9/H10C source seals/mapping retained, not Host proof.
Existing new-directory primitive cannot create enrolled executable/dependency/
configuration FILE bytes. No existing-object replace, ACL edit, rollback/delete,
rename fallback, CAS claim or new framework. Source-byte match is not acquisition
provenance or permission to install; actual protected enrollment still required.

CREATE EXACT library/local_orchestration/native_windows/NativeOwnedPayloadFileCreation.cs,
library/local_orchestration/native_windows/Win32OwnedPayloadFileCreationPort.cs,
library/local_orchestration/native_windows/NativeOwnedPayloadFileCreationSelfTests.cs.
MODIFY EXACT library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj
and library/local_orchestration/native_windows/SelfTests.cs ONLY three Compile
entries/one existing fake self-test invocation. DELETE0. Program/manifest/policy/
C9/core-readback/oldtests remain readonly. No new operational command/export.
Extend EXISTING Win32ReadbackPort partial/privateNativeMethods. Reuse C9
OpenRetainedAncestor/SnapshotRetainedAncestor/NativeSecurityAttributes plus
PathPrefixes/OpenAncestorForCreation/SnapshotAncestorForCreation/
IsValidDirectorySnapshot/TryCapturePayloadSnapshot/SnapshotsMatch/MapError.
Reuse exact existing readback observations and enrollment/path/SID/digest types.
Do not copy ancestor opening/normalization/SDDL policy or create another runner.
Private constructor may initialize existing C9 delegate fields in same partial
plus file-specific create/write/flush/read/snapshot delegates for offline fakes;
no production-configurable command/port capability.

Internal NativeOwnedPayloadFileCreator.Create(enrollment:NativeEnrollment,
target:AbsoluteWindowsPath,candidate:ReadOnlySpan<byte>) returns one bounded
OwnedPayloadFileCreationResult (CREATED_VERIFIED/TARGET_EXISTS_REFUSED/
CREATE_REFUSED/RECOVERY_REQUIRED, NativeReadFailure, optional existing
NativeEnrollmentObjectObservation). Derive unique actual enrollment entry by
canonical case-insensitive target; never caller role/digest/size/entry.
NativeOwnedPayloadBytes.Capture eagerly copies <=64MiB exact enrolled positive
length and checks copied SHA256, then exposes immutable/read-only owned bytes
only; no mutable array escape or lazy/path/URI/stream/network source. Reject
unknown/ambiguous entry, invalid/case-ambiguous Windows component, file-directory
collision, length/digest mismatch BEFORE native/file port. Reuse C9 target
derivation for parent/path collision validation, not another lexical grammar.
Owner from ProtectionPlan.Build only, descriptor ONLY
ProtectionPlan.PayloadFileSddl(manifest,entry.Role). No new ACL policy table.

Low-level owned-file port: retain every root-to-parent original ancestor handle
with C9 exact READ_CONTROL|FILE_READ_ATTRIBUTES, shareREAD only, OPEN_EXISTING,
OPEN_REPARSE_POINT|BACKUP_SEMANTICS. Validate original path/nonreparse/directory/
nonzero volume+fileID and stable identity; hold ALL through file creation/write/
flush/same-handle readback/post-ancestor-check. One CreateFileW target attempt,
exact CREATE_NEW1/share0/noninherit SECURITY_ATTRIBUTES with owned pinned full
derived SD at creation, required READ_CONTROL/read/write access and explicit
normal-file/open-reparse flags. Not CREATE_ALWAYS, OPEN_ALWAYS or delete sharing.
Existing80/183 refuses without adopting/reading/writing target. Native exception/
ambiguous output after entry -> RECOVERY_REQUIRED even laterMISSING/stale80/183.
Never infer clean refusal from exception-populated error code.

Write only owned copied bytes with explicit offset and bounded byte/chunk count;
no retry of failed/zero/short native write. Flush before readback. Verify contents
through SAME created handle, not reopen by path: snapshot postwrite before read,
read/hash exactly enrolledsize, EOFprobe0, second snapshot identical; no digest
copied from input/manifest as actual result. Require non-directory/nonreparse,
exactfinalpath/nonzero stablevolume+fileID, stabletimes/size/owner/fullSD,
SYSTEMowner and exact rolefileSDDL, enrolled digest/size. Ancestor postchecks also
exact. Keep created/ancestorhandles until all proofs; dispose only ownedhandles
once reverseorder; any uncertain disposal -> RECOVERY_REQUIRED. No auto-delete
partial file. Native sizes and operations finite; fake tests cannot qualify OS
cancellation/driver/privilege/locking, which remain later Host bounds/admission.

Before create: invalid input/descriptor/ancestor refusal -> CREATE_REFUSED.
Exact known exists + stable ancestors -> TARGET_EXISTS_REFUSED/None.
Known create failure with no createdhandle and proven stable ancestors may refuse;
any uncertain create/post-ancestor outcome takes precedence -> RECOVERY_REQUIRED.
Once a file may exist, write/flush/read/EOF/descriptor/content/identity/ancestor/
close failure is RECOVERY_REQUIRED with known observation if available, never
success/no-effect claim. No adoption/overwrite/fixup/recovery attempt.

TEST real Creator->Win32 port fake delegates, shared existing C9/enrollment
self-test helpers where safely accessible; no copied browser/image/mock harness.
A:new private primitive; B:N/A, no test retirement or publicbehavior move.
C10T1 existing ordinary enrollment/ProtectionPlan constructors beforedispatch;
legal EXE/DEPENDENCY/CONFIG select exact fileSDDL, copiedbytes unchanged after
callerbuffer mutation, content read/hash independently, all ancestors+created
handle retained through proof; normal valid path must succeed.
C10T2 precise CREATE_NEW/access/share/flags/noninherit/binarySD/address/lifetime,
unique enrolled membership and byte/hash/size limits; unknown/pathcollision/
reservedcomponents/digest mismatch -> zero create/write; exists -> zero
write/flush/file-read/adopt. Normalcase-insensitive match allowed.
C10T3 before/after ancestor drift, create unknown/error/exception/staleexists,
short/zero/failed write, flushfailure, EOFtrailing, bad content/size/owner/SD,
fileidentity/time drift, handle disposal uncertainty -> finite refusal/recovery
with original evidence; no delete/overwrite/ACLrewrite/retry/foreigncleanup.
C10T4 offline.NET10.0.302 build zero warnings/errors, existing self-test selector
fake-only (never native selectors), current C9/enrollment regressions inherited
through that selector; final-byte discriminating reverse mutations CREATE_ALWAYS,
share/noninherit, early ancestorrelease, wrong directory/roleSDDL, skipprehash,
path-reopen/digest-from-expected, omittedflush/EOF and partial-success.
Parameterize related forms, one cell per distinctproperty not duplicated huge
campaign. Root counter differentdoor. Capture exact files/blobs/LF/patchhash/
argv/env/version/elapsed/exit/full unreduced stdout/stderr beforeeachrun, restore
exactbytes/rebuildGREEN. Assemblyhash difference from GitSourceRevision is not
source mismatch or artifact equivalence. No runtimequalification from fakes.

Profile HIGH_ASSURANCE source-only bootstrap order; distinct independent source
review then eventual originalCVQ. Author /root/ticket30n4_peer_impl, C9 allocation
already RELEASED immutablehold; Root sole reviewer, distinct source-evidence
helper. Fresh ctx-ticket30g-owned-payload-file-20261020. Proposed contained WT
.worktrees/skill-improvement-30g-owned-payload-file and matching-review,
codex/same, exactbaseline/no reparse. Owned Temp
johnny30g-owned-payload-file-20261020 and -review-20261020, respectiveauthor/Root,
offline obj/bin/NuGetcache/DOTNET_CLI_HOME/raw; TTLthroughreview/seal thenreferenced
hold, no expirydelete or rejectedcleanupretry. Forecast core220/port350/test350
effective lines; >500 actual responsibilityreview signal, not minify/tiny-file.
Conditional grant-ticket30g-owned-payload-file-20261020 revision01 NOT_ACTIVE until
committed DOC review, normal existingconstructor/fakeselftest reuse and exact
allocation/baseline/roles readback. New private constructors built/tested before
filebehavior; no pre-existing newtype cycle or ceremonialstubred.
Offline sourceclearedNuGet/noaudit/no telemetry/workloadchecks/node reuse/build
servers; bounded child55/outer60 initial, no cumulative/countreset. No live
native filecreate/write/flush/SD/account/ACL/security/service/install/Host/CLI/
provider/network/cost/cleanup/push/release/deploy/formalactivation. Only ordinary
control buildprocesses/registeredoutputs. Return typed candidate/files/checks/
findings/deviations; no source/prompt narrative, no mainintegration/checkmarks.
30B/43/R0/DAP/TAL/Recovery and originalaccounting unchanged.


## 30N4-H10D — successful-created-process exit-proof teardown / closure31 proposal

Original30/runbook03 and batch-checklist-local-20261019-uncapped; approved first
CVQ source-order exception only. Architecture Root narrows topology helper's
successful-process lifecycle to teardown ONLY: no assign/resume/launch/job/token
composition until actual child token SID/LUID and installed process/thread DACL
readback exist. H6's five facts and B2 desired descriptors cannot supply that proof.
This implements the existing B2 exit-before-close obligation, not new policy.
Source baseline63d44d47ad984a75f513ce20fb10da5803c94d8c after independently
mapped H10C exact composition. Context04 and original SPEC/PRD/CHG unchanged.

CREATE EXACT library/local_orchestration/grant_authority/windows_subject_process_teardown.py
and tests/test_grant_authority_windows_subject_process_teardown.py.
MODIFY0/DELETE0/export0. B2/H6/H8/H9/H10A and native tools read-only.
One private _terminate_confirm_exit_and_close(creation:_SuspendedProcessCreation)->None.
Reuse B2 module namespace, _ProcessCreationError/_CreationFailureReason,
_CREATION_LOCK, _CREATION_RECORDS and _retain_recovery_record. No new public
DTO/error/state machine, generic native port, caller-trust flag, raw-handle/PID,
job/token argument, configurable native operation or effect entry.
A private fixed binder supplies kernel32 DLL plus typed callables for
WaitForSingleObject(HANDLE,DWORD)->DWORD, TerminateProcess(HANDLE,UINT)->signed32BOOL,
GetExitCodeProcess(HANDLE,PDWORD)->signed32BOOL. Tests patch only fixed native
boundary, no public injected arbitrary callbacks. Hold DLL/function references.

Before DLL load and EVERY wait/terminate/exit-code native operation require exact current B2 record type,
same issuing thread, registered identity, SUCCEEDED and both exact original
PROCESS/THREAD owner views OPEN. Use checked .handle getters, never raw PI/cached
alias fallback. Wrong foreign/type/thread -> INVALID_INPUT with zero teardown
calls; existing recovery/drift preserves B2 error/hold, never re-adopts partial
records. Hold B2 RLock through whole operation. A minimal private active-record
guard refuses same-thread recursive teardown; original record is retained/poisoned,
and outer operation rechecks state after every callback before another native
call or Close. This is a reentrancy guard, not another ownership engine.

Read exact original process handle with WaitForSingleObject(handle,0) once.
WAIT_OBJECT_0(0) -> exit-code proof, no terminate. WAIT_TIMEOUT(258) -> one
TerminateProcess with fixed private nonzero exit code, then one finite
WaitForSingleObject(handle,5000). No INFINITE/polling/retry. Exact uint32 wait
returns only: bool/negative/out-of-range/WAIT_FAILED/unexpected reject.
Native BOOL exact signed32 accepts any nonzero including2/-1, zero/malformed
reject. GetExitCodeProcess writes owned DWORD, initialized STILL_ACTIVE259;
only successful native return AND output !=259 proves exit. Recheck original
owners/aliases after each wait/terminate/exit-code call and immediately before closing. Both
owners must stay OPEN/strongly registered until proof; only then thread.Close
followed by process.Close. Thread Close uncertainty prevents process Close.
Process Close uncertainty retains original B2 record; never alternate CloseHandle.
After confirmed thread Close require thread CLOSED, process OPEN, original
registered SUCCEEDED record and checked unchanged process alias before process
Close. Final success requires both CLOSED and original registry entry removed.
After any native-entry unknown/exception/BaseException, timeout, bad result or
identity change: B2 RECOVERY_REQUIRED/poison/strong retention, zero unsafe cleanup
or retry. Before native entry binder failure retains original valid record and
reports NATIVE_CALL_FAILED; no disposal claim. Repeated invocation after confirmed
both closes refuses without native effects. No __del__/GC/automatic recovery.
Borrowed H8 job is not received or closed; no effect permissions are issued.

TEST entry is real private teardown over real B2 successful record constructed
by existing fake_native/launch_plan, imported decorated fixtures as in H10C.
Use same ABI fixture/SD harness, no duplicated creator/mockserver/framework.
A is this new bounded seam; B:N/A, no behavior migration/test retirement.
H10DT1 ordinary existing B2 constructor/import before dispatch; already-exited
and active-then-terminated succeed, exact event order wait0/optional terminate/
wait5000/exit-code/threadClose/processClose, both owners retained until proof,
no job/token/creator side effect. Non-1 signed BOOL success remains legal.
H10DT2 invalid type/foreign record/subclass/wrong parent/role/thread/closed/
recovery/alias/registry state refuse before teardown native entry; B2 partial/
unknown output never adopted. Same-thread reentrant callback and bounded thread
interleaving cannot double terminate/wait/close; outer detects poisoned state.
H10DT3 malformed/failed first wait, terminate false/exception, finitewait timeout/
failed/malformed, exit false/malformed/STILL_ACTIVE, drift after each native step,
KBI/SystemExit, thread/process Close uncertainty preserve exact record and no
further unsafe effect. No failure retried; no raw PID/alias recovery.
H10DT4 guarded focused+affected ABI/H6 suites, strict new2 plus imported contracts,
memorycompile/actual import/Git blobs/diffcheck; both fresh collection orders.
Named final-byte mutations cover exit-proof refusal, finite timeout beforeClose,
thread-before-proof, both-owner release, reentry and original-alias recheck.
One discriminating cell per distinct obligation; Root different-door counter.
Capture full stdout/stderr, argv/env whitelist, elapsed/exit, actual patch/hash/
product+test identities before runs, exactrestore thengreen. Zero red is finding.

Profile HIGH_ASSURANCE source construction under first-entry order exception;
ordinary engineering independent source review is not qualified CVQ/Host audit.
Author /root/grant_transport_impl prior H10C allocation/context closed to immutable
hold629d1266; Root sole reviewer/orchestrator, distinct source-evidence helper.
Fresh ctx-ticket30g-process-teardown-20261020. Proposed contained author WT
.worktrees/skill-improvement-30g-process-teardown and matching-review, codex/same.
Owned Temp johnny30g-process-teardown-20261020 and -review-20261020, respective
author/Root, bounded fake checks/evidence/onecache, TTLthroughreview/seal then
referencedhold; no expirydelete or retry of old cleanup. Forecast product250/
test300 effective lines, >500 actualstructuralreview signal, never forcedsplit.
Conditional grant-ticket30g-process-teardown-20261020 revision01 NOT_ACTIVE until
committed DOC review, source mapping, normal existing-constructor reuse and
exact nonreparse allocation/baseline/branch readback. New private function has no
public DTO preflight cycle; ordinary B2 constructors remain checked first.
Child55/outer60 initial limits; uncapped cumulative/corrections with retained
history and no unchanged retries. New paths authorized ONLY by ACTIVE Grant.

No real native calls/process/token/job/SD/SCM/account/ACL/install/security changes,
Host/CLI/model/provider/network/cost/push/release/deploy/activation/cleanup.
Guard precedes imports; all subject OS calls faked. Only bounded ordinary control
verification processes and registered outputs. No recovery holds released.
Source completion leaves30B/43 blocked and checklist01/02 open; no main integration.
Return COMPLETED/BLOCKED/CHANGE_DETECTED with candidate/files/checks/findings/
deviations and passive evidence. No prompt/ticket narration in product comments.


## 30N4-H10C — exact created-process owner admission into H6 / closure30 proposal

Original30/runbook03, batch-checklist-local-20261019-uncapped and the approved
first-entry source-order exception. Necessary bounded migration after B2 source
approval26867c76; not a new capability/authority, SPEC, PRD or Host permission.
Sourcebaselinec1b609466b8048e0a487df1d45450168807d48b6 (B2 engineering stage);
independent stage mapping must pass before this proposal can become ACTIVE.
No dependency on C9 implementation or its unresolved F1.

MODIFY EXACT library/local_orchestration/grant_authority/windows_retained_process.py
and tests/test_grant_authority_windows_retained_process.py. CREATE0/DELETE0.
ABI/B2, token/H9, job/H8 and all other source/test files are read-only. Retain
existing H6 observation DTO/error enum, native calls and all five fact checks;
do not add Grant issuer, process launcher, arbitrary handle protocol or public
effect entry. Source boundary is ONLY _ThreadBoundRetainedProcessReader's
process-owner admission/revalidation, not the shared native-owner helpers.

Keep _require_borrowed_handle_owner and _require_original_borrowed_alias unchanged
and PyHANDLE-only: H9 imports both and also passes INVALID_PROCESS, so a failure
enum branch cannot safely select a process owner. Job input continues through
the original native-only path. Add localized process-only validation which
accepts the original native owner OR exact current
windows_subject_process_abi._CreatedKernelHandleOwner PROCESS view. Reject
subclasses, structural lookalikes, THREAD role, wrong parent/view/thread,
PREPARED/CLOSING/CLOSED/RECOVERY, changed original alias and invalid aliases before
new reader native calls. Reuse B2's checked .handle boundary for its current
creation/owner readiness, original parent/role/thread/alias; do not read raw PI
fields to bypass it, reopen PID, duplicate/close the borrowed owners or weaken
B2. Revalidate the same owner and original process alias at every existing H6
before/after observation checkpoint. Existing INVALID_PROCESS remains the
sanitized reader error for rejected process input; no new error engine.

Use a module namespace import for the ABI dependency, not a cached class alias:
the existing ABI fake fixture reloads that module. Dependency stays H6 -> ABI
-> H10A/H7 (none imports H6), no runtime circular fallback. Keep
_QueryableTokenOwner's existing typed surface and runtime class validation;
do not replace with unchecked object/Any/duck typing or caller role strings.
An exact Python object is only an internal service ownership boundary, NOT
trusted Grant provenance or a same-process security sandbox.

TEST: preserve the real H6 reader.observe entry, its same-handle native fake
observations and all five returned facts. A: add process-only owner admission
at existing constructor/revalidation, no native behavior move. B:N/A, no test
retirement; existing native-owner, token and job consumers remain live.
Reuse H6 _FakeKernel32/_reader/_install_fake_native_handle_type and B2 existing
fake_native/launch_plan fixtures for normal creation, never copy their ABI/SD
harness. Register/reload B2 fake creation before installing H6 observation fakes;
do not confuse H6 token Close fake with process/thread ownership. Namespace
dependency must work regardless of focused test collection order.

H10CT1 ordinary constructors/import: old native process+job remains accepted;
normal B2 fake creation yields a live PROCESS owner accepted by H6, observe
returns the same five expected facts through the real reader, never closes
borrowed process/thread/job. Independently assert actual observed fake aliases,
not just delegation or fixture equality; no baseline-only candidate claim.
H10CT2 invalid custom THREAD/parent/view/type/thread/readiness/alias refuses before
reader DLL/native calls; live -> closed/recovery/alias mutation between reader
construction and observe refuses. Preserve correct legal native path and
confirmed creation owner lifetime; no all-input rejection.
H10CT3 H9 shared helper and job boundaries remain native-only. A custom created
PROCESS owner passed to either shared helper or job slot is rejected despite
INVALID_PROCESS reuse; unmodified H9 tests remain affected consumer regression.
Existing H6 before/during/after alias substitution and token-close/poison tests
remain executable; no suppressing failures or weakening assertions.
H10CT4 guarded affected H6/ABI/H9 suites, strict modified2 plus affected imported
contracts, memory compile/actual import/blob check and baseline range diff check.
Final-byte named mutations pin PROCESS role/live-state gate, original alias
revalidation and shared-helper/job non-widening; one behavioral cell per
obligation, not a new full campaign. Root uses a different counter door.
Full unreduced outputs/command/elapsed/exit/patch/source-test identities and
exact restore retained; keep old failures, no budget reset. No test retirement.

No new files; forecast product+90/test+180 effective lines is a review signal,
not forced minification or tiny-file splitting. Existing large H6 test uses its
same shared native fake; source comments technical only, no owner prompts/ticket
narrative. A true contract/scope difference returns CHANGE_DETECTED before effect.

Proposed author /root/grant_transport_impl, prior B2 allocation RELEASED to
immutable evidence hold by26867c76; Root sole reviewer/orchestrator, distinct
source-evidence helper. Fresh ctx-ticket30g-created-owner-reader-20261020,
proposed contained WTs .worktrees/skill-improvement-30g-created-owner-reader
and matching-review, codex/same. OwnedTemp/johnny30g-created-owner-reader-20261020
and -review-20261020 for author/Root bounded fake checks/evidence/one cache,
TTLthroughreview/seal then referenced hold, no expirydelete.
Conditional grant-ticket30g-created-owner-reader-20261020 revision01 NOT_ACTIVE
until committed DOC review, stage mapping, existing ordinary constructor/import
evidence reuse and exact nonreparse worktree/roles/baseline readback.
New admission logic cannot be demanded before building itself. Child55/outer60
initial bounds; no cumulative/count ceiling, preserve historical accounting.

No real native process/token/job/SD/converter/Host call, CLI/model/provider,
service/SCM/account/ACL/security/install/network/cleanup/push/release/deploy or
formal gate activation. Native/external guard precedes import and all OS calls
are fakes. Ordinary bounded control verification processes/registered outputs
only. Engineering source approval never qualifies CVQ/30B/43. R0/DAP/TAL/Recovery
and previous denied cleanup unchanged. Return COMPLETED/BLOCKED/CHANGE_DETECTED
with exact candidate, paths, checks, findings, deviations and passive evidence;
COMPLETED is implementation return only, not review/integration/qualification.

## 30N4-C9 — new owned directory protection-at-creation / closure29 proposal

Original30/runbook03 and same uncapped local batch; source-only protection-tool
build, independent of active H10B2 Python ABI. This is not another installer,
Policy Engine, Gate or authority. Withdrawn existing-object SetSecurityInfo/
Recover design stays NOT_ADMITTED: no proven descriptor CAS, no unsafe rollback.
Create only a new enrollment-derived managed directory with full protection at
creation; never adopt/edit/delete/recover an existing object. Actual OS privilege,
ACL/account/service/install/Host effects remain separately ungranted.

Baselinebeb7a4635d7529d424cc320ea01a2e53574f88a1. CREATE EXACT
library/local_orchestration/native_windows/NativeOwnedDirectoryCreation.cs,
library/local_orchestration/native_windows/Win32OwnedDirectoryCreationPort.cs,
library/local_orchestration/native_windows/NativeOwnedDirectoryCreationSelfTests.cs.
MODIFY EXACT library/local_orchestration/native_windows/SelfTests.cs and
library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj,
only fake-test wiring and three explicit Compile includes. DELETE0. Program.cs,
NativeManifest.cs, NativeEnrollment.cs, ProtectionPlan.cs and old native/readback
files are read-only. New Win32 source extends the EXISTING Win32ReadbackPort
partial class/private NativeMethods, not a second I/O framework or new effect CLI.

Reuse NativeEnrollment's canonical setup digest, configuration and <=128 typed
payload/dependency entries; ProtectionPlan.Build is the ONLY owner/descriptor
policy. Reuse AbsoluteWindowsPath/SidValue, NativeReadFailure/NativeReadResult,
NativeObjectObservation, WindowsReadback.ReadDirectoryMetadata, PayloadFileSnapshot,
PathPrefixes/NormalizeFinalPath/TryGetDescriptor/TryGetFinalPath and same existing
partial NativeMethods. Do not copy manifest validators, path/readback harnesses
or add another target manifest. Fake tests accept existing SelfTests manifest,
reuse NativeEnrollmentVerificationSelfTests.CreateNestedMatchForCommand when
nested enrollment is needed, instead of duplicating its full fixture. This is
an explicit retained test dependency, not evidence those tests may retire.

Finite internal NativeManagedTree CODE/DATA and private-constructed immutable
NativeOwnedDirectoryTarget(Path,Tree), derived only from current enrollment.
NativeOwnedDirectoryTargets.Derive returns stable parent-first case-insensitive
unique targets, excluding trusted Environment ProgramFiles/CommonApplicationData
stop roots. Include managed code/data roots, intermediate descendants below stop
roots, executable/dependency parent paths and configuration parents. Reject any
file-as-directory prefix collision, wrong tree/outside stop, >1024 unique
directories or >32767 path characters before effect; never normalize ambiguity
into a guessed target. Creator rederives/checks membership against THIS enrollment,
not trust a target made for another plan/path. Desired owner/SDDL always rebuilt
from exact current ProtectionPlan CodeRootSddl/DataRootSddl, no caller path/SDDL
or approval marker can supply policy.

Minimal internal OwnedDirectoryCreationStatus: CREATED_VERIFIED,
TARGET_EXISTS_REFUSED, CREATE_REFUSED, RECOVERY_REQUIRED. Result binds existing
NativeReadFailure plus optional NativeObjectObservation, no new failure engine.
One NativeDirectoryCreateResult(Created,TargetAlreadyExists,Failure) for the
private native port. Contradictory/unknown result combinations cannot become
verified. INativeOwnedDirectoryCreationPort.CreateNew(path,owner,descriptor)
is an internal I/O boundary only; NativeOwnedDirectoryCreator.Create(enrollment,
target) is the private policy composition, not a public/operational entrypoint.

Before effect, independently observe exact parent with existing directory
readback; missing/denied/reparse/non-directory refuses with zero create calls.
The PRODUCTION creation port must hold ALL ancestor handles simultaneously
through call AND post-snapshot, not just check paths then act. Open parent-first
using READ_CONTROL|FILE_READ_ATTRIBUTES, FILE_SHARE_READ ONLY (no WRITE/DELETE),
OPEN_EXISTING, OPEN_REPARSE_POINT|BACKUP_SEMANTICS. Verify each retained handle's
directory/nonreparse attributes, exact normalized final path and volume/file ID.
Any denied share/open/verification fails before CreateDirectoryW; no weaker flags,
fallback or retry. Bound the chain by admitted target derivation; no recursive
filesystem discovery. Existing trusted stop roots are observation-only, never
created, changed or adopted as managed targets.

Use exactly THREE localized typed fake-native delegates in the new partial file:
OpenRetainedAncestor(path,desiredAccess,shareMode,creationDisposition,flags,
out PayloadFileSnapshot,out NativeReadFailure)->SafeFileHandle;
SnapshotRetainedAncestor(handle,expectedPath,out PayloadFileSnapshot,
out NativeReadFailure)->bool; CreateDirectoryCall(path,ref NativeSecurityAttributes,
out int win32Error)->bool. Default bindings reuse existing private native helpers;
one internal constructor accepts the fake bindings. No new parallel port hierarchy.
Fake handles use SafeFileHandle(...,ownsHandle:false), never actual CloseHandle.
The actual production-port methods, not merely a high-level fake, must execute
in the offline tests so changing its native flags/lifetimes turns tests red.

Own/pin a binary RawSecurityDescriptor copy from the plan for one CreateDirectoryW
call. Validate owner/protected nonnull DACL and exact noninheritable
SECURITY_ATTRIBUTES size/pointer; no ambient ACL or caller buffer, no precheck
then overwrite. The API itself makes the exists decision atomically. Existing
target/error183 or80 always refuses, never open-and-adjust. Hold all ancestors
through same-handle post-snapshots in original order; recheck nonreparse/final
path/volume/fileID. Dispose retained handles on every path, including exceptions,
without a second create, polling, deletion or cleanup. Independent post-create
WindowsReadback directory observation must exactly match planned owner AND full
descriptor before CREATED_VERIFIED; same-handle snapshots are not independent
readback and cannot replace it.

Known failed call plus confirmed missing target can CREATE_REFUSED. Missing/
unreadable observations do not turn an UNKNOWN/exception call into proof no
effect happened: NativeReadFailure.Unavailable, contradictory outputs, any
successful-call post-snapshot/readback mismatch always RECOVERY_REQUIRED even
if a later target is missing. Preserve observations/finite result as recovery
evidence, never clear existing Recovery, roll back ACLs or delete partial setup.
SYSTEM ownership may require unavailable privileges; source compilation/fakes
do not prove them. Never fall back to current-user owner, weaker sharing or
existing-object adoption. Actual simultaneous ancestor-lock compatibility and
trusted-root protection require later separately authorized Host qualification.

C9T1 pure target derivation/normal constructor and nested code/config/dependency
coverage, canonical source/digest membership, dedupe/order/stop-root exclusion,
file-parent conflicts/count/path bounds and other-plan target rejection.
C9T2 high-level positive creation and exists/safe refusal, exact owner/full
descriptor independent readback, wrong owner/descriptor/kind/missing/read-denied/
unknown outcome -> finite Recovery; zero create on invalid source/parent.
C9T3 ACTUAL production port with fake-native delegates: every ancestor handle
open through create and post-snapshot; exact access/share/open/reparse/backup
flags, non-NULL owned descriptor pointer/bytes/noninheritance/size, one call;
bad ancestors/changed identity/finalpath/reparse/native exceptions and all
deterministic disposals, no writes/deletes/retries. Tests must not invoke the
default real native delegates or allocate owning real native handles.
C9T4 offline pinned.NET10.0.302 build warnings-as-errors and existing fake-only
self-test selector, actual artifact/source identities, bounded final-byte
reverse mutations for real native port retention/share/flags/descriptor pointer,
plan-target binding, independent post-readback and unknown-result handling.
Batch related cases without redundant old campaigns; full unreduced outputs/
named failure labels/actual patches+SHA/source-test blobs/timing/exit captured.
New fake helper emits a fixed technical failed-cell label before throwing, so
the existing Program self-test error wrapper does not hide the intended RED;
passing public self-test JSON remains unchanged. No Program.cs mutation.

Forecast new core/port <=350 effective lines EACH, new test <=500; these are
structure signals, not forced tiny splitting/minification. Existing SelfTests
gets only one RunContracts(manifest) call; project gets three Compile entries.
No prompts, owner directions or ticket narrative in source. One responsibility
per new file: derived-policy composition, actual native I/O, reusable fake tests.
No payload-file writer/service/SCM/new observer implementation in this slice.

Proposed author /root/ticket30n4_peer_impl, previous H10B1 allocation RELEASED;
Root sole reviewer/orchestrator, distinct native-tools helper. Fresh context
ctx-ticket30g-owned-directory-20261020; proposed contained WTs .worktrees/
skill-improvement-30g-owned-directory and matching-review, codex/same. OwnedTemp
johnny30g-owned-directory-20261020 and -review-20261020 respectively author/Root,
purpose fake test/build/evidence, TTLthroughreview/seal/referencedhold, no expiry
deletion. Conditional grant-ticket30g-owned-directory-20261020 revision01
NOT_ACTIVE before committed DOC review, existing normal manifest/enrollment/plan
construction preflight, exact nonreparse WT/baseline/role readback. New native
setter/actual directory cannot be demanded before building its source.
Child55/outer60 initial bounds, explicit offline NuGet.Config(clear sources),
no workload update/network/paid expansion and one owned build/cache root.

No actual managed native directory/file/ACL/account/service/SCM/Host effect or
qualification, real native selector, native SD/subject call, model/network/clone/cleanup/push/
release/deploy/formal activation. Only fake self-test modes may execute.
Control-plane contained worktree/registered Temp allocation and bounded local
build outputs remain allowed; they are not invocation of the tested creator.
Root continues B2 independently; no30B43 clearance or new PRD. R0/DAP/TAL/Recovery
and earlier denied cleanup remain untouched.

## 30N4-H10B2 — one suspended-create ABI boundary / closure28 active

Original30/runbook03, same batch-checklist-local-20261019-uncapped and first-CVQ
source-order exception. Root Architecture and distinct topology helper narrow
the next missing producer to ONE native ABI boundary. H10B1 is reviewed source,
not operational permission. Do not start another capability/options exploration.
Reuse H10A _SubjectLaunchPlan and UTF16 bounds, stdlib quoting, H3 checked native
boundary/strong recovery patterns (not pipe ACL policy), H7 test _match_values.
Catalog workflow-control contains only workflow-router-poc READY; no native
process module card exists, so no invented catalog match/adoption. No second
Runner/VM/Agent/Policy/owner framework or generic security-descriptor parser.

Sourcebaselinebeb7a4635d7529d424cc320ea01a2e53574f88a1, exact reviewed43-path
engineering stage. CREATE ONLY library/local_orchestration/grant_authority/
windows_subject_process_abi.py and tests/test_grant_authority_windows_subject_process_abi.py.
MODIFY0/DELETE0. H6/H8/H9/H10A and native-tool source remain read-only in this
slice. Later H6 exact-owner migration is a necessary separately bounded2MOD,
not a claim this ABI result already passes its PyHANDLE-only admission.

Private _create_suspended_process_as_user_w(plan:_SubjectLaunchPlan,
borrowed_primary_token_alias:int) returns one _SuspendedProcessCreation with
exact process/thread owner views and observed positive uint32 PID/TID. Revalidate
normal existing plan at the boundary; exact positive pointer-sized token alias,
reject bool/zero/signed or unsigned sentinel. It is a private trusted-service
primitive, not an effect gateway, Grant issuer, caller-controlled process API,
same-process sandbox or provenance proof. Later consumer must obtain the token
alias inside B1 job-then-token borrow and retain both contexts across creation,
assignment/observation. No such production composition is activated here.

One finite private _CreateProcessFailure: INVALID_INPUT, CREATOR_POISONED,
NATIVE_CALL_FAILED, RECOVERY_REQUIRED. Sanitized error
may carry the exact creation record iff RECOVERY_REQUIRED. Never log native
handles, argv/environment contents, raw native exception or descriptor bytes.
No dynamic Any or unchecked object crosses the checked external boundary.

Before native entry allocate/strongly register one record containing actual
PROCESS_INFORMATION storage, two pre-existing role-fixed owner views, issuing
thread identity and retained checked DLL/function references. Owner views read
their own PI field directly: no post-return PyHANDLE adoption window. Exact
_CreatedKernelHandleOwner class/parent identity/PROCESS-or-THREAD role, same
thread and original alias must be revalidated before use/close. No structural
lookalikes, substitution, role swap, zero/sentinel aliases or wrong-thread use.
RLock serializes creation, registry/poison publication and explicit Close.
Known successful records remain strongly registered until BOTH exact explicit
Close calls confirm; this supersedes helper's proposed accept_transfer removal
and avoids a new transfer state/API and abandonment gap. Returning success does
not implicitly release ownership, close, resume, terminate or claim cleanup.

FALSE with exactly untouched zero PI -> finite NATIVE_CALL_FAILED, remove only
that no-output construction record, never say a process was cleaned. Once native
entry begins, exception/KBI/SystemExit, FALSE with any output, malformed TRUE
output or unknown return -> retain full record and all known raw outputs, poison
creator, RECOVERY_REQUIRED.
Native BOOL return is an exact signed32 integer: zero is FALSE, any nonzero
(including2/-1) is TRUE; reject malformed/noninteger wrapper values, not valid
non-1 success. All successful outputs still require independent exact checks.
Do NOT automatically CloseHandle: closing a process handle is not termination
and may orphan a suspended unassigned process.
No alternate raw close, automatic terminate/wait, PID reopen, retry, __del__ or
GC cleanup. New creation fails before effect while poisoned. Explicit Close
after successful creation is one checked original-handle attempt, idempotent
only after confirmed success; uncertainty retains complete record/poison and
prohibits retry. Future high-level recovery must prove process exit before its
explicit process/thread closes; ABI alone cannot claim that proof.

Do not accept caller SD/memoryview. Internally convert independently named
_PROCESS_OBJECT_SDDL and _THREAD_OBJECT_SDDL, both exactly
O:SYG:SYD:P(A;;GA;;;SY)(A;;GA;;;BA), with revision1. Verify native descriptor
IsValid/IsSelfRelative are exact True, control/revision exact fixed selfrelative
DACL-present/protected revision1 without defaulted/auto/inherited/SACL flags,
owner SYSTEM and exactly the two unflagged allow GENERIC_ALL ACEs for SYSTEM
and Builtin Administrators, no extras/duplicates/null DACL. Reject malformed
native return before process entry. Use one localized checked buffer-protocol
adapter for the pywin32 self-relative readonly, 1-D contiguous byte-sized buffer,
20..65535 bytes, copy independently into Python-owned native storage retained
through call. Do not cast Python object addresses or invent another unmanaged
LocalFree owner. Semantic validation of owned fixed converter output plus real
buffer protocol avoids unsafe arbitrary relative offsets without another parser.
Actual process/thread installed DACL readback still belongs to later composition.

Exactly one checked Advapi32!CreateProcessAsUserW binding, no wrapper fallback.
Non-NULL exact enrolled application path; mutable command rendered only with
list2cmdline([plan.files.executable.path,*arguments]); allocate terminal-NUL by
UTF16LE units (not Python len). Explicit Unicode environment block, never ambient
parent environment: empty exactly4 zero bytes; nonempty NAME=VALUE entries each
NUL plus final NUL, bounded per H10A, no BOM/implicit extra terminator. Exact cwd,
non-NULL independent process/thread SECURITY_ATTRIBUTES, length exact,
bInheritHandle=False, bInheritHandles=False; flags only CREATE_SUSPENDED |
CREATE_UNICODE_ENVIRONMENT; STARTUPINFOW.cb exact. No shell/breakaway/searchPATH,
defaults or implicit startup handles. Retain all buffers and ABI references.
Two output handles distinct, positive pointer-sized nonsentinel; PID/TID exact
positive uint32. Child must remain suspended; this slice has NO Resume/Assign/
Terminate/wait/SCM/host or token acquisition calls.

H10B2T1 normal existing plan/strict import and fake exact ABI args/storage/flags/
owner roles/PI-before-call registration; successful positive paths and explicit
single close/idempotence, no qualification claim.
H10B2T2 empty/astral/bounded UTF16, mutable command, exact fixed descriptor inputs/
copies; malformed SD controls/owner/ACL/buffer, caller lookalikes and invalid
token refuse before fake create. Boundary SID/ACL checks do not broaden H3.
H10B2T3 partial outputs on FALSE/raise/KBI, malformed TRUE/IDs/aliases and Close
uncertainty -> exact strong retention/poison/no auto close/terminate/wait/reopen/
retry; valid false-zero path does not manufacture cleanup. Actual issuing-thread
tests, role/parent/alias substitution refused, DLL/buffer lifetimes retained.
H10B2T4 guarded focused pytest, strict new2, memorycompile/actualimport/hash,
actual final-byte named weakeners for distinct fixed ABI flags/noninheritance/
NULL pointer, empty+astral bytes, pre-registration/partial-output retention/
poison and original-owner close/no retry. One discriminating cell per logical
obligation, parameterize related cases; no 30-pair duplication of unchanged
H8/H9 campaigns. Root counter enters a different behavior door, full unreduced
outputs and actual patch/hash/source-test identities captured at execution.

Forecast <=450 effective product lines and <=500 test lines for this one ABI
responsibility; line count is review signal, not permission to minify/split into
tiny files. Reuse fixtures, no duplicate browser/mock/PNG infrastructure. If a
real responsibility cannot fit, return precise boundary finding before adding
a path; Root may revise under batch, no new PRD or permission invention.

Proposed author /root/grant_transport_impl (prior H10A allocation released hold),
Root sole reviewer/orchestrator, native-tools helper for bounded source facts.
Fresh ctx-ticket30g-process-abi-20261020; contained WTs .worktrees/
skill-improvement-30g-process-abi and matching-review, codex/same, proposed
ownedTemp/johnny30g-process-abi-20261020 and -review-20261020 respectively
author/Root, owner+purpose+TTLthroughreview/seal/referencedhold, no expirydelete.
Conditional grant-ticket30g-process-abi-20261020 revision01 NOT_ACTIVE until
committed document review, existing normal plan-constructor/import preflight
and exact contained nonreparse WT/roles/baseline readback. New native wrapper
cannot be demanded as a precondition to building itself; existing approved
first-entry order exception applies only to source/fake construction.
Child55/outer60 initial command bounds, resource/old-history accounting retained.

No actual native job/token/process/SD conversion/Host/CLI/model/service/SCM/
security/account/ACL/install/network/cleanup/push/release/deploy/formal activation.
Tests must replace every native loader/converter/call with bounded fakes and
guard unpatched external effects before import. No live credentials or target
data. Source engineering review is not qualified CVQ/30B/43 admission. R0/DAP/
TAL/Recovery and rejected cleanup untouched.

## 30N4-H10B1 — checked original-owner borrowing / closure27 source sealed

Original30/runbook03 same uncapped batch and first-entry source-order boundary.
Architecture readback confirms H8/H9 expose no protected original native owner to
the later suspended-create call. Checking an alias then reading a private field
outside the owning lifetime is not an acceptable seam; native calls release the
GIL and a same-thread callback can reenter close despite an RLock. First add the
small checked borrowing seam inside each existing owner boundary. This is a
bounded part of H10B, not a new stage, Gate, Broker, public capability or authority.

Sourcebaseline00a9c90d82f04a1cbeb906331f6a5d4059974657, reviewed source stage;
all H10A models unchanged/read-only. MODIFY ONLY
library/local_orchestration/grant_authority/windows_subject_lease.py,
tests/test_grant_authority_windows_subject_lease.py,
library/local_orchestration/grant_authority/windows_subject_token.py,
tests/test_grant_authority_windows_subject_token.py. CREATE0/DELETE0. Reuse each
module's existing owner/alias/metadata/thread validation, lifecycle RLock and
recovery hold; no common ownership framework, new DTO or duplicate native harness.

Add one private context-managed _borrow_native_owner(owner_ref) to each lease,
yielding the exact original native owner (not numeric alias/duplicate/serialized
handle). Hold its existing lifecycle lock through entry, body and exit. Validate
exact bound metadata, issuing thread, actual native owner class/original alias,
closed/recovery/global-poison state before yield; job also requires unexpired
lease. Do not expose an owner from an invalid/expired/poisoned/closed lease.
Track one per-lease active borrow; nested/reentrant borrowing and close while
borrowed fail with a finite BORROW_IN_USE reason before any native Close.
This narrowly extends the existing private failure enum, not a Router state.

On exit (including Exception/BaseException from body), clear active-borrow state
in a guaranteed finally path and revalidate the original owner/alias. For job,
also recheck finite clock/expiry; expiry refuses further use but legitimate
teardown after expiry remains possible. Owner/alias uncertainty uses existing
strong recovery retention/poison, never retries alias access or alternate Close.
A body exception alone is not proof the borrowed owner was lost: preserve known
ownership and propagate it if exit validation succeeds. No implicit Close,
duplication, native acquisition, retry, finalizer or poison clearing. Confirmed
normal close stays idempotent after borrow completion. Existing non-borrowed
ownership/failure semantics must not regress.

Private trusted-service source seam only: a consumer must not retain/close the
borrowed owner or bypass context use. It is not a sandbox against arbitrary Python
in the same process, an external handle API, protected issuer or Host qualification.
Later H10B2 must acquire contexts in fixed job-then-token order through the whole
create/assign/observe operation; its exact ABI and operational guards are NOT_ACTIVE.

H10B1T1 legal borrowed identity/lifetime and post-exit close; wrong metadata,
thread, closed, global poison, alias drift/lookalike/recovery and expired job refuse
before body. H10B1T2 actual same-thread callback attempting close/nested borrow is
refused with no Close, and bounded two-thread interleaving cannot race close while
borrow is active; real threading.get_ident in those tests, not a shared constant.
H10B1T3 Exception/BaseException body and alias-read interruption preserve exact
known owners/poison and no repeated native access; normal legal cleanup survives.
H10B1T4 targeted existing H8/H9 tests, strict4, memorycompile/actualimport and
guarded no-native effects. Each new job/token borrow/close refusal predicate gets
one named weakener RED/exactrestoreGREEN on final source and test bytes; Root
different door. Capture actual full patch/text/hash, source/test SHA/Gitblob,
command/env/timing/exit/full stdout/stderr at execution. No unchanged old campaigns.
Forecast each module +60 source/+130 test; >500 actual cohesive-boundary review,
not forced splitting, test fixture duplication or compression of readable code.

Proposed author /root/ticket30n4_peer_impl (H9 allocation released hold), Root sole
reviewer/orchestrator, native-tools distinct helper. Fresh ctx-ticket30g-owner-borrow-
20261020; proposed contained WTs .worktrees/skill-improvement-30g-owner-borrow and
matching-review, codex/same, ownedTemp/johnny30g-borrow-owner-20261020 and -review-
20261020, respective author/Root owner and TTLthroughreview/seal/referencedholds.
No automatic expiry deletion. Conditional grant-ticket30g-owner-borrow-20261020
revision01 NOT_ACTIVE until exact committed doc review, contained nonreparse
source/roles and existing normal value-constructor/import preflight. Native owner
operations are verified only by bounded fake tests, not an operational probe. Same child55/outer60
defaults, one owned cache and historical uncapped accounting; no resource reset.
No actual process/token/job/native/Host/service/SCM/security/account/ACL/install/
network/model/cleanup/push/release/deploy/formal activation or30B43 clearance.

## 30N4-H10 — bounded subject launch input / closure26 source sealed

Original30/runbook03 controlled readonly-subject producer, same uncapped local
batch/first-entry source-order boundary. Root and distinct architecture helper
confirm H8 owns job limits/handle, H9 owns primary token, H6 observes retained
processes; none creates the actual suspended subject. Put process ownership in
one separate module, not append process/thread/token orchestration to H8's job
file. This supersedes only closure24's earlier future "same module" direction;
no new PRD/SPEC/Runner/Agent/Gate or operational permission. It is a necessary
producer for the original restricted Host, not another pure authority resolver.

A sourcebaseline1ae18b760e3416ec78b73727e6be8cc94b338cda, exact reviewed engineering
stage (not qualified/formal source). CREATE ONLY
library/local_orchestration/grant_authority/windows_subject_process.py and
tests/test_grant_authority_windows_subject_process.py; MODIFY0/DELETE0.
All H1-H9/native/ledger/client paths read-only. Reuse _StrictModel,
_CanonicalWindowsPath, H7 _ObservedEnrollmentMatch and stdlib list2cmdline;
tests reuse H7 _match_values from tests.test_grant_authority_windows_service,
not duplicate its enrollment fixture/native harness. This is an explicit test
dependency; H7 cannot be retired while that consumer exists.

A exactly one private frozen strict required _SubjectLaunchPlan with four fields:
files:_ObservedEnrollmentMatch; arguments:immutable tuple of0..16 exact strings;
working_directory:_CanonicalWindowsPath; environment:immutable tuple of0..32
exact(name,value) string pairs. No defaults/null/extras/coercion or ambient values.
Each argument/value <=4096 Unicode codepoints, no NUL or unpaired surrogate;
empty argument/value permitted. Environment name ASCII[A-Za-z_][A-Za-z0-9_]{0,63},
preserve exact case/codepoints; reject case-insensitive duplicate names, never
first-match/normalize. Render [files.executable.path,*arguments] ONLY with stdlib
list2cmdline; resulting command line including final NUL <=16384 UTF16 code units.
Explicit environment block (name=value plus NUL per entry and final NUL; empty
block has two NULs) <=16384
UTF16 units. Finite internal parser limits, not authority/resource-budget grants.
No shell, quoting reimplementation or implicit parent-environment inheritance.
Nested C8 file values remain SOURCE_ONLY_UNQUALIFIED; constructor cannot confer
protected provenance, Grant, file lease, executable identity or permission to run.
Do not log raw argv/environment/config contents into Router/evidence metadata.

H10T1 normal direct/JSON/bounds/required/frozen/deep-immutable/extras/null/type/
Unicode preservation and UTF16-vs-codepoint/quoting expansion cells; legal empty
explicit environment and args; invalid key/NUL/surrogate/duplicate/overflow refuse.
H10T2 guard native/process/network/filesystem/environment/clock operations while
calling actual pure constructor; one shared fixture, no per-case scripts.
H10T3 actual required-field, duplicate-env and rendered UTF16-bound weakeners each
namedRED/exactrestoreGREEN; Root different door, full source/test SHA+Gitblob,
exact patch/text/hash/argv/env/exit/time/unfiltered stdout and stderr captured
programmatically at execution, not reconstructed summaries. Strict2/import/compile.
Forecast A source+100/test+250; >500 real structure review, no minify/forced split.

B is NOT_ACTIVE. After exact reviewed A and final H8/H9 source mapping, freeze a
separate same-ticket B binding for real suspended-process ownership: borrow checked
same-thread original owners, create one fresh job, fixed protected-source plan,
no inheritable handles/shell/fallback, assign job and independently observe H6
identity/membership before any resume. Process/thread object protection must prevent
an untrusted peer resuming the suspended thread before admission; no default-DACL
assumption. Unknown/partial/termination/wait/close outcomes retain owners/poison,
finite explicit teardown. Exact native ABI/security/readback and minimum existing
owner-borrow changes are to be frozen before B, not authorized as incidental work.
No actual native process/token/job/Host/service/security or setup now.

Root sole reviewer/orchestrator; released H8 /root/grant_transport_impl author,
distinct /root/ticket30_native_tools_review source helper. Proposed contained WTs
.worktrees/skill-improvement-30g-subject-process and matching-review, codex/same,
ctx-ticket30g-subject-process-20261020; ownedTemp/johnny30g-process-owner-20261020
and -review-20261020, owner+TTLthroughreview/seal/holds, no cleanup authority.
Conditional grant-ticket30g-subject-process-20261020 revision01 A_ONLY NOT_ACTIVE
until committed doc review/contained nonreparse Git and constructor preflight.
Child55/outer60/one owned cache/evidence-progress; history/no fixed-count/cumulative
limit unchanged. No operational Grant, WTS/OS/Host/model/permission/install/
cleanup/push/release/deploy/formal integration/30B43 clearance. No Owner renewal.

## 30N4-H9 — owned standard-subject primary token / closure25 proposal

Original30/runbook03 protected issuer/readonly subject scope, same uncapped local
batch. H8 job producer proceeds independently. The later suspended-launch owner
needs an OS-issued PRIMARY token for the separately enrolled standard subject;
H4 impersonation and H6 query-only tokens cannot substitute. Build this necessary
producer in its own token ownership boundary, not job/module coupling or another
Runner/Broker/policy engine. Actual acquisition/privileges/account setup remains
separately unapproved; source/fake tests confer no new service rights.

Sourcebaseline d7ca3e9cdbf8acf59359718fb1a36f1aef24f6a5, reviewed exact source stage.
CREATE ONLY library/local_orchestration/grant_authority/windows_subject_token.py
and tests/test_grant_authority_windows_subject_token.py; MODIFY0/DELETE0.
All existing H4/H6/H8/peer/ledger/native modules READ_ONLY; reuse _StrictModel,
_CanonicalSid/_PositiveUint32/_Uint64/_TokenType, H3 exact PyHANDLE checker,
H4 checked native calls/SID/LUID/token-value helpers where their meanings agree.
No production import from tests; tests import real product/shared fixture, not copies.

A exactly one private frozen strict required _PrimarySubjectIdentity:
subject_sid canonical SID; windows_session_id positive uint32; authentication_id_luid
uint64 including0; token_type _TokenType validated exactly PRIMARY (no coercion,
default/null/extra). This is observed-value consistency, not a role/Grant or proof
of token acquisition/restriction. Ordinary constructors/bounds/required/frozen/
type/PRIMARY-vs-IMPERSONATION direct+JSON matrix, strict2/compile/import and
actual required/default/type/token-kind weakeners namedRED/exactrestoreGREEN.
No native calls, token owner/loader, WTS probes or placeholder methods in A.

B after exact reviewed A: one private factory accepting protected-source-selected
expected subject SID/session plus owner_ref, returns private same-thread owning
primary-token lease. Validate all input metadata before native acquisition.
Use WTSQueryUserToken for that exact positive logged-on session, no enumeration/
current-session fallback/password/credential/interactive prompt. This requires
future LocalSystem+SeTcb operating authority; none is granted now and no service
account selection/setup is activated by writing this source.

Read actual TokenUser/TokenType/TokenSessionId/TokenStatistics/groups/elevation/
privileges through checked native wrappers and validate exact SID/session/PRIMARY;
reject built-in SYSTEM/LocalService/NetworkService, elevated or Administrators
membership (including filtered-admin membership), malformed/unknown metadata.
The expected SID/session must later be supplied by protected enrollment, not caller
self-report; this internal factory and values are not an authority entry.
CreateRestrictedToken flags0, deleting every observed privilege except
SeChangeNotifyPrivilege via the actual privilege LUID list; no SANDBOX_INERT,
WRITE_RESTRICTED, privilege enabling, LogonUser, shell, network or fallback.
DISABLE_MAX_PRIVILEGE is not used to pretend deletion: it ignores the delete list.
No new restricting SID/DACL policy is invented here; standard-account separation,
protected paths and native tool mediation still require their independent proofs.

Independently read new token back: exact source SID/session/authentication LUID/
PRIMARY/nonadmin/nonelevated, and no privilege other than optional ChangeNotify.
Observe values from new token, never copy Expected or base observations as result.
Retain exact distinct native restricted-token owner on issuing thread; close base
owner exactly once before exposing output. Neither numeric alias nor structural
Close lookalike is ownership. Alias/owner/thread mismatch refuses; no handle
duplication/PID reopen/other-session search/caller JSON token.
Lease requires explicit owning teardown/owner_ref; no GC finalizer promise.
Partial/unknown create/close outcome retains all identifiable owners strongly in
private process-lifetime recovery hold, poisons future acquisition, no retry/
alternate raw CloseHandle/exception-loss GC cleanup. No fake success/no token
leak to logs/serialization/other agent, no automatic Recovery clearing.

H9T1 A construction/strict/no-effect matrix above.
H9T2 B fake beneath actual native wrappers pins exact WTS session, base/new token
SID/session/LUID/type/admin/elevation/privilege checks and exact delete list/flags;
independent native outputs, not configuration echoed as observation.
H9T3 distinct native-owner identity, original alias/thread, base close-before-return,
one Close/idempotence, failure/unknown output/cleanup retention/poison, legal success.
H9T4 no unpatched native/token/process/network/filesystem/env/Host effects; actual
SID/session/kind/privilege/cleanup weakeners namedRED/exactrestoreGREEN, Root
different door. All raw proofs include source/test SHA/Gitblob, exact patch/hash,
full unfiltered stdout/stderr/command/exit/time. One ownedTemp cache/child55/outer60,
no unnecessary new first-red/baseline triplets or unchanged-suite campaigns.
Forecast A source+40/test+150, B source+250/test+350; >500 structure review not minify.

Root sole reviewer/orchestrator; released H7 author /root/ticket30n4_peer_impl,
distinct /root/ticket30_native_tools_review source helper. Preregister contained
.worktrees/skill-improvement-30g-subject-token and matching-review, codex/same,
ctx-ticket30g-subject-token-20261020; ownedTemp/johnny30g-token-owner-20261020 and
-review-20261020, owner+TTLthroughreview/seal/holds, no cleanup authority.
Conditional grant-ticket30g-subject-token-20261020 revision01 A_ONLY NOT_ACTIVE
until committed doc review/contained nonreparse/source/roles preflight.
B_NOT_ACTIVE until exact reviewed A; no new Owner technical renewal.
No actual WTS/token/job/process/Host/service/SCM/account/privilege/ACL/install/
model/cost/network/cleanup/qualification/formal integration/30B43/push/release/deploy.

## 30N4-H8 — service-owned native job lease / closure24 proposal

Original30/runbook03 section2, same uncapped batch/first-entry source-order scope.
Root and distinct architecture helper read exact876223b3 native job guard/port:
C# NativeJobGuard.Run waits and disposes handles in finally, and accepts only
three fixed fixture modes. Its JSON is not a live PyHANDLE ownership bridge.
The Python service therefore needs an in-process subject lifecycle owner. Build
that responsibility once, not a second Runner/Broker or another pure comparison
wrapper. This slice produces the job owner only; suspended subject/token launch
extends the SAME module later after its exact scope/preflight. No response path
or qualification is claimed while those producers remain absent.

Sourcebaseline876223b3d04d5a0baedda9d5cdbcd9c1092431a2 (reviewed source engineering
stage, not formal integration). CREATE ONLY
library/local_orchestration/grant_authority/windows_subject_lease.py and
tests/test_grant_authority_windows_subject_lease.py; MODIFY0/DELETE0.
H1/H2/H3/H4/H5/H6/C8, ledger/client, native C# and H7 paths READ_ONLY.
One product responsibility = owning subject job lifetime; one shared fake native
job fixture/matrix. No per-case scripts. Reuse existing _StrictModel, exact native
PyHANDLE checker and handle information helper from H3, canonical metadata aliases,
and H6 same-thread/alias ownership conventions. C# N2 bounds/order/ABI are reference
proofs, not an executable ownership transfer. Production code must not import tests;
tests must import and exercise the actual production model/implementation, not a copy.

A only one private frozen strict required _SubjectJobLimits:
active_process_limit literal integer1 (bool rejected);
process_memory_limit_bytes/job_memory_limit_bytes integer1..536870912;
process_user_time_100ns/job_user_time_100ns integer1..12000000000;
parent_wall_timeout_ms integer1..1200000.
process memory<=job memory and process CPU<=job CPU, no coercion/default/null/extra.
Memory ceiling reuses CVQ ResourceBounds/N2, wall ceiling CVQ ReadOnlyHostBounds
at reviewed24c79d22. CPU ceiling is finite100ns conversion of that wall maximum,
not a policy budget or permission. Operational grants must still supply/enforce
their narrower bounds; no change to C# fixture limits or existing CVQ contracts.
No IO/clock/UUID/native job calls/placeholder lease methods in A.

B after ordinary A constructors/strict/source review: implement private
_create_subject_job(limits, owner_ref) -> _SubjectJobLease. No caller supplied
job_ref: generate a fresh service-internal opaque identity once and bind it to the
actual retained unnamed noninheritable PyHANDLE returned by CreateJobObject.
Set exact extended limits active1/process+job memory/process+job CPU/KILL_ON_JOB_CLOSE,
no breakaway flags. Read native limits back and compare all fields/required flags;
verify handle inheritance and original owner/alias. No partial or expected-filled
readback. One owner retains exact job handle on the issuing thread and records
owner_ref, internal job_ref and monotonic expiry derived from limits.
No process/token creation, arbitrary command, PID reopen, handle duplication,
SCM/listener/helper/Grant/ledger operation or policy activation in this slice.

Lease exposes only metadata/liveness needed by the future same-module subject
owner; do not export a numeric handle as authority or hand ownership to caller.
Close invokes the same original PyHANDLE.Close exactly once; confirmed close is
idempotent. Wrong thread/alias drift/expired access refuses before further native
work. Cleanup uncertainty retains exact owner plus recovery state, poisons future
operations, does not retry close/alternate raw CloseHandle/GC/destructor disposal.
Creation/readback failure closes only confirmed newly owned job; uncertain close
must retain it in the raised private error. Native creation with no identifiable
owner is indeterminate failure, not a fabricated success. Finite resource lifetime
uses explicit owning caller teardown, not a background watchdog or cleanup promise.
No new resource authority, owner-signed DTO, protected provenance or capability
is established by these internal metadata values.

H8T1 A normal direct/JSON exact/bounds/frozen/required/type/cross-field cases,
strict2/memorycompile/import; actual required/default/strict-field weakeners
namedRED/exactrestoreGREEN, no ceremonial first-red.
H8T2 B fake below actual native job wrappers pins creation/flags/noninheritance,
every observed field mismatch, no return before all readbacks, exact handle owner,
original numeric alias/thread, internal jobref uniqueness, owner/TTL metadata.
H8T3 close once/idempotence/readback failure/unknown creation/close uncertainty
retention/poison/expiry, and legal lifecycle still succeeds.
H8T4 block unpatched real native/process/socket/filesystem/environment/Host effects;
actual source flags/readback/cleanup/identity weakener cells must namedRED and
exactrestoreGREEN. Root different door, full unfiltered raw stdout/timing/hash.
One ownedTemp mypycache, child55/outer60 initial bounds, evidence-progress/history.
Forecast A source+60/test+150; B source+240/test+350 effective. >500 triggers
structure review, not minification or automatic fragmentation/new framework.

Root sole reviewer/orchestrator; released /root/grant_transport_impl named author,
distinct /root/batch_authority_review source helper. Preregister contained
.worktrees/skill-improvement-30g-subject-lease and matching-review, codex/same,
ctx-ticket30g-subject-lease-20261020; ownedTemp/johnny30g-lease-owner-20261020 and
-review-20261020, owner+TTLthroughreview/seal/hold, no cleanup authority.
Conditional grant-ticket30g-subject-lease-20261020 revision01 A_ONLY NOT_ACTIVE
until exact committed document review/source/roles/contained nonreparse Git binding.
B_NOT_ACTIVE until exact reviewed A. No new Owner technical approval is required.
No actual job/native/process/token/Host/helper/SCM/model/permission/install/cleanup/
network/push/release/deploy/formal integration/qualification/30B43 clearance.

## 30N4-H7 — bounded observed-file wire consumer / closure23 proposal

Original30/runbook03 section2, same uncapped local batch/source-order exception.
Reviewed C8 command produces actual observed executable/configuration metadata;
the existing Python authority application needs a bounded typed consumer before
later service composition. Use the already planned windows_service.py application
boundary, not another enrollment resolver/authority engine or native reader.
H7 builds pure values/decoder ONLY, no service loop or effect capability yet.
Sourcebaseline876223b3d04d5a0baedda9d5cdbcd9c1092431a2 is exact-blob local source
staging, NOT formally integrated/qualified source. H1/H2B/H3/H4/H5/H6/C8 existing
proofs reused; no unchanged native test campaign or new protocol design.

CREATE ONLY library/local_orchestration/grant_authority/windows_service.py and
tests/test_grant_authority_windows_service.py; MODIFY0/DELETE0. Independent module
responsibility = protected Windows authority application edge; tests = its shared
wire/ordering fixture. No new per-case files/DTO package/Runner/framework.
A before B under existing type preflight; Root may derive bounded construction
Grant, review normal constructors, then bind exact reviewed A for decoder B.
No real Host/source qualification precondition is invented to build these values.

H7-A exactly two private frozen strict models using existing _StrictModel,
_CanonicalWindowsPath/_CanonicalSid/_Uint32/_Uint64 and Pydantic annotated aliases:
_ObservedEnrollmentFile has REQUIRED path, sha256, size_bytes, owner,
descriptor_sha256, volume_serial, file_id. Raw digest fields exactly64 lowercase
ASCIIhex, matching C8 Sha256Value (not a new authority/hash engine). size_bytes
strict integer1..67108864, volume uint32/fileIDuint64 including0; no bool/coercion.
_ObservedEnrollmentMatch has REQUIRED scope literal SOURCE_ONLY_UNQUALIFIED,
status literal MATCH, reason literal NONE, executable/configuration each exact
_ObservedEnrollmentFile, neither nullable, all extras rejected/no defaults.
Paths remain exact validated codepoints, never normalize/casefold/copy Expected.
These are wire-value consistency only; constructors never attest their source,
protection, real file contents, running image, exclusive lease or qualified Host.
Do not add public approval/status/result types or a second failure state machine.

H7-B one private _decode_observed_enrollment(payload: bytes) ->
_ObservedEnrollmentMatch | None. Exact bytes1..262144, strictUTF8, ONE JSON value,
duplicate keys/nonfinite/depth/malformed failures ->None, no partial observation.
Reuse existing client._unique_object/_reject_json_constant/_check_json_depth,
not another JSON parser; shared framing helper is not reused because C8 has no
four-byte frame and has a different frozen ceiling. Only exact MATCH/NONE with
both complete files returns the unqualified typed value; every REFUSED/null/
unknown status/scope/reason or missing/extra/mistyped field returnsNone.
No JSON/metadata is promoted to trusted authority or an effect capability.

H7T1 A ordinary direct/JSON legal construction, allfield required/nullability,
frozen/extras/bools/uint bounds/hash/SID/canonical Unicode path matrices and
literal nested fields. No constructor/field first-red ceremony; strict2/import.
H7T2 B actual decoder with independent literal C8-schema bytes produces exact
observed metadata, not expected substitution; valid bounds/Unicode/uint0 pass.
Refused/partial/duplicate/bounds/encoding/depth/shape/status mismatch refuse.
H7T3 block filesystem/Git/subprocess/socket/native/clock/env/provider operations,
exercise pure real decoder, no real observe command/helper/Host campaign.
H7T4 actual required/default/strict field (A) and decoder ceiling/duplicate/status/
partial bypass mutations (B) =>namedRED/exactrestoreGREEN; Root different door.
No expanded shared-helper source changes or reimplementation; source+90/test+180
effective forecast, >500 structural review not minify/split. Current claim is
wire-source engineering only; actual protected helper invocation/client peer/
ledger/read transaction/SCM/launcher/OS qualification remains later bounded work.

Root reviewer/orchestrator; released H6 author /root/ticket30n4_peer_impl,
distinct /root/ticket30_native_tools_review source helper. Preregister contained
.worktrees/skill-improvement-30g-service-wire and matching-review, codex/same,
ctx-ticket30g-service-wire-20261020; ownedTemp/johnny30g-wire-owner-20261020 and
-review-20261020, owner+TTLthroughreview/seal/holds, no cleanup authority.
Conditional grant-ticket30g-service-wire-20261020 rev01 A_ONLY NOT_ACTIVE until
DOC_PASS/exact stage mapping/source/role/nonreparse Git preflight. Child55/outer60,
one ownedTemp cache, full raw/time/source hashes; uncapped policy preserveshistory.
No install/Host/native/helper/process/security/SCM/network/cleanup/model/cost/
formal integration/qualification/30B43 release/push/release/deploy.

## 30N5-N6 — finite offline HTTP stimulus adapter / closure22 proposal

Original30/runbook03 section3, same uncapped batch/first-CVQ source-order scope.
N5 codec969aa0ee already source reviewed; next reuse it at the existing fixture
module's HTTP edge, not a new mock-server framework/provider or qualification.
This slice builds and tests handler code ONLY with in-memory socket doubles;
it never binds/listens/connects or launches CLI/Host/model. Real wire compatibility
with the installed CLI remains UNVERIFIED and may later yield UNAVAILABLE.

Sourcebaseline969aa0ee05c83720cdd1e25b71ac0594f91c8e2a.
MODIFY ONLY tests/staging/readonly_host_protocol.py and tests/test_readonly_review_host.py.
CREATE0/DELETE0; CVQ/Runner/process lifecycle/config/product/native/tooling READ_ONLY.
Reuse existing FunctionCallStimulus/encode_function_call_sse and independent literal
SSE oracle/shared fixtures. No additional request/result DTO, policy engine,
Response schema copy, token counter, permanent test script or parallel listener.
One factory takes exact valid FunctionCallStimulus and returns a typed standard
library BaseHTTPRequestHandler subclass. It creates no socket/process/thread/file,
never reads env/auth config, calls API, executes arguments or emits a PASS verdict.
No new constructor bootstrap: existing reviewed six-field carrier is sufficient.

Exactly one accepted POST /v1/responses per factory/fixture lifetime, shared finite
thread-safe attempt claim before body processing, all later attempts fixed429.
Invalid attempts consume the same one-attempt allowance; no internal retry/reset.
Fixed endpoint is fixture data, not a claim every CLI uses it. Other paths/methods
refuse with finite fixed response, never generic proxy/echo/arbitrary route.
Exactly one Content-Length ASCII decimal, inclusive1..65536bytes; missing/duplicate/
invalid/oversize refuses before body read. Any Transfer-Encoding, Authorization
or Proxy-Authorization refuses; this fixture must never receive real credentials.
Exact body length, strict UTF8/JSON object, reject duplicate keys/nonfinite values/
malformed/deep failures. Consumed fields: exact model==stimulus.model, stream is
True, tools list contains exactly one matching type=function/name==tool_name.
Other roster entries may remain: fixture does NOT hide or qualify Host tools.
Do not persist raw body/headers/prompts; no handler logging of request/error data.

On legal request, return HTTP200, Content-Type text/event-stream, correct byte
Content-Length, Connection close and exactly existing bounded six-event SSE bytes.
Use stdlib HTTP parser, not handwritten HTTP grammar. Header/request-line limits
retain stdlib finite limits; connection timeout5s before parsing, one request per
connection, finite output error/timeout handling. This is transport stimulus ONLY,
not observed denial/effect evidence. The future protected observer and qualified
Host must prove actual dispatch and restrictions; input IDs/fixture response never
become Observation/CaseResult or trusted authority.

N6F1 actual BaseHTTPRequestHandler.handle path over finite in-memory connection
double: legal literal request/headers/JSON returns200 and independent N5 literal
six-event oracle, Unicode/control preserved, exactly one attempt across instances.
N6F2 wrong method/path/framing/duplicate Content-Length/Transfer-Encoding/auth,
truncated or oversize body, invalidUTF8/JSON/duplicate key/nonfinite/deep input,
model/stream/tools mismatch or duplicate selected tool reject with fixed response;
boundary65536 legitimate input remains legal. No body/secret echo or log output.
N6F3 timeout set before request parsing, connection close, write/read failures finite,
second/concurrent attempt rejected; no socket bind/connect/process/API/env access.
Block real socket/process/provider effects, use one shared connection fake and
parameterized matrix; no per-case files/servers or new process runner.
N6F4 actual source weakening request allowance/body bound/model binding/framing or
auth rejection, SSE source substitution =>namedRED/exactrestoreGREEN; independent
Root different door. Reuse prior103 codec construction/behavior proofs unchanged;
affected full test file, strict2, guarded memorycompile/import/source hashes.
Forecast product+160/test+220 effective; >500 structural review not minify/split.

Root reviewer/orchestrator; released N5/C8 author /root/grant_transport_impl,
distinct /root/batch_authority_review source helper. Preregister contained
.worktrees/skill-improvement-30n5-finite-http and matching-review, codex/same,
ctx-ticket30n5-finite-http-20261020; ownedTemp/johnny30n5-http-owner-20261020 and
-review-20261020, owner+TTLthroughreview/seal/holds, no cleanup authority.
Conditional grant-ticket30n5-finite-http-20261020 rev01 NOT_ACTIVE until DOC_PASS,
fresh exact baseline/nonreparse Git/carrier-constructor preflight. Child55/outer60,
one ownedTemp mypy cache, full raw/timing/no ineffective retry. No actual network,
socket/Host/CLI/model/cost/config/security/install/cleanup/qualification/30B43
release/formal integration/push/release/deploy; later operational Grant separate.

## 30N3-C8 — observed enrollment output / closure21 proposal

Original30/runbook03 section2, same batch/first-entry source-order scope. Bounded
Architecture Owner readback finds C7 WindowsEnrollmentReadback already measures
closed CodeRoot plus configuration/ancestors on actual handles, and its verifier
checks complete inventory/protection/content. EnrollmentCommand only exposes
MATCH/refusal, so it cannot populate later observed image/config hashes. Do not
copy expected digests into H2 or create a persistent helper/second authority.
Reuse actual C7 objects and command/test seams; no native observer redesign.

Sourcebaseline7a24e165391bbc3beea2d13fb492555d3b8f485e. MODIFY ONLY
library/local_orchestration/native_windows/EnrollmentCommand.cs,
library/local_orchestration/native_windows/Program.cs,
library/local_orchestration/native_windows/NativeEnrollmentCommandSelfTests.cs.
CREATE0/DELETE0; parser/manifest/readback/verifier/job/C#project/Python/tests and
all external configuration READ_ONLY. Same original PRD/CHG/SPEC, no new policy.
Existing typed NativeEnrollment/Readback/ObjectObservation/Verification ordinary
construction already exists; no new public DTO or constructor bootstrap needed.

One exact new command selector observe-enrollment, one argument only, same strict
bounded enrollment stdin/parser and ONE existing readback callback. Existing
verify-enrollment and every old mode keep byte-for-byte output/exit semantics.
Only internal output selection/helper as needed, no generic query/command option.
Observe output root exact scope/status/reason plus executable/configuration.
Scope always SOURCE_ONLY_UNQUALIFIED; status/reason are existing verifier result,
never caller approved=true or a new qualification/PASS. Each payload is null if
no uniquely selected OBSERVED FILE exists at its corresponding enrollment path;
otherwise exact fields path, sha256, size_bytes, owner, descriptor_sha256,
volume_serial, file_id from that ACTUAL observation, not expected payload data.
Do not emit content, full SDDL, credentials, process/Grant identity or timestamps.
Executable selection searches actual CodeInventory; configuration actual DataObjects.
No first-match on ambiguity. Missing/unavailable observations cannot give MATCH.
For a verifier refusal, available genuine selected observations may remain in
the diagnostic output with REFUSED/nonzero exit; these never authorize a consumer.
This permits pinning actual wrong hash/size rather than laundering expected data.
Readback null/exception gives REFUSED/READBACK_FAILED with both payloads null.

Serialize the complete UTF8 JSON plus LF into one bounded in-memory buffer <=262144
bytes before a single external write; reuse a fixed-capacity MemoryStream rather
than new counting-stream framework. Overflow/output exception finite exit2/fixed
error, never success or native exception detail. This is bounded buffering, NOT
an atomic OS write claim: a faulted downstream stream can retain partial bytes,
which are unusable incomplete evidence. Old verify error shapes remain unchanged.
All observed values immutable existing types. Later consumer must separately
revalidate exact source/argv/binary/protection and status/paths/schema; this command
does not attest running client code or supply an exclusive retained-handle lease.
Service and client payload/config identity remain distinct enrollments, never
silently substituted. No subprocess/SCM/Host/session/ACL/pipe call in this slice.

C8F1 old verify/default/enrollment/job-CONTRACT fake self-tests unchanged green;
new selector legal result pinned to literal observed file IDs/digests/size/owner/
descriptor/volume and one callback. Unknown/extra args and invalid input =>0reads.
C8F2 real Program->EnrollmentCommand seam with existing shared matching builder;
wrong observed hash or size REFUSED and reports ACTUAL wrong value, missing/
unavailable/null/throw/selection mismatch no invented values; no output success
after failed verifier. Exact independent JSON schema/oracle, Unicode/escaping.
C8F3 finite buffer/output fault/error sanitization, no full SDDL/raw source/secret;
no new physical fixture or per-case scripts. Do not invent unreachable overflow
input; inspect/prove static bound and test genuine writer failure at current seam.
C8F4 actual source mutations at observed-vs-expected digest/size, wrong payload
selection/file ID, missing-result success or verification bypass =>namedRED and
exactrestoreGREEN. Root different door, full raw output. Existing reader/verifier
unchanged evidence reused; no unchanged full matrix campaign required.

Offline pinned .NET10.0.302 net10.0-windows, warnings-as-errors/nullable; existing
NuGet.Config clears sources. Build/output/cache only owned Temp, no restore from
network/package install/shared compiler. Execute self-test, enrollment-contract-
self-test and job-contract-self-test (fake only); NEVER inspect/verify/observe
against real paths, job-self-test/job-fixture modes, full native Python tests,
symlink/ACL/Host/IPC/permissions/network/service/installation effects. New command
is exercised through fake injected existing callback inside self-tests only.
Forecast product+100/test+120 effective; structure review >500, not minify/split.

Root reviewer/orchestrator, implementation-standard author named only after its
current lane returns/releases; independent source peer separate. Preregister
.worktrees/skill-improvement-30n3-observed-enrollment and matching-review, codex/same,
context ctx-ticket30n3-observed-enrollment-20261020, owned Temp/johnny30n3-observed-
owner-20261020 and -review-20261020; owner+TTL through review/seal, holds override.
Conditional grant-ticket30n3-observed-enrollment-20261020 rev01 NOT_ACTIVE until
DOC_PASS/exact baseline/nonreparse Git/ordinary prior-constructor checks. Child55/
outer60, raw argv/time/stdout evidence, no renewed cumulative/count ceiling.
No formal integration/qualification/30B43 clearance/cleanup/push/release/deploy.

## 30N4-H6 — retained process facts / closure20 proposal

Same original30/runbook03/local batch. Architecture readback of C7 at7a24e165:
C# N2 GetProcessId/GetProcessTimes/IsProcessInJob exists, but only internal to its
short fixture executable. A one-shot subprocess output outlives those handles;
a new persistent helper/protocol would add avoidable lifecycle/trust work.
Root and distinct architecture peer select a smaller Python platform ABI adapter,
not a second authority engine/helper service. Tiny cross-language native bindings
are necessary because existing C# internals are not callable here; reuse N2 ABI
semantics and H2 pure values/H4 token-query/Close primitives rather than duplicate
domain comparison or closed-file inventory. No modification to their reviewed code.

Sourcebaseline37410685e9232e6f50c8bd25066754e37c48b513 (H4 source staged only).
CREATE ONLY library/local_orchestration/grant_authority/windows_retained_process.py
and tests/test_grant_authority_windows_retained_process.py; MODIFY0/DELETE0.
H1/H2/H3/H4/C7/ledger/service/Host/config/CLI all READ_ONLY. N5closure19 and
H5closure18 unchanged and independent. Constructor A before reader B on immutable
reviewed A. No new PRD, generic Reader/lease registry/Protocol/store/runner.

H6-A one frozen strict _RetainedProcessObservation with required process_id
positiveuint32, windows_session_id uint32, process_creation_time_100ns positiveuint64,
job_membership existing _JobMembership restricted to MEMBER or NOT_MEMBER (not
UNAVAILABLE as a fabricated fact), process_image_path existing canonical Windows
path. Reuse H2 strict model and aliases. One finite observation-failure enum and
typed error may retain a Close-capable token owner only for failed/uncertain token
cleanup. Required token owner iff TOKEN_CLOSE_FAILED; other failures no owner.
No default/approved/trusted/ref/evidence/expected/process/job handle in result.
Ordinary direct/JSON/boundary construction, retained identity/lifetime negatives
before native behavior; no missing-code first-red ceremony.

H6-B private reader accepts exact native owning process+job PyHANDLE objects under
one issuing service thread. Validate pure inputs and both nonzero/non-sentinel
pointer-width numeric aliases (no coercing arbitrary caller objects) before native
call. Same-thread check before every read, exact original owning wrapper retained,
validate still-open original handle spelling before/after read; never OpenProcess
by PID, ProcessIdToSessionId, duplicate/reopen/Detach/Close borrowed process/job,
datetime/float FILETIME conversion or launch/kill/wait/enroll operations. Reader is
only a synchronous borrow, NOT an exclusive-lease proof: a strong reference cannot
prevent concurrent explicit Close/handle reuse. Future protected launcher must own
and serialize these exact handles over complete H4->H6->H2 binding window with no
outside callbacks; absent that qualified composition remains UNAVAILABLE. No bool,
caller marker or fake lock is promoted to proof of that external precondition.

Read GetProcessId and GetProcessTimes from SAME process handle, FILETIME high<<32|low
as exact unsigned64; IsProcessInJob exact SAME process/job pair must distinguish
native call failure from successful NOT_MEMBER. OpenProcessToken TOKEN_QUERY on
that SAME process owner, query existing TokenSessionId primitive on retained token;
close own temporary token exactly once before returning output. Recognize/retain
Close-capable token before validating query-handle shape (H4 E01 rule). Query/
validation/native failures still close; failed/uncertain Close retains exact owner,
poisons reader and next read refuses before effects. Never impersonate/Revert or
close caller-owned process/job. QueryFullProcessImageNameW flags0 on SAME process
handle, one bounded32768-WCHAR buffer; require nonempty returned length<capacity,
exact UTF16 units/content/termination and canonical H2 path, no truncation/normalizing
guesses/grow loop. Path is not file digest or proof loaded dependencies/config.

All ctypes argtypes/restype and raw returns confined to typed outer ABI wrappers;
zero/failed API result/invalid output yields finite error, no partial success,
bool-as-int acceptance, Any/type-ignore/caller expected substitution. Do not load
DLLs during import/constructor; B tests install finite fake DLL/API BELOW actual
bindings plus block real WinDLL/native calls. Reuse H4 native token/query owner
helpers where semantically exact, no copied comparison/security-role engine.
No claim these facts alone establish live writer (process handles remain valid
after exit), last-message identity, image-content/config digest, trust or Grant.
H4 actual message and later protected launcher/config/readback remain mandatory.

H6T1 literal ordinary constructor matrix allfivefields/JSON/strict/nullable/domain.
H6T2 actual native-wrapper fake path pins exact process/job/token handle args,
query class/TOKEN_QUERY, FILETIME high+low, known negative membership, bounded
Unicode path/session0 positives and token Close before result. Real API guard0.
H6T3 null/closed/int/bool/sentinel/malformed owner, wrongthread, query/API/shape/
image-too-long/length disagreement/noncanonical/zeroPID/time failures reject,
borrowed owner0Close; every own token cleanup phase and poison/no-second-effect
negative, malformed Close-capable token retained/closed as appropriate.
H6T4 actual raw FILETIME word swap/drop, wrong borrowed handle/query selector,
success-result vs membership confusion, token owner retention/Close or image
length weakening => namedRED/exactrestoreGREEN; independent Root differentdoor.
Shared native fake and parameterized cells, no per-case scripts. Preserve H4
unchanged proof, run only affected/new tests plus strict2/memory compile/import
and loaded-source hash. NativeC# old fixture campaigns never run here.
Source forecast200/test250effective; >500 triggers responsibility review, not
minify/split/newframework. No source prompt/ticket narrative or screenshots.

Primary ABI references fetched2026-10-20:
https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes
https://learn.microsoft.com/en-us/windows/win32/api/jobapi/nf-jobapi-isprocessinjob
https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-queryfullprocessimagenamew
Existing installed PyHANDLE class metadata (dir/descriptor only, no handle/API
operation) confirms Close/Detach/handle fields; no real token query used as proof.

Root reviewer/orchestrator; implementation-standard author allocation chosen only
after a current author returns/released (no simultaneous second lane); distinct
/root/ticket30_native_tools_review source peer. Preregister contained author
.worktrees/skill-improvement-30n4-retained-process and matching-review, codex/same;
owned Temp/johnny30n4-retained-owner-20261020 and -review-20261020 with owner+TTL
through review/seal, holds override. Context ctx-ticket30n4-retained-process-20261020.
Conditional grant-ticket30n4-retained-process-20261020 rev01 A_ONLY NOT_ACTIVE
until DOC_PASS/fresh baseline/Git/nonreparse/normal shared constructor preflight;
pin named author before dispatch. B later rev02. No Owner technical renewal.
Reuse one ownedTemp mypy cache, -B/no-cache/autopluginsdisabled, child55/outer60,
mechanical full raw/time capture and evidence-progress root-cause rule.
No real native probe/Host/service/install/ACL/network/model/operational grant/
source qualification/30B43 clearance/main integration/push/release/deploy/cleanup.
Return only source candidate/checks/evidence; actual exclusive lease/issuer remains
a later protected composition dependency, not a fabricated completed capability.

## 30N5 — finite offline Responses stimulus codec / closure19 proposal

Original30/runbook03 section3 and first-CVQ order exception only; parent uncapped
batch. This independent local fixture does not depend on H5 adoption or a live
issuer. H5 closure18 and all current source/Review/Recovery/cleanup holds remain
unchanged. Exact sourcebaseline24c79d2278b36afcc816a9eab1e6c2c18caabbd7, whose CVQ
pure evaluator is SOURCE_BEHAVIOR_STAGED_PASS only; no qualified-source upgrade.
No new PRD/SPEC semantics or CVQ port. Root's initial guessed package/ticket-path
reads failed; actual Git tree discovery then found the exact CVQ package/source,
not evidence a capability was absent.

CREATE ONLY tests/staging/readonly_host_protocol.py and
tests/test_readonly_review_host.py; MODIFY0/DELETE0. This is the shared finite
stimulus codec already planned by runbook3, not a generic mock server/Runner.
No library/readonly_review_host.py placeholder, HTTP listener, subprocess,
socket/file writes, Host/model request or credential/config access in this slice.
Existing process_runner/environment_core stay read-only for later lifecycle reuse.
Constructor first, then codec in same2files after immutable ordinary preflight.
Keep tests one responsibility/parameterized, no per-case standalone scripts.
Source forecast<=160effective/test<=200, screenshots/artifacts0 apart registered raw.

One immutable typed FunctionCallStimulus binds response/item/call identifiers,
model label, tool name and opaque arguments text. Each field required/non-null/
strict exact string. Each of the five identifiers/model/tool labels matches
[A-Za-z0-9_.:-]{1,128} exactly; arguments text is0..4096UTF8 bytes, rejects invalid
Unicode, preserves whitespace/control through JSON escaping, no strip/normalize/
coercion. Opaque
arguments are bounded raw model-output text (may deliberately be malformed JSON),
never parsed/executed or treated as trusted authority. No API key, real model
literal, project path/SHA/ticket prompt in shared source. Constructor invalid
input cannot call native, network or process functions; no new domain framework.

Codec emits exact UTF8 SSE bytes for one function-call response only. Ordered six
events: response.created, response.output_item.added,
response.function_call_arguments.delta, response.function_call_arguments.done,
response.output_item.done, response.completed; contiguous sequence numbers0..5,
output_index0, consistent response/item/call/name/arguments links and exact JSON
escaping. Start item has empty arguments, final item/completed output carry exact
opaque original text. Response status in_progress->completed; deterministic fixed
fixture timestamp/counters are synthetic protocol data, never billing/effect
observations. Two-LF event separators and terminal delimiter, finite total output
ceiling131072bytes, reject oversize before returning bytes. Ordinary valid bounded
carriers must encode, including4096ASCII bytes and worst escaping; do not invent
an unreachable over-ceiling caller case. Defensive output-bound mutation can use
an explicitly injected test bound without claiming that changes operational policy.
No arbitrary event/command/URL,
sleep/retry/server/evaluation or self-issued PASS/CaseResult/evidence record.
This narrow function-call wire variant does not claim custom-tool/native MCP
compatibility or that the installed CLI consumes it; those exact variants follow
only actual versioned discovery, not assumptions.

Official format sources actually fetched2026-10-20:
https://developers.openai.com/api/docs/guides/function-calling
https://developers.openai.com/api/reference/resources/responses/streaming-events
https://learn.chatgpt.com/docs/config-file/config-advanced
First two specify function-call streamed item/arguments events; provider config
documents responses/base_url/retry knobs, not proof this local binary supports
a loopback/native dispatch campaign. This is a finite protocol fixture, not an
API-backed client; no key/account/provider call is needed or permitted.

N5F1 constructor: normal Unicode arguments and explicit empty arguments positive;
missing/null/non-string/bool/blank identifiers/control/lone-surrogate and exact
UTF8 inclusive/exclusive size edges reject as specified. Opaque malformed argument
text remains literal, never executed or silently repaired.
N5F2 real codec: independent literal event names/sequence/IDs/status/output/arguments
assertions after ordinary JSON decoding; deterministic repeated bytes, escape/
Unicode roundtrip and empty args, finite byte ceiling. Expected not copied from
Actual/generator constants. A count-only/self-roundtrip test is insufficient.
N5F3 wrong item/call/name/arguments link, reordered/duplicate/missing/incorrect
sequence or escaping/terminal delimiter mutation at actual encoder each pins
named RED/restoredGREEN. Root different door. Full stdout/default traceback.
N5F4 no-effect/import/scope: inject forbidden socket/subprocess/provider/file-write
seams, constructor/encoder/import must perform zero effects; strict affected2files,
memorycompile/import and actual candidate source/hash. Do not run default pytest,
CLI or real API. Missing wire/native compatibility stays UNVERIFIED, not PASS.
New behavior has no ceremonial missing-code first-red; source mutation tests
prove discriminating power. Formal CVQ prerequisites/evaluator/admission unchanged.

Root reviewer/orchestrator, author /root/grant_transport_impl after37 source lane
released into CLEANUP_BLOCKED hold, distinct source peer /root/ticket30_native_tools_review.
Context ctx-ticket30n5-readonly-stimulus-20261020. Preregister contained author
.worktrees/skill-improvement-30n5-readonly-stimulus / matching-review, codex/same
branches; owned Temp/johnny30n5-stimulus-owner-20261020 and -review-20261020,
owner+TTL through review/seal, holds override; teardown only after evidence seal/
independent confirmation and exact safe scope, no denied cleanup retry.
Conditional grant-ticket30n5-readonly-stimulus-20261020 rev01 A_ONLY NOT_ACTIVE until
DOC_PASS, exact fresh source/Git/nonreparse and existing normal constructor checks;
rev02 codec only after A. Same-lifetime direct lane receipt/Runner NOT_REQUIRED;
current offered implementation-standard capability, no model hardcoded in source.
Explicit ownedTemp mypy cache, process-local autoplugin disable/no-cache/-B,
child55/outer60 and resource recording; evidence-progress not blind retries.
No native/Host campaign, socket bind/connect, service/install/security/environment/
global config/network policy, operational issuer,30B43 clearance, main integration,
push/release/deploy or old hold removal. Return exact candidate/files/checks/raw/
findings/deviations only; function-call fixture is not actual Host isolation proof.

## Mainline ticket contract

```json
{
  "schema_id": "mainline-ticket/revision-01",
  "ticket_ref": "wg-ticket-30",
  "ticket_revision": "rev-535a99b32754942aacc4870710766125881110e5f61646594a6d049846a8704d",
  "status": "waiting",
  "depends_on": ["wg-ticket-29"],
  "admission_ref": null,
  "evidence_refs": ["review-wg30a-fixture"]
}
```

此節點是完整 Ticket30 的開放狀態；30A 的已消耗 fixture Grant 不可成為真來源
或新實作 admission。29→30 是本票實際重用純投影的能力依賴，不是清單順序。
本輪文件工作有下節獨立授權；不因此將完整票30改成 admitted/completed。

## 30N4-H5 — owning pipe adoption / closure18 proposal

Same original30/runbook03/PRD009/CHG009/uncapped batch. Necessary source ownership
handoff, no new capability/PRD/Host gate. Root architecture readback and distinct
/root/batch_authority_review agree H3 returns owning PyHANDLE while H1 closes raw
int; directly passing int(owner) risks double-close. Reduce the next slice to
MODIFY ONLY library/local_orchestration/grant_authority/windows_transport.py and
tests/test_grant_authority_windows_transport.py; CREATE0/DELETE0. Do not yet create
windows_service.py or a temporary session wrapper; H1 already owns one-frame IO.
Existing H3 factory/peer/codec/ledger/native tools and all Host settings READ_ONLY.

First prepare one controlled engineering-only baseline: exact reviewed H3
8b0402e4dbb03f61b44146c41c7e1166c504879c plus reviewed H1
cc4744e24cb7ad28b212601d88e4ef3447e3280f, common5449c0634866b3334e3963c87b8603eb973e39bd.
Only2H1 files may be added to H3 tree, no hand edits/conflict resolution/other
candidate. Pin resulting merge SHA and all4source/test blobs before Grant activation.
This is isolated engineering composition, not formal main integration or qualified
adversarial review. Existing source/Recovery/lifecycle holds stay effective.

H5-A extend only existing WindowsMessagePipeError constructor with typed nullable
retained native pipe/event owner references needed when initialization cleanup
fails. Reuse existing failure enum/PyHANDLE/strict native boundary checks; no new
DTO/Protocol/enum or duplicate lifecycle state machine. Pure ordinary constructor,
no cleanup side effects, retained identity/lifetime and finite failure/nullable
state tests plus strict/memorycompile. B inactive until immutable A preflight.

H5-B migrate private _WindowsMessagePipeIO constructor from raw pipe integer to
the actual factory owning PyHANDLE. Validate exact native owner identity and
nonzero/non-sentinel pointer-width handle before event/IO; no int coercion of
caller objects or Detach. Perform all ordinary thread/deadline/cancellation input
checks before adoption; rejected input leaves pipe with caller, zero Close/IO.
After validated adoption, IO retains SAME wrapper for its lifetime; numeric alias
is only for Win32 calls. Normal close calls wrapper.Close exactly once, never
raw CloseHandle(pipe), and remains idempotent. Borrowed cancellation event untouched.
On completion-event creation/initialization failure after adoption, close confirmed
owned resources once; failed/indeterminate Close retains each uncertain owner in
the existing typed error, never reports cleanup success. Existing pending/drain
RECOVERY_HELD keeps SAME pipe/event/overlapped/buffer alive, forbids Close/reuse;
do not replace owners, add GC/finalizer cleanup, retry cleanup or hide exceptions.
No change to single-message count/byte bounds/thread/deadline/cancel semantics.

H5-TEST before migration enumerate every tracked constructor caller in combined
baseline; migrate only the existing H1 test helper/cases. Any non-test consumer
outside exact2paths is a concrete scope blocker, not permission to modify it.
TEST->A->B evidence stays through real IO connect/read/write/close seam; existing
native fake/weakref/finalizer helpers reused, no second browser/runner/fixture system.
Cases: lawful same-owner byte-exact single frame and exactly-once close; integer/
bool/zero/sentinel/nonowner reject before native effects; bad pure inputs leave
caller owner; failed init closes once or held failed-close owner; failed event
cleanup retained; normal close failure blocks reuse; pending drain holds SAME owner
and all active resources without second read. Preserve H1 regressions and H3 fixed
profile tests. Actual mutations owner retention/drop, raw-close substitution,
duplicate-close/idempotence and premature release on pending/failed-init => named
RED/restoredGREEN; Root different constructor-cleanup door. No old test retirement.
Forecast product+70/test+120 effective, same cycle budget/history;500 triggers
responsibility review not forced split/compression. No prompts/ticket narrative.

Root reviewer/orchestrator; author /root/ticket30n4_peer_impl ONLY after H4 correction
returned/released to source hold. Distinct /root/ticket30_native_tools_review.
Context ctx-ticket30n4-pipe-ownership-20261020. Preregister contained engineering
WT .worktrees/skill-improvement-30g-pipe-ownership-baseline and author
.worktrees/skill-improvement-30g-pipe-ownership / matching -review, codex/same
branches; owned Temp/johnny30n4-ownership-owner-20261020 and -review-20261020.
TTL through review/seal, holds override; no cleanup or denied-operation retry.
Conditional grant-ticket30n4-pipe-ownership-20261020 revision01 H5-A_ONLY remains
NOT_ACTIVE until DOC_PASS, exact combined baseline and fresh nonreparse/Git/normal
existing-constructor checks. B follows same2path revision02 after A, no Owner
renewal. Direct lane receipt/Runner NOT_REQUIRED. Focused patched-native pytest,
strict affected2files, memorycompile/guarded import, full raw stdout/stderr/argv/
elapsed/exit in ownedTemp; autoplugin disabled/no-cache/-B/child55/outer60.
No real pipe/token/event/Host probe, service/SCM/package/security/install action,
grant/dispatch/receipt/response effect, operational positive, qualification,30B43
clearance or main integration. Later retained process/job/rawFILETIME and closed
runtime/config observations remain necessary; never fill H2 from expected values.

## 30N4-H4 — last-message token observation / closure17 proposal

Same original30/PRD009/CHG009/runbook03 and parent uncapped batch; protected
service's necessary native identity edge, not an independent observer Framework.
Baseline c13d10171f3819c1b6770218303806dc20f14eb3. CREATE ONLY
library/local_orchestration/grant_authority/windows_message_identity.py and
tests/test_grant_authority_windows_message_identity.py; MODIFY0/DELETE0.
All H1/H2/H3/native tools/client/ledger/codec/source/Router remain READ_ONLY.
Reuse H2-A _StrictModel/_CanonicalSid/uint aliases/token+level enums and current
protocol fixtures. No duplicate SID, PID-from-enrollment or process-time reader.
N2 raw FILETIME/job observations remain a separate retained-handle responsibility,
never filled from expected enrollment values or rounded Python datetime.

H4-A constructor-first: one private frozen strict _LastMessageIdentity value with
endpoint_pid (positiveuint32), endpoint_session_id (uint32), last_message_sid
(canonicalSID), last_message_session_id(uint32), authentication_id_luid(uint64),
token_type(existing _TokenType), impersonation_level(existing _ImpersonationLevel).
No defaults, caller trusted/approved flag, handles, expected identity or raw token
bytes. Finite private observation-failure enum and typed exception can carry a
retained owning token solely on cleanup/revert uncertainty, never success. A only
definitions/normal constructor validation/roundtrips and negatives; no native calls
or observation behavior until immutable A ordinary constructor/strict/source review.

H4-B private thread-bound observer takes one positive borrowed pipe integer and
the issuing Python thread identity; no connect/read/write/decoder/ledger/spawn.
Caller must already have quarantined one complete message via H1, later protected
composition owns this ordering. Native observer cannot manufacture proof of prior
read. It records actual last-message security context, NOT actual writer identity.
Wrong input/thread/poisoned observer refuses before native calls. Before own
impersonation attempt, OpenThreadToken(GetCurrentThread(),TOKEN_QUERY,True) must
return ERROR_NO_TOKEN; any other error refuses. A pre-existing owning token is
closed and THREAD_NOT_CLEAN returned without impersonation or RevertToSelf: never
drop an unrelated thread's security context. Cleanup failure retains owner/fatal
hold. Current-thread pseudohandle is borrowed and must never be closed.

After clean-thread proof, query actual pipe client PID/session and attempt
ImpersonateNamedPipeClient on this issuing thread. Open only TOKEN_QUERY on its
thread token; query TokenUser,TokenSessionId,TokenStatistics,TokenType and
TokenImpersonationLevel. ConvertSidToStringSid must yield exact canonical spelling;
TokenUser has exact (PySID,int flags) shape, no caller fallback. TokenStatistics
AuthenticationId is a signed64 integer in installed pywin32311: validate exact int
-(2**63)..(2**63-1), reinterpret the SAME64 bits as uint64 for the existing domain
(not clamp/coerce/drop high bits). Reject bool/unknown shape/missing/overflow. Enum
mapping must explicitly match documented native finite values, unknown refuses.
Native token must be IMPERSONATION; no synthesized level for a primary token.
Observation may report ANONYMOUS but H2's later matching rejects it. All endpoints/
session primitives exact uint32 and endpoint PID positive. Never query ambient
process token or re-open a process by declared enrollment PID as a substitute.

Once impersonation was attempted, ALWAYS RevertToSelf in finally on the SAME
thread, including impersonation/OpenThreadToken/query/parse failure. No result
escapes until successful revert and owned-token Close. Revert failure is fatal,
poisons observer, retains any owning token/recovery evidence and raises a dedicated
BaseException-derived fatal failure; subsequent use performs zero native calls.
Successful revert but token-close failure likewise returns no identity and holds
owner. No retry or token replacement, raw CloseHandle, hidden global cleanup,
SeDebug enable, service control or actual process termination here. Later protected
service must terminate on fatal revert uncertainty; source exception/latch alone
is NOT qualified OS enforcement. No user/SQL/file/codec callback runs impersonated.

H4-TEST existing fixtures plus patched native boundaries only, no real token/pipe/
impersonation/privilege/Host probe. Constructor normal+all finite enum roundtrips,
null/bool/extra/missing/bounds. Positive exact native fake yields identity, native
signed -1 maps to uint64max and -(2**63) maps to highbit exactly. Negative unknown
native enums/session/SID/stats/PID/owner, each call failure, pre-existing token and
wrong thread. Assert exact call order/revert on every attempted path, no revert
before own attempt, no early success/extra read/ambient-token fallback, owning
token exactly-once Close and borrowed handles untouched. Cleanup/revert failures
retain evidence and poisoned next call is effect-free. Actual source mutations
remove clean-thread guard, LUID range/bit preservation, unconditional revert,
deferred success and retained-owner poison separately => namedRED then restoreGREEN;
Root uses a different cleanup-order/borrowed-handle door. Full raw output in owned
registered Temp only. Focused pytest, strict product/test, memorycompile/guarded
import. No new runner/server/policy DTO. Forecast product260/test380 effective;
500 signal requires responsibility review, not forced splitting or compression.

Conditional grant-ticket30n4-message-identity-20261020 revision01, parent samebatch;
H4-A only after DOC_PASS and fresh exact baseline/Git/nonreparse/normal prior-type
preflight. B NOT_ACTIVE until A immutable source preflight; Root then derives same
two-path revision02 without Owner renewal. Source author /root/ticket30n4_peer_impl
only AFTER current H2-B lane returns/released to hold; Root reviewer/orchestrator,
distinct /root/ticket30_native_tools_review. New context
ctx-ticket30n4-message-identity-20261020. Preregister own .worktrees/skill-improvement-
30g-message-identity and matching -review, codex/same branches, Temp/johnny30n4-
identity-owner-20261020 and -review-20261020. TTL through review/seal; holds override
expiry/no cleanup or denied-operation retry. Direct same-lifetime receipt/Runner
NOT_REQUIRED. Default60/child55, old history retained/evidence-progress repairs.
No native effect/Host qualification/install/security/30B43 integration authority.
Current ACTION_REQUIRED DOC_REVIEW, no source implementation Grant yet active.

Primary method facts: Microsoft RevertToSelf docs require process shutdown on
failure (future service boundary, not executed here); pywin32 b311 win32security.i
TokenUser/TokenStatistics and PyLARGE_INTEGER.cpp prove exact tuple/dict/signed64
return shapes. Installed stubs are incomplete, not justification for Any or casts.

## 30N4-H3 — explicit bounded read-pipe factory / closure16 proposal

Same original30/PRD009/CHG009/runbook03 and uncapped batch. Necessary protected
service transport construction, not a new authority engine, deployment or Host
qualification. H1 reviewed cc4744e2 owns IO lifetime; H2-A reviewed
c13d10171f3819c1b6770218303806dc20f14eb3 supplies canonical enrollment/SID values.
This independent source cut starts at exact H2-A candidate; H2-B remains separate
and READ_ONLY. No merge of unreviewed B required to construct this factory.

Baseline c13d10171f3819c1b6770218303806dc20f14eb3. CREATE ONLY
library/local_orchestration/grant_authority/windows_pipe_factory.py and
tests/test_grant_authority_windows_pipe_factory.py; MODIFY0/DELETE0. Reuse
_ProtectedPeerEnrollment normal revalidation, its existing canonical SID and
existing protocol/peer test fixture builders. No new policy DTO, port framework,
public package export, source reader, registry, ledger or duplicated IO runner.
Responsibility: construct one fixed Read pipe with explicit protection, verify
its native creation properties, return its owning PyHANDLE (not detached raw int).
Later reviewed composition explicitly transfers ownership to H1; no transfer,
server loop, connect/read/write, approval endpoint or service start in this cut.

H3-F1 private factory accepts existing enrollment value; revalidate before any
native boundary call. Fixed endpoint \\.\pipe\JohnnyGrantAuthority.Read.v1 only,
no caller-selected name/SDDL/rights/fallback. Service/client SID come from that
value, not ambient username; reject collision with SYSTEM/Admins full-right
principals. Value acceptance does NOT prove protected enrollment, standard-user
membership or authority. Those remain independent enrollment/Host requirements.
Construct explicit protected DACL: SYSTEM, Administrators and exact service SID
full0x001f01ff; exact client SID only0x00100003 (read/write data+synchronize), no
generic-write/create-instance/write-DACL. Owner exact service SID. No null/default
SD, inherited/extra/deny/object ACE, broad user group or caller-supplied approval.

H3-F2 CreateNamedPipe exact duplex|overlapped|first-instance, message type+message
readmode+blocking wait+remote-reject, maxinstances1, requested buffers exactly16388
each (existing4+16384 maximum frame), finite default timeout. Native buffer sizes
are advisory and may round/grow: this bounded factory profile requires initial
observed sizes to be exact integers16388..1048576 each, including normal rounded-up
sizes; smaller native reservations refuse this profile, not a claimed universal
Win32 guarantee. This is bounded
initial readback, NOT a lifetime kernel-memory quota; H1 enforces message bounds.
Explicit
SECURITY_ATTRIBUTES bInheritHandle=False. Retain actual owning native wrapper;
validate positive non-sentinel handle. Read back GetHandleInformation noninherit,
GetNamedPipeInfo type/server/maxinstance/initial-buffer bounds,
GetNamedPipeHandleState message-read/blocking state, and GetSecurityInfo exact
owner/protected DACL/complete ACE set+flags+masks+SIDs. Set equality must reject
duplicates as well as extras. Never repair drift or retry with weaker settings.
GetNamedPipeInfo cannot attest first-instance/remote/overlapped creation flags;
offline tests pin their exact emitted arguments, not fabricated OS readback.
All native dynamic readings validate at boundary; strict mypy, no Any/cast/waiver.

H3-F3 failures stop before exposing owner. If a confirmed acquired owner exists,
Close exactly once via owner, no raw CloseHandle/detach/double close/fallback.
Close failure must retain the owner in a named recovery exception/result, prohibit
success and preserve recovery evidence; do not claim teardown. Malformed native
return without provable ownership must explicitly remain unverified/recovery,
not a fabricated cleanup success. Creation failure returns bounded payload-free
error, no security setting change, default descriptor, alternate name or retry.
An explicit owner return does not imply actual writer identity or Host qualification.

H3-F4 offline fake native boundary only. Existing fixture enrollment and ordinary
legal owning-handle shape pass exact arguments+readback+no-early-close. Negative
cells cover invalid enrollment/pre-effect zero calls, SID privilege collision,
missing/default/wrong owner/DACL/control/ACE type/flags/mask/extra/duplicate,
inherited handle, wrong pipe mode/instances/buffer, invalid owner return,
each boundary exception and cleanup failure retained. No real pipe/event/ACL/Host
probe or actual installation, even for smoke. Patch native adapters, not core
security predicates. Source-only tests prove emitted calls/reducers, not OS
enforcement. Pin actual module file/hash. Each critical first-instance/remote/
noninherit/exact-ACL/owner-retention check gets actual mutation namedRED then
exactrestoreGREEN; reviewer different door uses duplicate ACE or cleanup failure.
Focused pytest, strict product+test, memory compile/guarded import, diffcheck.
Product forecast220/test320 effective; exceeding forecast/500 triggers cohesive
responsibility review, never compression or a second helper framework.

Conditional grant-ticket30n4-read-pipe-factory-20261020 revision01, parent
batch-checklist-local-20261019-uncapped; NOT_ACTIVE until distinct docs review,
fresh exact baseline/contained Git/nonreparse worktree admission and existing
normal enrollment constructor preflight. Named author /root/grant_transport_impl,
standard offered Luna/xhigh; Root reviewer/orchestrator; distinct source peer
/root/ticket30_native_tools_review. Prior H1 allocation moves to SOURCE_REVIEW_HOLD
before next active lane. New context ctx-ticket30n4-read-pipe-factory-20261020.
Preregister own .worktrees/skill-improvement-30g-pipe-factory and matching -review,
codex/same branches, Temp/johnny30n4-factory-owner-20261020 and -review-20261020.
Owner+TTL through review/seal, teardown exact registered assets only after release;
all Recovery/denied cleanup holds override expiry; no cleanup now. Same-lifetime
direct lane receipt/Runner NOT_REQUIRED. Default command60/child55; log resources,
diagnose repeats; old cumulative history retained without artificial cap reset.
Source engineering under first-entry ordering exception only; final qualification
and30B43 holds unchanged. ACTION_REQUIRED DOC_REVIEW then exact activation, not
operational pipe/service/security permission.

## 30N3-C7 — reviewed native composition / closure15 preparation

Necessary reuse, not new product behavior: current C6 staging1fe5c834 still has
older N2 accounting contract and old coupled Python physical fixture. Final
reviewed N2 source1e6847c94dbef84dc17dacaafcc008c6d8ce5379 (original30review
377f24ed) and F1 builder separation7fa12f0c1af3a9b61772636b686b953cb8be4406
(originalsealeb5507d0/d58ebc70) exist on held sidebranches, not automatically
included. Do not reimplement raw FILETIME/process/job queries already provided
by N2 WindowsJobPort or another candidate test builder. Preserve all old failures/
UNKNOWN/recovery; no fresh actual native Job/Host campaign is admitted.

Root source-engineering composition only, under original batch local integration
authority/first-entry staging scope. Exact base1fe5c8342ff7127ac7d19721a423fa42a6832711.
CREATE/DELETE0, allowed composite changes exactly4existingpaths:
library/local_orchestration/native_windows/NativeJobContracts.cs,
library/local_orchestration/native_windows/NativeJobSelfTests.cs,
library/local_orchestration/native_windows/Program.cs,
tests/test_native_authority_tools.py.
Only reviewed N2 and F1 changes, no hand edits, new glue, generic runner or API.
Common N2 mergebase88b707c8585501173bb6898f332ad52a5765ed66 already contains
the native job implementation; finalN2 changes exactlythese4. F1 commonB2
bf5a4a3c82131c308ffa85b2d899d4afd1cf32d9 changes only test_native_authority_tools.
The final Program must retain C6 selector/input bounds/constructor/readback and
adopt N2 exact accounting key; fixture must retain reviewed N2 assertions while
adopting F1 candidate-only build and default-zero symlink behavior.

Preregister Root-owned engineering stagingWT
.worktrees/skill-improvement-30n3-native-composition /
codex/skill-improvement-30n3-native-composition, sourcebaseline1fe5c834;
owned Temp/johnny30n3-native-composition-review-20261020. TTL through independent
review+qualification seal, explicit teardown, holds win; no cleanup or resetting
old C6/N2/F1 WTs/refs/output binaries. Separate outputs protect old exact built
artifacts. Root reviewer performs only ordinary conflict-free git merge --no-ff
of exact N2 then F1, not main integration. If conflict, stop that composition and
prepare same-ticket bounded author resolution, do not infer no-conflict safety,
reset/clean/rebase or ask Owner about routine code decisions.

Before merge, independent DOC scope consistency, Root baseline/clean/Git/
nonreparse admission; existing exact public constructors/evidence reused.
After merge prove exactly4paths, unchanged C6 parser/command/reader/verifier
blobs, finalN2 native contract/selftest blobs, retained F1 builder and N2 assertion
hunks. Run strict offline forced build, default/enrollment/job-CONTRACT-self-test
only (last uses fake port), focused F1 builder/default-no-symlink tests (all file/
subprocess APIs patched, no physical fixture). Do NOT run job-self-test,
job-fixture-* modes, full native Python file or actual Host/native jobs.
No actual symlink/ACL/protected path/pipe/service/model operation. Memory compile/
import/strict Python single affected test, diff checks, peer source review of
exact composite+caller/Expected continuity. Change expected result labels ONLY
as already reviewedN2, no new Expected fromActual. No mandatory full rerun of
unchanged C6/N2/F1 matrices or fake baseline-red claim; source behavior already
reviewed. This slice assembles accepted source, does not close full30/01/02.

Conditional grant-ticket30n3-native-composition-20261020, Root-owned integration
context ctx-ticket30n3-native-composition-20261020, distinct source peer
/root/ticket30_native_tools_review. SOURCE_STAGING_ONLY, no implementer authoring
permission and no operational Grant/Host資格. ACTIVE only after exact DOC_PASS/
resource/Git readback recorded. ACTION_COMPLETED -> AUTO_CONTINUE current
H1/H2 and this bounded engineering composition; formal30G/30B43 remain held.


## 30N4-H2 — protected peer binding values / closure14 proposal

Same original30/PRD009/CHG009/runbook02, uncapped local batch; necessary next
shared service source responsibility, independent of active H1 native IO. Not
another authority engine, Host framework or operational permission. H1 source
and tests are READ_ONLY and not assumed implemented/qualified here.

Baseline5449c0634866b3334e3963c87b8603eb973e39bd. CREATE2:
library/local_orchestration/grant_authority/windows_peer.py,
tests/test_grant_authority_windows_peer.py. MODIFY1:
library/local_orchestration/grant_authority/contracts.py, ONLY factoring its
existing canonical SID validator into one package-internal reusable constrained
SID value/helper and having AuthorityPeer use it with the SAME accepted/rejected
values. No new package export, new module/helper framework, path IO, nativeAPI,
SCM, service, token/job/process handle, grant issuance/claim/settle/reader/spawn,
client/ledger/codec/mainline/Router/Host/dependency or existingtest modification.
Otherpaths DELETE0. Source peer must examine actual old consumer uses before SID
factor; preserve AuthorityPeer JSON shape, primitive strictness and finite bounds.
Existing registration-specific path model is NOT a generic safe path validator;
do not adopt it by name or duplicate unrelated registration/provisioning behavior.

H2-A internal typed construction only: two frozen extra-forbid strict value models
(protected enrollment and complete observation), three finite internal enums for
token type, impersonation level and job membership. They are source-only values,
not trusted observations or authority. Reuse actual GrantReadRequest/GrantPlan/
AuthorityPeer/OpaqueMetadataId/EvidenceDigest; no copied plan/peer DTO and no stored
duplicate plan digest. No model_construct/copy/cast/Any/dynamic lookup/coercion
for success. A model round trip must retain exact SID/path/codepoints and no
normalization; integers reject bool, negative and overflow. Internal bounded
canonical Windows drive-path validation is effect-free: reject relative, UNC,
device, ADS, dot/trailing-ambiguity/control forms; never open/resolve filesystem
or claim path existence/protection. Native C5 remains the independent filesystem
and payload identity/protection mechanism.

Enrollment fields: schema1; existing request_binding, expected_plan, authority_peer;
session_ref/client_sid/windows_session_id/authentication_id_luid/process_id/
process_creation_time_100ns/job_ref/process_image_path/process_image_digest/
configuration_path/configuration_digest. SID != serviceSID. Client configuration
identity is distinct from authority_peer's service configuration identity; do not
equate those digests or substitute one for the other. Process/session uint32 (PID positive),
LUID uint64, creation positiveuint64. No password/tokenbytes/OS handles/ACL/approved
boolean. Image is client identity, not service executable identity; later actual
protected loader must establish each correct payload binding.

Observation fields: endpoint PID/session; last-message SID/session/LUID/token-type/
impersonation-level; retained PID/session/creation/jobref/job-membership; observed
image path+digest and config path+digest. All required, no success defaults or
unknown partial record; finite NOT_MEMBER/UNAVAILABLE cannot match. No actual-writer
field. Future native observer MUST derive these from retained noninheritable
process/job handles, exact last-message token and protected paths, never request
JSON or caller declarations. Missing observation gives no match, not invented data.

H2-B only after A immutable source/strict/ordinary construction review: pure exact
peer match and pure record binding, private/module-local interfaces, no new public
result/port. Match revalidates enrollment+observation and requires impersonation
token with level IDENTIFICATION or stronger, exact SID/session/LUID/endpointPID/
retainedPID+session+creation/jobref+MEMBER/imagepath+digest/configpath+digest.
Return validated bound enrollment or None, not a caller trusted flag. Endpoint
and retained process join must both match original enrollment. This proves value
consistency only: connected PID != proven writer; matching last-message context
does NOT show that process executed write. CONNECTED_PID_IS_ACTUAL_WRITER remains
UNPROVEN; operational admission still fail-closed pending qualified transfer
controls. Pure functions never establish OS provenance by accepting equal objects.

Record binding revalidates existing request and LedgerResult, accepts ONLY
LedgerDisposition.EXISTING (actual SQLiteGrantLedger.read success), matching
grant_ref/operation_ref, exact record.plan == enrollment.expected_plan and matching
record grant. ISSUED/CLAIMED_NEW/SETTLED/REFUSED must not masquerade as read result.
All four valid GrantLifecycle values may be returned as READ METADATA with their
existing exact fields, not converted to active authority; no claim/effect/expiry
permission is inferred. Later protected service composition owns order: H1 one
message -> real observer/mandatory revert -> successful match -> decoder ->
ledger.read -> record binding -> codec. Directly calling the pure binder alone
does NOT establish prior peer match/authorization; tests/documentation state it.

H2-TEST reuse existing protocol fixture builders and normal constructors, not a
new runner/mockserver/JSON codec. Normal exact observation and request/record
succeed; SID maximum bounds and lawful Windows paths retain exact values.
Parameterized negative cells cover primary/anonymous token, SID/session/LUID,
endpoint-vs-enrollment and endpoint-vs-retained PID, retained creation/session,
job ref/nonmember/unavailable, image/config path and digest, request/plan/ref/
ledger-disposition mismatch, null/bool/overflow/extra-field/noncanonical paths.
Actual source mutations removing token guard, LUID exact join, retained creation,
job membership, image/config join, request binding and plan equality must each
make corresponding named cell RED then exactrestore GREEN; zero-red is a finding.
Different Root door targets record disposition or configuration binding.
No new ordinal line cap; forecast product230/test320 plus small SID factor.
Overforecast/500effective lines triggers responsibility review, not artificial
compression/splitting. Existing protocol/SID tests must remain green.

Conditional grant-ticket30n4-protected-peer-20261020 revision01, parent sameuncapped
batch. H2-A only (constructors/SID factor/constructor tests), H2-B NOT_ACTIVE until
Root ordinary new-model constructor roundtrip/strict and independent source
preflight at immutable A. Then Root derives revision02 for SAME three paths and
remaining join tests; no Owner renewal or scope reset. Strong-type sequencing
inside existing implementation stage, not a new workflow/Gate or self-blocking
requirement for actual Host qualification before source construction.
Named standard offered Luna/xhigh implementation owner /root/ticket30n4_peer_impl,
Root sole reviewer/orchestrator, distinct /root/ticket30_native_tools_review
source peer after current C6/CVQ view closes. New ctx-ticket30n4-protected-peer-
20261020; same-lifetime direct lane, receipt/Runner NOT_REQUIRED.
Preregister own repository-contained .worktrees/skill-improvement-30g-windows-peer
and matching -review, branches codex/same names; owned Temp/johnny30n4-peer-owner-
20261020 and -review-20261020. TTL through review/seal, exact teardown, holds take
precedence; no cleanup or auto expiry, no denied-operation retry.
Root after DOC_PASS reads exact baseline/clean Git/nonreparse roots and existing
public DTO preflight before source allocation. All new-model A constructors tested
and reviewed before B behavior. Offline only, per-command60/child55 default,
record resource usage/diagnose changed bounds, no cumulative/attempt reset.
ACTION_REQUIRED source implementation only AFTER exact activation record;
currently DOCUMENT_REVIEW_PENDING, not an operational trusted Grant.


## 30N4-H1 — E01/E02 bounded correction / same closure13

Initial immutable dee1977a17ec0e325d2f7ccc1b3325d47da23286 stays preserved;
same H1 two paths only MODIFY, CREATE/DELETE0, baseline additive dee1977.
Original grant-ticket30n4-bounded-pipe-io-20261020 revision02 conditional on
independent DOC consistency and fresh owner Git/containment; same owner/context/
WT/parent uncapped batch. Initial32transport+2codec green/strict/import/three
actual mutants are retained, not adequate for final pass. No requirement change,
new API/framework/file or Host action. Root /different source peer agree:

E01 actual CreateEvent result is an owning PyHANDLE, while installed stub says
int and fake returns int. Root77f2d8 lawful wrapper-shaped constructor counter
refuses EVENT_CREATE_FAILED, no real native call. Use installed runtime exported
pywintypes.HANDLEType (confirmed import/type inventory only c024c1 and stub
pywintypes.pyi23), retain correct owner and separately validate its numeric
handle for int-typed APIs. Close via owning wrapper exactly once, no int-only
conversion that drops owner/double-closes; alternatively only an explicitly
proven Detach transfer, no cast/Any/stub edit/ctypes/new protocol framework.
Tests patch HANDLEType/CreateEvent with a typed owning fake BEFORE construction,
track owner lifetime/Close order, invalid numeric handle and exception paths;
lawful wrapper positive must pass, invalid result rejects finitely. No real
handle/resource creation even to discover its type.
Existing PRIVATE pipe_handle/cancellation_event interface remains numeric as
selected in H1: later protected factory must explicitly transfer pipe ownership
and retain borrowed stop-event owner through IO/hold. A PyHANDLE passed directly
instead of an admitted raw integer is not newly supported by this correction.
Do not silently change constructor input contract to suppress source finding.

E02 Root245812 malformed primary GetOverlappedResult True returns INVALID with
FAILED state and clears live OVERLAPPED/buffer. Independent source confirms this
does not establish terminal completion. Primary malformed/non-int/negative
completion must enter existing RECOVERY_HELD with all original live references,
no more IO/no close/no immediate retry; same behavior already covers malformed
drain. Add exact read and write/cancel relevant fake completion cells, assert
nonempty active resources and absence of owner/pipe close, plus lawful completion
still succeeds. Recovery hold is in-process owned resource state only, not
fabricated durable evidence or release of existing project Recovery.
Actual guard relaxation for both E01 ownership and E02 retention must yield
named RED and exactrestore GREEN; Root different completion/count door retained.

Run same focused34+new regression cells, strict affected4files, memory compile/
import with every OS-facing call patched before constructor, no real pipe/event/
token/service/ACL/Host test. Forecast overage triggers independent structural
review (one IO lifetime owner/one cohesive fake matrix), not artificial split.
Do not amend/reset already returned candidate; each correction ADDITIVE commit.

Author reported sibling Temp/johnny30n4-pipe-owner-20261020-evidence.zip,
SHA12d445bf4c4540e179ad8cfD6a77873379738a0e5e905116621dc7a1b5a219b3
(case-insensitive hex), outside preregistered owned output root. Preserve that
exact residue; original in-root raw logs remain primary evidence. No deletion/
move/rewrite, no automatic cleanup authority inferred from author report, no
retry of old policy-denied cleanup. Subsequent outputs ONLY inside registered
owner Temp root. Track ownership/teardown uncertainty independently of functional
review; no false resource lifecycle closure.


## 30N4-H1 — bounded Windows pipe IO / closure13

C6 final1fe5c8342ff7127ac7d19721a423fa42a6832711 independently SOURCE_STAGED_PASS:
E01 output-failure evidence closed, accepted MATCH and distinct Root actual
Verify/bound/parse/output red-to-green proofs sealed in original review. C6
allocation CLOSED_INTO_QUALIFIED_REVIEW_HOLD; source/outputs/refs retained.
H1 remains the only live source implementation cut below; no actual Host, main
integration, operational authority or full Ticket30/01/02 acceptance implied.

Original30/PRD009/CHG009/runbook02 shared protected Windows authority service,
same uncapped local batch and first-entry engineering staging only. Select the
next reusable native IO responsibility, NOT the entire service in one module.
Installed0.4.14 workflow catalog has only workflow-router-poc, no delivered Windows
authority card; do not invent/adopt a near-match. Reuse target-owned reviewed
N4-A1 codec5449c0634866b3334e3963c87b8603eb973e39bd and existing wire limit/
ledger/client without copying or changing them. Separate trust/enrollment/service
composition remains later; no all-refuse fake WindowsAuthorityChannel placeholder.
This cut implements real Windows IO calls in source, tests ONLY patched calls.

Exact sourcebaseline5449c0634866b3334e3963c87b8603eb973e39bd. CREATE2:
library/local_orchestration/grant_authority/windows_transport.py,
tests/test_grant_authority_windows_transport.py. MODIFY0/DELETE0. No package-root
export, contracts/codec/ledger/nativeC#/Router/profile/runtime/dependency changes.
Private cohesive message-pipe IO helper only; not a new public authority port,
DTO/catalog, WindowsAuthorityChannel, SCM host, enrollment resolver or framework.
Existing bytes/int/bool/finite exception values and installed pywin32 types suffice.
Private resource owner retains OVERLAPPED/event/buffer/pipe handles for exact
lifetime; no Any/cast/ignore/dynamic member lookup or caller trusted flag.

H1-IO: own one explicitly provided valid noninheritable pipe handle, issuing thread
identity, cancellation event and absolute finite request deadline. Connect/read/
write use existing installed overlapped pywin32 APIs, one operation at a time on
that same issuing thread; no thread/process/worker spawning, blocking INFINITE,
poll loop, second request, subprocess or generic file IO. Private caller must later
obtain handle from protected pipe factory; numeric handle is resource identity,
NOT role/authentication or operational permission. Helper must reject wrong-thread,
closed/failed/recovery-held state before another operation. No real API call during
tests or constructor preflight; source import must not create event/pipe/service.

H1-FRAME: one complete message into quarantined bytes, before any decoder/ledger
or authorization claim. Reuse existing16384 body+4header envelope size; bounded
read allocation is maximum frame+1 (16389), reject zero/overflow/ERROR_MORE_DATA,
malformed native result/count/error, partial-message completion/disconnect. Never
stitch/read again or decode/normalize content here; existing codec is sole framing
and JSON validator in later composition. Write exactly one already bounded bytes
frame, check actual completion count equals length, never partial write/retry.
Validate external native values at boundary then keep named/finite typed state.
pywin32 stub read-buffer is incomplete: primary upstream source documents standard
buffer/memoryview. Runtime narrow to actual supported memoryview before accessing
bytes; do not use unchecked object conversion or relax checker to hide API mismatch.

H1-CANCEL: default request duration <=10s, explicit stop event, finite native event
wait using remaining deadline; no busy polling/sleep. CancelIo is issued only on
the same thread that issued IO. On timeout/stop/failure with pending operation,
cancel then independently observe terminal GetOverlappedResult before buffer/
OVERLAPPED/event/pipe close. ERROR_OPERATION_ABORTED is terminal failure, never
success. ERROR_IO_INCOMPLETE or unconfirmed cancellation after finite1s drain
becomes recovery-held failure: retain all live native references and original
pipe ownership, forbid further IO, never drop/free/close still-pending memory.
One held operation maximum; no accumulating background registry or silent retries.
Keep this an in-process resource hold, not fabricated durable RECOVERY evidence
or automatic clearing of existing project RECOVERY_REQUIRED. Cleanup release
only follows confirmed terminal state; no __del__ destructive fallback.

H1-TEST: one cohesive typed fake call recorder at actual pywin32 module call seam,
patched BEFORE helper construction. No real CreateNamedPipe/CreateFile/Connect/
ReadFile/WriteFile/token/ACL/SCM/process calls, sleeps/stress or external models.
Positive connect/read/write record actual order, one native read/write, exact bytes/
count and finite waits; existing valid wire encode/decode confirms lawful data
remains intact, not an all-refuse test. Negative null/bool/invalid handle/time/
oversize/zero/MORE_DATA/native exception/wrong count/partial write/wrong thread/
stop/deadline/pending cancel/incomplete drain prove no second read/write and no
premature close; error messages finite, no raw frame or native exception payload.
Registered test fake buffers use ordinary memoryview, not fake Host observations.
Actual product weaken bound =>namedRED, same-thread check =>namedRED, terminal-
before-close/retention guard =>namedRED, exactrestoreGREEN. Root independently
mutates a different IO completion/count/error door. Source effects remain dormant.

Reuse installed Python3.11.9/pywin32311/types-pywin32/Pydantic/mypy2.3.0/pytest9.0.3;
no dependency/install/stub edits. Strict both new files+existing codec contracts,
memory compile/import, exact explicit focused pytest nodes, diff/source checks.
Forecast product~260/test~320lines,0docs/screenshots/deps; inspect structure if
growth exceeds forecast or500effective lines, no compression/arbitrary splitting.
No standalone test runner, mock server, duplicated codec or unmanaged outputs.

Conditional grant-ticket30n4-bounded-pipe-io-20261020, parent original uncapped
batch, closure13, CREATE2 exactly. Implementation owner /root/grant_transport_impl,
standard offered gpt-6-luna/xhigh; Root sole reviewer/orchestrator, distinct
/root/ticket30_native_tools_review source peer after C6 allocation closes.
New ctx-ticket30n4-bounded-pipe-io-20261020; repo-contained WT
.worktrees/skill-improvement-30g-windows-transport and matching -review,
branches codex/skill-improvement-30g-windows-transport and matching -review.
Pre-register both WTs and owned Temp/johnny30n4-pipe-owner-20261020 and -review-
20261020 HERE before creation; owners author/Root, TTL through review+seal,
Review/Recovery holds and precise teardown required, no automatic removal or
denied cleanup retry. Same-lifetime direct lane/receipt/Runner NOT_REQUIRED.
After independent DOC PASS, Root validates exactclean5449/Git/containment/roles
and existing codec/typed boundary constructors, then activates this source cut.
Private new helper construction is implementation output, no new public-contract
preflight cycle or fake protected pipe. Percommand60/child55 initial, monitor/
diagnose failures and preserve old accounting; no cumulative/fixed-count caps.
No actual pipe/token/SCM/account/ACL/network/Host/installation/native attack/
trusted issuer/protected enrollment/model/push/release/deploy/formal gate effect.
Return immutable candidate/files/full raw checks/mutations/deviations; Root waits,
reviews/corrects same ticket and stages only source engineering when proven.

## 30N3 — C6 E01 output-failure evidence correction / same closure12

Root immutable candidate1e5ce16cc9a6be2cd95ab0cd30a7312223a94405 original six paths
strict/default/enrollment green25c4ea, distinct source peer SOURCE_PASS, product
91/newtest274/helper17lines cohesive. Root different serialization reason door
named REDd38fe0/exactrestorea77cf5GREEN. Separate actual product output-write
failure catch return2->0 leaves alltestsGREENc79d79; exactrestore10adceGREEN.
Distinct source peer confirms missing non-null failing output stream cell in
existing C6-RESULT/exception truth contract. E01 EVIDENCE_DEFECT, not product bug,
new requirement, additional output policy or need to change functioning product.

Same grant-ticket30n3-enrollment-command-20261019 revision02 /closure12 /parent
uncapped batch; exact correctionbaseline1e5ce16cc9a6be2cd95ab0cd30a7312223a94405,
same author/WT/branch/context, Root/distinct peer. CREATE0/DELETE0; MODIFY only
library/local_orchestration/native_windows/NativeEnrollmentCommandSelfTests.cs.
Reuse existing normal matching fixture and add typed non-null faulting output
Stream. Through actual Program.Run valid parse/readback/Verify then Write failure
must return2, fixed enrollment_output_failed stderr, no raw sentinel, one callback;
assert output state actually reached, not null-output early rejection. Keep
legal normal MATCH positive. No separate test framework/product/API change.
Actual output catch2->0 =>new namedRED; exact productrestore/rebuildGREEN.
No false defective-baseline-red claim for the presently correct product; original
ZERO_RED and author newline-only assertion correction stay in history.
Other original source predicate proofs carry forward unchanged. Direct offline
strict rebuild/default/enrollment only, no legacy Python physical fixture or
native/job/Host execution. Existing registered Temp/TTL/teardown holds preserved.
Distinct DOC consistency then fresh clean1e5/source/Git/leaf/index readback activates
this bounded correction without Owner renewal. No qualification/formal integration.

## 30N3 — C6 enrollment command composition / closure12

Original PRD009/CHG009, batch-checklist-local-20261019-uncapped and existing
runbook02 native enrollment-tool responsibility only. No new PRD/authority/Host
surface. C5 final181d0daebc9ba64c8968231561708522bb590673 engineering sealfe51585a
closes E01; B2 exactbf5a4a3c82131c308ffa85b2d899d4afd1cf32d9 seal3c87ef77.
Root controlled engineering staging2831948c admitted only their conflict-free
composition in own review WT; actual merge51dc502f61b8dab31926e01b9c888e8b75d92ca3.
Root8805a5 offline forced strict build/default/enrollment selectors PASS;
710f3c proves all3B2 blobs and C5 reader/test/project/Program exact to their
reviewed sources. This merge is only source-engineering candidate construction
under first-CVQ order exception, not qualified integration, main or authority.

TEST-before-A: current public Program.Run covers plan/inspect but has no enrollment
command; approved B1 parser, C5 reader and B2 verifier have independent source
proofs. C6 joins those already accepted seams, no responsibility transfer/retirement.
No new DTO/port: internal command consumes Stream/Stream/TextWriter and injected
Func<NativeEnrollment,NativeEnrollmentReadback>; existing typed result retains
SOURCE_ONLY_UNQUALIFIED. A internal transport owns bounded parse/serialization;
Program remains composition root, existing reader/verifier remain behavior owners.
Later protected-service/B caller may use this candidate only after its own source/
Host admissions; no automatic activation follows.

C6-COMMAND: add exactly one CLI selector verify-enrollment, routing Program.Run to
cohesive internal EnrollmentCommand. Ordinary production composition lazily invokes
new WindowsEnrollmentReadback().Read only AFTER a valid NativeEnrollment has been
parsed. Preserve existing Program.Run five-argument callers with ordinary overload
or optional typed readback callback; no static reader effect, dynamic command,
shell, stdin-supplied observer, generic executor or test-only environment selector.
Do not move ledger/IPC/installer policy into this command.

C6-INPUT: reuse Program's bounded UTF8 stream reader, exposing its existing helper
internally with an explicit positive maximum parameter; original plan/inspect
retain32768-byte bound, enrollment uses existing131072-byte parser bound. One
maximum+1 bounded allocation/read, strict UTF8 and existing ordinary ParseBounded,
no truncation/coercion; no reader callback for invalid arguments, empty/overbound/
malformed/invalid UTF8/duplicate/unknown/stale enrollment. IO failure produces a
fixed finite error, never raw exception/input/path disclosure. No root/rights/
payload/namespace/parser relaxation; null input/streams/callback fail finite.

C6-RESULT: call injected actual readback once with parsed enrollment; B2 Verify
compares its result, never reconstruct observation from Expected or infer match
from OBSERVED alone. MATCH/NONE =>exit0; all ordinary REFUSED reasons or readback
exception/null =>exit2; invalid input/args =>exit64. Serialize only exact JSON
scope/status/reason enum names plus newline, no raw source/path/exception or fake
Host evidence. Invalid input writes no positive JSON, fixed stderr token. Existing
plan/inspect/default/enrollment behavior and selector exit contracts unchanged.
This command is a source tool, NOT a trusted issuer, protected approval or permission.

C6-TEST: reuse original valid enrollment fixture by passing it from existing
RunContracts; reuse B2 matching-readback/nested fixture via a narrow internal
test helper wrapper, not duplicated builders/security policies. Cohesive new
command selftest tests through actual Program.Run: valid independently expected
MATCH/0/three-key JSON; payload hash/size mismatch and unavailable readback =>2;
exception/null =>2; malformed/duplicate/unknown/invalid UTF8/max+1/exact permitted
UTF8 length input and wrong args =>64 with zero callback, never silent truncation.
Whitespace-boundary input may use ordinary valid JSON padding, not invented
payload schema. Assert exact callback count/binding and absence of raw sentinel
error text. No physical fixture, network, service or actual protected read.

C6-TRUTH: actual product weaken bypass B2 Verify =>named mismatch RED, restore
GREEN; call readback before parse =>invalid-input no-callback RED, restore GREEN;
weaken input bound =>named boundary RED/restoredGREEN. Reviewer uses a different
real product door (e.g. result/exit serialization or readback binding), reads
unreduced output and exact source/binary restoration. Missing negative power is
a finding, no all-refuse success. Existing B2/C5 named proofs carry forward by
unchanged blob, not broad unrelated04/native-job tests. Strict offline forced
compile/default/enrollment selectors; no old Python build fixture/symlink/nativejob.

Exact CREATE2 under library/local_orchestration/native_windows:
EnrollmentCommand.cs (bounded enrollment transport only),
NativeEnrollmentCommandSelfTests.cs (command boundary only).
Exact MODIFY4 same directory: Program.cs (selector/lazy composition/shared bounded
reader), JohnnyAuthority.Tools.csproj (explicit2includes),
NativeEnrollmentSelfTests.cs (one RunContracts call with existing enrollment),
NativeEnrollmentVerificationSelfTests.cs (only reuse wrapper/visibility for existing
matching fixture, no predicate/assertion weakening). DELETE0; other product/
parser/verifier/protection/native/Win32/Python/Host/config/test paths read-only.
Forecast product~130/test~210/helper~15lines;0screenshots/deps. Threshold signals
structure review, not minification/forced split or permission to create extra files.

Conditional grant-ticket30n3-enrollment-command-20261019, closure12,
parent uncapped batch, exact sourcebaseline51dc502f61b8dab31926e01b9c888e8b75d92ca3.
Root sole reviewer/orchestrator; /root/ticket30n2_native_impl standard offered
Luna/xhigh implementation owner, different /root/ticket30_native_tools_review
source-evidence peer. Previous C5 allocation CLOSED_INTO_HOLD, no cross-ticket
memory/role/authority claim. New ctx-ticket30n3-enrollment-command-20261019,
repo-contained .worktrees/skill-improvement-30n3-enrollment-command /
codex/skill-improvement-30n3-enrollment-command, matching -review Root WT.
Both WTs plus owned Temp/johnny30n3-enrollment-command-owner-20261019 and -review-
20261019 are pre-registered HERE before creation; owner respectively author/Root,
TTL until Review+evidence seal, Review/Recovery holds prevent automatic removal,
teardown only under precise authorized cleanup after holds release; no denied
cleanup retry. This is same-lifetime direct lane, receipt/Runner NOT_REQUIRED.

After independent DOC consistency, Root validates clean composite/contained Git/
branch/role, existing normal enrollment/readback/result constructors via exact
baseline selectors, then activates this exact six-path source Grant. No requirement
that new internal static command already exist; public typed inputs/outputs exist.
Existing offline .NET10.0.302/cleared NuGet sources/strict warnings-as-errors; use
registered obj/bin/cli/cache, no install/download/compiler server. Default60s/
child55s, finite resource/lifecycle monitoring, no cumulative/count cap/reset.
No SCM/ACL/account/pipe/network/native fixture/Host/model/spawn/receipt/remote/
cleanup/install/push/release/deploy/formal gate effect or qualification. Report
exact candidate/path/check/mutation/raw evidence/deviations, then Root review,
same-ticket correction and controlled engineering staging if all actual cells pass.

## 30N3 — C5 E01 actual-observation preservation / same closure11, Grant revision03

Root review exact38417fe9edfb6b39527fe58e614e8d5087bab517: all current tests green,
but actual final typed observation rewritten to expected.Configuration.Sha256/
SizeBytes remains GREEN under forced compiled mutation9d0758. ZERO_RED is
EVIDENCE_DEFECT C5-E01, not product failure/new B2 verification requirement.
Current product already returns actual configuration unchanged. Existing fake
positive derives Actual from Expected, so that frozen preservation property is
not discriminating. Raw initial/mutation/exactrestore in original30review.
Other named route/descriptor/configpath/configvolume/postvolume/deadline doors
red/restoredgreen; final product exact28d3049db600e8f6c86db8b1c0de2481f6f30014,
Root strict rebuild/default/enrollment green, own review WT clean.

Same grant-ticket30n3-enrollment-composition-20261019 revision03, same source owner/
WT/branch/context, new correction baseline full38417 SHA above. CREATE0/DELETE0,
MODIFY ONLY existing NativeEnrollmentReadbackCompositionSelfTests.cs in native_windows.
No product/DTO/parser/B2/Program/Python/fixture or behavior change. Add two ordinary
valid file observations: exact path/FILE/metadata and same volume, but (1) observed
digest different from expected with same size; (2) observed size different with
same digest. Both must return OBSERVED, exact actual literal hash/size unchanged,
no new comparison/rejection, no fake claim of B2 MATCH. Independently fixed literal
Expected, not copied from returned result or private helper. Reuse existing local
ReadWith/ObservedFile and cohesive test group; no new helper framework/newfile.

Actual temporary production copy of only expected hash must turn named first
cell RED, exactrestoregreen; copy of only expected size must turn second cell RED,
exactrestoregreen. No false baseline-red claim against correct original product:
this is test-evidence correction. Existing actual behavior/closure negatives and
legitimate direct/nested positives remain. Same direct offline forced build +
default/enrollment selectors from verification erratum revision02; no legacy coupled
fixture, broad pytest, native job, Host effect or denied cleanup retry. Preserve
initial21owner records/draft distinction/Root ZERO_RED. Independent DOC consistency
then fresh exact clean38417/roles/Git/leaf/index binds correction before work.
Uncapped parent/history/holds, Root sole reviewer and distinct source peer unchanged.

## 30N3 — C5 exact enrollment readback composition / closure11

Root bounded architecture review identifies next native dependency: compose the
already sealed C4 CodeRoot inventory with ONLY the declared DataRoot configuration
chain. DataRoot includes service-mutable ledger/evidence/recovery assets, therefore
C4 recursive enumeration MUST NOT receive DataRoot. Existing frozen B2 DataRoot
semantics require root/config/intermediate directories only; no new requirement.

Source engineering baseline8a24b9eb0a1899512319fe9b0f9a4b23b8816203 contains existing
NativeEnrollment, NativeEnrollmentReadback, NativeEnrollmentInventoryObservation,
NativeObjectObservation and C4/payload/directory readers. B2 verifier candidate
bf5a4a3c82131c308ffa85b2d899d4afd1cf32d9 is a separate held lineage, not integrated.
Root chooses NO prerequisite merge: this slice only returns the existing readback
value, never calls Verify or claims MATCH. Literal normal readback/call-roster
positives prove this composition; B2 source composition and executable verify mode
remain later bounded steps. Avoid a dependency cycle/new DTO/placeholder service.

Exact public sealed WindowsEnrollmentReadback: parameterless constructor binds
existing WindowsCodeInventoryReadback.ReadCodeRoot, WindowsReadback's internal
ReadDirectoryMetadata and WindowsPayloadReadback.ReadFile; public
Read(NativeEnrollment expected)->NativeEnrollmentReadback. Internal constructor
accepts exactly these three existing typed Func delegates for deterministic pure
fault-injection/call-roster tests, no new ports/results/DTOs or public path list.
Default constructor itself performs no I/O. Null arguments reject before callbacks.

C5-ROSTER: derive CodeRoot, DataRoot, all configuration parent paths and exact single
configuration file solely from the normally validated enrollment. Read CodeRoot
exactly once through C4, never DataRoot through that delegate. Require OBSERVED and
exact CodeRoot identity; otherwise refuse before DataRoot read. Directory sequence
DataRoot to immediate config parent, config once through payload reader, directory
sequence in reverse. Existing metadata reader checks directory kind and exact
native path internally; its DTO has no path/kind field, so do not invent an
extra claimed path identity check or fake field. Internal injected callbacks prove
ordering/bindings only, not actual OS authenticity. File DTO path/kind is explicit:
require exact configured path/FILE/OBSERVED and same DataRoot volume. All directories
must be OBSERVED with same DataRoot volume and each before/after volume/FileID/
owner/descriptor digest equal. No mutable DB/evidence child enumeration or ledger
open. Return first stable directory observations plus one config in existing
NativeEnrollmentReadback. Do not compare file digest to Expected here: B2 owns
payload/protection verification; no duplicate authorization/comparison engine.

C5-FAILURE: missing/denied/reparse/unavailable, null callback return/exception,
wrong code root/config path/kind, cross-volume or directory drift produce an
existing failed readback: CodeInventory non-OBSERVED/EMPTY at expected CodeRoot,
DataObjects exactly one failed DIRECTORY at expected DataRoot, no partial success/
invented observation. Normalize unknown/OBSERVED failure to UNAVAILABLE. Preserve
finite native failure where applicable; mismatch uses REPARSE_OR_IDENTITY_MISMATCH.
No new failure vocabulary, private catch-all success, unsafe DTO constructor.
C5-BOUNDS: before any callback validate every derived path <=32766characters and
data path count <=existing MaximumDataObjects4096 (config included). Cooperative
ten-second composition deadline checked before/after each callback and loop,
not an atomic filesystem snapshot or hard preemptive Host limit. Existing readers'
finite I/O bounds remain. Small internal optional clock Func<long> default-null
MAY be added only to existing internal test constructor to deterministically prove
deadline with Stopwatch timestamps; no public policy/port/timeout extension.

C5-TEST: source-only injected ordinary-constructor fixture (ProgramFiles/DataRoot
path contracts remain strict, do not spoof environment/modify protected folders).
Literal root/direct and nested config positive paths/metadata/hashes/size retain
exact values; independent expected roster; unrelated mutable ledger path must
never be requested. Null input/delegates and bound overflow =>zero callback;
failed CodeRoot =>zero data callbacks; each directory/file status, config wrong
path/kind/volume, directory pre/post identity/owner/SDDL/volume drift and callback
exception/null =>failed EMPTY/no partial. Independent one-field valid negative
fixtures, not overlapping invalids. Native default reader components' already
sealed real-boundary proofs carry forward unchanged; no installed/protected actual
positive claimed from fake composition. New behavior has no artificial stub-red.

C5-MUTATION: actual route C4 to DataRoot =>roster cell RED; remove pre/post FileID/
descriptor/volume checks separately =>corresponding named RED; remove config exact
path or cross-volume guard =>named RED; shorten bound checks =>boundary cell RED.
Exact restore/rebuild green each, Root chooses a different production door, zero
red becomes finding not pass. Strict compiler/warnings-as-errors, default selftest
plus actual enrollment-contract-self-test and memory/Python fixture compile only
if touched (none planned). No source-copy oracle or compressed script framework.

Exact CREATE2: library/local_orchestration/native_windows/WindowsEnrollmentReadback.cs,
library/local_orchestration/native_windows/NativeEnrollmentReadbackCompositionSelfTests.cs.
MODIFY2: library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj
(explicit compile includes only) and NativeEnrollmentSelfTests.cs (one normal call
inside RunContracts with existing valid enrollment). DELETE0. All other source/
tests/Program/Win32/parser/verifier/ledger/Router/Python/reference paths read-only.
Forecast product~160 and cohesive tests~240lines, docs this section/index/review,
screenshots0. Reuse existing DTO/readers/selftest fixture, >500effective structural
review only, no forced split/minification/extra files or ticket/prompt narrative.

Conditional grant-ticket30n3-enrollment-composition-20261019 under original uncapped
batch/PRD009/CHG009/approved runbook2, baseline exact8a24 above. Root sole reviewer/
orchestrator; /root/ticket30n2_native_impl author only AFTER N4-A1 source review and
engineering allocation release, distinct existing source peer
/root/ticket30_native_tools_review. New context ctx-ticket30n3-enrollment-composition.
New repo-contained .worktrees/skill-improvement-30n3-enrollment-composition /
codex/skill-improvement-30n3-enrollment-composition and separate matching -review WT.
Preregister owned Temp johnny30n3-enrollment-composition-owner-20261019 and -review-
20261019 for raw/cache/build. Owner/TTL through exact review+seal and all holds,
normal cleanup gate only, no cleanup-denial retry. Independent exact DOC consistency,
normal existing constructors plus clean source/roles/non-reparse/Git metadata/index
readback precede activation; this is local construction, not Host qualification
before its first build. No extra Owner renewal or perpetual allocation.

.NET10.0.302 existing offline source-cleared NuGet.Config/no new deps; exact installed
Python311 for bounded verification orchestration only. Verification binding erratum
revision02: Root Git77ce25 proves held F1 shared builder7fa12f0c is NOT an ancestor
of8a24. Do not invoke old _create_native_fixture/native_fixture: it couples build
to physical files and an os.symlink attempt outside this pure composition test.
Reuse the existing direct dotnet restore/build interface, not a new persisted build
script or copied fixture framework: project cwd native_windows, registered Temp
obj/bin through BaseIntermediateOutputPath/BaseOutputPath, RestoreConfigFile=NuGet.Config,
--disable-build-servers/-m:1/-nodeReuse:false/-p:UseSharedCompilation=false;
build --no-restore --no-incremental. Run only default self-test and enrollment-contract-
self-test (plus named C5 reflection check where needed); no broad pytest/native/job
campaign or selector inherited from another fixture. Same exact4paths/8a baseline/
author/Grant/closure, no public contract or authority change, no Python edits.
No install/account/ACL/service/pipe/network/
Host/model/authority/dispatch effect, verification MATCH claim, protected-source
qualification, formal source integration, push/release/deployment or checklist
completion. Original history/resources/Recovery and 30B/43 holds unchanged.

## 30N4-A1 — reuse Grant frame decoder / closure10

This is the next existing runbook section2 server-transport dependency, not a new
requirement/service/authority engine. Root read immutable30G client/contracts/
protocol tests at20bd6e3036608d61feb687ea6e0ff6b7953d3e11. Existing client owns
bounded response decoder, duplicate/depth/UTF8/JSON checks and request/response
encoders, but has no corresponding public request decoder. Readonly Architecture
inventory confirms no current native pipe/SCM entry or protected runtime manifest;
same-user AuthorityPeer is never OS authentication. No chosen design reopened.

Root chooses the smaller decoder dependency before the proposed five-path fake
service/extra result/port types. Do not create WindowsGrantReadService or four new
public DTO/enums/port merely to name a placeholder. Reuse GrantReadRequest and the
existing frame/parser responsibilities in client.py. No native capability dependency
is needed for pure request decoding; do not manufacture a combined/qualified base.
20bd is immutable ENGINEERING_SOURCE_BASELINE_ONLY, not implementation authority:
authority is this exact batch-derived child Grant and original approved SPEC/lineage.
Original held30G/N3/C4 branches are not merged or promoted by this local construction.

Public decode_read_request(request_frame:bytes)->GrantReadRequest|None, exported
from existing grant_authority/__init__.py. It returns a normally validated existing
two-ID request or None. No dynamic object/raw JSON crosses that boundary and no
Grant/read/peer approval is produced. Reuse/refactor existing _decode_response frame
body checks into one private common bounded decoder; do not copy a second JSON
parser or wire schema. Existing _ReadRequestWire enforces integer revision1 and
exact schema_revision/grant_ref/operation_ref. Existing response/client behavior
and all original protocol tests stay intact; no ledger issue/claim/consume/query,
transport/socket/pipe/SCM/process/environment/config/readback or formal dispatch.

GD01: ordinary constructor + encode/decode positive and independent literal framed
JSON with distinct IDs preserves exact values; reversed JSON key order/whitespace
legal. GD02: exact bytes only, four-byte big-endian length,1..16384 body, exact
total length; empty/short/zero/oversize/truncated/trailing/invalidUTF8 reject. Include
otherwise-valid JSON padded with spaces to exact16384 accepted,16385 rejected so
another schema error cannot mask bounds. GD03: duplicate/unknown/missing keys,
invalidJSON/nonfinite constants/depth>32, bool/float/string revision, badID/control/
noncanonical value reject; no transformations manufacture a valid ID. Unknown
approval/role/peer/path/command fields reject. GD04: all existing response/client
binding/refusal matrix still passes after common-body refactor, source-only scope
unchanged. GD05: actual common total-length/duplicate and request revision/extra
predicates each have named red/exactrestoregreen, Root different door; no test-copy
oracle/unsafe bypass constructor or artificial baseline-red for absent new API.

Exact MODIFY3 only: library/local_orchestration/grant_authority/client.py,
library/local_orchestration/grant_authority/__init__.py,
tests/test_grant_authority_protocol.py. CREATE0/DELETE0, no contracts/ledger/native/
Router/test framework/dependency/other path. Forecast source~35lines net/tests~90,
no screenshots, docs this section/index/review only; signal not compression quota.
Existing protocol test375lines remains cohesive; >500effective lines only triggers
structure/reuse review, not forced split or newfile permission. Temporary raw/cache
under exact registered named seat output, no worktree artifacts.

Conditional grant-ticket30n4-request-decoder-20261019 under original uncapped batch,
baseline full20bd SHA above, same original Ticket30/PRD009/CHG009/runbook scope;
author /root/ticket30n2_native_impl only AFTER C4 correction/review completes and
its allocation released; Root sole reviewer/orchestrator, distinct existing source
peer /root/ticket30_native_tools_review. New context ctx-ticket30n4-request-decoder,
new contained .worktrees/skill-improvement-30g-request-codec /
codex/skill-improvement-30g-request-codec, Root review uses separately registered
.worktrees/skill-improvement-30g-request-codec-review / matching codex branch.
These are isolated source-lineage workspaces, no move/reset/merge of held candidates.
Owner/TTL through exact review+seal and Review/Recovery holds, normal cleanup gate
only, no denied cleanup retry. Register before creation owned Temp roots
johnny30g-request-codec-owner-20261019 and johnny30g-request-codec-review-20261019
for cache/raw/pytest output; not a Temp repository or alternative clone.

Use existing exact devPython3.11.9/Pydantic2.13.4/mypy2.3.0/pytest9.0.3, no install.
Ordinary current contract/codec positive preflight, focused protocol suite and
strict changed source/tests, memory compile/import/diff-check, each actual reverse
predicate and immutable candidate required. Default single-command60s/child55s,
serial per seat, source-only HIGH_ASSURANCE engineering staging under existing
first-entry order exception; no protected-source or Host qualification claim.
Independent exact DOC pass then Root clean20bd/nonreparse/roles/Git/index readback
activates the child, not another Owner renewal. History/UNKNOWN/time retained.
No new public type/bootstrap cycle, service install/IPC/OS rights/Host/model/
network/credential/effect, formal integration, push/release/deployment. Later
native service wiring still requires its exact build/operational admission.

## 30N3 — C4 E01 evidence correction / same closure09, Grant revision02

Immutable03573829d2824fdf6f48cf0cb9bd33846627f746 meets source shape and actual
7path/44byte literal API positive, strict/default tests. Root different immediate-
child predicate mutation named red/restored green. But independent removal of
global child-volume guard and nested SameDirectoryMetadata volume equality both
leave configured/pure tests green. C4-E01 is EVIDENCE_DEFECT for frozen closure09
volume bindings, not product failure/new requirement. Preserve both ZERO_RED runs.
Original review records full commands/results and exact restore aa0a3c5e...

Same grant-ticket30n3-code-inventory-20261019 revision02, source baseline full0357
SHA above, same named owner/WT/branch/context. CREATE0/DELETE0, corrective MODIFY
only library/local_orchestration/native_windows/NativeCodeInventoryReadbackSelfTests.cs.
Product guards and original4path scope unchanged. Add two independently valid B1
constructor scenarios: initial root's immediate FILE on another volume, same path/
FileID/hash/size/kind/owner/SDDL otherwise; nested callback DIRECTORY root on another
volume than earlier parent observation, same FileID/owner/SDDL/hash/path/kind with
normal-volume children. Each separately refuses identity mismatch/EMPTY, and normal
7path/44byte control still passes. Remove only global volume guard -> first cell
red/exactrestoregreen; remove only nested volume equality -> second cell red/
exactrestoregreen. Do not combine FileID/descriptor drift to mask either predicate.
No extra fixture/selector/newfile/helper framework or public contract. Existing
cohesive413line test grows only these bounded cases; no forced split/minification.

Root original review and distinct immutable-source peer apply; different-seat DOC
check this exact binding then fresh clean0357/roles/Git/leaf/index activation before
continuation. Parent uncapped accounting, single-command deadlines, history/holds
and qualification limits unchanged. No Owner renewal/newPRD/Host/install/ACL/
service/network effect or formal integration. Return additive candidate/rawnamed
red and exactrestoredgreen; reviewer independently verifies corresponding cells.

## 30N3 — C4 closed CodeRoot inventory / closure09

C3 final7b2184dff3826eda312515978bdc066e20b366d5 is source-engineering staged
PASS, original review seal5c19eee0; E01/E02 corrected by actual named reds and
exact restores. Not qualified or integrated. Root selects the next existing
enrollment-readback dependency: bounded whole CodeRoot inventory, reusing C3
directory reader and B1 inventory values, not another scanner/PInvoke/DTO engine.
This is still original30N3/PRD/CHG/local batch, no new PRD or authority source.
Full NativeEnrollment/data-configuration chain/verifier/issuer/Host remains later.

Public WindowsCodeInventoryReadback.ReadCodeRoot(AbsoluteWindowsPath root) returns
existing NativeEnrollmentInventoryObservation. Default constructor binds existing
WindowsDirectoryReadback.ReadDirectory; internal constructor accepts exactly one
typed Func<AbsoluteWindowsPath,NativeEnrollmentInventoryObservation> for pure
tests. No new public DTO/port/enum or filesystem API. Public null input rejects
before adapter; default remains actual OS read through sole existing Win32 port.

C4-TREE: iterative bounded queue, never stack recursion; traverse only immediate
directory entries actually returned by C3. Each returned inventory root/path/kind
and immediate-child membership must match requested directory, not an arbitrary
deeper or external descendant. Every nonroot directory's metadata identity,
volume/owner/descriptor/hash must equal its earlier parent observation before
accepting its contents. Reject mismatches/case-alias duplicate paths/cycles,
unknown/failed child or unexpected root; whole failure has EMPTY Objects. Keep
root exactly once while merging each directory scan; root-only empty tree valid.
All objects stay within original root/on its volume, preserving exact paths and
existing immutable typed file hash/size/metadata. No fabricated missing children.

C4-BOUNDS: at most4096 final unique objects including root, aggregate file bytes
at most64MiB across the WHOLE tree (not reset per directory). Monotonic cooperative
10s before/after each directory call and queue iteration, no unsupported atomic
snapshot/uninterruptible-IO claim. Native child read retains C3 bound and external
test-process deadline remains. Enumeration/change races are not qualification:
this source slice cannot prove immutable OS-protected tree or turn current user
permissions into authority. Failure status uses existing finite values, no success
prefix. No DataRoot scan, remote/git, service, ACL, write/delete/install/network.

C4-TEST: same B1 normal DTO constructors and shared reader, no bypass constructors
or second build/fixture helper. Pure empty/nested positives, failed late child,
wrong parent/root/foreign path, changed directory identity/security, duplicate path,
separate aggregate/object exact-limit and over-limit, callback exception, null-before
call. Independently authored literal Expected paths/hashes/sizes/counts; mutate
actual recursive queue admission and global-budget/identity guard, each named red
then exactrestoregreen. Reviewer uses a different actual door, not test-copy logic.
Actual positive uses only PRE-REGISTERED owned root below existing seat Temp output,
code-inventory-fixture: alpha.bin exact UTF8 directory payload plus newline(18bytes),
sub/module.bin and sub/deep/last.bin exact page payload plus newline(13bytes each),
and empty directory. Expected7objects (root,alpha,sub,module,deep,last,empty),
44filebytes; literal payload digests reuse C3 proven values.
This explicit7path set, not an inferred traversal count, is Expected. Root creates
each seat's fixture after DOC admission with apply_patch/files and exact directory
creation only; no user file/write, reparse/ACL fixture or arbitrary Temp repository.
Native test selector JOHNNY_CODE_INVENTORY_TEST_ROOT supplies only this exact root;
missing means skip actual IO, invalid/overlong input fails finitely. Reuse C3's
bounded selector method pattern, not its different131object fixture or selector.

Exact CREATE2 under library/local_orchestration/native_windows:
WindowsCodeInventoryReadback.cs (composition/closure/bounds only),
NativeCodeInventoryReadbackSelfTests.cs (pure/explicit-owned native cases only).
MODIFY2 JohnnyAuthority.Tools.csproj (compile list) and SelfTests.cs (one call only).
No other path, original C3/PInvoke/WindowsReadback/NativeEnrollment*/Program/Python/
N2/B2 branch remains untouched. Forecast product~160/test~240lines is cohesion
signal, not compression/forced split; no new dependency/framework/second runner.
Reuse exact current offline compiler/test commands and registered output roots.

Conditional development Grant grant-ticket30n3-code-inventory-20261019, closure09,
parent batch-checklist-local-20261019-uncapped. Baseline full7b SHA above; author
/root/ticket30n2_native_impl, Root sole orchestrator/reviewer, source evidence peer
/root/ticket30_native_tools_review; same .worktrees/skill-improvement-30n3-native-seam
and codex/skill-improvement-30n3-native-seam, new context ctx-ticket30n3-code-inventory.
C3 allocation closes only as engineering-staged; review/Recovery holds retained.
One implementation-standard offered Luna/xhigh, HIGH_ASSURANCE engineering staging
under already approved first-CVQ method-order exception, not qualified review.
Same-lifetime direct lane receipt/runner NOT_REQUIRED. Independent DOC check and
Root fresh clean7b/roles/nonreparse/Git/leaf/index binding before ACTIVE dispatch.
Output/fixture owner named seat, TTL through review+seal; holds override expiry,
cleanup only existing exact admission, no denied cleanup retry. History uncapped,
single commands60s/compiler/test children55s initially, finite resource monitoring.
Return additive candidate/files/checks/mutations/findings/deviations; no qualified
Host/authority or formal integration claim. Scope/cost/rights unchanged.

## 30N3 — C3 E01/E02 correction / same closure08, Grant revision02

Root actual counter-review of2f6b3fd5584014c5c80c631dbca2204737b27e4c:
native later-enumeration-error partial-success and removal of child-volume/size
comparisons produced ZERO RED. Preserve raw initial review in original30 review,
not PASS or a new feature. Existing legitimate131object/byte positives, actual
PAGE0-completeness red and moved-converter/N1 red/restored green remain evidence.
E01/E02 are missing discriminating evidence for already frozen closure08, not
permission to alter Expected or expand source effects. Same owner/WT/branch/context,
parent uncapped history/cost/security/source/Host limits unchanged, no extra files.

Chosen E01 negative seam: internal optional Func<int,NativeReadFailure?> page-failure
test hook on sole Win32ReadbackPort, default null. For configured native test ONLY,
page0 executes REAL GetFileInformationByHandleEx and parses its real records; page1
returns NativeReadFailure.Denied. This becomes success=false/error5 and MUST flow
through the SAME existing actual other-error MapError/empty/false branch, not a
separate early failure shortcut. Other injected non-null enum values fail closed;
no injected success, fabricated listing or authority. Root/child real metadata,
PInvoke ownership and default native behavior unchanged. No fourth public port,
new selector/public DTO/error/status, arbitrary environment dispatch or framework.
Existing selector JOHNNY_DIRECTORY_READBACK_TEST_ROOT uses the same registered
ordinary fixture. Explicit configured negative asserts READ_DENIED/Objects empty
after actual first page and proves hook was reached. Label failure INJECTED after
real page, not OS ACL-denial or Host qualification. Default self-test remains pure.
Changing shared other-error branch to partial success must name red; restore green.

E02 add pure independently constructed valid child data: wrong volume with SAME
fileID/size/path/hash/kind, and observed size different from enumerated size with
SAME volume/fileID/path/hash/kind. Actual public facade must independently reject
each with identity-mismatch and empty Objects. Both normal positive cases continue.
Remove only volume guard -> volume cell red/restore; only size guard -> size cell
red/restore. Do not let another unrelated mismatch mask the target predicate.

Same grant-ticket30n3-directory-readback-20261019 revision02, baseline2f6b3fd5 full
SHA above; CREATE0/DELETE0 and corrective MODIFY only Win32ReadbackPort.cs,
Win32DirectoryReadback.cs, NativeDirectoryReadbackSelfTests.cs under the existing
native_windows directory. Public WindowsDirectoryReadback product guards stay
unchanged; tests touch them only in temporary bounded author/reviewer mutations
in each seat's OWN WT with exact restoration, never commit weakened guards.
No new fixture, dependency or input; original seven-path total scope still closes.
Root independently DOC-reviews this exact binding via different seat then reads
clean2f/role/Git/leaf/index before continuation. No Owner renewal, new PRD, reset,
additional qualification bypass or actual ACL/service/install/model/network effect.
Focused negatives/actual/native/default/strict + Root counter-doors, raw results and
exact restoration required. If new selftest growth crosses500effective lines, review
cohesion/reuse, no compressed code/forced split/unrelated framework or newfile.

## 30N3 — C3 bounded directory readback / closure08

Architecture Owner selects the existing next native dependency, not another
Wayfinder, PRD, gate or broad framework. C2 exactb42ae444f6b6e873fb0a40ae0b3667be51bdf468
and Root sealc5d98249 prove source file readback only; F1/B2 branches remain held,
not silently imported. The original Ticket30/PRD/CHG/uncapped batch/first-CVQ order
exception applies. Completed C2 allocation released; same owner/WT may take this
next isolated view only after exact source admission. No qualified integration.

Smallest independently observable result: one explicit directory and its immediate
entries, not a recursive CodeRoot inventory or full NativeEnrollment verifier.
Public WindowsDirectoryReadback.ReadDirectory(AbsoluteWindowsPath) returns existing
NativeEnrollmentInventoryObservation; root-only OBSERVED is a valid empty directory.
Use ordinary existing B1 object/inventory/metadata/hash/path constructors. Internal
typed immutable port results/entries permit injected negative tests, not bypass
success construction. Null input rejects before IO. Every failed result has EMPTY
Objects, never a partial positive. Existing finite ReadbackStatus values only.

C3-NATIVE: sole Win32ReadbackPort and nested NativeMethods become partial; cohesive
Win32DirectoryReadback.cs owns same-handle directory listing and strict decoding,
reuse existing prefix/finalpath/reparse/descriptor/snapshot checks and PInvokes.
Only new native entry GetFileInformationByHandleEx; no duplicated CreateFileW or
second interop/Runner. Root/listing handle read-control+list, OPEN_EXISTING,
noninherit/reparse-open/backup, ShareRead; ancestors metadata-only existing rights.
Reject non-directory/reparse root or child, wrong paths/kinds/IDs and native faults.
Use same handle across bounded pages; NextEntryOffset0 ends ONE page, not complete
enumeration. Only documented NO_MORE_FILES ends enumeration; errors discard all.
Record offsets aligned8, bounds/overflow/UTF16 byte-length strict, single filename
component only, reject malformed/duplicate/case-alias names; skip only dot/dotdot.
4096-byte native buffer, bounded page count4096, existing4096 object cap includes root.
Capture root metadata before/after listing; drift refuses, handles close on all exits.

C3-COMPOSE: façade owns validation/composition, native partial owns handle lifetime/
records; tests own fixtures/assertions. Files call existing WindowsPayloadReadback
for actual content; each child's volume/fileID must equal its enumerated identity.
Directory metadata must come from an actual handle checked as a DIRECTORY, not
assumed from a caller's kind or untyped metadata. Factor existing validated native-
metadata conversion from WindowsReadback as a small internal reusable operation;
preserve public Read method/flags/failures and actual getter tests. No copy of
descriptor hashing or public DTO bypass. Every child failure/malformed result or
scope/count mismatch discards the entire inventory. No filesystem/source discovery.

Bound cumulative file bytes to64MiB per directory and cooperative total10s, checked
before/after each native/child operation; one C2 payload call already has3s deadline.
These explicit local observer bounds do not grant ACL rights or claim preemptive
cancellation of an uninterruptible syscall/atomic whole-tree/128-bit ReFS identity.
Later recursive enrollment must reuse this primitive under its own exact source
binding, not treat immediate-child success as full CodeRoot qualification.

C3-TEST pure cells: root-only and mixed legitimate objects, exact bytes/hash/size;
strict malformed page/unaligned/short/overflow/oddUTF16/name/path/reparse/duplicate/
continuation cases;4096 inclusive/4097 rejection; aggregate byte boundary; root drift;
wrong child volume/ID/kind; later child or enumeration failure yields empty inventory;
port exception finite, null no portcall. Pin production continuation/identity/no-
partial/drift predicates, not only copied parser helper assertions. Author actual
identity predicate red/restored green; Root different continuation/no-partial/native
door red/restored green, zero-red is finding. Preserve N1/C2 actual getter/content.

Optional ACTUAL C# native case in the cohesive new self-test file uses ONE selector
JOHNNY_DIRECTORY_READBACK_TEST_ROOT read once; default null skips IO, invalid empty/
relative/over32766 fails existing finite self_test_failed path before IO, Program
unchanged. It is test data, NOT authority/enrollment/observer evidence. Root registers
new owned source-only ordinary directory fixture BEFORE creation: directory-readback-
fixture below each existing johnny30n3-native-seam-{owner,review}-20261019 Temp root.
Known literal alpha.bin (UTF8 "directory payload\n"), empty nested directory, and
page-000.bin..page-127.bin (UTF8 "page payload\n") exercise actual multiple pages.
Expected exact names/count/hash/size independent of Actual. Missing root/file-root
and held existing invalid-content fixture must refuse without partial objects.
No symlink/ACL/denial/protected-path probe, cleanup or unrelated job/native campaign.
Default self-test stays pure; explicit actual command only adds that registered
selector. Do not modify/erase any earlier fixture; owner/TTL through review+seal,
Review/Recovery holds dominate expiry and exact teardown remains separately gated.

Exact CREATE3: library/local_orchestration/native_windows/WindowsDirectoryReadback.cs,
library/local_orchestration/native_windows/Win32DirectoryReadback.cs,
library/local_orchestration/native_windows/NativeDirectoryReadbackSelfTests.cs.
MODIFY4: library/local_orchestration/native_windows/Win32ReadbackPort.cs (partial
and only necessary shared directory-kind seam; C2 behavior untouched),
library/local_orchestration/native_windows/WindowsReadback.cs (internal converter
extraction only), library/local_orchestration/native_windows/SelfTests.cs (onecall),
library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj (compileentries).
No Python edits/new builder, Program/ProtectionPlan/NativeEnrollment*/N2/issuer/Git/
source_gate or publicDTO/state changes. New files own separate façade/native/tests
responsibilities, no prompts/ticket narratives. Forecast façade~150/native~250/test~250
lines, review cohesion and >500effective growth signals, never minify/forcedsplit.

Conditional development child Grant after different-seat DOC PASS + Root exact
ticket/index/b42/clean contained nonreparse WT/branch/roles/constructors readback:

~~~yaml
grant_id: grant-ticket30n3-directory-readback-20261019
parent_authority: batch-checklist-local-20261019-uncapped
ticket: workflow-governance/30
slice: 30N3-C3
closure: 8
baseline: b42ae444f6b6e873fb0a40ae0b3667be51bdf468
implementation_owner: /root/ticket30n2_native_impl
reviewer_orchestrator: /root
independent_evidence_peer: /root/ticket30_native_tools_review
worktree: .worktrees/skill-improvement-30n3-native-seam
branch: codex/skill-improvement-30n3-native-seam
context_view: ctx-ticket30n3-directory-readback-20261019
profile: HIGH_ASSURANCE_SOURCE_ENGINEERING_STAGING_ONLY
implementation_profile: implementation-standard
create: [library/local_orchestration/native_windows/WindowsDirectoryReadback.cs, library/local_orchestration/native_windows/Win32DirectoryReadback.cs, library/local_orchestration/native_windows/NativeDirectoryReadbackSelfTests.cs]
modify: [library/local_orchestration/native_windows/Win32ReadbackPort.cs, library/local_orchestration/native_windows/WindowsReadback.cs, library/local_orchestration/native_windows/SelfTests.cs, library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj]
delete: []
~~~

TEST→A→B: WindowsReadback public Read remains the actual getter entry; metadata
conversion moves once into its internal shared operation, inherited by new façade.
Run actual old getter on candidate and mutate new conversion/consumer-owned predicate
before claiming transfer. No tests retired, no separate B refactor starts on faith.
Nullable warnings-as-errors/offline55s nonincremental SDK build, default pure and
explicit registered native tests, memory compile/import of unchanged Python test,
exact source/EXE/DLL/loaded-module identities and raw command/output/elapsed.
Return exactcandidate/files/checks/mutation/findings/deviations; Root review then
existing enrollment/transport/observer source prerequisites, not stop at this commit.
No services/accounts/ACL/network/model/remote/receipt/spawn/Host qualification,
formal integration/activation, push/release/deploy or policy-denied cleanup retry.
Primary API refs refreshed: Microsoft GetFileInformationByHandleEx and
FILE_ID_BOTH_DIR_INFO (same-handle continuation, recordalignment, nonpermanent IDs).
https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex
https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_both_dir_info

## 30N3 — C2 evidence correction binding / closure07

This is the existing closure06 C2 correction for Root review811d1220, not a new
capability/PRD or change to public ReadFile/DTO/safety/Host authority. E01/E02/E03,
exact six source/test paths and ordinary registered fixtures remain as frozen.
Same development grant-ticket30n3-file-content-20261019 revision02, source baseline
767af00730a8cc292fade05fbeab78a776cad754; original grant/attempt/failure history stays.
Author /root/ticket30n2_native_impl, same native-seam WT/branch/context; Root reviewer,
different /root/ticket30_native_tools_review evidence peer. No allocation reset.

Chosen E01 seam: internal optional post-read PayloadFileSnapshot transform on
Win32ReadbackPort, after REAL same-handle hash/EOF/second snapshot only. Default
production constructor has no transform; public API unchanged, no fake success or
authority. In existing NativePayloadReadbackSelfTests only, optional native negative
test uses ONE selector JOHNNY_PAYLOAD_DRIFT_TEST_PATH, read once. Null means skip
without IO; non-null must validate ordinary AbsoluteWindowsPath and bounded text
before any IO. Invalid input becomes existing finite InvalidOperationException /
self-test_failed exit1, no uncaught stack or raw-path diagnostic. Program unchanged.
Only the explicit Python test supplies the pre-registered owned generic payload
path; selector is test input, never authorization, provenance, enrollment or grant.

Configured native negative creates the normal typed internal port with a transform
that XORs one LastWriteTimeFileTime bit, then calls actual public ReadFile. Expect
REPARSE_OR_IDENTITY_MISMATCH/no content hash/size; FileId-only production guard
mutation must named-red and exact restoration green. This rejects a deliberate
negative observation and may NOT manufacture positive/native qualification.
Default self-test remains pure via PROCESS_ENV whitelist without selector. No
negative path reads in default production WindowsPayloadReadback construction.

E02 fixed existing writer hold uses registered ordinary file + ReadWrite access
with FileShare.ReadWrite across REAL ReadFile call; no write or ACL effect. Original
share-read refuses without content; loosened ShareAll must named-red, restore green.
E03 generic technical bytes use newly registered payload-readback-fixture, old
c2-payload-fixture sealed/untouched. Only affected native/pure/strict/import/source
checks, no unrelated N2/native-job/Host campaign. Core byte positive and stream
positive continue, never all-refuse or weaker Expected.

An author first configured-negative run occurred before this exact selector
binding was committed; retain its raw chronology and do NOT count it as execution
under revision02 or retrofit approval. It stayed within batch's local owned-file
readonly effects, not a Host/security/cost expansion; all further configured native
runs pause until this exact binding independently DOC-reviewed and Root read back.
Other original-scope source/pure/E02 correction work continues under prior binding.
No new paths/dependencies/public types/Program/ProtectionPlan/SCM/account/ACL/network/
remote/model/Host/receipt/spawn/formal activation, integration, push/release/deploy.
Same owner/TTL/Review+Recovery holds for exact16c7dbbb generic fixtures; no cleanup.


## 30N3 — C2 bounded same-handle file content readback / closure06

Architecture Owner selects the minimum next observable native capability after C1,
not full directory enrollment or a new authority system. Source-engineering staging
under the same original Ticket30/PRD/CHG, uncapped batch and first-CVQ order exception.
C1 exact cee7933187a9bfb3190b4ff2ec72c7768db59405 is source baseline; Root independent
native matched replay seal283dd8c9. This held engineering source is NOT qualified
authority. B2/F1 candidates are not silently imported or integrated as formal sources.

Public service WindowsPayloadReadback has ordinary default constructor and
ReadFile(AbsoluteWindowsPath path) -> existing NativeEnrollmentObjectObservation.
Reuse B1 FILE/metadata/contentSha256/size DTO and existing finite ReadbackStatus,
all already constructed and negatively tested at reviewed3b2. No new public DTO,
success tag, authority, enum, policy or Runner. Internal injected-port constructor/
same typed result for pure fault tests; no dynamic/cast/reflection/bypass success.
Null input rejects before native call. A wrong-path/kind or malformed port result
fails closed; failed observations contain neither file content hash nor size.

C2-HANDLE: sole Win32ReadbackPort owns all opens and native interop. Reuse checked
prefix/final-path/reparse/descriptor helpers, no copied PInvoke or second path open
for content. Final FILE handle stays alive throughout before metadata, bounded
content SHA256 and after metadata. Share read only on payload final handle, no
write/delete sharing; metadata-only original N1 Read flags and behavior unchanged.
Ancestors stay metadata-only with explicit existing access. Use only read rights,
OPEN_EXISTING/noninheritable/reparse-open; never request write/owner/DACL/delete,
enable privilege or alter token/ACL. Size from that same handle must be1..64MiB,
reject directory/empty/oversize before hashing, fixed bounded streaming buffer.
No File.ReadAllBytes/FileStream(path) or Read-metadata-then-reopen shortcut.

C2-CONTENT: same-handle observed bytes == initial size, EOF confirmed; re-read identity,
attributes, creation/last-write, size, finalpath and exact owner/descriptor after hash,
reject differences/error/timeout with existing finite failure/no partial digest.
Read-induced access timestamp is not a false drift signal. Sharing conflicts and
unavailable platform/read failures remain explicit failures, not empty-file success.
Use finite 3-second cooperative content deadline plus bounded outer process test;
do not claim an uninterruptible native call is cancelled by a mere elapsed check.
Prefer documented overlapped ReadAsync on the existing handle with cancellation,
without extra SYNCHRONIZE permission being assumed in frozen protection plan.
No extra service ACL right is granted here; protected positive remains unverified.
Handle cleanup uses using/finally on all exits; no retained/escaped SafeFileHandle,
fire-and-forget task or duplicate close. No whole-filesystem atomic snapshot claim:
this raw, unqualified observation is not issuer proof or a guarantee of future
execution identity against an independently mutable/mapped writer.

C2-TEST: focused pure wrapper/port fault/result checks in a separate responsibility
test class; same-handle bounds/drift comparison helper checks use actual comparison,
not mocks of the assertion. Existing N1 self-test/enrollment constructor tests and
actual owned metadata getter must stay green on candidate after helper refactor.
Add focused actual payload assertion in existing Python native-tool test module:
registered owned ordinary fixture only, known independent bytes/hash/size positive,
missing/directory/empty/oversize refusal without payload data, unchanged metadata
identity and successful exclusive reopen after read (no leaked reader).
No real reparse/ACL/denial probe; those remain explicitly injected/not qualified.
Run exact assertion with manually supplied registered fixture tuple if the old
shared setup would attempt an unsupported symlink; no hidden builder invocation.
No native job tests or unrelated N2 requalification in this slice.
Author actual production predicate removal must name red cell and exact restored
green; Root uses a different real content/bounds/drift/native predicate, zero red
is finding. Strict nullable warnings-as-errors, Python strict/compile, actual binary/
DLL/source/test hashes and full raw commands/output/time. No all-refuse completion.

Exact CREATE2: library/local_orchestration/native_windows/WindowsPayloadReadback.cs,
library/local_orchestration/native_windows/NativePayloadReadbackSelfTests.cs.
Exact MODIFY4: library/local_orchestration/native_windows/Win32ReadbackPort.cs,
library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj,
library/local_orchestration/native_windows/SelfTests.cs, tests/test_native_authority_tools.py.
csproj only compile entries, SelfTests only call into new cohesive pure tests.
WindowsReadback.cs/Program/ProtectionPlan/NativeEnrollment*/N2/Git/issuer/observer
source forbidden. Existing shared fixture body is not changed by C2; F1 is separate.
No additional dependencies or files. Review growth/reuse instead of compressing code
or hiding implementation in tests. Pure façade vs native handle lifetime vs focused
assertions remain distinct responsibilities; no owner prompts/ticket narrative in source.

Conditional development child binding after different-seat DOC PASS and fresh Root
same-lifetime source/contained clean WT/role readback:

~~~yaml
grant_id: grant-ticket30n3-file-content-20261019
parent_authority: batch-checklist-local-20261019-uncapped
ticket: workflow-governance/30
slice: 30N3-C2
closure: 6
baseline: cee7933187a9bfb3190b4ff2ec72c7768db59405
implementation_owner: /root/ticket30n2_native_impl
reviewer_orchestrator: /root
independent_evidence_peer: /root/ticket30_native_tools_review
worktree: .worktrees/skill-improvement-30n3-native-seam
branch: codex/skill-improvement-30n3-native-seam
context_view: ctx-ticket30n3-file-content-20261019
profile: HIGH_ASSURANCE_SOURCE_ENGINEERING_STAGING_ONLY
implementation_profile: implementation-standard
review_profile: ticket-review
create: [library/local_orchestration/native_windows/WindowsPayloadReadback.cs, library/local_orchestration/native_windows/NativePayloadReadbackSelfTests.cs]
modify: [library/local_orchestration/native_windows/Win32ReadbackPort.cs, library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj, library/local_orchestration/native_windows/SelfTests.cs, tests/test_native_authority_tools.py]
delete: []
~~~

Prior completed C1 allocation released, WT/ref/evidence retained. Owner output
johnny30n3-native-seam-owner-20261019 and Root output
johnny30n3-native-seam-review-20261019 retain owner/TTL through review/seal and
Review/Recovery hold; exact new ordinary fixture subdirectories registered before
creation. No cleanup/retry of denied action. Percommand60s/child55s, old usage retained.
No Host/install/SCM/service/account/ACL/network/model/remote/spawn/receipt effects,
protected-root writes, real qualification, formal integration/activation or
push/release/deploy. Return exactcandidate/files/checks/raw native+mutation outputs/
elapsed/deviations, Root review then original next inventory/installation prerequisites.

Primary references read for this seam: Microsoft CreateFileW (read/share/overlapped/
noninheritable flags), RandomAccess.ReadAsync (same SafeFileHandle, offset, cancellation),
GetFileInformationByHandle; no API reference is itself qualification evidence.
https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
https://learn.microsoft.com/en-us/dotnet/api/system.io.randomaccess.readasync?view=net-10.0


## 30N3 — F1 shared native-test fixture separation / closure05

Same original Ticket30/PRD/CHG and reviewed uncapped local batch; this repairs the
shared verification entry, not a new product policy, PRD, Runner or qualification.
B2 bf5a4a3c engineering seal3c87ef77 and C1 seal283dd8c9 remain held/unintegrated.
Reuse existing offline SDK builder, assertions and single tests/test_native_authority_tools.py.
MODIFY1/CREATE0/DELETE0, baseline bf5a4a3c82131c308ffa85b2d899d4afd1cf32d9.
No product source, expected masks, native job acceptance or SDK/config edits.

F1-BUILD: extract restore/build/candidate logic to one shared builder and session
native_candidate fixture; native_fixture depends on it and only creates the owned
ordinary payload fixture. Preserve offline NuGet.Config, nonincremental compile,
output-root isolation, per-child deadline, full stdout/stderr and exact candidate.
Pure self/enrollment/job-contract/native-job assertion functions consume candidate
only, not an unnecessary payload or symlink. Test selection doesn't invoke unrelated
native job workload. Modes/plan/missing use shared noncreating target-path helper,
unchanged actual CLI assertions/PROCESS_ENV, no physical protected-path creation.
Keep existing test assertions, including actual identity and failure labels.

F1-PROBE: default zero symlink attempts. Existing optional real reparse branch may
run only with explicit JOHNNY_NATIVE_REPARSE_OPT_IN=1 in an independently authorized
test invocation; this flag is a method selector, NOT permission or Host capability.
Missing opt-in gives exact INJECTED/not-opted-in evidence. Opted-in creation failure
stays injected/unavailable. Actual campaign here does NOT opt in or retry known1314.
No machine setting, ACL, account, privileged operation or qualification is implied.

F1-VERIFY: build-boundary test makes mkdir/payload-write/symlink fail-fast while
asserting both exact bounded SDK commands, timeout and output identity. Add default
native setup test with symlink fail-fast and explicit injected marker; mock branch
selection only, not core product or native assertion. Pure enrollment selection
must actually build/run with no native payload setup. Existing real owned native
getter runs against candidate and explicit injected reparse; no real symlink probe.
Strict mypy, compile/import, affected pytest, author actual guard mutation red/restore
green and Root different-door mutation red/restore green. Output must identify actual
candidate source+EXE+DLL/test hashes. Native N2/job tests not requalified by this cut.
No new public DTO, existing Python fixture typed shapes; constructor preflight reuses
the already reviewed candidate and observation contracts rather than fabricating it.

Conditional same-lifetime child Grant after independent DOC PASS and Root fresh
baseline/clean source/worktree/role readback (development authority, not trusted issuer):

~~~yaml
grant_id: grant-ticket30n3-fixture-separation-20261019
parent_authority: batch-checklist-local-20261019-uncapped
ticket: workflow-governance/30
slice: 30N3-F1
closure: 5
baseline: bf5a4a3c82131c308ffa85b2d899d4afd1cf32d9
implementation_owner: /root/ticket30_native_tools_impl
reviewer_orchestrator: /root
independent_evidence_peer: /root/ticket30_native_tools_review
worktree: .worktrees/skill-improvement-30n3-enrollment
branch: codex/skill-improvement-30n3-enrollment
context_view: ctx-ticket30n3-fixture-separation-20261019
profile: HIGH_ASSURANCE_SOURCE_ENGINEERING_STAGING_ONLY
implementation_profile: implementation-standard
review_profile: ticket-review
create: []
modify: [tests/test_native_authority_tools.py]
delete: []
~~~

Prior completed B2 allocation released; original WT/ref/outputs stay held, no reset.
Owner/output inherited: johnny30n3-enrollment-owner-20261019 ordinary registered root;
Root review output johnny30n3-review-20261019. TTL through exact review/seal with
Review/Recovery holds overriding expiration; no cleanup or denied operation retry.
Commands<=60s/children<=55s, history/elapsed preserved, no cumulative/count ceiling.
Forbidden other source/PRD/SPEC/remote/production data/secret/Host install/config/
model/network/account/service/ACL/receipt/spawn effects, formal activation or
push/release/deploy. Author returns exactcandidate/files/raw commands/results/
elapsed/mutations/deviations; Root independently reviews, then continues existing
native reader preparation. No checksum/assertion weakening or all-refuse shortcut.


## 30N3 — C1 native readback seam / closure04, independent of pure B2

This is the minimum responsibility extraction before later native content/inventory
work, not a new product capability/Ticket/PRD or Router stage. Same uncapped batch
and first-entry source-staging exception; does not extend qualified review/effects.
Independent from B2 MODIFY3: it changes only the existing native adapter boundary
and compile entry, not ProtectionPlan/verifier/tests or their expected behavior.

CREATE library/local_orchestration/native_windows/Win32ReadbackPort.cs owns the
EXACT existing internal Win32ReadbackPort class plus its necessary using directives.
MODIFY WindowsReadback.cs removes ONLY that class and now-unused using directives;
its public contracts/observer wrapper and internal INativeReadbackPort/result types
stay byte-equivalent apart from spacing/usings. MODIFY JohnnyAuthority.Tools.csproj
adds its sole compile entry. CREATE1/MODIFY2/DELETE0. No signatures, native API,
access/share flags, metadata mapping, failure behavior or another PInvoke set changes.
This separates public observation contracts from native handle/interop implementation
before extending either; no forced compression, duplicate helper or new framework.

SC1 before: existing pure self-test, enrollment-contract-self-test, strict compile,
and unchanged real owned-file getter assertion are available. Author must run the
old real getter before move, pin actual input/EXE/DLL and expected OBSERVED metadata;
then run that same assertion after the move. Reuse existing registered SDK fixture/
test assertions but do not repeat unsupported symlink privilege probes. Native read
only on registered seat-owned ordinary Temp file/directory; no protected-path writes,
ACL/reparse creation or Host qualification. Explicit failed-port cases stay INJECTED.
SC2 exact extracted class body hash equals baseline body; namespace/type signatures/
public APIs and other source blobs unchanged, strict nullable/warnings-as-errors,
affected pure tests green, no new dependencies. No behavior fallback/all-refuse.
SC3 an actual moved native getter success check mutation must make the unchanged
real getter test fail, exact restore/nonincremental build then green; Root uses a
different actual moved check. Source grep/wiring-only PASS is insufficient. No
later content/hash/directory enumeration implementation is granted in this cut.

Conditional development child binding after different-seat DOC PASS and fresh Root
contained clean source/role/WT readback; this is not protected runtime authority:

```yaml
grant_id: grant-ticket30n3-native-seam-20261019
parent_authority: batch-checklist-local-20261019-uncapped
ticket: workflow-governance/30
slice: 30N3-C1
closure: 4
stage: EXISTING_BEHAVIOR_EXTRACTION_ONLY
baseline: 3b2da4b00076bcfc500cce5560cb2a045550c802
implementation_owner: /root/ticket30n2_native_impl
reviewer_orchestrator: /root
independent_evidence_peer: /root/ticket30_native_tools_review
worktree: .worktrees/skill-improvement-30n3-native-seam
branch: codex/skill-improvement-30n3-native-seam
context_view: ctx-ticket30n3-native-seam-20261019
profile: HIGH_ASSURANCE_SOURCE_ENGINEERING_STAGING_ONLY
implementation_profile: implementation-standard
review_profile: ticket-review
create: [library/local_orchestration/native_windows/Win32ReadbackPort.cs]
modify: [library/local_orchestration/native_windows/WindowsReadback.cs, library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj]
delete: []
```

Separate completed N2 allocation released for this lane; its old WT/ref/source
stays under review hold, not reset or imported as authority. New WT/ref/output
owner=30N3-C1/named seat, output
C:/Users/GameBoy/AppData/Local/Temp/johnny30n3-native-seam-owner-20261019,
TTL through exact review/evidence seal, Review/Recovery holds override expiry;
normal exact teardown only, no denied cleanup retry. Root registers before dispatch.
Commands<=60s/child<=55s; old elapsed/failures retained, no cumulative/count cap or
unchanged blind retry. No B2 path overlap, source privileges/installer/SCM/account/
ACL/network/pipe/Host/model/remote/Agent-spawn/receipt effects or formal activation,
push/release/deployment. N2 native job is not called. Qualified audit/30B/43/TAL
holds remain; return candidate/exact files/raw commands+getter results/mutations/
timing/deviations, Root independent review then separate content-reader preparation.

## 30N3 — B2 pure verification / closure03

Same original lineage, uncapped batch and first-entry SOURCE_ENGINEERING staging.
B1 actual constructor preflight must pass and final exact commit be pinned below.
B2 is pure comparison/canonical protection-plan reuse ONLY, no native adapter yet.

Root + independent ordinary architecture peers read actual B1 contracts and N1
ProtectionPlan/WindowsReadback. Choose minimum MODIFY3/CREATE0/DELETE0:
library/local_orchestration/native_windows/NativeEnrollmentVerifier.cs,
library/local_orchestration/native_windows/NativeEnrollmentVerificationSelfTests.cs,
library/local_orchestration/native_windows/ProtectionPlan.cs. No other source,
Python/Program/project/parser/old SelfTests/N2 changes; future native reader not
granted. No new runner/fixture/state/policy engine.

Add only public static NativeEnrollmentVerifier.Verify(NativeEnrollment expected,
NativeEnrollmentReadback observed)->NativeEnrollmentVerification. Reject null;
normal mismatch returns finite existing REFUSED/reason, never an arbitrary exception
or MATCH. Build exact expected typed-path sets from expected manifest/payload entries:
CodeRoot DIRECTORY, executable/dependencies FILEs and every intervening DIRECTORY.
DataRoot DIRECTORY, only config FILE and its intervening DIRECTORY set; unrelated
mutable DataRoot files are not scanned or required absent. Conflicting file/dir
namespace expectations refuse, not guessed. Compare OrdinalIgnoreCase whole paths
and exact kinds/counts; no extras, missing paths or basename/prefix shortcut.

An observed failed inventory/object refuses READBACK_FAILED; mismatched root/set/
kind is INVENTORY_MISMATCH. Each declared file requires exact digest/size or
PAYLOAD_MISMATCH. Metadata must carry the complete existing NativeObjectObservation;
pure comparison DOES NOT invent expected OS file IDs absent from the enrollment.
Before/after same-handle identity/size/descriptor drift belongs to the future native
reader and must become failed observation, not claimed proven by these fake values.

ProtectionPlan adds public static string PayloadFileSddl(NativeSetupManifest,
NativePayloadRole), validating arguments and reusing its sole existing CreateSddl/
AceEntry/rights source. SYSTEM owner, SYSTEM/Admin FullControl, service code RX
for executable/dependency or existing data Modify for configuration; protected
DACL, file ACE flags None. Reuse existing directory CodeRootSddl/DataRootSddl for
all corresponding declared directories. No extra principal/right, root Plan JSON/
Build output/API change, actual ACL write or installing these descriptors.

Verifier compares parsed Owner and DACL-present/protected policy plus exact ACE
binary multiset (SID/mask/qualifier/flags/opaque bytes), no extra ACE and no string
format normalization. Do not claim queried metadata proves SACL/group policy.
Equivalent descriptor formatting/order may pass without permitting extra rights;
missing/null/unprotected/extra or changed ACE/owner refuses PROTECTION_MISMATCH.
Do not duplicate descriptor-construction policy in verifier/tests. Tests assert
independent SID/mask/flags expectations so changing the shared plan cannot make
both Expected and Actual silently green.

V4 positive complete synthetic protected-path observation matches exact payloads/
configuration/directory plans with Scope SOURCE_ONLY_UNQUALIFIED. It remains FAKE
comparison evidence, never an OS-protected enrollment/issuer/Host positive.
V5 independent one-change negatives: failed/missing/unavailable/reparse code/data,
wrong root, extra/missing/alias/wrong-kind path or intermediate directory, file/
directory namespace conflict, changed config/dependency/exe hash and size, owner/
unprotected/extra/changed mask/inheritance/unknown ACE. Preserve all B1 constructors
and A parser cases; don't satisfy a negative through some unrelated invalid field.
V6 actual author product guard weakening and Root different product door named red
then exact inverse/nonincremental green; strict warnings-as-errors, existing focused
pure pytest/compile/mypy and diff/scope/source readback. No broad native/old gate/
04 regression rerun; tests use passed existing enrollment fixture, parameterized
small variants and shared assertions, no independent bulky script/report tree.
Growth threshold signals demand responsibility review, not compression/splitting.

Retain existing roles, WT/ref/output ownership/TTL/Review+Recovery holds; <=60s
outer/<=55s child default, record all terminal elapsed/failures. No cumulative or
fixed correction count, no unchanged blind retry. No root setup/account/SID/service/
ACL/AppContainer/firewall/pipe/listener/remote/model/provider/Host/native read/spawn/
receipt or integration/activation, push/release/deployment/old cleanup retry.
A/B1 source engineering does not clear30B/43/TAL qualification holds.
Exact development Grant below activates only after different-seat DOC consistency
and Root fresh clean role/source binding. Next route ordinary pure review then
separate minimum native-reader preparation, not Human Owner technical approval.

B1 source baseline3b2da4b00076bcfc500cce5560cb2a045550c802 (actual
product9ee2908704da4f97e8f1e1a23c3a4707c0f93082) passed Root/peer constructor preflight,
sealed d7f5e7cc. This B2 binding is conditional on exact independent DOC PASS:

```yaml
grant_id: grant-ticket30n3-pure-verification-20261019
parent_authority: batch-checklist-local-20261019-uncapped
ticket: workflow-governance/30
slice: 30N3-B2
closure: 3
stage: PURE_COMPARISON_ONLY
baseline: 3b2da4b00076bcfc500cce5560cb2a045550c802
implementation_owner: /root/ticket30_native_tools_impl
reviewer_orchestrator: /root
independent_evidence_peer: /root/ticket30_native_tools_review
worktree: .worktrees/skill-improvement-30n3-enrollment
branch: codex/skill-improvement-30n3-enrollment
context_view: ctx-ticket30n3-pure-comparison-20261019
profile: HIGH_ASSURANCE_SOURCE_ENGINEERING_STAGING_ONLY
implementation_profile: implementation-standard
review_profile: ticket-review
create: []
modify: [library/local_orchestration/native_windows/NativeEnrollmentVerifier.cs, library/local_orchestration/native_windows/NativeEnrollmentVerificationSelfTests.cs, library/local_orchestration/native_windows/ProtectionPlan.cs]
delete: []
```

## 30N3 — B1 readback construction binding / closure02 history

This supersedes only the conditional B path/type plan of closure01 below. Same
Ticket/PRD/CHG/Owner batch/first-entry staging scope; A remains accepted ordinary
constructor preflight, no qualified source or operational authority. Root read
WindowsReadback/ProtectionPlan/NativeEnrollment in full at cb877f73; independent
/root/batch_authority_review confirmed the minimal reuse/fixture constraints.
Root chooses the engineering design, not a new Human Owner decision or SPEC.

Two actual gaps require the bounded source amendment: N1 Read closes its handle
before returning and exposes no content hash/size/inventory; root inheritance
ACEs cannot be compared literally to child-file DACLs. Never Read-then-reopen a
file to pretend same-handle identity. Temp fixtures cannot be valid protected
NativeSetupManifest paths; native Temp tests verify only low-level observation.
No constructor relaxation or ProgramFiles/ProgramData/ACL write is authorized.

B1 is constructor-only, no OS port/effect or pure comparator behavior yet:

| CREATE path under library/local_orchestration/native_windows/ | Single responsibility |
| --- | --- |
| NativeEnrollmentVerifier.cs | Immutable observation/verification input/result contracts; later same file owns pure comparison, no Win32 |
| NativeEnrollmentVerificationSelfTests.cs | Readback-contract and later comparison tests, reuse enrollment instance from existing self-test, no second fixture/builder/runner |

MODIFY exactly JohnnyAuthority.Tools.csproj (two compile entries) and
NativeEnrollmentSelfTests.cs (call new RunContracts(enrollment) only). No Program,
Python wrapper, parser, existing NativeManifest/ProtectionPlan/WindowsReadback,
N2 or other source edits in B1; CREATE2/MODIFY2/DELETE0. Shared fixture is passed
as a typed value rather than opening private fixture state or cloning setup code.

Frozen constructor domain, finite enums, ordinary validating immutable classes:
- NativeObservedObjectKind: FILE | DIRECTORY.
- NativeEnrollmentObjectObservation(path:AbsoluteWindowsPath, kind,
  metadata:NativeObjectObservation, contentSha256:Sha256Value?, sizeBytes:long?).
  Reuse metadata's finite ReadbackStatus. OBSERVED FILE requires hash and size
  1..67108864; DIRECTORY has neither; any failed metadata has neither. Null or
  undefined kind rejects; no path/hash normalization or mutable dictionaries.
- NativeEnrollmentInventoryObservation(root:AbsoluteWindowsPath,
  status:ReadbackStatus, objects:IEnumerable<NativeEnrollmentObjectObservation>).
  OBSERVED copies 1..4096 objects, exactly one root DIRECTORY, every object OBSERVED
  and at root/strict descendant, unique OrdinalIgnoreCase paths. Failed status
  copies zero objects only. Wrong-root/missing-root/non-directory-root reject.
- NativeEnrollmentReadback(codeInventory:NativeEnrollmentInventoryObservation,
  dataObjects:IEnumerable<NativeEnrollmentObjectObservation>) copies 1..4096 unique
  paths, including finite failed observations; do not turn a failed read into a
  successful inventory. B2 compares exact DataRoot/config ancestor set; it never
  closes over unrelated mutable DataRoot files.
- NativeEnrollmentVerificationStatus: MATCH | REFUSED; reason enum NONE |
  READBACK_FAILED | INVENTORY_MISMATCH | PAYLOAD_MISMATCH | PROTECTION_MISMATCH.
  NativeEnrollmentVerification(status,reason) validates finite pair: MATCH/NONE
  or REFUSED/non-NONE, immutable Scope=SOURCE_ONLY_UNQUALIFIED. No ACCEPTED/QUALIFIED
  status, evidence authority, service/session/grant state or Router transition.

B1 acceptance V1: ordinary complete file/directory/failure/inventory/readback/result
values construct; each null/tag/cross-field/bound/path/duplicate variant rejects,
collections defensively copied. Exact boundary positives4096 and64MiB survive.
V2: existing enrollment-contract-self-test runs both suites via the sole builder;
strict nullable/warnings-as-errors, unchanged Python wrapper strict/compile check,
no filesystem/native source call. V3: author weakens a real constructor guard and
Root a distinct one; named red -> exact inverse/forced --no-incremental green.
Run each command<=60s (compiler/test child<=55s), retain all timings/history; no
cumulative/count cap, no unchanged failure retry or new dependencies/framework.
Signals product300/test350 and500+ require responsibility review, not compression.

After actual B1 symbols/constructors and independent preflight pass, Root prepares
exact B2 child binding; B2 is NOT_GRANTED here. Expected B2 minimal paths are
CREATE WindowsPayloadReadback.cs (content/inventory orchestration only), MODIFY
WindowsReadback.cs (shared checked-handle primitive and one existing PInvoke set),
ProtectionPlan.cs (canonical derived file policy), these new verifier/self-tests,
csproj/Program and existing Python wrapper. No broad scan or second policy engine.
File policy derives existing SYSTEM/Admin full plus service code RX/config Modify,
explicit protected DACL and AceFlags.None; child directory policy derives existing
root descriptor. No extra principal/right; existing N1 plan JSON/API unchanged.
Actual applying those descriptors requires separate exact OS authorization.
Verification must protect declared intermediate directories under CodeRoot/DataRoot,
not assume metadata authenticity or demand that mutable DataRoot have no other data.

Exact child binding, conditional on different-seat DOC PASS and fresh role/Git
readback; development authority only, never protected issuer/operational Grant:

```yaml
grant_id: grant-ticket30n3-readback-constructors-20261019
parent_authority: batch-checklist-local-20261019-uncapped
ticket: workflow-governance/30
slice: 30N3-B1
closure: 2
stage: CONSTRUCTOR_ONLY
baseline: cb877f73a7696e822b89fcfcd82a5b5168df68e8
implementation_owner: /root/ticket30_native_tools_impl
reviewer_orchestrator: /root
independent_evidence_peer: /root/ticket30_native_tools_review
worktree: .worktrees/skill-improvement-30n3-enrollment
branch: codex/skill-improvement-30n3-enrollment
context_view: ctx-ticket30n3-readback-contracts-20261019
profile: HIGH_ASSURANCE_SOURCE_ENGINEERING_STAGING_ONLY
implementation_profile: implementation-standard
review_profile: ticket-review
create: [library/local_orchestration/native_windows/NativeEnrollmentVerifier.cs, library/local_orchestration/native_windows/NativeEnrollmentVerificationSelfTests.cs]
modify: [library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj, library/local_orchestration/native_windows/NativeEnrollmentSelfTests.cs]
delete: []
```

Retain existing seat-owned WT/ref/output registration, TTL through exact review
seal, Review/Recovery holds override expiry, no denied cleanup retry. A product
blobs and all prior evidence remain; no unrelated recompilation/native campaign.
No actual service/account/SID/ACL/AppContainer/firewall/install/persistent rights,
pipe/listener/remote/provider/model/Host/spawn/receipt effect, push/release/deploy
or formal gate activation. Qualified audit and30B/43/TAL holds remain unchanged.
Return typed candidate/files/actual symbols/checks/mutations/time/deviations;
Root routes to constructor preflight and then B2 preparation, not another ordinary
technical-approval question. No prompt/Owner narrative/work order in source.

## 30N3 — Protected payload/enrollment readback construction / closure01 history

Current A preflight candidate cb877f73a7696e822b89fcfcd82a5b5168df68e8:
CONSTRUCTOR_SOURCE_ENGINEERING_PREFLIGHT_PASS / PHASE_B_NOT_DISPATCHED /
QUALIFIED_AUDIT_BLOCKED / NOT_INTEGRATED. Root independent actual predicate reds,
exact restore/forced greens, strict and different-seat narrow preflight are sealed
in original30 review e7760267. Five guard zero-red and roundtrip-oracle history
remain; final product blob6cac5030c2e7a8e0885cfed18f3d590b92f329a3. No native
effect, source qualification or completed Ticket30 follows. Original A Grant below
is executed construction history; B requires its own exact binding/preflight.

Current local building slice, not a new Ticket/PRD or operational enrollment.
Parent=batch-checklist-local-20261019-uncapped; effective Owner policy at85028a76
and a75d9992, first-CVQ source-order exception retains its exact limits. Baseline
88b707c8585501173bb6898f332ad52a5765ed66 is reviewed source construction only;
N2's native counter-oracle investigation remains separate and cannot be hidden
by N3. N3 does not invoke N2/Host or use its unfinished native result as authority.

Architecture/reuse readback: runbook03 sections2/3/6; N1 source0a2e0661
NativeManifest/ProtectionPlan/WindowsReadback were read in full. N1 `inspect`
observes ACL/owner/file identity, but does not compare full payload/config hashes
to an enrolled manifest. 30G source20bd6e30 ledger remains the sole future grant
store; an injected PeerFrame/AuthorityPeer is not OS identity. N3 fills only this
readback/comparison prerequisite. No service/issuer/pipe or second authority engine.

Root chooses these separate responsibilities, not a monolithic installer:

| Exact source path under library/local_orchestration/native_windows/ | Phase / responsibility |
| --- | --- |
| CREATE NativeEnrollment.cs | A: immutable bounded enrollment/payload values and strict parser only; reuse NativeSetupManifest, named SID/path/hash values and ProtectionPlan's canonical setup digest; no OS calls |
| CREATE NativeEnrollmentSelfTests.cs | A: ordinary constructor/negative/JSON checks; later same shared finite fake-observer cases, no duplicated compiler/test runner |
| MODIFY JohnnyAuthority.Tools.csproj | A: explicit compile entries only |
| MODIFY Program.cs | A: enrollment-contract-self-test composition/finite output only; B: readonly verify-enrollment composition after actual constructor preflight |
| MODIFY tests/test_native_authority_tools.py | A: reuse sole typed fixture/nonincremental offline builder; bounded pure mode/schema tests; later B owns actual fixed-fixture readback checks |
| CREATE NativeEnrollmentVerifier.cs | B ONLY, not A: pure expected-versus-observed comparison and finite SOURCE_ONLY_UNQUALIFIED refusal result |
| MODIFY WindowsReadback.cs | B ONLY, not A: bounded handle-based payload hash/inventory observation, reuse current native object/ancestor/reparse/ACL readback |

A CREATE2/MODIFY3; B adds only the declared verifier CREATE and readonly adapter
MODIFY after actual new type construction/independent preflight. DELETE0. No edits
to N1 NativeManifest/ProtectionPlan/SelfTests, N2 job sources, grant_authority,
mainline_readback, Router, specs/skills/tickets/index/docs or package dependencies.
If constructor dependencies require a different path, return finding before edit;
Root may limit/review a necessary batch-local change, never silently cross scope.

Minimum typed semantics for A, with exact actual signature mapping returned for
preflight: enrollment identity (bounded canonical identifier), revision exactly1,
existing setup manifest plus its exact canonical SHA256, one finite payload entry
set containing the setup executable and one explicit configuration entry, other
declared dependencies, each exact absolute path/role/digest. Executable and
dependency entries stay within setup CodeRoot; the one protected configuration
entry stays within setup DataRoot, matching runbook03 section6's policy location.
Paths are unique using Windows case-insensitive identity; no
relative/ADS/device/reparse assumption, wrong-role root, duplicate alias,
blank/malformed digest, missing executable/config or inconsistent setup digest.
Executable entry path/hash must equal setup's existing path/hash, not a separately
caller-chosen executable. Configuration path/digest must match its payload entry.
Reuse named primitives; don't add speculative service/session/VM/Grant types.
List/JSON bytes/depth/individual file bytes have explicit finite positive bounds;
initial payload<=128 entries, JSON<=131072 UTF8 bytes, depth<=12 and file<=64MiB.
These are local verifier bounds, not operational granted cost/Host policy.
Collections are immutable/copied; no dynamic dictionaries beyond JSON boundary.

Observation/result shapes for B must have a real observed-object/failed-read
alternative, not fabricated successful metadata. Success carries observed owner/
SDDL, volume/file identity, content hash/size and actual closed inventory; missing,
denied, reparse/identity change or unavailable has no fabricated digest. Compare
expected N1 plan owner/protected DACL and exact declared payload/config inventory,
using CodeRootSddl for executable/dependencies and DataRootSddl for configuration;
never accept merely because caller wrote OBSERVED. Preserve uncertainty rather
than normalizing a descriptor/path into permission. Exact approved SDDL binary
semantic comparison is allowed; string-format equality alone is not provenance.
Read file metadata/hash under the same native handle, no write/delete sharing;
reparse ancestors, identity drift, extra entries, overflow and unknown kinds refuse.
Do not claim the returned hashes alone pin later execution or authenticate a
service/issuer; protected composition and operational qualification remain later.

A acceptance E1: validating constructors plus bounded JSON roundtrip preserve all
fields and reject every required omission/null/extra/unknown tag, duplicate fields,
oversize/depth/invalid UTF8, wrong setup digest, payload/config/executable mismatches,
case-insensitive duplicates, outside-root/wrong-role paths (including config under
CodeRoot or executable/dependency under DataRoot) and mutable input substitution.
E2: legitimate finite manifest and explicit failed observation/result variants
remain constructible; invalid input calls no OS/file observer. E3: actual source
checker, explicit project compile/CLI mode and strict offline pure tests/imports.
Root verifies new actual types before B; no resolver/filesystem call in A. This
is the same construction-before-behavior ordering already used in N1/N2, not a new
Gate or authority exemption. Test fakes are evidence of comparisons only.

B acceptance (conditional, NOT_DISPATCHED): exact fake observation gives match;
each hash/owner/DACL/file identity/config/inventory change refuses; missing/denied/
unavailable/reparse/overflow remain refusal. Native read-only tests only on exact
registered seat-owned fixture tree, no ProgramFiles/ProgramData creation or ACL
writes. A complete real protected-enrollment positive remains UNVERIFIED until
its separately approved OS setup; no all-reject claim of functional completion.
Root/peer actual predicate weakening must fail named test then exact restore green;
reuse N1/N2 unchanged tests, no broad unrelated rerun/fixture proliferation.

Conditional precise child Grant (source metadata, not production issuer record):

```yaml
grant_id: grant-ticket30n3-enrollment-20261019
parent_authority: batch-checklist-local-20261019-uncapped
ticket: workflow-governance/30
slice: 30N3
closure: 1
stage: CONSTRUCTOR_ONLY
baseline: 88b707c8585501173bb6898f332ad52a5765ed66
implementation_owner: /root/ticket30_native_tools_impl
reviewer_orchestrator: /root
independent_evidence_peer: /root/ticket30_native_tools_review
worktree: .worktrees/skill-improvement-30n3-enrollment
branch: codex/skill-improvement-30n3-enrollment
context_view: ctx-ticket30n3-enrollment-20261019
profile: HIGH_ASSURANCE_SOURCE_ENGINEERING_STAGING_ONLY
implementation_profile: implementation-standard
review_profile: ticket-review
create: [library/local_orchestration/native_windows/NativeEnrollment.cs, library/local_orchestration/native_windows/NativeEnrollmentSelfTests.cs]
modify: [library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj, library/local_orchestration/native_windows/Program.cs, tests/test_native_authority_tools.py]
delete: []
```

Conditional on different-seat ordinary DOC consistency, fresh exact committed
ticket/blob/LF/baseline/clean contained non-reparse worktree and live named role
readback; Root pins those before same-lifetime author dispatch. Phase B paths above
are not yet granted. No operational trusted source/enrollment/Host qualification
or formal integration follows from a pure constructor pass. Existing first-entry
exception cannot be reused to clear30B/43/TAL independent-review requirements.

Resource/asset declaration: initial command60s/child55s, no cumulative/attempt cap
under current batch, retain old timings/failures. No identical unchanged retry.
Seat-owned output C:/Users/GameBoy/AppData/Local/Temp/johnny30n3-enrollment-owner-20261019;
worktree/ref/output/SDK cache/fixture owner=30N3/named seat, TTL through exact review
and evidence seal, Recovery/Review hold overrides expiry, teardown via existing
admission only; no automatic deletion or denied-cleanup retry. No screenshot/docs
generation by author. Product/test growth signals300/350 and500+ structure review
are not compression/split targets. No prompt/ticket narratives in source.

Return fixed candidate/files/actual constructor symbols, pure tests/strict checker
results, findings/deviations/remaining nonclaims. Root/peer narrow review then
the next original N3 B-slice preparation, not a Human Owner technical question.
No service/user/ACL/AppContainer/firewall/config install, persistent permission,
real pipe/listener/Host/model/provider/target/remote/native job effects, push,
release/deploy/formal gate activation. R0/DAP/Recovery/denied44 unchanged.

## 30N1 — Native protection planning/readback tool / closure revision01

State: SOURCE_ENGINEERING_PASS / QUALIFIED_AUDIT_BLOCKED / NOT_INTEGRATED. Development
Grant executed; source0a2e0661eef741be1b9df103ae8874c284cf60f8 is staged, not authority
or an install-ready service. Source baseline40aef85adadc02d6b73a8e99d0c16e2c7b022eb3;
exact original authority leafblob475bc02f481f2818016519d476b7e2ba59f91f79 retained.
Owner approved
the existing batch's continued local construction and explicitly approved redistribution
of the SAME900 command seconds: author350/reviewer220/control330, total ceiling1500.
Original599.2 remains. Historical30G author161/reviewer84 remain charged. Root's
previous control timing is UNRECONCILED (including the interrupted large-log read);
reserve200 for that history rather than pretend it is zero or recovered. Commands
from this approval onward are additional, recorded per command. No more bulk-log scan.
No role cap, failed attempt or correction resets when this slice starts.

Same PRD/CHG/SPEC/CONTEXT bindings as30G below. Baseline45758b18a35431927f6e5f16ad7c362214c40a06;
final document-reviewed baseline/leaf is read back before dispatch. Root Architecture
Owner fixes this tool contract under the Owner's local batch, not a new PRD/SPEC.
One observable outcome: a compiled Windows tool produces exact WHOLE protection
descriptors and candidate-bound readonly object observations from validated data,
without applying policy or declaring isolation/authority qualification.

| Binding | Exact limitation |
| --- | --- |
| Proposed child Grant | grant-ticket30n1-native-tools-20261019, activated only after independent document review; development/same-lifetime, not runtime issuer authority |
| Named owner/reviewer | /root/ticket30_native_tools_impl current gpt-6-luna/xhigh; different /root/ticket30_native_tools_review gpt-6-sol/high, same currently available semantic capability mapping as30G; Root only control/docs |
| Worktrees | .worktrees/skill-improvement-30n1-native / codex/skill-improvement-30n1-native and .worktrees/skill-improvement-30n1-review / codex/skill-improvement-30n1-review; clean contained nonreparse identities allocated/read by Root |
| Profile | POC/HIGH_ASSURANCE source-only Windows protection tooling; ordinary independent engineering staging under approved first-entry exception, NOT qualified audit/final source integration |
| Resource subset | Current same-Grant amendment: author<=135 and reviewer<=100; control<=40 including document helper<=8. Historical author132.77 and reviewer86.58 remain charged. All source corrections are consumed; review continuation ONLY finishes the already-red, byte-restored getter mutation's rebuild/green and exact final readback, within reviewer remaining13.42. These are subsets of new350/220/330 caps, not new Owner costs; N2 is still conditional/ungranted. Every command<=60s, compiler/test subprocess timeout<=55s, serial, no automatic retries/load |
| Language | Python3.11 remains the backend/Grant/Router language. C# nullable+warnings-as-errors is a Windows-native provisioning/observation tool shim, not another backend or authorization engine. Installed SDK10.0.302/CLR10.0.10 enable offline build; Python freezer packages were measured NOT_INSTALLED. This platform-tool boundary avoids a new downloaded Python packager or copying backend Grant logic. No generic language-policy change |
| No effects | No service/user/ACL/AppContainer/firewall change, native Host/Codex session, model/provider/remote call, actual pipe/listener or grant issue/consume. Native readonly getters only on test-owned fixtures in B; plan/self-test have no native effect. No existing candidate import or baseline-source MODIFY/DELETE |
| Asset lifecycle | owner=30N1/named seat; registered fixture/build roots owned by one test fixture, TTL=verification/review seal, normal exact teardown only. Worktree/ref and existing Recovery/cleanup holds retained; never retry a policy-denied cleanup, never reset/clean/delete historical assets |

### Exact source boundary / reuse / responsibility

CREATE only the nine paths in the active boundary below. Program is composition/CLI;
NativeManifest owns strict values and bounded JSON; ProtectionPlan owns whole DACL
construction; WindowsReadback owns native READ_CONTROL/attributes handles; SelfTests
owns shared parameterized constructor/negative cases. Python test wrapper builds
ONCE per fixture, invokes actual candidate binary and retains unfiltered failures.
No duplicated per-case compiler/browser/PNG/server framework, no new dependencies.

Reuse existing Windows BCL/Win32 descriptor and safe-handle primitives. READY
workflow-router-poc catalog remains policy metadata only; do not translate/copy
its backend/Grant engine into C#. Inspected staging/process_runner has fixed10s
timeout, DEVNULL output and six-key overlay; these cannot satisfy compiler timeout,
SDK environment or unreduced output. Use a thin explicit shell=False subprocess.run
in the one test fixture (no second generic runner). Existing environment_core has
cleanup retries/checkout-global lease state; do not adopt it as OS protection proof
or run its cleanup on retained assets. Temporary build files are not Temp Git repos.

### Frozen public contract / ordinary constructor order

Namespace Johnny.NativeTools. Use immutable named value types SidValue,
AbsoluteWindowsPath, Sha256Value, ServiceNameValue and VersionValue, with ordinary
public validating constructors (no implicit string conversion). Values reject null,
blank/trim differences, controls and malformed data, never repair it. SID must roundtrip
to canonical Windows SID text; SHA256 exactly64 lowercase hex; service name ASCII
letter then letters/digits/_/- length1..64; version 3 or4 decimal components bounded
by System.Version. Path is absolute local drive, nonroot, no UNC/device/ADS/relative/
dot-segment/trailing separator/control input; component-bound descendant comparisons.

NativeSetupManifest(schemaRevision:int, serviceName:ServiceNameValue,
serviceSid:SidValue, controllerSid:SidValue, subjectSid:SidValue,
codeRoot:AbsoluteWindowsPath, dataRoot:AbsoluteWindowsPath,
executablePath:AbsoluteWindowsPath, executableVersion:VersionValue,
executableSha256:Sha256Value). Revision exactly1, service SID S-1-5-80-...;
the three SIDs distinct, subject/controller cannot be SYSTEM/Administrators/Everyone.
Code/data roots strictly below actual Windows ProgramFiles/CommonApplicationData,
not those broad roots; executable strict descendant of codeRoot and .exe suffix.
ParseBounded(string)->NativeSetupManifest and ToCanonicalJson(): flat snake_case keys
schema_revision/service_name/service_sid/controller_sid/subject_sid/code_root/data_root/
executable_path/executable_version/executable_sha256, exactly those10 fields.
UTF8 body1..32768bytes; reject duplicates, unknown/missing/null/type/coerced/bool,
malformed JSON/depth>8; no credentials, approval bool, arbitrary commands or env refs.

NativeToolScope has only SOURCE_ONLY_UNQUALIFIED. ProtectionPlan.Build(manifest)
returns immutable NativeProtectionPlan with manifest SHA256 and exact owner SYSTEM,
code-root/data-root/SCM/read-pipe SDDL. Whole protected filesystem DACL: SYSTEM/Admins
full; service RX code and Modify data, inheritable to children, no ordinary subject/
controller/Users ACE. SCM SYSTEM/Admins control; controller onlyCC/LC/RC. Read-pipe
SYSTEM/Admins/service full and exact subject/controller data read+write+SYNCHRONIZE
mask0x00100003, no FILE_CREATE_PIPE_INSTANCE or WRITE_DAC/owner; never GENERIC_WRITE.
Use BCL security descriptor objects/binary roundtrip, not unvalidated SDDL templates.
Plan is NOT applied/enrolled/approved, no command executor or apply/start route.

INativeObjectObserver.Read(AbsoluteWindowsPath)->NativeObjectObservation. Finite
ReadbackStatus OBSERVED/MISSING/READ_DENIED/REPARSE_OR_IDENTITY_MISMATCH/UNAVAILABLE;
only OBSERVED has owner:SidValue, descriptor:SDDL, descriptorSha256:Sha256Value,
volumeSerial:uint and fileId:ulong (all required); failures have none. ReadbackReport
contains exactly code-root/data-root/executable observations and source-only scope.
WindowsReadback uses explicit read-only safe handles, no reparse final/ancestor;
GetSecurityInfo/GetFileInformationByHandle/GetFinalPathNameByHandle compare actual
handle/path identity. Missing/denied/native failure returns finite non-success,
no raw exception/path leakage beyond the explicitly declared tool manifest/observation.
Never claim observation alone proves policy isolation, enrolled source or qualification.

Program entry supports exactly plan, inspect, self-test. plan/inspect consume one
bounded JSON manifest on stdin. Plan parses first and never constructs observer;
inspect validates before observer construction and reads ONLY those3 declared targets.
Unknown args/invalid manifest exit64 with stable reason, zero observer construction;
plan emits source-only JSON exit0, inspect exit0 only allOBSERVED else2 with explicit
statuses. self-test runs finite pure constructor/JSON/descriptor tests, no OS mutation.
No service/Host execution mode. B-native getter fixture tests may invoke the observer
directly against fixture-owned file/directory; this is not a Host qualification.

Strong-type construction first in SAME slice: add project/config/values/plan/CLI/
SelfTests plus observer interface/UNAVAILABLE initial implementation; compile and
construct/roundtrip every public success/failure/enum before native getters. An
immutable constructor cut gets different-seat type preflight; only then implement
getters and Python executable fixture. No constructor-cut integration/new budget.
Final tests must prove real getter success, not leave an all-UNAVAILABLE stub green.

### Closure N1–N5 / acceptance and build truth

N1 all public ordinary constructors/finite enum/JSON roundtrips plus each rejection
class; distinct valid SID/path/digest/version fixtures, no bypass/cast/dynamic/Any.
N2 parse generated descriptor binary and assert exact owner, protected flag, every
principal/mask/inheritance ACE, no extra grants; generic-write/create-instance mutation
must turn the named pipe-rights cell red then exact restore green.
N3 real getter observes owned Windows file/directory identity and descriptor; missing,
reparse, denied/native fault cases refuse (injected native port for failures when
actual fixture privileges cannot create them). Mark injected vs real precisely.
N4 actual candidate executable plan/inspect/self-test/unknown-arg paths, constructor
factory counter proves invalid/plan cause zero native read; one shared build fixture.
Independent reviewer mutates a DIFFERENT door (extra ACE/owner/path component or
missing identity check) and reads unreduced red output, restores exact blobs/green.
N5 exact nine-CREATE boundary; build nullable/warnings-as-errors, no NuGet packages/
feeds/telemetry/workload downloads or persistent build servers; Python wrapper strict
mypy and in-memory compile. Source/binary/config/SDK/runtime hashes recorded, source
fixture success is not an install-ready service or qualified observer/Host.

Build SDK10.0.302 pinned by global.json (rollForward=disable); net10.0-windows,
OutputTypeExe, Nullable enable, TreatWarningsAsErrors, deterministic fixed PathMap,
explicit compile items only. NuGet.Config clears sources; no PackageReference.
Compile with explicit temporary CLI HOME/cache/obj/bin and DOTNET_CLI_TELEMETRY_OPTOUT=1,
DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1, DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE=true,
UseSharedCompilation=false, nodeReuse=false, maxcpucount1, --disable-build-servers.
Explicit offline restore then build --no-restore, no implicit dotnet run/new/publish.
Existing process runner cannot hide output or select ambient credentials/providers.
Final command: py -3.11 -m pytest tests/test_native_authority_tools.py -q -p no:cacheprovider;
strict: py -3.11 -m mypy --strict tests/test_native_authority_tools.py; plus project
build/self-test through fixture, in-memory compile, diff/scope/blob readback. Each
subprocess <=55s and each outer command<=60s; no automatic rerun on timeout.
Growth signals each C# production file<=300 effective lines, SelfTests<=350, Python
wrapper<=180; crossing prompts responsibility review, not compression/new files.
TEST->A->B N/A new native tool, no prior behavior moved/retired. XSS/UI/DB/deploy N/A.

### Historical N1 boundary (completed source held; active N2 boundary below)

```text
modify = AGENTS.md
create = library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj
create = library/local_orchestration/native_windows/global.json
create = library/local_orchestration/native_windows/NuGet.Config
create = library/local_orchestration/native_windows/NativeManifest.cs
create = library/local_orchestration/native_windows/ProtectionPlan.cs
create = library/local_orchestration/native_windows/WindowsReadback.cs
create = library/local_orchestration/native_windows/Program.cs
create = library/local_orchestration/native_windows/SelfTests.cs
create = tests/test_native_authority_tools.py
forbid = AGENTS.md
forbid = CONTEXT.md
forbid = Workflow.md
forbid = CodeReview.md
forbid = skills/
forbid = template/
forbid = modules/
forbid = doc/
forbid = library/workflow_router/
forbid = library/local_orchestration/grant_authority/
forbid = library/local_orchestration/mainline_readback.py
```

Effective MODIFY/DELETE none via reviewed denied sentinel, as30A/30G. Cumulative
diff always compares to final docs baseline, not constructor cut. Native setup/observer/
first Host entry remain subsequent bounded source work; stage immutable engineering
candidates under the approved minimal-first-entry exception, not final qualification.
N1 author132.77/135 and reviewer94.523/100 remain charged; final4-test peer suite and
independent getter source-red/restored-green passed. Real symlink creation1314 was
unavailable; reparse/denied/native-fault negatives are explicitly injected, not OS
qualification. Worktrees and registered build roots carry QUALIFIED_REVIEW_HOLD
through full qualified review/evidence seal; no TTL-triggered deletion. Original
Recovery states are unchanged. Exact commands/raw output/hashes are in original review.
Only actual externally approved OS setup/observation and final CVQ may unblock30G/
30B/43. Return ImplementationReturn + candidate/files/checks/mutations/time/deviations;
no prompt/Owner narrative/ticket body inside source. Initial and first11.72s
correction remain history. One additional bounded correction addresses only the
reviewed implicit-restore sequence and self-test native/Temp side effect: explicit
offline restore then build --no-restore; self-test remains pure and real getter
assertions move to the existing Python fixture using installed PowerShell7.6.5
Add-Type on the actual candidate DLL/public observer, as independently exercised.
No new CLI mode or source path; no additional behavior/AC. Current author135/
reviewer100 caps require independent document review before resumed work. Final
source0a2e0661 passed the peer's actual4-test suite; its different getter-success
mutation produced GETTER_STATUS=MISSING/exit1 and source was byte-restored. Only
post-restore rebuild/green/final identity is newly allowed; mutated build output
is not a candidate artifact. No source repair/new mutation/Host effect allowed. No helper
delegation, push/release/deploy/old cleanup retry or unrecorded extra attempt.

## 30N2 — Bounded native job primitive / exact local source Grant

Current engineering evidence at 1e6847c94dbef84dc17dacaafcc008c6d8ce5379:
SOURCE_ENGINEERING_OBSERVED_FIXTURE_PASS / QUALIFIED_AUDIT_BLOCKED / NOT_INTEGRATED.
Root actual same-candidate build/predicate mutations/native closed fixture and
different-seat evidence-sufficiency review are sealed in the existing Ticket30
review. Historical J3 intermittent cause remains UNKNOWN; current counter-oracle
correction is not retroactive RCA. No real Host/issuer/install qualification.
The following original Grant/history remains intact, not renewed or reset.

Same original Ticket30/PRD/CHG/SPEC and first-entry source-staging exception.
This is the Windows primitive portion of the existing controlled-executor/observer
responsibility, not another Runner, authorization engine or Host qualification.
It may proceed only after N1 engineering acceptance and an explicit Root-derived
child Grant with the final exact source/contract versions. N1 immutable evidence
and qualified-audit hold remain. The exact Grant below activates after independent
document consistency PASS, not after any presumed Host qualification.

Current resource admission HOLD: after actual N1, author350-161-132.77=56.23;
retain old30G correction30, leaving26.23, below this slice's planned45 envelope.
Reviewer220-84-94.523=41.477 fits32. Do not underfund/retry this native slice just
to continue, release historical reservations silently, or pretend the overall
1500 ceiling was hit. This is a role-envelope allocation constraint; Root continues
other lawful evidence/source preparation. No additional Parent cost is authorized.

The paragraph above is historical admission arithmetic, superseded by the effective
local batch amendment. N2 is no longer blocked by cumulative resources or correction
count; only its exact ordinary engineering preflight/child-Grant binding remains.
Later proposals to add500 or renew B3 attempts likewise remain historical, not pending
Owner questions. They must not be used to reinstate a removed ceiling.

Subsequent bounded CVQ preparation at75d165b5e3b9e4e26b8b36af240d218b06447f4f:
strict21 passes, but ordinary independent review/root actual-package reproduction
finds retained F01 schema-callee identity bypass. B3 remains CHANGES_REQUESTED and
qualified-audit-blocked; no source/candidate integration. Peer staging costs4.884,
so cumulative reviewer183.407/220; no refund of prior work. Root's remaining75 is
conservatively held in full for preparation/review/evidence closeout, not asserted
as measured actual use; earlier UNRECONCILED/reserve200 remains. All350/220/330 caps
still apply. A renewed B3 author attempt is proposed, not automatically granted over
its explicit consumed attempt limit. The consolidated source-only budget/attempt
decision and four closed slices are in the existing runbook section1 below its
redistribution history. No security-setting/Host consent is requested before the
actual payload and protected observer are built and independently reviewed.

Purpose: prove a job is configured and independently read back by the parent
BEFORE an owned fixture process resumes, then enforce child-process/time/memory
bounds and terminate/observe that exact job. Merely compiling an interop declaration
or returning all refusals cannot satisfy this slice. It is NOT source isolation,
AppContainer/network protection, a service, protected Grant enrollment or any
native Codex/Claude session. No real Host executable may be selected or launched.

Exact CREATE (Grant revision02 below adds only the two responsibility boundaries):
- library/local_orchestration/native_windows/NativeJobInterop.cs
- library/local_orchestration/native_windows/NativeJobGuard.cs
- library/local_orchestration/native_windows/NativeJobSelfTests.cs
- library/local_orchestration/native_windows/NativeJobContracts.cs
- library/local_orchestration/native_windows/WindowsJobPort.cs

Exact proposed MODIFY (only after N1's reviewed source is staged and precisely bound):
- library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj
- library/local_orchestration/native_windows/Program.cs
- tests/test_native_authority_tools.py

No DELETE/other paths. Keep existing N1 manifest/plan/getter/self-test code unchanged.
Reuse its compiler fixture, SDK/config, output/evidence handling and candidate hash
checks; no new Python process runner, duplicate compiler fixture or new framework.
Program adds only job-self-test plus closed fixture modes, not run/exec/service or
arbitrary argv/path/commands. NativeJobInterop owns safe handles/Win32 marshalling;
NativeJobContracts owns immutable values/status/port declarations; WindowsJobPort
owns only the existing port's concrete Win32 calls, not sequencing decisions;
NativeJobGuard owns one bounded job's fixed lifecycle; NativeJobSelfTests owns
parameterized constructor/fault/native-fixture assertions. No prompt/ticket prose
in code. Production300/test350 effective-line signals trigger responsibility review,
not compression or further file creation. Strict nullable/warnings-as-errors persists.

Architecture: ordinary validating named bounds/result/status types first, then
native behavior after different-seat construction preflight, within the SAME
slice/budget. ActiveProcessLimit is exactly1, kill-on-job-close is required, explicit
process/job memory and CPU-time limits are nonzero/bounded, and neither breakaway
flag may be enabled. Source-fixture memory ceiling512MiB, CPU ceiling5s, parent wall
deadline<=3s, no retries. Read QueryInformationJobObject and compare every required
flag/value before the first CreateProcessW call; no admission from caller booleans.
Create only the current built tool in a closed fixture mode, with CREATE_SUSPENDED,
no inherited handles, explicit application name and a finite environment. Assign
the exact process handle to the configured job, query membership and identity,
then resume. Any earlier failure resumes zero threads. Hold exact handles through
exit/timeout/cancel; no PID-only termination, shell, system kill or recursive cleanup.
Failure to terminate/read back is RECOVERY_REQUIRED with retained handles/evidence,
never success. Query readback failure is not a default-limit PASS.

Return typed immutable SOURCE_ONLY_UNQUALIFIED observations: exact candidate image
identity/hash, process creation identity, configured/read-back job limits, finite
completion/timeout/cancel/native-failure result and confirmed residual state. An
observed owned fixture process is NOT an independently protected review subject.
Do not claim this primitive alone prevents in-process tools, agent RPC, network,
snapshot writes or DLL/config substitution. Those remain separate existing CVQ
requirements and require the later protected enrollment and actual Host campaign.

Closure J1: every bounds/result/status constructor and rejected unknown/native
state; record zero create/resume calls for invalid bounds/readback failure.
J2: actual owned candidate fixture completes inside the job, parent independently
queries limits/membership/image; no ambient executable or arbitrary process target.
J3: actual child fixture attempts to launch the same fixed tool, is denied by the
OS and reports the finite denied result. This is a fixture child, NOT a Host attack.
J4: actual sleep fixture timeout/cancel is terminated through its exact job; query
confirms zero active processes. Inject create/assign/readback/terminate failures
through a typed native port where real failures are not safely reproducible; label
injected vs actual. Preserve recovery evidence, never kill unrelated processes.
J5: author changes active-process limit1->2 or disables kill-on-close, gets a named
red, exact restore/green. Reviewer uses a different door (skip readback equality,
allow resume before assignment or turn termination failure into success), gets a
named red, exact restore/green. Preserve unreduced outputs and candidate hashes.
Existing N1 executable cases remain green through its shared Python fixture;
strict mypy/in-memory compile and cumulative Git scope also required.

Historical45/32/22 planning is not an active cumulative ceiling under the effective
Owner amendment. Continue elapsed/resource accounting and preserve all old entries.
Each command initially<=60s, child<=55s, one foreground process per seat; diagnose
and record workload before any per-command adjustment. No identical failure retry
without new evidence. Root does not implement source or treat staging as integration.

### Exact N2 direct-lane Grant and construction ordering

Parent `batch-checklist-local-20261019-uncapped`, source policy reviewed at85028a76,
authority recorda75d9992 and independent consistency PASS by
`/root/batch_authority_review`; original N1 engineering candidate and immutable
source baseline `0a2e0661eef741be1b9df103ae8874c284cf60f8`, tree
`9774ca07aad0048d9d9a092ab73f4206c88a421e`. No final qualification is inferred.

```yaml
grant_id: grant-ticket30n2-native-job-20261019
grant_revision: 2
parent_authority: batch-checklist-local-20261019-uncapped
ticket: wg-ticket-30
slice: 30N2
stage: IMPLEMENT
baseline: 0a2e0661eef741be1b9df103ae8874c284cf60f8
reviewed_constructor_baseline: eeb2eaaa370fe9f42078cbf15228476b6d1f0ca8
implementation_owner: /root/ticket30n2_native_impl
reviewer_orchestrator: /root
independent_evidence_peer: /root/ticket30_native_tools_review
worktree: .worktrees/skill-improvement-30n2-native
branch: codex/skill-improvement-30n2-native
context_view: ctx-ticket30n2-native-job-20261019
profile: HIGH_ASSURANCE_SOURCE_ENGINEERING_ONLY
implementation_profile: implementation-standard
review_profile: ticket-review
construct_before_behavior: true
correction_policy: EVIDENCE_PROGRESS_REQUIRED
cumulative_command_limit_policy: OWNER_REMOVED_FOR_LOCAL_BATCH
```

The eight exact CREATE/MODIFY paths above are the full source allowance. The single
machine boundary below replaces only the retired N1 construction boundary; it does
not retroactively change N1's accepted bytes or grant effect authority. Root allocated
this contained, non-reparse linked worktree clean at0a2e0661 and verified common Git
identity. Ownership is disjoint from retained B3's gate/driver; separate implementation
seats may work in parallel, one ticket/view each, no delegation by implementers.

Historical Phase A constructed internal named immutable bounds/result/status and
a narrow typed native port in its original three new files and passed at eeb2eaaa.
Grant revision02 moves those same values/port into NativeJobContracts.cs without
semantic change; only Phase B adds the concrete WindowsJobPort.cs implementation.
Explicit interop declarations in Phase A invoked no native operation. Reuse the
existing build fixture and retain the pure
job-contract-self-test mode, validate all ordinary constructors/finite failures,
zero create/resume calls for invalid bounds and strict compile. No process creation,
job setup, filesystem observation or other native behavior before different-seat
constructor preflight pins Phase A's actual commit. No new public product API or
constructor bypass; marshalling structs remain at the interop boundary.

After that existing type preflight, Phase B uses the SAME Grant/view and its
revision02 eight-path responsibility boundary to add
the J1–J5 behavior. Program's only new native commands are job-self-test and closed
owned-fixture modes (complete, child-denial attempt, sleep); never arbitrary run/
exec/argv/path or a real Host binary. Select the current candidate apphost explicitly;
when invoked as dotnet or an unexpected image refuse rather than spawning an ambient
executable. Record apphost AND loaded assembly digests; a generic apphost hash alone
cannot bind behavior. Use hidden/no-window own fixture, no inherited handles,
explicit finite environment. On pre-assignment failure terminate only the exact
owned suspended process handle; never resume it or kill by PID/name. Failed teardown
retains RECOVERY_REQUIRED evidence/ownership and blocks further fixture operations.
Job-create/limit-readback/assignment/resume sequencing must be independently testable.

Catalog reuse check: workflow-control only advertises workflow-router-poc, a transition/
metadata module, not a Win32 executor. Existing executor_routing is pure model selection;
host_lifecycle is recorded Host lifecycle/registration. Neither supplies a native job
primitive. Reuse N1's SDK/manifest/safe-handle conventions and single Python build fixture;
add only the missing Win32 shim, not a replacement Runner or Host framework. Existing
N1 cases remain test consumers. No duplicate fixture/compiler/cache setup or dependency.

Author and distinct reviewer use real owned fixture positives and policy-denial/
timeout/cancel assertions plus separately labelled injected failures, then different
source-door reverse red/restored green. Source engineering is staged only, never
APPROVED_SOURCE, qualified isolation or permission to unblock30G/30B/43. Return exact
candidate, full source diff, commands/raw results/mutations/start-to-terminal time,
native-vs-injected coverage, deviations and recovery/asset holds. No silent all-reject
pass, cleanup retry, source integration, push/release/deployment or persistent OS effect.

### Grant revision02 — necessary responsibility separation, not another capability

Root reviewed actual PhaseA eeb2eaaa at control dafb5391. The original Guard file
is405lines of values/port declarations plus a7line bounds holder, not an implemented
lifecycle. Adding the OS adapter and recovery state machine there would combine
three different responsibilities. Under the same batch authority, permit exactly
NativeJobContracts.cs (move existing immutable values/INativeJobPort, value-only,
estimated430–470lines) and WindowsJobPort.cs (existing port's Win32 implementation,
estimated260–320). Guard becomes sequencing/recovery only, estimated280–350;
Interop remains ABI/safehandles, SelfTests existing shared assertions/fixtures.
No new interface system, Runner, package, arbitrary executable or permission.
The line counts are review signals, not ceilings or pressure to compress; an actual
500+ file must receive explicit responsibility review before acceptance.

This is not a source rewrite by Root: same implementation owner performs the moves
after a different-seat document consistency PASS on this exact amendment. Its
reviewed constructors must keep their semantics and ordinary constructor checks;
do not restart preflight, historical accounting or TDD simply because a type moves.
Final source review independently checks the resulting dependency direction and
the same J1–J5 behavior, with original N1 cases retained. No actual Host qualification
or formal integration follows from adding these exact missing source boundaries.

```johnny-boundary
modify = library/local_orchestration/native_windows/JohnnyAuthority.Tools.csproj
modify = library/local_orchestration/native_windows/Program.cs
modify = tests/test_native_authority_tools.py
create = library/local_orchestration/native_windows/NativeJobInterop.cs
create = library/local_orchestration/native_windows/NativeJobGuard.cs
create = library/local_orchestration/native_windows/NativeJobSelfTests.cs
create = library/local_orchestration/native_windows/NativeJobContracts.cs
create = library/local_orchestration/native_windows/WindowsJobPort.cs
forbid = AGENTS.md
forbid = CONTEXT.md
forbid = Workflow.md
forbid = CodeReview.md
forbid = skills/
forbid = template/
forbid = modules/
forbid = doc/
forbid = library/workflow_router/
forbid = library/local_orchestration/grant_authority/
forbid = library/local_orchestration/mainline_readback.py
forbid = library/local_orchestration/native_windows/NativeManifest.cs
forbid = library/local_orchestration/native_windows/ProtectionPlan.cs
forbid = library/local_orchestration/native_windows/WindowsReadback.cs
forbid = library/local_orchestration/native_windows/SelfTests.cs
```

ACTION_COMPLETED / N2_EXACT_LOCAL_GRANT_BOUND -> AUTO_CONTINUE / TYPE_CONSTRUCTION,
then ordinary independent preflight -> same-owner native behavior -> independent
engineering review. No new Stage/Gate or resource-renewal question is introduced.

All fixture assets have Ticket30N2/seat owner, exact fixture identities, TTL through
review/evidence seal and normal exact teardown; failed teardown creates a hold.
No old worktree/ref/journal/denied-cleanup operation may be retried or substituted.
No service/account/ACL/AppContainer profile/firewall change, native Codex/Claude/
model/provider/network/pipe call, runtime Grant operation or production gate is
authorized. N1's SDK/no-package/no-download/no-build-server restrictions persist.

Native primitive sources (not claims of tested qualification):
https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information
https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information
https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-setinformationjobobject
https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-queryinformationjobobject

## 30G-SOURCE — Closure G1–G5 revision01 / historical construction, audit held

Owner2026-10-19 approved runbook revision02 first-entry CVQ order exception and
this exact source slice. Original PRD-20260805-009/CHG-20260805-009, SPEC workflow
governance03 blob a700cad60de40096770582b04915bf490fd66a19 and sealed CONTEXT04
blob06baa4dea5db1c3370086552c35a1d8f721ad47e remain. Also bind the reviewed adaptive
SPEC design blobffb5304ed0a53df5dbd0b7697e7e18cdfeb39c7c and original HostExternalEffectGateway
responsibility; this source code does NOT activate that gateway or requirement creation.
Runbook Owner-decision section is the exact new authority, not its historical proposed reply.

| Binding | Exact limitation |
| --- | --- |
| Source/control baseline | 5b3c50f0f39c03f2db15f8c14f26beb03507e945; final reviewed docs baseline and leaf blob read back in original review before dispatch; only authorized docs may change between them |
| Derived child Grant | grant-ticket30g-source-20261019, conditional on independent document review/preflight; same-lifetime development authority only, never a trusted runtime Grant record |
| Owner / independent reviewer | /root/ticket30g_source_impl, current implementation-standard gpt-6-luna/xhigh; /root/ticket30g_source_review, gpt-6-sol/high based on existing Owner mapping and successful current46 capability; Root orchestrates/integrates only, author has no helper/control tools |
| Worktrees / branches | .worktrees/skill-improvement-30g-source / codex/skill-improvement-30g-source; independent .worktrees/skill-improvement-30g-review / codex/skill-improvement-30g-review; Root binds clean Git/contained nonreparse identities before allocation |
| Profile | POC / HIGH_ASSURANCE because authorization lifecycle, despite source-only tests. Ordinary engineering preflight/review may stage exact immutable candidates; mandatory qualified isolated audit is still required before final approval/integration and is NOT supplied by an ordinary helper |
| Resource | Original599.2/600 retained; added900: author450 (A120, B300, correction30), reviewer300 (type preflight80, behavior/review/correction220), control150 including install-inventory helper<=35. <=60s EVERY command, serial bounded commands, zero automatic retries/load, initial+one correction for the whole closure. All failures/inspection/Git count. Report full command timing, not only stdout; async attempts require full start-to-terminal elapsed, not sum of poll waits |
| Control docs only | This leaf, feature README, original30 review, existing checklist/doc index/runbook; install detail is a section of the same runbook, not a new framework/installer script. Root does not edit the six source/test files |
| No effects | Test-owned disposable SQLite/file fixtures only; no actual service/ACL/account/pipe/socket/remote/credential/provider/Host/model session, native spawn by product/test, real source readback, admit_dispatch/receipt, Git writes by product, held candidate import/integration or old cleanup retry |
| Lifecycle | owner=30G/named seat; TTL=type/engineering review+sealed evidence; test tmp fixtures use context-managed teardown; worktree/ref/cache/artifacts retained under existing cleanup/Recovery holds, no alternate deletion. No screenshot/report output. Existing user/other-ticket assets untouched |

### Single observable result / source and trust separation

Durable local ledger and bounded readback client model the exact grant record,
single-winner claim, stable retry and strict peer/plan/frame comparison through
their actual public source seams. A valid local record succeeds at this SOURCE
seam; wrong/missing/replayed/ambiguous inputs refuse. Every success is explicitly
SOURCE_ONLY_UNQUALIFIED, not authenticated issuer/Host/30B-R1 evidence. Neither a
SQLite file nor a caller-created peer DTO/expected-plan supplies authorization.
The future independently protected service owns issuance, OS peer observation,
trusted clock, effect transport and protected evidence; none is built/launched here.

Reuse workflow-router-poc (READY card) metadata: ProjectId, RequirementId,
RevisionDigest, EvidenceDigest, OpaqueMetadataId, ProcessStage, ModelRole from
existing contracts and ProjectAuthorityContract from project_authority. No SQLite
Grant ledger was found in the scoped existing runtime; telemetry/install/wake
journals have different trust/lifecycles and are not promoted. Python sqlite3,
Pydantic2, hashlib/struct/json and existing unittest/TemporaryDirectory/parameterized
patterns suffice; no dependency/install/config edit. __init__ is explicit exports
only; contracts owns values/validation, ledger owns transactions, client owns wire
composition. Tests separate ledger versus protocol, share per-file fixture helpers.

### Exact public source contracts (ordinary constructors, no coercion)

Use frozen, extra-forbid, strict, revalidate-instances models; no Any/cast/bypass
success objects. New IDs reuse existing opaque type, not a second ID grammar.
Architecture fixes these signatures/meaning; private helper names remain engineering detail:

- GrantOperation: READ_MAINLINE | READ_REVIEW_SNAPSHOT only. GrantLifecycle:
  UNCONSUMED | CLAIMED | COMPLETE | RECOVERY_REQUIRED; not Router stages.
- GrantPlan: schema_revision Literal[1]; project_id; requirement_id and
  requirement_revision; ticket_ref and ticket_revision; stage; actor_role; operation;
  baseline_sha exact lowercase40 hex; authority ProjectAuthorityContract;
  not_before/expires_at strict nonnegative integer UTC seconds, expires_at>not_before.
  authority.project_id must equal project_id. Full declared authority/revision and
  all fields participate in digest; no transform/coercion of IDs/expected values.
- grant_plan_digest(plan)->EvidenceDigest: SHA256 of that validated plan's stable
  model_dump_json UTF8 bytes with sha256_ prefix; schema version pins serialization.
- GrantRecord: grant_ref, plan, lifecycle, correlation_ref optional, evidence_digest
  optional. UNCONSUMED: neither; CLAIMED: correlation only; COMPLETE/RECOVERY_REQUIRED:
  both required. evidence_digest identifies terminal execution evidence, not the plan.
  The ledger separately derives/stores/verifies the plan digest internally rather
  than trusting a caller-supplied plan hash; no additional public DTO field.
- LedgerResult: scope fixed SOURCE_ONLY_UNQUALIFIED; disposition ISSUED | CLAIMED_NEW |
  EXISTING | SETTLED | REFUSED; record only for first four, failure only REFUSED.
  Finite failures MISSING | BINDING_MISMATCH | NOT_YET_VALID | EXPIRED | REPLAY |
  CONFLICT | STORE_UNAVAILABLE | INVALID_RECORD. No path/SQL/exception text in results.
- SQLiteGrantLedger(database_path: Path): explicit test/controller-owned path, no
  default runtime/environment discovery. issue(grant_ref, plan), read(grant_ref),
  claim(grant_ref, expected_plan, correlation_ref, observed_at: int),
  settle(grant_ref, expected_plan, correlation_ref, terminal: GrantLifecycle,
  evidence_digest) each -> LedgerResult. issue records a SOURCE model only, not
  Owner approval. Identical issue returns EXISTING without resetting state;
  changed ID binding refuses. settle accepts only COMPLETE/RECOVERY_REQUIRED.
- AuthorityPeer: service_sid (bounded canonical S-1-... SID text), binary_digest,
  configuration_digest (existing EvidenceDigest), enrollment_ref opaque. This
  descriptive DTO is NOT OS proof. GrantReadRequest(grant_ref, operation_ref)
  contains only opaque IDs; operation_ref is the attempt/request correlation.
- PeerFrame(peer: AuthorityPeer, payload: bytes); AuthorityChannel Protocol
  exchange(request_frame: bytes)->PeerFrame. No concrete pipe/network implementation.
  GrantAuthorityClient(channel, expected_peer, expected_plan).read(request)->
  GrantReadResult, scope fixed SOURCE_ONLY_UNQUALIFIED, disposition VALIDATED_SOURCE_RECORD
  with record or REFUSED with finite CHANNEL_UNAVAILABLE | PEER_MISMATCH |
  FRAME_INVALID | BINDING_MISMATCH. No trust upgrade/integration authority.
- Request frame: 4-byte unsigned big-endian byte length + UTF8 JSON, schema_revision=1,
  grant_ref, operation_ref only. Response body same three keys plus record only.
  Body1..16384bytes, exact prefix/body match, no trailing/partial frames; duplicate/
  unknown/missing key, invalidUTF8/deep JSON, bool/coercion/unknown enum rejects.
  Compare exact peer, response IDs and whole expected plan before source success;
  no response/record raw body in log/error. TimeoutError/OSError become finite
  CHANNEL_UNAVAILABLE, no retry. Explicit encode_read_request and encode_read_response
  are value-only helpers, not issuers or self-authentication.

### Atomicity / failure / verification closure

G1 constructors: every public success/failure/enum/Protocol fake and JSON roundtrip,
wrong primitive/null/extra/enum/ID/time/state combination refused. New types do not
exist yet: reuse original Ticket30's type-first construction order, not a new Gate.
Phase A creates only __init__, contracts and constructor portion of protocol test;
no ledger/client behavior or fixture DB. Different-seat engineering type preflight
must pin actual candidate before Phase B. No early integration; cumulative six-CREATE
boundary always measured against the original source baseline, not the A commit.

G2 durable lifecycle: SQLite explicit transactions, parameterized SQL, finite timeout
(timeout=0/no automatic busy retry), durable commit before CLAIMED_NEW. One transaction
matches plan and validity then conditional UNCONSUMED->CLAIMED and correlation;
exactly one independent connection wins. Same correlation+plan returns stored in-progress/
terminal record without another claim/effect, even after reopening/crash simulation;
different correlation or any mismatched binding refuses. An expired retry may read an
existing same-correlation record, never CLAIMED_NEW. No auto-remint/unconsume/delete.
Settlement exact claim only; repeated identical terminal result EXISTING, conflicting
terminal/evidence/correlation refuses. Terminal evidence may differ from plan digest.
Malformed/corrupt records or stored plan-digest
inconsistency fail closed. A coordinated valid rewrite by a local same-user actor
is NOT detectable authority forgery here; only later protected storage can prevent it.
Source tests prove transaction/idempotency only, not filesystem protection, atomic
distributed effects, trusted time or a real service. No external effect callback API.

G3 protocol: exact permitted read succeeds through actual client and injected channel;
wrong peer fields, request/response ID, any plan binding, tampered record/digest state,
oversized/truncated/trailing/deep/duplicate-key frame and channel error refuse. No
caller-approved bool/path/ID unlocks real authority; test fake explicitly unqualified.
G4 truth: author reverse-mutes claim CAS/single-use and client peer/plan binding,
named tests red then exact restored green. Independent reviewer uses a different
door (reopen/retry/correlation or response/length/record binding), unreduced output;
zero red is finding. Existing599.2s and forgedGrant/140-case algorithm evidence
are reused, not rerun from/modify the held30B candidate.
G5 verification: python -m pytest tests/test_grant_authority_ledger.py tests/test_grant_authority_protocol.py -q -p no:cacheprovider;
python -m mypy --strict library/local_orchestration/grant_authority;
in-memory compile/import; public ledger/client fixture smoke and git diff --check.
One shared temp fixture per test lifecycle, two connections/threads max, no stress/
sleep/process launch; inherited environment must not select paid services.
Growth signals contracts<=220, ledger<=260, client<=180, tests<=350 each effective
lines; crossing requires responsibility review, never forced compression/file split.
Source has technical comments only, no Owner prompt/ticket narration. TEST→A→B=N/A
(new capability, not responsibility transfer); XSS/UI/SQL migration/deploy=N/A.

### Current cumulative machine boundary

Old30B fence below is historical text, no longer this active phase. Effective
MODIFY=none: existing parser requires a nonempty modify, so denied AGENTS sentinel
is the same reviewed30A encoding, not permission. Gate must prove all existing
MODIFY/DELETE refuse and only these six CREATE paths pass. Author may additively
edit these newly created files across A/B/correction; no existing baseline file.

```text
modify = AGENTS.md
create = library/local_orchestration/grant_authority/__init__.py
create = library/local_orchestration/grant_authority/contracts.py
create = library/local_orchestration/grant_authority/ledger.py
create = library/local_orchestration/grant_authority/client.py
create = tests/test_grant_authority_ledger.py
create = tests/test_grant_authority_protocol.py
forbid = AGENTS.md
forbid = CONTEXT.md
forbid = Workflow.md
forbid = CodeReview.md
forbid = doc/
forbid = modules/
forbid = skills/
forbid = template/
forbid = library/workflow_router/
forbid = library/local_orchestration/dispatch_authority.py
forbid = library/local_orchestration/mainline_readback.py
```

Return ImplementationReturn COMPLETED/BLOCKED/CHANGE_DETECTED, source phase,
candidate/baseline/files, checks/mutations, findings/deviations, cumulative exact
command time and unverified scope. Completed source/engineering preflight is not
final HIGH_ASSURANCE approval; stage immutable candidate until mandatory qualified
audit. This CVQ ordering exception does not exempt30G itself from its final audit,
does not integrate30B/43, and author cannot enable effects. Initial+one correction
limits and historical holds persist. ACTION_COMPLETED routes to the unique next
source action only when its preflight/budget is valid; no repeat Owner question.

### 30G immutable engineering handoff — 2026-10-19

Candidate20bd6e3036608d61feb687ea6e0ff6b7953d3e11, original source baseline
6f6c938cd3d6eeff9e07cdffddfcbfdcbdc08cd0; cumulative exactly six CREATE paths,
zero baseline MODIFY/DELETE. G1 accepted at5ddc263a after two narrow type findings;
G2–G5 different-seat engineering PASS by /root/ticket30g_source_review. Both seats
ran92 focused tests, strict mypy, compile/import; author public ledger/client smoke
passed. Author CAS mutation1red/restored1green, peer/plan13red/restored13green;
reviewer different-door stored-plan-digest mutation1red/restored1green. Original
review records exact commands, outputs, versions, limits and all earlier deviations.

Source-only legal records succeed, invalid bindings refuse; no caller DTO or local
SQLite file authenticates a protected issuer. No service/OS transport, real grant
enrollment, source read effect or Host qualification is established. Final mandatory
qualified isolated audit UNAVAILABLE/NOT_EXECUTED, so no final approval/integration.
Original599.2/600 and added900 allocation persist; author conservatively A51/B110,
reviewer A52/B32, correction30 unused. Source residue/worktrees retain existing
Review/Recovery holds; no denied cleanup retry, no normal whole-ticket closure.

## 30B-R1 fail-closed correction allocation — 2026-10-19

This bounded correction follows the Owner's latest explicit forged-Grant repair
instruction and `batch-checklist-local-20261018`; it is not a new PRD, authority
issuer, budget or final R1 acceptance. Prior attempts and R2 PASS remain intact.
The known `grant-forged` binding produced a candidate after ten fake transport
calls at `fd98f3958fa2d9ceca6d8a925efa27302c061df2`; retain that input as a
public-entry regression requiring rejection before transport construction.

Root's bounded source inventory found `dispatch_authority.read_dispatch_grant`
and its creator reading/writing `dispatch-authority.json`. The module explicitly
defines that file as an owner-intent marker, not a principal-separated issuer.
The existing project-authority observation reducer validates supplied readings,
not their authorization. Neither may be promoted to a trusted phase-Grant reader.
No qualified production issuer/readback composition was established in this
inventory. Consequently the public entry must return a named unavailable/missing
Grant failure with no candidate, factory, clock callback or network activity.
Nonempty IDs, a legitimate-looking old ID, ordinary JSON round-trips, caller
anchors and the owner-intent marker cannot enable it.

Reuse the existing readback coordinator as a private, explicitly unadmitted
algorithm-test seam, requiring injected transport/clock with no automatic live
transport fallback. Existing successful algorithm fixtures prove only parser,
snapshot and transport behavior, never Grant admission. Preserve their checks;
do not relabel them as successful public authority tests. Private Python symbols
are not a sandbox against malicious same-process code; no such claim is allowed.
Future public success requires independently qualified issuer/readback wiring
under the existing authority architecture and its original acceptance criteria.

| Allocation | Exact limitation |
| --- | --- |
| Derived Grant | `grant-ticket30b-r1-containment-20261019`, conditional on independent review of this committed allocation; parent is the existing batch authority |
| Control baseline | `71f418086f90ec6e4a71fc45297c231e19c9829d`; final allocation commit and leaf blob read back before dispatch |
| Source baseline | `fd98f3958fa2d9ceca6d8a925efa27302c061df2`; original cumulative baseline `930fad32e15a76cd54423e34ea941a630af039da` remains unchanged |
| Author / reviewer | Same semantic implementer role, replacement seat `/root/ticket30b_r1_impl` using the existing allocation's low-cost capability profile; original independent `/root/ticket30b_readback_review`. Root alone orchestrates; no author helper |
| Author workspace | Existing `.worktrees/skill-improvement-30b-readback`, branch `codex/skill-improvement-30b-readback`; preserve original candidate history |
| Allowed correction | Modify only the candidate's `library/local_orchestration/mainline_readback.py` and `tests/test_mainline_readback.py`; create/delete none. Original cumulative four-path boundary below remains unchanged |
| Root documents | This leaf, feature README, existing Ticket30 review and checklist only; no source edits by Root |
| Budget | Prior conservative 515/600 command seconds retained; remaining 85 seconds maximum, author 40 / independent review 35 / Root validation 10. No reset or automatic extension; no full unrelated suite reruns |
| Verification | First preserve the forged public call as red; then missing, forged and plausible-ID public calls reject with zero factory/clock effects. Keep algorithm fixture positives and SHA/digest negatives. Focused pytest, strict mypy, compile/import and diff checks; reviewer independently weakens the public rejection and observes the named regression fail, restores exact bytes and reruns |
| No effects | No real GET, target read, credential, external model API, receipt, dispatch, spawn by tested code, Host change, integration, push or release. Normal authorized development delegation remains allowed |
| Holds | Original source/Host positive qualification remains NOT VERIFIED; 30B and 43 remain unintegrated. Worktrees/candidate/evidence remain held; no cleanup retry or alternate deletion |

Document review is ordinary control-plane review, not the unavailable qualified
adversarial Host audit. Passing this correction closes the demonstrated public
candidate leak only; it cannot close full R1, Ticket30 or checklist01/02.

### Containment result (not production qualification)

Allocation `f8887d200111336d409538d7f739315a2224b87c` passed independent
document review, activating only the limited local correction Grant above.
Author candidate `0f6d467a2f4c1e39102c8fee334ac8bbdb70d4ac` adds the public
fail-closed result and preserves the original forged input as a regression.
43 focused tests, strict mypy, import and diff checks passed. Original independent
reviewer confirmed three public rejection cells; its injected-port bypass
mutation made both forged/plausible-ID cells fail, byte-exact restoration passed.
PASS_CONTAINMENT_ONLY; full source/Grant qualification remains NOT VERIFIED and
the mandatory isolated audit remains unavailable, so no integration or closure.
Budget conservatively charged at most599.2/600s including final Root reserve;
remaining budget is not authorization for another attempt. All raw evidence,
failed setup attempts, Host/tool inventory and exact rejected cleanup call are
in the existing Ticket30 review. No cleanup retry, push or Host change occurred.

### R1 positive acceptance — separately OPEN, 2026-10-19

Owner explicitly requires a legitimate Grant to succeed through trusted readback;
public reject-all containment does not satisfy R1. Keep `grant-forged` and the
0f6d467a regression unchanged. Success must bind a directly read protected issuer
record to the exact project/ticket/stage/actor/operation/baseline and validity
period, then read index and leaves at one fresh formal authority observation.
The issuer identity cannot originate from caller fields, fixture ports, an
ordinary repository file or the `dispatch-authority.json` owner-intent marker.
Wrong/forged/expired/replayed grants must still refuse before transport/effect.

Local adapter implementation is covered by the batch goal when that concrete
trusted source and contract are available; Root may narrow the original allowlist
and derive a same-lineage Grant without asking again for the batch authority.
No such qualified source was found in the scoped local_orchestration/workflow_router
inventory. Provisioning credentials, OS protection or an external issuer requires
its own external-effect authority; adding a caller-trusting resolver is not a fix.
Also retain599.2/600 command seconds: no implementation retry under a renamed
child or reset ledger. A future bounded attempt needs an explicit resource delta
or a verified accounting correction, not automatic fresh allocation.

Minimal Host restrictions, individual verification expectations and current gaps
are recorded once in `doc/AI-SKILL-IMPROVEMENT-CHECKLIST.md` revision30, section
“最小Host能力需求”. Existing raw failure/absence evidence stays in this ticket's
review. No new qualification attempt, cleanup retry, candidate edit or integration
is authorized by this status record. E02-style mandatory audit remains blocked;
independent content-only Ticket45 may proceed without borrowing this ticket's PASS.

## 30M 文件遷移授權紀錄 — 2026-10-18

Owner 本輪直接授權正式主線文件遷移、獨審、同票修正及受控本地整合，並準備
下一個無派工效應的真實來源讀回方案；不授權該 source/test 實作、push、release、
deployment、Host qualification 或正式結案。這是原 PRD／CHG／SPEC、原 Ticket30
的文件階段，不重用已消耗的 30A Grant，不另建 PRD／工作流程。

| 精確綁定 | 本輪文件階段 |
| --- | --- |
| Baseline | `d00018aa0117032ecba132e545a3085b29ec870a`；控制分支 `codex/skill-improvement-checklist` 讀回乾淨 |
| 作者／整合 owner | Root，Architecture Owner/control-plane；文件操作不是 production implementation owner override |
| Worktree／branch | repository-contained `.worktrees/skill-improvement-30m-docs`／`control/skill-improvement-30m-docs`；建立時 Git root／HEAD／非 reparse containment 已讀回 |
| 獨審 | 不同席位 `/root/ticket30m_docs_review`，只審本輪文件差異與既有 parser 相容性；Root 保留整合責任 |
| 精確 modify allowlist | `modules/tickets/workflow-governance/README.md`；`modules/tickets/workflow-governance/29-mainline-ticket-projection.md`；本 leaf；`doc/reviews/workflow-governance/30-trusted-independent-ticket-continuation-code-review.md`；`doc/AI-SKILL-IMPROVEMENT-CHECKLIST.md` |
| create／delete | 均無；其他 leaf 尚未證明必要成員／依賴者不寫入，不以 false/空陣列冒充已核准的 optional/無相依 |
| Forbidden | 所有程式／測試／模板／skill、sealed Context、PRD／CHG／SPEC 正文、其他票與 Recovery；無 target／正式派工／receipt／spawn 被測效應 |
| Profile／資源 | DOCS_ONLY；零 implementation lane，一個既有規則允許的唯讀盤點 helper、一位獨審。沿同票耗用，不加壓、不輪詢、不重跑 04；驗證命令各具 timeout，無付費服務 |
| Lifecycle | 此專用 worktree/ref owner=Root/Ticket30M，TTL=本輪文件審閱、整合、證據封存及獨立讀回後；僅精確身分且乾淨、已整合後 normal teardown，失敗保留 evidence／hold |
| Integration | 既有 `admit_control_plane_mutation`，control namespace、host principal、精確 baseline/diff、獨審與 journal；不直接 merge/push。它不是 Host 隔離的證明 |

有限驗收 30M-D1：批准來源→主線身分／目標／角色／成員／依賴逐一可追溯；不
修改歷史完成契約。30M-D2：唯一 machine fences、四類 binding、raw committed-byte
leaf digest、index/leaf 鏡像與既有純投影相容；非法 digest／版本／相依仍拒絕。
30M-D3：新鮮遠端唯讀查證與完整下一階段票面／Grant／推送決策包，不冒稱已
取得授權或 qualification。30M-D4：獨審、精確差異、本地 gate／readback／seal。
文件 schema 驗證沿用 30A 的純解析邏輯，不把真文件假裝 synthetic observation
送入 fixture-only public entry；不以文件通過勾選全票30或清單01／02。

`ACTION_COMPLETED → AUTO_CONTINUE → 30M_DOCS_MIGRATION` 只依本段既有授權
推進；下一 source/test Grant 候選維持未簽發。下一階段 baseline 綁本輪最終
受審本地版本，跨出本輪文件範圍的效果仍須各自授權。

## Owner 批准與當前 continuation

**本段30A為歷史已完成建置；現在的合法 continuation 是30M 文件遷移與30B票面
準備。下節候選不是已發出的實作或網路效果 Grant。**

Owner 2026-10-18 精確核准 `acf0ffa1780af3d229b7f80c6e063f6d642e6864` 與本票
舊 leaf blob `ded322b3c7e82399c31ff4cf67d3dbf3237af3fb`：Architecture Owner
沿原 `CHG-20260805-009` 依法 REVISE sealed Context revision 03，增列本專案
`johnnyliu365-sys/Johnny_AI_Skill`／`refs/heads/main`／`SINGLE_BRANCH`；原 SPEC
revision 03 寫定 fixture bootstrap 例外。兩者及本票經獨審後，條件式 30A Grant
可由控制面精確綁定執行；只有這些核准文件變更時不重問 Owner。

下列「候選／尚缺 Grant」段落保存當時的 source decision provenance；本節及
本票凍結的 30A-F1–F4 是當前限縮建置依據。正式 target source／Host effect 的
缺口仍有效。文件獨審後曾沿 `ACTION_COMPLETED → AUTO_CONTINUE → same-lifetime
30A IMPLEMENT / type-only Phase A` 推進；實際 constructor／獨審通過才續 parser。
目前 30A fixture 已完整驗收、整合及清理，返回 `ACTION_COMPLETED`；下一個
真 source／`admit_dispatch` effect 的程式變更與 qualification 不在這個兩檔 Grant，
不能以 fixture 完成自動啟用。實作 allocation 已釋放，不再使用本票已消耗的建置授權。

獨審 `35b25d60` 已關閉精確新型別 preflight 順序及 cumulative create 邊界兩項
文件 finding，確認五檔修訂在本次限定授權內。控制面依 Owner 條件式授權綁定
`grant-ticket30a-fixture-20261018`，只准上述具名 actor 及下列機械邊界；same-lifetime
bridge／receipt／descriptor 均 `NOT_REQUIRED`。這是 Owner Grant 的執行綁定，
不是 Agent 自行產生另一份授權來源。

```text
modify = AGENTS.md
create = library/local_orchestration/mainline_source.py
create = tests/test_mainline_source.py
forbid = CONTEXT.md
forbid = AGENTS.md
forbid = Workflow.md
forbid = CodeReview.md
forbid = doc/
forbid = modules/
forbid = skills/
forbid = template/
forbid = library/workflow_router/
forbid = library/local_orchestration/dispatch_authority.py
```

**機械編碼說明：有效 modify 集合仍為空。**既有 gate parser 強制要求非空
`modify`，故上面的 `AGENTS.md` 是同時被 `forbid = AGENTS.md` 無條件拒絕的
denied sentinel，絕不構成 AGENTS 修改權限。既有 evaluator 對所有 ChangeKind
先判大小寫不敏感的 forbid；任何 MODIFY 不是被 sentinel 的 forbid 拒絕，就是
未命中唯一 modify 而拒絕。Root 與獨審已用公開 parser/evaluator 證明兩個指定
CREATE 通過、全部 1,116 個既有 tracked path 的 MODIFY／DELETE 拒絕、未授權
CREATE 拒絕；這只使用既有規則，沒有修改 gate 或擴張允許檔案。Phase A 不先
整合；最終 Phase B 仍以原始 baseline 的 cumulative CREATE diff 整合。

| 派工綁定 | 核准範圍／待獨審後讀回 |
| --- | --- |
| Profile／角色 | `implementation-standard`：當下主機可用 `gpt-6-luna/xhigh`；不同席 `gpt-6-sol/high` 獨審，能力不低於實作者。這是本票 profile 資料，不寫入通用程式或 skill。以原 Profile 的語義角色及 Owner 已允許的現行模型對應；不變更全域 DAP/角色權限 |
| Baseline | 起點 `acf0ffa1780af3d229b7f80c6e063f6d642e6864`；最終文件受審後，控制面在本票既有 review 記錄完整 dispatch baseline SHA／ticket blob／worktree Git readback，確保至起點只改核准文件，再從該 baseline 建實作 worktree |
| Scope | 整張票相對原始派工 baseline 只 create 下文兩路徑，modify=none；Phase A→B 只可 additive 編輯本票剛建立的同兩檔，不能修改派工 baseline 已存在的任何檔案。Phase A SHA 是型別／行為建置依據，不重置 cumulative diff／權限 baseline；不得修改套件 exports、既有 projection／contracts／tests |
| TDD／型別 | 新功能不要求不存在程式的 ceremonial first-red。既有 observation/projection constructors 在派工前實跑。新公開型別不存在時，採下述同票受限 type-bootstrap Phase A；實際 constructor／negative／round-trip 與獨審通過前，不派 Phase B parser/source-read 行為。prototype 不作候選成功證據 |
| Resource／lifecycle | 一位實作者、零 helper、一位獨審；沿同票既有耗用與 finding，不重置預算。Git fixture 每命令 timeout 20s、本機驗證每命令有限 timeout；不平行加壓、不輪詢、不呼叫付費 API。fixture 由 pytest temp fixture 記 owner/test ID、session TTL、teardown；專用 worktree/ref 保留至 Review／證據封存／本地整合後才依精確身分受限移除 |
| XSS／UI／refactor | 無 render sink／正式 UI，XSS N/A；新增來源 assembly，未搬既有責任，TEST→A→B N/A；沿用投影，不能把腳本增加回報成產品拆分 |

公開 seam 凍結為 `RawGitBlobReadResult`（FOUND+bytes 或非 FOUND+None）、
`MainlineSourcePort.read_blob(observation: GitObservation, artifact_ref: TargetRelativePath)`、
`MainlineSourceRequest`（project_id、feature、synthetic observation）、
`MainlineSourceResult`（fixture-only scope、projection 或 finite failure 二擇一）、
`project_committed_mainline(request, port)`。`TargetRelativePath` 是本模組的具名
canonical relative-path value：不得 absolute、反斜線、空／`.`／`..` segment、
control 或非正規分隔；leaf 另外限同 feature 直接 `.md`。request 限 synthetic
`WORKTREE_HEAD` observation，拒絕 tracking／direct-remote 種類；它不是 authority
admission。內部 wire DTO 由實作者在本責任模組選最少集合，extra/duplicate/missing
皆拒絕，JSON 動態輸入只在 boundary 驗證，不能帶 Any／未驗證 dict 向內。
結果固定 `FIXTURE_ONLY`，不承載 raw source；未新增 authority engine。

30A 完成證據：原獨審席已核准修正 `629030f4678b5d600c9ad53baf60967c25ecefbc`，
四項 finding 全關閉。最終僅合併已審 Root docs carrier 的候選
`b7e9e2f35bd997c65df80541ec0196a000ab3e46` 經既有 mutation gate 回
`INTEGRATED`。整合後同一 Python process 先確認實際 import 位於控制 worktree，
source/test Git blob 精確相等，再跑完整 focused suite：91 passed；strict mypy、
compile 通過。這項實際載入讀回只覆蓋本次 fixture run，不是通用 Host qualification。
完整命令／版本／獨審突變／journal seal 與 cleanup 見既有 Ticket 30 review leaf。
不把 fixture 成功提升成真 authority／Host／dispatch／formal closure 證據。

### 同一 Grant 的有限型別建構順序

Architecture Owner 在同兩個 create 路徑內，將新能力的建置按必要先後分成兩個 cut，
不新增 Stage、Agent、Ticket、成本權限或驗收。Phase A 是只限本票新型別的精確
pre-dispatch construction bootstrap：允許具名實作者先建立真實 DTO／enum／Protocol／
path validator 與純 constructor 測試，除此不得實作或呼叫 parser、source port、
Git、Router、Host 或 native spawn。既有依賴 constructors 仍須 Phase A 派工前通過。
Phase A 以真實 module 的普通 constructor、錯 primitive／null／enum／payload 組合、
round-trip、strict checker 及獨審作為關卡；結果 pin 實際 SHA，禁止文件／in-memory
probe 替代。通過後以該受審 commit 為 Phase B source baseline，同一 owner／Grant／
worktree／剩餘額度接續 parser。獨審席位沿用到最終 30A-F1–F4，不重置 finding。
這個建構排序僅使已授權的新型別得以存在，沒有放寬型別驗證或任何真效應前提。
原始派工 source baseline `d2f2aa10` 始終證明：實作者對 source/test 的累積差異只
能是兩個 `CREATE`，不能用 Phase A 重置權限。Owner 另行核准的 Root 文件操作
有獨立作者／commit，並非實作者 modify 權限；例如 Closure02 的 `bacab24d` 只
改本票與既有 review leaf，control plane 獨審後才成為新的可信文件 carrier。
既有機械 gate 從**目前可信 control integration branch** 讀 boundary，以該分支與
candidate 的 Git merge-base 比對實際 diff；實作者正常合併精確 Root docs carrier
後，該整合 diff 仍只能有兩個 `CREATE`。准入須同時證明 carrier 相對原 source
baseline 沒有 source/test 變更，以及實際 integration diff 正好兩個新增檔；不能
用 caller 路徑過濾或未審 docs 來排除變更。Phase A 不先整合，任何既有 source/test
修改仍拒絕；這只是本次 Owner 明確核准的文件 baseline 續綁，不是新權限。

## 30B 精確候選 — 真實來源讀回，不產生派工效應

### 本批委任下的精確子票綁定

原建置及首輪複驗的歷史結果（最新限縮修正見上節）：原Grant已完成兩階段建置及一次有界修正；當時候選
`fd98f3958fa2d9ceca6d8a925efa27302c061df2`，原獨審者確認R2完整SHA缺陷閉合、
140聚焦tests通過。R1真實control／Grant來源讀回仍UNVERIFIED，必要合格隔離
audit為UNAVAILABLE，故REVIEW_BLOCKED、禁止整合。515/600s為保守累計command
估算，不重置、不把本次票面狀態更新作為新派工Grant。精確批准baseline930fad32／
leaf fb189f91及全部驗證在原review保留；下列為已消耗建置授權，不是新的執行次數。

本節取代下方歷史候選的「待Owner逐票核發」與固定30M baseline描述，其餘30B-R1～R4
及四路徑契約不變。授權來源 `batch-checklist-local-20261018`，見既有
`doc/AI-SKILL-IMPROVEMENT-CHECKLIST.md` revision27「本批授權」。Root 依 Owner
明確委任核發 `grant-ticket30b-readback-20261018`，狀態
`ISSUED_CONDITIONAL_ON_DOCUMENT_REVIEW / LOCAL_BUILD_ONLY`；文件獨審通過後自動
接續，不再要求 Owner 重複批准。30A Grant 已消耗，不重用。

- Source baseline：`8c9be91650d3cfb59d53c24b55b9a65fb72118b3`；本次 control baseline
  `2e52772770e81669a7e1f92391a432572d4ead4b`，中間僅既有 review ledger。
  實作起點為本節及必要 registry digest 寫定、獨審後的完整文件 commit；Root 在
  review leaf 記精確 SHA／ticket blob、核對與 source baseline 的程式 blobs 相同。
- Owner `/root/ticket30b_readback_impl`，能力由本次可用工具目錄與前次同類30A已驗
  能力比對：`gpt-6-luna`／`xhigh`；獨審 `/root/ticket30b_readback_review`，
  `gpt-6-sol`／`high`；Root 唯一 orchestrator／整合者。模型值僅本次分配資料。
- 原定 worktree／branch、四路徑、HIGH_ASSURANCE、600s累計／120s單命令及
  existing-type preflight、新型別先建構再獨審的順序沿用。命令紀錄保留實際耗時，
  修正不重置。原 initial＋一次correction耗盡時，由Root在本批內收斂但不加額度。
- Network=0；本地假 transport 測試及實作標準庫受限transport均可，禁止實際外部
  GET、paid API、credential、正式派工／Host啟用。正式來源正向證據保持未完成。
- `nohelper` 僅指實作者不得派helper。HIGH_ASSURANCE 仍須 reviewer-owned
  `AdversarialReviewPlan`：pin最終candidate／30B-R1～R4，檢查AUTHORIZATION、
  BOUNDARY_DATA、CONSISTENCY、ERROR_PARTIAL_FAILURE及REGRESSION，effect_scope
  為NO_EXTERNAL_EFFECT。不同席獨審不自動代替此audit；隔離必須有資格證據。
  若僅有READ_ONLY_INTENT_ONLY或UNAVAILABLE，記REVIEW_BLOCKED，不能整合或
  勾選；其餘已准入本地建置可繼續。沿既有CVQ來源確認，不新建隔離框架。
- Asset owner=本票具名作者／獨審；TTL=本批本票審閱與證據封存後；只清精確登記
  的乾淨且已整合worktree/ref，失敗或Recovery hold保留，不改其他資產。

原30B歷史機械邊界（現行30G只使用上節唯一active fence）：

```text
modify = library/local_orchestration/mainline_source.py
modify = tests/test_mainline_source.py
create = library/local_orchestration/mainline_readback.py
create = tests/test_mainline_readback.py
forbid = AGENTS.md
forbid = CONTEXT.md
forbid = Workflow.md
forbid = CodeReview.md
forbid = doc/
forbid = modules/
forbid = skills/
forbid = template/
forbid = library/workflow_router/
forbid = library/local_orchestration/dispatch_authority.py
```

Root 文件 modify allowlist：本leaf、同feature README、既有本票review及既有
checklist。獨審驗此差異、授權來源、唯一boundary與rawdigest鏡像；此步不改SPEC
或Context已封存版本，不創造新Host能力。`ACTION_COMPLETED → AUTO_CONTINUE`
進入同生命週期type-only實作，實際constructor獨審後才續行為，最後按原gate整合。

### 歷史候選（本批限定覆蓋以上段為準）

狀態 `PREPARED / GRANT_NOT_ISSUED / NO_RUNTIME_ACTIVATION`。原需求與 SPEC
AC9、同 Ticket30 lineage 不變；30A 已完成，不重做。30M 文件經獨審、本地
gate整合後，由該精確已讀回版本作 source baseline。原 source/test Grant 只准
兩個 CREATE，已消耗；本段四路徑修改／新增及新網路讀取不能借用它。

### 目的、角色、邊界與重用

把已審的 raw-byte parser 接到**受限唯讀**的正式來源讀回，輸出只可為 metadata
candidate 或具名拒絕；不接 `admit_dispatch`、receipt、Runner、spawn 或正式
結案。程式不凍結 Johnny 專屬 repo／SHA／票號／模型；專案的精確值只來自
受審的 control-plane 授權綁定。Authority 不是 caller 的 repository/authority_ref
參數、自報 `approved=true`、工作目錄、origin cache 或遠端 HEAD。

| 項目 | 精確票面候選 |
| --- | --- |
| Source baseline／leaf | 30M 最終 gate/readback SHA、Ticket30 blob、README blob、兩個 leaf raw digest 在既有 review 的 final decision seal 一次填定；候選不得用未提交或移動 HEAD 啟動 |
| Control／implementation／independent review | Root reviewer-orchestrator；預定 `/root/ticket30b_readback_impl`；不同席 `/root/ticket30b_readback_review`。派發前按當下有效 Profile 綁可用能力，沿用 least-cost implementation／reviewer不低於作者，不以模型名稱取得 authority |
| Worktree／branch | 預定 `.worktrees/skill-improvement-30b-readback`／`codex/skill-improvement-30b-readback`；獨審 `.worktrees/skill-improvement-30b-readback-review`。Grant 前不建立 allocation、不派工。創建時直接核對 containment、非 reparse、Git root/branch/HEAD/clean |
| MODIFY | `library/local_orchestration/mainline_source.py`；`tests/test_mainline_source.py` |
| CREATE | `library/local_orchestration/mainline_readback.py`；`tests/test_mainline_readback.py` |
| DELETE | 無；不得刪既有測試、降低 assertion 或更新 Expected 掩蓋失敗 |
| FORBIDDEN | `dispatch_authority.py`、Router、Receipt／Grant store、Runner、其他library/tests、skills、templates、SPEC／Context／PRD正文、正式branches/runtime/config/credentials；控制面另行維護本票與既有review/registry，不授予實作者文件擴權 |
| Responsibility／reuse | 原 `mainline_source.py` 提供唯一 wire parse/digest/graph assembly；新 `mainline_readback.py` 僅 trusted-anchor查核＋受限provider GET讀回協調。重用既有 GitObservation、DirectRemoteObservationRequest／observe_declared_remote、RawGitBlobReadResult、MainlineProjection及finite failures，不複製 schema／DFS／policy engine |
| 測試重用與增量 | 原 constructor/fixture cases不重寫；在原檔補 shared seam equivalence與fixture scope保護。新檔限參數化 transport/readback cases，fake已存在的port，不另造mock server、clone、wrapper或Runner。預期產品有效行增量≤350、測試≤350、實作者文件/截圖=0；超量是結構審查訊號，不可壓縮/碎拆取巧，亦不自動新增檔案 |
| Profile／預算候選 | 外部來源邊界按既有評估至少HIGH_ASSURANCE；獨審/對抗性要求不降級。新增命令累計上限600s、單命令120s，保留30A與歷次耗用；initial＋一次有界correction，超出先停。這是待Owner核准的新phase額度，**尚未追加**。無付費API/模型provider測試、無壓力負載；controller兩個具名工作席位，作者零helper |

### 輸入／輸出與不可繞過的來源限制

1. 輸入由可信 control-plane 綁定：Owner核准紀錄、原Ticket／SPEC版本、Grant ID、
   implementation baseline、Context04 exact commit/blob、四項binding revision/blob、
   repository provider/host/key、`refs/heads/main`、feature、metadata ID mapping及讀取
   時窗。Root在既有授權流程直接讀回受審、已提交的 exact anchors後才建立 reader；
   public request 只可選本ticket已綁的feature，不接受 caller 覆寫 anchor/repo/ref。
   不建立另一套簽發器；普通DTO建構不是authority。任何跨生命週期消費仍須走既有
   source/Grant資格驗證，不將此切片宣稱為可抵禦任意同process惡意caller的隔離。
2. 先驗權，後建構transport/讀取。無有效phase授權或批准來源無法讀回，連GET也
   不執行。只許已綁GitHub repository的公開、無credential HTTPS API GET；拒絕
   redirects、不同host/repo/ref、任意URL/path、非GET方法、超時/超量body，raw內容
   不進log。使用標準library transport，不執行clone/fetch、Git branch/ref寫入、
   checkout、工作副本讀取、原生spawn或任意shell。公開讀取不增加帳號/secret權限。
3. 讀 exact remote ref取得新鮮SHA R，再在**同一R**讀Context、canonical PRD/CHG、
   SPEC、index與兩個leaves。獨立核對provider回傳的repository/full ref與預先批准
   anchor；驗證Git blob identity/原始bytes及四個binding的commit/blob/revision、
   repo identity/ProjectId mapping，不能只比index自報值。不得拿本地origin/main或
   cached observation作freshremote。既有pure observation reducer只分類port回件，
   不可宣稱它本身已觀察網路。
4. 讀完再次讀 exact remote ref，必須仍為R且整輪在批准時窗內；移動/過期即拒絕，
   不混用第二個SHA的部分leaves。此兩次bounded observation是新30B交易一致性
   檢查；不沿用30A synthetic單次observation冒充正式來源。只從R的rawbytes驗證
   index/leaf鏡像/digest，沿用唯一parser及既有projection。不得把DIRECT_REMOTE_REF
   改標WORKTREE_HEAD以繞過fixture scope；最小抽取純blob assembly，原fixture
   wrapper仍只接受synthetic observation並回FIXTURE_ONLY，兩條路徑共同case須等價。
5. 輸出 scope=`READBACK_CANDIDATE_ONLY`，帶精確R、來源evidence digest與原有
   MainlineProjection；或者一個finite拒絕，不含原文/URL/path/secret。既有source
   failure和DirectRemoteObservationDecision能表達的原因直接沿用。只補必要的
   GRANT/ANCHOR_MISSING、DECLARATION_REVISION_MISMATCH、BINDING_REVISION_MISMATCH、
   TRANSPORT_LIMIT_EXCEEDED等具名差異；不建立第二套Router狀態機。普通missing
   blob、非法JSON、鏡像或digest錯配仍沿用30A失敗碼。

### 有限驗收與建構順序

| Cell | 必要正向／反向驗證 |
| --- | --- |
| 30B-R1 權限及來源 | 真control綁定在effect前讀回；無Grant、偽造caller anchor、自改repo/ref/ProjectId、缺批准版本，transport呼叫數=0。普通constructor成功不等於授權成功 |
| 30B-R2 同snapshot讀回 | 同R的index+leaves、四binding及Context exactblob通過；不同R、missingsource、舊Context03、錯revision/identity/rawdigest、重複/非法fence各自具名拒絕；讀完ref移動/過期不得輸出PASS |
| 30B-R3 共用assembly | 新seam與30A有效fixture投影相同；30A外部scope限制維持、91項既有聚焦回歸不退化。突變落在新實際readback入口使用的parser/transport，不只測舊copy |
| 30B-R4 無效應 | 成功或拒絕都沒有admit_dispatch、receipt、Runner、spawn、nativeGit/fs修改；GET allowlist、redirect、非GET、body/timeout限制及無secret輸出有negativecases。腳本不載入未核准source、Expected不從Actual生成 |

新public型別尚不存在時，在同一Grant/owner/四檔邊界內先做純constructor/validator/
normal round-trip、finite negatives、strict type，禁止transport/sourceeffect；獨審
通過pin commit才接有界readback協調。既有constructor派工前照跑。這只沿用30A
已審的建構排序，不要求新閘門先合格才能建置自己，也不降低最終真來源條件。
預定 commands：`python -m pytest tests/test_mainline_source.py tests/test_mainline_projection.py tests/test_mainline_readback.py tests/test_project_authority_observation.py -q`；
`python -m mypy --strict library/local_orchestration/mainline_source.py library/local_orchestration/mainline_readback.py`；
`python -m compileall -q library/local_orchestration/mainline_source.py library/local_orchestration/mainline_readback.py`；`git diff --check`。
實作者至少sourcebinding/digest兩個mutation，reviewer從不同門移動ref/假calleranchor
擇一反向突變，必須具名紅→byte-exact還原綠，讀取未縮減輸出。Scope diff從固定
baseline比對四路徑。兩個產品責任不得混入CLI/framework；不新增PRD、驗收或Gate。
Return=`IMPLEMENTED|BLOCKED|CHANGE_DETECTED`，candidate、baseline、files、checks、
findings、scope_deviations、unverified、累計attempt/time；原作者同票修正，Reviewer
獨審，既有機械gate本地整合。新真實Host/正式effect仍不在本票切片的PASS宣稱。

### 待簽發的精確Grant候選與遠端決策

`grant-ticket30b-readback-20261018` **CANDIDATE / NOT_ISSUED**：project/repo/ref、
原PRD/CHG/SPEC、final30M baseline及本leaf/README blobs按final seal綁定；actor/
reviewer/worktree/四路徑與上述30B-R1～R4、600s新增命令額度、same-lifetime/direct
lane、nohelper全部精確沿用。Owner核准前不派工。Root只能在批准來源獨立讀回、
原範圍無漂移時綁定執行，不能用本候選自行簽發；修改產品契約/其他路徑另停。
工作worktree/temp asset都要owner+TTL+teardown，Review/evidence seal先於清理；
使用者/正式commit/他票/Recovery不清除。

建議決策：**先核准30B本地實作，測試network預設0**；真實GET驗證僅在source已
正式publication、獨審通過與精確外部唯讀授權成立後執行一次。最多10次GET（repo
identity、兩次exactref、去重後最多7個blob），單次≤20s、全輪≤200s、每blob≤2MiB，
不重試、不呼叫外部模型、不寫remote/正式runtime。這項有界外部讀取可在同次
Owner決策給條件式授權；條件不成立只回UNAVAILABLE，不假裝合格。

推送不在現有授權內。直接觀察的遠端main仍為`a1cb6c13adbeb52a4117991727dcc3d4af6d2a33`。
控制基準d000相對該SHA已領先124個commit、淨變更87個path；**不得把整條支線
推送偽裝成僅本輪五文件遷移**。final seal提供完整精確candidate range、commit清單
digest及淨diff digest，以供一次決策，不用origin cache。推薦目前**不核准這個較廣
range的push**：它還包含其他已整合切片、未生效設計與模板，須另依既有promotion
規則核對範圍/獨審/來源後才非force推至`refs/heads/main`。不自行抽取新remote
commit、不變更批准binding以避開這個差異。這不阻擋30B本地建置；真來源成功格
在正式來源到位前保持NOT_VERIFIED，既有遠端舊版應明確拒絕。

若Owner選擇授權該精確完整range，push前須再次直接讀ref等於seal中的expected
oldSHA、確認ancestor與scope，使用非force exact`<approvedSHA>:refs/heads/main`，
不用provider Merge按鈕或lease/force；如remote移動則停，不自動rebase或追加range。
push後`git ls-remote <approvedremote> refs/heads/main`須等於approvedSHA，再從
provider在同SHA讀Context04/index/leaves及rawdigests；只有push+exactreadback才可
稱AUTHORITY_INTEGRATED。GitHub已有active Dependency Graph dynamic automation，
不能保證push零自動化；已查repo hooks=[]不是全GitHub App/organization自動化
不存在的證明。讀回失敗保持PUSH_UNCONFIRMED。這不是Release/Deployment授權。

可直接回覆的限縮核准文字（精確SHA／blob採既有review final decision seal）：
「核准Ticket30B在該seal的baseline與leaf綁定下按四路徑、30B-R1～R4、本地測試
network=0與600s新增命令額度實作、獨審、同票一次修正及受控本地整合；保留歷史
耗用。條件式核准source正式到位、獨審及effect前授權讀回後的一次10 GET／200s
公開唯讀驗證，不授予其他外部效果。**不核准push**，真來源缺失保持拒絕與
NOT_VERIFIED；不啟用admit_dispatch/Host/正式結案，不發布、不部署。」
若要push，必須另明文核准seal的完整oldSHA→exactcandidateSHA range及已知自動化
風險，不能從上述實作/GET授權推定。以上一次包列全，不要求Owner找Host、CI或
自行拼Grant；一般DTO/seam/fixture設計由Architecture Owner/實作者處理。

## 保留的最小 30A 候選

下列是**正式 target source 路線的終態候選**；本輪 30A fixture 只建置其中
committed bytes→validated candidate 的純隔離子集，不提前啟用 1–2 或真 Host。
終態意圖限於一個 source-bound、metadata-only 的 candidate projection：

1. 從**已核准且已 version-bind** 的 `ProjectAuthorityContract` 取得 declared repository 與
   full `project_authority_ref`；caller、prompt、工作副本或 `origin/<ref>` cache 不能選擇
   authority line。
2. 經既有 `DirectRemoteObservationPort`／`observe_declared_remote` 對該 declared ref 做一次
   fresh direct observation。caller SHA 只能作 mismatch assertion；authority SHA 是 direct
   observation 的結果。
3. 透過經准入的 committed-source readback boundary，從 observed SHA 讀 target-owned
   generic `modules/tickets/<feature>/README.md` index 與它正式指向的 ticket leaves。
   技術格式依下文 Architecture Owner 決策；實際 mainline 成員、依賴、owner／handoff
   與 revision 仍必須由 control plane 從已核准 target artifact 遷移，不得從敘事表推定。
4. 只有在 project、mainline、ticket、dependency 與 source revision 全部驗證後，才建立
   既有 `MainlineProjectionRequest` 並呼叫 `project_mainline_tickets`。輸出只可為
   `ready_for_recheck` 等 candidate metadata；它不是 Grant、admission、dispatch、Review、
   integration 或 closure authority。

這個候選不得接受 caller-built `MainlineTicket` 作為正式來源，不得 cache fallback、retry、
polling 或把 raw source 存進 Router state。remote 在 observation 後移動時，任何 effect
邊界仍必須重新准入；30A 本身沒有 effect 權力。

## 已存在、可重用但尚未組成 implementation authority 的能力

```text
selected: workflow-router-poc@112134ecee7c7ea770ca90c9ee3ed91f2a5ed8a9
why: reuse the existing immutable mainline candidate projection and graph validation
read: library/workflow_router/README.md → library/workflow_router/__init__.py → mainline_projection.py
dependency: existing ProjectAuthorityContract and direct-observation contracts
boundary: no authoritative source declaration/readback composition, Host admission or formal closure
```

- `library.workflow_router.mainline_projection` 已提供 strict `MainlineProjectionRequest`、
  `MainlineTicket`、有限狀態、dependency graph 驗證與純 candidate reducer；不得複製。
- `library.local_orchestration.project_authority` 已提供 `ProjectAuthorityContract`、
  `DirectRemoteObservationPort`、request/result/failure models 與
  `observe_declared_remote`；這是 fake-compatible contract，不等於本票已有 production
  declaration loader、provider adapter 或 Host binding。
- `library.local_orchestration.git_handoff_event_adapter.GitReadbackPort.read_blob` 是現有精確
  commit/path readback seam，但其 authority identity、source selection 與 failure semantics
  未被有效 SPEC 指定為 30A 的正式 mainline source boundary；不得直接宣布採用。

## 為何目前不能形成正式來源／effect implementation ticket

以下是仍未完成的 authority facts／effect Grant；不得由 implementer 猜測：

1. 哪個 target-versioned `ProjectAuthorityContract` declaration artifact/revision 是正式讀回的
   trust anchor，以及 control plane 如何獨立 read back 並證明該 declaration 已准入。
2. workflow-governance 等 target 的實際 mainline ID、required/optional set、dependency edges、
   owner／handoff、ticket leaf reference 與各自 revision/digest 尚未依下文 schema versioned
   into its feature index；現有 status table 不構成這些 authority facts。下文已準備
   本專案候選，不能由此跳過正式遷移與獨審。
3. 30A 隔離建置的條件式 Grant 已由上節 Owner 精確核准；剩下是文件獨審及
   reviewer-established baseline／owner／worktree／leaf 的實際讀回綁定。
   一般「繼續有界工作」指示仍不是其他 effect 的 Grant。

先前硬編 feature path、自報 Grant、未遷移的 parser 契約與行數 ceiling 均撤回。
下述 Architecture Owner 的通用技術決策只足以準備隔離 fixture 建置，不補足
target 事實或 effect Grant。上節 active `johnny-boundary` 只落實已核准的
fixture 建置；formal target/effect 不在其中，modify 始終為空。

## Architecture Owner 的限縮技術決策（非 implementation Grant）

在既有 AC9 設計基準內，source encoding、parser 邊界與有限失敗碼是工程決策，
不要求 Human Owner 再選一次。target-owned 的 `modules/tickets/<feature>/README.md`
保留人讀 status table，另有**唯一** `## Mainline source contract` heading，其後緊接
唯一 `json` fence；該 fence 是機器讀取的唯一 index，敘事表不是 authority。JSON
object 嚴格包含：`schema_id = mainline-index/revision-01`、`project_id`、`feature`、
`mainline_ref`、`objective_ref`、`owner_ref`、`handoff_ref`、`bindings[]`、`tickets[]`。
每個 binding 嚴格包含 `kind`（context/prd/change/spec）、`identity`、`artifact_ref`、
`revision_sha`（40 位小寫 hex）。AC9 所需四類來源各恰一筆，故 bindings 長度恰為
4 且 kind 不重複；空陣列、缺類別或重複類別為 `INDEX_SCHEMA_INVALID`。這只
驗證 fixture source-binding 完整性，不新增 authority resolver。每個 ticket 嚴格包含 `ticket_ref`、
`ticket_revision`（既有 `RevisionDigest`）、`leaf_ref`、`leaf_digest`
（`sha256_` 加 64 位小寫 hex）、`required`（boolean）、`status`（既有有限 enum）、
`depends_on[]`、`admission_ref`（nullable）、`evidence_refs[]`。所有 metadata ID 仍須
通過既有強型別 constructor，不另建平行 ID 規則。

每個精確 ticket leaf 在既有內容中另有唯一 `## Mainline ticket contract` heading，
緊接唯一 `json` fence，嚴格包含 `schema_id = mainline-ticket/revision-01`、
`ticket_ref`、`ticket_revision`、`status`、`depends_on[]`、`admission_ref`、
`evidence_refs[]`。leaf 是 graph/status 的正式來源；index 的相同欄位是綁定宣告，
兩者任一值不同即 `INDEX_BINDING_MISMATCH`，絕不採 first-match 或單邊覆蓋。
`required` 與 `leaf_ref` 由 index 宣告，與 leaf 原始 bytes digest 一起驗證；
只有從 committed leaf 解析出來且與 index 一致的節點能進既有投影。

Parser 必須拒絕重複 JSON key、未知／缺失欄位、空 tickets、重複 ticket／leaf ref、
跨 feature 的 leaf、未知依賴、非法狀態及 schema 漂移。`feature` 決定通用 index 路徑；
每個 leaf 只能是同 feature 目錄的直接 `.md` 子檔。index 與 leaf 必須在同一 direct
observed SHA 讀取；逐 leaf 的**原始 bytes** SHA-256 必須等於 `leaf_digest`，
再解析該 leaf 的唯一 contract fence。成功後才從驗證過的 committed leaves 建立
既有 `MainlineProjectionRequest`；
`source_revision = rev-<observed SHA>`，不可接受 caller／index 自報值。原始 Markdown／
JSON 只在讀取流程內暫存，不進結果、Router state 或 log。

最小 source read port 為 `read_blob(observation: GitObservation,
artifact_ref: TargetRelativePath) -> RawGitBlobReadResult`，要求 repository/ref 身分
隨 observation 綁定。`RawGitBlobReadResult` 只重用既有 `GitBlobReadStatus`，但
`FOUND` payload 必須是原始 `bytes`，非 FOUND 不得攜帶 payload；hash 以該 bytes
計算，UTF-8 解碼與 fenced JSON parse 必須嚴格拒絕非法序列、重複 key 與多重 block。
現有 `GitBlobReadResult.payload: str | None` 和只收 commit/path 的
`GitReadbackPort` 均不足以證明原始 bytes／authority identity，不得假借重用。
候選組合只做一次 `observe_declared_remote`、逐 exact blob 一次 read、一次既有純投影；
結果只有候選 metadata 或有限拒絕。source failure 僅限 `INDEX_NOT_FOUND`、
`INDEX_READ_UNAVAILABLE`、`INDEX_SCHEMA_INVALID`、`INDEX_BINDING_MISMATCH`、
`LEAF_NOT_FOUND`、`LEAF_READ_UNAVAILABLE`、`LEAF_DIGEST_MISMATCH`、
`PROJECTION_INVALID`；direct observation 失敗沿用既有 enum，不複製。

這項決策不把 30A 延伸到 Router／Host：目前 `project_mainline_tickets` 只有套件匯出
與測試消費者，沒有正式 Router caller。production repository binding、replace-ref-safe
Git 讀取、真 Host effect 前准入及正式結案均是後續獨立邊界。

## 本專案主線與 authority 宣告候選（非 live source）

以下是 2026-10-18 自**釘選 `3ca02bd5e90611c101d97cc79f06b4751c70cd1c`**
讀得的候選，不是 `## Mainline source contract`，也不是已准入
`ProjectAuthorityContract`。既有活躍 `PRD-20260805-009`／`CHG-20260805-009`
與 workflow-governance SPEC revision 02 管本功能；清單 revision 23 管整批進度。

| 主線維度 | 已查證的事實 | 建議宣告與影響 |
| --- | --- | --- |
| 專案／目標 | `modules/tickets/workflow-governance/README.md` 的 Delivery objective 是 completion re-enter Router、獨立安全接續、精確等待／HALT；清單 01–12 是 Owner 指定的整批完成目標，04 已完成本地回放 | 本專案 programme mainline 設「12 項必要成果全部具實作、驗證、獨審；不改 target 產品」；**不要**把 checklist 順序當 ticket dependency graph |
| 必要／選配 | Owner 要求 12 項必要實作與驗收；現有 status registry 含已整合切片與仍開的 Ticket 30；沒有逐票 `required` 的正式 source fence | 結果層 01–12 為 required，額外優化為 optional；先在 workflow-governance feature source 遷移 Ticket 29 已完成投影與 Ticket 30 開放 continuation，其他 ticket 的 required/optional 只依精確契約逐一驗證後登記，不由 status table 猜 |
| 依賴／接續 | 清單優先 02→04→05→06→07；Ticket 30 讀既有 Ticket 29 純投影，30A fixture 是真來源／`admit_dispatch` 驗證的前置技術能力；04 已完成 | 記錄可證明的能力邊 `29 → 30A fixture → 真來源／effect qualification`；01／02 的正式 closure 依賴該實證；其餘無精確相依證據者維持 `UNKNOWN`，准入的無相依工作可繼續 |
| 所有權／交接 | 清單指定 Root 管需求、衝突、派工，票級實作者依 Profile，另一席獨審；Ticket 30 尚未綁 active task/worktree | 宣告 role refs：Root control/reviewer orchestrator、Profile 選出的 implementation owner、獨立 reviewer；每次實際派工再釘 task/worktree/branch，實作者只回 candidate/evidence，不自行整合 |
| authority line | `origin` URL 是 `https://github.com/johnnyliu365-sys/Johnny_AI_Skill.git`；`git ls-remote --symref origin HEAD` 讀得 `refs/heads/main` → `a1cb6c13adbeb52a4117991727dcc3d4af6d2a33`。`CONTEXT.md` revision 03 **已封存**，project-authority Context revision 03 與 SPEC revision 11 也只有通用邊界，沒有本專案可讀回的完整宣告 | 推薦既有 target-owned `CONTEXT.md` 作唯一 declaration anchor，`main`／single-line 作候選，但**不能直接寫入**。須先取得適用的 approved change ref，由 Architecture Owner 在 `ARCHITECTURE/GRILL/CONTEXT` 執行 `REVISE`、pin 預期 sealed revision 03，再依既有流程封存與處理受影響 SPEC 基準。遠端 HEAD 不是核准；未完成前只可讀引 |

精確版本索引（均為本輪準備的**輸入**，不是自動升格的 authority）：

| 文件 | 已讀 commit／blob | 作用 |
| --- | --- | --- |
| `doc/AI-SKILL-IMPROVEMENT-CHECKLIST.md` rev23 | `3ca02bd5`／`ea4ea90a90662e73bed02466979c225037b635ac` | 01–12 進度／優先順序，不是 ticket graph |
| `modules/tickets/workflow-governance/README.md` | `3ca02bd5`／`d74b614f3633475708804bed07d9848b6d64451f` | 目標／人讀票面狀態，不是機器 source |
| Ticket 30 | `3ca02bd5`／`20a1f2cc1b9cac1e5697dbfb66eb05deb875bde5` | 原票 lineage；本次 docs 修訂後須改用最終新 blob |
| `CONTEXT.md` rev03 | `a5e2847312c4b3f9a78b424af02f1fa2ac38a8f5`／`9096c68199994b1414862828ffb0ce060f8482d7` | 本專案既有 Context，尚無 concrete authority declaration |
| project-authority Context rev03／SPEC rev11 | `80b5d96b29ab671c5a4103e66f0dcbbc12739b3a`／`771bb5cbba879d196c1f85b6b4721d4c5db870de`；同 commit／`27dfc04eef7de58aa25b3c7d9e136be0228553b2` | 可重用 declaration 型別／readback 邊界，非本專案核准值 |
| 活躍 PRD／CHG leaf | PRD `ede925d3f7b89236604f3b4b63c31708ab7f2ab6`／`6555d6e60645787a2f9a0ec6acd7849308172f09`；需求 leaf `8df8d2b3fa904d174e9e0c1f7d08f407402adce6`／`762b3be9a8a496689c360c5f2d8fd603a6ad68e8` | 原需求身分，不新增 PRD |
| `modules/spec/workflow-governance.md` rev02 | `51fa1e20f73d87b720f80b9d4dcc47b0de962898`／`4323863f09ef89382e27eb1e4fc99ba652171da4` | AC1–8 有效、AC9–11 已獨審設計基準；非實作 Grant |

此候選的歧義是**正式宣告載體／實際 required ticket graph**，不是 Owner 要自行填表。
推薦 `CONTEXT.md` 的合法 `REVISE` 路線，但本輪 docs-only 授權**不含**該寫入；
`router-control.md` Shared-Context authority 要求 approved change ref、Architecture Owner、
限定 stage、expected sealed revision 03。若選此路線，先形成該精確授權，再處理
受影響 SPEC 的合法 rebaseline；在這些條件前，不可把本候選讀作 live declaration。
逐票 graph 由 Root 以既有核准 leaf 做 docs-only migration，未能證明的 edge 不自造。

### 本輪 CI 來源窄查（不是退役證據）

- 本地 pin：控制 worktree HEAD `3ca02bd5e90611c101d97cc79f06b4751c70cd1c`；
  執行 `git ls-tree -r --name-only HEAD -- .github .gitlab-ci.yml .circleci
  azure-pipelines.yml Jenkinsfile .buildkite .travis.yml appveyor.yml
  bitbucket-pipelines.yml .drone.yml .woodpecker.yml Makefile Taskfile.yml
  justfile package.json pyproject.toml tox.ini noxfile.py Cargo.toml go.mod`，
  此範圍未見可宣告的 CI command source。
- 可讀遠端：`git remote -v`、`git ls-remote --symref origin HEAD`、
  `git ls-remote --heads origin`；九個 branch tip 的 GitHub Git tree API 遞迴路徑
  比對同一類 CI/wrapper 配置（`main a1cb6c13`、
  `codex/controlled-verification-intake 9707a1e5`、
  `codex/cve-01a-wire-foundation d0c93111`、`publication-0.4.9 c3cb81c4`，
  `verify/claude-publication-08-live-cutover 055d4d24`、
  `verify/claude-publication-15-v0414-codex-native-dispatch f5291dc3`、
  `verify/claude-publication-17-v0414-codex-readmission 818eef5a`、
  `verify/claude-publication-17-v0414-codex-readmission-r02 d6b2320f`、
  `verify/claude-publication-17-v0414-codex-readmission-r03 01b810f0`）；
  `origin/main` 的精確 readback 為上述 `a1cb6c13`、
  tree `truncated=false`，此範圍未見 CI 配置。實際批次命令（僅查 source path，
  不執行 CI；每筆 `CandidateCount=0` 且 `Truncated=False`）：

  ```powershell
  $remoteTips = git ls-remote --heads origin | ForEach-Object {
      $cols = $_ -split "`t"
      [pscustomobject]@{ Sha = $cols[0]; Ref = $cols[1] }
  }
  $remoteTips | ForEach-Object {
      $tree = Invoke-RestMethod -Uri ('https://api.github.com/repos/johnnyliu365-sys/Johnny_AI_Skill/git/trees/' + $_.Sha + '?recursive=1') -Headers @{ Accept = 'application/vnd.github+json' }
      $matches = @($tree.tree | Where-Object {
          $_.path -match '(^|/)(\.github/workflows/|\.gitlab-ci\.yml$|\.circleci/|azure-pipelines\.yml$|Jenkinsfile$|\.buildkite/|\.travis\.yml$|appveyor\.yml$|bitbucket-pipelines\.yml$|\.drone\.yml$|\.woodpecker\.yml$|Makefile$|Taskfile\.yml$|justfile$|package\.json$|pyproject\.toml$|tox\.ini$|noxfile\.py$)'
      } | Select-Object -ExpandProperty path)
      [pscustomobject]@{ Ref = $_.Ref; Sha = $_.Sha; Truncated = $tree.truncated; CandidateCount = $matches.Count }
  }
  ```

  未 fetch、未執行遠端 CI。
- 結論只限上述目前可讀分支／路徑：**此範圍未見**，不是「全專案無 CI」。
  `DeclaredTestCommand` 仍未有可信來源，**空命令清單絕不授權舊測試退役**；
  checklist 08、Ticket 32/36/39 的 retirement gap 維持開放。

## 30A 隔離建置：Closure revision 02，同票修正

Owner 2026-10-18 指定 `library/local_orchestration/dispatch_authority.py::admit_dispatch`
為**之後**第一個跨生命週期派工驗證入口。這只是優先順序，不使該入口、原生 spawn、
真實來源或正式結案合格。現行 AC 1–8 繼續有效；已獨審的 AC 9–11 只作建置設計
基準。新閘門不以「先合格」阻塞自己的隔離建置，真實 effect 仍須在自己的邊界
重新讀回來源與權限。

**現行 SPEC 衝突不得省略：**workflow-governance SPEC revision 02 的 AC9–11
收尾文字明定 Ticket 30 在 trusted source 與 per-ticket Host admission path 綁定前
`non-dispatchable`。本段 30A fixture 正是要建置該來源能力的一部分，故目前
連 fixture implementation dispatch 也**不能只靠 Ticket Grant 啟動**。
需要 Owner 同次精確核准一個**僅供隔離建置的受限 bootstrap 例外**，並在原 SPEC／
Ticket lineage 中依 Change Control 記錄、獨審後生效。例外只免除 fixture 建置前
須先完成它自己要建的真 source／Host qualification 這個循環；**不**改 AC9–11
驗收、安全不變量、真 effect 准入或 Ticket 30 整體 NON_DISPATCHABLE 狀態。
以上記錄首次候選的衝突；Owner 已在本輪核准此精確限縮例外，原 SPEC revision 03
及本票正依上節 Change Control 獨審，通過前仍不派工。

本階段的單一結果是：從**隔離且已提交的虛構 Git fixture** 讀取同一 commit 的
index／ticket leaf 原始 bytes，驗證上節封閉 schema、digest、綁定與依賴圖後，
呼叫既有 `project_mainline_tickets` 產生**候選 metadata**。fixture declaration 與
observation 均明標測試替身，不可成為本專案 authority、真遠端 readback、派工、
receipt、Host qualification 或 closure 證據。產品模組只持有受限的 source-read
port；Git fixture 的建立／提交／讀取限測試專用暫存目錄，不能寫共享 worktree、
正式 ref 或外部 remote。

| 票面欄位 | 30A 建置候選（待精確 Grant） |
| --- | --- |
| SPEC／需求 | 原 `PRD-20260805-009`／`CHG-20260805-009`、workflow-governance SPEC revision 02 AC-9；不建立新 PRD／SPEC |
| 控制、實作、獨審 | Root 控制與 reviewer orchestrator；一名由當下 Profile 選定的 `implementation-standard` 實作者在 repo-contained `.worktrees/skill-improvement-30a-fixture`／`codex/skill-improvement-30a-fixture`；另一席獨審者不與實作者共用 worktree。具名 task／Agent 在派工前才精確綁定 |
| Baseline／lane | 本次文件最終受審 commit 作實作 baseline，派工前完整 SHA 讀回；same-lifetime direct lane，bridge／receipt `NOT_REQUIRED`。Grant 前不建立實作 worktree 或派工 |
| 可新增 | `library/local_orchestration/mainline_source.py`：單一責任為受限 raw-byte committed-ticket source assembly；`tests/test_mainline_source.py`：專屬 fixture、正反驗收與突變。兩檔各有 AC-9 消費者與驗收，不複製現有投影／測試框架 |
| 可修改 | 無。重用 `library/workflow_router/mainline_projection.py`、`library/local_orchestration/project_authority/` 的型別與 observation，以及現有投影測試；若真需要改既有公開契約，先回同票修訂 allowlist，不能順手擴權 |
| 禁止 | `dispatch_authority.py`、Router／Host／runner／CLI、正式 PRD／SPEC／Context／authority declaration、其他 tests 與 target 產品；不得 push、deploy、release 或清理非本 fixture 資產 |
| 預期增量／產物 | 產品碼一個單責新模組、聚焦測試一檔；既有產品檔零、正式治理文件零、持久測試產物零。行數只作結構審查訊號，修正不重置原票預算；fixture 必須有 owner、TTL、teardown |
| Return | `IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、candidate SHA、實際檔案、具名測試／型別／反向突變、真實來源與 Host 未驗證項；實作者不整合、不推送 |

供 Owner **與上述 SPEC bootstrap 例外一起**精確核發的 Grant 候選：project 為本 `Johnny_AI_Skill`、
operation 僅 `Ticket 30 / 30A fixture source-and-test build`、原
`PRD-20260805-009`／`CHG-20260805-009`、上述 SPEC revision 02 AC9；
baseline 為本次 docs-only 最終獨審 commit（完整 SHA 於回件提供，核發時 pin，
不得用 `HEAD` 浮動值）；actor 為 Profile 選定的一名實作者，Root 為唯一 control
orchestrator，另一名不同席位獨審；branch/worktree、`create` 兩路徑、
`modify = none`、禁止範圍、Closure 30A-F1–F4、命令與 return 均以本節精確文字為限。
有效期只涵蓋本 Ticket 30A 一次受控候選實作與同票修正，修正不重置原預算；
候選 SHA 和逐項驗收須由獨審後才可受控本地整合。此段**不是** Grant 簽發、
不加入 `johnny-boundary`；實際 actor/task/worktree identity 須在派工時讀回並綁定，
任何不匹配或超界改動 fail closed。Grant 不涵蓋正式 source migration、
`admit_dispatch`／native spawn effect、push、release 或 deployment。

有限 Closure revision 候選：

1. `30A-F1`：同一 fixture commit 的唯一 index fence 與每個 committed leaf fence 經
   原始 bytes hash、嚴格 UTF-8／JSON 驗證；index↔leaf identity／status／dependencies
   完全一致。A waiting、獨立 B `ready_for_recheck`、依賴 A 的 C waiting；B 完成不
   使 A 或 required mainline 關閉。
2. `30A-F2`：working-copy 改動或另一 commit 的 leaf 不污染釘選 commit；錯 digest、
   缺 leaf、跨 feature／`..` path、重複 key／fence、非法 UTF-8、未知欄位、重複／
   未知／循環依賴及 index↔leaf 不符均有限拒絕，**零候選投影**。
3. `30A-F3`：caller 自報 repository/ref/SHA、ticket metadata 或 tracking ref 不可升格
   成真 authority；fixture port 只接受綁定 synthetic observation。同一 exact blob
   最多讀一次，無 retry、polling、cache fallback；結果／log／Router state 不含 raw
   bytes。對 `admit_dispatch`、native spawn、receipt store 設零呼叫 sentinel。
4. `30A-F4`：公開 success／failure DTO 經一般 constructor／round-trip 建構，
   strict mypy、聚焦投影回歸、compile/import、`git diff --check` 全綠；實作者對
   digest 與 leaf binding 做紅→綠突變，獨審從不同入口改壞 committed leaf 或
   source SHA，具名格轉紅且精確還原。

Revision 02 只補清 F1 的既有四類 binding 完整性，沿用 F1–F4、原 Grant、
原型別 PASS、原作者／獨審席、原始 cumulative baseline 與既有耗用。
首審 `43c9ebf1081f189e9adeb87f3717b6b50a2ec1b9` 的未解項全部保留：
F2 重複 heading 的尾端空白與深層 JSON 必須 finite rejection；F3 fixture 在
任何 Git command 前隔離 ambient Git environment，不能寫出本次 test-owned root；
F1 空／缺／重複 binding kind 拒絕。前兩類是原規則的負例補驗，F1 是控制面
修復 ticket 漏寫的 cardinality，不由 implementer 自選需求，不改 SPEC 或新增 PRD。
這次 ticket-only 變更是 Owner 已允許的文件 baseline 續綁；實作者只合併該
精確 docs commit，不修改 ticket，仍只修本票新建的兩個檔案。

預定命令：`python -m pytest tests/test_mainline_source.py tests/test_mainline_projection.py -q`、
`python -m mypy --strict library/local_orchestration/mainline_source.py`、
`python -m compileall -q library/local_orchestration/mainline_source.py`、`git diff --check`。
此節是**票面候選**，不是已跑結果或有效 `johnny-boundary`。受限 bootstrap
例外依原 SPEC Change Control 精確核准／獨審生效，且 Owner 核發精確 Grant
後，才將兩個 `create` 路徑轉成票內唯一活躍機器邊界、凍結 Closure revision、
獨審票面並派工；不能讓候選文字先取得 mutation authority。

## 剩餘正式來源啟用與 Grant

Control plane 須從已核准 target artifacts 決定實際 mainline 的成員、required flags、
依賴、owner/handoff 與 revisions，先以 docs-only migration version 到該 feature
index；不得拿本票的 schema 示例、敘事 status table 或 Agent 自報填入 authority
facts。同時須讀回 admitted `ProjectAuthorityContract` 的精確 declaration
artifact/revision。上節 **fixture-only 30A** 僅可經已生效的 SPEC bootstrap 例外
及精確 ticket Grant 建置與驗證，
但不能取代正式 migration。實際 target source 啟用與後續 `admit_dispatch` effect
驗證仍須遷移完成、獨審、正式 declaration readback 與另外的精確 effect Grant／
Host qualification；凡超出既有 SPEC 的產品、安全或權限邊界仍須 Change Control。

## P0 preflight 與未來 acceptance 下限

30A fixture 的 SPEC bootstrap 例外及 Grant 均生效、精確票面凍結後，
Architecture Owner 才能把該建置 slice 修成 type-only dispatchable cut；新型別
實際 constructor preflight 及獨審通過後才准同 owner 寫 parser/source-read 行為。
正式 target/effect slice 另待上游來源決策。依上節有限建構順序與各 slice 適用範圍：

- 用 ordinary public constructors 建立所有 success/failure DTO、enum、port request/result，
  覆蓋 exact primitive、nullability、finite disposition；禁止 `Any`、`cast`、coercion、
  bypass constructor、未驗證 dict 或動態 member lookup。
- 30A fixture 證明 caller 自報資料不能取代**synthetic observation 綁定**與 committed
  readback；正式 target/effect slice 才須證明它不能取代 admitted declaration 與 fresh
  direct observation。local tracking ref 在兩者都只可為 diagnostic。
- 命名 normal cell：A precise wait、independent B 為 `ready_for_recheck`、C 依賴 A 而
  waiting，且 B 完成後 A／required mainline 仍開放。
- 命名 failure cells：30A fixture 的 committed source missing/ambiguous/malformed、
  index↔leaf revision mismatch、incomplete/unknown/cyclic dependency；正式 slice 另覆蓋
  declaration 缺失及 direct observation unavailable/not-found/ambiguous/stale/moved/
  identity mismatch。全部 fail closed 且無 projection。
- 命名 boundary cells：30A fixture 的每個 exact blob 最多一次 read、無 retry/polling/
  cache fallback、raw content 不進 result/log/state、candidate 不觸發 Router/Host；正式
  slice 另證明一次 fresh direct observation。
- 由獨立 reviewer 從不同入口反向突變 authority SHA、index↔leaf revision、全域 freeze B
  與 false mainline closure；必須看到對應 cell 紅後 byte-for-byte 還原。
- 使用 Python 3.11 strict checker、focused projection regression、compile/import 與
  `git diff --check`；精確命令在 approved public contract 與 writable scope 固定後寫入。

XSS 目前為 `N/A`：候選沒有 Browser/WebView/DOM/JavaScript/render sink。若上游 source
format 或 consumer 引入 rendering，必須重新套 XSS gate，不得沿用 N/A。

## 完整 Ticket 30 與 Host blocker

即使未來 30A 通過，它也只關閉 fake/source-bound candidate projection，不關閉完整
Ticket 30。正式 A/B/C continuation 還需要每票 live Grant、owner/worktree/dependency
admission，以及在真實 effect 前的 qualified Host intercept。現行 same-lifetime lane 未有
該硬攔截；cross-lifetime `admit_dispatch` 也未完成此 ticket source readback。Declaration、
target index migration、implementation authority 或 Host capability 任一未完成，都不得
把清單 02、Ticket 30、dispatch 或 closure 標為完成。

## Stop／Return

對**source/test 實作派遣**，文件獨審及精確 baseline 綁定前返回：

```text
DOCUMENT_REVIEW_PENDING / NON_DISPATCHABLE
```

文件獨審／精確綁定通過後，按 Owner 已核准的條件式 Grant 記錄完整 baseline、
ticket blob、具名 owner／reviewer／worktree／branch，啟用唯一 `johnny-boundary`
並回 `AUTO_CONTINUE → IMPLEMENT`；不再索取相同範圍的 Owner 核准。
正式 source migration 和 Host effect 各維持後續獨立准入，不得以 30A 的綠燈
代替；不得把普通工程選擇升級成人工決策。

## 票面收斂與獨審紀錄

初稿 `76f6f32771e80add10c499db2c7479377b079c0c` 因推定 Grant、固定本專案
索引路徑、自創未遷移 grammar／公開 API 及硬行數上限，被獨立
`/root/wg_spec_review` 判為 `BLOCKED`。同票修正 `c5d6e2ff295883a03b49ffd3e8d72fbe51db0bb6`
撤回這些聲明；控制分支最終票面提交
`7e2dae948c5a949ad3f14aa0351f3b4edd0303f7` 由同一獨審者唯讀複驗
`PASS`，只代表 docs-only preflight 可用，不代表 implementation admission。
最終差異僅本 leaf 與同功能 registry；`git diff --check` 乾淨、
`tests/test_ticket_template_contract.py` 44 passed。完整 Ticket 30／清單 02
仍維持 `NON_DISPATCHABLE`。其後 Architecture Owner 在既有 SPEC 授權內收斂了上列
通用技術 source contract；這不是 target facts migration 或 implementation Grant。

## Source contract decision review — 2026-10-18

Architecture Owner 的 docs-only 決策提交 `0bfb4a2869f9fbb73e67a3c1a436a8e341fd66c2`
初審有兩項 source-binding finding：不能只讀 index 而不從 committed leaves 建圖，
以及既有字串型 blob result 不能證明 raw-byte digest。同票修正
`f13f35711594af241c83b803f91f0f472baa6241`（本 leaf blob
`823ef2d0e86bbc74a8508263be1a8bde678f6324`）由不同獨審席位唯讀複驗
`PASS`，兩項閉合；詳見
`doc/reviews/workflow-governance/30-trusted-independent-ticket-continuation-code-review.md`。
這只封閉通用 source schema 的技術選擇，不使 30A 可派工；target facts migration、
declaration readback、ticket-scoped Grant 與 qualified Host effect 均仍缺。
Root 在獨審之後對控制分支執行
`python -m pytest tests/test_mainline_projection.py tests/test_ticket_template_contract.py -q`：
`59 passed`、exit 0；`git diff --check` exit 0。這是既有純投影與模板回歸，
不是 30A source adapter 的 runtime 測試，也不代替上述獨審。
