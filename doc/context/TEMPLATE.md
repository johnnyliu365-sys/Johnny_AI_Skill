# 功能集群／worktree Context 模板

> 檔案路徑：`doc/context/<feature>/<worktree-id>.md`
> 僅描述已分派集群；不得覆寫共同 `CONTEXT.md` 或既有已核准規格。

| 欄位 | 內容 |
| --- | --- |
| 功能集群 | `<feature>` |
| Agent／worktree | `<AI>／<branch-or-worktree>` |
| 共同基準 | `<commit SHA>` |
| 狀態 | `DISCOVERY`／`SPECIFYING`／`TICKETING`／`BLOCKED` |
| 責任邊界 | `<In Scope>` |
| 禁止修改 | `<Out of Scope>` |

## 共用 Context 引用

- 共同基準 commit：`<SHA>`
- `CONTEXT.md` 章節：`<heading hierarchy>`
- 引用錨點：`<heading hierarchy> › <entry name>`
- 引用指紋：`<sha256-8>`（錨點行起至下一空行之文字）
- 行號（非規範性提示，可省略）：`<line>`

## 既有規格前置查核

| 產物 | 狀態 | 可沿用／不可改寫範圍 | 本次處置 |
| --- | --- | --- | --- |
| `modules/spec/<feature>.md` | `APPROVED`／`BLOCKED`／`SUPERSEDED` | `<facts>` | `<reuse/change/ignore>` |
| `modules/tickets/<feature>/` | `<status>` | `<facts>` | `<action>` |

## 已確認事實與約束

- `<fact>`

## 待決事項與跨集群依賴

- `<decision owner / impact / BLOCKED condition>`

## 衍生 SPEC 索引

> 專屬 Context 先記錄待回掛內容；共用 `CONTEXT.md` 的原引用章節必須由其 owner 回掛同一筆索引。

### `<SPEC-ID>｜<功能名稱>`

- 規格路徑：`modules/spec/<feature>.md`
- 專屬 Context：`doc/context/<feature>/<worktree-id>.md`
- 原共用 Context 引用：`<heading hierarchy> › <entry name>`，指紋 `<sha256-8>`，基準 `<SHA>`
- 收斂結果摘要：`<approved facts / decisions>`
- 責任範圍：`<In Scope / Out of Scope>`
- PRD／需求變更：`PRD.md §...`／`CHG-YYYYMMDD-NNN`／不適用
- 共用 Context 回掛狀態：`PENDING_OWNER_BACKLINK`／`PUBLISHED <docs-only SHA>`
