# 73｜Every review records its round and the cause of any rework; a report sums them per ticket

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2, R4-7; CodeReview.md §3 and §5; REQ-20261103-043, owner decision 2026-11-18 "B", lesson L-12） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision03 / receipt under `.worktrees/73-rework-out/` / owner implementation seat / worktree `.worktrees/73-rework` / branch `cp/wave3-73-rework` / baseline the wave-3 branch after ticket 76 is integrated |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `INTEGRATED`; dispatch=sha256:bffe4ff1c013ea8b6f80d49ca9cc682fe432c0a9a5b4f3b886f7ac384e4135e6 (`doc/handoffs/2026/workflow-governance/dispatch/JAS-73-1.yaml`)（candidate `b5121ee0` at `3cd4bf5d`; CI run 44608980985 green; S73-01 and S73-03 carried to wave 4） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/73-rework` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/73-rework-review` |
| 責任邊界 | the `rework-record` block in `CodeReview.md` §3, a report script, its README section, its tests, and the blocks of the wave-3 code-review records |
| 禁止修改 | every gate script other than the new one, `library/`, the `review-verdict` and `convergence-disposition` grammar, and every finding in an existing review record |
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

Process tier: strict.

**The problem.** Ticket 69 measures what a seat costs in tokens. It does not measure how often a ticket goes back. Rework is where cost and delay concentrate: in waves 2 and 3, each round sent back cost one more implementation and one more independent review. Nothing records the cause of each round. The cause is one of these:

- a rule the control plane wrote;
- a return that was not true;
- something the design did not foresee;
- an implementation detail.

The owner decided on 2026-11-18 ("B") that each ticket records its review rounds and the cause of each rework.

**Revision02** answers the rule-only review of revision01, and **revision03** the correction review of revision02 (`doc/reviews/workflow-governance/73-review-rounds-and-rework-cause-ticket-review.md`). The changes:

- causes now follow mechanically from the finding classes;
- the block, the report line and the exit codes are exact;
- only code-review records carry the block.

After this ticket:

1. **Scope.** The `rework-record` block appears only in code-review records (`doc/reviews/<feature>/<ticket>-…-code-review.md`).
   - A pre-dispatch rule-only review (`…-ticket-review.md`) carries no block and counts in no round, because it is outside the `CodeReview.md` §5 count.
   - One code-review record holds exactly one ticket. The ticket id is the record's file name up to its first `-`.
2. **The block.** `CodeReview.md` §3 gains one bullet: each review section of a code-review record ends with a fenced `rework-record` block that directly follows the section's `review-verdict` block. The report pairs each non-`RETURN` block with the nearest `review-verdict` block before it.
   - **Who writes it.** The reviewer writes the block at the end of its own section.
   - **A `CHANGE_DETECTED` return before any review** is a round too. Its block stands before the first review section; the control plane writes it.
   - **What does not change.** The `review-verdict` and `convergence-disposition` grammar, and `integrate.py`, which reads only those two blocks and ignores any other fence.
   - **The fields.** The block holds exactly these five lines, in this order, each key once:

     ```text
     candidate: <40 lower-case hex, or none>
     round: <1, 2, 3 … in order of appearance in the record; no leading zero>
     kind: INITIAL | CORRECTION | RETURN
     verdict: APPROVED | CHANGES_REQUESTED | BLOCKED | CONVERGENCE_REVIEW_REQUIRED | CHANGE_DETECTED
     causes: <empty, or causes joined by "," with no blank and no repeat, in the order of the table below>
     ```

   - `kind` copies the label the control plane set in the review request before dispatch (`rule-review-label`). `RETURN` marks a `CHANGE_DETECTED` return; its `candidate` is the returned commit, or `none`.
   - `round` is this record's own counter. It does not replace §5's count, which restarts with each closure revision.
   - `verdict` equals the section's `review-verdict` verdict, and `candidate` equals its candidate. For a `RETURN` block, `verdict` is `CHANGE_DETECTED`.
3. **Causes, mechanically from the findings.**
   - The causes are empty for `APPROVED`. They are empty for `CONVERGENCE_REVIEW_REQUIRED` only when the record has an `APPROVED` `convergence-disposition` for that candidate; otherwise they are not empty. For `CHANGES_REQUESTED`, `BLOCKED` and `CHANGE_DETECTED` they are not empty.
   - They come from every finding the section asks to have corrected, which is every §4 class except `OUT_OF_SCOPE_HARDENING`. A finding's class is the first §4 class named in its class cell. Each class maps to exactly one cause:

     | Cause | Mapped from |
     | --- | --- |
     | `CONTROL_PLANE_RULE` | `TICKET_DEFECT` |
     | `RETURN_UNTRUE` | an `EVIDENCE_DEFECT` whose finding cites a return or receipt statement that the evidence contradicts |
     | `DESIGN_UNFORESEEN` | `REQUIREMENT_CHANGED`, and every `RETURN` block |
     | `IMPLEMENTATION_DETAIL` | `IMPLEMENTATION_DEFECT`, and every other `EVIDENCE_DEFECT` |

4. **`rework_report.py`.** It is called as:

   ```text
   python rework_report.py RECORD...
   ```

   - **Per ticket**, it prints one line: `<ticket> rounds=<n> CONTROL_PLANE_RULE=<a> RETURN_UNTRUE=<b> DESIGN_UNFORESEEN=<c> IMPLEMENTATION_DETAIL=<d> final=<verdict>`.
     - Each cause count is the number of rounds that name the cause. A round with two causes counts once under each.
     - `final` is the last round's `verdict`, as recorded.
   - **After the ticket lines**, it prints one total line: `TOTAL tickets=<t> rounds=<n> CONTROL_PLANE_RULE=<a> RETURN_UNTRUE=<b> DESIGN_UNFORESEEN=<c> IMPLEMENTATION_DETAIL=<d>`.
   - **Reds.** Each red is one line naming the record and the reason:
     - `NO_REWORK_RECORD`: a code-review record with no block;
     - an unclosed fence;
     - a missing, repeated or out-of-order field;
     - a value outside its grammar;
     - an unknown cause;
     - causes that break item 3;
     - rounds that skip, repeat or do not start at 1;
     - a `verdict` or `candidate` that differs from the paired `review-verdict`;
     - a non-`RETURN` block with no `review-verdict` block before it;
     - a `RETURN` block after the first `review-verdict` block.
   - **Exit codes, red before fault as R4-2 states:**
     - when any red is found, the exit is 1; every red is printed, and each fault goes to standard error;
     - when no red is found but a record is unreadable or not UTF-8, the exit is 2;
     - otherwise the exit is 0;
     - 3 is a usage error.
5. **Backfill.** The implementation seat writes the blocks of these code-review records: 65, 66, 67, 68, 69, 70, 72, 74, 75 and 76.
   - It derives the causes from each record's own findings, by item 3. It changes no finding, and lists in the STATEMENT any finding whose class it found hard to map.
   - The two `CHANGE_DETECTED` returns before review are given here, each a `RETURN` block with `candidate: none`, before the record's first review section:
     - ticket 65's, before closure revision02 (65 record, line 213);
     - ticket 70's, before closure revision02 (70 record, line 237).
   - Tickets 71 and 73 get their blocks in their own reviews.
6. **The scripts README.**
   - Its introduction becomes "Twelve" and names `rework_report.py`.
   - `rework_report.py` joins the tool-fault list.
   - A section describes the block and the report.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/73-rework`.
- reviewer：`ticket-review` seat in `.worktrees/73-rework-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; CodeReview.md §3 to §5; the code-review records of item 5.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a command-line script and documents; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the block, the cause mapping, the report lines and the exit codes above.

## TDD 設計

1. 正常行為:
   - the report prints the exact lines for a fixture set of records, including a record with a `RETURN` round and a round with two causes;
   - in `tests/test_rework_report.py`, `integrate.check_review` gives the same result for a record with and without the block.
2. 規則違反／輸入錯誤: one test for each red of item 4.
3. 外部失敗／fail-closed:
   - an undecodable record beside a record with a red gives exit 1, with the fault on standard error;
   - an undecodable record alone gives exit 2.
4. 回歸保護: `tests/test_integrate.py` and `tests/test_gate_contract.py` pass unchanged; the README pin there is computed from the scripts present.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | the ticket id is the file name up to the first `-`; `65-…` against `650-…` |
| 2 | null／空字串／陣列 | 是 | empty causes on a `CHANGES_REQUESTED` round (red); non-empty causes on an `APPROVED` round (red); `candidate: none` outside a `RETURN` block (red) |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | cause names exact and case-sensitive; `round: 01` (red); `causes: A, B` (red); a 39- or 41-character candidate (red) |
| 5 | 錯誤碼是否一致 | 是 | red before fault (R4-2) |
| 6 | 例外是否會拋出 | 是 | undecodable input does not raise |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_rework_report.py tests/test_integrate.py tests/test_gate_contract.py -q` exits 0.
  - `mypy --strict --python-version 3.11` on the script and its test exits 0.
- **O1**: the report run over the ten backfilled records. Its output is captured, and the report gives exit 0 on them.
- **反向突變證據**, each restored after it turns a named test red:
  - accept an unknown cause;
  - accept causes on an `APPROVED` round;
  - let a fault suppress the reds;
  - accept a skipped round;
  - skip the cross-check against `review-verdict`.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last).

## 正式環境移植 SOP

- 不適用：a plugin script and documents.

## 完成回寫

The control plane writes these rows.

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
