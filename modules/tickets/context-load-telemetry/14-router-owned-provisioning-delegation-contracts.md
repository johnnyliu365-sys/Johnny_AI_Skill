# 14｜Router-owned telemetry-provisioning delegation contracts

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-CONTEXT-TELEMETRY-14-ROUTER-PROVISIONING-DELEGATION-CONTRACTS` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 11 / AC-22 |
| Requirement / Context / ADR | `PRD-20260827-041` / `CHG-20260827-041` / `doc/context/context-load-telemetry/main.md` Revision 11 / `ADR-20260827-029` |
| State / closure | `CLOSED / DONE / APPROVED / INTEGRATED / AUTHORITY_PUSH_CONFIRMED`; `CLOSURE-CONTEXT-TELEMETRY-14-ROUTER-PROVISIONING-DELEGATION-CONTRACTS`, revision 02 |
| Document revision | `02` |
| Approval authority | Project owner, 2026-08-27 (Asia/Taipei): approved Revision 11 and exactly one source-only Router grant/denial contract closure. |
| Source baseline / dependency | `b2ed02ecaf87d19557d76da27402493c2d482094`; candidate must descend from this committed ticket authority. Ticket 13 (`108ea43`) supplies the separate composition consumer; this ticket may depend only on the existing private `ApprovedDispatchArtifactRegistry` contract. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; `READY_LOW_MODEL`, one synchronous owner lane and no helpers. |
| Worktree / branch / task | Reviewer allocates `.worktrees/context-load-telemetry-14-router-owned-provisioning-delegation-contracts` on `implement/context-load-telemetry-14-router-owned-provisioning-delegation-contracts` from current committed `main`, then binds the exact ticket revision and baseline. This same-lifetime lane requires no runner, queue, receipt, descriptor, gateway or host workspace readback. |
| Delivery / language | `POC / STANDARD`; Python 3.11, complete annotations, strict finite internal contract, `mypy --strict`, pure deterministic proof and independent review. |
| XSS / effects | `XSS_NOT_APPLICABLE`. The closure is an in-process metadata-only decision. It creates no Johnny root, ledger, lock, stream, journal, report, storage reference, filesystem state, provider/host call, target-project effect, Git, network, runner, queue, receipt, publication, release or deployment effect. |

## Boundary declaration

```johnny-boundary
create = library/workflow_router/telemetry_provisioning_contracts.py
modify = library/workflow_router/telemetry_provisioning_contracts.py
create = tests/test_telemetry_provisioning_contracts.py
modify = tests/test_telemetry_provisioning_contracts.py
create = modules/element/python/context-load-telemetry/14-router-owned-provisioning-delegation-contracts/
modify = modules/element/python/context-load-telemetry/14-router-owned-provisioning-delegation-contracts/
forbid = library/workflow_router/__init__.py
forbid = library/workflow_router/contracts.py
forbid = library/workflow_router/router.py
forbid = library/workflow_router/private_router.py
forbid = library/workflow_router/policy_response.py
forbid = library/local_orchestration/
forbid = tests/test_workflow_router.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Create the private module
`library/workflow_router/telemetry_provisioning_contracts.py` with exactly one pure decision
entry point:

```python
authorize_router_telemetry_provisioning(
    registry: ApprovedDispatchArtifactRegistry,
    request: RouterTelemetryProvisioningRequest,
) -> RouterTelemetryProvisioningResult
```

`RouterTelemetryProvisioningRequest` carries only a `request_ref` plus the exact existing
approved-dispatch identity tuple: opaque `project_id`, `ticket_reference`, `handoff_reference`,
`implementation_owner_id`, `ticket_docs_commit` and `handoff_docs_commit`. It has no path, root,
layout, storage identity, stream, locator, lifecycle, operation, record, dynamic mapping or
optional authority fallback.

The function must use the existing private
`resolve_approved_dispatch_artifact` check. It returns exactly one finite result:

```text
AUTHORIZED(
  request_ref,
  project_id, ticket_reference, handoff_reference, implementation_owner_id,
  provisioning_authority_ref
)
| AUTHORITY_MISMATCH(request_ref, denial_ref)
```

An authorized result is produced only when the registry resolves the exact tuple **and** both
committed document references match. Its `provisioning_authority_ref` is a deterministic,
domain-separated SHA-256 opaque ID over that validated tuple; a denied result has no project,
ticket, handoff, owner, document commit, grant, storage reference or location field. A denial
uses a deterministic opaque `denial_ref` and cannot be treated as a retry grant. The module
never derives a `TelemetryStorageRef` or stream locator: a later, separately authorized durable
provisioning adapter will consume this authorization boundary and own its concrete entry write.

`TicketDecompositionDecision = READY_LOW_MODEL`: the owner-approved Revision 11 / ADR-029 fix
the responsibility boundary, existing trusted registry seam, finite outcome, source locations,
effect exclusion, fake seam and acceptance. This ticket has one pure authorization-gate closure;
it is not a root bootstrap, ledger writer, storage caller, composition change, Router-engine route
change or public capability.

## Frozen contract rules

The new module may import only `hashlib`, `enum`, Pydantic validation primitives, strongly typed
contracts from `library.workflow_router.contracts`, and
`ApprovedDispatchArtifactRegistry` / `resolve_approved_dispatch_artifact` from
`library.workflow_router.policy_response`. It must use ordinary strict `RouterModel`
constructors and complete annotations. It has no `Any`, `cast`, `object`-typed request or result,
dynamic lookup, raw mapping, path/string locator convention, callback, singleton, cache,
environment read, file/process/network import or exception-detail serialization.

The module remains private to its exact path: `library.workflow_router.__init__` remains
byte-identical, so no product caller receives a public provision API. The result is an ephemeral
Router authorization decision, not durable Router state and not evidence that Host Bootstrap has
created a root or that a ledger entry exists. Ticket 13's composition factory remains unchanged
and never imports this module.

Create
`modules/element/python/context-load-telemetry/14-router-owned-provisioning-delegation-contracts/README.md`
as a target-owned index to this ticket, the exact source/test files, the frozen registry contract
and ADR-029. It copies no source and explicitly records that authorization is neither root
bootstrap nor durable provisioning.

### Reusable-module selection record

```text
selected: no new direct reusable module.
dependency evidence: existing target-owned ApprovedDispatchArtifactRegistry and
                     resolve_approved_dispatch_artifact metadata contract.
read: current registry interface -> its exact resolution helper -> existing deterministic tests.
rejected: direct storage ledger/lock/composition import; TelemetryStorageRef construction;
          host bootstrap; a public provision API; runner/queue/receipt mechanisms.
boundary: this closure issues only a private metadata authorization/denial result and introduces
          no durable or external effect authority.
```

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| TPA1 | A `StaticApprovedDispatchArtifactRegistry` record and a request matching all six coordinates return `AUTHORIZED`. The result repeats only the validated opaque project/ticket/handoff/owner identifiers and one deterministic `provisioning_authority_ref`; repeating the same call returns byte-identical serialized output. |
| TPA2 | Independently changing project, ticket, handoff, implementation owner, ticket-document commit or handoff-document commit returns exactly `AUTHORITY_MISMATCH` with only `request_ref` and deterministic `denial_ref`. It carries no grant or identity field and makes no registry mutation. |
| TPA3 | Strict construction/round-trip rejects malformed finite IDs, wrong commit shapes, extra fields, `None`, raw filesystem-like values, storage/root/locator fields and dynamic mappings. Authorized and denied result shapes reject contradictory fields through ordinary Pydantic validation. |
| TPA4 | AST/source gates prove one typed entry point, use of `resolve_approved_dispatch_artifact`, domain-separated deterministic SHA-256 refs and absence of storage, root/layout, path, filesystem, host/provider, process/network, Router-engine, public-export, `Any`, `cast`, raw mapping, environment, retry/sleep/poll/queue/runner and exception-detail paths. |
| TPA5 | Focused tests, existing Router regression, strict type check, compilation and diff check pass. The element index names the exact private source/test/ADR and the no-bootstrap/no-provision/no-public-export boundary. |
| TPM1 | Reverse-mutate the entry point to bypass `resolve_approved_dispatch_artifact`; one of TPA2's altered-coordinate cases turns red, then exact restoration returns green. |
| TPM2 | Reverse-mutate authority-ref derivation to omit one committed document reference; TPA1's exact deterministic ref assertion turns red, then exact restoration returns green. |
| TPM3 | Reverse-mutate the module to add a forbidden storage/root/path or public-export form; TPA4 turns red, then exact restoration returns green. |

Strong-type preflight constructs every request, both finite result variants and the static
registry record through ordinary typed constructors and JSON round trips. It reverse-mutates one
forbidden result shape and one metadata identifier as negative validation evidence. No cast,
`Any`, bypass constructor, mock, dynamic dictionary or historical object reuse is success
evidence. This is new behavior, so no ceremonial baseline-red claim is admissible; TPA1–TPA5 and
restored TPM1–TPM3 are the required discriminating evidence.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_provisioning_contracts.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_workflow_router.py
py -3.11 -m mypy --strict library/workflow_router/telemetry_provisioning_contracts.py tests/test_telemetry_provisioning_contracts.py
py -3.11 -m compileall -q library/workflow_router/telemetry_provisioning_contracts.py
git diff --check b2ed02ecaf87d19557d76da27402493c2d482094 HEAD
git status --short
```

The Terra/xhigh reviewer validates the exact ticket blob/baseline/boundary, closed result shapes,
registry helper use, no-new-module selection record and absence of all root/storage/external
effects; reruns focused, Router-regression, strict-type and compilation gates; independently
reverse-mutates a registry-commit binding or denial shape the implementer did not choose; and
compares any full-suite failure against clean main with an untruncated traceback. The reviewer
also proves that no package export, Router route, storage contract, composition factory,
provider/host, target or Git sentinel changed.

## Ownership and return

This closure is same-lifetime synchronous: the Terra/xhigh reviewer dispatches, waits, receives
the return, reviews, commits the candidate, and submits it to the integration gate. It requires
no runner, queue, receipt, descriptor, gateway or host workspace readback. The Luna/xhigh
implementation owner modifies only this declared boundary, does not commit or push, and cannot
change requirements, architecture, contracts, selected modules, model profile or control another
agent.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with TPA/TPM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
No return authorizes root bootstrap, durable provisioning, a ledger/lock/stream/journal/report
effect, provider/host use, cost claim, target mutation, integration, push, publication, release
or deployment.

## Completion record

Luna/xhigh returned `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with no commit, push,
document edit, gate call or scope expansion. Its candidate changed only the two declared
source/test paths. TPA focused evidence was `5 passed, 11 subtests`; the Router regression was
`57 passed, 216 subtests`; `mypy --strict`, `compileall`, diff check and restored TPM1–TPM3 all
passed.

Terra/xhigh initially requested one additive correction: the grant digest incorrectly included
the caller correlation `request_ref`, although the frozen grant is over the six validated
dispatch coordinates only. The same owner lane corrected it and added the distinct-request-ref
acceptance case. The reviewer independently reverse-mutated the real dispatch-material function
to include `request_ref`; TPA1 failed with a mismatched authority reference, and exact
restoration returned the focused suite to green. This counter-mutation is distinct from the
implementer's registry-bypass, omitted-commit and forbidden-source mutations.

The candidate `9364fc89428df1a448d2ac60e4867bfe0d63e55e` on
`implement/context-load-telemetry-14-router-owned-provisioning-delegation-contracts` descends
from the committed ticket authority `ba01836183513b4f8c4b3a2e0bf88707bee4f5c6` and changes only
`library/workflow_router/telemetry_provisioning_contracts.py` and
`tests/test_telemetry_provisioning_contracts.py`. `admit_document_mutation` read this exact
ticket boundary from `main`, read the candidate change set from Git, and returned `INTEGRATED`
with that same candidate SHA. The source integration was non-force pushed to `origin/main`; fresh
direct remote readback returned `9364fc89428df1a448d2ac60e4867bfe0d63e55e`.

The final candidate full-suite result was `1841 passed, 31 skipped, 3805 subtests passed` with
three failures. Each was independently reproduced, untruncated, against clean `main` in the
same runtime: stale plugin-publication pin, refusal-guidance enum roster drift, and running
pytest `9.0.3` versus declared `9.1.1`. They are existing baseline failures outside this
boundary; no global-green claim is made. The exact review is
`doc/reviews/context-load-telemetry/14-router-owned-provisioning-delegation-contracts-code-review.md`.
