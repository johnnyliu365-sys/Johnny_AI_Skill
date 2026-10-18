# 30｜可信的獨立票接續與主線保持開放

| 欄位 | 內容 |
| --- | --- |
| State | `OWNER_APPROVED_30A_BOOTSTRAP / DOCUMENT_REVIEW_PENDING / NON_DISPATCHABLE`；完整 Ticket 30 與清單 02 仍未完成 |
| Requirement lineage | 沿用 `PRD-20260805-009`／`CHG-20260805-009` 與原 Ticket 30；不建立新 PRD、平行 Ticket 或第二套 authority |
| Effective authority | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` 的既有有效 AC 1–8 |
| Design evidence only | Owner-authorized、獨審通過的 SPEC design baseline `76d1f942e24975da28889c8b6ecee904c8ef3da0`，SPEC blob `6fd8c3098f48be40c2cf05a03f8284c186163c08`；它允許受控拆票規劃，不是 Ticket 30A implementation Grant 或 runtime activation |
| Prior candidate | `76f6f32771e80add10c499db2c7479377b079c0c` 的初審為 `BLOCKED`：錯把一般 owner 指示寫成 ticket-scoped Grant，並自創未獲核准的 API、source grammar 與硬預算 |
| Roles / worktree | Root＝Architecture Owner（本次文件修訂）及唯一 reviewer orchestrator；實作者 `/root/ticket30a_fixture_impl`，獨審 `/root/ticket30a_fixture_review`；repo-contained `.worktrees/skill-improvement-30a-fixture`／`codex/skill-improvement-30a-fixture`，文件獨審前不建立 lane |
| Profile | `STANDARD` proposal；30A 僅准在精確 Grant 後用隔離、已提交的本地 fixture Git 與本機測試命令；不得讀真實 target／remote、呼叫 provider／credential，或產生 Host／dispatch／closure effect |

## Owner 批准與當前 continuation

Owner 2026-10-18 精確核准 `acf0ffa1780af3d229b7f80c6e063f6d642e6864` 與本票
舊 leaf blob `ded322b3c7e82399c31ff4cf67d3dbf3237af3fb`：Architecture Owner
沿原 `CHG-20260805-009` 依法 REVISE sealed Context revision 03，增列本專案
`johnnyliu365-sys/Johnny_AI_Skill`／`refs/heads/main`／`SINGLE_BRANCH`；原 SPEC
revision 03 寫定 fixture bootstrap 例外。兩者及本票經獨審後，條件式 30A Grant
可由控制面精確綁定執行；只有這些核准文件變更時不重問 Owner。

下列「候選／尚缺 Grant」段落保存當時的 source decision provenance；本節及
本票凍結的 30A-F1–F4 是當前限縮建置依據。正式 target source／Host effect 的
缺口仍有效。當前 action 是 `CONTEXT/SPEC/TICKET docs review`，成功後
`ACTION_COMPLETED → AUTO_CONTINUE → same-lifetime 30A IMPLEMENT`。
文件獨審失敗只修同票文件，不能先派 source/test。

| 派工綁定 | 核准範圍／待獨審後讀回 |
| --- | --- |
| Profile／角色 | `implementation-standard`：當下主機可用 `gpt-6-luna/xhigh`；不同席 `gpt-6-sol/high` 獨審，能力不低於實作者。這是本票 profile 資料，不寫入通用程式或 skill。以原 Profile 的語義角色及 Owner 已允許的現行模型對應；不變更全域 DAP/角色權限 |
| Baseline | 起點 `acf0ffa1780af3d229b7f80c6e063f6d642e6864`；最終文件受審後，控制面在本票既有 review 記錄完整 dispatch baseline SHA／ticket blob／worktree Git readback，確保至起點只改核准文件，再從該 baseline 建實作 worktree |
| Scope | 只 create 下文兩路徑，modify=none；不得修改套件 exports、既有 projection／contracts／tests |
| TDD／型別 | 新功能不要求不存在程式的 ceremonial first-red。既有 observation/projection constructors 在派工前實跑。新公開型別不存在時，採下述同票受限 type-bootstrap Phase A；實際 constructor／negative／round-trip 與獨審通過前，不派 Phase B parser/source-read 行為。prototype 不作候選成功證據 |
| Resource／lifecycle | 一位實作者、零 helper、一位獨審；沿同票既有耗用與 finding，不重置預算。Git fixture 每命令 timeout 20s、本機驗證每命令有限 timeout；不平行加壓、不輪詢、不呼叫付費 API。fixture 由 pytest temp fixture 記 owner/test ID、session TTL、teardown；專用 worktree/ref 保留至 Review／證據封存／本地整合後才依精確身分受限移除 |
| XSS／UI／refactor | 無 render sink／正式 UI，XSS N/A；新增來源 assembly，未搬既有責任，TEST→A→B N/A；沿用投影，不能把腳本增加回報成產品拆分 |

公開 seam 凍結為 `RawGitBlobReadResult`（FOUND+bytes 或非 FOUND+None）、
`MainlineSourcePort.read_blob(observation: GitObservation, artifact_ref: TargetRelativePath)`、
`MainlineSourceRequest`（project_id、feature、synthetic observation）、
`MainlineSourceResult`（fixture-only scope、projection 或 finite failure 二擇一）、
`project_committed_mainline(request, port)`。`TargetRelativePath` 是本模組的具名
canonical relative-path value：不得 absolute、反斜線、空／`.`／`..` segment、
control 或非正規分隔；leaf 另外限同 feature 直接 `.md`。request 限 synthetic
`WORKTREE_HEAD` observation，拒絕 tracking／direct-remote 種類；它不是 authority
admission。內部 wire DTO 由實作者在本責任模組選最少集合，extra/duplicate/missing
皆拒絕，JSON 動態輸入只在 boundary 驗證，不能帶 Any／未驗證 dict 向內。
結果固定 `FIXTURE_ONLY`，不承載 raw source；未新增 authority engine。

### 同一 Grant 的有限型別建構順序

Architecture Owner 在同兩個 create 路徑內，將新能力的建置按必要先後分成兩個 cut，
不新增 Stage、Agent、Ticket、成本權限或驗收。Phase A 是只限本票新型別的精確
pre-dispatch construction bootstrap：允許具名實作者先建立真實 DTO／enum／Protocol／
path validator 與純 constructor 測試，除此不得實作或呼叫 parser、source port、
Git、Router、Host 或 native spawn。既有依賴 constructors 仍須 Phase A 派工前通過。
Phase A 以真實 module 的普通 constructor、錯 primitive／null／enum／payload 組合、
round-trip、strict checker 及獨審作為關卡；結果 pin 實際 SHA，禁止文件／in-memory
probe 替代。通過後以該受審 commit 為 Phase B source baseline，同一 owner／Grant／
worktree／剩餘額度接續 parser。獨審席位沿用到最終 30A-F1–F4，不重置 finding。
這個建構排序僅使已授權的新型別得以存在，沒有放寬型別驗證或任何真效應前提。

## 保留的最小 30A 候選

下列是**正式 target source 路線的終態候選**；本輪 30A fixture 只建置其中
committed bytes→validated candidate 的純隔離子集，不提前啟用 1–2 或真 Host。
終態意圖限於一個 source-bound、metadata-only 的 candidate projection：

1. 從**已核准且已 version-bind** 的 `ProjectAuthorityContract` 取得 declared repository 與
   full `project_authority_ref`；caller、prompt、工作副本或 `origin/<ref>` cache 不能選擇
   authority line。
2. 經既有 `DirectRemoteObservationPort`／`observe_declared_remote` 對該 declared ref 做一次
   fresh direct observation。caller SHA 只能作 mismatch assertion；authority SHA 是 direct
   observation 的結果。
3. 透過經准入的 committed-source readback boundary，從 observed SHA 讀 target-owned
   generic `modules/tickets/<feature>/README.md` index 與它正式指向的 ticket leaves。
   技術格式依下文 Architecture Owner 決策；實際 mainline 成員、依賴、owner／handoff
   與 revision 仍必須由 control plane 從已核准 target artifact 遷移，不得從敘事表推定。
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

## 為何目前不能形成正式來源／effect implementation ticket

以下是仍未完成的 authority facts／effect Grant；不得由 implementer 猜測：

1. 哪個 target-versioned `ProjectAuthorityContract` declaration artifact/revision 是正式讀回的
   trust anchor，以及 control plane 如何獨立 read back 並證明該 declaration 已准入。
2. workflow-governance 等 target 的實際 mainline ID、required/optional set、dependency edges、
   owner／handoff、ticket leaf reference 與各自 revision/digest 尚未依下文 schema versioned
   into its feature index；現有 status table 不構成這些 authority facts。下文已準備
   本專案候選，不能由此跳過正式遷移與獨審。
3. 30A 隔離建置的條件式 Grant 已由上節 Owner 精確核准；剩下是文件獨審及
   reviewer-established baseline／owner／worktree／leaf 的實際讀回綁定。
   一般「繼續有界工作」指示仍不是其他 effect 的 Grant。

先前硬編 feature path、自報 Grant、未遷移的 parser 契約與行數 ceiling 均撤回。
下述 Architecture Owner 的通用技術決策只足以準備隔離 fixture 建置，不補足
target 事實或 effect Grant。文件獨審前本票仍無 active `johnny-boundary`；
通過後才依已核准條件啟用兩個 create 路徑，modify 始終為空。

## Architecture Owner 的限縮技術決策（非 implementation Grant）

在既有 AC9 設計基準內，source encoding、parser 邊界與有限失敗碼是工程決策，
不要求 Human Owner 再選一次。target-owned 的 `modules/tickets/<feature>/README.md`
保留人讀 status table，另有**唯一** `## Mainline source contract` heading，其後緊接
唯一 `json` fence；該 fence 是機器讀取的唯一 index，敘事表不是 authority。JSON
object 嚴格包含：`schema_id = mainline-index/revision-01`、`project_id`、`feature`、
`mainline_ref`、`objective_ref`、`owner_ref`、`handoff_ref`、`bindings[]`、`tickets[]`。
每個 binding 嚴格包含 `kind`（context/prd/change/spec）、`identity`、`artifact_ref`、
`revision_sha`（40 位小寫 hex）；每個 ticket 嚴格包含 `ticket_ref`、
`ticket_revision`（既有 `RevisionDigest`）、`leaf_ref`、`leaf_digest`
（`sha256_` 加 64 位小寫 hex）、`required`（boolean）、`status`（既有有限 enum）、
`depends_on[]`、`admission_ref`（nullable）、`evidence_refs[]`。所有 metadata ID 仍須
通過既有強型別 constructor，不另建平行 ID 規則。

每個精確 ticket leaf 在既有內容中另有唯一 `## Mainline ticket contract` heading，
緊接唯一 `json` fence，嚴格包含 `schema_id = mainline-ticket/revision-01`、
`ticket_ref`、`ticket_revision`、`status`、`depends_on[]`、`admission_ref`、
`evidence_refs[]`。leaf 是 graph/status 的正式來源；index 的相同欄位是綁定宣告，
兩者任一值不同即 `INDEX_BINDING_MISMATCH`，絕不採 first-match 或單邊覆蓋。
`required` 與 `leaf_ref` 由 index 宣告，與 leaf 原始 bytes digest 一起驗證；
只有從 committed leaf 解析出來且與 index 一致的節點能進既有投影。

Parser 必須拒絕重複 JSON key、未知／缺失欄位、空 tickets、重複 ticket／leaf ref、
跨 feature 的 leaf、未知依賴、非法狀態及 schema 漂移。`feature` 決定通用 index 路徑；
每個 leaf 只能是同 feature 目錄的直接 `.md` 子檔。index 與 leaf 必須在同一 direct
observed SHA 讀取；逐 leaf 的**原始 bytes** SHA-256 必須等於 `leaf_digest`，
再解析該 leaf 的唯一 contract fence。成功後才從驗證過的 committed leaves 建立
既有 `MainlineProjectionRequest`；
`source_revision = rev-<observed SHA>`，不可接受 caller／index 自報值。原始 Markdown／
JSON 只在讀取流程內暫存，不進結果、Router state 或 log。

最小 source read port 為 `read_blob(observation: GitObservation,
artifact_ref: TargetRelativePath) -> RawGitBlobReadResult`，要求 repository/ref 身分
隨 observation 綁定。`RawGitBlobReadResult` 只重用既有 `GitBlobReadStatus`，但
`FOUND` payload 必須是原始 `bytes`，非 FOUND 不得攜帶 payload；hash 以該 bytes
計算，UTF-8 解碼與 fenced JSON parse 必須嚴格拒絕非法序列、重複 key 與多重 block。
現有 `GitBlobReadResult.payload: str | None` 和只收 commit/path 的
`GitReadbackPort` 均不足以證明原始 bytes／authority identity，不得假借重用。
候選組合只做一次 `observe_declared_remote`、逐 exact blob 一次 read、一次既有純投影；
結果只有候選 metadata 或有限拒絕。source failure 僅限 `INDEX_NOT_FOUND`、
`INDEX_READ_UNAVAILABLE`、`INDEX_SCHEMA_INVALID`、`INDEX_BINDING_MISMATCH`、
`LEAF_NOT_FOUND`、`LEAF_READ_UNAVAILABLE`、`LEAF_DIGEST_MISMATCH`、
`PROJECTION_INVALID`；direct observation 失敗沿用既有 enum，不複製。

這項決策不把 30A 延伸到 Router／Host：目前 `project_mainline_tickets` 只有套件匯出
與測試消費者，沒有正式 Router caller。production repository binding、replace-ref-safe
Git 讀取、真 Host effect 前准入及正式結案均是後續獨立邊界。

## 本專案主線與 authority 宣告候選（非 live source）

以下是 2026-10-18 自**釘選 `3ca02bd5e90611c101d97cc79f06b4751c70cd1c`**
讀得的候選，不是 `## Mainline source contract`，也不是已准入
`ProjectAuthorityContract`。既有活躍 `PRD-20260805-009`／`CHG-20260805-009`
與 workflow-governance SPEC revision 02 管本功能；清單 revision 23 管整批進度。

| 主線維度 | 已查證的事實 | 建議宣告與影響 |
| --- | --- | --- |
| 專案／目標 | `modules/tickets/workflow-governance/README.md` 的 Delivery objective 是 completion re-enter Router、獨立安全接續、精確等待／HALT；清單 01–12 是 Owner 指定的整批完成目標，04 已完成本地回放 | 本專案 programme mainline 設「12 項必要成果全部具實作、驗證、獨審；不改 target 產品」；**不要**把 checklist 順序當 ticket dependency graph |
| 必要／選配 | Owner 要求 12 項必要實作與驗收；現有 status registry 含已整合切片與仍開的 Ticket 30；沒有逐票 `required` 的正式 source fence | 結果層 01–12 為 required，額外優化為 optional；先在 workflow-governance feature source 遷移 Ticket 29 已完成投影與 Ticket 30 開放 continuation，其他 ticket 的 required/optional 只依精確契約逐一驗證後登記，不由 status table 猜 |
| 依賴／接續 | 清單優先 02→04→05→06→07；Ticket 30 讀既有 Ticket 29 純投影，30A fixture 是真來源／`admit_dispatch` 驗證的前置技術能力；04 已完成 | 記錄可證明的能力邊 `29 → 30A fixture → 真來源／effect qualification`；01／02 的正式 closure 依賴該實證；其餘無精確相依證據者維持 `UNKNOWN`，准入的無相依工作可繼續 |
| 所有權／交接 | 清單指定 Root 管需求、衝突、派工，票級實作者依 Profile，另一席獨審；Ticket 30 尚未綁 active task/worktree | 宣告 role refs：Root control/reviewer orchestrator、Profile 選出的 implementation owner、獨立 reviewer；每次實際派工再釘 task/worktree/branch，實作者只回 candidate/evidence，不自行整合 |
| authority line | `origin` URL 是 `https://github.com/johnnyliu365-sys/Johnny_AI_Skill.git`；`git ls-remote --symref origin HEAD` 讀得 `refs/heads/main` → `a1cb6c13adbeb52a4117991727dcc3d4af6d2a33`。`CONTEXT.md` revision 03 **已封存**，project-authority Context revision 03 與 SPEC revision 11 也只有通用邊界，沒有本專案可讀回的完整宣告 | 推薦既有 target-owned `CONTEXT.md` 作唯一 declaration anchor，`main`／single-line 作候選，但**不能直接寫入**。須先取得適用的 approved change ref，由 Architecture Owner 在 `ARCHITECTURE/GRILL/CONTEXT` 執行 `REVISE`、pin 預期 sealed revision 03，再依既有流程封存與處理受影響 SPEC 基準。遠端 HEAD 不是核准；未完成前只可讀引 |

精確版本索引（均為本輪準備的**輸入**，不是自動升格的 authority）：

| 文件 | 已讀 commit／blob | 作用 |
| --- | --- | --- |
| `doc/AI-SKILL-IMPROVEMENT-CHECKLIST.md` rev23 | `3ca02bd5`／`ea4ea90a90662e73bed02466979c225037b635ac` | 01–12 進度／優先順序，不是 ticket graph |
| `modules/tickets/workflow-governance/README.md` | `3ca02bd5`／`d74b614f3633475708804bed07d9848b6d64451f` | 目標／人讀票面狀態，不是機器 source |
| Ticket 30 | `3ca02bd5`／`20a1f2cc1b9cac1e5697dbfb66eb05deb875bde5` | 原票 lineage；本次 docs 修訂後須改用最終新 blob |
| `CONTEXT.md` rev03 | `a5e2847312c4b3f9a78b424af02f1fa2ac38a8f5`／`9096c68199994b1414862828ffb0ce060f8482d7` | 本專案既有 Context，尚無 concrete authority declaration |
| project-authority Context rev03／SPEC rev11 | `80b5d96b29ab671c5a4103e66f0dcbbc12739b3a`／`771bb5cbba879d196c1f85b6b4721d4c5db870de`；同 commit／`27dfc04eef7de58aa25b3c7d9e136be0228553b2` | 可重用 declaration 型別／readback 邊界，非本專案核准值 |
| 活躍 PRD／CHG leaf | PRD `ede925d3f7b89236604f3b4b63c31708ab7f2ab6`／`6555d6e60645787a2f9a0ec6acd7849308172f09`；需求 leaf `8df8d2b3fa904d174e9e0c1f7d08f407402adce6`／`762b3be9a8a496689c360c5f2d8fd603a6ad68e8` | 原需求身分，不新增 PRD |
| `modules/spec/workflow-governance.md` rev02 | `51fa1e20f73d87b720f80b9d4dcc47b0de962898`／`4323863f09ef89382e27eb1e4fc99ba652171da4` | AC1–8 有效、AC9–11 已獨審設計基準；非實作 Grant |

此候選的歧義是**正式宣告載體／實際 required ticket graph**，不是 Owner 要自行填表。
推薦 `CONTEXT.md` 的合法 `REVISE` 路線，但本輪 docs-only 授權**不含**該寫入；
`router-control.md` Shared-Context authority 要求 approved change ref、Architecture Owner、
限定 stage、expected sealed revision 03。若選此路線，先形成該精確授權，再處理
受影響 SPEC 的合法 rebaseline；在這些條件前，不可把本候選讀作 live declaration。
逐票 graph 由 Root 以既有核准 leaf 做 docs-only migration，未能證明的 edge 不自造。

### 本輪 CI 來源窄查（不是退役證據）

- 本地 pin：控制 worktree HEAD `3ca02bd5e90611c101d97cc79f06b4751c70cd1c`；
  執行 `git ls-tree -r --name-only HEAD -- .github .gitlab-ci.yml .circleci
  azure-pipelines.yml Jenkinsfile .buildkite .travis.yml appveyor.yml
  bitbucket-pipelines.yml .drone.yml .woodpecker.yml Makefile Taskfile.yml
  justfile package.json pyproject.toml tox.ini noxfile.py Cargo.toml go.mod`，
  此範圍未見可宣告的 CI command source。
- 可讀遠端：`git remote -v`、`git ls-remote --symref origin HEAD`、
  `git ls-remote --heads origin`；九個 branch tip 的 GitHub Git tree API 遞迴路徑
  比對同一類 CI/wrapper 配置（`main a1cb6c13`、
  `codex/controlled-verification-intake 9707a1e5`、
  `codex/cve-01a-wire-foundation d0c93111`、`publication-0.4.9 c3cb81c4`，
  `verify/claude-publication-08-live-cutover 055d4d24`、
  `verify/claude-publication-15-v0414-codex-native-dispatch f5291dc3`、
  `verify/claude-publication-17-v0414-codex-readmission 818eef5a`、
  `verify/claude-publication-17-v0414-codex-readmission-r02 d6b2320f`、
  `verify/claude-publication-17-v0414-codex-readmission-r03 01b810f0`）；
  `origin/main` 的精確 readback 為上述 `a1cb6c13`、
  tree `truncated=false`，此範圍未見 CI 配置。實際批次命令（僅查 source path，
  不執行 CI；每筆 `CandidateCount=0` 且 `Truncated=False`）：

  ```powershell
  $remoteTips = git ls-remote --heads origin | ForEach-Object {
      $cols = $_ -split "`t"
      [pscustomobject]@{ Sha = $cols[0]; Ref = $cols[1] }
  }
  $remoteTips | ForEach-Object {
      $tree = Invoke-RestMethod -Uri ('https://api.github.com/repos/johnnyliu365-sys/Johnny_AI_Skill/git/trees/' + $_.Sha + '?recursive=1') -Headers @{ Accept = 'application/vnd.github+json' }
      $matches = @($tree.tree | Where-Object {
          $_.path -match '(^|/)(\.github/workflows/|\.gitlab-ci\.yml$|\.circleci/|azure-pipelines\.yml$|Jenkinsfile$|\.buildkite/|\.travis\.yml$|appveyor\.yml$|bitbucket-pipelines\.yml$|\.drone\.yml$|\.woodpecker\.yml$|Makefile$|Taskfile\.yml$|justfile$|package\.json$|pyproject\.toml$|tox\.ini$|noxfile\.py$)'
      } | Select-Object -ExpandProperty path)
      [pscustomobject]@{ Ref = $_.Ref; Sha = $_.Sha; Truncated = $tree.truncated; CandidateCount = $matches.Count }
  }
  ```

  未 fetch、未執行遠端 CI。
- 結論只限上述目前可讀分支／路徑：**此範圍未見**，不是「全專案無 CI」。
  `DeclaredTestCommand` 仍未有可信來源，**空命令清單絕不授權舊測試退役**；
  checklist 08、Ticket 32/36/39 的 retirement gap 維持開放。

## 30A 隔離建置：Closure revision 01，條件式核准

Owner 2026-10-18 指定 `library/local_orchestration/dispatch_authority.py::admit_dispatch`
為**之後**第一個跨生命週期派工驗證入口。這只是優先順序，不使該入口、原生 spawn、
真實來源或正式結案合格。現行 AC 1–8 繼續有效；已獨審的 AC 9–11 只作建置設計
基準。新閘門不以「先合格」阻塞自己的隔離建置，真實 effect 仍須在自己的邊界
重新讀回來源與權限。

**現行 SPEC 衝突不得省略：**workflow-governance SPEC revision 02 的 AC9–11
收尾文字明定 Ticket 30 在 trusted source 與 per-ticket Host admission path 綁定前
`non-dispatchable`。本段 30A fixture 正是要建置該來源能力的一部分，故目前
連 fixture implementation dispatch 也**不能只靠 Ticket Grant 啟動**。
需要 Owner 同次精確核准一個**僅供隔離建置的受限 bootstrap 例外**，並在原 SPEC／
Ticket lineage 中依 Change Control 記錄、獨審後生效。例外只免除 fixture 建置前
須先完成它自己要建的真 source／Host qualification 這個循環；**不**改 AC9–11
驗收、安全不變量、真 effect 准入或 Ticket 30 整體 NON_DISPATCHABLE 狀態。
以上記錄首次候選的衝突；Owner 已在本輪核准此精確限縮例外，原 SPEC revision 03
及本票正依上節 Change Control 獨審，通過前仍不派工。

本階段的單一結果是：從**隔離且已提交的虛構 Git fixture** 讀取同一 commit 的
index／ticket leaf 原始 bytes，驗證上節封閉 schema、digest、綁定與依賴圖後，
呼叫既有 `project_mainline_tickets` 產生**候選 metadata**。fixture declaration 與
observation 均明標測試替身，不可成為本專案 authority、真遠端 readback、派工、
receipt、Host qualification 或 closure 證據。產品模組只持有受限的 source-read
port；Git fixture 的建立／提交／讀取限測試專用暫存目錄，不能寫共享 worktree、
正式 ref 或外部 remote。

| 票面欄位 | 30A 建置候選（待精確 Grant） |
| --- | --- |
| SPEC／需求 | 原 `PRD-20260805-009`／`CHG-20260805-009`、workflow-governance SPEC revision 02 AC-9；不建立新 PRD／SPEC |
| 控制、實作、獨審 | Root 控制與 reviewer orchestrator；一名由當下 Profile 選定的 `implementation-standard` 實作者在 repo-contained `.worktrees/skill-improvement-30a-fixture`／`codex/skill-improvement-30a-fixture`；另一席獨審者不與實作者共用 worktree。具名 task／Agent 在派工前才精確綁定 |
| Baseline／lane | 本次文件最終受審 commit 作實作 baseline，派工前完整 SHA 讀回；same-lifetime direct lane，bridge／receipt `NOT_REQUIRED`。Grant 前不建立實作 worktree 或派工 |
| 可新增 | `library/local_orchestration/mainline_source.py`：單一責任為受限 raw-byte committed-ticket source assembly；`tests/test_mainline_source.py`：專屬 fixture、正反驗收與突變。兩檔各有 AC-9 消費者與驗收，不複製現有投影／測試框架 |
| 可修改 | 無。重用 `library/workflow_router/mainline_projection.py`、`library/local_orchestration/project_authority/` 的型別與 observation，以及現有投影測試；若真需要改既有公開契約，先回同票修訂 allowlist，不能順手擴權 |
| 禁止 | `dispatch_authority.py`、Router／Host／runner／CLI、正式 PRD／SPEC／Context／authority declaration、其他 tests 與 target 產品；不得 push、deploy、release 或清理非本 fixture 資產 |
| 預期增量／產物 | 產品碼一個單責新模組、聚焦測試一檔；既有產品檔零、正式治理文件零、持久測試產物零。行數只作結構審查訊號，修正不重置原票預算；fixture 必須有 owner、TTL、teardown |
| Return | `IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、candidate SHA、實際檔案、具名測試／型別／反向突變、真實來源與 Host 未驗證項；實作者不整合、不推送 |

供 Owner **與上述 SPEC bootstrap 例外一起**精確核發的 Grant 候選：project 為本 `Johnny_AI_Skill`、
operation 僅 `Ticket 30 / 30A fixture source-and-test build`、原
`PRD-20260805-009`／`CHG-20260805-009`、上述 SPEC revision 02 AC9；
baseline 為本次 docs-only 最終獨審 commit（完整 SHA 於回件提供，核發時 pin，
不得用 `HEAD` 浮動值）；actor 為 Profile 選定的一名實作者，Root 為唯一 control
orchestrator，另一名不同席位獨審；branch/worktree、`create` 兩路徑、
`modify = none`、禁止範圍、Closure 30A-F1–F4、命令與 return 均以本節精確文字為限。
有效期只涵蓋本 Ticket 30A 一次受控候選實作與同票修正，修正不重置原預算；
候選 SHA 和逐項驗收須由獨審後才可受控本地整合。此段**不是** Grant 簽發、
不加入 `johnny-boundary`；實際 actor/task/worktree identity 須在派工時讀回並綁定，
任何不匹配或超界改動 fail closed。Grant 不涵蓋正式 source migration、
`admit_dispatch`／native spawn effect、push、release 或 deployment。

有限 Closure revision 候選：

1. `30A-F1`：同一 fixture commit 的唯一 index fence 與每個 committed leaf fence 經
   原始 bytes hash、嚴格 UTF-8／JSON 驗證；index↔leaf identity／status／dependencies
   完全一致。A waiting、獨立 B `ready_for_recheck`、依賴 A 的 C waiting；B 完成不
   使 A 或 required mainline 關閉。
2. `30A-F2`：working-copy 改動或另一 commit 的 leaf 不污染釘選 commit；錯 digest、
   缺 leaf、跨 feature／`..` path、重複 key／fence、非法 UTF-8、未知欄位、重複／
   未知／循環依賴及 index↔leaf 不符均有限拒絕，**零候選投影**。
3. `30A-F3`：caller 自報 repository/ref/SHA、ticket metadata 或 tracking ref 不可升格
   成真 authority；fixture port 只接受綁定 synthetic observation。同一 exact blob
   最多讀一次，無 retry、polling、cache fallback；結果／log／Router state 不含 raw
   bytes。對 `admit_dispatch`、native spawn、receipt store 設零呼叫 sentinel。
4. `30A-F4`：公開 success／failure DTO 經一般 constructor／round-trip 建構，
   strict mypy、聚焦投影回歸、compile/import、`git diff --check` 全綠；實作者對
   digest 與 leaf binding 做紅→綠突變，獨審從不同入口改壞 committed leaf 或
   source SHA，具名格轉紅且精確還原。

預定命令：`python -m pytest tests/test_mainline_source.py tests/test_mainline_projection.py -q`、
`python -m mypy --strict library/local_orchestration/mainline_source.py`、
`python -m compileall -q library/local_orchestration/mainline_source.py`、`git diff --check`。
此節是**票面候選**，不是已跑結果或有效 `johnny-boundary`。受限 bootstrap
例外依原 SPEC Change Control 精確核准／獨審生效，且 Owner 核發精確 Grant
後，才將兩個 `create` 路徑轉成票內唯一活躍機器邊界、凍結 Closure revision、
獨審票面並派工；不能讓候選文字先取得 mutation authority。

## 剩餘正式來源啟用與 Grant

Control plane 須從已核准 target artifacts 決定實際 mainline 的成員、required flags、
依賴、owner/handoff 與 revisions，先以 docs-only migration version 到該 feature
index；不得拿本票的 schema 示例、敘事 status table 或 Agent 自報填入 authority
facts。同時須讀回 admitted `ProjectAuthorityContract` 的精確 declaration
artifact/revision。上節 **fixture-only 30A** 僅可經已生效的 SPEC bootstrap 例外
及精確 ticket Grant 建置與驗證，
但不能取代正式 migration。實際 target source 啟用與後續 `admit_dispatch` effect
驗證仍須遷移完成、獨審、正式 declaration readback 與另外的精確 effect Grant／
Host qualification；凡超出既有 SPEC 的產品、安全或權限邊界仍須 Change Control。

## P0 preflight 與未來 acceptance 下限

30A fixture 的 SPEC bootstrap 例外及 Grant 均生效、精確票面凍結後，
Architecture Owner 才能把該建置 slice 修成 type-only dispatchable cut；新型別
實際 constructor preflight 及獨審通過後才准同 owner 寫 parser/source-read 行為。
正式 target/effect slice 另待上游來源決策。依上節有限建構順序與各 slice 適用範圍：

- 用 ordinary public constructors 建立所有 success/failure DTO、enum、port request/result，
  覆蓋 exact primitive、nullability、finite disposition；禁止 `Any`、`cast`、coercion、
  bypass constructor、未驗證 dict 或動態 member lookup。
- 30A fixture 證明 caller 自報資料不能取代**synthetic observation 綁定**與 committed
  readback；正式 target/effect slice 才須證明它不能取代 admitted declaration 與 fresh
  direct observation。local tracking ref 在兩者都只可為 diagnostic。
- 命名 normal cell：A precise wait、independent B 為 `ready_for_recheck`、C 依賴 A 而
  waiting，且 B 完成後 A／required mainline 仍開放。
- 命名 failure cells：30A fixture 的 committed source missing/ambiguous/malformed、
  index↔leaf revision mismatch、incomplete/unknown/cyclic dependency；正式 slice 另覆蓋
  declaration 缺失及 direct observation unavailable/not-found/ambiguous/stale/moved/
  identity mismatch。全部 fail closed 且無 projection。
- 命名 boundary cells：30A fixture 的每個 exact blob 最多一次 read、無 retry/polling/
  cache fallback、raw content 不進 result/log/state、candidate 不觸發 Router/Host；正式
  slice 另證明一次 fresh direct observation。
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

對**source/test 實作派遣**，文件獨審及精確 baseline 綁定前返回：

```text
DOCUMENT_REVIEW_PENDING / NON_DISPATCHABLE
```

文件獨審／精確綁定通過後，按 Owner 已核准的條件式 Grant 記錄完整 baseline、
ticket blob、具名 owner／reviewer／worktree／branch，啟用唯一 `johnny-boundary`
並回 `AUTO_CONTINUE → IMPLEMENT`；不再索取相同範圍的 Owner 核准。
正式 source migration 和 Host effect 各維持後續獨立准入，不得以 30A 的綠燈
代替；不得把普通工程選擇升級成人工決策。

## 票面收斂與獨審紀錄

初稿 `76f6f32771e80add10c499db2c7479377b079c0c` 因推定 Grant、固定本專案
索引路徑、自創未遷移 grammar／公開 API 及硬行數上限，被獨立
`/root/wg_spec_review` 判為 `BLOCKED`。同票修正 `c5d6e2ff295883a03b49ffd3e8d72fbe51db0bb6`
撤回這些聲明；控制分支最終票面提交
`7e2dae948c5a949ad3f14aa0351f3b4edd0303f7` 由同一獨審者唯讀複驗
`PASS`，只代表 docs-only preflight 可用，不代表 implementation admission。
最終差異僅本 leaf 與同功能 registry；`git diff --check` 乾淨、
`tests/test_ticket_template_contract.py` 44 passed。完整 Ticket 30／清單 02
仍維持 `NON_DISPATCHABLE`。其後 Architecture Owner 在既有 SPEC 授權內收斂了上列
通用技術 source contract；這不是 target facts migration 或 implementation Grant。

## Source contract decision review — 2026-10-18

Architecture Owner 的 docs-only 決策提交 `0bfb4a2869f9fbb73e67a3c1a436a8e341fd66c2`
初審有兩項 source-binding finding：不能只讀 index 而不從 committed leaves 建圖，
以及既有字串型 blob result 不能證明 raw-byte digest。同票修正
`f13f35711594af241c83b803f91f0f472baa6241`（本 leaf blob
`823ef2d0e86bbc74a8508263be1a8bde678f6324`）由不同獨審席位唯讀複驗
`PASS`，兩項閉合；詳見
`doc/reviews/workflow-governance/30-trusted-independent-ticket-continuation-code-review.md`。
這只封閉通用 source schema 的技術選擇，不使 30A 可派工；target facts migration、
declaration readback、ticket-scoped Grant 與 qualified Host effect 均仍缺。
Root 在獨審之後對控制分支執行
`python -m pytest tests/test_mainline_projection.py tests/test_ticket_template_contract.py -q`：
`59 passed`、exit 0；`git diff --check` exit 0。這是既有純投影與模板回歸，
不是 30A source adapter 的 runtime 測試，也不代替上述獨審。
