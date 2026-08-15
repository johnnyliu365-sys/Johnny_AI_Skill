# Receipt-bound Role Supervision Context

| Field | Value |
| --- | --- |
| State | `SEALED / SPEC_DRAFT_OWNER_REVIEW_REQUIRED` |
| Requirement / ADR | `PRD-20260815-023`, `CHG-20260815-023` / `ADR-20260815-012` |
| SPEC | `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2` |
| Prior shared Context | `main@2701ed563f26e116db69e8e4fcb84024754c9498` / SHA-256 `CD333B787670AC78F5B4A5DB495D7759B92AEA52F194D67559EF05142A6CD073` |
| Control owner | Architecture owner / current `main` |

## Confirmed facts

- The design must minimize total token cost without weakening correctness, authority or stable
  project delivery. Among designs that pass those hard gates, lower CPU and I/O cost wins.
- The reviewer is the sole Agent-to-Agent orchestrator. The architecture owner defines the
  contract and wakes only on existing typed architecture conditions; the implementation owner
  never wakes or controls another Agent.
- A Git ref event is a detection hint. Only a committed, exact, receipt/task/branch/baseline-
  validated handoff can produce a terminal event or trusted supervision fault.
- `GitRefEventAdapter -> RoleWakePort -> named role` is the only approved automatic wake chain.
  Active-turn blocking wait is not approved. Missing capability halts before implementation
  dispatch.
- Heartbeat is forbidden unless the user grants separate, explicit, scope-bound approval. Ticket
  approval, dispatch confirmation, auto-continue or a request to monitor does not approve it.
- Reviewer supervision starts only after host readback proves the implementer received the
  ticket, exact task/worktree binding and executable state. Pre-dispatch handoff time is not
  counted.
- Luna xhigh is the default implementer. Its total execution ceiling is thirty minutes and never
  resets. Terra-or-higher uses a two-hour inactivity lease; validated ref activity resets that
  lease inside the adapter without waking a model.
- Luna overrun is treated as a ticket-complexity defect. Split by observable closure when legal;
  otherwise replace the current task once with Terra high. The next new ticket returns to Luna
  xhigh. Terra high may receive one same-ticket continuation after an incomplete stop; a second
  incomplete stop routes `MODEL_CAPABILITY_INSUFFICIENT` to the architecture owner.
- Terminal identity is the write-owning execution task/session, not a shell, IDE or subprocess.
  A different task, writer, host or machine uses controlled replacement while the plugin is
  attached; old and new writers never overlap.
- Target projects own a plugin-neutral handoff tree, root manifest and root README operation
  guide. They contain no Secret, prompt, raw Context or plugin runtime dependency.
- The user may remove the plugin before handoff without checkpoint, push, readback or Router
  permission. A successor may use any workflow. If the successor voluntarily re-adopts Johnny,
  takeover creates new receipts and bindings; historical live receipts are not replayable.

## Boundaries

- No heartbeat, scheduled automation, cron, watchdog, recurring thread read, Git polling or
  repository-wide scan.
- No production deployment implementation, Provider integration, Secret handling or automatic
  external effect. Development receipts never imply push, release or deployment authority.
- No tickets, dispatch or implementation are authorized until the project owner approves the
  exact independent SPEC revision and the reviewer compiles it through the normal Router.
