# 27｜Ticket status projection 的必要證據守衛

| 欄位 | 內容 |
| --- | --- |
| State | `OPEN`；Owner 2026-10-18 改進清單項目 07 的第一個獨立切片 |
| Authority | Owner 要求完成、獨審、本機、實機及發布分開；必要子項 `NOT_VERIFIED` 不得被總驗收藏起 |
| Source baseline | 本票所在 docs-only commit；獨立 worktree |
| Implementation language | Python 3.11；沿用既有 `ticket_status_pipeline.py` 與顯示模板 |
| Implementation owner / reviewer | 分席；Reviewer 不修改候選工作樹 |
| Profile | `STANDARD`；純本機狀態投影，無外部 effect |

## 邊界宣告

```johnny-boundary
modify = library/local_orchestration/ticket_status_pipeline.py
modify = library/local_orchestration/ticket_status_template.py
modify = tests/test_ticket_status_pipeline.py
modify = tests/test_ticket_status_template.py
create =
delete =
forbid = modules/spec/
forbid = skills/
forbid = doc/requirements/
```

## Objective／Work

現有 owner-visible `johnny-status` 的 `APPROVED` 是自由宣告，`stage` 只有
`DONE | OPEN`；缺必要驗證時可能顯示已通過。沿用同一 parser/renderer，以顯式
opt-in 的擴充 stage 欄位增加必要性與證據引用，不改歷史三欄 block 的讀取語意：

`stage = <ref> | <label> | <DONE|OPEN|NOT_VERIFIED> | <REQUIRED|OPTIONAL> | <evidence-ref|->`

1. 新五欄格式與舊三欄不得混寫；新格式每個 DONE stage 都要非空、受限格式的
   evidence reference，未完成 stage 只能用 `-`；同一 ref 不得重複。舊三欄保持相容。
2. 五欄格式下，`state = APPROVED` 而任何 REQUIRED stage 為 `OPEN` 或
   `NOT_VERIFIED` 時，parser 拒絕；`DONE` 也不能代表 `APPROVED`，仍須獨審狀態。
   OPTIONAL 未完成可保留而不擋其他必要項。`NOT_VERIFIED` 顯示時不得用完成樣式。
3. 以固定情境涵蓋實作、獨審、本機驗證、實機驗收與發布（未適用的階段不必捏造
   DONE）；必要對抗驗證 `NOT_VERIFIED` 禁止顯示總項 APPROVED，OPTIONAL 待辦
   不擋必要完成；壞 block 仍出現在 `unreadable` 而非消失。
4. 不從 evidence 字串推斷真實核准，這張票只阻止狀態投影的邏輯假綠；
   來源／Review 真實性仍由現有 Reviewer 與 admission 驗證。不得宣稱本票單獨完成
   checklist 07 的父項／finding 責任收斂或取代正式結案 gate。

Run：`python -m pytest tests/test_ticket_status_pipeline.py tests/test_ticket_status_template.py -q`、
`git diff --check`。Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、candidate SHA、
變更檔、測試／反向突變結果、scope deviations、未驗證項。Reviewer 另席從錯誤的
`APPROVED + REQUIRED/NOT_VERIFIED` 做反向突變並還原。
