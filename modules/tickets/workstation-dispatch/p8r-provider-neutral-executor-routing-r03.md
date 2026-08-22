# P8R-R03｜Provider-neutral executor routing

| Field | Value |
| --- | --- |
| Artifact / closure | `P8R-EXECUTOR-ROUTING-03` / `CLOSURE-EXECUTOR-ROUTING-P8R-02` revision `02` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-EXECUTOR-ROUTING-20260822-01M4P6R8T0V2X4Z6B8D0F2H4J6` revision `02` / AC-01 through AC-11 |
| PRD / change | `PRD-20260822-030` / `CHG-20260822-030`, amended by `PRD-20260822-032` / `CHG-20260822-032` |
| Sealed Context / baseline | `CTX-EXECUTOR-ROUTING-20260823-02` / `doc/context/executor-routing/codex-provider-neutral-executor-routing-r02.md` / `f90d200b914aa91e0ffe63ef778668ac4024cc84` |
| State | `BLOCKED / REQUIREMENT_CHANGED / CHG-20260823-033` |
| Replaces | `p8-provider-neutral-executor-routing.md` revision `02`, which is `SUPERSEDED / CHG-20260822-032` and is not dispatch authority. |
| Control owner / reviewer | Current-session Codex reviewer; semantic `ticket-review` profile, Terra/xhigh. |
| Implementation owner | One current-session implementation owner; semantic `implementation-standard` profile, Luna/xhigh. |
| Elevation | Not authorized. A discovered indivisible capability gap returns `HIGH_ASSURANCE_REQUIRED`; it does not select Terra implementation. |
| Delivery stage / profile | `POC` / `STANDARD`; one lane, zero helpers. Evidence: single-component resolver, known-domain contract, reversible recovery, no security surface, no external effect. |
| Worktree / branch | Reviewer creates only `.worktrees/p8r-provider-neutral-executor-routing` at the exact baseline on `implement/p8r-provider-neutral-executor-routing`. |
| Known host gap | `KNOWN_GAP_WORKSPACE_BINDING_READBACK_UNAVAILABLE`; no task/workspace/profile/rank, receipt-delivery, runner or wake assertion is permitted. |
| Language / checker | Python 3.11; frozen Pydantic models, complete annotations, finite enums; `mypy --strict`. |
| XSS / effects | `N/A`; no Browser/WebView/HTML/DOM/JavaScript, host, process, credential, provider, receipt, task, worktree-control, runner or network effect in the implementation boundary. |

## Boundary declaration

```johnny-boundary
create = library/local_orchestration/executor_routing.py
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

## Observable closure and composition

Create one pure `ExecutorRoutingResolver`. Given an injected, normalized
`ExecutorRoutingTable`, `ExecutorProfileRegistry` and `RouteRequest`, it returns either one
selected semantic profile plus exact reviewer binding or one finite named rejection. The
Composition Root is the explicit caller that constructs the resolver from injected table/registry
fakes in tests; it holds no host client, credential, global singleton or effect port.

The resolver owns no configuration I/O. The registry boundary owns raw provider/model/effort and
capability evidence normalization before construction. The resolver imports no dispatch, receipt,
host-launch, credential, process or runner namespace. It writes no state and cannot invoke a
provider. Exact public contracts are the frozen revision-02 SPEC contracts:
`RoutingPurpose`, `ProfileAvailability`, `VerifiedCapabilityRank`, `ResolutionStatus`,
`ExecutorProfileRef`, `ExecutorProfile`, `RoutingKey`, `HardTicketAssessment`,
`ReviewBinding`, `OwnerOverrideRecord`, `RouteRequest`, `RouteResolution`,
`ExecutorRoutingTable` and `ExecutorProfileRegistry`.

## TDD, preflight and verification

| Cell | Required executable behavior / finite outcome |
| --- | --- |
| T1 | The same semantic routing table selects configured profiles for at least two fictitious providers without resolver source edits or real provider/model literals. |
| T2 | Project-initial/complex-change review and normal ticket opening/independent review select only their configured semantic references. |
| T3 | Normal implementation selects its configured profile and one reviewer binding of equal-or-higher verified rank. |
| T4 | Empty, malformed, duplicate or ambiguous routing/registry data fails closed; no default route exists. |
| T5 | Unavailable, stale or unknown selected profiles reject; no provider/profile switch occurs. |
| T6 | Missing, stale, cross-ticket, wrong-closure or self-asserted hard-ticket assessments reject; one valid exact assessment binds the configured Terra-implementation/Sol-review pair. |
| T7 | A lower-rank reviewer binding returns `REVIEWER_CAPABILITY_INSUFFICIENT`. |
| T8 | Missing/unknown/unavailable owner overrides reject; valid overrides remain auditable and cannot weaken review or bypass T6. |
| T9 | A bounded failed implementation/review cycle returns `MODEL_CAPABILITY_INSUFFICIENT` then `ARCHITECTURE_OWNER_REQUIRED`, never an inferred fallback. |
| T10 | Source-boundary checks reject any dispatch, receipt, host-launch, credential, process or runner import/callable exposure, and every public DTO rejects extra/unknown/null/bypass success forms. |
| M1 | Add a default route: T4 turns red; restore byte-for-byte and return green. |
| M2 | Accept a forged or cross-ticket hard-ticket assessment: T6 turns red; restore and return green. |
| M3 | Reverse the reviewer-rank comparison: T7 turns red; restore and return green. |
| M4 | Accept an unavailable override profile: T8 turns red; restore and return green. |
| M5 | Add a real provider/model literal to resolver source: T1/T10 turn red; restore and return green. |
| RM1 | Reviewer independently bypasses availability validation for an ordinarily selected profile (not the owner-override branch): T5 turns red; restore and return green. |

Strong-type preflight runs before source implementation and before review. It constructs every
success-path DTO through ordinary validators, then proves exact enum, nullability, primitive,
extra-field and malformed-reference rejection. `model_construct`, `model_copy`, casts, `Any`,
dynamic member lookup and historical-object reuse are negative-only inputs and cannot establish
success. New behavior has no legacy baseline-red claim; M1-M5 and RM1 are the required authentic
red evidence for test discrimination.

Run from the admitted worktree:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_executor_routing.py
py -3.11 -m mypy --strict library/local_orchestration/executor_routing.py tests/test_executor_routing.py
py -3.11 -m compileall -q library/local_orchestration/executor_routing.py
```

The reviewer re-runs the focused commands, full regression suite, strict DTO preflight, declared
boundary diff, M1-M5 and RM1. A zero-red mutation is a finding; restore each mutation byte for
byte before recording green evidence.

## POC manual admission, ownership and return

The reviewer may allocate the declared contained worktree and manually give the implementation
owner identifier-only references to this committed ticket, its baseline and the existing sealed
Context. This is not a host task binding and does not create a `PendingDispatchDescriptor`, issue
or consume a receipt, or claim automatic delivery/wake. The known host gap is recorded exactly as
above.

The implementation owner modifies only the declared boundary, does not commit, integrate, push,
control another Agent or create a worktree/task. After its return, the Terra/xhigh reviewer inspects
the worktree, runs review evidence and RM1, writes the candidate commit on the declared branch,
then invokes `admit_document_mutation` from `main`. The ticket must already be on `main`; the gate
and reviewer counter-mutation are the POC integration evidence.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with named test/type/mutation
evidence, `BLOCKED -> HALT` with the failed cell, or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
No return authorizes provider invocation/login, runner start, merge, push, release or deployment.

## Requirement-change block

Review reproduced a bypass path in which a malformed `ExecutorProfile` constructed outside
ordinary validation (`availability=AVAILABLE`, `availability_evidence=None`) inside a bypass-built
registry selected successfully from a valid ticket-opening route. Revision 02 also has no finite
status for malformed table/registry data and cannot represent stale or self-asserted assessment
facts without string conventions. Under `CHG-20260823-033`, this ticket is blocked: its uncommitted
source and tests are not implementation authority and must not be committed, integrated, pushed,
or reused as a replacement baseline. The replacement ticket may be opened only after the scoped
Context and SPEC revisions are approved.

```johnny-status
id = P8R-EXECUTOR-ROUTING-03
title = Provider-neutral executor routing
state = BLOCKED_REQUIREMENT_CHANGED_CHG_20260823_033
stage = D | typed route/profile resolver | BLOCKED
stage = E | capability/rank/rejection gates | BLOCKED
stage = M | five implementer and one reviewer reverse mutation | BLOCKED
```
