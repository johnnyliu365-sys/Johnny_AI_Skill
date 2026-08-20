# E14 — Claude Branch Wake Command

| Field | Value |
| --- | --- |
| State | `CLOSED` — the dispatcher ships and the live drive is evidenced end to end on the owner's host |
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
  model call. It is a cheap *necessary* condition -- and only that, per the
  next point.
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
| E14-R9 | A conversation held by a live session is refused, and an unreadable inventory refuses too | `LiveSessionGuardTests`; verified live below |
| E14-R10 | A conversation an app tab wraps is refused even with no process alive | `AppTabClaimTests`; verified live below |
| E14-R7 | Tests discriminate | Reverse mutation run: routing→always-first turned 6 cells red; dropping the probe marker check turned R6 red; both restored green |

All cells drive the real subprocess path through a stub CLI that records the
exact argv, rather than patching module internals — a mocked runner cannot
catch the command shape drifting away from what the CLI accepts.

## E14-R8 closed — the live drive, measured

Run on the owner's host against CLI `2.1.234`, authenticated with an
`sk-ant-oat01-` token from `claude setup-token` (108 characters), supplied
through `CLAUDE_CODE_OAUTH_TOKEN`.

1. **The capability probe passes for real.** The dispatcher's probe path
   returned `{"status": "CAPABILITY_PROVEN"}`, exit 0, in **5.2 s** — inside
   the runtime's 30-second cap with room to spare, which is what the deadline
   budget was added for.
2. **Branches are distinct and durable.** Two fresh session ids were opened
   with `--session-id`, one told `ALPHA-7731` and the other `BRAVO-4402`.
   Resumed separately with `--resume`, each returned **its own** token and
   neither carried the other's. Parallel Claude branches are therefore real,
   isolated, and survive process exit — not one invocation that happened to
   work.
3. **A named reviewer's branch really receives the wake.** A route table
   mapping `supervisor-reviewer` to branch A, plus a `ROLE_WAKE_V1` payload
   naming that reviewer, produced `{"status": "DELIVERED"}` in 8.7 s. Asked
   from *inside* branch A afterwards, the branch named the payload path it had
   been handed, and still answered `ALPHA-7731` when asked what it had been
   told earlier. So the wake landed in the reviewer's own branch and continued
   it, rather than opening a fresh one.

Point 3 is the evidence that matters, and it is the E11-equivalent for this
host: the delivery was confirmed from the receiving side, not from the
sender's own return value. A `DELIVERED` status is a claim about a command;
the branch naming the payload is a fact about what arrived.

## The tab the owner is watching — measured, then forbidden

The owner asked whether they would see their own tab move. Measured on a
disposable empty workspace the owner opened for the test:

- `claude agents --json` reports the real session id behind an app tab
  (`07199111-…`), so the Router can in fact find open tabs. The earlier
  statement that this was structurally impossible was too strong: there is no
  *injection* interface, but the id needed to resume the same conversation is
  right there.
- Driving that id with `claude -p --resume` **succeeded**: exit 0 in 4 s, and
  that conversation's own transcript grew from 31 lines / 41,042 bytes to 41
  lines / 49,516 bytes. No second file was created. The turn landed inside the
  tab's conversation.
- The app rendered **nothing**. The owner watched the tab throughout and
  reported no change of any kind, and the app's registry still timestamped
  that conversation 76 seconds *before* the write it had just received.

So an external drive of an open tab produces work the owner cannot see, while
the app goes on holding an in-memory history that no longer matches the file:
two writers over one transcript. Being able to do this is not a reason to
offer it.

**E14-R9.** `live_session_ids` reads the inventory before every delivery, and
a wake whose target is held is refused as `BRANCH_HELD_BY_LIVE_SESSION`. An
inventory that cannot be read refuses as well
(`LIVE_SESSION_CHECK_FAILED`) — not knowing is not the same as knowing the
branch is free, and the fail-open version of this guard would be worth
nothing. Verified live against the same tab:
`{"code": "BRANCH_HELD_BY_LIVE_SESSION", "status": "REFUSED"}` with the
transcript byte count identical before and after, so the refusal prevented
the write rather than merely reporting one.

**E14-R10 — process liveness is not the right question.** The owner reported
that the tab they had *not* touched left the live inventory anyway, and a
later check found its process back again. A process behind a tab comes and
goes; the tab stays open on screen throughout. So `live_session_ids` alone
would have called that conversation free and written into it invisibly during
every gap.

The desktop app records one JSON file per session under
`%APPDATA%\Claude\claude-code-sessions\**\local_*.json`, and each record
carries the app's own `sessionId` *and* the `cliSessionId` it wraps. The claim
therefore outlives the process and is readable from disk.
`app_claimed_session_ids` reads it before every delivery and refuses as
`BRANCH_HELD_BY_APP_TAB`. A record that will not parse, or a missing store
sitting beside an installed app, refuses as `APP_CLAIM_CHECK_FAILED` — the
record that cannot be read may be the one that mattered. Verified live: the
dispatcher returned `BRANCH_HELD_BY_APP_TAB` against the owner's real registry
with the transcript byte count unchanged.

This guard reads state the app owns and does not document. That is accepted
deliberately, because the failure mode is safe in one direction only: if the
format moves, the read fails and the wake is **refused**, never silently
allowed. A guard that fails open would not be worth having.

### What this does *not* license

The woken branch was asked what it received; it was not observed carrying out
a review and submitting a verdict. That last mile stays unproven here exactly
as it does for the Antigravity channel. And nothing in this result changes the
negative above: no interface delivers into a conversation the owner is sitting
in. The Router drives branches it owns.

## 狀態宣告

這個區塊是工單狀態頁唯一讀取的來源。改狀態就改這裡；不要期待任何工具去讀上面的英文句子。

```johnny-status
id = E14
title = Claude 分支喚醒命令
state = APPROVED
commit = da33781
released_in = v0.4.5
stage = R1 | 探索 | DONE
stage = R2 | 認證閘門 | DONE
stage = R3 | 分支路由 | DONE
stage = R4 | 具名拒絕 | DONE
stage = R5 | 訊息只帶路徑 | DONE
stage = R6 | probe 誠實性 | DONE
stage = R7 | 突變鑑別力 | DONE
stage = R8 | 實機驅動 | DONE
stage = R9 | 現役行程守衛 | DONE
stage = R10 | app 分頁守衛 | DONE
```
