# 04 — The Skill Narrates Wakes That Nothing Performs

| Field | Value |
| --- | --- |
| State | `OPEN` |
| Severity | `P0` — it manufactures false completion narratives, the failure mode this whole project exists to prevent |
| Found | 2026-08-20 by the owner, watching an agent report a wake that never happened |
| Baseline | `main` = `36ede46` |

## What happened

An agent working a real project (`SourceProjectA-code-review`) reported:

> `3338fdc` 不只是交付證據，也是 `ImplementationReturn` 的 commit 喚醒訊號。
> Router 應依此把案件喚醒並交給 `SUPERVISOR_REVIEWER`

The owner's response: **根本沒有喚醒阿.**

Verified: `%LOCALAPPDATA%\JohnnyRouter` does not exist on that machine, the
target project holds no subscription or wake-capability configuration, and no
runner is armed for it. **Nothing existed that could wake anything.**

## The defect

The skill states wake behavior in the indicative mood throughout:

- `context-routing.md`: "The Router wakes the architecture owner"
- `model-role-routing.md`: "this wakes the architecture owner", and a whole
  section titled "Mandatory wake triggers"
- `ticket-decomposition.md`: "Both routes wake the architecture owner"

An agent reads those as descriptions of a running system. They are not: they
describe a **protocol**. The mechanism that performs it is the installed
runtime, armed per project through `dispatch issue` → `runner subscribe` →
`runner start` with a declared wake capability. With none of that present,
every sentence above is still true as protocol and false as behavior.

The skill never says which it is, so a competent agent following it faithfully
will narrate wakes that did not occur — and will hand the owner a completion
story with a hole in it. This project's entire discipline is that a claim must
be backed by an effect that actually happened; the skill violates it in its
own text.

## Why this outranks a wording fix

The same defect class was found twice before in the plugin's own artifacts
(`PITFALL-REGISTER` D5: documentation describing an entry point that never
existed; the bare `johnny-router uninstall`). This instance is worse because
the reader is an *agent*, and its output is *sent to the owner as fact*.

## Design

1. Every wake sentence in the skill states its condition: the runtime must be
   installed and armed for this project, or there is no wake. Preferred
   phrasing is conditional and mechanism-naming — "an armed runner wakes …",
   not "the Router wakes …".
2. The skill gains an explicit readiness section: how an agent determines
   whether automation is live for the project it is in (root present,
   subscription present, runner running, wake capability proven), and what to
   say when it is not — that the handoff is committed and **the reviewer must
   be notified by the owner**, rather than implying a wake happened.
3. An agent must never report a wake it did not observe. Committing a handoff
   leaf is evidence of a commit, not of a delivery.

## Authorized implementation scope

```text
skills/johnny-project-takeover/SKILL.md
skills/johnny-project-takeover/references/context-routing.md
skills/johnny-project-takeover/references/model-role-routing.md
skills/johnny-project-takeover/references/ticket-decomposition.md
skills/johnny-project-takeover/references/router-control.md
modules/tickets/workflow-governance/
modules/tickets/PITFALL-REGISTER.md
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `04-R1` | No wake sentence in the skill or its references asserts a wake unconditionally; each names the mechanism and its precondition. Verified by grep over the changed files. |
| `04-R2` | The readiness section states the four observable conditions and the exact honest wording for the not-armed case. |
| `04-R3` | The skill states that a wake may only be reported when observed, and that a committed handoff is not a delivery. |
| `04-R4` | `skills/` is a payload root: the bundle digest changes, so this ships in the next release rather than silently diverging from the released artifact. Recorded, not worked around. |
