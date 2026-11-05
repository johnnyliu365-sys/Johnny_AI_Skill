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
