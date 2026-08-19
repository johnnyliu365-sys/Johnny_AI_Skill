# E12 — Antigravity Wake Command with Session Discovery

| Field | Value |
| --- | --- |
| State | `CLOSED` — control-plane executed after the dispatched lane produced nothing |
| Baseline | `main` at the commit this ticket lands in |
| Workload | `SMALL`; Python 3.11 strict, TDD, no baseline-red required (new capability, not a bugfix) |
| Depends on | E11 (closed): the channel is proven; this ticket makes it declarable |

## One outcome

An owner can declare a wake command that reliably wakes the named reviewer
conversation on this host, even though the Antigravity language-server address
and CSRF token change on every IDE launch. Deliverable: one module,
`library/local_orchestration/antigravity_wake_command.py`, runnable as

```text
py -3.11 -m library.local_orchestration.antigravity_wake_command --conversation <uuid> {payload_file}
```

which becomes the owner's `WakeCommandConfig.command` vector.

## Facts already established by E11 — do not rediscover

- `agentapi.bat` lives at `~/.gemini/antigravity-ide/bin/agentapi.bat` and
  forwards to `language_server_windows_x64.exe agentapi %*`.
- The client requires environment variables `ANTIGRAVITY_LS_ADDRESS`
  (`127.0.0.1:<port>`) and `ANTIGRAVITY_CSRF_TOKEN`. Both are per-IDE-launch
  dynamic.
- Discovery that works: enumerate `language_server_windows_x64.exe`
  processes; each command line carries `--csrf_token <uuid>`; its listening
  ports come from TCP listeners owned by that pid. The correct (port, token)
  pair is the one where `agentapi get-conversation-metadata <fake-id>`
  answers `trajectory not found` (authenticated service). Wrong port resets
  the connection; right port with missing token answers `missing CSRF token`.
- `send-message --title=<t> <conversation_id> <content>` exits 0 on success
  and demonstrably wakes the conversation's agent (E11: the woken agent read
  the payload file and wrote the ack).
- `new-conversation` is **not usable** from outside: every IDE language
  server rejects it (`projectsStore is nil`). Do not build on it.
- Antigravity conversation ids are UUIDs — the same shape as the contract's
  `CodexTaskId`, so `reviewer_task_id` carries the conversation id naturally.

## Frozen responsibility

- The module discovers (address, token) at invocation time; nothing is
  hardcoded or cached across runs. No IDE running, no authenticated server
  found, or `send-message` failing are finite nonzero exits with one typed
  JSON line on stdout — `CommandRoleWakePort` treats nonzero as `NO_EFFECT`,
  which is the honest outcome.
- Exit 0 exactly when one `send-message` succeeded. Never send twice; the
  port owns retry semantics (it never retries, by design).
- The message content is labeled as a Johnny wake, names the payload file
  path, and instructs the reviewer to read it. It must not paste the payload
  body into the message (identifiers-only discipline lives in the payload
  file).
- Discovery must not kill, restart, or reconfigure any process. Read-only
  process and socket enumeration only.
- Tests use a fake `agentapi` (a recording script standing in for the real
  one); no real conversation, no quota. One module-level seam (e.g. the
  agentapi executable path as an argument or parameter with the real default)
  makes that possible — the seam must default to the real binary.

## Authorized implementation scope

```text
library/local_orchestration/antigravity_wake_command.py
tests/test_antigravity_wake_command.py
modules/tickets/event-runner-binding/README.md   # E12 row update only
modules/tickets/event-runner-binding/e12-wake-command-discovery.md
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `E12-R1` | Discovery selects the authenticated (port, token) pair from process/socket enumeration alone; with no language server running the module exits nonzero with a typed `NO_LANGUAGE_SERVER` line and sends nothing. |
| `E12-R2` | With a fake agentapi: exactly one send-message invocation, correct conversation id and payload path in the arguments, exit 0. A failing fake (nonzero) yields a typed nonzero exit. |
| `E12-R3` | The module invoked through a real `WakeCommandConfig` + `CommandRoleWakePort` (with the fake agentapi) returns `HOST_ACCEPTED`; with the failing fake, `NO_EFFECT`. |
| `E12-R4` | The `{payload_file}` placeholder contract holds: the config vector carries it in exactly one argument and the port's substitution reaches the module unchanged. |
| `E12-R5` | `mypy --strict` clean; full suite green; `tests/.johnny-runtime` zero residue. |

## Environment facts

- Python is `py -3.11` (no `python`, no `pwsh`; Windows PowerShell 5.1).
- Console codepage is cp950: decode subprocess output as bytes/UTF-8, never
  `text=True`.
- Working copies are CRLF; mutation and edit scripts must normalize `\r\n`.
- Worktree location is governed: create yours at `.worktrees/e12-wake-command`
  under the repository root, never as a sibling folder.

## Closure evidence (2026-08-19, control-plane executed)

The dispatched worktree stood at the ticket baseline for twenty minutes with
no commits, no working-tree changes and neither target file created, so the
owner reassigned the ticket to the control plane. Nothing was overwritten.

- `E12-R1` The probe separates the authenticated endpoint from the rest: a
  wrong port fails, the right (address, token) pair succeeds, and discovery
  returns the first *proven* candidate out of a mixed pool. With no reachable
  server the module refuses `NO_LANGUAGE_SERVER` and sends nothing. A cell
  also pins that discovery only ever issues `get-conversation-metadata` — it
  is read-only by test, not by comment.
- `E12-R2` Exactly one `send-message`, carrying the conversation id and the
  payload path, with the environment variables the module is responsible for
  setting. A failing client is `SEND_FAILED`; an absent payload refuses before
  discovery runs; an absent client refuses first of all.
- `E12-R3` Declared as a real `WakeCommandConfig` and driven through
  `CommandRoleWakePort`: `HOST_ACCEPTED` on success, `NO_EFFECT` when the
  client fails.
- `E12-R4` The `{payload_file}` placeholder contract holds end to end — the
  port's substitution reaches the module and the attempt id appears in the
  delivered path.
- `E12-R5` `mypy --strict` clean; full suite `959 passed, 11 skipped`; zero
  runtime residue.

Reverse mutations, both discriminating: skipping the probe and returning the
first candidate turns two discovery cells red; pasting the payload body into
the message turns the identifiers-only cell red.

### Design note: the injected endpoint

`JOHNNY_ANTIGRAVITY_ENDPOINT` / `JOHNNY_ANTIGRAVITY_TOKEN` let an operator
supply the endpoint for the two cases discovery cannot serve — a
qualification driving the command deterministically, and a runner started as
a service by whatever launched the IDE. This is not a bypass: an injected
endpoint is probed by exactly the same read before anything is sent, so a
stale value is refused rather than trusted.

### Not yet done

The owner still has to declare this command in `wake-capability.json` and
name the reviewer conversation id. Doing so makes `probe_wake_capability`
send its disposable probe payload into that conversation, which is the
honest cost of a probe that runs the real command — noted in E11 and
unchanged here.
