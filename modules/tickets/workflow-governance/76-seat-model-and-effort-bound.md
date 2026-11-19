# 76｜Every seat's model and effort are bound to its profile: the dispatch names them, the USAGE cell records them, and the usage report goes red on a mismatch

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（R4-7; REQ-20261103-043 readiness criterion 5, owner direction 2026-11-19: tokens stay the unit; model and effort are recorded beside them） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/76-seat-binding-out/` / owner implementation seat / worktree `.worktrees/76-seat-binding` / branch `cp/wave3-76-seat-binding` / baseline the wave-3 branch after ticket 75 is integrated |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED`（strict tier; rule-only review before dispatch; after ticket 75） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/76-seat-binding` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/76-seat-binding-review` |
| 責任邊界 | the expectation template, `usage_report.py`, `evidence_gate.py`'s USAGE grammar, dispatch lint R8, their README sections and tests, the token-use section of the dispatch runbook |
| 禁止修改 | `library/`, `AGENTS.md`, `Workflow.md`, `CodeReview.md`, the skill references, every existing ticket and receipt |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = template/doc/handoffs/governance/usage-expectation.TEMPLATE.json
modify = skills/johnny-project-takeover/scripts/usage_report.py
modify = skills/johnny-project-takeover/scripts/evidence_gate.py
modify = skills/johnny-project-takeover/scripts/dispatch_lint.py
modify = skills/johnny-project-takeover/scripts/README.md
modify = doc/runbooks/dispatch-model-profile.md
modify = tests/test_gate_usage_report.py
modify = tests/test_gate_evidence.py
modify = tests/test_gate_dispatch_lint.py
modify = tests/test_state_file_templates.py
forbid = library/
forbid = AGENTS.md
forbid = Workflow.md
forbid = CodeReview.md
forbid = skills/johnny-project-takeover/references/
```

## 使用者拍板與可觀察結果

Process tier: strict.

**The problem.** The token expectation is a count of tokens per profile. A count is comparable only between seats that ran the same model at the same effort. Nothing bound either.

- **Ticket 67's model.** Its implementation seat ran `claude-opus-5-5`, because the control plane started it without naming a model. Every earlier wave-3 implementation seat ran `claude-sonnet-5-5`. Its 55 million processed tokens were compared with a 24-million limit measured on Sonnet.
- **The effort was never set.** A tally of the last 40 seat transcripts shows Sonnet seats at both `high` and `medium`. The profile registry of the dispatch runbook says `implementation-standard` is xhigh. No seat chose its effort deliberately.

On 2026-11-19 the owner set the direction:
- tokens stay the unit of account, like a stable coin;
- prices change, so no price table is used;
- what is recorded beside the tokens is the model and the effort.

The host transcript records both on every message (`"model"`, `"effort"`), so a program can read them.

After this ticket:

1. **The expectation names its model and effort.**
   - Each profile entry of `usage-expectation.TEMPLATE.json` becomes exactly `{"model": <string>, "effort": <string>, "output_tokens_max": <int>, "processed_tokens_max": <int>}`.
   - The model and effort are host profile data. The runbook says they are copied per host, as the registry's provider-neutral names already require.
   - For this repository's host, the template holds:
     - `implementation-standard`: `claude-sonnet-5-5` at `high`;
     - `implementation-elevated` and `ticket-review`: `claude-opus-5-5` at `high`.

     The runbook says these are the observed wave-2 and wave-3 bindings. The registry's `xhigh` intent and the observed `high` differ; that difference goes to the owner as a calibration item and is not changed here.
2. **The USAGE cell records the effort.**
   - The USAGE grammar gains one line, `effort: <value>`, directly after `model:`.
   - When a seat's messages carry more than one model or effort, the line lists every value, comma-joined in order of first appearance.
   - `evidence_gate.py` accepts the new line and requires its position. A USAGE cell without it remains valid for receipts written before this ticket, and is reported as `effort=UNRECORDED`.
3. **The usage report goes red on a mismatch.** `usage_report.py` compares each USAGE cell's model and effort with its profile entry:
   - a different or extra model gives `MODEL_MISMATCH`;
   - a different or extra effort gives `EFFORT_MISMATCH`;
   - both are reds (exit 1), joined by a comma with any `OVER_*` verdict.

   The token comparison is unchanged. An `effort=UNRECORDED` cell is compared on model and tokens only, and prints `EFFORT_UNRECORDED`, which is not red.
4. **The dispatch names them.** Dispatch lint gains R8: a dispatch file with a `profile:` field must also carry `model:` and `effort:` fields. Their absence is red (exit 1). R1 to R7 are unchanged.
5. **The runbook.** The token-use section states:
   - the control plane starts every seat with the model and effort its dispatch names;
   - a seat whose USAGE shows a mismatch is a red the review record explains;
   - the elevation route for a hard ticket stays `implementation-elevated`, with its own model, effort and expectation.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/76-seat-binding`, started with the model and effort its dispatch names.
- reviewer：`ticket-review` seat in `.worktrees/76-seat-binding-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：command-line scripts and a JSON template; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the expectation entry, the USAGE `effort:` line, the two new verdicts and R8 above.

## TDD 設計

1. 正常行為:
   - a USAGE cell matching its profile's model and effort, within its limits, gives `WITHIN`;
   - the receipts of tickets 65 to 72 are run as observation and listed in the capture, as `effort=UNRECORDED` with their model verdicts;
   - ticket 67's implementation receipt shows `MODEL_MISMATCH`.
2. 規則違反／輸入錯誤:
   - another model;
   - two models in one cell;
   - another effort;
   - a mismatch together with `OVER_PROCESSED`;
   - an expectation entry missing `model` or `effort` (schema break, exit 2);
   - a dispatch with `profile:` but no `model:`, or no `effort:` (R8 red).
3. 外部失敗／fail-closed: an unreadable expectation or receipt stays exit 2, with reds printed first, as R4-2 sets.
4. 回歸保護: every existing usage_report, evidence_gate and dispatch-lint test passes, or changes only where the new grammar requires it, with each change named in the STATEMENT.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule |
| 2 | null／空字串／陣列 | 是 | an empty `effort:` value; an empty model list |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | `claude-sonnet-5-5` versus `claude-sonnet-5-5-fast`; `high` versus `High` (case-sensitive, a mismatch); comma-joined lists in either order |
| 5 | 錯誤碼是否一致 | 是 | 1 for a mismatch or R8, 2 for a schema break, 3 for usage |
| 6 | 例外是否會拋出 | 否 | no new I/O |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_gate_usage_report.py tests/test_gate_evidence.py tests/test_gate_dispatch_lint.py tests/test_state_file_templates.py -q` exits 0, apart from base failures, each named.
  - `mypy --strict --python-version 3.11` on the three scripts and their tests exits 0.
- **反向突變證據**, each restored after it turns a named test red:
  - ignore the model;
  - ignore the effort;
  - compare the effort case-insensitively;
  - drop R8.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last), and the typed return in STATEMENT.

## 正式環境移植 SOP

- 不適用：plugin scripts and a template.

## 完成回寫

The control plane writes these rows.

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
