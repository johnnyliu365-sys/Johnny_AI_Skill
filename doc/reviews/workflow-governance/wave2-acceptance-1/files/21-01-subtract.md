# 01｜subtract

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（fixture 專案無 SPEC；需求 `REQ-CALC-002`，見 `doc/requirements/snapshots/calc/2026-11-07-v1.json`） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `CONTEXT.md` |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket 01 revision02 / receipt `doc/handoffs/2026/governance/receipts/01-subtract.md` / owner calc-subtract / worktree `.worktrees/calc-subtract` / branch `seat/calc-subtract` / baseline `8e6ae013374fb683e565be49b15488dc500a565f` |
| 實作語言 | Python 3.11（`CONTEXT.md` 統一後端語言） |
| 狀態 | `INTEGRATED`（candidate `45fc3873` landed by `integrate.py` as merge commit `ebb77083` on `main`; queue entry `LANDED` on `main-queue`; review record `doc/reviews/calc/01-subtract-code-review.md`, convergence disposition APPROVED） |
| 共同基準 | `8e6ae013374fb683e565be49b15488dc500a565f` |
| 實作者 | calc-subtract worktree |
| 審閱者 | `seat:ticket-review/61b-review` |
| 責任邊界 | `src/calc.py` 新增 `subtract`；`tests/test_calc.py` 的測試與其 contract 宣告；`tests/ledger/calc.json` 期望值帳本；收據與其證據 |
| 禁止修改 | `add` 的行為、其餘檔案 |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

REQ-CALC-002：`subtract(a, b)` 對任意兩個整數回傳 `a - b`。

## 實作範圍、依賴與 ticket elements

- element 路徑：不適用
- 實際原始碼路徑：`src/calc.py`、`tests/test_calc.py`
- 公開契約／資料模型：`subtract(a: int, b: int) -> int`

## TDD 設計

1. 正常行為：`subtract(5, 3) == 2`
2. 規則違反／輸入錯誤：負數與零，`subtract(3, 5) == -2`、`subtract(0, 0) == 0`、`subtract(-4, -6) == 2`
3. 外部失敗／fail-closed：不適用，無外部依賴
4. 回歸保護：既有 `test_add`

### 適用的缺陷類別（依 `CodeReview.md` §2.1，逐一列出必要案例，不適用者寫明理由）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 無路徑輸入 |
| 2 | null／空字串／陣列 | 否 | 型別為 int，無可空輸入 |
| 3 | 權限繞過 | 否 | 無權限邊界 |
| 4 | Token 格式與比較 | 否 | 無憑證 |
| 5 | 錯誤碼是否一致 | 否 | 無錯誤碼 |
| 6 | 例外是否會拋出 | 否 | 無外部依賴 |

## 完成定義與證據

- `python -m pytest -q` 全綠
- **紅燈輸出**：待實作者填入

## 正式環境移植 SOP

- 不適用

## 完成回寫

- 實際檔案：`src/calc.py`、`tests/test_calc.py`、`tests/ledger/calc.json`
- commit：待填
- WorkProgress：待填

## 邊界宣告（revision02）

```johnny-boundary
modify = src/calc.py
modify = tests/test_calc.py
create = tests/ledger/calc.json
create = doc/handoffs/2026/governance/receipts/
modify = modules/tickets/calc/01-subtract.md
forbid = doc/reviews/
forbid = doc/requirements/
```

## Revision02（審閱 `CHANGES_REQUESTED` 後，control plane 重訂）

審閱紀錄：`doc/reviews/calc/01-subtract-code-review.md`（main 上）。實作本身正確；退回的是票面缺口與證據缺口。

- **Profile**：`POC`。**XSS**：不適用（純函式，無瀏覽器、DOM 或不可信輸入）。**Closure revision**：revision02。
- **F1（票面）**：`contract_gate.py --repo . --snapshot doc/requirements/snapshots/calc/2026-11-07-v1.json --specs tests` 必須 exit 0。
  - `tests/test_calc.py` 的開頭註解區塊宣告 `requirement: REQ-CALC-001` 與 `requirement: REQ-CALC-002`，各自的 `source:` 為 `doc/requirements/sources/calc-rows.json sha256:<該檔 blob 的 sha256>`，並宣告 `mutation:`。
  - 期望值不得以字面常數寫在 assert 裡，一律從 `tests/ledger/calc.json` 讀取（gate 的 `LITERAL_EXPECTED` 規則）。
  - REQ-CALC-001 的綁定在 baseline 就缺，一併補上。
- **F2（票面）**：本節補上 Profile、XSS 與 Closure revision，審閱者已指定。
- **F3（證據）**：收據加一格 `mypy --strict --python-version 3.11 src tests`。
- **F4（證據）**：收據還要補上四項：
  - contract gate 那一格；
  - 實際的冒煙指令；
  - typed return（`ImplementationReturn: COMPLETED → ACTION_COMPLETED`）；
  - STATEMENT，寫明 revision01 在審閱前就把狀態設成 DONE。
- **F5（證據）**：加入大數值案例（超出 64 位元，例如 `2**64` 與 `-2**64`）。審閱者的 64 位元回繞突變必須讓它轉紅。
- 開工前先把 `origin/main` 合進 `seat/calc-subtract`；票面以 main 上的 revision02 為準，seat 分支上 revision01 改的狀態列與完成欄位捨棄。
- 收據的 cells 跑在 correction commit 上。收據檔放在 correction 之後另一個只加收據的 commit；送審候選是分支頂端，審閱者確認兩者之間只差收據與票面。
- 狀態：correction 完成、收據就緒時，狀態列維持 `IN_PROGRESS`，交由審閱；`DONE` 由審閱通過後設定。
