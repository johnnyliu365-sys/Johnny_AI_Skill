# Private Router SaaS POC 工單集

> 對應規格：[SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26](../../spec/private-router-saas.md)。本工單集僅允許在專案負責人明確核准唯一工單後開始實作。

## 交付目標

完成一個由本機薄插件呼叫的 Private Router POC 垂直切片：跨邊界僅有正規化的匿名 metadata 與摘要，服務邊界回傳型別化的下一步／權限決策；本機原文與 ContextPacket 永不離開本機。

資料缺失、未授權或回應無效時，流程必須 fail-closed，不得猜測下一步、讀取原文或呼叫下游 Agent／Skill。

## 工單狀態

| 工單 | 垂直能力 | 狀態 | 前置條件 |
| --- | --- | --- |
| [01-private-router-metadata-gate](01-private-router-metadata-gate.md) | metadata-only 決策閘門、本機 context gate 與安全自動接續 | `DONE` | 實作、驗證、review 與 handoff 已完成 |

## 共同基準

- 規格：`SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26`（`APPROVED`）
- 變更：`CHG-20260804-008`
- Context：[private-router-saas/main.md](../../../doc/context/private-router-saas/main.md)
- docs-only baseline：`d378076`
- 交付環境：本機 POC；使用 fake transport／fake entitlement，未部署外部服務。

## 非範圍與交接

本工單不建立真實 OAuth、帳號、資料庫、付款、後端部署、網路送出器或商業化功能；它們只能在下一個經 Wayfinder、Grill、SPEC 與工單核准的階段處理。

完成後須保留 TDD 紅燈／綠燈、型別檢查、隱私 smoke test、review 與驗收證據，並依 [Workflow.md](../../../Workflow.md#review-handoff) 交接。
