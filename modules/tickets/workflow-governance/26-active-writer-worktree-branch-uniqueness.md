# 26｜Active writer worktree／branch uniqueness

| 欄位 | 內容 |
| --- | --- |
| State | `SLICE_LOCAL_INTEGRATED` at `9cedb55f`；獨審通過，清單項目 06 尚未完成 |
| Authority | `modules/spec/receipt-bound-role-supervision.md` AC-17；Owner 本次要求防止共用工作樹互相覆蓋 |
| Source baseline | 本票所在 docs-only commit；獨立實作 worktree |
| Implementation language | Python 3.11；沿用現有 worker-assignment ledger／鎖 |
| Implementation owner / reviewer | 分席；Reviewer 不改實作者 worktree |
| Profile | `STANDARD`；只改本機派工 claim，無外部服務／push |

## 邊界宣告

```johnny-boundary
modify = library/local_orchestration/worker_assignment.py
modify = tests/test_worker_assignment.py
forbid = modules/spec/
forbid = skills/
forbid = doc/requirements/
```

## Objective／契約

現有 ledger 對 receipt 唯一，但兩個不同 receipt 可以同時 `CLAIMED` 同一
`worktree_ref` 或 `branch_ref`。在同一既有 OS-visible ledger lock 內，對非 terminal
assignment 增加 worktree/branch 互斥；已 `SETTLED` 的不同 receipt 不再佔用
worktree/branch，但原 receipt tombstone 仍禁止再次 claim。不得新增平行 registry、
timer、runner 或 ticket 狀態機。本票只處理這個已存在的受控 worker-claim 入口，
不宣稱攔住同步直派、任意工具寫入或 prewrite Git CAS；清單 06 須保持未完成。

## Work／驗收

1. 同 receipt 重 claim 維持原 `RECEIPT_ALREADY_CLAIMED`，包含 settled tombstone。
2. 不同 receipt 的 active claim 若共用 worktree 或 branch，使用具名有限拒絕；
   ledger byte 不變、第一位 writer 不被取代。不同 worktree **且** branch 可並行。
3. Settled 後，新的 receipt 可重用原 worktree/branch；同 receipt 不能重用。
4. 既有跨 process 鎖內決策，加入兩個不同 receipt 競爭同一 worktree 的並發回放。
   不得靠線程測試冒充 OS race。無法安全執行並發回放則回報缺口，不得宣稱完整。
5. Reviewer 反向突變工作樹互斥判斷：對應 cell 紅，還原綠；並核對 branch 對稱性。

Run：`python -m pytest tests/test_worker_assignment.py -q`、`git diff --check`。
Return：`IMPLEMENTED | BLOCKED | CHANGE_DETECTED`、candidate SHA、變更檔、測試數與
失敗輸出、反向突變、scope deviations、未驗證項。若需要改 receipt issuance 語意、
Host effect 或 AC-17，停止並回主 session。
