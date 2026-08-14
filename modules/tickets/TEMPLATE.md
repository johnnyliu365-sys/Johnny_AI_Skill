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
| 責任邊界 | `<In Scope>` |
| 禁止修改 | `<Out of Scope>` |
| 環境 | `LOCAL`／`STAGING`／`PRODUCTION` |

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
- **紅燈輸出**：`<每個行為第一次失敗的測試名稱與失敗原因；缺此項不得宣稱依 TDD 完成>`

## 正式環境移植 SOP

- Migration、環境變數名稱、順序、驗證、回滾／forward-fix：`<details>`

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：`PRG-YYYYMMDD-NNN`
