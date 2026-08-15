# ADR-20260816-014 — Project-neutral orchestration, evidence, and counterfactual telemetry

- Date: `2026-08-16 (Asia/Taipei)`
- Status: `ACCEPTED — exact SPEC revisions pending owner approval`
- Decision makers: project owner and architecture owner
- Related change: `CHG-20260816-025`
- Related specifications: Adaptive Project Orchestration Revision 07, Environment Capability
  Bootstrap Revision 02, Receipt-bound Role Supervision Revision 02 and Context Load Telemetry
  Revision 03

## Context

The previously approved isolation and supervision direction removed target-local Johnny state
and recurring model wake, but its feature specifications were not yet one coherent operating
contract. Initialization still assumed reviewer activation, isolated checkouts prohibited even
Johnny-internal immutable Git-object reuse, resource classes lacked exact caps, and telemetry
expected matched provider runs that would spend the tokens it was meant to measure.

The owner requires the control plane to minimize token cost while preserving stable production,
leave CPU and memory available for current or future local models, keep project artifacts
portable after plugin removal, and provide auditable token/cost charts only when requested.

## Decision

1. Each project owns one architecture-owner binding, one Senior binding and a bounded number of
   ticket-demand Implementer slots. Role identity is project-exclusive while active. Existing
   conversation tasks may be rebound only through exact typed readback.
2. A project Implementer slot uses a target-owned tree-shaped Context Library. Each ticket or
   correction resolves one immutable `context_epoch_id`; closed epochs remain indexed for later
   repair and audit but are not automatically model-visible.
3. Johnny-owned standalone workspaces may use a Johnny-internal append-only content-addressed
   seed/object pool. Immutable baseline generations are exact-digest referenced. Target Git
   storage, configuration and runtime never depend on the pool.
4. Initialization creates no empty governance tree. It adopts same-purpose target documents and
   may create only exact approved manifest entries. A missing root README may be created only by
   that manifest and must explain that Johnny is external and removable.
5. Resource plans are immutable, receipt-bound and one-shot. `LIGHT` and `STANDARD` have exact
   ceilings; `HEAVY_APPROVAL` requires separately approved values. Local inference/training
   reservations are deducted before Johnny capacity. Insufficient remainder stops Johnny work
   without killing or reconfiguring the model.
6. `TicketReceipt` alone authorizes implementation. A distinct `StageWorkReceipt` provides
   traceability for Architecture, Grill, SPEC and Senior planning but grants no execution or
   external-effect authority.
7. Runtime operation stores a small metadata-only `RuntimeEvidenceManifest` keyed by receipt.
   It references immutable Context exposure, interactive model reads, Git result diff/write and
   provider-usage evidence; it does not continuously calculate savings or persist raw content.
8. Only an explicit user report request runs the calculator. The primary no-takeover baseline is
   a zero-inference dry count of eligible Git-tracked text at the exact snapshot with Johnny
   Router, skills and Context-management inputs removed. Equal-output and cache behavior are
   explicit counterfactual assumptions, never observed facts.
9. Usage and cost remain separated by role, exact provider/model/revision, capability tier,
   reasoning effort, service tier and pricing revision. Provider-native currency is retained;
   missing usage or price remains unreported/unpriced.
10. Reports and charts are Johnny-owned and emitted to stdout on demand. The user may redirect
    them externally. The control plane never writes report files or raw telemetry into the
    controlled project.
11. Heartbeat, cron, watchdog and recurring model/thread/Git/filesystem polling remain forbidden
    without separate explicit user approval. Native event callbacks and one exact terminal
    reconciliation are not model wake loops.

## Alternatives rejected

- One implementation branch per historical ticket: rejected because it duplicates Git state
  and fragments repair Context; the project slot plus epoch library gives bounded retrieval.
- Target-linked worktrees or target-local telemetry: rejected because they couple and pollute
  the controlled repository.
- Full independent baseline model runs by default: rejected because measurement would consume
  extra tokens and create provider variance unrelated to Context management.
- Continuous aggregate reports: rejected because they spend CPU/I/O when no user needs a report
  and make stale aggregates look authoritative.
- Agent self-reported usage or source-character counts labeled as provider tokens: rejected
  because they are not runtime evidence.

## Consequences and recovery

- The control plane gains more contract types and receipt-indexed evidence, but active model
  Context stays bounded to the current leaf.
- Exact report generation can be CPU work; it is user-triggered, resource-bounded and may return
  `PARTIAL`, `NOT_OBSERVED`, `NOT_REPORTED`, `UNPRICED` or context-overflow states instead of
  guessing.
- Plugin detach/uninstall removes only ledger-proved Johnny-owned workspaces, generations,
  pools, streams and manifests. An unproved item is reported and skipped; it cannot block the
  remainder of uninstall or constrain the successor.
- Existing Senior admission decisions remain immutable. After exact SPEC approval, the Senior
  performs new decomposition rather than rewriting historical leaves.
