# 65｜Router library retirement (1): the flow engine, the private router, the profile and the router telemetry

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-1, R4-5; Workflow.md section 0; REQ-20261103-043 wave 3, owner decision 2026-11-18 "1A 2A"） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision02 / receipt under `.worktrees/65-retire-engine-and-private-router-out/` / owner implementation seat / worktree `.worktrees/65-retire-engine-and-private-router` / branch `cp/wave3-65-retire-engine` / baseline the wave-3 branch at dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language） |
| 狀態 | `INTEGRATED`; dispatch=sha256:3ed40d8062d899a554bb5135575d81782161e4a63236a90c7137647412baf94f (`doc/handoffs/2026/workflow-governance/dispatch/JAS-65.yaml`)（candidate `b185dea9` at `361ba136`; CI run 44342660977 green on `9b746c97`; S65-03, S65-06 carried） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/65-retire-engine-and-private-router` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/65-retire-engine-and-private-router-review` |
| 責任邊界 | removal of the router engine, private router, profile, router telemetry and router preflight CLI from `library/`, their tests and registered-failure rows; one new module for the Wayfinder gap rule |
| 禁止修改 | the gate scripts, the cross-lifetime bridge (ticket 66), the governance documents (ticket 67), the SPEC and ADR archive (ticket 68) |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = library/workflow_router/
modify = library/local_orchestration/
modify = tests/
modify = ci/registered-failures.json
modify = ci/README.md
modify = requirements-dev.txt
create = library/workflow_router/wayfinder_gap.py
create = tests/test_wayfinder_gap.py
delete = library/workflow_router/graph.py
delete = library/workflow_router/router.py
delete = library/workflow_router/temporal_runtime.py
delete = library/workflow_router/integrations.py
delete = library/workflow_router/collaboration.py
delete = library/workflow_router/guarded_integration.py
delete = library/workflow_router/private_router.py
delete = library/workflow_router/policy_response.py
delete = library/workflow_router/telemetry_provisioning_contracts.py
delete = library/workflow_router/review_admission.py
delete = library/workflow_router/profile.py
delete = library/workflow_router/telemetry.py
delete = library/workflow_router/telemetry_cli.py
delete = library/workflow_router/context_load_report.py
delete = library/workflow_router/model_role_readiness.py
delete = library/local_orchestration/johnny_router_cli.py
delete = library/local_orchestration/johnny_router_composition.py
delete = library/local_orchestration/telemetry_storage/__init__.py
delete = library/local_orchestration/telemetry_storage/composition.py
delete = library/local_orchestration/telemetry_storage/contracts.py
delete = library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
delete = library/local_orchestration/telemetry_storage/local_lock_adapter.py
delete = library/local_orchestration/telemetry_storage/ownership_ledger.py
delete = tests/test_workflow_router.py
delete = tests/test_private_router_metadata_gate.py
delete = tests/test_plugin_policy_and_response.py
delete = tests/test_autonomous_collaboration.py
delete = tests/test_guarded_integration_audit.py
delete = tests/test_guarded_integration_corrections.py
delete = tests/test_telemetry_provisioning_contracts.py
delete = tests/test_review_admission.py
delete = tests/test_router_review_admission.py
delete = tests/test_context_load_report.py
delete = tests/test_workflow_model_role_readiness.py
delete = tests/test_plugin_distribution_profile.py
delete = tests/test_plugin_distribution_router_composition.py
delete = tests/test_plugin_distribution_cli.py
delete = tests/test_plugin_distribution_vita_qualification.py
delete = tests/test_wayfinder_info_gap.py
delete = tests/test_johnny_owned_telemetry_storage_adapter.py
delete = tests/test_plugin_distribution_telemetry_report.py
delete = tests/test_telemetry_ownership_ledger.py
delete = tests/test_telemetry_storage_composition.py
delete = tests/test_telemetry_storage_contracts.py
delete = tests/test_telemetry_storage_lock_adapter.py
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

On 2026-11-18 the owner decided "1A 2A" (REQ-20261103-043, wave 3): retire the router library in full, and keep the Wayfinder two-round information-gap rule as a small executable function. This ticket is the first of the retirement tickets. Ticket 66 retires the cross-lifetime bridge, ticket 67 sweeps the governance documents, and ticket 68 archives the router-era SPECs and ADRs.

When this ticket is done:

- **Removed:**
  - the LangGraph adapter, the RouterEngine, the Temporal and Agents/MCP skeletons, collaboration topology and guarded integration;
  - the private router with its policy response, telemetry provisioning and review admission;
  - `profile.py` with its transition table and its seven reference-digest pins;
  - the router baseline telemetry (`telemetry.py`, `telemetry_cli.py`, `context_load_report.py`, `model_role_readiness.py`) and the local telemetry storage;
  - the router preflight CLI (`johnny_router_cli.py`, `johnny_router_composition.py`);
  - every test of these, and the registered-failure rows that name them.
- **Kept:**
  - `library/workflow_router/contracts.py`, the receipt vocabulary R4-1 and R4-5 name;
  - every module the cross-lifetime bridge still imports, because ticket 66 removes those;
  - `library/local_orchestration/johnny_router_contracts.py`, because the installer imports `PreflightProbe`;
  - the installer chain, `status` and `uninstall`.
- **The Wayfinder gap rule** moves into `library/workflow_router/wayfinder_gap.py`, a standalone function over the types in `contracts.py`. Its test, `tests/test_wayfinder_gap.py`, carries over every case that `tests/test_wayfinder_info_gap.py` pinned through the RouterEngine: the two-round limit, the blocking gap, the human-wait return, and anything else that file asserts.
- **Package imports:** `library/workflow_router/__init__.py` and `library/local_orchestration/__init__.py` no longer import or export any removed name, and importing either package loads no removed module. `__all__` lists only names that exist.
- **Dev dependencies:** `requirements-dev.txt` drops `langgraph`, `temporalio`, `openai-agents` and `mcp`, unless a remaining module or test still imports one. If one is still needed, the STATEMENT names it.
- **Payload:** the payload declarations and their tests keep passing. `tests/test_plugin_payload_boundary.py` still requires `contracts.py`. The lazy-graph assertion in `tests/test_plugin_distribution_payload_manifest.py` is removed, together with every other assertion about removed names.
- **Tests that pin router files from outside** change only where they named a removed file, and each change is named in the STATEMENT. These are `tests/test_adversarial_review_policy.py`, which reads `profile.py` and `test_workflow_router.py` for a digest, and the governance-consistency fixtures.

A module or test outside the delete list that turns out to depend only on removed code, and so would need deleting too, is a `CHANGE_DETECTED` return naming the file. It is not deleted by this ticket.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/65-retire-engine-and-private-router`.
- reviewer：`ticket-review` seat in `.worktrees/65-retire-engine-and-private-router-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; REQ-20261103-043 owner decision 2026-11-18; the wave-3 inventory summarised in the review record of this ticket when it is written.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：library and test removal; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：`contracts.py` unchanged. `wayfinder_gap.py` gets a typed function signature stated in its docstring.

## TDD 設計

1. 正常行為：
   - `tests/test_wayfinder_gap.py` passes, and covers every case of the deleted `test_wayfinder_info_gap.py`.
   - Every remaining test passes.
   - Importing `library.workflow_router` and `library.local_orchestration` succeeds.
2. 規則違反／輸入錯誤：
   - The Wayfinder function refuses a third round.
   - A test asserts that no removed module name is importable, and that no removed name appears in either package's `__all__`.
3. 外部失敗／fail-closed：the installer tests (`test_one_click_installer`, `test_live_install_*`, `test_refusal_guidance`) pass unchanged, apart from rows that named a removed module, each named.
4. 回歸保護：the full suite has no new red. The registered-failure list loses exactly the rows of deleted tests, and the CI jobs on both systems stay green.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule changes |
| 2 | null／空字串／陣列 | 是 | the Wayfinder function with no gaps and with an empty round list |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 否 | no tokens |
| 5 | 錯誤碼是否一致 | 是 | the installer's refusal codes unchanged |
| 6 | 例外是否會拋出 | 是 | importing a removed module raises `ModuleNotFoundError` |

## 完成定義與證據

- The full suite passes on the host under the host lock: its failure set is a subset of the base names, with zero new red.
- `mypy --strict --python-version 3.11` passes on `wayfinder_gap.py` and its test. Stdlib and the existing dependencies only. No `Any`.
- **反向突變證據**: each of these turns a named test red, then is restored.
  - Allow a third round in the Wayfinder function.
  - Re-add a removed name to `__all__`.
  - Re-import a removed module in a package `__init__`.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing `receipt_check.py` (P9) and `evidence_gate.py` (E1, run last). The STATEMENT names every changed assertion, every registered row removed, and every dependency dropped or kept.

## 正式環境移植 SOP

- 不適用：plugin library code. The publication payload changes only at publication 0.5.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用

## Revision02 (2026-11-18, after `CHANGE_DETECTED`)

The implementation seat stopped before committing. `library/local_orchestration/control_plane_mutation.py` is outside the delete list, and its repin rule (`_repin_failure`, refusal `POLICY_REPIN_STALE`) reads `library/workflow_router/profile.py` and `tests/test_workflow_router.py` at the candidate. The rule makes sure an edit to a digest-pinned policy document lands together with its pins in both files.

The owner decision of 2026-11-18 retires `profile.py`, including its seven reference-digest pins. After this ticket no pin exists, so the rule has nothing left to govern, and it would refuse every control-plane change to a pinned document as "unreadable at the candidate". Giving it a new pin source would be a new requirement, and no owner decision asks for one. The rule is therefore retired together with the pins.

Added to this ticket, inside the existing boundary (`library/local_orchestration/` and `tests/`):

- **`control_plane_mutation.py`:**
  - drops the repin step from `admit_control_plane_mutation`;
  - drops `_repin_failure`, `policy_pins`, `policy_digest` and `policy_document_id`, with the constants and the pattern that only they use;
  - drops the enum member `POLICY_REPIN_STALE`.
  - Every other step of the module is unchanged: the control-plane namespace, the mixed rule-and-subject refusal, content modes, the journal and the rest.
- **`refusal_guidance.py`** drops the `POLICY_REPIN_STALE` entry.
- **`tests/test_control_plane_mutation.py`** drops `PolicyPinTests` and every test that expects `POLICY_REPIN_STALE`. Every other test of the file passes unchanged.
- **`tests/test_refusal_guidance.py`** drops the two `POLICY_REPIN_STALE` rows, and its counts follow.
- **The STATEMENT** names each dropped test and the reason, which is that the pin source was retired by the owner decision of 2026-11-18.
- **One added reverse mutation** turns a named test red and is then restored: re-add `POLICY_REPIN_STALE` to the enum. The guard that turns red is a test asserting that the member is gone, in `tests/test_control_plane_mutation.py`.
