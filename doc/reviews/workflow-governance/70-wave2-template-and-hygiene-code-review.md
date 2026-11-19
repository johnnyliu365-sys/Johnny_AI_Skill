# REVIEW — ticket 70 Wave-2 follow-ups: ticket and receipt templates, and a cap on tracked path length

## Revision01 returned before review

Revision01 returned `CHANGE_DETECTED` before any review (see "Seat token use" below). No commit was reviewed, so the block has no candidate.

```rework-record
candidate: none
round: 1
kind: RETURN
verdict: CHANGE_DETECTED
causes: DESIGN_UNFORESEEN
```

## Revision02 initial review

**Verdict: `CHANGES_REQUESTED`.** The template work is done as revision02 asks. Every changed path is inside the boundary block, and no `forbid` path is touched. The four new ticket-template rows, the `INTEGRATED` state and its sentences, the multi-receipt sentence, the corrected defect-class heading and the `return:`/`items:` head of the receipt `STATEMENT` are all present and pinned. The README describes each of them, and the ticket-69 `USAGE` example is byte-identical to the base. I filled the receipt template myself, with a real capture, a `USAGE` cell and a `STATEMENT` that begins `return: COMPLETED`, and `evidence_gate.py` accepts it (`cells=1 defects=0`, exit 0). The only existing pins that changed are the state-list pin (`ALLOWED_STATES`) and the dropped-part tuple of the state-row test, and both are stronger than before. There was no heading pin at the base. The longest tracked path is 120 characters at the base, at the candidate and at today's `cp/wave3`. CI run 44361589539 is green on both jobs at the candidate. P9 and E1 pass when I rerun them.

One finding blocks approval, S70-01. TDD row 3 of the ticket is frozen: "`git ls-files` failing inside a Git work tree is a test failure, not a skip". The path test decides whether it is in a work tree by asking git itself. So any git failure that also breaks `git rev-parse` turns the real-tree check into a skip, and the skip reason ("is not a Git work tree (or git is absent)") is false. CM2 shows this: in a clone whose `.git/config` git cannot parse, `git ls-files` exits 128 and the test file exits 0 with one skip. CM2b shows the same for a linked worktree whose admin directory has gone. The seat's fixture test covers only a corrupt index. `rev-parse` still succeeds in that case, so the test never exercises the skip decision on the real-tree path.

The other findings do not block. S70-02 is an evidence defect: "names each offending path" is pinned only with one offender, so my CM1, which reports only the first offender, is zero-red. S70-03 is hardening. A 120-character cap does not prevent the Linux 255-byte component limit that the seat hit. S70-04 and S70-05 go to the control plane.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/70-wave2-template-and-hygiene.md`, closure revision02, read with `git show 4f370710:…`. The boundary block has 4 `modify`, 1 `create` and 7 `forbid` lines. The "Revision02" section supersedes the `RETURN`-cell bullet. Revision01 was never reviewed |
| Spec / requirement | workflow-governance Revision 04 R4-1, R4-7; REQ-20261103-043; `doc/reviews/workflow-governance/wave2-completion-2026-11-12.md`, "Follow-up work found in wave 2" (Templates; Repository hygiene) |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-70_dispatch.yaml`, base `96f095a900bf8b6efc554816461dfb1180a7f764`. It still names revision01 and a `RETURN` cell (S70-05) |
| Candidate | `1ed245a296cd56c8910e5c28888d588e0a5a213b` on `cp/wave3-70-templates`. `git ls-remote origin` returns the same sha. There are three commits, `e7c344c2`, `a86ca57a` and `1ed245a2`, on base `96f095a9`. That base is "tickets 65 and 69 INTEGRATED" and is an ancestor of `cp/wave3` |
| Commit identity | Author and committer `Johnny Liu <johnny.liu365@gmail.com>`. Every commit carries `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` |
| Changed paths | `M template/README.md`, `M template/doc/handoffs/governance/RECEIPT.TEMPLATE.md`, `M template/modules/tickets/TEMPLATE.md`, `M tests/test_state_file_templates.py`, `A tests/test_tracked_path_length.py`. These are exactly the boundary block's five paths. Nothing under `library/`, `skills/`, `modules/spec/` or `.claude-plugin/` is touched, and neither are `Workflow.md`, `AGENTS.md` or `CodeReview.md`. `tests/test_wave2_end_to_end.py` and `tests/test_gate_evidence.py` are unchanged. All blobs are LF |
| Review worktree | `.worktrees/70-templates-review`, detached at the candidate. Porcelain (with `--ignored`) was empty before and after. My one probe import wrote an ignored `tests/__pycache__/` there (03:26:03), which I removed |
| Receipt | `.worktrees/70-templates-out/RETURN.md` (LF, 111879 bytes, 0 CR). Cells: P1, T1, M1, C1, F1, P9, STATEMENT. The STATEMENT begins `return: COMPLETED` / `items:` |
| CI run | 44361589539, event `push`, branch `cp/wave3-70-templates`, `headSha` = candidate; `test (linux)` success, `test (windows)` success. I read it with `gh run view` and `gh run list` only. The earlier runs, 44354922308 (`e7c344c2`) and 44355650153 (`a86ca57a`), are `failure`. In the second one, the only `UNREGISTERED_FAILURE` is `test_a_non_ascii_tracked_path_is_counted_in_characters`, which matches receipt S6 |
| References applied | `AGENTS.md` (both P0 sections); `CodeReview.md` (whole file, §5 rule B); `review-checks.md` ("Defect categories", "Reviewer counter-mutation", "Ticket dispatch schema review"); `specification-ticketing.md` (the ticket-field list, lines 30–40) |
| XSS / privileged JS | Not applicable. The change covers Markdown templates and two stdlib test files, with no browser, DOM or JavaScript surface |
| Secret / provider / external effect | Not applicable. There is no secret, log, provider or webhook. The only external effect was the seat pushing its own branch, which the dispatch authorised |
| Agent control / profile fan-out / POC ancestry | Not applicable. There is one implementer seat, no Agent-control path and no POC/staging |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Boundary | PASS | `git diff --name-status 96f095a9 1ed245a2` gives five paths, and each one is a `modify`/`create` line of the boundary block. No `forbid` prefix appears |
| 2a | Four new template rows | PASS | `TEMPLATE.md:13-16`: `Closure revision`, `Strict checker`, `Profile / resource`, `XSS classification`. They sit directly after `實作語言` and before `狀態`. Each holds a backticked `<placeholder>`, and the XSS row uses the `／不適用：<reason>` alternative, as the existing rows do. Together with the existing rows (state, owner, worktree, branch, baseline, receipt), these cover `review-checks.md` "Ticket dispatch schema review" apart from allocation and correlation, which the ticket excludes. They also cover `specification-ticketing.md:31,37,38,40` (closure revision; strict checker; profile and resource plan; XSS classification and matrix reference). Model capability tier, lane ownership and helper plan (`:38-39`) are beyond the ticket's wording and not asked for |
| 2b | State list, `INTEGRATED`/`DONE` sentences | PASS | `TEMPLATE.md:17` lists `…／REVIEW_APPROVED／INTEGRATED／CONVERGENCE_REPLANNED`. It holds both sentences verbatim, as the ticket states them |
| 2c | One receipt per closure revision | PASS, with S70-04 | `TEMPLATE.md:17`: "The receipt part holds one receipt per closure revision, in revision order, each as receipt `<repository-relative receipt path>`." The separator between receipts is not stated |
| 2d | Defect-class heading | PASS | `TEMPLATE.md:40` cites `CodeReview.md` §2 and the "Defect categories" table of `skills/johnny-project-takeover/references/review-checks.md`. Both exist: `CodeReview.md` "## 2. 必要檢查索引" and `review-checks.md` "## Defect categories". No `§2.1` is left in the template. The full path is a justified deviation. CM6 reproduces the seat's reason: with the bare name, `test_plugin_payload_boundary` reports "payload content names paths that do not exist: review-checks.md". The README already cites `skills/johnny-project-takeover/scripts/usage_report.py` by full path in the same way |
| 2e | `STATEMENT` begins with `return:` and `items:` | PASS | `RECEIPT.TEMPLATE.md`: `## STATEMENT` / `cell: STATEMENT` / `return: COMPLETED` / `items:` / blank / `<statement-text>`. The `cell:` line is the gate's own section marker, and no prose comes before the two lines. A preamble paragraph explains them. There is no `RETURN` section |
| 2f | README | PASS | `template/README.md:65-74` describes the four rows, `INTEGRATED`, `DONE`, the multi-receipt part and the two `STATEMENT` lines, including "empty for `COMPLETED`" |
| 2g | Ticket-69 `USAGE` example unchanged | PASS | The preamble up to the placeholder table, minus the one added paragraph, has the same sha256 at the base and the candidate (`edb39dc5…`). The diff touches no line of the `USAGE` fence |
| 3a | Characters, not bytes | PASS | `path_length` is `len()` of the UTF-8-decoded `str`. CM by the seat (bytes) is red. My probe: a 120-character `字` path (240+ bytes) passes |
| 3b | Reads `git ls-files -z` | PASS | `tracked_paths` runs `git -C <root> ls-files -z` with `GIT_*` stripped and splits on NUL |
| 3c | Each offender on one escaped line | PASS for one offender; S70-02 | `escaped()` writes every byte outside printable ASCII, and the backslash, as `\xNN`. A newline in a name stays on the line. With several offenders, "each" is not pinned (CM1) |
| 3d | Skip outside a work tree, with a reason | PASS | `RealTreeTests` skips with "… is not a Git work tree (or git is absent): …" |
| 3e | Fail, not skip, when git fails inside a work tree | **FAIL: S70-01** | CM2 and CM2b: `git ls-files` exits 128 inside a checkout that has `.git`, and the real-tree test is SKIPPED with a false reason. The test file exits 0 |
| 3f | 120 passes, 121 fails | PASS | `test_a_tree_with_a_120_character_tracked_path_passes` and `…_121_…_fails_and_names_it` use a real `git init` index. `CapTests` covers the same boundary on bytes in memory. The seat's "cap raised to 160" mutation is red |
| 3g | Current tree passes; longest ≤ 120 | PASS | My own measurement (`git ls-tree -r -z --name-only`, decoded): base `96f095a9` has 1264 paths, candidate 1265 and `origin/cp/wave3` 1267. In all three the longest is 120 characters, `doc/context/claude-code-plugin-distribution/claude-code-plugin-distribution-r06-installed-cache-version-specific-tags.md`, and nothing is longer than 120. `git ls-files -z` in the review worktree gives 1265 paths with a maximum of 120. This matches receipt S3. The tree has 44 non-ASCII paths, and the test decodes all of them |
| 3h | Does the 120-character cap alone cover the Linux 255-byte component limit? | **No: S70-03** | Probe: `doc/` + 90 × `字` + `.md` is 97 characters, but one component is 273 bytes, and `offences()` returns `[]`. With emoji, 64 × U+1F600 gives 69 characters, a 259-byte component and 133 UTF-16 units, and `offences()` again returns `[]`. A component of 86 three-byte characters already exceeds 255 bytes. The seat's own fixture hit this in CI run 44355650153 |
| 4 | Filled receipt template passes the gate; e2e unchanged | PASS | In my clone `70-rev02-initial-gate` at the candidate, I filled the template body by hand. It had a real capture (`git rev-parse HEAD` plus `exit=0`), the tool digest of `evidence_gate.py` at the candidate, the `STATEMENT` beginning `return: COMPLETED`/`items:`, and one `USAGE seat:ticket-review/70-rev02-initial` cell. `evidence_gate.py … --require-cell R1` gave `cells=1 defects=0`, exit 0. The same receipt with the full preamble kept also gave `cells=1 defects=0`, and so did a `return: BLOCKED` variant with one item. `tests/test_wave2_end_to_end.py` is unchanged in the diff and passes in my P1 rerun |
| 5 | No existing template pin weakened | PASS | `git diff … tests/test_state_file_templates.py`: 194 insertions and 1 deletion. The deletion is the `dropped` tuple of `test_dropping_a_part_of_the_state_row_is_a_problem`, replaced by a superset (three more sentences). `ALLOWED_STATES` gains `INTEGRATED`. That is the state-list pin, named in receipt S2. There was no heading pin at the base (`git show 96f095a9:… \| grep '2\.1\|缺陷類別'` is empty), as S2 says. The file has 56 tests at the base and 68 at the candidate, and no test is removed or skipped |
| 6 | Receipt honest | PASS | P9 rerun: `receipt_check.py` on the receipt cut before `## P9`, with captures copied beside it, gives 5 `[ok]` and 0 defects, exit 0. Its output equals `P9.txt` byte for byte once my shell's CRLF is removed. On `RETURN.md` itself it gives 6 `[ok]`, exit 0. The E1 rerun with the dispatched arguments gives `cells=6 defects=0`, exit 0. All six raw blocks are byte-identical to their capture files, and the receipt has 0 CR. Recomputed sha256: `P1.txt` 4fd4bb4f…399398, `M1.txt` 7df878aa…dda8bb44, `F1.txt` 20dbc460…de8f7f7b. All four `tool_digest` values equal the sha256 of the blob at the candidate (`dispatch_lint` 3f5730c9…, `evidence_gate` 89f8839b…, `index_pins` 63eff436…, `receipt_fence_check` 8b3f845c…). The F1 failure set (5 names) is a subset of the 12 names in `jas48_F1_base.txt` (`comm -23` is empty). My P1 rerun gives the same counts as `P1.txt`: 335 passed, 1 skipped, 550 subtests. T1 rerun: `mypy --strict --python-version 3.11` on both files, no issues. M1 was run in a `--no-hardlinks` clone, the clone command is recorded, there are five mutations and each is red, the tree matched the candidate after the reverts, and porcelain was 0 |
| 7 | Seat deviations | All accepted | (a) Full-path heading citation: CM6 confirms the reason, and the cited file exists. (b) Four tools in `tool_digest`: `receipt_check.py` requires `dispatch_lint`/`receipt_fence_check`/`index_pins`, and E1 names `evidence_gate`/`index_pins`, so the four are the union of those requirements, each digest is correct, and the extra digests do no harm. (c) Captures rerun to remove CR: every capture now has 0 CR, every capture is dated after the candidate commit (01:42:10 +08:00), and every raw block equals its file. (d) Fixture names under 255 bytes: `spread()` keeps every component at 50 characters or fewer (at most 150 bytes for `字`), and the total stays exactly 120/121 characters. That keeps the test meaningful, and it is the reason for S70-03 |
| 8 | Reviewer counter-mutations | 6 run, plus 1 environment variant; CM1, CM2 and CM2b are zero-red | Table below |

### Reviewer counter-mutations

These ran in the disposable clone `.worktrees/70-templates-review-scratch/70-rev02-initial-cm` (`git clone -q --no-hardlinks <main checkout>`, then `checkout --detach 1ed245a2…`). Each ran with its full test file, using `python -m pytest <file(s)> -p no:cacheprovider -rfEs` with default verbosity and tracebacks. Nothing reduced the output: I read the whole capture of each run. Template mutations were committed inside the clone only, because the template tests read the blob at `HEAD`. Each mutation was restored with `git checkout -f --detach 1ed245a2 && git clean -fd`, and porcelain was 0 with `HEAD` equal to the candidate after each one. The doors differ from the seat's five: `INTEGRATED` removed, `§2.1` restored, the cap at 160, bytes counted, and `return:` removed.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| CM1 | First match | `offences()` adds `break` after the first over-length path | **zero red**: 13 passed. No fixture or in-memory case has two offenders (S70-02) |
| CM2 | Environment-scoped: the skip decision on the path production walks | Append `[core` to the clone's `.git/config`, so `git rev-parse` and `git ls-files` both exit 128 ("bad config line 14") | **zero red**: 12 passed, 1 skipped, exit 0. `SKIPPED … 70-rev02-initial-cm is not a Git work tree (or git is absent)` (S70-01) |
| CM2b | Same door, the worktree shape this repository uses | A linked worktree `70-rev02-initial-wt` of the clone, with its `.git/worktrees/<id>` admin dir moved away. `rev-parse`: "not a git repository: (NULL)" | **zero red**: 12 passed, 1 skipped, exit 0, the same false reason. The admin dir was moved back and the worktree removed and pruned |
| CM3 | Swallowed fault | `tracked_paths` returns `[]` when `git ls-files` exits non-zero | red: `test_a_failing_git_ls_files_inside_a_work_tree_is_a_failure_not_a_skip` (`GitListError not raised`) |
| CM4 | Lenient decode | `raw.decode("utf-8", "replace")` | red: `test_an_undecodable_path_is_reported_not_raised`, `test_an_undecodable_path_is_reported_even_when_short` |
| CM5 | Copy: does the heading point at something that exists on the real path? | Change the heading to `…/references/review-checks-gone.md` in the template and in the test's `DEFECT_HEADING` copy alike, so the exact-string pin agrees | red, on the real choke point: `test_plugin_payload_boundary.py::PayloadClosureTests::test_every_path_shaped_token_resolving_nowhere_is_declared` and `::test_the_committed_payload_is_closed` name `review-checks-gone.md`. The `CommittedPinTests::test_the_pinned_sha_exists` failure is pre-existing in a clone |
| CM6 | Seat deviation (a) | The heading and its pin changed to a bare `` `review-checks.md` `` | red: the same two payload-closure tests, with "payload content names paths that do not exist: review-checks.md". This confirms the deviation was needed |

Probe for item 3h, not a mutation: I imported `tests/test_tracked_path_length.py` from the review worktree and called `offences()` on the two paths in cell 3h. Both returned `[]`.

### Findings

| ID | Class | Severity | Blocks? | File:line | Observation | Verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S70-01 | `IMPLEMENTATION_DEFECT` (frozen TDD row 3: "`git ls-files` failing inside a Git work tree is a test failure, not a skip") | Low | **Yes** (initial review; it breaks an approved fail-closed contract) | `tests/test_tracked_path_length.py:53-59, 218-223`; fixture `:205-210` | `is_git_work_tree` treats every non-zero `git rev-parse --is-inside-work-tree` as "not a work tree", and `OSError` (no git) the same way. So any git fault that also breaks `rev-parse` skips the only real-tree check, with a false reason. Examples are an unparsable config, a pruned linked-worktree admin dir, and git's dubious-ownership refusal. The `OSError` branch of `tracked_paths` cannot be reached from `RealTreeTests`. The fixture test proves only that `tracked_paths` raises on a corrupt index, where `rev-parse` still succeeds, so the fail-not-skip property is pinned on a helper, not on the path the real-tree test takes | CM2, CM2b: exit 0 with 1 skip while `git ls-files` exits 128 | This correction. Decide "not a work tree" without git: skip only when neither `ROOT` nor any parent has a `.git` entry. Otherwise call `tracked_paths(ROOT)` unconditionally, so that a `GitListError` (including git absent) fails the test. Add one fixture that breaks `.git/config` and asserts that the real-tree check raises instead of skipping. Factor the check into a function of `root` so that the fixture can call it |
| S70-02 | `EVIDENCE_DEFECT` | Low | No. The candidate does name every offender. If it is still open after the correction review, rule B carries it to the next change of this test, because it would let a regression pass | `tests/test_tracked_path_length.py:87-99, 178-185` | The ticket says "names each offending path on one escaped line". Every fixture has at most one offender, so a reporter that stops at the first offender passes | CM1: zero red | This correction. Add two over-length paths plus one undecodable path to one fixture, and assert three lines that name all three |
| S70-03 | `OUT_OF_SCOPE_HARDENING` | Low | No | `tests/test_tracked_path_length.py:24, 73-75, 87-99` | The cap counts code points across the whole path. Linux refuses any component of more than 255 UTF-8 bytes, and that is the failure the seat hit in CI run 44355650153. A path of 97 characters can carry a 273-byte component, and a 69-character emoji path carries 259 bytes and 133 UTF-16 units. A file like that can be committed from Windows, where the limit is 255 UTF-16 units per component, and the Linux checkout then breaks. That is the mirror of ticket 61's failure. The 120-character cap alone does not prevent it | Probe in cell 3h: `offences()` returns `[]` for both | A follow-up hygiene ticket. The smallest guard is one more clause in `offences()`: report any `/`-separated component whose `len(component.encode("utf-8")) > 255`, on the same escaped line, plus one in-memory case of an 86 × `字` component. Optionally, count UTF-16 units for the Windows total |
| S70-04 | `TICKET_DEFECT` (control plane: the state-row wording is underspecified) | Low | No | `template/modules/tickets/TEMPLATE.md:17`; ticket revision02, "The state row" | "One receipt per closure revision, in revision order, each as receipt `<path>`" does not say what separates the receipts. The row's other parts are `; `-separated, and the test's `STATE_ROW_PREFIX` pins only the first. No script parses the receipt part today: `git grep` over `skills/` and `library/` finds no reader. The candidate follows the ticket's words exactly | Reading the template, the ticket and the test | Ticket 67 or the next template change. State the separator, for example "…, separated by `; `", and pin it |
| S70-05 | `TICKET_DEFECT` (control plane: dispatch identity) | Low | No | `C:/Temp/claude/jas-dispatch/JAS-70_dispatch.yaml:1, contracts[1], env.mutations` | The dispatch still names revision01 and requires "a RETURN cell passes evidence_gate.py". The ticket leaf in the seat worktree is revision01. The seat followed revision02 (receipt S1, S7, S9). The binding is inferred, not dispatched. This is the same shape as S65-05 | `grep revision` and `grep RETURN` on the dispatch | Control plane: issue or amend the dispatch for each closure revision before the correction |

### Commands

These ran from the main checkout unless noted, with `C:/Temp/claude/jas-venv/Scripts/python.exe` and `PYTHONUTF8=1`.

- `git ls-remote origin cp/wave3-70-templates`; `git log --format='%H %P %an <%ae> | %cn | %s' 96f095a9..1ed245a2`; `git merge-base --is-ancestor 96f095a9 cp/wave3`; `git diff --name-status 96f095a9 1ed245a2`; `git diff 96f095a9 1ed245a2 -- template/ tests/test_state_file_templates.py`
- Review worktree: `python -m pytest tests/test_state_file_templates.py tests/test_tracked_path_length.py tests/test_gate_evidence.py tests/test_wave2_end_to_end.py -q -rfEs -p no:cacheprovider` gave 335 passed, 1 skipped (symlinks), 550 subtests passed, exit 0. `python -m mypy --strict --python-version 3.11 --no-incremental tests/test_state_file_templates.py tests/test_tracked_path_length.py` reported no issues
- Path measurement: `git ls-tree -r -z --name-only <rev>` for `96f095a9`, `1ed245a2` and `origin/cp/wave3`, decoded, recording maximum characters, maximum component bytes and maximum UTF-16 units. Also `git ls-files -z` in the review worktree
- `gh run view 44361589539 --json headSha,conclusion,event,headBranch,jobs`; `gh run view 44361589539 --job <id> --log`, for both jobs (no `tracked_path` or `state_file_templates` failure; the compare step succeeded); `gh run list --branch cp/wave3-70-templates`; `gh run view 44355650153 --log-failed`
- Gate reproduction: `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py <my RETURN.md> --repo . --candidate 1ed245a2… --tool skills/johnny-project-takeover/scripts/evidence_gate.py --evidence-root <ev> --require-cell R1`, run in clone `70-rev02-initial-gate` on three receipts: body only, full preamble, and `BLOCKED`
- P9: `python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py <RETURN cut before ## P9> .worktrees/70-templates-review`, and the same on `RETURN.md`. E1: `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py .worktrees/70-templates-out/RETURN.md --repo .worktrees/70-templates-review --candidate 1ed245a2… --tool …/evidence_gate.py --tool …/index_pins.py --evidence-root .worktrees/70-templates-out --require-cell P1 --require-cell T1 --require-cell M1 --require-cell F1`
- `sha256sum` of `git show 1ed245a2:skills/johnny-project-takeover/scripts/<tool>.py` for the four tools; sha256 of `P1.txt`, `M1.txt` and `F1.txt`; raw block against capture for all six run cells
- F1: the `FAILED`/`ERROR` names of `F1.txt` compared, sorted, with `comm -23` against `C:/Temp/claude/jas48_F1_base.txt`

### Not verified

- I did not run a full-suite F1 of my own. As instructed, I relied on the seat's locked F1 and on CI.
- CI runs `pytest -q -rf`, so its log does not show skips. I could not see from the log that `RealTreeTests` ran rather than skipped on either job. `actions/checkout` gives a work tree, so it should have run, and it did not fail on either job.
- Git's dubious-ownership refusal (`safe.directory`) as a trigger for S70-01 is inferred from git's documented behaviour. I did not reproduce it, because that would mean changing ownership or security settings.
- `test_a_directory_that_is_not_a_work_tree_is_recognised` assumes that the system temp directory is not inside a Git work tree. I did not check this on the CI runners.
- macOS (HFS+/APFS) name limits are not considered.

### Residue

Everything I created carried the run id `70-rev02-initial`, and I removed all of it before returning. In `.worktrees/70-templates-review-scratch/`: `70-rev02-initial-gate` (clone), `70-rev02-initial-cm` (clone), `70-rev02-initial-ev` and `70-rev02-initial-cmout` (captures, fill scripts, `config.orig`), and the linked worktree `70-rev02-initial-wt` (removed with `git worktree remove` and pruned in the clone). In `%TEMP%`: `70-rev02-initial-measure.py`, `70-rev02-initial-ci-135004146034.log`, `70-rev02-initial-ci-135004146524.log`, `70-rev02-initial-ci-fail.log`, `70-rev02-initial-f1.txt` and `70-rev02-initial-base.txt`. One ignored `tests/__pycache__/` did not carry the run id. My `-I` probe import created it in the review worktree at 03:26:03, and nothing had been there at the start. I removed it, and porcelain `--ignored` is now empty. No process was left running. I did not touch the seat's worktree, the out directory, any other seat's directory or any tracked file. I did not push, and I triggered no CI.

```review-verdict
candidate: 1ed245a296cd56c8910e5c28888d588e0a5a213b
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/70-rev02-initial
reviewed_at: 2026-11-19
```

```rework-record
candidate: 1ed245a296cd56c8910e5c28888d588e0a5a213b
round: 2
kind: INITIAL
verdict: CHANGES_REQUESTED
causes: CONTROL_PLANE_RULE,IMPLEMENTATION_DETAIL
```

## Revision02 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`. Every open finding is non-blocking under rule B.** Correction 1 closes S70-01 to S70-04 as the coordinator's correction message asks.
- The real-tree check now skips only when neither the root nor any parent has a `.git` entry. A broken `.git/config` fails the test.
- A three-offender fixture names all three paths.
- `offences()` reports any component of more than 255 UTF-8 bytes.
- The state row states the `; ` separator, and a test pins it.

My CM1, CM2 and CM2b, which were zero-red at `1ed245a2`, are now red. So is CM12, which swallows the git failure in the new function. CM10 and CM11, aimed at the new component clause, are red too.

Three of my new counter-mutations stay zero-red, and they show two properties of the correction that hold but are not pinned:
- the skip rule's "any parent" walk and its `.git`-file form (CM7, CM8; S70-06);
- the component clause on a directory component rather than the leaf (CM9; S70-07).

Both are `EVIDENCE_DEFECT`s on a correct candidate. Under rule B they do not block, but a regression in either would let a change pass that should not: one would turn a real check into a skip, the other would admit a >255-byte directory component. So rule B requires both to be closed in the next change of this test. S70-05 stays with the control plane. It does not change an exit-code classification, a safety or scope boundary, or P0, so it does not block either.

| Field | Value |
| --- | --- |
| Candidate | `548665e5b0936b767c0108b57feec644a3bf3d08` on `cp/wave3-70-templates`, the same sha on `origin`. It is one additive commit on `1ed245a2` ("fix(template): correction 1 of ticket 70 (S70-01 to S70-04)"). Author `Johnny Liu <johnny.liu365@gmail.com>`, trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. There is no reset, amend or force: `1ed245a2` is its parent |
| Correction scope | `git diff --name-only 1ed245a2 548665e5`: `template/README.md`, `template/modules/tickets/TEMPLATE.md`, `tests/test_state_file_templates.py`, `tests/test_tracked_path_length.py`. In the ticket template, only the `狀態` row changed. `96f095a9..548665e5` still touches exactly the boundary block's five paths. The receipt is in `.worktrees/70-templates-out`, outside the repository |
| Correction authority | The coordinator's correction message (S70-01 to S70-04, with S70-05 kept by the control plane), as relayed to this seat |
| Review worktree | `.worktrees/70-templates-review`, detached at the candidate. Porcelain `--ignored` was empty before. My mypy run left an ignored `.mypy_cache/` there, which I removed, and porcelain `--ignored` is empty again |
| Receipt | `.worktrees/70-templates-out/RETURN.md`, rebuilt (LF, 157350 bytes, 0 CR). Every run cell names candidate `548665e5…`. Cells: P1, T1, M1 (9 mutations), C1, F1, P9, STATEMENT (`return: COMPLETED`, `items:`) |
| CI run | 44381551978, event `push`, `headSha` = candidate. `test (windows)` success and `test (linux)` success. I read it with `gh run view` and `gh run list` only, and `C1.txt` names the same run and sha |
| References applied | As in the initial review, plus `CodeReview.md` §5 rule B for the disposition of what remains open |

### Cell results (correction)

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| C1 | S70-01: skip only with no `.git` entry anywhere; git failure is a failure | PASS (closed), with S70-06 | `has_git_entry` checks `(candidate / ".git").exists()` for the root and every parent, without git. `real_tree_offences` raises `NotAWorkTree` only in that case, and `RealTreeTests` skips only on `NotAWorkTree`. A new fixture breaks `.git/config` and asserts `GitListError` through `real_tree_offences`, the same function the real-tree test calls. CM2 is now red: `RealTreeTests` fails with `GitListError: git ls-files exited 128: fatal: bad config line 14`. CM2b is red: `… fatal: not a git repository: (NULL)`. CM12 is red. In the review worktree, which is a linked worktree with a `.git` file, `RealTreeTests` PASSES and is not skipped (`-v` run) |
| C2 | S70-02: every offender named | PASS (closed) | `test_every_offender_is_named_not_only_the_first` (two long paths and one undecodable path, in memory) and `test_a_tree_with_three_offending_paths_names_all_three` (a real index). CM1 is now red on both |
| C3 | S70-03: 255-byte component clause, with its own fixture | PASS (closed), with S70-07 | `offences()` computes `max(len(component.encode("utf-8")) for component in text.split("/"))` and reports `component of N bytes, cap 255: <escaped>` on one line. Fixtures: the 97-character path with a 273-byte component, exactly 255 bytes passing and 256 failing, and two 120-byte components in one path passing. CM10 (`>=`) and CM11 (characters instead of bytes) are red. The real tree passes: no component is longer than 78 bytes (measured in the initial review, and the correction adds no path) |
| C4 | S70-03 deviation: no README cap sentence, docstring instead | Accepted | `template/README.md` describes the target-project templates that the plugin ships. The cap is a hygiene test of the plugin repository, it is not a template, and the ticket requires no README text for it (revision01 "The template README describes the new rows …", revision02 "describes these two lines"). The module docstring states both limits and the skip rule, and anyone reading a failure of this test sees it first. A README sentence would describe something the README's reader never receives |
| C5 | Changed `CapTests` wide-character fixtures | Accepted: equivalent and necessary | `test_the_length_is_counted_in_characters_not_bytes`. Before, `"字"*117+".md"` (120 characters, a single 354-byte component) and `"字"+that` (121 characters, 357 bytes). After, `spread("字", 120)` (120 characters, 350 bytes, components of 147 bytes or fewer) and `spread("字", 121)` (121 characters, 353 bytes). I measured all four. It is the same character, the same 120/121 boundary and the same assertions (`== []`, `len(...) == 1`, and `len(bytes) > cap`). The `é` case is unchanged (234 bytes in one component). Under the new clause the old pair would report a component offence: the old 120-character path gives 1 line and breaks `== []`, and the old 121-character path gives 2 lines and breaks `== 1`. The change is therefore required, and the bytes-not-characters property still discriminates, because 350 bytes is far above the 120 cap. The seat's mutation 4 (bytes counted) is red, now with 5 failures |
| C6 | S70-04: separator stated and pinned | PASS (closed) | `TEMPLATE.md:17`: "…in revision order; several receipts are written as receipt `<…>`; receipt `<…>`, separated by `; `, like the other parts of the row." `MULTI_RECEIPT_SENTENCE` pins it exactly (`tests/test_state_file_templates.py:124-128`), and the README test pins "separated by `; `" (`:1053`). The seat's mutation 8 (sentence removed) is red with 4 failures. The revision01 wording "one receipt per closure revision, in revision order" survives. `MULTI_RECEIPT_SENTENCE` is a pin this ticket added, so changing it weakens no pre-existing pin |
| C7 | Tests and types at the candidate | PASS | Review worktree: P1 set 341 passed, 1 skipped (symlinks), 553 subtests passed, the same counts as `P1.txt`. `tests/test_tracked_path_length.py` `-v` gives 19 PASSED, 0 skipped. `mypy --strict --python-version 3.11` on both test files reports no issues |
| C8 | Receipt honest (P9, E1) | PASS | P9 rerun: `receipt_check.py` on the receipt cut before `## P9`, with the captures beside it, gives 5 `[ok]`, 0 defects, exit 0, and its output equals `P9.txt` once my shell's CR is removed. On `RETURN.md`, 6 `[ok]` and 0 defects. The E1 rerun with the dispatched arguments and `--candidate 548665e5…` gives `cells=6 defects=0`, exit 0. All six raw blocks are byte-identical to their capture files. Recomputed sha256: `P1.txt` c3cdf013…15dd2d9f, `M1.txt` 1edbb057…5e9780a84, `F1.txt` b76902e8…ee541e1dd. Each of the four `tool_digest` values equals the blob sha256 at the candidate and appears in all 6 run cells. F1 has 5 failed names, a subset of the 12 base names (`comm -23` empty). STATEMENT S2 counts 19 tests in the path file, which is correct. S7 gives one disposition for each finding, and S8 lists nine mutations, each red, matching `M1.txt` |

### Reviewer counter-mutations (correction)

These ran in the disposable clone `.worktrees/70-templates-review-scratch/70-rev02-correction-cm` (`git clone -q --no-hardlinks <main checkout>`, then `checkout --detach 548665e5…`), with `python -m pytest tests/test_tracked_path_length.py -p no:cacheprovider -rfEs`. I used default verbosity and tracebacks, put no reducer in between, and read the whole capture of each run. Each mutation was restored with `git checkout -f --detach 548665e5 && git clean -fd`, and porcelain was 0 after each. CM2's config was restored from a byte copy. The linked worktrees `70-rev02-correction-wt` and `-wt2` were removed with `git worktree remove --force` and `git worktree prune`. For CM2b, the moved admin dir `70-rev02-correction-wtadmin` was moved back first.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| CM1 (rerun) | First match | `break` after the first over-length path in `offences()` | red: `test_every_offender_is_named_not_only_the_first`, `test_a_tree_with_three_offending_paths_names_all_three` |
| CM2 (rerun) | Environment, real-tree path | `[core` appended to the clone's `.git/config` | red: `RealTreeTests::test_no_tracked_path_…` fails with `GitListError: git ls-files exited 128: fatal: bad config line 14 in file .git/config` |
| CM2b (rerun) | Environment, linked worktree | The admin dir of linked worktree `70-rev02-correction-wt` moved away | red: `RealTreeTests` fails with `GitListError: … fatal: not a git repository: (NULL)` |
| CM7 | S70-01 skip rule: the parent walk | `has_git_entry` checks only `root`, not `root.parents` | **zero red**: 19 passed. Every fixture has `.git` at its root, so the "any parent" half of the rule is not pinned (S70-06) |
| CM8 | S70-01 skip rule: the `.git`-file form | `.exists()` replaced by `.is_dir()` | **zero red**: 19 passed in the clone. Also **zero red** in the linked worktree `70-rev02-correction-wt2`, whose `.git` is a file: overlap-masking, because the walk reaches the main checkout's `.git` directory above `.worktrees/`. Outside such a nesting, the real-tree check would skip a linked worktree, and nothing fails (S70-06) |
| CM9 | S70-03 clause: which component | Only the last component is measured (`text.split("/")[-1:]`) | **zero red**: 19 passed. Every over-255 fixture has the wide component as the leaf, so a >255-byte directory component is not pinned (S70-07) |
| CM10 | S70-03 clause: edge | `widest >= MAX_COMPONENT_BYTES` | red: `test_a_component_of_exactly_255_bytes_passes_and_256_fails` |
| CM11 | S70-03 clause: unit | Component length counted in characters | red: `test_a_component_of_273_bytes_in_a_short_path_is_reported`, `test_a_component_of_exactly_255_bytes_passes_and_256_fails` |
| CM12 | S70-01: swallowed fault in the new function | `real_tree_offences` returns `[]` on `GitListError` | red: `test_a_broken_git_config_makes_the_real_tree_check_fail_not_skip` |

### Findings (status after correction 1)

| ID | Class | Severity | Status | Blocks? | File:line | Observation | Verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S70-01 | `IMPLEMENTATION_DEFECT` | Low | **Closed** | — | `tests/test_tracked_path_length.py:61-66, 80-87, 289-295` | The skip is decided from the file system. A git failure inside a work tree is `GitListError` on the real-tree path | CM2, CM2b and CM12 red; C1 | — |
| S70-02 | `EVIDENCE_DEFECT` | Low | **Closed** | — | `tests/test_tracked_path_length.py:197-205, 279-286` | Multi-offender fixtures, in memory and in a real index | CM1 red | — |
| S70-03 | `OUT_OF_SCOPE_HARDENING` (done in this correction at the coordinator's request) | Low | **Closed** | — | `tests/test_tracked_path_length.py:28, 116-118, 207-225` | 255-byte component clause with fixtures. The README sentence was replaced by the docstring, and I accept that (C4) | CM10, CM11 red | — |
| S70-04 | `TICKET_DEFECT` | Low | **Closed** | — | `template/modules/tickets/TEMPLATE.md:17`; `tests/test_state_file_templates.py:124-128, 1053` | The separator is stated and pinned in the row and the README | Seat mutation 8 red | — |
| S70-05 | `TICKET_DEFECT` (control plane: dispatch identity) | Low | **Open**, control plane | No (no exit-code classification, safety/scope boundary or P0 involved) | `C:/Temp/claude/jas-dispatch/JAS-70_dispatch.yaml:1` | The dispatch still names revision01 and a `RETURN` cell. The correction went out as a coordinator message | Unchanged | Control plane, as the coordinator stated |
| S70-06 | `EVIDENCE_DEFECT` | Low | **Open, new** | No (rule B: the candidate behaves correctly). A regression would turn the real-tree check into a skip, which lets a change pass, so rule B requires it to be fixed in the next change of this test | `tests/test_tracked_path_length.py:61-66`; fixtures `:254-277` | Two halves of the skip rule are unpinned. "Any parent" is unpinned because every fixture has `.git` at its root. The `.git`-file form of a linked worktree is unpinned because every fixture is a `git init` directory, and in this repository the main checkout's `.git` above `.worktrees/` masks it | CM7, CM8 zero red | Next change of this test. Smallest fix, two fixtures: (a) `real_tree_offences(repo / "sub")` on a tracked subdirectory that has no `.git` of its own returns `[]` and does not raise `NotAWorkTree`; (b) a temp directory outside any repository, holding only a `.git` file `gitdir: <missing path>`, raises `GitListError`, not `NotAWorkTree` |
| S70-07 | `EVIDENCE_DEFECT` | Low | **Open, new** | No (rule B: the candidate behaves correctly). A regression would admit a >255-byte directory component, so rule B requires it to be fixed in the next change of this test | `tests/test_tracked_path_length.py:116-118, 207-225` | Every over-limit fixture puts the wide component in the leaf, so a clause that measures only the last component passes | CM9 zero red | Next change of this test. Smallest fix: one in-memory case, `"字" * 86 + "/a.md"`, expecting exactly one `component of 258 bytes` line |

### Commands (correction)

These ran from the main checkout unless noted, with `C:/Temp/claude/jas-venv/Scripts/python.exe` and `PYTHONUTF8=1`.

- `git ls-remote origin cp/wave3-70-templates`; `git log --format=… 1ed245a2..548665e5`; `git diff --stat` and `git diff --name-only 1ed245a2 548665e5`; `git diff 1ed245a2 548665e5 -- template/ tests/`
- Review worktree, with `PYTHONDONTWRITEBYTECODE=1`: the P1 test set (`-q -rfEs -p no:cacheprovider`); `tests/test_tracked_path_length.py -v`; `mypy --strict --python-version 3.11 --no-incremental` on both test files
- `gh run view 44381551978 --json headSha,conclusion,event,headBranch,jobs`; `gh run list --branch cp/wave3-70-templates`
- Fixture equivalence: `spread()` and `offences()` imported with `-B` from the clone, measuring characters, bytes, the character count and the widest component of the old and new fixtures
- P9: `receipt_check.py <RETURN cut before ## P9> .worktrees/70-templates-review`, and the same on `RETURN.md`. E1: `evidence_gate.py .worktrees/70-templates-out/RETURN.md --repo .worktrees/70-templates-review --candidate 548665e5… --tool …/evidence_gate.py --tool …/index_pins.py --evidence-root .worktrees/70-templates-out --require-cell P1 --require-cell T1 --require-cell M1 --require-cell F1`
- sha256 of `P1.txt`, `M1.txt` and `F1.txt`; raw block against capture for every run cell; the four tool blob digests at `548665e5`; F1 names compared with `comm -23` against `jas48_F1_base.txt`

### Not verified (correction)

- I did not run a full-suite F1 of my own. As instructed, I relied on the seat's locked F1 (5 base failures) and on CI.
- CI's `-rf` output does not show skips. With the new rule, a skip on CI is only possible without any `.git` entry, and `actions/checkout` creates one.
- `test_a_directory_with_no_git_entry_anywhere_is_the_only_skip` still assumes that the system temp directory and all its parents hold no `.git`. I did not check the runners.
- I did not re-measure the 120-character maximum. The correction adds no tracked path.

### Residue (correction)

Everything I created carried the run id `70-rev02-correction`, and I removed it all before returning:
- the clone `70-rev02-correction-cm`;
- the capture and script directory `70-rev02-correction-out`, with its `p9/` copy and `config.orig`;
- the linked worktrees `70-rev02-correction-wt` and `70-rev02-correction-wt2`, removed and pruned;
- the temporarily moved admin dir `70-rev02-correction-wtadmin`, moved back before the worktree was removed.

All of these were in `.worktrees/70-templates-review-scratch/`. One ignored `.mypy_cache/` did not carry the run id. My mypy run created it in the review worktree, where nothing had been before, and I removed it. No process of mine is left. I did not touch any tracked file, the seat's worktree, the out directory or another seat's directory. I did not push, and I triggered no CI.

```review-verdict
candidate: 548665e5b0936b767c0108b57feec644a3bf3d08
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/70-rev02-correction
reviewed_at: 2026-11-19
```

```rework-record
candidate: 548665e5b0936b767c0108b57feec644a3bf3d08
round: 3
kind: CORRECTION
verdict: CONVERGENCE_REVIEW_REQUIRED
causes:
```

## Convergence disposition (control plane, 2026-11-19)

The correction review returned `CONVERGENCE_REVIEW_REQUIRED`: every blocking finding is closed and the open findings are non-blocking under CodeReview §5 rule B. Each carried finding keeps the smallest fix the reviewer named (lesson L-19).

```convergence-disposition
candidate: 548665e5b0936b767c0108b57feec644a3bf3d08
reviewer_verdict: CONVERGENCE_REVIEW_REQUIRED
disposition: APPROVED
rule: CodeReview §5 rule B (owner-approved 2026-11-05)
carried:
  - S70-05
  - S70-06
  - S70-07
```

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, against the expectation the owner confirmed on 2026-11-18 ("1A"); appended to the receipt as `USAGE` cells at integration.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/70-impl` | claude-sonnet-5-5 | 360 | 406527 | 30496495 | 99442 | 30903382 | OVER_PROCESSED |
| `seat:ticket-review/70-rev02` | claude-opus-5-5 | 162 | 403116 | 11259717 | 84228 | 11662995 | WITHIN |

The implementation seat is over its processed expectation (30903382, 28.8 % over); over is explained here and does not block integration (owner decision 2026-11-18 "1A"). Facts on record: the seat ran three rounds in one seat (the `CHANGE_DETECTED` return of revision01, revision02 with two red Linux CI runs before the green one, and correction 1), and it ran the full suite under the host lock in each of the last two rounds. The review seat is within its expectation.
