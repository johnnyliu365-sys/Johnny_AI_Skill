# 75｜The repository's own tickets follow the harness: the ticket template carries the target rows, and dispatch lint checks the dispatch digest

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-1, R4-7; REQ-20261103-043, owner decision 2026-11-19 "A" on dispatch digests, owner request 2026-11-19 to update `modules/tickets/TEMPLATE.md`） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision03 / receipt under `.worktrees/75-own-tickets-out/` / owner implementation seat / worktree `.worktrees/75-own-tickets` / branch `cp/wave3-75-own-tickets` / baseline the wave-3 branch after ticket 74 is integrated |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `IN_PROGRESS`; dispatch=sha256:2cbb06108d7033455b47da4477983be2b15fb1dea7ae52c030f4dc4b0f85b393 (`doc/handoffs/2026/workflow-governance/dispatch/JAS-75-1.yaml`)（revision03; strict tier; rule-only reviews: revision01 and revision02 CHANGES_REQUESTED; revision03 applies the reviewer's exact fixes; after ticket 74） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/75-own-tickets` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/75-own-tickets-review` |
| 責任邊界 | the repository's own ticket template; dispatch lint rule R7, its README section and its tests |
| 禁止修改 | `template/`, every other gate script, `library/`, the governance documents, every existing ticket |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = modules/tickets/TEMPLATE.md
modify = skills/johnny-project-takeover/scripts/dispatch_lint.py
modify = skills/johnny-project-takeover/scripts/README.md
modify = tests/test_gate_dispatch_lint.py
forbid = template/
forbid = library/
forbid = AGENTS.md
forbid = Workflow.md
forbid = CodeReview.md
forbid = skills/johnny-project-takeover/references/
```

## 使用者拍板與可觀察結果

Process tier: strict.

**The problem.** The plugin requires each target project to bind a dispatched ticket to its dispatch file: the state row carries `dispatch=sha256:<hex>` of that file. This is R4-1's default route, set out in `template/modules/tickets/TEMPLATE.md:17`. The repository's own tickets did not do this.

- Its own template, `modules/tickets/TEMPLATE.md`, is an older version. It has no dispatch digest, and it lacks the target template's rows for closure revision, strict checker, profile and XSS classification. Its defect-category heading cites `CodeReview.md` §2.1, which does not exist (S61 gap 1).
- Its dispatch files lived outside the repository, so nothing could check what a seat had been sent.

On 2026-11-19 the owner chose "A":
- keep the dispatch files that still exist, in `doc/handoffs/2026/workflow-governance/dispatch/`;
- record their digests in the state rows of tickets 65 to 72;
- do not reconstruct digests for older tickets;
- make a check refuse a dispatch without a matching digest, so the rule does not depend on memory.

The owner also asked for the old template to be updated.

**Revision02** answers the rule-only review of revision01, and **revision03** the correction review of revision02 (`doc/reviews/workflow-governance/75-own-tickets-follow-the-harness-ticket-review.md`).

After this ticket:

1. **`modules/tickets/TEMPLATE.md` carries the target rows.**
   - It gains the rows `Closure revision`, `Strict checker`, `Profile / resource` and `XSS classification`, worded as in `template/modules/tickets/TEMPLATE.md`.
   - Its 狀態 row takes exactly this repository form: `` `<STATE>`; dispatch=sha256:<64 lower-case hex> (`<repository-relative dispatch path>`)（<optional note>） ``.
     - `<STATE>` is one of the target's eight states: `PLANNED`, `IN_PROGRESS`, `BLOCKED`, `DONE`, `SUPERSEDED`, `REVIEW_APPROVED`, `INTEGRATED` and `CONVERGENCE_REPLANNED`.
     - The digest is written when the ticket is dispatched. A ticket never dispatched carries none.
   - The note under the row states two deliberate deviations from the target grammar:
     - the digest is kept after `INTEGRATED` (owner decision 2026-11-19 "A");
     - the receipt path stays in the Agent Context binding row.
   - The defect-category heading cites `CodeReview.md` §2 and the "Defect categories" table of `review-checks.md`, as the target template does.
   - The 完成定義 section keeps its reverse-mutation wording. It does not take the target's "紅燈輸出" slot, which contradicts `implementation-tdd.md`.
   - Its machine-readable boundary block, role assignment and frontend sections stay as they are. The target template lacks them, and this ticket does not change `template/`.
   - The `Process tier:` template line is not added here. Ticket 74's `rule-process-tier` leaves it to wave 4.
2. **Dispatch lint R7 checks the digest.** `dispatch_lint.py` gains an option `--ticket <ticket-file>`. Without it, the lint behaves exactly as before. With it, R7 works as follows:
   - **Which cell.** R7 takes the first table row whose first cell is exactly `狀態`.
   - **The digest.** That cell must hold exactly one `dispatch=sha256:`. The run of `[0-9A-Za-z]` after it must be exactly 64 characters, all in `[0-9a-f]`, and equal to the sha256 of the dispatch file's bytes. Text after that run is ignored, whether it is a space, `(`, `;` or the end of the cell.
   - **Red, exit 1, each with a problem line starting `R7` that names the expected and the found digest:**
     - no 狀態 row;
     - an empty 狀態 cell;
     - no `dispatch=sha256:`;
     - two `dispatch=sha256:` in the cell;
     - a run of a length other than 64;
     - upper-case hex;
     - a digest that does not match the file.
   - **Usage, exit 3.** An unreadable or non-UTF-8 ticket file gives exit 3, as dispatch_lint already classifies an unreadable dispatch file (`scripts/README.md:7`, `:30`). It prints nothing on stdout and is decided before R1 to R7 run.
   - **The script's own text.** The module docstring, the `USAGE` string, the `## dispatch_lint.py` usage line and the README section describe R7 and the option. The README's line 7 sentence, that dispatch_lint "reads one file", is updated.
   - The spec's exit list for dispatch lint (`modules/spec/workflow-governance.md:171`, `0 / 1 / 2 / 3`) differs from README:7, which says it has no tool fault. That difference is older than this ticket, and goes to wave 4.
3. **Order and naming of dispatch files.**
   - **The README section states only the generic order:**
     - the dispatch file names a base that precedes the commit that records the file and its digest;
     - the digest is written into the ticket's state row in the control plane's checkout, not in the worktree leaf at the base;
     - `dispatch_lint.py <dispatch> --ticket <ticket>` runs next, and the dispatch goes out only on exit 0;
     - dispatch files are named as R4-1 names them, `<ticket>-<n>.yaml`, where `<n>` is the dispatch revision;
     - a file whose digest is recorded is never rewritten.
   - **Repository-specific facts stay out of the plugin README.** The `JAS-` prefix, the seven existing `JAS-<NN>.yaml` files, and ticket 75's own dispatch going out without `--ticket` (R7 does not exist before it lands) are control-plane records. The control plane writes them in the "Dispatch digests" note of `modules/tickets/workflow-governance/README.md`.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/75-own-tickets`.
- reviewer：`ticket-review` seat in `.worktrees/75-own-tickets-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a template and a command-line script; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：R7 and the `--ticket` option above.

## TDD 設計

1. 正常行為:
   - a ticket whose state row carries the dispatch file's digest passes R7;
   - an observation run, listed in the capture, runs the lint with `--ticket` on each of the seven dispatch files under `doc/handoffs/2026/workflow-governance/dispatch/` against its ticket. Each run prints no `R7` line. JAS-67 exits 0. The other six exit 1 on R5 only, which is expected because they predate R5 (ticket 72).
2. 規則違反／輸入錯誤: each red case of item 2 has its own test, and so do these two:
   - a digest of another file;
   - the dispatch file changed by one byte after the digest was written.

   A digest followed by ` (`, by `; ` or by the end of the cell passes.
3. 外部失敗／fail-closed: an unreadable ticket and a non-UTF-8 ticket each give exit 3, with empty stdout.
4. 回歸保護: every R1 to R6 test passes unchanged, and a run without `--ticket` gives the same output as before on the same file.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule |
| 2 | null／空字串／陣列 | 是 | an empty 狀態 cell (exit 1); `dispatch=sha256:` with nothing after it (exit 1) |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | 63 and 65 characters (exit 1); upper-case hex (exit 1); `<hex>x` (exit 1); two `dispatch=sha256:` tokens (exit 1); a digest followed by ` (` or `; ` (pass) |
| 5 | 錯誤碼是否一致 | 是 | 1 for R7; 3 for an unreadable ticket, as dispatch_lint classifies an unreadable dispatch file |
| 6 | 例外是否會拋出 | 是 | the unreadable-ticket case |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_gate_dispatch_lint.py -q` exits 0.
  - `mypy --strict --python-version 3.11` on the script and its test exits 0.
- **反向突變證據**, each restored after it turns a named test red:
  - accept upper-case hex;
  - skip R7 when the digest is missing;
  - compare only the first 16 hex characters.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last), and the typed return in STATEMENT.

## 正式環境移植 SOP

- 不適用：a template and a plugin script.

## 完成回寫

The control plane writes these rows.

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
