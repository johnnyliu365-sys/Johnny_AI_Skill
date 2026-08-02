# <專案名稱>

本檔案是多 AI 協作的共用專案事實來源。專屬 Context 只能引用並補充已分派範圍，不得覆寫本檔。

## 已確認事實與共同邊界

- `<fact / decision / boundary>`

## 識別碼登錄

- SPEC 專案代號：`<PROJECT>`（全大寫 kebab-case）。
- SPEC 功能鍵：全大寫 kebab-case，穩定對應 `modules/spec/<feature>.md`；不得因 AI、worktree 或修訂變更。
- SPEC 格式：`SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>`；新規格的 ULID 由所屬 worktree 以 CSPRNG 產生，完整 ID 不含 AI／worktree。
- 發布前查核：讀取本檔衍生 SPEC 索引與 `modules/spec/`，不得重用 ID 或新增仍有效功能集群的第二份規格。

## 衍生 SPEC 索引

> 任一專屬 Context 引用本檔後，其 SPEC 核准時，原引用章節必須在此回掛。由本檔 owner 在自己的 worktree
> 以 docs-only commit 發布；未發布者不得成為跨 worktree ticket 的共同基準。

### `<SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>｜<功能名稱>`

- 規格路徑：`modules/spec/<feature>.md`
- 專屬 Context：`doc/context/<feature>/<worktree-id>.md`
- 原引用章節：`<heading hierarchy>，起始行 <line>，基準 <SHA>`
- 收斂結果摘要：`<approved facts / decisions>`
- 責任範圍：`<In Scope / Out of Scope>`
- PRD／需求變更：`PRD.md §...`／`CHG-YYYYMMDD-NNN`／不適用
- 回掛 commit：`<docs-only SHA>`
