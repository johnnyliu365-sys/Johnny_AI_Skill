# 76｜Every seat's model and effort are bound to its profile: the dispatch names them, the USAGE cell records them, and the usage report goes red on a mismatch

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（R4-7; REQ-20261103-043 readiness criterion 5, owner direction 2026-11-19: tokens stay the unit; model and effort are recorded beside them） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision03 / receipt under `.worktrees/76-seat-binding-out/` / owner implementation seat / worktree `.worktrees/76-seat-binding` / branch `cp/wave3-76-seat-binding` / baseline the wave-3 branch after ticket 75 is integrated |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `IN_PROGRESS`; dispatch=sha256:277328602a04edfe8b3847cb58a4126966eb3dd1c4ee895e139990458dcbe426 (`doc/handoffs/2026/workflow-governance/dispatch/JAS-76-1.yaml`)（revision03; strict tier; rule-only review of revision01 CHANGES_REQUESTED, revision02 APPROVED; revision03 adds the reviewer's three exact sentences; after ticket 75） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/76-seat-binding` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/76-seat-binding-review` |
| 責任邊界 | the expectation and receipt templates, this repository's own expectation file, `usage_report.py`, `evidence_gate.py`'s USAGE grammar, dispatch lint R8, their README sections and tests, the token-use section and revision record of the dispatch runbook |
| 禁止修改 | `library/`, `AGENTS.md`, `Workflow.md`, `CodeReview.md`, the skill references, every existing ticket and receipt |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = template/doc/handoffs/governance/usage-expectation.TEMPLATE.json
modify = template/doc/handoffs/governance/RECEIPT.TEMPLATE.md
modify = template/README.md
modify = skills/johnny-project-takeover/scripts/usage_report.py
modify = skills/johnny-project-takeover/scripts/evidence_gate.py
modify = skills/johnny-project-takeover/scripts/dispatch_lint.py
modify = skills/johnny-project-takeover/scripts/README.md
modify = doc/runbooks/dispatch-model-profile.md
modify = tests/test_usage_report.py
modify = tests/test_gate_evidence.py
modify = tests/test_gate_dispatch_lint.py
modify = tests/test_state_file_templates.py
create = doc/handoffs/2026/workflow-governance/usage-expectation.json
forbid = library/
forbid = AGENTS.md
forbid = Workflow.md
forbid = CodeReview.md
forbid = skills/johnny-project-takeover/references/
```

## 使用者拍板與可觀察結果

Process tier: strict.

**The problem.** The token expectation is a count of tokens per profile. A count is comparable only between seats that ran the same model at the same effort, and nothing bound either.

- **The model.** Ticket 67's implementation seat ran `claude-opus-5-5`, because the control plane started it without naming a model. Every earlier wave-3 implementation seat ran `claude-sonnet-5-5`. Its two receipts were then compared with limits measured on Sonnet:
  - the first pass processed about 31.8 million tokens;
  - the correction receipt processed 55.1 million.
- **The effort.** A tally of the last 40 seat transcripts shows Sonnet seats at both `high` and `medium`. The provider-neutral registry of the dispatch runbook says `xhigh` for `implementation-standard`, `ticket-review` and `implementation-elevated`. No seat chose its effort deliberately.

On 2026-11-19 the owner set the direction:
- tokens stay the unit of account, like a stable coin;
- prices change, so no price table is used;
- what is recorded beside the tokens is the model and the effort.

The host transcript records both on every message (`"model"`, `"effort"`), so a program can read them.

**Revision02** answers the rule-only review of revision01, and **revision03** adds the three sentences the correction review offered (`doc/reviews/workflow-governance/76-seat-model-and-effort-bound-ticket-review.md`). Model names stay out of shipped files.

After this ticket:

1. **Value grammar.** A model or effort value is one item matching `[A-Za-z0-9][A-Za-z0-9._-]*`. A list of values joins items with `,`, with no blanks and no repeats, in order of first appearance. Comparison is case-sensitive.
2. **The expectation names a model and an effort, and the shipped template stays provider-neutral.**
   - Each profile entry is exactly `{"model": <one item>, "effort": <one item>, "output_tokens_max": <int>, "processed_tokens_max": <int>}`.
   - The shipped `template/doc/handoffs/governance/usage-expectation.TEMPLATE.json` holds the placeholders `"<host-model>"` and `"<host-effort>"`. It names no provider or model, as the runbook requires (`dispatch-model-profile.md:27-30`).
   - This repository's own copy, `doc/handoffs/2026/workflow-governance/usage-expectation.json`, which is not shipped, holds this host's values with the owner-confirmed token limits:
     - `implementation-standard`: `claude-sonnet-5-5` at `high`, as observed on the seats of tickets 65, 66, 68, 69, 70 and 72;
     - `ticket-review`: `claude-opus-5-5` at `high`, as observed;
     - `implementation-elevated`: assumed equal to `ticket-review` until measured, since no elevated seat has run.
   - The runbook records these as observed host data, not dispatch policy, in a `REVISION_04` entry of its revision record. The provider-neutral registry is unchanged.
   - The registry's `xhigh` for all three profiles differs from the observed `high`. That difference is a calibration item for the owner, and this ticket does not change it.
   - `template/README.md`'s row for the expectation names all four fields.
3. **The USAGE cell records the effort.**
   - The USAGE grammar gains one line, `effort: <value list>`, directly after `model:`. The shipped `RECEIPT.TEMPLATE.md` gains that line with an `<effort>` placeholder.
   - `evidence_gate.py` accepts the line only in that position. A value that breaks the grammar is a defect line `USAGE_FIELD_INVALID` (exit 1).
   - A USAGE cell without the line stays valid, so receipts written before this ticket still pass. evidence_gate prints nothing new.
4. **The usage report prints the model and effort, and goes red on a mismatch.**
   - Each USAGE cell prints `<seat> <profile> model=<value list> effort=<value list|UNRECORDED> output=<n> processed=<n> <verdict>`.
   - The verdict is a comma-joined list of words, in this fixed order:
     - `MODEL_MISMATCH`: the cell's model list is not exactly the profile's one model;
     - `EFFORT_MISMATCH`: the cell's effort list is not exactly the profile's one effort;
     - `OVER_OUTPUT`;
     - `OVER_PROCESSED`;
     - `EFFORT_UNRECORDED`: the cell has no `effort:` line.
   - `WITHIN` is printed only when none of the other words applies. `UNKNOWN_PROFILE` is unchanged, and stands alone: no other word is appended to it.
   - `MODEL_MISMATCH`, `EFFORT_MISMATCH` and the `OVER_*` words are reds (exit 1). `EFFORT_UNRECORDED` alone is not.
   - A value in a receipt or in the expectation that breaks the grammar of item 1, and an expectation entry missing `model` or `effort`, are schema breaks (exit 2). Reds print first, as R4-2 sets.
5. **The dispatch names them (R8).**
   - A dispatch file with a top-level `profile:` field must also carry top-level `model:` and `effort:` fields. Top-level means a field at column 0, outside a code fence.
   - Each of `model:` and `effort:` must have a non-empty value that obeys item 1.
   - A missing or invalid field is red (exit 1). After the per-line rules, the lines are exactly `R8 profile: without model:`, `R8 profile: without effort:`, `R8 model: invalid` and `R8 effort: invalid`, in that order, each printed when it applies. Each value is one item of item 1, optionally inside one pair of double quotes; a list is invalid in a dispatch.
   - R8 runs with or without ticket 75's `--ticket`. R1 to R7 are unchanged.
   - Ticket 75's regression test "without `--ticket` the output is as before" may change only for files that carry `profile:`. The STATEMENT names each such change.
6. **The runbook's token-use section** says:
   - the control plane starts every seat with the model and effort its dispatch names;
   - a mismatch is a red that the review record explains;
   - the elevation route for a hard ticket stays `implementation-elevated`, with its own entry.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/76-seat-binding`, started with the model and effort its dispatch names.
- reviewer：`ticket-review` seat in `.worktrees/76-seat-binding-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：command-line scripts and JSON and Markdown templates; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the value grammar, the expectation entry, the USAGE `effort:` line, the report line and its verdict order, and R8 above.

## TDD 設計

1. 正常行為:
   - a USAGE cell matching its profile's model and effort, within its limits, prints `WITHIN`;
   - an observation run, listed in the capture, runs the report with the repository's own expectation file on these receipts:
     - `RETURN.md` under `C:/Users/User/Desktop/Johnny_AI_Skill/.worktrees/` in `65-retire-engine-and-private-router-out`, `66-retire-bridge-out`, `68-archive-specs-out`, `69-token-use-per-seat-out`, `70-templates-out` and `72-lint-out`;
     - both receipts of ticket 67: `.worktrees/67-doc-sweep-out/RETURN.md` and `.worktrees/67-doc-sweep-out-c1/RETURN.md`.

     Each prints `EFFORT_UNRECORDED`. Ticket 67's implementation cells also print `MODEL_MISMATCH`. Ticket 71 has no receipt yet.
2. 規則違反／輸入錯誤:
   - another model;
   - two models in one cell;
   - another effort;
   - `High` against `high`;
   - a mismatch together with `OVER_PROCESSED`, in the fixed order;
   - a value with a blank, an empty value and a repeated item: `USAGE_FIELD_INVALID` in evidence_gate, exit 2 in the report;
   - an expectation entry missing `model` or `effort` (exit 2);
   - each R8 case of item 5.
3. 外部失敗／fail-closed: an unreadable expectation or receipt stays exit 2, with reds printed first.
4. 回歸保護:
   - every existing usage_report, evidence_gate and dispatch-lint test passes, or changes only where the new grammar or report line requires it, with each change named in the STATEMENT;
   - `tests/test_state_file_templates.py` pins the new template placeholders and field order;
   - an unfilled expectation template is a schema break (exit 2). The cross-check fills both placeholders with the USAGE fixture's model and effort before it runs the report.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule |
| 2 | null／空字串／陣列 | 是 | an empty `effort:` value; an empty model list; `model: ""` in a dispatch |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | `claude-sonnet-5-5` against `claude-sonnet-5-5-fast`; `high` against `High`; `a,b` against `b,a` (a mismatch against a one-item profile either way); `a, b` (invalid) |
| 5 | 錯誤碼是否一致 | 是 | 1 for a mismatch, `USAGE_FIELD_INVALID` or R8; 2 for a schema break; 3 for usage |
| 6 | 例外是否會拋出 | 否 | no new I/O |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_usage_report.py tests/test_gate_evidence.py tests/test_gate_dispatch_lint.py tests/test_state_file_templates.py -q` exits 0, apart from base failures, each named.
  - `mypy --strict --python-version 3.11` on the three scripts and their tests exits 0.
- **反向突變證據**, each restored after it turns a named test red:
  - ignore the model;
  - ignore the effort;
  - compare the effort case-insensitively;
  - drop R8;
  - print `WITHIN` beside `EFFORT_UNRECORDED`.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last), and the typed return in STATEMENT.

## 正式環境移植 SOP

- 不適用：plugin scripts and templates.

## 完成回寫

The control plane writes these rows.

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
