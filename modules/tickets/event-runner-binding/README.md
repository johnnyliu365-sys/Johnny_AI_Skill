# Event runner binding ticket registry

| Field | Binding |
| --- | --- |
| SPEC / AC | `modules/spec/receipt-bound-role-supervision.md` (`GitRefEventAdapter -> HandoffValidator -> RoleWakePort`) + Plugin Distribution Revision 02 AC-08, AC-09, AC-11 |
| Baseline | live-install line complete at `6a5706e`; rollback point `v0.4.0` = `d1d2080` |
| Authority | Owner-direct allocation, same mode as the live-install line |
| Workload | `external_effects=LOCAL_HOST`, `uncertainty=KNOWN_DOMAIN`, `recovery=RECOVERABLE` → derived `STANDARD`; the wake-capability gate is treated at `HIGH_ASSURANCE` review depth because a false capability claim silently breaks supervision |
| Boundary | Per-user Johnny root only; no heartbeat, polling, cron or watchdog; the runner sleeps on native Git ref signals and wakes at most one named reviewer per validated handoff; an unproven wake capability stays `HOST_WAKE_CAPABILITY_UNAVAILABLE` and degrades to a recorded completion candidate, never to a silent success |

## Honest capability model

`RoleWakePort` is the only path that may claim automatic wake, and it is admitted only after a
declared host command passes its own probe. Everything else records a completion candidate in
the durable wake inbox and keeps the typed block. Recording a candidate is never reported as a
wake.

| # | Ticket | Sole closure | State |
| --- | --- | --- | --- |
| E1 | Wake capability config + probe | Owner-declared host wake command is probed before any claim; absent/failing config yields `UNAVAILABLE` | `IN_PROGRESS` |
| E2 | Command role-wake port | Real `RoleWakePort` over the declared command with exactly-once, never-retry-ambiguity semantics | `PLANNED` |
| E3 | Durable wake candidate inbox | Unproven capability records one deduplicated candidate per attempt and stays typed-blocked | `PLANNED` |
| E4 | Runner process + lifecycle port | Detached per-project runner hosting the supervision controller; start/stop/status through a real `RunnerLifecyclePort` | `PLANNED` |
| E5 | CLI wiring | `johnny-router runner start\|stop\|status`, `wake-inbox list`, `wake-capability probe` | `PLANNED` |
| E6 | Gated end-to-end qualification | Real repository, real commit to the exact ref, real detached runner, real wake delivery, zero residue | `PLANNED` |
| E7 | Owner real-machine smoke | Owner runs the runner against a disposable repository and observes a real wake | `OWNER_EFFECT_REQUIRED` |

## E6 status — 4/5 real cells green, R3 blocked by CR-E6-01

The gated qualification runs the whole real chain and proves, against a real
repository and a real detached process:

| Cell | Result |
| --- | --- |
| R1 runner starts detached and records its channel | PASS |
| R2 proven capability resolves the command channel | PASS |
| R3 exact-ref commit delivers a real wake | PASS (after E8) |
| R4 stop is acknowledged and the process exits | PASS |
| R5 workspace is fully removable | PASS |

Two earlier R3 failures were the qualification's own defects and are fixed:
committing outside the exact reserved leaf (which the adapter correctly
classified `SOURCE_ADVANCED` and kept silent — a real proof that ordinary
source commits do not wake anyone), and an unsealed handoff payload.

### CR-E6-01 — the runner never seeds the durable receipt

Root cause, isolated by in-process tracing rather than inference: the native
watcher fires (verified directly: four real signals from one commit),
`prepare` returns `PREPARED`, `start` returns `ACTIVE`, and the supervision
chain reaches the wake stage — but the injected host wake port is never
called and the runtime halts with `ROLE_WAKE_UNAVAILABLE`. The cause is in
`LiveDispatchMetadataBoundary.claim_role_wake_attempt`: it admits a claim only
when the canonical `TicketReceipt` already exists in the durable checkpoint as
`ACTIVE` with a matching digest. The runner composition arms supervision
without ever registering the subscription's receipt into that boundary, so
every claim returns `ATTEMPT_CONFLICT` and no wake can be attempted.

This is a composition gap in the runner, not a defect in the frozen
supervision, adapter or boundary contracts — each behaved exactly as
specified, and the fail-closed posture held: no wake was claimed, nothing was
reported as delivered, and the runtime halted visibly instead of going quiet.

Defined fix (next ticket, not attempted here): the runner must register the
approved dispatch artifacts and issue the ticket receipt into the durable
boundary from the subscription spec before arming supervision, and must halt
with an exact typed failure when that seeding does not read back.

### CR-E6-01 closed by CLOSURE-E8-02 (OVR-EVENT-RUNNER-E8-REFREEZE-20260819-01)

The E8 closure exceeded the allowed correction count across two rounds that
both failed on the same authority-model defect (a runner minting approval from
caller data, then the same minting renamed instead of removed). The reviewer
escalated; the owner refroze the closure as CLOSURE-E8-02 with exactly one
additive correction and this final design:

- The runner composition holds no issuance-capable object.
  `runner_receipt_seeding` exports only `verify_receipt_claimable` (a pure
  read against a narrow `ReceiptReadPort`): the receipt must already be the
  exact `ACTIVE` canonical one in the durable checkpoint, or the runner halts
  with `RECEIPT_NOT_DISPATCHED` and the exact verification failure. The
  payload necessarily still ships the boundary and store classes — any code
  in the same Python process could import and construct them — so in-process
  hard isolation is not claimed here; it arrives with the workstation process
  boundary.
- Receipt issuance is a dispatch-authority effect owned by the control plane
  (`LiveDispatchMetadataStore.register_artifact` + `issue_receipt` behind the
  dispatch flow's admission). Qualifications stand in for a dispatcher through
  a test-only store fixture, the established 05B idiom; no issuing wrapper
  ships in the payload for anything to misuse.
- Containment additionally requires the Johnny base itself to resolve to
  itself, closing the redirected-base circularity, and the regression suite
  locks a real base-junction case plus a module-surface cell proving no
  issuing export exists.

The causal chain remains proven: the same wake claim conflicts against an
unseeded boundary and succeeds once a dispatcher has issued the receipt; the
gated qualification passes 5/5 with R3 green in under 2 seconds. The proper
dispatch-authority integration (who may issue, from which principal, over
which boundary) is deliberately out of scope here and belongs to the
multi-model workstation line, where issuance becomes a control-plane-process
privilege rather than an importable function.

### CLOSURE-E8-03 (OVR-EVENT-RUNNER-E8-R03-20260819-01)

The E8-02 final review found three residuals and the owner authorized one
further additive correction:

- **P0** the runner composition itself still constructed the full
  `LiveDispatchMetadataBoundary`, an object whose type carries issuance
  methods. The runner now holds only `WakeScopedDispatchBoundary` — exactly
  `read_receipt`, `claim_role_wake_attempt`, `settle_role_wake_attempt`; the
  full boundary is a private detail of that facade and no issuance name
  exists in the runner module's namespace (pinned by regression).
- **P1** both junction regressions used an absent bundle, so a missing ZIP
  produced the same `UNAVAILABLE` as the guard and removing the guard stayed
  green. Both cells now use a real extractable bundle: without the guard,
  extraction lands in the redirected target and the emptiness assertion
  turns red.
- **P1** the closure narrative claimed "the runtime payload can mint
  nothing", which overstated the isolation; it now states the precise claim
  (composition holds no issuance-capable object) and the residual
  single-process limitation explicitly.

| # | Ticket | State |
| --- | --- | --- |
| E8 | Runner receipt verification (CR-E6-01, CLOSURE-E8-02, CLOSURE-E8-03) | `CLOSED` — wake-scoped composition; discriminating junction regressions; E6 R3 green |
