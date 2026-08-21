# P4｜把 Router 接進實際流程

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（Router 接線；上游為 P2 綁定與 P3 佇列，兩者皆已完成） |
| 第一步排查起點 | `library/local_orchestration/work_queue.py`（佇列契約） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／worktree `.worktrees/p4`／branch `implement/p4-dispatch-session` |
| 實作語言 | Python 3.11 |
| 狀態 | `DONE` |
| 共同基準 | `5567520`（程式碼基準；worktree HEAD 為綁定 commit，派工訊息載明） |
| 實作者 | Fable 5（**Owner override record**：owner 於 2026-08-21 指定；依 `dispatch-model-profile.md` 分層，難票本應先派 Opus 5 Extra、失敗後才升 Fable——此為 owner 直接指派，非控制面選擇） | |
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

- **全套件責任**：三張票並行實作，實作者只跑本票邊界內的測試檔；全套件與殘留檢查由審閱者於整合前逐張執行（比照 governance 11 的責任轉移，這是審閱者的未完成義務，不得因實作者回報綠即視為滿足）。

## 不在本票範圍

commit 觸發的實機驗證（需要真的 runner），以及跨 host 的工人生成。

## 正式環境移植 SOP

不適用（本機協調，無 migration 或部署影響）。

## 完成回寫

- 實際檔案：`library/local_orchestration/dispatch_session.py`、`tests/test_dispatch_session.py`
- commit：`64cb1a2`，經 `admit_document_mutation` 判為 `INTEGRATED`
- **兩條路徑**：派工＝admit → claim → spawn（claim 先於 spawn：帳先於被記的事；spawn 失敗立即補償 settle，補償失敗獨立具名 `SPAWN_COMPENSATION_FAILED`）。整合＝settle → 入列（`record_worker_return`）與 peek → resolve → pull → 閘門（`integrate_next_work`），兩個進入點刻意分開以保住 P3 的解耦
- **沒有第二條整合路徑的證明是命名空間性質**：模組不持 subprocess／filesystem／發放面；六個上游進入點全部身分釘住（`is` 斷言）；越界 candidate 經此路徑必 REFUSED 且 main HEAD 不動（真 git repo 驗證）
- **誠實邊界**：settle 與 enqueue 之間無跨檔交易，中斷的回傳以 `RETURN_ENQUEUE_FAILED` 具名，下一次呼叫補完入列而非重複 settle；入列了卻沒 settle 的帳（本模組不可能產生）以 `RETURN_LEDGER_INCONSISTENT` 拒絕不修補
- **反向突變**：實作者四組（佇列 pre-flight、spawn 補償、subprocess 繞閘門、失敗碼折疊），SHA-256 驗證還原。審閱者另做一組不同方向的：整合端把佇列讀取失敗折疊成 `QUEUE_EMPTY`（C 族形狀）→ 恰好 1 紅（`test_an_unreadable_queue_is_never_reported_as_empty`），還原後 27 綠
- mypy --strict 對新模組無誤
- 全套件（受閘測試開啟）：1355 passed、1 skipped、3164 subtests、零 FAILED、無殘留

```johnny-status
id = P4
title = 把 Router 接進實際流程
state = DONE
stage = D | 派工路徑 | DONE
stage = I | 整合路徑 | DONE
stage = M | 突變驗證 | DONE
```
