# 61｜Wave-2 acceptance (1): one ticket end to end on a fixture project, finished by a fresh session from files alone

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-1, R4-4, R4-7, R4-8, as amended 2026-11-07; REQ-20261103-043 implementation readiness criterion 1） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/61-wave2-end-to-end-out/` / owner implementation seat / worktree `.worktrees/61-wave2-end-to-end` / branch `cp/wave2-61-wave2-end-to-end` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11 for the test（CONTEXT.md Implementation language）; Markdown for the run record |
| 狀態 | `IN_PROGRESS`（part A returned (candidate `4215b980`); part B run recorded at `ac251c87`; initial review dispatched） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | part A: `implementation-standard` seat, worktree `.worktrees/61-wave2-end-to-end`; part B: the seats the control plane starts for the run, each named in the run record |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/61-wave2-end-to-end-review` |
| 責任邊界 | one end-to-end test, and the record of one live run on a fixture project outside this repository |
| 禁止修改 | everything else; no gate script, template, spec or governance document changes in this ticket |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
create = tests/test_wave2_end_to_end.py
create = doc/reviews/workflow-governance/wave2-acceptance-1/
forbid = skills/
forbid = library/
forbid = template/
forbid = modules/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = .github/
forbid = ci/
```

## 使用者拍板與可觀察結果

The owner set wave-2 acceptance criterion 1 on 2026-11-03 (REQ-20261103-043, implementation readiness):

> On a fixture target project, at least one ticket goes from a requirement snapshot through dispatch, implementation, independent review and merge-queue integration to a landed commit. The session is deliberately ended mid-ticket, and a new session finishes it from the ticket, receipt and queue files alone.

This ticket gives the criterion two pieces of committed evidence.

### A. The loop as a test (`tests/test_wave2_end_to_end.py`)

In a temporary directory the test builds a fixture target project from `template/`: a git repository with a local bare remote, a queue branch, and an `integration.json` filled from `integration.TEMPLATE.json`. Its `ci_status_command` is a script inside the fixture that answers `green`.

It then drives the real scripts, each as a subprocess with no patch, through one ticket:

1. `requirement_snapshot.py take` on a one-row requirement list.
2. A ticket written from `template/modules/tickets/TEMPLATE.md`, with its state row carrying `dispatch=sha256:` of a dispatch file that `dispatch_lint.py` passes.
3. An implementation commit on a seat branch, with a receipt built from `RECEIPT.TEMPLATE.md` around a real capture. `evidence_gate.py` passes it.
4. A review record with a `review-verdict` block committed on the integration branch.
5. `integrate.py submit`, then `land`, then `readback`.

The test ends with the queue entry `LANDED`, `landed_sha` a merge commit whose second parent is the candidate, and the remote integration branch at that commit.

**The session break.** The loop is cut in two after step 3. The second half runs in a new Python process that is given only the fixture's path. That process holds no object, variable or argument from the first half. It reads the ticket state row, the receipt and the queue file to decide what is left, and finishes steps 4 and 5. A second case cuts after step 4 instead (after `submit`, before `land`). The test asserts that the decision the second process makes from the files equals the step that was in fact next.

### B. One live run with fresh agent sessions (`doc/reviews/workflow-governance/wave2-acceptance-1/`)

The control plane runs the same loop once with real seats on a fixture project outside this repository (`C:/Temp/claude/jas61-fixture`, with its bare remote beside it):

- A first implementation seat takes the requirement snapshot, writes the dispatch, and makes the implementation commit. It is then stopped on purpose before its receipt; this is the mid-ticket session end.
- A second, fresh seat is given only the fixture's path and the instruction to continue the open ticket by the plugin's rules. It gets no transcript and no summary of the first seat's work. It must find where the ticket stands from the files, then finish the receipt.
- An independent reviewer seat reviews.
- Integration runs `integrate.py submit`, `land` and `readback`.

The record directory holds:

- a `RUN.md` naming each seat, its model, its start and end, and the exact instruction each was given;
- the ticket, receipt, review record, queue file and `integration.json` as they stood at the end, copied byte for byte;
- `git log --graph` of the fixture's integration and queue branches;
- the first seat's last tool output and the second seat's first file reads, showing that the resume came from the files.

No script is committed under `doc/reviews/`.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane; it also conducts part B and writes its record.
- implementation owner：part A, `implementation-standard` seat in `.worktrees/61-wave2-end-to-end`.
- reviewer：`ticket-review` seat in `.worktrees/61-wave2-end-to-end-review`; it reviews part A and the part B record.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; REQ-20261103-043; tickets 50 to 57 for the scripts and templates the loop uses.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a test and a run record; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：`tests/test_wave2_end_to_end.py`
- 公開契約／資料模型：the state files of ticket 57 and the queue schema of ticket 50, read through the scripts.

## TDD 設計

1. 正常行為：the full loop lands one merge commit and reads back `LANDED`. Each of the two session cuts resumes at the right step from the files alone.
2. 規則違反／輸入錯誤：
   - The second process refuses to continue when the ticket state row's `dispatch=` digest does not match the dispatch file.
   - It refuses when the receipt fails `evidence_gate.py`.
   - It refuses when the review record does not admit the candidate.
   - In each case nothing is landed.
3. 外部失敗／fail-closed：
   - When the fixture remote is unreachable at `land`, the result is exit 2 and the queue is unchanged.
   - When `ci_status_command` answers red, the entry is `LANDED_CI_RED` and a second `land` is blocked.
4. 回歸保護：the test runs only the committed scripts and templates as subprocesses, with no patch. A change to any of them that breaks the loop turns it red.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | paths come from the fixture the test builds |
| 2 | null／空字串／陣列 | 否 | no new input shape |
| 3 | 權限繞過 | 是 | a review record that does not admit the candidate lands nothing; the second process gets no state but the files |
| 4 | Token 格式與比較 | 是 | the `dispatch=sha256:` digest compared with the dispatch file |
| 5 | 錯誤碼是否一致 | 是 | unreachable remote exit 2; red CI blocks |
| 6 | 例外是否會拋出 | 是 | the second process on a broken state file |

## 完成定義與證據

- `python -m pytest tests/test_wave2_end_to_end.py -q` exit 0, and the test passes on both CI jobs. `mypy --strict --python-version 3.11` on the test exit 0. Stdlib only, no `Any`.
- **反向突變證據**：each mutation below turns a named test red; then restore.
  - Give the second process an in-memory value from the first.
  - Skip the digest check.
  - Land without a review record.
  - Treat a red readback as green.
- Part B: the record directory holds every item listed above. The reviewer confirms from the second seat's first reads that it resumed from the files.
- Receipt: R4-7 cells, passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (P9) and `evidence_gate.py` (E1, run last). The full suite runs under the host lock: its failure set is a subset of the base names, with zero new red.

## 正式環境移植 SOP

- 不適用：a test and a record; the fixture lives outside this repository and is removed after the run.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
