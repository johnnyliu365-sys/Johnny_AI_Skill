# R03-03 — Senior-only dispatch gateway and high-assurance capability proof

## Admission

| Field | Value |
| --- | --- |
| State / closure | `PLANNED / HIGH_ASSURANCE_REQUIRED / NON_DISPATCHED` / `R03-03-CS-01` |
| Authority | `PRD-20260816-026` / `CHG-20260816-026`; [`REQ-20260816-026`](../../../../doc/requirements/active/2026/workflow-governance/REQ-20260816-026.md); [`ADR-20260816-015`](../../../../doc/adr/ADR-20260816-015-live-receipt-dispatch-settlement.md); Revision 03 AC-26–AC-30; [`DEC-20260816-521`](DEC-20260816-521-r03-live-dispatch-decomposition.md) |
| Context / baseline | `doc/context/receipt-bound-role-supervision/main.md` Revision 03 / reviewed `R03-02` integration commit, recorded by later receipt; no baseline inferred now |
| Dependency / admission | `R03-01` and `R03-02` `COMPLETE / APPROVED / INTEGRATED`; independent reviewer, high-assurance implementation profile and disposable-resource plan must be approved before implementation |
| XSS | `XSS_N/A`; native host-control boundary only |

## Observable closure

The sole privileged composition root either proves an exact Senior-only gateway and complete
receipt-bound supervision chain using a disposable owned metadata root, or returns truthful
finite `CAPABILITY_UNAVAILABLE` before any live task/message/branch/wake effect. Tool inventory,
one-shot thread read, synthetic success and prompt-only delivery never qualify. A successful fake
test is boundary evidence only and does not authorize real dispatch.

Create only after high-assurance admission:

```text
library/local_orchestration/reviewer_dispatch_gateway.py
library/local_orchestration/reviewer_dispatch_composition.py
library/local_orchestration/__init__.py
tests/test_reviewer_dispatch_gateway.py
tests/test_reviewer_dispatch_capability_proof.py
```

The gateway owns only `ReviewerDispatchGatewayPort` adaptation and typed readback. The composition
root is the only verified `SUPERVISOR_REVIEWER` caller and receives an already claimed R03-02
operation. It re-resolves exactly six envelope fields: `ACTION_REQUIRED`, `dispatch_ref`,
`registry_commit`, `ticket`, `receipt`, `owner_task`. Before its one permitted host call it proves
task/worktree/branch/baseline, model/profile, Context epoch, restricted-tool policy and
Git-event/lease/RoleWakePort capability. No implementation owner receives a control port or alias.

Production rejects process-local registry/fake composition. No heartbeat, scheduler, cron,
watchdog, recurring thread/Git/filesystem read, polling, timer loop, target-local state, database,
service/MCP state, target mutation, push/release/deploy, Secret or raw prompt/content is allowed.
Current-host unsupported is only a finite capability result: it creates no receipt, settlement,
dispatch confirmation or execution-start assertion.

## High-assurance TDD / proof

| Cell | First-red / proof | Green or truthful halt |
| --- | --- | --- |
| `R03-03-T01` envelope / ownership | focused gateway test fails before production composition exists | extra/missing/copied body/path/URI/prompt, wrong Senior/task/receipt/descriptor/registry and implementation-owner call yield zero host effects |
| `R03-03-T02` delivery truth | dedicated fake-adapter test supplies each host outcome | delivered settles only R03-02 claim; replay/quarantine yields zero calls; no cell claims execution start |
| `R03-03-T03` capability | tool-inventory, synthetic-success, absent subscription or absent wake-proof test first returns `CAPABILITY_UNAVAILABLE` | only separately proved adapter + chain may reach host-call branch; unsupported current host is valid fail-closed evidence |
| `R03-03-T04` source gate | source gate first fails before gateway exists | reverse-mutate fake/process-local composition, recurring behavior, dynamic/bypass form and target persistence to red then restore |
| `R03-03-T05` integration | disposable owned-root acceptance uses a proved adapter boundary and no live task/message/branch/target write/wake | proves teardown/no ambient mutation; real effect needs a later separately authorized effect ticket |

Verification: focused proof tests, full unittest discovery, strict mypy, in-memory compilation,
source/reverse-mutation gates, disposable-root teardown, scope/diff/porcelain/cache readback and
independent CodeReview. No implementation begins without named high-assurance approval.

## Return and rollback

This capability-proof commit is separate from any real host-effect authority. Revert it and remove
only adapter-owned disposable records to restore fail-closed behavior; never delete target Git
history. `COMPLETED` cannot claim live capability without a later effect ticket; `BLOCKED` returns
`CAPABILITY_UNAVAILABLE` or exact finite capability failure; `CHANGE_DETECTED` routes to
architecture. It never dispatches PAG-01/PAG-02 or an Implementer.
