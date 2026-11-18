# 72｜Dispatch lint: R5 judges one verifiable action per line, not a character cap

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2; REQ-20261103-043, owner decision 2026-11-18 "B", lesson L-10） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/72-lint-out/` / owner implementation seat / worktree `.worktrees/72-lint` / branch `cp/wave3-72-lint` / baseline the wave-3 branch after ticket 69 is integrated |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `INTEGRATED`（candidate `8c770265` at `fa4019fa`; CI run 44381596401 green; S72-05, S72-06 carried） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/72-lint` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/72-lint-review` |
| 責任邊界 | `dispatch_lint.py`, its README section, its tests |
| 禁止修改 | every other gate script, `library/`, the governance documents |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/dispatch_lint.py
modify = skills/johnny-project-takeover/scripts/README.md
modify = tests/test_gate_dispatch_lint.py
modify = tests/test_wave2_end_to_end.py
forbid = library/
forbid = Workflow.md
forbid = AGENTS.md
forbid = CodeReview.md
forbid = template/
```

## 使用者拍板與可觀察結果

**The problem.** Today R5 refuses any line longer than 400 characters. The limit is meant to stop one line from carrying too many instructions. In wave 3 every R5 failure (JAS-65 three times, JAS-69 once) was fixed by splitting a sentence over two lines, with no change in content. The rule measures length, while the intent is one instruction per line. The owner decided on 2026-11-18 ("B") that R5 judges one verifiable action per line.

After this ticket:

- **R5 — one action per line.** A line outside a code fence holds at most one action. A line holds more than one action when it contains a clause separator, which is a half-width `;` followed by a space, or a full-width `；`. These do not count as separators:
  - a separator inside a backtick span;
  - a separator in the value of a `cmd:` field, because a command line is one action however many shell statements it holds.

  A separator inside double or single quotes counts, because dispatch values are written in quotes and the rule exists for exactly those. The problem line reads `R5 line <n> holds <k> actions; put each on its own list item`.
- **R6 — runaway line.** No line, outside a code fence or inside one, is longer than 2000 characters. This is a safety cap against a pasted blob, not the instruction rule.
- R1 to R4 and the exit codes (0, 1, 3) are unchanged. The README section and the module docstring describe R5 and R6.
- **Changed tests:**
  - The two existing R5 tests become R6 tests at the new limit.
  - New R5 tests cover:
    - exactly one action;
    - two actions;
    - a full-width separator;
    - a separator in backticks;
    - a separator in a `cmd:` value;
    - a separator in quotes;
    - a `;` with no following space, which is not a separator, for example `a;b`.
  - Each changed assertion is named in the STATEMENT.
- **`tests/test_wave2_end_to_end.py`** changes only if its fixture dispatch breaks the new R5. If so, the fixture is split into list items, and the STATEMENT names the change.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/72-lint`.
- reviewer：`ticket-review` seat in `.worktrees/72-lint-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; `dispatch_lint.py` and its tests.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a command-line script; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the rule list above.

## TDD 設計

1. 正常行為:
   - a dispatch with one action per line passes;
   - the dispatches of tickets 65 and 69 under `C:/Temp/claude/jas-dispatch/` are run as observation, and every line the new R5 reports is listed in the capture.
2. 規則違反／輸入錯誤: one test per case of the R5 list above, and the R6 boundary (2000 passes, 2001 fails).
3. 外部失敗／fail-closed: an unreadable or non-UTF-8 file stays exit 3.
4. 回歸保護: every R1 to R4 test passes unchanged.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule |
| 2 | null／空字串／陣列 | 是 | an empty line and a line of spaces are not actions |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | `;` followed by a space versus `;` without one; the full-width form; an unbalanced backtick does not hide the rest of the line |
| 5 | 錯誤碼是否一致 | 是 | 1 for R5 and R6, 3 for usage, as before |
| 6 | 例外是否會拋出 | 否 | no new I/O |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_gate_dispatch_lint.py tests/test_wave2_end_to_end.py -q` exits 0.
  - `mypy --strict --python-version 3.11` on the script and its test exits 0.
- **反向突變證據**, each restored after it turns a named test red:
  - count separators inside backticks;
  - exempt quotes;
  - drop the `cmd:` exemption;
  - accept 2001 characters.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last).

## 正式環境移植 SOP

- 不適用：a plugin script.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
