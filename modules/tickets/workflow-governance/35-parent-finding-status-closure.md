# 35｜Ticket status 的父項與 Finding 可追蹤結案

| 欄位 | 內容 |
| --- | --- |
| State | `SLICE_LOCAL_INTEGRATED` at `215a599f`；獨審通過，清單 07 的正式證據來源／結案准入仍開放 |
| Authority | Owner 清單 07；沿用既有 `PRD-20260805-009`／`CHG-20260805-009` 與 Ticket 27，不建新 PRD |
| Baseline | 派工時精確釘選本控制分支 HEAD；實作／審閱不同隔離 worktree |
| Profile／roles | `STANDARD`；實作者低成本適配模型，另一席不低於實作者的獨立審閱 |
| Nature | 現有 `johnny-status` owner-visible 投影；不成為正式 Router/Review 授權來源 |

## 邊界宣告

```johnny-boundary
modify = library/local_orchestration/ticket_status_pipeline.py
modify = library/local_orchestration/ticket_status_template.py
modify = tests/test_ticket_status_pipeline.py
modify = tests/test_ticket_status_template.py
forbid = library/workflow_router/
forbid = skills/
forbid = modules/spec/
forbid = doc/requirements/
```

無新檔、無第二套狀態機；沿用現有 parser、`build_document` 與 renderer。實作者先查重用現有 stage/evidence 解析與 escaping helper。原始碼只留技術註解，不能塞 Owner prompt 或工單敘事。

## Work／驗收

1. 以向下相容的可選 metadata，讓一張 ticket 宣告精確子票 ID 與 `REQUIRED|OPTIONAL`，以及 Finding 的 ID、責任人、`OPEN|CLOSED` 與去向。`CLOSED` 必須有非空且受限格式的 disposition/evidence ref；`OPEN` 必須保留責任人但不得冒充已結案。不得讓任意字串被當核准證據。
2. 在同一次 `build_document` 的已讀票集合中解析 parent→child；同一 ID 重複、未知 required child、自我相依、循環、required child 非 `APPROVED`，都不能產生一列假 `APPROVED` parent。保持 `unreadable` 顯式錯誤而非靜默略過或全域凍結無關票。Optional child 未完成不擋 parent，其狀態仍顯示。
3. Parent `APPROVED` 若有 `OPEN` Finding、Finding 無責任人或已結案 Finding 缺去向，必須拒絕／標示不可讀；合法 Finding 保留 ID、owner、去向供人查。輸入及模板 HTML escape 必須沿用既有安全邊界。
4. 不改舊三欄 block 既有語意；無 child/finding metadata 的既有五欄 block 仍照舊。這只是狀態投影，不能宣稱驗證 evidence-ref 的實際內容或授予正式 closure。必要 evidence 的真偽仍在既有 Review/Router admission。
5. 固定情境：A 的必要 stage 為 `NOT_VERIFIED`、B approved、parent 宣告二者為 required 時 parent 不可顯示通過；B optional 未完則 parent 可通過；無關 C 仍可正常顯示。Finding OPEN 保留 owner 且不得假裝已有去向、CLOSED 缺去向、未知 child、循環及惡意 HTML 值均有回歸格。Reviewer 對 required-child 放寬與 Finding-open 放寬各做反向突變紅→還原綠。

Run：`python -m pytest tests/test_ticket_status_pipeline.py tests/test_ticket_status_template.py -q`、`git diff --check`。Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、候選 SHA、路徑、測試/突變結果、非權威範圍、findings/deviations。若需改正式 Review/Router grant、既有 AC 或新增來源，回 `CHANGE_DETECTED`，不得自行擴張。

## 實作與獨審結果

候選 `f65120b9` 的初次獨審發現重複父票 ID 仍可顯示 `APPROVED`；原票原分支以 additive correction `5c6b33a4` 修正。原 reviewer 在公開 `build_document` 入口重跑，兩筆重複父票均標為不可讀，無關票仍顯示；將重複判斷反向突變後對應測試轉紅，還原後轉綠。初次審閱對必要子票及 OPEN Finding 的兩項反向突變也均紅→綠。最終候選 121 tests／205 subtests 與 strict mypy 通過，四個宣告路徑的 Git blob 與受審候選相同；受控本地整合於 `215a599f`。詳見 `doc/reviews/workflow-governance/35-parent-finding-status-closure-code-review.md`。這一投影不驗證 evidence-ref 真偽，也不授予正式 Router／Review closure。
