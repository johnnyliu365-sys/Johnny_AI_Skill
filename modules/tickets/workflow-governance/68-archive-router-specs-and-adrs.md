# 68｜Router library retirement (3): the seven router-era SPECs archived, a SPEC archive rule, the router-era ADRs superseded

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（Revision 04; REQ-20261103-043 wave 3, owner decision 2026-11-18 "3A 4A"; owner decision B of 2026-11-03: historical SPECs are archived, not deleted, in wave 3） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/68-archive-specs-out/` / owner implementation seat / worktree `.worktrees/68-archive-specs` / branch `cp/wave3-68-archive-specs` / baseline the wave-3 branch after ticket 65 is integrated |
| 實作語言 | Markdown documents; Python 3.11 for the test change（CONTEXT.md Implementation language） |
| 狀態 | `REVIEW_APPROVED`（candidate `c3ecdd6b`; correction review `APPROVED`; S68-02 to ticket 67, S68-03 and S68-04 carried as known debt） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/68-archive-specs` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/68-archive-specs-review` |
| 責任邊界 | the SPEC archive tree, the moved SPECs, the SPEC index, the SPEC archive rule in the requirement-lineage reference, the state of nine ADRs and their index, the active references to the moved SPECs, and the governance-consistency test |
| 禁止修改 | `library/`, the gate scripts, `Workflow.md`, `AGENTS.md`, `CodeReview.md` and the other references (ticket 67), the dispatch profile runbook (ticket 69 changes it), historical records |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = modules/spec/README.md
modify = skills/johnny-project-takeover/references/requirement-lineage.md
modify = doc/archive/README.md
modify = doc/adr/README.md
modify = doc/adr/ADR-20260804-001-private-router-saas.md
modify = doc/adr/ADR-20260805-002-autonomous-collaboration-control-plane.md
modify = doc/adr/ADR-20260808-003-local-orchestration-installer.md
modify = doc/adr/ADR-20260814-010-reviewer-owned-orchestration-gateway.md
modify = doc/adr/ADR-20260814-011-tiered-model-router-lifecycle.md
modify = doc/adr/ADR-20260815-012-receipt-bound-event-driven-completion-supervision.md
modify = doc/adr/ADR-20260823-014-cross-lifetime-handoff-bridge.md
modify = doc/adr/ADR-20260823-016-codex-cli-cross-lifetime-wake-bridge.md
modify = doc/adr/ADR-20260827-029-host-bootstrap-router-provisioning-and-composition.md
modify = CONTEXT.md
modify = ProjectSchedule.md
modify = doc/requirements/active/
modify = tests/test_governance_consistency.py
modify = tests/test_plugin_payload_boundary.py
create = doc/archive/specs/
delete = modules/spec/router-framework.md
delete = modules/spec/private-router-saas.md
delete = modules/spec/autonomous-collaboration-audit.md
delete = modules/spec/receipt-bound-role-supervision.md
delete = modules/spec/executor-routing.md
delete = modules/spec/plugin-release-telemetry.md
delete = modules/spec/context-load-telemetry.md
forbid = library/
forbid = skills/johnny-project-takeover/scripts/
forbid = Workflow.md
forbid = AGENTS.md
forbid = CodeReview.md
forbid = doc/runbooks/
forbid = doc/reviews/
forbid = doc/handoffs/
forbid = doc/context/
forbid = modules/tickets/
forbid = .claude-plugin/
forbid = .codex-plugin/
```

## 使用者拍板與可觀察結果

On 2026-11-18 the owner decided "3A 4A" (REQ-20261103-043, wave 3):

- **3A:** archive only the seven router-era SPECs.
- **4A:** the requirement-lineage reference gains a SPEC archive rule at `doc/archive/specs/<year>/`. The router-era ADRs are marked `SUPERSEDED` and stay where they are.

This carries out owner decision B of 2026-11-03: historical SPECs are archived, not deleted.

When this ticket is done:

- **The SPEC archive rule** (`requirement-lineage.md`, new section "SPEC archive"):
  - A SPEC that no longer governs any active work moves, unchanged, to `doc/archive/specs/<year>/<slug>.md`. The year is the year it is archived.
  - The archive root `doc/archive/specs/README.md` lists only year partitions. Each year index lists one row per archived SPEC: an archive ID `ARCH-SPEC-YYYYMMDD-NNN`, the leaf link, the SPEC ID, its last active revision, the reason, the replacement where one exists, and the historical source commit (the last commit with the SPEC at its active path).
  - The active SPEC index (`modules/spec/README.md`) keeps only the archive ID and the archive reference of an archived SPEC, never its title narrative or status.
  - Active documents that cite an archived SPEC cite its archive path.
  - Historical records keep the path they were written with. These are review records, tickets, handoffs and feature Context files. Git history is the evidence for that path.
  - The validation rules of the reference apply to SPEC archive IDs as they apply to `ARCH-REQ` bundles. Each of these is `HALT / REQUIREMENT_LINEAGE_INVALID`:
    - a duplicate archive ID;
    - a dangling or mixed active/archive reference;
    - a SPEC present at both paths.
- **The seven SPECs** are moved with `git mv`, so their content is byte-identical, to `doc/archive/specs/2026/`:
  - router-framework, private-router-saas, autonomous-collaboration-audit, receipt-bound-role-supervision, executor-routing, plugin-release-telemetry and context-load-telemetry;
  - with IDs `ARCH-SPEC-20261118-001` to `-007` in that order;
  - reason: the router library they specify was retired by tickets 65 and 66 (owner decision 2026-11-18 "1A");
  - replacement: workflow-governance Revision 04 where it applies, otherwise none.
- **`doc/archive/README.md`** gains the SPEC partition row.
- **The nine ADRs** (001, 002, 003, 010, 011, 012, 014, 016 and 029):
  - each gets state `SUPERSEDED`;
  - each gets a `Superseded by` line naming REQ-20261103-043, the owner decision of 2026-11-18 and workflow-governance Revision 04;
  - their decision text is not changed;
  - `doc/adr/README.md` shows the same state for each.
- **Active references** to the moved SPECs point at the archive path. These are in:
  - `CONTEXT.md`;
  - `ProjectSchedule.md`;
  - the active requirement leaves under `doc/requirements/active/` that link them.

  Each changed file is named in the STATEMENT.
- **Known references left for later tickets:**
  - `doc/runbooks/dispatch-model-profile.md` is changed by ticket 69 and swept by ticket 67;
  - `library/workflow_router/README.md` was rewritten by ticket 65.

  Each remaining reference outside the boundary is listed in the STATEMENT as a follow-up for ticket 67.
- **`tests/test_governance_consistency.py`**:
  - its precedence-note sweep also reads `doc/archive/specs/`, so an archived SPEC keeps its precedence note;
  - its fixtures that use `modules/spec/router-framework.md` are changed to a SPEC that is still active, or to the archive path, wherever the case still describes a real path;
  - each changed assertion is named in the STATEMENT.
- **`tests/test_plugin_payload_boundary.py`**: the `DEVELOPMENT_ONLY` declaration of `modules/spec/context-load-telemetry.md` follows the move, and the archive tree stays out of the payload. A test asserts that `doc/archive/specs/` is not a payload path.
- **The active PRD and CHG pairs** of the retired features stay active in this ticket. The STATEMENT lists each pair whose only SPEC is now archived, as an owner decision for later retirement under the existing `ARCH-REQ` rule.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/68-archive-specs`.
- reviewer：`ticket-review` seat in `.worktrees/68-archive-specs-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket; REQ-20261103-043 owner decision 2026-11-18; `skills/johnny-project-takeover/references/requirement-lineage.md`.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：documents and one test; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the archive index row above.

## TDD 設計

1. 正常行為:
   - `tests/test_governance_consistency.py` passes with the archived SPECs read from `doc/archive/specs/`.
   - Every link in the changed documents resolves to an existing file. This is checked by a script whose output is the L1 capture.
2. 規則違反／輸入錯誤: one test each in `tests/test_governance_consistency.py` for:
   - a SPEC present at both its active and archive path;
   - two archive rows with one ID;
   - an archived SPEC without its precedence note.
3. 外部失敗／fail-closed: an undecodable archived SPEC is reported as `UNDECODABLE`, as for an active one.
4. 回歸保護: `git diff -M --stat` shows each of the seven moves as a 100% rename. The full suite has no new red, and the CI jobs on both systems stay green.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | `doc/archive/specs` is not matched by a rule for `doc/archive/specs-old` or `modules/spec` |
| 2 | null／空字串／陣列 | 是 | an empty archived SPEC is `NOTE_MISSING`, as for an active one |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 是 | archive IDs `ARCH-SPEC-YYYYMMDD-NNN`, exact |
| 5 | 錯誤碼是否一致 | 否 | no exit code changes |
| 6 | 例外是否會拋出 | 是 | an undecodable archived SPEC does not raise |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_governance_consistency.py tests/test_plugin_payload_boundary.py -q` exits 0, apart from `CommittedPinTests::test_the_pinned_sha_exists`.
  - `mypy --strict --python-version 3.11 tests/test_governance_consistency.py` exits 0.
- **L1**: a link check of every changed Markdown file, in which every relative link resolves.
- **R1**: `git diff -M --stat <base>` names the seven 100% renames.
- **反向突變證據**, each restored after it turns a named test red:
  - drop the archive tree from the precedence-note sweep;
  - accept a SPEC at both paths;
  - accept a repeated archive ID.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last). The STATEMENT lists every changed reference, every reference left for ticket 67, every changed assertion, and the PRD/CHG pairs listed for the owner.

## 正式環境移植 SOP

- 不適用：documents; the archive tree is not in the payload.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
