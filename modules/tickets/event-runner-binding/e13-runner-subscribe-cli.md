# E13 — `runner subscribe`: the Subscription Builder Reaches the CLI

| Field | Value |
| --- | --- |
| State | `CLOSED` |
| Baseline | `main` = `cf091c9` |
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

## Closure evidence (2026-08-19)

- `E13-R1` A receipt seeded through `_issue_receipt_fixture` plus a valid
  inputs file → `runner subscribe` prints exactly `{"status": "WRITTEN"}`,
  exit 0; `runner-subscriptions.json` round-trips through
  `RunnerSubscriptionFile.model_validate_json`.
- `E13-R2` A `receipt_locator` naming a ticket dispatch never issued →
  `{"status": "REFUSED", "failure": "RECEIPT_NOT_DISPATCHED"}`, exit 2, no
  subscriptions file written. The CLI reads the receipt once through
  `WakeScopedDispatchBoundary.read_receipt`; a `NOT_FOUND`/`STALE_REVISION`/
  `CLOSED` read result is refused before `build_subscription` is ever called,
  so an unclaimable receipt can never reach it.
- `E13-R3` Five distinct malformed-input cells, each naming the failing
  section: missing inputs file, malformed JSON, an invalid `receipt_locator`,
  an invalid `inputs` section, and no path argument at all — all typed
  `{"status": "REFUSED", "failure": "INPUTS_FILE_INVALID", "section": ...}`
  (or `INPUTS_FILE_UNREADABLE` for the file-level misses), exit 2, no file
  written.
- `E13-R4` Same seeded receipt, no wake command declared in the test layout →
  `WAKE_CAPABILITY_UNAVAILABLE`, exit 2, no file written. The wake proof is
  produced by `build_subscription`'s own probe; the CLI never sees or forwards
  a capability value from the inputs file.
- `E13-R5` `RunnerSubscribeIsolationTests`: `runner_cli` holds none of
  `LiveDispatchMetadataStore`, `LiveDispatchMetadataBoundary`,
  `JohnnyMetadataRoot`, `IssuanceScopedDispatchBoundary`,
  `TicketReceiptIssueRequest`, `ApprovedDispatchArtifactRegisterRequest`,
  `admit_dispatch`, `create_dispatch_grant`, `issue_receipt` or
  `register_artifact`; its source never mentions
  `live_dispatch_metadata_store`, `issuance_scoped_boundary` or
  `dispatch_authority`. The runtime-binding cell captures the actual boundary
  object the subscribe path constructs and asserts `type(bound) is
  WakeScopedDispatchBoundary` with no `issue_receipt`/`register_artifact`
  attribute — the E8-style pin, not a comment.
- `E13-R6` `mypy --strict` clean over `runner_cli.py` and
  `tests/test_event_runner_cli.py`; full suite `946 passed, 11 skipped,
  2713 subtests passed`; zero residue (`tests/.johnny-runtime` absent,
  `git status` clean beyond the two authorized source files).

CLI smoke through `johnny_live_cli.run_live_cli(("runner", "subscribe",
"<inputs.json>"), johnny_root)`: a dispatched receipt yields
`{"status": "WRITTEN"}` exit 0 and a round-tripping subscriptions file; the
same inputs with the `ticket_reference` changed to one never dispatched
yields `{"status": "REFUSED", "failure": "RECEIPT_NOT_DISPATCHED"}` exit 2.

The fix: `SubscriptionInputs` and `TicketReceiptReadRequest` are validated
through `model_validate_json` on each section's re-serialized JSON, not
`model_validate` on the parsed `dict` — both models are `strict=True`, and
pydantic's Python-object strict mode rejects a plain `str` for
`supervision_class` where its JSON mode accepts and coerces it. Using
`model_validate_json` keeps the CLI's validation identical to every other
JSON-file entry point in this codebase (`dispatch_cli.py`'s `issue`
subcommand) without duplicating `SubscriptionInputs`' own logic.
