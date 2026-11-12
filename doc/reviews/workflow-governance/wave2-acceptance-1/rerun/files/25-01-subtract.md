# 01｜subtract(a, b) 回傳 a - b

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（無 SPEC；需求直接取自 `doc/requirements/snapshots/calc/2026-11-12-v1.json` 的 REQ-CALC-002） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `CONTEXT.md` |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | `CONTEXT.md` |
| Agent Context binding | ticket calc/01 revision02 / receipt `doc/handoffs/2026/governance/receipts/calc-01-subtract-c1.md` / owner calc-subtract / worktree `.worktrees/calc-subtract` / branch `seat/calc-subtract` / baseline main |
| 實作語言 | Python 3.11，僅標準函式庫（`CONTEXT.md` › 實作語言） |
| 狀態 | `INTEGRATED`（candidate `4d68e3b1` landed by `integrate.py` as merge commit `d5905ee6` on `main`; queue entry `LANDED` on `main-queue`; receipts `doc/handoffs/2026/governance/receipts/calc-01-subtract-c1.md` (cells at `3c51c45`) and `doc/handoffs/2026/governance/receipts/calc-01-subtract-c2.md` (cells at `92d59c0`); review record `doc/reviews/calc/01-subtract-code-review.md`, revision02 correction review APPROVED） |
| 共同基準 | main |
| 實作者 | calc-subtract／`.worktrees/calc-subtract` |
| 審閱者 | `seat:ticket-review/61r-review` |
| 責任邊界 | `src/calc.py` 的 `subtract`；`tests/test_calc.py` 的測試與 contract 宣告；`tests/ledger/calc.json` 期望值帳本；收據與證據 |
| 禁止修改 | `add`、需求來源、快照、其他治理檔 |
| 環境 | LOCAL |

## 使用者拍板與可觀察結果

REQ-CALC-002：`subtract(a, b)` 對任意兩個整數回傳 `a - b`。

## 實作範圍、依賴與 ticket elements

- element 路徑：不適用
- 實際原始碼路徑：`src/calc.py`、`tests/test_calc.py`
- 公開契約／資料模型：`subtract(a: int, b: int) -> int`

## TDD 設計

1. 正常行為：subtract(5, 3) == 2
2. 規則違反／輸入錯誤：負數與零，subtract(3, 5) == -2、subtract(0, 0) == 0
3. 外部失敗／fail-closed：不適用（純函式，無外部依賴）
4. 回歸保護：既有 add 測試維持綠燈

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | 無路徑處理 |
| 2 | null／空字串／陣列 | 否 | 型別為 int，無空值輸入 |
| 3 | 權限繞過 | 否 | 無權限 |
| 4 | Token 格式與比較 | 否 | 無憑證 |
| 5 | 錯誤碼是否一致 | 否 | 無錯誤碼 |
| 6 | 例外是否會拋出 | 否 | 無外部依賴 |

## 完成定義與證據

- `python -m pytest -q` 全綠
- **紅燈輸出**：待實作者於首次紅燈時填入

## 正式環境移植 SOP

- 不適用（無 migration、環境變數）

## 完成回寫

- 實際檔案：待填
- commit：待填
- WorkProgress：不適用

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

審閱紀錄：`doc/reviews/calc/01-subtract-code-review.md`（在 main 上）。實作正確；退回的原因是票面缺口與證據缺口。

- **Closure set**：本票只關 REQ-CALC-002，並一併補上 REQ-CALC-001 的 contract 綁定（baseline 就缺）。Closure revision 為 revision02。
- **Profile**：`POC`，單一實作席位。**資源**：本機 Python 3.11 venv。**XSS**：不適用，理由是純函式，沒有瀏覽器、DOM 或不可信輸入。
- **Strict checker**：`mypy --strict --python-version 3.11 src tests`。**Allocation**：一個實作席位、一個獨立審閱席位。**Correlation**：`calc/01`，queue key 為 `calc-01-subtract@<candidate>`。
- **F1（票面）**：`contract_gate.py --repo . --snapshot doc/requirements/snapshots/calc/2026-11-12-v1.json --specs tests` 必須 exit 0。
  - `tests/test_calc.py` 的開頭註解區塊要宣告 REQ-CALC-001 與 REQ-CALC-002。
  - `source:` 寫 `doc/requirements/sources/calc.md`，附上它的 sha256。
  - 還要宣告 `mutation:`。
  - 期望值一律從 `tests/ledger/calc.json` 讀取，assert 裡不得出現字面期望值；`assertEqual` 也一樣，不只限於 `assert` 敘述。
- **F2（票面）**：新的修正派工檔 `calc-01-subtract-c1.md` 帶 `registry_commit`、`correction_ref` 與 `preflight:` 區塊。`preflight.py` 必須 exit 0，並放進收據。
- **F3（票面）**：本節補上 Closure set、Profile、資源、XSS、strict checker、allocation 與 correlation。審閱者已指定。
- **F4（證據）**：收據加上 strict checker 那一格。
- **F5（證據）**：加入超過 2**53 與超過 64 位元的案例。審閱者的 float 突變必須讓測試轉紅。
- 開工前先把 `origin/main` 合進 `seat/calc-subtract`。票面以 main 上的 revision02 為準。
- 收據的 cells 跑在 correction commit 上，至少要有：
  - tests、strict checker、contract gate、preflight；
  - 至少一個反向突變及其還原；
  - typed return（`ImplementationReturn: COMPLETED → ACTION_COMPLETED`）；
  - 每個選擇的 STATEMENT。

  收據放在之後另一個只加收據的 commit。送審候選是分支頂端。
- 狀態：修正完成、交付審閱時，狀態列維持 `IN_PROGRESS`；`DONE` 在審閱通過後才設定。
