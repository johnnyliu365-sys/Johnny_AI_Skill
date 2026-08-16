# Receipt-bound Role Supervision Context

| Field | Value |
| --- | --- |
| State | `SEALED / REVISION_01_APPROVED / REVISION_02_APPROVED / REVISION_03_APPROVED / REVISION_04_APPROVED / REVISION_05_APPROVED / REVISION_06_OWNER_APPROVED / SENIOR_BRIDGE_REVIEW_REQUIRED` |
| Requirement / ADR | `PRD-20260815-023`, `CHG-20260815-023`, `PRD-20260816-025`, `CHG-20260816-025`, `PRD-20260816-026`, `CHG-20260816-026`, `PRD-20260816-027`, `CHG-20260816-027`, `PRD-20260816-028`, `CHG-20260816-028`, `PRD-20260816-029`, `CHG-20260816-029` / `ADR-20260815-012`, `ADR-20260816-014`, `ADR-20260816-015`, `ADR-20260816-016`, `ADR-20260816-017` |
| SPEC | `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2` |
| Shared Context | `main@f7eb3d3c9c88c23c3bc29bc9565ebc5b3b7096f9`; role facts from `CHG-20260815-023`, latest seal `CHG-20260815-024` |
| Control owner | Architecture owner / current `main` |

## Confirmed facts

- The design must minimize total token cost without weakening correctness, authority or stable
  project delivery. Among designs that pass those hard gates, lower CPU and I/O cost wins.
- The Senior (the reviewer role) is the sole Agent-to-Agent orchestrator. The architecture owner defines the
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
- A ticket has exactly one valid private Router receipt at a time. Supervision, execution-start
  evidence and leases bind that receipt; there is no separate execution receipt. Same-ticket
  correction reuses it. A receipt-bound identity change requires Router revocation before one
  same-ticket replacement receipt can become valid.
- The live `TicketReceipt` remains active after delivery; a separate one-shot dispatch claim is
  settled by the host delivery result. The historical `TicketDispatchReceipt` contract is only
  a pure Router-confirmation projection and cannot be persisted as independent authority.
- Approved dispatch artifacts and live receipt/claim lifecycle are durable metadata under the
  installer-owned Johnny root. One project/ticket has at most one active or quarantined receipt,
  receipts have no expiry, and plugin removal deletes only ledger-proved Johnny-owned live state.
- Before any Agent-control effect, exact readback must admit the Senior, pending descriptor,
  implementation task, worktree, branch preparation mode, baseline, model/profile, Context epoch,
  restricted-tool posture and complete supervision chain. Identifiers, prompts and config bytes
  alone are not readback.
- Host delivery has only `DELIVERED`, `NO_EFFECT` or `EFFECT_UNCERTAIN`. A proved no-effect may
  retry only the same dispatch operation. An uncertain effect quarantines the operation and
  receipt; there is no automatic retry, replacement receipt or second dispatch.
- Revision 04 has one finite self-host bootstrap route for R03-01 through R03-03. The separate
  owner-approved BPB may bridge only exact R03-00 so that the Revision-05 executable policy can be
  implemented; it does not widen that three-ticket allowlist. Neither route is available to
  another project/ticket. Architecture defines policy but never selects or dispatches an
  Implementer.
- R03-01 uses an owner-approved no-receipt `BootstrapDispatchGrant`. R03-02 and R03-03 require a
  real active `TicketReceipt` plus a separate one-shot `BootstrapTransportGrant`; neither grant
  is a `WorkReceipt` member or live-capability evidence.
- Senior commits an immutable attempt leaf before every bootstrap host call. The attempt consumes
  the grant. Crash, timeout, ambiguous error or missing exact readback is `EFFECT_UNCERTAIN` and
  cannot retry. Every correction receives a new grant; R03-02/R03-03 retain their receipt only
  when ordinary same-ticket identity remains unchanged.
- Until `NORMAL_ACTIVE`, the user may relay only `BOOTSTRAP_RETURN_AVAILABLE` plus `grant_ref` to
  wake the Senior. Senior independently reads Git/handoff evidence; the relay is not authority or
  completion proof.
- Approved review may create a distinct exact bootstrap integration grant without a second owner
  prompt. R03-03 still requires explicit ticket-specific high-assurance approval. Only reviewed
  integration plus real positive host/supervision readback closes bootstrap and enables normal
  automatic dispatch.
- Normal automatic dispatch is limited to one unique dependency-complete, already-approved
  low/standard ticket with all normal receipt/workspace/baseline/supervision gates. High assurance,
  external effects, changes, ambiguity and multiple candidates still require the owner.
- Architecture, Grill, SPEC and Senior planning may receive a `StageWorkReceipt` for provenance.
  It is a distinct non-execution receipt and can never dispatch an Implementer, mutate source or
  authorize an external effect. `TicketReceipt` remains the only implementation receipt.
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
- A receipt reference committed in a handoff is opaque historical provenance only. Live Router
  receipts, grants and bindings stay in Johnny-owned private state and are removed with the
  plugin.
- The user may remove the plugin before handoff without checkpoint, push, readback or Router
  permission. A successor may use any workflow. If the successor voluntarily re-adopts Johnny,
  takeover creates new receipts and bindings; historical live receipts are not replayable.
- A `DIAGNOSTIC_OWNER` is created only by a Senior diagnosis ticket, uses `gpt-5.6-sol` at
  `xhigh`, and is read-only. It returns findings to the Senior, cannot implement, review,
  dispatch or integrate, and becomes inactive after the diagnosis. It has no heartbeat.

## Revision 05 approved route

The failed R03-01 review returned `TICKET_DEFECT -> ARCHITECTURE / CHANGE_CONTROL`. The bounded
Grill result and approved replacement facts are indexed at
[`revisions/rev05-r03-ticket-defect-recovery.md`](revisions/rev05-r03-ticket-defect-recovery.md).
They are not implementation authority. The original grant remains consumed, R03-01 is
non-integrable and R03-02/R03-03 remain blocked. The Router return is `APPROVAL_GRANTED ->
ACTION_COMPLETED / SPEC`; the next action belongs to `TICKETS / SENIOR_READMISSION`. Senior may
draft decomposition and policy-correction tickets but may not create any R03-01A through R03-01D
grant or dispatch until the Workflow/executable policy correction is separately reviewed and
integrated. Exact R03-00 bridge review follows Revision 06 below.

## Revision 06 approved policy bridge

The exact one-ticket bridge facts are sealed at
[`revisions/rev06-r03-00-policy-bridge.md`](revisions/rev06-r03-00-policy-bridge.md). The bridge
does not make R03-00 dispatchable by approval alone: the only next action is an independent Senior
review of its exact commit. Only an `APPROVED` bridge review may precede a separately committed and
owner-approved R03-00 grant. R03-01A through R03-01D remain blocked.

## Boundaries

- No heartbeat, scheduled automation, cron, watchdog, recurring thread read, Git polling or
  repository-wide scan.
- No production deployment implementation, Provider integration, Secret handling or automatic
  external effect. Development receipts never imply push, release or deployment authority.
- Revision 03 does not create a task-event subscription, `RoleWakePort`, host gateway or current
  capability claim. The separately required supervision chain still halts dispatch when absent.
- Revision 04 is an explicit self-host exception, not a generic fallback. It cannot be inferred
  from `CAPABILITY_UNAVAILABLE`, copied into a target project or used after `NORMAL_ACTIVE`.
- Exact bridge approval authorizes independent Senior bridge review only. No grant, attempt,
  receipt, dispatch or implementation exists from approval alone; R03-00 remains non-dispatched
  until bridge review and a separate owner-approved grant both exist.
