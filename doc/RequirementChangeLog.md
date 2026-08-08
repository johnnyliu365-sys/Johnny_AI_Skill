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
| Linked specification | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` (`DRAFT`) |
| Acceptance | The approved specification must demonstrate a one-click normal uninstall that removes all verified owned components, an idempotent absence result, fail-closed foreign/tampered state, and proof that target repositories are untouched. |
