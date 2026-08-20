# V1 — Owner Status Surface

| Field | Value |
| --- | --- |
| State | `PARTIALLY CLOSED` — R1 approved by the owner; R2/R3 landed; R4 open |
| Baseline | `main` at `da33781` (E14 closed) |
| Workload | `STANDARD`; Python 3.11 strict for the generator, TDD, reverse mutation required. The mockup phase is HTML/CSS only |
| Depends on | E14 (closed): the wake channel exists and is invisible; this ticket makes it observable |
| Gate | R1 approved. The owner then reassigned implementation to the control plane directly, so the boundary note at the foot of this ticket no longer describes who built it. |

## One outcome

Without opening a terminal or reading a JSONL file, the owner can see which
workers are running, what is waiting on their decision, and what has finished.

Two deliverables, in order:

1. **A static mockup** for the owner to react to. No generator, no data
   plumbing — one self-contained HTML file with realistic content, so the owner
   can say "yes, that's what I want to look at" or redirect before anyone
   writes the machinery.
2. **The generator**, after the owner approves the mockup: a stdlib-only Python
   module that rewrites that page from real Johnny-root state at the moment
   state changes.

## Facts already established — do not rediscover

Measured on the owner's Windows host; the evidence is in
`modules/tickets/event-runner-binding/e14-claude-branch-wake-command.md`.

- **The desktop app cannot be the surface.** Driving the conversation behind an
  open tab lands in the transcript but renders nothing (the owner watched it;
  the app's registry timestamp stayed 76 seconds behind the write it had just
  received). `claude --bg` background agents are tracked by
  `claude agents --json` but the app displays nothing for them. And a CLI
  session has no MCP servers (`claude mcp list` → none), so a Router-driven
  worker cannot call the app's own session-message channel either.
- **A Windows toast renders on this host** via the WinRT
  `ToastNotificationManager` from PowerShell, with no extra module installed.
  The owner saw it. The owner also ruled it insufficient on its own: it shows
  once, then it is gone, and it cannot carry standing state.
- **`TOAST_SENT` is not proof a human saw anything.** It means the API accepted
  the call. Focus Assist swallows toasts silently. Treat this exactly like
  `auth status` claiming `loggedIn: true` for a token the server then rejects
  with 401 — the API's own success value is not the capability.

## R1 — the static mockup (do this first, then stop)

One self-contained HTML file, no build step, no external requests other than a
Google Fonts stylesheet if you want one. Realistic content throughout — no
lorem, no `TODO`, no obviously fake `foo`/`bar`. Use the project's real
vocabulary: `reviewer_ref`, `project_id`, `ticket_reference`, `receipt_id`,
`attempt_id`, and the real status names listed below.

Three lanes, in priority order — **what needs the owner comes first**, because
that is the entire reason this page exists:

| Lane | Contents |
| --- | --- |
| Waiting on you | Items the Router refused or cannot progress without a human. Each row needs: why it stopped (typed code), which project and ticket, how long it has waited, and what the owner is supposed to do about it |
| Working | Branches the Router is currently driving: reviewer, project, ticket, what it was woken for, when it started |
| Done | Verdicts that completed: `APPROVAL_GRANTED` / `APPROVAL_DENIED`, project, ticket, when |

The "Waiting on you" rows must be able to represent at least these real refusal
codes, because each one implies a different owner action and the page is
worthless if they all look alike:

- `BRANCH_HELD_BY_APP_TAB` — the owner has that conversation open in the app;
  the Router refused rather than write into it invisibly. Owner action: close
  the tab, or handle the item themselves.
- `REVIEWER_NOT_MAPPED` — no route from that reviewer to a branch. Owner
  action: add the route.
- `NOT_AUTHENTICATED` / `DRIVE_FAILED` — the host cannot drive. Owner action:
  re-authenticate.
- `CANDIDATE_INBOX` — no wake capability was proven for this project, so the
  item was recorded and nobody was woken. Owner action: relay it.

Design constraints for the mockup:

- It is an operations surface, scanned and not read. State must be legible at a
  glance from form, not only from text — the owner should be able to tell a
  blocked item from a running one without reading a word.
- Both light and dark must be handled properly, including the "system" state
  where the host stamps no theme attribute at all.
- Wide rows scroll inside their own container; the page body never scrolls
  sideways.
- Timestamps are for a person deciding what is stale: relative age is what
  matters, with the absolute time available.
- **No decorative dashboard furniture.** No fake sparkline that charts nothing,
  no vanity totals, no gauge without units. Every element on the page must
  correspond to something the generator can actually produce from the state
  listed in R3.

Hand the file to the owner and **stop there**. Do not start R2 or later until
the owner has responded.

## R2 — the generator

Only after R1 is approved.

A stdlib-only module, `library/local_orchestration/owner_status_surface.py`,
that renders the approved page from real state and writes it atomically
(temp file plus `os.replace`, the pattern already used by
`event_runner._write_state`) to a path derived from `JohnnyRootLayout`, never
configured.

Hard constraints:

- **Stdlib only.** The runtime venv is hash-locked; adding a dependency is out
  of scope for this ticket and will be rejected.
- **No polling, no heartbeat, no timer, no port.** The page is rewritten when
  state changes, by whatever already handles that change. The browser's own
  refresh is the only repetition allowed.
- **Never writes into a target project.** Per-user Johnny root only.
- **Reads, never mutates, the state it displays.** This surface has no
  authority; it must not claim, settle, or consume anything.

## R3 — the state it renders

Read through the existing accessors rather than hardcoding filenames; confirm
each one in the code before use, and do not invent a source that is not already
written by something:

- runner status — `event_runner.runner_state_path`
- armed subscriptions — `event_runner.subscriptions_path`
- items nobody was woken for — `wake_candidate_inbox.read_candidates`
- review returns awaiting consumption — the `review_return` /
  `review_return_consumption` pair
- dispatch history — the dispatch journal written by `dispatch_authority`
- wake attempt outcomes, including refusals — the role-wake attempt store

If a source is unreadable, the page says so **in place of that lane**. It must
never render an empty lane that looks like "nothing is waiting" when the truth
is "this could not be read" — that failure would defeat the entire purpose of
the surface.

## R4 — notification, kept in its place

The toast is a pointer, not the record.

1. The durable record is written **first**. Only then is a toast attempted.
2. Toast capability is **probed, never asserted**, following
   `wake_capability.probe_wake_capability`: an owner-visible claim that
   notification works must rest on the notification path having actually run.
   A return value of `TOAST_SENT` does not qualify on its own — decide what
   does, and write down why it discriminates.
3. A failed or swallowed toast changes nothing about the item's state. It is
   still on the page, still in the file.
4. One toast per item. No repeats, no nagging, no digest timer (that would be
   polling).

## Acceptance

| Ref | Requirement | Evidence required |
| --- | --- | --- |
| V1-R1 | Static mockup delivered and owner-approved | Owner's response recorded in this ticket |
| V1-R2 | Generator writes the page atomically under the Johnny root, stdlib only | Test asserting no partial file is ever observable, and an import-surface test proving no third-party import |
| V1-R3 | An unreadable source renders as "unreadable", never as an empty lane | Test with a corrupted source asserting the lane says so; reverse mutation (swallow the error, render empty) must turn it red |
| V1-R4 | Every refusal code that needs an owner action reaches the page with its own action text | Test per code listed in R1 |
| V1-R5 | The durable record precedes the toast, and a failed toast leaves the item intact | Test with a failing toast path asserting the record exists and the item still renders |
| V1-R6 | Nothing on the page is decorative | Review: each element traces to a field in R3 |
| V1-R7 | Tests discriminate | Reverse mutation for at least R3 and R5, both restored green |

## Delivery log

**R1 — approved.** The mockup landed as `v1-owner-status-surface.html` and the
owner approved the direction. Three ticket requirements were missing from it
and were implemented in R2 rather than carried forward: the four refusal codes
shared one chip style, no row said what the owner should do, and there was no
unreadable-source state. The mockup also came back in English rather than the
Traditional Chinese the dispatch asked for.

**R2/R3 — landed.** `library/local_orchestration/owner_status_surface.py`,
stdlib-only, renders and writes atomically to `<johnny-root>/owner-status.html`
and refreshes itself in the browser every 30 seconds. Every source is read
independently, so one failure marks its own lane and never silences a peer. A
missing file is reported as genuinely empty; a file that will not parse is
reported as unreadable with its path and the parse error, and the lane carries
a `不完整` flag while the page header says the page is incomplete. Reverse
mutation confirms the suite discriminates: rendering the reassuring empty
message under an unreadable lane turns one cell red, and swallowing a source
error turns two red; both restored green. 17 cells, 19 subtests.

**R4 — open, and blocked on a missing record.** `CommandRoleWakePort` runs the
wake command with `capture_output=True` and then **discards stdout**: on a
non-zero exit it returns `NO_EFFECT` carrying no reason. So the dispatcher's
typed refusal codes — `BRANCH_HELD_BY_APP_TAB`, `REVIEWER_NOT_MAPPED`,
`NOT_AUTHENTICATED` — are written to a pipe nobody reads and exist nowhere on
disk. The surface already knows how to present all of them, and the owner
action text for each is written and tested, but today only `CANDIDATE_INBOX`
and `RUNNER_NOT_RUNNING` can actually reach the page from real state.

Closing R4 means making the reason durable: record the child's typed code as an
observation next to the attempt, without letting it influence any control
decision — the port's typed effect statuses must keep coming from the exit
code and timeout behaviour alone, never from something a child process printed.

## Boundary for the implementation owner

This ticket is written by the control plane, which does not implement. The
implementation owner owns every design and code decision inside these
constraints, and owns saying so if a constraint here is wrong — argue it in the
ticket rather than working around it silently.

Two rules this project has been burned by often enough to state plainly:

- **Do not report a state you did not observe.** The page may only show what a
  source actually said. A lane that guesses is worse than no page — see
  `modules/tickets/workflow-governance/04-skill-implies-a-runtime-that-may-not-exist.md`,
  where narrating an unperformed wake is exactly the defect that cost the owner
  their trust in this system.
- **Read `modules/tickets/PITFALL-REGISTER.md` before starting.** Most "new"
  problems on this project are a repeat of a family already recorded there,
  including the false-green family this ticket's R3 and R4 exist to avoid.
