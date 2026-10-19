# Core capability implementation decision — revision01

Status: REVIEWABLE_DESIGN / EXTERNAL_ENROLLMENT_NOT_AUTHORIZED.
Parent: Owner's existing12-item local batch; original Ticket30 and workflow/adaptive
SPEC lineages. This plan selects implementation responsibilities, not a new PRD,
Router, policy engine, qualification verdict or production activation.
Baseline10b06f82c0825d6339d12712f0b2f752114c8790; assessment2026-10-19.

## 1. Determination from current evidence

| Subject | Actually present / verified | What remains to be built or proved |
| --- | --- | --- |
| Grant | dispatch_authority.py documents owner-intent marker; no protected issuer implementation in scoped local_orchestration/workflow_router | Protected Owner approval, authoritative plan store, authenticated direct readback, one-shot consume and owned read transport |
| Windows | NTFS; current process AdministratorEnabled=False (not proof of a separate standard account); CodexSandboxService.OpenAI.Codex running asLocalSystem | That vendor service is not a Johnny issuer; no modification/reuse as one. New trust separation must be enrolled and tested |
| Codex CLI | Installed0.163.0-alpha.10.2; SHA256F6DBF48CB70F62649C645F26C87DC9BF84CC36986202DFAD8E12FB5B8CA70312; --sandbox read-only, --ignore-user-config and feature switches exposed | Actual closed roster, permitted snapshot read and before-effect denial still unqualified; this CLI never qualifies Desktop |
| Claude CLI | Installed2.1.231; --tools, --strict-mcp-config, --setting-sources, --no-session-persistence and --max-budget-usd exposed | All-tools-off cannot meet CVQ's permitted-read positive. A dollar flag alone does not prove token/request/retry limits; prior offline UNAVAILABLE is retained |
| CVQ | Approved SPEC09 / wire05 at13fc7a760cb274d6927af0ab108b1cb09037127d, blobs089649eb7751c059815d0bc62bad9e2eb38df515 / cc04eb9dc97680b1e11285b677c4aba5b858a49e | controlled_verification package is absent from integrated control tree; B3 candidate27bb0129 remains blocked. Complete its already authorized source convergence first; no one-line-ready claim |

Read commands: exact CLI --version/--help, app-server --help and
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
uses qualified discovery. Source Review and protected observation precede operational
qualification. This plan does not waive any source/audit bootstrap requirement;
if native source-independent policy/observer cannot be enrolled without circular
self-certification, report that exact dependency for a bounded method-order decision.

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

## 5. Cost, order and one external decision

Estimates below are engineering planning ranges, NOT measured duration/token cost:
local grant contracts/ledger/client 1–2 engineer-days; protected Windows enrollment/
IPC/evidence 2–4; readonly protocol/adapter/qualification 2–4, plus existing CVQ/B3
source convergence. Native/runtime differences can produce an honest unavailable
result. Local source tests require no vendor fees. Maintenance: service/runtime
and CLI upgrades invalidate their exact protection/tool qualification; rerun the
affected finite cases, not every ticket. No per-ticket service installation.

Next30B slice is exact source-only authority client + ledger validation, not a new
remote attempt. Proposed additional900 command seconds: author450/reviewer300/
Root150, each command<=60s, initial+one correction, no stress/hidden retry. Includes
strict checks, issuer binding positives/negatives, durable one-winner/retry cases,
real algorithm regression and independent mutations. Rationale: two new source
responsibilities plus IPC comparison/readback and existing140-case surface,
conservative compile/import/mypy and finite failure reserve; actual usage recorded.
Original599.2/600 stays charged; approved ceiling would become1500, no platform
quota shortage is alleged. Operational Host attempts get their own later exact
manifest, not silently funded from these900s. Ticket46 has its own already-admitted
300s new local command-source allocation; it does not replenish30B.

Engineering choice: select local protected authority + native readonly Host route.
Owner's only new decision NOW is whether to permit that external trust-boundary
enrollment and the attached30B source-budget delta. We build/package the service,
configuration, fixture and verification recipe; Owner supplies OS consent/access,
not a finished issuer or Host product. Installation waits for reviewed source and
an exact executable/config/identity/rollback manifest; no blanket elevated command.

Alternative if this PC cannot host that boundary: deploy the SAME limited authority
API to a separately administered Windows host and use its authenticated transport.
This requires machine/admin/network access and protected deployment; it does not
assume an existing working service or ask Owner to implement one. Extra transport/
operations cost makes it the second choice. Neither option weakens the invariants.

Proposed precise reply: “核准本機受保護authority與原生readonly Host方案；准許在
受審來源及精確安裝/資格manifest備妥後，進行本機服務身分、受限主體、保護目錄/
IPC設定及零外部模型費用的有限Host qualification。30B保留599.2秒原帳，源碼
建置追加900命令秒，總上限1500；不授權真模型新費用、push、發布、部署到其他
專案、舊殘留刪除或未驗證正式閘門啟用。”

This candidate reply is not an active Grant. If declined, independently admitted
local work continues; the exact external effects wait. R0/DAP/TAL/Recovery and
30B/43 holds remain. Existing CVQ approval is not asked again.

## Sources for proposed primitives

- OpenAI official subagents: https://learn.chatgpt.com/docs/agent-configuration/subagents
- OpenAI app-server/versioned schema: https://learn.chatgpt.com/docs/app-server
- OpenAI provider/retry config: https://learn.chatgpt.com/docs/config-file/config-reference
- Claude CLI/hooks: https://code.claude.com/docs/en/cli-reference and https://code.claude.com/docs/en/hooks
- Windows authenticated pipe peer: https://learn.microsoft.com/en-us/windows/win32/ipc/impersonating-a-named-pipe-client
- SQLite transactions/durability: https://www.sqlite.org/lang_transaction.html and https://www.sqlite.org/atomiccommit.html
