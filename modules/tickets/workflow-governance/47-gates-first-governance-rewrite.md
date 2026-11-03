# 47｜Gates-first governance rewrite (documents only)

| Field | Binding |
| --- | --- |
| State / Closure | CORRECTION_1_LOCAL / INDEPENDENT_REVIEW_PENDING; 47-D1–D5 revision02 |
| Authority | Owner 2026-11-03 takeover instruction; `PRD-20261103-043` / `CHG-20261103-043`; `modules/spec/workflow-governance.md` Revision 04 |
| Baseline | `a1cb6c1` (main); branch `cp/wave1-gates-first` |
| Grant / roles | Control plane (Claude) authors the documents; independent review by a separate reviewer seat (Opus) before integration |
| Workspace | clone `C:/Temp/claude/jas-main`, branch `cp/wave1-gates-first` |
| Profile / limits | COMPACT: documents only; no runtime, installer, publication pin or target-project write |
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
create = doc/reviews/workflow-governance/47-gates-first-governance-rewrite-code-review.md
create = doc/requirements/active/2026/workflow-governance/REQ-20261103-043.md
create = doc/HARNESS-CHANGELOG.md
create = modules/tickets/workflow-governance/47-gates-first-governance-rewrite.md
create = modules/tickets/workflow-governance/48-port-gate-scripts.md
forbid = library/
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
| D2 | `grep -c "狀態在檔案，轉移在腳本" Workflow.md` | 1; and the section-zero anchors `#workflow-router`, `#role-boundary` still exist |
| D3 | `grep -c "Revision 04 R4-4" CodeReview.md` | 1; the sentence "The reviewer alone owns the final review conclusion." is unchanged |
| D4 | `grep -c "^## Revision 04" modules/spec/workflow-governance.md` | 1; R4-1 to R4-6 present |
| D5 | `git diff --stat a1cb6c1..HEAD` | only the paths in the boundary block; `tests/test_adversarial_review_policy.py` changes exactly one pinned phrase because the rule it pinned changed under `CHG-20261103-043` |
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
