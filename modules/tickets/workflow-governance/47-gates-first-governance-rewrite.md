# 47｜Gates-first governance rewrite (documents only)

| Field | Binding |
| --- | --- |
| State / Closure | CONVERGENCE_REPLANNED / INDEPENDENT_REVIEW_PENDING; Closure revision06 (47-D1–D7, M1–M2) after the revision05 initial review returned CHANGES_REQUESTED with TICKET_DEFECT R5-03, R5-05 (revision04: R4-03, R4-05, R4-10; revision03: R3-01, R3-04; revision02: R2-01; revision01: initial and correction review both CHANGES_REQUESTED) |
| Authority | Owner 2026-11-03 takeover instruction; `PRD-20261103-043` / `CHG-20261103-043`; `modules/spec/workflow-governance.md` Revision 04 |
| Baseline | `a1cb6c1` (main); branch `cp/wave1-gates-first` |
| Grant / roles | Control plane authors the documents; independent review by a separate `ticket-review` seat before integration |
| Workspace | the control plane's own checkout of branch `cp/wave1-gates-first` (not disposable; its evidence runs there); the reviewer reproduces every cell in a fresh clone |
| Profile / limits | COMPACT: documents only; no runtime behaviour change — the policy digest pins in `library/workflow_router/profile.py` and `tests/test_workflow_router.py` move with the reference they pin; no installer, publication pin or target-project write |
| Language / return | Markdown; `ImplementationReturn` COMPLETED with the exact commit, the five document diffs and the pytest result of the document-pinning tests |

```johnny-boundary
modify = Workflow.md
modify = CodeReview.md
modify = modules/spec/workflow-governance.md
modify = doc/README.md
modify = doc/requirements/active/2026/workflow-governance/README.md
modify = modules/tickets/workflow-governance/README.md
modify = tests/test_adversarial_review_policy.py
modify = skills/johnny-project-takeover/SKILL.md
modify = skills/johnny-project-takeover/references/router-control.md
modify = skills/johnny-project-takeover/references/adversarial-review.md
modify = skills/johnny-project-takeover/references/codex-native-same-lifetime-delegation.md
modify = skills/johnny-project-takeover/references/delivery-profile.md
modify = skills/johnny-project-takeover/references/model-role-routing.md
modify = modules/spec/review-assurance.md
modify = skills/johnny-project-takeover/
modify = modules/spec/
modify = doc/runbooks/dispatch-model-profile.md
modify = AGENTS.md
modify = library/workflow_router/profile.py
modify = tests/test_workflow_router.py
create = doc/reviews/workflow-governance/evidence/47/
create = modules/tickets/workflow-governance/49-wording-drift-and-vendor-names.md
create = doc/reviews/workflow-governance/47-gates-first-governance-rewrite-code-review.md
create = doc/requirements/active/2026/workflow-governance/REQ-20261103-043.md
create = doc/HARNESS-CHANGELOG.md
create = modules/tickets/workflow-governance/47-gates-first-governance-rewrite.md
create = modules/tickets/workflow-governance/48-port-gate-scripts.md
modify = template/modules/tickets/README.TEMPLATE.md
forbid = .github/
forbid = .claude-plugin/
forbid = .codex-plugin/
forbid = template/*
forbid = template/modules/*
forbid = template/modules/tickets/TEMPLATE.md
```

## One observable behavior

An agent that opens `Workflow.md` section 0 reads that state lives in ticket, receipt and
merge-queue files and that transitions are decided by scripts with the fixed exit-code
contract; it is no longer told to re-enter a Router or to hold a live descriptor. `CodeReview.md`
keeps the reviewer as the sole owner of the review conclusion and names the integration script,
not the reviewer, as the executor of integration. The governance SPEC carries Revision 04 with
rules R4-1 to R4-6. The improvement checklist is replaced by a change log on this line; the
revision-135 checklist stays on branch `codex/skill-improvement-checklist` where it was written.

## Acceptance

| Cell | Check | Expected |
| --- | --- | --- |
| D1 | `pytest tests/test_workflow_router.py tests/test_plugin_policy_and_response.py tests/test_adversarial_review_policy.py tests/test_plugin_payload_boundary.py` | same pass set as main `a1cb6c1` with the venv from `requirements-dev.txt`; the four document-term tests pass |
| D2 | `grep -c "狀態只存在三種檔案" Workflow.md` | 1; and the section-zero anchors `#workflow-router`, `#role-boundary` still exist |
| D3 | `grep -c "Revision 04 R4-4" CodeReview.md` | 2 (the integration clause in section 2 and the integration sentence in section 5); the sentence "The reviewer alone owns the final review conclusion." is unchanged |
| D4 | `grep -c "^## Revision 04" modules/spec/workflow-governance.md` | 1; R4-1 to R4-6 present |
| D5 | `python doc/reviews/workflow-governance/evidence/47/d5_union.py` (committed script; reads the three boundary blocks at HEAD and tags every path of `git diff --name-only a1cb6c1..HEAD`) | exit 0: no path outside every boundary; the policy digest pins for router-control.md, review-checks.md and implementation-authority.md move with the documents under `CHG-20261103-043` |
| D6 | `pytest tests -q` full suite on the candidate and on a fresh clone of main `a1cb6c1`, both in the same environment and both raw outputs committed under `doc/reviews/workflow-governance/evidence/47/` | the candidate's failure-name set is a subset of main's run; both sets listed by name in the receipt |
| D7 | `python doc/reviews/workflow-governance/evidence/47/d7_sweep.py` (committed script, revision06 instrument): paragraph-joined units over `skills/`, `modules/spec/`, `Workflow.md`, `CodeReview.md`, `AGENTS.md`, `doc/runbooks/`, `template/`; patterns a1 (a reviewer who integrates), a2 (a reviewer who submits), a3 (a fixed integrator role), b (a receipt-bound bridge, live descriptor or merge-queue file that is mandatory, required, kept, retained, reserved or the default); every hit printed with its class | exit 0: every hit is one of: states the Revision 04 rule with a pattern-specific word-bounded marker in its own unit; a dated record row or a row under an Amendments, Revision Signatures or Approval Record heading; a ticket or review record of this line; for pattern b, a document whose first 40 lines carry the scope note "not the default (R4-1)" (it describes the bridge's own mechanics). Zero hits classified LIVE RETIRED RULE |
| M1 | remove the exit-code sentence from Workflow.md section 0 | D2 still 1 but the reviewer must flag the contract loss; recorded as a review check, not a script |
| M2 | restore `skills/johnny-project-takeover/references/model-role-routing.md` from commit `a47e976b` (the text the revision04 review flagged as R4-02 and R4-04) in a disposable edit, run D7, restore | D7 exit 1 with at least two LIVE hits in that file; `git status --porcelain` empty after restore |

## Correction 1 (after REVIEW-001 `CHANGES_REQUESTED`)

| Finding | Class | Disposition |
| --- | --- | --- |
| F-01 | IMPLEMENTATION_DEFECT | Section 0 now defines "Router" as the gate scripts over the state files and states that every "return to the Router" sentence in this file and in router-control.md reads as: write the typed record into the receipt, next gate reads the files. SKILL.md item 4 says the same. |
| F-02 | IMPLEMENTATION_DEFECT | Section 0 adopts the router-control.md Continuation rule 2 list for `WAIT_FOR_HUMAN` and states R4-3 as a filter, not a second list. |
| F-03 | IMPLEMENTATION_DEFECT | R4-2 integration row and section 0 require an independent review record with verdict `APPROVED` before integration. |
| F-04 | TICKET_DEFECT | Boundary widened to SKILL.md, router-control.md and adversarial-review.md; the contradictions named are edited at their lines; metadata no longer lists paths. |
| F-05 | REQUIREMENT_CHANGED | Owner decision recorded in R4-1 and R4-7: the live descriptor stays transitional until wave 3; the queue carries single-consume and anti-replay (key, states, compare-and-swap). |
| F-06 | TICKET_DEFECT | R4-7 adds the wave-2 schemas: queue entry, receipt cell, snapshot row, contract-gate codes, post-push readback, exit mapping. |
| F-07 | EVIDENCE_DEFECT | The test pins "is its admission, not its executor". |
| F-08 | IMPLEMENTATION_DEFECT | Change log names no target project. |
| F-09 | IMPLEMENTATION_DEFECT | Items 02 and 03 carry their residuals to wave 2. |
| F-10 | IMPLEMENTATION_DEFECT | Rows 47 and 48 sit inside the status table. |
| F-11, F-12 | OUT_OF_SCOPE_HARDENING | Deferred to wave 2 tickets. |
| F-13 | EVIDENCE_DEFECT | Review record and `ImplementationReturn` committed at `doc/reviews/workflow-governance/47-gates-first-governance-rewrite-code-review.md`. |

## Convergence replan (closure revision02, after correction 1 re-review `CHANGES_REQUESTED`)

Per CodeReview.md section 5 the initial review plus one correction review were used on revision01; the ticket returns to the control plane for re-planning instead of a third correction. Revision02 widens the closure to every file that states who integrates or how the Router is re-entered, moves the router-control policy digest pins with the document, and adds D6 (full suite with committed raw output).

| Finding | Disposition in revision02 |
| --- | --- |
| N-01 | `library/workflow_router/profile.py` and `tests/test_workflow_router.py` pin the new router-control.md digest computed by `policy_digest`. |
| N-02 | The receipt lists the full-suite failure set by name with the raw output committed under evidence; deviations stated. |
| N-03 | Section 0 and router-control.md say host absolute paths are excluded; repository-relative paths are allowed. |
| N-04 | REQ Scope lists every widened file. |
| F-01 leftovers | AGENTS.md item 5, SKILL.md AUTO_CONTINUE bullet and the codex-native reference now say record-then-gate. |
| F-03 | R4-7 binds `review_candidate` = `candidate` and `reviewer` != `submitter`; section 0 chain includes the coverage-map guard. |
| F-04 | SKILL.md and router-control.md no longer say the reviewer integrates. |
| F-05 | Decision recorded in the REQ (open owner decision row) and in the Revision 04 signatures. |
| F-06 | R4-7 adds lock recovery, `LANDED_CI_RED`, queue path, affected-spec rule, snapshot file format and location. |
| F-07 | The test pins both halves of the new sentence and rejects the old one. |
| F-11, F-12 | Wording drift fixed here (Workflow.md section 5, CodeReview.md section 5); vendor and model names tracked by ticket 49. |

## Re-plan to closure revision03 (after the revision02 initial review `CHANGES_REQUESTED`)

The revision02 initial review (record: `doc/reviews/workflow-governance/47-gates-first-governance-rewrite-code-review.md`, "Revision02 initial review") returned R2-01 as a `TICKET_DEFECT`; per CodeReview.md §4 item 3 the closure is rebuilt before the fix. Cells D2 and D3 are re-frozen against the delivered text; the text is not reverted. Revision03 keeps D1, D4, D5, D6 and M1 unchanged.

| Finding | Class | Disposition in revision03 |
| --- | --- | --- |
| R2-01 | TICKET_DEFECT | D2 greps the section-0 phrase that exists ("狀態只存在三種檔案"); D3 expects 2 because section 5 also cites R4-4 since correction 1. |
| R2-02 | EVIDENCE_DEFECT | The `ImplementationReturn` for revision03 lists every cell D1–D6 and M1 with its result; every raw capture under `doc/reviews/workflow-governance/evidence/47/` opens with the candidate sha and the command. |
| R2-03 | IMPLEMENTATION_DEFECT | AGENTS.md states that pending dispatch is ticket state plus queue row (R4-1, R4-7) and that the live descriptor is the transitional cross-lifetime path, not the default. |
| R2-04 | TICKET_DEFECT | Profile row above and the REQ effect-boundary row state the pin exception: digest pins move with the reference; no behaviour change. |
| R2-05 | IMPLEMENTATION_DEFECT | router-control.md note lists `LANDED_CI_RED` among the refused terminal states. R4-7: lock reclaim no longer depends on a liveness test; clearing `LANDED_CI_RED` is defined; `pages.json` is defined. |
| F-03 residual | IMPLEMENTATION_DEFECT | R4-7: the integration script reads `review_candidate` and `reviewer` from the review record; queue-row copies that differ bounce with `REVIEW_MISMATCH`. |
| F-07 residual | EVIDENCE_DEFECT | `tests/test_adversarial_review_policy.py` pins the whitespace-normalised executor phrase "Integration is executed by the versioned integration script from the merge queue". |
| F-05 | REQUIREMENT_CHANGED (recorded) | Owner confirmation of the descriptor decision is still pending; it gates integration onto `main`, not this review. |
| R49-06 (from ticket 49) | OUT_OF_SCOPE_HARDENING | Host absolute paths removed from this ticket's Workspace row and from the review record; raw logs are committed under evidence instead of referenced on a host. |
| D5 wording (control plane, before the revision03 review) | TICKET_DEFECT | D5 said "only the paths in the boundary block"; since ticket 49 shares the branch, its review record and evidence directory also appear in `a1cb6c1..HEAD`. D5 now names both boundary blocks. |
| N49-05 (from ticket 49 revision02 review) | OUT_OF_SCOPE_HARDENING | Raw pytest captures under `evidence/47/` carry the checkout and interpreter paths. Carried to the wave-2 evidence-gate ticket as a rule: the capture step strips the checkout root and the interpreter root before a capture is committed. Existing captures stay as recorded. |

## Re-plan to closure revision04 (after the revision03 initial review `CHANGES_REQUESTED`)

Review record section "Revision03 initial review". R3-01 and R3-04 are `TICKET_DEFECT`; the closure is rebuilt here, in its own commit, before any content or evidence commit of revision04. Boundary widened to `delivery-profile.md`, `model-role-routing.md` and `modules/spec/review-assurance.md`; D5 re-frozen as the union of the boundaries of every ticket on this line; the Workspace row states where the evidence runs.

| Finding | Class | Disposition in revision04 |
| --- | --- | --- |
| R3-01 | TICKET_DEFECT | Boundary widened. delivery-profile.md and model-role-routing.md say the reviewer owns the conclusion and the integration script runs integration (R4-4); the review-assurance SPEC gets an amendment row: ARA-01 reads "review conclusion" and integration by script under `CHG-20261103-043`. REQ Scope lists the three files. |
| R3-02 | IMPLEMENTATION_DEFECT | codex-native reference: the reviewer owns waiting, receipt of the typed result, review and reverse mutation; integration is the script's. |
| R3-03 | IMPLEMENTATION_DEFECT | router-control.md: the receipt-bound bridge is available for a cross-lifetime handoff until wave 3, not mandatory. Workflow.md section 0, AGENTS.md and R4-1 say the same thing in the same words: a pending dispatch is the ticket's state row plus the digest of its dispatch file; the queue holds integration candidates only. |
| R3-04 | TICKET_DEFECT | D5 frozen here, before delivery, as the union of the boundaries on this line. |
| R3-05 | IMPLEMENTATION_DEFECT | R4-7: an entry with the `clears` field set to the red entry's key is the one exemption admitted while the block holds; `reason` carries bounce codes only. |
| R3-06 | TICKET_DEFECT (wave 2) | R4-7 defines the review-record block the integration script reads: the last fenced `review-verdict` block whose `candidate` equals the queue candidate; `reviewer` is a seat identity string, not a role label. Records on this line add the block when the wave-2 script lands. |
| R3-07 | OUT_OF_SCOPE_HARDENING | Carried to the wave-2 contract gate: the integrator rule is pinned in every reference that states it, not only in CodeReview.md. |
| R3-08 | EVIDENCE_DEFECT | Workspace row corrected: evidence runs in the control plane's checkout; the reviewer's fresh-clone run is the independent reproduction. |
| R3-09 | OUT_OF_SCOPE_HARDENING | Already routed (N49-05 row above). |
| F-05 | REQUIREMENT_CHANGED (recorded) | Unchanged: owner confirmation pending; gates integration onto `main`. |

## Re-plan to closure revision05 (after the revision04 initial review `CHANGES_REQUESTED`)

Review record section "Revision04 initial review". R4-03, R4-05 and R4-10 are `TICKET_DEFECT`s: competing statements sit in references and SPECs outside every boundary, and the new default path was named but not defined. Instead of widening file by file, revision05 makes the check governance-wide: D7 sweeps the whole governance set for the two retired rules with every hit classified, the boundary covers the skill directory, the SPEC directory and the dispatch runbook, D5 and D7 run committed scripts (R4-09), and D6 compares against a main run made in the same environment (R4-08). Frozen here before any content or evidence commit of revision05.

| Finding | Class | Disposition in revision05 |
| --- | --- | --- |
| R4-01 | IMPLEMENTATION_DEFECT | router-control.md Revision 04 note: the default is the ticket's state row plus the dispatch-file digest; the merge queue holds integration candidates. |
| R4-02 | IMPLEMENTATION_DEFECT | model-role-routing.md and SKILL.md: the receipt-bound route is available for a cross-lifetime handoff until wave 3 and is not the default. |
| R4-03 | TICKET_DEFECT | Boundary covers `skills/johnny-project-takeover/`; review-checks.md and implementation-authority.md scope their bridge rules to the receipt-bound route; their digest pins move. |
| R4-04 | IMPLEMENTATION_DEFECT | model-role-routing.md and the dispatch runbook: the approved candidate is submitted to the queue by the implementation owner or a budget holder who is not that candidate's reviewer; the reviewer never submits what it reviewed. |
| R4-05 | TICKET_DEFECT | Boundary covers `modules/spec/`; workflow-adoption-activation.md step 2 and project-authority-integration.md say integration runs by script; each approved SPEC gets an Amendments entry under `CHG-20261103-043`. |
| R4-06 | IMPLEMENTATION_DEFECT | R4-7: `clears` lists every red key the entry fixes; while blocks hold only an entry whose `clears` lists every currently red key is admitted. |
| R4-07 | TICKET_DEFECT (wave 2) | R4-7: `reviewer` and `submitter` share the format `seat:<profile>/<run-id>`; the script checks format and inequality; proving the host issued the identity is the wave-2 review-run receipt. CodeReview.md §3 tells reviewers to end the record with the `review-verdict` block. |
| R4-08 | EVIDENCE_DEFECT | Receipt M1 row reads the porcelain output correctly; D6 compares against a main run in the same environment, committed as `rev05-D6-main.txt`. |
| R4-09 | EVIDENCE_DEFECT | D5 and D7 run scripts committed under `evidence/47/`. |
| R4-10 | TICKET_DEFECT (wave 2) | R4-1 defines the dispatch file (the machine-form dispatch that dispatch lint admits) and the State-row entry `dispatch=sha256:<hex>`; the template field is delivered by the wave-2 state-file templates ticket. |
| R3-07 | OUT_OF_SCOPE_HARDENING | Unchanged: routed to the wave-2 contract gate (pin the integrator rule in every reference). D7 is the document-level check until then. |

## Re-plan to closure revision06 (after the revision05 initial review `CHANGES_REQUESTED`)

Review record section "Revision05 initial review". R5-03 (`TICKET_DEFECT`): the D7 instrument was line-based, used a narrow verb set and loose substring exemptions, and did not catch a counter-mutation; R5-05 (`TICKET_DEFECT`): the ticket template names a fixed integration owner and `template/` was forbidden. Revision06 replaces the instrument (paragraph-joined units, four patterns, word-bounded pattern-specific exemptions, a header scope note for bridge-internal documents) and adds M2, the counter-mutation that must turn D7 red; the boundary admits exactly the one template file. Frozen here before any content or evidence commit of revision06.

| Finding | Class | Disposition in revision06 |
| --- | --- | --- |
| R5-01 | IMPLEMENTATION_DEFECT | claude-code-plugin-distribution.md: the reviewer reviews after the returned result; integration runs by the integration script (R4-4); Amendments entry. |
| R5-02 | IMPLEMENTATION_DEFECT | adversarial-review.md: the cross-lifetime receipt and live-descriptor controls belong to the receipt-bound route, available until wave 3 and not the default (R4-1). |
| R5-03 | TICKET_DEFECT | D7 instrument replaced as described; M2 added. |
| R5-04 | IMPLEMENTATION_DEFECT | autonomous-collaboration-audit.md: guarded integration is run by the integration script (R4-4); Amendments entry. |
| R5-05 | TICKET_DEFECT | Boundary admits `template/modules/tickets/README.TEMPLATE.md`; its integration-owner field becomes an integration row naming the script (R4-4), no fixed integrator. |
| R5-06 | IMPLEMENTATION_DEFECT | router-control.md:116-121 scoped to the bridge path. |
| R5-07 | IMPLEMENTATION_DEFECT | dispatch runbook: the receipt-bound kind is the bridge route, available until wave 3 and not the default; the R4-1 default named as the cross-lifetime default. |
| R5-08 | IMPLEMENTATION_DEFECT | Workflow.md flowchart dispatch node names the ticket state row and dispatch-file digest; the descriptor only on the transitional bridge. |
| R5-09 | IMPLEMENTATION_DEFECT | executor-routing.md gets its Amendments entry (lines 195 and 240); plugin-distribution.md and receipt-bound-role-supervision.md get a scope note and an Amendments entry where their text is touched. |
| R5-10 | EVIDENCE_DEFECT | Receipt Deviations row generated from the D6 comparison, never stale text. |
| R5-11 | TICKET_DEFECT (wave 2) | R4-7: the inequality compares seat identities (profile and run) and the submitter must not appear as `reviewer` in any `review-verdict` block of the candidate's record; submission happens after the record exists and copies its fields; `clears` keys are written `<ticket>@<candidate>`; a red entry whose block has lifted is marked `CLEARED`. |
| R5-12 | TICKET_DEFECT (wave 2) | R4-1: the dispatch file lives in the target project at `doc/handoffs/<year>/governance/dispatch/<ticket>-<n>.yaml` (path parameterised) so any host can recompute the digest. |
| R3-07 | OUT_OF_SCOPE_HARDENING | Unchanged: routed to the wave-2 contract gate; D7 with M2 is the document-level check until then. |
