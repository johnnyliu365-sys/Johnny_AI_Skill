# ADR-20260827-029 — Host-bootstrap root, Router-owned provisioning, and composition consumption

- Date: `2026-08-27 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `PRD-20260827-041` / `CHG-20260827-041`
- Refines: `ADR-20260827-025` through `ADR-20260827-028`; it authorizes no durable ledger write,
  host effect, provider effect, target-project mutation, publication, release or deployment.

## Context

The delivered private storage adapter correctly requires a pre-existing owned ledger entry, and
the delivered composition factory correctly performs no effect. Treating a missing entry as a
factory defect would make the factory auto-register caller input; treating it as a bootstrap
defect would make installation select a project identity. Either shortcut collapses root
readiness, runtime authority and storage consumption into a caller-forgeable path.

## Decision

1. **Host Bootstrap owns root readiness only.** It may establish or verify the per-user
   `JohnnyRootLayout` during an authorized host lifecycle. It does not create a telemetry
   ownership-ledger entry or select a telemetry project, stream, storage reference, ledger
   reference, stream locator or initial revision.
2. **The Router owns runtime delegation.** A future private Router capability may request
   provisioning only after a validated project/ticket authority binds one opaque telemetry
   identity. The Router derives the initial revision and internal relative locator; no application
   caller receives a provision capability, raw path input or authority to select a ledger
   location.
3. **Provisioning is an explicit owned-state effect.** Its future adapter obtains the exact
   identity lock before creating an entry, writes only under the Johnny root, and has finite
   duplicate/authority/boundary outcomes. It is not a branch of `TelemetryStoragePort.execute`,
   `resolve`, recovery lookup, transaction recovery or host bootstrap.
4. **Composition only consumes.**
   `compose_johnny_owned_telemetry_storage(layout)` continues to construct the delivered private
   ledger, lock and transaction adapter over one injected layout. It never calls bootstrap,
   Router delegation, provision, registration, discovery or repair. An absent entry remains
   `STORAGE_OWNERSHIP_MISMATCH` before stream or journal effect.
5. Public storage DTOs and package exports remain unchanged. Product callers depend on
   `TelemetryStoragePort`; test callers may replace it with a fake without composing or
   provisioning the production graph.

## Consequences

- The next source-only slice can define the private Router provision command/result boundary and
  test fakes without opening the root or writing a ledger entry.
- A later durable-provisioning slice needs its own exact effect authority and must prove its
  identity lock, atomic duplicate handling, containment and absence of application-caller
  authority.
- A host-bootstrap change remains separately scoped: it may make the root ready but cannot make
  telemetry storage ready for an arbitrary project.

## Alternatives rejected

- **Factory auto-provisions a missing entry.** Rejected: construction would acquire an owned-state
  effect and turn a consumer into a caller-controlled authority source.
- **Host Bootstrap seeds a default telemetry entry.** Rejected: installation lacks a
  project/ticket binding and would create unused or mis-bound durable state.
- **Expose a public `create` method on the ledger or storage port.** Rejected: it makes the
  caller-selected identity or location part of the authority boundary.
