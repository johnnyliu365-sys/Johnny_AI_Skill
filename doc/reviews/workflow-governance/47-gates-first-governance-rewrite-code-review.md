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

## ImplementationReturn (control plane, closure revision05)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Order | re-plan `217e2db1` (revision05 frozen: D7, boundary, committed D5/D7 scripts, D6 main baseline) → content `6f199b5a` → this evidence commit (adds captures and this section only) |
| Candidate | `6f199b5ad9f326cbcdfc5ff689c58b4398c066b7` (content); every capture headed with it; the D6 capture records the tracked-file state of the tree at run start (tree: 0 tracked files modified) |
| D1 | PASS — `3 failed, 121 passed, 564 subtests passed in 4.91s`; failures: ['tests/test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists', 'tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services', 'tests/test_workflow_router.py::WorkflowRouterTests::test_temporal_approval_signal_requires_matching_authority_state']; raw `evidence/47/rev05-D1.txt` |
| D2 | PASS — counts ['1', '1', '1']; raw `evidence/47/rev05-D2.txt` |
| D3 | PASS — counts ['2', '1']; raw `evidence/47/rev05-D3.txt` |
| D4 | PASS — counts ['1', '7']; raw `evidence/47/rev05-D4.txt` |
| D5 | PASS — `--- paths: 67; outside every boundary: 0` (committed script `evidence/47/d5_union.py`); raw `evidence/47/rev05-D5.txt` |
| D6 | PASS — candidate `10 failed, 1919 passed, 31 skipped, 15 warnings, 3950 subtests passed in 231.64s (0:03:51)`; main `a1cb6c1` in a fresh clone, same environment: `10 failed, 1918 passed, 31 skipped, 15 warnings, 3949 subtests passed in 235.16s (0:03:55)`; candidate failures (10) ⊆ main failures (10): extra on candidate = none; main-only = none; raw `evidence/47/rev05-D6-full.txt`, `evidence/47/rev05-D6-main.txt` |
| D7 | PASS — `--- live retired-rule hits: 0` (committed script `evidence/47/d7_sweep.py`; every hit listed with its class); raw `evidence/47/rev05-D7.txt` |
| M1 | check performed — exit-code bullet removed in a disposable edit: exit-code phrase 0, D2 phrase 1; Workflow.md restored, porcelain for it empty; raw `evidence/47/rev05-M1.txt` |
| F-07 mutation | executor reworded to a reviewer seat running the merge by hand → `1 failed, 7 passed, 72 subtests passed in 0.10s` (`test_tara1b` red); restored; raw `evidence/47/rev05-F07-mutation.txt` |
| Policy pins | router-control.md, review-checks.md and implementation-authority.md digests moved with the documents in profile.py and test_workflow_router.py |
| Deviations | D6 names present on main but absent on the candidate are the run-to-run variable ones listed above; captures carry host paths as recorded (R3-09, routed) |

## Revision05 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `8597f8bc` (evidence commit); content commit `6f199b5a`; re-plan commit `217e2db1` |
| Baseline | `a1cb6c1` (main) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; fresh LF clones of the candidate and of main |
| Summary | All executable cells pass as written; D1 and D6 give the same failure-name sets on the candidate and on main; the committed D5 and D7 scripts reproduce their captures exactly. Approval is blocked because two live statements of retired rules remain inside the boundary (R5-01, R5-02), the D7 sweep cannot see statements that wrap across lines or use other verbs and did not catch a counter-mutation restoring the revision04 text (R5-03, `TICKET_DEFECT`), and competing references mean `HALT / ROUTE_REFERENCE_INVALID` under Workflow.md:85. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| D1 | PASS | candidate `3 failed, 121 passed, 564 subtests`; main `3 failed, 120 passed, 563 subtests`; same three environment names; matches `rev05-D1.txt` |
| D2 | PASS | phrase 1 (Workflow.md:81); anchors :75, :246 |
| D3 | PASS | `Revision 04 R4-4` 2 (CodeReview.md:50, :99); reviewer sentence once, as on main |
| D4 | PASS | `^## Revision 04` 1; R4-1..R4-7 at :162, 167, 180, 185, 189, 193, 199 |
| D5 | PASS | committed `d5_union.py` from the clone root: exit 0, 77 paths, 0 outside; the 67 paths in `rev05-D5.txt` carry identical tags; the other 10 are the rev05 captures, [47] |
| D6 | PASS | candidate `10 failed, 1919 passed, 31 skipped, 3950 subtests`; fresh main clone, same venv `10 failed, 1918 passed, 31 skipped, 3949 subtests`; both 10-name sets identical to each other and to `rev05-D6-full.txt` and `rev05-D6-main.txt`; the candidate capture states `tree: 0 tracked files modified` |
| D7 | PASS as written; not pinning | exit 0; same 16 hits as `rev05-D7.txt`, every class correct by hand; but the sweep misses claude-code-plugin-distribution.md:67-68, adversarial-review.md:13-14 and the runbook:59, and the counter-mutation was not caught (R5-03) |
| M1 | PASS (check performed) | exit-code bullet removed in a throwaway edit: exit-code phrase 0, D2 phrase 1, anchors 1/1; doc suites only the 3 environment failures; restored; porcelain empty |
| Observable behavior | PASS (scoped) | section 0, CodeReview.md:49-52, R4-1..R4-7 and the change log read as the ticket states; competing statements remain outside them (R5-01, R5-02, R5-06..R5-08) |
| Order | PASS | `217e2db1` → `6f199b5a` → `8597f8bc`; the ticket diff over that range is empty; both scripts committed in the re-plan; the evidence commit adds only captures and the return section |
| F-07 mutation | RED as expected | executor reworded: `3 failed, 7 passed` (tara1b and two tara1 subtests); restored `8 passed, 72 subtests`; porcelain empty |
| Receipt | PASS with one Low residual | every cell has a result; every capture headed with `6f199b5a` and its command; `rev05-D6-main.txt` headed with `a1cb6c13`; the D6 claim matches; the Deviations row is stale (R5-10) |

### Re-plan rows

| Row | Status | Evidence |
| --- | --- | --- |
| R4-01 | CLOSED | router-control.md:12-15 names the ticket state row plus dispatch-file digest as the default; the merge-queue file holds integration candidates only |
| R4-02 | CLOSED | model-role-routing.md:39-41 and SKILL.md:47-48; the same wording problem remains in adversarial-review.md:13-14 (R5-02) |
| R4-03 | CLOSED | review-checks.md:64-66 and implementation-authority.md:22-23, :35 scoped to the receipt-bound route; `policy_digest` = `rev-ff325539648f7eec`, `rev-c8178b809b9552a1`, router-control `rev-9ce1ed43d5660ec6`, equal to the pins; old digests gone; PolicyPinTests 7 passed; `test_adversarial_review_policy.py` 8 passed incl. tara7 |
| R4-04 | CLOSED (text) | model-role-routing.md:23-27: the reviewer never submits what it reviewed; runbook:64-68 and :92-94 carry the amendment; `submitter != reviewer` can be met with one reviewer seat; two wave-2 gaps remain (R5-11) |
| R4-05 | PARTIAL | closed in workflow-adoption-activation.md:89-92 (Amendments :204) and project-authority-integration.md:250, :254 (Amendments :570); open: executor-routing.md:195 edited without an Amendments entry (R5-09); claude-code-plugin-distribution.md:67-68 (R5-01) and autonomous-collaboration-audit.md:61 (R5-04) still assign integration to a role |
| R4-06 | CLOSED | spec:201: `clears` lists every red key and only an entry clearing all currently red keys is admitted; trace A red, B (clears A) red, C (clears A,B) green lifts the block; "currently red" only implied (R5-11) |
| R4-07 | CLOSED | spec:202 identity format and checks; CodeReview.md:67-68 `review-verdict` bullet |
| R4-08 | CLOSED | M1 row matches `rev05-M1.txt`; `rev05-D6-main.txt` committed, its 10 names equal the reviewer's main run; residual R5-10 |
| R4-09 | CLOSED | both scripts committed in `217e2db1`; run from the clone root they reproduce their captures |
| R4-10 | PARTIAL | R4-1 defines the dispatch file by reference to dispatch lint and the State-row entry; no location is defined for the dispatch file (R5-12) |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| R5-01 | `IMPLEMENTATION_DEFECT` | Medium (blocking) | modules/spec/claude-code-plugin-distribution.md:67-68 | APPROVED SPEC: "The reviewer, not the implementation owner, reviews and integrates after the returned result." A live statement of retired rule (a) inside the boundary; untouched since `a1cb6c1`; D7 misses it because the sentence wraps across two lines. | paragraph-joined sweep |
| R5-02 | `IMPLEMENTATION_DEFECT` | Medium (blocking) | references/adversarial-review.md:13-14 | "Cross-lifetime handoff keeps the separate receipt and live-descriptor controls from `review-checks.md`": unscoped, same shape as R4-02, inside the boundary; D7 misses it (hyphenated `live-descriptor`, verb "keeps", line wrap). | own sweep |
| R5-03 | `TICKET_DEFECT` | Medium (blocking) | evidence/47/d7_sweep.py:10-16; ticket D7 | The sweep greps line by line, so wrapped statements are invisible; its verb set lacks `requires`/`keeps`/`retain`/`reserved`; its patterns lack `live-descriptor`; the classifier exempts on bare substrings (`NOT_REQUIRED`, `R4-1` which also matches `R4-10`, `retired`, `transitional`). Counter-mutation: restoring the `a47e976b` model-role-routing.md (both the R4-02 and R4-04 regressions) left D7 at exit 0 with 0 live hits and the doc tests at the 3 environment failures: zero red. | own counter-mutation; restored; porcelain empty |
| R5-04 | `IMPLEMENTATION_DEFECT` | Low | modules/spec/autonomous-collaboration-audit.md:61 | APPROVED SPEC: "The control-plane/main owner owns … guarded integration" assumes a fixed integrator, against R4-4; outside D7's patterns. | `grep -rniE "guarded integration"` |
| R5-05 | `TICKET_DEFECT` | Low | template/modules/tickets/README.TEMPLATE.md:7 | The template field `整合負責人 \| <AI／worktree>` names a fixed integration owner, against R4-4; `template/` is `forbid` in the 47 boundary and not among the D7 roots. | `grep -rn 整合負責人 template/` |
| R5-06 | `IMPLEMENTATION_DEFECT` | Low | references/router-control.md:116-121 | "Only `IMPLEMENTATION_DISPATCH_CONFIRMED` may consume … receipt and create a cross-lifetime implementation lane" and "A cross-lifetime handoff with no proved bridge is `UNAVAILABLE`" are not scoped to the bridge path and read as "cross-lifetime means bridge only". | read file |
| R5-07 | `IMPLEMENTATION_DEFECT` | Low | doc/runbooks/dispatch-model-profile.md:52-62 | The runbook offers only two dispatch kinds; "Cross-lifetime receipt-bound dispatch … requires the live descriptor" is its only cross-lifetime option; it never names the R4-1 default. | read file |
| R5-08 | `IMPLEMENTATION_DEFECT` | Low | Workflow.md:22 | The flowchart node "Implementation dispatch → receipt、descriptor、…host gate" still puts the descriptor on every dispatch; the section-0 reading rule covers "Router" but not this node. | read file |
| R5-09 | `IMPLEMENTATION_DEFECT` | Low | modules/spec/executor-routing.md:195 | The body of this APPROVED SPEC was edited in `6f199b5a` with no Amendments entry under `CHG-20261103-043`, against the R4-05 disposition. | `git diff a1cb6c1..8597f8bc`; grep Amendment |
| R5-10 | `EVIDENCE_DEFECT` | Low | review record, revision05 return, Deviations row | Says main-only names are "listed above" while the D6 row says main-only = none; stale text. | read record |
| R5-11 | `TICKET_DEFECT` | Low (wave 2) | spec:201-202 | (1) the `seat:<profile>/<run-id>` inequality compares runs, so a reviewer submitting from a second run passes; (2) submission time relative to the review is undefined; (3) the key format inside `clears` and a cleared state are undefined. | read R4-7 |
| R5-12 | `TICKET_DEFECT` | Low (wave 2) | spec:164; Workflow.md:81 | The default dispatch depends on a dispatch file with no defined location; a resuming session cannot resolve the digest. | grep `dispatch file\|派工檔` |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | `--no-hardlinks` LF clones of `8597f8bc` and of main `a1cb6c1` | 0 |
| 2–4 | D6 candidate; D6 main; FAILED-name set diffs (candidate vs main, vs both committed captures) | 1 / 1 (10 failed each); 0 / 0 / 0 |
| 5 | D1 candidate; D1 main; name-set diff | 1 / 1 (3 failed each); 0 |
| 6 | D2 / D3 / D4 greps | 0 |
| 7–8 | committed `d5_union.py` and `d7_sweep.py` from the clone root; diffs vs captures | 0 (77 paths, 0 outside); 0 (0 live; identical) |
| 9 | `policy_digest` of the three references; pin greps; PolicyPinTests; `test_adversarial_review_policy.py -v` | 0; 0; 0 (7 passed); 0 (8 passed) |
| 10 | M1 throwaway edit, greps, D1 files + control_plane_mutation, restore | 1 (3 environment failures only); porcelain empty |
| 11 | F-07 mutation, policy test, restore, rerun | 1 (3 failed); 0 (8 passed); porcelain empty |
| 12 | counter-mutation: model-role-routing.md ← `a47e976b`; D7 plus doc tests; restore | D7 0 (not caught); 1 (3 environment failures only); porcelain empty |
| 13 | own paragraph-joined sweeps over skills/, modules/spec/, Workflow.md, CodeReview.md, AGENTS.md, doc/runbooks/, template/ | 0 |
| 14 | `git log`, `rev-list --parents`, `show --stat`; ticket diff `217e2db1..8597f8bc` | 0 (empty) |
| 15 | added-line scan of `a1cb6c1..8597f8bc` without evidence (1318 lines) | 0 (no host path; vendor literals only in branch ids, the `codex-native` file name, boundary rules, ticket-49 denylists and quoted findings; no external project name; no chat tone) |

Raw logs: retained by the reviewer seat on its host; not committed.

Not verified: whether the control-plane checkout's HEAD was `6f199b5a` when its D6 ran (the capture states the tracked-file count and the claimed candidate, not HEAD output); the owner's F-05 confirmation; external target-project names other than the ones this seat knows; Markdown rendering; tickets 48 and 49 cells and commit `34c79f0f`; wave-2 behaviour of the R4-7 schemas.

## ImplementationReturn (control plane, closure revision06)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Order | re-plan `99c06388` (revision06 frozen: new D7 instrument, M2, template file admitted) → content `bfbd58ff` → this evidence commit (adds captures and this section only) |
| Candidate | `bfbd58ff516adb72176a23c1b86db01811d53381` (content); every capture headed with it; the D6 capture records HEAD and the tracked-file state at run start (tree: 0 tracked files modified) |
| D1 | PASS — `3 failed, 121 passed, 564 subtests passed in 5.17s`; failures: ['tests/test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists', 'tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services', 'tests/test_workflow_router.py::WorkflowRouterTests::test_temporal_approval_signal_requires_matching_authority_state']; raw `evidence/47/rev06-D1.txt` |
| D2 | PASS — counts ['1', '1', '1']; raw `evidence/47/rev06-D2.txt` |
| D3 | PASS — counts ['2', '1']; raw `evidence/47/rev06-D3.txt` |
| D4 | PASS — counts ['1', '7']; raw `evidence/47/rev06-D4.txt` |
| D5 | PASS — `--- paths: 83; outside every boundary: 0` (committed `evidence/47/d5_union.py`); raw `evidence/47/rev06-D5.txt` |
| D6 | PASS — candidate `11 failed, 1919 passed, 31 skipped, 15 warnings, 3949 subtests passed in 274.12s (0:04:34)`; main `a1cb6c1` in a fresh clone, same environment: `10 failed, 1918 passed, 31 skipped, 15 warnings, 3949 subtests passed in 280.94s (0:04:40)`; candidate failures (10) vs main failures (10): none: the candidate failure-name set equals the same-environment main run; raw `evidence/47/rev06-D6-full.txt`, `evidence/47/rev06-D6-main.txt` |
| D7 | PASS — `--- live retired-rule hits: 0` (committed `evidence/47/d7_sweep.py`, revision06 instrument; every hit listed with its class and pattern); raw `evidence/47/rev06-D7.txt` |
| M1 | check performed — exit-code bullet removed in a disposable edit: exit-code phrase 0, D2 phrase 1; Workflow.md restored, porcelain empty; raw `evidence/47/rev06-M1.txt` |
| M2 | PASS — model-role-routing.md restored from `a47e976b` in a disposable edit: D7 exit 1 with 2 LIVE hits in that file; file restored, porcelain empty; raw `evidence/47/rev06-M2.txt` |
| F-07 mutation | executor reworded to a reviewer seat running the merge by hand → `1 failed, 7 passed, 72 subtests passed in 0.10s` (`test_tara1b` red); restored; raw `evidence/47/rev06-F07-mutation.txt` |
| Policy pins | every reference whose text changed has its digest moved in profile.py and test_workflow_router.py (listed in the content commit message) |
| Deviations | none: the candidate failure-name set equals the same-environment main run; captures carry host paths as recorded (R3-09, routed) |

## Revision06 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `7804a937` (evidence commit); content commit `bfbd58ff`; re-plan commit `99c06388` |
| Baseline | `a1cb6c1` (main) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; fresh LF clones of the candidate and of main |
| Summary | The content commit breaks a test that passes on main while the receipt claims equal failure sets; a live statement of a retired rule remains in `SKILL.md` inside the boundary; two counter-mutations left D7 green. The instrument and template problems are `TICKET_DEFECT`s and return to the control plane before any fix. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| D1 | PASS | candidate `3 failed, 121 passed, 564 subtests`; main `3 failed, 120 passed, 563 subtests`; same three names; matches `rev06-D1.txt` |
| D2 | PASS | phrase 1 (Workflow.md:81); anchors :75, :246 |
| D3 | PASS | `Revision 04 R4-4` 2 (:50, :99); reviewer sentence once, unchanged |
| D4 | PASS | `^## Revision 04` 1; R4-1..R4-7 at :162, 167, 180, 185, 189, 193, 199 |
| D5 | PASS | committed `d5_union.py`: exit 0, 94 paths, 0 outside; identical to `rev06-D5.txt` once the 11 rev06 captures are removed |
| D6 | FAIL | candidate `12 failed, 1918 passed`; main (fresh clone, same venv) `10 failed, 1918 passed`; nothing fails on main only. Candidate-only: (1) `SUBFAILED(phrase='cross-lifetime receipt-bound handoff') tests/test_plugin_publication.py::SynchronousDispatchGuidanceTests::test_t3_wait_is_native_one_shot_and_bridge_is_not_required`, fails alone on the candidate and passes alone on main; the same line sits in the committed `rev06-D6-full.txt`; (2) `test_codex_receipt_removal_acceptance.py::…test_a7_…` failed in the full run and passed alone (treated as flaky). The candidate set is not a subset of main's. |
| D7 | PASS as written; not pinning | committed `d7_sweep.py`: exit 0, 33 hits, identical to `rev06-D7.txt`; every hit checked by hand (markers in the same sentence; the two dated rows are Amendments rows; the one scoped file carries its note at line 3). The sweep misses SKILL.md:134-135 and template/README.md:43-45, and two counter-mutations stay green (N-03). |
| M1 | PASS (check performed) | exit-code bullet removed in a disposable edit: exit-code phrase 0, D2 phrase 1, anchors 1/1; D1 files only the 3 environment failures; restored; porcelain empty |
| M2 | PASS as written; own counter-mutations 2 of 22 not red | model-role-routing.md from `a47e976b`: D7 exit 1, 2 LIVE hits (:23 a2, :36 b2); restored. 22 earlier versions restored one at a time: 20 turn D7 red; not red: `implementation-authority.md` from `a47e976b` (and from `a1cb6c1`), the R4-03 text; `Workflow.md` from `8597f8bc`, the R5-08 flowchart. |
| Observable behavior | PASS (scoped) | section 0, CodeReview.md:49-52, R4-1..R4-7 and the change log read as the ticket states; SKILL.md:134-135 competes (N-02) → `HALT / ROUTE_REFERENCE_INVALID` under Workflow.md:85 |
| Order | PASS | `99c06388` → (`5bcc0db9`, ticket 48) → `bfbd58ff` → `7804a937`; `git diff 99c06388..7804a937` over the ticket and both scripts empty; the evidence commit adds only captures and the return section |
| F-07 mutation | RED as expected | a different clause mutated ("is its admission, not its executor" → "the reviewer also executes integration"): `test_adversarial_review_policy.py` 1 failed, 8 passed; D7 also flags CodeReview.md:49 LIVE; restored; 8 passed |
| Receipt | FAIL | every capture headed with `bfbd58ff` and its command (D6-main with `a1cb6c13`), all valid UTF-8; `rev06-D6-full.txt` states `head` and `tree: 0 tracked files modified`; the D7 claim matches. The D6 claim does not: the return says "candidate failures (10) vs main failures (10): none" and Deviations "none" while the same row quotes `11 failed` and the capture holds a SUBFAILED not on main (N-01). |

### Re-plan rows

| Row | Status | Evidence |
| --- | --- | --- |
| R5-01 | CLOSED | claude-code-plugin-distribution.md:66-67 and Amendments :392 |
| R5-02 | CLOSED | adversarial-review.md:13-14 |
| R5-03 | PARTIAL | instrument replaced (paragraph units, 7 patterns, sentence-scoped markers) and M2 turns it red; still missing: fenced code skipped; one match per pattern per unit; `reviewer\b` misses "reviewers"; b1 lacks bare `require`, `remains bound` and a bare `descriptor`; two counter-mutations stay green (N-03) |
| R5-04 | PARTIAL | autonomous-collaboration-audit.md:61 still names a fixed owner of guarded integration while its Amendments row says "no fixed integrator" (N-05) |
| R5-05 | CLOSED | template/modules/tickets/README.TEMPLATE.md:7 integration row; D5 tags it [47]; nothing else under template/ changed |
| R5-06 | CLOSED | router-control.md:116, :120-121 |
| R5-07 | CLOSED | dispatch runbook:59-61 |
| R5-08 | CLOSED (text), unpinned | Workflow.md:22 node; reverting it leaves D7 green because the node sits in a fenced mermaid block |
| R5-09 | CLOSED | executor-routing.md:191, :238, Amendments :269; plugin-distribution.md:132, Amendments :317; receipt-bound-role-supervision.md scope note line 3, Amendments :579; every edited approved SPEC (10 files) carries a `CHG-20261103-043` entry |
| R5-10 | OPEN | the Deviations row is generated but the comparison reads only `^FAILED` lines, so it misses the SUBFAILED and states "none" next to `11 failed` (N-01) |
| R5-11 | PARTIAL | spec:201-202 define `<ticket>@<candidate>`, `CLEARED`, the submitter rule and the submission timing; the anti-replay list omits `CLEARED` while router-control.md:16 includes it (N-04) |
| R5-12 | CLOSED | spec:164 dispatch-file location |
| R3-07 | CLOSED (routed) | pins for all 7 references equal `policy_digest`; PolicyPinTests plus `test_adversarial_review_policy.py` 15 passed, 79 subtests |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| N-01 | `IMPLEMENTATION_DEFECT` + `EVIDENCE_DEFECT` | Medium (blocking) | references/codex-native-same-lifetime-delegation.md:48; tests/test_plugin_publication.py:888; revision06 return D6/Deviations rows | `bfbd58ff` rewrote "cross-lifetime receipt-bound handoff" as "cross-lifetime handoff that takes the receipt-bound bridge route"; the `_assert_t3` phrase pin now fails on the candidate and passes on main, so D6 is red; the phrase count is 1 at a1cb6c1, 8597f8bc and 99c06388 and 0 at bfbd58ff; the test file is outside the boundary; the receipt's name set ignores `SUBFAILED`; D1 does not cover this test file. | own D6 runs; single-test reruns; `git show <c>:… \| grep -c` |
| N-02 | `IMPLEMENTATION_DEFECT` | Medium (blocking) | SKILL.md:134-135 | "A pending dispatch remains bound to its live descriptor." Unscoped, in the boundary, in the skill entry file; contradicts R4-1 and AGENTS.md:20-22; unchanged since a1cb6c1; D7 misses it ("remains bound" is not in its verb set). | own paragraph-joined sweep |
| N-03 | `TICKET_DEFECT` | Medium (blocking) | evidence/47/d7_sweep.py (fence skip in `units()`, b1 verb list, `reviewer\b`, single `pat.search`) | Zero red under review-checks.md counter-mutation point 2: restoring implementation-authority.md from a47e976b (the R4-03 text) gives exit 0; restoring Workflow.md from 8597f8bc (the R5-08 flowchart inside a mermaid fence, which the sweep skips) gives exit 0; the sweep also misses N-02 and N-06. `SCOPE_NOTE` matches any one-line "not the default … R4-1" in the first 40 lines and then exempts every b/d hit in the whole file, wider than the header note D7 describes. | own counter-mutations |
| N-04 | `IMPLEMENTATION_DEFECT` | Low (wave 2) | spec:201 | the anti-replay refusal list omits `CLEARED`, which the same bullet calls terminal; router-control.md:16 lists it; read literally the SPEC lets a `CLEARED` key be re-queued. | read both lines |
| N-05 | `IMPLEMENTATION_DEFECT` | Low | modules/spec/autonomous-collaboration-audit.md:61 | "The control-plane/main owner owns … guarded integration (run by the versioned integration script, R4-4)" still names a fixed owner, against R4-4; the Amendments row claims "no fixed integrator"; D7 exempts it on the `R4-4` marker. | read file |
| N-06 | `TICKET_DEFECT` | Medium | template/README.md:43-45 | "A fixed dispatch response is produced only from the live Private Router pending descriptor and its reviewed ticket/handoff receipt." makes the live descriptor the only dispatch source, a live statement of the retired rule in a D7 root; `forbid = template/*` blocks a fix; D7 misses it. | `grep -rn -i descriptor template/` |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | `--no-hardlinks` LF clones of the candidate at 7804a937 and of main a1cb6c1 | 0 |
| 2–4 | D6 candidate; D6 main; `comm` of the FAILED/SUBFAILED name sets; single-test reruns (a7, t3 class on both) | 1 (12 failed); 1 (10 failed); candidate-only 2, main-only 0; t3 SUBFAILED on the candidate, 10 passed on main |
| 5–6 | D1 candidate / main; D2 / D3 / D4 greps | 1 / 1 (3 failed each, same names); 0 |
| 7–8 | `python -I -X utf8 d5_union.py` and `d7_sweep.py`; diffs against the captures | 0 (94 paths, 0 outside) / 0 (0 live); identical |
| 9–10 | own D7 detail script (sentence plus exempting marker, finditer); own sweeps a/b/c; Chinese greps; descriptor and pending-dispatch greps | 0 (N-02, N-06 found) |
| 11–12 | M1; M2 (model-role-routing ← a47e976b), D7, restore | 1 (3 environment failures only); D7 1 (2 LIVE); porcelain empty |
| 13 | 23 counter-mutations one file at a time | D7 1 on 20; 0 on implementation-authority (×2) and Workflow.md; porcelain empty each time |
| 14 | own F-07 mutation; policy test; D7; restore | 1 (1 failed); 1 (1 LIVE); 0 (8 passed) |
| 15–16 | `policy_digest` of 7 references vs the pins; PolicyPinTests plus `test_adversarial_review_policy.py`; Amendments grep over the 10 edited SPECs | 0; 0 (15 passed); 0 |
| 17–18 | `git log`, `rev-list --parents`, `show --stat`, `merge-base --is-ancestor`; ticket/script diff `99c06388..7804a937`; capture header and UTF-8 checks | 0 (empty); 0 (all UTF-8; D7 mixed CRLF/LF) |
| 19 | added-line scan of `a1cb6c1..7804a937` excluding evidence (1680 lines) | 0 (no host path; vendor words only in branch ids, the `codex-native` file name, boundary rules, quoted findings and pre-existing product-host sentences; no project name; no chat tone) |

Raw logs: retained by the reviewer seat on its host; not committed.

Not verified: why a7 fails only in the full run (passes alone; treated as flaky); whether the control-plane checkout's HEAD really was `bfbd58ff` when D6 ran (only the capture's `head:` line); the owner's F-05 confirmation; external target-project names other than the ones this seat knows; Markdown and mermaid rendering; tickets 48 and 49 and the commits after `7804a937`; wave-2 behaviour of the R4-7 schemas.

## Revision07 (superseded without review)

Revision07 was frozen at `b5c25bea`, its content committed at `ab624d06` and `bff31425`, and a cell run was started; before a review was dispatched the owner decided on 2026-11-03 to scope the consistency check to the routed governance set (closure revision08). No evidence of that run is committed; the revision07 content stays on the branch and is covered by the revision08 cells.

## ImplementationReturn (control plane, closure revision08)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Order | re-plan (revision08 frozen by owner decision: D7 scoped to the routed governance set, D8 precedence notes, five-file M2) → content `497f147a` → this evidence commit (adds captures and this section only) |
| Candidate | `497f147aa14353d86351126c730150b30a4b4c9c` (content); every capture headed with it; the D6 capture records HEAD and the tracked-file state at run start (tree: 0 tracked files modified) |
| D1 | PASS — `3 failed, 121 passed, 564 subtests passed in 6.18s`; failures: ['tests/test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists', 'tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services', 'tests/test_workflow_router.py::WorkflowRouterTests::test_temporal_approval_signal_requires_matching_authority_state']; raw `evidence/47/rev08-D1.txt` |
| D2 | PASS — counts ['1', '1', '1']; raw `evidence/47/rev08-D2.txt` |
| D3 | PASS — counts ['2', '1']; raw `evidence/47/rev08-D3.txt` |
| D4 | PASS — counts ['1', '7']; raw `evidence/47/rev08-D4.txt` |
| D5 | PASS — `--- paths: 107; outside every boundary: 0` (committed `evidence/47/d5_union.py`); raw `evidence/47/rev08-D5.txt` |
| D6 | PASS — candidate `10 failed, 1919 passed, 31 skipped, 15 warnings, 3950 subtests passed in 369.34s (0:06:09)`; main `a1cb6c1` in a fresh clone, same environment: `10 failed, 1918 passed, 31 skipped, 15 warnings, 3949 subtests passed in 359.88s (0:05:59)`; name sets built from FAILED and SUBFAILED lines: candidate 10 names, main 10 names; none: the candidate failure-name set (FAILED and SUBFAILED) equals the same-environment main run; candidate names: ['tests/test_atomic_conditional_replace_capability.py::test_acr2_linux_requires_an_actual_linux_kernel_and_backend', 'tests/test_atomic_conditional_replace_capability.py::test_acr6_exact_test_only_boundary', 'tests/test_guarded_integration_corrections.py::ReceiptBoundCorrectionTests::test_reviewed_router_profile_composes_return_integration_and_audit', 'tests/test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists', 'tests/test_plugin_publication.py::CandidateMetadataTests::test_l5_stale_candidate_pin_is_named_before_generation', 'tests/test_plugin_publication.py::PublicationReachabilityTests::test_deleting_the_actual_publication_anchor_makes_the_marketplace_pin_unreachable', 'tests/test_plugin_publication.py::PublicationReachabilityTests::test_the_marketplace_pin_is_bound_to_the_actual_publication_anchor', 'tests/test_refusal_guidance.py::ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered', 'tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services', 'tests/test_workflow_router.py::WorkflowRouterTests::test_temporal_approval_signal_requires_matching_authority_state']; raw `evidence/47/rev08-D6-full.txt`, `evidence/47/rev08-D6-main.txt` |
| D7 | PASS — `--- live retired-rule hits: 0` (committed `evidence/47/d7_sweep.py`, revision08 instrument; every match listed with its class and pattern); raw `evidence/47/rev08-D7.txt` |
| D8 | PASS — `--- SPECs without the precedence note: 0` (committed `evidence/47/d8_precedence.py`; every historical SPEC listed); raw `evidence/47/rev08-D8.txt` |
| M1 | check performed — exit-code bullet removed in a disposable edit: exit-code phrase 0, D2 phrase 1; Workflow.md restored, porcelain empty; raw `evidence/47/rev08-M1.txt` |
| M2 | PASS — five restorations, each: D7 exit and LIVE hits in the restored file: skills/johnny-project-takeover/references/model-role-routing.md<-a47e976b: exit 1, 2 live, porcelain 0; skills/johnny-project-takeover/references/implementation-authority.md<-a47e976b: exit 1, 2 live, porcelain 0; Workflow.md<-8597f8bc: exit 1, 1 live, porcelain 0; skills/johnny-project-takeover/SKILL.md<-7804a937: exit 1, 2 live, porcelain 0; template/README.md<-7804a937: exit 1, 2 live, porcelain 0; raw `evidence/47/rev08-M2.txt` |
| F-07 mutation | executor reworded to a reviewer seat running the merge by hand → `1 failed, 7 passed, 72 subtests passed in 0.13s` (`test_tara1b` red); restored; raw `evidence/47/rev08-F07-mutation.txt` |
| Policy pins | every reference whose text changed has its digest moved in profile.py and test_workflow_router.py (listed in the content commit message) |
| Deviations | none: the candidate failure-name set (FAILED and SUBFAILED) equals the same-environment main run; captures carry host paths as recorded (R3-09, routed) |

## Revision08 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `641850d5` (evidence commit); content commit `497f147a`; re-plan commit `bbfe3c1a` |
| Baseline | `a1cb6c1` (main) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; fresh LF clones of the candidate and of main |
| Summary | The revision08 content is correct and every cell reproduces as written; the receipt matches the reviewer's runs; N-01 to N-06 are closed in the files. One live retired-rule statement remains in a D7 root that the instrument misses and the boundary keeps it from being fixed (N8-01, `TICKET_DEFECT`); three Low findings to fix in the same re-plan. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| D1 | PASS | candidate `3 failed, 121 passed, 564 subtests`; main `3 failed, 120 passed, 563 subtests`; same three names; matches `rev08-D1.txt` |
| D2 | PASS | 1 / 1 / 1 |
| D3 | PASS | 2 / 1; reviewer sentence unchanged |
| D4 | PASS | 1 / 7; R4-1..R4-7 at spec:162, 167, 180, 185, 189, 193, 199 |
| D5 | PASS | exit 0, 119 paths at the candidate, 0 outside; the path set of `a1cb6c1..497f147a` (107) identical to `rev08-D5.txt`; pins for router-control, implementation-authority and review-checks moved |
| D6 | PASS | candidate `10 failed, 1919 passed, 31 skipped, 3950 subtests` (head 641850d5, 0 files modified at start); main fresh clone, same venv `10 failed, 1918 passed, 31 skipped, 3949 subtests`; FAILED+SUBFAILED name sets equal (10 = 10) and equal to both committed captures |
| D7 | PASS as written; not complete | exit 0, 48 hits, byte-identical to `rev08-D7.txt` after CRLF strip; every hit checked by hand (45 "states the rule" with the marker in their own sentence; runbook:84 under a "Revision record" heading; spec:214 a dated row; no scope-note exemption used). Own paragraph-joined sweep with fenced lines (118 sentences) found one miss: N8-01; no wrong exemption |
| D8 | PASS | exit 0, identical to `rev08-D8.txt`; all 20 notes byte-identical at non-empty line 2 (line 3 in receipt-bound-role-supervision.md); two of the twenty files are not historical SPECs (N8-02) |
| M1 | PASS (check performed) | exit-code phrase 0, D2 still 1 1 1; restored; porcelain empty |
| M2 | PASS | all five restorations give D7 exit 1 with LIVE hits in the restored file: 2, 2, 1, 2, 2; matches `rev08-M2.txt`. Own run: 50 earlier versions of the 15 D7-root files changed on this line, restored one at a time: 37 red, 13 green; 11 of the green ones expected (no a–e statement, or another cell pins the change); the two unexpected are N8-03 and N8-04 |
| Observable behavior | PASS (scoped) | Workflow.md:78-86 and CodeReview.md:47-52 read as the ticket states; R4-1..R4-7 present; the change log replaces the checklist; the handover runbook still competes (N8-01) |
| Order | PASS | `bbfe3c1a` → `497f147a` (21 files: notes plus one Workflow.md line) → `641850d5` (captures plus the return section only); the ticket/script diff over that range is empty; the Revision07 section matches git (no review, no captures); its claim "its cells were run" has no capture behind it (N8-04) |
| F-07 mutation | RED as expected | own door ("admits it and the reviewer then executes it"): `SUBFAILED(term='is its admission, not its executor')`, 1 failed, 8 passed; D7 stays 0 on that wording (no "integrat" word) but the test pins it; restored |
| Receipt | PASS with one note | every cell has a result; every capture headed with 497f147a and its command; D6-full states `head:` and `tree: 0 tracked files modified`; D6, D7 and D8 claims match; all 12 captures valid UTF-8; the M2 header describes the loop rather than an exact command; the Order row gives no re-plan sha (N8-04) |
| Policy pins / payload | PASS | `policy_digest` of all 7 references equals the pins; no stale pin; PolicyPinTests + `test_adversarial_review_policy.py` + the t3 class 25 passed; `test_plugin_payload_boundary.py` 40 passed with only the pinned-sha environment failure; all 9 PayloadClosureTests pass |
| Added-line scan | PASS | 1870 added lines, evidence excluded: no host absolute path; vendor words only in branch ids, the codex-native file name, boundary rules, quoted findings, ticket-49 denylists and one pre-existing product-host sentence; no external project name; no chat tone |

### Prior findings

| ID | Status | Evidence |
| --- | --- | --- |
| N-01 | CLOSED | codex-native:48 keeps "cross-lifetime receipt-bound handoff" (count 1), scoped in the same sentence; the t3 pin passes; D6 and the receipt read FAILED and SUBFAILED |
| N-02 | CLOSED | SKILL.md:134-136; the 7804a937 restoration turns D7 red |
| N-03 | CLOSED (as frozen) | fenced lines scanned, finditer per sentence, bound/only/requires verbs, five-line scope note; M2 red on all five; residual gaps N8-01, N8-03 |
| N-04 | CLOSED | spec:201 refusal list includes `CLEARED` |
| N-05 | CLOSED | autonomous-collaboration-audit.md:63; Amendments :129 |
| N-06 | CLOSED | template/README.md:41-44; admitted in the boundary; the 7804a937 restoration turns D7 red |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| N8-01 | `TICKET_DEFECT` | Medium (blocking) | doc/runbooks/handover-2026-08-22-plugin-distribution.md:107-117 | Under "## 整合怎麼做" a present-tense instruction says the reviewer commits the reviewed candidate to the candidate branch and passes it through the gate ("審閱者審完後代為 commit 到候選分支，再過閘門"): a live statement of the retired rules (reviewer integrates and submits), against R4-4, R4-7 and model-role-routing.md:23-26. The file is in a frozen D7 root (`doc/runbooks/`) and no exemption covers a dated handover document; D7 misses it (pattern c needs 整合 in the same sentence; no Chinese submit or commit pattern; the heading is its own unit). The boundary admits only `doc/runbooks/dispatch-model-profile.md`; the re-plan prose names "the dispatch runbook" while the D7 row and ROOTS name `doc/runbooks/`. | own sweep; reviewer and commit grep; D7 output has 0 lines naming the file |
| N8-02 | `TICKET_DEFECT` | Low (fix with N8-01) | modules/spec/TEMPLATE.md:3; modules/spec/README.md:3 | D8 requires the note on every file in `modules/spec/` except workflow-governance.md, so the SPEC template (pinned as a template by test_workflow_router.py:1003) now says every new SPEC predates Revision 04, waives `ROUTE_REFERENCE_INVALID` and archives it in wave 3; the index README is called "this SPEC" too. | read both files; the D8 script's `listdir` scope |
| N8-03 | `TICKET_DEFECT` | Low | Workflow.md:86; ticket Acceptance | No cell pins the revision08 precedence sentence: restoring Workflow.md from bfbd58ff leaves D2 at 1, D7 and D8 at exit 0 and the doc tests at the 3 environment failures (zero red under review-checks point 2); a D2-style grep would pin it. | counter-mutation |
| N8-04 | `OUT_OF_SCOPE_HARDENING` / `EVIDENCE_DEFECT` | Low | review record Order row and Revision07 section; AGENTS.md (fb55623f text) | (a) the revision08 Order row gives no re-plan sha; the Revision07 section claims "its cells were run" with no capture behind it. (b) Restoring AGENTS.md from fb55623f (pending dispatch "票面狀態與整合佇列列") gives D7 exit 0: pattern d has no 整合佇列 noun and b1 needs a mandatory or default verb, so the "queue holds integration candidates only" half of R4-1 is not pinned; no live statement of that kind exists today; route to the wave-2 contract gate next to R3-07. | read the record; counter-mutation |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | `--no-hardlinks` LF clones: candidate at 641850d5, main at a1cb6c13 | 0 |
| 2–4 | D6 candidate; D6 main; `comm` of FAILED/SUBFAILED name sets vs each other and both captures | 1 (10 failed) / 1 (10 failed); 0 |
| 5–6 | D1 candidate / main; D2 / D3 / D4 greps | 1 / 1 (same 3 names); 0 |
| 7–8 | `d5_union.py` and path-set comparison; `d7_sweep.py`, `d8_precedence.py` and `cmp` against the captures | 0 (119 paths, 0 outside; identical); 0 / 0 (identical) |
| 9–10 | own sentence sweep over the D7 roots (fences included); reviewer/commit/merge and queue/dispatch greps; note position and wording check over 20 SPECs | 0 (N8-01 found); 0 |
| 11–12 | M1; M2 five restorations with D7 each | 0; 1 ×5; porcelain empty |
| 13–14 | 50 own counter-mutations; Workflow.md ← bfbd58ff and AGENTS.md ← fb55623f with D2/D7/D8 and the D1 files | 37 red / 13 green; all green apart from environment failures (N8-03, N8-04) |
| 15 | own F-07 mutation; policy test; D7; restore | 1 (1 failed); 0; 0 (8 passed) |
| 16–17 | `policy_digest` of 7 references vs pins; stale-pin search; PolicyPinTests + adversarial + t3; `test_plugin_payload_boundary.py -rA` | 0; 0; 0 (25 passed); 1 (only pinned-sha; 40 passed) |
| 18–20 | `git log`/`show --stat` of the three commits and revision07; ticket/script diff `bbfe3c1a..641850d5`; capture header and UTF-8 checks; added-line scan (1870 lines) | 0 (empty); 0; 0 |

Raw logs: retained by the reviewer seat on its host; not committed.

Not verified: whether the control-plane checkout really was at 497f147a when its D6 ran (only the capture's `head:` line); that revision07's cells were ever run (no captures exist); the owner's F-05 confirmation; external target-project names other than the ones this seat knows; Markdown and mermaid rendering; whether Workflow.md:86 "專案 SPEC" is meant to cover a pre-Revision-04 SPEC in a target project that has no note; ticket 48 and the commits after 641850d5; wave-2 behaviour of the R4-7 schemas.

## ImplementationReturn (control plane, closure revision09)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Order | re-plan `ab7472b4` (revision09 frozen: D7 roots name the routed runbook, D8 covers historical SPECs and dated handover runbooks, D9 pins the precedence sentence) → content `1c5c1336` → this evidence commit (adds captures and this section only) |
| Candidate | `1c5c1336da97e1a082330ae8b081601a5dd8f1fc` (content); every capture headed with it; the D6 capture records HEAD and the tracked-file state at run start (tree: 0 tracked files modified) |
| D1 | PASS — `3 failed, 121 passed, 564 subtests passed in 6.57s`; failures: ['tests/test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists', 'tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services', 'tests/test_workflow_router.py::WorkflowRouterTests::test_temporal_approval_signal_requires_matching_authority_state']; raw `evidence/47/rev09-D1.txt` |
| D2 | PASS — counts ['1', '1', '1']; raw `evidence/47/rev09-D2.txt` |
| D3 | PASS — counts ['2', '1']; raw `evidence/47/rev09-D3.txt` |
| D4 | PASS — counts ['1', '7']; raw `evidence/47/rev09-D4.txt` |
| D5 | PASS — `--- paths: 118; outside every boundary: 0` (committed `evidence/47/d5_union.py`); raw `evidence/47/rev09-D5.txt` |
| D6 | PASS — candidate `10 failed, 1919 passed, 31 skipped, 15 warnings, 3950 subtests passed in 271.20s (0:04:31)`; main `a1cb6c1` in a fresh clone, same environment: `10 failed, 1918 passed, 31 skipped, 15 warnings, 3949 subtests passed in 416.75s (0:06:56)`; name sets built from FAILED and SUBFAILED lines: candidate 10 names, main 10 names; none: the candidate failure-name set (FAILED and SUBFAILED) equals the same-environment main run; candidate names: ['tests/test_atomic_conditional_replace_capability.py::test_acr2_linux_requires_an_actual_linux_kernel_and_backend', 'tests/test_atomic_conditional_replace_capability.py::test_acr6_exact_test_only_boundary', 'tests/test_guarded_integration_corrections.py::ReceiptBoundCorrectionTests::test_reviewed_router_profile_composes_return_integration_and_audit', 'tests/test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists', 'tests/test_plugin_publication.py::CandidateMetadataTests::test_l5_stale_candidate_pin_is_named_before_generation', 'tests/test_plugin_publication.py::PublicationReachabilityTests::test_deleting_the_actual_publication_anchor_makes_the_marketplace_pin_unreachable', 'tests/test_plugin_publication.py::PublicationReachabilityTests::test_the_marketplace_pin_is_bound_to_the_actual_publication_anchor', 'tests/test_refusal_guidance.py::ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered', 'tests/test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services', 'tests/test_workflow_router.py::WorkflowRouterTests::test_temporal_approval_signal_requires_matching_authority_state']; raw `evidence/47/rev09-D6-full.txt`, `evidence/47/rev09-D6-main.txt` |
| D7 | PASS — `--- live retired-rule hits: 0` (committed `evidence/47/d7_sweep.py`, revision08 instrument; every match listed with its class and pattern); raw `evidence/47/rev09-D7.txt` |
| D8 | PASS — `--- defects: 0 (covered files: 19)` (committed `evidence/47/d8_precedence.py`; every historical SPEC listed); raw `evidence/47/rev09-D8.txt` |
| D9 | PASS — count ['1'] (the section-0 precedence sentence); raw `evidence/47/rev09-D9.txt` |
| M1 | check performed — exit-code bullet removed in a disposable edit: exit-code phrase 0, D2 phrase 1; Workflow.md restored, porcelain empty; raw `evidence/47/rev09-M1.txt` |
| M2 | PASS — five restorations, each: D7 exit and LIVE hits in the restored file: skills/johnny-project-takeover/references/model-role-routing.md<-a47e976b: exit 1, 2 live, porcelain 0; skills/johnny-project-takeover/references/implementation-authority.md<-a47e976b: exit 1, 2 live, porcelain 0; Workflow.md<-8597f8bc: exit 1, 1 live, porcelain 0; skills/johnny-project-takeover/SKILL.md<-7804a937: exit 1, 2 live, porcelain 0; template/README.md<-7804a937: exit 1, 2 live, porcelain 0; raw `evidence/47/rev09-M2.txt` |
| F-07 mutation | executor reworded to a reviewer seat running the merge by hand → `1 failed, 7 passed, 72 subtests passed in 0.12s` (`test_tara1b` red); restored; raw `evidence/47/rev09-F07-mutation.txt` |
| Policy pins | every reference whose text changed has its digest moved in profile.py and test_workflow_router.py (listed in the content commit message) |
| Deviations | none: the candidate failure-name set (FAILED and SUBFAILED) equals the same-environment main run; captures carry host paths as recorded (R3-09, routed) |

D6 was run three times on the candidate and every run is committed. Run 1 (`rev09-D6-full-run1.txt`, in parallel with the main-clone suite) had one name not on main, `tests/test_codex_receipt_removal_acceptance.py::CodexReceiptRemovalAcceptanceTests::test_a5_foreign_records_and_payload_bytes_are_preserved`. Run 2 (`rev09-D6-full-run2.txt`, serial, but with another seat's pytest on the host; 319 s) had that file green alone (10 passed) and one other name not on main, `tests/test_codex_registration_target_project_isolation_acceptance.py::CodexRegistrationTargetProjectIsolationAcceptanceTests::test_b5_compensation_acceptance_preserves_both_external_repository_snapshots`. Run 3 (`rev09-D6-full.txt`, serial, both files green alone first: 22 passed; 271 s) has exactly main's ten names. Both load-sensitive names are acceptance tests that spawn host processes and touch no path changed by this ticket; they are reported here, not hidden. The first revision09 return, committed at `76e585d2` with `BLOCKED` on the strength of run 1, is replaced by the section above.
