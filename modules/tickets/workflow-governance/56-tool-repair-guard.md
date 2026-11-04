# 56｜Tool-repair guard: a repair touches only the declared tools

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-3、R4-8 tool-repair guard） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision03 / receipt under `.worktrees/56-tool-repair-guard-out/` / owner implementation seat / worktree `.worktrees/56-tool-repair-guard` / branch `cp/wave2-56-tool-repair-guard` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `CONVERGENCE_REPLANNED`（closure revision03 after the revision02 correction review `CONVERGENCE_REVIEW_REQUIRED`: S56-09 to S56-14; implementation 3 dispatched, new review cadence） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/56-tool-repair-guard` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/56-tool-repair-guard-review` |
| 責任邊界 | the repair guard script, its tests and the scripts README |
| 禁止修改 | everything else |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/README.md
create = skills/johnny-project-takeover/scripts/repair_guard.py
create = tests/test_gate_repair_guard.py
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

The owner approved wave 2 and R4-8 on 2026-11-04. R4-3 lets a seat repair a broken tool inside a declared allowlist, in its own commit, without touching assertions, expected values, product code or any gate. A reviewer or a gate runs `repair_guard.py --repo <dir> --repair <commit> --dispatch <dispatch.yaml>` on that commit. Exit 0 with `paths=N defects=0`; exit 1 with one line per defect; exit 2 when git or the file system cannot serve the check; exit 3 on bad arguments or a dispatch without the two blocks below.

### Dispatch blocks (R4-8), same grammar as the preflight block of ticket 55

```
repair_allowlist: ["<repository-relative path or directory/>", ...]
protected_paths: ["<repository-relative path or directory/>", ...]
```

Each is one line at column 0 whose value is one JSON array of strings. An entry ending in `/` covers that directory and everything under it; otherwise it is an exact path. The guard also always protects `skills/johnny-project-takeover/scripts/` (the gate scripts) whether or not `protected_paths` names it.

### Defect codes (exit 1)

| Code | When |
| --- | --- |
| `OUTSIDE_ALLOWLIST` | a path changed by the repair commit (against its first parent; added, modified, deleted or renamed, both sides of a rename) is covered by no `repair_allowlist` entry |
| `PROTECTED_PATH_TOUCHED` | a changed path is covered by a `protected_paths` entry or by the gate-script directory, even if it is also in the allowlist |
| `REPAIR_NOT_SINGLE_PARENT` | the repair commit is a merge or a root commit (a repair is one ordinary commit) |
| `TEXT_VALUE_INVALID` | a string the gate reads (a block entry, or a path git reports) breaks the text-value rule; the subject is printed escaped |

### What counts and how it is compared (revision02)

- Every changed path counts, submodule pointers (gitlinks) included, whatever the repository says about ignoring submodules: the diff runs with `-c diff.ignoreSubmodules=none` and `--ignore-submodules=none`, and with external diff drivers and text conversion off. A tracked `.gitmodules` with `ignore = all` and a repository setting `diff.ignoreSubmodules=all` change nothing.
- Replace refs are ignored (`--no-replace-objects`), and the repository-selecting `GIT_*` variables (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`) are removed from every git child.
- The empty tree for a root commit is asked from git for the repository's object format, never hard-coded.
- Case on Windows, fail-closed in both directions: an allowlist entry covers a path when they are equal ignoring ASCII case only (non-ASCII characters compared exactly, so the allowlist never widens beyond what the file system treats as one name); a protected entry and the gate-script directory cover a path when they are equal under full Unicode case folding (so protection never narrows). Elsewhere comparison is exact.
- The dispatch file is decoded as UTF-8 with surrogate escapes: an undecodable byte or a raw control character on a block line (inside or outside a JSON string) is `TEXT_VALUE_INVALID` (exit 1); the same on a line the gate does not read is ignored. A block line that is not one JSON array of strings for another reason is exit 3.
- Red before fault (the reading of R4-2 in ticket 52 revision04): the gate reports every red it can find and exits 1 if there is one, with a fault printed on stderr; it exits 2 only when it found no red.
- A stdout or stderr that cannot be written ends the run with exit 2.
- Why `protected_paths` is required although R4-8 names only `repair_allowlist`: the spec, ledger and product paths of a target project are not known to the guard, so the dispatch declares them; the guard adds the gate-script directory itself. A correction of R4-8 saying so is proposed to the owner.

### Text values (all wave-2 gates; added after the ticket 52 review)

Every string read from an input is valid Unicode without lone surrogates and without control characters (U+0000–U+001F, U+007F) unless a field explicitly allows them; a string that breaks this is never a tool fault: in a file the gate reads it is a red of the input (exit 1), and in an argument it is a usage error (exit 3). Every subject printed in a defect line is printed in a form that cannot span two lines or forge another line (Python `repr` or an equivalent escape), so one defect is always one line.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/56-tool-repair-guard`.
- reviewer：`ticket-review` seat in `.worktrees/56-tool-repair-guard-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket, the dispatch file, R4-3, R4-8.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a stdlib command-line script; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：`skills/johnny-project-takeover/scripts/repair_guard.py`
- 公開契約／資料模型：typed dataclasses `PathRule`, `Defect`; the blocks parsed with `json.loads` (no YAML dependency); changed paths from `git diff --name-status -M <commit>^ <commit>` with `-c core.quotepath=false` and `-z`; exit codes 0/1/2/3.

## TDD 設計

1. 正常行為：a temporary repository with a repair commit that changes only an allowlisted tool file → exit 0.
2. 規則違反／輸入錯誤：one test per defect code; a rename from an allowlisted path to a protected one reports `PROTECTED_PATH_TOUCHED`; a deletion outside the allowlist reports `OUTSIDE_ALLOWLIST`; a dispatch without either block → 3.
3. 外部失敗／fail-closed：unknown commit → exit 2 with git's stderr; `--repo` not a repository → 2; dispatch unreadable → 2.
4. 回歸保護：a gitlink bump outside the allowlist is red with `.gitmodules` `ignore = all` and with `diff.ignoreSubmodules=all`; a replace ref that hides a protected change does not hide it; `GIT_OBJECT_DIRECTORY` and `GIT_WORK_TREE` set in the environment change nothing; a Windows case variant of the gate-script directory is protected; allowlist `strasse/` does not cover `straße/a.py` and `kit/` does not cover a Kelvin-sign path, while protected `Straße/` covers `strasse/x`; a raw control character inside a JSON string on a block line is exit 1; an undecodable byte on a block line is exit 1 and on another line is ignored; a multi-line git error prints on one line; a root commit in a SHA-256 repository (skipped with a stated reason only if this git cannot create one); a closed stdout is exit 2; a non-ASCII path is matched correctly (no quoted path); directory entries match by path segment (`tools/` does not cover `tools2/x`); a path equal to a directory entry without the slash is not covered by it.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | entries and paths: equal, one extra character (`tools2/`), trailing slash, case variant (Windows: compared case-insensitively and documented), URL-encoded text not decoded, `..` in an entry refused (exit 3), empty entry refused (exit 3) |
| 2 | null／空字串／陣列 | 是 | empty allowlist (every change is outside), empty protected list (gate scripts still protected), `null` values (exit 3) |
| 3 | 權限繞過 | 是 | direct: a change to a gate script inside the allowlist is still red; indirect: a rename that moves a protected file out of its directory is red on its old side |
| 4 | Token 格式與比較 | 否 | no tokens |
| 5 | 錯誤碼是否一致 | 是 | the three codes distinct; a red never exits 2 and a fault never exits 1 |
| 6 | 例外是否會拋出 | 是 | git failing → exit 2 with git's stderr; no traceback |

## 完成定義與證據

- `python -m pytest tests/test_gate_repair_guard.py -q` exit 0; `mypy --strict --python-version 3.11` exit 0; stdlib only; no `Any`.
- **反向突變證據**：for each code remove its check → its test red → restore; plus: built-in gate-script protection removed (red), prefix matched without segment boundary (red), only the new side of a rename checked (red), quoted paths (red).
- Receipt: R4-7 cells; `tool_digest` lists the three wave-1 scripts and `repair_guard.py`; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9).
- full suite: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：plugin-local script.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Re-plan to closure revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record: `doc/reviews/workflow-governance/56-tool-repair-guard-code-review.md`. S56-07 and S56-08 are `TICKET_DEFECT`s; the closure is rebuilt here before correction 1.

| Finding | Class | Disposition in revision02 |
| --- | --- | --- |
| S56-01 | IMPLEMENTATION_DEFECT | submodule pointers always count, as above |
| S56-02 | IMPLEMENTATION_DEFECT | raw control characters on a block line are `TEXT_VALUE_INVALID` |
| S56-03 | IMPLEMENTATION_DEFECT | dispatch decoded with surrogate escapes; bad bytes matter on block lines only |
| S56-04 | IMPLEMENTATION_DEFECT | ASCII case for the allowlist, full folding for protection |
| S56-05 | IMPLEMENTATION_DEFECT | an unwritable stdout or stderr is exit 2 |
| S56-06 | EVIDENCE_DEFECT | tests for replace refs, the scrubbed variables, the gate directory case variant, multi-line git errors and the SHA-256 empty tree |
| S56-07 | TICKET_DEFECT | `TEXT_VALUE_INVALID` named; red before fault; git output read as input |
| S56-08 | TICKET_DEFECT | why `protected_paths` is required stated; an R4-8 correction proposed |

## Re-plan to closure revision03 (after the revision02 correction review `CONVERGENCE_REVIEW_REQUIRED`)

Review record section "Revision02 correction review". CodeReview §5: revision02 used its one initial and one correction review. Root cause of S56-09 and S56-10: the guard asked git for the repair commit's parents and for a commit-to-commit diff, and git answers both through history rewriting (grafts, replace refs, shallow files) that a repository can carry. Revision03 reads the history it needs from raw objects and diffs trees. Revision03 starts a new cadence: one initial review and one correction review.

### Rules added in revision03 (binding)

- History from raw objects: the guard reads the repair commit as a raw object (`git --no-replace-objects cat-file --batch`, the name on standard input), takes its `tree` line and its `parent` lines from that object, reads the first parent the same way for its tree, and diffs the two tree ids (`git diff-tree` or `git diff` on tree ids, with the submodule, external-diff and text-conversion rules of revision02). Grafts (`info/grafts`, `GIT_GRAFT_FILE`), replace refs and shallow files therefore cannot change the parents or the trees compared. A merge is recognised from its parent lines; a root commit is diffed against the empty tree of the repository's object format. A first parent whose object the store cannot serve is a fault.
- Environment: in addition to the revision02 list, `GIT_COMMON_DIR`, `GIT_GRAFT_FILE`, `GIT_SHALLOW_FILE`, `GIT_REPLACE_REF_BASE` and the `GIT_CONFIG_*` variables are removed from every git child, and `GIT_NO_REPLACE_OBJECTS=1` and `GIT_NO_LAZY_FETCH=1` are set.
- Streams: an output stream that cannot be written decides the exit only when the reds could not be delivered. If every red line was written to stdout and only stderr fails, the exit is 1 (red before fault); if stdout fails, the exit is 2.
- Text-defective dispatch: entries of a block that holds a text defect are not used, but every rule that needs no entry still applies, so a change under the gate-script directory is reported as `PROTECTED_PATH_TOUCHED` next to `TEXT_VALUE_INVALID`.
- Evidence: a mutation that survives as equivalent stays in the M1 capture, marked equivalent with the reason; a capture is never edited after the run. The per-code mutations of the completion definition are run at every candidate.

| Finding | Class | Disposition in revision03 |
| --- | --- | --- |
| S56-09 | IMPLEMENTATION_DEFECT | history from raw objects; tests with a graft file in the repository, in the common directory of a linked worktree and through `GIT_GRAFT_FILE`, for a single-parent, a merge and a root commit |
| S56-10 | EVIDENCE_DEFECT | a test whose replacement commit has a parent with the repair's tree |
| S56-11 | EVIDENCE_DEFECT | tests for `GIT_COMMON_DIR`, a bare repository verdict, a block line ending in two carriage returns, and an upper-case `Z` in an allowlist entry |
| S56-12 | TICKET_DEFECT | the stream rule above |
| S56-13 | TICKET_DEFECT | the text-defective dispatch rule above |
| S56-14 | EVIDENCE_DEFECT | the evidence rule above |
