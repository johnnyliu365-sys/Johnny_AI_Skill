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
