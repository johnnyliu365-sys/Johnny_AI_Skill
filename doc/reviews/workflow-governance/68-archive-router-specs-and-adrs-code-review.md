# REVIEW — ticket 68 Router library retirement (3): the seven router-era SPECs archived, a SPEC archive rule, the router-era ADRs superseded

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`.** The archive work is clean:
- The seven SPECs moved as 100% renames. Each blob id is identical at both paths.
- Every changed path is inside the boundary block, and no `forbid` path is touched.
- The year index has the seven rows in ticket order. Each row has all seven fields, and its SPEC ID matches the leaf.
- The nine ADRs are `SUPERSEDED` in place. Only their status lines changed, plus one metadata link in ADR-016.
- My link check over the 30 changed Markdown files finds 59 relative links and 0 dangling.
- My reruns of P9 and E1 pass.
- Three of my counter-mutations turn the governance test red, from doors the seat did not use.

One finding blocks approval, S68-01. The new "SPEC archive" section of `requirement-lineage.md` adds a fifth bullet that the ticket's rule list does not contain. That bullet says "An archived SPEC keeps its precedence note, and the governance-consistency test reads `doc/archive/specs/` as it reads `modules/spec/`". The reference ships in the payload, and it states rules for target projects. The precedence note (`CHG-20261103-043`) and `tests/test_governance_consistency.py` exist only in this repository. The ticket asks for that property in the test, not in the rule. The bullet also forced two payload declarations, `doc/archive/specs/` and `modules/spec/`, to be filed as `TARGET_OWNED`. In that sentence, though, the two paths describe our own test. The fix is two lines of prose plus two dictionary entries, and my FIX1 probe confirms it.

The other findings do not block:
- S68-02 and S68-06 are ticket defects for the control plane. ADR-019 is outside the boundary and still links to a moved SPEC. The payload-test clause of the ticket was stale.
- S68-03 and S68-04 are hardening. CM3, CM4 and CM6 are zero-red.
- S68-05 is an evidence defect. The ticket names an L1 capture, but the receipt has none.
- S68-07 is the replacement cell for executor-routing. It is for the owner to decide.
- S68-08 is the seat's untagged helper files.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/68-archive-router-specs-and-adrs.md`, closure revision01, read with `git show 96f095a9:…`. Boundary block: 18 `modify`, 1 `create` (`doc/archive/specs/`), 7 `delete`, 13 `forbid` |
| Spec / requirement | workflow-governance Revision 04; REQ-20261103-043 wave 3, owner decision 2026-11-18 "3A 4A"; owner decision B of 2026-11-03 (archive, not delete) |
| Rule at base | `git show 96f095a9:skills/johnny-project-takeover/references/requirement-lineage.md` (Retirement, Validation; no SPEC section) |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-68_dispatch.yaml`, base `96f095a900bf8b6efc554816461dfb1180a7f764`, cells P1 T1 M1 C1 F1 P9 E1. It has no L1 cell (see S68-05) |
| Candidate | `ef99068858f8be9dea770f099af0e80af1f4631c` on `cp/wave3-68-archive-specs`. `git ls-remote origin` gives the same sha. It is one commit (`git rev-list --count 96f095a9..ef990688` = 1), its parent is `96f095a9`, and `96f095a9` is an ancestor of `cp/wave3` |
| Commit identity | Author `Johnny Liu <johnny.liu365@gmail.com>`; trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` |
| Changed paths | 32 entries in `git diff -M --name-status 96f095a9 ef990688`: 7 `R100`, 2 `A` (`doc/archive/specs/README.md`, `doc/archive/specs/2026/README.md`), 23 `M` |
| Review worktree | `.worktrees/68-archive-specs-review`, detached at the candidate. `git status --porcelain --ignored` was empty before and after |
| Receipt | `.worktrees/68-archive-specs-out/RETURN.md` with `STATEMENT.txt` and captures P1, T1, M1, C1, F1, P9, E1, `F1.lock.txt` |
| CI run | 44355299685, event `push`, branch `cp/wave3-68-archive-specs`, `headSha` = candidate. `test (linux)` success, `test (windows)` success. The log has 0 `UNREGISTERED_FAILURE` and 0 `REGISTERED_NOT_FAILING` lines. Read with `gh run view` only |
| References applied | `AGENTS.md` (both P0 sections); `CodeReview.md` (whole file, §5 rule B); `review-checks.md` (test truthfulness with reviewer counter-mutation, path identity/prefix, token comparison, missing values, exception behaviour); `requirement-lineage.md` at base and at candidate |
| XSS / privileged JS | Not applicable. The change is Markdown documents and two Python test files, with no browser, DOM or JavaScript surface |
| Secret / provider / external effect | Not applicable. There is no secret, log, provider or webhook. The only external effect is the seat's push of its own branch, which the dispatch authorised |
| Agent control / profile fan-out / POC ancestry | Not applicable. There is one implementer seat, no Agent-control path, and no POC or staging |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Every changed path inside the boundary; nothing forbidden touched | PASS | Each of the 32 paths matches a `modify`, `create` or `delete` line. The 7 deletes are exactly the 7 `delete =` lines. The two `A` paths and the 7 rename targets are under `doc/archive/specs/`. The six requirement leaves are under `doc/requirements/active/`. No path is under `library/`, `skills/johnny-project-takeover/scripts/`, `doc/runbooks/`, `doc/reviews/`, `doc/handoffs/`, `doc/context/`, `modules/tickets/`, `.claude-plugin/` or `.codex-plugin/`. `Workflow.md`, `AGENTS.md` and `CodeReview.md` are untouched |
| 2 | Seven moves are 100% renames, byte-identical | PASS | `git rev-parse 96f095a9:modules/spec/<n>.md` equals `git rev-parse ef990688:doc/archive/specs/2026/<n>.md` for all seven (for example, router-framework `c3c994a9…` = `c3c994a9…`, context-load-telemetry `08c7ef3c…` = `08c7ef3c…`). `git cat-file -e ef990688:modules/spec/<n>.md` fails for all seven, so no SPEC remains at its active path. `git diff -M --stat` shows `0` changed lines for each rename |
| 3a | SPEC archive rule says what the ticket says | **FAIL: S68-01** | `requirement-lineage.md:30-46, 57-59` (lines at the candidate) carry the ticket's items. These are: the unchanged move to `doc/archive/specs/<year>/<slug>.md` with the archive year; the root lists only year partitions; the seven year-index fields; the active index keeps only the ID and archive reference; active documents cite the archive path; historical records keep their path; validation as for `ARCH-REQ`; and the three HALT cases. The bullet at lines 43-44 is not one of the ticket's rule items (S68-01). "The move is a rename; the content is not edited" (line 31) restates "unchanged" and adds nothing new |
| 3b | Consistent with the existing `ARCH-REQ` rules | PASS | The partition-only root matches "Archive roots list only direct partitions". Replacement "where one exists" matches "replacement IDs when any". Historical source commit and last active revision match the `ARCH-REQ` bundle fields. The new validation bullet reuses `HALT / REQUIREMENT_LINEAGE_INVALID` and contradicts no existing bullet |
| 4 | Archive root lists only year partitions | PASS | `doc/archive/specs/README.md` has one row, `2026` → `2026/README.md`. `doc/archive/README.md` gains the SPEC partition row |
| 5 | Year index: seven rows, ticket order, every field | PASS | `ARCH-SPEC-20261118-001` to `-007` are router-framework, private-router-saas, autonomous-collaboration-audit, receipt-bound-role-supervision, executor-routing, plugin-release-telemetry and context-load-telemetry, which is the ticket's order. Each row has an ID, a leaf link, the SPEC ID, the last active revision, the reason, the replacement and the historical source. Each SPEC ID is found in its leaf (7/7 by `grep`). The last-revision cells match each leaf's state row and its revision or amendment tables |
| 6 | Historical source commit holds the SPEC at its active path | PASS | Every row names `96f095a9…:modules/spec/<n>.md`, and those blobs exist (cell 2). `96f095a9` is the candidate's parent, so it is the last commit on this line with the active path |
| 7 | Active SPEC index | PASS | `modules/spec/README.md` drops the two rows it had for archived SPECs (receipt-bound-role-supervision, context-load-telemetry). A new section lists only the archive ID and the archive link for all seven, with no title narrative or status |
| 8 | Nine ADRs `SUPERSEDED`, with a Superseded-by line | PASS | 001, 002, 003, 010, 011, 012, 014, 016 and 029 each read `SUPERSEDED` with the previous state in brackets. Each has a line naming REQ-20261103-043, owner decision 2026-11-18 "3A 4A" and workflow-governance Revision 04 with its SPEC ID. ADR-002 and ADR-016 are Chinese documents and use `被取代：` with the same content. I accept that as the label in the document's own language |
| 9 | ADR decision text unchanged | PASS | `git diff -M 96f095a9 ef990688 -- doc/adr/ADR-*` touches only the status line or `## Status` paragraph, and adds the Superseded-by line. In ADR-014, the status continuation clause is kept word for word. The one other change is ADR-016:7, `關聯規格`, a metadata link repointed to the archive path. It is not decision text, and the STATEMENT names it |
| 10 | ADR README agrees | PASS | All nine rows read `SUPERSEDED`. Rows for 003 and 010 are new; see judgement J2 |
| 11 | Active references resolve (reviewer L1) | PASS, with S68-02 | `l1_68-rev01-initial.py` reads every non-deleted `.md` path of the diff from the candidate blobs and resolves each relative link against the candidate tree. The result is files=30, links=59, dangling=0 (`L1_68-rev01-initial.txt`). The seven archived SPECs contain no Markdown links, so the move breaks none of their own links. A repo-wide `git grep` for links into the seven old paths finds ADR-019:7 (outside the boundary, S68-02), `doc/handoffs/README.md:35` and three `modules/tickets/` leaves, and the last two groups are historical records the rule keeps |
| 12 | Governance test: the sweep reads the archive tree | PASS | `historical_files()` (sweep) and `note_defects()` (note) both add `archived_specs()`. CM1 drops it from the sweep only, and 5 tests go red. The seat's M1a dropped it from the note check only, and 3 went red. So both halves are pinned |
| 13 | The three ticket rule tests are real | PASS | Both paths: the seat's M1b is red, and the test starts with `assertEqual(archive_defects(self.base), [])`, so the red comes from the injected copy alone. Repeated ID: the seat's M1c makes two tests red. Missing note: M1a and my CM1 are red. Token exactness: CM2 is red on `ARCH-SPEC-20261118-0011`. Prefix: CM5 makes 17 tests red, including `test_a_similarly_named_archive_directory_is_not_the_spec_archive`. Undecodable archived SPEC: asserted for both the sweep and the note check, and red under M1a and CM1 |
| 14 | Changed fixtures still describe real paths | PASS | `ARCHIVED_SPEC` = `doc/archive/specs/2026/router-framework.md`, `ACTIVE_SPEC` = `modules/spec/review-assurance.md` (a historical active SPEC that carries the note) and the payload fixture `modules/spec/workflow-governance.md` all exist at the candidate |
| 15 | No existing assertion weakened | PASS | Three injection tests change only their target path. The undecodable/empty test keeps the active-SPEC case on `ACTIVE_SPEC` and adds the archived cases. `EXPECTED_TOLERATED` moves the executor-routing line to its archive path with the same count (2). In the payload test, the fixture swap keeps the same assertion, and the `_REFERENCES_OUTSIDE_PAYLOAD` equality assertion is unchanged |
| 16 | Payload test | PASS (judgement J4) | `git log -S'context-load-telemetry.md' 96f095a9 -- tests/test_plugin_payload_boundary.py` shows the declaration was removed by ticket 65 (`1e9f73da`), so nothing was left to move (S68-06). `test_the_spec_archive_is_not_a_payload_path` asserts four paths, including `doc/archive/specs-old/x.md` |
| 17 | P1 / T1 rerun (clone at candidate) | PASS | Two files: 1 failed (`CommittedPinTests::test_the_pinned_sha_exists`, allowed), 98 passed, 333 subtests, exit 1 (`BASE_68-rev01-initial.txt`). `mypy --strict --python-version 3.11` on both files: "Success: no issues found in 2 source files" |
| 18 | Receipt honest | PASS, with S68-05 | P9: `receipt_check.py <out>/RETURN.md <review worktree>` gives 6 `[ok]`, 0 defects, exit 0. E1: `evidence_gate.py` with the dispatched arguments and `--candidate ef990688…` gives `cells=7 defects=0`, exit 0. The P1 raw block is byte-identical to `P1.txt` (sha256 `23300e91f6155d6a597d8bae8cd579d6697c39ac71c3c13a4b3bd23441e69ef5` for both). The tool_digest values recompute to the same sha256 from the candidate blobs, for example `evidence_gate.py` = `89f8839b…f54afd` and `index_pins.py` = `63eff436…7b7ccf`. The STATEMENT's out-of-boundary list equals my grep (runbook:7, ADR-019:7, the archived private-router-saas self-reference, historical trees). Its PRD/CHG list equals my grep of `doc/requirements/active` acceptance sources (002, 006, 010, 023, 030 with amendment 033; 007 and 008 already retired) |
| 19 | Seat F1 | PASS | `F1.txt`: 5 failed, all within the 12 base names of `C:/Temp/claude/jas48_F1_base.txt`. CI Windows gives 5 failed, and CI Linux gives 345 failed + 2 errors with 0 unregistered. I did not rerun the full suite (see "Not verified") |
| 20 | Reviewer counter-mutations | 6 run (+1 fix probe); CM3, CM4, CM6 zero-red (S68-03, S68-04) | Table below |

### Judgement calls the seat reported

| # | Seat's call | Judgement |
| --- | --- | --- |
| J1 | Replacement "Revision 04" for 001, 003, 004, 005; "none" for 002, 006, 007 | Correct for 001 (Revision 04 replaces the Router loop), 003 and 004 (both carry Revision 04 amendments, and R4-1/R4-4 govern their subject), and 002, 006 and 007 (Revision 04 has no SaaS, release or telemetry rule). For 005 the call is doubtful, and the owner should decide it: see S68-07 |
| J2 | ADR README gains rows for 003 and 010 | Correct. The ticket requires "`doc/adr/README.md` shows the same state for each" of the nine, and that cannot hold without the two rows. The README is in the boundary |
| J3 | Scope line of REQ-20261103-043 repointed | Correct. The leaf is an active requirement under `doc/requirements/active/`, and the rule says active documents cite the archive path. The target blobs are identical, so the line still names the same Amendments entries |
| J4 | Payload test: no `DEVELOPMENT_ONLY` to move; one fixture changed; a not-in-payload test added; four `TARGET_OWNED` entries | The first three are correct. Of the four entries, `doc/archive/specs/README.md` and `modules/spec/README.md` are correct, because the rule tells a target project where its indexes live. `doc/archive/specs/` and `modules/spec/` are needed only by the S68-01 bullet, and in that bullet they describe this repository's own test. They go with S68-01 |
| J5 | First M1 capture regenerated | Acceptable. The rerun used the same three mutations, gave the same red sets and ran at the candidate. The capture in the receipt is the one that ran, and the STATEMENT discloses the regeneration and its reason (the exit-line format) |
| J6 | Helper scripts left in scratch and temp without a run-id tag | A process finding, S68-08. It does not affect the candidate |

### Reviewer counter-mutations

These ran in the disposable clone `.worktrees/68-archive-specs-review-scratch/clone-68-rev01-initial`. I made it with `git clone --no-hardlinks --no-checkout <main checkout>` and then `checkout --detach ef990688…`, and removed it after the review. Each run used `python -m pytest <full file(s)> -q -rfE -p no:cacheprovider`, with no `-x` and no output-reducing wrapper. I judged red and green on the unfiltered output in `CM_68-rev01-initial.txt`, which also records the diff and command of each run. After each run, `git checkout -- .` restored the clone, and porcelain was `[]` all seven times. The baseline was 1 failed (the pinned sha), 98 passed.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| CM1 | Other half of the sweep (the seat's M1a removed the note half) | Remove `specs += archived_specs(base, defects)` from `historical_files()` only | red ×5: `test_every_tolerated_hit_is_reported_by_file_and_count`, `test_the_archive_tree_is_in_the_sweep`, `test_a_retired_sentence_in_a_historical_spec_without_the_note_is_red`, `test_an_undecodable_or_missing_or_empty_document_is_red_not_skipped`, `test_the_same_sentence_under_the_note_is_tolerated_and_reported_with_its_count` |
| CM2 | Token comparison: prefix instead of exact | `ARCHIVE_ID.fullmatch` → `ARCHIVE_ID.match` | red: `SUBFAILED(bad='ARCH-SPEC-20261118-0011') test_an_archive_id_must_have_the_exact_format` |
| CM3 | Mixed active/archive reference outside the SPEC index (real tree) | `CONTEXT.md` router-framework row back to `modules/spec/router-framework.md`; both P1 files | **zero red**: only the pre-existing pinned-sha failure. `archive_defects` reads only `modules/spec/README.md` (S68-03) |
| CM4 | One leaf indexed twice (first match / overlap) | Add a row `ARCH-SPEC-20261118-008` → `router-framework.md` to the 2026 index | **zero red**: 57 passed. `indexed[leaf]` is overwritten without a check, so the rule's "one row per archived SPEC" is not pinned (S68-04) |
| CM5 | Path prefix: archive discovery widened | `SPEC_ARCHIVE_DIRECTORY = "doc/archive"` | red ×17, including `test_a_similarly_named_archive_directory_is_not_the_spec_archive`, `test_the_spec_archive_is_consistent` and `test_the_archive_tree_is_in_the_sweep` |
| CM6 | Root shape | Add a non-year row `misc` → `2026/router-framework.md` to `doc/archive/specs/README.md` | **zero red**: 57 passed. `archive_defects` skips the root, so "the root lists only year partitions" is not pinned (S68-04) |
| FIX1 | Fix probe for S68-01, not a mutation | Delete `requirement-lineage.md:43-44` | `test_every_reference_that_escapes_is_a_declared_exception` is red, naming exactly `'modules/spec/'` and `'doc/archive/specs/'` as declared but no longer escaping. No other test changes. The smallest fix is therefore those two lines plus `tests/test_plugin_payload_boundary.py:91` and `:96` |

### Findings

| ID | Class | Severity | Blocks? | File:line | Observation | Verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S68-01 | `IMPLEMENTATION_DEFECT` (frozen AC: the rule section lists the ticket's items; "introduces nothing the ticket did not ask for") | Medium | **Yes** | `skills/johnny-project-takeover/references/requirement-lineage.md:43-44`; `tests/test_plugin_payload_boundary.py:91, 96` | The shipped rule gains a normative bullet that is not among the ticket's rule items. It also names two things that exist only in this repository: the CHG-043 precedence note and the governance-consistency test. A target-project agent routed to this reference is told about a note and a test that do not exist for it. The bullet then forced `doc/archive/specs/` and `modules/spec/` into `_REFERENCES_OUTSIDE_PAYLOAD` as `TARGET_OWNED`, although in that sentence they describe our development material. That sidesteps `test_no_skill_or_command_points_at_our_own_development_material` by category, not by content. The ticket puts this property under the test (`tests/test_governance_consistency.py` bullet), where the candidate already implements it | `git grep -i 'governance-consistency\|precedence note' -- skills/` gives this line only. FIX1 shows the removal is self-contained | Same branch, additive correction: delete lines 43-44 and the two dictionary entries at `:91` and `:96`. Keep `doc/archive/specs/README.md` and `modules/spec/README.md`. Rerun P1, T1 and L1 |
| S68-02 | `TICKET_DEFECT` (boundary omitted an active reference) | Low | No. The seat kept to the boundary and listed it as the ticket instructs | `doc/adr/ADR-20260824-019-provider-usage-telemetry-evidence.md:7` | ADR-019 is `ACCEPTED` and not among the nine. It links `../../modules/spec/context-load-telemetry.md`, which no longer exists. After integration, the repository holds a dangling active reference, which the new rule calls `HALT / REQUIREMENT_LINEAGE_INVALID`. The ticket foresaw only the runbook and `library/workflow_router/README.md` | `git grep` for links into the old paths (cell 11). The STATEMENT lists it for ticket 67, and no ticket 67 leaf exists yet | Control plane: put ADR-019:7 (and the runbook line 7) in ticket 67's boundary. Alternatively, widen this ticket's boundary in a closure revision, so that the S68-01 correction repoints it too |
| S68-03 | `OUT_OF_SCOPE_HARDENING` | Low | No. The ticket froze no test for it, and the one-time L1 covers this ticket's files | `tests/test_governance_consistency.py:567-571` | `MIXED_ACTIVE_ARCHIVE_REFERENCE` is checked only in `modules/spec/README.md`. An active document, such as `CONTEXT.md` or a requirement leaf, that names an archived SPEC by its old path passes. This is the rule's "active documents cite the archive path" and "dangling or mixed reference" | CM3 zero red | Follow-up hardening of the same test. It would let a regression pass, so it should land with the next change to this check (ticket 67 sweeps these references) |
| S68-04 | `OUT_OF_SCOPE_HARDENING` | Low | No | `tests/test_governance_consistency.py:541-542, 557` | Two index-shape properties of the rule are not pinned. First, one leaf can be indexed under two IDs, because `indexed[leaf]` is overwritten silently. Second, the archive root can list a non-year row, because the root is skipped | CM4 and CM6 zero red | Follow-up: `DUPLICATE_ARCHIVE_LEAF` when `leaf in indexed`, and a year-pattern check on the root rows |
| S68-05 | `EVIDENCE_DEFECT` (receipt) | Low | No. My L1 reproduces it (cell 11) | `RETURN.md` (no L1 section); the ticket's TDD item 1 and DoD "L1"; the dispatch `cells` | The ticket says the link check "is checked by a script whose output is the L1 capture". The receipt has no L1 cell or capture, and the STATEMENT only reports "59 relative links, 0 dangling". The dispatch also left L1 out of `cells`, so the root cause is on the control-plane side | Read `RETURN.md` and the out directory listing | Since a correction is due anyway (S68-01), add an L1 cell with its capture to the correction receipt. Control plane: add L1 to this dispatch's cells |
| S68-06 | `TICKET_DEFECT` (stale clause) | Low | No | ticket, bullet `tests/test_plugin_payload_boundary.py` | The ticket says the `DEVELOPMENT_ONLY` declaration of `modules/spec/context-load-telemetry.md` "follows the move". Ticket 65 (`1e9f73da`) had already removed it, so it is absent at the base. The seat handled it correctly and said so | `git show 96f095a9:tests/test_plugin_payload_boundary.py \| grep context-load-telemetry` is empty; `git log -S` names `1e9f73da` | Control plane: no change to the candidate; note it in the ticket's completion write-back |
| S68-07 | `TICKET_DEFECT` (undecided "where it applies") | Low | No. The seat surfaced it for the owner | `doc/archive/specs/2026/README.md:9` | For `ARCH-SPEC-20261118-005` (executor-routing), the replacement is "workflow-governance Revision 04". The SPEC's subject is provider-neutral executor/model routing. Revision 04 (R4-1 to R4-8) has no model-routing rule: it only amended the SPEC's integration sentences (R4-4). Model choice now lives in `doc/runbooks/dispatch-model-profile.md`, which is not a SPEC | `grep -i 'model\|profile\|executor'` over `modules/spec/workflow-governance.md:158-230` finds no routing rule | Owner decision. If "none" (or "Revision 04, integration sentences only"), change one cell |
| S68-08 | `OUT_OF_SCOPE_HARDENING` (process / residue) | Low | No. The candidate is unaffected | `C:/Users/User/AppData/Local/Temp/{e68a..e68f,gen68}.py`, `base68.txt`; `.worktrees/68-archive-specs-scratch/*.py` | The seat left untagged helpers in its scratch directory and in the user temp directory, which is outside the dispatched locations. The dispatch residue rule names "directory, clone, lock and process", not files, so the seat could not remove them under its own run-id rule | `ls` of both locations | Control plane removes them after checking. The dispatch template's residue rule should also cover files and should keep helpers inside `scratch` |

### Commands

These ran from the main checkout unless noted. Python was `C:/Temp/claude/jas-venv/Scripts/python.exe` with `PYTHONUTF8=1`. My captures are in `.worktrees/68-archive-specs-review-scratch`.

- `git diff -M --stat`, `--name-status` and `--word-diff` for `96f095a9 ef990688`; `git rev-list --count`; `git ls-remote origin refs/heads/cp/wave3-68-archive-specs`; `git merge-base --is-ancestor 96f095a9 cp/wave3`
- For each of the seven: `git rev-parse 96f095a9:modules/spec/<n>.md` and `ef990688:doc/archive/specs/2026/<n>.md`; `git cat-file -e ef990688:modules/spec/<n>.md`
- `git grep` from the review worktree for the seven names (with `.md`, without `.md`, and as link targets), inside and outside `doc/reviews`, `doc/handoffs`, `doc/context` and `modules/tickets`; also `git grep` over the requirement leaves' acceptance sources
- `l1_68-rev01-initial.py <main> 96f095a9… ef990688…` → `L1_68-rev01-initial.txt` (files=30, links=59, dangling=0, exit 0)
- `python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py <out>/RETURN.md <review worktree>` → exit 0
- `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py <out>/RETURN.md --repo <review worktree> --candidate ef990688… --tool skills/johnny-project-takeover/scripts/index_pins.py --tool skills/johnny-project-takeover/scripts/receipt_fence_check.py --evidence-root <out> --require-cell P1 --require-cell T1 --require-cell M1 --require-cell F1` (from the review worktree) → `cells=7 defects=0`, exit 0
- `git show ef990688:<script> | sha256sum` for the four tool_digest scripts; `sha256sum P1.txt M1.txt`; the P1 raw block extracted and compared with `cmp`
- `gh run view 44355299685 --json …` and `gh run view 44355299685 --log` (0/0 checker lines, summary counts)
- In the clone: P1 files baseline → `BASE_68-rev01-initial.txt`; `mypy --strict --python-version 3.11` on both files; `cm_68-rev01-initial.py <clone> <out>` → `CM_68-rev01-initial.txt`

### Raw-log note

`L1_68-rev01-initial.txt`, `BASE_68-rev01-initial.txt` and `CM_68-rev01-initial.txt` are unedited tool output. CI was read with `gh run view` only. Nothing was pushed, and no run was triggered. No tracked file was modified anywhere. The single clone was made with `--no-hardlinks` and was removed after the review, as were my two helper scripts (`l1_68-rev01-initial.py`, `cm_68-rev01-initial.py`), the extracted P1 block and the CI log copy. The diff and command of each mutation are kept in `CM_68-rev01-initial.txt`. The host lock was not taken, because I ran no full suite. I did not touch the seat's worktree, out directory or scratch directory, or any other seat's worktree. I only read the seat's out directory and listed its scratch directory.

### Not verified

- A reviewer full suite at the candidate. The change is Markdown plus two test files, and no other test names a moved path (`git grep` outside the two test files finds only `tests/test_file_lock.py:62`, a `modules/element/…/context-load-telemetry` directory that did not move). The seat's locked F1 and both CI jobs cover it.
- The seat's M1a–M1c were not rerun. CM1–CM6 are independent of them, and their capture was read unfiltered.
- That `96f095a9` stays "the last commit with the SPEC at its active path" once the branch lands as a merge commit. The `cp/wave3` commits after `96f095a9` also hold the active paths. Any of them is valid evidence, and the cell names one that does.
- Linux behaviour of the new tests, beyond the CI Linux job's success with 0 unregistered failures.

```review-verdict
candidate: ef99068858f8be9dea770f099af0e80af1f4631c
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/68-rev01-initial
reviewed_at: 2026-11-19
```

```rework-record
candidate: ef99068858f8be9dea770f099af0e80af1f4631c
round: 1
kind: INITIAL
verdict: CHANGES_REQUESTED
causes: CONTROL_PLANE_RULE,IMPLEMENTATION_DETAIL
```

## Revision01 correction review

**Verdict: `APPROVED`.** Correction 1 (`c3ecdd6b`) applies the coordinator's dispositions exactly:
- **S68-01.** `requirement-lineage.md` loses the two bullet lines and nothing else. `tests/test_plugin_payload_boundary.py` loses the `doc/archive/specs/` and `modules/spec/` entries and nothing else. Both new regression doors, CM8 and CM9, are red.
- **S68-07.** The executor-routing replacement now reads "none (the semantic profile data stays in doc/runbooks/dispatch-model-profile.md)".
- **S68-05.** L1 is now a receipt cell with a capture, and E1 requires it. CM7 shows that E1 refuses a receipt without it.
- **S68-08.** The seat's untagged helpers are gone from both locations.

My L1, P9 and E1 reruns pass at the candidate. CM1, CM2 and CM5 are still red. I did not rerun the full suite, as the coordinator directed. The seat's locked F1 at the candidate and CI run 44367305470 cover it.

Four findings stay open, and none blocks approval under rule B. None of them changes an exit-code classification, breaks a safety or scope boundary, or violates P0:
- **S68-02** is a control-plane ticket defect: ADR-019:7 goes to ticket 67.
- **S68-03** and **S68-04** are hardening, carried as known debt.
- **S68-06** is a stale ticket clause that needs no change.

No implementation or evidence defect remains open.

| Field | Value |
| --- | --- |
| Ticket | Unchanged: closure revision01 at `96f095a9` |
| Correction authority | The coordinator's correction message, as relayed: S68-01, S68-07, S68-05 and S68-08 fixed; S68-02, S68-03, S68-04 and S68-06 left unchanged |
| Candidate | `c3ecdd6b761d3ad994a828090ab856163ead9f14` on `cp/wave3-68-archive-specs`. `git ls-remote origin` gives the same sha. It is one additive commit whose parent is `ef990688` (`git rev-list --count ef990688..c3ecdd6b` = 1), with no amend or force |
| Commit identity | Author `Johnny Liu <johnny.liu365@gmail.com>`; trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` |
| Changed paths (`ef990688..c3ecdd6b`) | `doc/archive/specs/2026/README.md` (+1/−1), `skills/johnny-project-takeover/references/requirement-lineage.md` (−2), `tests/test_plugin_payload_boundary.py` (−2). All three are inside the boundary. Nothing forbidden is touched, and the gate scripts are unchanged (`git diff --quiet ef990688 c3ecdd6b -- skills/johnny-project-takeover/scripts`) |
| Review worktree | `.worktrees/68-archive-specs-review`, detached at `c3ecdd6b`. `git status --porcelain --ignored` was empty before and after |
| Receipt | `.worktrees/68-archive-specs-out/RETURN.md` (LF, 0 CR). Cells P1, T1, M1, L1, C1, F1, P9, STATEMENT and E1 each name candidate `c3ecdd6b` |
| CI run | 44367305470, event `push`, `headSha` = candidate. `test (linux)` success, `test (windows)` success. The log has 0 `UNREGISTERED_FAILURE` and 0 `REGISTERED_NOT_FAILING` lines. Read with `gh run view` only |
| References applied | As in the initial review, plus `CodeReview.md` §5 rule B for this correction review |
| XSS / secrets / Agent control / profile / POC | Not applicable, for the same reasons as the initial review |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | S68-01: bullet and two entries gone, nothing else changed in those files | PASS | `git diff ef990688 c3ecdd6b -- skills/…/requirement-lineage.md` removes exactly the two lines of the bullet. `-- tests/test_plugin_payload_boundary.py` removes exactly `"doc/archive/specs/": "TARGET_OWNED"` and `"modules/spec/": "TARGET_OWNED"`. `doc/archive/specs/README.md` and `modules/spec/README.md` stay declared. The SPEC archive section now holds the four ticket bullets plus the validation sentence. P1 has 331 subtests where it had 333, which matches the two fewer `TARGET_OWNED` subtests |
| 2 | S68-07 cell | PASS | `doc/archive/specs/2026/README.md:9` replacement cell is "none (the semantic profile data stays in doc/runbooks/dispatch-model-profile.md)". This is the only changed cell in the file. The runbook path is plain text, not a link, so the L1 count is unchanged |
| 3 | S68-05: L1 is real and E1 requires it | PASS, with an observation | The receipt has an `## L1` cell (candidate `c3ecdd6b`, exit 0). Its raw block is byte-identical to `L1.txt` (sha256 `cc5531a6…d06f1e`). The E1 cell's command and capture include `--require-cell L1`. CM7: the same gate on a copy of the receipt with the L1 section removed gives `NOT_RUN L1: required cell has no run cell`, `cells=7 defects=1`, exit 1, which is contract red and not fault 2. Observation: `L1.txt` is a one-line summary (`links_checked=59 dangling=0`) with no per-link listing. The script it names (`l1_68.py`) was deleted under S68-08, so the capture cannot be recomputed from the receipt alone. My independent L1 (cell 4) reproduces the totals, so I record this only as advice: keep the L1 script beside the captures in future receipts |
| 4 | Reviewer L1 rerun | PASS | My checker reads candidate blobs: files=30, links=59, dangling=0, exit 0 (`L1_68-rev01-correction.txt`) |
| 5 | P9 / E1 rerun | PASS | `receipt_check.py <out>/RETURN.md <review worktree>`: 7 `[ok]` (P1 T1 M1 L1 C1 F1 P9) plus E1, 0 defects, exit 0. `evidence_gate.py` with `--candidate c3ecdd6b…` and `--require-cell P1 T1 M1 L1 F1`: `cells=8 defects=0`, exit 0. The tool_digest values recompute from the candidate blobs, for example `evidence_gate.py` = `89f8839b…f54afd` and `index_pins.py` = `63eff436…7b7ccf`. The P1 raw block is byte-identical to `P1.txt` (sha256 `de069cb9…b1b67d`). P1 has 1 failed (the allowed pinned sha), 98 passed. T1: "Success: no issues found in 2 source files", exit 0 |
| 6 | S68-08: the seat's residue is gone (by listing) | PASS | `ls C:/Users/User/AppData/Local/Temp` shows none of `e68a`–`e68f.py`, `gen68.py`, `base68.txt` or `now68.txt`. The only name containing `68` is the unrelated `339d3453-…ade68.tmp`. `.worktrees/68-archive-specs-scratch` is empty. `.worktrees/68-archive-specs-out/prev` does not exist. The host lock is held by `J70-r1`, not by `JAS68R1` |
| 7 | STATEMENT updated | PASS | It names correction 1, its dispositions, the two remaining `TARGET_OWNED` entries, replacement "none" for 005, the L1 cell and the removed residue. The out-of-boundary and PRD/CHG lists are unchanged and still match my grep from the initial review (no referencing file changed) |
| 8 | Seat F1 | PASS | Per the STATEMENT: 5 failed, all within the base names. That count matches CI Windows (5 failed) and the 0 unregistered failures on both jobs. Not rerun, by direction |

### Reviewer counter-mutations (correction)

These ran in the disposable clone `.worktrees/68-archive-specs-review-scratch/clone-68-rev01-correction`. I made it with `git clone --no-hardlinks --no-checkout <main checkout>` and then `checkout --detach c3ecdd6b…`, and removed it afterwards. Each run used `python -m pytest <full file> -q -rfE -p no:cacheprovider`, with no wrapper. The output in `CM_68-rev01-correction.txt` is unfiltered and records the diff and command of each run. After each run, `git checkout -- .` restored the clone, and porcelain was `[]` each time. CM7 ran on a copy of the receipt in the scratch directory, with output in `CM7_68-rev01-correction.txt`.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| CM1 (rerun) | Sweep half of the archive read | Remove `specs += archived_specs(...)` from `historical_files()` | red ×5, the same tests as at the initial review |
| CM2 (rerun) | Token exactness | `ARCHIVE_ID.fullmatch` → `.match` | red: `SUBFAILED(bad='ARCH-SPEC-20261118-0011')` |
| CM5 (rerun) | Path prefix | `SPEC_ARCHIVE_DIRECTORY = "doc/archive"` | red ×17 tests (plus the five `test_an_archive_id_must_have_the_exact_format` subtests) |
| CM7 (new) | The gate, not the test | E1 with `--require-cell L1` on the receipt minus its `## L1` section | red: `NOT_RUN L1: required cell has no run cell`, exit 1 |
| CM8 (new) | S68-01 regression: the prose comes back | Restore the deleted bullet in `requirement-lineage.md` without the entries | red: `test_every_reference_that_escapes_is_a_declared_exception` (`'doc/archive/specs/'` and `'modules/spec/'`), `test_no_skill_or_command_points_at_our_own_development_material`, `test_the_committed_payload_is_closed` (plus the pinned sha) |
| CM9 (new) | S68-01 regression: the declarations come back | Restore the two `TARGET_OWNED` entries without the bullet | red: `test_every_reference_that_escapes_is_a_declared_exception` (plus the pinned sha) |

### Findings (status after correction 1)

| ID | Class | Severity | Status | Blocks? | File:line | Observation / verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S68-01 | `IMPLEMENTATION_DEFECT` | Medium | **Closed** | — | `requirement-lineage.md:40-44`; `tests/test_plugin_payload_boundary.py:88-96` | Bullet and both entries are removed and nothing else changed (cell 1). CM8 and CM9 are red | — |
| S68-02 | `TICKET_DEFECT` (boundary) | Low | Open, owned by the control plane | No. Under rule B it changes no exit code, breaks no safety or scope boundary, and violates no P0 | `doc/adr/ADR-20260824-019-provider-usage-telemetry-evidence.md:7` | Unchanged: a dangling link to the old context-load-telemetry path, listed in the STATEMENT | Ticket 67 boundary |
| S68-03 | `OUT_OF_SCOPE_HARDENING` | Low | Carried | No (hardening) | `tests/test_governance_consistency.py:567-571` | Unchanged: mixed references are checked only in the SPEC index (initial CM3) | Known debt. It would let a regression pass, so it should land with the next change to this check |
| S68-04 | `OUT_OF_SCOPE_HARDENING` | Low | Carried | No (hardening) | `tests/test_governance_consistency.py:541-542, 557` | Unchanged: one leaf can be indexed under two IDs, and the archive root can list a non-year row (initial CM4, CM6) | Known debt |
| S68-05 | `EVIDENCE_DEFECT` | Low | **Closed** | — | `RETURN.md` `## L1`; E1 cell | The L1 cell is present and required by E1. CM7 is red. The summary-only capture is noted as advice (cell 3) | — |
| S68-06 | `TICKET_DEFECT` (stale clause) | Low | Open, no change needed | No | ticket, payload-test bullet | The candidate handled it correctly | Control plane, completion write-back |
| S68-07 | `TICKET_DEFECT` (replacement cell) | Low | **Closed** | — | `doc/archive/specs/2026/README.md:9` | The cell reads "none (…dispatch-model-profile.md)", as dispositioned | — |
| S68-08 | Process / residue | Low | **Closed** | — | `C:/Users/User/AppData/Local/Temp`; `.worktrees/68-archive-specs-scratch` | Listings show the files are gone (cell 6) | — |

### Commands (correction)

- `git rev-parse c3ecdd6b^`; `git rev-list --count ef990688..c3ecdd6b`; `git ls-remote origin refs/heads/cp/wave3-68-archive-specs`; `git diff -M --stat` and `git diff ef990688 c3ecdd6b`; `git diff --quiet ef990688 c3ecdd6b -- skills/johnny-project-takeover/scripts`
- `l1_68-rev01-correction.py <main> 96f095a9… c3ecdd6b…` → `L1_68-rev01-correction.txt`
- `receipt_check.py <out>/RETURN.md <review worktree>` → exit 0; `evidence_gate.py <out>/RETURN.md --repo <review worktree> --candidate c3ecdd6b… --tool …/index_pins.py --tool …/receipt_fence_check.py --evidence-root <out> --require-cell P1 --require-cell T1 --require-cell M1 --require-cell L1 --require-cell F1` → `cells=8 defects=0`, exit 0
- `git show c3ecdd6b:<script> | sha256sum` for the four tool_digest scripts; the L1 and P1 raw blocks extracted and compared with `cmp`; `sha256sum L1.txt P1.txt`
- `gh run view 44367305470 --json …` and `--log` (0/0 checker lines)
- `ls` of the user temp directory, `.worktrees/68-archive-specs-scratch` and `.worktrees/68-archive-specs-out`; `cat C:/Temp/claude/jas-fullsuite.lock/owner.txt`
- `cm_68-rev01-correction.py <clone> <out>` → `CM_68-rev01-correction.txt`; CM7 gate run → `CM7_68-rev01-correction.txt`

### Raw-log note (correction)

`L1_68-rev01-correction.txt`, `CM_68-rev01-correction.txt` and `CM7_68-rev01-correction.txt` were unedited tool output. I read them in full before judging, and the results quoted above are taken from them. The coordinator's residue rule for this run required removing every file I created, so they were removed before return. CI was read with `gh run view` only. Nothing was pushed, and no run was triggered. No tracked file was modified anywhere. The clone was made with `--no-hardlinks` and removed afterwards. So were the helper scripts `l1_68-rev01-correction.py` and `cm_68-rev01-correction.py` and the receipt copy `RETURN_noL1_68-rev01-correction.md`. The host lock was not taken, because no full suite was run. I did not touch the seat's worktree, out directory or scratch directory, or any other seat's worktree.

### Not verified (correction)

- A reviewer full suite at `c3ecdd6b`. It was not run, by direction. The seat's locked F1 and both CI jobs cover it.
- The seat's rerun M1a–M1c at `c3ecdd6b`. My CM1, CM2 and CM5 reruns are independent of them.
- The per-link content behind the seat's `L1.txt`, because its script was removed. My own L1 gives the same totals.

```review-verdict
candidate: c3ecdd6b761d3ad994a828090ab856163ead9f14
verdict: APPROVED
reviewer: seat:ticket-review/68-rev01-correction
reviewed_at: 2026-11-19
```

```rework-record
candidate: c3ecdd6b761d3ad994a828090ab856163ead9f14
round: 2
kind: CORRECTION
verdict: APPROVED
causes:
```

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, against the expectation the owner confirmed on 2026-11-18 ("1A"); appended to the receipt as `USAGE` cells at integration.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/68-impl` | claude-sonnet-5-5 | 252 | 1313245 | 21814895 | 89071 | 23128392 | WITHIN |
| `seat:ticket-review/68-rev01` | claude-opus-5-5 | 156 | 438736 | 12192988 | 77680 | 12631880 | WITHIN |
