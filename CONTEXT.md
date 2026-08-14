# 通用功能模組庫

本檔案是本專案的共用事實來源。所有功能集群的 SPEC、工單與元素索引只能引用並補充本檔，不得覆寫其邊界。

## 已確認事實與共同邊界

- 專案目標：將使用者授權的既有本機專案中，可安全抽離的功能，重新實作為可重用、強型別且可測試的通用模組庫。
- 授權來源專案僅供唯讀參考：SourceProjectA、來源專案B、來源專案C `來源專案C` 與 `來源專案D`；本專案不得回寫、搬移或修改它們的任何檔案。
- 首要功能集群為：NLP、金流串接，以及可靠性、LINE transport、身份解析、地理解析、互動／遊戲規則等其他候選集群。
- 產物必須重新定義資料模型、公開介面、依賴與測試；不得直接複製來源專案的秘密、設定、營運資料、租戶資料、資料庫 schema、PII、憑證或網域業務規則。
- `來源專案D` 的 ML 訓練產物僅可作為離線分類／品質分析的參考，不能成為對外訊息、派單或付款決策的權威。
- SourceProjectA 金流原始碼受其 P0／P1 部署與驗證閘門限制；本專案只抽取可測試的付款契約、idempotency、帳本與 provider adapter 模式，不能宣稱相容或可啟用既有正式收款。
- 每個實作模組資料夾都必須有 README，說明責任、公開契約、相依、禁止用途、來源追溯與驗證命令。
- `private-router-saas` 是已完成、僅供追溯的 metadata-only Router POC；`CHG-20260805-010` 已撤銷其 SaaS、支付、entitlement、價格、商業化與服務部署方向。既有 POC 原始碼在獨立 cleanup ticket 前保留，不得視為現行產品承諾。
- 現行目標是本機、可拔除的多 AI 協作／稽核控制平面：使用者保有模型與專案；plugin 不作為客戶專案 runtime、CI、建置或部署相依。停用或移除 plugin 後，客戶專案必須仍可運作。
- 每張已核准工單在交付給具名 implementation owner 前，必須停在精確的 dispatch-confirmation 人類閘門；確認交付後，planning lane 自動進入下一個 Grill，ticket execution lane 在獨立 branch/worktree 持續執行、回傳、受控整合與稽核。
- 工作流程的 commit 只是可追溯的完成證據，必須轉為 `ACTION_COMPLETED` 並重新交由 Router 判定下一步；除 Profile 宣告的權限閘門外，不得因 commit、docs-only commit 或單一工作階段完成而停止。缺少必要來源、具名 owner、權限、能力或有效決策時必須 fail-closed，而不是假裝等待或自行繼續。
- 控制面 Agent 僅負責 Wayfinder、Grill、Context、SPEC、ticket、實作前 handoff、review 與 handoff。正式實作必須由另一位具名 implementation owner 完成；該 owner 如遇需求、公開契約、架構、前端組合或驗收變更，必須以 `REQUIREMENT_CHANGED` 回交控制面重新收斂。
- 只有 ticket 具名 reviewer 可控制 implementation Agent/task。實作者不得
  spawn、delegate、follow-up、steer、wait、interrupt 或 close 其他 Agent；
  角色名稱、model 或 prompt 不是 authority。Router effect gate 與 host tool
  surface 必須共同強制此規則，失敗固定為 `HALT / ROLE_FORBIDDEN`。
- `local-orchestration-installer` 是已開始規格化的 Windows 使用者層級 POC：目標是在 Agent UI 外建立由安裝器擁有的本機控制面、插件 payload 與 metadata-only runtime，並以一鍵解除安裝移除**僅由該安裝器建立**的內容。它不得寫入、刪除或成為任何目標／公司專案的 runtime、CI、版本控制或檔案依賴；現有手動 marketplace 安裝若非本安裝器所有，必須視為 foreign installation，不得覆寫或移除。

## 識別碼登錄

- SPEC 專案代號：`AI-WORKFLOW`。
- SPEC 功能鍵：全大寫 kebab-case，穩定對應 `modules/spec/<feature>.md`。
- SPEC 格式：`SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>`。

## 衍生 SPEC 索引

### `SPEC-AI-WORKFLOW-REUSABLE-MODULE-LIBRARY-20260801-01KYYV8YJFZ467BC1RGDNY64QP`｜通用功能模組庫

- 規格路徑：`modules/spec/reusable-module-library.md`
- 專屬 Context：`doc/context/reusable-module-library/main.md`
- 原引用章節：`已確認事實與共同邊界`
- 收斂結果摘要：已核准將來源專案的候選能力分為 NLP、金流與其他功能集群；只在本專案重新實作可驗證的通用邊界。
- 責任範圍：本機通用模組庫與 README；不含任何來源專案、部署、外部 provider、真實資料或憑證操作。
- PRD／需求變更：`PRD.md §1`／`CHG-20260801-001`
- 回掛 commit：待文件基準提交；工單待第二次核准。

### `SPEC-AI-WORKFLOW-ROUTER-FRAMEWORK-20260802-01KZ2M4P6R8T0V2X4Z6B8D0F2H`｜專案流程 Router 框架 POC

- 規格路徑：`modules/spec/router-framework.md`
- 專屬 Context：`doc/context/router-framework/main.md`
- 原引用章節：`Workflow.md §0 流程 Router`
- 收斂結果摘要：固定引擎只處理強型別狀態、關卡轉移、最小 Context 引用與能力 allowlist；個別專案以 Profile 定義 POC、MVP 與商用關卡條件。
- 責任範圍：本機 Python POC；Pydantic、LangGraph、OpenAI Agents SDK、Temporal 與 MCP 的可測接點；不執行真實 LLM、Temporal server、外部 MCP server 或部署。
- PRD／需求變更：`PRD.md §6`／`CHG-20260802-002`
- 回掛狀態：POC 實作、48 項測試、嚴格型別檢查與 code review 已完成；交付索引為 `modules/element/python/router-framework/01-poc-router-core/README.md`。後續任何真實專案升級仍須以新 CHG 重走 Workflow。

### `SPEC-AI-WORKFLOW-MODULE-APPLICATION-SKILL-20260802-01KZ2Q8V4N6R9T1X3Z5B7C9D1F3H`｜可重用模組選擇 Skill POC

- 規格路徑：`modules/spec/module-application-skill.md`
- 專屬 Context：`doc/context/module-application-skill/main.md`
- 原引用章節：`library/MODULE_CATALOG.md`
- 收斂結果摘要：先選擇最少 READY 模組，再載入其 README、公開 API 與精確契約；不再預設讀取整個 library。
- 責任範圍：可攜 skill、選擇卡與新專案模板入口；不含套件發行或任何專案寫入。
- PRD／需求變更：`PRD.md §7`／`CHG-20260802-003`
- 回掛狀態：POC 已完成並通過 skill validator 與 code review。

### `SPEC-AI-WORKFLOW-PLUGIN-DISTRIBUTION-20260802-01KZ3N5P7R9T1V3X5Z7B9D1F3H`｜Johnny AI Skill Plugin Distribution POC

- 規格路徑：`modules/spec/plugin-distribution.md`
- 專屬 Context：`doc/context/plugin-distribution/main.md`
- 原引用章節：`Workflow.md §0 流程 Router`、`skills/` 與 `library/MODULE_CATALOG.md`
- 收斂結果摘要：以 Git marketplace 安裝 repository-root plugin；plugin 僅提供 AI 控制平面，已核准的公司專案變更則由公司 repository 自主持有。
- 責任範圍：manifest、marketplace catalog、接管 skill 與 README；不含目標專案寫入、全域設定寫入、runtime、MCP、hook 或部署。
- PRD／需求變更：`PRD.md §8`／`CHG-20260802-004`
- 回掛狀態：POC 已完成靜態驗證與 code review；安裝至個人 Codex 環境為使用者後續選擇。

### `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` — Claude Code Plugin Distribution POC

- Specification: `modules/spec/claude-code-plugin-distribution.md`
- Worktree Context: `doc/context/claude-code-plugin-distribution/main.md`
- Scope: provide a Claude Code marketplace entry while retaining one shared `skills/` source and zero target-project dependency.
- PRD / change: `PRD.md §9`; `CHG-20260802-005`.
- Handoff state: static validation passed in feature commit `d662993`; a live `claude plugin validate .` run requires a Claude Code installation.

### `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` — Context Load Telemetry POC

- Specification: `modules/spec/context-load-telemetry.md`
- Worktree Context: `doc/context/context-load-telemetry/main.md`
- Scope: produce metadata-only evidence for baseline/router context-load comparison; no raw ContextPacket text is persisted.
- PRD / change: `PRD.md §10`; `CHG-20260803-006`.
- Handoff state: implementation and static validation passed in feature commit `319ae97`; docs-only handoff pending.

### `SPEC-AI-WORKFLOW-PLUGIN-RELEASE-TELEMETRY-20260803-01KZ6F8G0H2J4K6M8N0P2Q4R6S` — Plugin Release 0.3.0

- Specification: `modules/spec/plugin-release-telemetry.md`
- Worktree Context: `doc/context/plugin-release-telemetry/main.md`
- Scope: package the current Router telemetry and TDD/Code Review source in the existing shared Codex/Claude Code plugin.
- PRD / change: `PRD.md §11`; `CHG-20260803-007`.
- Handoff state: metadata update and static validation passed in feature commit `368d513`; release ready to push.

### `SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26` — Private Router SaaS POC

- Specification: `modules/spec/private-router-saas.md` (`APPROVED`).
- Worktree Context: `doc/context/private-router-saas/main.md`.
- Scope: private typed Router control plane, source-local Context resolution, private policy/Profile logic, user-facing terminology abstraction, and fake entitlement validation. No model hosting, raw-content transfer, real OAuth/payment, database, or production deployment.
- PRD / change: `PRD.md §12`; `CHG-20260804-008`.
- Handoff state: `01-private-router-metadata-gate` is complete and reviewed. The POC now has metadata-only requests, a fail-closed service boundary, local Context gating, and automatic continuation limited to declared safe transitions; real SaaS infrastructure remains a later MVP change.

### `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` — Continuous Workflow Governance POC

- Specification: `modules/spec/workflow-governance.md` (`APPROVED` on `2026-08-05`).
- Worktree Context: `doc/context/workflow-governance/main.md`.
- Scope: make `ACTION_COMPLETED` post-commit routing explicit; define automatic-continuation, human-wait, and fail-closed boundaries; require separate implementation ownership and frontend composition/DI handoff evidence.
- PRD / change: `PRD.md §13`; `CHG-20260805-009`.
- Handoff state: `01-enforce-continuation-and-handoff` is `DONE`. The named implementation worktree finished at `a94e207`; independent control-plane review is `APPROVED` in `doc/reviews/workflow-governance/01-enforce-continuation-and-handoff-code-review.md`, and reviewed implementation was integrated by `2f545c8`. The next declared Router stage is `HANDOFF`; only a new requirement may return to Grill.

### `SPEC-AI-WORKFLOW-AUTONOMOUS-COLLABORATION-AUDIT-20260805-01KZ7A2C4E6G8J0L2N4P6R8T` — Autonomous Multi-AI Collaboration and Audit POC

- Specification: `modules/spec/autonomous-collaboration-audit.md` (`APPROVED` on `2026-08-05`).
- Worktree Context: `doc/context/autonomous-collaboration-audit/main.md`.
- Scope: non-commercial positioning, collaboration-topology selection, dispatch-confirmation wait, parallel planning/ticket lanes, guarded branch/worktree provisioning, integration, Grill audit, and fixed handoff response format.
- PRD / change: `PRD.md §14`; `CHG-20260805-010`.
- Handoff state: the owner selected `ONE_IMPLEMENTATION_AGENT` and confirmed delivery of `01-topology-dispatch-lanes` on `2026-08-05`. This confirmation is the ticket-scoped implementation authority. Control-plane/reviewer remains Codex/current `main`; the existing separate implementation worktree is `workflow-implementation` / `codex/implementation-private-router-saas-01`. The implementation owner must synchronize this dispatch-record main commit before its first red test. Planning has automatically entered Grill for ticket 02; ticket 03 remains planned.

### `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` — Local Orchestration Adapter and Detachable Installer POC

- Specification: `modules/spec/local-orchestration-installer.md` (`APPROVED` on `2026-08-08`; ticket-specific dispatch is still required for implementation authority).
- Worktree Context: `doc/context/local-orchestration-installer/main.md`.
- Scope: Windows per-user installer/uninstaller, owned-install ledger, metadata-only local orchestration adapter, injected host registration adapters, and a guarded local Git port. The installer deletes only its recorded, verified owned payload and state; it never changes target projects.
- PRD / change: `PRD.md §15`; `CHG-20260808-011`; reviewer-gateway
  revision `CHG-20260814-018`.
- Handoff state: owner-approved specification is ready for ticket planning. Actual Codex/Claude host registration commands remain a capability contract to be validated in an approved implementation ticket; absent or non-removable host capability is an install-time fail-closed result, not a silent partial install.
- Revision `CHG-20260811-012`: add disposable Codex reviewer/implementer
  profile proof and receipt-bound lifecycle. Only reviewer receives orchestration
  tools; implementation multi-agent control must be physically unavailable or
  the host remains `INSTALL_BLOCKED`. This adds Tickets 06A-06C and changes
  Ticket 04 dependencies; it does not reopen completed tickets or change
  05A-05C/05S4 plugin lifecycle acceptance.
- Revision `CHG-20260814-018`: Johnny now owns the sole local orchestration
  gateway. Only the named reviewer may receive its exact receipt-bound
  capability; the implementation owner receives no gateway port/credential and
  its effective host session must separately prove built-in multi-agent tools
  absent. Integrated 06A remains truthful blocked evidence, planned 06B/06C are
  superseded by 06G0P-06G4. Dispatch preflight found that the integrated 06A
  result permits `SUPPORTED` with malformed process evidence, so 06G0P is the
  only eligible first child; 06G0 transport proof follows it. Current desktop
  CLI access denial and the profile-unaware App task
  creation contract remain measured blockers, not authorization for a prompt or
  undocumented-config workaround.
- Revision `CHG-20260812-014`: the exact reviewed version-one candidate must be
  pushed to remote `staging` with create-or-fast-forward-only semantics and SHA
  readback before release-build/system-integration begins. The former package
  Ticket 04 is a non-dispatchable parent decomposed into nine serial
  tickets with separate acceptance responsibility. The first packaged version
  is identified by source/staging SHA, pinned toolchain, manifest and artifact
  digests plus review evidence; later feature/architecture work starts from
  `staging` and cannot overwrite that immutable record. Manifest and installer
  source are independently implemented/integrated before candidate freeze/push;
  the release binary is later built from a clean export of that exact remote SHA.

### `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` — Guided Bootstrap and Adaptive Delivery

- 狀態：`DRAFT / OWNER_REVIEW_REQUIRED`。
- 來源：`CHG-20260813-016`、`CHG-20260813-017`、`ADR-20260813-008`、`ADR-20260813-009`、`PRD.md §17`、`doc/context/adaptive-project-orchestration/main.md`。
- 收斂結果：安裝與專案初始化分離；使用者確認精確初始化計畫後，專案文件與 implementer worktree 均由 target project 自主持有。先建立 reviewer，核准工單後才由 reviewer 建立或重用 implementer。
- 自適應原則：以風險、耦合、可逆性、不確定性、驗證環境與外部效果選擇 `COMPACT / STANDARD / HIGH_ASSURANCE`，並依證據選擇 implementer 模型能力與最少安全數量；不得用行數或專案大小單獨降級。
- 版本生命週期：第一版 POC 經獨立驗收後先凍結精確 commit／版本身分；後續功能與架構 ticket 只能從已驗證的 staging SHA 建立分支／worktree，再以 guarded integration 回到 staging。staging 不等於 release，也不取代 disposable effect 測試環境。
- 不變底線：reviewer-only orchestration、強型別、TDD、獨立 review、XSS／Secret／workspace／ownership／guarded integration 閘門不可調降。
- 邊界：不移動既有 worktree，不改 05S1R freeze，不授權 target-project mutation、host task creation、push、package、release 或 deployment。
