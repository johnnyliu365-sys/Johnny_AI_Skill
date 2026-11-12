# Wave-2 acceptance 1, part B, clean rerun (2026-11-12)

The first run of part B (`../RUN.md`) showed the loop working end to end, but its fresh session had also read the plugin's own ticket 61, which describes the run. This rerun closes that gap. The control plane ran it on 2026-11-12 under the owner's decision "A" on evidence: the seat transcripts stay off the public repository and are kept on the run host, with their hashes recorded here.

## What changed from the first run

- **No test description reachable.** The seats were pointed at `C:/Temp/claude/jas61r/plugin`, a `git archive` export of `cp/wave2-gates` at `943004ac`, and told to read only the project and that copy. The export has no `.git` history. It also leaves out `modules/tickets/workflow-governance/`, `doc/reviews/`, `doc/requirements/active/2026/workflow-governance/`, `doc/handoffs/` and `doc/HARNESS-CHANGELOG.md`, so no file in it describes this test or criterion 1.
- **A fixture that needs no invented input.** The project at `C:/Temp/claude/jas61r/fixture` keeps its requirement source in the row format the snapshot tool reads (`doc/requirements/sources/calc-rows.json`, generated from `calc.md`). Its `AGENTS.md` names the plugin copy and does not mention a test.
- **No hint in the fresh session's prompts.** The second seat was never told that this is a test. Every prompt is in `prompts.md`, verbatim.

## Seats

All times are UTC on 2026-11-12, taken from the transcripts (`rounds.txt`).

| Seat | Model | Rounds | Role |
| --- | --- | --- | --- |
| Seat 1 | Claude Sonnet 5.5 | 09:03:33 to 09:04:32 | Took the snapshot, wrote the ticket and the dispatch, made the implementation commit, then was ended on purpose (its prompt says so) |
| Seat 2 | Claude Sonnet 5.5 | 09:04:47 to 09:08:35, 09:14:27 to 09:16:06, 09:21:23 to 09:22:13, 09:24:30 to 09:25:10 | Fresh session. Each round's prompt said only that an earlier session ended without hand-over, or that the review had come back. It found the state from the files every time, made the receipt and both corrections, and ran `integrate.py` |
| Seat 3 | Claude Opus 5.5 | 09:09:06 to 09:13:46, 09:16:18 to 09:21:05, 09:22:22 to 09:24:25 | Independent reviewer `seat:ticket-review/61r-review` |
| Control plane | Claude Opus 5.5 | between rounds | Wrote ticket revision02 and the correction dispatch after the first review, added a note on the review cadence, and set the ticket `INTEGRATED` at the end |

## What happened

1. **Seat 1:**
   - `e54b8df` on `main`, pushed: the snapshot, the ticket and the dispatch (`dispatch_lint.py` passes). The state row read `PLANNED` with `dispatch=sha256:e6ca4afb…`.
   - `d4fca80` on `seat/calc-subtract`, not pushed: `subtract` and three tests.

   `state_after_seat1.txt` is the repository at the cut. It shows an unpushed seat branch and no receipt, review or queue.
2. **Seat 2, round 1.** It read the project's `AGENTS.md`, git (status, branches, log, worktrees, `ls-remote`), the ticket, the dispatch, the configuration, the plugin copy's rules and the diff of `d4fca80`. It concluded that the implementation was done and that the receipt and the review were missing. It wrote the receipt (`evidence_gate.py`: `cells=3 defects=0`), committed it as `a09a5d9`, and pushed the branch.
3. **Seat 3, initial review: `CHANGES_REQUESTED`.**
   - F1 to F3 are ticket defects: `contract_gate.py` is red, the dispatch has no `preflight:` block and no `registry_commit`, and the ticket lacks the closure set, Profile, XSS, strict checker, allocation and correlation.
   - F4 and F5 are evidence defects: no strict-type cell, and a float mutation that no test catches.
4. **Control plane.** It wrote revision02 of the ticket and the correction dispatch `calc-01-subtract-c1.md`, with `registry_commit`, `correction_ref` and a `preflight:` block (`4868400`).
5. **Seat 2, round 2.**
   - It found the review and revision02 from git and the files.
   - It merged `main` into the seat branch.
   - It added the contract header, an expected-value ledger and cases past 2**53 and 64 bits (`3c51c45`).
   - Every gate passed: `contract_gate.py` 0 defects, `preflight.py` `served=2`, `mypy --strict` clean.
   - It wrote the receipt `calc-01-subtract-c1.md` (`068a570`; `cells=10 defects=0` at `3c51c45`).
6. **Seat 3.**
   - It found F1 to F5 closed.
   - One evidence gap remained (C1): a declared mutation had no run cell.
   - Revision02 is a new closure revision, so the control plane read this review as revision02's initial review, `CHANGES_REQUESTED` for C1, and recorded that in a note (`20d7ce4`).
7. **Seat 3 and seat 2, the correction.**
   - Seat 2 (round 3) ran the mutation and added the receipt `calc-01-subtract-c2.md` (`4d68e3b`; `cells=2 defects=0` at `92d59c0`).
   - Seat 3 gave revision02's correction review: `APPROVED` (`c710d1e`).
8. **Seat 2, round 4.** It ran `integrate.py` with submitter `seat:implementer/calc-subtract-r3`:

   | Step | Exit | Output |
   | --- | --- | --- |
   | `submit` | 0 | `QUEUED … parent=c710d1e…` |
   | `land` | 0 | `LANDED_PENDING_CI … landed_sha=d5905ee6…` |
   | `readback` | 0 | `LANDED_PENDING_CI -> LANDED` |

   `git-show-landed.txt` shows the merge commit, with parents `c710d1e` (the tip) and `4d68e3b` (the candidate).
9. **Control plane.** It set the ticket `INTEGRATED` with both receipts (`090bee6`).

## Evidence that the resume came from the files alone

The transcripts are held on the run host under `C:/Temp/claude/jas61r/run/transcripts/` and are not committed. They are excerpts of the raw transcripts with line ends normalised to LF; otherwise each block is copied unchanged.

| File | sha256 |
| --- | --- |
| `seat1.md` | `1307866977ffd235cf779e395e01f4e18922f3129e4e4ea3770070277ab3f41d` |
| `seat2.md` | `420fca2aea3b6eb56d3fa1882a1a6c06a9fc0d84945d00a5426768cd395be1dc` |
| `seat3.md` | `548d5b5a21f1f3ebf51193d08e8a940e59d69380fa3aee79e4da5c08fe53f633` |
| `rounds.txt` | `652f168e6db160e7ee8887b922d72adc6e53cdb97b2485392921cf4a6afe1027` |

Every tool call of every seat was checked in the raw transcripts. The correction review counted seat 1 at 15, seat 2 at 41 across four rounds, and seat 3 at 58; the control plane's own first scan, 17, 43 and 61, also counted harness entries that are not tool calls. Every command and path names the fixture or the plugin copy under `C:/Temp/claude/jas61r/`, apart from writes to the seat's own scratch directory. None reads this repository, ticket 61, its review or any record of this run.

What the harness put in front of every seat cannot be removed from a subagent started in this session, and this record states it plainly. Each seat's context began with this repository's `CLAUDE.md`, the owner's memory index and this repository's git status. That status lists recent commit subjects, among them ticket 61's. No fixture state reached a seat that way: the injected text names no fixture commit, branch, file or requirement.

Two further channels were within reach and went unused (correction review S61-06):
- The harness made this repository each seat's primary working directory.
- The session's shared scratch directory held the control plane's fixture-building and collection scripts.

No seat read either; the tool-call listing shows every read under `C:/Temp/claude/jas61r/`. A later rerun, such as the wave-3 Codex run, starts its seats with the fixture as working directory and a scratch area of their own.

## Result

Criterion 1 is met in this run:
- a ticket of a fixture project went from a requirement snapshot through dispatch, implementation, independent review, two corrections and merge-queue integration to a landed merge commit;
- the session that started it was ended mid-ticket;
- a new session finished it from the ticket, receipt, review record and queue files, and from the plugin's rules, with no hand-over.

What the plugin learns. These are follow-up work, not blockers:

- **The same template gaps as in the first run.** The ticket template has no rows for Profile, XSS, closure revision, strict checker, allocation or correlation. It has no `preflight:` or `registry_commit` guidance for a first dispatch. The state row holds only one receipt path.
- **The contract gate checks only `assert` statements.** An `assertEqual` with a literal expected value passes it.
- **A receipt cannot name its own commit.** Both runs settled on "cells at the code commit; the candidate is the tip that adds only receipts". The plugin should state this rule.

## Files

| File | What it is |
| --- | --- |
| `files/` and `files/MANIFEST.tsv` | The project's files as they stood at the end, copied byte for byte. That covers the ticket, the dispatches, every receipt with its captures, the review record, the snapshot and the integration configuration from `origin/main`, and the queue file from `origin/main-queue`. To keep every tracked path short enough for a Windows checkout, each copy is stored under a short numbered name; `MANIFEST.tsv` maps that name to its path in the project and its sha256 |
| `git-log-main.txt`, `git-log-main-queue.txt`, `git-show-landed.txt` | The branch graphs and the landed merge commit |
| `state_after_seat1.txt` | The repository at the cut |
| `prompts.md`, `rounds.txt` | Every prompt, verbatim, and every round's start and end |
