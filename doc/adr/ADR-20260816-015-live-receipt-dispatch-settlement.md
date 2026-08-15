# ADR-20260816-015 — Live receipt dispatch admission and uncertain-effect quarantine

- Date: `2026-08-16 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `CHG-20260816-026`
- Related specification: Receipt-bound Role Supervision Revision 03

## Context

The Router already validates reviewed ticket/handoff metadata and a supplied dispatch receipt,
but its approved-artifact registry and private service are deterministic process-local fakes.
They cannot prove that a live receipt was uniquely issued, that the selected task/workspace is
still the admitted writer, or that a host delivery effect happened exactly once.

Repeating a host call after a timeout can dispatch the same ticket twice. Treating a successful
tool invocation as execution-start evidence can start supervision before the implementation task
is executable. Neither risk can be repaired with a heartbeat or repeated thread reads.

## Decision

1. One canonical `TicketReceipt` is durable Johnny-owned private metadata and remains active for
   the ticket execution. The existing `TicketDispatchReceipt` is a pure compatibility projection
   into the Router confirmation event, not a second receipt.
2. Approved dispatch artifacts are registered immutably by exact project, ticket, ticket digest,
   ticket-doc commit, handoff, handoff-doc commit and implementation owner. Conflicting bytes under
   one identity halt before receipt issuance.
3. Receipt issuance is compare-and-swap against one live `PendingDispatchDescriptor`. One
   project/ticket has at most one active or quarantined receipt. Receipts have no time expiry.
4. Before effect, an injected admission adapter reads the exact Senior, implementation task,
   worktree, branch-preparation mode, baseline, model/profile, Context epoch, restricted-tool
   posture and supervision-chain capability. A raw path, prompt, profile label or chat claim is
   not readback.
5. Dispatch uses a separate one-shot operation claim. A synchronous host result has three
   meanings: `DELIVERED`, `NO_EFFECT` or `EFFECT_UNCERTAIN`. Delivered settles only the operation;
   the receipt remains active. Proved no-effect may retry only the same operation identity.
   Uncertain effect quarantines the operation and receipt until one exact reconciliation or
   Router revocation. No automatic retry is legal.
6. The host-facing envelope contains only the six canonical dispatch identifiers. The Senior is
   the sole caller and the implementation owner receives no gateway capability.
7. Durable state uses the existing installer-owned metadata journal/checkpoint boundary below
   `%LOCALAPPDATA%\JohnnyAIWorkflow`. No new database, service or target-project state is added.
   Plugin removal deletes only ledger-proved Johnny-owned live state and never edits target Git.
8. Dispatch admission also requires the separately specified supervision chain. This decision
   does not invent a missing Codex task-event subscription or `RoleWakePort`; unavailable
   capability fails closed before the Agent-control effect.

## Consequences

- A crash can resume from immutable metadata without manufacturing a receipt or repeating an
  uncertain host effect.
- The live adapter has more finite states than the test fake, but idle cost remains zero: no
  heartbeat, timer loop, periodic read or polling is introduced.
- Current Codex `send_message_to_thread`/one-shot readback may satisfy a future host delivery port
  only when an implementation ticket proves exact task binding and result semantics. Tool
  presence alone is not capability proof.
- If the supervision wake chain remains unavailable after this adapter is implemented, normal
  implementation dispatch still halts. The receipt adapter cannot weaken that independent gate.

## Rejected alternatives

- Persisting only `TicketDispatchReceipt`: rejected because it omits registry, lifecycle, task,
  Context and operation-settlement identity.
- Marking the ticket receipt consumed after delivery: rejected because the same receipt must
  remain the execution/supervision authority through terminal handoff and correction.
- Retrying a timed-out host call with a new receipt or operation ID: rejected because the first
  effect may have succeeded.
- Heartbeat, recurring thread read or Git polling: rejected by owner policy and unnecessary for
  dispatch settlement.
- Target-local receipt files or a new database/MCP service: rejected because they couple the
  control plane to the project or expand the approved runtime boundary.
