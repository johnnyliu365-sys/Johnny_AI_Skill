# P4｜把 Router 接進實際流程

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（Router 接線；上游為 P2 綁定與 P3 佇列，兩者皆已完成） |
| 第一步排查起點 | `library/local_orchestration/work_queue.py`（佇列契約） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision；worktree／branch 待派工時建立 |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 新增 `library/local_orchestration/dispatch_session.py` 與其測試 |
| 禁止修改 | `work_queue.py`、`worker_assignment.py`、`document_mutation_gate.py`、`dispatch_authority.py`、任何既有票 |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/local_orchestration/dispatch_session.py
modify = tests/test_dispatch_session.py
create = library/local_orchestration/dispatch_session.py
create = tests/test_dispatch_session.py
forbid = library/local_orchestration/work_queue.py
forbid = library/local_orchestration/worker_assignment.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = library/local_orchestration/dispatch_authority.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

派工與整合**走 Router**，不靠控制面記得去呼叫它。

## 現在的斷點：零件齊了，但沒有人用

P2 的綁定、P3 的佇列、08 的閘門都已完成並整合，但**三者都要控制面主動呼叫**。
實測：2026-08-21 整個工作階段的每一次整合，都是控制面手動下 `git merge` 或手動組
`DocumentMutationRequest`。零件存在不等於治理生效——**沒有被呼叫的閘門保護不了任何東西**。

## 兩個階段

1. **派工**：發 receipt → claim 指派 → 生工人（host 的事）三者成為一條路徑，
   任何一步失敗都不留下半套狀態。
2. **整合**：工人回傳 → settle → 入列 → 拉取 → **經閘門整合**。
   閘門不再是可選的呼叫，而是這條路徑唯一的整合方式。

## TDD 設計

1. 正常行為：一次完整往返，帳上留下 claim、settle、入列、拉取、整合各一筆。
2. 規則違反／輸入錯誤：整合繞過閘門 → 不可能（沒有第二條路徑）；以命名空間斷言證明
   本模組沒有直接呼叫 git merge 的能力。
3. 外部失敗／fail-closed：中途任一步失敗 → **不得留下半套狀態**（claim 了卻沒入列、
   或入列了卻沒 claim）。
4. 回歸保護：四個上游模組的既有行為與測試不受影響。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 路徑判斷由上游模組負責 |
| 2 | null／空字串／陣列 | 是 | 空佇列、無指派、無 receipt 三者行為各自明確 |
| 3 | 權限繞過 | **是** | 本模組不得繞過閘門整合；不得自行發 receipt |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | 每一步的失敗各自具名，不得折疊成同一個 |
| 6 | 例外是否會拋出 | 是 | 每一步失敗都 fail-closed 且不留半套狀態 |

## 完成定義與證據

- 一次完整往返的帳目可讀回，五筆紀錄齊全。
- **反向突變證據**：至少三組——讓中途失敗留下半套狀態、讓整合繞過閘門、
  讓失敗代碼折疊；各指名哪個測試轉紅、還原後轉綠。
- 全套件綠、零殘留，列出**完整**的 `FAILED`／`SUBFAILED` 清單。

## 不在本票範圍

commit 觸發的實機驗證（需要真的 runner），以及跨 host 的工人生成。

## 正式環境移植 SOP

不適用（本機協調，無 migration 或部署影響）。

## 完成回寫

- 實際檔案：待填
- commit：待填

```johnny-status
id = P4
title = 把 Router 接進實際流程
state = IN_PROGRESS
stage = D | 派工路徑 | OPEN
stage = I | 整合路徑 | OPEN
stage = M | 突變驗證 | OPEN
```
