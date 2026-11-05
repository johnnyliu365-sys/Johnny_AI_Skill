# 60｜Gate hardening: the findings carried when the six wave-2 gates were approved

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-2, R4-4 trust boundary, R4-7, R4-8; CodeReview §5 rule B carried findings） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/60-gate-hardening-carried-out/` / owner implementation seat / worktree `.worktrees/60-gate-hardening-carried` / branch `cp/wave2-60-gate-hardening-carried` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `REVIEW_APPROVED`（revision01 initial review APPROVED on `1c0fb917`; record `doc/reviews/workflow-governance/60-gate-hardening-carried-code-review.md`; ready for integration） |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/60-gate-hardening-carried` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/60-gate-hardening-carried-review` |
| 責任邊界 | the six wave-2 gate scripts, their test files and the scripts README |
| 禁止修改 | everything else; no gate's exit-code contract or binding rule changes |
| 環境 | `LOCAL` |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = skills/johnny-project-takeover/scripts/README.md
modify = skills/johnny-project-takeover/scripts/evidence_gate.py
modify = skills/johnny-project-takeover/scripts/requirement_snapshot.py
modify = skills/johnny-project-takeover/scripts/contract_gate.py
modify = skills/johnny-project-takeover/scripts/coverage_map.py
modify = skills/johnny-project-takeover/scripts/preflight.py
modify = skills/johnny-project-takeover/scripts/repair_guard.py
modify = tests/test_gate_evidence.py
modify = tests/test_gate_requirement_snapshot.py
modify = tests/test_gate_contract.py
modify = tests/test_gate_coverage_map.py
modify = tests/test_gate_preflight.py
modify = tests/test_gate_repair_guard.py
forbid = skills/johnny-project-takeover/scripts/dispatch_lint.py
forbid = skills/johnny-project-takeover/scripts/receipt_fence_check.py
forbid = skills/johnny-project-takeover/scripts/index_pins.py
forbid = skills/johnny-project-takeover/scripts/integrate.py
forbid = library/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = .github/
forbid = template/
```

## 使用者拍板與可觀察結果

The owner adopted CodeReview §5 rule B on 2026-11-05 and confirmed the R4-4 trust boundary. Tickets 51 to 56 were approved with findings carried; this ticket closes them. Every gate keeps its exit codes, codes and binding rules; the work is tests that pin behaviour the gates already have, plus the small hardening items below. Two items must land before any other change of their gate (CodeReview §5 rule B, "a regression would let a forbidden change pass"): S53-30 and S54-17.

### Items

| Gate | Finding | Work |
| --- | --- | --- |
| evidence gate | S51-26 | tests with a malformed digest value and with two different values beside each of `cat-file` exiting non-zero, an answer outside the format, and an unservable root tree: exit 1, the red on stdout, the fault on stderr |
| evidence gate | S51-27 | README and docstring: a non-blob `--tool` gives `TOOL_DIGEST_MISSING` when no cell lists it and `TOOL_DIGEST_STALE` when one does; always exit 1 with the fault on stderr |
| evidence gate | S51-28 | tests pinning one red per malformed occurrence, one disagreement red per path, and a value beside its upper-case copy counted as a disagreement |
| evidence gate | S51-29 | the not-a-repository test helper uses only a temporary directory (never the drive root) and matches the gate's fault code and its own text, not git's English message |
| requirement snapshot | S52-37 | test: equal rows after v2 and v3 print `unchanged` and write nothing |
| requirement snapshot | S52-38 | tests: stray names `<date>-v9Xjson`, a short date, `-v9.JSON` and `-V9.json` are not versions (take and diff) |
| requirement snapshot | S52-39 | tests: stray `.v2.claim.bak` and `x.v2.claim` do not block take |
| requirement snapshot | S52-40 | test: U+001F is escaped on every printed line |
| requirement snapshot | S52-41 | C1 control characters (U+0080–U+009F) are escaped on every printed line too, with a test (U+009B from a root path on the success line) |
| contract gate | S53-30 | **must land first for this gate.** Test: a batch answer whose body hashes to an id that differs from the asked id only in its last hex digit is a fault (pins the full-width comparison) |
| contract gate | S53-31 | a blob forged as an object of another kind is reported with its id and the word forged or mismatch, like the tree and commit kind faults |
| contract gate | S53-32 | no work: SHA-1 collision resistance is carried by the R4-4 integration clone (fetched with `transfer.fsckObjects`, which uses git's collision-detecting SHA-1); the README says so |
| coverage-map guard | S54-16 | tests: an unknown-path match is not satisfied by a `carried_to` with an extra leading segment or a case variant while the spec is unreadable (exit 1 with `CARRIED_TARGET_MISSING`) |
| coverage-map guard | S54-17 | **must land first for this gate.** Every git child also runs with `-c core.commitGraph=false`; a test with a forged commit-graph that would move `--base main^` gives the true result |
| preflight gate | S55-24 | the namespace check strips a drive-relative first component like the device check, so `C:GLOBALROOT\x` is exit 3; README and STATEMENT wording agree |
| preflight gate | S55-25 | an interrupt that lands outside `main`'s handlers (start-up after argument parsing, stream setup, output) exits 2 with one line; a test injects one into each window it can reach in-process |
| repair guard | S56-27 | test: with two forged trees the fault names the first one met, as documented |

Not in this ticket: S55-11 and S55-26 (a Windows job object for the process tree) are wave 3.

### Rules every wave-2 gate follows (binding)

Unchanged and still binding: red before fault, text values with one line per printed subject, the git environment rules of each gate, JSON input rules, and the exit codes of R4-2. No existing assertion changes unless a row above changes the rule it pins; each such change is named in the STATEMENT section.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/60-gate-hardening-carried`.
- reviewer：`ticket-review` seat in `.worktrees/60-gate-hardening-carried-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket, tickets 51 to 56 and their review records (the findings named above), R4-2, R4-4.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：stdlib command-line scripts; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the six gate scripts above
- 公開契約／資料模型：unchanged from tickets 51 to 56.

## TDD 設計

1. 正常行為：each gate's existing suite stays green.
2. 規則違反／輸入錯誤：one test per row of the items table, each failing under the counter-mutation its review named (C01, C02, C07, C08, C09 for ticket 51; K13, K30 to K34, K50 for 52; R1, R1b for 53; Y1, Y2 for 54; K9 for 56).
3. 外部失敗／fail-closed：S54-17 forged commit-graph; S55-25 interrupts; S51-26 fault kinds.
4. 回歸保護：the full suite; every gate's own mutation set from its approved receipt still red.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | S52-38 version names, S52-39 claim names, S54-16 unknown-path prefix and case, S55-24 drive-relative namespace |
| 2 | null／空字串／陣列 | 否 | no new input shape |
| 3 | 權限繞過 | 是 | S53-30 full-width hash comparison; S54-17 commit-graph |
| 4 | Token 格式與比較 | 是 | S51-28 value case, S53-30 id width |
| 5 | 錯誤碼是否一致 | 是 | S51-26 red before fault; S55-25 interrupts exit 2 |
| 6 | 例外是否會拋出 | 是 | S55-25 interrupt windows; S53-31 kind fault |

## 完成定義與證據

- each of the six gate test files exit 0; `mypy --strict --python-version 3.11` on each changed script exit 0; stdlib only; no `Any`.
- **反向突變證據**：every counter-mutation named in TDD 2 is red; S54-17 without the flag is red; S55-24 without the strip is red; S52-41 without C1 escaping is red. An equivalent survivor stays in the M1 capture, marked, with its reason.
- Receipt: R4-7 cells; `tool_digest` lists the three wave-1 scripts and the six gate scripts; every cell runs at the committed candidate and each capture starts with the sha256 of the scripts it ran; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9).
- full suite under the host lock: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：plugin-local scripts.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Carried after approval

The revision01 initial review approved `1c0fb917` with five non-blocking findings. The control plane routes them as follows:

| Finding | Route |
| --- | --- |
| S60-01 | an inherited `GIT_TEST_COMMIT_GRAPH` re-enables the commit-graph the S54-17 flag turns off. This is in the forged-store class the R4-4 integration clone settles, so it does not block. It goes with the next change of the coverage-map guard: drop every `GIT_TEST_*` name from the child environment, add a test, and correct the README sentence. The same environment rule goes into ticket 50's next revision for `integrate.py` |
| S60-02 | carried to wave 3 with S55-11 and S55-26 (job object or signal handler) |
| S60-03 | the next change of the contract gate: pin the SHA-256 width of the hash comparison |
| S60-04 | the next change of the preflight gate: interrupt the standard-error flush too |
| S60-05 | evidence only, receipt of this ticket; the reviewer's unfiltered rerun stands |
