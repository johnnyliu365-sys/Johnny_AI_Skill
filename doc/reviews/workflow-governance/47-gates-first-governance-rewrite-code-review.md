# REVIEW-001 — ticket 47 Gates-first governance rewrite (documents only)

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `f4d43817fbcce48188e66c986b23ed7acde42046` on `cp/wave1-gates-first` |
| Baseline | `a1cb6c1` (main) |
| Reviewer | independent seat (Opus); authored nothing in this ticket |
| Reviewed at | 2026-11-03 11:45 +0800 |
| Closure | 47-D1–D5 revision01 + M1 review check + "One observable behavior" |

## Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| D1 | PASS | candidate and main both `3 failed, 120 passed, 563 subtests`; failure sets identical (2 x `temporal_sdk_bridge` DLL blocked by application control policy, 1 x `test_the_pinned_sha_exists` in shallow clone). Extra doc-reading suites (`test_control_plane_mutation`, `test_plugin_distribution_payload_manifest`, `test_private_router_metadata_gate`, `test_ticket_status_template`): 146 passed on both. |
| D2 | PASS | count 1; anchors `workflow-router` (Workflow.md:75) and `role-boundary` (Workflow.md:246) present |
| D3 | PASS | count 1; "The reviewer alone owns the final review conclusion." present once at main and candidate (CodeReview.md:49) |
| D4 | PASS | count 1 (spec:158); R4-1..R4-6 at spec:162,167,180,185,189,193 |
| D5 | PASS | 11 paths == boundary modify/create set exactly; no `forbid` path touched; test diff is one line |
| M1 | PASS (check performed) | exit-code sentence present at Workflow.md:82 and consistent with spec:178 |
| Observable behavior | FAIL | see F-01: Workflow.md still tells the agent to re-enter the Router |

## Findings

| ID | Class (CodeReview §4) | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| F-01 | `IMPLEMENTATION_DEFECT` | High (blocking) | Workflow.md:15-27, :30-31, :38, :92-93 vs :80-82 | Ticket observable behavior: the agent "is no longer told to re-enter a Router". The flowchart (`T --> R`, :26), the stage-order text ("每一個箭頭都必須先以 typed event 回到 Router", :31), :38 ("完成後以 typed event 返回 Router") and 0.1 `AUTO_CONTINUE` ("宣告動作後重新路由", :93) still say so, inside the same file and section the ticket rewrote. :36 shows all eleven stages with no `GREENFIELD` qualifier, contradicting :89. | read candidate Workflow.md; `grep -n "回到 Router\|返回 Router\|T --> R\|重新路由"` → 26, 31, 38, 93 |
| F-02 | `IMPLEMENTATION_DEFECT` | High (blocking) | Workflow.md:84 vs Workflow.md:94, :145, :169; router-control.md:69-76; spec:183 | :84 says `WAIT_FOR_HUMAN` is used **only** for P0, `REQUIREMENT_CHANGED` and forbidden clash. Unchanged :94 in the same section says it is used **only** for Profile-declared approval, owner decision or irreversible external effect (= router-control.md:69). Two competing "only" lists. :84 also drops SPEC/ticket approval waits (route table :145 "approval wait"), the Wayfinder gap wait (:169 `WAIT_FOR_HUMAN / WAYFINDER_INPUT_GAP`) and irreversible effects; the P0 list in AGENTS.md:28-56 does not contain them. R4-3 (spec:183) only restricts what a seat escalates; :84 generalises it to all of `WAIT_FOR_HUMAN`, contradicting spec:160 ("does not change the role boundary, the P0 list ..."). Also `REQUIREMENT_CHANGED` is a return to change control (router-control.md:34-35), not a human wait. | read both files; AGENTS.md P0 sections read |
| F-03 | `IMPLEMENTATION_DEFECT` | High (blocking) | Workflow.md:82; spec:176; CodeReview.md:49-51 | The transition chain "派工 lint → 預檢 → 契約閘門 → 證據閘門 → 整合腳本" has no review step, and the R4-2 integration row ("queue entry fast-forwards ..., affected specs rerun green, remote sha equals ..., then push") does not check a recorded independent `APPROVED` or reviewer ≠ implementer. CodeReview.md:50-51 says `APPROVED` is the integration's admission, but no gate enforces it, so the spec as written admits integration of an unreviewed candidate; this contradicts spec:160 (role boundary unchanged). Chain also omits the coverage-map gate listed at spec:175 and REQ:17. | read spec R4-2 table, Workflow.md:82, CodeReview.md:49-51 |
| F-04 | `TICKET_DEFECT` | High (blocking) | Workflow.md:81, :87-89 vs router-control.md:22-26, :39-42, :86-103, :153-156; adversarial-review.md:30-31; skills/johnny-project-takeover/SKILL.md:24-28 | Section 0 still points to router-control.md (:88) but contradicts it: (a) :81 "live descriptor 都不是 authority" vs router-control.md:93-96 (cross-lifetime path: Private Router owns the live `PendingDispatchDescriptor`, mandatory); (b) :81 persisted metadata includes "路徑" vs router-control.md:40-41 (must not contain filesystem paths); (c) :87 asserts router-control.md's state-machine section "only describes GREENFIELD since Revision 04", but that file is unchanged and still declares itself authoritative for routing behavior (:22-23) and LangGraph/Temporal as the transition composer (:153-156); (d) CodeReview.md:49-51 (integration by script) vs adversarial-review.md:30-31 ("alone owns ... integration"), SKILL.md:27-28 and router-control.md:86-87 (reviewer integrates) — CodeReview.md itself indexes adversarial-review.md. By Workflow.md:85 these are competing references → `HALT / ROUTE_REFERENCE_INVALID` for any agent that follows the documents. Ticket 47 forbids `skills/` and REQ:18 scope does not list these references; no wave schedules their reconciliation (REQ:20 wave 3 retires only the router library). Control plane must widen the boundary or cut a reconciliation ticket before integration. | read router-control.md in full; grep `integrat` in skills references |
| F-05 | `REQUIREMENT_CHANGED` | Medium | spec:164 (R4-1); REQ:16-17; router-control.md:98-103 | R4-1 removes the live descriptor as authority but names no replacement for single-consume / anti-replay / anti-forgery dispatch admission (receipt consumed once; copied, replayed or mismatched ticket/owner/worktree/baseline halts before effect). The CHG "Old rule / New rule" does not say whether that security invariant survives. Checklist item 02's residuals (Grant issuer, `admit_dispatch` wiring) are also not carried (HARNESS-CHANGELOG.md:14). Needs an owner/Grill decision, not a seat's guess. | read REQ, R4-1, router-control.md, checklist rev 135 row 02 |
| F-06 | `TICKET_DEFECT` | Medium (blocks wave-2 dispatch, not this integration) | spec:164, :171-176, :191 | Wave 2 (REQ:20: contract gate, requirement snapshot CLI, merge-queue script, state-file templates) cannot be implemented from Revision 04 without the seat inventing contract: `MERGE-QUEUE.json` has no path, row schema, writer, ordering or concurrency rule (R4-4 allows any budget holder to integrate concurrently); receipt field set unspecified; requirement snapshot has no file format, path or digest algorithm; contract gate terms "spec", "requirement id", "literal expected value", "named mutation" undefined; "affected specs" derivation unspecified; integration row checks remote sha before push but not post-push readback (`LOCAL_INTEGRATED` vs `AUTHORITY_INTEGRATED` / `PUSH_UNCONFIRMED`, router-control.md:128-131) and maps no condition to exit 1 vs 2; dispatch lint `0/1/3` has no code for an unreadable input. | read spec Revision 04 |
| F-07 | `EVIDENCE_DEFECT` | Medium | tests/test_adversarial_review_policy.py:41 | New pin "Integration is executed by the versioned" pins only a sentence prefix that ends before the executor. Mutation M-A (CodeReview.md:50 rewritten to "versioned reviewer, who alone owns integration") → TARA1 PASS; M-B (admission clause replaced with "`APPROVED` is optional") → PASS; only deleting the prefix (M-C) → FAIL. The pin does not pin the new rule (script executor, merge queue, `APPROVED` as admission) and accepts the retired rule. Rest of the test file unchanged (one-line diff). | three mutations, each restored; `git status --porcelain` empty after |
| F-08 | `IMPLEMENTATION_DEFECT` | Medium | doc/HARNESS-CHANGELOG.md:24 | Item 12 disposition "first target run on Vita360 (wave 2 acceptance)": names a target project in the plugin repo, contradicts the checklist's own governing decision (rev 135 header: replay against a real project uses an isolated fixture; generic skill carries no target-specific names; replay cases are fictional) and the owner residual "Host test not authorized", and is not backed by Revision 04 or REQ:10 ("does not authorize ... any target-project write"). | checklist fetched from `codex/skill-improvement-checklist` @ `3913fd65`; rows 02, 03, 12 sampled |
| F-09 | `IMPLEMENTATION_DEFECT` | Low | doc/HARNESS-CHANGELOG.md:15 | Item 03 disposition "dispatch lint script (wave 1)" maps a ticket-content completeness gate (checklist: ticket 45 `ticket_content.py`, residual: Host effect pre-wiring, Expected semantics, dependency readiness) onto a dispatch-form lint; the residuals are dropped. `ticket_content.py` is not on main, so the plugin on this line does not rely on it; record the residuals or say "not carried". Row 09 "kept as review policy" checked: consistent with CodeReview.md §5. | checklist row 03; `ls library/workflow_router/ticket_content.py` → absent |
| F-10 | `IMPLEMENTATION_DEFECT` | Low | modules/tickets/workflow-governance/README.md:31-32 | Rows 47 and 48 are appended after the "Authority and handoff" paragraph with no blank line and no header/delimiter row, so they render as paragraph text, not as entries of the Ticket status table (:11-16). | read file |
| F-11 | `OUT_OF_SCOPE_HARDENING` | Low | Workflow.md:279; CodeReview.md:96 | :279 "指定單一整合者" vs R4-4 "a single fixed integrator ... must not be assumed"; CodeReview.md:96 still has "Router 才可進入 guarded integration" after :49-51 moved integration to a script. Wording drift, not a new rule. | read files |
| F-12 | `OUT_OF_SCOPE_HARDENING` | Low | spec:203; REQ:7; ticket 47 Grant row; ticket 48 P4 | Narrative / vendor names: spec signature "a section-zero loop already proven on real tickets in a target project" (unverifiable claim in a SPEC); "Claude control plane", "Opus", "Sonnet" as fixed model/vendor names; ticket 48 P4 denylist spells target names (`vita360|champion|zeabur|railway|PRD-VITA`). No chat tone found in Workflow.md, CodeReview.md, spec Revision 04. | `git diff -U0 a1cb6c1..HEAD` added lines grepped for target/vendor/narrative terms |
| F-13 | `EVIDENCE_DEFECT` | Low | ticket 47 "Language / return" row | Ticket requires `ImplementationReturn` COMPLETED with commit, document diffs and pytest result; no receipt is in the candidate and none was supplied to the reviewer. All cells were re-run by the reviewer instead. | `git diff --name-only` lists no receipt |

### Answers to the requested judgements

- (a) Section 0 keeps `ACTION_COMPLETED` → `CompletionEvidence` before any next step (Workflow.md:83, :97-98) and keeps `HALT / ROUTE_REFERENCE_INVALID` (:85). It contradicts router-control.md, which it still references, on `WAIT_FOR_HUMAN` scope (F-02), live descriptor authority, metadata paths and its own authority scope (F-04), and contradicts its own file on Router re-entry (F-01).
- (b) Under-specified for wave 2: merge-queue schema/concurrency, receipt fields, requirement-snapshot format, contract-gate terms, post-push readback and exit mapping (F-06); review admission missing from the integration gate (F-03); dispatch anti-replay replacement (F-05).
- (c) Sampled checklist rows 02, 03, 12: 02 loses the dispatch-admission residuals (F-05), 03 mis-maps and drops residuals (F-09), 12 contradicts a checklist decision and names a target (F-08).

## Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | `git clone --no-hardlinks --depth 50 -b cp/wave1-gates-first <repo> C:/Temp/claude/jas47-rv` + autocrlf=false, `rm -r --cached`, `reset --hard` | 0 (HEAD f4d43817fb) |
| 2 | same for `-b main` → `C:/Temp/claude/jas47-main` | 0 (HEAD a1cb6c1) |
| 3 | `git diff --name-only a1cb6c1..HEAD` | 0 (11 paths) |
| 4 | D1 pytest (4 files), candidate | 1 (3 failed / 120 passed) |
| 5 | D1 pytest (4 files), main | 1 (3 failed / 120 passed) |
| 6 | `diff` of the two FAILED sets | 0 (identical) |
| 7 | pytest control_plane_mutation, payload_manifest, private_router_metadata_gate, ticket_status_template — candidate / main | 0 / 0 (146 passed each) |
| 8 | D2 / D3 / D4 greps | 0 (counts 1 / 1 / 1) |
| 9 | `git diff --stat a1cb6c1..HEAD` | 0 (11 files, +218 / -26) |
| 10 | TARA1 under mutations M-A / M-B / M-C, restored after each | 0 / 0 / 1 |
| 11 | `git fetch --depth 1 <repo> codex/skill-improvement-checklist` + `git show FETCH_HEAD:doc/AI-SKILL-IMPROVEMENT-CHECKLIST.md` | 0 (3913fd65) |
| 12 | added-line scan for target/vendor/narrative terms | 0 (hits listed in F-08, F-12) |

Raw pytest logs: `C:/Temp/claude/jas47-rv-pytest-cand.txt`, `-main.txt`, `-cand2.txt`, `-main2.txt`.

Not verified: the full repository test suite (only the eight document-reading suites were run), and Markdown rendering in a real renderer (F-10 is judged from GFM table rules).

## ImplementationReturn (control plane, correction 1)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Candidate | the commit that carries this file (see `git log -1 -- doc/reviews/workflow-governance/47-gates-first-governance-rewrite-code-review.md`) |
| Files | Workflow.md, CodeReview.md, modules/spec/workflow-governance.md, skills/johnny-project-takeover/SKILL.md, skills/johnny-project-takeover/references/router-control.md, skills/johnny-project-takeover/references/adversarial-review.md, doc/HARNESS-CHANGELOG.md, modules/tickets/workflow-governance/README.md, modules/tickets/workflow-governance/47-gates-first-governance-rewrite.md, tests/test_adversarial_review_policy.py |
| Checks | tests/test_workflow_router.py tests/test_plugin_policy_and_response.py tests/test_adversarial_review_policy.py tests/test_plugin_payload_boundary.py: same failure set as main (environment only) |
| Findings | F-01..F-13 dispositions in the ticket Correction 1 table |
| Deviations | none |
