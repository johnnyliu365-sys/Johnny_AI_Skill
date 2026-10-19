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

## 30G-SOURCE — Closure G1–G5 revision01 / current bounded construction

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

```johnny-boundary
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
