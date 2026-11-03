# REVIEW-001 — ticket 47 Gates-first governance rewrite (documents only)

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `f4d43817fbcce48188e66c986b23ed7acde42046` on `cp/wave1-gates-first` |
| Baseline | `a1cb6c1` (main) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket |
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
| F-08 | `IMPLEMENTATION_DEFECT` | Medium | doc/HARNESS-CHANGELOG.md:24 | Item 12 disposition "first target run on <source-project names>": names a target project in the plugin repo, contradicts the checklist's own governing decision (rev 135 header: replay against a real project uses an isolated fixture; generic skill carries no target-specific names; replay cases are fictional) and the owner residual "Host test not authorized", and is not backed by Revision 04 or REQ:10 ("does not authorize ... any target-project write"). | checklist fetched from `codex/skill-improvement-checklist` @ `3913fd65`; rows 02, 03, 12 sampled |
| F-09 | `IMPLEMENTATION_DEFECT` | Low | doc/HARNESS-CHANGELOG.md:15 | Item 03 disposition "dispatch lint script (wave 1)" maps a ticket-content completeness gate (checklist: ticket 45 `ticket_content.py`, residual: Host effect pre-wiring, Expected semantics, dependency readiness) onto a dispatch-form lint; the residuals are dropped. `ticket_content.py` is not on main, so the plugin on this line does not rely on it; record the residuals or say "not carried". Row 09 "kept as review policy" checked: consistent with CodeReview.md §5. | checklist row 03; `ls library/workflow_router/ticket_content.py` → absent |
| F-10 | `IMPLEMENTATION_DEFECT` | Low | modules/tickets/workflow-governance/README.md:31-32 | Rows 47 and 48 are appended after the "Authority and handoff" paragraph with no blank line and no header/delimiter row, so they render as paragraph text, not as entries of the Ticket status table (:11-16). | read file |
| F-11 | `OUT_OF_SCOPE_HARDENING` | Low | Workflow.md:279; CodeReview.md:96 | :279 "指定單一整合者" vs R4-4 "a single fixed integrator ... must not be assumed"; CodeReview.md:96 still has "Router 才可進入 guarded integration" after :49-51 moved integration to a script. Wording drift, not a new rule. | read files |
| F-12 | `OUT_OF_SCOPE_HARDENING` | Low | spec:203; REQ:7; ticket 47 Grant row; ticket 48 P4 | Narrative / vendor names: spec signature "a section-zero loop already proven on real tickets in a target project" (unverifiable claim in a SPEC); "Claude control plane", "Opus", "Sonnet" as fixed model/vendor names; ticket 48 P4 denylist spells target names (`<source-project names>|<source-project name>|<source-project name>|<source-project name>|<source-project name>`). No chat tone found in Workflow.md, CodeReview.md, spec Revision 04. | `git diff -U0 a1cb6c1..HEAD` added lines grepped for target/vendor/narrative terms |
| F-13 | `EVIDENCE_DEFECT` | Low | ticket 47 "Language / return" row | Ticket requires `ImplementationReturn` COMPLETED with commit, document diffs and pytest result; no receipt is in the candidate and none was supplied to the reviewer. All cells were re-run by the reviewer instead. | `git diff --name-only` lists no receipt |

### Answers to the requested judgements

- (a) Section 0 keeps `ACTION_COMPLETED` → `CompletionEvidence` before any next step (Workflow.md:83, :97-98) and keeps `HALT / ROUTE_REFERENCE_INVALID` (:85). It contradicts router-control.md, which it still references, on `WAIT_FOR_HUMAN` scope (F-02), live descriptor authority, metadata paths and its own authority scope (F-04), and contradicts its own file on Router re-entry (F-01).
- (b) Under-specified for wave 2: merge-queue schema/concurrency, receipt fields, requirement-snapshot format, contract-gate terms, post-push readback and exit mapping (F-06); review admission missing from the integration gate (F-03); dispatch anti-replay replacement (F-05).
- (c) Sampled checklist rows 02, 03, 12: 02 loses the dispatch-admission residuals (F-05), 03 mis-maps and drops residuals (F-09), 12 contradicts a checklist decision and names a target (F-08).

## Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | `git clone --no-hardlinks --depth 50 -b cp/wave1-gates-first <repo> <fresh clone>` + autocrlf=false, `rm -r --cached`, `reset --hard` | 0 (HEAD f4d43817fb) |
| 2 | same for `-b main` → a second fresh clone | 0 (HEAD a1cb6c1) |
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

Raw pytest logs: retained by the reviewer seat on its host; not committed (the revision02 review commits its full-suite logs under `evidence/47/`).

Not verified: the full repository test suite (only the eight document-reading suites were run), and Markdown rendering in a real renderer (F-10 is judged from GFM table rules).

## Correction 1 re-review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `d581ebc` (parent `f4d4381`) on `cp/wave1-gates-first` |
| Re-reviewed at | 2026-11-03 11:53 +0800 |
| Clone | fresh `--depth 50` clone, `core.autocrlf=false`, index rebuilt to LF |
| Scope | F-01..F-13 plus defects introduced by the correction |

### Per-finding status

| ID | Status | Evidence |
| --- | --- | --- |
| F-01 | CLOSED | Workflow.md:79 defines "Router" as running the gate scripts over the state files and says how to read "回到 Router" / "返回 Router" in this file and in router-control.md. SKILL.md:17-19 item 4 and router-control.md:7-17 (Revision 04 note) say the same. Read this way, :26, :31, :38 and :93 are now consistent. Low residual: the reading rule names only "本檔" and router-control.md. AGENTS.md:18 ("回到 Router"), SKILL.md:92 ("route again") and codex-native-same-lifetime-delegation.md:39 are outside that stated scope. They are readable only through the general definition. |
| F-02 | CLOSED | Workflow.md:84 defers to router-control.md Continuation rule 2 (router-control.md:81-88: Profile approval, owner decision, irreversible effect, Wayfinder gap). It treats R4-3 as a filter. Workflow.md:94 and :169 now agree. spec:183 still says "only" but limits it to what a seat escalates, so it does not compete. |
| F-03 | PARTIAL | spec:176 and Workflow.md:82 now require an independent review record with verdict `APPROVED` before integration. Residual (Medium, IMPLEMENTATION_DEFECT): the R4-7 queue field `review` (spec:201) is only "path of the review record whose verdict is `APPROVED`". Nothing binds the record to `candidate`, and reviewer ≠ implementer/submitter is never checked, so the gate cannot enforce "independent": a submitter can commit their own `APPROVED` record. The coverage-map gate is still missing from the Workflow.md:82 chain (Low). |
| F-04 | PARTIAL | Fixed: adversarial-review.md:30-32, Workflow.md:81 (paths removed, bridge stated as transitional) and router-control.md authority scope via the note. Not fixed, although the ticket's Correction 1 table says "edited at their lines": SKILL.md:27-28 still makes the reviewer "the owner of delegation, waiting, review and integration", and router-control.md:99 still says "the reviewer dispatches, waits, receives, reviews and integrates". Both compete with CodeReview.md:49-51 and R4-4, which triggers `HALT / ROUTE_REFERENCE_INVALID` under Workflow.md:85. |
| F-05 | PARTIAL | R4-1 (spec:164) and R4-7 (spec:201) now state single-consume and anti-replay: a (ticket, candidate) key, terminal states refused, and compare-and-swap on the queue commit and the remote tip. router-control.md:13-16 repeats this. The invariant now sits at integration, the only external effect; that design is acceptable. Residual (Low): the Correction 1 table says "Owner decision recorded", but REQ-20261103-043 is unchanged (no diff f4d4381..d581ebc). There is no new Revision Signature row (spec:212 is still the original) and no owner record anywhere in the candidate. |
| F-06 | PARTIAL | R4-7 adds the queue entry, receipt cell, snapshot row, contract-gate codes, post-push readback and exit mapping. Residual (Medium, TICKET_DEFECT; blocks the wave-2 merge-queue ticket, not this integration): (1) "one lock row per run, released by the same run" has no schema and no recovery for a run that dies holding it. That contradicts REQ:8 ("a session that dies loses nothing") and leaves the queue permanently locked. (2) No state is defined for the entry when CI on the landed sha is red after the push. (3) The queue file path and the derivation of "affected specs" are still unspecified. (4) The snapshot row has no file format or location. |
| F-07 | PARTIAL | Requested check: restoring CodeReview.md to the main sentence turns TARA1 red (`SUBFAILED term='is its admission, not its executor'`, exit 1). Mutation M-B (admission weakened to "`APPROVED` is optional") is also red. Mutation M-A ("Integration is executed by the versioned reviewer, who alone owns integration; the review `APPROVED` is its admission, not its executor") still passes, exit 0. The executor (integration script, merge queue) is not pinned, so the pin accepts the retired rule. Residual Medium, EVIDENCE_DEFECT. |
| F-08 | CLOSED | `grep -ciE "<source-project names>" doc/HARNESS-CHANGELOG.md` → 0; :24 reads "first run on a target project". |
| F-09 | CLOSED | HARNESS-CHANGELOG.md:14-15 carry the residuals of items 02 and 03 to wave 2. |
| F-10 | CLOSED | README.md: rows 47 and 48 sit at lines 17-18, inside the status table, before "## Shared baseline". |
| F-11 | OPEN (non-blocking, OUT_OF_SCOPE_HARDENING) | Workflow.md:279 and CodeReview.md:96 are unchanged. The ticket table says "deferred to wave 2 tickets", but no `PLANNED` ticket carries it, as CodeReview.md §4 item 5 requires. |
| F-12 | OPEN (non-blocking, OUT_OF_SCOPE_HARDENING) | spec:212 is unchanged; same note as F-11. |
| F-13 | CLOSED | The review record with `ImplementationReturn` is committed at doc/reviews/workflow-governance/47-gates-first-governance-rewrite-code-review.md. Its content is false; see N-02. |

### New findings introduced by correction 1

| ID | Class (CodeReview §4) | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| N-01 | `IMPLEMENTATION_DEFECT` (the fix needs a boundary change by the control plane) | High (blocking) | skills/johnny-project-takeover/references/router-control.md (whole file); library/workflow_router/profile.py:209-210; tests/test_workflow_router.py:296-297, :756-761, :2437 | Editing router-control.md changed its content digest from `sha256_8ac50716…` to `sha256_a35c381e…`, but the pin sits in library/workflow_router/profile.py and test_workflow_router.py. D1 now fails: `SUBFAILED(policy='router-control') RouteInstructionContractTests::test_profile_route_table_and_policy_metadata_are_exact`. Main passes that test. A second doc suite also turns red: `SUBFAILED(policy='router-control') test_control_plane_mutation.py::PolicyPinTests::test_the_recomputed_digest_matches_the_repository_s_own_pin`, where main had 146/146 green. The ticket boundary still forbids `library/` and does not list tests/test_workflow_router.py. | D1 pytest: 4 failed (3 environment failures + 1 new subfail) / 120 passed / 562 subtests, exit 1. Extra suites: 1 failed / 146 passed, exit 1. `git grep 8ac507168f938503` → profile.py + test file. |
| N-02 | `EVIDENCE_DEFECT` | High (blocking) | doc/reviews/workflow-governance/47-gates-first-governance-rewrite-code-review.md, `ImplementationReturn` "Checks" row | The record says the four D1 files give the "same failure set as main (environment only)" and lists "Deviations: none". Both are false (N-01), and no raw output is attached. | reviewer re-ran D1 in a fresh clone |
| N-03 | `IMPLEMENTATION_DEFECT` | Low | Workflow.md:81 vs spec:201-203 | Workflow.md:81 says the persisted state "不含檔案系統路徑". R4-7 makes the state files carry paths: queue `review`, receipt `capture`, `tool_digest` `path=sha256`, snapshot `source_ref` "URL or path". State that repository-relative artifact references are allowed and host filesystem paths or URIs are not, or align the two. | read both |
| N-04 | `TICKET_DEFECT` | Low | doc/requirements/active/2026/workflow-governance/REQ-20261103-043.md:18; ticket 47 boundary | The boundary was widened to SKILL.md, router-control.md, adversarial-review.md and the review record "under CHG-20261103-043", but the CHG Scope row still lists only Workflow.md section 0, the CodeReview clause, the checklist, the new scripts, tests and the SPEC revision. | `git diff f4d4381..d581ebc --stat -- doc/requirements` → empty |

### Commands (correction 1)

| # | Command | Exit |
| --- | --- | --- |
| 1 | `git clone --no-hardlinks --depth 50 -b cp/wave1-gates-first <repo> <fresh clone>` + LF normalisation | 0 (HEAD d581ebc) |
| 2 | `git diff --stat f4d4381..HEAD`; `git diff --name-only a1cb6c1..HEAD` | 0 (10 files +140/-18; 15 paths, all in the widened boundary) |
| 3 | D1 pytest (4 files) | 1 (4 failed: 3 environment failures identical to main + `SUBFAILED policy='router-control'`) |
| 4 | `diff` of the FAILED lines against the main log | 0, but this diff hides the SUBFAILED line; checked the summary by hand |
| 5 | pytest control_plane_mutation, payload_manifest, private_router_metadata_gate, ticket_status_template | 1 (1 failed / 146 passed; main 0) |
| 6 | TARA1 under M-old / M-A / M-B, restored after each, `git status --porcelain` empty | 1 / 0 / 1 |
| 7 | F-08..F-12 greps and reads | 0 |
| 8 | `git grep` of the router-control digest prefix | 0 (profile.py:209-210, test_workflow_router.py:296-297, 756-761, 2437) |

Raw log: retained by the reviewer seat on its host; not committed.

Not verified: the full repository test suite, and whether an owner decision for F-05 exists outside the repository.

## ImplementationReturn (control plane, closure revision02)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Candidate | the commit that carries this file (`git log -1 -- doc/reviews/workflow-governance/47-gates-first-governance-rewrite-code-review.md`) |
| Files | AGENTS.md, Workflow.md, CodeReview.md, modules/spec/workflow-governance.md, doc/requirements/active/2026/workflow-governance/REQ-20261103-043.md, skills/johnny-project-takeover/SKILL.md, references router-control.md / adversarial-review.md / codex-native-same-lifetime-delegation.md, library/workflow_router/profile.py, tests/test_workflow_router.py, tests/test_adversarial_review_policy.py, modules/tickets/workflow-governance/47-*.md, 49-*.md, README.md, doc/HARNESS-CHANGELOG.md |
| D6 full suite | `11 failed, 1918 passed, 31 skipped, 15 warnings, 3950 subtests passed in 222.22s (0:03:42)`; raw: `doc/reviews/workflow-governance/evidence/47/c2-pytest-full.txt` |
| D6 failure set | tests/test_atomic_conditional_replace_capability.py::test_acr2_linux_requires_an_actual_linux_kernel_and_backend; tests/test_atomic_conditional_replace_capability.py::test_acr6_exact_test_only_boundary; tests/test_guarded_integration_corrections.py::ReceiptBoundCorrectionTests::test_reviewed_router_profile_composes_return_integration_and_audit; tests/test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists; tests/test_plugin_publication.py::CandidateMetadataTests::test_l5_stale_candidate_pin_is_named_before_generation; tests/test_plugin_publication.py::PinnedTreeBindingTests::test_pinning_the_root_commit_is_rejected; tests/test_plugin_publication.py::PublicationReachabilityTests::test_deleting_the_actual_publication_anchor_makes_the_marketplace_pin_unreachable; tests/test_plugin_publication.py::PublicationReachabilityTests::test_the_marketplace_pin_is_bound_to_the_actual_publication_anchor; tests/test_refusal_guidance.py::ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered; tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services; tests/test_workflow_router.py::WorkflowRouterTests::test_temporal_approval_signal_requires_matching_authority_state |
| D6 comparison | identical to the main `a1cb6c1` baseline measured in the same environment (11 names); the ticket 48 seat measured 12 at `f4d4381` with `test_acr6_committed_candidate_diff_and_forbidden_paths` additionally red, so that test is environment-sensitive and is listed as a deviation, not claimed green |
| F-07 mutation | old integration sentence restored in a disposable edit: `2 failed, 7 passed, 71 subtests passed in 0.10s`; raw: `doc/reviews/workflow-governance/evidence/47/c2-mutation-F07.txt` |
| Policy pin | router-control.md digest moved to `rev-59038c10683e71ea` in profile.py and test_workflow_router.py |
| Deviations | the 11 baseline failures are environment or publication-pin failures not addressed by this ticket; one ACR test varies between runs |

## Revision02 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `9e02e95` on `cp/wave1-gates-first` (Closure revision02, 47-D1–D6) |
| Review kind | initial review of revision02 (CodeReview.md §5 re-plan; not a third correction) |
| Reviewed at | 2026-11-03 12:12 +0800 |
| Clones | fresh `--depth 50` clones of the candidate and of main `a1cb6c1`, `core.autocrlf=false`, index rebuilt to LF |

### Cells

| Cell | Result | Evidence |
| --- | --- | --- |
| Boundary / D5 | PASS | `git diff --name-only a1cb6c1..9e02e95` gives 22 paths, all in the boundary block (`create = doc/reviews/workflow-governance/evidence/47/` covers the 2 evidence files). No path under `.github/`, `.claude-plugin/`, `.codex-plugin/` or `template/` is touched. |
| D1 | PASS | `3 failed, 121 passed, 564 subtests`, same 3 environment failures as main (2 × temporal DLL blocked, 1 × pinned sha in shallow clone). The router-control subtest is green. |
| D2 | **FAIL** | `grep -c "狀態在檔案，轉移在腳本" Workflow.md` → **0**, expected 1. Correction 1 replaced that phrase at Workflow.md:79 and revision02 did not update the cell. Anchors `workflow-router` and `role-boundary` are present (2). |
| D3 | **FAIL** | `grep -c "Revision 04 R4-4" CodeReview.md` → **2** (CodeReview.md:50, :97), expected 1. "The reviewer alone owns the final review conclusion." is present once and unchanged. |
| D4 | PASS | count 1; `### R4-1`..`### R4-7` present (7) |
| D6 | PASS with deviation | Reviewer full suite on the candidate: `12 failed, 1917 passed, 31 skipped, 3950 subtests`, exit 1. On main: `12 failed, 1916 passed, 31 skipped, 3949 subtests`, exit 1. The two failure-name sets are **identical** (12 names). The receipt raw (`evidence/47/c2-pytest-full.txt`) has 11 names. The extra name in both of my runs is `test_atomic_conditional_replace_capability.py::test_acr6_committed_candidate_diff_and_forbidden_paths` (`RuntimeError: ticket authority baseline is not an ancestor of candidate`, depth-dependent). The receipt already states this as the ACR deviation. The +1 pass on the candidate is the new `test_tara1b`. |
| M1 | PASS (check performed) | exit-code sentence present at Workflow.md:82 |

### Per-item status

| Item | Status | Evidence |
| --- | --- | --- |
| N-01 | CLOSED | `PolicyPinTests` + `RouteInstructionContractTests::test_profile_route_table_and_policy_metadata_are_exact`: `8 passed, 35 subtests`. The digest moved to `rev-59038c10683e71ea` in profile.py:209-210 and test_workflow_router.py:296-297, :756-761, :2437. |
| N-02 | CLOSED (Low residual, see R2-02) | The receipt D6 failure set matches the committed raw output (11 names). The deviation about the environment-sensitive ACR test is stated and agrees with my runs. |
| N-03 | CLOSED | Workflow.md:81 allows repository-relative paths and excludes host absolute paths; router-control.md:17-19 says the same. |
| N-04 | CLOSED | REQ:18 lists the widened files, including the profile.py and test_workflow_router.py pins. |
| F-01 leftovers | CLOSED | AGENTS.md:18, SKILL.md:94 and codex-native-same-lifetime-delegation.md:39 now say record-then-gate. The remaining "route again" at router-control.md:82 is covered by the Workflow.md:79 reading rule. |
| F-03 | CLOSED (Low residual) | spec:201 adds `review_candidate` (must equal `candidate`) and `submitter` != `reviewer`. Workflow.md:82 states the same and adds the coverage-map guard. Residual: R4-7 does not say these two values are read from the review record rather than taken from the queue row the submitter writes. Workflow.md:82 implies the record. The wave-2 ticket must make it explicit. |
| F-04 | CLOSED | SKILL.md:27-31 and router-control.md:100-102 now route integration to the versioned script. `grep` finds no remaining "reviewer … integrates" in skills/, Workflow.md, CodeReview.md or AGENTS.md. |
| F-05 | RECORDED, owner confirmation pending | REQ:19 "Open owner decision" row and spec signature row 2. Both state that the control plane decided and that the owner has not yet confirmed. This must be confirmed before integration onto `main`. |
| F-06 | CLOSED (Low residual, see R2-05) | spec:201-203 add the queue path, `LANDED_CI_RED`, the affected-spec rule, lock reclaim and the snapshot file and location. |
| F-07 | PARTIAL (Low, `EVIDENCE_DEFECT`, non-blocking) | M-old (main sentence restored) → 3 red (both pinned halves + `tara1b`), exit 1. M-B (admission weakened) → red. M-A keeps both pinned halves and swaps the executor ("Integration is executed by the versioned reviewer seat, who runs the merge by hand …") → `8 passed`, exit 0. The executor phrase sits between the two pins across a line break and is still unpinned. `tara1b` is a denylist of two literal strings. Fix: pin the whitespace-normalised phrase "Integration is executed by the versioned integration script from the merge queue". |
| F-11 | CLOSED | Workflow.md:279 and CodeReview.md:96-97 now name the integration script. |
| F-12 | CLOSED (tracked) | spec signature narrative removed; vendor/model names carried by ticket 49 (`PLANNED`) |

### New findings on revision02

| ID | Class (CodeReview §4) | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| R2-01 | `TICKET_DEFECT` | High (blocking) | ticket 47 Acceptance D2, D3; Workflow.md:79; CodeReview.md:50, :97 | Two frozen cells are red against the delivered text: D2 = 0 (expected 1) and D3 = 2 (expected 1). Both changes are intended content: the section-0 phrase was rewritten in correction 1, and CodeReview §5 now also cites R4-4. The revision02 re-plan kept the old expectations, so the control plane must re-freeze D2 and D3. Restoring the old text would reopen F-01 / F-11. | the greps in "Cells" above |
| R2-02 | `EVIDENCE_DEFECT` | Low | review record, `ImplementationReturn (closure revision02)`; evidence/47/c2-pytest-full.txt | The ImplementationReturn reports only D6 and F-07. There are no D1–D5 results for revision02, which is how R2-01 went unreported. The raw capture has no header naming the candidate sha or the command. | read the record and the raw file |
| R2-03 | `IMPLEMENTATION_DEFECT` | Medium (blocking) | AGENTS.md:20-21 vs Workflow.md:81; spec:164 | AGENTS.md still says every pending implementation dispatch must be bound by the live descriptor, a receipt and exact artifact references. Workflow.md:81 and R4-1 say pending dispatch is ticket state plus queue rows, with the descriptor only a transitional cross-lifetime path. Under Workflow.md:85 these are competing references. AGENTS.md is already in the boundary. | read both |
| R2-04 | `TICKET_DEFECT` | Low | ticket 47 "Profile / limits" row; REQ:20 "Effect boundary" | Both still say "documents only; no runtime", but the candidate edits `library/workflow_router/profile.py` (the pinned policy constants). State the exception: pin constants move with the document; no behaviour change. | `git diff a1cb6c1..9e02e95 -- library/` |
| R2-05 | `IMPLEMENTATION_DEFECT` | Low | router-control.md:15 vs spec:201 | The router-control note lists the refused terminal states as `LANDED` or `BOUNCED`; R4-7 adds `LANDED_CI_RED`. Wave-2 gaps that remain under-specified: "run id is not live" has no cross-host liveness test; how `LANDED_CI_RED` is cleared is not specified; `pages.json` is used in the affected-spec rule without a definition. | read both |

### Commands (revision02)

| # | Command | Exit |
| --- | --- | --- |
| 1 | fresh clones of `cp/wave1-gates-first` (HEAD 9e02e95) and `main` (a1cb6c1), LF-normalised | 0 / 0 |
| 2 | `git diff --name-only a1cb6c1..HEAD` vs boundary block | 0 (22 paths, all covered) |
| 3 | `pytest tests -q` candidate, then main, run one after the other | 1 / 1 (12 failed each; name sets identical) |
| 4 | diff of my candidate failure set vs receipt raw | 1 (receipt lacks `test_acr6_committed_candidate_diff_and_forbidden_paths`; deviation already stated) |
| 5 | D1 pytest (4 files) | 1 (3 environment failures, same as main) |
| 6 | PolicyPinTests + route-table policy test | 0 (8 passed) |
| 7 | D2 / D3 / D4 greps | counts 0 / 2 / 1 (D2, D3 red) |
| 8 | TARA under M-old / M-A / M-B, restored after each, `git status --porcelain` empty | 1 / 0 / 1 |
| 9 | greps for remaining reviewer-integrates and re-enter-Router sentences | 0 (none outside the covered reading rule) |

Raw logs: `doc/reviews/workflow-governance/evidence/47/rev02-review-pytest-full-cand.txt`, `doc/reviews/workflow-governance/evidence/47/rev02-review-pytest-full-main.txt` (committed copies of the reviewer seat's files).

Not verified: whether the owner has confirmed the F-05 decision; Markdown rendering in a real renderer.

## ImplementationReturn (control plane, closure revision03)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Candidate | `fb55623f747039d24555fab0e5017831da9926ac` (content); the commit that carries this section adds only evidence files under `evidence/47/`, `evidence/49/` and this record (`git diff fb55623..HEAD --stat`) |
| Re-plan commit | `3ffe1b12` (tickets re-frozen before the fix); content commit `fb55623` |
| D1 | PASS — `3 failed, 121 passed, 564 subtests passed in 5.27s`; the three failures are the environment set of main (two temporal DLL loads blocked by application control policy, one pinned sha absent in this clone); raw `evidence/47/rev03-D1.txt` |
| D2 | PASS — count 1; anchors `workflow-router` and `role-boundary` present (1 / 1); raw `evidence/47/rev03-D2.txt` |
| D3 | PASS — count 2; the reviewer sentence present once; raw `evidence/47/rev03-D3.txt` |
| D4 | PASS — `## Revision 04` once; `### R4-1`..`R4-7` seven; raw `evidence/47/rev03-D4.txt` |
| D5 | PASS — every path in `a1cb6c1..HEAD` is in ticket 47's boundary block or (the ticket 49 review record and evidence directory) in ticket 49's; raw `evidence/47/rev03-D5.txt` |
| D6 | PASS — `10 failed, 1919 passed, 31 skipped, 15 warnings, 3950 subtests passed in 227.21s (0:03:47)`; failure set vs the revision02 reviewer's main run (`rev02-review-pytest-full-main.txt`, 12 names): extra on candidate = none; absent on candidate = ['tests/test_atomic_conditional_replace_capability.py::test_acr6_committed_candidate_diff_and_forbidden_paths', 'tests/test_plugin_publication.py::PinnedTreeBindingTests::test_pinning_the_root_commit_is_rejected']; raw `evidence/47/rev03-D6-full.txt` |
| M1 | check performed — with the exit-code bullet removed in a disposable edit the exit-code phrase counts 0 while D2 still counts 1; the loss is visible to a reader only, as the ticket says; file restored, worktree clean; raw `evidence/47/rev03-M1.txt` |
| F-07 mutation | executor reworded to "the versioned reviewer seat, who runs the merge by hand" → `1 failed, 7 passed, 72 subtests passed in 0.10s` (`test_tara1b` red); restored; raw `evidence/47/rev03-F07-mutation.txt` |
| Policy pin | router-control.md digest moved to `rev-8d6082758541d385` in profile.py and test_workflow_router.py |
| Deviations | the D6 failures are the environment and publication-pin set already recorded for this environment; one ACR test varies between runs and is listed by name above when it differs |

## Revision03 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `34997e8f` (evidence commit); content commit `fb55623f`; re-plan commit `3ffe1b12` |
| Baseline | `a1cb6c1` (main) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket |
| Clones | fresh `--no-hardlinks` clones of the candidate and of main, `core.autocrlf=false`, index rebuilt to LF |
| Summary | Every executable cell is green and the failure sets on the candidate and on main are identical. Two things block approval: three live references still give the integration role to the reviewer, against CodeReview.md and R4-4; and router-control.md disagrees with Workflow.md section 0 and AGENTS.md on the cross-lifetime dispatch path. Workflow.md:85 sends any agent that meets either conflict to `HALT / ROUTE_REFERENCE_INVALID`. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| D1 | PASS | Candidate `3 failed, 121 passed, 564 subtests`; main `3 failed, 120 passed, 563 subtests`; identical failure-name sets (two temporal DLL tests blocked by application control policy, `test_the_pinned_sha_exists`); no SUBFAILED lines. |
| D2 | PASS | `狀態只存在三種檔案` count 1 (Workflow.md:81); `id="workflow-router"` 1; `id="role-boundary"` 1. |
| D3 | PASS | `Revision 04 R4-4` count 2 (CodeReview.md:50, :97); the reviewer sentence once at :49, unchanged from main. |
| D4 | PASS | `^## Revision 04` 1; `### R4-1`..`R4-7` at spec:162, 167, 180, 185, 189, 193, 199. |
| D5 | PASS | 36 paths (22 A, 14 M), all covered by the union of the ticket 47 and ticket 49 `modify`/`create` entries; 0 uncovered; 0 under forbid paths. Caveat: the D5 Expected text was changed inside the evidence commit (R3-04). |
| D6 | PASS | Candidate `10 failed, 1919 passed, 31 skipped, 3950 subtests`, exit 1; main `10 failed, 1918 passed, 31 skipped, 3949 subtests`, exit 1; the two 10-name sets identical and identical to the receipt raw. Composition: 2 ACR, guarded-integration profile, pinned sha, 3 publication-pin, refusal enum audit, 2 temporal DLL. The +1 pass is `test_tara1b`. |
| M1 | PASS (check performed) | Exit-code bullet removed as a disposable edit: D2 stays 1, the exit-code phrase drops to 0, the doc suites still give only the 3 environment failures, so only a reader notices the loss. Restored; porcelain empty. |
| Observable behavior | PARTIAL | Workflow.md section 0 and CodeReview.md:49-51 read as the ticket states. Three references CodeReview.md indexes still name the reviewer as integrator (R3-01, R3-02). |

### Re-plan rows

| Row | Status | Evidence |
| --- | --- | --- |
| R2-01 | CLOSED | D2 = 1 and D3 = 2 on the delivered text; text not reverted. |
| R2-02 | CLOSED | Results for D1–D6, M1 and F-07; all 8 `rev03-*.txt` captures headed with cell, candidate `fb55623f…`, command. One statement is false (R3-04). |
| R2-03 | CLOSED | AGENTS.md:20-22 matches Workflow.md:81 and R4-1. Remaining conflict with router-control.md:108 filed as R3-03. |
| R2-04 | CLOSED | Profile row and REQ effect boundary state the pin exception; the `library/` diff is exactly the 2 pin constants. |
| R2-05 | PARTIAL | router-control.md:15 lists the three terminal states; lock reclaim and `pages.json` defined at spec:201; the clearing rule cannot be satisfied as written (R3-05). |
| F-03 residual | CLOSED | spec:201 reads `review_candidate` and `reviewer` from the record; `REVIEW_MISMATCH` defined; Workflow.md:82 agrees. Record format unspecified (R3-06). |
| F-07 residual | CLOSED | MUT-A (executor reworded to a reviewer seat running the merge by hand): `test_tara1b` FAILED, `1 failed, 7 passed`, exit 1; restored. Counter-mutations through other doors stay green (R3-07). |
| F-05 | OPEN (recorded, non-blocking for this review) | REQ row and spec signature row say owner confirmation is pending and gates integration onto `main`. |
| R49-06 | CLOSED | No drive-letter path in tickets 47, 48, the README or the 47 review record. Committed captures still carry host paths (R3-09). |
| D5 wording | PARTIAL | The union wording matches the branch; the Expected change was made in evidence commit `34997e8f`, after content commit `fb55623f`, with no new closure revision (R3-04). |
| Router-control digest pin | CLOSED | `policy_digest(router-control.md)` = `rev-8d6082758541d385`, equal at all six pin sites; PolicyPinTests 7 passed; test_control_plane_mutation.py 54 passed. |
| Profile / Workspace rows | CLOSED | Workspace row has no host path; Profile row states the pin exception. |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| R3-01 | `TICKET_DEFECT` | High (blocking) | references/delivery-profile.md:75-76; references/model-role-routing.md:24; modules/spec/review-assurance.md:68 (ARA-01) | Unchanged from main and still say the reviewer integrates: "The reviewer retains the final review conclusion and integration"; `SUPERVISOR_REVIEWER` owns "… independent review, correction routing and guarded integration"; ARA-01 requires CodeReview.md to state "the reviewer alone owns review conclusion and integration". All three compete with CodeReview.md:49-51, R4-4 and Workflow.md:279. CodeReview.md §2 indexes both references; REQ-20261103-043 says it amends `CHG-20260827-042` (the review-assurance CHG), yet that SPEC has no revision. Revision02 claimed to widen the closure to "every file that states who integrates", but these paths are outside both boundary blocks. Under Workflow.md:85 this is `HALT / ROUTE_REFERENCE_INVALID`. Widen the boundary or cut a reconciliation ticket. | `grep -rniE integrat skills/` filtered; main shows the same lines; `git diff a1cb6c1..34997e8f --stat` on the three files is empty |
| R3-02 | `IMPLEMENTATION_DEFECT` | Medium (blocking) | references/codex-native-same-lifetime-delegation.md:22-23 | In the boundary and edited in this ticket, yet still says the reviewer "remains responsible for waiting, receiving the typed result, review, reverse mutation and integration gates": assumes a fixed integrator, against R4-4, SKILL.md:28-30 and router-control.md:101-102. | read file |
| R3-03 | `IMPLEMENTATION_DEFECT` | Medium (blocking) | router-control.md:108 vs Workflow.md:81, AGENTS.md:22; spec:201 | router-control.md:108: "The receipt-bound bridge remains mandatory for a cross-lifetime handoff"; Workflow.md:81 and AGENTS.md:22: usable but no longer the default, the default is the queue file. Competing rules on authoritative dispatch state. Also, the R4-7 queue entry needs `candidate` (full sha) and a review record and has no owner, worktree, branch or baseline fields, so a pending implementation dispatch cannot be a queue row; the stated "default" path cannot be implemented as specified. | read the three files and spec:201 |
| R3-04 | `TICKET_DEFECT` | Medium | ticket 47 D5 Expected and its "D5 wording" row; review record ImplementationReturn "Candidate" row | `git diff fb55623..34997e8f` changes the frozen D5 Expected and adds the "D5 wording" row inside the receipt commit, after the content commit, while the closure is still labelled revision03; the original D5 is red on the candidate, so the cell was re-frozen after delivery. The receipt also says the commit "adds only evidence files … and this record" while it also changes ticket 47 and the ticket 49 review record. Same shape as ticket 49's R49-02. | `git diff --name-only fb55623..34997e8f` (14 paths, including the ticket) |
| R3-05 | `IMPLEMENTATION_DEFECT` | Low (blocks the wave-2 merge-queue ticket) | spec:201 | `LANDED_CI_RED` "blocks further landings until cleared" while clearing needs "a later entry whose `reason` names the red entry lands": the fix entry cannot land while landings are blocked; no exemption stated: a deadlock. `reason` is overloaded with bounce codes. | read R4-7 |
| R3-06 | `TICKET_DEFECT` | Low (wave 2) | spec:201 | The integration script must read `review_candidate`, `reviewer` and the `APPROVED` verdict from the review record, but no record schema is defined; the repository's records append several reviews to one file with different candidates and verdicts, so which section is read is unspecified; `reviewer` is a role label, not an identity `submitter != reviewer` can compare. | read the record and R4-7 |
| R3-07 | `OUT_OF_SCOPE_HARDENING` | Low | tests/test_adversarial_review_policy.py | Counter-mutations through other doors stay green: MUT-B rewrote CodeReview.md:49-51 so the reviewer "runs every merge personally" and quoted the pinned phrase as a "retired draft line" (`8 passed`); MUT-C reverted adversarial-review.md:30-32 to "alone owns the final review conclusion and integration." (`8 passed`; D1 files and control_plane_mutation only the 3 environment failures). The integrator rule is pinned in CodeReview.md only, as a literal phrase. | mutations restored, porcelain empty |
| R3-08 | `EVIDENCE_DEFECT` | Low | evidence/47/rev03-D6-full.txt:47, :90, :207 | The D6 capture shows the worktree path of the primary checkout: the receipt's full suite ran in the primary working checkout, not in the disposable clone the Workspace row names, and the capture does not prove the tree state at `fb55623`. The reviewer's run in a disposable clone reproduces the same 10 names. | read capture |
| R3-09 | `OUT_OF_SCOPE_HARDENING` | Low | evidence/47/rev03-D1.txt, rev03-D6-full.txt, rev03-F07-mutation.txt | Committed captures carry host absolute paths (venv, user-profile checkout, temp). Sits awkwardly with the R49-06 disposition and Workflow.md:81; no cell catches it. | drive-letter grep over `evidence/47/*.txt` |

Added-line scan of `a1cb6c1..34997e8f`, excluding evidence: no external target-project name; no host absolute path; no vendor or model literal in live role rows (hits are branch identifiers, the `codex-native` file name and quoted historical findings); no chat tone or unverifiable narrative.

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1–3 | fresh LF clones of the candidate and main (system `core.autocrlf=true` overridden locally; index rebuilt) | 0 |
| 4–5 | D6 candidate, then main, `pytest tests -q -p no:cacheprovider` | 1 / 1 (10 failed each) |
| 6–7 | D1 candidate / main (4 files) | 1 / 1 (3 failed each) |
| 8 | `diff` of FAILED-name sets: D6 cand vs main, D1 cand vs main, D6 cand vs receipt raw | 0 / 0 / 0 |
| 9 | `pytest tests/test_control_plane_mutation.py -k PolicyPinTests`; full file | 0 (7 passed); 0 (54 passed) |
| 10 | `policy_digest(router-control.md)`; `git grep 8d6082758541d385 -- library tests` | 0 (6 pin sites) |
| 11–12 | D2 / D3 / D4 greps; D5 union check | 0 |
| 13 | M1 disposable edit + greps + doc suites, restore | 3 environment failures only; porcelain empty |
| 14–15 | MUT-A / MUT-B / MUT-C, restore after each; MUT-C with D1 files + control_plane_mutation | 1 / 0 / 0; 1 (3 environment failures only) |
| 16 | `git diff --name-only fb55623..34997e8f`; `git log a1cb6c1..34997e8f` | 0 (14 paths incl. ticket 47; 10 commits) |
| 17 | added-line scan; evidence host-path grep | 0 |
| 18 | `grep -rniE integrat skills/`; reads of AGENTS, Workflow §0/§5/§7, CodeReview, spec R4, SKILL.md, router-control, adversarial-review, codex-native, delivery-profile, model-role-routing, implementation-authority, review-assurance spec | 0 |

Raw logs: retained by the reviewer seat on its host (D6 candidate and main, D1 candidate and main, policy pins, control-plane mutation, mutations, D5, boundary, added-line scan, failure-name sets); not committed.

Not verified: whether the owner has confirmed the F-05 descriptor decision outside the repository; external target-project names other than the one this seat knows (the dispatch denylist was not supplied); Markdown rendering in a real renderer; ticket 49 cells.

## ImplementationReturn (control plane, closure revision04)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Order | re-plan `70c7a97c` (revision04 frozen: boundary widened, D5 as the union of the boundaries on this line, Workspace row) → content `a47e976b` → this evidence commit (adds captures and this section only) |
| Candidate | `a47e976bae2204be398025f92da6922b89b4079b` (content); every capture below is headed with it |
| D1 | PASS — `3 failed, 121 passed, 564 subtests passed in 4.98s`; failures: ['tests/test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists', 'tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services', 'tests/test_workflow_router.py::WorkflowRouterTests::test_temporal_approval_signal_requires_matching_authority_state']; the environment set of main; raw `evidence/47/rev04-D1.txt` |
| D2 | PASS — counts ['1', '1', '1'] (phrase, `workflow-router` anchor, `role-boundary` anchor); raw `evidence/47/rev04-D2.txt` |
| D3 | PASS — counts ['2', '1'] (`Revision 04 R4-4`, reviewer sentence); raw `evidence/47/rev04-D3.txt` |
| D4 | PASS — counts ['1', '7']; raw `evidence/47/rev04-D4.txt` |
| D5 | PASS — `--- paths: 51; outside every boundary: 0`; every path tagged with the tickets (47, 48, 49) whose boundary at HEAD covers it; raw `evidence/47/rev04-D5.txt` |
| D6 | PASS — `10 failed, 1919 passed, 31 skipped, 15 warnings, 3950 subtests passed in 223.31s (0:03:43)`; vs the revision02 reviewer's main run (12 names): extra on candidate = none; absent on candidate = ['tests/test_atomic_conditional_replace_capability.py::test_acr6_committed_candidate_diff_and_forbidden_paths', 'tests/test_plugin_publication.py::PinnedTreeBindingTests::test_pinning_the_root_commit_is_rejected']; run in the control plane's checkout as the Workspace row states; raw `evidence/47/rev04-D6-full.txt` |
| M1 | check performed — exit-code bullet removed in a disposable edit: exit-code phrase 0, D2 phrase 1; file restored (porcelain for Workflow.md empty: NO); raw `evidence/47/rev04-M1.txt` |
| F-07 mutation | executor reworded to a reviewer seat running the merge by hand → `1 failed, 7 passed, 72 subtests passed in 0.10s` (`test_tara1b` red); restored; raw `evidence/47/rev04-F07-mutation.txt` |
| Policy pin | router-control.md digest moved to `rev-5735230f566619df` in profile.py and test_workflow_router.py |
| Deviations | the D6 failures are the environment and publication-pin set of this environment; names absent on the candidate are the run-to-run variable ones listed above; captures carry host paths as recorded (R3-09, routed) |

## Revision04 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `ed69f822` (evidence commit); content commit `a47e976b`; re-plan commit `70c7a97c` |
| Baseline | `a1cb6c1` (main) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; fresh LF clones of the candidate and of main |
| Summary | Every executable cell is green; candidate and main have identical failure-name sets in D1 and D6, matching the receipt. R3-01, R3-02, R3-04 and R3-08 are closed. Approval is blocked by competing references (Workflow.md:85 → `HALT / ROUTE_REFERENCE_INVALID`): router-control.md's own Revision 04 note still names the merge-queue file as the default cross-session route; three references in the boundary and two outside it still make the receipt-bound bridge or live descriptor required for every cross-lifetime handoff; the new model-role-routing sentence gives queue submission to `SUPERVISOR_REVIEWER`, colliding with `submitter` != `reviewer`; an APPROVED SPEC outside every boundary still says the reviewer integrates. R4-03 and R4-05 are `TICKET_DEFECT`s. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| D1 | PASS | Candidate `3 failed, 121 passed, 564 subtests`; main `3 failed, 120 passed, 563 subtests`; identical failure-name sets (2 temporal DLL, `test_the_pinned_sha_exists`). |
| D2 | PASS | phrase 1 (Workflow.md:81); anchors at :75 and :246. |
| D3 | PASS | `Revision 04 R4-4` 2 (:50, :97); reviewer sentence once at :49, same as main. |
| D4 | PASS | `^## Revision 04` 1; R4-1..R4-7 at spec:162, 167, 180, 185, 189, 193, 199. |
| D5 | PASS | 59 paths, 0 outside every per-ticket modify/create set minus forbid; the 51 paths the capture covers carry the same tags; the 8 `rev04-*` captures added in `ed69f822` are [47]. |
| D6 | PASS | Candidate `10 failed, 1919 passed, 31 skipped, 3950 subtests`; main `10 failed, 1918 passed, 31 skipped, 3949 subtests`; the 10-name sets identical to each other and to `rev04-D6-full.txt`; no SUBFAILED. |
| M1 | PASS (check performed) | exit-code bullet removed in a disposable edit: exit-code phrase 0, D2 phrase and anchors unchanged, doc suites still only the 3 environment failures; restored; porcelain empty. |
| Observable behavior | PASS (scoped) | Section 0, CodeReview.md:49-51, R4-1..R4-7 and the change log read as the ticket states; references outside section 0 still compete (R4-01..R4-05). |

### Re-plan rows

| Row | Status | Evidence |
| --- | --- | --- |
| R3-01 | CLOSED | delivery-profile.md:75-77 and model-role-routing.md:23-26 updated; review-assurance.md ARA-01 amended with an Amendments entry; REQ Scope lists the three files. The new model-role-routing wording creates R4-04. |
| R3-02 | CLOSED | codex-native-same-lifetime-delegation.md:22-24. |
| R3-03 | PARTIAL | router-control.md:108-110 now "available … until it retires in wave 3; not the default". Workflow.md:81, AGENTS.md:20-22 and spec:164 agree with each other. The same file still contradicts them at :12-14 (R4-01); other references still require the bridge (R4-02, R4-03); the named default is not defined (R4-10). |
| R3-04 | CLOSED | D5 frozen in re-plan `70c7a97c`; neither later commit touches the ticket. |
| R3-05 | PARTIAL | `clears` added, `reason` bounce codes only, the `clears` entry admitted while the block holds; a second red (the fix entry itself red) deadlocks again (R4-06). |
| R3-06 | PARTIAL | "which section" settled (last `review-verdict` block for the candidate); `submitter` has no identity format, "recorded by the host" is unverifiable, CodeReview.md does not tell reviewers to write the block (R4-07). |
| R3-07 | OPEN (routed) | Reverting delivery-profile.md:75-77 to "conclusion and integration." leaves D1 + control_plane_mutation green; the integrator rule is pinned in CodeReview.md only. |
| R3-08 | CLOSED | Workspace row states where evidence runs; `rev04-D6-full.txt:47` shows that checkout; the fresh-clone run reproduces the 10 names. |
| R3-09 | OPEN (routed, N49-05) | `rev04-D1.txt`, `rev04-D6-full.txt`, `rev04-D5.txt:3` carry host absolute paths. |
| Digest pin | CLOSED | `policy_digest(router-control.md)` = `rev-5735230f566619df`, equal at all six pin sites; PolicyPinTests 7 passed. |
| Workspace | CLOSED | No host path; states where evidence runs. |
| tara3 | PASS | `tests/test_adversarial_review_policy.py` 8 passed, 72 subtests; the pinned sentences present. |
| F-07 mutation | RED as expected | `test_tara1b` FAILED plus a tara1 SUBFAILED, `2 failed, 7 passed`; restored. |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| R4-01 | `IMPLEMENTATION_DEFECT` | Medium (blocking) | references/router-control.md:12-14 | The Revision 04 note still says "the default cross-session route is the merge-queue file", contradicting :108-110 in the same file, Workflow.md:81, AGENTS.md:20-22 and spec:164. In the boundary; not updated in `a47e976b`. | read file; `git diff a47e976b^..a47e976b` on it touches only :108-110 |
| R4-02 | `IMPLEMENTATION_DEFECT` | Medium (blocking) | references/model-role-routing.md:37-38; SKILL.md:47 | Both in the boundary; both still make the bridge mandatory across lifetimes ("remain required only for a cross-lifetime handoff"; "Cross-lifetime handoffs retain their receipt-bound route"). | grep `live descriptor\|receipt-bound` over skills/ |
| R4-03 | `TICKET_DEFECT` | Medium (blocking) | references/review-checks.md:64-66; references/implementation-authority.md:22-23, :33-36 | Outside every boundary. review-checks.md (indexed for every review): a cross-lifetime handoff "must bind one live descriptor and receipt"; implementation-authority.md: the gateway is "the only Agent-control effect entry" validated "against the live pending descriptor". review-checks.md's digest is pinned (tara7), so editing it moves those pins. | read files |
| R4-04 | `IMPLEMENTATION_DEFECT` | Medium (blocking) | references/model-role-routing.md:23-26 (added in `a47e976b`) vs spec:201, Workflow.md:82; doc/runbooks/dispatch-model-profile.md:64-65 | `SUPERVISOR_REVIEWER` now owns "independent review … and submission of the approved candidate to the merge queue" while R4-7 requires `submitter` != `reviewer`: a single reviewer seat fails admission on every entry it reviews. The runbook still says the reviewer "is the only role that submits it to integration". | grep `submitter\|submission` |
| R4-05 | `TICKET_DEFECT` | Medium (blocking) | modules/spec/workflow-adoption-activation.md:90-91 (APPROVED) | "reviewer waits once, reviews and integrates" against CodeReview.md:49-51, R4-4 and Workflow.md:279; outside every boundary. project-authority-integration.md:254 "reviewer allocation, wait, review, and guarded integration" is ambiguous. | `grep -rniE integrat modules/spec/` |
| R4-06 | `IMPLEMENTATION_DEFECT` | Low (wave-2 merge-queue ticket) | spec:201 | Red entry A, fix entry B with `clears`=A; if B lands red, two blocks hold and one `clears` key cannot name both; "no manual override" → deadlock. | read R4-7 |
| R4-07 | `TICKET_DEFECT` | Low (wave 2) | spec:201-202; CodeReview.md §3 | `submitter` has no identity format (inequality may compare namespaces and pass vacuously); the script cannot verify that the host recorded the `reviewer` string; CodeReview.md does not mention the `review-verdict` block. | read R4-7 and CodeReview.md |
| R4-08 | `EVIDENCE_DEFECT` | Low | review record, revision04 return rows M1 and D6 | M1 row says "porcelain for Workflow.md empty: NO" while `rev04-M1.txt` shows empty porcelain; D6 is compared with the revision02 reviewer's main run, not a main run in the same environment (this review's main run gives the identical 10 names). | read capture; own D6 main run |
| R4-09 | `EVIDENCE_DEFECT` | Low | evidence/47/rev04-D5.txt:3 | The D5 command runs an uncommitted host scratchpad script, so the capture cannot reproduce the cell; tags independently checked and correct. | read capture |
| R4-10 | `TICKET_DEFECT` | Low (wave 2) | Workflow.md:81; AGENTS.md:21; spec:164; router-control.md:109; modules/tickets/TEMPLATE.md | The new default "ticket state row plus the digest of its dispatch file" is never defined: no reference defines a "dispatch file" (Workflow.md §3.2 carries `dispatch_ref`) and TEMPLATE.md has no state-row digest field. | grep `dispatch file\|派工檔\|dispatch_ref`; read TEMPLATE |

`WAIT_FOR_HUMAN` scope: no new conflict. "Return to the Router": no conflict. Added-line scan of `a1cb6c1..ed69f822` (evidence excluded): no host absolute path; no external target-project name among the names this seat knows; vendor and model literals only as branch identifiers, the `codex-native` file name, ticket 49 denylists and quoted historical findings; no chat tone or unverifiable narrative.

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | fresh `--no-hardlinks` LF clones of candidate `ed69f822` and main `a1cb6c1` | 0 |
| 2–4 | D6 candidate; D6 main; `diff` of FAILED-name sets (candidate vs main, candidate vs receipt) | 1 / 1 (10 failed each); 0 / 0 |
| 5 | D1 candidate / main + name-set `diff` | 1 / 1 (3 failed each); 0 |
| 6 | D2 / D3 / D4 greps | 0 |
| 7 | D5 union script over the 47/48/49 boundary blocks + tag diff vs capture | 0 (59 paths, 0 outside) |
| 8–9 | `policy_digest(router-control.md)`; pin greps; `pytest tests/test_control_plane_mutation.py -k PolicyPinTests` | 0; 0 (7 passed) |
| 10 | `pytest tests/test_adversarial_review_policy.py -v` | 0 (8 passed) |
| 11 | M1 disposable edit + greps + D1 files + control_plane_mutation, restore | 1 (3 environment failures only); porcelain empty |
| 12 | F-07 mutation, restore | 1 (tara1b red, tara1 subtest red); porcelain empty |
| 13 | counter-mutation: delivery-profile.md:75-77 reverted, D1 files + control_plane_mutation, restore | 1 (3 environment failures only; not caught) |
| 14 | `git log` / `git diff --stat` over `a1cb6c1..ed69f822`, `70c7a97c..ed69f822`, `a47e976b^..a47e976b` | 0 |
| 15 | governance greps (`integrat`, `live descriptor\|receipt-bound\|mandatory\|bridge`, `submitter\|submission`, Router re-entry phrases, `dispatch file\|派工檔`) over skills/, modules/spec/, Workflow.md, CodeReview.md, AGENTS.md, doc/runbooks/ | 0 |
| 16 | added-line scan; evidence host-path grep | 0 |

Raw logs: retained by the reviewer seat on its host (D6 candidate and main with name sets, D1 candidate and main, D5 and tag diffs, digest and pins, policy tests, M1, F-07, counter-mutation, added-line scan); not committed.

Not verified: whether the control-plane checkout's tree equalled `a47e976b` when its D6 ran (the capture shows the path, not the tree); the owner's F-05 confirmation; external target-project names beyond those this seat knows; Markdown rendering; tickets 48 and 49 cells and commit `1334f0c4`.
