# REVIEW — ticket 50 Merge-queue integration script

## Revision01 initial review

**Verdict: CHANGES_REQUESTED.** Under CodeReview §5 rule B, two of the open findings would block approval even after a correction review: S50-01 (TICKET_DEFECT, already with the owner) and S50-02 (IMPLEMENTATION_DEFECT, safety). The rest do not block approval. S50-03 is a gap that would let a bad change through if the code regressed, so it must be closed in the next change to this gate.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/50-merge-queue-integration.md`, revision01 (state row `IN_PROGRESS`, blob at `860057ac`) |
| Closure revision | revision01 (initial review) |
| Candidate | `37bacce9b15cb56d7b0ab667e937df323e2b8f13` on `cp/wave2-50-merge-queue-integration`, one commit on base `9a26eeb133c5a4dd9647cb3fe76d923a83954a12` (the dispatch `base`) |
| Author / trailer | `Johnny Liu <johnny.liu365@gmail.com>`; `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. The trailer names the model that did the work, as the receipt STATEMENT 16 and the dispatch ask, so it is correct. |
| Paths changed | `skills/johnny-project-takeover/scripts/README.md` (M), `skills/johnny-project-takeover/scripts/integrate.py` (A), `tests/test_integrate.py` (A). These match the `johnny-boundary` block exactly; no forbidden path is touched. |
| Receipt | `.worktrees/50-merge-queue-integration-out/RETURN.md` (cells STATEMENT, P1, T1, M1, M1B, F1, P9) |
| Specs read | R4-2 (integration row and red before fault), R4-4 (trust boundary), R4-7 (merge-queue file and review-record block), R4-8 (integration script and its amendments); CodeReview §5 rule B |
| References applied | `CodeReview.md`, `review-checks.md` (including reviewer counter-mutation points 1–5). XSS: not applicable (stdlib CLI, no browser or DOM surface). Agent control: not applicable (the script controls no agent). |
| Reviewer worktree | `.worktrees/50-merge-queue-integration-review`, detached at the candidate; porcelain empty before and after |
| Reviewer | `seat:ticket-review/50-rev01-initial` |
| Environment | Windows 11, `C:/Temp/claude/jas-venv` (Python 3.11), `PYTHONUTF8=1`, Git for Windows |

## Cell results

| # | Check | Result |
| --- | --- | --- |
| 1 | Config keys, queue schema, states, bounce reasons, exit codes | Every key in the configuration table is implemented with its default (`queue_branch` = `<branch>-queue`, `timeout_seconds` = 600). All 11 entry fields, all 6 states, the 4 terminal states, all 5 written bounce reasons and the 3 reds that write nothing are implemented. Exit codes match R4-2 and R4-8: 0 landed, recorded or nothing to do; 1 bounce or red precondition; 2 fault; 3 usage. Red before fault holds in submit, land and readback: a fault never drops a red (pinned by LandBounceTests, ReadbackTests and CM-C below). One deviation: a NaN or Infinity value, or a text-rule break in the config, exits 3 without naming the key (**S50-04**). |
| 2 | submit, land and readback against real git | My own probes ran against local bare remotes. In both race probes the race came from the remote itself: a `pre-receive` hook moved a ref after the ref advertisement, so the script's push code was not mocked. A tip moved this way gives `TIP_MOVED`: the atomic transaction is refused, the tip keeps the hook's value, the candidate is not landed, and the bounce is written on the queue branch only. A queue moved this way gives `QUEUE_MOVED`: the tip is unchanged, the entry stays `QUEUED`, and nothing is written. Queue writes have the queue sha as parent and never touch the tip; `land` lands one entry per run; `BLOCKED_BY_CI` and clearing behave as the ticket says (BlockedByCiTests pass in my P1). |
| 3 | R4-4 integration clone | Each run makes a fresh `git init --template=` and fills it with one fetch carrying `-c transfer.fsckObjects=true -c fetch.fsckObjects=true`. A malformed commit is refused even when it sits only on a seat branch (probe: readback exit 2, `index-pack failed`). The clone is removed on every path. Counter-mutation CM-B2 makes the clone borrow the remote's store through `objects/info/alternates`, so no object crosses the fsck fetch; it turns the forged-object and malformed-object tests red for the intended reason, so the path the run actually uses is pinned. A record that exists only on a seat branch, or only in the candidate's tree, is refused by the real script at submit and at land (probe `seatrec`: exit 1 `REVIEW_MISMATCH`, tip unchanged). The land half of that refusal is not pinned by any test (**S50-03**). A global git config can weaken the fsck (**S50-07**). |
| 4 | Shared rules | The git environment is correct: replace objects, grafts, commit-graph, the listed `GIT_*` variables and every `GIT_CONFIG*` variable are handled, and my reruns RE-P7/P8/P9/P11/P14/P15 are all red for the intended reason. Text values are checked and escaped to one line (RE-O1s and RE-O12 red; RE-O1 and RE-O2 are defence in depth, see M1 notes). The JSON input rules hold, except that a UTF-8 BOM in `pages.json` is a red (**S50-06**). An unwritable stdout gives exit 2: probe with `>&-` exits 2, and RE-O3 is red. Timeouts: `spec_command`, `invariant_command` and `ci_status_command` each run under `timeout_seconds`. On timeout the whole process tree is killed through `taskkill /F /T`. My probe launched the child with `DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP` and gave it a grandchild; both were dead after the 15 s timeout (heartbeat file stopped growing). RE-P2 and RE-P3 are red. The POSIX `killpg` path cannot be exercised on this host (CM-E survives here; it is environment-scoped). |
| 5 | Counter-mutations and the equivalence claims | I ran 25 mutations of my own, one at a time, with unfiltered `-rfE` output; the table is below. I accept both equivalence claims. **R7**: whenever `reviewer == submitter`, the submitter is the `reviewer` of the last matching block, so the "submitter appears as reviewer in a block" problem is always added as well. The admission outcome is the same and only the problem text differs. **R10**: at land the selected block's `candidate` equals `entry.candidate` (it is selected by that equality and `_single`), and `_judge` separately bounces `review_candidate != candidate`, so both comparisons give the same answer. Removing either check alone survives; removing both turns test 845 red. |
| 6 | Receipt | `receipt_check.py` gives exit 0 (0 defects). `evidence_gate.py` with `--tool` for the three wave-1 scripts plus `integrate.py` and `--require-cell P1 T1 M1 F1 P9` gives `cells=6 defects=0`, exit 0. `RETURN.md` and all six captures contain 0 CR (`F1.wait`, which no cell uses, contains 1 CR). Every raw block is byte-identical to its capture. Every `exit:` equals the capture's `exit=` line. Every capture starts with the sha256 of the script it ran, and the tool digests equal the blobs at the candidate. **M1 tails are filtered**: each shard shows only one summary line, with no test names. **17 mutations were judged RED on shards that crashed** with exit 3221225794 (0xC0000142, no output), and the counts around P1 and P2 look like the host collapsing (**S50-05**). |
| 7 | Boundary | Only the declared paths are changed. Author and trailer are correct. Imports are stdlib only (`ctypes` included). No `Any` and no `type: ignore` in the script. No target-project or vendor name appears in the added lines. `tests/test_plugin_payload_boundary.py`: 40 passed, 1 failed, and the failure is `CommittedPinTests::test_the_pinned_sha_exists` only. |
| 8 | Types and suites | `mypy --strict --python-version 3.11` on the script gives exit 0. On the test file (with `MYPYPATH` pointing at the scripts directory) it reports 4 errors, at lines 825, 993, 1013 and 1025. The ticket does not require mypy on the tests (**S50-09**). P1 (`tests/test_integrate.py`): 161 passed, 322 subtests, exit 0, 252 s. F1 under the host lock: 8 failed, 3421 passed, 35 skipped, exit 1. All 8 failures are in the base list (normalised base `^FAILED` names, `LC_ALL=C comm`); zero new red. |

### Reviewer counter-mutations (one disposable copy each, `-rfE`, unfiltered)

| ID | Door | Mutation | Selection | Result |
| --- | --- | --- | --- | --- |
| CM-A | land location | land reads the record through a new method that searches every remote branch | whole file | RED, but for the wrong reason: the new method bypasses the tests' `_record` patch, so every successful-land test fails. Void. |
| CM-A2 | land location | the same search, routed through `Integrator._record` so the patch still applies | whole file | RED only on `SourceRuleTests` (my `type: ignore` comment). Void. |
| **CM-A3** | land location (first match) | CM-A2 without the comment | whole file | **SURVIVED** (161 passed). Against this mutant, probe `seatrec` **lands** a candidate whose only record is on a seat branch. See S50-03. |
| CM-B | trust boundary | the clone borrows the remote's store through alternates | whole file | SURVIVED, but void: my alternates file was written CRLF, so git ignored it |
| CM-B2 | trust boundary | CM-B with the alternates file written LF | whole file | RED: both forged-object and malformed-object subtests (land, readback, submit) |
| CM-C | exit-code door | a readback CI-status fault is reported as a red | ReadbackTests, CommandFaultTests | RED (13) |
| CM-D | overlap | the queue file's text walk is removed | CorruptQueueTests, JsonAndQueueUnitTests | SURVIVED. Equivalent: every field has its own regex that excludes control characters. Defence in depth, not a gap. |
| CM-E | environment-scoped | POSIX `os.killpg` is removed | CommandFaultTests | SURVIVED on Windows. This path runs only on POSIX; not verified here. |
| RE-P2, P3, P4, P7, P8, P9, P11, P14, P15 | seat mutations judged on crashed shards, rerun | as in M1 | CommandFaultTests, ResolveArgvZeroTests, GitEnvironmentTests | all RED, each for the intended reason (tree-kill heartbeat, timeout line, batch subtests, argv and environment spies, `GIT_DIR` real-run test) |
| RE-O1 | output | the subject of a red is not escaped | OutputRuleTests, CorruptQueueTests, ArgumentTests | SURVIVED. Masked by `printable_line`; no subject can hold a backslash (ticket, sha and seat regexes). Equivalent. |
| RE-O1s / RE-O2 / RE-O12 | output | the seat's O1 exactly / the seat's O2 exactly / both together | same | RED / SURVIVED (the seat marked O2 equivalent in advance, but M1 reports it RED on a crash) / RED |
| RE-O3, O4, O6, O7 | output and cleanup | as in M1 | OutputRuleTests, UnexpectedErrorTests, RemoteFaultTests, NormalFlowTests | all RED |

## New findings

| ID | Class | Rule B | Closure item | Finding |
| --- | --- | --- | --- | --- |
| S50-01 | `TICKET_DEFECT` | **blocks** (the script can never land) | ticket "Review record (R4-7)" and the `land` step: the record is read "as the blob at the current remote tip of `branch`", and the candidate must have "the current tip as its ancestor" | This is the conflict the seat reported, now confirmed by the reviewer. A record names its candidate by sha, so a record in the tree of the tip T can never name a descendant of T: the descendant's id contains T's id, which contains the record. My probe `conflict`: with the record committed at the tip and the candidate a sibling, `submit` exits 0 and `land` exits 1 with `NOT_FAST_FORWARD`; a candidate built on top of the record tip cannot be named by it (`submit` exits 1, `REVIEW_MISMATCH`). Read literally, nothing can ever land. The control plane has already routed this to the owner. **Does the `_record` patch hide anything else?** It replaces only the source of the record bytes in the successful-land tests. The fast-forward check, affected specs, commands, the atomic push, the leases and the queue commit all still run against real git, and the land refusals that concern the record location (tests 877 and 883) use the real `_record`. Beyond the conflict, it hides one thing: no test pins *where* `land` reads the record (S50-03). |
| S50-02 | `IMPLEMENTATION_DEFECT` | **blocks** (safety: authorization bypass through an indirect entry, defect class 3) | ticket `land`: "re-reads the review record at that tip (else BOUNCED REVIEW_MISMATCH), computes the affected specs …, runs `spec_command` …"; R4-4 "the review APPROVED is its admission"; class 3 "a candidate landing without its own approved record" | `_judge` runs `spec_command` and `invariant_command` whenever the candidate is a fast-forward, even after it has found `REVIEW_MISMATCH`. The configured commands then execute code from the candidate's tree (its `test_*.py` specs) inside the integration runner, with the runner's own credentials, before any approval exists. The queue branch is an ordinary branch on the shared remote, so a seat can write a `QUEUED` row directly. Probe `unapproved`: such a row was written with no submit and no record anywhere, then `land` was run. It exited 1 with `REVIEW_MISMATCH`, and the candidate's spec had written its marker file. Because of S50-01, this currently happens on every real land. The STATEMENT (item 6) presents running the commands after a review red as red before fault; test 942 pins that behaviour. Fail-closed reading: when `NOT_FAST_FORWARD` or `REVIEW_MISMATCH` is found, run no configured command on the candidate and report the reds already found. If the control plane reads red before fault as requiring the commands, this becomes a ticket question, and it blocks either way. |
| S50-03 | `EVIDENCE_DEFECT` | does not block on its own, **but would let a bad change through if the code regressed: close it in the next change to this gate** | TDD 4 "a review record read from the candidate branch instead of the tip is not accepted"; defect class 3 (indirect) | The real script reads the record at the tip (probe `seatrec`: exit 1). No test pins this for `land`. Test 668 covers only `submit`. Tests 877 and 883 cannot tell "the tip" from "any branch that holds the path". CM-A3, a land-only read of the record from any remote branch, passes all 161 tests, and against that mutant probe `seatrec` lands a candidate whose only record a seat pushed to its own branch (`LANDED_PENDING_CI`, tip moved). Needed: a land test with the approving record only on a seat branch that descends from the candidate, expecting `REVIEW_MISMATCH` and an unchanged tip. Whatever the owner decides for S50-01 moves where the record is read, so this test must pin the new location. |
| S50-04 | `IMPLEMENTATION_DEFECT` | does not block (exit 3 is correct) | ticket configuration: "`NaN`/`Infinity` and text-rule breaks are exit 3 naming the key"; the README says the same | Probe `config`: `config: NaN is not allowed`, `config: Infinity is not allowed`, `config holds a control character (U+0009)`, `config holds a lone surrogate (U+D800)`. None of these messages names the key. Tests 1719 and 1738 call `usage()` without `key`, so the property is not pinned either. |
| S50-05 | `EVIDENCE_DEFECT` | does not block (my reruns show the candidate behaves correctly) | completion definition, M1 ("for each bounce reason and each rule above remove its check → its test red"); review-checks point 5 | M1 reports "94 mutations, 92 red". For P3, P4, P7, P8, P9, P11, P13, P14, P15 and O1–O7, all eight shards exited 3221225794 (0xC0000142, a process that failed to start) and printed nothing, yet each is marked `RESULT …: RED`. P2 had six such shards. P1 (95 failures in about 13 s per shard), E7 and E8 have failure counts that no single-rule mutation can explain. The capture keeps one summary line per shard and no test names, so the reason for any red cannot be read. The seat's equivalence list says O2 was "marked equivalent in advance", but the capture says RED. I reran the git-environment, tree-kill, timeout, batch and output mutations myself (all red for the intended reason except RE-O1 and RE-O2, which are equivalent). The receipt must rerun every mutation whose shards crashed, or whose counts show the collapse, and keep the failing names (`-rfE`), one pytest at a time. |
| S50-06 | `IMPLEMENTATION_DEFECT` | does not block (a false red, not red/fault confusion) | ticket JSON rule: only "a BOM-less non-UTF-8 byte" is an input error | `parse_pages` decodes `pages.json` with plain `utf-8`. A target project whose `pages.json` starts with a UTF-8 BOM therefore bounces every candidate `SPEC_RED` (probe `pagesbom`: `Unexpected UTF-8 BOM`). The config accepts a BOM (`utf-8-sig`), and so do the other wave-2 gates. The queue file's refusal of a BOM is a schema choice for a file only the script writes, and I accept it. |
| S50-07 | `OUT_OF_SCOPE_HARDENING` | does not block; touches R4-4, so the control plane may want to lift it into the ticket | R4-4 trust boundary (the ticket's git environment list is met literally) | The script removes every `GIT_CONFIG*` variable but still reads the global and system git config. Probe `fsck`: `HOME/.gitconfig` with `[fetch "fsck"] badEmail = ignore` makes the verified fetch accept the malformed commit, so `readback` exits 0 where it exits 2 without that file. A seat that runs as the same OS user can write that file. Suggestion: after the scrub, set `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL` to a fresh path that does not exist, the same way `GIT_GRAFT_FILE` is handled. |
| S50-08 | `OUT_OF_SCOPE_HARDENING` | does not block | R4-4 (availability) | The fetch takes `+refs/heads/*`, so one malformed object on any seat branch makes every `submit`, `land` and `readback` exit 2 until it is removed (probe `fsck`). Fetching only `branch`, `queue_branch` and the branches that hold queued candidates would limit this. |
| S50-09 | `OUT_OF_SCOPE_HARDENING` | does not block | not required by the ticket (mypy is required on the script only) | `mypy --strict` on `tests/test_integrate.py` reports 4 errors: line 825 (`mock.patch.object` given a callable typed `None`) and lines 993, 1013 and 1025 (`Callable[[], str]` passed where `Callable[[], None]` is expected). |

Other notes, not findings:

- The STATEMENT choice to accept a convergence disposition only with the verdict `CONVERGENCE_REVIEW_REQUIRED` is narrower than the ticket text. It matches every real record in `doc/reviews/workflow-governance` (tickets 51 to 54), and I accept it.
- Accepting `green\r\n` as "one trailing newline" is acceptable on Windows.
- Over-inclusion in spec naming is the safe direction. A spec that names `x/src/a.py` counts as naming `src/a.py`, because `/` is not excluded on the left.

## Commands

```text
# baseline P1 (review worktree)
sha256sum skills/johnny-project-takeover/scripts/integrate.py; python -m pytest tests/test_integrate.py -q -p no:cacheprovider -rfE      -> 161 passed, 322 subtests, exit=0
python -m mypy --strict --python-version 3.11 skills/johnny-project-takeover/scripts/integrate.py                                      -> exit=0
MYPYPATH=skills/johnny-project-takeover/scripts python -m mypy --strict --python-version 3.11 tests/test_integrate.py                     -> 4 errors
python -m pytest tests/test_plugin_payload_boundary.py -q -p no:cacheprovider -rfE                                                     -> 1 failed (test_the_pinned_sha_exists), 40 passed
python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py <out>/RETURN.md <review worktree>                        -> 0 defects, exit=0
python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py <out>/RETURN.md --repo <review worktree> --candidate 37bacce9b15cb56d7b0ab667e937df323e2b8f13 \
  --tool .../dispatch_lint.py --tool .../receipt_fence_check.py --tool .../index_pins.py --tool .../integrate.py \
  --require-cell P1 --require-cell T1 --require-cell M1 --require-cell F1 --require-cell P9 --evidence-root <out>                       -> cells=6 defects=0, exit=0
# own byte checks: CR count, raw block == capture, exit: == capture exit= ; blob sha256 of the four tools at the candidate
# probes (scratch/probe.py, local bare remotes, in-process; _record patched only where a land must pass the review step)
probe.py base/... . conflict seatrec config | race fsck timeout stdout | unapproved pagesbom ; probe.py mutA2 . seatrec
# counter-mutations (scratch/cm_driver.py): one copy per mutation, python -m pytest <selection> -q -p no:cacheprovider -rfE, sequential
# F1 under the host lock (mkdir C:/Temp/claude/jas-fullsuite.lock, run id 50-rev01-initial; waited for jas59-f1-1132937-1793898973;
# acquired 2026-11-05T17:34:58Z, released 2026-11-05T18:01:44Z after checking it still named this run)
python -m pytest tests -q -p no:cacheprovider -rfE                                                                                    -> 8 failed, 3421 passed, 35 skipped, exit=1; new vs base: none
```

## Raw-log note

The reviewer captures are in `.worktrees/50-merge-queue-integration-review-scratch/`:

- `P1.txt`, `F1.txt` and `F1.wait` (lock wait log, with the other pytest command lines seen on the host);
- `payload.txt`;
- `probe-1.txt` to `probe-6-mutA2.txt`;
- `cm/<ID>.txt` (diff and full pytest output for each mutation), plus `cm-run*.log`.

They are not committed. No output-reducing wrapper was used: pytest ran directly with `-rfE`, and every judgement above was read from the full output.

While these runs were going, the host also ran the full suites of `jas60` and `jas59` and single-file runs of other seats. That load came from the gates of tickets 51 to 57, the governance consistency tests and the state-file templates.

## Not verified

- POSIX behaviour: the `killpg` tree kill (CM-E is environment-scoped) and executable-bit lookup. Linux CI (ticket 59) was not run.
- A remote over a network transport (ssh or https). Every probe used a local path.
- A SHA-256 remote end to end. I rely on the seat's `RecordedBehaviourTests`, which pass in my P1.
- Whether the owner's resolution of S50-01 keeps or changes the other land rules. S50-02 and S50-03 must be re-judged against that resolution.

```review-verdict
candidate: 37bacce9b15cb56d7b0ab667e937df323e2b8f13
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/50-rev01-initial
reviewed_at: 2026-11-06
```
