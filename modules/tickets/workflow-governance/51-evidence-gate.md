# 51｜Evidence gate: a receipt proves every cell or the run is red

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2 evidence gate row、R4-7 receipt cell） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用（Revision 04 does not seal a new Context） |
| Agent Context binding | ticket revision01 / receipt under `doc/reviews/workflow-governance/evidence/51/` / owner implementation seat / worktree `.worktrees/51-evidence-gate` / branch `cp/wave2-51-evidence-gate` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED` |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/51-evidence-gate` |
| 審閱者 | `ticket-review` seat, its own worktree `.worktrees/51-evidence-gate-review` |
| 責任邊界 | the evidence gate script, its tests and the scripts README |
| 禁止修改 | everything else; in particular the three wave-1 scripts and the ticket 48 receipt checker |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/README.md
create = skills/johnny-project-takeover/scripts/evidence_gate.py
create = tests/test_gate_evidence.py
forbid = skills/johnny-project-takeover/scripts/dispatch_lint.py
forbid = skills/johnny-project-takeover/scripts/receipt_fence_check.py
forbid = skills/johnny-project-takeover/scripts/index_pins.py
forbid = doc/reviews/workflow-governance/evidence/48/
forbid = library/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = .github/
forbid = template/
```

## 使用者拍板與可觀察結果

The owner approved wave 2 on 2026-11-04 ("先做wave2"). A plugin user runs
`python skills/johnny-project-takeover/scripts/evidence_gate.py <receipt.md> --repo <dir> --candidate <sha> --tool <path> [--tool <path> ...] [--require-cell <name> ...] [--evidence-root <dir>]`.
Exit 0 with `cells=N defects=0` when every run cell proves itself; exit 1 with one line per defect code otherwise; exit 2 when git or the file system cannot serve the check; exit 3 on bad arguments. The receipt checker committed for ticket 48 (`evidence/48/receipt_check.py`) stays as the record of that ticket; this gate is the plugin's general instrument and closes the gaps the ticket 48 review found in it (NF-16) and F-06.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane；writes this ticket and the dispatch, does not implement it.
- implementation owner：`implementation-standard` seat in `.worktrees/51-evidence-gate`; TDD, source, tests, one commit per correction.
- reviewer：`ticket-review` seat in `.worktrees/51-evidence-gate-review`; does not share the implementer's worktree.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket, the dispatch file named in the dispatch, R4-2, R4-7, the ticket 48 review record section "Revision05 initial review" (NF-16) and F-06.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a stdlib command-line script; no UI boundary.

- element 路徑：不適用（plugin-local script）
- 實際原始碼路徑：`skills/johnny-project-takeover/scripts/evidence_gate.py`
- 公開契約／資料模型：the receipt format below; typed dataclasses for `Cell`, `Defect`; exit codes 0/1/2/3.

### Receipt format the gate reads (R4-7 receipt cell)

A run cell is a `## <name>` section with the lines `cell: <name>`, `candidate: <full sha>`, `tool_digest:` followed by `- <repository-relative path>=<sha256 hex>` lines, `capture: <path relative to the evidence root>`, `exit: <comma-separated exit codes in capture order>`, then the capture in one four-backtick fence. A statement section is `## <name>` with `cell: STATEMENT` and no `capture:`, `exit:` or fence.

### Defect codes (exit 1)

| Code | When |
| --- | --- |
| `NO_CELLS` | the receipt holds no run cell (a run that checked nothing; F-06) |
| `NOT_RUN` | a `## ` section has no `cell:` line, or a `--require-cell` name has no run cell |
| `CELL_FIELD_MISSING` | a run cell lacks `candidate`, `tool_digest:` (the label itself), `capture` or `exit` |
| `STATEMENT_HAS_RUN_FIELDS` | a `cell: STATEMENT` section carries `capture:`, `exit:` or a fence, or uses a name passed in `--require-cell` |
| `DUPLICATE_CELL` | two run cells share a name |
| `CANDIDATE_MISMATCH` | a cell's `candidate` differs from `--candidate` |
| `TOOL_DIGEST_MISSING` | a `--tool` path has no `tool_digest` line in a cell |
| `TOOL_DIGEST_STALE` | a listed digest differs from sha256 of `git show <candidate>:<path>` |
| `CAPTURE_MISSING` | the capture file does not exist under the evidence root |
| `CAPTURE_CR` | the capture holds a CR byte |
| `BLOCK_MISMATCH` | the fenced block differs from the capture byte for byte (block = the lines between the fences joined with LF plus a final LF) |
| `EXIT_MISMATCH` | the `exit:` list differs from the `exit=N` lines of the capture, in order |

A capture path that escapes the evidence root (absolute path, `..` segments after normalisation, a drive letter) is `CAPTURE_MISSING`, never read.

## TDD 設計

1. 正常行為：a receipt with two run cells and one statement section, every field correct → exit 0, `cells=2 defects=0`.
2. 規則違反／輸入錯誤：one test per defect code above, each built from the good receipt by one change; a cell carrying two defects reports both.
3. 外部失敗／fail-closed：`git show` failing for a listed tool (unknown candidate in the repository) → exit 2 with git's stderr; the receipt path is a directory or unreadable → exit 2; `--repo` not a repository → exit 2; no `--tool` or no `--candidate` → exit 3.
4. 回歸保護：the seven NF-16 escape shapes from the ticket 48 review (section without `cell:`, statement opt-out, missing `tool_digest:` label, missing capture reported as fault, mixed candidates, exit list contradicting the capture) each give exit 1 with the code above; a receipt written with CRLF line endings is read (the receipt's own line endings are normalised; captures are not).

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | capture paths: equal to the root, one extra character, trailing slash, case variant on Windows, `..` traversal, absolute path, empty path |
| 2 | null／空字串／陣列 | 是 | empty receipt, empty `exit:` value, empty `tool_digest:` list, blank `--tool`, a capture of zero bytes with an empty block |
| 3 | 權限繞過 | 否 | no access control; the gate reads files and git objects only |
| 4 | Token 格式與比較 | 是 | sha256 hex: 63 and 65 characters, upper-case hex, non-hex; candidate: short sha refused (`CELL_FIELD_MISSING`), full sha compared exactly |
| 5 | 錯誤碼是否一致 | 是 | every defect code above distinct and printed as `<code> <section>: <detail>`; a red never exits 2 and a fault never exits 1 |
| 6 | 例外是否會拋出 | 是 | git unavailable, receipt unreadable, capture unreadable after existing (permission) → exit 2 with the cause, no traceback |

## 完成定義與證據

- `python -m pytest tests/test_gate_evidence.py -q` exit 0; `mypy --strict --python-version 3.11` on the script exit 0; stdlib only; no `Any`.
- The gate run on its own receipt (the seat's `RETURN.md`) with `--tool skills/johnny-project-takeover/scripts/evidence_gate.py` exits 0; that run is recorded as cell `E1`, its capture produced by writing the gate's output and re-running to confirm byte identity (the self-reference note of ticket 48).
- The gate run on the ticket 48 c10 receipt (`--evidence-root` its directory, the three wave-1 scripts as `--tool`, the c10 sha as candidate, the c10 clone as `--repo`): the exit and every code printed are recorded as cell `E2`; the result is an observation, not an assertion (that receipt was written under the ticket 48 format).
- **反向突變證據**：for each defect code, remove its check → the test of that code turns red → restore. Plus: block comparison after CRLF normalisation (must be red); exit list compared as a set instead of in order (red); capture path not confined to the root (red).
- full suite: failure set a subset of the base names of the environment; zero new red.

## 正式環境移植 SOP

- 不適用：a plugin-local script; no migration, no environment variable.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用（WPR-only handoff retired; the receipt and the review record hold the evidence）
