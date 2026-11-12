# REVIEW — ticket 61 Wave-2 acceptance (1) end to end

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`.** Part A is correct and passes every check I ran. Its one open finding, S61-01, is an evidence gap that does not block approval under rule B. The verdict comes from part B, finding S61-05. The ticket requires the record to hold the exact instructions each seat was given, the first seat's last tool output and the second seat's first file reads, and it requires the reviewer to confirm the resume from those reads. The record holds summaries of these items, not the items themselves. So the criterion's core fact cannot be checked from the record and the fixture: that the second session saw only the files, with no hand-over. The fix is documentation only, inside the ticket's `create` path `doc/reviews/workflow-governance/wave2-acceptance-1/`. Part A needs no change for this verdict.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/61-wave2-end-to-end.md`, revision01, read at `a8809e63` (state row: part A returned `4215b980`, part B recorded at `ac251c87`, initial review dispatched) |
| Requirement | REQ-20261103-043, "Implementation readiness" row, wave-2 acceptance criterion (1) |
| Dispatch (part A) | `C:/Temp/claude/jas-dispatch/JAS-61_dispatch.yaml`, base `803c0471c3dc88a19d5997af1fcac5bf241e0eea` |
| Candidate (part A) | `4215b980bb3dc19dee5c7563f7ed412c97f08464` on `cp/wave2-61-wave2-end-to-end` (on origin at the same sha); one commit on `803c0471`; author and committer Johnny Liu |
| Record (part B) | `doc/reviews/workflow-governance/wave2-acceptance-1/` committed at `ac251c87` on `cp/wave2-gates` |
| Fixture (part B) | `C:/Temp/claude/jas61/fixture`, origin `C:/Temp/claude/jas61/remote.git`; `origin/main` `7868360`, `origin/main-queue` `c3a1c16` |
| Seat receipt | `.worktrees/61-wave2-end-to-end-out/RETURN.md` |
| Review worktree | `.worktrees/61-wave2-end-to-end-review`, detached at the candidate, porcelain empty |
| Reviewer | `seat:ticket-review/61-rev01-initial` |
| References applied | `CodeReview.md` (whole), `review-checks.md` (Test truthfulness and the reviewer counter-mutation, Task/worktree binding, Ticket dispatch schema review) |
| Not applicable | XSS: no browser, DOM or JS surface. Secret, Provider, external effect: none; the remote is a local bare repository and nothing goes to the network. Profile fan-out and POC/staging: none. |
| CI | run 42341356820 on the candidate: windows `success`; linux `failure`, with only ticket 50's two `tests/test_integrate.py` tests unregistered (ticket 64), and no failure or error naming `test_wave2_end_to_end.py` |

### Part A — the end-to-end test

| # | Check | Result |
| --- | --- | --- |
| 1 | Real committed scripts as subprocesses; no patch, no import | **PASS.** Every script runs as `[sys.executable, SCRIPTS/<name>, ...]`: `requirement_snapshot.py take` and `verify`, `dispatch_lint.py`, `evidence_gate.py`, and `integrate.py submit`, `land` and `readback`. The imports are stdlib only (lines 26–38, and lines 66–72 in the child). There is no `mock`, no `sys.path` change and no script import, and `RegressionTests` pins this. My production mutations P1–P4 each turned the file red, so the test does run the committed code. |
| 2 | Second half in a new process given only the fixture path; leak channels | **PASS for this candidate; the guard is weaker than the STATEMENT claims (S61-01).** I read the child: it uses only `sys.argv[1]` and one static constant, the path of the scripts directory. The launch guard pins argv (six items) and nothing else. `extra_env` is `set(env) - set(clean_environment())`, which compares two calls to the same function, so it is empty unless the harness adds a key after the call. `env_extra` checks only the `JAS61_` prefix, which nothing ever sets. My probes: R0 shows that the child inherits `PYTEST_CURRENT_TEST` (the running test's name), runs with the harness's current directory (the plugin checkout, not the fixture), and can list `aux/rows.json` beside its own script. In R1, R2 and R3 the first half passed the candidate sha through an environment variable, a temp file outside the fixture and the child script's own text. The child used the value (a probe asserted `leak == candidate`), and all 15 original tests stayed green, zero red. There are no module globals or cache across processes, and `-I` drops the user site and the `PYTHON*` variables. |
| 3 | Each process decides the next step from the files; the test asserts the decision | **PASS.** The child reads the state row (state word, `dispatch=` digest, receipt path, implementer), re-gates the receipt with `evidence_gate.py`, and reads the queue with `git fetch` and `git show origin/main-queue:<queue_path>`. It decides `review`, `land`, `readback` or `none`. The test asserts the decision and the performed steps against `STEPS[3]`, `STEPS[5]`, `STEPS[6]` and `none`. My mutation S1 made the child ignore a `DONE` row, and that turned red. The decision logic is test code, not a plugin script (S61-02). |
| 4 | Both cuts; every TDD 2 refusal and TDD 3 fail-closed case | **PASS.** Cut after step 3 and cut after `submit` are both covered, plus the cut after `land` (readback only) and the third-process cases. TDD 2: digest mismatch (`DISPATCH_DIGEST_MISMATCH`); a receipt failing the gate, by edited capture and by stale tool digest (`RECEIPT_GATE_RED`); a review record that does not admit the candidate, by wrong candidate, a non-APPROVED verdict and self review (`SUBMIT_REFUSED`/`REVIEW_MISMATCH`). Each asserts that nothing landed: the remote tip and the queue tip are unchanged and the queue is empty. Defect category 6, a broken state row, has four shapes. TDD 3: unreachable remote at `land` gives exit 2 with `tool fault`, and the queue text and both tips are unchanged; red CI gives `LANDED_CI_RED`, and a second `land` exits 1 with `BLOCKED_BY_CI` and changes nothing. |
| 5 | Stand-in reviewer `seat:review/run-2` written by the second process | **Acceptable for a mechanics test.** Step 4 of part A has the second process finish steps 4 and 5. The stand-in is a seat id distinct from the submitter, so `integrate.py`'s review admission is exercised for real, and the self-review subtest proves that the submitter-as-reviewer path refuses. It approves whatever passes the gate, so it proves nothing about review independence. Part B carries that, and the seat says so in its STATEMENT. Not a finding. |
| 6 | Seat conventions where the ticket is silent | **Acceptable for this ticket; they point to plugin gaps (S61-03).** The conventions are: dispatch at `<stem>.dispatch.yaml`; implementer row = submitter seat id; review record at `doc/reviews/<stem>.md`. The template's state row binds the dispatch by digest but names no path. Part B put the dispatch at `doc/handoffs/2026/governance/dispatch/<ticket>.md`. The template's implementer row is `<AI／worktree>` (part B: `calc-subtract worktree`). On resume, part A's second process submits under the first seat's id, while part B's second seat used its own. |
| 7 | Reviewer counter-mutations | **Done; 9 runs, table below.** Every mutation the seat reported mutated the test's own child or harness. I entered through the production scripts (P1–P4) and the leak channels (R0–R3). All four production mutations went red. The three leak channels gave zero red, and that is reported as S61-01, not as a pass. |
| 8 | Receipt | **PASS.** `receipt_check.py` gives `receipt defects: 0`, exit 0, and `evidence_gate.py` with `--require-cell` P1 T1 M1 F1 P9 E1 gives `cells=6 defects=0`, exit 0, both on the full receipt. RETURN.md and every capture have 0 CR bytes. Each raw block equals its capture byte for byte (P1, T1, M1, F1, P9, E1). Each `exit:` list equals the capture's `exit=` lines in order; M1 is `0,1,1,1,1,0`. M1 is whole: the clone line (with `core.autocrlf=false`), four mutation sections each with exit 1, and `restored` with exit 0. Each section is the unfiltered tail, as the dispatch allows. The seat's F1 failure set (5) is a subset of the normalised base `^FAILED` names (12), with zero new red. |
| 9 | Boundary | **PASS.** `git diff --name-status 803c0471 4215b980`: `A tests/test_wave2_end_to_end.py` only. Author and committer are Johnny Liu. Stdlib only, with no `Any` and no `type: ignore`. The blob is LF (0 CR). My own `mypy --strict --python-version 3.11` gives `Success: no issues found in 1 source file`, exit 0. The trailer names the model. |
| F1 | My full suite on the candidate, under the host lock | **PASS.** `5 failed, 3770 passed, 37 skipped, 7511 subtests passed in 1129.28s`, exit 1. The failure set is a subset of the base, with zero new red, and it equals the seat's set. The seat reported 7510 subtests and I got 7511; the difference is outside this file, and the failure sets are identical. |

#### Reviewer counter-mutations (clone `--no-hardlinks`, `core.autocrlf=false`, at `4215b980`; one pytest at a time; whole test file; unfiltered output read)

| Id | Door | Mutation | Result |
| --- | --- | --- | --- |
| R0 | observation | the child reports `PYTEST_CURRENT_TEST`, its current directory and its script directory's listing; a probe asserts what it sees | 16 passed: the child sees the harness's test name, the plugin checkout as its current directory, and `rows.json` |
| R1 | environment | the first half sets `os.environ["RESUME_CANDIDATE"]`; the child uses it as the candidate | **16 passed, zero red**; the probe confirms the leaked value was used |
| R2 | temp file outside the fixture | the first half writes `aux/state.txt`; the child reads it beside its own script | **16 passed, zero red**; the leaked value was used |
| R3 | child script text | the harness writes the candidate into the child source before launch | **16 passed, zero red**; the leaked value was used |
| P1 | `integrate.py` readback | a `red` CI answer is recorded as `LANDED` | red: 2 FailClosed tests |
| P2 | `integrate.py` exit codes | `EXIT_FAULT = 2` → `1` | red: `test_an_unreachable_remote_at_land_is_exit_two_and_the_queue_is_unchanged` |
| P3 | `integrate.py submit` | the review check at submit is removed | red: 6 tests and all 3 review-refusal subtests |
| P4 | `evidence_gate.py` | the raw-block and capture comparison is skipped | red: `test_a_receipt_that_fails_the_evidence_gate_is_refused` |
| S1 | child decision | a `DONE`/`SUPERSEDED` state row is ignored | red: `test_a_finished_ticket_leaves_nothing_for_a_third_process` |

After every run the clone was restored with `git checkout -- .`, and its porcelain was empty.

### Part B — the live run record

| # | Check | Result |
| --- | --- | --- |
| 10 | Copies equal the fixture at `origin/main` / `origin/main-queue`, byte for byte | **PASS.** All 21 files under `fixture/` in `ac251c87` equal the fixture blobs: 20 against `origin/main` and `MERGE-QUEUE.json` against `origin/main-queue`. `git-log-main.txt` and `git-log-main-queue.txt` equal a fresh `git log --graph --format='%h %p %an %s'` of both branches. |
| 11 | Landed commit is a merge with parents (tip, candidate); queue entry `LANDED` | **PASS.** `ebb77083…` has parents `8d3ab408…` (the tip after the disposition) and `45fc3873…` (the candidate). The queue entry `01-subtract@45fc3873…` is `LANDED` with `landed_sha ebb77083…`, reviewer `seat:ticket-review/61b-review` and submitter `seat:implementation-standard/61c-resume3`. The remote's `main` is `7868360`, whose only change after `ebb7708` is the ticket's state row. |
| 12 | RUN.md matches the fixture history and the review record | **PASS, with gaps in the timeline.** Every sha and step in "What happened" matches the fixture graph, the commit times and the review record: `CHANGES_REQUESTED` on `545adb36`; `CONVERGENCE_REVIEW_REQUIRED` on `45fc3873`; the convergence-disposition `APPROVED` under rule B, carrying F6, G1–G4. The first receipt has the 4 judged cells plus STATEMENT, as stated. `times.txt` gives each seat's first start and last end. The start and end of seat 2's rounds 2 and 3 and of seat 3's round 2 are missing; the ticket asks for each seat's start and end (part of S61-05). |
| 13 | The second seat resumed from the files, with no hand-over | **NOT VERIFIABLE from the record (S61-05).** The fixture does support it, as far as it goes: `state_after_seat1.txt` shows a clean `main`, an unpushed seat branch, no receipt, no review and no queue branch. The ticket row was `PLANNED`. No hand-over file exists in the fixture or in the seat worktree (only ignored `.mypy_cache`). Seat 2's later commits act on facts it could read from git. But the instructions are given as "was told: …" summaries, not verbatim. Seat 2's first reads are the control plane's prose account of its report. Seat 1's last tool output is not in the record. `state_after_seat1.txt` and `state_after_seat2.txt` are repository snapshots in the control plane's `run/` directory, not seat output. Nothing in the record lets a reader check, independently of the control plane's account, that the instruction carried no state. |
| 14 | The four plugin gaps in RUN.md | (1) Real: `template/modules/tickets/TEMPLATE.md` has no Profile, XSS, closure-revision or typed-return rows, and line 36 cites `CodeReview.md` §2.1, which does not exist (§2 has no subsections). Follow-up ticket: **yes**. (2) Real: a receipt committed beside its candidate cannot name that commit. Part B used "cells at the implementation commit, candidate = receipt-only tip". Part A kept receipts out of git. Neither rule is written down. Follow-up ticket: **yes**. (3) Real, but a fixture-construction defect: the row fields `requirement_snapshot.py` needs are documented in `scripts/README.md`. Follow-up ticket: **no**. (4) Real: the template lists `DONE` with no transition rule, seat 2 set `DONE` before review (`545adb3`), and the control plane set the fixture ticket to `INTEGRATED`, a state the template's list does not hold. Follow-up ticket: **yes**, the same template ticket as (1). Also missing from the list: S61-02 and S61-03. |

### Findings

| # | Class | Blocks approval | Closure item | Finding | Route |
| --- | --- | --- | --- | --- | --- |
| S61-01 | `EVIDENCE_DEFECT` | no (rule B: candidate correct, property not pinned) | Part A "That process holds no object, variable or argument from the first half"; completion mutation "Give the second process an in-memory value from the first" | The guard pins argv only. `extra_env` is tautological, `env_extra` checks an unused prefix, and neither the child script's bytes nor the temp root nor the current directory is pinned. R1–R3 leaked the candidate through the environment, a temp file and the script text with zero red. R0 shows that real harness values (`PYTEST_CURRENT_TEST`, the current directory) do reach the child today, though unused. The STATEMENT's "an environment equal to the harness base" overstates the guard. If this regressed, a test that leaks state would pass as a files-only resume. | Fix at the next change of this test (rule B, "would admit what it should not"): launch the child with an explicit allow-listed environment and `cwd` = the fixture, from a fresh directory that holds only the script; assert that the script bytes equal the constant template, and that the child's reported environment keys equal the allow-list. Not required for part A to land. |
| S61-02 | `OUT_OF_SCOPE_HARDENING` | no | AGENTS.md start order step 5 (the next gate script decides from the state files); TDD 4 | The resume decision exists only as the test's `SECOND_HALF` string (part A) and as an agent's judgment (part B). No committed plugin script reads the state row, receipt and queue and names the next step. Part A therefore proves that the files are sufficient, not that the plugin decides. | Follow-up `PLANNED` ticket: a committed next-step reader with typed exits, which part A's child would then call. |
| S61-03 | `OUT_OF_SCOPE_HARDENING` | no | Part A conventions (ticket silent); part B resume | The plugin defines none of these: (a) the dispatch file's path (the state row carries only its digest); (b) who the submitter is on resume, the original seat (part A) or the resuming seat (part B); (c) worktree ownership on resume (part B's seat 2 worked in seat 1's `.worktrees/calc-subtract`); (d) the review record path (part A `doc/reviews/<stem>.md`, part B `doc/reviews/<feature>/<ticket>-code-review.md` as in AGENTS.md). | Fold into the template follow-up with RUN.md gaps (1) and (4). |
| S61-04 | `OUT_OF_SCOPE_HARDENING` | no | TDD 2 (clarity) | The subtest named "changes requested" uses a record whose blocks name the wrong candidate; the CHANGES_REQUESTED verdict is the "verdict not approved" subtest. Two of the child's paths are untested: `QUEUE_BROKEN`, and the receipt path escaping the fixture. Both are the test's own resume logic, not plugin code. | Carry to the S61-02 ticket, where that logic becomes production code. |
| S61-05 | `EVIDENCE_DEFECT` | **yes** (see below) | Part B record contents ("the exact instruction each was given"; "its start and end"; "the first seat's last tool output and the second seat's first file reads, showing that the resume came from the files"); completion: "the record directory holds every item listed above. The reviewer confirms from the second seat's first reads that it resumed from the files." | The record summarises the instructions and seat 2's first reads instead of holding them. It omits seat 1's last tool output, and the per-round start and end times. I cannot confirm the resume from seat 2's first reads, because they are not in the record. | Correct additively under `doc/reviews/workflow-governance/wave2-acceptance-1/`, docs only. Add the verbatim instruction text of every seat round. Add seat 1's last tool call and its output, and seat 2's first tool calls and their outputs up to its state conclusion, copied unedited from the session transcripts. Add the start and end of every round to `times.txt`. Say in RUN.md where each excerpt came from. Then a correction review. |

**Why S61-05 blocks.** Under rule B, an evidence defect does not block when the candidate behaves correctly and a test merely does not pin it. S61-05 is not that kind of gap. The fact part B exists to establish is that the second session was confined to the files, with no hand-over. That fact is the criterion itself, and the record does not show it; I could not establish it from the record and the fixture. It is a confinement property, and the ticket's own completion definition requires the reviewer to confirm it from the raw reads. I therefore hold it on the blocking side. Nothing found contradicts RUN.md's account. The finding is that the account cannot yet be checked.

### Commands

All Python runs used `C:/Temp/claude/jas-venv/Scripts/python.exe` with `PYTHONUTF8=1`.

- `receipt_check.py <out>/RETURN.md <review worktree>`: `receipt defects: 0`, exit 0.
- `evidence_gate.py <out>/RETURN.md --repo <review worktree> --candidate 4215b980… --tool dispatch_lint.py --tool receipt_fence_check.py --tool index_pins.py --require-cell P1 T1 M1 F1 P9 E1`: `cells=6 defects=0`, exit 0.
- Scratch `raw_check.py`: every block equals its capture, each exit list equals its capture, and no CR anywhere.
- `python -m mypy --strict --python-version 3.11 tests/test_wave2_end_to_end.py` (cache in scratch): exit 0.
- `git diff --name-status 803c0471 4215b980`; `git log -1 --format='%an <%ae> | %cn <%ce>'`; `git cat-file blob` byte count of the test blob.
- Full suite: `python -m pytest tests -q -p no:cacheprovider` in the review worktree at `4215b980`, under the host lock: exit 1, 5 failed, all in the base.
  - Acquired 2026-11-07T05:09:11Z with `mkdir`; `owner.txt` named `run=61-rev01-initial`.
  - At acquisition, no other pytest process was running (`Win32_Process` python processes with `pytest` in the command line: none).
  - Released 05:28:12Z: `owner.txt` was checked, then the directory was renamed and removed.
- Counter-mutations: scratch `mutate.py` in `git -c core.autocrlf=false clone --no-hardlinks` of the candidate. Each run: `python -m pytest tests/test_wave2_end_to_end.py -q -rfE -p no:cacheprovider`, one at a time, after the lock was released.
- CI: `gh run view 42341356820 --json …` and `gh run view 42341356820 --log`, after completion. The Linux `check_registered_failures.py` step listed exactly the two `tests/test_integrate.py` failures as `UNREGISTERED_FAILURE`. No triggers.
- Part B, run in the fixture with `GIT_OPTIONAL_LOCKS=0` after the first read:
  - `git cat-file blob origin/main:<p>` and `origin/main-queue:<p>` compared by sha256 against `ac251c87:<record>/<p>`;
  - `git log --graph --format='%h %p %an %s'` for both branches, diffed against the record;
  - `git rev-list --parents -n1 ebb77083`;
  - `git log --all --format='%h %cI …'`;
  - the review record's verdict and disposition blocks;
  - the ticket's state row at `02ba789` and at `origin/main`;
  - a check of the seat worktree's status.

### Raw-log note

Every pytest and mutation run was direct, with no output-reducing wrapper, and I read the full output before judging. The captures, all LF, are in `.worktrees/61-wave2-end-to-end-review-scratch/`:
- `F1-review.txt`, the full suite;
- `M-<id>.txt`, one per mutation, holding the diff stat, the full pytest output, the exit code and the restored porcelain;
- `ci-run.log` and `ci-linux.log`, the CI job logs;
- `base.txt`, the normalised base names;
- `pytest_at_acquisition.txt`, which is empty.

My first `git status` in the fixture, before I set `GIT_OPTIONAL_LOCKS=0`, refreshed the stat cache of `C:/Temp/claude/jas61/fixture/.git/index` (mtime 13:09:54 local). No ref, object, tracked file or working-tree content changed.

### Not verified

- **That `test_wave2_end_to_end.py` actually ran on Linux.** The CI job runs pytest with `-q` and writes junit to the runner's temp directory, so the log prints no per-test pass line. What the log does show: no failure or error line names the file, the job's one collection error is another file (`test_codex_registration_contracts.py`), and the registered-failure check named only ticket 50's two tests. I did not download the junit artifact.
- **The seat sessions' transcripts.** Judging from the record and the fixture alone, as instructed, I did not read them. That is exactly what S61-05 asks the record to carry.
- **The removal of the fixture after the run.** It is still present, pending this review.
- **The Windows CI job's per-test result for the file**, for the same `-q` reason. The job concluded `success`.

```review-verdict
candidate: 4215b980bb3dc19dee5c7563f7ed412c97f08464
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/61-rev01-initial
reviewed_at: 2026-11-07
```

## Revision01 correction review

**Verdict: `APPROVED`.** S61-05, the only finding that blocked, is closed. The clean rerun of part B is backed by verbatim prompts, round times, and transcript excerpts whose hashes match the copies kept on the run host. I read the raw subagent transcripts myself, including the whole of seat 2's first round. No seat read this repository, ticket 61, its review or the first run's record, and nothing the harness injected carried fixture state. The landed merge, the queue entry and the byte copies all match the fixture. Part A is unchanged at `4215b980`. Every finding still open is in a class that does not block approval under §5 rule B, and each is carried below.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/61-wave2-end-to-end.md`, revision01, section "Correction 1" (added at `943004ac`), read at `f6c33831` |
| Candidate (part A) | `4215b980bb3dc19dee5c7563f7ed412c97f08464`; `cp/wave2-61-wave2-end-to-end` locally and on origin still name it |
| Record (part B) | `doc/reviews/workflow-governance/wave2-acceptance-1/rerun/` (RUN.md, prompts.md, rounds.txt, fixture byte copies, git logs, landed commit, state at the cut) at `f6c33831`; the first run's `RUN.md` is marked superseded |
| Owner decision | "A", 2026-11-12: transcripts stay off the public repository; the record holds prompts verbatim, round times, and the sha256 of unedited excerpts kept on the run host |
| Fixture | `C:/Temp/claude/jas61r/fixture`, origin `C:/Temp/claude/jas61r/remote.git`: `main` `090bee6`, `main-queue` `cb2c4a2`, `seat/calc-subtract` `4d68e3b` (remote refs equal the local `origin/*`) |
| Plugin copy given to the seats | `C:/Temp/claude/jas61r/plugin`, a `git archive` of `943004ac` (923 files, no `.git`) |
| Excerpts on the run host | `C:/Temp/claude/jas61r/run/transcripts/` |
| Raw transcripts read | the subagent transcripts of seat 1 `aa3d5234fa1730a2c`, seat 2 `a35b1380a9374e0fa` and seat 3 `a231e7c4b9e248e43`, read locally; no content copied into the repository |
| Reviewer | `seat:ticket-review/61-rev01-correction` |
| Full suite | not rerun: part A's candidate is unchanged since the initial review, whose full suite ran on it (5 failed, all in the base list, zero new red) |

### Cell results

| # | Check | Result |
| --- | --- | --- |
| C1 | Excerpt hashes equal RUN.md | **PASS.** sha256 of `seat1.md` `13078669…3f41d`, `seat2.md` `420fca2a…be1dc`, `seat3.md` `548d5b5a…f633` and `rounds.txt` `652f168e…1027` equal the table in `rerun/RUN.md`. `rerun/rounds.txt` in the repository equals the run-host copy byte for byte. |
| C2 | Excerpts match the raw transcripts | **PASS, with one normalisation (S61-08).** I compared every fenced block of the three excerpts (5, 54 and 5 blocks) with the raw transcripts. Tool calls match the indent-1 JSON of the raw `tool_use` inputs. Tool results and prompts match the raw strings. Each "context the harness injected" block equals the five text items of the seat's first request, joined by line feeds. The only difference: the excerpts are LF only, so one tool result (`LINT PASS\r\n`, seat 2, 09:08:02Z) lost its CR. |
| C3 | Every prompt in prompts.md is verbatim | **PASS.** All 8 rounds are verbatim (seat 1 ×1, seat 2 ×4, seat 3 ×3); the resumed rounds include the harness's "coordinator sent a message" prefix. Each round's start and end equal the first and last timestamped record of that round in the raw transcript. |
| C4 | No seat read this repository, ticket 61, its review or the first run's record | **PASS.** The raw transcripts hold 114 tool calls (15, 41 and 58 by unique id), and I listed every one with every path it names. Each Bash call starts with `cd` into `C:/Temp/claude/jas61r/…` or only writes there. Read, Grep, Write and Edit target the fixture or the plugin copy. The exceptions are the seats' own files: seat 2 wrote and ran its own `mk.py`, `mk2.py` and `mk3.py` in the session scratchpad and stopped its own background task, and seat 3 read its own persisted tool output. One seat 2 call tried `cd C:/Temp/claude/plugin` (no such directory, error suppressed) and then changed into the copy. I read seat 2's first round in full, every call and every result, 09:04:47 to 09:08:35Z. It read the fixture's `AGENTS.md`, git state and files, then the copy's `AGENTS.md`, `Workflow.md` router, `implementation-tdd.md`, `implementation-authority.md`, `CodeReview.md`, the scripts README and the template. It concluded from the fixture alone: the ticket is `PLANNED` with a pending dispatch, the seat branch is unpushed, and there is no receipt, review or queue. A keyword scan of the round found no text describing the test. |
| C5 | What the harness injected, and whether it carried fixture state | **No fixture state; the record's account is incomplete (S61-06).** Every seat received: the user-level and project `CLAUDE.md` and the memory index; this repository's git status, whose commit subjects include `943004ac` ("… part B is rerun clean"); an environment block naming **this repository as the primary working directory** and the session scratchpad; the model, date, commit-attribution, deferred-tool, skill, agent, MCP and auto-mode notices; and the agent system prompt. Scanned for fixture identifiers (the fixture path name, `calc`, `REQ-CALC`, fixture shas, `seat/calc`, `01-subtract`), none matched. Only the git-status subject mentions ticket 61 or the rerun. RUN.md names only the `CLAUDE.md` files, the memory index and the git status. |
| C6 | The plugin copy holds no description of the test | **PASS.** The copy holds no match, under any case or spelling, for wave-2 acceptance, the criterion text, ticket 61, `61-wave2`, the fixture path name, `test_wave2_end_to_end`, `REQ-20261103-043` or "Implementation readiness". Nor does it hold "session break", "mid-ticket", "files alone", "fresh session" or "deliberately ended" in this sense. Compared with the tree at `943004ac`, the copy leaves out `modules/tickets/workflow-governance/`, every `doc/reviews/` directory, `doc/requirements/active/2026/workflow-governance/` and `doc/handoffs/`, as RUN.md says. The remaining `PRD/CHG-20261103-043` mentions (a runbook and specs) concern the merge queue, not the criterion. |
| C7 | Landed commit `d5905ee6`: a merge with parents (`c710d1e`, `4d68e3b`); queue entry `LANDED` | **PASS.** `d5905ee6a828163a85a95d154bbe6df04cbf8835` has parents `c710d1efc04a7955383213ca4d3bd65dbc523cb7` and `4d68e3b1f8ccf22f19ff76a006f7370eb8cf7f0c`, and author `merge-queue`. The queue entry `calc-01-subtract@4d68e3b1…` on `main-queue` is `LANDED`, with `landed_sha d5905ee6…`, reviewer `seat:ticket-review/61r-review` and submitter `seat:implementer/calc-subtract-r3`. `main` `090bee6` differs from `d5905ee6` only in the ticket's state row. |
| C8 | Byte copies equal `origin/main` / `origin/main-queue` | **PASS.** 25 of 25 files under `rerun/fixture/` equal the fixture blobs (24 on `origin/main`, `MERGE-QUEUE.json` on `origin/main-queue`). `git-log-main.txt`, `git-log-main-queue.txt` and `git-show-landed.txt` equal a fresh run of the commands in the collector. `state_after_seat1.txt` equals the run-host copy, and it shows seat 1 stopped with `e54b8df` pushed, `d4fca80` unpushed, and no receipt, review or queue. |
| C9 | RUN.md's account matches the fixture history | **PASS, except the tool-call counts (S61-08).** Every sha, step and verdict in "What happened" matches the graph and the review record: `CHANGES_REQUESTED` on `a09a5d9`; `CONVERGENCE_REVIEW_REQUIRED` on `068a570`; the control-plane note `20d7ce4`; `APPROVED` on `4d68e3b` at `c710d1e`. Every commit to the review record is additive. RUN.md counts 17, 43 and 61 tool calls; the raw transcripts hold 15, 41 and 58. |
| C10 | Rerun review cadence vs CodeReview §5 | **Consistent in count, irregular in labelling (S61-07); landing does not depend on it.** Revision01 got one initial review (`CHANGES_REQUESTED`, with ticket defects). Under §4.3 the ticket defects require a new closure revision before rework, so the first review of the rework (`068a570`) is revision02's initial review, and `c710d1e` is its one correction review. That is within §5's limit of one initial plus one correction per revision. Two things are irregular. First, the control plane dispatched that review as a "correction review", allowing `CONVERGENCE_REVIEW_REQUIRED`, and relabelled it afterwards. Second, its note reads the reviewer's verdict as `CHANGES_REQUESTED`. §5 gives the control plane no such reading: it may only add a rule B `convergence-disposition`, and the reviewer alone owns the conclusion (§2). The note leaves the reviewer's block unchanged. The landed candidate was admitted on the reviewer's own `APPROVED` block for `4d68e3b`, not on the note. |
| C11 | Part A unchanged | **PASS.** The branch and its origin ref are still `4215b980`. The candidate tree is the one reviewed in the initial review, so its cells, mutations and full suite stand. |

### Finding status

| # | Class | Blocks approval | Status after correction 1 | Route |
| --- | --- | --- | --- | --- |
| S61-01 | `EVIDENCE_DEFECT` | no (rule B) | open, carried | Fix at the next change of `tests/test_wave2_end_to_end.py`, as the ticket's Correction 1 records: allow-listed environment, `cwd` = the fixture, a fresh script directory, and pinned script bytes and environment keys |
| S61-02 | `OUT_OF_SCOPE_HARDENING` | no | open, carried | Follow-up `PLANNED` ticket: a committed next-step reader |
| S61-03 | `OUT_OF_SCOPE_HARDENING` | no | open, carried; the rerun shows it again (seat 2 had to propose the review-record name and the queue ticket id) | Template follow-up |
| S61-04 | `OUT_OF_SCOPE_HARDENING` | no | open, carried | With S61-02 |
| S61-05 | `EVIDENCE_DEFECT` | was yes | **closed.** Prompts verbatim (C3), round times (C3), excerpt hashes (C1), and the resume from the files alone confirmed from the raw transcripts (C4, C5) | — |

### New findings

| # | Class | Blocks approval | Closure item | Finding | Route |
| --- | --- | --- | --- | --- | --- |
| S61-06 | `EVIDENCE_DEFECT` | no (rule B: the property holds and was verified from the raw transcripts; the record understates the exposure) | Part B "finished … from the ticket, receipt and queue files alone"; RUN.md "What the harness put in front of every seat" | Two channels were within reach of every seat, and RUN.md mentions neither. (1) The harness named this repository, which holds ticket 61 and both run records, as each seat's primary working directory: a command without an explicit `cd` would have run here. (2) The session scratchpad named to every seat is shared with the control plane. It held the control plane's fixture-building and collection scripts for both runs, and still does. No seat used either channel (C4). | Correct RUN.md's account of the injected context at its next touch. For the wave-3 Codex rerun (criterion 3), start seats with the fixture as working directory and a scratch area of their own. |
| S61-07 | `OUT_OF_SCOPE_HARDENING` | no | CodeReview §5 cadence | The fixture's revision02 review was dispatched as a correction review and relabelled as an initial review only after the verdict came back. The control-plane note then restated the reviewer's `CONVERGENCE_REVIEW_REQUIRED` as `CHANGES_REQUESTED`. That is consistent with §5's count, but §5 provides no such reinterpretation. §5 also does not say that a ticket-defect revision restarts the review count. | Plugin follow-up: state in CodeReview §5 that a new closure revision's first review is its initial review, and that the control plane labels the review before dispatch. |
| S61-08 | `EVIDENCE_DEFECT` | no | rerun/RUN.md accuracy | RUN.md's tool-call counts (17, 43, 61) do not match the raw transcripts (15, 41, 58 by unique id). The excerpts, called "unedited", are LF-normalised; one CR in a tool result was dropped. Neither changes what the record shows. | Correct the counts and add an "LF-normalised" note at the record's next touch. |

### Commands

All reads were local; nothing was written to the repository, the fixture or the run host. Git in the fixture ran with `GIT_OPTIONAL_LOCKS=0`.

- **Hashes.** `sha256sum` of the four files under `C:/Temp/claude/jas61r/run/transcripts/`, compared with `rerun/RUN.md`; `git cat-file blob f6c33831:…/rerun/rounds.txt | cmp - <run-host rounds.txt>`.
- **Transcripts.** The three raw subagent transcripts were parsed with scratch scripts in the session scratchpad (outside the repository):
  - a full readable dump of each;
  - a list of every tool call with the paths it names;
  - a unique-id count of tool calls;
  - a list of every attachment and request blob, each scanned for fixture identifiers;
  - an extract of the injected context;
  - a verbatim and timestamp check of every `prompts.md` block against the round prompts;
  - a block-by-block check of each excerpt against the raw strings and tool inputs.

  Seat 2's first round was read in full.
- **Plugin copy.** Recursive `grep -I` for the terms in C6; the export's file list compared with `git ls-tree -r 943004ac`.
- **Fixture.** `git rev-list --parents -n1 d5905ee6`; `git cat-file blob origin/main-queue:…/MERGE-QUEUE.json`; `for-each-ref` on the bare remote; the review record's history with `git log`, `git diff` and `--numstat`. The sha256 of every `rerun/fixture/` blob at `f6c33831` was compared with `origin/main` or `origin/main-queue`. `git log --graph --format='%h %p %an %s'` and `git show -s --format=…` were compared with the committed text files.
- **Part A.** `git rev-parse cp/wave2-61-wave2-end-to-end` and `git ls-remote origin cp/wave2-61-wave2-end-to-end`.
- **Initial record.** The committed `61-wave2-end-to-end-code-review.md` equals the initial review's record.

### Not verified

- **Seat 1's round, seat 2's rounds 2–4 and seat 3's rounds** were checked through the full tool-call list, the path scan and the keyword scan, not read line by line. Seat 2's round 1 was read line by line.
- **The integrity of the raw transcripts themselves.** They are the harness's files and are taken as raw.
- **The fixture ticket's code and tests.** I did not review these again; the fixture's own reviewer did. My checks covered the landing facts and the record.
- **No full suite and no CI run**, because part A is unchanged.
- **The contents of the control plane's scratch files** in the shared session scratchpad (beyond their names) were not read. My own transcript dumps there were removed at the end of this review, so they cannot become a channel for a later seat.

```review-verdict
candidate: 4215b980bb3dc19dee5c7563f7ed412c97f08464
verdict: APPROVED
reviewer: seat:ticket-review/61-rev01-correction
reviewed_at: 2026-11-12
```
