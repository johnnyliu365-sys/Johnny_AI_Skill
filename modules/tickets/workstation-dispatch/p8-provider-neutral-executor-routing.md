# P8R｜Provider-neutral executor routing

| Field | Value |
| --- | --- |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-EXECUTOR-ROUTING-20260822-01M4P6R8T0V2X4Z6B8D0F2H4J6` revision 01 / AC-01 through AC-10 |
| PRD / change | `PRD-20260822-030` / `CHG-20260822-030` |
| Sealed Context | `CTX-EXECUTOR-ROUTING-20260822-01` / `doc/context/executor-routing/codex-provider-neutral-executor-routing.md` / baseline `67e8fea352029a1156bb661c1613988fea3d3a6f` |
| State | `APPROVED / NOT_DISPATCHED` |
| Acceptance Closure Set | `CLOSURE-EXECUTOR-ROUTING-P8R-01` / revision 01 |
| Control owner | Current-session Codex reviewer; the reviewer is the sole Agent-to-Agent orchestrator. |
| Implementation owner | Unassigned until receipt admission. Standard profile reference: `implementation-standard` (current profile data: Luna/xhigh). |
| Independent reviewer | Standard profile reference: `ticket-review` (current profile data: Terra/xhigh); verified capability rank must be greater than or equal to the implementation profile's rank. |
| Worktree / branch / task / receipt / correlation | Unissued. The admitted dispatch descriptor is the sole authority to populate them. |
| Delivery profile / resource plan | `HIGH_ASSURANCE` / one implementation lane, one independent reviewer, zero helpers, no host/process/provider effect. |
| Implementation language | Python 3.11; frozen Pydantic contracts, explicit finite enums and `mypy --strict`. |
| XSS classification | `N/A`: no Browser/WebView/HTML/DOM/JavaScript source, sink or renderer. |
| Environment | Local pure Python tests only. Claude/Codex credential, CLI, host execution and runner capabilities are not dependencies of this ticket. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/executor_routing.py
create = library/local_orchestration/executor_routing.py
modify = tests/test_executor_routing.py
create = tests/test_executor_routing.py
forbid = library/local_orchestration/dispatch_session.py
forbid = library/local_orchestration/dispatch_authority.py
forbid = library/local_orchestration/worker_assignment.py
forbid = library/local_orchestration/work_queue.py
forbid = library/local_orchestration/document_mutation_gate.py
forbid = modules/tickets/
forbid = doc/
forbid = skills/
```

## Observable closure

Implement one pure `ExecutorRoutingResolver` and its typed contracts. Given a normalized routing
table, normalized profile registry and a typed request, it returns one selected profile and, for
an implementation route, the exact reviewer binding; otherwise it returns one finite named
rejection. It performs no filesystem, Git, process, credential, receipt, task, worktree, runner
or provider operation.

The route table stores only semantic profile references. Provider/model/effort and verified
capability rank exist only in injected profile data. Tests use fictitious provider/model values;
no resolver source literal may name a real provider or model.

## Frozen contracts and behavior

Create the named public contracts from SPEC revision 01:

- `RoutingPurpose`, `ProfileAvailability`, `VerifiedCapabilityRank` and `ResolutionStatus`
  finite enums.
- Frozen validated `ExecutorProfileRef`, `ExecutorProfile`, `RoutingKey`,
  `HardTicketAssessment`, `ReviewBinding`, `OwnerOverrideRecord`, `RouteRequest` and
  `RouteResolution` types, with explicit nullability and no `Any`.
- An injected `ExecutorRoutingTable` and `ExecutorProfileRegistry` whose invalid/missing/
  duplicate data becomes a named rejection rather than a default.
- A pure `ExecutorRoutingResolver.resolve()` result with no host/effect capability.

Required mappings are data-driven:

1. Project-initial review and requirement-change review that includes a complex-decision
   inventory select only their configured decision-support profile.
2. General ticket opening/review select only the configured supervisor/reviewer profile.
3. Normal implementation selects its configured implementation profile and binds a reviewer
   whose verified capability rank is not lower.
4. A Terra implementation exception requires a same-ticket, same-closure
   `HardTicketAssessment` proving both no further valid decomposition and a named capability
   gap beyond the standard implementation profile. That result binds the configured elevated
   reviewer for the same ticket only.
5. A bounded failed implementation/review cycle returns `MODEL_CAPABILITY_INSUFFICIENT` then
   `ARCHITECTURE_OWNER_REQUIRED`; it never chooses a further implementation profile.

An owner override must include an owner decision reference and select a registered,
`AVAILABLE` profile. It cannot bypass the hard-ticket assessment or produce a reviewer binding
whose rank is lower than the implementation rank.

## TDD and type preflight

| Cell | Required executable behavior / expected named outcome |
| --- | --- |
| T1 | Two fictitious providers resolve the same semantic routing purposes without resolver source changes. |
| T2 | Initial/complex-change review and normal ticket opening/review select their configured references only. |
| T3 | Normal implementation resolves its configured implementation profile plus a reviewer binding whose rank is equal or higher. |
| T4 | Missing, empty, malformed, duplicate or ambiguous route/registry data returns its specified fail-closed result; no default route exists. |
| T5 | Unavailable, stale or unknown selected profile rejects rather than switching provider/profile. |
| T6 | Missing, stale, cross-ticket, wrong-closure or self-asserted hard-ticket assessment rejects; valid assessment produces the configured Terra-implementation/Sol-review binding for that exact ticket. |
| T7 | A lower-rank reviewer binding returns `REVIEWER_CAPABILITY_INSUFFICIENT`. |
| T8 | Missing/unknown/unavailable owner override rejects; a valid override is auditable and cannot weaken review or bypass T6. |
| T9 | Bounded model insufficiency returns the architecture-owner route, with no inferred implementation fallback. |
| T10 | Source-boundary scan proves the resolver imports no dispatch, receipt, host-launch, credential or runner namespace. |
| M1 | Add a default route; T4 turns red, then green after exact restoration. |
| M2 | Accept a forged/cross-ticket hard-ticket assessment; T6 turns red, then green after exact restoration. |
| M3 | Reverse the reviewer-rank comparison; T7 turns red, then green after exact restoration. |
| M4 | Accept an unavailable override profile; T8 turns red, then green after exact restoration. |
| M5 | Add a real provider/model literal to resolver source; T1/T10 turns red, then green after exact restoration. |

Strong-type preflight constructs ordinary public success-path instances for every contract, then
rejects unknown enum values, malformed references, missing assessment evidence, invalid
nullability and bypass construction. `model_construct`, casts, `Any`, dynamic member lookup and
historical-object reuse cannot be success evidence.

## Verification

The implementation owner runs only the focused closure in its admitted worktree:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_executor_routing.py
py -3.11 -m mypy --strict library/local_orchestration/executor_routing.py tests/test_executor_routing.py
```

The reviewer runs the same focused closure, all five restored reverse-mutation cells, the full
regression suite, source-boundary checks and one independent reviewer counter-mutation through a
different path. Run only one pytest process per checkout. New behavior records named green
evidence; it does not make a ceremonial first-red claim.

## Ownership, profile and return

- Default admission is one Luna/xhigh implementation owner and one Terra/xhigh independent
  reviewer. This ticket does not pre-approve the hard-ticket exception; if its complete closure
  later requires one, return `HIGH_ASSURANCE_REQUIRED` for an owner-reviewed ticket revision.
- The implementation owner receives identifier-only dispatch, may modify only the declared
  boundary, does not commit, does not integrate and cannot control another Agent. The reviewer
  inspects the returned worktree, writes the candidate commit after approval, and is the only
  role that may submit it to the integration gate.
- Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED`,
  `BLOCKED -> HALT` with the named failed cell, or
  `CHANGE_DETECTED -> REQUIREMENT_CHANGED`. No return authorizes a provider invocation, login,
  runner start, merge, push, release or deployment.

```johnny-status
id = P8R
title = Provider-neutral executor routing
state = APPROVED_NOT_DISPATCHED
stage = D | typed route/profile resolver | OPEN
stage = E | hard-ticket and reviewer-rank gates | OPEN
stage = M | five reverse mutations | OPEN
```
