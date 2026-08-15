# 模組規格

每個功能集群只有一份有效規格。`reusable-module-library.md` 已核准；其工單仍待使用者第二次核准，核准前不得建立實作或測試。

## 獨立規格

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Receipt-bound role supervision | [`receipt-bound-role-supervision.md`](receipt-bound-role-supervision.md) | Revision 01／02 `APPROVED`；Senior 可依 receipt union／event／Debugger 新修訂重新拆票，仍不得自行 dispatch 或啟用 heartbeat。 |
| Environment capability bootstrap | [`environment-capability-bootstrap.md`](environment-capability-bootstrap.md) | Revision 01／02 `APPROVED`；Senior 可依精確資源上限／本地模型 reservation 新修訂重新拆票，仍不得自行 dispatch、安裝或執行外部 effect。 |

## 已核准隔離衝突修訂

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Adaptive project orchestration | [`adaptive-project-orchestration.md`](adaptive-project-orchestration.md) | Revision 06／07 `APPROVED`；Senior 可依角色／Context Library／seed／manifest 新修訂重新拆票；既有 admission leaf 不改寫。 |
| Context-load telemetry | [`context-load-telemetry.md`](context-load-telemetry.md) | Revision 02／03 `APPROVED`；Senior 可依 receipt evidence／按需報表／zero-inference baseline 新修訂重新拆票；未授權報表執行或 provider call。 |
