# 52｜Requirement snapshot CLI: versioned, never overwritten

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-5 requirement snapshot、R4-7 snapshot file） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision05 / receipt under `doc/reviews/workflow-governance/evidence/52/` / owner implementation seat / worktree `.worktrees/52-requirement-snapshot` / branch `cp/wave2-52-requirement-snapshot` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `CONVERGENCE_REPLANNED`（closure revision05 after the revision04 correction review `CONVERGENCE_REVIEW_REQUIRED`: S52-28 to S52-30, evidence only; revision05 initial review CHANGES_REQUESTED (evidence only); correction 1 dispatched） |
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

`ROW_FIELD_MISSING`, `ROW_FIELD_TYPE` (a field of the wrong type, an unexpected field, a blank or whitespace-only `requirement_id`, a string that breaks the text-value rule below), `DUPLICATE_REQUIREMENT`, `STATUS_UNKNOWN`, `SOURCE_REF_ABSOLUTE` (a `source_ref` that is empty, starts with `/`, `\` or `~`, carries a drive letter, or has a `..` segment; a URL with a scheme is allowed), `DIGEST_FORMAT`, `SNAPSHOT_DIGEST_MISMATCH` (a stored version whose `source_sha256` does not match its rows: reported by `verify`, and by `take` or `diff` whenever they read that version; exit 1), `NAME_INVALID` (a source name with a path separator, `..`, characters outside `[A-Za-z0-9._-]`, a trailing dot, a Windows reserved device name, or a case variant of an existing source). `take` and `diff` apply every name rule, the case-variant rule included, because they know the root; `verify` takes a single file and applies the name rules to the file's `source` value, not the case-variant rule and not a comparison with the directory the file sits in.

JSON input: a repeated key in an object (a row or the top level) is `ROW_FIELD_TYPE`; version numbers in file names and arguments are ASCII digits only; a top-level `source` or `source_sha256` that breaks the text-value rule is `ROW_FIELD_TYPE` as well as its format code, as for row fields.

`requirement_id`: printable characters only (letters, digits, `._:-/`), 1 to 128 characters; anything else is `ROW_FIELD_TYPE`.

### Version uniqueness

A version number is unique per source whatever the date. `take` claims the number before it publishes: it creates `<root>/<source>/.v<n>.claim` exclusively, re-scans the published files, and if any published file already carries version `n` or higher it removes its claim and exits 2 (another writer won); otherwise it publishes `<date>-v<n>.json` exclusively and removes the claim. A claim it cannot create (another writer holds it) is exit 2. A claim left behind by a crash makes later `take` runs exit 2 naming the claim file, which the owner removes. Claim files are never committed: the scripts README tells target projects to ignore `.v*.claim`.

### Text values (all wave-2 gates; added after the ticket 52 review)

Every string read from an input is valid Unicode without lone surrogates and without control characters (U+0000–U+001F, U+007F) unless a field explicitly allows them; a string that breaks this is a red of the input (exit 1), never a tool fault. Every subject printed in a defect line is printed in a form that cannot span two lines or forge another line (Python `repr` or an equivalent escape), so one defect is always one line.


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
3. 外部失敗／fail-closed：two concurrent `take` runs on one source with different dates: exactly one publishes `vN`, the other exits 2 and publishes nothing (a real two-process test plus an injected interleaving); a stale claim exits 2 naming it; root not writable → exit 2; input unreadable → exit 2; input that is not JSON, or JSON without a `rows` list → exit 1 `ROW_FIELD_TYPE` (a red of the input); an existing target file at write time (a race) → exit 2, never overwritten (exclusive create).
4. 回歸保護：with v1 and v3 published the next `take` writes v4 (highest + 1, not count + 1); a lone surrogate and a newline inside an id are reds printed on one line; the canonical digest does not depend on input key order, row order or the input file's line endings; `taken_at` is not part of `source_sha256`.

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

## Re-plan to closure revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record: `doc/reviews/workflow-governance/52-requirement-snapshot-code-review.md`. S52-07 is a `TICKET_DEFECT`; the closure is rebuilt here before correction 1. The seat's choices for the open cases are adopted where they fit R4-2 and written into the defect codes above; version uniqueness and the text-value rule are new.

| Finding | Class | Disposition in revision02 |
| --- | --- | --- |
| S52-01 | IMPLEMENTATION_DEFECT | text-value rule: a lone surrogate is `ROW_FIELD_TYPE` exit 1 in `take` and `verify` |
| S52-02 | IMPLEMENTATION_DEFECT | `requirement_id` character set; every printed subject escaped, one defect per line |
| S52-03 | IMPLEMENTATION_DEFECT | version claim file, re-scan after claiming, exit 2 for the loser |
| S52-04 | EVIDENCE_DEFECT | the v1/v3 gap test |
| S52-05 | IMPLEMENTATION_DEFECT | README and docstring match the codes above |
| S52-06 | OUT_OF_SCOPE_HARDENING (taken now) | `diff` applies the case-collision rule |
| S52-07 | TICKET_DEFECT | the codes, `source_ref`, `requirement_id`, damaged-version and version-uniqueness rules above |

## Re-plan to closure revision03 (after the revision02 initial review `CHANGES_REQUESTED`)

Review record section "Revision02 initial review". S52-12 is a `TICKET_DEFECT`: the closure is rebuilt here before correction 2. Behaviour stays; the ticket now says what `verify` checks, and three cheap hardening items are taken.

| Finding | Class | Disposition in revision03 |
| --- | --- | --- |
| S52-10 | EVIDENCE_DEFECT | tests pairing a newline with an otherwise invalid `source_ref` and with an otherwise invalid source name, each asserting one line |
| S52-11 | IMPLEMENTATION_DEFECT | docstring matches the README and the code |
| S52-12 | TICKET_DEFECT | `verify` applies the name rules only, as above |
| S52-13, S52-14, S52-15 | OUT_OF_SCOPE_HARDENING (taken now) | top-level text rule, ASCII digits, repeated keys, as above, one test each |

### Correction 3 under revision03 (after the revision03 initial review `CHANGES_REQUESTED`)

No ticket defect was found, so revision03 stands. S52-16: the claim-file name pattern uses ASCII digits too, with one test. S52-17 (taken now): a version argument too long to name a stored version is "the requested version does not exist" (exit 2) with that message, never a raw exception text. The next review is the one correction review of revision03.

## Re-plan to closure revision04 (after the revision03 correction review `CONVERGENCE_REVIEW_REQUIRED`)

Review record section "Revision03 correction review". CodeReview §5: revision03 used its one initial and one correction review. Root cause of S52-18 and S52-20: the order of checks decided the exit, because a fault met early stopped the run before a red could be found. Revision04 fixes the order and the precedence. Revision04 starts a new cadence: one initial review and one correction review.

### Rules added in revision04 (binding)

- Red before fault (R4-2, "a red is never reported as a tool fault"): a command checks everything it can before it decides the exit. If it found any red, it prints every red on stdout and exits 1; a fault met on the way is printed on stderr, on one line, and does not change the exit. It exits 2 only when it found no red and a fault stopped it. The same holds for `take`, `verify` and `diff`.
- Order in `take` and `diff`: argument grammar (exit 3), then the name rules on `--source` (`NAME_INVALID`), then version lookups (an over-long version argument in either position is "the requested version does not exist", exit 2 unless a red was found), then reading and checking the stored files.
- Case variants: an existing directory entry collides with a source name only when the entry is ASCII and equal to the source name ignoring ASCII case; a non-ASCII entry never collides (NTFS keeps it distinct).
- Receipt: the receipt carries cell `P9`; its capture is the checker run on the receipt without its `P9` section, LF only; the receipt is then rebuilt with that section.

| Finding | Class | Disposition in revision04 |
| --- | --- | --- |
| S52-18 | IMPLEMENTATION_DEFECT | the order above; a test with an invalid source name and an over-long version argument gives exit 1 `NAME_INVALID` |
| S52-19 | EVIDENCE_DEFECT | the over-long argument tested in the second position too |
| S52-20 | TICKET_DEFECT | red before fault, as above; a test with a damaged v2 and a missing v9 gives exit 1 with `SNAPSHOT_DIGEST_MISMATCH` and the missing version on stderr |
| S52-21 | IMPLEMENTATION_DEFECT | docstring matches the README on claim names and the over-long rule |
| S52-22 | OUT_OF_SCOPE_HARDENING (taken now) | ASCII-only case comparison, with a test using the ligature and the Kelvin sign |
| S52-23 | EVIDENCE_DEFECT | the receipt carries `P9` as above |

### Correction 1 under revision04 (after the revision04 initial review `CHANGES_REQUESTED`)

No ticket defect was found, so revision04 stands. One clarification of its first binding rule, in the same direction as ticket 53 revision03: a failure derived from the bytes of an input or a stored version (deep nesting that the JSON parser cannot follow, for example) is a red of that file with the code a non-JSON file gets, never a fault; this replaces the revision01 acceptance of deep nesting as a fault. Only an error no input can produce (a programming error) may still end the run at once with exit 2. S52-24: as above, one test per reachable case. S52-25, S52-26: the tests the review names. S52-27 (taken now): a take test that nothing is read under an invalid source name. The next review is the one correction review of revision04.

## Re-plan to closure revision05 (after the revision04 correction review `CONVERGENCE_REVIEW_REQUIRED`)

Review record section "Revision04 correction review". CodeReview §5: revision04 used its one initial and one correction review. The candidate behaves as the closure says; the open findings are tests that do not pin it. Revision05 keeps every rule and adds the tests and two small output rules. It starts a new cadence: one initial review and one correction review.

### Rules added in revision05 (binding)

- Every line the tool prints, the usage line and the success and `unchanged` lines included, is escaped to one line like defect and fault lines.
- Repeated-key collection is linear in the number of keys.

| Finding | Class | Disposition in revision05 |
| --- | --- | --- |
| S52-28 | EVIDENCE_DEFECT | deep object nesting tested in take, verify and diff |
| S52-29 | EVIDENCE_DEFECT | tests with two defects of the same code and subject, in a row and at the top level |
| S52-30 | EVIDENCE_DEFECT | an unchanged take leaves a CRLF stored version byte-identical |
| S52-31 | OUT_OF_SCOPE_HARDENING (taken now) | every printed line escaped |
| S52-32 | OUT_OF_SCOPE_HARDENING (taken now) | linear repeated-key collection, with a 40000-key test under a time bound |

### Correction 1 under revision05 (after the revision05 initial review `CHANGES_REQUESTED`)

No ticket defect was found, so revision05 stands; the blocking items are tests. S52-34: printed-line tests with ESC, TAB, NUL and DEL through the usage error and through a fault line. S52-35: an id present three times reports every pair; two case-variant collisions (a mocked listing) report both. S52-36: stray `-v<n>.json.bak` and `-v<n>.jsonx` files next to real versions change neither take nor diff. Taken now, S52-33: `NaN`, `Infinity` and `-Infinity` anywhere in a JSON file are `ROW_FIELD_TYPE`, as for other non-JSON input. The next review is the one correction review of revision05.
