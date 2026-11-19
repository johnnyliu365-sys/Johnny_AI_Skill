# 67｜Router library retirement (4): the governance documents name no retired surface, and the file lock returns to the module library

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-1; REQ-20261103-043 wave 3, owner decision 2026-11-18 "1A 2A 3A 4A", owner decision 2026-11-19 "A" on `exclusive-file-lock`） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/67-doc-sweep-out/` / owner implementation seat / worktree `.worktrees/67-doc-sweep` / branch `cp/wave3-67-doc-sweep` / baseline the wave-3 branch named in the dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language）for the module, the tests and the sweep pattern; the documents stay in their current language |
| 狀態 | `PLANNED`（strict tier: an independent rule-only review of this ticket precedes dispatch） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/67-doc-sweep` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/67-doc-sweep-review` |
| 責任邊界 | the routed governance documents, the plugin README and command, the module catalog and library READMEs, the consistency sweep test, the restored file lock and its test |
| 禁止修改 | the gate scripts, `library/workflow_router/*.py`, `library/local_orchestration/`, the SPEC archive, the review records, the ticket set other than this ticket's own completion rows |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = AGENTS.md
modify = Workflow.md
modify = CodeReview.md
modify = README.md
modify = commands/johnny-project-takeover.md
modify = .agents/plugins/johnny-ai-skill/rules/worktree-containment.md
modify = skills/johnny-project-takeover/SKILL.md
modify = skills/johnny-project-takeover/references/
modify = template/README.md
modify = doc/runbooks/dispatch-model-profile.md
modify = doc/adr/ADR-20260824-019-provider-usage-telemetry-evidence.md
modify = modules/spec/workflow-governance.md
modify = library/MODULE_CATALOG.md
modify = library/catalog/workflow-control/README.md
modify = library/catalog/capabilities/README.md
modify = library/workflow_router/README.md
modify = library/功能集群/python/exclusive_file_lock/README.md
modify = tests/test_governance_consistency.py
modify = tests/test_adversarial_review_policy.py
modify = tests/test_antigravity_registration.py
create = library/功能集群/python/exclusive_file_lock/__init__.py
create = library/功能集群/python/exclusive_file_lock/file_lock.py
create = tests/test_exclusive_file_lock.py
delete = doc/runbooks/e7_owner_smoke.py
forbid = library/local_orchestration/
forbid = skills/johnny-project-takeover/scripts/
forbid = doc/archive/
forbid = doc/reviews/
forbid = ci/registered-failures.json
```

## 使用者拍板與可觀察結果

**The problem.** Tickets 65 and 66 removed the flow engine, the private router and the cross-lifetime bridge from `library/`. Ticket 68 archived their SPECs. The documents an agent reads at wake still describe them:

- `AGENTS.md` calls the live descriptor "a transitional path until wave 3".
- The skill's readiness check tells an agent to run `runner status` and `wake-capability probe`, which now answer as unknown commands.
- `router-control.md`, `implementation-authority.md`, `review-checks.md`, `model-role-routing.md`, `adversarial-review.md`, `codex-native-same-lifetime-delegation.md` and `context-routing.md` still name the bridge, the live descriptor or the retired CLI families.
- The dispatch runbook, the worktree rule for Antigravity and the plugin README name removed modules.
- `doc/runbooks/e7_owner_smoke.py` imports modules that no longer exist.
- The catalog card `workflow-router-poc` is `READY` for an engine that is gone.
- The catalog card `exclusive-file-lock` is `READY`, but its only source and test were deleted by ticket 66.

The consistency sweep does not catch any of this, because it exempts every sentence that says "transitional", "過渡", "until wave 3" or "bridge route". An agent that follows these documents runs a command that does not exist, or treats a retired path as an option. The owner decided the retirement on 2026-11-18 ("1A 2A 3A 4A") and on 2026-11-19 chose "A" for the file lock: restore it into the module library rather than retire the card.

After this ticket:

1. **No retired surface is named as live.** In the swept set below, no sentence names a retired surface as something to run, read, bind or choose. A sentence may name one only to state that it was retired. The retired surfaces are:
   - the flow engine and its frameworks: `RouterEngine`, `LangGraph`, `Temporal`, `profile.py`;
   - the router telemetry: `telemetry_cli`;
   - the bridge: the live descriptor, `PendingDispatchDescriptor`, the `runner` family, `event_runner`, `wake-inbox`, `wake-capability`, `dispatch_cli`, `review_cli`, `johnny_router_cli`;
   - removed modules named by path, such as `worktree_containment.py` and `library/local_orchestration/file_lock.py`.

   The bare word "Router" is not a retired surface: it names the workflow routing concept in `Workflow.md`, and stays. The launcher `johnny-router.ps1` with `status` and `uninstall` is not retired either.
2. **The swept set** is the routed set the sweep already reads, plus:
   - `README.md`;
   - `commands/`;
   - `.agents/`;
   - `library/catalog/`;
   - `library/MODULE_CATALOG.md`;
   - every `README.md` directly under a `library/` package or a `library/功能集群/<language>/<module>/` folder.

   Dated handover runbooks, live-verification records, ADRs marked `SUPERSEDED`, the SPEC archive and the review records are history, and stay out of the swept set.
3. **The sweep test enforces it.**
   - `tests/test_governance_consistency.py` gains one pattern, `RETIRED_SURFACE`, over the swept set. Its only exemption is a sentence that states the retirement, through `retired`, `退場` or `已移除`.
   - `BRIDGE_EXEMPT` loses `until (it retires|wave 3)`, `transitional`, `過渡` and `bridge (route|path)`.
   - Every sentence these exemptions used to hide is rewritten to state the rule without the bridge, or deleted when it only described the bridge.
4. **The governance SPEC keeps its approved text.** `modules/spec/workflow-governance.md` gains one status note under R4-1: the cross-lifetime live descriptor that R4-1 calls transitional was retired in wave 3 (tickets 65 and 66, REQ-20261103-043), and no dispatch route uses it. The SPEC is outside the `RETIRED_SURFACE` pattern. A test pins the note.
5. **Specific items:**
   - `AGENTS.md`: the live-descriptor sentence of the state paragraph is removed, and the paragraph states only the ticket state row and the merge queue.
   - `SKILL.md`: the readiness check no longer calls `runner status` or `wake-capability probe`. It states that no runner exists and that a wake happens only through the host's own session start or resume.
   - `doc/runbooks/dispatch-model-profile.md`: the removed modules and CLI families named in it are replaced by what the control plane does now, or deleted.
   - `doc/runbooks/e7_owner_smoke.py` is deleted. It exercised the runner, and nothing it imports exists.
   - `.agents/plugins/johnny-ai-skill/rules/worktree-containment.md`: the sentence naming `worktree_containment.py` is replaced by the containment predicate that exists, `library/local_orchestration/path_containment.py` `resolves_within_root`, or removed. `tests/test_antigravity_registration.py` changes only if its assertion on this file breaks.
   - `doc/adr/ADR-20260824-019-provider-usage-telemetry-evidence.md`: the link to `modules/spec/context-load-telemetry.md` points to `doc/archive/specs/2026/context-load-telemetry.md`.
   - `library/catalog/workflow-control/README.md`: the row `workflow-router-poc` is removed. `library/workflow_router/README.md` already describes the contracts that stay. `library/MODULE_CATALOG.md` changes only if it names the card.
   - `tests/test_adversarial_review_policy.py`: an assertion that requires a retired term (today `live descriptor`) is replaced by one on the rule that replaced it. The STATEMENT names each changed assertion.
6. **`exclusive-file-lock` is restored, card `READY`.**
   - `library/功能集群/python/exclusive_file_lock/file_lock.py` is `library/local_orchestration/file_lock.py` as of `c9af7725^`. The only allowed changes are the module docstring's references to deleted modules.
   - `__init__.py` exports `ExclusiveFileLock`, `ExclusiveWindowsFileLock` and `FileLockAcquireDecision`.
   - `tests/test_exclusive_file_lock.py` is `tests/test_file_lock.py` as of `c9af7725^`, with these changes and no others:
     - imports from the new path, including the child-process scripts;
     - `NamingTests.test_every_consumer_holds_that_same_object` is removed, because every consumer it lists was retired;
     - `DocumentationTests` reads the card only; the element README of ticket 08 is a historical record;
     - the docstring no longer names deleted test files.
   - The card names the new public import, the new contract source and the new test. Its behaviour and strict evidence rows are refreshed from this ticket's run. `library/catalog/capabilities/README.md` keeps the card `READY`.
   - `library.local_orchestration.file_lock` stays absent; `tests/test_wayfinder_gap.py` already asserts that.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/67-doc-sweep`.
- reviewer：`ticket-review` seat in `.worktrees/67-doc-sweep-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; the files of the boundary block.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。A retired surface in a file outside the boundary, or a sentence whose rewrite would change a rule rather than remove a retired path, is a `CHANGE_DETECTED` return naming the file and line.

### 前端組合與依賴注入

**N/A reason**：documents, a test and a standard-library module; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：`ExclusiveFileLock`, `ExclusiveWindowsFileLock`, `FileLockAcquireDecision` at `library.功能集群.python.exclusive_file_lock`, unchanged in behaviour.

### Observation on the base (control plane, `5d407dce`)

Files of the swept set with at least one mention of a retired surface or of a removed exemption phrase (`cross-lifetime`, `until wave 3`, `過渡`, `bridge route`), before this ticket:

- `skills/johnny-project-takeover/references/router-control.md` (10);
- `skills/johnny-project-takeover/SKILL.md` (6);
- `skills/johnny-project-takeover/references/implementation-authority.md` (5);
- `doc/runbooks/dispatch-model-profile.md` (5);
- `review-checks.md`, `model-role-routing.md`, `adversarial-review.md` (3 each);
- `codex-native-same-lifetime-delegation.md`, `modules/spec/workflow-governance.md`, the ADR-019 link (2 each);
- `context-routing.md`, `library/workflow_router/README.md`, `Workflow.md`, `README.md`, `AGENTS.md`, `worktree-containment.md` (1 each).

The new pattern's first red run on the base is the authoritative list; the STATEMENT reports it.

## TDD 設計

1. 正常行為:
   - on the result, `RETIRED_SURFACE` reports no hit;
   - every existing sweep test stays green;
   - `tests/test_exclusive_file_lock.py` passes on Windows with the same test and subtest counts as the old file, less the removed test.
2. 規則違反／輸入錯誤: these injections into a copy of the swept set each turn `RETIRED_SURFACE` red:
   - `runner status` in `SKILL.md`;
   - "the live descriptor remains a transitional option" in `AGENTS.md`;
   - `PendingDispatchDescriptor` in `router-control.md`;
   - `wake-capability probe` in `README.md`;
   - `RouterEngine` in a `library/` README.

   These each stay green:
   - "Router" alone;
   - `johnny-router.ps1 status`;
   - a sentence stating that the bridge was retired.
3. 外部失敗／fail-closed:
   - a file of the swept set that is missing or not UTF-8 stays a test failure, as today;
   - the lock's existing fail-closed cells (an empty path, a failed acquisition retains no handle) pass at the new path.
4. 回歸保護:
   - the four removed `BRIDGE_EXEMPT` entries leave no sentence that a remaining pattern now reports;
   - `tests/test_wayfinder_gap.py` still finds `library.local_orchestration.file_lock` absent.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | the swept set: `library/catalog/` versus a file `library/catalog.md`; a `README.md` one folder deeper than a module folder is not in the set; the old and new lock module paths are distinct |
| 2 | null／空字串／陣列 | 是 | an empty swept file has no hit; the lock's empty-path cell |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | `Temporal` matches case-sensitively and only as a word; `runner` matches only as a CLI family (`runner status`, `runner start`), not the English word "runner" in prose; `johnny-router.ps1 status` does not match |
| 5 | 錯誤碼是否一致 | 否 | no exit codes change |
| 6 | 例外是否會拋出 | 是 | the lock's release-primitive error cell passes at the new path |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_governance_consistency.py tests/test_adversarial_review_policy.py tests/test_antigravity_registration.py tests/test_exclusive_file_lock.py tests/test_wayfinder_gap.py -q` exits 0.
  - `mypy --strict --python-version 3.11` on the lock module, its test and the sweep test exits 0.
- **反向突變證據**, each restored after it turns a named test red:
  - drop `RETIRED_SURFACE` from the patterns;
  - put `transitional` back into `BRIDGE_EXEMPT`;
  - remove `commands/` from the swept set;
  - remove the SPEC status note.
- **Lock evidence**: the restored module and the old one differ only in the docstring. A `git diff --no-index` of the two is attached; the test diff is attached too.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last), and the typed return in STATEMENT.

## 正式環境移植 SOP

- 不適用：plugin documents and a library module.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
