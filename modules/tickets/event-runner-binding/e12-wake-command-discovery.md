# E12 — Antigravity Wake Command with Session Discovery

| Field | Value |
| --- | --- |
| State | `OPEN` — awaiting named implementation owner (Antigravity/Gemini) |
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
