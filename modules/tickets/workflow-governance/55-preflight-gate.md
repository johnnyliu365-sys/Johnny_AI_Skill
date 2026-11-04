# 55｜Preflight gate: every named tool starts and serves before any product edit

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2 preflight row、R4-3、R4-8 preflight） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision03 / receipt under `.worktrees/55-preflight-gate-out/` / owner implementation seat / worktree `.worktrees/55-preflight-gate` / branch `cp/wave2-55-preflight-gate` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `CONVERGENCE_REPLANNED`（closure revision03 after the revision02 correction review `CONVERGENCE_REVIEW_REQUIRED`: S55-13 to S55-15; implementation 3 dispatched, new review cadence） |
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

### Launching argv0 (revision02)

The gate resolves `argv0` to an absolute program path itself, the same way on every platform, before it launches anything:

- an `argv0` that names a drive (a letter and a colon at its start, or a `\\?\` or UNC prefix) must be absolute; a drive-relative name such as `Z:prog.exe` or `Z:sub\prog.exe` is refused as `TOOL_UNSERVED` ("cannot be resolved"), and this check runs before every other rule (revision03);
- an absolute `argv0` is used as given;
- a relative `argv0` that contains a path separator (`/` or `\`) is joined to the dispatch file's directory;
- a bare name is looked up in the `PATH` entries only (on Windows with the `PATHEXT` extensions), never in the current directory or the dispatch directory;
- a program whose resolved name ends in `.bat` or `.cmd` (any case) is refused: Windows runs it through `cmd.exe`, which interprets its arguments, so it cannot be run without a shell. Name the interpreter or the executable instead.

A name that cannot be resolved and a refused batch file are `TOOL_UNSERVED` (exit 2) with distinct causes. The gate's own helpers (the process-tree kill on Windows) are launched by absolute system path, never looked up.

### Causes reported with `TOOL_UNSERVED` (exit 2)

`start` cannot be launched (not found, not executable); `start` exits non-zero; `start` or `probe` exceeds the timeout (the process is killed); `probe` exits non-zero; `probe` output (stdout and stderr, decoded with replacement) does not contain `expect`; `argv0` cannot be resolved; `argv0` is a batch file; an unexpected error while serving one tool (the cause names the exception type, and the later tools are still tried). Every tool is tried; all failures are reported, not only the first; the exit is 2 when any tool failed, whichever tool came last. A stdout or stderr that cannot be written ends the run with exit 2, never another code.

### Text values (all wave-2 gates; added after the ticket 52 review)

Every string read from an input is valid Unicode without lone surrogates and without control characters (U+0000–U+001F, U+007F) unless a field explicitly allows them; a string that breaks this is never a tool fault: preflight has no red (R4-2), so in the dispatch file it is exit 3 (the dispatch does not follow the grammar) and in an argument it is exit 3. The dispatch-path argument and `--timeout` are checked before anything is read; `--timeout` must match its whole text, with no trailing newline or surrounding space. Every subject printed in a defect line is printed in a form that cannot span two lines or forge another line (Python `repr` or an equivalent escape), so one defect is always one line.

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
4. 回歸保護：`Z:sub\prog.exe`, `Z:sub/prog.exe` and `C:sub\prog.exe` are refused; a PATHEXT set to a non-default list changes which bare names resolve; quotes and blanks around a PATH entry are removed; an unexpected error outside the tool loop is exit 2 with one stderr line and no traceback; an unexpected error after a child started kills that child before the next tool runs; the dispatch path `CON`, `CONIN$`, `AUX` or `COM1` is exit 3 without opening it; an unserved tool followed by a served one → exit 2; an argument `a&b` and an argument `x|y`, without spaces, echoed back literally; a `.cmd` and a `.BAT` argv0 refused; a relative argv0 with a separator runs the dispatch-directory copy even when the gate runs from another directory; a bare name is not found in the current directory; a path argument with LF, TAB, ESC or a lone surrogate → 3; `--timeout "5
"` → 3; U+001F in a value → 3; a tab-only line inside the block → 3; the default timeout is 120 seconds; a path with a newline in a read diagnostic prints on one line; a closed stdout → 2; an unexpected error in the first tool still tries the second; the gate never runs a command through a shell; output with invalid UTF-8 is matched after replacement decoding; CRLF dispatch files parse the same.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | the gate resolves no repository paths; commands are run as given |
| 2 | null／空字串／陣列 | 是 | empty or whitespace-only `expect` (refused, exit 3: it proves nothing), empty `tool` name, empty argv, `null` values |
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

## Disposition correction (revision01, before the initial review)

The text-value paragraph was copied from the gates that have a red and said "exit 1"; R4-2 gives preflight the exits 0/2/3 only. The implementation seat found the conflict, recorded it in its STATEMENT section and chose exit 3; the control plane adopts that choice as the ticket text above. Nothing else changes, and the candidate is reviewed against this text.

## Re-plan to closure revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record: `doc/reviews/workflow-governance/55-preflight-gate-code-review.md`. S55-03 and S55-04 are `TICKET_DEFECT`s; the closure is rebuilt here before correction 1.

| Finding | Class | Disposition in revision02 |
| --- | --- | --- |
| S55-01 | IMPLEMENTATION_DEFECT | path argument checked against the text-value rule before the read, exit 3 |
| S55-02 | IMPLEMENTATION_DEFECT | `--timeout` matched in full |
| S55-03 | TICKET_DEFECT | batch-file argv0 refused, `TOOL_UNSERVED` |
| S55-04 | TICKET_DEFECT | argv0 resolved by the gate as above, the same on every platform |
| S55-05 | EVIDENCE_DEFECT | exit 2 when any tool failed, with the unserved-then-served test |
| S55-06 | EVIDENCE_DEFECT | metacharacter arguments without spaces |
| S55-07 | EVIDENCE_DEFECT | the four boundaries pinned |
| S55-08 | OUT_OF_SCOPE_HARDENING (taken now) | the tree kill by absolute system path |
| S55-09 | OUT_OF_SCOPE_HARDENING (taken now) | an unexpected error is a per-tool cause |
| S55-10 | OUT_OF_SCOPE_HARDENING (taken now) | an unwritable stdout or stderr is exit 2 |
| S55-11 | OUT_OF_SCOPE_HARDENING | not taken: long-running and detached processes stay out of wave 2; a Windows job object is a wave-3 candidate |
| S55-12 | accepted decisions | except whitespace-only `expect`, now refused (exit 3) |

### Disposition correction (revision02, before the correction review)

TDD 4 asks both that a path argument holding LF is exit 3 and that a path with a newline prints on one line in a read diagnostic; the first rule makes the second unreachable. The read-diagnostic case is pinned instead with characters the argument rule admits (U+2028, NEL, a backslash), as the seat chose and recorded. Nothing else changes.

## Re-plan to closure revision03 (after the revision02 correction review `CONVERGENCE_REVIEW_REQUIRED`)

Review record section "Revision02 correction review". CodeReview §5: the closure revision used its one initial and one correction review. Root cause of S55-13: the argv0 rules were an ordered list without a rule for names that carry a drive, so the separator rule caught a drive-relative name first. Revision03 puts the drive rule first. Revision03 starts a new cadence: one initial review and one correction review.

| Finding | Class | Disposition in revision03 |
| --- | --- | --- |
| S55-13 | IMPLEMENTATION_DEFECT | a name that carries a drive must be absolute; checked first |
| S55-14 | EVIDENCE_DEFECT | a test for the run-level handler next to the per-tool one |
| S55-15 | EVIDENCE_DEFECT | a test with a non-default PATHEXT |
| S55-16 | OUT_OF_SCOPE_HARDENING (taken now) | a test for quotes and blanks around a PATH entry |
| S55-17 | OUT_OF_SCOPE_HARDENING (taken now) | a child whose serving raised is killed before the next tool |
| S55-18 | OUT_OF_SCOPE_HARDENING (taken now) | Windows device names as the dispatch path are exit 3 before any open |
