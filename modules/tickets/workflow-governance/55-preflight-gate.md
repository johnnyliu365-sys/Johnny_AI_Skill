# 55｜Preflight gate: every named tool starts and serves before any product edit

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2 preflight row、R4-3、R4-8 preflight） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/55-preflight-gate-out/` / owner implementation seat / worktree `.worktrees/55-preflight-gate` / branch `cp/wave2-55-preflight-gate` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED` |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/55-preflight-gate` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/55-preflight-gate-review` |
| 責任邊界 | the preflight gate script, its tests and the scripts README |
| 禁止修改 | everything else |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/README.md
create = skills/johnny-project-takeover/scripts/preflight.py
create = tests/test_gate_preflight.py
forbid = skills/johnny-project-takeover/scripts/dispatch_lint.py
forbid = skills/johnny-project-takeover/scripts/receipt_fence_check.py
forbid = skills/johnny-project-takeover/scripts/index_pins.py
forbid = library/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = .github/
forbid = template/
```

## 使用者拍板與可觀察結果

The owner approved wave 2 and R4-8 on 2026-11-04. A seat runs `preflight.py <dispatch.yaml> [--timeout <seconds>]` before its first product edit. Exit 0 with `tools=N served=N` when every declared tool starts and its probe shows the expected text; exit 2 with one line `TOOL_UNSERVED <tool>: <cause>` per failing tool (a tool fault, R4-2: preflight is 0/2/3, it has no red); exit 3 when the dispatch has no `preflight:` block, the block does not follow the grammar below, or the arguments are bad.

### Dispatch block grammar (R4-8)

```
preflight:
  - tool: "<name>"
    start: ["<argv0>", "<arg>", ...]
    probe: ["<argv0>", "<arg>", ...]
    expect: "<substring>"
```

`preflight:` starts at column 0; each item starts with `  - tool:` and its other keys are indented four spaces; every value is one JSON value on the same line (a JSON string for `tool` and `expect`, a JSON array of strings for `start` and `probe`). The block ends at the next line that starts at column 0. `start` runs to completion first (wave 2 supports tools that start and exit, such as a version check or an environment build; long-running servers are out of scope); `probe` runs after it; both run without a shell, with the dispatch file's directory as working directory, each bounded by `--timeout` (default 120 seconds).

### Causes reported with `TOOL_UNSERVED` (exit 2)

`start` cannot be launched (not found, not executable); `start` exits non-zero; `start` or `probe` exceeds the timeout (the process is killed); `probe` exits non-zero; `probe` output (stdout and stderr, decoded with replacement) does not contain `expect`. Every tool is tried; all failures are reported, not only the first.

### Text values (all wave-2 gates; added after the ticket 52 review)

Every string read from an input is valid Unicode without lone surrogates and without control characters (U+0000–U+001F, U+007F) unless a field explicitly allows them; a string that breaks this is a red of the input (exit 1), never a tool fault. Every subject printed in a defect line is printed in a form that cannot span two lines or forge another line (Python `repr` or an equivalent escape), so one defect is always one line.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/55-preflight-gate`.
- reviewer：`ticket-review` seat in `.worktrees/55-preflight-gate-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket, the dispatch file, R4-2, R4-3, R4-8.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a stdlib command-line script; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：`skills/johnny-project-takeover/scripts/preflight.py`
- 公開契約／資料模型：typed dataclass `PreflightItem`; the grammar above parsed with `json.loads` per value (no YAML dependency); exit codes 0/2/3.

## TDD 設計

1. 正常行為：two items whose `start` and `probe` are the venv python printing a known string → exit 0.
2. 規則違反／輸入錯誤：no block, an item missing a key, a value that is not JSON, `start` not an array of strings, an empty array, a key at the wrong indent, an unknown key → each exit 3 naming the line.
3. 外部失敗／fail-closed：each cause above in its own test, including a timeout test with a short `--timeout` (the child is killed and no process is left running); two failing tools → two lines.
4. 回歸保護：the gate never runs a command through a shell (an argument containing `&&` or `|` is passed literally); output with invalid UTF-8 is matched after replacement decoding; CRLF dispatch files parse the same.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | the gate resolves no repository paths; commands are run as given |
| 2 | null／空字串／陣列 | 是 | empty `expect` (refused, exit 3: an empty expectation proves nothing), empty `tool` name, empty argv, `null` values |
| 3 | 權限繞過 | 是 | no shell: shell metacharacters in arguments are not interpreted (direct); a probe that tries to read stdin gets EOF (indirect) |
| 4 | Token 格式與比較 | 否 | no tokens; `expect` is a plain substring compared exactly (case-sensitive) |
| 5 | 錯誤碼是否一致 | 是 | one code, `TOOL_UNSERVED`, with distinct cause texts; never exit 1 |
| 6 | 例外是否會拋出 | 是 | every launch and timeout failure caught → exit 2 with the cause; dispatch unreadable → exit 2; no traceback |

## 完成定義與證據

- `python -m pytest tests/test_gate_preflight.py -q` exit 0; `mypy --strict --python-version 3.11` exit 0; stdlib only; no `Any`.
- **反向突變證據**：for each cause remove its check → its test red → restore; plus: commands run through a shell (red), only the first failure reported (red), empty `expect` accepted (red), timeout not enforced (red).
- Receipt: R4-7 cells; `tool_digest` lists the three wave-1 scripts and `preflight.py`; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9).
- full suite: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：plugin-local script.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
