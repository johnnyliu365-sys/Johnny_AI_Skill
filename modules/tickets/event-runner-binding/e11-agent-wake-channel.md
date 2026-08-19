# E11 — Can a Wake Command Actually Start an Agent? (Phase B)

| Field | Value |
| --- | --- |
| Origin | Owner directive 2026-08-19: before investing in dispatch authority (phase C), prove or refute the one assumption everything downstream rests on |
| State | `OPEN` — experiment in progress |
| Baseline | `main` = `1e6c22c` |
| Workload | `SMALL` investigation; the deliverable is evidence, not code |

## The assumption under test

The whole automation line assumes an owner can declare a host command that,
when the runner fires it with a payload file, causes a real agent task to
start, read that payload, and act. E6 proved the command is *executed* and
the payload is *delivered to it* — it never proved any command exists whose
execution *is an agent starting work*. If no such command exists on any
platform, phases C and D build on nothing.

## Host inventory (2026-08-19, this machine)

- `claude` CLI: **absent** (desktop app only, no PATH-exposed CLI)
- `codex` CLI: **absent**
- Antigravity `agentapi`: **present** at
  `~/.gemini/antigravity[-ide]/bin/agentapi.bat`, backed by
  `language_server_windows_x64.exe agentapi`, with
  `new-conversation [--model=...] [--title=...] <prompt>` and
  `get-conversation-metadata <id>` — a real command-line conversation starter
  for the platform the owner actually dispatches implementers on.

## Success condition

Through the real `CommandRoleWakePort` (not a bare subprocess), with a real
`ROLE_WAKE_V1` payload: the declared command returns `HOST_ACCEPTED`, and a
real agent conversation demonstrably starts and acts on the payload (the act
must be observable outside the conversation, e.g. a file the agent writes
whose content could only come from the payload).

Budget: minimal model (`flash_lite` if available), one conversation, one
attempt. A refusal or an inert conversation is a valid experimental result
and is recorded as such.
