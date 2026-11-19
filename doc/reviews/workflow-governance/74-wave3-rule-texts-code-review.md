# Ticket 74: initial review of closure revision04

- Candidate: `4943d76c3413f8c4cfbad9c0f70eafc9bb7f8a6c` (branch `cp/wave3-74-rule-texts`). It is 4 commits on base `0a722c165b0db055d23e9a65d44e883d15a1e7c0`; the base is an ancestor of the candidate.
- Ticket: `modules/tickets/workflow-governance/74-wave3-rule-texts.md` revision04, read at the candidate.
- Dispatch: `doc/handoffs/2026/workflow-governance/dispatch/JAS-74-1.yaml` at `cp/wave3` `89457bf9`. Its sha256 is `1066881111e914a9af7b4d2da411fa75a66246099477f19ec3eb1898c7973bfb`, which matches the review request and the ticket state row at `89457bf9`. Apart from that state row, the ticket text at `89457bf9` is the same as at the candidate.
- Receipt: `.worktrees/74-rule-texts-out/RETURN.md`. It differs from `RETURN.as-returned.md` only by the appended `USAGE` cell.
- Label: initial review of closure revision04. The control plane set this label before dispatch.
- Seat and run: `ticket-review` seat, run id `R74-1`. I modified nothing in the candidate, branch or other worktrees.
- References applied: `CodeReview.md` §1 to §5, and `review-checks.md` (Required dimensions; Test truthfulness; Reviewer counter-mutation, points 1 to 5). XSS, security-boundary, profile and UI do not apply: the change is governance prose plus one stdlib test, with no browser, secret, provider or external effect.
- Environment: `C:/Temp/claude/jas-venv`, `PYTHONUTF8=1`. Output was unfiltered: pytest ran directly with `-q -rf`, and the full mutation output was read before judging.

## Findings

| id | §4 class | severity | location | finding | evidence |
| --- | --- | --- | --- | --- | --- |
| S74-01 | `OUT_OF_SCOPE_HARDENING` (does not block) | Medium | `skills/johnny-project-takeover/references/specification-ticketing.md` `#rule-process-tier`, strict list (`.agents/`, `ci/registered-failures.json`, `modules/spec/workflow-governance.md`, `modules/tickets/TEMPLATE.md`) | Rule 3 has a shipped skill reference name four of this repository's own development files. The payload policy forbids that (`test_no_skill_or_command_points_at_our_own_development_material`). The seat wrote the four names as plain text. The content is the ticket's, so no Closure item is violated. But the payload-closure guard can no longer see these four names. No test inside the boundary can settle this; the conflict is between rule 3's content and the payload policy. **Smallest fix:** the integration record accepts the plain-text form. The policy question goes to wave 4 with the template line: should the rule-bearing list stay in a shipped reference, or move to a governance file that is not shipped? No new mechanism. | In a clone, I restored the backticks on the seven tokens. `tests/test_plugin_payload_boundary.py` then fails 4 new tests. One message reads `PayloadClosureError: payload content references paths it does not carry: .agents/, ci/registered-failures.json, modules/spec/workflow-governance.md, modules/tickets/TEMPLATE.md`. With the candidate as committed, only the registered `CommittedPinTests::test_the_pinned_sha_exists` fails. A `DEVELOPMENT_ONLY` declaration would still fail the skills/commands test, so a declaration in that test cannot fix it. |
| S74-02 | none (observation, no defect) | Info | `router-control.md` `#rule-content-digest-only` bullet 1 (evidence_gate.py); `specification-ticketing.md` strict list (scripts/, scripts/README.md) | These three tokens name files in the shipped payload. The scan cannot resolve them from `references/`, so they are written without backticks. Meaning is unchanged, and the block carries the quoted sentence's content. Backticks are presentation, not content. The list's formatting is now mixed (for example "modules/tickets/TEMPLATE.md and `template/`"), which is cosmetic. No action. | Same clone run: `test_every_path_shaped_token_resolving_nowhere_is_declared` goes red with the backticks restored. |
| S74-03 | `EVIDENCE_DEFECT` (does not block) | Low | `RETURN.md` STATEMENT items 10, 11, 12, 14 | Four sentences of STATEMENT prose do not match the record. **Item 10** says "five additive commits" but lists four (`git rev-list --count` gives 4). **Item 14** gives failure counts 3, 3, 2, 5 and 3; the M1 capture and my rerun show 4, 4, 3, 6 and 4 (the CRLF case added in `4943d76c` is red in every mutation). **Item 12** calls run 44464843273 the first Windows run with the new test red, but run 44462560594 at `af8e0797` already shows `test_removed_anchor_is_red`, `test_anchor_moved_to_another_section_is_red` and `test_duplicated_anchor_is_red` as `UNREGISTERED_FAILURE`. **Item 11** says "every sentence is otherwise as the ticket gives it" but does not mention two small wording changes: "The process tier is decided" and "under `CodeReview.md` §5 rule B". Both keep the meaning; the second one is needed because `specification-ticketing.md` has no §5. The cells, captures, P9 and E1 are correct. **Smallest fix:** this record states the corrections; no receipt rebuild. | `M1.txt` lines 97, 198, 292, 431 and 524. `gh run view 44462560594 --log-failed`. `git rev-list --count 0a722c16..4943d76c` gives 4. |
| S74-04 | `TICKET_DEFECT` (evidence expectation only; does not block this candidate) | Low | ticket 完成定義 (the P1 command "exits 0") and TDD 4; dispatch cell P1 `assert` | No commit on this base can make the P1 command exit 0. Three `tests/test_plugin_publication.py` pin tests fail at base `0a722c16` with `PinnedCommitError`, and all three are registered for ticket 62. The dispatch's only named exception, `CommittedPinTests::test_the_pinned_sha_exists`, lives in `test_plugin_payload_boundary.py`, which is not in the P1 files. The candidate adds no red, and nothing inside the boundary could close this. I judge that the frozen behaviour is unaffected, so this needs no Closure rebuild. **Smallest fix:** in the dispatch file, P1 asserts name the registered base failures of the P1 files by test id. That is dispatch-authoring practice, not a new mechanism. | At base, `pytest tests/test_plugin_publication.py` gives `3 failed, 64 passed` with the same three ids. At the candidate, P1 gives `3 failed, 210 passed, 9 skipped`. All three are in `ci/registered-failures.json` and `C:/Temp/claude/jas48_F1_base.txt`. |
| S74-05 | `OUT_OF_SCOPE_HARDENING` (does not block) | Low | `tests/test_governance_rule_texts.py`, `ANCHOR_LINE` / `rule_defects` | Two of my counter-mutations turned no test red, so these two properties are not pinned. **CM-B:** an anchor wrapped in a code fence still counts, even though the heading scan does honour fences. **CM-H:** a second anchor written `<a id='…'>` with single quotes is not counted as a duplicate. The test also does not check that `## Receipt integrity` is the last section. None of these is in the TDD matrix. All four required red cases and categories 1, 2 and 6 are pinned. **Smallest fix:** next time this test is touched, skip anchor lines inside fences (reuse the fence tracking in `heading_lines`) and count both quote forms. | CM-B: `exit=0 16 passed`. CM-H: `exit=0 16 passed`. Both were restored with an empty porcelain. |

There are no blocking findings. The candidate gives the seven rules and the §3 sentence exactly as the ticket does, at the named places, and no other sentence changes.

## Per-check table

| # | check | result | evidence |
| --- | --- | --- | --- |
| 1 | Each rule at its named place, anchor on its own line, block = ticket content in the document's language | PASS | **Rule 1:** new last section `## Receipt integrity` at router-control.md:166, with the anchor below the heading. **Rule 2:** after the last paragraph of "Allocation and correction". **Rule 5:** after rule 2. **Rule 3:** after the last paragraph of `## Ticket`, before `## Frontend contract`. **Rule 7:** after the last paragraph of `## Dispatch normalization`; its scope sentence (R4-1, not the envelope) is the ticket's own item text. **Rule 4:** after the §4 classification list. **Rule 6:** after the last §5 bullet, at the end of the file, so it does not swallow the rule B bullets (S74R-19). Rules 4 and 6 are Chinese. I checked the translation sentence by sentence (最小修正, 去處, 不新增機制…除非…說明原因; initial／correction 標籤, 不得改標, 依回傳原樣記錄). The English rules match the quoted sentences, apart from the form deviations in S74-01 and S74-02 and the two wording changes noted in S74-03. |
| 2 | `Workflow.md` §3 sentence and link | PASS | It is one sentence, directly after the reference list of `## 3. Tickets`: 此規則之後開立的每張 ticket 都載明其流程層級, linked to `skills/johnny-project-takeover/references/specification-ticketing.md#rule-process-tier`. The anchor exists once in that file. The sentence keeps the S74R-24 wording. |
| 3 | No other sentence changed | PASS | `git diff --numstat 0a722c16 4943d76c` shows only additions (12/2/15/10/28/320, with 0 deletions). There are 0 removed lines. `git diff --check` is clean. All six paths are `modify` or `create` entries in the boundary block; no forbidden path is touched. |
| 4 | Backticks dropped: meaning and the "carries that sentence's content" rule | PASS for content; finding on policy | The meaning is unchanged, and the only quoted sentence affected (rule 1 bullet 1) still carries its content. Classification: S74-02 is form only, with no defect. S74-01 is an `OUT_OF_SCOPE_HARDENING` policy conflict that is carried, not blocking. I confirmed the seat's claim by restoring the backticks: 4 new red results in `test_plugin_payload_boundary.py`. |
| 5 | Test vs TDD design; M1 rerun; counter-mutations | PASS (with S74-05) | All seven anchors, files, sections and terms match TDD 1. The §3 link is checked. TDD 2 has all four red cases. TDD 3 covers both a missing file and a non-UTF-8 file. Categories 1, 2 and 6 are covered. The main test reads the real repository path, so it does not test a copy. `mypy --strict --python-version 3.11` reports `Success`. **M1 rerun** in clone `R74-1-clone`, with the whole file and no `-x`: M1-1 exit=1 (4 failed), M1-2 exit=1 (4), M1-3 exit=1 (3), M1-4 exit=1 (6), M1-5 exit=1 (4). Each failure set includes `test_every_rule_stands_at_its_place_with_its_terms`, and each mutation was restored with an empty porcelain. **Counter-mutations through other doors:** CM-A (a `###` subsection between the section heading and the anchor, nearest-heading door) exit=1, 3 failed. CM-C (a heading splits rule 1 so `--candidate` leaves the block, block-boundary door) exit=1, 3 failed. CM-D (anchor id in a different case, exact-id door) exit=1, 4 failed. CM-B and CM-H turned nothing red; see S74-05. |
| 6 | Receipt is true | PASS (with S74-03) | Every cell names `candidate: 4943d76c…`. The three `tool_digest` values equal the sha256 of the blobs at the candidate. **P1:** rerun matches (3 failed, 210 passed, 9 skipped, 383 subtests), and the three failures are base-red (S74-04). **T1:** rerun exits 0. **M1:** the capture matches my rerun. **C1:** `gh run view 44468047975` shows headSha `4943d76c`, conclusion success, and both `test (windows)` and `test (linux)` success. **F1:** the capture's 5 failures are all in the base list and registered. I did not rerun the full suite; CI green on both operating systems covers it. **P9:** `receipt_check.py` on `RETURN.as-returned.md` gives receipt defects 0. **E1:** `evidence_gate.py` on `RETURN.md` (with USAGE) gives `cells=7 defects=0`, exit 0. **Residue claims:** the seat worktree has no ignored or untracked files, `74-rule-texts-scratch` is empty, and no `r74a` lock exists. The STATEMENT prose inaccuracies are listed in S74-03. |
| 7 | Rule 3 records, rule 2 residue scope, rule 6 placement vs post-67 texts | PASS | **Rule 3 records:** each transition named has its source in the post-67 text. The dispatch digest in the state row: AGENTS.md "pending implementation dispatch 以票面狀態列（含派工檔 digest）". `REVIEW_APPROVED`: CodeReview §5 rule B, where the control plane sets 票面狀態. `BLOCKED` and `SUPERSEDED`: discovery-change.md:142-143. Integration by script: Workflow.md:82, which also requires the review candidate to equal the queue candidate, matching rule 1 bullet 2. **Rule 2:** ticket 67 (`867ddb53`, `0f621d9c`) did not touch "Allocation and correction". The kept sentence "Active owners may clear known reproducible residue in their own worktree; no other Agent may edit across worktrees" is consistent with rule 2's own-cache bullet and its "outside its allocated worktree" limit (S74R-25). **Rule 6:** §5 is the last section, and the block runs from the anchor to the end of the file. No sentence contradicts a rule, so I agree there is no `CHANGE_DETECTED`. |

## Commands run (in `R74-1-clone` unless noted)

- In the review worktree: the P1 command from the dispatch (`-q -rfEs -p no:cacheprovider`), exit 1, with the 3 registered pin failures.
- `pytest tests/test_plugin_publication.py` at base `0a722c16`, exit 1, with the same 3 failures.
- `pytest tests/test_plugin_payload_boundary.py`: exit 1 at the candidate (1 registered failure), and exit 1 with the backticks restored (5 failures, 4 of them new).
- `mypy --strict --python-version 3.11 tests/test_governance_rule_texts.py`, exit 0.
- `R74-1-mut.py`: the five M1 mutations plus CM-A, CM-B, CM-C, CM-D and CM-H, each restored with an empty porcelain.
- `evidence_gate.py RETURN.md … --require-cell P1 T1 M1 F1`, `cells=7 defects=0`, exit 0. `receipt_check.py RETURN.as-returned.md`, defects 0.
- `gh run view` for 44468047975 (green) and for the superseded runs 44462486410, 44462560594 and 44464843273.

## Residue (rule `rule-seat-residue`, run id R74-1)

Removed: the scratch directory `.worktrees/74-rule-texts-review-scratch`, which I created and tagged with `OWNER-R74-1.txt`. That covers the clone `R74-1-clone`, `R74-1-mut.py`, `R74-1-mut.log` and `R74-1-mypycache`. I took no host lock and did not run the full suite. No processes are left (PROCESSES_LEFT=0). Left and handed back: the review worktree, still detached at the candidate and clean, and this output directory.

```review-verdict
candidate: 4943d76c3413f8c4cfbad9c0f70eafc9bb7f8a6c
verdict: APPROVED
round: initial
closure_revision: revision04
reviewer: ticket-review seat (claude-opus-5-5), run R74-1
reviewed_at: 2026-11-19T06:25:52Z
blocking: none
```

```rework-record
candidate: 4943d76c3413f8c4cfbad9c0f70eafc9bb7f8a6c
round: 1
kind: INITIAL
verdict: APPROVED
causes:
```

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, against the expectation the owner confirmed on 2026-11-18 ("1A"); appended to the receipt as `USAGE` cells at integration.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/r74a` | claude-sonnet-5-5 | 222 | 225069 | 17465781 | 66007 | 17691072 | WITHIN |
| `seat:ticket-review/R74-1` | claude-opus-5-5 | 80 | 171303 | 4750158 | 40546 | 4921541 | WITHIN |

The implementation seat ran `claude-sonnet-5-5` at effort `high` on all 306 messages, as its dispatch named. It is the first wave-3 seat started with both set explicitly. The review seat ran `claude-opus-5-5` at `high`.

### Disposition of the non-blocking findings (control plane)

The initial review is `APPROVED`. Its non-blocking findings are recorded and carried:

| Item | Class | Disposition |
| --- | --- | --- |
| S74-01: rule 3 names four development paths in plain text so that the payload guard stays green | OUT_OF_SCOPE_HARDENING | Accepted in this form; whether the strict list belongs in a shipped reference goes to wave 4 |
| S74-02: three tokens without backticks | observation | No action |
| S74-03: four sentences of STATEMENT prose are wrong (items 10, 11, 12, 14); the cells, captures, P9 and E1 are correct | EVIDENCE_DEFECT, Low | Recorded here as the correction; the receipt stays as returned |
| S74-04: no commit on this base can make the P1 command exit 0, because the dispatch names only one of the registered base failures | TICKET_DEFECT, Low (dispatch) | From the next dispatch on, the control plane names each registered base failure by test id in the P1 assertion |
| S74-05: an anchor inside a code fence counts, and a single-quoted duplicate is not counted | OUT_OF_SCOPE_HARDENING | Wave 4 |
