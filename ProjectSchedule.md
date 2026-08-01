# 通用功能模組庫工作排程

## 現行階段

- 日期：2026-08-02（Asia/Taipei）
- 階段：`AWAITING_TICKET_CONFIRMATION`
- 目前功能集群：`reusable-module-library`
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
- 下一張候選：`08-python-line-transport-identity`；必須等待使用者明確確認後才可開始。
