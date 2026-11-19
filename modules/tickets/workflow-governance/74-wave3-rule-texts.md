# 74｜Wave-3 rule texts: content digests, seat residue, process tiers, smallest fixes, consolidated corrections, review labels and resume conventions

| 欄位 | 內容 |
| --- | --- |
| 對應規格 ID | `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`（REQ-20261103-043: owner decision 2026-11-18 "B" (L-3, L-9, L-11), control-plane disposition 2026-11-18 (L-19, L-20), control-plane disposition 2026-11-19 (ticket 67 and ticket 74); carried findings S61-03, S61-07, S72-05） |
| 規格撰寫 AI | control plane |
| 第一步排查起點 | `doc/context/workflow-governance/main.md` |
| PRD 索引 | `PRD-20261103-043` |
| 需求變更 | `CHG-20261103-043` |
| Sealed Context binding | 不適用 |
| Agent Context binding | ticket revision01 / receipt under `.worktrees/74-rule-texts-out/` / owner implementation seat / worktree `.worktrees/74-rule-texts` / branch `cp/wave3-74-rule-texts` / baseline the wave-3 branch after ticket 67 is integrated |
| 實作語言 | Python 3.11（CONTEXT.md Implementation language）for the test; each document keeps its own language |
| 狀態 | `PLANNED`（strict tier: an independent rule-only review of this ticket precedes dispatch; after ticket 67） |
| 共同基準 | the `cp/wave3` commit named in the dispatch |
| 實作者 | `implementation-standard` seat, worktree `.worktrees/74-rule-texts` |
| 審閱者 | `ticket-review` seat, worktree `.worktrees/74-rule-texts-review` |
| 責任邊界 | the seven rule texts below, each at its named place, and one test that pins them |
| 禁止修改 | every gate script, `library/`, `template/`, the ticket template, the SPEC, any rule not named below |
| 環境 | `LOCAL` and GitHub Actions on the plugin repository |

## 邊界宣告（機器可讀，整合前由閘門讀取）

```johnny-boundary
modify = CodeReview.md
modify = Workflow.md
modify = skills/johnny-project-takeover/references/router-control.md
modify = skills/johnny-project-takeover/references/implementation-authority.md
modify = skills/johnny-project-takeover/references/specification-ticketing.md
modify = doc/runbooks/dispatch-model-profile.md
create = tests/test_governance_rule_texts.py
forbid = library/
forbid = template/
forbid = skills/johnny-project-takeover/scripts/
forbid = modules/spec/
forbid = AGENTS.md
```

## 使用者拍板與可觀察結果

**The problem.** Waves 1 to 3 kept running into the same seven gaps. Each was worked around by hand in a dispatch, a correction or a review record, and none of them is written in the governance documents:

- Receipts tried to name the commit that contains them, which a commit cannot do (L-3; S61 gap 2).
- Seats left processes, clones and locks behind, and another seat cleared them without knowing whose they were (L-9).
- Every ticket got the same process weight, whatever kind of change it carried (L-11).
- Low-impact findings were answered with new mechanisms (L-19).
- Rules changed after dispatch reached the seat as several partial corrections, and the review then judged against a superseded sentence (L-20).
- A review was relabelled from correction to initial after its verdict came back (S61-07).
- The dispatch path, the submitter and the worktree on resume, and the review record path were left to each seat (S61-03).
- Dispatch lines failed the new R5 because of literal payloads and rationales after `; ` (S72-05).

The owner adopted the lessons on 2026-11-18 ("B"). The control plane assigned the rule texts to this ticket on 2026-11-19.

After this ticket, each rule below stands at its place. Each place carries the HTML anchor named in the rule, on its own line directly above the rule. The seat writes each rule in the language of its document, with the content stated here and nothing more.

1. **`rule-content-digest-only`** in `router-control.md`, beside the receipt and state-row rules (L-3).
   - The integrity of a receipt, a ticket state row or an index row rests on content digests only.
   - A file never names the commit that contains it.
   - A receipt names the commit its cells ran at and the digests of what it covers.
   - The control plane names the candidate, which is the commit that adds the receipt, in the review request.
2. **`rule-seat-residue`** in `implementation-authority.md`, section "Allocation and correction" (L-9).
   - Every process, temporary directory, clone, worktree, branch, lock or port a seat starts carries the seat's run id, in its name or in an owner file.
   - Before it returns, the seat removes everything that carries its tag. Its STATEMENT lists what it removed, and anything left with the reason.
   - No one removes another seat's resource or an untagged one. Untagged residue is reported to the control plane.
   - The existing sentence about clearing known residue in one's own worktree is replaced by this rule.
3. **`rule-process-tier`** in `specification-ticketing.md`, section "Ticket", with one sentence and a link in `Workflow.md` §3 (L-11, L-5). The tier is decided by the kind of change; the highest kind in a ticket decides; the ticket's 狀態 row names it.
   - **light**: changes to records only. Records are ticket state rows, review and integration records, requirement rows and the changelog, with no change to a rule, test, script, template or module. The control plane commits them directly, without a seat or a review.
   - **standard**: code, tests, templates or documents changed within the existing rules. One implementation seat, and reviews as `CodeReview.md` §5 sets out.
   - **strict**: a change to a governance rule, to a gate script's verdict or exit codes, or to a security or confinement boundary. Governance rules are in `AGENTS.md`, `Workflow.md`, `CodeReview.md`, the skill references and the dispatch runbook. The standard tier applies, plus an independent rule-only review of the ticket before dispatch.
4. **`rule-smallest-fix`** in `CodeReview.md` §4 (L-19).
   - For a finding of severity Low, or one that does not block under §5 rule B, the reviewer names one of two things: the smallest fix that closes it, or acceptance as a known debt with its carry destination.
   - A correction adds no new mechanism (script, gate, schema or rule) unless the finding cannot be closed without one. The reviewer states why.
5. **`rule-consolidated-correction`** in `dispatch-model-profile.md`, section "Dispatch and reporting discipline" (L-20).
   - A rule changed after dispatch reaches the seat as one consolidated correction. It names every earlier sentence it supersedes.
   - A review request names the sections that are authoritative for the review, and the sentences superseded under this rule.
6. **`rule-review-label`** in `CodeReview.md` §5 (S61-07).
   - The first review of a new closure revision is its initial review; the count of §5 restarts.
   - The control plane labels each review in the review request before dispatch, as initial or correction, with its closure revision. It never relabels a review after the verdict.
   - A reviewer's verdict is recorded as returned, `CONVERGENCE_REVIEW_REQUIRED` included.
7. **`rule-dispatch-authoring`** in `specification-ticketing.md`, section "Dispatch normalization" (S61-03, S72-05).
   - The dispatch file of a target project lives at `doc/handoffs/<year>/<feature>/dispatch/<ticket-stem>.md`. The state row names that path beside its digest.
   - On resume, the resuming seat is the submitter of what it commits. The implementer row lists the seats in order.
   - On resume, the resuming seat works in its own worktree under `.worktrees/`. The control plane first checks that the previous seat's worktree is clean and that its commits are on the branch, then removes that worktree's registration. No seat edits another seat's worktree.
   - The review record is `doc/reviews/<feature>/<ticket-stem>-code-review.md`, as `AGENTS.md` lists.
   - In a dispatch, a literal payload goes in backticks; a literal payload is a commit subject, a quoted sentence or a command. Each enumerated item is its own list item. A rationale goes on its own line, never after `; `.

No other sentence changes. A sentence that contradicts one of these rules is a `CHANGE_DETECTED` return naming its file and line; the seat does not reconcile it.

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

1. 正常行為: `tests/test_governance_rule_texts.py` finds each anchor exactly once, in its named file and section. The paragraph after it carries these terms:
   - `rule-content-digest-only`: `digest`;
   - `rule-seat-residue`: `run id`, `STATEMENT`;
   - `rule-process-tier`: `light`, `standard`, `strict`;
   - `rule-smallest-fix`: `rule B`;
   - `rule-consolidated-correction`: `supersede`;
   - `rule-review-label`: `CONVERGENCE_REVIEW_REQUIRED`;
   - `rule-dispatch-authoring`: `doc/handoffs/`, `doc/reviews/`.
2. 規則違反／輸入錯誤:
   - a copy with one anchor removed turns its test red;
   - a copy with one anchor moved to another section turns its test red;
   - a copy with one anchor duplicated turns its test red.
3. 外部失敗／fail-closed: a named file that is missing or not UTF-8 fails the test with the file named.
4. 回歸保護: `tests/test_governance_consistency.py`, `tests/test_adversarial_review_policy.py` and `tests/test_control_plane_mutation.py` pass unchanged.

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
  - `python -m pytest tests/test_governance_rule_texts.py tests/test_governance_consistency.py tests/test_adversarial_review_policy.py tests/test_control_plane_mutation.py -q` exits 0.
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
