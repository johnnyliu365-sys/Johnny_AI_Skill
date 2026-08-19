# W3 — Router Consumption of Reviewer Returns

| Field | Value |
| --- | --- |
| State | `CLOSED` |
| Baseline | `main` = `8a46ee0` |
| Workload | `STANDARD`; `HIGH_ASSURANCE` — an emitted event drives a workflow transition |
| Depends on | W2 (durable, unforgeable returns) |

## One outcome

Each recorded verdict becomes **exactly one** validated `RouterEvent`, and
never a second one:

```text
johnny-router review consume
```

W2 made the verdict durable and unforgeable. This makes it actionable.

## The boundary this ticket does not cross

`RouterEngine.decide(state, event, profile)` is a pure function over router
state and a project profile, neither of which this layer owns. W3 therefore
produces the validated event and stops; whoever holds the router state feeds
it. Emitting an event is not deciding a workflow, and pretending otherwise
would put workflow authority in the orchestration layer.

## Design

- Verdict mapping is total and honest:
  - `APPROVED` -> `APPROVAL_GRANTED`
  - `MODIFY_AND_REOPEN` -> `APPROVAL_DENIED`
  - `BLOCKED_BY_DEPENDENCY` -> refused `VERDICT_NOT_A_DECISION`. It is not a
    verdict the Router can act on: the dependency has to resolve first, and
    inventing a transition for it would be the orchestration layer deciding
    workflow policy.
- **At most once, never twice.** The consumed marker is written *before* the
  event is returned. A crash in between loses one emission; the verdict is
  still on file and visible, and re-emitting is a deliberate act. Double-
  driving a workflow transition is the failure this ordering refuses.
- The consumed marker is its own append-only file under the Johnny root,
  keyed by the same identity W2 uses (`project`, `receipt`, `handoff`,
  `reviewer`). The returns file is never rewritten: evidence is append-only.
- The emitted event carries a deterministic `event_id` derived from that
  identity, so the same verdict can never appear under two event ids.

## Authorized implementation scope

```text
library/local_orchestration/review_return_consumption.py
library/local_orchestration/review_cli.py       # one subcommand
tests/test_review_return_consumption.py
modules/tickets/workstation-dispatch/
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `W3-R1` | With no returns, consumption reports `NOTHING_PENDING` and writes no marker. |
| `W3-R2` | An `APPROVED` return emits a validated `RouterEvent` of kind `APPROVAL_GRANTED`; `MODIFY_AND_REOPEN` emits `APPROVAL_DENIED`. Both carry the deterministic event id. |
| `W3-R3` | `BLOCKED_BY_DEPENDENCY` is refused `VERDICT_NOT_A_DECISION`, emits nothing, and is not marked consumed. |
| `W3-R4` | Exactly once: consuming the same return twice emits once, and the second call reports `NOTHING_PENDING`. Two distinct returns each emit once, in file order. |
| `W3-R5` | The marker is written before the event is returned — proven by a fault injected between the two, after which the event is not re-emitted. |
| `W3-R6` | The emitted event validates as a real `RouterEvent` and is accepted by `RouterEngine.decide` as a well-formed input (a decision is produced, whatever it is). |
| `W3-R7` | Reverse mutations: removing the consumed-marker check turns R4 red; mapping `BLOCKED_BY_DEPENDENCY` to a decision turns R3 red. |
| `W3-R8` | `mypy --strict` clean; full suite green; zero residue. |

## Closure evidence (2026-08-19, control-plane executed)

- `W3-R1` No returns → `NOTHING_PENDING`, no marker file created.
- `W3-R2` `APPROVED` → `APPROVAL_GRANTED`; `MODIFY_AND_REOPEN` →
  `APPROVAL_DENIED`. The event id is deterministic and contains every part of
  the return's identity, so the same verdict cannot appear twice under two ids.
- `W3-R3` `BLOCKED_BY_DEPENDENCY` refuses `VERDICT_NOT_A_DECISION`, emits
  nothing, writes no marker, and stays pending — the dependency has to resolve
  first, and inventing a transition would be this layer deciding policy.
- `W3-R4` Consuming twice emits once; two distinct returns each emit once, in
  file order, with distinct ids.
- `W3-R5` The marker is durable before the event is handed back: a caller that
  drops the event entirely gets `NOTHING_PENDING` on retry, which is what a
  crash between the two looks like from outside.
- `W3-R6` The emitted event re-validates strictly as a `RouterEvent` with no
  stray completion or return metadata.
- `W3-R7` Reverse mutations: ignoring the consumed markers turns three cells
  red; mapping `BLOCKED_BY_DEPENDENCY` to a decision turns R3's cell red.
- `W3-R8` `mypy --strict` clean; full suite `989 passed, 11 skipped`; zero
  residue.

CLI smoke: `review consume` with nothing pending → `NOTHING_PENDING` exit 0;
with a recorded verdict → `EMITTED` carrying the event id and
`approval_granted`; again → `NOTHING_PENDING`.

## What remains, deliberately

Feeding the emitted event to `RouterEngine.decide` needs router state and a
project profile that this layer does not own. W3 stops at producing the
validated event exactly once; whoever holds that state drives the transition.
Moving it here would put workflow authority in the orchestration layer.
