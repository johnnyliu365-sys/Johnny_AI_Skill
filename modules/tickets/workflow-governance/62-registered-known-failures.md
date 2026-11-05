# 62｜Known failures CI registers that are not environment failures

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-6; REQ-20261103-043 implementation readiness criterion 2; ticket 59 review findings S59-02, S59-03, S59-05） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/62-registered-known-failures-out/` / owner implementation seat / worktree `.worktrees/62-registered-known-failures` / branch `cp/wave2-62-registered-known-failures` / baseline the wave-2 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED` |
| 共同基準 | the `cp/wave2-gates` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/62-registered-known-failures` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/62-registered-known-failures-review` |
| 責任邊界 | the tests named below, the code they find defective inside the boundary, and the rows of `ci/registered-failures.json` that become passing |
| 禁止修改 | everything else; `.claude-plugin/marketplace.json` is not re-pinned by a seat (publication is the owner's) |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = tests/test_atomic_conditional_replace_capability.py
modify = tests/test_file_lock.py
modify = tests/test_guarded_integration_corrections.py
modify = tests/test_refusal_guidance.py
modify = tests/test_plugin_payload_boundary.py
modify = tests/test_plugin_publication.py
modify = ci/registered-failures.json
modify = ci/README.md
forbid = .claude-plugin/
forbid = skills/
forbid = Workflow.md
forbid = CodeReview.md
forbid = AGENTS.md
forbid = template/
forbid = .github/
```

## 使用者拍板與可觀察結果

Ticket 59 made CI green on Linux and Windows by registering every failing test by name. Its review (S59-02, S59-03, S59-05) found rows that are not environment failures: they fail on every platform, or the runner has the capability the reason says it lacks. After this ticket each such row is either gone from `ci/registered-failures.json` because its test passes, or carries a cause that a reviewer can confirm from the failure text and a `follow_up` that names an open ticket.

| Rows | Observed failure | Work |
| --- | --- | --- |
| `test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists` and the three `test_plugin_publication.py` pin tests (both OS) | the marketplace pin `0b3afd3645946f97662c336f0e6ac0dcae502e69` names a commit that no branch of the repository holds | diagnose where the pinned commit went; the tests stay as they are. Re-pinning the marketplace is publication, so the seat returns `CHANGE_DETECTED` with the commit the pin should name, and the rows stay registered with that cause until the owner re-pins |
| `test_atomic_conditional_replace_capability.py::test_acr6_exact_test_only_boundary` (both OS) | fails on main | diagnose; fix the test if it pins a stale boundary, else return `CHANGE_DETECTED` |
| `test_guarded_integration_corrections.py::…::test_reviewed_router_profile_composes_return_integration_and_audit` (both OS) | the audit step gives `SUSPEND` where the test expects `ADVANCE` | diagnose which side is current Router behaviour; fix the test if the Router is right, else return `CHANGE_DETECTED` |
| `test_refusal_guidance.py::ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered` (both OS) | the uncovered-enum roster is stale | update the roster to the enums the library holds, each placed with its reason |
| `test_atomic_conditional_replace_capability.py::test_acr2_…` and `test_acr3_…` (Linux; acr2 also Windows) | the test's own label validator refuses `linux-fs:ext2/ext3` because of the slash | fix the label or the validator inside the test so the Linux runner qualifies or fails for a stated runner cause |
| `test_file_lock.py::BlockingAcquisitionTests::test_a_waiter_is_held_out_and_then_let_in_rather_than_refused` (Linux) | `ValueError: I/O operation on closed file`: the test closes the waiter's stdin and then calls `communicate()`, which flushes stdin on POSIX | fix the test so the POSIX `fcntl.flock` path is exercised |

A row whose test now passes is removed (the checker's `REGISTERED_NOW_PASSING` makes a stale row red). No test is skipped, deleted or weakened; an assertion changes only where the diagnosis shows the test pins behaviour that is no longer the rule, and each such change is named in the STATEMENT with its evidence.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/62-registered-known-failures`.
- reviewer：`ticket-review` seat in `.worktrees/62-registered-known-failures-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; ticket 59 and its review record (S59-02, S59-03, S59-05).
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：tests and a CI list; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the registered-failure schema of ticket 59.

## TDD 設計

1. 正常行為：each fixed test passes on the host and on both runners; its row is gone.
2. 規則違反／輸入錯誤：each fixed test still fails under the counter-mutation that removes the behaviour it pins.
3. 外部失敗／fail-closed：the pin tests keep failing while the pinned commit is absent.
4. 回歸保護：`ci/check_registered_failures.py` exit 0 on a CI run of the candidate, both jobs.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path comparison changes |
| 2 | null／空字串／陣列 | 否 | no new input |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | the label form `linux-fs:<name>` (acr2, acr3) |
| 5 | 錯誤碼是否一致 | 否 | no exit codes change |
| 6 | 例外是否會拋出 | 是 | the closed-stdin `ValueError` (file lock) |

## 完成定義與證據

- the six test files pass on the host apart from the pin tests; `mypy --strict --python-version 3.11` on each changed test file exit 0; no `Any`.
- **反向突變證據**：for each fixed test, remove the behaviour it pins → red → restore.
- **CI evidence**：one run on a commit of this branch with both jobs `success`; run id, URL and the jobs JSON captured in the receipt.
- Receipt: R4-7 cells; passes `doc/reviews/workflow-governance/evidence/48/receipt_check.py` (cell P9); full suite under the host lock: failure set a subset of the base names; zero new red.

## 正式環境移植 SOP

- 不適用：tests and the CI list. The marketplace re-pin, if the diagnosis calls for one, is the owner's publication step.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
