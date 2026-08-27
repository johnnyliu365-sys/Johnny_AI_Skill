# 模組規格

每個功能集群只有一份有效規格。`reusable-module-library.md` 已核准；其工單仍待使用者第二次核准，核准前不得建立實作或測試。

## 獨立規格

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Receipt-bound role supervision | [`receipt-bound-role-supervision.md`](receipt-bound-role-supervision.md) | `APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED`；reviewer 可拆票／開票，仍不得自行 dispatch 或啟用 heartbeat。 |
| Environment capability bootstrap | [`environment-capability-bootstrap.md`](environment-capability-bootstrap.md) | `APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED`；reviewer 可拆票／開票，仍不得自行 dispatch、安裝工具或執行外部 effect。 |

## 已核准隔離衝突修訂

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Adaptive project orchestration | [`adaptive-project-orchestration.md`](adaptive-project-orchestration.md) Revision 09 draft | Revision 05–08 已核准範圍不變；Revision 09 procedural managed-artifact behavior 為 `OWNER_REVIEW_REQUIRED`，尚未授權開 R09 票或 dispatch。 |
| Context-load telemetry | [`context-load-telemetry.md`](context-load-telemetry.md) Revision 11 | `APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED`；既有 opaque storage、per-stream ledger/CAS、lock-bound transaction adapter 與 no-effect private composition binding 已交付；新增 Host Bootstrap root、Router runtime delegation、composition consumption 的責任拓撲，且僅授權第一張 source-only Router grant/denial contract 票。 |
