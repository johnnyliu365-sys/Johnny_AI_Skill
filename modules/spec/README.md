# 模組規格

每個功能集群只有一份有效規格。`reusable-module-library.md` 已核准；其工單仍待使用者第二次核准，核准前不得建立實作或測試。

## 獨立規格

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Receipt-bound role supervision | [`receipt-bound-role-supervision.md`](receipt-bound-role-supervision.md) | Revision 01 `APPROVED`；Revision 02 receipt union／event／Debugger 為 `OWNER_REVIEW_REQUIRED`，未核准前 Senior 不得依新修訂拆票。 |
| Environment capability bootstrap | [`environment-capability-bootstrap.md`](environment-capability-bootstrap.md) | Revision 01 `APPROVED`；Revision 02 精確資源上限／本地模型 reservation 為 `OWNER_REVIEW_REQUIRED`，未核准前不得依新修訂拆票。 |

## 已核准隔離衝突修訂

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Adaptive project orchestration | [`adaptive-project-orchestration.md`](adaptive-project-orchestration.md) | Revision 06 `APPROVED`；Revision 07 角色／Context Library／seed／manifest 為 `OWNER_REVIEW_REQUIRED`；既有 admission leaf 不改寫。 |
| Context-load telemetry | [`context-load-telemetry.md`](context-load-telemetry.md) | Revision 02 `APPROVED`；Revision 03 receipt evidence／按需報表／zero-inference baseline 為 `OWNER_REVIEW_REQUIRED`；尚未授權報表執行或 provider call。 |
