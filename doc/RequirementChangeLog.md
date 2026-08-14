# 需求變更紀錄

本檔案是已確認需求與正式介面變更的唯一歷程；不取代 `grill-with-docs → CONTEXT.md → to-spec → to-tickets → TDD` 主線。

## CHG-20260801-001｜建立通用功能模組庫

- 日期：2026-08-01（Asia/Taipei）
- 產品版本：`v0.1`
- 狀態：已納入已核准 SPEC，待工單核准
- PRD 索引：`PRD.md §1–5`
- 規格索引：`SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`（`APPROVED`）

### 決策摘要與理由

- 決策：在本專案建立通用模組庫，依 NLP、金流串接與其他同功能集群分類；來源專案保持唯讀。
- 理由：保留可重用能力，同時移除來源專案的業務耦合、秘密、環境與營運資料依賴。

### 需求變更內容

- 原有內容：本專案只有 AI 協作 Bootstrap 規範，沒有可重用功能模組。
- 變更後內容：啟用完整文件結構，經規格、工單與 TDD 後建立本機通用模組庫與 README。

### 變更後影響範圍

- 後端／API／Webhook：僅建立本機契約與 fake adapter；不連線或啟用外部服務。
- 資料庫／快取／Provider：建立可替換的抽象；不帶入來源 schema、資料或設定。
- 安全／成本／隱私／維運：禁止帶入 secrets、PII、tenant、營運資料與付款憑證。
- 規格／工單／TDD／`CONTEXT.md`：建立 `reusable-module-library` 的正式追溯鏈。

### 關聯技術方案與文件

- 可重用方案：來源專案C 的規則式文字解析；來源專案D 的 outbox、worker、state guard、emergency stop；SourceProjectA 的付款流程切分與多模態分析邊界；來源專案B 的強型別規則引擎。
- 排除方案：直接複製來源原始碼、來源資料表、Provider 設定、UI、部署配置或任何秘密。

## CHG-20260802-002｜新增可重用專案流程 Router 框架 POC

- 日期：2026-08-02（Asia/Taipei）
- 產品版本：`v0.2-router-poc`
- 狀態：已由使用者核准實作
- PRD 索引：`PRD.md §6`
- 規格索引：`SPEC-AI-WORKFLOW-ROUTER-FRAMEWORK-20260802-01KZ2M4P6R8T0V2X4Z6B8D0F2H`（`APPROVED`）

### 決策摘要與理由

- 決策：在既有通用模組庫旁建立本機 Router framework POC，作為日後接管任何專案時的流程引擎。
- 理由：現有流程嚴謹但共享 Context 會持續膨脹；Router 以最小來源視圖、capability catalog 與一次性引用映射維持可追溯性。

### 需求變更內容

- 原有內容：Workflow 只定義 Router 的治理規則，沒有可執行的強型別核心。
- 變更後內容：新增 Pydantic 契約、LangGraph transition、Agents capability adapter、Temporal human-wait skeleton 與 MCP source port；POC 不連線任何外部服務。

### 影響與控制

- Context：中央僅保存來源 URI、revision、span、一次性引用 ID、引用者指紋與目標產物；原文僅屬引用 Agent 的工作區。
- 安全／成本：禁止 Secret、付費 Provider、網路呼叫與真實專案寫入。
- 升級：POC 證據完成後才可由新的 `REQUIREMENT_CHANGED` 申請 MVP，必須重跑 Wayfinder。

## CHG-20260802-003｜新增可重用模組選擇卡與可攜 Skill

- 日期：2026-08-02（Asia/Taipei）
- 版本：`v0.3-module-selector-poc`
- 狀態：已由使用者核准實作
- PRD 索引：`PRD.md §7`
- 規格索引：`SPEC-AI-WORKFLOW-MODULE-APPLICATION-SKILL-20260802-01KZ2Q8V4N6R9T1X3Z5B7C9D1F3H`（`APPROVED`）

### 決策

以短卡片和 `$apply-reusable-modules` 取代全量模組閱讀。卡片只提供選擇與最小閱讀路徑；採用、實作與外部操作仍受目標專案 Workflow 控制。

## CHG-20260802-004｜將 Johnny AI Skill 發行為可拔除的 private Git plugin POC

- 日期：2026-08-02（Asia/Taipei）
- 版本：`v0.4-plugin-distribution-poc`
- 狀態：已由使用者核准實作
- PRD 索引：`PRD.md §8`
- 規格索引：`SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H`（`APPROVED`）

### 決策

將此 private GitHub repository 的 workflow、Wayfinder、Router 與既有 skills 包裝為 Git marketplace 可安裝的 Codex plugin。plugin 是外部控制平面；公司專案不可以它作為 runtime、CI、設定或來源碼依賴，拔除後只失去這套 AI 流程能力。

### 影響與控制

- 新增 plugin manifest、Git marketplace catalog、主接管 skill 與根目錄 README。
- marketplace 指向 repository root 的 Git URL 與 `main`；使用者可在自己的 Codex 環境安裝、停用或移除，這次不寫入任何使用者設定或公司專案。
- 不新增 MCP、App、hook、Secret、Provider、runtime service 或部署。
- 任何經公司專案核准採用的功能，必須成為公司專案自己的版本化、測試與 commit；禁止 symlink、Git submodule、cache import 或其他反向依賴。

## CHG-20260802-005 — Add Claude Code private plugin distribution

| Field | Value |
| --- | --- |
| Date | `2026-08-02` |
| Requested by | Project owner |
| Change | Make the existing detachable Johnny AI Skill usable from Claude Code in addition to Codex. |
| Decision | Add root Claude plugin and marketplace metadata that discovers the same `skills/` source; document user-scope install, update, invocation, and removal. |
| In scope | `.claude-plugin/`, shared README instructions, and compatible Codex manifest metadata. |
| Out of scope | Target-project changes, copied skills, runtime dependencies, hooks, MCP, services, and secrets. |
| Linked specification | `modules/spec/claude-code-plugin-distribution.md` |
| Acceptance | Static repository validation must pass; `claude plugin validate .` remains an explicit user-environment smoke test because Claude Code is absent from this workspace. |

## CHG-20260803-006 — Add Router context-load telemetry

| Field | Value |
| --- | --- |
| Date | `2026-08-03` |
| Requested by | Project owner |
| Change | Add local, metadata-only telemetry so matched baseline and Router runs can prove or reject a claim of reduced Agent context. |
| Decision | Extend the Router POC with strict JSONL evidence records, source fingerprints instead of raw text/URIs, provider usage capture fields, and fail-closed pair validation. |
| In scope | `library/workflow_router/`, Router tests, local usage guide, and formal evidence documents. |
| Out of scope | Company repository telemetry commits, raw prompt/source capture, secrets, external telemetry services, and a production supervisor. |
| Linked specification | `modules/spec/context-load-telemetry.md` |
| Acceptance | Only comparable provider-reported input-token pairs may report reduction; all invalid evidence fails closed. |

## CHG-20260803-007 — Package current skill as plugin release 0.3.0

| Field | Value |
| --- | --- |
| Date | `2026-08-03` |
| Requested by | Project owner |
| Change | Package the latest workflow source, including Router telemetry and updated TDD/Code Review rules, as the existing Codex and Claude Code plugin. |
| Decision | Release the shared-skill source through the existing marketplace identity; increment only the Codex semantic manifest version to `0.3.0` and keep Claude Code commit-SHA versioning. |
| In scope | Plugin metadata, shared skill/README release guidance, validation, review, commit, and push. |
| Out of scope | Target-project files, ZIP artifacts, runtime service, automatic provider telemetry, hooks, MCP, or secrets. |
| Linked specification | `modules/spec/plugin-release-telemetry.md` |
| Acceptance | Both platform manifests and skills validate; tests/type checks remain green; release remains detachable and target-project independent. |

## CHG-20260804-008 — Add private Router SaaS POC control plane

| Field | Value |
| --- | --- |
| Date | `2026-08-04` |
| Requested by | Project owner |
| Previous rule | Johnny AI Skill is a static, detachable private Git plugin. Its local skill and Router POC have no remote service, entitlement check, or protected decision logic. |
| Changed rule | Introduce a separate private Router SaaS POC. A thin local plugin submits only typed pseudonymous metadata, account-scoped salted revision digests, stage events, entitlement mode, and finite structured redacted-summary claims. A private Router returns typed decisions and user-facing action labels; core Profiles and policy logic remain private. |
| Reason | A static delivered skill exposes its core logic and cannot safely provide a controlled, commercial Router path. The owner selected a private Router SaaS while prohibiting customer raw-content transfer and model hosting. |
| In scope | POC contracts, test-only private service port, fake entitlement, local privacy validation, complete POC transitions, terminology mapping, Architecture/Grill/specification, and later approved tests. |
| Out of scope | Raw source/document/prompt/path/URI upload, model hosting or payment, real OAuth/payment/webhook/database/production deployment, SLA, target-project dependency, and a claim of platform-wide enforcement. |
| PRD | `PRD.md §12` |
| Context | `doc/context/private-router-saas/main.md`; `CONTEXT.md §衍生 SPEC 索引` |
| ADR | `doc/adr/ADR-20260804-001-private-router-saas.md` |
| Linked specification | `SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26` (`APPROVED` on `2026-08-04`) |
| Impact and controls | Existing approved Router, telemetry, and plugin POCs remain unchanged. All missing entitlement, metadata, approval, capability, service, or contract conditions fail closed. Source and ContextPacket content are structurally excluded from service contracts and persistence. |

## CHG-20260805-009 — Govern post-commit continuation and separated frontend implementation

| Field | Value |
| --- | --- |
| Date | `2026-08-05` |
| Requested by | Project owner |
| Previous rule | The Router and takeover skill describe safe automatic continuation, while the control/implementation split and frontend composition/DI requirements were documented in commit `7769710`. The documentation did not make a completed commit an explicit non-terminal Router event or define the return contract between a control-plane Agent and a separate implementation owner. |
| Changed rule | A commit is evidence for `ACTION_COMPLETED`, never an implicit terminal state. The Router must immediately classify the next declared transition as `AUTO_CONTINUE`, `WAIT_FOR_HUMAN`, or `HALT`. Future formal frontend tickets must carry a composition and dependency-injection handoff; every implementation owner must return evidence or a typed change event to the control plane. |
| Reason | The owner observed an avoidable workflow stop after a commit and requires the loop to continue without ceremonial confirmation. Role separation also needs a concrete handoff/return boundary so frontend design remains testable and no Agent silently changes approved architecture. |
| In scope | Workflow/skill/template policy, Router event and handoff contract, frontend composition/DI requirements, Context/PRD/specification/ticket traceability, and static validation in a future approved ticket. |
| Out of scope | Target-project runtime dependency, automatic creation of a new host-model turn, external Agent dispatcher, background worker, bypassing platform approvals, source/test/deployment implementation in this control-plane task, or retroactive changes to completed tickets. |
| PRD | `PRD.md §13` |
| Context | `doc/context/workflow-governance/main.md`; `CONTEXT.md §衍生 SPEC 索引` |
| Linked specification | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` (`APPROVED` on `2026-08-05`) |
| Acceptance | The approved future policy must make post-commit re-routing observable, distinguish legitimate approval waits from failures, require a named separate implementation owner before implementation, and block formal frontend tickets that lack composition-root and DI evidence. |

## CHG-20260805-010 — Reposition to non-commercial autonomous multi-AI collaboration

| Field | Value |
| --- | --- |
| Date | `2026-08-05` |
| Requested by | Project owner |
| Previous rule | The active direction included a private Router SaaS POC, commercial pricing/validation language, and a single project-stage Router that moved a ticket directly toward implementation after approval. The workflow did not model a user-confirmed ticket dispatch followed by concurrent planning and ticket-execution lanes. |
| Changed rule | The active direction is a non-commercial, detachable multi-AI collaboration and audit workflow. After a committed ticket names its implementation owner, the control plane asks whether it has been delivered. No response is `WAIT_FOR_HUMAN`; a confirmed dispatch is that ticket's scoped approval, starts its execution lane and immediately routes the planning lane to the next Grill. Branch/worktree provisioning, integration and Grill audit must proceed automatically when their typed evidence is valid. |
| Reason | The owner wants a complete autonomous workflow with no non-essential pauses, not a commercial SaaS. The flow must support one or two collaborating coding Agents while retaining explicit human authority only for real approvals and ticket-dispatch confirmation. |
| In scope | Repositioning documents; collaboration topology selection; project and ticket Router lanes; typed dispatch confirmation; worktree/branch lifecycle; guarded integration; post-integration Grill audit; fixed ready/handoff response; Router/profile/skill/template/test changes in a later approved ticket. |
| Out of scope | SaaS, pricing, billing, customer accounts, entitlements, hosting, private Router service, model hosting, target-project runtime coupling, automatic host-model-turn creation, bypassing platform approvals, and source/test implementation before ticket delivery confirmation. |
| Historical treatment | `CHG-20260804-008`, `modules/spec/private-router-saas.md`, ADR-20260804-001 and their completed POC remain historical evidence. They are superseded for future direction, not deleted or retroactively rewritten. |
| PRD | `PRD.md §12` (historical) and `PRD.md §14` (active) |
| Context | `doc/context/autonomous-collaboration-audit/main.md`; `CONTEXT.md §衍生 SPEC 索引` |
| Linked specification | `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` (`APPROVED` on `2026-08-05`) |
| Acceptance | The approved specification must define that an opened ticket immediately becomes `IN_PROGRESS` and asks its one dispatch question; exact human versus automatic-event waits; typed events; parallel-lane ownership; safe Git integration; audit/rework return behavior; host capability limits; and the fixed project-owner response format. |

## CHG-20260808-011 — Add local orchestration adapter and one-click detachable installer

| Field | Value |
| --- | --- |
| Date | `2026-08-08` |
| Requested by | Project owner |
| Previous rule | The active workflow is a detachable plugin and local Router POC. It has no real user-scope runtime, physical installer/uninstaller, durable local orchestration adapter, host lifecycle adapter or guarded real-Git port. Manual Codex/Claude marketplace installation remains separate from a company project. |
| Changed rule | Add a Windows-first, per-user Local Orchestration Adapter and matching one-click installer/uninstaller POC. Its normal uninstall must remove the installed plugin payload, runner, queue, checkpoints, ledger, launcher and only the Codex/Claude registrations it created; no target/company project may be touched. |
| Reason | The owner requires a detachable plugin that is useful as a local automation control plane but can be cleanly removed in one action. A plugin that leaves its runtime or host registration behind is not acceptable. |
| In scope | Typed metadata-only local runtime; owned-install ledger; runtime lifecycle; local queue/checkpoint; injected host lifecycle adapters; strict project registry and guarded Git port; user-scope Windows setup/uninstall package; install/update/status/remove tests and documentation. |
| Out of scope | Target-project modifications or dependencies; forced model turns or host-login bypass; raw Context/source/prompt/path/URI/Secret/PII capture; remote Router/SaaS/MCP/Temporal service/database; system-wide/admin install; network deployment; removal of foreign/manual plugins; automatic push or deploy. |
| Host capability boundary | A host is supported only when a tested adapter can detect, create and remove a registration with an installer-owned receipt. Missing CLI, user authentication, host policy, incompatible lifecycle or a pre-existing foreign registration is `INSTALL_BLOCKED`; the installer must clean up its staging area and never report a partial success. |
| PRD | `PRD.md §15` |
| Context | `doc/context/local-orchestration-installer/main.md`; `CONTEXT.md §已確認事實與共同邊界` and `§衍生 SPEC 索引` |
| ADR | `doc/adr/ADR-20260808-003-local-orchestration-installer.md` |
| Linked specification | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` (`APPROVED` on `2026-08-08`) |
| Acceptance | The approved specification must demonstrate a one-click normal uninstall that removes all verified owned components, an idempotent absence result, fail-closed foreign/tampered state, and proof that target repositories are untouched. |

## CHG-20260811-012 — Restrict implementation-Agent control to the named reviewer

| Field | Value |
| --- | --- |
| Date | `2026-08-11` |
| Requested by | Project owner |
| Previous rule | The workflow separates control-plane/reviewer and implementation ownership, but Codex multi-agent tools are enabled by default and no installed role profile or effect gate proves that an implementation owner cannot create or control another Agent. |
| Changed rule | Only the ticket's named reviewer may create, dispatch, follow up, steer, wait for, interrupt or close implementation Agents/tasks. An implementation owner receives one approved ticket, works alone in its own worktree and returns typed evidence; every direct or indirect implementation-side orchestration attempt is `HALT / ROLE_FORBIDDEN` before host effect. |
| Reason | The project owner requires a high-trust reviewer/specification role to control lower-cost implementation roles and forbids an implementer from recursively creating or controlling more implementers. |
| In scope | Workflow/skill/review policy; typed reviewer-role authority gate; disposable Codex custom-agent capability proof; receipt-bound reviewer/implementer profile install and complete removal; exact negative replay/forgery/indirect-path tests. |
| Out of scope | Target-project files; model hosting; forced model turns; platform-wide claims; Claude support before a separate capability proof; network, Secret, push, release or deployment. |
| Official host fact | Current Codex documentation states that multi-agent tools are enabled by default, custom agents are config layers, and `agents.enabled=false` disables multi-agent tools. Whether that key is safely effective inside an implementation custom-agent layer is an unproven host capability and must be tested in a disposable `CODEX_HOME`; inability to prove it is `INSTALL_BLOCKED`, not a prompt-only fallback. |
| Affected specifications | `modules/spec/autonomous-collaboration-audit.md` revision 02 and `modules/spec/local-orchestration-installer.md` revision 02. |
| Ticket impact | Add autonomous Ticket 04 and local Tickets 06A-06C; update Windows package Ticket 04 dependencies. Completed tickets and 05A-05C/05S4 behavior remain immutable unless their own acceptance is independently changed. |
| Acceptance | A valid exact reviewer dispatch succeeds once; copied/forged/replayed reviewer authority and every implementation-owner orchestration surface fail with `ROLE_FORBIDDEN`; install/remove leaves no owned agent profile or target-project change. |

## CHG-20260812-013 — Require tiered XSS review from architecture through Code Review

| Field | Value |
| --- | --- |
| Date | `2026-08-12` |
| Requested by | Project owner |
| Previous rule | Security review prohibited injection generally, but workflow architecture, SPEC, tickets, TDD and Code Review did not require a closed XSS classification or distinguish ordinary browser impact from JavaScript-accessible host capability. |
| Changed rule | Any untrusted data rendered through Browser, WebView, HTML/DOM renderer or JavaScript execution context must enter XSS Review. If JavaScript can reach Native Bridge, IPC, Extension API or another privileged capability, review escalates to the complete JavaScript-to-host effect graph. |
| Reason | XSS inside a privileged desktop/plugin context can expand beyond a web session into host program authority; prevention must be designed and tested before implementation rather than discovered after code is written. |
| In scope | Workflow architecture/Grill, Context, SPEC and ticket classification; source-to-sink and privileged capability matrices; isolated renderer TDD; fake bridge/IPC/extension negative tests; Code Review sink/capability enumeration and reversal. |
| Out of scope | Adding a renderer to the current POC, live browser/host effects, target-project changes, new runtime dependencies, push, release or deployment. |
| Current project impact | The local-orchestration-installer POC is `XSS_NOT_APPLICABLE` because it has no Browser/WebView/HTML/DOM/JavaScript context. The approved SPEC and Context now record that reason; every future renderer ticket must classify again and cannot inherit this result. |
| Acceptance | `AGENTS.md`, `Workflow.md` and `CodeReview.md` define the mandatory tiered gate; affected SPEC/tickets cannot implement without a named classification and test matrix; privileged tests fail closed before fake host effect and preserve one exact authorized positive case. |

## CHG-20260812-014 — Add staging warm backup and immutable version-one package convergence

| Field | Value |
| --- | --- |
| Date | `2026-08-12` |
| Requested by | Project owner |
| Previous rule | Package Ticket 04 combined build configuration, payload assembly, installer UI, install smoke, uninstall/absence verification and release evidence in one future implementation ticket. The repository had no remote `staging` branch and no formal boundary separating an immutable first packaged version from later feature or architecture work. |
| Changed rule | After all runtime/host prerequisites are approved and integrated, separately implement and independently integrate the pure payload-manifest contract and bounded Inno installer/build source. Freeze that exact clean `main` candidate and publish it to remote `staging` by branch creation or verified fast-forward-only push with exact SHA readback. Only then may release build/system-integration tickets start, and the release build uses a clean export of that remote SHA. Decompose Ticket 04 into serial 04A-04I acceptance responsibilities, including separate manifest, installer source, Windows environment, build, install and uninstall acceptance. Bind the first packaged version to immutable source/staging SHA, pinned toolchain, manifest and binary digests plus review evidence; later feature/architecture work starts from `staging` through normal change control. |
| Reason | Preserve an off-machine warm source backup before higher-risk system integration, prevent a broad package ticket from obscuring failures, and keep a stable first-version identity while allowing later development to continue from a known reviewed baseline. |
| In scope | Remote staging preflight/publication/readback; package-ticket decomposition; exact version-one source/toolchain/manifest/artifact identity; serial disposable install and uninstall acceptance; subsequent development baseline rule. |
| Out of scope | Immediate push of the current unfinished POC; pushing `main`; force-push, reset or silent conflict resolution; public release, deployment, code signing, auto-update, target-project mutation, Secret handling or binary publication before its own gate. |
| Current repository fact | `origin` currently exposes `main` at `cbdfa7751c21c0355cb3aaaae5b7f045d9e84154` and no `staging` ref; local `main` is ahead. This fact requires a future exact candidate gate and does not authorize publishing the current incomplete baseline. |
| PRD / Context / ADR | `PRD.md §15`; `doc/context/local-orchestration-installer/main.md`; `doc/adr/ADR-20260812-006-version-one-staging-and-package-convergence.md` |
| Affected specification/tickets | `modules/spec/local-orchestration-installer.md` AC-11/AC-12; local package parent 04 decomposed into 04A-04I. |
| Owner authority | The owner explicitly authorizes the future 04D staging push after 04A/04B package-source integration and 04C exact-candidate approval. That authority is limited to safe create-or-fast-forward publication of the exact candidate and mandatory readback; any mismatch or divergence halts. |
| Acceptance | No release-build/system-integration child starts before remote `staging` equals the complete-source frozen candidate. Each child owns one bounded acceptance concern. The final version-one record is complete and immutable, while later feature/architecture work begins from `staging` and receives a new change/ticket lineage. |

## CHG-20260813-015 — Move disposable repository tests into a project-owned runtime namespace

| Field | Value |
| --- | --- |
| Date | `2026-08-13` |
| Requested by | Project owner |
| Previous rule | Integrated 05S1 requires each disposable environment root to be a direct child of the resolved OS `%TEMP%` directory. Failed runs can therefore leave globally shared `johnny-stage-env-*` residue discovered by another worktree, while that later ticket has no authority to clean it. |
| Changed rule | Every 05S1-based repository test environment is rooted below the exact current plugin checkout at `tests/.johnny-runtime/`. Each worktree owns a separate namespace. No test may create, scan or clean an OS-global `johnny-stage-env-*` namespace or place the runtime in a target project. Exact marker-bound teardown removes only its lease and an empty runtime parent; stale/unclaimed residue blocks without automatic deletion. |
| Reason | Test artifacts should be attributable to the project/worktree that created them. Locality prevents cross-worktree TEMP collisions and makes crash residue visible without granting broad host cleanup authority. |
| In scope | 05S1 allocator root admission, exact ignore rule, all integrated direct test callers, stale-residue/reparse/marker TDD, tracked/ignored/OS-TEMP/target-project non-interference, and dependent E3D/E4 refreeze. |
| Out of scope | Installed product root, target-project files, production package staging, live Codex/user profile, OS-global cleanup, new worktree, network, push, release or deployment. |
| Context / ADR | `doc/context/local-orchestration-installer/main.md`; `doc/adr/ADR-20260813-007-project-owned-disposable-test-runtime.md` |
| Affected specification | `modules/spec/local-orchestration-installer.md` / AC-13 |

## CHG-20260813-016 — Add guided project bootstrap and adaptive delivery profiles

| Field | Decision |
| --- | --- |
| Status | `REQUIREMENT_APPROVED / SPEC_DRAFTED / TICKETS_NOT_CREATED` |
| Previous rule | Installation exposed plugin/runtime capabilities but did not define one explicit project bootstrap flow. The collaboration POC asked for a fixed Agent count before planning and otherwise applied substantially the same documentation and verification ceremony regardless of project or ticket risk. |
| Changed rule | Installation provides only a Johnny-owned README and initialization entry point. After a selected target Git repository passes read-only preflight, one explicit confirmation authorizes exact target-owned project artifacts, a project-local ignored `.johnny/worktrees/` execution root and reviewer activation. Implementers are created/reused later only by the reviewer for receipt-bound tickets. A typed `COMPACT / STANDARD / HIGH_ASSURANCE` assessment selects documentation depth, verification breadth, implementation model capability and the minimum safe lane count for each ticket. |
| Reason | Small, reversible work should not pay the same ceremony cost as privileged, destructive or cross-boundary work, while project size alone must never downgrade security or authority controls. The primary experience should be guided automation, with README/manual steps as recovery rather than the normal workflow. |
| In scope | Install/init separation, exact preview and confirmation, target-owned artifacts, project-local worktree lifecycle, reviewer-first activation, evidence-based delivery profiles, model capability tiers, bounded lane count, reviewer-owned read-only research support and reclassification. |
| Out of scope | Silent target writes, installer-time project selection, forced/unverified host turns or models, model-name authority, unbounded Agent fan-out, implementation-owner delegation, moving existing worktrees, current 05S1R scope, push, release or deployment. |
| Security invariants | Reviewer-only orchestration, exact receipt/workspace/owner binding, strong types, TDD, independent review, XSS/Secret/ownership gates and guarded integration apply to every profile. Hard escalation triggers can only increase assurance. |
| PRD / Context / ADR / SPEC | `PRD.md §17`; `doc/context/adaptive-project-orchestration/main.md`; `ADR-20260813-008`; `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` |
| Current gate | Owner review of exact AC-01 through AC-10; ticket files and implementation remain blocked until SPEC approval. |
| Ticket impact | New bounded Ticket 05S1R atomically migrates the allocator and seven integrated direct test callers. E3D and E4 are `REQUIREMENT_CHANGED / 05S1R_DEPENDENCY`; their uncommitted work remains preserved pending explicit disposition. |
| Acceptance | No `from_system_temp` path remains; every disposable lease is below the exact plugin checkout runtime parent; no case creates or cleans `%TEMP%/johnny-stage-env-*`; stale project-local residue blocks and remains byte-identical; successful full verification leaves tracked, ignored, runtime, target-project and OS-TEMP sentinels unchanged/absent as applicable. |

## CHG-20260813-017 — Require post-POC staging development lifecycle

| Field | Decision |
| --- | --- |
| Status | `REQUIREMENT_APPROVED / SPEC_DRAFT_REVISED / TICKETS_NOT_CREATED` |
| Previous rule | `CHG-20260812-014` preserves this repository's first packaged version and says later work begins from remote staging, but the adaptive target-project workflow did not yet require the same lifecycle for every user's accepted first POC. |
| Changed rule | After a target project's first POC is independently reviewed and accepted, Johnny freezes its exact commit/version identity and requires a confirmed staging-transition plan. Every later feature or architecture ticket branch/worktree must descend from the admitted staging SHA and return only through guarded integration. Staging is neither release nor a disposable effect-test environment. |
| Reason | Users without software-delivery experience need a safe default that preserves the known-good first result, provides a recoverable integration lineage and prevents accidental direct development on the only stable baseline. |
| In scope | Local staging creation/readback, separately authorized remote create-or-fast-forward publication, exact ancestry enforcement, immutable POC/version identity, guarded staging integration and clear separation from disposable effect testing and release promotion. |
| Out of scope | Creating a branch or worktree now; automatic push; force/reset/delete; target-project mutation; package/build/install; release/deployment; changing the active 05S1R ticket or existing implementation lanes. |
| Safety invariants | POC review/acceptance and exact commit must exist first. Local Git mutation requires the confirmed plan; remote mutation requires separate authority and history/SHA readback. Wrong/stale/dirty/diverged baselines halt before source, Git, Agent or host effect. |
| PRD / Context / ADR / SPEC | `PRD.md §17`; `doc/context/adaptive-project-orchestration/main.md`; `ADR-20260813-009`; adaptive orchestration SPEC AC-11. |
| Current gate | Exact AC-01 through AC-11 and the revised eight-ticket candidate decomposition remain `OWNER_REVIEW_REQUIRED`; no formal ticket or implementation is authorized. |
| Acceptance | A reviewed/accepted POC can produce one exact local staging baseline; authorized remote publication is create-or-fast-forward-only with exact readback; all later ticket bases prove descent from staging; frozen POC/version bytes and identity remain unchanged; staging never claims release or effect-test authority. |

## CHG-20260814-018 — Replace host-profile-only orchestration with the Johnny reviewer gateway

| Field | Decision |
| --- | --- |
| Status | `REQUIREMENT_APPROVED / SPEC_REVISION_APPROVED / TICKETS_REPLANNED` |
| Previous rule | `CHG-20260811-012` expected two Codex custom-agent profiles plus a shared Router gate to prove that reviewer tools were present and implementation tools absent. Integrated Ticket 06A truthfully returned `INSTALL_BLOCKED / ROLE_ISOLATION_UNPROVEN / ACCESS_DENIED / OUTPUT_UNAVAILABLE`; 06B/06C therefore could not start. |
| Changed rule | Johnny owns the sole local orchestration gateway. Only the ticket's named reviewer may receive a receipt-bound gateway capability. An implementation owner receives neither gateway port nor credential, and its effective host session must also disable/remove built-in multi-agent/thread-control tools. Every effect binds the exact project, ticket, reviewed handoff, unconsumed receipt, target owner, worktree, branch, expected baseline, action, correlation and live pending descriptor. Direct, indirect, copied, forged, replayed, aliased or mismatched paths fail before effect. |
| Reason | A host profile alone cannot establish sole ownership of orchestration when the supported task-creation transport cannot prove that the intended profile was applied. Centralizing effects in Johnny supplies one auditable authority boundary while retaining host-level least privilege as a second independent control. |
| In scope | Workflow and Code Review governance; local installer Context/SPEC; transport capability proof; pure receipt-bound gateway authority; owned restricted-profile lifecycle; reviewer-only composition; disposable end-to-end role-isolation acceptance. |
| Out of scope | Prompt-only enforcement; undocumented host configuration edits; adding a network/MCP service; live user Codex mutation; target-project write; new worktree; push, package, install, release or deployment. |
| Current host facts | Official Codex configuration documents `agents.enabled` and `features.multi_agent` controls plus custom-agent configuration layers. In this environment the desktop-bundled Codex executable resolves under WindowsApps but direct shell invocation is access-denied, while the currently exposed App task-creation surface has no custom-agent/profile binding input. These are capability facts, not permission to invent an adapter. |
| Impact on prior tickets | 06A remains immutable, integrated truthful blocked evidence. Planned autonomous Ticket 04 and local 06B/06C are `SUPERSEDED` by 06G0P-06G4. Package 04A-04I remain dependency-waiting. Dispatch preflight found that 06A's result contract permits `SUPPORTED` with malformed process evidence, so 06G0P is the only eligible first child; 06G0-06G4 remain dependency-waiting. |
| PRD / Context / ADR / SPEC | `PRD.md §15`; `doc/context/local-orchestration-installer/main.md`; `doc/adr/ADR-20260814-010-reviewer-owned-orchestration-gateway.md`; `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` revision 03. |
| Acceptance | 06G0P first makes supported process evidence a finite, constructible and enforced state. Then one supported local transport launches or binds the exact restricted implementation session in the exact assigned worktree and proves effective built-in tool absence; one reviewer-only gateway positive path reaches a fake effect; all implementation, replay, foreign, mismatch and alias paths reach zero effects; install/remove owns only exact profile/gateway artifacts and preserves foreign/global/target state. Any unavailable effective readback remains `INSTALL_BLOCKED / ROLE_ISOLATION_UNPROVEN`. |

## CHG-20260814-019 — Make Router enforce tiered model handover and low-model admission

| Field | Decision |
| --- | --- |
| Status | `REQUIREMENT_APPROVED / SPEC_REVISION_APPROVED / ROUTER_PHASE_ONLY` |
| Previous rule | The Router POC selected generic capabilities and the adaptive orchestration draft selected model tiers/resources, but neither closed when the architecture owner may sleep, when the supervisor must wake it, whether a ticket is safe for a low-cost implementer, or how optional UI design sources affect routing. |
| Changed rule | The human owner and highest-capability architecture owner converge and approve the SPEC; a typed readiness gate then hands control to a Terra supervisor/reviewer, which compiles the approved SPEC into admitted tickets for a Luna implementation owner. The Router owns finite sleep/wake, decomposition/admission and design-source decisions. Figma is optional and never forced. |
| Ticket closure | One observable closure, one implementation owner, one primary change/effect boundary, a finite TDD matrix, deterministic verification and zero unresolved design decisions. Split by behavior/state/effect/ownership/verification, never by line or file count. |
| Wake triggers | Ambiguous/contradictory SPEC, undefined public contract, architecture or cross-ticket conflict, changed requirement, unprovable AC, new external/privileged boundary, high-assurance trigger or bounded model-capability convergence failure. |
| UI source rule | `FIGMA`, `SCREENSHOT`, `DESIGN_BRIEF`, `EXISTING_DESIGN_SYSTEM` and `NONE` are valid source kinds. Capability state determines use/wait/fallback/halt. Runtime renderer flow alone determines XSS applicability. |
| In scope now | Governance references and adaptive SPEC revision; then pure typed Router contracts/profile/decision/preflight tests in bounded serial tickets. |
| Paused | 06G0P independent review/integration, 06G0-06G4, package/staging/build/install/remove and all other rework/new feature tickets until Router acceptance. Existing commits remain immutable evidence. |
| Out of scope | Provider API, live model invocation, forced Figma/plugin installation, target-project write, new worktree, push, packaging, install, release, deployment, Secret or other host effect. |
| PRD / Context / ADR / SPEC | `PRD.md §17`; `doc/context/adaptive-project-orchestration/main.md`; `ADR-20260814-011`; adaptive orchestration SPEC revision 02 / AC-12 through AC-14. |
| Owner approval | Approved in the control conversation on `2026-08-14`; implementation remains ticket/receipt/owner bound and independently reviewed. |

## CHG-20260815-020 — Seal shared Context before ticket planning

| Field | Decision |
| --- | --- |
| Status | `REQUIREMENT_APPROVED / SPEC_REVISION_03 / ROUTER_PHASE_ONLY` |
| Previous rule | Minimal Context routing limited source loading, but did not prevent supervisors, ticket splitters or later lanes from appending shared `CONTEXT.md`; historical ticket/handoff state accumulated there. |
| Changed rule | Shared project Context is architecture-owned, drafted only in `ARCHITECTURE`/`GRILL` and sealed at `CONTEXT` before SPEC approval. Every later role is read/reference-only. Missing or changed shared facts return upstream; revision requires architecture ownership, approved change authority and the exact prior sealed revision. |
| Content boundary | Stable cross-feature facts, invariant boundaries and metadata-only indexes are allowed. Ticket/progress/handoff/commit/test/review/worktree state and duplicated SPEC/policy prose are forbidden. No hard line-count limit is used. |
| Router impact | R01's completed revision-03 commits remain immutable evidence but their policy digests become stale. Refreeze R01 metadata, then implement one independent shared-Context lifecycle gate before model-role or ticket-admission work. |
| Out of scope | Target-project mutation, new worktree, moving historical evidence, 06G0P review/integration, package, staging push, install, release, deployment or Secret handling. |
| Owner approval | Required directly by the project owner in the control conversation on `2026-08-15`. |
