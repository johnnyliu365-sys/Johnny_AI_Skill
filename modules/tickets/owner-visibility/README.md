# Owner visibility ticket registry

| Field | Binding |
| --- | --- |
| SPEC / AC | Derived from `receipt-bound-role-supervision` — supervision that the owner cannot observe is not supervision |
| Baseline | E14 closed at `da33781`; the Claude branch wake channel works and is invisible to the owner |
| Authority | Owner-direct allocation; the owner named this gap and required a surface they can actually see |
| Workload | `external_effects=LOCAL_HOST`, `uncertainty=KNOWN_DOMAIN`, `recovery=RECOVERABLE` → derived `STANDARD` |
| Boundary | Per-user Johnny root only; no polling, no heartbeat, no service listening on a port; the surface is written at the moment state changes and read by the owner's browser. Nothing here may write into a target project. |

## Why this line exists

The Router can drive Claude branches (E14). The owner cannot see any of it. Three
separate routes into the desktop app were measured on the owner's host and all
three are closed:

| Route | Result | How it was established |
| --- | --- | --- |
| Drive the conversation behind an open tab | The turn lands in the transcript; the app renders nothing and its registry timestamp stays 76 s behind the write | The owner watched the tab and reported no change; transcript grew 31 → 41 lines |
| Start work as a background agent (`claude --bg`) | Tracked by `claude agents --json` as `kind=background`; the app shows nothing | The owner looked and reported nothing in the app |
| Have the worker call the app's own session-message channel | Not available: a CLI session has no MCP servers configured | `claude mcp list` → "No MCP servers configured" |

So the visible surface has to live outside the app. A Windows toast was proven
to render on this host, but the owner's verdict on it is recorded and binding:
**a toast alone is too unfriendly for a general user** — it appears once and is
gone, and it cannot show standing state.

## Honest capability model

The file is the evidence; the toast is only a pointer. Focus Assist silently
swallows toasts, and `TOAST_SENT` from the notification API means the API
accepted the call, **not** that a human saw it — the same false-green shape as
`auth status` reporting `loggedIn: true` for a token the server rejects
(`PITFALL-REGISTER.md` family C). Nothing may report an owner as notified on
the strength of a toast return value. Every notification writes its durable
record first; a swallowed toast then costs latency, never the item.

| # | Ticket | Sole closure | State |
| --- | --- | --- | --- |
| V1 | Owner status surface | The owner sees, at a glance and without opening a terminal, which workers are running, what is waiting on their decision, and what finished | `OPEN` — see [`v1-owner-status-surface.md`](v1-owner-status-surface.md) |
