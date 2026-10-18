# 30｜可信的獨立票接續與主線保持開放

| 欄位 | 內容 |
| --- | --- |
| State | `30A_PROPOSED / UPSTREAM_DECISION_REQUIRED / NON_DISPATCHABLE`；完整 Ticket 30 與清單 02 仍未完成 |
| Requirement lineage | 沿用 `PRD-20260805-009`／`CHG-20260805-009` 與原 Ticket 30；不建立新 PRD、平行 Ticket 或第二套 authority |
| Effective authority | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` 的既有有效 AC 1–8 |
| Design evidence only | Owner-authorized、獨審通過的 SPEC design baseline `76d1f942e24975da28889c8b6ecee904c8ef3da0`，SPEC blob `6fd8c3098f48be40c2cf05a03f8284c186163c08`；它允許受控拆票規劃，不是 Ticket 30A implementation Grant 或 runtime activation |
| Prior candidate | `76f6f32771e80add10c499db2c7479377b079c0c` 的初審為 `BLOCKED`：錯把一般 owner 指示寫成 ticket-scoped Grant，並自創未獲核准的 API、source grammar 與硬預算 |
| Roles / worktree | Root 保持 control owner／reviewer orchestrator；尚未配置 implementation owner、reviewer、task、receipt、branch、baseline 或 implementation worktree |
| Profile | `STANDARD` proposal；不得讀真實 remote、Git、shell、network、provider 或 credential，不得產生 Host／dispatch／closure effect |

## 保留的最小 30A 候選

30A 的意圖限於一個 source-bound、metadata-only 的 candidate projection：

1. 從**已核准且已 version-bind** 的 `ProjectAuthorityContract` 取得 declared repository 與
   full `project_authority_ref`；caller、prompt、工作副本或 `origin/<ref>` cache 不能選擇
   authority line。
2. 經既有 `DirectRemoteObservationPort`／`observe_declared_remote` 對該 declared ref 做一次
   fresh direct observation。caller SHA 只能作 mismatch assertion；authority SHA 是 direct
   observation 的結果。
3. 透過經核准的 committed-source readback boundary，從 observed SHA 讀 target-owned
   generic `modules/tickets/<feature>/README.md` index 與它正式指向的 ticket leaves。source
   格式、index-to-leaf binding、revision/digest 規則必須來自已核准的 target artifact，
   不能由 30A ticket author 或 implementer 發明。
4. 只有在 project、mainline、ticket、dependency 與 source revision 全部驗證後，才建立
   既有 `MainlineProjectionRequest` 並呼叫 `project_mainline_tickets`。輸出只可為
   `ready_for_recheck` 等 candidate metadata；它不是 Grant、admission、dispatch、Review、
   integration 或 closure authority。

這個候選不得接受 caller-built `MainlineTicket` 作為正式來源，不得 cache fallback、retry、
polling 或把 raw source 存進 Router state。remote 在 observation 後移動時，任何 effect
邊界仍必須重新准入；30A 本身沒有 effect 權力。

## 已存在、可重用但尚未組成 implementation authority 的能力

```text
selected: workflow-router-poc@112134ecee7c7ea770ca90c9ee3ed91f2a5ed8a9
why: reuse the existing immutable mainline candidate projection and graph validation
read: library/workflow_router/README.md → library/workflow_router/__init__.py → mainline_projection.py
dependency: existing ProjectAuthorityContract and direct-observation contracts
boundary: no authoritative source declaration/readback composition, Host admission or formal closure
```

- `library.workflow_router.mainline_projection` 已提供 strict `MainlineProjectionRequest`、
  `MainlineTicket`、有限狀態、dependency graph 驗證與純 candidate reducer；不得複製。
- `library.local_orchestration.project_authority` 已提供 `ProjectAuthorityContract`、
  `DirectRemoteObservationPort`、request/result/failure models 與
  `observe_declared_remote`；這是 fake-compatible contract，不等於本票已有 production
  declaration loader、provider adapter 或 Host binding。
- `library.local_orchestration.git_handoff_event_adapter.GitReadbackPort.read_blob` 是現有精確
  commit/path readback seam，但其 authority identity、source selection 與 failure semantics
  未被有效 SPEC 指定為 30A 的正式 mainline source boundary；不得直接宣布採用。

## 為何目前不能形成 exact implementation ticket

目前 approved/effective source 沒有同時回答下列 public-contract 決策；依 P0，這些不能由
低階 implementer 猜測：

1. 哪個 target-versioned `ProjectAuthorityContract` declaration artifact/revision 是 30A 的
   trust anchor，以及 control plane 如何獨立 read back 並證明該 declaration 已准入。
2. generic `<feature>` index 如何宣告 mainline ID、required/optional set、dependency edges、
   ticket leaf reference 與各自 revision/digest；現行 workflow-governance index 不得被宣稱
   已完成此 migration。
3. source parser 使用哪個**既有或 owner-approved**格式，如何處理 duplicate、missing、
   ambiguous、stale、mismatch 與 observation/readback race；目前沒有獲核准的 HTML-comment
   JSON 或其他 machine-readable grammar。
4. observed remote SHA 到 committed blob readback 的正式 public port 是重用既有
   `GitReadbackPort`、收窄 adapter，或另一個已核准介面；其 request/result/nullability、
   credential-free evidence 與 race semantics 尚未由 authority 固定。
5. 一份只允許 30A source/test 變更的 ticket-scoped implementation Grant、精確 owner／
   reviewer／worktree／branch／baseline 與 writable boundary。一般「繼續有界工作」指示
   不是這份 Grant，也不能推導出兩檔 create allowlist。

因此先前未獲核准的 hard-coded feature path、source grammar、public API 與行數 ceiling
全部撤回。本票目前沒有 `johnny-boundary`；任何 source/test create 或 modify 都未獲授權。

## 上游必須產生的最小決策

Architecture Owner 必須在原 PRD／Ticket lineage 與既有 SPEC 授權內，先完成一份
可獨審的 source contract revision，至少固定：

- generic `<feature>` index 與 ticket leaf 的既有/新增正式 schema、identity、revision 與
  digest binding；若需要 migration，指定 target-owned migration artifact 與順序；
- admitted `ProjectAuthorityContract` declaration 的精確 artifact/revision/readback；
- direct observation 後 committed-source port 的 public request/result、有限 disposition、
  staleness/race precedence，以及 raw source 的 ephemeral/privacy 邊界；
- 30A candidate result 與既有 `MainlineProjectionRequest` 的唯一 dependency direction；
- ticket-scoped Grant、精確 roles/worktree/baseline、最小 writable scope、驗證命令與
  recovery/rollback。

若 Architecture Owner 選擇既有 source/readback contract，ticket 必須引用其精確
public symbol 與版本；若新 contract 超出既有 SPEC 的產品、安全或權限邊界，才依
原 Change Control 取得 Human Owner 核准，不能在 30A 內偷做。純技術型別／schema
選擇不另送 Human Owner；實作仍須另有精確 ticket-scoped Grant。

## P0 preflight 與未來 acceptance 下限

上游決策完成後，Architecture Owner 才能把 30A 修成 dispatchable ticket。派工前與
implementer 第一個 red 前都必須：

- 用 ordinary public constructors 建立所有 success/failure DTO、enum、port request/result，
  覆蓋 exact primitive、nullability、finite disposition；禁止 `Any`、`cast`、coercion、
  bypass constructor、未驗證 dict 或動態 member lookup。
- 證明 raw caller repository/ref/SHA/index/tickets 不能取代 admitted declaration、direct
  observation 與 committed readback；local tracking ref 只可為 diagnostic。
- 命名 normal cell：A precise wait、independent B 為 `ready_for_recheck`、C 依賴 A 而
  waiting，且 B 完成後 A／required mainline 仍開放。
- 命名 failure cells：declaration/readback missing，direct observation unavailable/not-found/
  ambiguous/stale/moved/identity mismatch，source missing/ambiguous/malformed、index↔leaf
  revision mismatch、incomplete/unknown/cyclic dependency；全部 fail closed 且無 projection。
- 命名 boundary cells：一次 direct observation、每個 exact blob 一次 read、無 retry/
  polling/cache fallback、raw content 不進 result/log/state、candidate 不觸發 Router/Host。
- 由獨立 reviewer 從不同入口反向突變 authority SHA、index↔leaf revision、全域 freeze B
  與 false mainline closure；必須看到對應 cell 紅後 byte-for-byte 還原。
- 使用 Python 3.11 strict checker、focused projection regression、compile/import 與
  `git diff --check`；精確命令在 approved public contract 與 writable scope 固定後寫入。

XSS 目前為 `N/A`：候選沒有 Browser/WebView/DOM/JavaScript/render sink。若上游 source
format 或 consumer 引入 rendering，必須重新套 XSS gate，不得沿用 N/A。

## 完整 Ticket 30 與 Host blocker

即使未來 30A 通過，它也只關閉 fake/source-bound candidate projection，不關閉完整
Ticket 30。正式 A/B/C continuation 還需要每票 live Grant、owner/worktree/dependency
admission，以及在真實 effect 前的 qualified Host intercept。現行 same-lifetime lane 未有
該硬攔截；cross-lifetime `admit_dispatch` 也未完成此 ticket source readback。Declaration、
target index migration、implementation authority 或 Host capability 任一未完成，都不得
把清單 02、Ticket 30、dispatch 或 closure 標為完成。

## Stop／Return

目前唯一合法返回是：

```text
UPSTREAM_DECISION_REQUIRED / TICKET_DEFECT / NON_DISPATCHABLE
```

附本票完整 SHA、上述五項 gap 與初審 finding。不得 dispatch、建立 implementation
worktree、修改 source/test、執行真實 readback、整合或 push。Architecture Owner 完成
既有授權內的 source contract、且 Human Owner 提供必要的精確 ticket-scoped Grant 後，
在同一 Ticket 30 lineage 追加有限 Closure revision，重跑 independent ticket review，
再由 Router 決定下一步；不得把普通工程選擇升級成人工決策。
