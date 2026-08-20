# E11 — Can a Wake Command Actually Start an Agent? (Phase B)

| Field | Value |
| --- | --- |
| Origin | Owner directive 2026-08-19: before investing in dispatch authority (phase C), prove or refute the one assumption everything downstream rests on |
| State | `CLOSED` — **the assumption holds**: a real agent was woken by a host command and acted on the payload |
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

- `claude` CLI: **present but not on `PATH`** — corrected 2026-08-20. The
  original entry said "absent", which was a PATH lookup mistaken for an
  inventory. It lives at
  `%APPDATA%\Claude\claude-code\<version>\claude.exe` (versioned directory,
  so any hardcoded path ages out). This does not change E11's conclusion —
  the wake channel was proven through Antigravity — but it does mean this
  host has a second automatable agent CLI that the inventory wrote off.
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

## Result (2026-08-19, control-plane executed): PROVEN

A real Antigravity agent was woken through `agentapi send-message` into an
existing conversation and, within the bounded window, **read the payload file
and wrote the ack file** whose content — `receipt_id=receipt-e11-test-001` —
could only have come from the payload. `send-message` returned exit 0
(`HOST_ACCEPTED` semantics under `CommandRoleWakePort`).

This settles phase B affirmatively: the wake channel is not just command
execution, it demonstrably starts an agent acting on the delivered payload.
The mode that works is precisely the contract's native one — waking an
**existing named task** (`reviewer_task_id` = the conversation id), not
creating a new one.

## Operational constraints discovered (all recorded for the composition work)

1. **Session-dynamic address and token.** The `agentapi` client needs
   `ANTIGRAVITY_LS_ADDRESS` and `ANTIGRAVITY_CSRF_TOKEN`; both change on every
   IDE launch and are discoverable from the running
   `language_server_windows_x64.exe` command line (`--csrf_token`) and its
   listening ports. A production wake command therefore needs a small
   discovery wrapper as its executable, or a runner started with the values
   injected. The capability probe honestly fails when the IDE is not running.
2. **`new-conversation` is not usable from outside.** Every reachable IDE
   language server rejects it: the client always sends a `project_env_config`,
   and with `ANTIGRAVITY_PROJECT_ID` set the server answers
   `projectsStore is nil`. Waking an existing conversation via `send-message`
   is the working path — and the better one for the contract.
3. **The probe sends a real message.** `probe_wake_capability` runs the actual
   declared command, so with this channel the probe deposits its disposable
   probe payload into the reviewer conversation. Acceptable (the payload is
   labeled), but worth a probe-aware wrapper message.
4. **Host inventory.** No `codex` CLI exists on this machine. The `claude`
   CLI does exist but is not on `PATH` (see the corrected entry above), so
   Antigravity was the channel proven here, not the only possible one.

## What this unlocks

Phase C (dispatch authority at the workstation process boundary) and phase D
(reviewer return path) now rest on a proven foundation: commit → watcher →
adapter → durable claim → host command → **agent acting**. Every link has
direct evidence.
