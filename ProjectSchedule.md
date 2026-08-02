# 通用功能模組庫工作排程

## 現行階段

- 日期：2026-08-02（Asia/Taipei）
- 階段：`ROUTER_FRAMEWORK_POC_DONE`
- 目前功能集群：`router-framework`；`reusable-module-library` 維持既有完成狀態，不與本 POC 混合。
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
