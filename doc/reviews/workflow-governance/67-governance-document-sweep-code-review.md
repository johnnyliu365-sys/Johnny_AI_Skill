# Ticket 67 — initial review of closure revision04

- Candidate: `867ddb53021b79f97afc1ccce3b10d6c6db03555` (branch `cp/wave3-67-doc-sweep`, one commit on base `2753e60748acc495903c12ab39bb3435635536b5`)
- Ticket: `modules/tickets/workflow-governance/67-governance-document-sweep.md` revision04, read at the candidate
- Dispatch: `doc/handoffs/2026/workflow-governance/dispatch/JAS-67.yaml`, sha256 `89db4177c8495a709372b60fdc9cb820133acedd4d0085a961272963d624cc77` (recomputed, equal)
- Receipt: `.worktrees/67-doc-sweep-out/RETURN.md` (as returned: `RETURN.as-returned.md`; the only difference is the appended USAGE cell)
- Seat: independent `ticket-review`, run id `R67-1`, worktree `.worktrees/67-doc-sweep-review` detached at the candidate (porcelain empty before and after)
- References applied: `CodeReview.md` §1-§5, `review-checks.md` (Test truthfulness, Reviewer counter-mutation points 1-5), `module-catalog-routing.md` (card rows only)
- Round: initial

## Findings

| id | classification (§4) | severity | blocking | location | finding | evidence |
| --- | --- | --- | --- | --- | --- | --- |
| S67-01 | IMPLEMENTATION_DEFECT | Medium | yes | `Workflow.md:81`, last sentence of the first bullet of §0 | The sentence "跨生命週期的 receipt-bound bridge（`router-control.md`〈Dispatch admission〉）在第三波退場前仍可用，但不是預設路徑。" survives. It tells a waking agent that the retired cross-lifetime bridge is still usable and sends it to a router-control section that no longer describes it. Item 5 requires every sentence of `Workflow.md` that names a retired surface to be deleted; the problem statement names exactly this effect ("treats a retired path as an option"). Deleting the sentence leaves the rest of the bullet intact; no test pins it. | `grep` at the candidate; the sweep stays green because pattern d exempts "不是預設" and the closed list has no bridge term. The STATEMENT (item 2) does not list it. |
| S67-02 | IMPLEMENTATION_DEFECT | Low | yes | `Workflow.md:89` | The clause "其 graph 與 private router 不再是流程 authority，退場排在 Revision 04 第三波" names the retired graph and private router and says their retirement is still scheduled. Item 5 says to delete the clause and keep the still-valid rule: "`library/workflow_router/` 的 typed contracts 保留為受據欄位的型別定義". | Counter-mutation R4 (case-insensitive term match): the real-tree test reports exactly one hit, `Workflow.md:89 (RETIRED_SURFACE) 其 graph…第三波`. The case-sensitive `Private Router` term misses it. |
| S67-03 | IMPLEMENTATION_DEFECT (typed return) | Low | yes | `skills/johnny-project-takeover/references/router-control.md:116-119` | "Wake capability has exactly three finite dispositions … `AVAILABLE` when a cross-lifetime bridge is present and actual delivery is proved, and `UNAVAILABLE` when that bridge is absent" still names the retired bridge as a disposition that can be reached. Item 5 means its clause must go. The seat found that deleting it breaks "exactly three". The ticket covers that case: "a sentence whose meaning cannot survive the deletion is a `CHANGE_DETECTED` return naming its file and line". The seat instead returned `COMPLETED`, with "CHANGE_DETECTED items: none", and only suggested a follow-up. Correction: the return names `router-control.md:116-119`, and the assertion that pins the three names (`test_references_qualify_receipt_bridge_by_lifetime`), as a `CHANGE_DETECTED` item. The control plane then decides the sentence or records it as carried. The seat must not write new text. | STATEMENT items 2 ("Kept on purpose") and the header line; candidate text at lines 116-119 |
| S67-04 | EVIDENCE_DEFECT | Low | yes (initial round) | `tests/test_governance_consistency.py` (RETIRED_SURFACE and `SPEC_R41_FROZEN`) | Three properties of items 1 and 4 are not pinned; each of my counter-mutations turned nothing red. **R1:** removing one term (`pending descriptor`, the most frequent base hit) from `RETIRED_TERMS` leaves all tests green, so the closed list is not pinned term by term. **R2:** dropping `path == GOVERNANCE_SPEC` from the frozen check leaves all tests green. The AGENTS.md injection has no R4-1 heading or status note, so the path scope of item 4 ("only in `modules/spec/workflow-governance.md`") is never exercised. **R3:** stopping the scan of a unit after its first completed-retirement sentence (`continue` to `break`) leaves all tests green, so no test puts a live sentence after an exempt one in the same unit. Correction: one injection per `RETIRED_TERMS` entry, or an equality pin of the tuple to the ticket's list; one test that puts the status note under an `### R4-1` heading together with the R4-1 sentence in a file other than the SPEC and expects red; one unit made of a completed-retirement sentence followed by a live one. | `counter-mutations.txt` R1, R2 and R3: each `74 passed, 231 subtests passed`, exit 0, restored with porcelain empty |
| S67-05 | OUT_OF_SCOPE_HARDENING | Low | no | sweep design (ticket items 1 and 3) | Because the term list is closed and pattern d keeps its `R4-1` and "不是預設" exemptions, bridge-availability wording is not guarded. **R5:** putting back the `Workflow.md:22` clause that item 5 deletes ("；descriptor 僅限過渡 bridge（R4-1）") stays green. `Workflow.md:81` (S67-01) is green in the real tree. **R6:** deleting "No automatic effect may be stated." and the honest statement from the new SKILL.md readiness text turns no test red; only the four base pin failures show. This is the fail-closed rule the rule-only review raised as S67R-19 (High). The seat followed the ticket's closed list, so this is not a candidate defect. Under rule B these gaps would let a regression through, so they belong in the next change to this sweep. | `counter-mutations.txt` R5 (exit 0) and R6 (4 failed, all four base pin tests) |
| S67-06 | OUT_OF_SCOPE_HARDENING | Low | no | `SKILL.md:46`, `router-control.md:108`, `implementation-authority.md:22` and `:28` | Some antecedents dangle after the deletions. "The default is the ticket's state row…" lost its subject "cross-lifetime" in SKILL.md and router-control.md. In implementation-authority.md, "This gateway, its receipt…" now refers to a gateway whose definition was deleted, and ":28 … in either path" now describes only one path. The rules still read correctly, and item 5 forbids new text, so this goes to a later editorial pass. | Candidate text; STATEMENT item 2 |
| S67-07 | OUT_OF_SCOPE_HARDENING (carried) | Low | no | outside the boundary or frozen by the ticket | These are not defects of this ticket. (a) `modules/tickets/event-runner-binding/README.md:26` and `e10-handoff-driven-wake.md:13` still name the deleted `doc/runbooks/e7_owner_smoke.py`; they are ticket records, and the ticket set is in 禁止修改. (b) `doc/context/local-orchestration-installer/{main,msix}.md` and `doc/context/module-application-skill/main.md` name `workflow-router-poc` or the workflow-control partition; context records are outside the boundary. (c) `doc/runbooks/dispatch-model-profile.md:97` under 最小派工訊息 still calls `dispatch_ref`, registry commit, receipt and owner task "跨生命週期 receipt-bound 路徑的欄位", but item 5 freezes that section ("unchanged"). The control plane should carry all three. | `grep` at the candidate |

There are no findings on the boundary, the lock restore, the SKILL.md replacement text, the SPEC status note, the exemption removals, the receipt or CI.

## Per-check table

| check | result | evidence |
| --- | --- | --- |
| §1 admission: ticket, dispatch, receipt and candidate identity | PASS | Dispatch sha256 recomputed equal. HEAD is the candidate, and its parent is the base. The receipt names the candidate in every cell. |
| Boundary block: no file outside modify/create/delete; forbid untouched | PASS | `git diff --name-status 2753e607 867ddb53`: 29 paths. All are in `modify` (references/ as a prefix), `create` (3) or `delete` (2). Nothing under `library/local_orchestration/`, `scripts/`, `doc/archive/`, `doc/reviews/` or `ci/registered-failures.json`. |
| Item 1: closed term list, case-sensitive, completed-retirement exemption, `退場前`/`until`/`before` | PASS (the code matches the ticket); evidence gap in S67-04 | `RETIRED_TERMS` compared to the ticket's list one term at a time: equal. The exemption forms and the pending words are equal. It is a separate check that does not read history, and `EXPECTED_TOLERATED` is unchanged. |
| Item 2: swept set | PASS | `RETIRED_SURFACE_ROOTS` is `ROUTED_ROOTS` minus the SPEC, plus README.md, commands, .agents, library/catalog and MODULE_CATALOG.md, plus the two globs. The PATTERNS roots are unchanged. `library/local_orchestration/README.md` is in the set and clean. |
| Item 3: exemption removals | PASS | `BRIDGE_EXEMPT` lost exactly the four entries; d lost `過渡`, `退場` and `僅限過渡`; e lost `live descriptor 是` and `僅限`. Nothing outside the boundary turned red, so no fallback entry was kept. |
| Item 4: SPEC status note and `SPEC_R41_FROZEN` | PASS; path-scope pin missing (S67-04 R2) | The note text equals the ticket's and sits directly under `### R4-1`. The R4-1 sentence is unchanged. The frozen check runs only when `path == GOVERNANCE_SPEC` and the note is present. |
| Item 5: specific edits (AGENTS, SKILL readiness, Workflow:22, runbook, .agents rule, e7, ADR, workflow-router-poc, path-containment, test pins) | PASS | Diff read item by item. The AGENTS.md deletion is exact. `Workflow.md:22` is exact. The runbook bullet reduced to the clause, and "Receipt" is capitalised. The ADR target `doc/archive/specs/2026/context-load-telemetry.md` exists. The catalog page and its row are deleted. The path-containment rows name the short-names suite. |
| Item 5: SKILL.md replacement is exactly the ticket's | PASS | A script extracted the quoted text from the ticket. It appears verbatim in SKILL.md, preceded by "…is a **protocol**.\n" and followed by " Never report a wake you did". |
| Item 5: general deletion in Workflow.md and the references | FAIL | S67-01 (`Workflow.md:81`), S67-02 (`Workflow.md:89`), S67-03 (`router-control.md:116-119`, wrong typed return) |
| Item 5: changed or removed assertions | PASS | tara2 lost `runner` and `live descriptor`. tara6 lost `live descriptor` and `cross-lifetime`; its text was in deleted sentences, and the STATEMENT names it. The publication pins listed in the ticket were removed. The payload set lost `runner-subscriptions.json`. Antigravity is unchanged. |
| Item 6: lock module vs `c9af7725^` | PASS | My own `git diff --no-index`: only the docstring (references to deleted modules and the alias rationale) and the alias comment, which reads "Kept for callers of the earlier name". No code changed. The +/- lines equal the seat's L1. |
| Item 6: lock test vs `c9af7725^` | PASS | Only the allowed changes: docstring, consumer import block, new import path in the module, the three child scripts and both `patch` targets, the consumer test removed, the element README and the `TelemetryStorageLockPort` assertion removed. The +/- lines equal the seat's L2. |
| Item 6: `__init__` exports, card, 32/11, old path absent | PASS | `__init__.py` exports the three names. The card rows are refreshed, and its one sentence replaces the telemetry bullet. My run: `32 passed, 11 subtests passed`. `find_spec('library.local_orchestration.file_lock')` is `None`. |
| TDD 2/3 injections (seat's tests) | PASS | Every injection the ticket lists is present in `RetiredSurfaceTests`, together with the b2 case, the SPEC cases, the green cases and the missing, undecodable and empty cases. |
| P1 (ticket 完成定義) | 4 failed, 317 passed; all four are base failures | Reviewer rerun (`P1-reviewer.txt`): the same four fail with `PinnedCommitError` or the pinned sha absent. All four are in `C:/Temp/claude/jas48_F1_base.txt` and registered in `ci/registered-failures.json`. The dispatch named only one of them; the other three have the same cause and are not caused by this candidate. Not a finding. |
| T1 mypy --strict | PASS | Reviewer rerun: `Success: no issues found in 4 source files` |
| M1, the seat's six mutations | PASS | Each is red for the intended reason: MA 19, MB 5 (b2 case and SPEC cases), MC 3 (commands injection and set), MD 14 (SPEC sentence live), ME 3 (`退場前` cases), MF 6 (completed-retirement greens). Each was restored with porcelain empty, and the control run passed 74. |
| Reviewer counter-mutation (review-checks: own doors, unfiltered output) | 4 zero-red doors (S67-04, S67-05) | Disposable clone. pytest ran directly with `-q -rfE` and no output reducer, and I read the full output. R1 (overlap), R2 (path scope), R3 (first match) and R5 (real-tree restore) were green. R6 (removing the readiness copy) showed only base failures. R4 (case-insensitive, the control) was red with 24 failures, including `test_matching_is_case_sensitive`, and also exposed `Workflow.md:89`. |
| Receipt truth | PASS | Every raw block of RETURN.md and RETURN.as-returned.md is byte-equal to its capture file (LF). Each cell's `exit` equals its capture's `exit=` lines. The tool digests equal sha256 of the four scripts at the candidate. My E1 rerun gives `cells=8 defects=0`, exit 0. |
| CI | PASS | `gh run view 44442001687`: headSha `867ddb53…`, both jobs `success`. No `UNREGISTERED_FAILURE` or `REGISTERED_NOT_FAILING` line in either job log. |
| F1 (seat) | PASS | 5 failed, all in the base list, so no new red. I did not rerun the full suite, since CI is green on both jobs and F1 is a subset of the base list; I took no host lock. |
| Kept router-control sentences and e7 references | router-control: S67-03 (wrong typed return, not wrong text); e7: carried (S67-07) | See findings |

## Correction requested (same ticket, same branch, additive commit)

1. Delete the last sentence of the first §0 bullet at `Workflow.md:81` (S67-01).
2. Delete the clause "其 graph 與 private router 不再是流程 authority，退場排在 Revision 04 第三波" at `Workflow.md:89`, and keep the typed-contracts clause (S67-02).
3. In the correction return, name `router-control.md:116-119` and its pin as a `CHANGE_DETECTED` item, without new text (S67-03).
4. Add the three pins of S67-04.
5. Rerun P1, T1, the M1 mutations affected by the new tests, and E1.

S67-05 to S67-07 go to the control plane as carried items and do not block.

```review-verdict
candidate: 867ddb53021b79f97afc1ccce3b10d6c6db03555
verdict: CHANGES_REQUESTED
round: initial
reviewer: ticket-review seat (claude-opus-5-5), run R67-1
reviewed_at: 2026-11-19T02:45:36Z
blocking: S67-01, S67-02, S67-03, S67-04
```

---

## Correction review (round: correction)

- Candidate: `0f621d9cfee48bd4e1b0277ace5a19633da55613`. It is three commits on base `2753e607`: `867ddb53` (reviewed above), then `6fac3de8` (correction 1: `Workflow.md` and `tests/test_governance_consistency.py` only), then `0f621d9c` (correction 2: `router-control.md` only). All three are in the boundary's `modify` list.
- Receipt: `.worktrees/67-doc-sweep-out-c1/RETURN.md`. The as-returned copy differs only by the USAGE cell the control plane appended.
- Authority: the initial findings table above, plus the owner decision of 2026-11-19 on S67-03 (exact replacement text). S67-05 to S67-07 are carried by the control plane and are not re-raised here.
- Seat: the same `ticket-review` seat, run id `R67-2`. The worktree is detached at the candidate, with porcelain empty before and after. I did not re-review unchanged parts.

### Findings, initial round

| id | status | evidence |
| --- | --- | --- |
| S67-01 | CLOSED | `git diff 867ddb53 0f621d9c -- Workflow.md`: the last sentence of the first §0 bullet is deleted, and the rest of the bullet is byte-identical. |
| S67-02 | CLOSED | `Workflow.md:89` now ends "…保留為受據欄位的型別定義。". Nothing else on the line changed. |
| S67-03 | CLOSED (by owner decision) | A script compared the `router-control.md` paragraph that begins "Wake capability" with the owner's text: exactly one such paragraph, and it is equal. The diff of that file across the two corrections is one paragraph: 1 line added, 4 removed. Nothing else in the file changed. The new last sentence is a completed retirement, and the real tree stays green. `BridgeCapability.AVAILABLE` in `library/` is carried to wave 4, as the receipt's item 11 records. |
| S67-04 | CLOSED | I reran the counter-mutations myself in a fresh disposable clone, on the full `tests/test_governance_consistency.py`, with unfiltered output (`counter-mutations-c1.txt`). Each is red for the intended reason and was restored with porcelain empty. **R1** (`pending descriptor` dropped from `RETIRED_TERMS`): 2 failed, the closed-list pin and the pending-descriptor injection. **R1b** (`wake-inbox` dropped, a term with no other injection): 1 failed, the closed-list pin. **R2** (`path == GOVERNANCE_SPEC` dropped): 5 failed, the four subtests for files other than the SPEC plus the copy injection. **R3** (`continue` to `break`): 3 failed, the three units of the R3 test. |

### Did the corrections introduce a defect

None found.
- `git diff 867ddb53 0f621d9c` touches only the three files named above.
- The 53 lines added to the test file are additive. No existing assertion changed, and `EXPECTED_TOLERATED` is unchanged.
- No other governance document claims three dispositions.
- `mypy --strict` passes on the four files.
- P1 at the candidate, rerun by me (`P1-reviewer-c1.txt`): 4 failed, 321 passed. The four failures are the same base pin failures as before, registered and in `jas48_F1_base.txt`. The four new tests pass.

Two observations, neither a finding:
- (a) The closed-list pin compares `RETIRED_TERMS` with a sample dictionary in the same file. Removing a term from both at once would stay green. The ticket's list lives only in prose, so this is as far as an in-repository pin can reach.
- (b) The kept pin `"AVAILABLE" in router` in `test_references_qualify_receipt_bridge_by_lifetime` is also satisfied by the substring `UNAVAILABLE`. It predates this ticket and belongs with the carried `BridgeCapability.AVAILABLE` item for wave 4.

### Receipt truth

| check | result |
| --- | --- |
| Raw blocks equal capture files (RETURN.md and RETURN.as-returned.md) | PASS: all 8 cells byte-equal, LF. Each cell's `exit` equals the `exit=` lines of its capture, M1 included (`0,1,1,1,1,1,1,1,1,1,0`). |
| Every cell at the candidate | PASS: `candidate: 0f621d9c…` in every cell |
| Tool digests | PASS: equal to sha256 of the four scripts at the candidate |
| E1 rerun by the reviewer | PASS: `cells=8 defects=0`, exit 0 |
| C1 / CI run 44450313109 | PASS: headSha `0f621d9c…`, both jobs `success`, zero `UNREGISTERED_FAILURE` or `REGISTERED_NOT_FAILING` lines in either log |
| F1 | PASS: 5 failed, all in the base list, so no new red. I did not rerun it and took no host lock. |
| STATEMENT | Matches the diff. Items 2, 3, 9, 11 and 12 describe exactly the corrections I observed, and M1 includes my R1, R2 and R3 as red. |

### Conclusion

All blocking findings of the initial round are closed, the corrections introduce no defect, and the receipt is true. No finding of this ticket remains open, so `CONVERGENCE_REVIEW_REQUIRED` is not attached and §5 rule B does not apply. S67-05, S67-06 and S67-07, and the `BridgeCapability.AVAILABLE` item, stay with the control plane as carried items.

```review-verdict
candidate: 0f621d9cfee48bd4e1b0277ace5a19633da55613
verdict: APPROVED
round: correction
reviewer: ticket-review seat (claude-opus-5-5), run R67-2
reviewed_at: 2026-11-19T03:45:52Z
open_findings: none
carried_by_control_plane: S67-05, S67-06, S67-07, BridgeCapability.AVAILABLE (wave 4)
```

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, against the expectation the owner confirmed on 2026-11-18 ("1A"); appended to the receipt as `USAGE` cells at integration.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/JAS67C1-024737` | claude-opus-5-5 | 376 | 740500 | 54327294 | 146829 | 55068170 | OVER_OUTPUT,OVER_PROCESSED |
| `seat:ticket-review/R67-2` | claude-opus-5-5 | 130 | 404958 | 10969708 | 56152 | 11374796 | WITHIN |

### Over-expectation explanation (control plane)

The implementation seat is over both expectations: 146829 output against 130000, and 55068170 processed against 24000000. The over-expectation is recorded here and does not block, as the owner decided. Two control-plane causes account for it:

1. **The seat ran on the wrong model.** The dispatch named the profile `implementation-standard`, but the control plane started the seat without naming a model. It therefore ran on `claude-opus-5-5`, while every earlier wave-3 implementation seat ran on `claude-sonnet-5-5`. The profile does not hold the review back: the reviewer ran on `claude-opus-5-5`, which ranks at least as high. From now on the control plane names the model explicitly when it starts a seat.
2. **The seat ran three rounds in one context.** The first pass, correction 1 and correction 2 all ran in the same seat, so each round re-read the context the earlier rounds had built up. The figures above are the sum over all three rounds.

The review seat is within both expectations: 56152 output and 11374796 processed, over the initial and the correction round.

### Carried items

| Item | Source | Destination |
| --- | --- | --- |
| S67-05: the closed term list does not guard wording about the bridge being available | correction review | wave 4 |
| S67-06: some antecedents dangle after the deletions | correction review | wave 4 |
| S67-07: tickets of `event-runner-binding` name the deleted `e7_owner_smoke.py`; `doc/context` records name `workflow-router-poc`; `dispatch-model-profile.md:97` | correction review | wave 4 |
| `BridgeCapability.AVAILABLE` in `library/local_orchestration/project_authority/contracts.py`, and a publication-test pin on "AVAILABLE" that also matches "UNAVAILABLE" | owner decision 2026-11-19, correction review | wave 4 |
| The term-list test compares the list with a sample in the same file | correction review observation | wave 4 |
