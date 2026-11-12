# Continuous Workflow Governance POC — Ticket Set

> Commit identifiers in this record that predate 2026-11-03's identity rewrite are the pre-rewrite identifiers; read them through `doc/reviews/workflow-governance/evidence/47/commit-identity-rewrite-2026-11-03.txt` (old commit, new commit, identical tree).

> Approved specification: [workflow-governance.md](../../spec/workflow-governance.md) (`SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P`). This ticket set creates no implementation authority by itself.

## Delivery objective

Deliver one control-plane policy vertical slice: completion evidence must re-enter the Router, safe stages continue in the active task, declared authority gates wait precisely, unsafe conditions halt, and implementation work returns its evidence or a requirement-change event to the control plane. The slice applies the same rules to formal frontend handoff without adding a target-project runtime dependency.

## Ticket status

| Ticket | User-observable capability | State | Required authority |
| --- | --- | --- | --- |
| [01-enforce-continuation-and-handoff](01-enforce-continuation-and-handoff.md) | Post-commit Router continuation, typed implementation return, and policy/template enforcement | `DONE` | Review approved; integrated into `main` by merge `2f545c8` (the ticket file records the closure; this row had gone stale) |
| [02-repo-contained-worktree-layout](02-repo-contained-worktree-layout.md) | Every agent's worktree lives under the repository root, proven host-side | `CLOSED` | Owner-executed 2026-08-19; R1-R6 green, reverse mutation proven. The dispatch-admission gate its R3 anticipated is now wired by workstation-dispatch W1 |
| [03-suite-order-fragility](03-suite-order-fragility.md) | A poisoned shared runtime root is reported once, with its cause and remedy, instead of eighty misleading failures | `CLOSED` | Real cause found: per-process claim map versus a shared on-disk root, orphaned by concurrent pytest processes. The opening diagnosis was wrong and is corrected in place |
| [04-skill-implies-a-runtime-that-may-not-exist](04-skill-implies-a-runtime-that-may-not-exist.md) | The skill no longer narrates wakes nothing performs; agents must verify automation readiness before claiming any automatic effect | `CLOSED` | Found by the owner watching a false wake narrative on a real project; ships as 0.4.4 |
| [47-gates-first-governance-rewrite](47-gates-first-governance-rewrite.md) | Workflow section 0 states that state lives in files and transitions are decided by scripts; CodeReview names the integration script as executor | `REVIEW_APPROVED` | Correction review of closure revision09 APPROVED on `9483ef19`; owner confirmed the descriptor decision (F-05) on 2026-11-03 |
| [48-port-gate-scripts](48-port-gate-scripts.md) | Dispatch lint, receipt fence check and index pins run from the plugin with the fixed exit-code contract | `REVIEW_APPROVED` | Initial review of closure revision05 APPROVED on c10; integrated onto the wave-1 branch |
| [49-wording-drift-and-vendor-names](49-wording-drift-and-vendor-names.md) | Governance documents name roles and profiles, never vendor or model literals | `REVIEW_APPROVED` | Correction review of closure revision05 APPROVED on `5ad316bf`; lands with ticket 47 on this line |
| [50-merge-queue-integration](50-merge-queue-integration.md) | An approved candidate lands by script from the merge queue: fast-forward, affected specs and invariants green in a verified integration clone, one atomic two-branch push, CI read back | `INTEGRATED` (`64010e6e` at `b95b4acd`; red readback cleared by 64) | Wave 2; R4-2, R4-4, R4-7, R4-8 |
| [51-evidence-gate](51-evidence-gate.md) | A receipt proves every cell (five fields, digests, LF captures, byte-identical blocks, exit lists) or the evidence gate is red | `INTEGRATED` (`6fbec950`) | Wave 2; R4-2, R4-7 |
| [52-requirement-snapshot](52-requirement-snapshot.md) | Requirement snapshots are taken, verified and diffed as versioned files that are never overwritten | `INTEGRATED` (`64251c9a`) | Wave 2; R4-5, R4-7 |
| [53-contract-gate](53-contract-gate.md) | Every active requirement has a spec, every spec cites its source at the recorded digest, binds no retired requirement, has no literal expected value and names a mutation | `INTEGRATED` (`c876bd46`) | Wave 2; R4-2, R4-6, R4-7, R4-8 |
| [54-coverage-map-guard](54-coverage-map-guard.md) | A test removed between two commits is carried, dropped with a reason or escalated in the coverage map, or the guard is red | `INTEGRATED` (`8fc352d1`) | Wave 2; R4-2, R4-8 |
| [55-preflight-gate](55-preflight-gate.md) | Every tool a dispatch names starts and serves before the first product edit, or the run stops as a tool fault | `INTEGRATED` (`c3aa5a5f`) | Wave 2; R4-2, R4-3, R4-8 |
| [56-tool-repair-guard](56-tool-repair-guard.md) | A tool-repair commit touches only the declared allowlist and never a spec, ledger, product source or gate script | `INTEGRATED` (`cbb8306d`) | Wave 2; R4-3, R4-8 |
| [57-state-file-templates](57-state-file-templates.md) | A project created from the template starts with the ticket state row, receipt, queue file and integration configuration the gates read | `INTEGRATED` (`f423748b` at `7da279a7`) | Wave 2; R4-1, R4-7, R4-8 |
| [58-governance-hardening-row13](58-governance-hardening-row13.md) | A reworded document that brings a retired rule back goes red in the plugin's own tests, and the wave-1 scripts close the gaps their review carried | `INTEGRATED` (`02814a05` at `88321851`, CI green) | Wave 2; R4-1, R4-4, change-log row 13 |
| [59-ci-linux-windows](59-ci-linux-windows.md) | Every push runs the whole suite on Linux and Windows, green only when each failure is registered by name with a reason | `INTEGRATED` (`e067b81b` at `ea51e1c1`, CI green) | Wave 2 acceptance; R4-6, readiness criterion 2 |
| [60-gate-hardening-carried](60-gate-hardening-carried.md) | The findings carried when the six wave-2 gates were approved under rule B are pinned or closed, the two that guard a forbidden change first | `INTEGRATED` (`1c0fb917` at `093f221e`) | Wave 2; R4-2, R4-4, CodeReview §5 rule B |
| [61-wave2-end-to-end](61-wave2-end-to-end.md) | One ticket goes from a requirement snapshot to a landed merge commit on a fixture project, and a fresh session finishes it from the ticket, receipt and queue files alone | `IN_PROGRESS` (part A passes; part B evidence corrected, clean rerun next) | Wave 2 acceptance; readiness criterion 1 |
| [62-registered-known-failures](62-registered-known-failures.md) | Every failure CI registers that is not an environment failure is fixed in its test or carries a confirmed cause and an open follow-up | `INTEGRATED` (`bb9c4502` at `68c318a5`, CI green) | Wave 2 acceptance follow-up; ticket 59 S59-02, S59-03, S59-05 |
| [63-short-name-containment](63-short-name-containment.md) | A Windows 8.3 short-name alias of the repository root is the same path for containment, while junctions and reparse points stay refused | `INTEGRATED` (`8e6aed94` at `5c704541`, CI green) | Wave 2 acceptance follow-up; ticket 59 S59-04; AGENTS.md P0 |
| [64-integrate-hook-tests-posix](64-integrate-hook-tests-posix.md) | The two integration-script tests that make the remote refuse a push write their hook executable, so they fail closed on Linux as on Windows | `INTEGRATED` (`4283a006` at `70a741f7`, CI green) | Wave 2; red CI readback of `b95b4acd` (R4-7 follow-up) |

## Shared baseline

- Specification: `SPEC-AI-WORKFLOW-WORKFLOW-GOVERNANCE-20260805-01KZ6T8V2R4Y6B8D0F2H4J6M8P` (`APPROVED` on `2026-08-05`)
- Change: `CHG-20260805-009`
- Context: [workflow-governance/main.md](../../../doc/context/workflow-governance/main.md)
- Documentation baseline: `04146af` (`docs: draft continuous workflow governance`)
- Delivery environment: local Python workflow-router POC plus detached Codex/Claude guidance source. No hosted service, background worker, target-project dependency, or external provider is in scope.

## Authority and handoff

The control plane owns the tickets, the dispatch and the review binding; it does not implement. Implementation seats work in `.worktrees/<ticket-id>` under the repository root or in the disposable clone the dispatch names; the reviewer seat owns the review conclusion; integration is run by the versioned integration script from the merge queue (Revision 04 R4-4). The earlier line's implementation binding (branch `codex/implementation-private-router-saas-01`, base `7769710`, owner approval of `2026-08-05`) is a record kept in Git history.

The implementation handoff consists of the approved specification, this ticket, Context references, TDD cuts, exact target paths, and the return-event rules. A completion returns evidence for review; a requirement, architecture, public-contract, frontend composition/DI, or acceptance change returns `REQUIREMENT_CHANGED` to Grill.
