# <專案名稱>

本檔案是多 AI 協作的共用專案事實來源。專屬 Context 只能引用並補充已分派範圍，不得覆寫本檔。

## 已確認事實與共同邊界

- `<fact / decision / boundary>`

## 識別碼登錄

- SPEC 專案代號：`<PROJECT>`（全大寫 kebab-case）。
- SPEC 功能鍵：全大寫 kebab-case，穩定對應 `modules/spec/<feature>.md`；不得因 AI、worktree 或修訂變更。
- SPEC 格式：`SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>`；新規格的 ULID 由所屬 worktree 以 CSPRNG 產生，完整 ID 不含 AI／worktree。
- 發布前查核：讀取本檔衍生 SPEC 索引與 `modules/spec/`，不得重用 ID 或新增仍有效功能集群的第二份規格。

## 實作語言規範

> 本節是本專案依 `Workflow.md` §9 通用條件所做的**實例決定**；通用條件不在此重複。

| 欄位 | 內容 |
| --- | --- |
| 專案類型 | `<workload shape：I/O bound／CPU bound／高併發；延遲由什麼主導>` |
| **統一後端語言** | `<language>` |
| 前端／行動端 | `<language>`（平台決定，非選擇） |
| 資料庫 | `SQL`（不計入語言選擇） |
| 法規／成熟度綁定例外 | `<domain → language>`／無 |
| 閘門生效階段 | `<例如：POC 豁免，MVP 起強制>` |

### 為何統一而非按領域分派

| 分歧領域 | 按適用性會選 | 實際決定 | 依據（須為實測或可查證事實） |
| --- | --- | --- | --- |
| `<domain>` | `<language>` | `<language>` | `<evidence>` |

### 偏離統一語言的觸發條件

偏離須有**實測依據**，不接受預期或偏好；觸發後仍須經需求變更紀錄與核准。

| 語言 | 觸發條件 |
| --- | --- |
| `<language>` | `<measurable trigger>` |

## 衍生 SPEC 索引

> 任一專屬 Context 引用本檔後，其 SPEC 核准時，原引用章節必須在此回掛。由本檔 owner 在自己的 worktree
> 以 docs-only commit 發布；未發布者不得成為跨 worktree ticket 的共同基準。

### `<SPEC-<PROJECT>-<FEATURE>-<YYYYMMDD>-<ULID>｜<功能名稱>`

- 規格路徑：`modules/spec/<feature>.md`
- 專屬 Context：`doc/context/<feature>/<worktree-id>.md`
- 原引用章節：`<heading hierarchy> › <entry name>`，指紋 `<sha256-8>`，基準 `<SHA>`
- 收斂結果摘要：`<approved facts / decisions>`
- 責任範圍：`<In Scope / Out of Scope>`
- PRD／需求變更：`PRD.md §...`／`CHG-YYYYMMDD-NNN`／不適用
- 回掛 commit：`<docs-only SHA>`
