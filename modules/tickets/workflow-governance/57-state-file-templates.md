# 57｜State-file templates: a new project starts with the files the gates read

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-1 pending dispatch, R4-7 merge-queue file and receipt cell, R4-8 state-file templates, as confirmed by the owner on 2026-11-05） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision02 / receipt under `.worktrees/57-state-file-templates-out/` / owner implementation seat / worktree `.worktrees/57-state-file-templates` / branch `cp/wave2-57-state-file-templates` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11 for the test（CONTEXT.md Implementation language）; the templates are Markdown and JSON |
| 狀態 | `INTEGRATED`（candidate `f423748b` integrated on `cp/wave2-gates` at `7da279a7` on 2026-11-06; record `doc/reviews/workflow-governance/wave2-integration-2026-11-06.md`） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/57-state-file-templates` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/57-state-file-templates-review` |
| 責任邊界 | the target-project templates for the ticket state row, the receipt, the queue file and the integration configuration, the template README, one test file and one `.gitattributes` line |
| 禁止修改 | everything else, every gate script and this repository's own `modules/tickets/TEMPLATE.md` included |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = template/README.md
modify = template/modules/tickets/TEMPLATE.md
create = template/doc/handoffs/governance/MERGE-QUEUE.TEMPLATE.json
create = template/doc/handoffs/governance/integration.TEMPLATE.json
create = template/doc/handoffs/governance/RECEIPT.TEMPLATE.md
create = tests/test_state_file_templates.py
modify = .gitattributes
forbid = skills/
forbid = library/
forbid = modules/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = .github/
```

## 使用者拍板與可觀察結果

The owner approved wave 2 and R4-8 on 2026-11-04 and confirmed the queue-branch correction on 2026-11-05. A project created from `template/` starts with the four state files the wave-2 gates and the integration script read, so the first ticket needs no hand-made file:

- **Ticket state row** (`template/modules/tickets/TEMPLATE.md`): the `狀態` row reads `` `<STATE>`; dispatch=sha256:<64 lower-case hex of the dispatch file>; receipt `<repository-relative receipt path>` ``, with the allowed states listed as now plus `REVIEW_APPROVED` and `CONVERGENCE_REPLANNED`; the row says the `dispatch=` and receipt parts are present while a dispatch is pending (R4-1) and how the digest is computed (sha256 of the dispatch file's bytes).
- **Queue file** (`MERGE-QUEUE.TEMPLATE.json`): exactly `{"entries": []}` and a final newline; its location in a project is the `queue_path` on the queue branch (ticket 50), which the template README states.
- **Integration configuration** (`integration.TEMPLATE.json`): one object with exactly the keys of ticket 50's configuration table (`remote`, `branch`, `queue_branch`, `queue_path`, `spec_command`, `invariant_command`, `ci_status_command`, `timeout_seconds`), each with a placeholder value of the right JSON type; the argument lists are lists of strings and `ci_status_command` holds exactly one `{sha}`.
- **Receipt** (`RECEIPT.TEMPLATE.md`): one run cell in the R4-7 shape with the five fields (`cell`, `candidate`, `tool_digest` with one `path=sha256` line, `capture`, `exit`) and a raw block, one `STATEMENT` cell, LF only, written so that filling the placeholders gives a receipt the evidence gate (ticket 51) can read; it names which placeholders a seat replaces.
- The template README adds the four files to the fixed structure and to the build order, and states that the queue file lives on the queue branch, not on the integration branch.
- **Line endings** (revision02): `.gitattributes` gains one line, `template/doc/handoffs/governance/* text eol=lf`, so the three files come out LF in every checkout (a CRLF queue file is a schema break for ticket 50); the existing lines stay as they are. The test judges every byte rule (LF only, final newline, exact bytes, no BOM) on the committed blob, so a CRLF working copy of a correct candidate is green.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/57-state-file-templates`.
- reviewer：`ticket-review` seat in `.worktrees/57-state-file-templates-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket, ticket 50 (configuration and queue schema), ticket 51 (receipt grammar), R4-1, R4-7, R4-8.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：templates and one test; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the five template paths above and `tests/test_state_file_templates.py`
- 公開契約／資料模型：the schemas of tickets 50 and 51, read from those tickets; the test holds the expected key sets as data, not by importing a gate script.

## TDD 設計

1. 正常行為：the queue template parses to `{"entries": []}`; the configuration template has exactly the eight keys with the right types; the receipt template has one run cell with the five fields and one statement cell; the ticket template's state row carries the `dispatch=sha256:` and receipt parts.
2. 規則違反／輸入錯誤：a test that fails if a key is added, removed or renamed in the configuration template, if `ci_status_command` holds no or two `{sha}`, if the queue template holds an entry, or if the receipt template has a CR byte or a missing field.
3. 外部失敗／fail-closed：the JSON templates parse with repeated keys refused and `NaN` refused; a BOM in any template is a failure.
4. 回歸保護：when `skills/johnny-project-takeover/scripts/evidence_gate.py` is present, the receipt template filled with a real capture and digest by the test passes it (exit 0); when `integrate.py` is present, its configuration parser accepts the configuration template with placeholders replaced. Both checks skip with a stated reason when the script is absent.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | `queue_path` placeholder is a canonical repository-relative path; template file names exact |
| 2 | null／空字串／陣列 | 是 | empty `entries`; no empty argument list in the configuration template |
| 3 | 權限繞過 | 否 | templates grant nothing |
| 4 | Token 格式與比較 | 是 | the `dispatch=sha256:` form and the `{sha}` placeholder compared exactly |
| 5 | 錯誤碼是否一致 | 否 | no exit codes in templates |
| 6 | 例外是否會拋出 | 否 | no runtime code beyond the test |

## 完成定義與證據

- `python -m pytest tests/test_state_file_templates.py -q` exit 0; `mypy --strict --python-version 3.11` on the test file exit 0; stdlib only.
- **反向突變證據**：remove a key from the configuration template, add an entry to the queue template, add a CR to the receipt template, drop the `dispatch=` part from the state row, each → a named test red → restore.
- Receipt: R4-7 cells; `tool_digest` lists the three wave-1 scripts; every cell runs at the committed candidate; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9).
- `tests/test_plugin_payload_boundary.py` and `tests/test_plugin_distribution_payload_manifest.py` pass apart from `CommittedPinTests::test_the_pinned_sha_exists`; full suite under the host lock: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：templates are copied into a new project by its owner.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record section "Revision01 initial review". S57-02 is a `TICKET_DEFECT`: nothing pinned the templates' line endings, so the boundary gains `.gitattributes` and the line-endings bullet above. This is a closure rebuild: the work is one additive correction commit on the revision01 candidate `27318feb`, and the next review is the revision02 initial review.

| Finding | Class | Work in correction 1 |
| --- | --- | --- |
| S57-01 | IMPLEMENTATION_DEFECT | LF, final-newline, exact-byte, BOM and CR checks read the committed blob (`git cat-file blob HEAD:<path>` or the index), not the working copy; shape checks normalise first; a test runs the suite's byte rules in a clone checked out with `core.autocrlf=true` and is green |
| S57-02 | TICKET_DEFECT | the `.gitattributes` line above; a test that `git check-attr eol` gives `lf` for each of the three files |
| S57-03 | EVIDENCE_DEFECT | a test that `queue_branch` differs from `branch` in the configuration template (counter-mutation C3 red) |
| S57-04 | IMPLEMENTATION_DEFECT / EVIDENCE_DEFECT | the README's structure comment and State-files row say the queue lives on the queue branch, and a test pins each place (D1, D2 red); the copy-to path reads `modules/tickets/<feature>/<ticket>.md` as in AGENTS.md |
| S57-07 | EVIDENCE_DEFECT | M1 tails keep `SUBFAILED` lines; P1 runs with `-rs` so the skip reason is in a capture |

Carried, no work here: S57-05 (the integrate.py cross-check runs the template's own list shapes) goes to ticket 50's landing; S57-06 (placeholder enforcement and wording in the receipt template) is out-of-scope hardening.

### Correction 2 under revision02 (after the revision02 initial review `CHANGES_REQUESTED`)

No ticket defect was found, so revision02 stands. S57-08 (confinement): the clone in `CrlfCheckoutTests` is made with `--no-hardlinks`, so removing it never changes a file of the repository under test, and a test asserts that the mode bits of that repository's object files are the same after the class as before. P1 runs with `-rfEs` so a red capture names its failures (S57-11). Carried, no work here: S57-09 (a working copy that differs from the committed blob is not red), S57-10 (README sentences outside the pinned places). The next review is the one correction review of revision02.

### Carried after approval (CodeReview §5 rule B)

S57-05 goes to ticket 50's landing; S57-06, S57-09, S57-10 and S57-12 go to the next change of the templates or this test file. The disposition and its reasons are in the review record.
