# 67｜Router library retirement (4): the governance documents name no retired surface, and the file lock returns to the module library

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04 R4-1; REQ-20261103-043 wave 3, owner decision 2026-11-18 "1A 2A 3A 4A", owner decision 2026-11-19 "A" on `exclusive-file-lock`） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision04 / receipt under `.worktrees/67-doc-sweep-out/` / owner implementation seat / worktree `.worktrees/67-doc-sweep` / branch `cp/wave3-67-doc-sweep` / baseline the wave-3 branch named in the dispatch |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language）for the module, the tests and the sweep pattern; the documents stay in their current language |
| 狀態 | `IN_PROGRESS`; dispatch=sha256:89db4177c8495a709372b60fdc9cb820133acedd4d0085a961272963d624cc77 (`doc/handoffs/2026/workflow-governance/dispatch/JAS-67.yaml`)（revision04; strict tier; rule-only reviews: revision01 and revision02 CHANGES_REQUESTED, revision03 APPROVED; revision04 keeps the launcher rules of S67R-24） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/67-doc-sweep` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/67-doc-sweep-review` |
| 責任邊界 | the routed governance documents, the plugin README and command, the module catalog and library READMEs, the consistency sweep test, the restored file lock and its test |
| 禁止修改 | the gate scripts, `library/workflow_router/*.py`, `library/local_orchestration/`, the SPEC archive, the review records, the ticket set (the control plane writes this ticket's completion rows) |
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
modify = library/catalog/capabilities/README.md
modify = library/workflow_router/README.md
modify = library/功能集群/python/exclusive_file_lock/README.md
modify = library/功能集群/python/path_containment/README.md
modify = tests/test_governance_consistency.py
modify = tests/test_adversarial_review_policy.py
modify = tests/test_antigravity_registration.py
modify = tests/test_plugin_publication.py
modify = tests/test_plugin_payload_boundary.py
create = library/功能集群/python/exclusive_file_lock/__init__.py
create = library/功能集群/python/exclusive_file_lock/file_lock.py
create = tests/test_exclusive_file_lock.py
delete = doc/runbooks/e7_owner_smoke.py
delete = library/catalog/workflow-control/README.md
forbid = library/local_orchestration/
forbid = skills/johnny-project-takeover/scripts/
forbid = doc/archive/
forbid = doc/reviews/
forbid = ci/registered-failures.json
```

## 使用者拍板與可觀察結果

Process tier: strict.

**The problem.** Tickets 65 and 66 removed the flow engine, the private router and the cross-lifetime bridge from `library/`. Ticket 68 archived their SPECs. The documents an agent reads at wake still describe them:

- `AGENTS.md` calls the live descriptor a transitional path until wave 3.
- The skill's readiness check tells an agent to run `runner status` and `wake-capability probe`. Both now answer as unknown commands.
- The skill references, the dispatch runbook, the worktree rule for Antigravity, the plugin README, the command and the template README still name the bridge, the pending descriptor, the private router or the retired CLI families.
- `doc/runbooks/e7_owner_smoke.py` imports four modules that no longer exist.
- The catalog card `workflow-router-poc` is `READY` for an engine that is gone.
- The card `exclusive-file-lock` is `READY`, but its only source and test were deleted by ticket 66.
- The card `path-containment` cites a regression suite that ticket 66 deleted.

The consistency sweep catches none of this, because it exempts every sentence that says "transitional", "過渡", "until wave 3" or "bridge route". An agent that follows these documents runs a command that does not exist, or treats a retired path as an option.

The owner decided the retirement on 2026-11-18 ("1A 2A 3A 4A"). On 2026-11-19 the owner chose "A" for the file lock: restore it into the module library rather than retire the card.

**Revision02** answers the rule-only review of revision01, and **revision03** the correction review of revision02 (`doc/reviews/workflow-governance/67-governance-document-sweep-ticket-review.md`). It names the swept set, the term list and the exemption exactly, and requires deletion rather than new text wherever a retired sentence has no replacement.

After this ticket:

1. **`RETIRED_SURFACE`, a closed term list.** `tests/test_governance_consistency.py` gains a check `RETIRED_SURFACE`. It is a separate check, not a row of `PATTERNS`, so it never reads historical files, and `EXPECTED_TOLERATED` does not change. It reports a sentence of the swept set, using the same units and `sentence_of` as `PATTERNS`, that matches any of these regexes:

   ```text
   RouterEngine   LangGraph   \bTemporal\b   profile\.py   telemetry_cli   TelemetryStorageLockPort
   Private Router   pending descriptor   live[- ]descriptor   PendingDispatchDescriptor
   \brunner (start|stop|status|subscribe)\b   runner-subscriptions   event_runner
   \b(armed|unarmed) (runner|wake)\b   wake-inbox   wake-capability
   dispatch_cli   review_cli   johnny_router_cli   worktree_containment\.py   local_orchestration/file_lock
   ```

   - Matching is case-sensitive.
   - The bare word "Router" is not on the list, and neither is `johnny-router.ps1` with `status` or `uninstall`. Both stay.
   - The only exemption is a sentence stating a completed retirement. A sentence counts when it matches `\b(was|were) retired\b`, `\bretired (in|by)\b`, `已退場` or `已移除`. It does not count when it also holds `退場前`, `until` or `before`.
2. **The swept set of `RETIRED_SURFACE`.** It reads the existing `ROUTED_ROOTS`, minus `modules/spec/workflow-governance.md`, plus:
   - `README.md`;
   - `commands/`;
   - `.agents/`;
   - `library/catalog/`;
   - `library/MODULE_CATALOG.md`;
   - the glob `library/*/README.md`;
   - the glob `library/功能集群/*/*/README.md`.

   The existing patterns keep their current roots.

   Out of the set, as history: dated handover runbooks, live-verification records, ADRs marked `SUPERSEDED`, the SPEC archive and the review records. `library/local_orchestration/README.md` is in the set; it is clean today, and a hit there is a `CHANGE_DETECTED` return.
3. **Exemptions removed.**
   - `BRIDGE_EXEMPT` loses `until (it retires|wave 3)`, `transitional`, `過渡` and `bridge (route|path)`.
   - Pattern d's own exemptions lose `過渡`, `退場` and `僅限過渡`.
   - Pattern e's own exemptions lose `live descriptor 是` and `僅限`.
   - Every sentence these used to hide, inside the boundary, is deleted, or rewritten as in item 5.
   - If removing an entry turns a file outside the boundary red, the seat keeps that one entry and names the entry and the file in the STATEMENT. The one exception is the SPEC (item 4).
4. **The governance SPEC keeps its approved text.**
   - `modules/spec/workflow-governance.md` gains one status note directly under the R4-1 heading: "Status (wave 3): the cross-lifetime live descriptor that R4-1 keeps as a transitional path was retired in wave 3 (tickets 65 and 66, REQ-20261103-043); no dispatch route uses it."
   - The R4-1 sentence that holds "transitional path until wave 3" stays verbatim.
   - A constant `SPEC_R41_FROZEN` holds that phrase. The sweep honours it only in `modules/spec/workflow-governance.md`, and only while the status note is present.
5. **Specific items.** Deletion is the default. New text is allowed only where it is given here.
   - `AGENTS.md`: delete the last sentence of the state paragraph ("跨生命週期的 live descriptor 是第三波退場前的過渡路徑，不是預設。"). Nothing else in the paragraph changes.
   - `SKILL.md`, readiness check: the text from "The mechanism that performs it is the installed Johnny runtime" through the honest statement "…so the owner must notify the reviewer.*" is replaced by exactly: "No runner, subscription or wake capability exists: they were retired in wave 3 (tickets 65 and 66). No automatic effect may be stated. The honest statement is: *the handoff is committed; no automation is armed for this project, so the owner must notify the reviewer.* The kept launcher commands `status` and `uninstall` run through the exact launcher path `<runtime root>\launcher\johnny-router.ps1`, where `<runtime root>` is `JOHNNY_ROOT` when set, else `%LOCALAPPDATA%\JohnnyRouter`; never invoke a bare `johnny-router` name." The rest of the section stays.
   - `Workflow.md:22`: delete "；descriptor 僅限過渡 bridge（R4-1）" from the flow-chart node label.
   - `doc/runbooks/dispatch-model-profile.md`:
     - Delete the "Cross-lifetime receipt-bound dispatch" bullet except its clause "the default cross-lifetime route is the ticket's state row plus the dispatch-file digest (R4-1)". That clause becomes the bullet.
     - In "Same-lifetime synchronous dispatch", delete the words "A live descriptor," and capitalise the following "receipt". The rest of the list stays.
     - "最小派工訊息" is unchanged.
   - `SKILL.md`, the skill references, `README.md`, `commands/johnny-project-takeover.md`, `template/README.md` and `Workflow.md`:
     - Delete each sentence or clause that names a retired surface.
     - Where a sentence states a still-valid rule beside a retired path, delete the clause about the retired path and keep the rule.
     - No new rule is written. A sentence whose meaning cannot survive the deletion is a `CHANGE_DETECTED` return naming its file and line.
   - `.agents/plugins/johnny-ai-skill/rules/worktree-containment.md`: delete the paragraph naming `worktree_containment.py`. The `.worktrees/` sentence stays.
   - `doc/runbooks/e7_owner_smoke.py` is deleted. It exercised the runner, and four of its imports no longer exist.
   - `doc/adr/ADR-20260824-019-provider-usage-telemetry-evidence.md`: the link to `modules/spec/context-load-telemetry.md` points to `doc/archive/specs/2026/context-load-telemetry.md`.
   - The card `workflow-router-poc` is removed:
     - delete `library/catalog/workflow-control/README.md`;
     - delete its row in `library/MODULE_CATALOG.md`.

     `library/workflow_router/README.md` already describes the contracts that stay. A `RETIRED_SURFACE` hit in it is deleted.
   - The card `path-containment`: the behaviour-evidence row and the reading path name `tests/test_path_containment_short_names.py`, in plain text, instead of the deleted suite.
   - Tests that pin a retired term:
     - `tests/test_adversarial_review_policy.py`: the tara2 terms `live descriptor` and `runner` leave the tuple, and the others stay; the tara6 assertion on "live descriptor" in `review-checks.md` is removed.
     - `tests/test_plugin_publication.py`: the assertions on "cross-lifetime receipt-bound handoff", "unavailable bridge must not halt", "unarmed wake", "For a cross-lifetime handoff", "跨生命週期、receipt-bound" and "live pending descriptor 或 handoff receipt" are removed, or point at the text that remains after the deletion.
     - `tests/test_plugin_payload_boundary.py`: the expected set of unresolved tokens loses `runner-subscriptions.json`.
     - `tests/test_antigravity_registration.py` changes only if its assertion breaks.
     - In general, an assertion whose text lies in a deleted sentence is removed. The STATEMENT names every changed or removed assertion.
6. **`exclusive-file-lock` is restored, card `READY`.**
   - `library/功能集群/python/exclusive_file_lock/file_lock.py` is `library/local_orchestration/file_lock.py` as of `c9af7725^`. Only two changes are allowed:
     - the module docstring's references to deleted modules;
     - the comment above `ExclusiveWindowsFileLock` ("The name six importers still use"), which becomes "Kept for callers of the earlier name".
   - `__init__.py` exports `ExclusiveFileLock`, `ExclusiveWindowsFileLock` and `FileLockAcquireDecision`.
   - `tests/test_exclusive_file_lock.py` is `tests/test_file_lock.py` as of `c9af7725^`, with only these changes:
     - every import and every `patch(...)` target string uses the new path, the child-process scripts included;
     - the import block of consumer modules is removed;
     - `NamingTests.test_every_consumer_holds_that_same_object` is removed, because every consumer it lists was retired;
     - `DocumentationTests` reads the card only, because the element README of ticket 08 is a historical record;
     - its assertion on `TelemetryStorageLockPort` is removed;
     - the docstring no longer names deleted test files.
   - Expected on Windows: 32 tests and 11 subtests pass.
   - The card:
     - names the new public import, contract source and test, in plain text;
     - replaces its `TelemetryStorageLockPort` sentences with one sentence: "It carries no telemetry, storage or ledger semantics.";
     - has its behaviour and strict-evidence rows refreshed from this ticket's run.

     `library/catalog/capabilities/README.md` keeps the card `READY`.
   - `library.local_orchestration.file_lock` stays absent; `tests/test_wayfinder_gap.py:79` already asserts that.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/67-doc-sweep`.
- reviewer：`ticket-review` seat in `.worktrees/67-doc-sweep-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; the files of the boundary block.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。A `RETIRED_SURFACE` hit outside the boundary, or a sentence whose meaning cannot survive the deletion, is a `CHANGE_DETECTED` return naming the file and line.

### 前端組合與依賴注入

**N/A reason**：documents, tests and a standard-library module; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：`ExclusiveFileLock`, `ExclusiveWindowsFileLock`, `FileLockAcquireDecision` at `library.功能集群.python.exclusive_file_lock`, unchanged in behaviour.

### Observation on the base

- The first red run of `RETIRED_SURFACE` on the base is the authoritative list of hits, and the STATEMENT reports it.
- The rule-only review measured these reds on removing the exemptions:
  - `SKILL.md:41` and `:134`;
  - `router-control.md:9` and `:109`;
  - the SPEC R4-1 sentence, which item 4 handles.

## TDD 設計

1. 正常行為:
   - on the result, `RETIRED_SURFACE` reports no hit, and every existing sweep test stays green with `EXPECTED_TOLERATED` unchanged;
   - `tests/test_exclusive_file_lock.py` passes on Windows with 32 tests and 11 subtests.
2. 規則違反／輸入錯誤:
   - Each of these, injected into a copy of the swept set, turns `RETIRED_SURFACE` red:
     - `runner status` in `SKILL.md`;
     - the verbatim deleted `AGENTS.md` sentence, put back;
     - `PendingDispatchDescriptor` in `router-control.md`;
     - `wake-capability probe` in `README.md`;
     - `RouterEngine` in `library/workflow_router/README.md`;
     - one term in a file under each new root (`commands/`, `.agents/`, `library/catalog/`, `library/MODULE_CATALOG.md`, `library/功能集群/python/path_containment/README.md`);
     - "until it is retired, the live descriptor stays";
     - with the exemption dropped, "the live descriptor was retired in wave 3".
   - "Cross-lifetime handoffs must use the transitional receipt-bound route.", injected into `Workflow.md`, turns pattern b2 red.
   - The SPEC's R4-1 sentence, injected verbatim into `AGENTS.md`, turns red; it is exempt only in the SPEC.
   - The SPEC with its status note removed turns red.
   - These stay green:
     - "Router" alone;
     - `johnny-router.ps1 status`;
     - "the live descriptor was retired in wave 3";
     - prose "runner" outside the list.
3. 外部失敗／fail-closed:
   - a file of the swept set that is missing or not UTF-8 stays a test failure, as today;
   - the lock's fail-closed cells (an empty path; a failed acquisition retains no handle) pass at the new path.
4. 回歸保護:
   - `tests/test_wayfinder_gap.py` still finds `library.local_orchestration.file_lock` absent;
   - `tests/test_plugin_publication.py` and `tests/test_plugin_payload_boundary.py` pass.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | `library/catalog/` versus a file `library/catalog.md`; a `README.md` one folder deeper than the globs is not in the set; the old and new lock paths are distinct |
| 2 | null／空字串／陣列 | 是 | an empty swept file has no hit; the lock's empty-path cell |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | `Temporal` versus `temporal`; `runner status` versus prose "runner"; `退場前` does not exempt; `johnny-router.ps1 status` does not match |
| 5 | 錯誤碼是否一致 | 否 | no exit codes change |
| 6 | 例外是否會拋出 | 是 | the lock's release-primitive error cell passes at the new path |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_governance_consistency.py tests/test_adversarial_review_policy.py tests/test_antigravity_registration.py tests/test_plugin_publication.py tests/test_plugin_payload_boundary.py tests/test_exclusive_file_lock.py tests/test_wayfinder_gap.py tests/test_path_containment_short_names.py -q` exits 0.
  - `mypy --strict --python-version 3.11` on the lock module, its test and the sweep test exits 0.
- **反向突變證據**, each restored after it turns a named test red:
  - drop `RETIRED_SURFACE`;
  - put `transitional` back into `BRIDGE_EXEMPT`;
  - remove `commands/` from the swept set;
  - remove the SPEC status note;
  - let `退場前` exempt;
  - drop the completed-retirement exemption.
- **Lock evidence**: `git diff --no-index` of the old and new module, and of the old and new test, attached; each shows only the allowed changes.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last), and the typed return in STATEMENT.

## 正式環境移植 SOP

- 不適用：plugin documents and a library module.

## 完成回寫

The control plane writes these rows.

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
