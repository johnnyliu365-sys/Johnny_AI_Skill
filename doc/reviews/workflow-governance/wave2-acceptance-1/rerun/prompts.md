# Seat prompts, verbatim (rerun)

The control plane wrote these prompts. Each one is copied verbatim from the first message of its round in the seat's transcript. The transcripts stay on the run host; their hashes are in `RUN.md`.

## seat1, round 1 (start 2026-11-12T09:03:33.448Z, end 2026-11-12T09:04:32.873Z)

```text
You are working in a fixture target project at C:/Temp/claude/jas61r/fixture. It is a git repository whose remote `origin` is the local bare repository C:/Temp/claude/jas61r/remote.git.

Start by reading the fixture's AGENTS.md. It names the plugin copy this project uses, C:/Temp/claude/jas61r/plugin. Read that copy's AGENTS.md and follow its start order. Read only files inside the fixture and that plugin copy. The plugin's gate scripts are in C:/Temp/claude/jas61r/plugin/skills/johnny-project-takeover/scripts/, and their usage is in the README.md beside them. Use Python C:/Temp/claude/jas-venv/Scripts/python.exe with PYTHONUTF8=1.

Your task is the requirement REQ-CALC-002 in doc/requirements/sources/calc-rows.json (subtract(a, b) returns a - b). Carry it exactly this far:
1. Take the first snapshot of that requirement source with requirement_snapshot.py into doc/requirements/snapshots/, source name `calc`.
2. Write one ticket for REQ-CALC-002 under modules/tickets/calc/ from the fixture's modules/tickets/TEMPLATE.md.
3. Write a machine-form dispatch file for it at doc/handoffs/2026/governance/dispatch/, and make it pass dispatch_lint.py.
4. Fill the ticket's state row as the template describes: the state, `dispatch=sha256:` of the dispatch file, and the receipt path the work will use under doc/handoffs/2026/governance/receipts/.
5. Commit the snapshot, the ticket and the dispatch on `main`, and push `main`.
6. Create a worktree at C:/Temp/claude/jas61r/fixture/.worktrees/calc-subtract on a new branch `seat/calc-subtract`. Add subtract to src/calc.py, with tests in tests/test_calc.py, run the tests, and commit there. Do not push that branch.

Then stop. This session is being ended on purpose in the middle of the ticket, as part of an acceptance test. Do not write the receipt and do not ask for a review. Leave no hand-over note, summary file or comment for a later session beyond what the plugin's rules themselves require the project files to hold.

Commit as Johnny Liu <johnny.liu365@gmail.com>, with a last trailer line `Co-Authored-By: <the model that actually did the work> <noreply@anthropic.com>`. Never push anywhere except the fixture's `origin`.

Return only:
- the commits you made, with sha, subject and branch;
- the files you created;
- the exact last command you ran, with its output.
```

## seat2, round 1 (start 2026-11-12T09:04:47.270Z, end 2026-11-12T09:08:35.841Z)

```text
You are a new session in a project at C:/Temp/claude/jas61r/fixture. It is a git repository; its remote `origin` is C:/Temp/claude/jas61r/remote.git.

An earlier session was working on a ticket here and ended without any hand-over. You have no transcript and no summary of what it did. Continue the open work by the plugin's rules, and find where it stands from the project's files.

Start with the project's AGENTS.md. It names the plugin copy this project uses, C:/Temp/claude/jas61r/plugin; read that copy's AGENTS.md and follow its start order. Read only files inside the project and that plugin copy. The plugin's gate scripts are in C:/Temp/claude/jas61r/plugin/skills/johnny-project-takeover/scripts/, with their usage in the README.md beside them. Use Python C:/Temp/claude/jas-venv/Scripts/python.exe with PYTHONUTF8=1.

Take the ticket as far as you can on your own. The independent review must be done by someone other than you. When the work reaches the point where it needs that review, stop and report what the reviewer needs: the candidate sha, its branch, the receipt path and the review record path the project uses.

As the very first thing you report, list what you read to decide where the work stood, files and git commands, in the order you read them, and what you concluded from each.

Commit as Johnny Liu <johnny.liu365@gmail.com>, with a last trailer line `Co-Authored-By: <the model that actually did the work> <noreply@anthropic.com>`. Never push anywhere except the project's `origin`.

Return only:
- the list of what you read;
- what you concluded;
- the commits you made (sha, subject, branch);
- what you pushed;
- the review hand-off details.
```

## seat2, round 2 (start 2026-11-12T09:14:27.921Z, end 2026-11-12T09:16:06.845Z)

```text
The coordinator sent a message while you were working:
The review has come back. Continue the open work in C:/Temp/claude/jas61r/fixture by the plugin's rules, and work out from the project's files what changed. As before, read only the project and the plugin copy C:/Temp/claude/jas61r/plugin, and stop when the work next needs the independent reviewer.

Report, in this order:
- what you read, and what you concluded from it;
- the commits you made;
- what you pushed;
- the review hand-off: the candidate sha, the sha the cells ran at, the branch, the receipt path and the review record path.

The same rules as before apply: commit identity, trailer, and pushing only to the project's origin.

Address this before completing your current task.
```

## seat2, round 3 (start 2026-11-12T09:21:23.725Z, end 2026-11-12T09:22:13.357Z)

```text
The coordinator sent a message while you were working:
The review has come back again. Continue the open work in C:/Temp/claude/jas61r/fixture by the plugin's rules, and work out what changed from the project's files. As before, read only the project and the plugin copy, and stop when the work next needs the independent reviewer.

Report, in this order:
- what you read and what you concluded;
- the commits you made;
- what you pushed;
- the review hand-off: the candidate sha, the sha the cells ran at, the branch, the receipt path and the review record path.

The same rules as before apply.

Address this before completing your current task.
```

## seat2, round 4 (start 2026-11-12T09:24:30.381Z, end 2026-11-12T09:25:10.474Z)

```text
The coordinator sent a message while you were working:
The review has come back again. Continue the open work in C:/Temp/claude/jas61r/fixture by the plugin's rules, and work out what changed from the project's files. Take the ticket as far as the plugin's rules let you without the reviewer. As before, read only the project and the plugin copy.

You run the integration script yourself:
- Use C:/Temp/claude/jas61r/plugin/skills/johnny-project-takeover/scripts/integrate.py with the project's integration.json.
- Pick a submitter id of your own, in the form seat:<profile>/<run-id>, different from the reviewer's.
- Read the CI result back.

Report, in this order:
1. What you read and what you concluded.
2. Each integrate.py command, with its exit code and its full stdout and stderr.
3. The queue entry as it stands at the end, read from the queue branch.
4. The landed commit and its parents.
5. Any commits you made and what you pushed.

The same rules as before apply.

Address this before completing your current task.
```

## seat3, round 1 (start 2026-11-12T09:09:06.484Z, end 2026-11-12T09:13:46.123Z)

```text
You are the independent ticket-review seat for one ticket in a project at C:/Temp/claude/jas61r/fixture. Your seat id is seat:ticket-review/61r-review. You authored nothing in this ticket.

The project is a git repository; its `origin` is C:/Temp/claude/jas61r/remote.git. Read the project's AGENTS.md first. It names the plugin copy C:/Temp/claude/jas61r/plugin. Read that copy's AGENTS.md, CodeReview.md and skills/johnny-project-takeover/references/review-checks.md, and follow them. Read only files inside the project and that plugin copy. Use Python C:/Temp/claude/jas-venv/Scripts/python.exe with PYTHONUTF8=1. The plugin's scripts are in C:/Temp/claude/jas61r/plugin/skills/johnny-project-takeover/scripts/.

The ticket is modules/tickets/calc/01-subtract.md, for requirement REQ-CALC-002, on branch `seat/calc-subtract` on origin.
- The candidate for the queue is the branch tip, a09a5d90535a273fd44b714363bb924d97778a35.
- The receipt's cells ran at the implementation commit d4fca80be98dfbabb2b8fd53fe13ae44414e89ed.
- The commit between them is meant to add only the receipt, its captures and the ticket close-out.
- The receipt is doc/handoffs/2026/governance/receipts/calc-01-subtract.md.

Review the candidate as the plugin's CodeReview.md requires. Cover at least these:
1. The ticket and the dispatch, and that the dispatch digest equals the state row.
2. The implementation and its tests against REQ-CALC-002.
3. The receipt: run evidence_gate.py on it against d4fca80, and confirm that `git diff d4fca80 a09a5d9` touches only the receipt, its captures and the ticket.
4. Every gate the plugin defines that applies to this project. Run each one; do not take a seat's word that it does not apply.
5. One counter-mutation of your own.

Do the review in a clone of the project made with --no-hardlinks under C:/Temp/claude/jas61r/review-scratch/.

Then write the review record at doc/reviews/calc/01-subtract-code-review.md on the project's `main` branch, in its main working copy. End it with a fenced review-verdict block holding `candidate: a09a5d90535a273fd44b714363bb924d97778a35`, `verdict` (APPROVED or CHANGES_REQUESTED), `reviewer: seat:ticket-review/61r-review` and `reviewed_at` (today).

Commit the record on main as Johnny Liu <johnny.liu365@gmail.com>, with a last trailer line `Co-Authored-By: <the model that did the work> <noreply@anthropic.com>`, and push main to the project's origin.

Do not touch the seat branch or the queue, and do not run integrate.py.

Return only: the verdict, the findings with their class, the record's commit sha on main, and what you pushed.
```

## seat3, round 2 (start 2026-11-12T09:16:18.161Z, end 2026-11-12T09:21:05.351Z)

```text
The coordinator sent a message while you were working:
Control plane: you are next for the correction review of ticket 01 in C:/Temp/claude/jas61r/fixture. Your seat id stays seat:ticket-review/61r-review. Under CodeReview §5 the verdict is APPROVED, CHANGES_REQUESTED or CONVERGENCE_REVIEW_REQUIRED.

The control plane wrote revision02 of the ticket and a correction dispatch, `calc-01-subtract-c1.md`, on main at 4868400. It answers your F1 to F3 and sets the work for F4 and F5.

The candidate is the tip of `seat/calc-subtract` on origin: 068a57044246e2b195aafa18e23d74cb0697de15.
- The seat says its cells ran at 3c51c45fe5b958e9aed7f601649ab1d98062b8bb.
- The commit after 3c51c45 adds only the receipt `calc-01-subtract-c1.md` and its captures.
- The seat merged origin/main first (b70830c).
- One choice is open: the spec header declares a mutation `add-subtracts-operands` that the seat did not run, because `add` is outside the ticket. Judge it.

Check:
- F1 to F5 are closed:
  - contract_gate.py exits 0;
  - preflight.py exits 0 on the c1 dispatch;
  - mypy --strict passes;
  - your float mutation turns tests red.
- `git diff 3c51c45 068a570` touches only the receipt and its captures.
- The merge took main's revision02 ticket whole.
- evidence_gate.py passes on the new receipt against 3c51c45.
- Every applicable gate, run by you.
- One more counter-mutation of your own.

Read only the project and the plugin copy, and work in your --no-hardlinks scratch clone. Then append a section headed "## Correction review" to doc/reviews/calc/01-subtract-code-review.md on main. It ends with a new review-verdict block: candidate 068a57044246e2b195aafa18e23d74cb0697de15, verdict, reviewer seat:ticket-review/61r-review, reviewed_at today. Commit it with the same identity and trailer rules, and push main.

Do not touch the seat branch or the queue, and do not run integrate.py.

Return only: the verdict, the findings with their class, the record's commit sha, and what you pushed.

Address this before completing your current task.
```

## seat3, round 3 (start 2026-11-12T09:22:22.779Z, end 2026-11-12T09:24:25.568Z)

```text
The coordinator sent a message while you were working:
Control plane: next is revision02's one correction review of ticket 01 in C:/Temp/claude/jas61r/fixture. Your seat id is still seat:ticket-review/61r-review. The control plane note in the record (main, 20d7ce4) reads your last review as revision02's initial review: CHANGES_REQUESTED, for C1 only. The verdict now is APPROVED, CHANGES_REQUESTED or CONVERGENCE_REVIEW_REQUIRED (CodeReview §5), and no third correction follows.

Candidate: 4d68e3b1f8ccf22f19ff76a006f7370eb8cf7f0c, the tip of `seat/calc-subtract` on origin.
- The seat merged origin/main, docs only, as 92d59c0.
- It ran the declared mutation `add-subtracts-operands` at 92d59c0.
- It added a separate receipt, `calc-01-subtract-c2.md`, whose two cells name 92d59c0. The c1 receipt, with its cells at 3c51c45, is unchanged.

Check:
- C1 is closed: run evidence_gate.py on c2 against 92d59c0 and on c1 against 3c51c45.
- The three tool blobs (src/calc.py, tests/test_calc.py, tests/ledger/calc.json) are identical at 3c51c45, 92d59c0 and 4d68e3b.
- `git diff 068a570 4d68e3b` adds only the review record from main, the c2 receipt and its captures.
- Every earlier closure still holds.
- Judge whether a second receipt that adds to the first is acceptable evidence.

Read only the project and the plugin copy. Work in your scratch clone.

Then append a section headed "## Revision02 correction review" to doc/reviews/calc/01-subtract-code-review.md on main. End it with a review-verdict block: candidate 4d68e3b1f8ccf22f19ff76a006f7370eb8cf7f0c, the verdict, reviewer seat:ticket-review/61r-review, reviewed_at today. Commit it with the same rules and push main. Do not touch the seat branch or the queue, and do not run integrate.py.

Return only: the verdict, any findings with their class, the record's commit sha, and what you pushed.

Address this before completing your current task.
```
