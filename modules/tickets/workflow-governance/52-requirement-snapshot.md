# 52｜Requirement snapshot CLI: versioned, never overwritten

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-5 requirement snapshot、R4-7 snapshot file） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `doc/reviews/workflow-governance/evidence/52/` / owner implementation seat / worktree `.worktrees/52-requirement-snapshot` / branch `cp/wave2-52-requirement-snapshot` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED` |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/52-requirement-snapshot` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/52-requirement-snapshot-review` |
| 責任邊界 | the snapshot script, its tests and the scripts README |
| 禁止修改 | everything else |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/README.md
create = skills/johnny-project-takeover/scripts/requirement_snapshot.py
create = tests/test_gate_requirement_snapshot.py
forbid = skills/johnny-project-takeover/scripts/dispatch_lint.py
forbid = skills/johnny-project-takeover/scripts/receipt_fence_check.py
forbid = skills/johnny-project-takeover/scripts/index_pins.py
forbid = skills/johnny-project-takeover/scripts/evidence_gate.py
forbid = library/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = .github/
forbid = template/
```

## 使用者拍板與可觀察結果

The owner approved wave 2 on 2026-11-04. R4-5 says `TAKEOVER` and `DELTA` enter from a requirement snapshot; R4-7 fixes its file. A plugin user runs:

- `requirement_snapshot.py take --source <name> --input <rows.json> [--root <dir>] [--taken-at <ISO-8601 UTC>]` → writes `<root>/<source>/<date>-v<n>.json` (default root `doc/requirements/snapshots`), `n` one higher than the highest existing version for that source; prints the path; exit 0. When the rows equal the latest version's rows, nothing is written, the latest path is printed with `unchanged`, exit 0.
- `requirement_snapshot.py verify <snapshot.json>` → exit 0 when the file is well formed and its `source_sha256` matches; exit 1 with one line per defect otherwise.
- `requirement_snapshot.py diff --source <name> <vA> <vB> [--root <dir>]` → prints `added`, `removed` and `changed` requirement ids, one per line; exit 0 (informational).

Exit 2 when the file system cannot serve the run (root not writable, input unreadable); exit 3 on bad arguments. A snapshot file is never overwritten or edited; a later edit is the next version (R4-7).

### File format (R4-7)

`{"source": <name>, "taken_at": <ISO-8601 UTC>, "source_sha256": <sha256 of the canonical JSON of rows>, "rows": [...]}`. Row fields: `requirement_id` (non-empty, unique in the file), `page_id`, `title`, `type`, `source_ref` (URL or repository-relative path; never a host absolute path), `source_sha256` (64 lower-case hex), `status` (`active` | `retired`), `version` (integer ≥ 1). Canonical JSON: keys sorted, separators `,` and `:`, UTF-8, rows sorted by `requirement_id`. The file itself is written with LF and a final LF.

### Defect codes (`take` refuses with exit 1 and writes nothing; `verify` reports)

`ROW_FIELD_MISSING`, `ROW_FIELD_TYPE`, `DUPLICATE_REQUIREMENT`, `STATUS_UNKNOWN`, `SOURCE_REF_ABSOLUTE`, `DIGEST_FORMAT`, `SNAPSHOT_DIGEST_MISMATCH` (verify only), `NAME_INVALID` (a source name with a path separator, `..`, or characters outside `[A-Za-z0-9._-]`).

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/52-requirement-snapshot`.
- reviewer：`ticket-review` seat in `.worktrees/52-requirement-snapshot-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket, the dispatch file, R4-5, R4-7.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a stdlib command-line script; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：`skills/johnny-project-takeover/scripts/requirement_snapshot.py`
- 公開契約／資料模型：typed dataclasses `Row`, `Snapshot`; the file format above; exit codes 0/1/2/3.

## TDD 設計

1. 正常行為：`take` twice with different rows → `v1` then `v2`; with equal rows the second run writes nothing and prints `unchanged`; `diff v1 v2` lists the changes; `verify` exits 0 on both files.
2. 規則違反／輸入錯誤：one test per defect code; `take` with a defect writes no file and leaves earlier versions byte-identical.
3. 外部失敗／fail-closed：root not writable → exit 2; input unreadable → exit 2; input that is not JSON, or JSON without a `rows` list → exit 1 `ROW_FIELD_TYPE` (a red of the input); an existing target file at write time (a race) → exit 2, never overwritten (exclusive create).
4. 回歸保護：the canonical digest does not depend on input key order, row order or the input file's line endings; `taken_at` is not part of `source_sha256`.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | source name: `..`, `a/b`, `a\b`, absolute, empty, trailing dot, case variants that collide on Windows (`Source` vs `source` refused as the same directory) |
| 2 | null／空字串／陣列 | 是 | `null` field, empty string id, whitespace-only id, empty rows list (allowed: an empty snapshot is a valid version), missing `rows` |
| 3 | 權限繞過 | 否 | no access control |
| 4 | Token 格式與比較 | 是 | `source_sha256`: 63/65 characters, upper case, non-hex |
| 5 | 錯誤碼是否一致 | 是 | codes distinct; printed `<code> <requirement_id or field>: <detail>` |
| 6 | 例外是否會拋出 | 是 | write failure mid-file leaves no partial file (write to a temporary name in the same directory, then exclusive rename) → exit 2 |

## 完成定義與證據

- `python -m pytest tests/test_gate_requirement_snapshot.py -q` exit 0; `mypy --strict --python-version 3.11` exit 0; stdlib only; no `Any`.
- The receipt follows R4-7 cells; every `tool_digest` lists the three wave-1 scripts and `requirement_snapshot.py`; it passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9, which verifies the three wave-1 digests; the reviewer verifies the fourth).
- **反向突變證據**：for each defect code remove its check → its test red → restore; plus: overwrite allowed (red), digest over unsorted keys (red), `taken_at` inside the digest (red), non-exclusive create (red).
- full suite: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：plugin-local script.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
