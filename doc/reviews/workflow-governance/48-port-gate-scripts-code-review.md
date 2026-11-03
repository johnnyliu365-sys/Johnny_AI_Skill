# REVIEW — ticket 48 Port three proven gate scripts

> Commit identifiers in this record that predate 2026-11-03's identity rewrite are the pre-rewrite identifiers; read them through `doc/reviews/workflow-governance/evidence/commit-identity-rewrite-2026-11-03.txt` (old commit, new commit, identical tree).

## Revision01 initial review

| Field | Value |
| --- | --- |
| Verdict | `CHANGES_REQUESTED` |
| Reviewer | independent review seat. Authored nothing in this ticket. |
| Ticket leaf | `modules/tickets/workflow-governance/48-port-gate-scripts.md`. The blob was `6851ae4` at base `f4d4381`. It is `b180d06` at branch tip `7335e78`, which changed P4 during this review (P4 now also scopes `tests/test_gate_*.py` and reads its denylist from the dispatch). Both revisions were checked. |
| Spec | `modules/spec/workflow-governance.md` Revision 04 R4-2 (exit 0 pass / 1 red / 2 tool fault / 3 usage; "a red is never reported as a tool fault and a tool fault is never reported as a red"); R4-7 last bullet (a gate that cannot start exits 2, never 1) |
| Candidate | base `f4d43817fbcce48188e66c986b23ed7acde42046`; c1 `1d9f2a96f88d0ce36cc7fe744e5a024b5da8182c` (scripts); c2 `c41cc29d9ee760ceea4ad1ccd9365e1774e2103f` (tests) |
| Review checkout | `git clone --no-hardlinks` of the implementation clone; c2 detached; `core.autocrlf=false`; index rebuilt; `git status` empty. Base checkout made the same way at `f4d4381`. |
| Source | read-only checkout at `f9f4a64def9c205a656411da10509eea1c6de9e3`, clean. All six receipt sha256 values equal the sha256 of the working-tree files. Those files are CRLF, so the values are not the sha256 of the `git show` blobs. |
| References applied | CodeReview.md §1–§5; review-checks; implementation-tdd (reverse mutation); language-policy (Python 3.11 strict). XSS, secret, provider and UI references: not applicable, because the change is three stdlib CLI scripts and their tests, with no network, secret or DOM surface. |

## Findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| F-01 | `IMPLEMENTATION_DEFECT` | Medium | `skills/johnny-project-takeover/scripts/index_pins.py:256`, `:535`; docstring `:33-34` | An index file that is not UTF-8 raises an uncaught `UnicodeDecodeError` in `scan()`, and the process exits **1**, which reads as a contract red. The docstring promises exit 3 for an "unreadable index file". `main()` only checks `is_file()`. Likewise, `--json` to a path that cannot be written raises `FileNotFoundError`, which also exits 1. Both are tool or usage faults reported as reds, against R4-2. `dispatch_lint.py:97` catches the same case and exits 3, and has a test for it. `index_pins` has no such case. | probe B3: `printf '\xff\xfe| x |\n' > BAD.md; index_pins.py --check BAD.md` gives a traceback with exit=1. probe B3b: `--json <missing-dir>/out.json` gives a traceback with exit=1. |
| F-02 | `TICKET_DEFECT` | Medium | ticket "One observable behavior" and P6 (0/1/3 for every script); `index_pins.py:501-506`, `:421-430`, `:468-469`; `scripts/README.md` exit paragraph and index_pins paragraph | `SHALLOW_HISTORY` exits **1**. A shallow clone is an environment or tool fault: the history needed to derive the revision is absent. It is not a red of the index. The source exited 2 here. The scripts README states "a tool fault is never reported as a red" and, a few lines later, lists the shallow clone under exit 1. When `git` cannot start, the script reports "not inside a git repository" and exits 3, whereas R4-7 calls for 2. The ticket lists only 0/1/3 for each script, but the seat still gave `receipt_fence_check` an exit 2, so the ticket's list is not what decides the matter. The control plane should state the tool-fault exit for `index_pins` (proposed: `SHALLOW_HISTORY` and git-not-startable exit 2), add it to P6, and then the implementation follows. | Test `ShallowHistoryTests` asserts `code == 1`. probe B4: with `PATH=/nonexistent`, `index_pins.py --check INDEX.md` exits 3 with the message "not inside a git repository". |
| F-03 | `IMPLEMENTATION_DEFECT` | Medium | `dispatch_lint.py:43`, `:86`; `index_pins.py:321`, `:458` | Two options the seat added let a caller make a rule vacuous and still get exit 0. (a) `--chat-words ","` or `--chat-words ""` yields an empty list, so `chat = None` and R3 never fires: a dispatch containing a default chat word gets `LINT PASS` with exit 0. (b) `--sealed-state ""`, or any substring of a state cell such as `o`, makes every row "sealed" through the substring test at `:321`. A stale row is then never compared with `git log -1` and `--check` exits 0. That contradicts the ticket's observable behaviour ("gets the stale rows with exit 1"). The source hard-coded both values, so it had neither bypass. Expected fix: an empty or blank value is a usage error (exit 3), and the sealed word matches as a whole word. | probe B1: default exit=1; `--chat-words ,` exit=0; `--chat-words ''` exit=0. probe B2: stale row with default options exit=1; `--sealed-state ''` exit=0; `--sealed-state o` exit=0. |
| F-04 | `EVIDENCE_DEFECT` | Medium | `tests/test_gate_index_pins.py`, `tests/test_gate_dispatch_lint.py`; receipt "decisions" bullet 5 | The receipt says the port removed only project-specific real-shape cases, the mutation harness and correction ids. It also dropped generic source cases: the `_looks_pinned` negatives (bare hex, `sha256=` form, only one side present) and the three-row `MALFORMED_PIN` orphan canary. The parent-relative `../leaf` resolution and `SEALED_PIN_MISSING` also have no case in the port. Reverse mutations in a disposable copy survive, with `test_gate_index_pins.py` exit 0 on every one: X2 (bare 40/64-hex accepted as a pin), X5 (`MALFORMED_PIN` orphan finding removed), X1 (`while startswith("./")` replaced by `lstrip("./")`), X3 (`SEALED_PIN_MISSING` replaced by silent `continue`). For dispatch_lint, cutting the default R3 list from 9 words to the 3 the tests use (X6) still exits 0, and so does R5 skipping line 1 (X7). This is lower risk because the source tested only one word. | Commands below; X1–X3, X5–X7 each exit=0. X4 and X4b (`SKIP_UNTRACKED` / `SKIP_NO_BLOB` removed from `DEFECTS`) also survive. They are not counted against the tests, because after `resolve_leaf` filters on tracked files those branches can only be reached through a git failure. |
| F-05 | `EVIDENCE_DEFECT` | Low | `jas48_RETURN.md` cells P1–F1 | (1) No cell carries its own `tool_digest` or `exit` field. Tool digests appear once, in a header block. Their values are correct: each equals the sha256 of `git show c2:<path>`. Exit appears only in `result:` text. (2) Each `capture:` is a bare file name outside the repository, not a repository-relative path. (3) The raw blocks are not byte-identical to their captures. The P1, P2, P3, P5, P6 and F1 captures (and both base captures) are CRLF while the receipt blocks are LF. They are equal after CRLF→LF normalisation, which is the comparison `receipt_fence_check` itself makes. M1–M3 and P4 are identical apart from the final LF. (4) The P4 cell ran the `6851ae4` wording (scripts only). The current blob `b180d06` also scopes the tests, so the P4 evidence predates the current ticket revision. The reviewer reran P4 over both scopes: zero hits. | `receipt_check.py` (reviewer script) per cell: missing=['tool_digest','exit']; status IDENTICAL_AFTER_CRLF_NORMALIZE / IDENTICAL(+final LF). |
| F-06 | `OUT_OF_SCOPE_HARDENING` | Low | `receipt_fence_check.py` `main`, `explicit`, `scan` | Exit-0 passes inherited from the source, where nothing was checked: a section with zero fences (`fences=0 failures=0`, exit 0), `--scan` of a directory with no receipts (exit 0), and `--help` (exit 0, while the other two scripts exit 3). `--scan` ignores extra positional arguments, and `--require-cmd` is parsed but never used. None of this breaks the ticket's closure set. It belongs in the wave-2 evidence-gate ticket, which requires every cell to carry its fields. | probes: empty section exit=0; empty scan dir exit=0; `--help` exit=0. |

## Requested judgements

- **Port fidelity of dispatch_lint.** R1–R5 regexes, quote stripping, fence toggling and the 400-character limit are unchanged. Only the list became data, and the default keeps all 9 source words. No rule was weakened, apart from the F-03 empty-list bypass.
- **Port fidelity of receipt_fence_check.** The `## `-section, capture-distance (3 lines), cmd, redirect/chain/EVD/authority/loop/filter, elision, `LEGACY_UNCLAIMED_EXIT` and self-note logic is unchanged. The diff touches comments and docstrings, plus three things: the allowlist moved from a sidecar file to `--legacy-allowlist` (empty by default, so stricter); `default_authority_root` was added; and the filter-destination resolve was renamed, with the same value. The set of failure codes is identical, except for the new `EVIDENCE_ROOT_UNREADABLE` / `SCAN_ROOT_UNREADABLE`.
- **Port fidelity of index_pins.** Revision is still `git log -1 --format=%H -- <leaf>`, and Digest is still `sha256(git show <rev>:<leaf>)` on raw bytes. The defect set is the source's, plus `SHALLOW_HISTORY`. The state column now also accepts `state`. The source-specific leaf column aliases were removed, which is acceptable for the generic row format.
- **Exit decision, receipt_fence_check 2 vs 3.** An unreadable evidence or scan root exits 2, which matches R4-7. A missing heading, a missing receipt and an unreadable allowlist exit 3; this is accepted, since the result is never 0 and never a red. A missing heading could equally be a missing cell, which is a NOT_RUN red. Note this for the wave-2 evidence gate.
- **Exit decision, index_pins 1 for the shallow boundary.** Not accepted (F-02).
- **Exit decision, dispatch_lint --chat-words.** Replacing the list is accepted, and keeping the default is correct because it is R3. Accepting an empty list is not (F-03). An unreadable dispatch exits 3, which is consistent with the dispatch-lint row (0/1/3).
- **Genericity.** Neither the old P4 denylist nor the dispatch denylist (`<source-project names>`, not reproduced here) hits the scripts or `tests/test_gate_*.py`. A wider scan also found no hits for ticket, review or correction ids, rule-history tags, model or vendor names, environment names or dated narrative. The only CJK text is the R3 default list and the R4 terminator, which are rule data. The docstrings carry no project history.
- **Boundary.** `git diff --name-only f4d4381..c2` lists 7 created paths, all inside the `create` set. No forbidden path appears. The two `modify` paths (`.claude-plugin/plugin.json`, ticket README) are untouched. The payload `trees` already include `skills`.
- **Strict typing.** `mypy --strict --python-version 3.11` on the three scripts: no issues.
- **Admission note (not a seat defect).** The candidate sits on `f4d4381`. The branch tip is now `7335e78`. The README dependency "Ticket 47 reviewed" is not met: ticket 47 is `CONVERGENCE_REPLANNED / INDEPENDENT_REVIEW_PENDING`. Integration therefore needs that dependency cleared and a rebase. The candidate touches no path changed in `f4d4381..7335e78`.

## Commands and exits

| Cell | Command (reviewer's own) | Exit / result |
| --- | --- | --- |
| P1 | `python -m pytest tests/test_gate_dispatch_lint.py -q -p no:cacheprovider` | 0; 17 passed, 17 subtests |
| P2 | `python -m pytest tests/test_gate_receipt_fence_check.py -q -p no:cacheprovider` | 0; 45 passed, 3 subtests |
| P3 | `python -m pytest tests/test_gate_index_pins.py -q -p no:cacheprovider` | 0; 32 passed, 22 subtests |
| P4 | `grep -rniE "<source-project names>" skills/johnny-project-takeover/scripts` | 1 (zero hits) |
| P4 (b180d06 scope) | the same grep, plus a wider id/vendor/narrative pattern, over the scripts and `tests/test_gate_*.py` | zero hits |
| P5 | `python -m pytest tests/test_plugin_payload_boundary.py -q` | 1; only `CommittedPinTests::test_the_pinned_sha_exists`, the same id that fails at base (see F1 base set) |
| P6 | dispatch_lint: good / prose / no-args / `--bogus` | 0 / 1 / 3 / 3 |
| P6 | receipt_fence_check: match / body mismatch / no capture / missing ev-root / unknown heading / no-args / `--bogus` | 0 / 1 / 1 / 2 / 3 / 3 / 3 |
| P6 | index_pins: stale `--check` / `--write` / `--check` after write / no-args / `--check --write` | 1 / 0 / 0 / 3 / 3 |
| M1 | R3 append block deleted from a disposable copy of `dispatch_lint.py`; P1 | 1; 6 failed (R3 subtests, independent-violations, word-list, `--chat-words`) |
| M2 | `FENCE_CAPTURE_MISSING` append replaced by `pass`; P2 | 1; 2 failed (`test_requires_nearby_capture`, distance 3/4) |
| M2b | `CAPTURE_MISSING` append replaced by `pass`; P2 | 1; 2 failed |
| M3 | drift test `old_rev == new_rev and old_digest == new_digest` changed to `old_rev == new_rev`; P3 | 1; 5 failed |
| M3b | sealed verify `actual != old_digest` changed to `actual is None`; P3 | 1; 3 failed |
| X1–X7 | survivor probes (F-04) | 0 each |
| B1–B4 | behaviour probes (F-01, F-02, F-03) | as quoted in findings |
| mypy | `mypy --strict --python-version 3.11` on the 3 scripts | 0 |
| F1 c2 | `python -m pytest tests -q -p no:cacheprovider` on c2 | 1; 12 failed, 2010 passed, 31 skipped |
| F1 base | the same, on a disposable `f4d4381` checkout | 1; 12 failed, 1916 passed, 31 skipped |

The failure sets are identical: c2 adds no red. The 94 extra passes are the 17 + 45 + 32 new gate tests. The receipt's claim of 12 base failures is confirmed. All 12 are environment- or pin-bound; none touches the new files.

- `test_atomic_conditional_replace_capability.py`: `test_acr2_linux_requires_an_actual_linux_kernel_and_backend`, `test_acr6_exact_test_only_boundary`, `test_acr6_committed_candidate_diff_and_forbidden_paths`
- `test_guarded_integration_corrections.py`: `ReceiptBoundCorrectionTests::test_reviewed_router_profile_composes_return_integration_and_audit`
- `test_plugin_payload_boundary.py`: `CommittedPinTests::test_the_pinned_sha_exists`
- `test_plugin_publication.py`: `CandidateMetadataTests::test_l5_stale_candidate_pin_is_named_before_generation`, `PinnedTreeBindingTests::test_pinning_the_root_commit_is_rejected`, `PublicationReachabilityTests::test_deleting_the_actual_publication_anchor_makes_the_marketplace_pin_unreachable`, `PublicationReachabilityTests::test_the_marketplace_pin_is_bound_to_the_actual_publication_anchor`
- `test_refusal_guidance.py`: `ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered`
- `test_workflow_router.py`: `WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services`, `WorkflowRouterTests::test_temporal_approval_signal_requires_matching_authority_state`

Not verified: whether the seat's mutation runs are reproducible. Only the reviewer's own edits were run. Linux/POSIX behaviour of the cross-OS path normalisation was not run: this host is Windows only and WSL Ubuntu is unavailable.

## Revision02 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | c3 `0d1ef7540dda513f562210846fdb3dcfcf536eeb` on `cp/wave1-ticket48-candidate` (parent c2 `c41cc29d`, grandparent c1 `1d9f2a96`, base `f4d43817`) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; LF review clone of the seat's clone |
| Summary | Every cell in the closure set reproduces and all 12 ticket mutations go red; F-01..F-05 closed. Three new `IMPLEMENTATION_DEFECT`s against the exit contract (R4-2/R4-7, P6, the F-01 disposition) prevent `APPROVED`. One correction review remains for this closure revision. |
| Method | mutations as single-occurrence text replacements restored byte for byte, porcelain empty after each; pytest output read directly; CLI probes against `git show 0d1ef754:<path>` copies whose sha256 equal the receipt's `tool_digest`; references applied: CodeReview.md §1–§5, AGENTS.md P0, Workflow.md §0, review-checks.md, implementation-tdd.md; XSS, secret, provider and UI references not applicable (stdlib CLI scripts, no network, secret or DOM surface) |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 | PASS | 23 passed, 36 subtests, exit 0; same as the receipt. |
| P2 | PASS | 47 passed, 3 subtests, exit 0. |
| P3 | PASS | 47 passed, 58 subtests, exit 0; generic row format used. |
| P4 | PASS | dispatch denylist over the scripts and `tests/test_gate_*.py`: grep exit 1, zero hits; pattern extraction checked separately. |
| P5 | PASS | exit 1; only `CommittedPinTests::test_the_pinned_sha_exists`, the base id. |
| P6 | PASS, with gaps (NF-01, NF-02, NF-03) | one invocation per (script, code) pair: dispatch_lint 0/1/3; receipt_fence_check 0/1/2/3; index_pins 0/1/2/3 with 2 for SHALLOW_HISTORY (check and write; index unchanged), not a repository, unusable PATH, `--json` to a missing directory or a directory; 3 for bad option, no mode, missing file, directory argument, non-UTF-8 index. Every pair has a test (`ToolFaultTests` 6 cases, `ShallowHistoryTests` 2, `UsageTests::test_index_that_is_not_utf8_exits_3_not_1`, receipt_fence_check `ExitCodeContractTests`). |
| P7 | PASS | `--chat-words` with `''`, `,`, `' '`, `' , ,'` exit 3 with one usage line; default run exits 1 (R3). `--sealed-state` `''` or `' '` exit 3; on a stale `open` row, `o` and `pen` exit 1 (STALE); `OPEN` exits 1 with SEALED_PIN_INVALID (whole-cell match). Each case has a test. |
| P8 | PASS | every named case read and real: pinned-shape negatives (6 shapes, `_looks_pinned` and CLI), MALFORMED_PIN orphan canary (three rows), parent-relative leaf (`../x.md`, `./../x.md`), SEALED_PIN_MISSING, every default chat word (iterates `DEFAULT_CHAT_WORDS` itself), R5 on line 1. |
| P9 | PASS, one note (NF-05) | all 21 cells carry `cell`, `candidate`=c3, three `tool_digest` lines, `capture`, `exit`; digests equal sha256 of `git show 0d1ef754:<path>`; captures and receipt LF with 0 CR bytes; every raw block byte-identical to its capture. |
| M1–M12 | PASS (12 of 12 red) | own edits: M1 19 failed; M2 2 (+M2b 6); M3 7 (+M3b 4); M4 4 (different door); M5 2; M6 4; M7 4; M8 2; M9 4; M10 2; M11 6; M12 3; all restored clean. |
| Survivor probes | 3 survive | red: X1 `sha256=` form; X2 one side only; X3 orphan case check; X4 first malformed row only; X5 `..` from the wrong directory; X6 SEALED_PIN_MISSING revision-only; X7, X7b default words; X8, X8b R5 boundary; X9a not-repo→3; X9b `_toplevel` swallows OSError; X9e, X9f catch-all narrowed; X9g GitFault→1; X9h shallow→3; X9i dispatch_lint without the UnicodeDecodeError catch; X9j `--root`→2; X9k IndexUnreadable→1; X9l json never written. Survive: X5b (redundant branch, no behaviour change); X9d (json `except`→`raise`, catch-all still gives 2); X9c (ls-files failure→`set()` gives exit 3 instead of 2, untested; NF-03). |
| F1 | PASS | 10 failed, 2035 passed, 31 skipped, exit 1; same set as the receipt and ⊆ the 12 base names; zero new red; 2022 + 23 new = 2045 = 10 + 2035. |
| Observable behavior | FAIL in part | main path holds; "a red is never reported as a tool fault" fails under the host's default cp950 stdout (NF-01). |
| Boundary | PASS | 7 paths, all in `create`; plugin.json and the tickets README untouched; stdlib only, Python 3.11.9; `mypy --strict --python-version 3.11` no issues; no `Any`, no `type: ignore`. |
| Changed assertions | PASS | exactly the two the seat lists (ShallowHistoryTests 1→2; "not a repository" moved to `ToolFaultTests` exit 2); all other test changes are additions. |
| Receipt integrity | PASS, one note | chain, digests, captures and per-cell exits match; the F1 deviation (10 of 12 base names red) reproduced and accepted: both are environment- or pin-bound tests outside the change. |

The seat's reading of P6 "index argument missing" (an argument naming a missing file → 3; no argument keeps discovery mode) is accepted; the control plane may reword the ticket at the next revision.

### Prior findings

| ID | Status | Evidence |
| --- | --- | --- |
| F-01 | CLOSED, residue in NF-01 | non-UTF-8 index exits 3 without traceback; unwritable or directory `--json` exits 2 before `--write`; both state-writing scripts have a catch-all to 2; dispatch_lint can still reach the caller as an uncaught traceback with exit 1 through stdout encoding. |
| F-02 | CLOSED for the named cases | SHALLOW_HISTORY, git not startable and not a repository exit 2; README updated; `--root` not a directory (NF-02) and a failing git query (NF-03) do not follow the mapping. |
| F-03 | CLOSED | P7 probes and tests; M11, M12 red. |
| F-04 | CLOSED | P8 cases read; M4–M7, M9, M10 red; probes X1–X8 red. |
| F-05 | CLOSED | all five fields per cell, LF, byte-identical blocks; P4 over both scopes; residue NF-05. |
| F-06 | CARRIED (OUT_OF_SCOPE_HARDENING) | `--help` exits 0; empty section `fences=0 failures=0` exit 0; wave-2 evidence-gate ticket. |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| NF-01 | `IMPLEMENTATION_DEFECT` | Medium | `index_pins.py:462-469`, `receipt_fence_check.py:869-875`, `dispatch_lint.py:103-105` | Under the host's default stdout encoding (cp950, `PYTHONUTF8` unset) a red whose printed text contains a character outside the code page is reported wrongly: index_pins and receipt_fence_check as tool fault 2 (the c3 catch-all turns the `UnicodeEncodeError` into a fault after the red was computed); dispatch_lint ends in an uncaught traceback with exit 1. Against R4-2, the F-01 disposition and P6. Tests and dispatch always set `PYTHONUTF8=1`, so the guard exists only in that environment. Suggested fix: reconfigure stdout/stderr with `errors="backslashreplace"` at entry, plus a test with a non-cp950 leaf or capture name. | probes B7 (index_pins red row with a non-cp950 leaf: `tool fault: UnicodeEncodeError`, exit 2; with UTF-8, exit 1), B8 (receipt_fence_check CAPTURE_MISSING with a non-cp950 name: exit 2), B9 (dispatch_lint prose line: traceback, exit 1) |
| NF-02 | `IMPLEMENTATION_DEFECT` | Low | `index_pins.py:508-509`; `tests/test_gate_index_pins.py` UsageTests "root is not a directory"; README exit-3 list | `--root` missing or not a directory → exit 3, pinned by a new assertion; R4-7 says an unreadable input directory exits 2 and P6 maps "not a repository" to 2; receipt_fence_check maps its missing roots to 2; the README exit-3 list does not mention it. | probe B3: `--root <absent>` and `--root <file>` exit 3; X9j turns the usage test red |
| NF-03 | `IMPLEMENTATION_DEFECT` + `EVIDENCE_DEFECT` | Low | `index_pins.py:119-125`, `:138`, `:141-145`; docstring `:34-36` | The docstring says a failing git query exits 2; only a `git ls-files` failure does, and nothing tests it (X9c survives). When `git log -1 -- <leaf>` fails (exit 128) the leaf is reported as SKIP_UNTRACKED, a red with exit 1: a tool fault reported as a red. | probe B5 (HEAD object removed: `git log` 128, `ls-files` 0, `--check` reports SKIP_UNTRACKED, exit 1); X9c: P3 stays green |
| NF-04 | `OUT_OF_SCOPE_HARDENING` | Low | `index_pins.py:141-145` | A tracked leaf with a non-ASCII name appears quoted in `git ls-files` output under the default `core.quotepath`, never resolves, and gives a false SKIP_UNRESOLVED red; dates from c1; no closure cell names it. Candidate fix: `-c core.quotepath=false ls-files -z`. | probe B7 with UTF-8: SKIP_UNRESOLVED for a tracked non-ASCII leaf |
| NF-05 | `EVIDENCE_DEFECT` | Low | receipt cell P6 `exit:` | The field reads "0,1,2,3 per (script, code) pair; see capture" while the capture holds 23 exits; not machine-checkable. P7 shows the right form (exits listed in file order). | receipt P6 row |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | LF review clone of the seat's clone at `0d1ef754` (`core.autocrlf=false` set in the clone, index rebuilt) | 0 |
| 2 | `git rev-parse HEAD HEAD~1 HEAD~2 HEAD~3`; `git diff --name-only f4d43817..HEAD` | 0 (7 paths) |
| 3–5 | P1, P2, P3 pytest | 0 / 0 / 0 |
| 6 | P4 grep with the dispatch denylist | 1 (zero hits) |
| 7 | P5 pytest | 1 (base id only) |
| 8 | P6 and P7 CLI probes on the c3 blobs | as in the cells |
| 9 | shallow clone `--depth 1`, `index_pins --check` and `--write` | 2 / 2 |
| 10 | corrupt object store, `index_pins --check` | 1 (NF-03) |
| 11 | cp950 probes for the three scripts | 2 / 2 / 1 (NF-01) |
| 12 | `receipt_fence_check --help`; empty section | 0 / 0 (F-06) |
| 13 | sha256 of `git show 0d1ef754:<script>`; receipt field and capture check | 0 |
| 14 | `python -m mypy --strict --python-version 3.11` on the three scripts | 0 |
| 15 | mutation harness for M1–M12, M2b, M3b, X1–X9l, each followed by the named test file | 1 for each M; survivors X5b, X9c, X9d exit 0 |
| 16 | `git diff c41cc29d 0d1ef754 -- tests/` (removed lines) | 0 |
| 17 | F1 `pytest tests -q -p no:cacheprovider` | 1 (10 failed, all base names) |
| 18 | `git status --porcelain` in the review clone, the seat clone and the control plane | 0 lines each |

The 10 F1 failures: `test_atomic_conditional_replace_capability.py::test_acr2_linux_requires_an_actual_linux_kernel_and_backend`, `::test_acr6_exact_test_only_boundary`; `test_guarded_integration_corrections.py::ReceiptBoundCorrectionTests::test_reviewed_router_profile_composes_return_integration_and_audit`; `test_plugin_payload_boundary.py::CommittedPinTests::test_the_pinned_sha_exists`; `test_plugin_publication.py::CandidateMetadataTests::test_l5_stale_candidate_pin_is_named_before_generation`, `::PublicationReachabilityTests::test_deleting_the_actual_publication_anchor_makes_the_marketplace_pin_unreachable`, `::PublicationReachabilityTests::test_the_marketplace_pin_is_bound_to_the_actual_publication_anchor`; `test_refusal_guidance.py::ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered`; `test_workflow_router.py::WorkflowRouterTests::test_agents_mcp_and_temporal_adapters_load_without_external_services`, `::test_temporal_approval_signal_requires_matching_authority_state`.

Raw logs: retained by the reviewer seat on its host (P1–P5, P9, mypy, F1, probes 1–4, mutation summary, M1–M12, M2b, M3b, X*); not committed.

Not verified: the seat's own mutation runs; why the two base names pass in this environment; POSIX/Linux behaviour (Windows host only); unreadable-permission directories; the source checkout of the original scripts.

## Revision02 correction review

**Verdict: `CHANGES_REQUESTED`, `CONVERGENCE_REVIEW_REQUIRED`**

| Field | Value |
| --- | --- |
| Candidate | c4 `9e98c9626e26e09fc4209c21d2450686e118a857` (chain c4 → c3 `0d1ef754` → c2 `c41cc29d` → c1 `1d9f2a96` → base `f4d43817`) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; LF review clone of the seat's clone |
| Summary | c4 closes NF-01, NF-02 and NF-05, and NF-03 for the two git queries the finding named. One implementation defect stays open in the NF-03 family: a third git query, `git show <rev>:<leaf>`, still turns a failure into a contract red with exit 1 (NF-06), and the "with the git message" clause is not pinned by any test (NF-07). CodeReview.md §5 allows no third correction, so the candidate returns to the control plane. |
| References | CodeReview.md §1–§5, AGENTS.md P0, Workflow.md §0, review-checks.md (reviewer counter-mutation rule), implementation-tdd.md; XSS, secret, provider and UI references not applicable |

### Findings status

| ID | Status | Evidence |
| --- | --- | --- |
| NF-01 | CLOSED | B7, B8, B9 on the c4 blobs with `PYTHONUTF8` unset and `PYTHONIOENCODING=cp950` (and also with it unset): each exits 1, no traceback, prints `ก`; a tool fault whose stderr holds U+0E01 exits 2, escaped; `_harden_streams` reconfigures with `errors="backslashreplace"` only, so the host encoding stays. Mutations M13, R1, R2, R3 (`replace`), R4 (forcing utf-8) red; R8, R9 (dropping stderr from the reconfigure) survive harmlessly because stderr already defaults to `backslashreplace`. |
| NF-02 | CLOSED | B3: `--root <absent>` with `--check` and `--root <file>` with `--write` exit 2 with `tool fault: --root … is not a readable directory`; the usage case moved to `ToolFaultTests::test_root_that_is_missing_or_not_a_directory_exits_2`; docstring and README updated; M14 (back to 3) 6 subfailures, R7 (fault as exit 1) 6. |
| NF-03 | PARTIAL | B5 (HEAD object removed): `git log` 128, `ls-files` 0, index_pins exits 2 with `git log -1 -- leaf.md failed with exit 128: fatal: bad object HEAD`, no `SKIP_UNTRACKED`; corrupt `.git/index` makes `ls-files` 128 and index_pins exits 2 on `--check` and `--write`; M15 3 red, M16 (X9c) 2 red. Open: a failing `git show` reports `SKIP_NO_BLOB` or `SEALED_PIN_INVALID` with exit 1 (NF-06); the git-message clause unpinned (NF-07). |
| NF-04 | CARRIED | OUT_OF_SCOPE_HARDENING; c4 does not touch `core.quotepath`, as the dispatch required. |
| NF-05 | CLOSED | receipt P6 `exit:` lists 26 values equal in order to the 26 `exit=` lines of the capture; N1 3 of 3; N3 6 of 6. |

### Cells

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 | PASS | exit 0; 24 passed, 36 subtests (c3 23, plus the cp950 test) |
| P2 | PASS | exit 0; 48 passed, 3 subtests |
| P3 | PASS | exit 0; 52 passed, 67 subtests (c3 47, plus root fault, git log fault, ls-files fault, git fault as a process, cp950) |
| P4 | PASS | denylist (8 terms) over the scripts and `tests/test_gate_*.py`: exit 1, zero hits |
| P5 | PASS | exit 1; only `CommittedPinTests::test_the_pinned_sha_exists` (base name) |
| P6 | PASS, with gap NF-06 | one invocation per (script, code) pair: dispatch_lint 0/1/3; receipt_fence_check 0/1/2/3; index_pins 0, 1 (STALE), 2 (SHALLOW_HISTORY check and write, not a repository, empty PATH, `--root` missing, `--root` file, `--json` missing directory, `--json` directory, `git log` failing, `ls-files` failing), 3 (`--bogus`, no mode, missing index file, directory argument, non-UTF-8 index) |
| P7 | PASS | default R3 exits 1; `--chat-words` `''`, `,`, `' '`, `' , ,'` exit 3 with a usage line; `--sealed-state` `''`, `' '` exit 3; stale `open` row with `o`, `pen` exit 1 STALE; `OPEN` matches the whole cell |
| P8 | PASS | c4 removes no test line except the moved `--root` case; every named case present; P1 and P3 green |
| P9 | PASS, one note | see Receipt integrity |
| M1–M12 | not re-run (c3 review 12 of 12 red) | c4 changes none of those code paths; P1–P3 green at c4 |
| M13–M16 | PASS (4 of 4 red, reviewer's own edits) | M13 1 failed; M14 6 subfailed; M15 2 subfailed + 1 failed; M16 2 subfailed; all restored byte for byte, porcelain empty |
| Reviewer counter-mutations | 6 red, 4 survive | red R1, R2, R3, R4, R7; survive R8, R9 (harmless), R5, R6 (removing git stderr from the fault message leaves P3 green: NF-07) |
| F1 | PASS | 10 failed, 2042 passed, 31 skipped, exit 1 (2035 + 7 new tests); all 10 in the 12 base names; zero new red; same set as the seat's |
| c3 → c4 non-weakening | PASS | only removed test line is the UsageTests `--root` entry, now asserted as exit 2 in ToolFaultTests; every other test change additive; script removals are old docstrings, the `--root` usage return, the `code == 0 and` condition (replaced by a raise) and the old `ls-files` message |
| Code review | PASS except NF-06, NF-07 | streams reconfigured once at entry before any output, encoding kept; typing complete; `mypy --strict --python-version 3.11` no issues (mypy 2.3.0); no `Any`, no `type: ignore`; stdlib only (`io` added); README and docstrings cover `--root` and the git-query exits |
| Boundary | PASS | `git diff --name-only f4d43817..9e98c962`: the 7 create paths; plugin.json and the tickets README untouched; no forbid path |
| Receipt integrity | PASS, one note | the 13 run cells each carry `cell`, `candidate`=c4, three `tool_digest` lines equal to sha256 of `git show 9e98c962:<path>`, `capture`, `exit`; RETURN.md and all captures 0 CR bytes; every raw block byte-identical to its capture; `exit` lists match capture order. Note: the trailing `## changed_assertions` section carries `cell:` but no `tool_digest`, `capture` or `exit`; a statement, not a run, which an R4-7 evidence gate would read as `NOT_RUN`; its content (one changed assertion) matches the diff |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| NF-06 | `IMPLEMENTATION_DEFECT` (residue of NF-03; against R4-2 and the Correction 1 NF-03 row) | Low | `index_pins.py:137-149` (`blob_sha256_at` turns a non-zero `git show` into `None`), `:391-393` (`SKIP_NO_BLOB`), `:380-384` (`SEALED_PIN_INVALID … = N/A`); docstring `:36-37`; README lines 75-77 | `git show <rev>:<leaf>` is the third git query and its failure is still a contract red with exit 1; the rev comes from a successful `git log` and the leaf is tracked, so this failure can only be an object-store or promisor fault. c4 narrowed the docstring and README from "a git query fails" to the two named queries instead of fixing it. If the control plane reads the NF-03 parenthetical as the complete scope, reclassify as OUT_OF_SCOPE_HARDENING. Code read only: `shallow_boundary` (`:157-171`) also turns a failing `rev-parse` into `set()`. | offline blobless sparse clone (`--filter=blob:none --sparse`, promisor remote moved away): `git log` 0, `ls-files` 0, `git show` 128; `--check` and `--write` give `SKIP_NO_BLOB`, exit 1; a sealed row gives `SEALED_PIN_INVALID … = N/A differs`, exit 1; a local repo with the leaf blob deleted also gives `SKIP_NO_BLOB`, exit 1 |
| NF-07 | `EVIDENCE_DEFECT` (NF-03 disposition "with the git message") | Low | `tests/test_gate_index_pins.py:638`, `:653` | The new fault tests assert only the script's own prefix (`"git log"`, `"git ls-files"`), never git's stderr; removing `{self.last_stderr}` from either message leaves P3 green. The behaviour is correct at c4. | counter-mutations R5, R6: P3 exit 0, 52 passed |
| NF-08 | `OUT_OF_SCOPE_HARDENING` (note) | Low | `index_pins.py:131-132` | In a repository with no commits a staged leaf now exits 2 (`does not have any commits yet`); before c4 it was `SKIP_UNTRACKED` exit 1. A leaf with no history in a repository that has commits is still exit 1. Matches the dispatch; recorded so a follow-up decides whether an unborn HEAD is a red or a fault. | probe "unborn HEAD": `git log` 128, index_pins exit 2 |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | LF review clone of the seat's clone at `9e98c962`; `git log --format='%h %p'` | 0 (chain as stated) |
| 2 | CRLF scan of the worktree against the blobs | 0 (2 out-of-scope files, explained) |
| 3 | sha256 of `git show 9e98c962:<script>` against the worktree and the receipt | 0 (13 of 13 cells) |
| 4 | `git diff --name-only f4d43817..9e98c962`; `git diff 0d1ef754..9e98c962` (removed lines) | 0 (7 paths; 1 test line removed) |
| 5 | F1 `PYTHONUTF8=1 python -m pytest tests -q -p no:cacheprovider` | 1 (10 failed, all base names) |
| 6 | P1, P2, P3, P5 pytest one at a time | 0 / 0 / 0 / 1 |
| 7 | P4 grep with the denylist | 1 (zero hits) |
| 8 | `python -m mypy --strict --python-version 3.11` on the three scripts | 0 |
| 9 | probes: cp950 B7/B8/B9 (PYTHONIOENCODING=cp950, then unset), B3, B5, `ls-files` failure, blob removed, unborn HEAD | 1/1/1; 2/2; 2; 2/2; 1 (NF-06); 2 |
| 10 | offline blobless sparse clone: `--check`, `--write`, sealed row | 1 / 1 / 1 (NF-06) |
| 11 | one invocation per (script, code) plus the P7 options | as in P6 and P7 |
| 12 | mutation harness M13 M14 M15 M16 R1–R9 (single-occurrence edit, named test file, byte restore, porcelain) | 1 for M13–M16, R1, R2, R3, R4, R7; 0 for R5, R6, R8, R9 |
| 13 | stderr-only mutated copies with a non-cp950 fault message | 2 / 2 (harmless) |
| 14 | receipt check (fields, digests, LF, block equals capture, exit order) | 0 |
| 15 | `git status --porcelain` in the review clone, the seat clone and the control plane | 0 lines each |

Raw logs: retained by the reviewer seat on its host; not committed.

Not verified: M1–M12 re-run at c4 (code unchanged since c3; c3 review 12 of 12 red); the seat's own mutation runs; POSIX/Linux behaviour; unreadable-permission directories; a real console (as opposed to a pipe) under cp950; whether `rev-parse` can fail inside `shallow_boundary` while the other queries succeed (code read only).

## Revision03 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | c5 `947e0e51446acf5516ca7a9f910ff39d13217c51` (chain c5 → c4 `9e98c962` → c3 `0d1ef754` → c2 `c41cc29d` → c1 `1d9f2a96` → base `f4d43817`) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; LF review clone of the seat's clone, index rebuilt |
| Summary | c5 does what it was asked: all four git queries exit 2 with git's own message when the environment is broken; all cells reproduce and all 18 mutations go red. One problem blocks approval: P10's own rule makes some real reds come out as tool faults. In a healthy repository (`git fsck` exit 0) a sealed row whose recorded revision is wrong, and an open row whose leaf was deleted in its last commit, now exit 2 where c4 correctly exited 1. R4-2 says a red is never reported as a tool fault and R4-3 would send the fault to tool repair instead of an index fix. The script follows P10 word for word, so this is a ticket defect (NF-09) for the control plane. |
| References | CodeReview.md §1–§5, AGENTS.md P0, Workflow.md §0, review-checks.md (counter-mutation rule; pytest read unfiltered), implementation-tdd.md; XSS, secret, provider and UI references not applicable |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 | PASS | exit 0; 24 passed, 36 subtests |
| P2 | PASS | exit 0; 48 passed, 3 subtests |
| P3 | PASS | exit 0; 55 passed, 73 subtests (c4's 52 plus git show open, git show sealed, rev-parse in the shallow check) |
| P4 | PASS | dispatch denylist over the scripts and `tests/test_gate_*.py`: exit 1, zero hits |
| P5 | PASS | exit 1; only `CommittedPinTests::test_the_pinned_sha_exists` (base name) |
| P6 | PASS | one invocation per (script, code) pair on the c5 blobs: dispatch_lint 0/1/3; receipt_fence_check 0/1/2/3; index_pins 0, 1, 2 (real `--depth 1` SHALLOW_HISTORY check and write with the index unchanged, not a repository now with git's `fatal:` text, empty PATH, `--json` to a missing directory), 3 (`--bogus`, no mode, missing index file, non-UTF-8 index) |
| P7 | PASS | default chat word 1; `--chat-words` `''`, `,`, `' '`, `' , ,'` exit 3; `--sealed-state` `''`, `' '` exit 3; stale `open` row with `o`, `pen` exit 1 STALE; `open` against an `OPEN` cell matches the whole cell |
| P8 | PASS | every named case present and run; c5 touches none |
| P9 | PASS | see Receipt integrity |
| P10 | PASS as frozen; the frozen rule itself is NF-09 | own probes, each exit 2 with git's stderr and no `SKIP_NO_BLOB` / `SEALED_PIN_INVALID` / `SKIP_UNTRACKED`: leaf blob deleted (open and sealed × check/write, index unchanged); corrupt `.git/index`; HEAD object removed; real `--depth 1` clone with a malformed `.git/shallow`. cp950 probes B7, B8, B9 exit 1, no traceback, `ก` printed. `--root` absent or a file exit 2 |
| M1–M12 | PASS (12 of 12 red) | own edits on c5 |
| M13–M18 | PASS (6 of 6 red) | M13 1, M14 6, M15 3, M16 2; M17 rebuilt as the ticket describes 5 (the seat's `return None` shape 5); M18 per message: git log 3, git show 5, ls-files 2, `--is-shallow-repository` 2, `--show-toplevel` 2, `rev-parse --git-dir` 0 (NF-10); every file restored byte for byte, porcelain empty |
| Counter-mutations | 7 red, 1 survives | R1 GitFault as exit 1: 15; R2 git show stderr cut: 4; R3 `--is-shallow-repository` failure → `set()`: 2; R5 `_toplevel` failure → `None`: 2; R6 sealed path swallows the fault: 2; R7 open path swallows the fault: 2; R8 `last_stderr` from stdout: 7; R4 `--git-dir` failure → `set()` survives (NF-10) |
| F1 | PASS | run 1: 11 failed = the 10 base names plus one transient oracle `PROCESS_FAILED` under host load (that file alone: 34 passed); run 2: 10 failed, 2045 passed, 31 skipped; all 10 among the 12 base names; zero new red |
| Observable behavior | FAIL in part (NF-09) | the main path holds and environment faults exit 2; reds that now exit 2 in a healthy repository: J1 (sealed row, revision a real commit where the leaf did not exist), J2 (sealed row, revision names no object), J3 (open row, leaf deleted in its last commit then re-added to the index only); c4 gave 1/1/1 |
| Boundary | PASS | `git diff --name-only f4d43817..947e0e51`: the 7 create paths; c5 touches only `index_pins.py`, the scripts README and `tests/test_gate_index_pins.py`; plugin.json and the tickets README untouched; stdlib only; `mypy --strict --python-version 3.11` no issues; no `Any`, no `type: ignore`; docstring and README say any failing git query exits 2 with git's message |
| Receipt integrity | PASS | 8 run cells each carry `cell`, `candidate`=c5, three `tool_digest` lines equal to sha256 of `git show 947e0e51:<path>`, `capture`, `exit` in capture order (P10 7 values; M17-M18 1,1); 0 CR bytes; every raw block byte-identical (P10 compared fence-aware); the statement section carries `cell: STATEMENT` |
| Changed assertions | PASS (diff); judgement in NF-09 | the only weakened-looking line is `assertIsNone(blob_sha256_at(..., "never-added.md"))` → `assertRaises(GitFault)` + `assertIn("fatal:")`; the helper move keeps `assertNotEqual(returncode, 0)`; everything else additive. The changed assertion is literally what P10 requires but pins the J1 shape as a tool fault; the seat's behaviour note is not accepted under R4-2 when the cause is the recorded revision rather than the environment (NF-09) |

### Prior findings

| ID | Status | Evidence |
| --- | --- | --- |
| F-01 | CLOSED | non-UTF-8 index exits 3 without traceback; `--json` to a missing directory exits 2 |
| F-02 | CLOSED | SHALLOW_HISTORY, git not startable and not a repository exit 2; M8 red |
| F-03 | CLOSED | P7; M11, M12 red |
| F-04 | CLOSED | P8; M4–M7, M9, M10 red |
| F-05 | CLOSED | five fields per run cell, LF, byte-identical blocks |
| F-06 | CARRIED | OUT_OF_SCOPE_HARDENING |
| NF-01 | CLOSED | cp950 probes exit 1; M13 red |
| NF-02 | CLOSED | `--root` absent or a file exits 2; M14 red |
| NF-03 | CLOSED | git log and ls-files failures exit 2 with git's text; M15, M16 red |
| NF-04 | CARRIED | OUT_OF_SCOPE_HARDENING; the non-ASCII leaf still gives a red (SKIP_NO_PATH_IN_CELL) |
| NF-05 | CLOSED | `exit` lists every exit in capture order |
| NF-06 | CLOSED for environment failures; overreach in NF-09 | blob-deleted and malformed-shallow probes exit 2; `SKIP_NO_BLOB` removed; M17 red |
| NF-07 | CLOSED except one query (NF-10) | git's message pinned for log, show, ls-files, `--is-shallow-repository`, `--show-toplevel`; not for `rev-parse --git-dir` |
| NF-08 | CARRIED | OUT_OF_SCOPE_HARDENING; an unborn HEAD is a fault |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| NF-09 | `TICKET_DEFECT` (P10 against R4-2 and R4-3) | Medium | ticket P10 row; `index_pins.py:150-152`, `:387-391`; docstring `:26-28` vs `:36-39`; `tests/test_gate_index_pins.py:119-124` | P10 makes every non-zero `git show` exit 2. On the sealed path the revision comes from the index under check, so a wrong sealed pin is a red; on the open path a tracked leaf whose last commit deleted it is a work-tree red. Both now exit 2, contradicting R4-2 and routing an index error to tool repair (R4-3), and contradicting the docstring's own sealed rule. NF-06's premise holds only for the open path with a live leaf. Suggested rule: check the recorded revision and path first; revision not a commit, or path not in its tree, while the repository is complete → red; tree lists the path but the blob cannot be read → fault (exit 2); one test per side. | J1/J2/J3 probes with `git fsck --no-dangling` exit 0: c5 2/2/2 (`fatal: path '…' exists on disk, but not in '<rev>'`); c4 1/1/1 |
| NF-10 | `EVIDENCE_DEFECT` (P10 "one test per query") | Low | `index_pins.py:173-175`; ToolFaultTests | `git rev-parse --git-dir` in the shallow-boundary check has no test: turning its failure into `set()` (R4) or dropping git's text (M18e) leaves P3 green; probably unreachable once `--is-shallow-repository` succeeded; merge the two calls into one query. | R4, M18e: P3 exit 0, 55 passed |
| NF-11 | `TICKET_DEFECT` (closure set) | Low | ticket Acceptance table | The revision03 table lists M1–M12, M17 and M18; M13–M16 exist only in the c4 dispatch, so the frozen closure does not name them. | ticket at the control plane; the c4 dispatch cell M13-M16 |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | LF clone of the seat's clone at `947e0e51`; `git log --format='%H %P' f4d43817..947e0e51`; `git ls-files --eol` | 0 |
| 2–4 | sha256 of `git show 947e0e51:<script>` vs the working tree and the receipt; `git diff --name-status f4d43817..947e0e51`; `git diff 9e98c962..947e0e51 -- skills/ tests/` | 0 (3 of 3 equal); 0 (7 A paths); 0 |
| 5 | F1 full suite twice, plus the oracle file alone | 1 (11: 10 base + 1 transient) / 1 (10 base) / 0 |
| 6–8 | P1, P2, P3, P5 pytest; P4 grep; `mypy --strict --python-version 3.11` | 0 / 0 / 0 / 1; 1 (zero hits); 0 |
| 9–12 | P10 probes (blob deleted ×4, corrupt index ×2, HEAD removed ×2, shallow malformed ×4); judgement probes J1–J3 on c5 and c4; cp950 B7–B9 and `--root` probes; P6/P7 probe script plus a real `--depth 1` SHALLOW_HISTORY check and write | 2 each; c5 2/2/2 vs c4 1/1/1; 1/1/1 and 2/2/2; as in P6 and P7; 2/2 |
| 13–14 | mutation harness M1–M12; M13–M16, M17, M17b, M18a–f, R1–R8 | 1 for each; 1 for each except M18e and R4 (0) |
| 15–16 | receipt check (fields, digests, CR bytes, block equals capture, exit order; fence-aware P10 compare); `git status --porcelain` in the review clone and the seat clone | 0; 0 / 0 |

Raw logs: retained by the reviewer seat on its host; not committed.

Not verified: the seat's own mutation runs; whether `rev-parse --git-dir` can fail after `--is-shallow-repository` succeeds; blobless or promisor partial clones at c5 (covered at c4); POSIX/Linux behaviour; a real console under cp950; unreadable-permission directories; the root cause of the transient oracle `PROCESS_FAILED` beyond host load.

## Revision04 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | c7 `4861c208cc9647dbd9482c9b2dcc44121bb70b40` (chain c7 → c6 `a02856b7` → c5 `947e0e51` → c4 `9e98c962` → c3 `0d1ef754` → c2 `c41cc29d` → c1 `1d9f2a96` → base `f4d43817`) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; LF review clone of the seat's clone |
| Summary | Closure revision04 mostly holds: every cell reproduces, all 21 ticket mutations (plus M18 variants a–h) turn red, J1–J3 exit 1 in healthy repositories while environment faults exit 2 with git's stderr. One Medium defect blocks approval (NF-12): a sealed row in a shallow clone is reported as `SEALED_PIN_INVALID` exit 1, an environment fault reported as a red; c6 re-introduced it (c5 gave exit 2). One Low implementation defect (NF-13) and one Low evidence defect (NF-14). One correction review remains. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| P1 / P2 / P3 / P5 | PASS | 24 passed; 48 passed; 65 passed, 85 subtests; P5 only the pinned-sha base name |
| P4 | PASS | the dispatch denylist (8 terms) over the scripts and `tests/test_gate_*.py`: zero hits; pattern sanity check 1 hit |
| P6 | PASS | one invocation per (script, code) pair on copies of the c7 blobs: dispatch_lint 0/1/3; receipt_fence_check 0/1/2/3; index_pins 0, 1, 2 (not a repository with git's `fatal:` text, `--json` to a missing directory, unusable PATH), 3 (`--bogus`, no mode, no args, `--check --write`, missing file, directory argument, non-UTF-8 index) |
| P7 | PASS | empty or blank options exit 3; substring states give STALE; whole-cell match |
| P8 | PASS | no P8 case removed; M4–M7, M9, M10 red |
| P9 | PASS with note (NF-14) | see Receipt integrity |
| P10 | FAIL in part (NF-12, NF-13) | healthy repositories: J1, J2, J5 (revision names a tree object) exit 1 SEALED_PIN_INVALID on check and write; J3 exit 1 SKIP_NO_BLOB, index unchanged; J4 (nested leaf, correct sealed pin) exit 0. Broken repositories: blob deleted with revision and tree intact (open/sealed × check/write) exit 2 with `fatal: bad object <rev>:leaf.md`; tree object deleted exit 2; HEAD object removed exit 2; corrupt `.git/index` exit 2; malformed `.git/shallow` exit 2. `GIT_TRACE` shows the shallow check is one invocation. cp950 B7–B9 exit 1, escaped, no traceback; `--root` absent or a file exit 2. Failures: in a `--depth 1` clone a sealed row pinned before the boundary exits 1 SEALED_PIN_INVALID on check and write (NF-12); in a linked worktree of a shallow clone SHALLOW_HISTORY is never raised (NF-13) |
| M1–M21 | PASS (21 of 21 red, plus M18 a–h) | own single-occurrence edits, restored byte for byte, porcelain empty |
| Counter-mutations | 14 red, 2 survive (harmless) | red R1–R6, R9–R16 (pre-checks skipped, faults swallowed into reds or empty results, batch-check stdin dropped, wrong answer line); survive R7 (unreachable answer guard) and R8 (`tree_lists` accepting a non-blob entry still ends in a digest mismatch, exit 1); no mutation covers NF-12 or NF-13 because neither has a test |
| F1 | PASS | 8 failed, 2057 passed, 31 skipped; every failure among the 12 base names; zero new red |
| Observable behavior | FAIL in part (NF-12) | main path, J1–J3 and every environment fault as specified; "history is shallow → exit 2" fails for sealed rows in a shallow clone and for any row in a linked worktree of one |
| Boundary | PASS | 7 `create` paths only; plugin.json and the tickets README untouched; `dispatch_lint.py` and `receipt_fence_check.py` unchanged since c4; stdlib only; `mypy --strict --python-version 3.11` no issues; no `Any`, no `type: ignore`; docstring and README state the fault-versus-red rule |
| Receipt integrity | PASS with note (NF-14) | both receipts 0 CR bytes; every run cell carries the five fields; exit lists in capture order; statement sections `cell: STATEMENT`; c6 changed-assertions statement matches the diff |
| Changed assertions | PASS | `git diff 947e0e51..4861c208 -- tests/` removes exactly two things, both correct under P10 (the J1 shape back to a red with a `missing_reason` assertion and the unreadable-blob fault moved to its own test; the shallow-check test probing the single combined query); everything else additive; c7 changes no existing assertion |

### Prior findings

| ID | Status | Evidence |
| --- | --- | --- |
| F-01, F-03, F-04, NF-01, NF-02, NF-03, NF-05, NF-06, NF-07, NF-10, NF-11 | CLOSED | as in the cells |
| F-02 | CLOSED for the main work tree; residue NF-12, NF-13 | real `--depth 1` SHALLOW_HISTORY on an open row exits 2; M8 red |
| F-05 | CLOSED; new residue NF-14 | |
| NF-09 | CLOSED for full repositories; residue NF-12 | J1, J2, J3, J5 exit 1 with `git fsck` exit 0; M19, M20 red |
| F-06, NF-04, NF-08 | CARRIED | OUT_OF_SCOPE_HARDENING |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| NF-12 | `IMPLEMENTATION_DEFECT` (against P10 "the environment cannot serve the query → exit 2", the observable behaviour "history is shallow → 2", and R4-2) | Medium | `index_pins.py:149-165` (`is_commit`: batch-check `missing` → `False`), `:190-192`, `:443-447`; docstring `:37-41` | In a shallow clone a sealed row whose recorded revision lies beyond the boundary names a real commit of the repository that is not present locally; `is_commit` returns False and the row is reported `SEALED_PIN_INVALID … is not a commit of this repository` exit 1, a false red that R4-3 routes to an index repair of a correct pin. The SHALLOW_HISTORY check inspects only DRIFT findings. c4 1, c5 2, c6 back to 1; no test. The script already asks git whether the repository is shallow, so it can fault (exit 2) when a revision is missing in a shallow repository. Not blocking: in a non-shallow repository whose commit object was deleted, the same row is also exit 1; a script cannot tell that from a mistyped revision without a connectivity walk. | S0 full repository sealed row exit 0; S1 its `--depth 1` clone (fsck 0, shallow true) `--check` and `--write` exit 1; S1 under the c4/c5/c7 blobs 1/2/1 |
| NF-13 | `IMPLEMENTATION_DEFECT` (P6 "2 = SHALLOW_HISTORY", M8 path) | Low | `index_pins.py:223`, `:231-234` | `shallow_boundary` reads `<git-dir>/shallow`; in a linked worktree `--git-dir` is `.git/worktrees/<name>` while `shallow` lives in the common directory, so the boundary set is empty: a stale open row reports STALE (exit 1) and `--write` pins the leaf to the boundary commit with exit 0, exactly what SHALLOW_HISTORY prevents; AGENTS.md P0 puts agent worktrees at `.worktrees/<ticket-id>`. Candidate fix: `--git-common-dir`. Related: `--is-shallow-repository` true with no shallow file found yields an empty set instead of a fault. | S4 main work tree exit 2 SHALLOW_HISTORY; S5 linked worktree `--check` exit 1 STALE, `--write` exit 0 `rewrote=1` |
| NF-14 | `EVIDENCE_DEFECT` (P9) | Low | c6 receipt run cells; captures in both out directories | (1) every c6 `tool_digest` block names `index_pins.py`, `scripts/README.md` and `tests/test_gate_index_pins.py` instead of the three scripts (values correct; c7 receipt has the right set); (2) c6 P1, P2, P3, P5, P10, F1 and c7 P3, M18f, F1 captures contain CRLF; raw blocks equal only after normalisation; P10 differs by two trailing LFs; (3) the c6 `## F1 failure set` section is a second run-shaped cell reusing `F1.txt` with no raw block | receipt check per cell; CR counts |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1–2 | LF review clone at `4861c208`; `git ls-files --eol`; chain; `git diff --name-status f4d43817..4861c208`; script and test diffs | 0 |
| 3–5 | P1, P2, P3, P5; P4 grep; mypy | 0/0/0/1; 1; 0 |
| 6–10 | P6/P7 probes; P10 judge (J1–J5 with fsck), broken (blob, tree, HEAD, index, lost commit), shallow (S0–S5 with `GIT_TRACE`, S1 under c4/c5/c7), cp950 and `--root` | as in the cells |
| 11 | receipt check on both receipts | 0 (NF-14) |
| 12 | process check, then F1 | 1 (8 failed, all base names) |
| 13 | mutation harness M1–M21, M18a–h, R1–R16 | 1 for every M and R1–R6, R9–R16; 0 for R7, R8 |
| 14 | `git status --porcelain` in the review clone, the seat clone and the control plane | 0 lines each |

Raw logs: retained by the reviewer seat on its host; not committed.

Not verified: the seat's own mutation runs; blobless and promisor partial clones at c7; POSIX/Linux behaviour; a real console under cp950; unreadable-permission directories; why the two workflow-router base names passed in this F1 run. Another seat's pytest (a different checkout) ran during the per-file mutation runs; none during F1.
