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
| Adaptive project orchestration | [`adaptive-project-orchestration.md`](adaptive-project-orchestration.md) Revision 10 | `APPROVED / R09A_TICKET_OPENING_AUTHORIZED`；absent/delete 與祖先 digest cascade 契約已閉合，R09A ticket 仍需另行核准才可 dispatch。 |
| Context-load telemetry | [`context-load-telemetry.md`](context-load-telemetry.md) Revision 11 | `APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED`；既有 opaque storage、per-stream ledger/CAS、lock-bound transaction adapter 與 no-effect private composition binding 已交付；新增 Host Bootstrap root、Router runtime delegation、composition consumption 的責任拓撲，且僅授權第一張 source-only Router grant/denial contract 票。 |

## 待 owner 精確核准的架構草案

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Workflow adoption activation and admission | [`workflow-adoption-activation.md`](workflow-adoption-activation.md) | `DRAFT / OWNER_EXACT_APPROVAL_PENDING`；未授權 target bootstrap、source、dispatch 或發布。 |
| Designerless UI co-design | [`designerless-ui-codesign.md`](designerless-ui-codesign.md) | `DRAFT / OWNER_EXACT_APPROVAL_PENDING`；未授權 design provider、UI source、implementation 或發布。 |
