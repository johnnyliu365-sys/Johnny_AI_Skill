# 53｜Contract gate: every requirement has a spec, every spec is bound and honest

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2 contract gate row、R4-6、R4-7 contract-gate codes、R4-8 contract-gate declaration） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/53-contract-gate-out/` / owner implementation seat / worktree `.worktrees/53-contract-gate` / branch `cp/wave2-53-contract-gate` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED` |
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
- Specs: every file named `test_*.py` under `--specs`. Each spec's first comment block (the leading run of lines starting with `#`, before any code) holds declarations, one per line: `# requirement: <id>` (one or more), `# source: <repository-relative path> sha256:<64 hex>` (one or more), `# mutation: <name>` (one or more).
- A `source:` that is a URL (contains `://`) cannot be verified offline in wave 2: exit 2 with `SOURCE_UNSERVABLE`, never a red.

### Defect codes (R4-7; exit 1)

| Code | When |
| --- | --- |
| `NO_SPEC_FOR_REQUIREMENT` | an active requirement is declared by no spec |
| `SOURCE_MISSING` | a declared repository-relative source does not exist in the working tree, or escapes the repository |
| `SOURCE_DIGEST_MISMATCH` | sha256 of the source file's bytes differs from the declared digest |
| `RETIRED_REQUIREMENT_BOUND` | a spec declares a requirement that is retired or absent from the snapshot |
| `LITERAL_EXPECTED` | an `assert` whose test is a comparison with a literal constant on either side: a number, a string, bytes, or a list, tuple, set or dict display made only of such constants. `None`, `True` and `False` do not count |
| `NO_MUTATION` | a spec that declares a requirement has no `mutation:` line |

A spec with a malformed declaration line (unknown key, missing digest, digest not 64 lower-case hex) is reported with the code of the clause it fails (`SOURCE_MISSING` for an unusable source line, `NO_MUTATION` for an empty mutation name) and the detail names the line.

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
4. 回歸保護：declarations after the first code line are ignored; Windows CRLF spec files read the same; a source path given with `./` or backslashes resolves the same, and one with `..` escaping the repository is `SOURCE_MISSING`.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | source paths: equal to the repo root, one extra character, trailing slash, case variant, `..` traversal, absolute path, empty path |
| 2 | null／空字串／陣列 | 是 | empty snapshot rows (every spec then binds an absent requirement), empty `--specs` directory (no spec: every active requirement red), empty declaration values |
| 3 | 權限繞過 | 否 | no access control |
| 4 | Token 格式與比較 | 是 | digests 63/65 characters, upper case, non-hex; requirement ids compared exactly (case-sensitive), surrounding whitespace stripped |
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
