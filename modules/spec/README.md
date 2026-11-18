# 模組規格

每個功能集群只有一份有效規格。`reusable-module-library.md` 已核准；其工單仍待使用者第二次核准，核准前不得建立實作或測試。

## 獨立規格

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Environment capability bootstrap | [`environment-capability-bootstrap.md`](environment-capability-bootstrap.md) | `APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED`；reviewer 可拆票／開票，仍不得自行 dispatch、安裝工具或執行外部 effect。 |
| Local orchestration installer | [`local-orchestration-installer.md`](local-orchestration-installer.md), revision `04`, SHA-256 `c2af8d8b3a10418a1450ef44eaf3ee89c6494311ceb68f543a4ef7e0e75de0af` | `APPROVED / BOUNDED_TICKETING_AUTHORIZED` |

## 已核准隔離衝突修訂

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Adaptive project orchestration | [`adaptive-project-orchestration.md`](adaptive-project-orchestration.md) Revision 10 | `APPROVED / R09A_TICKET_OPENING_AUTHORIZED`；absent/delete 與祖先 digest cascade 契約已閉合，R09A ticket 仍需另行核准才可 dispatch。 |

## 已歸檔 SPEC

只保留歸檔 ID 與歸檔參照；歸檔規則見 `skills/johnny-project-takeover/references/requirement-lineage.md` 的「SPEC archive」。

| 歸檔 ID | 歸檔參照 |
| --- | --- |
| `ARCH-SPEC-20261118-001` | [`doc/archive/specs/2026/router-framework.md`](../../doc/archive/specs/2026/router-framework.md) |
| `ARCH-SPEC-20261118-002` | [`doc/archive/specs/2026/private-router-saas.md`](../../doc/archive/specs/2026/private-router-saas.md) |
| `ARCH-SPEC-20261118-003` | [`doc/archive/specs/2026/autonomous-collaboration-audit.md`](../../doc/archive/specs/2026/autonomous-collaboration-audit.md) |
| `ARCH-SPEC-20261118-004` | [`doc/archive/specs/2026/receipt-bound-role-supervision.md`](../../doc/archive/specs/2026/receipt-bound-role-supervision.md) |
| `ARCH-SPEC-20261118-005` | [`doc/archive/specs/2026/executor-routing.md`](../../doc/archive/specs/2026/executor-routing.md) |
| `ARCH-SPEC-20261118-006` | [`doc/archive/specs/2026/plugin-release-telemetry.md`](../../doc/archive/specs/2026/plugin-release-telemetry.md) |
| `ARCH-SPEC-20261118-007` | [`doc/archive/specs/2026/context-load-telemetry.md`](../../doc/archive/specs/2026/context-load-telemetry.md) |

## 已核准的功能集群架構

| 功能集群 | 規格 | 狀態 |
| --- | --- | --- |
| Workflow adoption activation and admission | [`workflow-adoption-activation.md`](workflow-adoption-activation.md) | `APPROVED / WA_01_TICKET_OPENING_AUTHORIZED`；未授權 target bootstrap、source、dispatch 或發布。 |
| Designerless UI co-design | [`designerless-ui-codesign.md`](designerless-ui-codesign.md) | `APPROVED / UIX_01_TICKET_OPENING_AUTHORIZED`；未授權 design provider、UI source、implementation 或發布。 |

兩個集群各自只產生 readiness evidence；共同 `PAQ-REL-01` 才能持有一次版本 bump、payload
重生／重釘、publication 與 Codex／Claude installed readback。若兩集群在同一 baseline
ready，必須合成一次 release，不得由 `WA-06`／`UIX-06` 分別發布。
