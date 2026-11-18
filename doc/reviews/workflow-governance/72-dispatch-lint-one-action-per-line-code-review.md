# REVIEW — ticket 72 Dispatch lint: R5 judges one verifiable action per line, not a character cap

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`.** The rule change is correct on every row of the ticket I could probe. Only the three boundary paths change, and nothing forbidden is touched. R1 to R4 and the exit codes are unchanged: the base test file, run unchanged against the candidate script, fails only its two old R5 tests. The two old R5 tests became R6 tests at 2000. R6 is pinned at 2000/2001 inside and outside a fence. `tests/test_wave2_end_to_end.py` passes unchanged. CI run 44354627815 is green on both jobs at the candidate. P9 and E1 pass when I rerun them on the receipt as returned, the tool digests recompute, and the P1, M1, C1 and F1 raw blocks are byte-identical to their captures. Seven of my ten counter-mutations turn a named test red for the intended reason.

Three of my counter-mutations turn nothing red (RM1, RM2, RM3). Under `review-checks.md` point 2, each is a finding (S72-01 to S72-03). None of them is a behaviour defect, because the candidate does the right thing on every probe. They are evidence gaps, and S72-01 is the kind that would let a regression through: the brief's "the `cmd:` exemption ... not to a list item ... containing `cmd:`" is not pinned. The correction is a few subtest values in the existing test file. No finding blocks approval under §5 rule B. This is the initial review, though, so the evidence gaps go back to the seat now, in one additive commit.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/72-dispatch-lint-one-action-per-line.md`, closure revision01, read with `git show 96f095a9:…`. Boundary block: 4 `modify`, 5 `forbid`. "使用者拍板與可觀察結果" is authoritative |
| Spec / requirement | workflow-governance Revision 04 R4-2 (exit meaning 0 pass / 1 red / 3 usage, red before fault); REQ-20261103-043, owner decision 2026-11-18 "B"; lesson L-10 |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-72_dispatch.yaml`, base `96f095a900bf8b6efc554816461dfb1180a7f764`, names revision01. It matches the ticket |
| Candidate | `fe9b02567f52b89cde4a74ca63de843a9cd4cfdc` on `cp/wave3-72-lint`. `git ls-remote origin cp/wave3-72-lint` returns the same sha. It is one commit whose parent is `96f095a9` |
| Commit identity | Author `Johnny Liu <johnny.liu365@gmail.com>`. Trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` (see "Not verified") |
| Review worktree | `.worktrees/72-lint-review`, detached at the candidate. Porcelain was empty before and after. My probe left one ignored `__pycache__/` there, which I removed (see "Raw-log note") |
| Receipt | `.worktrees/72-lint-out/RETURN.md` (50210 bytes, LF, 0 CR). Every cell's candidate is `fe9b0256` |
| CI run | 44354627815, `headSha` = candidate, `test (linux)` success, `test (windows)` success. Read with `gh run view` only |
| References applied | `AGENTS.md` (both P0 sections); `CodeReview.md` (whole file, §5 rule B); `review-checks.md` (test truthfulness with reviewer counter-mutation, token parsing/comparison, missing values, error-code consistency) |
| XSS / privileged JS | Not applicable. This is a command-line text linter with no browser, DOM or JavaScript surface |
| Secret / provider / external effect | Not applicable. There is no secret, log, provider or webhook. The only external effect is the seat's push of its own branch, which the dispatch authorised |
| Agent control / profile fan-out / POC ancestry | Not applicable. There is one implementer seat, no Agent-control path, and no POC or staging |
| P0 source type | `count_actions(line: str) -> int`, no `Any`, no `type: ignore`. `mypy --strict --python-version 3.11` on the script and its test gives exit 0 |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Only boundary paths change; nothing forbidden touched | PASS | `git diff --name-status 96f095a9 fe9b0256` gives `M` for `skills/johnny-project-takeover/scripts/README.md`, `…/scripts/dispatch_lint.py` and `tests/test_gate_dispatch_lint.py`. All three are `modify` lines. `tests/test_wave2_end_to_end.py` is unchanged (`git diff --stat` is empty). Nothing under `library/` or `template/`, and not `Workflow.md`, `AGENTS.md` or `CodeReview.md`. No other gate script is touched |
| 2a | Separator forms: `; ` and `；` | PASS | `SEPARATOR = re.compile(r"; |；")` (`dispatch_lint.py:40`). My probe: `a;  b` → 2, `a;\tb` → 0, `a;<NBSP>b` → 0, `a<U+3000>b` → 0, `"a；b"` → R5. Pinned: two/three actions (`:131`, `:138`), full-width with and without a space (`:143`, RM4 red) |
| 2b | Backtick exemption, including an unbalanced backtick | PASS, but S72-03 | `re.sub(r"`[^`]*`", "``", line)` (`:47`) blanks balanced spans only. Probe: `` x ` y; z `` → R5; `` `a; b` then ` c; d `` → R5 (the pair hides `a; b`, the unbalanced rest is counted); `` run `a` then `b; c` `` → pass. Pinned: `:148` (seat M1-a red), `:153` (my RM9 red), `:156`. Not pinned: a second span (RM3 zero red, S72-03) |
| 2c | `cmd:` exemption only for the value of a field named exactly `cmd` | PASS, but S72-01 | `CMD_FIELD = ^\s*(?:-\s+)?cmd:(\s|$)` (`:39`), matched at line start. Probe: `- run the cmd: a; b` → R5; `Cmd: a; b`, `cmd : a; b`, `cmdx`, `mycmd:`, `note: cmd: a; b` → R5; `  - cmd: a; b` → pass. A `- cmd:` list item is a YAML mapping whose key is `cmd`, so exempting it is right. Pinned: `:159` (seat M1-c red; my RM10 red on `- cmd:`), `:164` for prose and similar names. Not pinned: a list item that only contains `cmd:` (RM2 zero red, S72-01) |
| 2d | Quotes counted | PASS | `count_actions` does not call `strip_quoted`. Pinned: `:169`, double and single quotes (seat M1-b red, 4 failed) |
| 2e | `a;b` is not a separator | PASS | Pinned: `:174`, and `note: one action;` in `:127` |
| 2f | Empty lines and lines of spaces | PASS | `lint` skips them before R2 to R5 (`:73`), and `count_actions` floors at 1. Pinned: `:177` |
| 2g | Fenced code untouched by R5 | PASS | R5 runs after the fence `continue` (`:70-74`). Pinned: `:180` (my RM8 red) |
| 2h | R6 at 2000 and 2001, inside and outside fences | PASS | R6 runs before the fence toggle (`:68-69`), so it covers fence lines, fenced lines and line 1. Probe: outside 2000 → pass, 2001 → R6; inside 2000 → pass, 2001 → R6; a fence marker of 2001 → R6; a 2009-character line with a separator gives R6 and R5. Pinned: `:100` (outside, both sides), `:118` (inside, both sides), `:110` (line 1). Seat M1-d red; my RM5 (old placement) and RM6 (`>=`) red |
| 3 | R1 to R4 and exit codes 0, 1, 3 unchanged; no R1 to R4 assertion weakened | PASS | The diff of `lint` touches only the old R5 lines and the new R6 lines. The base test file (`git show 96f095a9:tests/test_gate_dispatch_lint.py`), run unchanged against the candidate in my clone: 3 failed, 23 passed. The failures are `test_r5_line_length_boundary` and both subtests of `test_r5_applies_to_line_1_of_a_one_line_document`, which are the two old R5 tests. Every R1 to R4, exit-code, encoding and usage test passes unchanged. `git diff -U0` removes only the docstring line, `LINE_LIMIT = 400`, the two `def test_r5_…` lines and their two `["R5"]` assertions |
| 4 | The two old R5 tests became R6 tests; no other changed assertion | PASS | Old names missing at the candidate: exactly those two. They come back as `test_r6_line_length_boundary` and `test_r6_applies_to_line_1_of_a_one_line_document`, with `["R5"]` → `["R6"]` and `LINE_LIMIT` 400 → 2000. The second test's line is now 2008 characters. The STATEMENT names both changes and the docstring. There are 18 new test names: the 16 new tests in the STATEMENT plus the 2 renamed |
| 5 | Every other test that runs `dispatch_lint` | PASS | `grep -rl dispatch_lint` over `tests/`, `doc/`, `skills/` and `.github/`. It is run only by `tests/test_wave2_end_to_end.py:506` (unchanged; its fixture has no separator) and imported only by its own test. `tests/test_gate_repair_guard.py` uses the path as a protected name only. `doc/reviews/…/evidence/48/receipt_check.py` digests the file and does not run it. P1 in my review worktree: 55 passed, 56 subtests passed |
| 6 | Strict type | PASS | `mypy --strict --python-version 3.11` on the script and its test, with the cache in my scratch: `Success: no issues found in 2 source files` |
| 7 | Receipt honesty: P9, E1, digests, raw blocks | PASS | P9 rerun on the full `RETURN.md` against my review worktree: 8 `[ok]` and 1 `[statement]`, `receipt defects: 0`, exit 0. E1 rerun on the receipt as returned, from the dispatch command: `cells=7 defects=0`, exit 0. The `tool_digest` values recompute from the candidate blobs (`git show fe9b0256:<path> \| sha256sum`) for all four tools. The raw blocks of P1, M1, C1 and F1 equal their capture files byte for byte. One recomputed capture digest is `sha256(F1.txt) = 14f89eec6e8f1b98df2e4e46886ff3bcf46fe77cf77e9eb290f0a7ca64edb4ef`, and the extracted F1 block hashes the same. F1's five failures are each in `C:/Temp/claude/jas48_F1_base.txt`. C1 equals my own `gh run view`. The M1 capture records the clone command and each pytest command, and keeps the full FAILURES sections |
| 8 | Seat's convention choices | ACCEPTED, with S72-02 | See "Judgement of the seat's choices" |
| 9 | Reviewer counter-mutations | 10 run; 7 red, 3 zero red (S72-01 to S72-03) | Table below |
| 10 | Seat CI | PASS | Both jobs `success` on the candidate sha |

### Judgement of the seat's choices

- **A full-width `；` counts with or without a following space.** Accepted. This is the literal reading: the ticket attaches "followed by a space" to the half-width form only. It is also the right reading, because CJK text puts no space after `；`. A test pins it, and my RM4 turns it red.
- **A trailing `; ` does not make a second action.** Accepted on intent, with a note. The ticket's sentence "A line holds more than one action when it contains a clause separator" read literally would flag `a; `. A separator with no clause after it does not start a second instruction, though, and `<k>` in the problem line has to count something. Counting non-blank clauses is the consistent choice. The choice makes the gate more lenient than the literal sentence only for a line whose second "action" is empty, so the risk is nil. Two things are open:
  - no test pins the choice (RM1 zero red, S72-02);
  - the convention holds only at the true end of the line. Inside a quoted value, `note: "do a; "` counts 2, because the closing `"` is a non-blank clause, while `note: do a; ` counts 1. Dispatch values are quoted, so in practice the convention rarely applies. This is stricter, not more lenient, so it needs no fix, but the STATEMENT should say it.

### Reviewer counter-mutations

All ten ran in `git clone --no-hardlinks` of the review worktree at `fe9b0256` (`.worktrees/72-lint-review-scratch/72-rev01-initial-clone`). Each ran the whole `tests/test_gate_dispatch_lint.py` without `-x`, using `python -m pytest tests/test_gate_dispatch_lint.py -q -rfE -p no:cacheprovider` directly with no output-reducing wrapper. I read the unfiltered stdout and stderr. Each was restored with `git checkout -- .`, and porcelain was `''` after every one. The diff and full output of each are in `72-rev01-initial-M.txt`. None of these doors is one the seat reported. The seat's four were: separators counted in backticks, quotes exempted, the cmd exemption dropped, 2001 accepted.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| RM1 | Empty-clause handling (the seat's own convention) | `max(1, len(SEPARATOR.split(bare)))`, which drops the non-blank filter | **zero red**: 40 passed, 49 subtests passed. The mutant counts `note: a; ` as 2 where the candidate counts 1 (S72-02) |
| RM2 | Exemption widened (a list item that only contains `cmd:`) | `CMD_FIELD = ^\s*(?:-\s+[^:]*?)?cmd:(\s|$)` | **zero red**: 40 passed, 49 subtests passed. The mutant exempts `- run the cmd: a; b`, which the candidate refuses (S72-01) |
| RM3 | First match (only the first backtick span blanked) | `re.sub(…, line, count=1)` | **zero red**: 40 passed, 49 subtests passed. The mutant counts `` run `a` then `b; c` `` as 2 where the candidate counts 1 (S72-03) |
| RM4 | Full-width needs a space | `SEPARATOR = "; \|； "` | red: `test_r5_full_width_separator_counts_with_or_without_a_space[note: first；second]` |
| RM5 | R6 back in the old R5 place (outside fences only) | R6 check moved after the fence `continue` | red: `test_r6_applies_inside_a_code_fence_too` |
| RM6 | R6 off by one, lower side | `len(line) >= MAX_LINE` | red: `test_r6_line_length_boundary`, `test_r6_applies_inside_a_code_fence_too` |
| RM7 | First match in the count (stops at the first separator) | `min(2, …)` | red: `test_r5_three_actions_are_counted` |
| RM8 | R5 leaks into fences | count and report R5 on fenced lines | red: `test_r5_does_not_apply_inside_a_code_fence` |
| RM9 | An unbalanced backtick hides the rest | backtick span regex `` `[^`]*(`|$) `` | red: `test_r5_an_unbalanced_backtick_does_not_hide_the_rest_of_the_line` |
| RM10 | Exemption narrowed (`- cmd:` no longer exempt) | `CMD_FIELD = ^\s*cmd:(\s|$)` | red: `test_r5_separator_in_a_cmd_value_does_not_count[- cmd: "a; b"]` |

### Judgement of the observation lines

I read every flagged line of `C:/Temp/claude/jas-dispatch/JAS-65_dispatch.yaml` (20) and `JAS-69_dispatch.yaml` (18) at the line numbers in `OBS.txt`. Each count equals the count of non-blank `; `/`；` clauses on that line. The run reports no R1 to R4 and no R6 line. By the rule's intent, holding more than one instruction:

| Kind | Lines (65 / 69) | Judgement |
| --- | --- | --- |
| Packed enumerations in one quoted value (`pytest_rule`, `host_lock`, `mutations`, `prohibited` items, `receipt.rule`) | 15, 16, 18, 25, 26, 27, 62 / 15, 16, 18, 25, 26, 27, 62 | **True positive**, and the rule's main target. `pytest_rule` holds four separate rules: one pytest at a time, the full suite only under the lock, no mutation worker while holding it, stay in turn. `receipt.rule` holds seven. "Put each on its own list item" is the right repair |
| Parenthetical preconditions on a path field (`worktree`, `out_dir`, `scratch`) | 5, 19, 20 / 5, 19, 20 | **True positive.** `worktree` carries three checkable preconditions: branch, HEAD = base, porcelain empty. In `out_dir` the first clause ("receipt and captures") is a label, not an instruction, so `<k>` is one too high, but two real instructions remain |
| Two deliverables in one `summary` or `contracts` item | 4, 29, 31, 33 / 30, 31, 32, 33 | **True positive.** Examples: "remove … ; keep …"; "delete exactly the list; a file outside it … is a CHANGE_DETECTED return"; "refuses repeated keys …; every printed subject escaped" |
| A cell `assert:` that also carries procedure | 50, 53, 56 / 50, 53, 56 | **True positive in intent.** Each has a second instruction: "every other pytest … named in the STATEMENT", "then rebuild the receipt", "E1 runs last". On 53 the middle clause ("the P9 capture is the checker run on the receipt without its P9 section, LF") explains the expectation and is not an instruction, so `<k>` = 3 is one high. The line still holds two |
| `return` item | 65 / 65 | **True positive.** "do not merge, do not remove the worktree; push only this ticket's branch" holds two instructions |
| A rationale clause after `; ` | 30 / — | **False positive.** "every module the cross-lifetime bridge … still imports stays, with its tests; ticket 66 removes those". The second clause is a reason, not an instruction |
| A literal payload that contains `; ` (the commit subject in `commits`) | 58 / — | **False positive.** "refactor(library): retire …; Wayfinder gap rule kept as one function (ticket 65), …". The separator is inside the commit subject the seat must type verbatim. Splitting it as the problem line suggests would change the subject. Writing the subject in backticks avoids it under the current rule |

So 36 of 38 flagged lines hold more than one instruction, and 2 are false positives (JAS-65 lines 30 and 58). Both false positives follow from the owner-decided lexical rule ("quotes count"). The candidate implements that rule faithfully, so neither is a candidate defect. They are input to dispatch authoring (S72-05).

### Findings

| ID | Class | Severity | Blocks? | File:line | Observation | Verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S72-01 | `EVIDENCE_DEFECT` (row "a separator in the value of a `cmd:` field", exemption limited to a field named `cmd`) | Low | No. The candidate is correct. If this is still open after the correction review, rule B carries it to the next change of this gate, because a regression would let a multi-action list item pass | `tests/test_gate_dispatch_lint.py:164-167`; `dispatch_lint.py:39` | The negative cases are `mycmd:`, `note: cmd:` and `cmd2:`. None is a list item. Widening `CMD_FIELD` so that any list item reaching `cmd:` is exempt changes no test result. The candidate itself refuses `- run the cmd: a; b` (probe), so this is evidence only | RM2: zero red | This correction, smallest fix: add `'- run the cmd: a; b'` to the subtest tuple of `test_r5_the_cmd_exemption_is_only_for_a_field_named_cmd` |
| S72-02 | `EVIDENCE_DEFECT` (row 4 of the defect table: `;` followed by a space versus `;` without one; the seat's stated convention) | Low | No. A regression would be stricter, not more lenient | `tests/test_gate_dispatch_lint.py:127-129`; `dispatch_lint.py:48` | The STATEMENT states the convention "a trailing `; ` at the end of a line is not a second action". No test exercises it: `note: one action;` has no space, so it tests the `a;b` row. In addition, the convention does not hold inside a quoted value (`note: "do a; "` → 2), and the STATEMENT does not say so | RM1: zero red; probe | This correction, smallest fix: add `self.assertEqual(dispatch_lint.lint(dispatch("note: one action; ")), [])` to `test_r5_one_action_passes`, and add one STATEMENT sentence on the quoted case |
| S72-03 | `EVIDENCE_DEFECT` (row "a separator inside a backtick span") | Low | No. A regression would be stricter | `tests/test_gate_dispatch_lint.py:148-151`; `dispatch_lint.py:47` | Every exempt-span test has one span. Blanking only the first span changes no test result | RM3: zero red | This correction, smallest fix: add ``"note: run `a` then `b; c`"`` to the subtest tuple of `test_r5_separator_inside_backticks_does_not_count` |
| S72-04 | `OUT_OF_SCOPE_HARDENING` | Low | No | `dispatch_lint.py:39, 45` | The exemption tests the line, not the field. A `cmd:` value written as a YAML block scalar (`cmd: >` and then indented `a; b`) is refused on its continuation line (probe: `R5 line 3 holds 2 actions`). The ticket does not define multi-line values, every dispatch so far writes `cmd:` on one line, and R6 leaves room for that. A false red here is a refusal and never a pass | Probe | Follow-up hardening, or one sentence in the README that a `cmd:` value is one line |
| S72-05 | `OUT_OF_SCOPE_HARDENING` (dispatch authoring, control plane) | Low | No | `C:/Temp/claude/jas-dispatch/JAS-65_dispatch.yaml:30, 58` | The observation run shows two kinds of false positive under the owner-decided rule: a rationale clause after `; `, and a literal payload (a commit subject) that contains `; `. Every wave-3 dispatch also fails the new R5 as written (20 and 18 lines). The next dispatches need the enumerations split into list items | "Judgement of the observation lines" | Control plane, not this ticket (the governance documents and dispatch templates are outside the boundary): tell dispatch authors to put literal payloads in backticks, to drop or comma-join rationale clauses, and to emit enumerations as list items |

### Commands

These ran from the main checkout or the review worktree as noted. Python was `C:/Temp/claude/jas-venv/Scripts/python.exe` with `PYTHONUTF8=1`. Clones, captures and helper scripts are in `.worktrees/72-lint-review-scratch`, each named with `72-rev01-initial`.

- `git rev-parse HEAD`, `git log --oneline -3`, `git diff --stat|--name-status 96f095a9 HEAD` in the review worktree → candidate, one commit, three paths
- `git ls-remote origin cp/wave3-72-lint` → `fe9b0256…`
- `python -m pytest tests/test_gate_dispatch_lint.py tests/test_wave2_end_to_end.py -q -rfEs -p no:cacheprovider` (review worktree, `PYTHONDONTWRITEBYTECODE=1`) → 55 passed, 56 subtests passed
- `python -m mypy --strict --python-version 3.11 <script> <test> --cache-dir <scratch>/72-rev01-initial-mypycache` → exit 0
- the base test file copied into the clone as `tests/test_rev01_base_dispatch_lint.py`, run once and deleted → 3 failed (the two old R5 tests), 23 passed
- comparing the old and new test names (`comm`), and `git diff -U0 … | grep '^-'` → cell 3 and cell 4
- `grep -rln dispatch_lint` and the per-file grep → cell 5
- edge probe → `72-rev01-initial-probe.txt` (cells 2a to 2h, S72-02, S72-04)
- `python -I -X utf8 72-rev01-initial-tools/mutate.py <clone> 72-rev01-initial-M.txt` → RM1 to RM10
- `python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py .worktrees/72-lint-out/RETURN.md .worktrees/72-lint-review` → exit 0
- `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py .worktrees/72-lint-out/RETURN.md --repo .worktrees/72-lint-review --candidate fe9b0256… --tool …/dispatch_lint.py --tool …/evidence_gate.py --evidence-root .worktrees/72-lint-out --require-cell P1 --require-cell T1 --require-cell M1 --require-cell F1` → `cells=7 defects=0`, exit 0
- `git show fe9b0256:<tool> | sha256sum` for the four tools; a block-versus-capture comparison for P1, M1, C1 and F1, with sha256 of each capture
- `grep -c <name> C:/Temp/claude/jas48_F1_base.txt` for each of F1's five failures → all present
- `gh run view 44354627815 --json headSha,conclusion,jobs,url` → candidate, `success`, both jobs `success`
- `sed -n <n>p` of each flagged line in both wave-3 dispatches

### Raw-log note

`72-rev01-initial-M.txt` and `72-rev01-initial-probe.txt` are unedited tool output. I kept them as evidence. Before returning I removed the clone `72-rev01-initial-clone`, the helper directory `72-rev01-initial-tools` (the mutation runner; each mutation's diff is in the M capture), `72-rev01-initial-mypycache` and the intermediate files `72-rev01-initial-base_test.py`, `-old.txt` and `-new.txt`. My first mutation run decoded `git diff` output as cp950 under `-I` and lost three diffs. I fixed the runner and reran all ten, and the capture is from that clean run. CI was read with `gh run view` only. Nothing was pushed, and no workflow run was triggered. No tracked file was modified anywhere. The clone was made with `--no-hardlinks`. My edge probe ran with `-I`, which ignores the host's `PYTHONDONTWRITEBYTECODE`. It wrote one ignored `skills/johnny-project-takeover/scripts/__pycache__/dispatch_lint.cpython-311.pyc` into the review worktree; its timestamp equals the probe's, 02:18:21. I removed it, and porcelain with `--ignored` is empty again. I did not touch the seat's worktree `.worktrees/72-lint`, its scratch `.worktrees/72-lint-scratch` or its clone `r72a-m1clone`, or any other seat's worktree.

### Not verified

- F1 was not rerun: the brief excludes the full suite. F1 is accepted from the seat's locked capture (its five failures are all in the base list) and from CI.
- The seat's M1-a to M1-d were not rerun. My RM1 to RM10 are independent of them, and their captures keep full FAILURES sections.
- A Linux interpreter on this host. Linux behaviour is taken from the CI job.
- The model the trailer names (Claude Sonnet 5.5) against the profile table, which lists Luna/xhigh for `implementation-standard` with "Verify before selection". I cannot read which model the host ran.
- The F1 lock log (`F1.lockinfo.txt`) was not audited line by line.
- The R4-2 table lists `0 / 1 / 2 / 3` for dispatch lint, while the script has no exit 2. The ticket says the exit codes 0, 1, 3 stay "as before", and that is what the candidate does. This predates the ticket and is not judged here.

```review-verdict
candidate: fe9b02567f52b89cde4a74ca63de843a9cd4cfdc
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/72-rev01-initial
reviewed_at: 2026-11-19
```

## Revision01 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`. Every open finding is non-blocking under rule B.** Correction 1 (`8c770265`) closes S72-01, S72-02 and S72-03 as specified. Each pin is the smallest fix the initial review named, and my RM1, RM2 and RM3 reruns now each turn the new subtest red for the intended reason. The S72-04 README sentence is there. S72-05 is unchanged, on the coordinator's instruction. The correction touches only the test file and the README; the receipt was rebuilt outside the tree. The script and `tests/test_wave2_end_to_end.py` are byte-identical to `fe9b0256`. No existing assertion changed. P9 and E1 pass when I rerun them, and CI run 44369248294 is green on both jobs at the candidate.

One of my three new counter-mutations turns nothing red: RM11, which makes the `cmd:` exemption case-insensitive. That is a new evidence gap, S72-06. The candidate behaves correctly (`Cmd: a; b` is refused), so the finding is an `EVIDENCE_DEFECT` and does not block approval under rule B. But a regression through it would let a multi-action line pass. Rule B therefore requires the pin at the next change of this gate, and this review is the second of the closure revision with an evidence defect open. That is what puts the verdict at `CONVERGENCE_REVIEW_REQUIRED` rather than `APPROVED`. No finding changes an exit-code classification, breaks a safety or scope boundary, or violates P0, so the control plane may record a rule B `convergence-disposition`.

| Field | Value |
| --- | --- |
| Ticket | Unchanged: closure revision01 at `96f095a9` |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-72_dispatch.yaml`, unchanged. The coordinator relayed the correction scope |
| Candidate | `8c770265818bc986a20ca9ea50accc16ad56da06` on `cp/wave3-72-lint`. `git ls-remote origin` gives the same sha. It is one additive commit whose parent is `fe9b0256`; there was no amend or force |
| Commit identity | Author `Johnny Liu <johnny.liu365@gmail.com>`. Trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. The seat run id is `r72b` |
| Changed paths (`fe9b0256..8c770265`) | `M skills/johnny-project-takeover/scripts/README.md` (+2/−1) and `M tests/test_gate_dispatch_lint.py` (+7/−2). Both are `modify` lines. `git diff --quiet fe9b0256 8c770265 -- …/dispatch_lint.py tests/test_wave2_end_to_end.py` holds |
| Review worktree | `.worktrees/72-lint-review`, detached at `8c770265`. Porcelain, including ignored files, was empty before and after |
| Receipt | `.worktrees/72-lint-out/RETURN.md` (59531 bytes, LF, 0 CR). Every cell's candidate is `8c770265` |
| CI run | 44369248294, `headSha` = candidate. `test (linux)` success, `test (windows)` success. Read with `gh run view` only |
| References applied | As in the initial review, plus `CodeReview.md` §5 rule B for this correction review |
| XSS / secrets / Agent control / profile / POC | Not applicable, for the same reasons as the initial review |

### Cell results (correction)

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The correction touches only the test file, the README and the receipt | PASS | `git diff --name-status fe9b0256 8c770265` lists two `M` paths, both inside the boundary. The receipt and captures are under `.worktrees/72-lint-out`, outside the tree. The script is unchanged, so there is no behaviour change |
| 2 | No existing assertion changed | PASS | `git diff -U0 fe9b0256 8c770265 -- tests/test_gate_dispatch_lint.py` removes two lines, the two `for body in (…)` tuples. Each is rewritten with all of its original values and one value appended: ``"note: run `a` then `b; c`"`` and `"- run the cmd: a; b"`. One assertion is added, `note: one action; ` passes. Every other line is untouched. The STATEMENT says the correction adds three values and one assertion and changes or removes none, and the diff agrees |
| 3 | S72-01 | CLOSED | `tests/test_gate_dispatch_lint.py:170` adds `- run the cmd: a; b` and expects `["R5"]`. RM2r is red: `SUBFAILED[- run the cmd: a; b] …test_r5_the_cmd_exemption_is_only_for_a_field_named_cmd` |
| 4 | S72-02 | CLOSED | `:130` asserts that `note: one action; ` passes. RM1r is red: `FAILED …test_r5_one_action_passes`. The STATEMENT convention paragraph now says that inside quotes, `note: "do a; "` counts as two actions (stricter, never more lenient). That matches my initial probe |
| 5 | S72-03 | CLOSED | `:150-154` adds ``note: run `a` then `b; c` `` to the exempt tuple. RM3r is red: ``SUBFAILED[note: run `a` then `b; c`] …test_r5_separator_inside_backticks_does_not_count`` |
| 6 | S72-04 | CLOSED (hardening note taken) | README line 26: "A `cmd:` value is a single line, so a multi-line block is refused on its continuation line". This is accurate for a continuation line that holds a separator; one without a separator passes. "Refused" is slightly broad, but it describes a false red, never a pass, so I leave it as is |
| 7 | S72-05 | CARRIED | No change, by the coordinator's instruction. It is a control-plane matter (dispatch authoring) outside this boundary |
| 8 | P1 and strict type | PASS | In the review worktree: `pytest tests/test_gate_dispatch_lint.py tests/test_wave2_end_to_end.py -q -rfEs -p no:cacheprovider` gives 55 passed, 58 subtests passed (two more subtests than at `fe9b0256`). `mypy --strict --python-version 3.11` on the script and its test gives `Success: no issues found in 2 source files` |
| 9 | Receipt: P9, E1, digests, raw blocks | PASS | P9 rerun on the full `RETURN.md` against the review worktree: 8 `[ok]` and 1 `[statement]`, `receipt defects: 0`, exit 0. E1 rerun on the receipt as returned, with the dispatched arguments and `--candidate 8c770265…`: `cells=7 defects=0`, exit 0. All four `tool_digest` values recompute from the `8c770265` blobs. The P1, T1, M1, C1, F1, P9 and E1 raw blocks are each byte-identical to their capture. One recomputed capture digest is `sha256(M1.txt) = dfc17c829555cc64b70679e7eb9caf60b8d69ca16302c8d488b1d82ca7e9611d`. M1 now holds seven mutations, including my RM1 to RM3 as M1-e to M1-g, each red with full FAILURES sections |
| 10 | Seat F1 at the candidate | PASS (not rerun) | 5 failed, 3644 passed. Each of the five names is in `C:/Temp/claude/jas48_F1_base.txt`. The STATEMENT names the other python processes found at lock acquisition, none of which had a pytest child |
| 11 | Reviewer counter-mutations | 6 run; 5 red, RM11 zero red (S72-06) | Table below |
| 12 | Seat CI | PASS | Both jobs `success` on `8c770265` |

### Reviewer counter-mutations (correction)

All six ran in `git clone --no-hardlinks` of the review worktree, checked out at `8c770265` (`.worktrees/72-lint-review-scratch/72-rev01-correction-clone`; porcelain `''` before). Each ran the whole `tests/test_gate_dispatch_lint.py` without `-x`, using `python -m pytest tests/test_gate_dispatch_lint.py -q -rfE -p no:cacheprovider` directly with no output-reducing wrapper. I read the unfiltered output. Each was restored with `git checkout -- .`, and porcelain was `''` after every one. Baseline at the candidate: 40 passed, 51 subtests passed.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| RM1r | Rerun of RM1 (empty clause counted) | `max(1, len(SEPARATOR.split(bare)))` | red: `test_r5_one_action_passes`. Zero red at the initial review |
| RM2r | Rerun of RM2 (exemption widened to a list item that only contains `cmd:`) | `^\s*(?:-\s+[^:]*?)?cmd:(\s\|$)` | red: `test_r5_the_cmd_exemption_is_only_for_a_field_named_cmd[- run the cmd: a; b]`. Zero red at the initial review |
| RM3r | Rerun of RM3 (first span only) | `re.sub(…, line, count=1)` | red: ``test_r5_separator_inside_backticks_does_not_count[note: run `a` then `b; c`]``. Zero red at the initial review |
| RM11 | New: the exact name, by case | `CMD_FIELD = re.compile(…, re.IGNORECASE)`, so `Cmd:` and `CMD:` become exempt | **zero red**: 40 passed, 51 subtests passed. The candidate refuses `Cmd: a; b` (initial probe; the script is unchanged), the mutant admits it (S72-06) |
| RM12 | New: the exact name, by prefix | `CMD_FIELD = ^\s*(?:-\s+)?cmd` (colon and boundary dropped) | red: `test_r5_the_cmd_exemption_is_only_for_a_field_named_cmd[cmd2: "a; b"]` |
| RM13 | New: the exit-code door (R4-2 classification) | `main` returns 0 when every problem is an R5 line | red: `test_r5_exits_1_as_a_process_and_names_the_rule` |

### Findings (status after correction 1)

| ID | Class | Severity | Status | Blocks? | File:line | Observation / verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S72-01 | `EVIDENCE_DEFECT` | Low | **Closed** | — | `tests/test_gate_dispatch_lint.py:170` | `- run the cmd: a; b` is pinned as R5. RM2r is red | — |
| S72-02 | `EVIDENCE_DEFECT` | Low | **Closed** | — | `tests/test_gate_dispatch_lint.py:130`; STATEMENT | The trailing `; ` convention is pinned and the quoted case is stated. RM1r is red | — |
| S72-03 | `EVIDENCE_DEFECT` | Low | **Closed** | — | `tests/test_gate_dispatch_lint.py:150-154` | A second span is pinned. RM3r is red | — |
| S72-04 | `OUT_OF_SCOPE_HARDENING` | Low | **Closed** (README note) | — | `skills/johnny-project-takeover/scripts/README.md:26` | The single-line `cmd:` limit is documented. A real multi-line exemption is still a possible follow-up, but it is not needed | — |
| S72-05 | `OUT_OF_SCOPE_HARDENING` (dispatch authoring) | Low | Carried | No (hardening) | `C:/Temp/claude/jas-dispatch/JAS-65_dispatch.yaml:30, 58` | Unchanged, by the coordinator's instruction | Control plane: dispatch authoring guidance (backtick literal payloads, drop or comma-join rationale clauses, emit enumerations as list items) |
| S72-06 | `EVIDENCE_DEFECT` (row "the value of a `cmd:` field"; the exemption is for a field named exactly `cmd`) | Low | New, open | No. The candidate is correct. It changes no exit-code classification, breaks no safety or scope boundary, and violates no P0. Under rule B it is a gap that would let a regression pass, so it must be pinned at the next change of this gate | `tests/test_gate_dispatch_lint.py:169-172`; `dispatch_lint.py:39` | The negative cases differ from `cmd` by prefix, suffix or position, never by case. A case-insensitive `CMD_FIELD` changes no test result. YAML keys are case-sensitive, so `Cmd:` is a different field. RM11: zero red | Next change of `dispatch_lint.py` (rule B carry). Smallest fix: add `'Cmd: "a; b"'` to the subtest tuple of `test_r5_the_cmd_exemption_is_only_for_a_field_named_cmd` |

### Commands (correction)

- `git log -1 --format='%H %P …'`, `git diff --name-status fe9b0256 8c770265`, `git diff fe9b0256 8c770265`, `git diff -U0 … | grep '^-[^-]'`, `git diff --quiet fe9b0256 8c770265 -- <script> <e2e test>`, `git ls-remote origin cp/wave3-72-lint`
- `python -m pytest tests/test_gate_dispatch_lint.py tests/test_wave2_end_to_end.py -q -rfEs -p no:cacheprovider` (review worktree, `PYTHONDONTWRITEBYTECODE=1`) gives 55 passed, 58 subtests passed
- `python -m mypy --strict --python-version 3.11 <script> <test> --cache-dir <scratch>/72-rev01-correction-mypycache` gives exit 0
- `python -I -X utf8 72-rev01-correction-tools/mutate.py <clone> 72-rev01-correction-M.txt` runs RM1r to RM3r and RM11 to RM13
- `python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py .worktrees/72-lint-out/RETURN.md .worktrees/72-lint-review` gives exit 0
- `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py .worktrees/72-lint-out/RETURN.md --repo .worktrees/72-lint-review --candidate 8c770265… --tool …/dispatch_lint.py --tool …/evidence_gate.py --evidence-root .worktrees/72-lint-out --require-cell P1 --require-cell T1 --require-cell M1 --require-cell F1` gives `cells=7 defects=0`, exit 0
- A block-versus-capture comparison and sha256 for every cell; `git show 8c770265:<tool>` hashed for the four tools
- `grep -c <name> C:/Temp/claude/jas48_F1_base.txt` for F1's five failures
- `gh run view 44369248294 --json headSha,conclusion,jobs,url`

### Raw-log note (correction)

The counter-mutation results above are copied from the unedited capture `72-rev01-correction-M.txt`. That capture, the clone, the runner and the mypy cache all carry this run id, and I removed them before returning, as the coordinator asked. The files of run `72-rev01-initial` are left in place. CI was read with `gh run view` only. Nothing was pushed, and no run was triggered. No tracked file was modified. The host lock was not taken, because no full suite was run. I did not touch the seat's worktree, its scratch or clones, or any other seat's worktree.

### Not verified (correction)

- A reviewer full suite at `8c770265`. It is not required for a test-and-README correction. The seat's locked F1 and both CI jobs cover it.
- The seat's M1-a to M1-g were not rerun as its runs. My RM1r to RM3r reproduce M1-e to M1-g independently.
- The trailer's model against the profile table, as in the initial review.

```review-verdict
candidate: 8c770265818bc986a20ca9ea50accc16ad56da06
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/72-rev01-correction
reviewed_at: 2026-11-19
```

## Convergence disposition (control plane, 2026-11-19)

The correction review returned `CONVERGENCE_REVIEW_REQUIRED`: every blocking finding is closed and the open findings are non-blocking under CodeReview §5 rule B. Each carried finding keeps the smallest fix the reviewer named (lesson L-19).

```convergence-disposition
candidate: 8c770265818bc986a20ca9ea50accc16ad56da06
reviewer_verdict: CONVERGENCE_REVIEW_REQUIRED
disposition: APPROVED
rule: CodeReview §5 rule B (owner-approved 2026-11-05)
carried:
  - S72-05
  - S72-06
```

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, against the expectation the owner confirmed on 2026-11-18 ("1A"); appended to the receipt as `USAGE` cells at integration.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/72-impl` | claude-sonnet-5-5 | 180 | 277222 | 10460409 | 52502 | 10737811 | WITHIN |
| `seat:ticket-review/72-rev01` | claude-opus-5-5 | 110 | 334089 | 7027312 | 70157 | 7361511 | WITHIN |
