# 模組規格

每個功能集群只有一份有效規格。`reusable-module-library.md` 已核准；其工單仍待使用者第二次核准，核准前不得建立實作或測試。

## 獨立規格

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Receipt-bound role supervision | [`receipt-bound-role-supervision.md`](receipt-bound-role-supervision.md) | `APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED`；reviewer 可拆票／開票，仍不得自行 dispatch 或啟用 heartbeat。 |
| Environment capability bootstrap | [`environment-capability-bootstrap.md`](environment-capability-bootstrap.md) | `APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED`；reviewer 可拆票／開票，仍不得自行 dispatch、安裝工具或執行外部 effect。 |
