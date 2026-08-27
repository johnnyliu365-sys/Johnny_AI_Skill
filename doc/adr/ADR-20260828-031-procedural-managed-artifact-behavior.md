# ADR-20260828-031｜Procedural managed-artifact behavior

- 日期：`2026-08-28（Asia/Taipei）`
- 狀態：`ACCEPTED`
- 決策者：Project owner
- 關聯規格：`SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2`（owner 接受後修訂）
- 關聯需求變更：`PRD-20260828-043`／`CHG-20260828-043`

## 背景與問題

AC-17 已要求每個正式 workflow/process/document artifact 都能沿
`root index -> bounded partition index -> exact leaf` 解析；R02C1 也已交付純解析器，
能在讀取時拒絕 cycle、duplicate parent、dangling node 與 edge metadata mismatch。
目前缺口在寫入面：`TargetDocumentPlan` 只表達一組精確文件 mutation，並未把「leaf
內容變更」與「直接父索引 edge 變更」定義成不可分割的同一個領域操作。因此 Agent
可以建立文件、通過一般路徑邊界，卻忘記更新索引，直到後來的 consumer 才發現
orphan artifact。

這個問題不能以擴充提示詞或持續載入完整 Context 解決。規則是否出現在當前 prompt
不應決定 artifact tree 是否正確；正確性必須來自 Agent 所能採取的正常操作、該操作
的有限結果，以及最終 authority gate。

Codex 官方文件確認：插件可攜帶 lifecycle hook；`PreToolUse` 能觀察多數本機 shell、
`apply_patch`、MCP 與 function-tool 呼叫並對支援的呼叫 block/rewrite；`Stop` 可在回傳
`decision: block` 時建立新的 continuation。同一份文件也明示 specialized tool path
可能不經預設 hook path，因此 hook 是 guardrail 而不是完整 enforcement boundary。
證據來源：[`Codex hooks`](https://learn.chatgpt.com/docs/hooks)，讀取日 `2026-08-28`。

## 決策

採用「provider-neutral managed operation + host behavior adapter + repository authority
gate」三層結構。

### 1. Provider-neutral managed operation

新增嚴格、有限的 managed-artifact 合約：

```text
ManagedArtifactAction = CREATE | REVISE | REPLACE | ARCHIVE

ManagedArtifactDecision =
    PLANNED
  | ARTIFACT_PATH_NOT_FOUND
  | PARENT_INDEX_NOT_FOUND
  | EDGE_STATE_MISMATCH
  | DUPLICATE_PARENT
  | LIFECYCLE_CONFLICT
  | BASELINE_MISMATCH
  | ARTIFACT_TREE_INVALID

ManagedArtifactPlan = {
  project_id,
  baseline_commit,
  action,
  selected_root_to_leaf_path,
  leaf_mutation,
  direct_parent_index_mutation,
  expected_post_state
}
```

Planner 是純函式：它只接受 caller 已選定的一條 root-to-leaf metadata path，不接受
raw prompt、聊天紀錄、任意 filesystem discovery、URI、絕對路徑或 callable。它計算
leaf digest/revision/lifecycle 與直接父 edge 的新 metadata，輸出有限 mutation plan。
既有 `TransactionalTargetDocumentWriter` 的 successor adapter 對 exact baseline 執行
all-or-nothing write；任何中途失敗都回復 leaf 與 index 的原始 bytes。成功回傳前，
既有 artifact resolver 必須由 candidate post-state 重新解析該選定路徑。

### 2. Host behavior adapter

Codex 第一個 adapter 由插件封裝，不寫入 target project 的 `.codex/`：

1. 插件提供具名 managed-artifact tool/command。Agent 提交 intent 與 exact selected
   metadata path；它不需要再執行一個「更新索引」步驟。
2. `PreToolUse` 對能可靠分類的 `apply_patch`、shell 與其他本機直接寫入進行拒絕；
   reason 只回傳受管工具名稱、normalized relative path ID 與 finite code
   `RAW_MANAGED_WRITE_DENIED`。無法可靠分類的命令不得被猜測式改寫成成功。
3. `Stop` 在 ending turn 以受影響的 exact path set 執行 candidate-tree validation。
   第一次發現 orphan、dangling 或 stale edge 時回傳 bounded correction continuation；
   `stop_hook_active = true` 或同 turn 已續跑時，回傳
   `BEHAVIOR_REPAIR_EXHAUSTED`，不得循環。
4. Hook 不保存 transcript、raw command、absolute path、secret 或 source body。插件解除
   安裝後 adapter 消失，target 文件與 Git 歷史不變。

Claude 或其他 host adapter 不在第一個 implementation cluster 內。Provider-neutral
合約不得匯入 Codex 名稱；未來只需新增經該 host 實測 admission 的 adapter，不重寫
planner、writer 或 repository gate。

### 3. Repository authority gate

Host hook 不承重 authority。`admit_document_mutation` 的 successor preflight 從
integration ref 讀 ticket boundary，從 candidate diff 取得受影響的 managed paths，
並僅沿那些 paths 所屬的 direct-parent chain 驗證 candidate post-state：

- 新 leaf 必須在同一 candidate 有一個 matching direct-parent edge；
- leaf digest/revision/lifecycle 改變時，直接父 edge 必須同步改變；
- replace/archive 必須移除或改寫 active edge，並建立契約要求的 replacement/archive
  edge；
- orphan leaf、dangling edge、duplicate parent、cycle、stale metadata 或 mixed lifecycle
  都在 Git merge 前回傳 `ARTIFACT_TREE_INVALID`；
- 無受管文件變更的 source ticket 不承擔額外全樹掃描成本。

Gate 從 authority branch 讀規則並從 candidate commit 讀變更；caller 或 Agent 的成功
宣稱不構成證據。只有 gate、non-force push 與 direct remote readback 完整時，結果才是
既有的 `AUTHORITY_INTEGRATED`。

## Composition、資料流與生命週期

```text
Agent intent
  -> host adapter (Codex first)
  -> ManagedArtifactPlanner (pure, provider-neutral)
  -> TargetDocumentTransactionPort
  -> transactional local adapter
  -> exact-path ArtifactTreeResolver post-check
  -> candidate commit
  -> repository artifact mutation preflight
  -> existing integration/push/readback authority flow
```

- Composition Root：插件 host lifecycle config 組合 Codex hook adapter 與受管工具；
  local-orchestration composition 組合 planner、transaction port 與 resolver；integration
  gate 只注入 Git reader/effect boundary，不匯入 host adapter。
- Ownership：target repository 擁有 leaf、index 與 Git history；插件擁有 hook、tool、
  planner policy 與 removable local control-plane code。
- Lifetime：planner per call；transaction adapter per operation；hook invocation per host
  lifecycle event；不得 cache target content 或建立 background service。
- Tests：pure planner 使用 in-memory nodes；writer 使用 disposable repository/forced
  failure adapter；host adapter 使用 official hook JSON fixtures；gate 使用 disposable Git
  candidates與 reviewer counter-mutation。
- Read projection：結果只輸出 action、finite decision、opaque artifact/index IDs、revision、
  digest與 candidate/authority commit identity。UI/console 只顯示 sanitized correction，
  不顯示 raw command、transcript、absolute path 或文件內容。

## Profile 與能力語意

這個機制不增加文件數量。`COMPACT`、`STANDARD`、`HIGH_ASSURANCE` 仍由 delivery profile
決定需要哪些 artifact；一旦某 artifact 被要求或明確建立，其 index invariant 對三個
profile 都相同。

Host behavior capability 有三種結果：

```text
ACTIVE         = installed, trusted/enabled and real hook behavior proved
UNAVAILABLE    = host lacks or disables the adapter; do not claim behavioral enforcement
NOT_APPLICABLE = the current host path does not use that adapter
```

`UNAVAILABLE` 不得阻擋純文件 writer 或 repository gate；它只表示缺少早期行為回饋。
反過來，`ACTIVE` 也不能取代 gate。

## Grill 收斂

| 問題 | 決策 |
| --- | --- |
| 可觀察結果 | Agent 使用一個 managed operation 後，leaf 與直接父 edge 同時正確；漏索引的 supported raw write 會立即失敗，ending turn 會得到一次 bounded repair。 |
| Error behavior | 每層只回傳 finite code；任何 ambiguous path、stale baseline、partial write、unavailable hook 或 invalid post-state 都不產生成功。 |
| Data owner/pipeline | Target owns documents/indexes; plugin planner normalizes intent to metadata, transaction writes candidate bytes, resolver/gate projects sanitized identity evidence. |
| Concurrency/consistency | Exact baseline compare-and-swap prevents stale plans；leaf/index 是一筆可恢復 transaction，不允許半完成狀態。 |
| Authorization | Hook 不授予文件 authority；ticket boundary、reviewer gate、push/readback 規則不變。 |
| Security/privacy | 不執行 hook input，不保存 raw command/transcript/secret；不產生 network/provider/background effect。 |
| Rollback | Revert source/plugin release removes adapter；既有 target documents remain. A failed transaction restores exact prior bytes. |
| XSS trigger | `N/A`：沒有 Browser/WebView/DOM/HTML rendering；未來若 UI 顯示不可信內容，需另走 XSS gate。 |
| Out of scope | Claude adapter、全 repo 歷史索引遷移、自動猜父索引、訓練/微調模型、next-major no-clone cache、publication/release effect。 |

## 替代方案與取捨

1. **只強化 skill/AGENTS 文字。** 拒絕：仍依賴當前 Context、trigger 與模型服從，沒有
   穩定的 action/result 因果。
2. **只有 Stop 時掃描並叫 Agent 修。** 拒絕作為主路徑：它把錯誤延後，且無法保證
   leaf/index 原子性；保留為 bounded recovery feedback。
3. **只有 pre-commit/CI。** 拒絕作為唯一控制：回饋太晚且可被 local actor 繞過；可
   作補充，但 authority 仍是 gate。
4. **PreToolUse 完全禁止所有 Markdown 寫入。** 拒絕：會誤傷 source/docs，且官方明示
   hook coverage 不是完整 enforcement boundary。
5. **為每個 provider 重寫文件系統。** 拒絕：provider-neutral planner/writer/gate 應只
   有一份；host 差異留在薄 adapter。

## 後果、風險與回復方式

- 優點：正確索引成為正常操作的既有結果；Agent 不需記第二步；漏索引在最早可觀察
  邊界得到回饋；所有旁路仍由 gate 擋住。
- 代價：新增 host hook/tool 的 packaging 與 installed qualification；現有
  `ArtifactDocumentKind`、writer result、refusal guidance 與 publication payload 都需
  演進。
- 誤判風險：hook 只拒絕能可靠解析的本機寫入；模糊 shell 不猜測、不宣稱攔截，由
  Stop/gate 接手。
- 迴圈風險：Stop continuation 僅一次，第二次輸出具名 exhaustion；owner/reviewer
  取得完整 sanitized evidence，而不是無限續跑。
- 相容風險：既有 resolver 與 unmanaged source path 保持不變；新 planner 只能透過
  新 contract 進入 writer。Provider adapter 採 additive registration。
- 回復：source candidate 可整體 revert；發布後可安裝上一個 immutable plugin 版本。
  Uninstall 不得修改 target repo。

## Owner 決策與後續路由

Owner 已接受本 ADR。Router 現可：

1. 建立並封存一份新的 Adaptive Project Orchestration Context revision；
2. 修訂既有 Adaptive Project Orchestration SPEC（不建立平行 SPEC）；
3. 在 exact SPEC Revision 09 另經 owner 核准後，由 reviewer 拆出 provider-neutral
   core、transaction adapter、Codex behavior adapter、repository gate 與 installed
   qualification 的串行 tickets；
4. 各 ticket 分別核准後才 dispatch；plugin publication/release 仍需另一張具名 effect
   ticket與直接 readback。

前兩步已完成，project owner 也已核准 exact SPEC Revision 09 draft
`ef1cd4a0c74023c58e04fd44d06c58c41b8daadf`。R09A 分解後因 absent/delete 與 ancestor
digest-cascade 公開契約未閉合而回到 `UPSTREAM_DECISION_REQUIRED`；project owner 已核准
exact SPEC Revision 10 correction `b0a973a8a66d0dbbd88e94990eaa8dc6716b7954`，恢復 reviewer
開立 R09A 的 authority。R09A 仍須另行核准，且沒有 implementation 或 release authority。

## 修訂／淘汰紀錄

- `2026-08-28`：建立 proposal；等待 project owner 接受、拒絕或要求修改。
- `2026-08-28`：Project owner 核准候選 commit
  `4a43b182b2913b1ea9a00b8dbec212eb84c89a33` 中的 ADR-031；授權建立新的 sealed
  Adaptive Project Orchestration Context revision 與既有 SPEC 的 owner-review draft。
- `2026-08-28`：Project owner 核准 exact SPEC Revision 09 draft
  `ef1cd4a0c74023c58e04fd44d06c58c41b8daadf`；只授權 reviewer 開立 R09A ticket。
- `2026-08-28`：R09A 分解發現 Revision 09 無法完整表示 present-to-absent delete，且未
  明訂 leaf digest 變更必須沿選定祖先鏈更新至 root；開票暫停，等待 Revision 10
  correction owner decision。
- `2026-08-28`：Project owner 核准 exact SPEC Revision 10 correction
  `b0a973a8a66d0dbbd88e94990eaa8dc6716b7954`；恢復 reviewer 開立 R09A ticket 的 authority。
