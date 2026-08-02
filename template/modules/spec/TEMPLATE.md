# <功能名稱> 規格

| 欄位 | 內容 |
| --- | --- |
| 規格 ID | `SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>` |
| 規格狀態 | `DRAFT`／`APPROVED`／`SUPERSEDED` |
| 撰寫 AI 簽名 | `<AI>／<worktree>／基準 <commit SHA>` |
| 排查起點 Context | `doc/context/<feature>/<worktree-id>.md` |
| PRD 索引 | `PRD.md §...`／不適用 |
| 需求變更 | `CHG-YYYYMMDD-NNN`／不適用 |
| 共用 Context 回掛 | `CONTEXT.md §...／衍生 SPEC 索引`／不適用 |

## 問題、目標與不做範圍

## 使用者流程與驗收條件

## 領域模型、資料流與責任邊界

## API／事件、資料庫、快取、Provider、權限與維運

## 測試切點與 TDD 設計

## 風險、相容性、回滾與部署前提

## 收斂與回掛

- 共用 Context 回掛內容：`<SPEC ID、路徑、收斂結果、責任範圍、PRD／CHG>`
- 關聯 CHG 的 SPEC 收斂結果：`<section / 不適用>`
- 回掛共同基準 commit：`<docs-only SHA / 待 owner 發布>`

## 修訂簽名

| 日期 | AI／worktree／基準 SHA | 摘要 |
| --- | --- | --- |
| `<ISO-8601>` | `<signature>` | `<revision>` |

## 核准紀錄

- 決策者：`<name>`
- 日期：`<Asia/Taipei date>`
- 核准範圍：`<scope>`
