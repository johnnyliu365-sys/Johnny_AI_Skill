# ADR-20260815-012 — Receipt-bound Git event supervision and detachable handoff

- Date: `2026-08-15 (Asia/Taipei)`
- Status: `PROPOSED / OWNER_APPROVAL_REQUIRED`
- Decision makers: project owner and architecture owner
- Related specification: `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2`
- Related change: `CHG-20260815-023`

## Context

Repeated model-driven thread reads spend tokens when nothing changed. Interval Git polling moves
that waste to CPU and I/O, while neither approach proves who may wake a role. The host currently
does not expose a receipt-bound implementation completion subscription. Supervision therefore
needs an explicit Git event boundary, a separately proved role-wake capability and a durable
target-owned handoff tree.

The owner forbids heartbeat unless separately and explicitly approved. The owner also requires
the plugin to remain removable: uninstalling it must not block the project or force a successor
to adopt the same Router.

## Decision

1. The pure Router remains deterministic and consumes only validated metadata-only events.
2. A native `GitRefEventAdapter` observes the exact bound branch/ref. A ref change is only a
   hint; validation reads the committed handoff with
   `git show <handoff-commit>:<exact-leaf>` and verifies receipt, task, branch, baseline ancestry,
   digest and terminal meaning.
3. An ordinary source commit or working-tree change never wakes a model. A valid terminal
   handoff wakes the named reviewer once through a separately proved `RoleWakePort`. Invalid
   content in the reserved handoff path emits one trusted `SUPERVISION_FAULT / INVALID_HANDOFF`
   and then halts.
4. Dispatch is forbidden unless the complete Git-event-to-role-wake chain is proven. There is
   no active-turn blocking fallback, heartbeat, cron, watchdog, scheduled polling, recurring
   thread read or recurring Git/filesystem scan.
5. One one-shot native deadline is allowed per active execution binding. It is not a heartbeat:
   it produces no periodic wake and fires only at the declared supervision boundary. Terra-or-
   higher uses a two-hour inactivity lease reset silently by validated ref activity. Luna xhigh
   uses a non-resettable thirty-minute total execution ceiling.
6. The reviewer is the sole Agent orchestrator. A wake causes read-only diagnosis first. The
   reviewer may continue the same bound implementation only within the finite model policy in
   the SPEC; architecture wakes only for the existing typed architecture conditions.
7. The authority unit is the write-owning execution session/task, not a PowerShell window, IDE
   or subprocess. A new task, writer, host or machine uses controlled replacement while the
   plugin remains attached; old and new bindings never write concurrently.
8. Every target project owns a bounded, plugin-neutral handoff tree and machine-readable root
   manifest. The root README explains normal operation, terminal replacement, deployment
   separation and plugin removal.
9. The user may remove the plugin at any time without checkpoint, push, readback or Router
   permission. Removal does not modify target source or CI and does not constrain the successor's
   workflow. Only already committed and accessible Git content is naturally portable; unfinished
   work and in-flight external effects receive no cleanup guarantee from a removed plugin.
10. A successor who voluntarily adopts this Router performs a fresh takeover and receives new
    task/receipt/correlation bindings. Historical live receipts are never replayed.

## Alternatives rejected

- Heartbeat or scheduled wake: rejected because it spends model tokens without evidence and is
  forbidden without explicit user approval.
- Recurring Git/thread polling: rejected because idle CPU/I/O or model cost grows with time.
- Same-turn blocking model wait: rejected by the owner; only the event adapter plus wake port is
  admissible.
- Host handoff-operation status as task completion: rejected because it cannot bind the
  implementation task and receipt.
- Requiring a clean detach before uninstall: rejected because the plugin must remain removable
  before a successor chooses a workflow.

## Consequences and recovery

- Idle supervision has no model wake and no periodic read. Event adapters scale with active
  execution bindings rather than shells or repository size.
- Loss of the wake port halts new dispatch; it does not justify a fallback mechanism.
- Target runtime, CI, deployment and project artifacts never depend on the plugin.
- Controlled replacement recovers only committed checkpoints if the old writer is unavailable.
- Rollback disables the adapter and role-wake composition. Forward fix requires a newly proven
  capability revision; no periodic fallback is introduced.
