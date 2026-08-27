# 10｜Private ownership-ledger CAS substrate

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-CONTEXT-TELEMETRY-10-OWNERSHIP-LEDGER-CAS` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 07 / AC-06 through AC-08 and AC-16 |
| Requirement / Context / ADR | `PRD-20260827-041` / `CHG-20260827-041` / `doc/context/context-load-telemetry/main.md` Revision 07 / `ADR-20260827-022` through `ADR-20260827-025` |
| State / closure | `CLOSED / DONE / APPROVED / INTEGRATED`; `CLOSURE-CONTEXT-TELEMETRY-10-OWNERSHIP-LEDGER-CAS`, revision 01 |
| Document revision | `02` — completion evidence only; the frozen acceptance closure remains revision 01. |
| Approval authority | Project owner, 2026-08-27 (Asia/Taipei): authorized Revision 07's private pre-provisioned ownership-ledger and compare-and-swap substrate. |
| Source baseline / dependency | `8a41419d84001105d38814329e23f214adf43c36`; candidate must descend from the committed ticket authority. Ticket 09 (`096d471`) supplies the local exact lock port. Ticket 06 remains `SUPERSEDED` and non-integrable. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; one synchronous owner lane and no helper. |
| Worktree / branch / task | Reviewer allocates `.worktrees/context-load-telemetry-10-ownership-ledger-cas` on `implement/context-load-telemetry-10-ownership-ledger-cas` from committed `main` that descends from the source baseline, then binds its exact ticket revision and baseline. This same-lifetime lane needs no runner, queue, receipt, descriptor, gateway or host workspace readback. |
| Delivery / language | `POC / HIGH_ASSURANCE`; Python 3.11, complete annotations, strict finite DTOs, `mypy --strict`, adversarial mutation evidence and full review. Persistent ownership state raises the assurance. Luna/xhigh remains the implementation profile because the closure is fully specified and Terra/xhigh supplies the supervisor-grade review; this is not a hard-ticket model elevation. |
| XSS / effects | `XSS_NOT_APPLICABLE`. Only disposable test roots may contain a seeded private ledger. No telemetry stream, transaction journal, provider, credential, host CLI, target-project, Git, network, runner, queue, receipt, publication, release or deployment effect is authorized. |

## Boundary declaration

```johnny-boundary
modify = library/local_orchestration/telemetry_storage/ownership_ledger.py
create = library/local_orchestration/telemetry_storage/ownership_ledger.py
modify = tests/test_telemetry_ownership_ledger.py
create = tests/test_telemetry_ownership_ledger.py
modify = modules/element/python/context-load-telemetry/10-private-ownership-ledger-cas/
create = modules/element/python/context-load-telemetry/10-private-ownership-ledger-cas/
forbid = library/local_orchestration/telemetry_storage/__init__.py
forbid = library/local_orchestration/telemetry_storage/contracts.py
forbid = library/local_orchestration/telemetry_storage/local_lock_adapter.py
forbid = library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
forbid = library/local_orchestration/telemetry_storage/composition.py
forbid = library/workflow_router/
forbid = library/local_orchestration/file_lock.py
forbid = library/local_orchestration/path_containment.py
forbid = library/local_orchestration/johnny_root_layout.py
forbid = library/workflow_router/telemetry.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

`LocalTelemetryOwnershipLedger` is a private, direct-module implementation of a private
`TelemetryOwnershipLedgerPort`. It is never re-exported from `telemetry_storage/__init__.py` or
injected into a public composition root in this ticket. Given a strict existing
`TelemetryStorageRef` and expected project/revision, it resolves exactly one pre-provisioned
entry or returns one finite private decision:

```text
LedgerResolutionDecision = FOUND | NOT_FOUND | OWNERSHIP_MISMATCH | CLOSED
                         | CONFLICT | BOUNDARY_REJECTED
```

An entry binds the full opaque storage identity, current lifecycle, current revision and an
internally typed relative stream locator. It accepts neither a caller path nor a caller root.
Missing entry is `NOT_FOUND`; project, stream, ledger-ref or revision mismatch is
`OWNERSHIP_MISMATCH`; `DETACHED` or `REMOVED` is `CLOSED`; malformed, absolute, traversal or
otherwise invalid internal state is `BOUNDARY_REJECTED`. No such outcome creates, registers,
repairs or changes the ledger.

The only mutation is an internal compare-and-swap. Its expected revision must match a fresh
entry revision, then it atomically replaces only the supplied next lifecycle/revision pair. A
stale contender returns `CONFLICT` and leaves bytes and entry unchanged. There is no public
provision/create operation; tests seed a disposable already-owned ledger fixture directly, and
that setup is not importable production behavior.

`TicketDecompositionDecision = HIGH_ASSURANCE_REQUIRED`: Revision 07 already fixes identity,
pre-provisioning, finite failure meanings, source direction and the later transaction boundary,
but persistent ownership state requires adversarial verification. This ticket still owns one
private ledger/CAS seam, so Luna/xhigh implementation plus Terra/xhigh review is sufficient; it
does not choose transaction ordering, mutate a telemetry stream, recover a journal, map a public
`TelemetryStorageResponse`, or decide provider, host, target or release behavior.

## Frozen implementation rules

Create only `library/local_orchestration/telemetry_storage/ownership_ledger.py`. It exports the
private port, strict named ledger values, finite results and `LocalTelemetryOwnershipLedger` from
that exact module only. It may use standard-library JSON/file primitives behind strict validation;
it may not import `JsonlContextUsageStore`, `TelemetryStoragePort`, the lock adapter, legacy CLI,
provider, host, Router state, dynamic mapping, `Any`, cast, callback or global singleton.

The constructor receives an injected already-owned telemetry-root layout. Callers supply typed
opaque identity only. Before every read and CAS write, the root and internally derived ledger
location must pass `resolves_within_root`. A containment, filesystem, JSON or validation failure
is sanitized `BOUNDARY_REJECTED` and exposes no path, exception text, source text, prompt,
credential, URI or provider data.

The ledger format is schema-versioned and canonical enough for byte-for-byte no-effect tests. CAS
writes through a same-directory temporary file followed by owned replacement; it may not retry,
sleep, poll, self-lock, create a missing entry or reconstruct a caller identity. The later
transaction ticket, not this ticket, holds the lock across lookup, journal recovery, stream
mutation and lifecycle CAS.

Create `modules/element/python/context-load-telemetry/10-private-ownership-ledger-cas/README.md`
as a target-owned index to this ticket, exact private module, focused tests, selected module card
and ADR. It copies no production source and claims neither stream transaction nor production
provisioning.

### Reusable-module selection record

```text
selected: path-containment@cf9e126
why: reject a derived ledger location whose root or existing ancestor redirects outside the
     injected Johnny telemetry root before read or CAS write.
read: path-containment README -> public import -> worktree-containment behavior evidence.
dependency: standard library only.
rejected: exclusive-file-lock@60d2ab0 (the future transaction adapter owns lock lifetime);
          JsonlContextUsageStore; Ticket 06's superseded candidate; provider/host/runner paths.
gap: no ownership-ledger reusable card exists; this is target-owned private infrastructure.
boundary: no provisioning, stream, transaction, provider, host, target, publication, release or
          deployment behavior.
```

## High-assurance adversarial matrix

| Risk | Required ticket evidence | Excluded follow-on concern |
| --- | --- | --- |
| Caller forges or omits ownership | OLA1/OLA2 prove exact pre-provisioned binding and no auto-create path. | Provisioning workflow itself. |
| Stale writer overwrites newer lifecycle | OLA3/OLM1 prove CAS conflict has no byte effect. | Stream-and-ledger transaction ordering. |
| Derived location escapes Johnny root | OLA5/OLM3 prove containment rejection before effect. | Lock-held stream access. |
| Failed replacement reports success | OLA3/OLA5/OLM4 prove no false success or mixed ledger result. | Crash journal recovery across stream mutation. |

`ADR-20260827-025` owns the rejected alternatives and the eventual all-or-nothing transaction
requirement. The following transaction/recovery adapter ticket must re-use this ledger seam and
add its independent-process and restart evidence; it may not weaken these cells.

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| OLA1 | A disposable fixture seeds one complete pre-provisioned entry. Exact lookup returns `FOUND` with matching opaque identity, lifecycle, revision and internal relative locator; no result serializes a filesystem path. |
| OLA2 | Missing entry, cross-project/stream/ledger-ref identity and stale expected revision return `NOT_FOUND` or `OWNERSHIP_MISMATCH`; each leaves bytes unchanged and creates no entry. |
| OLA3 | Matching CAS advances exactly the requested lifecycle/revision once. Repeating from old revision returns `CONFLICT`; bytes remain at the first successful post-state. |
| OLA4 | `DETACHED` or `REMOVED` pre-provisioned entry returns `CLOSED`; lookup and rejected CAS leave bytes unchanged. |
| OLA5 | Malformed ledger record, absolute/traversal locator, redirected telemetry root or redirected ledger ancestor returns sanitized `BOUNDARY_REJECTED` before replacement or outside-root effect. |
| OLA6 | Source/AST gates prove no package re-export, public storage/composition/legacy-codec/lock/provider/host import, raw-path input/output, auto-provision, retry/sleep/polling, dynamic mapping/`Any`/cast, or mutation outside the CAS path. |
| OLA7 | Focused tests, strict type check and compilation pass. Fixture seeding is test-local, never an importable production provision API; candidate diff and clean worktree remain reviewer evidence, not persisted test assertions. |
| OLM1 | Remove expected-revision comparison from CAS; OLA3 turns red, then byte-exact restoration returns green. |
| OLM2 | Convert `NOT_FOUND` into entry creation; OLA2 and OLA6 turn red, then restoration returns green. |
| OLM3 | Permit absolute/traversal locator; OLA5 turns red, then restoration returns green. |
| OLM4 | Treat failed temporary replacement as success; OLA3/OLA5 turns red, then restoration returns green. |

Strong-type preflight constructs every private success/failure DTO through ordinary constructors
and validates finite decision, lifecycle, revision, nullability and locator forms. No cast,
`Any`, bypass constructor, dynamic lookup, mock or caller path is success evidence. The OLM cells
are required reverse evidence; this new behavior has no baseline-red claim.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_ownership_ledger.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_storage_contracts.py
py -3.11 -m mypy --strict library/local_orchestration/telemetry_storage/ownership_ledger.py tests/test_telemetry_ownership_ledger.py
py -3.11 -m compileall -q library/local_orchestration/telemetry_storage/ownership_ledger.py
git diff --check 8a41419d84001105d38814329e23f214adf43c36 HEAD
git status --short
```

The Terra/xhigh reviewer validates ticket blob, baseline, boundary, pre-provisioning and module
selection; reruns focused/type/compile gates; proves fixture seeding cannot be reached from
production source; and checks no Ticket 06 source was used. The reviewer reverse-mutates the
containment result from reject to accept with the same redirected fixture; OLA5 must turn red.
After byte-exact restoration, rerun focused evidence. Full-suite/residue checks and guarded
integration remain reviewer responsibilities; report known clean-baseline failures without
attributing them to this ticket.

## Ownership and return

This is a same-lifetime synchronous lane: Terra/xhigh dispatches, waits, receives, reviews,
writes the candidate commit and submits it to the integration gate. No runner, queue, receipt,
descriptor, gateway or host workspace readback is required. Luna/xhigh modifies only this
boundary, does not commit or push, and cannot change requirements, architecture, public contracts,
selected modules, model profile or control another agent.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with OLA/OLM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
No return authorizes stream or transaction-journal implementation, provider/host use, cost claim,
target mutation, integration, push, publication, release or deployment.

## Completion record

Luna/xhigh returned `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` without a commit or
push. Terra/xhigh reviewed the exact two-path candidate, requested and verified removal of its
ignored `.mypy_cache` residue, then committed candidate
`a06c0fd5d2dc78e8b77eb671d9a304b74a0202a6`. It descends from the committed ticket authority
`23f4ae1ff68df48a7e02368690cc86236b3abe1d`.

`admit_document_mutation` read this ticket's boundary from `main`, read the candidate diff from
Git, and returned `INTEGRATED` with the same exact `integrated_commit` SHA. Its only candidate
paths are `ownership_ledger.py` and `test_telemetry_ownership_ledger.py`; the element index was
already part of the committed ticket authority and was not modified by the candidate.

The review record is
`doc/reviews/context-load-telemetry/10-private-ownership-ledger-cas-code-review.md`. It contains
the OLA/OLM, strict-type, independent reviewer counter-mutation and full-suite baseline evidence.
The succeeding lock-bound stream transaction/recovery and composition closures remain separate
work; this ticket neither implements nor authorizes them.
