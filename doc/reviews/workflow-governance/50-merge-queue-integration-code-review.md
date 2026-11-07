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

## Revision02 initial review

**Verdict: CHANGES_REQUESTED.** The revision02 work does what it set out to do. Merge landing works against real git with no patch of `Integrator._record`. No configured command runs before admission, before a clean merge, or for an entry that is `ALREADY_LANDED`. S50-01 to S50-09, S58-04 and S60-01 are closed.

One new finding blocks approval under CodeReview §5 rule B: **S50-10**, an `IMPLEMENTATION_DEFECT` that misclassifies the exit code. When a candidate is fetched by its sha and that verified fetch fails, the script ignores the failure, so a fault is reported as a `MERGE_CONFLICT` red and a bounce is written. The other new findings do not block approval.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/50-merge-queue-integration.md` at `5cb8efef`; its Revision02 section replaces every fast-forward statement above it |
| Closure revision | revision02 (initial review; new cadence after the owner decision "1.A" of 2026-11-07) |
| Spec | `modules/spec/workflow-governance.md` at `5cb8efef`: R4-2, R4-4, R4-7 and R4-8 as amended, signature row 2026-11-07 |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-50b_dispatch.yaml` |
| Candidate | `26b6cc9a04eb0b4d46296528679bcd8887a63cac`: three additive commits on `37bacce9`. `5eccf309` changes the script, README and tests; `0ebcbcb8` and `26b6cc9a` change tests only. |
| Author / trailer | All three commits are by `Johnny Liu <johnny.liu365@gmail.com>`. Each carries `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, which names the model that did the work, so the trailer is correct. |
| Paths changed (`9a26eeb1..26b6cc9a`) | `skills/johnny-project-takeover/scripts/README.md` (M), `skills/johnny-project-takeover/scripts/integrate.py` (A), `tests/test_integrate.py` (A). These are exactly the three declared paths. |
| Receipt | `.worktrees/50-merge-queue-integration-out-r2/RETURN.md` (cells STATEMENT, P1, T1, M1, M1B, F1, P9), with `E1.txt` |
| Script digest at candidate | `integrate.py` sha256 `08ac7a3fab751016c508794a6b977970b4e61cab94219d585c57b88b4f5a8f91`, equal to every capture's first line and to `tool_digest` |
| Reviewer worktree | `.worktrees/50-merge-queue-integration-review`, detached at the candidate; porcelain empty before and after |
| Reviewer | `seat:ticket-review/50-rev02-initial` |
| Environment | Windows 11, git 2.54.0.windows.1, `C:/Temp/claude/jas-venv` (Python 3.11), `PYTHONUTF8=1` |

## Cell results

| # | Check | Result |
| --- | --- | --- |
| 1 | Land order, `landed_sha`, reasons, real-git land | `_judge` follows the order the dispatch asks for. (1) The record is read at the tip; any review red or record-read fault returns at once. (2) The candidate is fetched (only now). (3) An object that is not a commit gives `MERGE_CONFLICT`. (4) `merge-base --is-ancestor candidate tip` gives `ALREADY_LANDED`. (5) A candidate with no shared history gives `MERGE_CONFLICT`. (6) `merge-tree --write-tree` exit 1 gives `MERGE_CONFLICT`. (7) `commit-tree` with the tip as first parent. (8) Specs, then invariants, on the merged tree. (9) One atomic push with two leases. `landed_sha` is the merge commit. `NOT_FAST_FORWARD` is gone from the code, the queue schema and the README; `MERGE_CONFLICT` and `ALREADY_LANDED` are bounce reasons the queue accepts. Probe `land` used real git and no patch: the record sits on the tip and the candidate is a sibling. `submit` exits 0; `land` exits 0 with `LANDED_PENDING_CI`; the merge commit's parents are (tip, candidate); its tree equals `git merge-tree --write-tree tip cand`; `landed_sha` is the merge; the commands saw `specs/test_a.py`; `readback` gives `LANDED`. A new key for the same candidate then gives `ALREADY_LANDED` with no command. |
| 2 | S50-02: no candidate code before admission | Probe `unapproved` writes a QUEUED row with no record; the candidate's spec would write a file. Result: exit 1 `REVIEW_MISMATCH`, no configured command, the candidate's code never runs, tip unchanged. Probe `bounces` covers six cases: a conflicting candidate, an unrelated-history candidate, a blob, a missing sha, an ancestor of the tip and the tip itself. Each gives `MERGE_CONFLICT` or `ALREADY_LANDED` with the commands not run and the tip unchanged. **Merge drivers and attributes.** In a plain non-bare repository whose worktree holds the candidate's `.gitattributes` (`* merge=evil filter=evil`) and whose `HOME` config defines `merge.evil.driver`, `git merge-tree --write-tree` *does* run the driver (positive control: the driver ran and resolved the conflict). In the script both preconditions are missing. `merge-tree` runs in a fresh clone before any checkout, so no worktree attributes exist. Every git child has `GIT_CONFIG_NOSYSTEM=1` and a `GIT_CONFIG_GLOBAL` that does not exist, so no driver or filter is defined; `git config --list --show-origin` under the script's environment shows no global, XDG or system file. Probe `driver`: the same candidate, the same `HOME` driver and a `.gitconfig` inside the candidate tree give `MERGE_CONFLICT`, and the driver never runs. The checkout of the merged tree, where filters could apply, happens only after admission and a clean merge. |
| 3 | Merge mechanics | `merge-tree --write-tree --no-messages tip cand`, then `commit-tree <tree> -p tip -p cand -m "merge-queue: land <key>"`. Parents and tree are verified (probe `land`). **Identity** comes only from the script's `IDENTITY` table, passed in the environment of the `commit-tree` child (`merge-queue <merge-queue@integrate.invalid>`, author and committer). With it removed (CM-I) git has no identity, because global and system config are not read, and every land faults: red. Inherited `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` would pass through, which is harmless. **A missing candidate, a non-commit, or unrelated history** each give `MERGE_CONFLICT` and nothing runs (probe `bounces`). **Fetch by sha** is confined: it has no destination refspec, so objects land only in the clone's store, under both fsck options. Probe `bysha`: a candidate that is not a branch tip lands; the seat branch's later commit is not landed; every other remote ref is unchanged; the scratch area is empty afterwards. **The failure path of that fetch is not confined to faults (S50-10).** **git < 2.38**: the script has no version check and the README does not state the requirement; only STATEMENT 2 does. Simulated at the process boundary (merge-tree exiting 129 with its old usage line), the run exits 2 with `git merge-tree failed with exit 129: usage: git merge-tree <base-tree> <branch1> <branch2>`; the queue and tip are unchanged and nothing runs. It fails closed, but the message does not name the requirement (S50-14), and no test pins it (S50-11). |
| 4 | The seat's other choices | A fault while reading the record now ends the run with exit 2, nothing is written and no command runs. This replaces old test 975 (`test_a_fault_in_the_review_read_runs_no_command_and_is_exit_two`; seat N04 is red). I accept it: nothing is admitted, so nothing may run, and red before fault still holds because no red was found. `GIT_DISCOVERY_ACROSS_FILESYSTEM` is no longer removed. The removed list is now exactly the thirteen names of `evidence_gate.py` `GIT_REMOVED_VARIABLES`, plus every `GIT_CONFIG*` and `GIT_TEST_*` name, which matches the Revision02 row for S58-04 and S60-01. The variable only widens repository discovery, and every child runs with `-C` into the clone, so dropping it from the list is harmless. Accepted. |
| 5 | Closure of S50-03..09, S58-04, S60-01 | See the status table. Probe `fsck`, every result read from unfiltered output. A malformed commit on an unrelated seat branch: `readback` exit 0, `land` exit 0. A malformed tip: exit 2. A malformed tip with `HOME/.gitconfig` and `XDG_CONFIG_HOME/git/config` both setting `fetch.fsck.badEmail = ignore`: still exit 2. Control: a plain `git fetch` with that `HOME` exits 0, so the configuration really would weaken the fetch. The narrowed fetch takes `refs/heads/<branch>` and, when it exists, `refs/heads/<queue_branch>`. The record is a blob on the tip, so it is fetched (probe `land` reads it with no patch). The candidate is fetched after admission. Nothing land needs is missing. |
| 6 | M1 | 60 mutations at the candidate in a `git clone --no-hardlinks` copy, one pytest per run, the full file with `-rfE --tb=line --maxfail=1`. I read every mutation's diff and its first failing test or subtest in the unfiltered capture; all 57 reds are red for the intended reason (table below). `--maxfail=1` shortens each run but does not filter its output: the failing name and its assertion are kept. **N02** (land-time `review_candidate` vs candidate removed) is equivalent, the same argument as R10: the selected block's candidate equals the candidate and `check_review` compares the row copy with that block; N02b (both removed) is red. Accepted. **O2** (`printable_line` dropped) is equivalent: every string is escaped where it is built (`escape`, `shown`, `_config_error`), as my RE-O2 found in revision01, and O1 (the escaper itself) is red. Accepted as defence in depth. **O5** (`except KeyboardInterrupt` removed) lets the interrupt escape the mutant, and pytest aborts the session in the interrupt test after 181 passed, three times. Not counting it, and adding O5b (caught but not reported; red in `M1B.txt` at the interrupt test), is correct. No run crashed. |
| 7 | Receipt | `receipt_check.py RETURN.md <review worktree>`: 0 defects, exit 0. `evidence_gate.py` with `--tool` for the three wave-1 scripts and `integrate.py`, and `--require-cell` P1, T1, M1, M1B, F1 and P9: `cells=6 defects=0`, exit 0. `RETURN.md` and all seven captures (P1, T1, M1, M1B, F1, P9, E1) contain 0 CR. Every raw block is byte-identical to its capture. Every `exit:` equals the capture's `exit=` lines in order. **E1 was written last**: `E1.txt` at 08:44:51, after `RETURN.md` at 08:44:41 and P9 at 08:44:40, and every capture is later than the last commit (05:33:44). The seat's F1 holds 8 failures, all in the base list. The M1 cell's `exit: 0,0` records the clone and checkout; the mutation verdicts are in the capture body. That is how the cell is defined, and I note it only so the 0 is not read as "no red". |
| 8 | Boundary, types | Only the three declared paths are changed. All commits are by Johnny Liu. Imports are stdlib only. There is no `Any` and no `type: ignore` in the script, and the added lines name no target project and no vendor. `mypy --strict --python-version 3.11` on the script and the test file: `Success: no issues found in 2 source files`, exit 0. |
| 9 | Suites | P1 (`tests/test_integrate.py -rfEs`): 194 passed, 344 subtests, exit 0, 270 s. F1 under the host lock (run id `50-rev02-initial`, acquired 2026-11-07T01:19:40Z with no other pytest running, released 01:33:44Z by renaming the lock and then removing it, after checking owner.txt): 8 failed, 3454 passed, 35 skipped, exit 1. All 8 failures are in the base list (`LC_ALL=C comm -23` against the normalised `^FAILED` names): zero new red. My counter-mutations ran before and after the lock, never while I held it. |

### Probe table (real git, local bare remotes; no patch of `Integrator._record` except where stated)

| Probe | Setup | Result |
| --- | --- | --- |
| land | record on the tip, candidate a sibling; `submit`, `land`, `readback`, then a new key for the same candidate | submit 0; land 0 `LANDED_PENDING_CI` with landed_sha = merge; parents (tip, cand); tree = `merge-tree` tree; identity `merge-queue`; commands ran on the merge; readback `LANDED`; new key `ALREADY_LANDED`, no command |
| seatrec | approving record only on a seat branch descending from the candidate | exit 1 `REVIEW_MISMATCH`, tip unchanged, no command, entry `BOUNCED REVIEW_MISMATCH` |
| unapproved | QUEUED row written directly, no record anywhere, candidate spec writes a file | exit 1 `REVIEW_MISMATCH`, no command, candidate code not run, tip unchanged |
| bounces | conflict, unrelated history, blob, missing sha, ancestor, the tip itself (each with an approving record) | `MERGE_CONFLICT` ×4, `ALREADY_LANDED` ×2; each exit 1, no command, tip unchanged |
| race (main) | `pre-receive` hook moves `main` after the advertisement | exit 1 `TIP_MOVED`; atomic transaction refused; `main` keeps the hook's value; bounce written on the queue branch only |
| race (queue) | the hook rewinds the queue branch | exit 1 `QUEUE_MOVED`; `main` unchanged; entry stays `QUEUED`; nothing written |
| fsck | malformed commit on an unrelated seat branch / on the tip / on the tip with global and XDG `badEmail=ignore` | readback 0 and land 0 / exit 2 / exit 2 (control: a plain fetch with that config exits 0); a git child reads no global, XDG or system config |
| driver | candidate `.gitattributes` `merge=evil filter=evil`; driver defined in `HOME` config / in the candidate's own `.gitconfig` | the driver never runs; `MERGE_CONFLICT`; positive control in a plain worktree repository runs the driver |
| bysha | candidate is an ancestor of its seat branch's tip | lands by sha; parents (tip, cand); the later seat commit is not landed; other refs unchanged; clone removed |
| badsha | malformed candidate commit, (a) not a branch tip, (b) a branch tip | **(a) exit 1 `MERGE_CONFLICT`, bounce written**; (b) exit 2 fault, nothing written (S50-10) |
| unadm-bad | no record; the candidate's branch tip is malformed | exit 1 `REVIEW_MISMATCH`; the candidate is not fetched before admission |
| oldgit | `merge-tree` answers exit 129 with the pre-2.38 usage line (simulated at `run_process`) | exit 2, one fault line; queue and tip unchanged; no command |
| config | NaN, Infinity, TAB, U+0000, a lone surrogate in values | exit 3, each message `config key `<key>`: …` |
| pagesbom | `pages.json` with a UTF-8 BOM | accepted |

### Reviewer counter-mutations (one disposable copy each, full file, `-rfE`, one pytest at a time)

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| CM-A3r | land location (first match) | the clone fetches every branch again, and land alone takes the record from whichever branch holds it | **RED**: `AdmissionTests::test_a_record_that_only_a_seat_branch_holds_is_review_mismatch_at_land` (plus three fetch-scope tests). S50-03 is pinned. |
| CM-B2r | trust boundary | the clone borrows the remote's store through alternates (LF) | RED: forged-object, malformed-object, global-config and candidate-branch fsck tests (7) |
| CM-G | order | the candidate is fetched (again) before the record is read | RED, but only through the fetch-count spies (3 != 2); not judged as pinning the order, see CM-G2 |
| CM-G2 | order / exit code | the one candidate fetch is moved before the record read (same count) | **SURVIVED** (194 passed). See S50-13. |
| CM-I | identity | `commit-tree` without the script's identity | RED: every successful land faults (`git commit-tree` has no identity) |
| CM-Q | exit-code class | any `merge-tree` failure (an old git's exit 129 included) becomes `MERGE_CONFLICT` | **SURVIVED** (194 passed). See S50-11. |
| CM-R | order (step 1 before step 2) | for a record that does not admit, `ALREADY_LANDED` is decided first and replaces `REVIEW_MISMATCH` | **SURVIVED** (194 passed). See S50-12. No command runs in either order. |

### Status of the revision01 findings

| ID | Class | Status | Evidence |
| --- | --- | --- | --- |
| S50-01 | TICKET_DEFECT | **closed** | Owner decision "1.A" and the spec amendments; probe `land` lands a sibling of the record commit with no patch; `RealLandTests` asserts the method is unpatched |
| S50-02 | IMPLEMENTATION_DEFECT (safety) | **closed** | `_judge` returns before fetch, merge or command on any review red or record fault; probes `unapproved`, `bounces`, `driver`; seat N03 and N04 are red |
| S50-03 | EVIDENCE_DEFECT | **closed** | `test_a_record_that_only_a_seat_branch_holds_is_review_mismatch_at_land`; my CM-A3r is red on it |
| S50-04 | IMPLEMENTATION_DEFECT | **closed** | probe `config` names the key for every case; seat N29–N32 are red |
| S50-05 | EVIDENCE_DEFECT | **closed** | M1 rerun one pytest at a time, unfiltered; the crash rule was applied (O5 not counted, O5b red); every red read for its reason |
| S50-06 | IMPLEMENTATION_DEFECT | **closed** | `utf-8-sig`; probe `pagesbom` accepted; seat N17 is red |
| S50-07 | OUT_OF_SCOPE_HARDENING | **closed** | `GIT_CONFIG_NOSYSTEM=1` and a fresh `GIT_CONFIG_GLOBAL` per child; probe `fsck` with global and XDG `badEmail=ignore` still exits 2; seat N24 and N25 are red |
| S50-08 | OUT_OF_SCOPE_HARDENING | **closed** | fetch of branch and queue branch by name, candidate after admission; probe `fsck` unrelated branch: exit 0; seat N23b is red |
| S50-09 | OUT_OF_SCOPE_HARDENING | **closed** | mypy strict clean on both files |
| S58-04, S60-01 | routed | **closed** | removed list = the evidence gate's 13 names + `GIT_CONFIG*` + `GIT_TEST_*`; seat N26–N28 are red |
| S57-05 | routed | carried, as the ticket says | (not in this candidate's tree) |

## New findings

| ID | Class | Rule B | Closure item | Finding |
| --- | --- | --- | --- | --- |
| S50-10 | `IMPLEMENTATION_DEFECT` | **blocks** (exit-code misclassification: a fault reported as a red) | R4-2 "a tool fault is never reported as a red"; ticket TDD 3 "a forged object … makes the fsck clone fail → exit 2, nothing pushed"; R4-4 verified fetch | `Clone.fetch_candidate` raises a fault for a failed fetch only when a branch points at the candidate (`if fetched.code != 0 and heads`). When the candidate is fetched by its sha, any failure is ignored, fsck failure included. The candidate is then missing and the entry is bounced `MERGE_CONFLICT`. Probe `badsha` used the same malformed candidate commit twice. As a branch tip it gives exit 2 (`the verified fetch failed: fatal: index-pack failed`), nothing written, entry still `QUEUED`. As the parent of a branch tip it gives exit 1 `MERGE_CONFLICT`, and a permanent `BOUNCED` entry is written on the queue branch. Any other failure of the by-sha fetch is turned into the same red: a dropped connection, a timeout below the git limit, or a remote that refuses unadvertised wants (STATEMENT 6 names that last case). Fix: treat a failed by-sha fetch as a fault unless the remote says it does not hold the object. Pin both shapes. |
| S50-11 | `EVIDENCE_DEFECT` | does not block (the code is right today; but a regression here would turn a fault into a red) | R4-2 exit classes; ticket "every git … failure caught → exit 2" | CM-Q, which makes any `merge-tree` failure a `MERGE_CONFLICT` (an old git's usage exit 129 included), passes all 194 tests. The real code faults (probe `oldgit`: exit 2, nothing written). Needed: a test where `merge-tree` fails with an exit other than 0 or 1 and the run exits 2 with nothing written. |
| S50-12 | `EVIDENCE_DEFECT` | does not block | ticket Revision02 land steps 1 then 2 | CM-R passes all 194 tests. In CM-R a candidate the record does not admit, but which the tip already contains, is recorded `ALREADY_LANDED` instead of `REVIEW_MISMATCH`. No command runs in either order, so this is the recorded reason only. Needed: a land test with a non-admitting record for a candidate the tip contains, expecting `REVIEW_MISMATCH`. |
| S50-13 | `EVIDENCE_DEFECT` | does not block (the code is right today; but a regression here would turn a red into a fault) | ticket Revision02 step 1 ("no configured command runs" — the candidate is touched only after admission); R4-2 exit classes | CM-G2 moves the single candidate fetch in front of the record read and passes all 194 tests. Nothing pins that the candidate is touched only after admission. The real code is right (probe `unadm-bad`): with no record and a malformed object at the candidate's branch tip, the run exits 1 `REVIEW_MISMATCH`. Under CM-G2 the same entry would be an exit-2 fault and the record red would not be found. Needed: that probe as a test (unadmitted entry, malformed candidate branch, expect `REVIEW_MISMATCH` and no fault). |
| S50-14 | `OUT_OF_SCOPE_HARDENING` | does not block | not in the ticket | `git merge-tree --write-tree` needs git 2.38 or later. Only STATEMENT 2 says so; the README and the script docstring do not, and nothing checks the version. On an older git the run fails closed (exit 2), but the message is git's own usage line. Suggest stating the requirement in the README and the docstring, and naming it in the fault (for example, when `merge-tree` exits 129). |

Notes, not findings:

- A missing candidate, a non-commit and an unrelated-history candidate are all `MERGE_CONFLICT`. The ticket names none of these cases; this fails closed to a bounce with no command run. Accepted.
- An inherited `GIT_ATTR_SOURCE`, `GIT_AUTHOR_DATE` or `GIT_COMMITTER_DATE` passes through to the children. These come from the runner's own environment, not from a seat, and cannot run code without a driver definition, which no config the children read can hold.

## Commands

```text
git -C <repo> show 5cb8efef:modules/tickets/workflow-governance/50-merge-queue-integration.md ; ... show 5cb8efef:modules/spec/workflow-governance.md
git log/diff 37bacce9..26b6cc9a ; git diff --name-status 9a26eeb1 26b6cc9a ; git cat-file blob HEAD:<script> | sha256sum
python -m mypy --strict --python-version 3.11 skills/johnny-project-takeover/scripts/integrate.py tests/test_integrate.py      -> no issues in 2 files, exit 0
python -m pytest tests/test_integrate.py -q -p no:cacheprovider -rfEs                                                           -> 194 passed, 344 subtests, exit=0
python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py <out-r2>/RETURN.md <review worktree>              -> 0 defects, exit 0
python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py <out-r2>/RETURN.md --repo <review worktree> --candidate 26b6cc9a04eb0b4d46296528679bcd8887a63cac \
  --tool dispatch_lint.py --tool receipt_fence_check.py --tool index_pins.py --tool integrate.py \
  --require-cell P1 --require-cell T1 --require-cell M1 --require-cell M1B --require-cell F1 --require-cell P9 --evidence-root <out-r2>   -> cells=6 defects=0, exit 0
# own byte checks: CR count of RETURN.md and every capture; raw block == capture; exit: == capture exit= lines; file times (E1 last)
# M1 audit: every "=== <id>" section's diff and first FAILED/SUBFAILED name read from M1.txt and M1B.txt
# probes: rev02/probe2.py (land seatrec unapproved bounces race fsck driver bysha oldgit badsha unadmbad), probe.py (config pagesbom); plain-git control for the merge driver
# counter-mutations: rev02/cm2_driver.py, one copy each, python -m pytest tests/test_integrate.py -q -p no:cacheprovider -rfE, sequential, none during the lock
# F1 under the host lock (mkdir C:/Temp/claude/jas-fullsuite.lock; owner.txt run=50-rev02-initial; released by rename then remove after checking owner.txt)
python -m pytest tests -q -p no:cacheprovider -rfE                                                                                 -> 8 failed, 3454 passed, 35 skipped, exit=1; new vs base: none
```

## Raw-log note

The reviewer captures are in `.worktrees/50-merge-queue-integration-review-scratch/rev02/` and are not committed:

- `P1.txt` and `F1.txt`;
- `F1.wait` (lock log, with the list of other pytest processes at acquisition);
- `probe-a.txt` to `probe-f.txt`;
- `cm/<ID>.txt` (diff and full pytest output for each counter-mutation) and `cm-run*.log`.

pytest ran directly with `-rfE`, with no output-reducing wrapper. Every verdict above was read from the full output.

## Not verified

- A network remote (ssh or https). The behaviour of a remote that refuses unadvertised wants was not run; it is reasoned from the code (S50-10).
- A real git older than 2.38. That case was simulated at the process boundary.
- POSIX: the `killpg` tree kill and the executable bit. Linux CI was not run.
- A SHA-256 remote with merge landing. I rely on the seat's `RecordedBehaviourTests`, which pass in my P1.
- The S57-05 cross-check, which is carried to after integration, as the ticket says.

```review-verdict
candidate: 26b6cc9a04eb0b4d46296528679bcd8887a63cac
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/50-rev02-initial
reviewed_at: 2026-11-07
```
