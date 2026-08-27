# 13｜Private telemetry-storage composition binding

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-CONTEXT-TELEMETRY-13-PRIVATE-STORAGE-COMPOSITION-BINDING` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-CONTEXT-LOAD-TELEMETRY-20260803-01KZ5E7F9G1H3J5K7M9N1P3Q5R` Revision 10 / AC-21 |
| Requirement / Context / ADR | `PRD-20260827-041` / `CHG-20260827-041` / `doc/context/context-load-telemetry/main.md` Revision 10 / `ADR-20260827-025`–`028` |
| State / closure | `CLOSED / DONE / APPROVED / INTEGRATED`; `CLOSURE-CONTEXT-TELEMETRY-13-PRIVATE-STORAGE-COMPOSITION-BINDING`, revision 02 |
| Document revision | `02` |
| Approval authority | Project owner, 2026-08-27 (Asia/Taipei): explicitly authorized Revision 10's one source-only private composition binding after Ticket 12 integration. |
| Source baseline / dependency | `3b11f71ae10e338841aede1adddbbd93d6aec704`; candidate must descend from this committed ticket authority. Ticket 09 (`096d471`) supplies the local lock port, Ticket 11 (`e05f03a`) the per-stream ledger, and Ticket 12 (`c359d92`) the private transaction adapter. Ticket 06 remains superseded and non-integrable. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; `READY_LOW_MODEL`, one synchronous owner lane and no helpers. |
| Worktree / branch / task | Reviewer allocates `.worktrees/context-load-telemetry-13-private-storage-composition-binding` on `implement/context-load-telemetry-13-private-storage-composition-binding` from current committed `main`, then binds the exact ticket revision and baseline. This same-lifetime lane requires no runner, queue, receipt, descriptor, gateway or host workspace readback. |
| Delivery / language | `POC / STANDARD`; Python 3.11, complete annotations, strict finite public port, `mypy --strict`, direct no-effect proof and independent review. |
| XSS / effects | `XSS_NOT_APPLICABLE`. Construction of the composition graph is the only authorized behavior; it creates no filesystem state and invokes no storage operation. No provider, credential, host CLI, target-project, Git, network, runner, queue, receipt, publication, release or deployment effect is authorized. |

## Boundary declaration

```johnny-boundary
create = library/local_orchestration/telemetry_storage/composition.py
modify = library/local_orchestration/telemetry_storage/composition.py
create = tests/test_telemetry_storage_composition.py
modify = tests/test_telemetry_storage_composition.py
create = modules/element/python/context-load-telemetry/13-private-storage-composition-binding/
modify = modules/element/python/context-load-telemetry/13-private-storage-composition-binding/
forbid = library/local_orchestration/telemetry_storage/__init__.py
forbid = library/local_orchestration/telemetry_storage/contracts.py
forbid = library/local_orchestration/telemetry_storage/johnny_owned_adapter.py
forbid = library/local_orchestration/telemetry_storage/ownership_ledger.py
forbid = library/local_orchestration/telemetry_storage/local_lock_adapter.py
forbid = library/local_orchestration/file_lock.py
forbid = library/local_orchestration/path_containment.py
forbid = library/local_orchestration/johnny_root_layout.py
forbid = library/workflow_router/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Create only
`compose_johnny_owned_telemetry_storage(layout: JohnnyRootLayout) -> TelemetryStoragePort` in
`library/local_orchestration/telemetry_storage/composition.py`. Each ordinary call receives the
already-valid injected `JohnnyRootLayout`, constructs exactly one fresh
`LocalTelemetryOwnershipLedger(layout)`, exactly one fresh
`LocalTelemetryStorageLockAdapter(layout)`, then exactly one fresh
`JohnnyOwnedTelemetryStorageAdapter(layout, ledger, lock)`, and returns it as the existing
`TelemetryStoragePort`.

`TicketDecompositionDecision = READY_LOW_MODEL`: Revision 10 / ADR-028 fix the source location,
factory signature, dependency order, lifetime, no-effect behavior, public-surface rule, test
fake seam and all excluded behavior. This is one composition-root boundary, not a second storage
adapter, a new public contract, a provisioning workflow or a storage-operation implementation.

## Frozen composition rules

The composition module exports only `compose_johnny_owned_telemetry_storage` from its exact
module path. `telemetry_storage/__init__.py` remains byte-identical to the authority baseline;
there is no package-root re-export of the factory, transaction adapter, ledger or lock adapter.

The factory imports only:

```text
library.local_orchestration.johnny_root_layout: JohnnyRootLayout
library.local_orchestration.telemetry_storage.contracts: TelemetryStoragePort
library.local_orchestration.telemetry_storage.johnny_owned_adapter: JohnnyOwnedTelemetryStorageAdapter
library.local_orchestration.telemetry_storage.local_lock_adapter: LocalTelemetryStorageLockAdapter
library.local_orchestration.telemetry_storage.ownership_ledger: LocalTelemetryOwnershipLedger
```

It has no module-level mutable state, cache, singleton, environment read, raw path/string input,
resolver callback, dynamic mapping, storage reference, caller-selected dependency or `execute`
call. It may not call the JSONL codec, create a directory/file, provision/register/repair an
identity, construct a request/response, touch a target, or add retry/sleep/polling/queue/runner
behavior. A factory call creates a fresh graph; two calls may share the caller-supplied layout
object but may not share any adapter/ledger/lock instance.

The returned port is the production injection point. A caller that needs a test double holds a
`TelemetryStoragePort` directly; it does not invoke or patch production composition. The adapter,
ledger and lock remain private implementation details and their behavior is frozen by Tickets
09/11/12.

Create `modules/element/python/context-load-telemetry/13-private-storage-composition-binding/README.md`
as a target-owned index to this ticket, exact factory/test source, frozen port contract,
Tickets 09/11/12 and ADR-028. It copies no source and must say that composition is not
provisioning or an operation invocation.

### Reusable-module selection record

```text
selected: no new direct reusable module.
dependency evidence: the delivered local lock adapter retains Ticket 09's selected
                     exclusive-file-lock@60d2ab0 and path-containment@cf9e126 behind its
                     existing private contract.
read: capability cards -> exact public sources -> behavior evidence; Ticket 09/11/12 contracts.
rejected: direct ExclusiveFileLock/path-containment use; JsonlContextUsageStore; new adapter,
          global cache, provisioner, provider/host and runner mechanisms.
boundary: composition binds delivered target-owned private adapters only; it does not inherit a
          new filesystem, telemetry, provider, target, publication or release authority.
```

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| CPA1 | An ordinary `JohnnyRootLayout` passed to the factory returns one `TelemetryStoragePort` whose concrete value is `JohnnyOwnedTelemetryStorageAdapter`; its private layout, ledger and lock are respectively the exact supplied layout, `LocalTelemetryOwnershipLedger` and `LocalTelemetryStorageLockAdapter`, all bound to that same layout. |
| CPA2 | Two ordinary calls with one layout return distinct adapter, ledger and lock objects. Before and after construction, the disposable layout base and telemetry root do not exist; construction invokes no `execute`, creates no ledger/lock/stream/journal/report state and returns no path-bearing public value. |
| CPA3 | A typed fake `TelemetryStoragePort` can be supplied directly to a test caller seam without importing or invoking the production factory. The factory itself accepts no caller-selected dependency, storage ref, request, root string or dynamic mapping. |
| CPA4 | AST/source gates prove the exact five frozen imports, one factory, one public `__all__` name, dependency construction order and no package-root re-export. They reject JSONL/codec, `Path`, `os`, environment, filesystem, request/response construction, `execute`, cache/singleton, provider/host/runner/queue, retry/sleep/poll, `Any`, `cast`, raw mapping and dynamic lookup forms. |
| CPA5 | Focused tests, strict type check, compilation and diff check pass. Element index names the exact factory/test/ADR/dependencies and its no-provision/no-operation limitation. Fixture roots and fakes are test-local only. |
| CPM1 | Reverse-mutate one factory dependency to use a new/different layout; CPA1 turns red, then exact restoration returns green. |
| CPM2 | Reverse-mutate the factory to cache or reuse a constructed dependency; CPA2 turns red, then exact restoration returns green. |
| CPM3 | Reverse-mutate the factory to import/call a legacy codec or perform a filesystem/operation action; CPA2/CPA4 turns red, then exact restoration returns green. |

Strong-type preflight constructs the injected `JohnnyRootLayout`, the returned port and a test
fake port through ordinary typed constructors/classes. No cast, `Any`, dynamic lookup, raw
mapping, bypass constructor or test mock is success evidence. This is new source behavior, so
no ceremonial baseline-red claim is admissible; CPA1–CPA5 and restored CPM1–CPM3 are the required
discriminating evidence.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_storage_composition.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_storage_contracts.py tests/test_johnny_owned_telemetry_storage_adapter.py
py -3.11 -m mypy --strict library/local_orchestration/telemetry_storage/composition.py tests/test_telemetry_storage_composition.py
py -3.11 -m compileall -q library/local_orchestration/telemetry_storage/composition.py
git diff --check 3b11f71ae10e338841aede1adddbbd93d6aec704 HEAD
git status --short
```

The Terra/xhigh reviewer validates the exact ticket blob/baseline/boundary, the no-new-module
selection record, direct source direction and absence of composition effects; reruns every
focused/type/compile gate; independently reverse-mutates a real production lifetime or
no-effect branch the implementer did not choose; and compares any full-suite failure against
clean main with untruncated traceback. The reviewer also proves that no package export, public
contract, storage-operation, provider/host, target or Git sentinel changed.

## Ownership and return

This closure is same-lifetime synchronous: the Terra/xhigh reviewer dispatches, waits, receives
the return, reviews, commits the candidate, and submits it to the integration gate. It requires
no runner, queue, receipt, descriptor, gateway or host workspace readback. The Luna/xhigh
implementation owner modifies only this declared boundary, does not commit or push, and cannot
change requirements, architecture, contracts, selected modules, model profile or control another
agent.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with CPA/CPM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or `CHANGE_DETECTED -> REQUIREMENT_CHANGED`.
No return authorizes a storage operation, provision, provider/host use, cost claim, target
mutation, integration, push, publication, release or deployment.

## Completion record

Luna/xhigh returned `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with no commit, push,
document-gate call, ticket/document edit or scope expansion. Terra/xhigh independently reviewed
the two declared candidate paths, direct import graph, lifetime/no-effect proof and reusable
selection record; reran focused, regression, strict-type and compilation gates; and verified the
declared CPM1–CPM3 mutation evidence.

The independent reviewer counter-mutation reversed the real adapter constructor argument order.
CPA1 then failed at the production `TelemetryOwnershipLedgerPort` runtime type guard rather than
constructing a false graph; restoring the exact `(layout, ledger, lock)` order returned the
focused suite to green. This is distinct from the implementer's layout/lifetime/no-effect
mutations.

The reviewer committed candidate `108ea43e8b8a8f8bccbe3e6ced1eac59f26dda35` on
`implement/context-load-telemetry-13-private-storage-composition-binding`. It descends from
committed Ticket 13 authority `bb3217a417bbce5e129139a98dbb63b2366a29f9` and changes only
`composition.py` and its direct test. `admit_document_mutation` read this ticket boundary from
`main`, read the candidate change set from Git, and returned `INTEGRATED` with that same exact
candidate SHA. The source integration was non-force pushed to `origin/main`; fresh direct remote
readback returned `108ea43e8b8a8f8bccbe3e6ced1eac59f26dda35`.

The exact source review is
`doc/reviews/context-load-telemetry/13-private-storage-composition-binding-code-review.md`. Its
full-suite result records only the three failures reproduced against clean main; no global-green
claim is made. Composition is now bound, but no caller integration, provisioning or storage
operation was performed by this closure.
