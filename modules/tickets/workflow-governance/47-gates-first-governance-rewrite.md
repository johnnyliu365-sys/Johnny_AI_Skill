# 47｜Gates-first governance rewrite (documents only)

| Field | Binding |
| --- | --- |
| State / Closure | CONVERGENCE_REPLANNED / INDEPENDENT_REVIEW_PENDING; Closure revision03 (47-D1–D6) after the revision02 initial review returned CHANGES_REQUESTED with TICKET_DEFECT R2-01 (revision01: initial and correction review both CHANGES_REQUESTED) |
| Authority | Owner 2026-11-03 takeover instruction; `PRD-20261103-043` / `CHG-20261103-043`; `modules/spec/workflow-governance.md` Revision 04 |
| Baseline | `a1cb6c1` (main); branch `cp/wave1-gates-first` |
| Grant / roles | Control plane authors the documents; independent review by a separate `ticket-review` seat before integration |
| Workspace | a disposable clone of branch `cp/wave1-gates-first` |
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
forbid = .github/
forbid = .claude-plugin/
forbid = .codex-plugin/
forbid = template/
```

## One observable behavior

An agent that opens `Workflow.md` section 0 reads that state lives in ticket, receipt and
merge-queue files and that transitions are decided by scripts with the fixed exit-code
contract; it is no longer told to re-enter a Router or to hold a live descriptor. `CodeReview.md`
keeps the reviewer as the sole owner of the review conclusion and names the integration script,
not the reviewer, as the executor of integration. The governance SPEC carries Revision 04 with
rules R4-1 to R4-6. The improvement checklist is replaced by a change log on this line; the
revision-135 checklist stays on the Codex branch where it was written.

## Acceptance

| Cell | Check | Expected |
| --- | --- | --- |
| D1 | `pytest tests/test_workflow_router.py tests/test_plugin_policy_and_response.py tests/test_adversarial_review_policy.py tests/test_plugin_payload_boundary.py` | same pass set as main `a1cb6c1` with the venv from `requirements-dev.txt`; the four document-term tests pass |
| D2 | `grep -c "狀態只存在三種檔案" Workflow.md` | 1; and the section-zero anchors `#workflow-router`, `#role-boundary` still exist |
| D3 | `grep -c "Revision 04 R4-4" CodeReview.md` | 2 (the integration clause in section 2 and the integration sentence in section 5); the sentence "The reviewer alone owns the final review conclusion." is unchanged |
| D4 | `grep -c "^## Revision 04" modules/spec/workflow-governance.md` | 1; R4-1 to R4-6 present |
| D5 | `git diff --stat a1cb6c1..HEAD` | only the paths in this boundary block or in ticket 49's boundary block (the two tickets share this branch; ticket 49's review record and evidence directory are its); the policy digest pins for router-control.md move with the document under `CHG-20261103-043` |
| D6 | `pytest tests -q` full suite, raw output committed under `doc/reviews/workflow-governance/evidence/47/` | failure set equals the main baseline (environment failures only), listed by name in the receipt |
| M1 | remove the exit-code sentence from Workflow.md section 0 | D2 still 1 but the reviewer must flag the contract loss; recorded as a review check, not a script |

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
