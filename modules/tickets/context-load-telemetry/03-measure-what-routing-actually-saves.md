# 03｜量出路由實際省下什麼（載入量，不是計費）

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 不適用（承接 `modules/spec/context-load-telemetry.md`；本票只做可算的那一半） |
| 第一步排查起點 | `library/workflow_router/profile.py`（路由表，106 個 `ProcessStage` 條目）與 `library/workflow_router/telemetry.py`（既有的記錄與換算機制） |
| PRD 索引 | 不適用 |
| 需求變更 | 不適用 |
| Sealed Context binding | 不適用 |
| Agent Context binding | 本票 revision；worktree／branch 待派工時建立 |
| 實作語言 | Python 3.11 |
| 狀態 | `IN_PROGRESS` |
| 共同基準 | `<派工時填入>` |
| 實作者 | `<派工時填入>` |
| 審閱者 | 控制面（Opus 5） |
| 責任邊界 | 新增 `library/workflow_router/context_load_report.py` 與其測試 |
| 禁止修改 | `telemetry.py`、`profile.py`、`contracts.py`（讀取，不修改） |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/workflow_router/context_load_report.py
create = library/workflow_router/context_load_report.py
modify = tests/test_context_load_report.py
create = tests/test_context_load_report.py
forbid = library/workflow_router/telemetry.py
forbid = library/workflow_router/profile.py
forbid = library/workflow_router/contracts.py
forbid = modules/tickets/
```

## 使用者拍板與可觀察結果

owner 拿得到一個**可辯護的數字**：「路由讓一次 stage 進入需要載入的參考資料，
從 X 降到 Y」——而且那個數字的計算方式攤在測試裡，任何人可以自己重算。

## 這張票**不**宣稱什麼（先寫，因為這是它最容易變成謊的地方）

**它量的是「應該載入多少」，不是「provider 實際計了多少 token」。**

- 來源是**路由表的宣告**與**檔案的實際大小**，不是任何 host 的計費回報。
- Token 數是**估算**（`telemetry.py` 既有的 `estimate_text_tokens`），不是真實用量。
- 因此任何輸出**必須自我標示為估算**。回報中不得出現「省下 N 個 token」這種讀起來像
  計費數字的說法；正確的說法是「載入量從 X bytes 降到 Y bytes（估算 T 個 token）」。

**這條是硬性的。** 本專案最貴的一族缺陷就是「敘述沒有發生的事」（governance 04）。
一份把估算講成實測的報表，比沒有報表更糟。

## 可算的素材（2026-08-22 實測）

| 素材 | 數字 |
| --- | --- |
| `references/` | 18 份，合計 **68,557 bytes** |
| `SKILL.md` | 7,756 bytes |
| `Workflow.md` | 18,616 bytes |
| 路由表條目 | `profile.py` 內 106 個 `ProcessStage` 引用 |

路由的主張是：進入一個 stage 時，agent 讀 `SKILL.md` ＋ `Workflow.md` 的相關列
＋ **該 stage 的路由列指名的那一份 reference**，而不是 18 份全讀。

## 要達成的事

一份報表，對**每一個 stage**回答：

1. **無路由基線**：全部 references 的合計大小（＋估算 token）。
2. **路由後**：該 stage 實際指名的 reference 大小（＋估算 token）。
3. **比值**與差額。
4. **整體摘要**：跨所有 stage 的平均與最壞情況。

資料**全部從 repo 自身推導**——路由表讀 `profile.py` 的既有結構，檔案大小讀檔案本身。
不需要任何執行期收集，因此**現在就算得出來**。

## 不可讓的性質

1. **不得寫死 reference 清單。** 從路由表與目錄實際內容推導；未來新增一份 reference，
   報表自動涵蓋。以測試釘住：加一份假 reference，基線數字必須改變。
2. **路由表指名但檔案不存在 → 具名失敗**，不得當成 0 bytes 忽略。
   （那正是 `ROUTE_REFERENCE_INVALID` 那一族——找不到就停，不憑記憶補。）
3. **估算標示不得可省略。** 輸出結構本身要帶「這是估算」的欄位，不是靠寫報表的人記得加註。
4. 報表**只讀不寫**——不得修改任何 repo 檔案或 Johnny root 內容。

## TDD 設計

1. 正常行為：給定路由表與 references 目錄，每個 stage 算出基線／路由後／比值。
2. 規則違反／輸入錯誤：路由指名不存在的檔案 → 具名失敗；空 references 目錄 → 具名失敗，
   不得回報「省了 100%」。
3. 外部失敗／fail-closed：檔案讀不到 → 具名失敗，**不得當成 0**。
4. 回歸保護：`telemetry.py` 的既有行為與測試完全不變（本票只讀它的估算函式）。

### 適用的缺陷類別（依 `CodeReview.md` §2.1）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | references 目錄的掃描不得掃進子目錄或相鄰目錄 |
| 2 | null／空字串／陣列 | **是** | 空目錄、路由表為空、stage 沒有指名 reference 三者各自具名，**都不得是「省了全部」** |
| 3 | 權限繞過 | 否 | 唯讀報表 |
| 4 | Token 格式與比較 | 否 | 不涉憑證 |
| 5 | 錯誤碼是否一致 | 是 | 檔案缺失、目錄空、路由表讀取失敗各自可區分 |
| 6 | 例外是否會拋出 | 是 | 每個讀取失敗 fail-closed |

## 完成定義與證據

- **反向突變證據**：至少三組——把 reference 清單寫死（新增假檔案後基線不變 → 轉紅）、
  讓缺檔當成 0 bytes、讓估算標示可省略；各指名哪個測試轉紅、還原後轉綠。
- **實際跑一次並把數字附在完成回寫裡**——本票的產出是那個數字，不只是程式碼。
- 實作者只跑邊界內測試檔；全套件與殘留檢查由審閱者於整合前執行。
- venv 建在 repo 外 ASCII 路徑，`pytest==9.1.1`。

## 不在本票範圍

**真實 provider 計費用量的配對比較**（見下方「為什麼 B 不在這裡」）；
把報表接進 CLI 或看板；跨專案的比較。

## 為什麼真實用量比較（B）不在這裡

不是「以後再做」，是**它有一個結構性難題，值得先寫下來**：

真正的配對比較要求**同一件工作做兩次**——一次不用 Router、一次用。但第二次已經被第一次
污染（答案已知、路徑已探過），所以兩次的 token 用量不可比。這不是工程問題，是實驗設計問題。

可行的近似有兩條，各有代價：

- **不同票、同難度分層**：拿多張同層級的票做統計比較。需要樣本量，而我們現在只有 20 幾張。
- **只記錄不比較**：把每次派工的 host 回報用量（Claude Code 的 subagent 回報有此數字）
  持久化，累積成基線。**這條是可做的，而且應該先做**——但它產出的是趨勢，不是對照組。

兩條都需要 P8（路由決策變成可查詢的資料）先落地，否則「這次派工用了哪一層、載了哪些
reference」還是只存在我的判斷裡，記錄下來也無法交叉比對。

## 正式環境移植 SOP

不適用（唯讀報表）。

## 完成回寫

- 實際檔案：待填
- commit：待填
- **實測數字**：待填

```johnny-status
id = 03
title = 量出路由實際省下什麼
state = IN_PROGRESS
stage = R | 報表推導 | OPEN
stage = H | 估算標示不可省 | OPEN
stage = M | 突變驗證 | OPEN
```
