# 51｜Evidence gate: a receipt proves every cell or the run is red

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2 evidence gate row、R4-7 receipt cell） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用（Revision 04 does not seal a new Context） |
| Agent Context binding | ticket revision02 / receipt under `doc/reviews/workflow-governance/evidence/51/` / owner implementation seat / worktree `.worktrees/51-evidence-gate` / branch `cp/wave2-51-evidence-gate` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `CONVERGENCE_REPLANNED`（closure revision02 after the revision01 initial review: S51-02, S51-07 TICKET_DEFECT; correction 1 dispatched to the same seat） |
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
| `EXIT_MISMATCH` | the `exit:` list differs from the capture's lines that consist of `exit=N` alone (a line holding `exit=N` inside longer text does not count), in order |
| `FIELD_REPEATED` | a run cell holds a second `cell:`, `candidate:`, `tool_digest:`, `capture:` or `exit:` line, or a second fence |
| `CELL_NAME_MISMATCH` | a run cell's `cell:` value differs from its `## ` heading name |

A capture path that escapes the evidence root (absolute path, `..` segments after normalisation, a drive letter, a link or junction resolving outside it) is `CAPTURE_MISSING`, never read. A `tool_digest` path is checked for form before git is asked: a path that is absolute, has a drive letter, has a `..` segment, starts with `:` (pathspec magic) or is empty is `TOOL_DIGEST_STALE` (a receipt red), never a tool fault; a well-formed path is read from the repository root (`git show <candidate>:<path>`), so `--repo` may name any directory inside the repository.

Relation to R4-7: a cell missing one of the five R4-7 fields is what R4-7 calls `NOT_RUN`; the gate reports it with the more specific code `CELL_FIELD_MISSING` and keeps `NOT_RUN` for a section without `cell:` and an absent required cell. R4-7's "repository-relative" capture path is the case where `--evidence-root` is the repository root; the gate accepts any evidence root so a seat can keep captures outside the tree until they are committed.

### Text values (all wave-2 gates; added after the ticket 52 review)

Every string read from an input is valid Unicode without lone surrogates and without control characters (U+0000–U+001F, U+007F) unless a field explicitly allows them; a string that breaks this is a red of the input (exit 1), never a tool fault. Every subject printed in a defect line is printed in a form that cannot span two lines or forge another line (Python `repr` or an equivalent escape), so one defect is always one line.


## TDD 設計

1. 正常行為：a receipt with two run cells and one statement section, every field correct → exit 0, `cells=2 defects=0`.
2. 規則違反／輸入錯誤：one test per defect code above, each built from the good receipt by one change; a cell carrying two defects reports both.
3. 外部失敗／fail-closed：`git show` failing for a listed tool (unknown candidate in the repository) → exit 2 with git's stderr; the receipt path is a directory or unreadable → exit 2; `--repo` not a repository → exit 2; no `--tool` or no `--candidate` → exit 3.
4. 回歸保護：the six NF-16 escape shapes from the ticket 48 review (section without `cell:`, statement opt-out, missing `tool_digest:` label, missing capture reported as fault, mixed candidates, exit list contradicting the capture) each give exit 1 with the code above; a receipt written with CRLF line endings is read (the receipt's own line endings are normalised; captures are not); a receipt with a UTF-8 BOM is read; an outward directory junction under the evidence root is `CAPTURE_MISSING` (a test that needs no symlink privilege); `--repo` a subdirectory of the repository gives the same result as the root.

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

## Re-plan to closure revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record: `doc/reviews/workflow-governance/51-evidence-gate-code-review.md`. S51-02 and S51-07 are `TICKET_DEFECT`s; the closure is rebuilt here before correction 1.

| Finding | Class | Disposition in revision02 |
| --- | --- | --- |
| S51-01 | IMPLEMENTATION_DEFECT | digest-path form check first (`TOOL_DIGEST_STALE`); root-relative `git show`; one test per side |
| S51-02 | TICKET_DEFECT | `FIELD_REPEATED` |
| S51-03 | OUT_OF_SCOPE_HARDENING (taken now) | `CELL_NAME_MISMATCH` |
| S51-04 | OUT_OF_SCOPE_HARDENING (taken now) | paths read from the repository root; subdirectory `--repo` test |
| S51-05 | EVIDENCE_DEFECT | `EXIT_MISMATCH` counts whole `exit=N` lines only, with a test |
| S51-06 | OUT_OF_SCOPE_HARDENING (taken now) | junction test; BOM test |
| S51-07 | TICKET_DEFECT | six shapes; the relation to R4-7 stated |
| S51-08 | OUT_OF_SCOPE_HARDENING | not taken: only the script is required to pass `mypy --strict` |
| S51-09 | accepted decisions | none |
| text values | added for every wave-2 gate | the text-value rule above |
