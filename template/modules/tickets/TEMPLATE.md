# NN｜<垂直切片名稱>

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | 完整 `SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>`（`§x、AC-y`） |
| 規格撰寫 AI | `<AI>` |
| 第一步排查起點 | `doc/context/<feature>/<worktree-id>.md` |
| PRD 索引 | `PRD.md §...`／不適用 |
| 需求變更 | `CHG-YYYYMMDD-NNN`／不適用 |
| 共用 Context 回掛 | `CONTEXT.md §...／衍生 SPEC 索引`／不適用 |
| 狀態 | `PLANNED`／`IN_PROGRESS`／`BLOCKED`／`DONE`／`SUPERSEDED` |
| 共同基準 | `<docs-only commit SHA>` |
| 實作者 | `<AI／worktree>` |
| 審閱者 | `<AI／worktree>` |
| 責任邊界 | `<In Scope>` |
| 禁止修改 | `<Out of Scope>` |
| 環境 | `LOCAL`／`STAGING`／`PRODUCTION` |

## 使用者拍板與可觀察結果

## 實作範圍、依賴與 ticket elements

- element 路徑：`modules/element/<language>/<feature>/<ticket-id>/`
- 實際原始碼路徑：`<paths>`
- 公開契約／資料模型：`<types and ports>`

## TDD 設計

1. 正常行為：`<red test>`
2. 規則違反／輸入錯誤：`<red test>`
3. 外部失敗／fail-closed：`<red test>`
4. 回歸保護：`<test>`

## 完成定義與證據

- `<tests / typecheck / build / manual acceptance>`

## 正式環境移植 SOP

- Migration、環境變數名稱、順序、驗證、回滾／forward-fix：`<details>`

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：`PRG-YYYYMMDD-NNN`
