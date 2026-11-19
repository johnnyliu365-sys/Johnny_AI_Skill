# 79｜A read-only question goes straight to its leaf: the entry routes only changes through the workflow

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（REQ-20261103-043, owner decision 2026-11-20 "A": fix in 0.5.0 that a read-only question walks the whole governance chain） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/79-lookup-out/` / owner implementation seat / worktree `.worktrees/79-lookup` / branch `cp/wave3-79-lookup` / baseline the wave-3 branch after ticket 73 is integrated |
| 實作語言 | Markdown governance text; Python 3.11 for the test（CONTEXT.md Implementation language） |
| 狀態 | `PLANNED`（strict tier; rule-only review before dispatch; after ticket 73, before ticket 71） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/79-lookup` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/79-lookup-review` |
| 責任邊界 | the entry condition and one read-only-lookup paragraph in `AGENTS.md`, the skill's trigger description and one start step in `SKILL.md`, and one test that pins them |
| 禁止修改 | `Workflow.md`, `CodeReview.md`, the skill references, the gate scripts, `library/`, `commands/`, `template/` |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = AGENTS.md
modify = skills/johnny-project-takeover/SKILL.md
create = tests/test_entry_read_only_lookup.py
forbid = Workflow.md
forbid = CodeReview.md
forbid = skills/johnny-project-takeover/references/
forbid = skills/johnny-project-takeover/scripts/
forbid = library/
forbid = commands/
forbid = template/
```

## 使用者拍板與可觀察結果

Process tier: strict.

**The problem.** On a host where the 0.4.14 plugin is installed, the owner asked Codex only to look up a document. Codex started at `Workflow.md` and read outward through the governance chain. That is unnecessary, and it is wrong: the tree rule already resolves one path from an index to the exact leaf (`artifact-tree-routing.md`, Tree invariant). 0.5.0 has the same cause:

- `AGENTS.md` sends every task through its start order "在讀取 target source、執行工具或寫入前", a reading included.
- The skill's description triggers on any "new, inherited, or active software project", and its first start step reads `Workflow.md`.
- No rule exempts a read-only question.

The owner decided on 2026-11-20 ("A") to fix this in 0.5.0, before ticket 71, because ticket 77's Codex acceptance would otherwise reproduce it. Version markers on the copies that target projects hold go to wave 4.

After this ticket:

1. **`AGENTS.md`, the start order's condition.** The line "在讀取 target source、執行工具或寫入前：" becomes "在改動 target、推進流程或執行會寫入的工具之前：". The five steps stay as they are.
2. **`AGENTS.md`, a read-only-lookup paragraph** directly after the five steps. An HTML anchor `read-only-lookup` stands on its own line above it. The paragraph says exactly:

   "唯讀查詢（只問某份文件的內容、某張票的狀態或某條規則的寫法，不要求改動）不走上面的啟動順序：從下方「Target project 正式來源」的標準位置，或專案既有的同用途路徑，找到該類文件的索引，一次解析一條路徑到確切的 leaf，讀完即回答。不讀 Workflow、Router 或其他 reference，不載入整棵樹，不寫受據。查詢中發現需要改動時，停下並改走上面的啟動順序。"

3. **`SKILL.md`, the trigger description.** The frontmatter `description` becomes exactly:

   "Route an action that changes a software project's workflow state (Wayfinder, architecture, requirements, specification, tickets, implementation, review, handoff, integration) through Johnny's governed workflow. Use when Codex must take over or resume a project, select the next governed stage, dispatch or review an implementer, or apply Johnny workflow policy without adding a runtime dependency to the target project. Not for a read-only question about an existing document, ticket or rule: answer it from that document's index and leaf."

4. **`SKILL.md`, the start.** The section `## Start` gains a first step before the current step 1. The current steps are renumbered 2 to 5, with no other change. The new step says exactly:

   "1. A read-only question (the content of a document, the state of a ticket, the wording of a rule) is not a workflow action: resolve it from that document's index to the exact leaf, as the target project's `AGENTS.md` read-only-lookup paragraph says, answer, and stop. Do not read `Workflow.md` for it."

5. **`tests/test_entry_read_only_lookup.py`** pins items 1 to 4:
   - the condition line;
   - the anchor and the paragraph, in that place;
   - the description;
   - the new first start step, and that the five original steps follow it in order.

No other sentence changes. The pins of `tests/test_plugin_publication.py` and `tests/test_governance_consistency.py` on these files keep passing unchanged. A test that breaks is a `CHANGE_DETECTED` return naming the test.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/79-lookup`.
- reviewer：`ticket-review` seat in `.worktrees/79-lookup-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：governance text and one test; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the entry condition, the lookup paragraph, the description and the start step above.

## TDD 設計

1. 正常行為: the new test passes on the result, and `tests/test_plugin_publication.py`, `tests/test_governance_consistency.py` and `tests/test_governance_rule_texts.py` pass unchanged.
2. 規則違反／輸入錯誤: each of these, on a copy, turns the new test red:
   - the old condition line put back;
   - the paragraph removed;
   - the anchor moved below the paragraph;
   - the description's last sentence removed;
   - the new start step moved after the original first step.
3. 外部失敗／fail-closed: a missing or non-UTF-8 file fails the test with the file named.
4. 回歸保護: the RETIRED_SURFACE sweep passes on the new text; the payload closure test passes, with no new path-shaped inline token in the shipped text.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 否 | no path rule |
| 2 | null／空字串／陣列 | 是 | an empty description fails |
| 3 | 權限繞過 | 是 | the lookup paragraph allows no write and no receipt; a question that turns into a change goes back to the start order |
| 4 | Token 格式與比較 | 是 | the condition line compared exactly; the anchor id exact |
| 5 | 錯誤碼是否一致 | 否 | no exit codes |
| 6 | 例外是否會拋出 | 是 | the missing-file case |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_entry_read_only_lookup.py tests/test_plugin_publication.py tests/test_governance_consistency.py tests/test_governance_rule_texts.py tests/test_plugin_payload_boundary.py -q` exits 0, apart from the registered base failures, each named by test id in the dispatch.
  - `mypy --strict --python-version 3.11` on the new test exits 0.
- **反向突變證據**, each restored after it turns a named test red: the five cases of TDD 2.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last), and the typed return in STATEMENT.

## 正式環境移植 SOP

- 不適用：governance text in the plugin.

## 完成回寫

The control plane writes these rows.

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
