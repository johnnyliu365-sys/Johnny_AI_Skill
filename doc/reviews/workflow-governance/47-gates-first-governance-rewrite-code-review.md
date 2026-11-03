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
| 1 | `git clone --no-hardlinks --depth 50 -b cp/wave1-gates-first <repo> C:/Temp/claude/jas47-rv2` + LF normalisation | 0 (HEAD d581ebc) |
| 2 | `git diff --stat f4d4381..HEAD`; `git diff --name-only a1cb6c1..HEAD` | 0 (10 files +140/-18; 15 paths, all in the widened boundary) |
| 3 | D1 pytest (4 files) | 1 (4 failed: 3 environment failures identical to main + `SUBFAILED policy='router-control'`) |
| 4 | `diff` of the FAILED lines against the main log | 0, but this diff hides the SUBFAILED line; checked the summary by hand |
| 5 | pytest control_plane_mutation, payload_manifest, private_router_metadata_gate, ticket_status_template | 1 (1 failed / 146 passed; main 0) |
| 6 | TARA1 under M-old / M-A / M-B, restored after each, `git status --porcelain` empty | 1 / 0 / 1 |
| 7 | F-08..F-12 greps and reads | 0 |
| 8 | `git grep` of the router-control digest prefix | 0 (profile.py:209-210, test_workflow_router.py:296-297, 756-761, 2437) |

Raw log: `C:/Temp/claude/jas47-rv2-pytest-cand.txt`.

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
