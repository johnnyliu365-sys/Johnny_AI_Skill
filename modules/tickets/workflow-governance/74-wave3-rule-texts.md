# 74｜Wave-3 rule texts: content digests, seat residue, process tiers, smallest fixes, consolidated corrections, review labels and dispatch authoring

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（REQ-20261103-043: owner decision 2026-11-18 "B" (L-3, L-9, L-11), control-plane disposition 2026-11-18 (L-19, L-20), control-plane disposition 2026-11-19 (ticket 67 and ticket 74); carried findings S61-07, S72-05） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision04 / receipt under `.worktrees/74-rule-texts-out/` / owner implementation seat / worktree `.worktrees/74-rule-texts` / branch `cp/wave3-74-rule-texts` / baseline the wave-3 branch after ticket 67 is integrated |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language）for the test; each document keeps its own language |
| 狀態 | `REVIEW_APPROVED`; dispatch=sha256:1066881111e914a9af7b4d2da411fa75a66246099477f19ec3eb1898c7973bfb (`doc/handoffs/2026/workflow-governance/dispatch/JAS-74-1.yaml`)（candidate `4943d76c`; initial review `APPROVED`） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/74-rule-texts` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/74-rule-texts-review` |
| 責任邊界 | the seven rule texts below, each at its named place, one sentence in `Workflow.md` §3, and one test that pins them |
| 禁止修改 | every gate script, `library/`, `template/`, the ticket template, the SPEC, any rule not named below |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = CodeReview.md
modify = Workflow.md
modify = skills/johnny-project-takeover/references/router-control.md
modify = skills/johnny-project-takeover/references/implementation-authority.md
modify = skills/johnny-project-takeover/references/specification-ticketing.md
create = tests/test_governance_rule_texts.py
forbid = library/
forbid = template/
forbid = skills/johnny-project-takeover/scripts/
forbid = modules/spec/
forbid = AGENTS.md
forbid = doc/runbooks/
```

## 使用者拍板與可觀察結果

Process tier: strict.

**The problem.** Waves 1 to 3 kept running into the same gaps. Each was worked around by hand in a dispatch, a correction or a review record, and none of them is written in the governance documents:

- A receipt cannot name the commit that contains it, and two commits were both called "candidate" (L-3; S61 gap 2).
- Seats left processes, clones and locks behind, and another seat cleared them without knowing whose they were (L-9).
- Every ticket got the same process weight, whatever kind of change it carried (L-11).
- Low-impact findings were answered with new mechanisms (L-19).
- Rules changed after dispatch reached the seat as several partial corrections, and a review then judged against a superseded sentence (L-20).
- A review was relabelled from correction to initial after its verdict came back (S61-07).
- Dispatch lines failed the new R5 because of literal payloads and rationale clauses (S72-05).

The owner adopted the lessons on 2026-11-18 ("B"). The control plane assigned the rule texts to this ticket on 2026-11-19. S61-03 (dispatch-file path, submitter and worktree on resume, review record path) is not in this ticket. It needs changes to `AGENTS.md` and `template/`, and goes to wave 4.

**Revision02** answers the rule-only review of revision01, **revision03** the correction review of revision02, and **revision04** the narrow check of revision03 (`doc/reviews/workflow-governance/74-wave3-rule-texts-ticket-review.md`).

**How rules are placed.**
- Each rule below goes at its named place.
- An HTML anchor with the rule's id stands on its own line directly above the rule. In a new section, the anchor goes below the section heading.
- A rule's block runs from its anchor to the next anchor or heading, whichever comes first.
- The seat writes each rule in the language of its document. The block states the content given here and nothing more. Where a rule gives a sentence in quotes, the block carries that sentence's content.
- No other sentence changes.

1. **`rule-content-digest-only`** goes in `router-control.md`, in a new last section `## Receipt integrity` (L-3).
   - "Integrity rests on content digests, never on a commit id that a file would have to name about itself."
   - "A receipt's `candidate:` field, and the `--candidate` that `evidence_gate.py` checks, are the commit its cells ran at."
   - "When the receipt is committed after that commit, the candidate for review and for the merge queue is the commit that adds the receipt, and its diff is the receipt only."
   - "`USAGE` cells are appended after the candidate is set, in a record commit."
2. **`rule-seat-residue`** goes in `implementation-authority.md`, section "Allocation and correction", after its last paragraph (L-9).
   - "Every process, scratch directory, clone, lock or port that a seat starts for its run carries the seat's run id, in its name or in an owner file."
   - "Before it returns, the seat removes everything that carries its tag, and lists in its STATEMENT or review record what it removed and anything it left, with the reason."
   - "The allocated worktree, the branch and the receipt directory are not residue: the seat hands them back, and does not remove them."
   - "Files the seat's own commands write inside its allocated worktree, such as caches, are its own, and the seat removes them."
   - "No seat removes another seat's resource or an untagged one outside its allocated worktree; it reports untagged residue to the control plane."
   - The existing sentence on clearing residue in one's own worktree stays.
3. **`rule-process-tier`** goes in `specification-ticketing.md`, section "Ticket", after its last paragraph (L-11, L-5). `Workflow.md` §3 gains one sentence after its reference list, linking `#rule-process-tier`: "Every ticket opened after this rule names its process tier." The rule block says:
   - The tier is decided by the kind of change. When a ticket carries several kinds, the strictest kind decides.
   - A ticket opened after this rule names its tier on the first line of its section 使用者拍板與可觀察結果, as `Process tier: standard` or `Process tier: strict`. The template line and the tickets already open are wave-4 work.
   - **Records** are not tickets. A record change only appends to the record files: a new review or integration record, a new row, a new completion entry. It edits no existing field or block that a gate reads, such as a state row, `review-verdict`, `convergence-disposition`, a dispatch digest or a receipt path. It edits no recorded decision. Two exceptions are records too: the state-row and index transitions a governance rule assigns to the control plane, and writing or revising a ticket. They include the dispatch digest and receipt at dispatch, `REVIEW_APPROVED` under §5 rule B, and `INTEGRATED` or `DONE`, and `BLOCKED` or `SUPERSEDED` under a requirement change (`discovery-change.md`). Writing or revising a ticket is reviewed under that ticket's tier. The control plane commits records directly. Anything else is a ticket.
   - **standard**: code, tests or documents changed within the existing rules. It takes one implementation seat and reviews as `CodeReview.md` §5 sets out.
   - **strict**: a change to a governance rule, to a gate's verdict, grammar or exit codes, or to a security or confinement boundary. Rule-bearing files include:
     - `AGENTS.md`, `Workflow.md`, `CodeReview.md`;
     - `skills/johnny-project-takeover/SKILL.md`, its references, `scripts/` and `scripts/README.md`;
     - the dispatch runbook;
     - `modules/tickets/TEMPLATE.md` and `template/`;
     - `.agents/` rules;
     - `ci/registered-failures.json`;
     - `modules/spec/workflow-governance.md`;
     - any test that pins a governance rule.

     A strict ticket takes the standard tier plus an independent rule-only review of the ticket before dispatch.
   - The rule-only review of a ticket is not a review in `CodeReview.md` §5's count. Its `CHANGES_REQUESTED` produces a new ticket revision before dispatch.
4. **`rule-smallest-fix`** goes in `CodeReview.md` §4, after the classification list (L-19).
   - "For a finding that does not block under §5 rule B, the reviewer names the smallest fix that closes it, or proposes that it be carried to one of the destinations that §4 item 5 and §5 rule B allow."
   - "A correction adds no new mechanism (a script, gate, schema or rule) unless the finding cannot be closed without one, and the reviewer states why."
5. **`rule-consolidated-correction`** goes in `implementation-authority.md`, section "Allocation and correction", after `rule-seat-residue` (L-20).
   - "A rule changed after dispatch reaches the seat as one consolidated correction that names every earlier sentence it supersedes."
   - "A review request names the sections authoritative for the review and the sentences superseded under this rule."
6. **`rule-review-label`** goes in `CodeReview.md` §5, after its last bullet (S61-07).
   - "The first review of a new closure revision is its initial review; the count restarts."
   - "The control plane labels each review in the review request before dispatch: initial or correction, with its closure revision. It never relabels a review after the conclusion."
   - "A conclusion is recorded as returned, including an attached `CONVERGENCE_REVIEW_REQUIRED`."
7. **`rule-dispatch-authoring`** goes in `specification-ticketing.md`, section "Dispatch normalization", after its last paragraph (S72-05). It applies to the dispatch file whose digest the ticket's state row carries (R4-1), not to the envelope.
   - "In a dispatch file, a commit subject or other literal payload goes in backticks."
   - "Each enumerated item is its own list item."
   - "A rationale clause is dropped or joined with a comma, never placed after `; `."

**Before dispatch.** Ticket 67 rewrites sentences in `router-control.md` and `implementation-authority.md`. After 67 is integrated, the control plane checks these places against the new text: rule 1's new section, and rules 2 and 5 after the last paragraph of "Allocation and correction". It checks for contradiction, then names the base in the dispatch.

A sentence that contradicts one of these rules is a `CHANGE_DETECTED` return naming its file and line; the seat does not reconcile it.

## 實作範圍、依賴與 ticket elements

### 角色指派（必填）

- 流程／Grill／ticket owner：control plane.
- implementation owner：`implementation-standard` seat in `.worktrees/74-rule-texts`.
- reviewer：`ticket-review` seat in `.worktrees/74-rule-texts-review`.
- **Owner override record**：`N/A`
- `ImplementationHandoff`：this ticket.
- `ImplementationReturn`：`COMPLETED → ACTION_COMPLETED`／`BLOCKED → HALT`／`CHANGE_DETECTED → REQUIREMENT_CHANGED → Grill`。

### 前端組合與依賴注入

**N/A reason**：governance documents and one test; no UI boundary.

- element 路徑：不適用
- 實際原始碼路徑：the paths in the boundary block
- 公開契約／資料模型：the seven anchors.

## TDD 設計

1. 正常行為: `tests/test_governance_rule_texts.py` finds each anchor exactly once, in its named file and section. The rule's block (anchor to the next anchor or heading) carries these terms:
   - `rule-content-digest-only`: `digest`, `--candidate`;
   - `rule-seat-residue`: `run id`, `STATEMENT`;
   - `rule-process-tier`: `Process tier`, `standard`, `strict`;
   - `rule-smallest-fix`: `rule B` or `規則 B`;
   - `rule-consolidated-correction`: `supersede`;
   - `rule-review-label`: `CONVERGENCE_REVIEW_REQUIRED`;
   - `rule-dispatch-authoring`: `dispatch file`.

   `Workflow.md` §3 links `#rule-process-tier`.
2. 規則違反／輸入錯誤: each of these, on a copy, turns its test red:
   - one anchor removed;
   - one anchor moved to another section;
   - one anchor duplicated;
   - the `Workflow.md` §3 link removed.
3. 外部失敗／fail-closed: a named file that is missing or not UTF-8 fails the test with the file named.
4. 回歸保護: `tests/test_governance_consistency.py`, `tests/test_adversarial_review_policy.py`, `tests/test_control_plane_mutation.py` and `tests/test_plugin_publication.py` pass unchanged.

### 適用的缺陷類別

| # | 類別 | 是否適用 | 本工單的必要案例 |
| --- | --- | --- | --- |
| 1 | 路徑前綴誤匹配 | 是 | anchor `rule-process-tier` versus a longer id such as `rule-process-tier-x` |
| 2 | null／空字串／陣列 | 是 | an anchor followed by an empty paragraph fails |
| 3 | 權限繞過 | 否 | no permission path |
| 4 | Token 格式與比較 | 否 | literal terms only |
| 5 | 錯誤碼是否一致 | 否 | no exit codes |
| 6 | 例外是否會拋出 | 是 | the missing-file case |

## 完成定義與證據

- The tests:
  - `python -m pytest tests/test_governance_rule_texts.py tests/test_governance_consistency.py tests/test_adversarial_review_policy.py tests/test_control_plane_mutation.py tests/test_plugin_publication.py -q` exits 0.
  - `mypy --strict --python-version 3.11` on the new test exits 0.
- **反向突變證據**: for two of the anchors, remove the anchor and then the required term. Each turns a named test red and is restored.
- **CI evidence**: one run on a commit of this branch, with both jobs `success`.
- **Receipt**: R4-7 cells, passing P9 and E1 (E1 runs last), and the typed return in STATEMENT.

## 正式環境移植 SOP

- 不適用：plugin documents.

## 完成回寫

- 實際檔案：`<paths>`
- commit：`<SHA>`
- WorkProgress：不適用
