# 70｜Wave-2 follow-ups: ticket and receipt templates, and a cap on tracked path length

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-1, R4-7; `doc/reviews/workflow-governance/wave2-completion-2026-11-12.md`, "Follow-up work found in wave 2"） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/70-templates-out/` / owner implementation seat / worktree `.worktrees/70-templates` / branch `cp/wave3-70-templates` / baseline the wave-3 branch after ticket 69 is integrated |
| 實作語言 | Markdown templates; Python 3.11 for the tests（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED`（starts after ticket 69 is `INTEGRATED`: both change the receipt template and its test） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/70-templates` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/70-templates-review` |
| 責任邊界 | the target ticket template, the receipt template, the template README, their test, and one new repository-hygiene test |
| 禁止修改 | the gate scripts, `library/`, `Workflow.md`, `AGENTS.md`, `CodeReview.md`, the references (ticket 67) |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = template/modules/tickets/TEMPLATE.md
modify = template/doc/handoffs/governance/RECEIPT.TEMPLATE.md
modify = template/README.md
modify = tests/test_state_file_templates.py
create = tests/test_tracked_path_length.py
forbid = library/
forbid = skills/
forbid = Workflow.md
forbid = AGENTS.md
forbid = CodeReview.md
forbid = modules/spec/
forbid = .claude-plugin/
```

## 使用者拍板與可觀察結果

The wave-2 completion record lists follow-ups that the two runs of ticket 61 part B found in the templates, and one repository-hygiene item. The owner put the wave-2 follow-ups in wave 3 (REQ-20261103-043, 2026-11-12). The rule items are not in this ticket: the receipt that names its own commit, the CodeReview §5 sentence (S61-07) and the resume conventions (S61-03) are governance text, so ticket 67 sweeps them.

After this ticket:

- **The ticket template** (`template/modules/tickets/TEMPLATE.md`) has a row for each field that `review-checks.md` "Ticket dispatch schema review" and `specification-ticketing.md` require but the template lacked:
  - `Closure revision`: the revision of the finite Acceptance Closure Set;
  - `Strict checker`: the command and version;
  - `Profile / resource`: the semantic profile reference and the resource-plan reference;
  - `XSS classification`: the classification and the exact matrix reference, or the reason it does not apply.

  Each row carries a placeholder in the template's existing style. Allocation and correlation are cross-lifetime receipt fields, and the bridge is retired by ticket 66, so they are not added here. Ticket 67 decides their wording in `review-checks.md`.
- **The state row** of the template:
  - adds `INTEGRATED` to the state list;
  - says that `INTEGRATED` is set when the integration script has landed the candidate and its readback matches;
  - says that `DONE` is set for a ticket that closes without an integration candidate;
  - lets the receipt part hold one receipt per closure revision, in revision order, each as `receipt \`<path>\``.
- **The defect-class heading** of the template cites `CodeReview.md` §2 and the "Defect categories" table of `review-checks.md`, not the `CodeReview.md` §2.1 that no longer exists.
- **The receipt template** (`RECEIPT.TEMPLATE.md`) gains a typed-return cell, `## RETURN`, which is informational like `STATEMENT`. It holds these lines:
  - `cell: RETURN`;
  - `return:` with one of `COMPLETED`, `BLOCKED` or `CHANGE_DETECTED`;
  - `items:` and a list of items, which is empty for `COMPLETED`.

  The template, filled with a real capture, still passes `evidence_gate.py`. If the gate refuses the new cell, that is a `CHANGE_DETECTED` return, not a gate change.
- **The template README** describes the new rows and the `RETURN` cell.
- **`tests/test_state_file_templates.py`**:
  - pins each new row, the state list with `INTEGRATED`, the multi-receipt state row and the `RETURN` cell;
  - asserts that the template no longer cites `§2.1`.
- **`tests/test_tracked_path_length.py`**:
  - fails when any tracked path (from `git ls-files -z`) is longer than 120 characters. That is the longest path tracked today, so the cap admits the current tree and refuses a longer one;
  - names each offending path on one escaped line;
  - skips, with a stated reason, when the checkout is not a Git work tree.

  The `files/` flattening of ticket 61 was the fix for a path of 153 characters. This test catches the next one before Windows CI does.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/70-templates`.
- reviewer：`ticket-review` seat in `.worktrees/70-templates-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; the wave-2 completion record; ticket 57 (state-file templates); ticket 69 (the `USAGE` cell).
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：templates and tests; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the template rows and the `RETURN` cell above.

## TDD 設計

1. 正常行為:
   - Every new pin passes.
   - The receipt template, filled with a real capture, a `USAGE` cell and a `RETURN` cell, passes `evidence_gate.py`.
   - The path test passes on the current tree.
2. 規則違反／輸入錯誤:
   - a template copy without one of the new rows fails its pin;
   - a template copy with `§2.1` fails;
   - a fixture tree with a 121-character tracked path fails the path test, which names that path;
   - a 120-character path passes.
3. 外部失敗／fail-closed: `git ls-files` failing inside a Git work tree is a test failure, not a skip.
4. 回歸保護: every existing template pin passes unchanged, apart from the state-list and heading pins, each named in the STATEMENT.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule |
| 2 | null／空字串／陣列 | 是 | an empty `items:` list under `COMPLETED` |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | the path length is counted in characters of the decoded path, not bytes, with non-ASCII paths in the fixture |
| 5 | 錯誤碼是否一致 | 否 | no exit codes |
| 6 | 例外是否會拋出 | 是 | an undecodable path from `git ls-files -z` is reported, not raised |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_state_file_templates.py tests/test_tracked_path_length.py tests/test_gate_evidence.py -q` exits 0.
  - `mypy --strict --python-version 3.11` on both test files exits 0.
- **反向突變證據**, each restored after it turns a named test red:
  - remove the `INTEGRATED` state;
  - restore the `§2.1` citation;
  - raise the cap to 160;
  - count bytes instead of characters.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last).

## 正式環境移植 SOP

- 不適用：templates ship with the plugin at publication 0.5.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
