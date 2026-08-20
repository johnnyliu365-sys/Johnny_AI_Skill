# 08｜文件變更閘門

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（治理能力；規範來源為 `Workflow.md` §文件層級、`AGENTS.md` P0 權限與所有權、`TEMPLATE.md` 責任邊界／禁止修改） |
| 規格撰寫 AI | 不適用 |
| 第一步排查起點 | `library/local_orchestration/dispatch_authority.py`（同形狀的既有閘門） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision／無 receipt／owner 待填／worktree 待填／branch 待填／baseline `2a6a3e7` |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `2a6a3e7` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 新增 `library/local_orchestration/document_mutation_gate.py` 與其測試；`TEMPLATE.md` 的邊界欄位改為機器可讀 |
| 禁止修改 | `dispatch_authority.py`、`worktree_containment.py`、任何既有票的內容、`AGENTS.md`、`Workflow.md` |
| 環境 | `LOCAL` |

## 使用者拍板與可觀察結果

一個 agent 動到自己票沒有宣告的檔案時，**那份變更進不了 main**，並留下具名拒絕與
journal。文件不再靠 agent 自律。

## 為什麼這是成本問題，不是文書問題

owner 指出的依賴鏈：**文件可信 → 派工可以最小 → 便宜的模型做得動 → 省 token。**

反例已經發生：控制面沒讀 `TEMPLATE.md` 就自創八張票的格式、自行新增
`doc/runbooks/dispatch-model-profile.md`、**自行刪除** `owner_status_surface.py`
與其十七個測試（只事後告知，無授權）。每一份漂移的副本，之後**每一個讀者**都要多花
context 判斷哪一份算數——成本是複利的。

閘門一鬆，最小派送與模型分層會**無聲失效**：票還在、規則還在，但已經不能拿來省任何東西。

## 執行點：整合，不是按鍵

**必須誠實面對的限制**：Router 是一個 Python 函式庫，不是檔案系統掛鉤。它無法阻止一個
擁有寫入工具的 agent 落下鍵。宣稱「動手前擋住」而實作在事後檢查，就是本專案登記簿
C 族的形狀。

因此閘門設在**變更成為共用真相之前**——即整合進 main 之前。worktree 是草稿，main 是
真相；草稿裡寫錯不構成治理失效，寫錯的東西進了版控才構成。

host 專屬的按鍵層攔截（例如某個 host 的 hook）**不屬於 Router**，那會讓它綁死在一個
host 上。若日後要做，是 host adapter 的責任。

## 三個門檻

| 動作 | 門檻 |
| --- | --- |
| 修改既有檔案 | 該路徑必須落在票的責任邊界內，且不在禁止修改內 |
| 新增檔案 | 需要明示授權。`Workflow.md` 已明文「不得建立平行的 Context、SPEC、ticket 或 review 來源」 |
| 刪除檔案 | 獨立且更高的門檻，不與修改同級——刪除不可逆 |

## 前置：邊界必須機器可讀

`責任邊界` 與 `禁止修改` 目前是自由文字，機器讀不了。改為明確的路徑清單
（glob 或前綴），與 `johnny-status` 同樣以宣告區塊承載。

**不得從自由文字推測路徑。** 推測出來的邊界會產生看起來成立的拒絕與放行，正是這個
閘門要防的東西。票沒有宣告可讀邊界時，回傳具名拒絕，不猜。

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／ticket owner：控制面（Opus 5）；不得實作此 ticket。
- implementation owner：`<派工時填入>`；於自己的 worktree 實作。
- reviewer：控制面（Opus 5）。
- **Owner override record**：`N/A`
- `ImplementationHandoff`：本票 revision。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／
  `CHANGE_DETECTED → REQUIREMENT_CHANGED`。

### 前端組合與依賴注入

**N/A reason**：純本機治理邏輯，不觸及任何 UI 邊界。

- 實際原始碼路徑：`library/local_orchestration/document_mutation_gate.py`
- 公開契約／資料模型：`DocumentMutationRequest`／`DocumentMutationResult`／
  具名的 `DocumentMutationFailure`（比照 `DispatchAdmissionFailure` 的有限列舉）

## TDD 設計

1. 正常行為：變更只動到宣告邊界內的檔案 → 放行。
2. 規則違反／輸入錯誤：動到邊界外、新增未授權檔案、刪除未授權檔案 → **三種各自具名**
   的拒絕，不得共用同一個代碼。
3. 外部失敗／fail-closed：票讀不到、邊界區塊缺失或無法解析 → 拒絕（不是放行）。
   **不知道邊界在哪，不等於沒有邊界。**
4. 回歸保護：`dispatch_authority` 既有行為不受影響；此閘門不得取得發放能力。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | **是** | 七種邊界全測：相等、多一字元（`doc/` vs `doc2/`）、尾斜線、大小寫（Windows）、URL 編碼、路徑遍歷（`a/../../b`）、空路徑 |
| 2 | null／空字串／陣列 | 是 | 邊界清單為空、變更清單為空、路徑為空字串三者行為必須各自明確 |
| 3 | 權限繞過 | **是** | 直接改檔 vs 間接（改 symlink／junction 指向邊界外、改 `.gitignore` 讓刪除不可見） |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | 三種拒絕對外可區分；對內原因碼唯一 |
| 6 | 例外是否會拋出 | 是 | 票不存在、邊界區塊壞掉、檔案系統錯誤各自 fail-closed |

## 完成定義與證據

- 三種門檻各有具名拒絕，且拒絕時**沒有任何變更進入 main**。
- **反向突變證據**（規則見 `implementation-tdd.md`）：至少三組——拿掉邊界比對、
  把新增降級成修改、把「讀不到票就放行」改回去；各指名哪個測試轉紅、還原後轉綠。
- 路徑比對的七種邊界案例全部有測試。
- 全套件綠、零殘留，列出**完整**的 `FAILED`／`SUBFAILED` 清單。

## 正式環境移植 SOP

不適用（本機治理邏輯，無 migration 或部署影響）。

## 完成回寫

- 實際檔案：`<待填>`
- commit：`<待填>`
- WorkProgress：不適用

```johnny-status
id = 08
title = 文件變更閘門
state = IN_PROGRESS
stage = B | 邊界機器可讀 | OPEN
stage = G | 閘門 | OPEN
stage = M | 突變驗證 | OPEN
```
