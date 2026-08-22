# R07A — Host capability readback contract

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TAD-ADAPTIVE-R07-HOST-CAPABILITY-01` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` Revision 07 / AC-03R7, AC-04R7 and acceptance item 20 |
| Requirement / Context / upstream | `PRD-20260822-031` / `CHG-20260822-031` / `CTX-HOST-GATEWAY-20260822-01` (sealed) / `TAD-ADAPTIVE-R06-ISOLATION-01` |
| State / closure | `APPROVED_NOT_DISPATCHED`; `CLOSURE-ADAPTIVE-R07A-HOST-CAPABILITY-01`, revision `01` |
| Approval authority | Project owner directive, 2026-08-22 (Asia/Taipei): after Revision 07 approval and remote baseline synchronization, open this first no-effect ticket and attempt receipt-bound dispatch. |
| Baseline / dependency | `dc60b7f25a61fb4c43c6a749e3a15d28fd1f4b8d`; no implementation ticket precedes it. |
| Control owner / reviewer | Current-session Codex reviewer; semantic `ticket-review` profile (current intent: Terra/xhigh), to be host-verified before any dispatch. |
| Implementation owner | Unassigned until receipt admission; semantic `implementation-standard` profile (current intent: Luna/xhigh). No hard-ticket elevation is authorized. |
| Worktree / branch / task / receipt / correlation | Unissued. The live approved-dispatch descriptor is the sole authority to allocate or bind them. |
| Delivery profile / resource plan | `HIGH_ASSURANCE`; one implementation lane, one independent reviewer, zero helpers. The high-assurance profile adds adversarial verification; it does not replace the standard Luna implementation profile. |
| Implementation language / checker | Python 3.11; frozen Pydantic contracts, explicit finite enums, complete annotations; `mypy --strict`. |
| XSS / effects | `N/A`; no Browser/WebView/HTML/DOM/JavaScript. This ticket has no filesystem, Git, process, credential, provider, task, receipt-consumption, runner, network or host-control effect. |
| Environment / rollback | Local pure-Python tests only. Revert the one ticket implementation commit if independent review rejects it; no external compensation is possible or needed. |

## Boundary declaration

```johnny-boundary
create = library/workflow_router/host_gateway_contracts.py
create = library/local_orchestration/codex_host_capability_readback.py
modify = library/workflow_router/__init__.py
modify = library/local_orchestration/__init__.py
create = tests/test_codex_host_capability_readback.py
forbid = library/workflow_router/thread_host_contracts.py
forbid = library/local_orchestration/codex_thread_host_binding.py
forbid = library/local_orchestration/codex_thread_dispatch.py
forbid = library/local_orchestration/live_dispatch_metadata_boundary.py
forbid = modules/tickets/
forbid = doc/
forbid = skills/
```

## Observable closure

One pure, provider-neutral host-capability readback boundary accepts one strict request and either
one typed observation or an explicit unavailable-port condition. It returns exactly one
metadata-only `HostCapabilityReadbackResult`: a validated, exact observation returns `VERIFIED`;
the current host's absence of effective profile/effort/rank readback returns
`CAPABILITY_UNAVAILABLE` with no observation; malformed, absent-project, not-ready, unverified
and mismatched evidence return their own finite failures. It neither reserves a task nor exposes
workspace verification, receipt-bound admission, delivery, or any host-control capability.

`TicketDecompositionDecision = READY_LOW_MODEL`: the public contract is frozen by approved
Revision 07, the closure has one no-effect result boundary, and every rejection is deterministically
verifiable. `HIGH_ASSURANCE` remains satisfied by the approved threat/failure matrix and the
reverse-mutation/reviewer requirements below. No source fact, profile mapping, host payload shape
or public contract may be invented during implementation; a discovered gap returns
`ImplementationReturn.CHANGE_DETECTED`.

## Frozen contracts and dependency direction

Create only the following public contract family in
`library/workflow_router/host_gateway_contracts.py`, re-exported intentionally through the
existing package root:

1. Finite `HostCapabilityReadbackStatus` and matching failure type, with exactly
   `VERIFIED`, `CAPABILITY_UNAVAILABLE`, `PAYLOAD_INVALID`, `PROJECT_REQUIRED`,
   `TASK_NOT_READY`, `PROFILE_UNVERIFIED`, and `PROFILE_MISMATCH` as declared by Revision 07.
2. Frozen, strict, extra-forbidden `HostCapabilityReadbackRequest`,
   `HostCapabilityObservation`, and `HostCapabilityReadbackResult` models. The request uses only
   the Revision 07 reservation/host/project/task/profile/effort references and a named,
   non-negative verified-capability rank requirement. The observation uses only the declared
   host/project/task/profile/effort/rank/evidence/digest values. Raw paths, prompts, source,
   payload bodies, URIs, credentials and dynamic input are not fields.
3. Result validation enforces the exclusive nullable shape: `VERIFIED` has one observation and
   no failure; every other status has its exactly matching failure and no observation. A verified
   observation must match the request's host, project, task, semantic profile and effort, and
   have rank no lower than the request; a mismatch never leaks an observation.
4. `CodexHostCapabilityReadback` is a pure local adapter over these contracts. It receives only
   an already-normalized typed observation or an explicit unavailable condition. It must not
   parse an invented Codex payload, infer evidence from a model request, configuration, CLI login,
   prompt, shell directory, task self-report, existing thread-binding digest or runner state.
   Its unavailable branch is the current-host behavior and returns only
   `CAPABILITY_UNAVAILABLE`.

The workflow-router contract module depends on no local-orchestration module. The local adapter
may depend on the public contract module only. Existing Codex directory/thread binding and
one-shot dispatch code are immutable inputs to later serial tickets; importing, broadening or
calling them here is forbidden. There is no effect port in this closure.

The Composition Root is deliberately empty at this stage: the caller explicitly constructs the
pure adapter with no configuration, provider client, credential or global singleton. A later,
separately approved ticket may compose a verified host port only after its own receipt-bound
admission; it cannot repurpose this closure's unavailable result as an effect capability.

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| `HG1` | Ordinary public validation constructs every success-path request, observation and `VERIFIED` result; serialised results contain only declared metadata fields and no raw workspace/prompt/source/credential text. |
| `HG2` | The explicit unavailable current-host adapter returns exactly `CAPABILITY_UNAVAILABLE`, its matching failure and `observation is None`; it performs no tool, process, network, task, receipt or filesystem operation. |
| `HG3` | Exact host/project/task/profile/effort evidence with rank equal to or above the requirement returns only `VERIFIED`; lower rank, different host/project/task/profile/effort, missing capability evidence or an unverified rank returns the named finite failure and no observation. |
| `HG4` | Unknown status/failure, extra fields, invalid reference/rank primitive type, `None` in required fields, success-with-failure, failure-with-observation and non-matching status/failure are rejected by ordinary validators. |
| `HG5` | `PAYLOAD_INVALID`, `PROJECT_REQUIRED` and `TASK_NOT_READY` are constructible only as their matching finite failed results; none exposes an observation or a capability port. |
| `HG6` | A bounded AST/source gate proves both owned modules have complete annotations and no `Any`, `object`, casts, dynamic lookup, bypass constructor, broad catch, filesystem/Git/process/network/thread-control import or callable host-control entry. |
| `HG7` | Focused tests, strict type checking, import/compile validation, exact declared-boundary diff and no cache/runtime residue are green. This is new behavior: record named green evidence and do not claim a ceremonial baseline-first-red run. |
| `HM1` | Remove the result's success/failure exclusivity check; `HG4` turns red, then restoration returns green byte-for-byte. |
| `HM2` | Make the unavailable adapter return `VERIFIED`; `HG2` turns red, then restoration returns green byte-for-byte. |
| `HM3` | Remove one request/observation identity or rank comparison; the corresponding `HG3` cell turns red, then restoration returns green byte-for-byte. |
| `HM4` | Add one forbidden host/process/thread-control import or capability exposure to an owned source module; `HG6` turns red, then restoration returns green byte-for-byte. |

Strong-type preflight runs before implementation and again before review. It constructs the public
success path through ordinary validators, then proves malformed references, unknown enums,
nullability violations, extra fields and bypass construction cannot serve as success evidence.
`model_construct`, `model_copy`, casts, `Any`, dynamic member lookup and historical-object reuse
are negative-only evidence. Missing preflight is `HALT / TICKET_SCHEMA_INVALID`.

## Verification and review

The implementation owner runs only the following focused commands from its admitted worktree:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_codex_host_capability_readback.py
py -3.11 -m mypy --strict library/workflow_router/host_gateway_contracts.py library/local_orchestration/codex_host_capability_readback.py library/workflow_router/__init__.py library/local_orchestration/__init__.py tests/test_codex_host_capability_readback.py
py -3.11 -m compileall -q library/workflow_router/host_gateway_contracts.py library/local_orchestration/codex_host_capability_readback.py
```

The Terra/xhigh reviewer re-runs all focused checks, validates the committed ticket blob and
strong-type preflight, confirms the declared boundary and no-effect import gate, replays all four
restored reverse mutations, and performs one independent counter-mutation through a different
test path. A zero-red counter-mutation is a finding. The reviewer must specifically prove that
the unavailable branch cannot be converted into a model assertion, static configuration or a
prompt-derived success result.

## Ownership, receipt and return

The implementation owner receives only the identifier-only dispatch envelope after a live
descriptor, matching unconsumed receipt, verified Luna/xhigh task profile and a three-way
workspace proof exist. It may modify only this ticket's boundary, makes one implementation commit,
and cannot control another Agent, integrate, push, reserve a task, consume a receipt or invoke a
provider. The reviewer may not bypass receipt/workspace/profile admission by using the existing
generic subagent interface.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with named evidence,
`BLOCKED -> HALT` with the failed TDD cell, or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
No return authorizes task creation, host delivery, runner wake, merge, push, release or deployment.

```johnny-status
id = TAD-ADAPTIVE-R07-HOST-CAPABILITY-01
title = Host capability readback contract
state = APPROVED_NOT_DISPATCHED
stage = D | strict DTO/result exclusivity | OPEN
stage = E | unavailable and evidence comparison | OPEN
stage = M | four reverse mutations | OPEN
```
