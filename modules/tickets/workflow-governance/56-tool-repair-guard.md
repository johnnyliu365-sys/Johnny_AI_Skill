# 56｜Tool-repair guard: a repair touches only the declared tools

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-3、R4-8 tool-repair guard） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/56-tool-repair-guard-out/` / owner implementation seat / worktree `.worktrees/56-tool-repair-guard` / branch `cp/wave2-56-tool-repair-guard` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED` |
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
4. 回歸保護：a non-ASCII path is matched correctly (no quoted path); directory entries match by path segment (`tools/` does not cover `tools2/x`); a path equal to a directory entry without the slash is not covered by it.

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
