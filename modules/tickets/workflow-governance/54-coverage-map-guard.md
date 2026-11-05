# 54｜Coverage-map guard: no assertion disappears silently

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2 coverage-map row、R4-8 coverage map） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision03 / receipt under `.worktrees/54-coverage-map-guard-out/` / owner implementation seat / worktree `.worktrees/54-coverage-map-guard` / branch `cp/wave2-54-coverage-map-guard` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `REVIEW_APPROVED`（candidate `763284bf`; correction review CONVERGENCE_REVIEW_REQUIRED, approved under CodeReview §5 rule B and the R4-4 trust boundary on 2026-11-05 with findings carried; awaiting integration） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/54-coverage-map-guard` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/54-coverage-map-guard-review` |
| 責任邊界 | the coverage-map guard script, its tests and the scripts README |
| 禁止修改 | everything else |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/README.md
create = skills/johnny-project-takeover/scripts/coverage_map.py
create = tests/test_gate_coverage_map.py
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

The owner approved wave 2 and R4-8 on 2026-11-04. A plugin user runs
`coverage_map.py --repo <dir> --base <commit> --candidate <commit> --map <repository-relative path> --specs <repository-relative directory>`.
The guard lists every test function present in a spec file under `--specs` at `--base` and absent at `--candidate` (a spec file is `test_*.py`; a test is a module-level or class-level function whose name starts with `test`; its id is `<path>::<name>` or `<path>::<Class>::<name>`; a test moved to another file or renamed counts as removed under its old id). Each removed id must have a row in the map file read at `--candidate`. Exit 0 with `removed=N defects=0`; exit 1 with one line per defect; exit 2 when git cannot serve a commit or a file; exit 3 on bad arguments.

### Inputs (revision02)

- `--repo` must be the top level of a git work tree: `git rev-parse --show-toplevel` run there, resolved, equals `--repo` resolved. A directory that is not a work tree, or a subdirectory of one, is exit 2.
- `--specs` must name a directory (a tree object) at `--base`, at `--candidate`, or at both. A path that names no tree at either commit (a typo, a file, a case variant on a case-sensitive store) is exit 2 naming the path and both commits: a guard that checks nothing must not pass. A tree present at one commit only is read as empty at the other.
- Spec files are regular blobs (mode `100644` or `100755`) named `test_*.py` under `--specs`. A symbolic link (`120000`) or a submodule entry (`160000`) is not a spec file and is never parsed; a spec file that becomes a link at the candidate has all its tests removed.
- Paths from git are decoded as UTF-8 with `surrogateescape`, so a path that is not UTF-8 is still a test id: compared byte-exactly, printed escaped, never a tool fault. A map row cannot name such an id (map text follows the text-value rule), so its removal is `UNMAPPED_REMOVAL`.
- Tests are found at module level and in class bodies, at any depth of nested classes, and inside `if`, `else`, `try`, `except`, `finally`, `with`, `for`, `while` and `match` blocks at those levels (fail-closed: a test hidden in a block is still a test). Functions nested in functions are not tests.
- Specs are parsed with the grammar of the interpreter that runs the guard (Python 3.11); a spec using later syntax does not parse and is exit 2. The README says so.

### Text values (all wave-2 gates)

Every string read from an input is valid Unicode without lone surrogates and without control characters (U+0000–U+001F, U+007F) unless a field explicitly allows them. In map text a string that breaks this is `MAP_ROW_INVALID` (exit 1); in an argument it is exit 3; never a tool fault. Every subject printed on stdout or stderr, a fault message included, is escaped (JSON with ASCII escapes, or Python `repr`) so that one defect or one fault is one line; a raw argument or a parser message that repeats a raw path is never echoed unescaped.

### Map file (R4-8)

`{"rows": [{"assertion": <id>, "disposition": "carried" | "dropped" | "escalated", "carried_to": <id or "">, "reason": <text or "">, "ticket": <text or "">}]}`, UTF-8 JSON, read as the blob at `<candidate>:<map>`. A map path that names a submodule entry or a tree is `MAP_ROW_INVALID` for the file.

### Defect codes (exit 1)

| Code | When |
| --- | --- |
| `UNMAPPED_REMOVAL` | a removed test id has no map row |
| `CARRIED_TARGET_MISSING` | `carried`, but `carried_to` is empty or names no test at `--candidate` |
| `DROPPED_WITHOUT_REASON` | `dropped` with an empty or whitespace-only `reason` |
| `ESCALATED_WITHOUT_TICKET` | `escalated` with an empty or whitespace-only `ticket` |
| `MAP_ROW_INVALID` | a row whose `disposition` is unknown, whose fields are missing or not strings, or a duplicate `assertion` |

A map file absent at `--candidate` while tests were removed is `UNMAPPED_REMOVAL` for each; absent while nothing was removed is exit 0. A map file that is not JSON is `MAP_ROW_INVALID` for the file.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/54-coverage-map-guard`.
- reviewer：`ticket-review` seat in `.worktrees/54-coverage-map-guard-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket, the dispatch file, R4-2, R4-8.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a stdlib command-line script; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：`skills/johnny-project-takeover/scripts/coverage_map.py`
- 公開契約／資料模型：typed dataclasses `TestId`, `MapRow`, `Defect`; the codes above; exit codes 0/1/2/3. Test enumeration uses the standard `ast` module on the blobs from `git show`; a spec that does not parse at either commit is exit 2 naming the commit and path (the guard cannot serve an unparseable side).

## TDD 設計

1. 正常行為：a temporary repository where a commit removes one test and the map carries it to a new test → exit 0; nothing removed and no map → exit 0.
2. 規則違反／輸入錯誤：one test per defect code; two removed tests with one row → one `UNMAPPED_REMOVAL`; a renamed test counts as removed.
3. 外部失敗／fail-closed：unknown `--base` or `--candidate` → exit 2 with git's stderr; `--repo` not a repository → 2; a spec that does not parse → 2.
4. 回歸保護：a plain directory inside a work tree as `--repo` → 2; `--specs` naming nothing at either commit, a file, a case variant → 2; an empty but present `--specs` tree → 0; a symlinked spec unchanged → 0 and a spec replaced by a link → its tests removed; a non-UTF-8 spec path unchanged → 0 and removed → `UNMAPPED_REMOVAL`; a lone surrogate in `--map` or `--specs` → 3; a newline in a spec path or in `--base` prints as one line on stderr; tests inside each block kind listed above are found; a submodule under `--specs` is skipped; a submodule map path is `MAP_ROW_INVALID`; a shape-invalid row prints `UNMAPPED_REMOVAL` for its id; tests inside a nested class; async test functions; a file deleted entirely (every test in it removed); a spec added at the candidate (nothing removed); CRLF files.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | `--specs` prefix: a file in `specs2/` when `--specs specs` (not matched), trailing slash, backslash form, `..`, absolute path refused (exit 3) |
| 2 | null／空字串／陣列 | 是 | empty `rows`, missing `rows`, empty strings and whitespace in each field, an empty but present `--specs` tree (exit 0), a `--specs` absent at both commits (exit 2) |
| 3 | 權限繞過 | 否 | no access control |
| 4 | Token 格式與比較 | 是 | test ids compared exactly; a row id with surrounding whitespace is `MAP_ROW_INVALID`, not trimmed silently |
| 5 | 錯誤碼是否一致 | 是 | the five codes distinct; a red never exits 2 and a fault never exits 1 |
| 6 | 例外是否會拋出 | 是 | git failing for each query → exit 2 with git's stderr; no traceback |

## 完成定義與證據

- `python -m pytest tests/test_gate_coverage_map.py -q` exit 0; `mypy --strict --python-version 3.11` exit 0; stdlib only; no `Any`.
- **反向突變證據**：for each code remove its check → its test red → restore; plus: class-level tests ignored (red), map read from the working tree instead of `--candidate` (red), renamed test treated as kept (red).
- Receipt: R4-7 cells; `tool_digest` lists the three wave-1 scripts and `coverage_map.py`; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9).
- full suite: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：plugin-local script.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Re-plan to closure revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record: `doc/reviews/workflow-governance/54-coverage-map-guard-code-review.md`. S54-02 and S54-06 are `TICKET_DEFECT`s; the closure is rebuilt here before correction 1.

| Finding | Class | Disposition in revision02 |
| --- | --- | --- |
| S54-01 | IMPLEMENTATION_DEFECT | `--repo` must be the work-tree top level, exit 2 otherwise; a test that does not depend on where the system temp directory lies |
| S54-02 | TICKET_DEFECT | `--specs` naming no tree at either commit is exit 2; an empty present tree is exit 0 |
| S54-03 | IMPLEMENTATION_DEFECT | paths decoded with `surrogateescape`; never a fault |
| S54-04 | IMPLEMENTATION_DEFECT | text-value rule: an argument breaking it is exit 3 |
| S54-05 | IMPLEMENTATION_DEFECT | every subject on stderr escaped to one line |
| S54-06 | TICKET_DEFECT | links and submodules are not spec files |
| S54-07 | EVIDENCE_DEFECT | tests for each block kind, the submodule skip, the submodule map path and the `UNMAPPED_REMOVAL` line of a shape-invalid row; README says how the map is read and that `MAP_ROW_INVALID` subjects are `rows[N]` or the map path |
| S54-08 | OUT_OF_SCOPE_HARDENING | not taken: the guard parses with Python 3.11 and says so; a later grammar is a wave-3 candidate |

## Re-plan to closure revision03 (after the revision02 correction review `CONVERGENCE_REVIEW_REQUIRED`)

Review record section "Revision02 correction review". CodeReview §5: revision02 used its one initial and one correction review. Root cause of S54-09: whether a path names a tree was inferred from the file paths under it, so a tree with nothing in it looked absent. Revision03 asks git for tree entries directly. Revision03 starts a new cadence: one initial review and one correction review.

### Rules added in revision03 (binding)

- Trees are listed, not inferred: `ls-tree -r -t` (or an equivalent that reports tree entries) decides whether `--specs` and the map path name a tree. An empty tree object at `--specs` is a present, empty tree (exit 0 when nothing was removed); an empty tree object at the map path is `MAP_ROW_INVALID` for the map path, like any tree.
- Every git child runs with the repository-selecting `GIT_*` variables removed (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`), as in tickets 53 and 56.
- A repeated key in any object of the map file is `MAP_ROW_INVALID` (for the row, or for the file at the top level), as ticket 52 treats repeated keys.
- Red before fault (the reading of R4-2 in ticket 52 revision04): the guard reports every red it can find and exits 1 if there is one, with a fault printed on stderr; it exits 2 only when it found no red.

| Finding | Class | Disposition in revision03 |
| --- | --- | --- |
| S54-09 | IMPLEMENTATION_DEFECT | trees listed directly; tests with an empty tree object at `--specs` and at the map path |
| S54-10 | EVIDENCE_DEFECT | tests for U+001F in a row field, a second `case` and a second `except` handler, and a `test_` function nested in a helper (not a test) |
| S54-11 | OUT_OF_SCOPE_HARDENING (taken now) | `GIT_*` variables removed, with a test that sets `GIT_DIR` |
| S54-12 | OUT_OF_SCOPE_HARDENING (taken now) | repeated keys are `MAP_ROW_INVALID`, with a row test and a top-level test |

### Disposition correction (revision03, during implementation 3)

The ticket 51 revision03 review found that git follows replace refs in `cat-file` and `ls-tree`, so a blob read "at HEAD" or "at a commit" can be another object (S51-16), and that a lookup can fetch over the network in a partial clone. The same applies here. Added to this revision: Every git child runs with `--no-replace-objects` (and `GIT_NO_REPLACE_OBJECTS=1`), with `GIT_NO_LAZY_FETCH=1`, and with the repository-selecting `GIT_*` variables removed (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`, and the `GIT_CONFIG_*` variables); a replace ref never redirects a lookup and a lookup never fetches over the network. One test with `git replace` on a blob this gate reads. Nothing else changes.

### Correction 1 under revision03 (after the revision03 initial review `CHANGES_REQUESTED`)

No ticket defect was found, so revision03 stands; the blocking items are tests. S54-13: one test per red-before-fault edge the review names (the `::` separator in the unknown-path match; a non-tool-fault error in opening a side, in listing tests and in reading the map, each keeping the reds found so far; a spec whose base blob cannot be read never inventing `CARRIED_TARGET_MISSING`). S54-14: a test that sets the whole `GIT_CONFIG_*` family. Taken now, S54-15: every git child also runs with `GIT_GRAFT_FILE` pointing at a path that does not exist, after any inherited value is dropped, so grafts cannot move a relative revision; a test with `info/grafts` and one with an inherited `GIT_GRAFT_FILE`, each with `--base main^`. The next review is the one correction review of revision03.

### Carried after approval (CodeReview §5 rule B)

- S54-16 (EVIDENCE_DEFECT): later gate-hardening ticket.
- S54-17 (forged-store class (commit-graph)): settled by the R4-4 trust boundary (a fetched integration clone carries no seat commit-graph); the one-flag hardening `-c core.commitGraph=false` goes to the next change of this gate.
