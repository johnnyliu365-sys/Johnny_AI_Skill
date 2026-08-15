# R03-02 — Task/workspace admission and dispatch-claim settlement reducer

## Admission

| Field | Value |
| --- | --- |
| State / closure | `PLANNED / READY_LOW_MODEL / NON_DISPATCHED` / `R03-02-CS-01` |
| Authority | `PRD-20260816-026` / `CHG-20260816-026`; [`REQ-20260816-026`](../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-026.md); [`ADR-20260816-015`](../../../../doc/adr/ADR-20260816-015-live-receipt-dispatch-settlement.md); Revision 03 AC-26–AC-29; [`DEC-20260816-521`](DEC-20260816-521-r03-live-dispatch-decomposition.md) |
| Context / baseline | `doc/context/receipt-bound-role-supervision/main.md` Revision 03 / reviewed `R03-01` integration commit, recorded by later receipt; no baseline inferred now |
| Dependency / model | `R03-01` `COMPLETE / APPROVED / INTEGRATED`; one `gpt-5.6-luna` xhigh implementation lane |
| Language / resources | Python 3.11; `python -m mypy --strict library tests`; deterministic injected in-memory ports only; no helper or live host/task/worktree/Git effect |
| XSS | `XSS_N/A` |

## Observable closure

Given a valid active receipt and injected typed observations, return exactly one task/workspace
admission and non-transferable dispatch-claim transition, then reduce a supplied strict host
outcome into `DELIVERED`, `NO_EFFECT` or `EFFECT_UNCERTAIN`. This closure invokes no gateway and
does not read a live task/worktree, issue a receipt, create a branch, send a message or assert a
live capability.

Create only:

```text
library/local_orchestration/task_workspace_dispatch_admission.py
library/local_orchestration/dispatch_claim_store.py
library/local_orchestration/__init__.py
tests/test_task_workspace_dispatch_admission.py
```

`R03-01` contracts are upstream read-only. The application module owns strict port protocols and
the coordinator; the claim module owns the adapter/reducer for the injected installer-owned
metadata boundary. Composition injects receipt-read, admission-observation and claim-store ports;
it may not instantiate a gateway, process-local registry, thread/Git client, clock loop, timer,
target path or singleton.

The finite matrix includes both `WorkspacePreparationMode` values; every Revision-03
`TaskWorkspaceAdmissionKind`; `DELIVER_TICKET`; claim lifecycle
`ISSUED|CLAIMED|SETTLED|CANCELLED|QUARANTINED`; every claim-result kind; every
`HostDispatchOutcome`; and every `LiveDispatchDecisionKind`. `READY` or
`PREPARATION_REQUIRED` needs exact observed values and non-empty readback refs. Unavailable data
remains absent. `DELIVERED` requires delivery/task-revision evidence, `NO_EFFECT` forbids it, and
uncertain result quarantines claim/receipt. Fresh-branch mode grants only the later implementation
owner authority to create/switch its own branch.

## TDD / preflight

| Cell | First-red command | Green proof |
| --- | --- | --- |
| `R03-02-T01` admission | `python -m unittest tests.test_task_workspace_dispatch_admission.TaskWorkspaceAdmissionTests.test_both_branch_modes_and_every_rejection_are_finite_and_effect_free` fails before module creation | wrong Senior/task/worktree/profile/context/tool policy/baseline, dirty tree, branch conflict, unproved supervision and host unavailable are exact kinds with zero claim/gateway calls |
| `R03-02-T02` claim | `python -m unittest tests.test_task_workspace_dispatch_admission.DispatchClaimTests.test_claim_is_nontransferable_and_replay_or_concurrent_consume_has_zero_gateway_calls` fails before reducer creation | copied/forged/replayed/wrong descriptor/registry/Senior/task and storage failures have finite results and no second eligible call |
| `R03-02-T03` settlement | `python -m unittest tests.test_task_workspace_dispatch_admission.DispatchSettlementTests.test_no_effect_reuses_only_the_same_operation_and_uncertain_quarantines` fails before coordinator creation | delivered settles only the claim, no-effect restores only same operation, timeout/exception/missing identity quarantines and forbids retry/replacement |
| `R03-02-T04` source gate | `python -m unittest tests.test_task_workspace_dispatch_admission.DispatchAdmissionSourceGateTests.test_reducer_has_no_host_or_recurring_effect_surface` fails before module creation | reverse mutations reject gateway/thread/Git calls, heartbeat/polling/timers, dynamic/bypass forms and target persistence |

Run focused/full unittest, strict mypy, in-memory compile, `git diff --check`, and exact
scope/porcelain/cache readback. Ordinary constructor/round-trip and finite nullability matrices
must pass before green.

## Return and rollback

One integration commit changes only this scope. Revert it and quarantine only adapter-owned claim
state to roll back; never call a host or edit target history. `COMPLETED` returns full
admission/claim/settlement evidence; `BLOCKED` covers unavailable upstream store/receipt or
impossible typed readback; `CHANGE_DETECTED` returns to architecture. Completion unlocks only
high-assurance R03-03 admission, never dispatch.
