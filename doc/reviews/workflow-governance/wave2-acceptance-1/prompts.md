# Seat prompts, verbatim

The control plane wrote these prompts. Each one is copied verbatim from the first message of its round in the seat's transcript. The transcripts themselves stay on the run host; their hashes are in `RUN.md`.

## seat1, round 1 (start 2026-11-07T04:30:36.209Z, end 2026-11-07T04:31:54.999Z)

```text
You are working in a fixture target project at C:/Temp/claude/jas61/fixture. It is a git repository whose remote, `origin`, is the local bare repository C:/Temp/claude/jas61/remote.git.

Start by reading the fixture's AGENTS.md. It sends you to the plugin's governance in C:/Users/User/Desktop/Johnny_AI_Skill; read that repository's AGENTS.md and follow its start order. The plugin's gate scripts are in C:/Users/User/Desktop/Johnny_AI_Skill/skills/johnny-project-takeover/scripts/, and their usage is in the README.md beside them. Use Python C:/Temp/claude/jas-venv/Scripts/python.exe with PYTHONUTF8=1.

Your task is the requirement REQ-CALC-002 in doc/requirements/sources/calc-rows.json: subtract(a, b) returns a - b. Carry it this far and no further:
1. Take the first snapshot of the requirement source with requirement_snapshot.py into doc/requirements/snapshots/, using the source name `calc`.
2. Write one ticket for REQ-CALC-002 under modules/tickets/calc/ from the fixture's modules/tickets/TEMPLATE.md.
3. Write a machine-form dispatch file for it at doc/handoffs/2026/governance/dispatch/, and check it with dispatch_lint.py until it passes.
4. Set the ticket's state row as the template describes. It names the state, `dispatch=sha256:` of the dispatch file, and the receipt path the work will use, under doc/handoffs/2026/governance/receipts/.
5. Commit the snapshot, ticket and dispatch on `main` and push `main`.
6. Create a worktree at C:/Temp/claude/jas61/fixture/.worktrees/calc-subtract on a new branch `seat/calc-subtract`. Add subtract to src/calc.py with tests in tests/test_calc.py, run the tests, and commit there. Do not push that branch.

Then stop. This session is being ended on purpose in the middle of the ticket, as part of an acceptance test. Do not write the receipt, do not ask for a review, and do not leave any hand-over note, summary file or comment for a later session beyond what the plugin's rules themselves require the project files to hold. Commit as Johnny Liu <johnny.liu365@gmail.com>, with a last trailer line `Co-Authored-By: <the model that actually did the work> <noreply@anthropic.com>`. Never touch the plugin repository, and never push anywhere except `origin` of the fixture.

Return only: the commits you made (sha and subject, on which branch), the files you created, and the exact last command you ran with its output.
```

## seat2, round 1 (start 2026-11-07T04:32:07.989Z, end 2026-11-07T04:34:24.647Z)

```text
You are a new session in a fixture target project: C:/Temp/claude/jas61/fixture. It is a git repository; its remote `origin` is C:/Temp/claude/jas61/remote.git.

An earlier session was working on a ticket here and ended without any hand-over. You have no transcript and no summary of what it did. Continue the open work by the plugin's rules, and find where it stands from the project's files alone.

Start with the fixture's AGENTS.md. It sends you to the plugin's governance in C:/Users/User/Desktop/Johnny_AI_Skill. Read that repository's AGENTS.md and follow its start order. The plugin's gate scripts are in C:/Users/User/Desktop/Johnny_AI_Skill/skills/johnny-project-takeover/scripts/, with their usage in the README.md beside them. Use Python C:/Temp/claude/jas-venv/Scripts/python.exe with PYTHONUTF8=1.

Take the ticket as far as you can on your own. The independent review must be done by someone other than you. When the work reaches the point where it needs that review, stop. Report exactly what the reviewer needs: the candidate sha, its branch, the receipt path and the review record path the project uses.

As the very first thing you report, list the files and git commands you read to decide where the work stood, in the order you read them, and what you concluded from each.

Commit as Johnny Liu <johnny.liu365@gmail.com>, with a last trailer line `Co-Authored-By: <the model that actually did the work> <noreply@anthropic.com>`. Never touch the plugin repository. Never push anywhere except the fixture's `origin`.

Return only:
- the list of what you read;
- what you concluded;
- the commits you made (sha, subject, branch);
- what you pushed;
- the review hand-off details.
```

## seat2, round 2 (start 2026-11-07T04:42:09.896Z, end 2026-11-07T04:43:28.171Z)

```text
The coordinator sent a message while you were working:
The review has come back. Continue the open work in C:/Temp/claude/jas61/fixture by the plugin's rules, and find what changed from the project's files. As before, stop when the work next needs the independent reviewer.

In your first report item, list what you read and what you concluded from it. Then give the commits you made, what you pushed, and the review hand-off: the candidate sha, the sha the cells ran at, the branch, the receipt path and the review record path.

The same rules apply as before: commit identity, the trailer, pushing only the fixture's origin, and never touching the plugin repository.

Address this before completing your current task.
```

## seat2, round 3 (start 2026-11-07T04:47:08.887Z, end 2026-11-07T04:47:46.791Z)

```text
The coordinator sent a message while you were working:
The review has come back again. Continue the open work in C:/Temp/claude/jas61/fixture by the plugin's rules, and find what changed from the project's files. This time, take the ticket as far as the plugin's rules let you without the reviewer.

You run the integration script yourself:
- Run it with the fixture's integration.json, from C:/Users/User/Desktop/Johnny_AI_Skill/skills/johnny-project-takeover/scripts/integrate.py.
- Use a submitter id of your own, in the form seat:<profile>/<run-id>. It must differ from the reviewer's.
- Read the CI result back.

In your first report item, list what you read and what you concluded from each item. Then report:
- each integrate.py command you ran, with its exit code and its full stdout and stderr;
- the queue entry as it stands at the end, read from the queue branch;
- the landed commit and its parents;
- any commits you made and what you pushed.

The same rules apply as before: commit identity, trailer, push only to the fixture's origin, and never touch the plugin repository.

Address this before completing your current task.
```

## seat3, round 1 (start 2026-11-07T04:34:46.236Z, end 2026-11-07T04:41:17.730Z)

```text
You are the independent ticket-review seat for one ticket in a fixture target project. Your seat id is seat:ticket-review/61b-review. You authored nothing in this ticket.

Fixture: C:/Temp/claude/jas61/fixture. It is a git repository whose `origin` is C:/Temp/claude/jas61/remote.git. Read the fixture's AGENTS.md first. It sends you to the plugin's governance in C:/Users/User/Desktop/Johnny_AI_Skill; read that repository's AGENTS.md and CodeReview.md and follow them. Use Python C:/Temp/claude/jas-venv/Scripts/python.exe with PYTHONUTF8=1. The plugin's scripts are in C:/Users/User/Desktop/Johnny_AI_Skill/skills/johnny-project-takeover/scripts/.

Ticket: modules/tickets/calc/01-subtract.md, requirement REQ-CALC-002, branch `seat/calc-subtract` on origin.

The submitted candidate is the branch tip 545adb36f1196a6462718361fc7b101d07517c11. It contains:
- the implementation commit bd3e756, which the receipt's cells ran at;
- one commit after it that adds only the receipt, its captures and the ticket close-out.

Review the candidate as the plugin's CodeReview.md requires. At least:
1. The ticket, the dispatch file, and that the dispatch digest equals the state row.
2. The implementation and its tests against REQ-CALC-002.
3. The receipt at doc/handoffs/2026/governance/receipts/01-subtract.md. Run evidence_gate.py on it against bd3e756.
4. That `git diff bd3e756 545adb3` touches only the receipt, captures and ticket. If so, the cells at bd3e756 stand for the candidate's code.
5. One counter-mutation of your own.
6. Anything the seat chose where the plugin's rules are silent. The ticket state is set to DONE before review, and contract_gate.py was not run because the fixture has no spec. Say whether each is a finding, and of which class.

Do the review in a clone of the fixture made with --no-hardlinks under C:/Temp/claude/jas61/review-scratch/.

Then write the review record at doc/reviews/calc/01-subtract-code-review.md, on the fixture's `main` branch, in the fixture's main working copy. The record ends with a fenced review-verdict block with these four keys: `candidate: 545adb36f1196a6462718361fc7b101d07517c11`, `verdict` (APPROVED or CHANGES_REQUESTED), `reviewer: seat:ticket-review/61b-review` and `reviewed_at` (today). Commit it on main as Johnny Liu <johnny.liu365@gmail.com>, with a last trailer line `Co-Authored-By: <the model that did the work> <noreply@anthropic.com>`, and push main to the fixture's origin.

Do not touch the seat branch, the queue, or the plugin repository. Do not run integrate.py.

Return only:
- the verdict;
- the findings with their class;
- the record's commit sha on main;
- what you pushed.
```

## seat3, round 2 (start 2026-11-07T04:43:37.885Z, end 2026-11-07T04:46:51.133Z)

```text
The coordinator sent a message while you were working:
Control plane: next is the correction review of fixture ticket 01. Your seat id stays seat:ticket-review/61b-review. The verdict is APPROVED, CHANGES_REQUESTED or CONVERGENCE_REVIEW_REQUIRED (CodeReview §5).

The control plane wrote the ticket's revision02 on the fixture's `main` (285843e), together with a correction dispatch, 01-subtract-c1.md. Revision02 answers your F1 and F2 and lists the work for F3 to F5.

Candidate: 45fc3873bb002d2dfd3fecd52eee31ad92de5f20, the tip of `seat/calc-subtract` on origin.
- The seat says its cells ran at b00b521c23f6f8b6ec863cbae0509f93ddca4e52.
- It says the commit after b00b521 adds only the receipt and its captures under doc/handoffs/2026/governance/receipts/.
- Receipt: doc/handoffs/2026/governance/receipts/01-subtract-c1.md.
- The seat merged origin/main into the branch first (007d1e7).

Check:
- F1 to F5 are closed:
  - contract_gate.py exits 0 at the candidate;
  - mypy --strict passes;
  - your 64-bit wraparound mutation is now red;
  - the receipt has the contract cell, the smoke command, the typed return and its statements.
- `git diff b00b521 45fc387` touches only the receipt and captures.
- The merge took main's revision02 ticket whole.
- evidence_gate.py passes on the new receipt against b00b521.
- Add one counter-mutation of your own.

Work in your --no-hardlinks scratch clone.

Then append a section headed "## Correction review" to doc/reviews/calc/01-subtract-code-review.md on the fixture's main. It ends with a new review-verdict block: candidate 45fc3873bb002d2dfd3fecd52eee31ad92de5f20, the verdict, reviewer seat:ticket-review/61b-review, and reviewed_at today. Commit it with the same identity and trailer rules as before, and push main to the fixture's origin.

Do not touch the seat branch, the queue or the plugin repository, and do not run integrate.py.

Return only: the verdict, any findings with their class, the record's commit sha, and what you pushed.

Address this before completing your current task.
```
