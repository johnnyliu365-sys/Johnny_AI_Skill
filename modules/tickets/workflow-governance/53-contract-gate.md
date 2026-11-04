# 53｜Contract gate: every requirement has a spec, every spec is bound and honest

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2 contract gate row、R4-6、R4-7 contract-gate codes、R4-8 contract-gate declaration） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision04 / receipt under `.worktrees/53-contract-gate-out/` / owner implementation seat / worktree `.worktrees/53-contract-gate` / branch `cp/wave2-53-contract-gate` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `CONVERGENCE_REPLANNED`（closure revision04 after the revision03 initial review: S53-15 to S53-18 TICKET_DEFECT; correction 1 dispatched to the same seat） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/53-contract-gate` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/53-contract-gate-review` |
| 責任邊界 | the contract gate script, its tests and the scripts README |
| 禁止修改 | everything else |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/README.md
create = skills/johnny-project-takeover/scripts/contract_gate.py
create = tests/test_gate_contract.py
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
`contract_gate.py --repo <dir> --snapshot <snapshot.json> --specs <directory under the repo>`.
Exit 0 with `requirements=N specs=M defects=0`; exit 1 with one line `<code> <spec or requirement>: <detail>` per defect; exit 2 when git, the file system or a source cannot be served; exit 3 on bad arguments.

### What the gate reads

- The snapshot: an R4-7 snapshot file (ticket 52's format). Requirements with `status` `active` must each be declared by at least one spec; `retired` ones must be declared by none.
- Specs: every file named `test_*.py` (case-sensitive) under `--specs`. Each spec's first comment block (the leading run of lines starting with `#`, before any code) holds declarations, one per line: `# requirement: <id>` (one or more), `# source: <repository-relative path> sha256:<64 hex>` (one or more), `# mutation: <name>` (one or more). Only these three lower-case keys are declarations; every other comment line, including `# SPDX-License-Identifier: …` or `# Requirement: …`, is free text and ignored.
- `--repo` must be the top level of a git work tree: `git rev-parse --show-toplevel` run there, resolved, equals `--repo` resolved; otherwise exit 2. Every git child runs with the `GIT_*` variables that select a repository or a work tree (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`) removed from its environment.
- Source bytes (revision03, the same design as ticket 51): a declared source path is first checked for canonical form (non-empty, at most 1024 bytes in UTF-8, the text-value rule, `/` as its only separator after the `./` and backslash normalisation of TDD 4, no leading `/` or `:`, no drive letter, no empty, `.` or `..` segment after that normalisation); a path that fails is `SOURCE_MISSING` naming the line. A canonical path is then looked up once, literally, by writing `HEAD:<path>` to the standard input of `git cat-file --batch-check` and reading the content through `git cat-file --batch`; it is never a pathspec and never on a command line. `missing` or a type other than `blob` is `SOURCE_MISSING`. Only git failing to start, exiting non-zero or answering outside its format is exit 2. The digest is over the blob, so it is the same on every host whatever its line-ending settings.
- Empty and missing values: an empty `requirement:` value is `RETIRED_REQUIREMENT_BOUND` (bound to no requirement of the snapshot); a spec that declares a requirement and no `source:` line is `SOURCE_MISSING`; an empty `mutation:` value is `NO_MUTATION`.
- Declaration values: only spaces and tabs around a value are removed. A value that then breaks the text-value rule is a red with the code of its key: `requirement:` gives `RETIRED_REQUIREMENT_BOUND`, `source:` gives `SOURCE_MISSING`, `mutation:` gives `NO_MUTATION`, each naming the line.
- Spec text (revision03): a spec file is decoded the way Python decodes source (its PEP 263 coding declaration or UTF-8, with a BOM honoured), and the decoded text is what is parsed, analysed and quoted in details, so offsets and text always agree. Everything derived from a spec's bytes (decoding, parsing, walking the tree, rendering a detail) runs inside one per-spec guard: any failure there is a red of that spec (`LITERAL_EXPECTED` with a detail saying the spec cannot be analysed and why), whatever exception type it raises. Only reading the file from disk and running git can be exit 2. Links and junctions under `--specs` are not followed.
- Snapshot: a repeated key in any object makes the file not an R4-7 snapshot (exit 3), as in ticket 52.
- Snapshot ids are compared exactly, never stripped; a snapshot whose `requirement_id` values break the ticket 52 character set is not an R4-7 snapshot (exit 3).
- Output streams: defect lines go to stdout, one per line; the summary line goes to stdout at exit 0 and to stderr at exit 1.
- A `source:` that is a URL (contains `://`) cannot be verified offline in wave 2: exit 2 with `SOURCE_UNSERVABLE`, never a red.

### Defect codes (R4-7; exit 1)

| Code | When |
| --- | --- |
| `NO_SPEC_FOR_REQUIREMENT` | an active requirement is declared by no spec |
| `SOURCE_MISSING` | a declared source path is not canonical, or is not a blob at `HEAD` |
| `SOURCE_DIGEST_MISMATCH` | sha256 of the source file's bytes differs from the declared digest |
| `RETIRED_REQUIREMENT_BOUND` | a spec declares a requirement that is retired or absent from the snapshot |
| `LITERAL_EXPECTED` | an `assert` whose test is a comparison with a literal constant on either side: a number, a string, bytes, or a list, tuple, set or dict display made only of such constants. `None`, `True` and `False` do not count |
| `NO_MUTATION` | a spec that declares a requirement has no `mutation:` line |

A `source:` line with a missing digest or a digest that is not 64 lower-case hex is `SOURCE_MISSING` naming the line. An assertion the gate cannot analyse within its limits (nesting deeper than its recursion budget, a literal too large to render) is `LITERAL_EXPECTED` with a detail saying so: an unverifiable contract is not honest, and the run never exits 2 because of it. Literal details are rendered from the source text, truncated to 120 characters.

### Text values (all wave-2 gates; added after the ticket 52 review)

Every string read from an input is valid Unicode without lone surrogates and without control characters (U+0000–U+001F, U+007F) unless a field explicitly allows them; a string that breaks this is a red of the input (exit 1), never a tool fault. Every subject printed in a defect line is printed in a form that cannot span two lines or forge another line (Python `repr` or an equivalent escape), so one defect is always one line.


## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/53-contract-gate`.
- reviewer：`ticket-review` seat in `.worktrees/53-contract-gate-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket, the dispatch file, R4-2, R4-6, R4-7, R4-8.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：a stdlib command-line script; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：`skills/johnny-project-takeover/scripts/contract_gate.py`
- 公開契約／資料模型：typed dataclasses `Requirement`, `SpecDeclaration`, `Defect`; the codes above; exit codes 0/1/2/3. The literal check uses the standard `ast` module; a spec that does not parse is exit 1 with `LITERAL_EXPECTED` naming the syntax error line (an unreadable contract is not honest), never a traceback.

## TDD 設計

1. 正常行為：a snapshot with two active requirements, two specs declaring them with correct sources and mutations and ledger-based asserts → exit 0.
2. 規則違反／輸入錯誤：one test per defect code; a spec carrying several defects reports each; `assert x == expected_from_ledger` is not a literal; `assert x == 3`, `assert "a" == y`, `assert x in (1, 2)` are literal; `assert x is None` is not.
3. 外部失敗／fail-closed：snapshot unreadable → 2; snapshot that is not an R4-7 snapshot (not JSON, no `rows`, a row without `requirement_id` or `status`) → 3 with the reason (the argument is not a snapshot); `--specs` not a directory → 2; URL source → 2 `SOURCE_UNSERVABLE`.
4. 回歸保護：an assert behind 1500 `not` and an assert against a 4000-digit hex literal each give exit 1 with `LITERAL_EXPECTED`; a spec whose first source is correct and a later one is wrong reports the later one; `Test_x.py` is not collected; a newline, CR, U+2028 or NEL inside a snapshot id or any subject is escaped so one defect is one line; declarations after the first code line are ignored; a latin-1 and a cp950 spec with a PEP 263 declaration and a non-ASCII literal each give `LITERAL_EXPECTED` exit 1; a spec that cannot be decoded is a red; `ast.parse` raising `RecursionError` or `MemoryError` is a red; a 40000-character source path and a `:(glob)` source are `SOURCE_MISSING`; git failing during a lookup is exit 2, never `SOURCE_MISSING`; a control character or ESC inside a declaration value, or one other than a space or a tab around it, is a red with its key's code (spaces and tabs around a value are removed); `--repo` a subdirectory or a plain directory inside a work tree is exit 2; an inherited `GIT_DIR` does not change the result; a junction under `--specs` is not followed; a snapshot with a repeated key is exit 3; every fault message prints on one line, and a usage error prints the fixed usage banner followed by one escaped error line; the scripts README test counts with number words up to twenty; Windows CRLF spec files read the same; a source path given with `./` or backslashes resolves the same, and one with `..` escaping the repository is `SOURCE_MISSING`.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | source paths: equal to the repo root, one extra character, trailing slash, case variant, `..` traversal, absolute path, empty path |
| 2 | null／空字串／陣列 | 是 | empty snapshot rows (every spec then binds an absent requirement), empty `--specs` directory (no spec: every active requirement red), empty declaration values |
| 3 | 權限繞過 | 否 | no access control |
| 4 | Token 格式與比較 | 是 | digests 63/65 characters, upper case, non-hex; requirement ids compared exactly (case-sensitive); spaces and tabs around a declaration value removed, nothing else |
| 5 | 錯誤碼是否一致 | 是 | the six codes distinct, one line each; a red never exits 2 and a fault never exits 1 |
| 6 | 例外是否會拋出 | 是 | unreadable spec file (permission) → exit 2 with the path; syntax error in a spec → exit 1 as above; no traceback in any case |

## 完成定義與證據

- `python -m pytest tests/test_gate_contract.py -q` exit 0; `mypy --strict --python-version 3.11` exit 0; stdlib only; no `Any`.
- **反向突變證據**：for each of the six codes remove its check → its test red → restore; plus: literal check counting `None` (red), declarations read past the first code line (red), source path not confined to the repository (red).
- Receipt: R4-7 cells; `tool_digest` lists the three wave-1 scripts and `contract_gate.py`; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9).
- full suite: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：plugin-local script.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Re-plan to closure revision02 (after the revision01 initial review `CHANGES_REQUESTED`)

Review record: `doc/reviews/workflow-governance/53-contract-gate-code-review.md`. S53-05 and S53-06 are `TICKET_DEFECT`s; the closure is rebuilt here before correction 1.

| Finding | Class | Disposition in revision02 |
| --- | --- | --- |
| S53-01 | IMPLEMENTATION_DEFECT | an assertion the gate cannot analyse is `LITERAL_EXPECTED`; details rendered from source text, truncated |
| S53-02 | IMPLEMENTATION_DEFECT | text-value rule: every subject escaped to one line |
| S53-03 | EVIDENCE_DEFECT | multi-source and case-sensitive name tests |
| S53-04 | IMPLEMENTATION_DEFECT | README introduction and unexpected-error rule name every script present |
| S53-05 | TICKET_DEFECT | declaration keys, empty values, missing source, snapshot ids and output streams as above |
| S53-06 | TICKET_DEFECT | source bytes read as the blob at `HEAD`; git failures exit 2 |
| S53-07 | OUT_OF_SCOPE_HARDENING | not taken: the literal rule stays syntactic (R4-8); deeper analysis is a wave-3 candidate |

## Re-plan to closure revision03 (after the revision02 correction review `CONVERGENCE_REVIEW_REQUIRED`)

Review record section "Revision02 correction review". CodeReview §5: the closure revision used its one initial and one correction review, so the control plane rebuilds the design. Root cause of S53-01, S53-08 and S53-12(b): a red or a fault was chosen by exception type, so every new exception an analyser can raise was a new door to exit 2. Revision03 classifies by where a failure comes from: anything derived from a spec's bytes is a red of that spec; only disk reads and git are faults. Root cause of S53-09 and S53-12(a): source paths reached git as pathspecs on a command line; revision03 uses the canonical form and one literal lookup through standard input, the same design as ticket 51 revision03. Revision03 starts a new cadence: one initial review and one correction review.

| Finding | Class | Disposition in revision03 |
| --- | --- | --- |
| S53-08 | IMPLEMENTATION_DEFECT | specs decoded as Python decodes source; one per-spec guard |
| S53-09 | IMPLEMENTATION_DEFECT | canonical source path, literal lookup through standard input |
| S53-10 | IMPLEMENTATION_DEFECT | declaration values: spaces and tabs removed only; text-value rule with the key's code |
| S53-11 | IMPLEMENTATION_DEFECT | number words up to twenty in the README test |
| S53-12 | EVIDENCE_DEFECT | tests for a pathspec-magic source, parser exceptions and a lookup failure |
| S53-13 | TICKET_DEFECT | `--repo` is the work-tree top level; repository-selecting `GIT_*` variables removed; `SOURCE_MISSING` and row 4 text corrected |
| S53-14 | OUT_OF_SCOPE_HARDENING (taken now) | repeated snapshot keys exit 3; links and junctions under `--specs` not followed; tests for one-line fault and usage messages |

### Disposition correction (revision03, during implementation 3)

The ticket 51 revision03 review found that git follows replace refs in `cat-file` and `ls-tree`, so a blob read "at HEAD" or "at a commit" can be another object (S51-16), and that a lookup can fetch over the network in a partial clone. The same applies here. Added to this revision: Every git child runs with `--no-replace-objects` (and `GIT_NO_REPLACE_OBJECTS=1`), with `GIT_NO_LAZY_FETCH=1`, and with the repository-selecting `GIT_*` variables removed (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`, and the `GIT_CONFIG_*` variables); a replace ref never redirects a lookup and a lookup never fetches over the network. One test with `git replace` on a blob this gate reads. Nothing else changes.

## Re-plan to closure revision04 (after the revision03 initial review `CHANGES_REQUESTED`)

Review record section "Revision03 initial review". S53-15 to S53-18 are `TICKET_DEFECT`s; the closure is rebuilt here before correction 1. The revision03 design (per-spec guard, source decoding, canonical paths, one literal lookup, git environment) stands.

### Rules added in revision04 (binding)

- One commit per run: `HEAD` is resolved once to a full object id at the start, and every lookup of the run uses that id through one `cat-file --batch` process.
- Entry mode and unservable objects: a source's tree entry is read from its parent tree (`<commit>:<parent>`) through the same standard input. A source whose entry is a symbolic link (mode `120000`) or a gitlink is `SOURCE_MISSING` ("not a regular file"): a contract cites file content, never a link. An entry the parent tree names but the store cannot serve is a fault; a path the parent tree does not name is `SOURCE_MISSING`.
- Red before fault (the reading of R4-2 applied in tickets 51, 52, 54 and 56, awaiting owner confirmation): the gate reports every red it can find and exits 1 if there is one, with each fault, `SOURCE_UNSERVABLE` included, printed on stderr on one line; it exits 2 only when it found no red. The test that pinned the opposite is inverted.
- Wording, as TDD 4 now says: spaces and tabs around a declaration value are removed; a usage error prints the banner and one escaped error line.

| Finding | Class | Disposition in revision04 |
| --- | --- | --- |
| S53-15 | TICKET_DEFECT | absent and unservable told apart through the parent tree; tests with a pruned blob and a blobless clone give exit 2 |
| S53-16 | TICKET_DEFECT | symbolic-link and gitlink sources are `SOURCE_MISSING`, with a test that changes the target |
| S53-17 | TICKET_DEFECT | red before fault, with a URL source beside a literal red, an unreadable spec beside a red, and a git fault after reds |
| S53-18 | TICKET_DEFECT | the wording above |
| S53-19 | EVIDENCE_DEFECT | removal mutants for all six codes in M1 |
| S53-20 | EVIDENCE_DEFECT | tests for a chained comparison with a literal beyond the first comparator, Unicode whitespace as the separator and in the key, the `--batch` size check, an inexact `missing` answer, and `-True` |
| S53-21 | OUT_OF_SCOPE_HARDENING (taken now) | one commit per run, as above |
