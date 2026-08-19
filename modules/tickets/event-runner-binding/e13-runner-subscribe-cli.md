# E13 — `runner subscribe`: the Subscription Builder Reaches the CLI

| Field | Value |
| --- | --- |
| State | `OPEN` — awaiting named implementation owner (Antigravity/Gemini) |
| Baseline | `main` at the commit this ticket lands in |
| Workload | `SMALL`; Python 3.11 strict, TDD, no baseline-red required |
| Depends on | E9 (closed): `subscription_builder.build_subscription` exists and is tested |

## One outcome

An owner can compose a runner subscription from the command line:

```text
johnny-router runner subscribe <inputs.json>
```

which reads the already-issued receipt from the durable checkpoint, probes
both capabilities, writes `runner-subscriptions.json`, and prints exactly one
typed JSON line. Today `build_subscription` is callable only from a source
checkout, so the runner cannot be fed work on an installed host.

## The inputs file

One JSON document with two sections:

- `receipt_locator`: `project_id`, `ticket_reference`, `ticket_revision` —
  exactly what `TicketReceiptReadRequest` needs. The CLI **reads** the receipt
  through the wake-scoped boundary; it never constructs one. A receipt that
  dispatch never issued is a typed refusal (`RECEIPT_NOT_DISPATCHED`).
- `inputs`: the existing `SubscriptionInputs` fields, validated by that model
  exactly as-is. Do not duplicate its validation in the CLI.

## Authority rules (inherited from E8/E9 — the reviewer will check these)

- The CLI holds only `WakeScopedDispatchBoundary`. No issuance-capable object
  may appear anywhere in this path.
- Capability proofs stay probed, never supplied: the CLI passes nothing
  capability-shaped through from the inputs file.
- Every receipt-bound identifier is derived from the stored receipt (that is
  already how `build_subscription` works — do not add pass-throughs).

## Authorized implementation scope

```text
library/local_orchestration/runner_cli.py
library/local_orchestration/subscription_builder.py   # only if a receipt-read helper is genuinely needed
tests/test_event_runner_cli.py
modules/tickets/event-runner-binding/README.md        # E13 row update only
modules/tickets/event-runner-binding/e13-runner-subscribe-cli.md
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `E13-R1` | Valid inputs + issued receipt (via the established `_issue_receipt_fixture` idiom) → `runner-subscriptions.json` written, exit 0, one typed `{"status":"WRITTEN"}` line; the written file round-trips through `RunnerSubscriptionFile.model_validate_json`. |
| `E13-R2` | Undispatched receipt → typed `RECEIPT_NOT_DISPATCHED`, nonzero exit, no file written. |
| `E13-R3` | Missing, unreadable, or schema-invalid inputs file → typed refusal, nonzero exit, no file written; the refusal names which section failed. |
| `E13-R4` | Unprovable wake capability → typed `WAKE_CAPABILITY_UNAVAILABLE`, nonzero exit (declare no wake command in the test layout). |
| `E13-R5` | The CLI path imports no issuance-capable name; pin it the E8 way — assert on the runtime objects or module surface, not on comments. |
| `E13-R6` | `mypy --strict` clean; full suite green; `tests/.johnny-runtime` zero residue. |

## Environment facts

- Python is `py -3.11` (no `python`, no `pwsh`; Windows PowerShell 5.1).
- Console codepage is cp950: decode subprocess output as bytes/UTF-8, never
  `text=True`.
- Working copies are CRLF; mutation and edit scripts must normalize `\r\n`.
- Worktree location is governed: create yours at `.worktrees/e13-runner-subscribe`
  under the repository root, never as a sibling folder.
- The runner CLI dispatch lives in `runner_cli.py` (`run_runner_family`); the
  `subscribe` subcommand joins `start`/`stop`/`status` there. Look at how
  `wake-capability probe` is wired for the established pattern.
