# NN｜<垂直切片名稱>

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 完整 `SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>`（`§x、AC-y`） |
| 規格撰寫 AI | `<AI>` |
| 第一步排查起點 | `doc/context/<feature>/<worktree-id>.md` |
| PRD 索引 | `PRD-YYYYMMDD-NNN`／不適用 |
| 需求變更 | `CHG-YYYYMMDD-NNN`／不適用 |
| Sealed Context binding | `<shared revision/digest + exact feature Context revision/digest>`／不適用 |
| Agent Context binding | `<ticket revision / receipt / owner / worktree / branch / baseline / side_context_id>` |
| 實作語言 | 填入 `CONTEXT.md` › `## 實作語言規範` 的**統一後端語言**（不是從清單挑選）。偏離須先滿足該節觸發條件、有實測依據並經需求變更核准。**實作者不得自行決定**；未填不得進入 `implement`，審閱一律 `BLOCKED`。 |
| 狀態 | `PLANNED`／`IN_PROGRESS`／`BLOCKED`／`DONE`／`SUPERSEDED` |
| 共同基準 | `<docs-only commit SHA>` |
| 實作者 | `<AI／worktree>` |
| 審閱者 | `<AI／worktree>` |
| 責任邊界 | `<In Scope>`；**權威來源是下方 `johnny-boundary` 區塊**，本欄只是給人看的摘要 |
| 禁止修改 | `<Out of Scope>`；同上，權威來源是 `forbid =` |
| 環境 | `LOCAL`／`STAGING`／`PRODUCTION` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

`library/local_orchestration/document_mutation_gate.py` 在變更整合進 `main` 之前
讀這個區塊，比對這條分支實際動到的檔案。**閘門讀的是 `main` 上這張票的版本**，不是
候選分支上的版本——否則要放寬邊界的那次變更就能順手改掉自己被比對的規則。

上面表格的兩欄是自由文字，機器讀不了；**不得從自由文字推測路徑**，推測出來的邊界會
產生看起來成立的拒絕與放行。沒有這個區塊、或區塊解析失敗，閘門一律拒絕整合（不是
放行）：不知道邊界在哪，不等於沒有邊界。

```johnny-boundary
# 每行一筆。四個 key 對應三個門檻加一條禁令；同一路徑要做兩件事就寫兩行。
# 結尾 `/` 表示「這個目錄與其下全部」；沒有結尾斜線就是精確路徑，
# `doc` 不涵蓋 `doc/a.md`。單層萬用字元用 `*`，不跨 `/`。
modify = <可修改的既有檔案或目錄，至少一筆；缺此欄不得整合>
create = <可新增的路徑；不寫就是一個都不准新增>
delete = <可刪除的檔案，只接受精確路徑、不得用萬用字元；不寫就是一個都不准刪除>
forbid = <明確禁止的路徑；比上面三欄優先，且比對時不分大小寫>
```

三個門檻不同級，因為三件事的後果不同：

| 動作 | 門檻 | 拒絕代碼 |
| --- | --- | --- |
| 修改既有檔案 | 落在 `modify` 內，且不在 `forbid` 內 | `MODIFICATION_OUTSIDE_BOUNDARY` |
| 新增檔案 | 需在 `create` 明示授權（預設一個都不准） | `CREATION_NOT_AUTHORIZED` |
| 刪除檔案 | 需在 `delete` 逐一列出**精確路徑**；刪除不可逆，不與修改同級 | `DELETION_NOT_AUTHORIZED` |

`delete` 不收萬用字元是刻意的：拿掉一個模組與它的十七個測試要寫十八行，而那正是
「自行刪除 `owner_status_surface.py` 與其十七個測試」當時缺的那道摩擦力。

改名同時算一次刪除與一次新增，兩邊都要授權；symlink 與 submodule 進不了閘門，因為
它們指向的東西閘門看不到也框不住。

## 使用者拍板與可觀察結果

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：`<AI／worktree>`；負責需求收斂、SPEC／ticket、實作前 handoff 與 review，不得實作此 ticket。
- implementation owner：`<另一位 AI／worktree>`；負責 TDD、正式原始碼、測試、驗證與 commit。
- reviewer：`<AI／worktree>`；不得與 implementation owner 共用 worktree。
- **Owner override record**：`N/A`／`<專案負責人、日期、單張 ticket、例外範圍與原因>`；未有明確記錄不得由同一 Agent 承擔控制面與 implementation owner。
- `ImplementationHandoff`：`<approved SPEC/ticket/Context/TDD 引用、角色 ID、前端組合引用（如適用）>`；只存 metadata reference，不可保存原文、prompt、path、URI、Secret 或 PII。
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`；實作者不得靜默修改需求、公開契約、架構或 UI/DI 邊界。

### 前端組合與依賴注入（僅正式前端 ticket 必填）

- UI 組合邊界（screen／layout／component）：`<composition>`
- Composition Root 與依賴生命週期：`<path / scope>`
- 注入的具名介面（API、state、navigation、clock、feature flag、analytics、i18n、權限等）：`<interfaces>`
- production binding 與 test fake／stub：`<bindings>`
- 元件輸入／輸出、loading／empty／error、權限與可存取性驗收：`<acceptance>`

非前端 ticket 必須填寫 **N/A reason**：`<為何不觸及正式 UI 邊界>`。禁止元件內建立全域 singleton、直接讀取環境，或隱式存取外部服務。

- element 路徑：`modules/element/<language>/<feature>/<ticket-id>/`
- 實際原始碼路徑：`<paths>`
- 公開契約／資料模型：`<types and ports>`

## TDD 設計

1. 正常行為：`<red test>`
2. 規則違反／輸入錯誤：`<red test>`
3. 外部失敗／fail-closed：`<red test>`
4. 回歸保護：`<test>`

### 適用的缺陷類別（依 `CodeReview.md` §2.1，逐一列出必要案例，不適用者寫明理由）

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | `是／否` | `<七種邊界：相等、多一字元、尾斜線、大小寫、URL 編碼、路徑遍歷、空路徑>` |
| 2 | null／空字串／陣列 | `是／否` | `<五種：null、undefined、''、純空白、空容器；並註明哪些等價>` |
| 3 | 權限繞過 | `是／否` | `<直接存取 + 間接存取（其他入口／內部呼叫／背景工作）>` |
| 4 | Token 格式與比較 | `是／否` | `<格式案例 + 來源斷言未用 ===／== 比對憑證>` |
| 5 | 錯誤碼是否一致 | `是／否` | `<對外碼固定不可區分 + 對內原因碼唯一；註明哪些原因必須保持可區分>` |
| 6 | 例外是否會拋出 | `是／否` | `<每個外部依賴注入失敗：主流程行為 + 是否傳播>` |

> 第 7 類「測試是否真的涵蓋描述」由審閱者負責，不在本表。
> **未列出的類別若事後成為缺陷，根因記為工單缺陷。**

## 完成定義與證據

- `<tests / typecheck / build / manual acceptance>`
- **反向突變證據**（規則見 `implementation-tdd.md`，本欄只填證據）：
  `<每個具名行為：拿掉它 → 哪個測試轉紅、失敗訊息 → 還原後轉綠。缺此項不得宣稱行為已被測到>`
- **缺陷修正**另填 baseline-red 的測試名稱與失敗原因。新行為不需要、也不得表演首次紅燈。

## 正式環境移植 SOP

- Migration、環境變數名稱、順序、驗證、回滾／forward-fix：`<details>`

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：`PRG-YYYYMMDD-NNN`
