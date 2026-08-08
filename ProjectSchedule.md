# 通用功能模組庫工作排程

## 現行階段

- 日期：2026-08-08（Asia/Taipei）
- 階段：`LOCAL_ORCHESTRATION_INSTALLER_POC_SPEC_DRAFT`
- 目前功能集群：`local-orchestration-installer` 正在規格化；既有 `autonomous-collaboration-audit` POC 已收斂至 handoff，`router-framework`、`context-load-telemetry` 與 `reusable-module-library` 維持既有完成狀態，不混入本 POC。
- 唯一工作流程：`Workflow.md`

## 順序

1. 建立共同 Context、PRD、需求變更、安全邊界與 SPEC，並取得使用者核准。
2. 拆成單一垂直工單並取得第二次核准。
3. 逐張工單依 TDD，在本專案重新實作、Smoke Test、review 與 handoff。

## 優先序

1. Python NLP 契約與規則式文字處理。
2. Python 金流契約、帳本與 idempotency 邊界。
3. Python 可靠性與 LINE transport 集群。
4. Kotlin 地理解析候選集群。
5. C# 遊戲規則候選集群。

## Ticket Handoff

- `01-library-root-and-readmes`：`DONE`（commit `9b218a9`）。
- `02-python-nlp-contracts`：`DONE`（commit `88fbfc0`）。
- `03-python-nlp-rule-parsers`：`DONE`（commit `d03880e`）。
- `04-python-nlp-provider-boundaries`：`DONE`（commit `02fa06f`；起始 rollback tag `rollback/ticket-04-start-20260801`）。
- `05-python-payment-contracts-ledger`：`DONE`（commit `17ed764`）。
- `06-python-payment-provider-reconciliation`：`DONE`（commit `6c7d9dc`）。
- `07-python-reliability-core`：`DONE`（commit `7b56135`）。
- `08-python-line-transport-identity`：`DONE`（commit `fd5187b`）。
- `09-python-event-timeline-audit`：`DONE`（commit `655f09d`）。
- `10-python-engagement-rules`：`DONE`（commit `f0a4bfc`）。
- 下一張候選：`11-kotlin-offline-geo-resolution`；必須等待使用者明確確認後才可開始。

## Router Framework POC

1. `01-poc-router-core`：`DONE`；已建立 Profile 驅動的路由核心、Context 引用映射與四個框架接點，並完成測試與 review。
2. POC 完成後，才依證據決定是否擴充為能接管真實專案的 MVP；不得自動升級。

## Module Application Skill POC

1. `01-module-catalog-skill`：`DONE`；已建立 READY 模組選擇卡、可攜 Codex skill 和新專案最小載入指引。
2. 後續套件發行或全域 skill 安裝必須由新的 CHG、SPEC 與 ticket 處理；目前只交付可版控的 repo 內來源。

## Plugin Distribution POC

1. `01-private-git-plugin`：`DONE`；已建立 repository-root plugin manifest、private Git marketplace catalog、接管 skill 與可拔除契約 README。
2. 個人 Codex 環境的實際安裝、啟用、停用與 marketplace 移除由使用者自行選擇；不得當作公司專案的 runtime 或 CI 依賴。

## Claude Code Plugin Distribution POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Wayfinder and specification | DONE | `SPEC-AI-WORKFLOW-CLAUDE-CODE-PLUGIN-DISTRIBUTION-20260802-01KZ4C6D8E0F2G4H6J8K0M2N4P` |
| Shared-skill Claude manifest and marketplace entry | DONE | `modules/tickets/claude-code-plugin-distribution/01-claude-code-plugin.md` |
| Static validation and code review | DONE | JSON, skill/plugin validation, 48 tests, 54 strict type-checked source files, and diff check |
| Live Claude Code smoke test | USER_ENVIRONMENT | `claude plugin validate .` after cloning with private-repository access |

## Context Load Telemetry POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Wayfinder, change, specification, and ticket | DONE | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` |
| Metadata-only telemetry and validator | DONE | `modules/tickets/context-load-telemetry/01-metadata-only-telemetry.md` |
| Test, type-check, and review | DONE | 55 tests, strict type checking across 56 source files, compile check, and review |

## Plugin Release 0.3.0

| Milestone | State | Evidence |
| --- | --- | --- |
| Change, specification, and release ticket | DONE | `SPEC-AI-WORKFLOW-PLUGIN-RELEASE-TELEMETRY-20260803-01KZ6F8G0H2J4K6M8N0P2Q4R6S` |
| Manifest and shared-skill packaging | DONE | `modules/tickets/plugin-release-telemetry/01-package-current-skill.md` |
| Validation and review | DONE | Plugin/skill validation, 55 tests, strict type checking across 56 source files, and diff check |
| Commit | DONE | `368d513` (`release: package plugin version 0.3.0`) |
| Push | IN_PROGRESS | Push the reviewed release and its documentation handoff to `origin/main` |

## Historical Private Router POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Wayfinder, Architecture, Grill, and ADR | DONE | `doc/context/private-router-saas/main.md`; `doc/adr/ADR-20260804-001-private-router-saas.md` |
| Change and specification draft | DONE | `CHG-20260804-008`; `modules/spec/private-router-saas.md` |
| Product-owner specification approval | DONE | Owner approved `SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26` on `2026-08-04` |
| Ticket planning and second approval | DONE | Project owner approved `01-private-router-metadata-gate` on `2026-08-04` |
| Implementation, test, review, and release | DONE | 64 tests, strict type check, compile, plugin validation, Code Review, and handoff completed for `01-private-router-metadata-gate` |

| Future commercialisation / deployment | SUPERSEDED | `CHG-20260805-010` changes the active objective to non-commercial multi-AI collaboration automation. |

## Continuous Workflow Governance POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Requirement change and Grill | DONE | `CHG-20260805-009`; `doc/context/workflow-governance/main.md` |
| Specification | DONE | `modules/spec/workflow-governance.md` (`APPROVED` on `2026-08-05`) |
| Ticket plan, named implementation owner, and second approval | DONE | `01-enforce-continuation-and-handoff` approved on `2026-08-05`; implementation worktree assigned and reviewer recorded. |
| Implementation, verification, review, and handoff | DONE | Implementation worktree completed at `a94e207`; independent 73-test / strict-type review is `APPROVED` in `doc/reviews/workflow-governance/01-enforce-continuation-and-handoff-code-review.md`; integrated by `2f545c8`. |

## Autonomous Multi-AI Collaboration and Audit POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Requirement change and Grill | DONE | `CHG-20260805-010`; `doc/context/autonomous-collaboration-audit/main.md` |
| Specification | DONE | `modules/spec/autonomous-collaboration-audit.md` (`APPROVED` on `2026-08-05`) |
| Ticket 01 dispatch | IN_PROGRESS | Owner selected `ONE_IMPLEMENTATION_AGENT` and confirmed `01-topology-dispatch-lanes` as delivered to the named existing implementation worktree; planning lane moved to Grill for ticket 02. |
| Ticket 02 / 03 | PLANNED | Ticket 02 is in planning-lane Grill; ticket 03 remains planned. Each receives authority only from its own future delivery confirmation. |
| Implementation, review, and handoff | IN_PROGRESS | Ticket 01 implementation owner synchronizes its own worktree, performs TDD and returns typed evidence. |

## Local Orchestration Adapter and Detachable Installer POC

| Milestone | State | Evidence |
| --- | --- | --- |
| Requirement change, Wayfinder, Architecture and Grill | DONE | `CHG-20260808-011`; `doc/context/local-orchestration-installer/main.md`; `doc/adr/ADR-20260808-003-local-orchestration-installer.md` |
| Specification | DONE | `modules/spec/local-orchestration-installer.md` was approved by the owner on `2026-08-08`. |
| Ticket 01 dispatch | WAIT_FOR_HUMAN | `01-owned-install-lifecycle` is selected and `IN_PROGRESS`; it has exactly one pending delivery-confirmation question. |
| Tickets 02–04 / implementation | PLANNED | They remain unselected. Ticket 01 receives source/test authority only from its own positive delivery receipt. |
