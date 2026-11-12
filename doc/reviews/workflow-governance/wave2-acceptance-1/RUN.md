# Wave-2 acceptance 1, part B: one ticket on a fixture project, finished by a fresh session

> **Superseded as evidence for criterion 1 by the clean rerun in [`rerun/RUN.md`](rerun/RUN.md) (2026-11-12).** This first run is kept as the record of what the rerun fixed.

This is the live run of ticket 61 part B. It took one ticket of a fixture target project from a requirement snapshot to a merge commit landed by `integrate.py`. The first session was ended on purpose mid-ticket, and a new session finished the ticket from the project's files alone.

The control plane (Claude Opus 5.5) conducted the run on 2026-11-07. The plugin tree in use was `cp/wave2-gates` at `b95b4acd` (tickets 50 to 60, 62 and 63 integrated) and later commits that changed no script.

## Fixture

The fixture was the git repository `C:/Temp/claude/jas61/fixture`. Its `origin` was the local bare repository `C:/Temp/claude/jas61/remote.git`. Both lived outside this repository and are removed after the run.

The control plane built the skeleton (`8e6ae01`):
- an `AGENTS.md` that sends a session to this plugin's `AGENTS.md`;
- a `CONTEXT.md`;
- `src/calc.py` with `add`, and its test;
- the requirement source `doc/requirements/sources/calc-rows.json`, with two rows: REQ-CALC-001 for `add` and REQ-CALC-002 for `subtract`;
- the ticket and receipt templates from `template/`;
- `doc/handoffs/2026/governance/integration.json`, filled from `integration.TEMPLATE.json`. Its spec and invariant commands run the fixture's pytest, and its CI-status command is a fixture script that answers `green`.

## Seats and timeline

The times below are UTC and come from `times.txt`. Every seat was a separate subagent session, with no transcript of any other.

| Seat | Model | Start, end | Role in the ticket |
| --- | --- | --- | --- |
| Seat 1 | Claude Sonnet 5.5 | 04:30:39, 04:32:00 | Took the snapshot, wrote the ticket and the dispatch, and made the implementation commit. Then it was ended on purpose |
| Seat 2 | Claude Sonnet 5.5 | 04:32:10, 04:34:34; resumed for two more rounds, last end 04:47:58 | A fresh session. It found the state from the files, wrote the receipt, made the correction, then ran `integrate.py` |
| Seat 3 | Claude Opus 5.5 | 04:34:50, 04:41:29; resumed once, end 04:47:01 | The independent reviewer, `seat:ticket-review/61b-review` |
| Control plane | Claude Opus 5.5 | throughout | Built the fixture. After the first review it wrote the ticket's revision02 and the correction dispatch. After the correction review it wrote the convergence disposition. At the end it set the ticket `INTEGRATED` |

### Instructions given

**Seat 1** was told:
- where the fixture is, and that its `AGENTS.md` leads to the plugin's governance;
- to take requirement REQ-CALC-002 through these steps: the snapshot, a ticket from the template, a dispatch checked by `dispatch_lint.py`, the ticket's state row, a commit on `main` that is pushed, and the implementation with tests in a worktree on `seat/calc-subtract`, committed there;
- then to stop.

It was told that the session is ended on purpose mid-ticket as part of an acceptance test. It was told to write no receipt, ask for no review, and leave no hand-over note, summary file or comment beyond what the plugin's rules require the project files to hold.

**Seat 2** was told only this:
- the fixture's path;
- that an earlier session was working on a ticket here and ended without any hand-over, and that it has no transcript and no summary;
- to continue the open work by the plugin's rules, find where it stands from the project's files alone, and stop when the work needs an independent review;
- to report, first, the files and git commands it read to decide where the work stood, in order, and what it concluded from each.

It was resumed twice. Each time it was told only that the review had come back and to continue from the files. On the last round it was also told to run `integrate.py` itself with a submitter id of its own, and to read the CI result back.

**Seat 3** was told the candidate and the branch, and to review the candidate as the plugin's `CodeReview.md` requires. It was told to write the record on the fixture's `main` with a `review-verdict` block, and not to run `integrate.py`.

## What happened

1. **Seat 1** made two commits:
   - `02ba789` on `main`, pushed: the snapshot `2026-11-07-v1.json`, the ticket `modules/tickets/calc/01-subtract.md`, and the dispatch `01-subtract.md` (`dispatch_lint.py` passed). The ticket's state row was `PLANNED` with `dispatch=sha256:443f120e…` and the receipt path.
   - `bd3e756` on `seat/calc-subtract`, not pushed: `subtract` and three tests.

   Then it stopped. `state_after_seat1.txt` is the repository as it left it: an unpushed seat branch, no receipt, no review, no queue branch.

2. **Seat 2** resumed from the files alone. Its first report listed what it read, in this order:
   - the fixture's `AGENTS.md`, `git status`, `git branch -a` and `git log --all --graph`, which showed the unpushed seat branch and its implementation commit;
   - `git ls-remote`, which showed that no receipt, review or queue branch existed;
   - the plugin's `AGENTS.md`;
   - the ticket, whose state row read `PLANNED` and whose close-out fields were unfilled;
   - the dispatch, the configuration, the snapshot, and the diff of `bd3e756`.

   It concluded that the implementation was done, and that the receipt, the close-out and the review were missing. It checked that the dispatch digest equals the state row and that `dispatch_lint.py` passes. It wrote the receipt (`evidence_gate.py`: `cells=4 defects=0` at `bd3e756`), committed it as `545adb3`, pushed the seat branch, and stopped for review.

3. **Seat 3's initial review** (`5a51205`) returned `CHANGES_REQUESTED` on `545adb3`. It found the implementation correct, but blocked approval on two ticket defects and three evidence defects:
   - F1, ticket: `contract_gate.py` is red, because no spec declares REQ-CALC-001 or 002.
   - F2, ticket: the ticket has no Profile, no XSS classification, no closure revision and no named reviewer.
   - F3, evidence: no strict type check.
   - F4, evidence: the receipt has no contract cell, no smoke command, no typed return and no statements.
   - F5, evidence: no case beyond 64 bits; the reviewer's wraparound mutation stayed green.
   - F6, the template gaps behind F2 and F4, went to the plugin.

4. **The control plane** wrote the ticket's revision02 and the correction dispatch `01-subtract-c1.md` on `main` (`285843e`).

5. **Seat 2, resumed and told only that the review was back**, found the review record and revision02 from the files. It then:
   - merged `main` into the seat branch (`007d1e7`);
   - bound both requirements in the test, read expected values from a ledger, and added the case beyond 64 bits (`b00b521`; `contract_gate.py` exit 0, `mypy --strict` clean);
   - wrote the receipt `01-subtract-c1.md` (`45fc387`; `evidence_gate.py`: `cells=8 defects=0` at `b00b521`).

6. **Seat 3's correction review** (`4c39170`) returned `CONVERGENCE_REVIEW_REQUIRED` on `45fc387`. F1 to F5 were closed except the smoke command line. The open findings G1 to G4 were evidence and hardening gaps on a correct candidate. The control plane recorded a convergence disposition, `APPROVED`, under CodeReview §5 rule B (`8d3ab40`).

7. **Seat 2, resumed again**, ran `integrate.py` with the fixture's configuration and submitter `seat:implementation-standard/61c-resume3`:
   - `submit`: exit 0, `QUEUED … parent=8d3ab40…`;
   - `land`: exit 0, `LANDED_PENDING_CI … landed_sha=ebb77083…`;
   - `readback`: exit 0, `LANDED_PENDING_CI -> LANDED`.

   `git-show-landed.txt` shows the landed commit. It is a merge commit with parents `8d3ab40` (the tip) and `45fc387` (the candidate). The queue entry on `main-queue` is `LANDED`.

8. **The control plane** set the ticket `INTEGRATED` (`7868360`).

## What this shows

- **The loop works end to end.** One ticket went from a requirement snapshot to a merge commit landed by the integration script, through dispatch, implementation, independent review, a correction and merge-queue integration. Its session was ended mid-ticket, and a fresh session finished it. Every handover between seats went through the ticket, the receipt, the review record and the queue, and never through a message.
- **The "files alone" part is weakened** (see "Evidence of the resume" below): the fresh session also read the plugin's ticket 61, which describes this run. A clean rerun points the fresh session at a plugin checkout that does not hold the acceptance ticket.
- **The gates caught real defects in a ticket written by an agent:**
  - the contract gate found that no requirement was bound;
  - review found missing ticket fields;
  - a counter-mutation found a missing boundary case.
- **What the plugin learns from the run.** None of these blocked the run.
  - The ticket and receipt templates lack Profile, XSS and closure-revision rows and a typed-return slot, and the ticket template cites a section of CodeReview.md that no longer exists (F6).
  - A receipt committed beside its candidate cannot name its own commit. The run used "cells at the implementation commit; candidate = the tip that adds only the receipt". The reviewer checked that the two differ only in receipt files. The rule is not written in the plugin.
  - The fixture's requirement source lacked fields the snapshot tool needs. Seat 1 made an uncommitted input file. That is a defect of the fixture the control plane built, not of the seat.
  - A seat set the ticket to `DONE` before review. Nothing in the templates says when `DONE` is set.

## Evidence of the resume (added after the revision01 review, owner decision "A", 2026-11-12)

The revision01 review (S61-05) asked for four things: the exact prompt of every seat round, seat 1's last tool call and its output, seat 2's first reads up to its conclusion, and the start and end of every round. The owner decided that the seat transcripts stay off the public repository. The record therefore holds them in two places:

- **In this directory:** `prompts.md`, every round's prompt copied verbatim from the transcript, with the round's start and end.
- **On the run host only, not committed:** unedited excerpts of each seat's transcript, made by the control plane. Each excerpt holds every round's prompt, the context the harness injected before the seat's first step, and seat 1's last tool call with its result. For seat 2's first round it holds every tool call and its result up to the first conclusion. The excerpts are under `C:/Temp/claude/jas61/run/transcripts/`:

| File | sha256 |
| --- | --- |
| `seat1.md` | `385ba20904876a07b4e3974ff01d953c80dae42f3f87e9ffe371e15e0e8c1ee7` |
| `seat2.md` | `53fcf067aac3c9d02aad03164002b770d6f80c5504f8cfd2361d38bee3492e99` |
| `seat3.md` | `21bac603099fe5f53a772255bb9bc6cd2f7da947241a9909c55e96f99e10eee6` |
| `rounds.txt` | `f05f37d4edcbc7b84dca8244c47efa03c77efdb27b58a3b3ad4a137fc513ba2b` |

What the excerpts show. The round times in `rounds.txt` replace the coarser times in `times.txt`.

- **Seat 1, last step:** a single `SubagentHandback`, at 04:31:54Z. Before it, the last commit is `bd3e756` in the worktree. Nothing was written afterwards.
- **Seat 2's context before its first step:** besides its prompt, the harness injected the plugin repository's `CLAUDE.md`, the owner's memory index, and the plugin repository's git status. That status lists recent plugin commits, among them the subject of ticket 61, so the seat could tell it was in an acceptance test. No fixture state reached it this way: the injected text names no fixture commit, branch or file, and no requirement.
- **Seat 2, round 1, from its first step to its conclusion:** 30 tool calls, in this order:
  - From 04:32:10 to 04:32:18Z it read only fixture files and ran git on the fixture: `AGENTS.md`, `git status`, `branch -a`, `log --all --graph`, `worktree list`, `ls-remote`, `CONTEXT.md`, then the ticket, the dispatch directory, the configuration and the snapshot.
  - From 04:32:18Z it read the plugin's scripts README, `Workflow.md`, `implementation-tdd.md`, `CodeReview.md`, and the ticket list with ticket 57.
  - **At 04:33:00Z it read the plugin's own ticket 61** (`sed -n 1,120p modules/tickets/workflow-governance/61-wave2-end-to-end.md`). That ticket describes this run, including that the first seat stops before its receipt.
  - It wrote the receipt only after that read, from 04:33:19Z on.

  The fixture state it reported had been read by 04:32:18Z. Its reading of where the work stood did not need ticket 61, but it saw ticket 61 before it acted. **The resume was therefore not from the fixture's files alone.** The plugin checkout it was sent to also held the description of the test. This weakens part B's evidence for criterion 1. The control plane reports it to the owner rather than counting it as met.

## Files in this directory

| File | What it is |
| --- | --- |
| `files/` and `files/MANIFEST.tsv` | The project's files as they stood at the end, copied byte for byte. That covers the ticket, the dispatches, every receipt with its captures, the review record, the snapshot and the integration configuration from `origin/main`, and the queue file from `origin/main-queue`. To keep every tracked path short enough for a Windows checkout, each copy is stored under a short numbered name; `MANIFEST.tsv` maps that name to its path in the project and its sha256 |
| `git-log-main.txt`, `git-log-main-queue.txt` | The graphs of both branches, each line holding the commit, its parents, its author and its subject |
| `git-show-landed.txt` | The landed merge commit |
| `state_after_seat1.txt`, `state_after_seat2.txt` | The repository state when seat 1 ended and when seat 2 first stopped |
| `times.txt` | Seat start and end times |
