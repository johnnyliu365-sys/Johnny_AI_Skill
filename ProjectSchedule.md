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
| Ticket 01 implementation | DONE / APPROVED / INTEGRATED | Closure `C1..C8` passed; implementation `ddd9f55`, correction `040a0f6`, review `dc63364` and guarded merge `491f98b`. |
| Ticket 02 implementation | DONE / APPROVED / INTEGRATED | Closure `D1..D8` passed; implementation `6cc8fb5`, independent review `4527f49`, guarded merge `92c58bf`; allocation and branch released. |
| Ticket 03 implementation | DONE / APPROVED / INTEGRATED | Closure `H1..H8`; implementation `16597b6`, H7 correction `673ff7c`, final review `5601594`, guarded merge `60cb8cf`; allocation and branch released. |
| Toolchain and Codex capability probe | DONE / VERIFIED | Inno Setup 6.7.3 is installed per user with valid signature and compile proof. One disposable Codex CLI marketplace/plugin was installed, hash-verified and completely removed without target-project access. |
| Parent Ticket 05 Codex CLI adapter | SUPERSEDED / CONVERGENCE_DECOMPOSED | Correction review found CR-80..CR-85; rejected branch/SHAs remain evidence and its allocation/receipt are closed. |
| Ticket 05A CLI contract/preflight | DONE / APPROVED / INTEGRATED | Implementation `97ab31c`; repaired handoff `fb755268`; review `d54c0bd`; owner-authorized ledger-preserving merge `b22c6c4`; post-merge verification passed. |
| Ticket 05B transactional registration | BLOCKED / TICKET_DEFECT | Implementation `5e919069` and handoff `ef1cf42` passed green/type/scope checks but initial review found CR-92..CR-97; finite ticket revision and readable ceiling decision are required before any correction. |
| Ticket 05C receipt removal/replay | PLANNED / DEPENDENCY_WAIT | Starts only after 05A/05B independent approval/integration. |
| Ticket 04 implementation | PLANNED / DEPENDENCY_WAIT | Pinned compiler is ready; package work waits for all decomposed Codex adapter children 05A–05C. |

### Ticket 05 selection after external capability proof

The owner-authorized probe resolved the two external uncertainties without
claiming that discovery code is production source. Codex CLI 0.144.0-alpha.4
completed exact marketplace add, plugin add, structured verification, plugin
remove and marketplace remove for a disposable local payload; matching source
and installed hashes plus final plugin/marketplace/path absence were recorded.
Inno Setup 6.7.3 was independently signature/version/compile verified.

Ticket `05-codex-cli-host-adapter` is now the sole selected vertical slice. It
must turn the documented CLI mechanism into strict receipt-bound adapter source
within K1–K8, four production files and one test. It uses exactly one branch in
the existing sole implementation worktree; no second live registration,
additional worktree, target-project access or schedule is authorized. Ticket 04
remains dependency-waiting until independent Ticket-05 approval and integration.

Initial independent review `dac99fd` reproduced false/escaping boundary results,
partial registration residue, foreign absence-proof acceptance and an adapter
contract incompatible with the documented CLI. Ticket design repair
`CLOSURE-LOCAL-INSTALL-T05-02` adds the missing installer-owned marketplace
source boundary and exact public JSON contract. The same implementation lane
received its one additive correction; Ticket 04 remains dependency-waiting.

The single correction review covered `c2ea3f8`, `3f6c41a`, `13d02de` and
`4c9525b`. Although focused/full tests and strict typing pass, the public CLI
JSON DTOs, canonical root/proof binding, finite failure mapping, cleanup proof,
foreign collision gate and evidence matrix still fail CR-80..CR-85. Ticket 05
is now `CONVERGENCE_REVIEW_REQUIRED`; no third same-closure correction,
integration, Ticket-04 dispatch, new branch or new worktree is permitted before
control-plane decomposition.

### Ticket 05 convergence decomposition

Owner instruction on 2026-08-10 authorized the required control-plane split.
The failed monolithic Ticket 05 is historical and cannot receive another
implementation correction. Its unchanged approved-SPEC outcome is now three
serial vertical slices: 05A makes the documented CLI/source/collision preflight
observable without mutation; 05B makes registration transactional with exact
receipt and verified current-attempt compensation; 05C makes receipt-bound
removal/replay conjunctive and enables the final `SUPPORTED` projection.

Evidence requirements remain inside each child closure rather than becoming a
horizontal test ticket. The original cumulative `400` production / `450` test
line ceilings remain the final cluster ceiling. Only 05A is selected, with one
unique receipt and one new-ticket branch in the existing sole implementation
worktree. The rejected parent branch remains immutable evidence; no second
worktree, concurrent 05B/05C branch, live mutation, packaging or schedule is
authorized.

### Ticket 05B selection and dispatch

Owner instruction `可以開始派工` on 2026-08-10 selects only Ticket 05B after
05A integration `b22c6c4`. The named implementation owner remains task
`019fcc9c-f34f-7d53-a313-c70c90bf3245` using `gpt-5.6-terra` at `xhigh` in the
single existing implementation worktree. The owner must preserve the clean 05A
branch at `fb755268`, then create `codex/implementation-codex-cli-registration-05b`
from the exact control dispatch commit. Handoff
`hnd_local_orchestration_install_05b_20260810`, allocation
`aln_local_orchestration_install_05b_20260810` and receipt
`rcpt_local_orchestration_install_05b_20260810` authorize only frozen closure
B1–B5. No second worktree, live Codex mutation, target-project write, Ticket
05C/04 work, merge, push, deployment or schedule is authorized.
