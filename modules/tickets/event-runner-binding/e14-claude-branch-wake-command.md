# E14 — Claude Branch Wake Command

| Field | Value |
| --- | --- |
| State | `PARTIALLY CLOSED` — the dispatcher ships and is proven against a stub; the live drive is gated on owner authentication |
| Baseline | `main` at the commit this ticket lands in |
| Workload | `MEDIUM`; Python 3.11 strict, TDD, reverse mutation required |
| Depends on | E12 (closed): establishes the wake-command contract this module implements for a second host |

## One outcome

The Router can drive Claude Code conversation branches, one branch per
reviewer, resolved per attempt. Deliverable:
`library/local_orchestration/claude_wake_command.py`, runnable as

```text
py -3.11 -m library.local_orchestration.claude_wake_command {payload_file}
```

which becomes the owner's `WakeCommandConfig.command` vector.

## What the host actually offers — measured, not assumed

Measured on the owner's Windows workstation against CLI `2.1.234`:

- The CLI installs off `PATH` at
  `%APPDATA%\Claude\claude-code\<version>\claude.exe`, one directory per
  version. Discovery must pick the highest version, not the first found.
- `claude -p` runs exactly one turn and exits. `--session-id <uuid>` opens a
  named branch, `--resume <id>` continues a stored one, `--fork-session`
  branches it. These are the primitives that make "different branches" real.
- `claude auth status` prints `{"loggedIn": …, "authMethod": …}` and needs no
  model call. It is the only honest source for whether a drive can succeed.
- **`claude auth status` does not validate the token.** It reports
  `{"loggedIn": true, "authMethod": "oauth_token"}` whenever a token is present
  in the environment, and the first real call can still fail
  `401 Invalid bearer token`. Measured on this host: status said logged in,
  the drive returned 401. An auth-status-only capability check would therefore
  report `PROVEN` on a host that cannot drive anything -- which is precisely
  why the probe requires a completed turn instead.
- The long-lived token issued by `claude setup-token` begins `sk-ant-oat01-`
  (the prefix is in the CLI binary). A stored value that does not carry that
  prefix is not the issued token; the browser step's authorization code is the
  value most easily mistaken for it.
- `claude agents --json` lists live sessions (pid, sessionId, cwd) and works
  **without** authentication. Enumeration is free; driving is not.
- `claude setup-token` issues a long-lived token, which is the correct
  credential for automation: an interactive OAuth session expires and cannot
  refresh headlessly, which is exactly how this host was found (`loggedIn:
  false`, `claude -p` → `OAuth session expired and could not be refreshed`).

### The negative result, established by reading the whole surface

**No interface delivers a turn into a conversation someone is already sitting
in.** Every top-level command was enumerated (`agents`, `auth`, `auto-mode`,
`doctor`, `gateway`, `import`, `install`, `mcp`, `plugin`, `project`,
`setup-token`, `ultrareview`, `update`); none injects input into a running
session, and `claude agents`' options are all defaults for *future* dispatched
sessions, not controls over live ones. The in-app session-message tool is
callable only by an agent already inside a session, and its own contract
excludes orchestrating background work.

So this channel is shaped differently from Antigravity's, and the difference
must never be blurred: Antigravity **wakes an existing conversation** (E11
proved a real agent read the payload and acted). Claude **drives a branch the
Router owns**. The owner's open window is not a wake target on this host.

## Design

Target resolution is per attempt, which is what makes the plural in
"different branches" true. The wake payload the Router renders is
identifiers-only `key=value` text carrying `reviewer_ref` and `project_id`
(`RoleWakeRequest.render_identifiers_only_payload`). The dispatcher reads
those two keys and resolves them through an owner-declared table at
`<johnny-root>/claude-branch-routes.json`:

```json
{
  "routes": [
    {
      "reviewer_ref": "supervisor-reviewer",
      "session_id": "11111111-1111-4111-8111-111111111111",
      "project_id": "SourceProjectA"
    }
  ]
}
```

A project-scoped route outranks a project-agnostic one. An unmapped reviewer
is refused by name as `REVIEWER_NOT_MAPPED`; it is never delivered to some
other branch, which is the failure that would be worst to have.

The message sent to the branch names the payload **path** and never its body,
following E12: identifiers stay in the file, not on a command line or in a
chat message.

## Probe honesty — the part most likely to rot

`probe_wake_capability` renders the declared command against a disposable
payload (`{"probe":true,…}`) that names no reviewer, and requires exit 0.
Exiting 0 on a payload the dispatcher cannot deliver would make `PROVEN` mean
"the dispatcher can read a file" — the false-green shape this project has
been bitten by repeatedly (see `PITFALL-REGISTER.md` family C). So the probe
path performs a **real end-to-end drive of a throwaway branch** and requires a
completed model turn (a marker in stdout) before reporting success. Exit code
alone is not accepted; the reverse mutation for this is in the suite.

Two limits are deliberate and are not to be papered over later:

1. The probe proves the host can drive *a* Claude branch. It does **not**
   prove the reviewer's own branch is reachable, because the probe payload
   names no reviewer. Route failures surface at wake time.
2. The probe drives a fresh `--session-id` where a real wake uses `--resume`.
   That is the single intentional difference between the probed invocation
   and the delivered one.

The probe also runs with a fast model, because `probe_wake_capability` caps
the probe at 30 seconds and a cold turn on a large model can exceed it. An
owner whose probe times out gets `PROBE_TIMEOUT` and the honest
`CANDIDATE_INBOX` fallback — never a claimed wake.

## Acceptance

| Ref | Requirement | Evidence |
| --- | --- | --- |
| E14-R1 | Discovery picks the highest installed CLI version; a non-version directory is ignored; an env override wins | `ExecutableDiscoveryTests` |
| E14-R2 | An unauthenticated host refuses before spending a turn | `AuthenticationGateTests` — asserts the only subprocess call was `auth status` |
| E14-R3 | Distinct reviewers reach distinct branches | `DeliveryTests.test_two_reviewers_reach_two_different_branches` — asserts the two recorded `--resume` ids differ |
| E14-R4 | An unmapped reviewer is refused, not misdelivered | `DeliveryTests.test_unmapped_reviewer_is_refused_by_name_not_delivered_elsewhere` — asserts zero drive calls |
| E14-R5 | The message names the payload path and not its body | same cell — asserts `receipt_id` and the action are absent from the message |
| E14-R6 | The probe requires a completed turn, not exit 0 | `ProbeHonestyTests.test_exit_zero_without_a_completed_turn_is_refused` |
| E14-R7 | Tests discriminate | Reverse mutation run: routing→always-first turned 6 cells red; dropping the probe marker check turned R6 red; both restored green |

All cells drive the real subprocess path through a stub CLI that records the
exact argv, rather than patching module internals — a mocked runner cannot
catch the command shape drifting away from what the CLI accepts.

## What remains open

**E14-R8 (open): the live drive.** No cell in this suite has driven a real
Claude branch, because the host's CLI reported `loggedIn: false` throughout
development. When the owner has run `claude setup-token` and
`claude auth status` reports logged in, the outstanding evidence is:

1. `probe_drive` against the real CLI returns `CAPABILITY_PROVEN` within the
   30-second probe cap. First live attempt: `DRIVE_FAILED` in 2.8s against a
   host whose `auth status` claimed `loggedIn: true` -- the stored token was
   not an `sk-ant-oat01-` token. The refusal was correct and is retained
   here as evidence that the probe discriminates.
2. Branch isolation end to end: open two branches with known session ids,
   plant a distinct token in each, resume each and confirm each returns its
   own — proving durable, non-contaminating parallel branches rather than one
   working invocation.
3. A real reviewer branch receives a wake and the woken agent acts on the
   payload, which is the E11-equivalent evidence for this host.

Until R8 is evidenced, this channel is implemented but unproven on any live
host, and nothing may report otherwise — the skill's Automation readiness
gate (governance 04) applies to it exactly as written.
