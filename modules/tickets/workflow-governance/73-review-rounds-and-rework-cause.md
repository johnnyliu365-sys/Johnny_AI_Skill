# 73｜Every review records its round and the cause of any rework; a report sums them per ticket

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2, R4-7; CodeReview.md §3 and §5; REQ-20261103-043, owner decision 2026-11-18 "B", lesson L-12） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/73-rework-out/` / owner implementation seat / worktree `.worktrees/73-rework` / branch `cp/wave3-73-rework` / baseline the wave-3 branch after tickets 67 and 72 are integrated |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED`（after ticket 67, which also changes `CodeReview.md`, and ticket 72, which also changes the scripts README） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/73-rework` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/73-rework-review` |
| 責任邊界 | the `rework-record` block in `CodeReview.md` §3, a report script, its README section, its tests, and the wave-3 review records' blocks |
| 禁止修改 | `integrate.py` and every other gate script, `library/`, the review-verdict grammar |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = CodeReview.md
modify = skills/johnny-project-takeover/scripts/README.md
modify = doc/reviews/workflow-governance/
create = skills/johnny-project-takeover/scripts/rework_report.py
create = tests/test_rework_report.py
forbid = skills/johnny-project-takeover/scripts/integrate.py
forbid = skills/johnny-project-takeover/scripts/evidence_gate.py
forbid = library/
forbid = Workflow.md
forbid = AGENTS.md
```

## 使用者拍板與可觀察結果

**The problem.** Ticket 69 measures what a seat costs in tokens. It does not measure how often a ticket goes back. Rework is where the cost and the delay concentrate: in waves 2 and 3, a round sent back cost one more implementation and one more independent review. Nothing records the cause of each round. That cause is one of these:

- a rule the control plane wrote;
- a seat's return that was not true;
- something the design did not foresee;
- an implementation detail.

The owner decided on 2026-11-18 ("B") that each ticket records its review rounds and the cause of each rework.

After this ticket:

- **`CodeReview.md` §3** gains one bullet: every review record ends each review section with a fenced `rework-record` block, after its `review-verdict` block. The `review-verdict` grammar and `integrate.py` do not change, because the integration script reads only `review-verdict`. The new block holds:

  ```text
  candidate: <sha>
  round: <1-based review round of this ticket, across closure revisions>
  kind: INITIAL | CORRECTION
  verdict: <the review-verdict of this section>
  causes: <comma-separated list, empty when the verdict is APPROVED>
  ```

  `causes` takes values from this fixed set, each mapped from the CodeReview §4 classes of the blocking findings:

  | Cause | Mapped from |
  | --- | --- |
  | `CONTROL_PLANE_RULE` | `TICKET_DEFECT`, or a blocking finding caused by the control plane's own dispatch or ticket edit |
  | `RETURN_UNTRUE` | an `EVIDENCE_DEFECT` where the return claimed something the evidence does not show |
  | `DESIGN_UNFORESEEN` | `REQUIREMENT_CHANGED` and every `CHANGE_DETECTED` return |
  | `IMPLEMENTATION_DETAIL` | `IMPLEMENTATION_DEFECT` |

  A `CHANGE_DETECTED` return before any review is recorded as a round of its own, with `kind: INITIAL`, `verdict: CHANGE_DETECTED` and `causes: DESIGN_UNFORESEEN`.
- **`rework_report.py`:**

  ```text
  python rework_report.py RECORD...
  ```

  It prints one line per ticket, with:
  - the number of rounds;
  - the rounds by cause;
  - the final verdict.

  It also prints a total line.

  Exit codes, as R4-2 sets them:
  - 0: the input is read;
  - 1: a malformed `rework-record` block, an unknown cause, a non-empty cause list on an `APPROVED` round, or rounds out of order. Every red is printed, even when a fault is met on the way;
  - 2: an unreadable file;
  - 3: a usage error.
- **The wave-3 review records** of tickets 65, 66, 68, 69, 70 and 72 gain their blocks. The control plane names the cause of each round. The seat checks each block against the record's own findings and lists any disagreement in the STATEMENT; it changes no finding. The ticket 65 record, for example, starts like this, and the reviewer determines the rest:
  - round 1, the `CHANGE_DETECTED` before review: `DESIGN_UNFORESEEN`;
  - round 2, the initial review: `IMPLEMENTATION_DETAIL`.
- **The scripts README** describes the block and the report.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/73-rework`.
- reviewer：`ticket-review` seat in `.worktrees/73-rework-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; CodeReview.md §3 to §5; the wave-3 review records.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a command-line script and documents; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the block and the cause set above.

## TDD 設計

1. 正常行為:
   - the report prints the right totals for a fixture set of records;
   - `integrate.py`'s existing tests pass unchanged with records that carry the new block.
2. 規則違反／輸入錯誤: one test each for:
   - a missing field;
   - an unknown cause;
   - causes on an `APPROVED` round;
   - round numbers that skip or repeat;
   - a `kind` outside the two values.
3. 外部失敗／fail-closed: an undecodable record is exit 2, and the reds of the other records are still printed.
4. 回歸保護: `tests/test_integrate.py` passes unchanged.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule |
| 2 | null／空字串／陣列 | 是 | an empty cause list on a `CHANGES_REQUESTED` round is red |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | cause names exact and case-sensitive; ASCII digits only in `round` |
| 5 | 錯誤碼是否一致 | 是 | red before fault (R4-2) |
| 6 | 例外是否會拋出 | 是 | undecodable input does not raise |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_rework_report.py tests/test_integrate.py -q` exits 0.
  - `mypy --strict --python-version 3.11` on the script and its test exits 0.
- **O1**: the report run over the wave-3 review records, with its output captured.
- **反向突變證據**, each restored after it turns a named test red:
  - accept an unknown cause;
  - accept causes on an `APPROVED` round;
  - let a fault suppress the reds;
  - accept a skipped round.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last).

## 正式環境移植 SOP

- 不適用：a plugin script and documents.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
