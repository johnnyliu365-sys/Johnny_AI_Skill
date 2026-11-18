# 66｜Router library retirement (2): the cross-lifetime bridge — runner, wake, dispatch, review return and receipt-bound supervision

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-1; AGENTS.md "the live descriptor is a transitional path until wave 3"; REQ-20261103-043 wave 3, owner decision 2026-11-18 "1A"） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/66-retire-bridge-out/` / owner implementation seat / worktree `.worktrees/66-retire-bridge` / branch `cp/wave3-66-retire-bridge` / baseline the wave-3 branch after ticket 65 is integrated |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `INTEGRATED`（candidate `2d11118c` at `cded7a27`; CI run 44390034272 green; S66-01 and S66-03 to ticket 67） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/66-retire-bridge` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/66-retire-bridge-review` |
| 責任邊界 | removal of the cross-lifetime bridge from `library/`: the live CLI `dispatch`, `review`, `runner`, `wake-inbox` and `wake-capability` families and everything only they reach; their tests and registered-failure rows; the refusal-guidance entries of removed codes |
| 禁止修改 | the gate scripts, the installer chain, `contracts.py`, the governance documents (ticket 67), the SPEC and ADR archive (ticket 68), and the test files tickets 68, 70 and 72 change in parallel (a needed change there is a `CHANGE_DETECTED` return) |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/workflow_router/
modify = library/local_orchestration/
modify = tests/
modify = ci/registered-failures.json
modify = ci/README.md
modify = requirements-dev.txt
delete = library/local_orchestration/antigravity_wake_command.py
delete = library/local_orchestration/claude_wake_command.py
delete = library/local_orchestration/codex_thread_dispatch.py
delete = library/local_orchestration/codex_thread_host_binding.py
delete = library/local_orchestration/command_role_wake_port.py
delete = library/local_orchestration/commit_trigger_intake.py
delete = library/local_orchestration/deadline_capability.py
delete = library/local_orchestration/dispatch_authority.py
delete = library/local_orchestration/dispatch_cli.py
delete = library/local_orchestration/dispatch_session.py
delete = library/local_orchestration/event_runner.py
delete = library/local_orchestration/event_runner_main.py
delete = library/local_orchestration/executor_routing.py
delete = library/local_orchestration/file_lock.py
delete = library/local_orchestration/git_handoff_event_adapter.py
delete = library/local_orchestration/issuance_scoped_boundary.py
delete = library/local_orchestration/live_dispatch_metadata_boundary.py
delete = library/local_orchestration/live_dispatch_metadata_store.py
delete = library/local_orchestration/one_shot_deadline.py
delete = library/local_orchestration/project_runner_registry.py
delete = library/local_orchestration/project_subscription_runtime.py
delete = library/local_orchestration/receipt_bound_supervision.py
delete = library/local_orchestration/review_cli.py
delete = library/local_orchestration/review_return.py
delete = library/local_orchestration/review_return_boundary.py
delete = library/local_orchestration/review_return_consumption.py
delete = library/local_orchestration/role_wake_composition.py
delete = library/local_orchestration/runner_cli.py
delete = library/local_orchestration/runner_lifecycle_port.py
delete = library/local_orchestration/runner_receipt_seeding.py
delete = library/local_orchestration/senior_review_inbox.py
delete = library/local_orchestration/senior_review_inbox_state.py
delete = library/local_orchestration/subscription_builder.py
delete = library/local_orchestration/wake_candidate_inbox.py
delete = library/local_orchestration/wake_capability.py
delete = library/local_orchestration/wake_scoped_boundary.py
delete = library/local_orchestration/windows_native_git_ref.py
delete = library/local_orchestration/windows_senior_review_inbox_store.py
delete = library/local_orchestration/windows_supervision_composition.py
delete = library/local_orchestration/work_queue.py
delete = library/local_orchestration/worker_assignment.py
delete = library/local_orchestration/worktree_containment.py
delete = library/workflow_router/deadline_contracts.py
delete = library/workflow_router/execution_replacement.py
delete = library/workflow_router/git_handoff_contracts.py
delete = library/workflow_router/live_dispatch_contracts.py
delete = library/workflow_router/review_inbox_contracts.py
delete = library/workflow_router/role_wake_contracts.py
delete = library/workflow_router/supervision_policy.py
delete = library/workflow_router/supervision_runtime_contracts.py
delete = library/workflow_router/thread_dispatch_contracts.py
delete = library/workflow_router/thread_host_contracts.py
delete = tests/test_antigravity_wake_command.py
delete = tests/test_claude_wake_command.py
delete = tests/test_codex_thread_dispatch.py
delete = tests/test_codex_thread_host_binding.py
delete = tests/test_commit_trigger_intake.py
delete = tests/test_dispatch_authority.py
delete = tests/test_dispatch_session.py
delete = tests/test_event_runner_cli.py
delete = tests/test_event_runner_qualification.py
delete = tests/test_execution_replacement.py
delete = tests/test_executor_routing.py
delete = tests/test_file_lock.py
delete = tests/test_git_handoff_event_adapter.py
delete = tests/test_live_dispatch_metadata_boundary.py
delete = tests/test_live_dispatch_metadata_store.py
delete = tests/test_one_shot_deadline.py
delete = tests/test_parallel_worker_dispatch.py
delete = tests/test_plugin_distribution_git_subscription.py
delete = tests/test_plugin_distribution_runner_registry.py
delete = tests/test_receipt_bound_supervision.py
delete = tests/test_ref_watch_capability.py
delete = tests/test_review_return.py
delete = tests/test_review_return_concurrency.py
delete = tests/test_review_return_consumption.py
delete = tests/test_role_wake_composition.py
delete = tests/test_runner_receipt_seeding.py
delete = tests/test_senior_review_inbox.py
delete = tests/test_single_handoff_review_submission.py
delete = tests/test_subscription_builder.py
delete = tests/test_supervision_policy.py
delete = tests/test_wake_delivery.py
delete = tests/test_whole_chain_qualification.py
delete = tests/test_windows_native_git_ref_notification.py
delete = tests/test_work_queue.py
delete = tests/test_worker_assignment.py
delete = tests/test_worktree_containment.py
forbid = library/workflow_router/contracts.py
forbid = library/local_orchestration/bootstrap_install.py
forbid = library/local_orchestration/johnny_live_install.py
forbid = library/local_orchestration/plugin_install_transaction.py
forbid = library/local_orchestration/plugin_uninstall_transaction.py
forbid = library/local_orchestration/runtime_dependency_lock.py
forbid = tests/test_governance_consistency.py
forbid = tests/test_plugin_payload_boundary.py
forbid = tests/test_state_file_templates.py
forbid = tests/test_gate_dispatch_lint.py
forbid = tests/test_wave2_end_to_end.py
forbid = skills/
forbid = Workflow.md
forbid = AGENTS.md
forbid = CodeReview.md
forbid = template/
forbid = modules/spec/
forbid = doc/adr/
forbid = .claude-plugin/
forbid = .codex-plugin/
```

## 使用者拍板與可觀察結果

On 2026-11-18 the owner decided "1A" (REQ-20261103-043, wave 3): retire the router library in full, including the whole cross-lifetime bridge, and keep `contracts.py` (the receipt vocabulary), the installer chain, and `status` and `uninstall`. Ticket 65 removed the flow engine, the private router, the profile and the router telemetry. This ticket removes the bridge.

The delete list was computed on 2026-11-18 from the import graph of `library/`, with the package `__init__` files left out:

- **Starting points:** the live-CLI families `dispatch_cli`, `review_cli` and `runner_cli`, the event runner entry, and the two host wake commands.
- **What is removed:** every module those reach, unless a kept module also reaches it.
- **Kept modules:**
  - the installer chain, `status` and `uninstall`;
  - the publication modules;
  - the Codex and Antigravity skill registration;
  - the fake install lifecycle of tickets 01 and 02;
  - ticket status, refusal guidance, the document mutation gate and the control-plane mutation door;
  - the target-document modules, and through them `role_supervision_contracts.py`;
  - project authority;
  - the artifact-tree, library-selection, managed-artifact, requirement-lineage, test-engineer and UI co-design contracts.
- **`executor_routing.py`** is removed with the bridge. Its SPEC, `modules/spec/executor-routing.md`, is one of the seven the owner archives (decision 3), and no kept module imports it.

When this ticket is done:

- **The live CLI** (`johnny_live_cli.py`) keeps `status` and `uninstall` exactly as they are. `dispatch`, `review`, `runner`, `wake-inbox` and `wake-capability` answer like any other unknown command: one JSON line with the code `UNKNOWN_COMMAND` and exit 3. A test asserts this for each of the five.
- **Removed files:** every file of the delete list, and no other. A module or test outside the list that would need deleting is a `CHANGE_DETECTED` return naming it.
- **Package imports:** `library/workflow_router/__init__.py` and `library/local_orchestration/__init__.py` no longer import or export a removed name, and importing either package loads no removed module.
- **Refusal guidance:** `refusal_guidance.py` drops each entry whose code only a removed module raised. `tests/test_refusal_guidance.py` follows, and its counts change with it.
- **Tests that also test kept code** change only where they named removed code. Each change is named in the STATEMENT. The two known so far are:
  - `tests/test_document_mutation_gate.py`, which builds its fixture with `dispatch_authority`;
  - `tests/test_review_correction_regressions.py`, which mixes installer cases with bridge cases. The installer cases stay.
- **Registered failures:** every row of a deleted test leaves `ci/registered-failures.json` in the same commit as the deletion, and `ci/README.md` follows.
- **Dev dependencies:** `requirements-dev.txt` drops `pywin32` and `types-pywin32` only if no remaining module or test imports `win32*`. Either way the STATEMENT names the importer, or says there is none.
- **The runtime dependency lock** of the installer is not changed. The STATEMENT lists every lock entry that only removed code used, as a follow-up for publication 0.5.
- **`contracts.py`** is unchanged. The STATEMENT lists every type in it that no remaining module or test uses, as a follow-up.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/66-retire-bridge`.
- reviewer：`ticket-review` seat in `.worktrees/66-retire-bridge-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; REQ-20261103-043 owner decision 2026-11-18; ticket 65 and its review record.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：library and test removal; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：`contracts.py` and the `status` and `uninstall` output unchanged.

## TDD 設計

1. 正常行為：
   - `status` and `uninstall` behave exactly as before, and the installer tests (`test_one_click_installer`, `test_live_install_*`, `test_refusal_guidance`) pass.
   - Importing both packages succeeds.
2. 規則違反／輸入錯誤：
   - each of the five removed CLI families gives `UNKNOWN_COMMAND` with exit 3;
   - a test asserts that no removed module is importable and that no removed name appears in either package's `__all__`.
3. 外部失敗／fail-closed：the uninstall and install refusal codes are unchanged.
4. 回歸保護：the full suite has no new red. The registered-failure list loses exactly the rows of deleted tests, and the CI jobs on both systems stay green.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule changes |
| 2 | null／空字串／陣列 | 是 | the live CLI with no argument still means `status` |
| 3 | 權限繞過 | 是 | a removed family cannot be reached under another spelling: each case variant and each prefix is `UNKNOWN_COMMAND` |
| 4 | Token 格式與比較 | 否 | no tokens |
| 5 | 錯誤碼是否一致 | 是 | `UNKNOWN_COMMAND` exit 3, as before for any unknown command |
| 6 | 例外是否會拋出 | 是 | importing a removed module raises `ModuleNotFoundError` |

## 完成定義與證據

- The full suite passes on the host under the host lock: its failure set is a subset of the base names, with zero new red.
- `mypy --strict --python-version 3.11` passes on `johnny_live_cli.py`, `refusal_guidance.py`, both package `__init__` files and every changed test. No `Any`.
- **反向突變證據**: each of these turns a named test red, then is restored.
  - Route `runner` back to its family.
  - Re-add a removed name to `__all__`.
  - Re-import a removed module in a package `__init__`.
  - Drop the `UNKNOWN_COMMAND` exit code to 0.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing `receipt_check.py` (P9) and `evidence_gate.py` (E1, run last). The STATEMENT lists every deleted file, every changed assertion, every registered row removed, every dependency dropped or kept, the unused lock entries and the unused `contracts.py` types.

## 正式環境移植 SOP

- 不適用：plugin library code. The installed runtime changes only at publication 0.5.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Control-plane note before review (2026-11-19)

The ticket says unknown commands exit 3 "as before". That is a factual error of the ticket (lesson L-8): at the base `run_live_cli` returned **2** for an unknown command. The seat made every unknown command exit 3, as the ticket asked, and named the change.
The control plane keeps exit 3. It is the usage-error code of R4-2, it matches the `CAPABILITY_UNAVAILABLE` exit 3 of `status` and of the runtime entry, and no file in the repository reads the old value 2. This note is the authority for that one behaviour change; every other statement of revision01 stands.

Prose outside the boundary that still names deleted files (for ticket 67): `.agents/plugins/johnny-ai-skill/rules/worktree-containment.md` line 9 (`worktree_containment.py`); `library/功能集群/python/exclusive_file_lock/README.md` (`file_lock.py`, `tests/test_file_lock.py` as contract source and evidence).
