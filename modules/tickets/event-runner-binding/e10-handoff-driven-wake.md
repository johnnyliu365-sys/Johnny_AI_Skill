# E10 — The Handoff-driven Wake Does Not Fire (CR-E7-01)

| Field | Value |
| --- | --- |
| Origin | Control-plane E7 owner-smoke preparation, 2026-08-19 |
| State | `CLOSED` — root cause isolated by direct observation and fixed; E10-R1–R5 all green |
| Severity | `P0` — invalidates the headline 0.4.1 claim that a Git ref event wakes a reviewer |
| Baseline | `main` = `c4e0790` |
| Workload | `STANDARD`; `HIGH_ASSURANCE` review depth, same as the rest of the wake chain |

## What is proven

Established by a clean, controlled run of `doc/runbooks/e7_owner_smoke.py`
against a disposable repository, with no in-process diagnostics touching the
durable state:

- The runner arms correctly: `prepare` returns `PREPARED`, `start` returns
  `ACTIVE`, state is `RUNNING`, and the resolved channel is `HOST_COMMAND`
  (not the candidate inbox).
- The **deadline** wake path really delivers. A `ROLE_WAKE_V1` payload with
  `action=SUPERVISION_DEADLINE` reaches the declared host command.
- The **handoff-driven** wake path does **not** deliver. With the deadline not
  yet due, a sealed terminal `HandoffLeaf` committed to the exact watched ref
  at the reserved path produced no wake within 60 seconds.
- The failure is not a field mismatch. All fourteen admission-context fields
  were compared against the committed leaf and matched exactly, and the
  registration's `exact_git_ref` and `reserved_handoff_ref` were correct.
- The failure is not the unbatched composition: both supervision builders pass
  the wake port through identically.

## Why this was not caught (CR-E7-01)

`test_r3_exact_ref_commit_delivers_a_real_wake` asserted only
`"handoff" in payload`. A `SUPERVISION_DEADLINE` payload satisfies that,
because it carries the field `handoff_id=-`. The qualification's fixture also
sets `started_at_ms=1_000`, which puts the supervision deadline permanently in
the past, so a deadline wake fires the instant supervision arms.

The two together made R3 pass on a wake that would have been delivered with no
commit at all. The assertion is now discriminating (it refuses
`SUPERVISION_DEADLINE`) and R3 is **red**, committed failing rather than
weakened, exactly as CR-E6-01 was.

A second defect found on the way, already fixed: `subscription_builder`
inherited the same `started_at_ms=1_000` fixture constant, so every composed
subscription had an already-expired deadline. It now reads
`monotonic_ns() // 1_000_000`, the clock `one_shot_deadline` actually compares
against, pinned by regression.

## What must be determined

Root cause has **not** been isolated. The two candidates, in order:

1. The native ref watcher never signals for these commits, so the adapter is
   never invoked.
2. The watcher signals and the adapter classifies the event silently
   (`SOURCE_ADVANCED`, a consumed handoff id, or a readback failure that
   returns a silent decision).

Isolate this the way CR-E6-01 was isolated: in-process tracing on a real
repository, observing the watcher callback and the adapter decision directly,
rather than inferring from the absence of a wake.

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `E10-R1` | Root cause named with direct observation, not inference: either the watcher callback count for a real commit, or the exact adapter decision returned. |
| `E10-R2` | A real commit of a sealed terminal leaf to the exact watched ref delivers a `ROLE_WAKE_V1` payload whose `action` is the handoff completion, with the deadline not due. |
| `E10-R3` | E6 R3 is green again with the discriminating assertion intact; deleting the `assertNotEqual` on `SUPERVISION_DEADLINE` must not be needed to pass. |
| `E10-R4` | A reverse mutation proves R3 discriminates: with the wake suppressed, R3 turns red rather than passing on the deadline. |
| `E10-R5` | The README's automatic-wake claim is restored only to what the evidence supports. |

## Release impact

`README.md` claimed for 0.4.1 that the event runner is driven by exact Git ref
events. The runner does arm on those events and the channel is real, but the
only wake proven to be delivered is the deadline. The README is corrected to
say so until this ticket closes.

## Closure (2026-08-19, control-plane executed)

**Root cause (E10-R1), directly observed.** `RoleWakeCoordinator.wake` refuses
a `REVIEW_HANDOFF` wake whose `review_instruction` is `None`, returning
`ATTEMPT_CONFLICT` before the durable store is consulted — and
`wake_request_from_git_decision` always builds handoff wakes with
`review_instruction=None`, because filling it is the Senior review inbox's
job. The unbatched composition removed that layer without reassigning the
responsibility, so every handoff-driven wake was structurally refused while
deadline wakes (a different trigger) kept flowing. Observed in-process with
recorders on the watcher sink, the adapter, and the coordinator: 4 native
signals, `TERMINAL_HANDOFF_ACCEPTED`, one coordinator call returning
`ATTEMPT_CONFLICT` with the boundary's claim never invoked.

**Fix.** `SingleHandoffReviewSubmission` in
`windows_supervision_composition.py`: without batching, the single validated
handoff is its own batch, so the instruction is derived one-to-one from
identifiers the wake request's chain already binds (batch
`single-<handoff-id>`, trigger commit = observed commit, one cluster, one
ticket read naming the chain's ticket and receipt). Nothing mints authority:
the coordinator still claims against the durable receipt exactly as before,
and the derived instruction rides into the payload as
`review_batch_id`/`review_trigger_commit`/`review_cluster` lines.

**Also fixed on the way.** The qualification's lease started at the fixture
constant `1_000`, so the deadline wake fired at arm time and closed the
runtime before any handoff could act — it now starts on the host's real
monotonic clock. And the qualification's wait predicate was file existence,
which the capability probe satisfies by itself; it now waits for a real
`ROLE_WAKE_V1` payload.

- `E10-R2` Real detached runner, real commit, deadline not due: delivered
  payload has `action=REVIEW_HANDOFF`, the real observed commit, the real
  `handoff_id`, and the derived review-instruction lines.
- `E10-R3` Gated E6 is `5 passed` with the discriminating R3 intact.
- `E10-R4` Reverse mutation: dropping the wrapper from the builder turns R3
  red (60s, no wake); restoring turns it green in ~2s.
- `E10-R5` The README known-defect warning is replaced by the fix record.

Unit regressions in `tests/test_single_handoff_review_submission.py` pin the
coordinator gate itself (no instruction → refused before the store), the
derived instruction's shape, and pass-through for deadline and already-filled
requests.
