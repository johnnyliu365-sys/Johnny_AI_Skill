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
