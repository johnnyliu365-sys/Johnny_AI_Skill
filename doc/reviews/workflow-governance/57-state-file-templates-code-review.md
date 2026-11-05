# REVIEW — ticket 57 State-file templates

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `27318feb1f4b871c8f2ebff5601783fb0ce27b2e` on `cp/wave2-57-state-file-templates` (one commit on `9a26eeb1`) |
| Ticket | revision01, blob `e44499ba`, identical at the base, the candidate and the `cp/wave2-gates` tip; ticket 50 blob `62667f34` (same at base and tip); ticket 51 grammar read at the tip (`f70a404c`) |
| Reviewer | independent `ticket-review` seat (run `57-rev01-initial`) in its own detached worktree `.worktrees/57-state-file-templates-review`; authored nothing in this ticket |
| Summary | All four templates match the ticket text. The README states that the queue lives on the queue branch. The receipt template, filled by the reviewer with a real capture and digest, passes `evidence_gate.py` (exit 0), with and without its preamble. The ticket's four mutations and 18 of 22 reviewer counter-mutations turn red. Receipt, boundary, mypy, payload tests and the full suite all pass. One finding needs a correction: the test's byte checks read the working copy, not the committed blob. In a checkout made with Git for Windows' default `core.autocrlf=true`, 7 tests go red against a correct candidate, and that is the Windows environment ticket 59 will run (S57-01). One ticket defect goes to the control plane (S57-02). The other findings do not block. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| State row | PASS | reads `` `<STATE>`; dispatch=sha256:<64 lower-case hex of the dispatch file>; receipt `<repository-relative receipt path>` ``; the five base states plus `REVIEW_APPROVED` and `CONVERGENCE_REPLANNED`; says the `dispatch=` and receipt parts are present while a dispatch is pending (R4-1); digest = sha256 of the dispatch file's bytes, 64 lower-case hex |
| Queue template | PASS | blob bytes are exactly `{"entries": []}` plus LF; no BOM |
| Configuration template | PASS | exactly the eight keys of ticket 50's table; four strings, three non-empty lists of strings, `ci_status_command` with exactly one argument equal to `{sha}`, `timeout_seconds` 600 (an int, not a bool); `queue_path` placeholder is canonical; strict parse (repeated keys, NaN and BOM refused) |
| Receipt template | PASS | one run cell with `cell`, `candidate`, `tool_digest:` plus one `- path=sha256` line, `capture`, `exit` and a four-backtick raw block; one `STATEMENT` cell; LF only in the blob; names the eight placeholders a seat replaces |
| Receipt template, reviewer fill | PASS | filled with a real capture (mypy --strict on the test, `exit=0`) and the real sha256 of `evidence_gate.py` at the candidate (`0d099836…942f`), then run through `evidence_gate.py --require-cell R1`: `cells=1 defects=0`, exit 0, both with the preamble kept and with it dropped. Extra probes: a second `## STATEMENT` section gives exit 0; a `<statement-text>` placeholder left in place gives exit 0 (S57-06) |
| README | PASS except S57-04 | the four files are in the fixed structure and in a new "State files" section; build-order step 4 added; states "The queue file lives on the queue branch, not on the integration branch" |
| P1 / T1 (test file, mypy) | PASS | 38 passed, 1 skipped, 135 subtests; `-rs` shows the skip reason "the integration script is absent: its configuration parser cannot be run on the template" (integrate.py is in no commit on any branch); mypy --strict --python-version 3.11: no issues |
| Ticket mutations (rerun by the reviewer) | PASS | key removed, queue entry added, CR in the receipt, dispatch part dropped: each exit 1 with the named tests red; restored |
| Reviewer counter-mutations | FINDING | 22 run through other doors (digest width, digest wording, a dropped state, receipt part, queue extra key, queue final newline, queue whitespace, float timeout, `{SHA}`, `queue_branch`=branch, `queue_branch` removed, directory `queue_path`, repeated key, three-backtick fence, cell/heading mismatch, run field in the statement, a section without `cell:`, two candidate values, BOM, two README contradictions, build-order step removed). 19 red; 3 green: C3 (S57-03), D1 and D2 (S57-04) |
| CRLF checkout | FINDING | fresh clone with the host's system `core.autocrlf=true`: 7 failed in the new test (S57-01). In the same checkout, the gate, payload and template-status tests sampled (262) pass apart from the pinned-sha base failure |
| Receipt | PASS | `receipt_check.py` exit 0 (P1, T1, M1, F1, P9 ok; 0 defects); `evidence_gate.py` with the three wave-1 tools and `--require-cell` P1/T1/M1/F1/P9: `cells=5 defects=0`, exit 0; LF only in the receipt and all captures; an independent comparison confirms every raw block is byte-identical to its capture and every exit list equals the capture's `exit=N` lines in order; every cell is at the candidate |
| Boundary | PASS | exactly the six declared paths (2 M, 4 A); author and committer Johnny Liu <johnny.liu365@gmail.com>; stdlib only, no `Any`; `git diff --check` clean; no target-project or vendor name in the diff (only the plugin's own skill path); trailer `Co-Authored-By: Claude Sonnet 5.5` taken as naming the model that did the work, as instructed (the dispatch profile lists `implementation-standard` as Luna/xhigh; see the owner decision on wrong-model trailers in `6f1dbc52`) |
| Payload tests | PASS | `test_plugin_payload_boundary.py` and `test_plugin_distribution_payload_manifest.py`: 51 passed, 1 failed, and the failure is only `CommittedPinTests::test_the_pinned_sha_exists` |
| Full suite (host lock) | PASS | lock `C:/Temp/claude/jas-fullsuite.lock` acquired 10:27:33Z and released 10:42:52Z by `57-rev01-initial`; 8 failed, 3298 passed, 36 skipped, 6639 subtests in 916 s; all 8 failures are base names; zero new red. At acquisition other pytests were running in other checkouts: `.worktrees/60-gate-hardening-carried` (seven gate/payload test files) and `.worktrees/58-governance-hardening-row13` (three test files) |
| STATEMENT choices | 11 agree, 1 qualified | choice 6 ("CR refused in the three new files only") is right in intent, but it is checked on working-copy bytes (S57-01) |

### New findings

| ID | Class | Rule B | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| S57-01 | IMPLEMENTATION_DEFECT | does not block (no exit-code, safety or P0 effect) | Medium (correction requested) | `tests/test_state_file_templates.py:131-136, 343-350, 383-386, 527-530` | LF, final-newline and exact-byte checks read working-copy bytes. In a checkout with `core.autocrlf=true` (the Git for Windows system default on this host; also, as I understand it, the default on GitHub's `windows-latest` runners that ticket 59 targets, though I did not check a runner) the committed LF blobs come out as CRLF, and 7 tests go red against a correct candidate: 3 subtests of the LF test, queue exact bytes, receipt no-CR, receipt shape, digest line. Pitfall register family E "CRLF 工作副本". Fix inside the boundary: judge the committed blob (`git cat-file blob HEAD:<path>`, or the index) for the byte rules, or normalise before the shape checks and keep the CR rule on the blob | fresh clone, 7 failed; same clone re-checked-out with LF, 0 failed |
| S57-02 | TICKET_DEFECT | does not block | Low | ticket 57 boundary; ticket 50 queue file "UTF-8, LF" | Nothing pins the templates' line endings. A project copying `MERGE-QUEUE.TEMPLATE.json` from a CRLF checkout gets a CRLF queue file, which ticket 50 reads as a schema break (exit 2). The register prescribes a `.gitattributes` pin, but `.gitattributes` is outside the six declared paths. Route: control plane adds `template/doc/handoffs/governance/* text eol=lf` (or equivalent) to this ticket or ticket 59 | read; CRLF bytes observed in the clone |
| S57-03 | EVIDENCE_DEFECT | does not block; a gap that would let a regression through, so carry to the next change of this test | Low | `tests/test_state_file_templates.py:152-186` | Counter-mutation C3: setting `queue_branch` to the same placeholder as `branch` (queue on the integration branch, against the R4-8 amendment) gives zero red. The integrate.py cross-check would not catch it either, because it overwrites `queue_branch` | C3 green |
| S57-04 | IMPLEMENTATION_DEFECT (documentation only) plus EVIDENCE_DEFECT | does not block | Low | `template/README.md:29, 53, 56`; tests `:603-620` | The README tests pin only the presence of the queue-branch sentence. The structure comment (D1) and the State-files row (D2) can both say "integration branch" with zero red. The table's copy-to path `modules/tickets/<ticket>.md` differs from the AGENTS.md standard `modules/tickets/<feature>/<ticket>.md` | D1, D2 green; read |
| S57-05 | EVIDENCE_DEFECT | does not block; carry to ticket 50's landing | Low | `tests/test_state_file_templates.py:716-744` | When integrate.py lands, the cross-check overwrites every template value except the key set and `timeout_seconds` (all three argument lists are replaced) and asserts only `exit != 3`, so it never runs the template's own list shapes through the real parser (the "copy" shape). Never run: the script is absent | read; skip observed |
| S57-06 | OUT_OF_SCOPE_HARDENING | does not block | Low | `template/doc/handoffs/governance/RECEIPT.TEMPLATE.md:5-17` | "A placeholder left in place is a defect" is enforced by no gate (a left `<statement-text>` gives exit 0). `<candidate-sha>` says "40-digit", while ticket 50 says the repository's object format. "Replace every placeholder below" also covers the preamble table, which itself holds every placeholder. The statement heading is fixed as `## STATEMENT` and repeats once per choice (the gate accepts that) | gate probes |
| S57-07 | EVIDENCE_DEFECT | does not block | Low | seat receipt M1, P1 | The M1 "pytest tail" lists only `FAILED` lines, so the `SUBFAILED` cells counted in "5 failed" and "3 failed" are filtered out (review-checks counter-mutation point 5). P1 was run without `-rs`, so the skip reason claimed in the STATEMENT is not in a capture. The reviewer reran both unfiltered: the named tests are red and the skip reason is as stated | reviewer reruns |

Correction scope: S57-01 is the only finding that needs a correction before approval. S57-03, S57-04 and S57-07 may be closed in the same additive commit. S57-02 goes to the control plane. S57-05 and S57-06 are carried.

### Commands

- `git show --stat 27318feb`; `git diff --name-status 9a26eeb1 27318feb`; `git diff --check`; `git log -1 --format=%(trailers)`; blob ids via `git rev-parse <rev>:<ticket path>`
- `python doc/reviews/workflow-governance/evidence/48/receipt_check.py .worktrees/57-state-file-templates-out/RETURN.md .worktrees/57-state-file-templates-review` → exit 0
- `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py RETURN.md --repo <review worktree> --candidate 27318feb… --tool <three wave-1 scripts> --require-cell P1 T1 M1 F1 P9 --evidence-root .worktrees/57-state-file-templates-out` → `cells=5 defects=0`, exit 0
- Reviewer fill: `fill.py` (template read from the candidate blob, real mypy capture `R1.txt`, real digest of `evidence_gate.py` at the candidate) → `evidence_gate.py … --tool skills/johnny-project-takeover/scripts/evidence_gate.py --require-cell R1` → exit 0 (preamble kept and dropped); two-statement and leftover-placeholder probes → exit 0
- In a scratch clone of the candidate: `python -m pytest tests/test_state_file_templates.py -q -p no:cacheprovider -rs` (LF: 38 passed, 1 skipped; CRLF via system `autocrlf=true`: 7 failed); `mutate.py` (22 reviewer mutations) and `mutate_ticket.py` (4 ticket mutations), each restored with `git checkout --`, porcelain empty after; `python -m mypy --strict --python-version 3.11 tests/test_state_file_templates.py` → exit 0; `python -m pytest tests/test_plugin_payload_boundary.py tests/test_plugin_distribution_payload_manifest.py -q -rf` → only the pinned-sha failure
- Full suite: `fullsuite.sh` (atomic `mkdir` lock, owner file holding the run id and start time, `python -m pytest -q -p no:cacheprovider` in the review worktree, lock removed only if the owner file names `57-rev01-initial`) → 8 failed, all base names
- Unfiltered output was read for every run; no output-reducing wrapper was used for judging red or green.

Raw logs: kept in `.worktrees/57-state-file-templates-review-scratch/` (`F1.raw`, `lock-log.txt`, `M-review.txt`, `M-ticket.txt`, `fill/`); not committed. The scratch clone was removed. Porcelain is empty in the main checkout and in the review worktree, which is still detached at the candidate.

Not verified: integrate.py's real configuration parser (the script is not committed anywhere); a real GitHub `windows-latest` runner (the CRLF behaviour was reproduced only with this host's Git for Windows system config); Linux and macOS; SHA-256 object-format repositories; a full suite with no concurrent pytest in other checkouts.

```review-verdict
candidate: 27318feb1f4b871c8f2ebff5601783fb0ce27b2e
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/57-rev01-initial
reviewed_at: 2026-11-05
```

## Revision02 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `40b7ea469224b0fcd37d88ad77215eb5ecf2a827` on `cp/wave2-57-state-file-templates`. It is the correction commit on `27318feb`, which is one commit on `9a26eeb1`. |
| Ticket | Revision02 is blob `9687d875` at `2f6f01d1`. At the `cp/wave2-gates` tip `9b5c07cf` the blob is `196f6d3b`, and the only difference is the state row. Ticket 50 is `62667f34` (the same at base, candidate and tip). Ticket 51's grammar was read at the tip (`f70a404c`). |
| Reviewer | Independent `ticket-review` seat, run `57-rev02-initial`, in the detached worktree `.worktrees/57-state-file-templates-review`. The seat authored nothing in this ticket. The run was interrupted after the full suite finished, because the host process exited. It was resumed from the same scratch. Nothing was rerun except four counter-mutations (C3, D1, D2, W1), which were run in a new disposable clone. |
| Summary | The correction closes S57-01, S57-02, S57-03, S57-04 and S57-07. The `.gitattributes` change is one added line. A fresh clone made with the system `core.autocrlf=true` checks out the three files as LF and is green. Every byte rule reads the committed blob. All revision01 rules still hold. The reviewer filled the receipt template and it passes `evidence_gate.py`. The receipt, the boundary, mypy, the payload tests and the full suite pass. One new finding blocks approval under rule B because it breaks confinement (S57-08). The new `CrlfCheckoutTests` clones the repository under test by plain local path, so git hard-links the object files. The test's `remove_tree` then calls chmod on those shared files, which clears the read-only attribute on every object file of the source repository. On this host that is the shared `.git/objects` of the main checkout and every seat worktree. The fix is one flag, `--no-hardlinks`, which every other test in the suite that clones the repository already uses. Three findings are non-blocking hardening (S57-09 to S57-11). |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Templates exactly as the ticket states | PASS | `git diff 27318feb 40b7ea46` touches only `.gitattributes`, `template/README.md` and the test file, so the four templates are byte-identical to revision01, which passed. Read again at the candidate: the queue blob is `{"entries": []}` plus LF. The configuration has the eight keys, `queue_branch` `<integration branch>-queue` differs from `branch`, and `ci_status_command` holds exactly one `{sha}`. The receipt has one run cell, one `STATEMENT` cell and a four-backtick fence. The state row is unchanged. |
| README (S57-04) | PASS | The structure comment says "lives on the queue branch only". The State-files queue row says "on the queue branch". The ticket row's copy-to path is `modules/tickets/<feature>/<ticket>.md`, as in AGENTS.md. The old path occurs nowhere. |
| `.gitattributes` (S57-02) | PASS | `git diff 9a26eeb1 40b7ea46 -- .gitattributes` adds exactly `template/doc/handoffs/governance/* text eol=lf` after the two existing lines, which are unchanged. `git check-attr -a` gives `text: set` and `eol: lf` for each of the three files and no attribute for the README or the ticket template. `git ls-files --eol` gives `i/lf w/lf attr/text eol=lf` for the three files. |
| Fresh clone with `core.autocrlf=true` | PASS | Clone made with `--no-hardlinks`. `core.autocrlf=true` comes from `C:/Program Files/Git/etc/gitconfig`. The three files are `w/lf`; `.gitattributes`, the README, the ticket template and the test are `w/crlf`. Test file: 47 passed, 1 skipped, 149 subtests, exit 0. In revision01 the same kind of checkout gave 7 failed. |
| Byte rules on the committed blob (S57-01) | PASS | `committed_bytes` runs `git -C ROOT cat-file blob HEAD:./<path>`. The `./` resolves against `-C ROOT`, which is correct even if ROOT were a subdirectory. Every LF, final-newline, exact-byte, BOM and CR rule, and every shape check, reads that blob; the README and the ticket template are CRLF-normalised first. Git failing to serve the blob fails the test, with no fallback to the working copy. |
| `HEAD:./path` when HEAD is not the tree under test | Sound for the landing paths; see S57-09 | X20: a `--depth 1` shallow clone (the shape of the default CI checkout) is green. Ticket 50's integration clone fast-forwards, so HEAD equals the candidate there. When HEAD and the tree differ, the verdict describes HEAD: X1 and X2 (uncommitted or staged edit) give zero red, and X18 (HEAD at `27318feb`, tree and index at the candidate) gives 7 failed. The file mixes three sources: the HEAD blob for content, the index for `check-attr --cached`, and the working copy for existence. X19: from a `git archive` export with no repository, 110 failed. That is fail-closed, as STATEMENT 1 says. |
| `CrlfCheckoutTests` design | FINDING S57-08 (confinement); otherwise sound | The clone goes into `tempfile.mkdtemp` and is removed by `addCleanup`; no `state-template-*` directory was left after any run. HEAD is pinned with `update-ref --no-deref`. The test asserts the local `core.autocrlf=true`, checks out only `.gitattributes` and `CLONE_PATHS`, scrubs `GIT_*`, and guards against recursion with `JAS_STATE_TEMPLATE_CLONE_CHILD`. Two independent signals: the pin works end to end (no CR in the clone's working copy of the three files), and a CRLF working copy of all five templates plus `.gitattributes` is green. The child reads the same blob as the parent, so its byte rules add nothing on their own. It takes about 40 to 67 s under host load (two clones). Not confined: see the hard-link probe (H1) in the next row. |
| Hard-link probe (H1) | FINDING S57-08 | Scratch clone with all 254 object files set read-only. After `pytest -k CrlfCheckoutTests` (2 passed), 0 of 254 were read-only. Control with `tools/hardlink_probe.py`: plain local clone, nlink 2 → after `remove_tree` 254→0; with `--no-hardlinks`, nlink 1 → 254→254. Main checkout `.git/objects`: 7 of 254 read-only before my P1 run in the review worktree, 0 after. |
| Receipt template, reviewer fill | PASS | Template read from the candidate blob. Filled with a real capture (my T1 mypy output, LF) and the real sha256 of `evidence_gate.py` at the candidate (`0d099836…942f`). `evidence_gate.py --tool skills/johnny-project-takeover/scripts/evidence_gate.py --require-cell R1` gives `cells=1 defects=0`, exit 0, both with the preamble kept and with it dropped. Incidental check: my first fill used the raw mypy capture, which holds a CR, and the gate refused it with `CAPTURE_CR` and `BLOCK_MISMATCH`, exit 1. |
| P1 (test file) | PASS | Review worktree: 47 passed, 1 skipped, 149 subtests, exit 0. `-rs` shows the reason "the integration script is absent: its configuration parser cannot be run on the template". |
| T1 (mypy) | PASS | `mypy --strict --python-version 3.11 tests/test_state_file_templates.py`: "Success: no issues found in 1 source file", exit 0. |
| Revision01 mutations C3, D1, D2 (my rerun) | PASS | C3: `test_the_queue_branch_placeholder_differs_from_the_branch_placeholder` and `test_the_configuration_has_no_problem` red. D1: `test_the_structure_comment_for_the_queue_file_says_the_queue_branch` red. D2: `test_the_state_files_row_for_the_queue_file_says_the_queue_branch` red. All three were green in revision01. |
| CRLF-checkout door W1 (my rerun) | PASS | `committed_bytes` changed to return `path.read_bytes()`, in a checkout with system autocrlf: `test_gitattributes_holds_the_pin_once…` and both `CrlfCheckoutTests` red. |
| Reviewer counter-mutations X1–X17 (my doors) | 14 red, 3 green (S57-09, S57-10) | Red: X3 (later line overriding the receipt to `eol=crlf`, pin line kept once: `test_git_reports_lf…` red), X4 (pin narrowed to `*.json`), X5 (`*.bat` line removed), X6 (configuration blob CRLF), X7 (queue with a second final newline), X8 (README BOM), X9 (`{SHA}`), X10 (`600.0`), X11 (directory `queue_path`), X12 (three-backtick fence), X13 (statement with `exit: 0`), X15 (pin line duplicated), X16 (later `-text` line), X17 (eighth state `ARCHIVED`). Green: X1 (queue entry in the working copy only), X2 (staged only), X14 (a new README sentence elsewhere telling the reader to commit `MERGE-QUEUE.json` to the integration branch). Each was committed with `hash-object --no-filters` in a disposable clone, the whole file ran (no `-x`), and the clone was reset; porcelain was empty after. |
| Seat M1 (10 mutations) | PASS | Read unfiltered from the capture: every mutation exit 1 with the named tests red, `SUBFAILED` lines kept (S57-07). Each mutation is committed in the blob, which the design requires (STATEMENT 7). |
| Receipt | PASS | `receipt_check.py` exit 0 (P1, T1, M1, F1, P9 ok; 0 defects). `evidence_gate.py` with the three wave-1 tools and `--require-cell` P1/T1/M1/F1/P9: `cells=5 defects=0`, exit 0. My own comparison (`tools/receipt_compare.py`): 0 CR bytes in the receipt and all captures, no BOM; every raw block is byte-identical to its capture; every `exit:` list equals the capture's `exit=N` lines in order; every candidate is the candidate; every `tool_digest` equals the sha256 of the blob at the candidate. |
| Boundary | PASS | Exactly the seven declared paths (3 M, 4 A), cumulative from `9a26eeb1`. Author and committer are Johnny Liu <johnny.liu365@gmail.com> on both commits. `git diff --check` is clean. Stdlib only, no `Any`, no `type: ignore`. No target-project or vendor name in the diff; the only hit is the environment-variable prefix `JAS_`, the plugin repository's own abbreviation. The trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` is taken as naming the model that did the work, as instructed. |
| Payload tests | PASS | `test_plugin_payload_boundary.py` and `test_plugin_distribution_payload_manifest.py`: 51 passed, 1 failed, 252 subtests. The failure is only `CommittedPinTests::test_the_pinned_sha_exists`. |
| Full suite (host lock) | PASS | Lock `C:/Temp/claude/jas-fullsuite.lock` was held by `jas59-f1-979036-1793876976` (started 11:40:16Z) while I retried every 30 s from 11:50:53Z. Acquired 12:16:49Z and released 12:29:10Z by `57-rev02-initial`, removed only after the owner file named that run. Result: 8 failed, 3307 passed, 36 skipped, 6653 subtests in 738 s. All 8 failures are base names; zero new red; `test_state_file_templates.py` passed inside the suite. The host process exit came after the release, so the suite did not need a rerun. Pytests in other checkouts: at 11:45Z, before acquisition, there were the ticket 59 full suite (the lock holder), `.worktrees/60-gate-hardening-carried` gate tests and mutation workers, and ticket 50 `test_integrate.py` shards with their mutation workers. My process query at acquisition returned nothing because of a quoting error, so the set at acquisition is not recorded. |

### Revision01 findings

| ID | Class | Status | Evidence |
| --- | --- | --- | --- |
| S57-01 | IMPLEMENTATION_DEFECT | CLOSED | Fresh autocrlf clone green (was 7 failed). The seat's working-copy mutation is red, and so is my own rerun (W1). `CrlfCheckoutTests` passes against the correct candidate. |
| S57-02 | TICKET_DEFECT (control plane) → work in revision02 | CLOSED | One added line; `check-attr` gives `eol: lf` for the three files; removing the line is red (seat M1); X3, X4, X15 and X16 are red. |
| S57-03 | EVIDENCE_DEFECT | CLOSED | C3 red in my rerun. |
| S57-04 | IMPLEMENTATION_DEFECT (documentation) + EVIDENCE_DEFECT | CLOSED | Copy-to path corrected. D1 and D2 red in my rerun. Another door (X14) is still open; see S57-10. |
| S57-05 | EVIDENCE_DEFECT | CARRIED to ticket 50's landing, as the ticket says | The cross-check still skips (integrate.py is absent). |
| S57-06 | OUT_OF_SCOPE_HARDENING | CARRIED | No change. |
| S57-07 | EVIDENCE_DEFECT | CLOSED | M1 tails are unfiltered from the short summary on, `SUBFAILED` lines included. P1 ran with `-rs` and holds the skip reason. |

### New findings

| ID | Class | Rule B | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| S57-08 | IMPLEMENTATION_DEFECT (closure item: Revision02 S57-01 row, "a test runs the suite's byte rules in a clone") | **Blocks approval: breaks confinement.** The test writes outside its temporary directory, into the object store of the repository under test. | Medium | `tests/test_state_file_templates.py:437` (`clone … str(ROOT)` without `--no-hardlinks`), `:343-348` (`remove_tree` chmods on error) | Cloning a local path hard-links the object files. Git creates them read-only, so on Windows `shutil.rmtree` fails on them, and `make_writable` then runs `os.chmod(name, S_IWRITE)`. On NTFS the attribute belongs to the shared file record, so every object file of ROOT loses its read-only attribute. On this host ROOT's object store is the main checkout's `.git/objects`, which all seat worktrees share. Content is unchanged and Linux is unaffected (unlink does not need the write bit). Every other test that clones the repository already avoids this with `--no-hardlinks`, `--no-local` or a `file://` URL, for example `tests/test_live_install_qualification.py:133` and `tests/test_one_click_installer.py:243`. Fix inside the boundary: add `--no-hardlinks` (a full copy took 1.4 s here) and add a test that the mode bits of ROOT's object files are the same after the class as before. | H1: 254→0 read-only after `CrlfCheckoutTests`. Control: plain clone 254→0; `--no-hardlinks` 254→254. Main object store 7→0 after my P1. |
| S57-09 | OUT_OF_SCOPE_HARDENING | Does not block | Low | `:144-167` (HEAD blob), `:420` (`check-attr --cached`, the index), `:382-390` (working copy) | Zero red under review-checks point 2. The verdict describes HEAD, not the tree on disk: an uncommitted or staged template edit is invisible (X1, X2 green), and a tree at the candidate on a HEAD at `27318feb` is judged as `27318feb` (X18 red). The ticket allows "HEAD or the index", and on the landing paths (CI checkout, integration clone fast-forward, shallow clone) HEAD is the tree under test, so no regression can land through this. It is still a stale green for anyone who runs the file before committing. Suggestion: also assert that the CRLF-normalised working copy equals the normalised blob, so a divergence is red. | X1, X2 green; X18 7 failed; X20 green |
| S57-10 | OUT_OF_SCOPE_HARDENING | Does not block | Low | `:722-750` | The README pins check fixed places only: the structure line, the State-files row and the queue-branch sentence. A new sentence anywhere else that tells the reader to commit `MERGE-QUEUE.json` to the integration branch passes. | X14 green |
| S57-11 | OUT_OF_SCOPE_HARDENING (control plane: the dispatch cell template) | Does not block | Low | dispatch `JAS-57b_dispatch.yaml`, cell P1 | `-rs` replaces pytest's default `-r fE`. A red P1 capture would therefore list no `FAILED` or `ERROR` names in its short summary, only in the FAILURES section. My X18 run with `-rs` showed only `SKIPPED` in its summary. `-rfEs` keeps both. | X18 capture |

Correction scope: S57-08 needs one additive correction commit before approval. S57-09, S57-10 and S57-11 are carried. Under CodeReview §5, the next review is the single correction review of revision02.

### Commands

- `git log --format=… -3 40b7ea46`; `git diff --name-status 9a26eeb1 40b7ea46` and `27318feb 40b7ea46`; `git diff --check`; `git check-attr -a`; `git ls-files --eol`; `git rev-parse <rev>:<ticket path>` for ticket blob identity
- `python -m pytest tests/test_state_file_templates.py -q -rs -p no:cacheprovider` in the review worktree → exit 0; `python -m mypy --strict --python-version 3.11 tests/test_state_file_templates.py` → exit 0
- Fresh clone `git clone --no-hardlinks <review worktree> clone-ro` (system `core.autocrlf=true`), detached at the candidate → test file exit 0
- `tools/hardlink_probe.py` (plain clone and `--no-hardlinks`); read-only counts via PowerShell `IsReadOnly`
- `tools/mutate.py` (X1–X17, then C3, D1, D2, W1) in a disposable `--no-hardlinks` clone: each mutation committed with `hash-object --no-filters` (or left in the working copy or index for X1 and X2), the whole file run, then `reset --hard` and `clean -fdx`; porcelain empty after each batch
- X18: `checkout --detach 27318feb` then `checkout 40b7ea46 -- .`; X19: `git archive 40b7ea46 … | tar -x` into a temporary directory outside any repository, removed afterwards; X20: `git clone --depth 1 file://…`
- `receipt_check.py <out-c1>/RETURN.md <review worktree>` → exit 0; `evidence_gate.py RETURN.md --repo <review worktree> --candidate 40b7ea46… --tool <three wave-1 scripts> --require-cell P1 T1 M1 F1 P9 --evidence-root <out-c1>` → exit 0; `tools/receipt_compare.py`
- `tools/fill.py` (preamble dropped and kept) → `evidence_gate.py … --tool skills/johnny-project-takeover/scripts/evidence_gate.py --require-cell R1` → exit 0 twice
- `python -m pytest tests/test_plugin_payload_boundary.py tests/test_plugin_distribution_payload_manifest.py -q -rf`
- `tools/fullsuite.sh`: atomic `mkdir` lock, owner file holding the run id and start time, `python -m pytest tests -q -p no:cacheprovider` in the review worktree, lock removed only if the owner file names `57-rev02-initial`. Failure names compared to the normalised `^FAILED` lines of `jas48_F1_base.txt` with `comm` → no new name.
- I read the unfiltered output of every run. No output-reducing wrapper was used to judge red or green. Red names were taken from the FAILURES headers, because my runs used `-rs` (see S57-11).

Raw logs are in `.worktrees/57-state-file-templates-review-scratch/rev02/` (`F1.raw`, `lock-log.txt`, `M-review.txt`, `M-review2.txt`, `X18-…`, `X19-…`, `X20-…`, `hardlink-probe.txt`, `crlf-ro-probe.txt`, `fill/`, `tools/`) and are not committed. The scratch clones were removed. Porcelain is empty in the main checkout and in the review worktree, which is still detached at the candidate. One side effect cannot be restored exactly: the read-only attribute on the main object store's object files. Running the candidate's test (P1 and the full suite) cleared it, from 7 of 254 to 0, and the original set of 7 is not known. That attribute change is S57-08 itself. Git does not need the attribute to read or write the repository. I did not mark all objects read-only again, because that would change other seats' shared store beyond its state before my run.

Not verified: integrate.py's configuration parser (the script is not committed anywhere); a real GitHub `windows-latest` runner (the autocrlf behaviour was reproduced only with this host's Git for Windows system config); whether `remove_tree` hits hard-linked objects on the Linux runner (it should not, because unlink does not need the write bit); macOS; SHA-256 object-format repositories; a full suite with no concurrent pytest in other checkouts; the set of other pytests at the moment I acquired the lock.

```review-verdict
candidate: 40b7ea469224b0fcd37d88ad77215eb5ecf2a827
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/57-rev02-initial
reviewed_at: 2026-11-05
```

## Revision02 correction review

**Verdict: `CONVERGENCE_REVIEW_REQUIRED`.** Every finding still open is in the class rule B does not block on, so the control plane may record a convergence disposition.

| Field | Value |
| --- | --- |
| Candidate | `f423748b005ca17ab0a112c65188e55c07d8bac2` on `cp/wave2-57-state-file-templates`. It is one additive commit on `40b7ea46`, which is on `27318feb`, which is on `9a26eeb1`. |
| Ticket | Revision02 with "Correction 2 under revision02": blob `fc9e59f9` at `860057ac`. At the `cp/wave2-gates` tip `70dd7fb7` the blob is `3fd7bf97`; the only difference is the state row. Dispatch: `JAS-57c_dispatch.yaml`. |
| Reviewer | Independent `ticket-review` seat, run `57-rev02-correction`, in the detached worktree `.worktrees/57-state-file-templates-review`. The seat authored nothing in this ticket. This is the single correction review of closure revision02. |
| Summary | S57-08 is closed. The clone in `CrlfCheckoutTests` is made with `--no-hardlinks` through one helper. My H1 probe at the candidate found no file under the source `.git` added, removed or changed (size, mtime or mode) across the class, and all 335 read-only object files stayed read-only. So the mode check in `setUpClass` and `tearDownClass` writes nothing. S57-11 is closed: P1 ran with `-rfEs`. Every revision02 rule and every S57-01 to S57-07 closure still holds. The receipt passes both checkers. One new evidence gap is open (S57-12). The synthetic source-repository test pins the helper, not the clone call `make_clone` actually makes. The check on the repository under test can only go red if that repository holds at least one read-only object file. With `make_clone` cloning by hard links directly and every object file already writable, the whole file is green (K1w). The candidate's behaviour is correct, so rule B does not block. I could not run the full suite myself: the host lock was held by other seats for the whole 45-minute limit. The seat's F1 under the lock is verified against its capture. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| Diff | PASS | `git diff --name-status 40b7ea46 f423748b`: only `M tests/test_state_file_templates.py`. Additive: two helpers (`object_file_modes`, `clone_without_hardlinks`), `setUpClass`/`tearDownClass`, and the test `test_removing_the_clone_leaves_the_source_object_files_with_the_same_mode_bits`; `make_clone` calls the helper. No existing assertion changed, no import added. `git diff --check` is clean. |
| H1 hard-link probe at the candidate (S57-08) | PASS | `--no-hardlinks` clone at `f423748b`, all 335 object files set read-only, `.git` snapshotted before and after `pytest -k CrlfCheckoutTests -rfEs` (3 passed). Result: `added=0 removed=0 changed=0` over 360 files; read-only 335/335 before and after; no `state-template-*` directory left in `%TEMP%`. |
| Mode check writes nothing | PASS | `object_file_modes` runs `git rev-parse --path-format=absolute --git-path objects` and `stat` only. The H1 snapshot covers every file under `.git`, so nothing was written, not even an mtime change. In a worktree, `--git-path objects` resolves to the common object store. |
| Seat mutations marked equivalent (M-12, M-13) | Not equivalent mutants; no gap while both detectors stay; see S57-12 and S57-13 | M-12 deletes both detectors while the fault is absent, and M-13 deletes them while the fault is present. Neither is an equivalent mutant. M-13 shows that nothing else in the file catches hard-linking, so the two detectors are the only guard. My K2 (flag removed, synthetic assertion removed, `tearDownClass` check kept) gives ERROR at teardown, red. My K3 (flag removed, `tearDownClass` check removed) gives the synthetic test FAILED, red. So each detector alone catches removal of the flag from the helper, provided the repository under test holds a read-only object file. The open door is K1 (the next row). |
| Reviewer counter-mutations | 5 red, 1 green (S57-12) | K1, in a clone with all object files read-only and in a clone with only new loose objects read-only: `make_clone` changed to an inline `git clone` of ROOT without `--no-hardlinks`, helper and both assertions kept. ERROR at teardown, red. K1w, the same mutation with every object file of the repository under test made writable first: 48 passed, exit 0, zero red. K2 red; K3 red. W1, `committed_bytes` returning the working copy, committed so the inner clone runs it too: `test_gitattributes_holds_the_pin_once…` and both `CrlfCheckoutTests` red. In the seat's M1 the same door turned only 1 test red; see S57-13. |
| P1 (test file, S57-11) | PASS | Review worktree, `-q -rfEs`: 48 passed, 1 skipped, 149 subtests, exit 0, with the stated skip reason. |
| Fresh clone with `core.autocrlf=true` (S57-01, S57-02) | PASS | `--no-hardlinks` clone; `core.autocrlf=true` comes from the system config. The three files are `i/lf w/lf attr/text eol=lf`; the README is `w/crlf`. Test file: 48 passed, 1 skipped, exit 0. |
| T1 (mypy) | PASS | `mypy --strict --python-version 3.11`: no issues, exit 0. |
| Revision02 rules | PASS | Templates, README and `.gitattributes` are unchanged since `40b7ea46` (0 diff lines). The cumulative diff from `9a26eeb1` is exactly the seven declared paths. In the receipt, the ten correction-1 mutations are all red again. |
| Receipt template, reviewer fill | PASS | Template blob at the candidate, filled with a real LF capture (my T1) and the real sha256 of `evidence_gate.py` (`0d099836…942f`). `evidence_gate.py --require-cell R1`: `cells=1 defects=0`, exit 0, both with the preamble dropped and with it kept. |
| Receipt | PASS | `receipt_check.py`: exit 0 (P1, T1, M1, F1, P9 ok; 0 defects). `evidence_gate.py` with the three wave-1 tools and `--require-cell` P1/T1/M1/F1/P9: `cells=5 defects=0`, exit 0. My own comparison: 0 CR bytes in the receipt and every capture, no BOM; every raw block byte-identical to its capture; every `exit:` list equals the capture's `exit=N` lines in order (M1: `1×11,0,0`); every candidate and every `tool_digest` is correct at `f423748b`. The M1 tails are unfiltered from the short summary on, with 12 `SUBFAILED` lines and 1 `ERROR` line kept. |
| Boundary | PASS | Only the test file changed in this commit. Author and committer are Johnny Liu <johnny.liu365@gmail.com>. The trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` is taken as naming the model that did the work. Stdlib only. I read the added lines in full: they contain no model or vendor name and no target-project path. |
| Payload tests | PASS | 51 passed, 1 failed, 252 subtests. The failure is only `CommittedPinTests::test_the_pinned_sha_exists`. |
| Full suite, reviewer run | NOT RUN (lock unavailable for 45 minutes) | `fullsuite.sh`, run id `57-rev02-correction`: atomic `mkdir`, retried every 30 s from 18:46:12Z, gave up at 19:31:39Z (exit 99). The lock was never created by this run and nothing was removed. Holders seen in turn: `60-rev01-initial` (from 18:43:19Z), `jas59b-f1-1311949` (from 18:56:10Z), `58-rev01-initial` (from 19:08:24Z), `jas59b-f1-1318636` (from 19:20:59Z). Each new holder took the lock within 30 s of the previous release. Since the lock was never acquired, there was no acquisition moment to record. Pytests seen while waiting: at 18:44Z, the `60-rev01-initial` full suite (`pytest tests`) and a three-file run (`test_governance_consistency`, `test_gate_index_pins`, `test_gate_receipt_fence_check`); at 19:00Z, the `jas59b` full suite; at the end, `jas59b_cell.py F1` in `.worktrees/59-ci-linux-windows` with its full suite. |
| Full suite, seat F1 | PASS (seat evidence, verified) | Under the lock (`jas57c-f1-652-1793901873`, 18:31:59Z to 18:43:17Z): 8 failed, 3308 passed, 36 skipped, 6657 subtests in 676 s. All 8 failure names are base names (my `comm` against the normalised `jas48_F1_base.txt`); zero new red. The block is byte-identical to the capture. |

### Status of S57-08 to S57-11

| ID | Class | Status | Evidence |
| --- | --- | --- | --- |
| S57-08 | IMPLEMENTATION_DEFECT (confinement) | CLOSED | H1 at the candidate: no change under the source `.git`; read-only 335/335 kept. The seat's M-11 (flag removed) is red, as are my K2 and K3. |
| S57-09 | OUT_OF_SCOPE_HARDENING | CARRIED, as the ticket says | Unchanged by design: the file judges HEAD. |
| S57-10 | OUT_OF_SCOPE_HARDENING | CARRIED, as the ticket says | Unchanged. |
| S57-11 | OUT_OF_SCOPE_HARDENING (dispatch) | CLOSED | The dispatch P1 cell and my P1 use `-rfEs`. |

### New findings

| ID | Class | Rule B | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| S57-12 | EVIDENCE_DEFECT (closure item: Correction 2, "a test asserts that the mode bits of that repository's object files are the same after the class as before") | Does not block: the candidate's behaviour is correct, and the gap is in a pin. A regression would be red in a fresh checkout, where git makes every object read-only, and on this host's shared store, which holds 75 read-only object files of 335 at present. It is green only in a store with no read-only object file. Carry to the next change of this test file. | Low | `tests/test_state_file_templates.py:381-385` (helper), `:453-461` (`setUpClass`/`tearDownClass`), `:490-507` (synthetic test), `make_clone` | Of the two detectors, the synthetic test pins the helper, which is a copy of the path, not the clone `make_clone` makes. The check on the repository under test is environment-scoped: if every object file is already writable, a chmod-on-delete changes nothing it can see. K1w (`make_clone` cloning by hard links directly, every object file writable) is green. Suggested pin, independent of the host: in `make_clone`, assert that `st_nlink == 1` for the clone's pack and loose object files. | K1w green; K1 red when any object file is read-only |
| S57-13 | EVIDENCE_DEFECT (seat M1) | Does not block; the reviewer supplied the missing evidence, so no work is needed | Low | seat receipt M1, mutations 9, 12 and 13 | M-12 and M-13 are labelled "equivalent". They are detector deletions, not equivalent mutants, although the reasoning given (M-11 against M-13) is right. Mutation 9 (`committed_bytes` reading the working copy) was written to the clone's working copy but not committed, so the inner scratch clone ran the unmutated committed test file: 1 red here, against 3 in correction 1. My committed W1 gives 3 red. | W1, K2, K3 |

The open findings are S57-12 (EVIDENCE_DEFECT) and the carried S57-05 (to ticket 50's landing), S57-06, S57-09 and S57-10 (OUT_OF_SCOPE_HARDENING). None of them blocks approval under rule B: no exit-code misclassification, no safety or confinement break, no P0. Per CodeReview §5, the control plane may record a `convergence-disposition` with `disposition: APPROVED`, carrying S57-12 to the next change of this test file. This review does not start a third correction.

### Commands

- `git show --stat f423748b`; `git log -1 --format=…`; `git diff --name-status 40b7ea46 f423748b` and `9a26eeb1 f423748b`; `git diff --check`; `git rev-parse <rev>:<ticket path>`
- Review worktree: `python -m pytest tests/test_state_file_templates.py -q -rfEs -p no:cacheprovider` → exit 0; `python -m mypy --strict --python-version 3.11 tests/test_state_file_templates.py` → exit 0; `python -m pytest tests/test_plugin_payload_boundary.py tests/test_plugin_distribution_payload_manifest.py -q -rfE` → only the pinned-sha failure
- `receipt_check.py <out-c2>/RETURN.md <review worktree>` → exit 0; `evidence_gate.py … --candidate f423748b… --tool <three wave-1 scripts> --require-cell P1 T1 M1 F1 P9 --evidence-root <out-c2>` → exit 0; `tools/receipt_compare.py`; `comm` of the seat's F1 names against the base names
- `tools/fill.py` (dropped and kept) → `evidence_gate.py … --tool skills/johnny-project-takeover/scripts/evidence_gate.py --require-cell R1` → exit 0 twice
- Two `git clone --no-hardlinks` scratch clones detached at the candidate: one with every object file set read-only through PowerShell `IsReadOnly`, one left writable. `tools/snapshot.py` and `tools/snapdiff.py` around `pytest -k CrlfCheckoutTests` (H1). `tools/mutate2.py` for K1, K2, K3 and W1: each mutation written with `hash-object --no-filters`, committed and written to the working copy, the whole file run with `-rfEs`, then `reset --hard` and `clean -fdx`, with the read-only marking repeated before each run in the read-only clone. K1w was done by hand in the writable clone with every object set writable. Porcelain was empty in both clones afterwards, and both clones were removed.
- Fresh clone (system `core.autocrlf=true`): `git ls-files --eol`; the whole test file → exit 0
- `tools/fullsuite.sh` (atomic `mkdir` lock, owner file `run.txt`, 30 s retry, 45-minute limit, removal only if the file names `57-rev02-correction`) → gave up, exit 99; `tools/pytests.ps1` recorded the running pytests
- I read the unfiltered output of every run, with no output-reducing wrapper. Red and green were judged from the short summary of `-rfEs` runs, which lists `FAILED` and `ERROR` lines.

Raw logs are in `.worktrees/57-state-file-templates-review-scratch/rev02c/` (`P1.raw`, `T1.raw`, `payload.raw`, `H1.raw`, `h1-before.json`, `h1-after.json`, `M-review.raw`, `P1-crlfclone.raw`, `receipt_check.raw`, `evidence_gate.raw`, `receipt_compare.raw`, `fill/`, `lock-log.txt`, `tools/`, this `section.md`) and are not committed. Porcelain is empty in the main checkout and in the review worktree, which is still detached at the candidate. No run at this candidate changed an object file's mode.

Not verified: a reviewer full suite at this candidate (lock unavailable for the 45-minute limit; the seat's F1 under the lock is the full-suite evidence); integrate.py's configuration parser (absent); a real GitHub `windows-latest` runner and Linux; whether another seat running the file at the earlier candidate `40b7ea46` (hard links) while this candidate's class runs on the shared store could make this candidate's `tearDownClass` go red. It could not make it wrongly green.

```review-verdict
candidate: f423748b005ca17ab0a112c65188e55c07d8bac2
verdict: CONVERGENCE_REVIEW_REQUIRED
reviewer: seat:ticket-review/57-rev02-correction
reviewed_at: 2026-11-06
```

### Convergence disposition (2026-11-06, CodeReview §5 rule B)

The correction review closed S57-08 and S57-11. The one new open finding, S57-12, is an evidence gap in a pin, and the candidate's behaviour is correct: no exit code, safety or confinement effect, no P0. S57-13 needs no work (the reviewer supplied the evidence). Every open finding is in the class that does not block approval; the reviewer's verdict block above is unchanged. The reviewer could not run the full suite within the lock limit; the seat's locked F1 (8 failures, all base names) was verified against its capture, and the full suite runs again in the integration clone before landing.

| Finding | Class | Carried to |
| --- | --- | --- |
| S57-05 | EVIDENCE_DEFECT | ticket 50's landing (the integrate.py cross-check runs the template's own list shapes) |
| S57-06 | OUT_OF_SCOPE_HARDENING | a later template change |
| S57-09 | OUT_OF_SCOPE_HARDENING | the next change of this test file |
| S57-10 | OUT_OF_SCOPE_HARDENING | the next change of this test file |
| S57-12 | EVIDENCE_DEFECT | the next change of this test file (assert `st_nlink == 1` for the clone's object files in `make_clone`) |

```convergence-disposition
candidate: f423748b005ca17ab0a112c65188e55c07d8bac2
reviewer_verdict: CONVERGENCE_REVIEW_REQUIRED (seat:ticket-review/57-rev02-correction)
disposition: APPROVED
rule: CodeReview §5 rule B (owner-approved 2026-11-05)
carried:
  - S57-05
  - S57-06
  - S57-09
  - S57-10
  - S57-12
```
