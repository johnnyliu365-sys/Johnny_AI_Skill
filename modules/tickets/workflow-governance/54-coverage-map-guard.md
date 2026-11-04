# 54｜Coverage-map guard: no assertion disappears silently

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2 coverage-map row、R4-8 coverage map） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/54-coverage-map-guard-out/` / owner implementation seat / worktree `.worktrees/54-coverage-map-guard` / branch `cp/wave2-54-coverage-map-guard` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED` |
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

### Map file (R4-8)

`{"rows": [{"assertion": <id>, "disposition": "carried" | "dropped" | "escalated", "carried_to": <id or "">, "reason": <text or "">, "ticket": <text or "">}]}`, UTF-8 JSON, read with `git show <candidate>:<map>`.

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
4. 回歸保護：tests inside a nested class; async test functions; a file deleted entirely (every test in it removed); a spec added at the candidate (nothing removed); CRLF files.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | `--specs` prefix: a file in `specs2/` when `--specs specs` (not matched), trailing slash, backslash form, `..`, absolute path refused (exit 3) |
| 2 | null／空字串／陣列 | 是 | empty `rows`, missing `rows`, empty strings and whitespace in each field, empty `--specs` directory |
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
