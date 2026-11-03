# REVIEW — ticket 49 Vendor and model names out of governance documents

> Commit identifiers in this record that predate 2026-11-03's identity rewrite are the pre-rewrite identifiers; read them through `doc/reviews/workflow-governance/evidence/commit-identity-rewrite-2026-11-03.txt` (old commit, new commit, identical tree).

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `924f5bb6003232838327cdbd968140929766ff63` on `cp/wave1-gates-first` (parents 4e7770f → 7335e78) |
| Baseline | `7335e78f` (ticket 47 closure revision02 plus scrub commits) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; read-only, no pytest by instruction |
| Reviewed at | 2026-11-03 (Asia/Taipei) |
| Closure | 49-W1–W2 revision01, "One observable behavior", johnny-boundary block, the control plane's "Ticket correction" table |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| W1 | PASS as written | The scoped command at `924f5bb` returns exactly 1 hit, the W1 row itself, matching Expected. The original unscoped form returns 49 hits: 48 in tickets 04–23 ("Opus 5" / "Sonnet 5" as implementer and reviewer) plus the W1 row. At baseline `7335e78` the unscoped form also hit REQ:7, 47 Grant, 48 Grant and 49:30, so the diff removed the three in-boundary literals. |
| W2 | FAIL against the frozen Expected | 48:49 P4 reads `<source-project names from the dispatch, not written in this ticket>`. W2 Expected says the denylist comes from "a parameter file named in the ticket"; ticket 48 names no parameter file. The P4 change landed in `a557a25`, before this baseline, and this diff does not touch it. Ticket 49 State row still claims "W2 … done". |
| Observable behavior | PARTIAL | Source-project names: 0 hits in `git diff --name-only a1cb6c1..924f5bb` for the one target-project name known to this seat from its host environment; the dispatch denylist was not available. Profile names `decision-support`, `ticket-review`, `implementation-standard` exist at `doc/runbooks/dispatch-model-profile.md:21-23`. Tickets 47 and 48 Grant rows use them; REQ:7 says "the control plane". Vendor literals still in boundary files, invisible to the W1 pattern: `modules/spec/workflow-governance.md:7` and `:148` read "Codex control plane"; tickets README:31 reads "Codex/current worktree is the control-plane owner and reviewer". Outside the boundary but on this line: the ticket 47 review record line 9 reads "independent seat (Opus)". |
| Boundary | FAIL (subset) | Changed files: REQ-20261103-043, 47, 48, 49, the tickets README. The ticket 49 leaf is not in its own modify/create set (ticket 47, by contrast, lists itself). The README was changed in `4e7770f`, before `924f5bb` added it to the boundary. No forbid path (`library/`, `skills/`, `tests/`) is touched. |
| Correction legitimacy | Legitimate in kind, defective in execution | A real TICKET_DEFECT: the W1 row contains its own pattern, and editing tickets outside the boundary would breach the boundary, so "zero hits" was unreachable; narrowing the scope is not in itself a weakening. Defects: (a) the stated reason "closed tickets 01–23" is false, because 06, 07, 08, 09, 22 and 23 are `IN_PROGRESS`; (b) "scoped to the boundary files" is false, because the W1 command scans 49 (not in the boundary) and skips the tickets README (in the boundary); (c) the closure stays "revision01" after an Expected change, although CodeReview §4.3 requires a rebuilt Closure revision before implementing; (d) the W1 correction landed in the same commit as the implementation (`4e7770f`), and the boundary correction came after the README edit. |

### Findings

| ID | Class (CodeReview §4) | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| R49-01 | `IMPLEMENTATION_DEFECT` | Medium | modules/tickets/workflow-governance/48-port-gate-scripts.md:49 | P4 takes its denylist "from the dispatch". W2 requires a parameter file named in the ticket, and none is named. 49:5 still says W2 is done. If "dispatch" is what the control plane intends, W2 has to be re-cut as a TICKET_DEFECT under a new closure revision. | `git show 924f5bb:…/48-…md`, W2 row at 49:31 |
| R49-02 | `TICKET_DEFECT` | Medium | 49-wording-drift-and-vendor-names.md:5,30,37 | W1 Expected changed but the closure is still `49-W1–W2 revision01`, against CodeReview §4.3. The correction was made in the implementation commit, not before it. | `git show 4e7770f` |
| R49-03 | `TICKET_DEFECT` | Medium | 49-…md:37; tickets README:31 | The correction says W1 is "scoped to the boundary files", but the command adds 49 and leaves out the tickets README. The README carries a vendor literal in a role statement. It also calls tickets 01–23 "closed" while 06–09, 22 and 23 are `IN_PROGRESS` and still name "Opus 5"/"Sonnet 5" as role holders. The exemption needs an accurate reason or a follow-up ticket. | `git grep` state rows 05–23; W1 command text |
| R49-04 | `TICKET_DEFECT` | Medium | 49-…md:30; modules/spec/workflow-governance.md:7,148; tickets README:31 | The W1 pattern covers only the Opus/Sonnet/Haiku family plus "Claude control plane". It cannot see "Codex control plane", the exact counterpart of the literal removed from REQ:7, so the observable behavior ("never a vendor or model literal") is not encoded in any cell. The ticket must decide whether historical signature and authority rows are exempt. Host identifiers such as `.claude-plugin/`, `.codex-plugin/` and "Codex/Claude host approval" (spec:31) are functional host names and not counted. | `git grep -niE` over the line's files at 924f5bb |
| R49-05 | `TICKET_DEFECT` | Low | 49-…md:11-19 | The ticket's own leaf is missing from its boundary, but this diff changes its State row and adds the correction table. By the reasoning the correction used to add the README, the leaf belongs in the boundary. | `git diff --name-only 7335e78..924f5bb` vs the johnny-boundary block |
| R49-06 | `OUT_OF_SCOPE_HARDENING` | Low | 47-…md:9; 48-…md:10; tickets README:31; ticket 47 review record lines 9, 53, 66 | Not added lines. Host absolute paths (two temp-clone paths and one user-profile path) and "(Opus)" remain in persisted documents, against Workflow §0 "不含主機絕對路徑". | `git grep` at 924f5bb |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | `wc -l CodeReview.md AGENTS.md Workflow.md; git log --oneline -4 924f5bb; git diff --stat 7335e78..924f5bb` | 0 |
| 2 | `cat CodeReview.md; sed -n 1,119p AGENTS.md; sed -n 75,155p Workflow.md` | 0 |
| 3 | `git show 924f5bb:…/49-…md; git diff 7335e78..924f5bb` | 0 |
| 4 | W1 scoped, at the commit and in the worktree (HEAD = 924f5bb) | 0 (1 hit) |
| 5 | W1 unscoped at 924f5bb and `-c` at 7335e78 | 0 (49 hits / baseline 52) |
| 6 | `git log a1cb6c1..924f5bb; git diff --name-only a1cb6c1..924f5bb; git show --stat 4e7770f 924f5bb` | 0 |
| 7 | `git show 4e7770f -- …/49-…md`; vendor/model/target grep over the line's files at 924f5bb | 0 |
| 8 | `git show 924f5bb:…/48-…md`, `…/README.md`, `…/47-…md`; state rows of tickets 05–23 | 0 |
| 9 | profile-name grep over `doc/runbooks/dispatch-model-profile.md`, spec, Workflow.md, CodeReview.md | 0 |
| 10 | spec Revision 04 and signature rows; ticket 47 review record F-12 | 0 |
| 11 | `git diff -U0 7335e78..924f5bb \| grep '^+' \| grep -iE "<drive-letter path>\|token\|secret\|password\|key="` | 1 (no hits) |

Not verified: the dispatch's source-project denylist (not provided; only the one name known to this seat was checked). No pytest was run, by instruction. Nothing was found contradicting Workflow §0 or spec Revision 04; the only governance conflict is R49-02 against CodeReview §4.3. Added lines show no chat tone, host absolute paths or secrets.

## ImplementationReturn (control plane, closure revision02)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Candidate | `fb55623f747039d24555fab0e5017831da9926ac` (content); the commit that carries this section adds only evidence files and this record |
| Re-plan commit | `3ffe1b12` (closure rebuilt before the fix) |
| W1 | PASS — 3 hits: the W1 row, the spec "Authoring AI / baseline" row, the spec Revision Signatures row dated 2026-08-05; raw `evidence/49/rev02-W1.txt` |
| W2 | PASS — ticket 48 P4 names the dispatch file as the carrier of its denylist and spells no name; raw `evidence/49/rev02-W2.txt` |
| W3 | PASS — zero hits (`git grep` exit 1); raw `evidence/49/rev02-W3.txt` |
| Observable behavior | no source-project name on this line (checked by the ticket 48 reviewer's P4 denylist, outside this record); tickets 47 and 48 Grant rows, REQ Authority row and the README authority paragraph name roles and profiles; dated spec rows exempt as stated in the ticket |

## Revision02 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `34997e8f` (evidence commit); content commit `fb55623f`; re-plan commit `3ffe1b12` |
| Baseline | `7335e78f` |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; read-only, no pytest by instruction |
| Closure | 49-W1–W3 revision02, "One observable behavior", johnny-boundary block, "Ticket corrections" table |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| W1 | PASS at the candidate | At `34997e8f` exactly 3 hits, exit 0: spec:7 (the "Authoring AI / baseline" row), spec:148 (the Revision Signatures row dated 2026-08-05) and the W1 row. Nothing else matches. The same command at re-plan commit `3ffe1b12` gives 5 hits; the extra two are the R49-04 corrections row (which spelled the new literals) and README:31. The corrections-row hit could only go away by editing the frozen closure text, and that edit was made in implementation commit `fb55623f` (N49-01). |
| W2 | PASS | the P4 cell names the dispatch file as the carrier and spells no name |
| W3 | PASS | 0 hits over the W1 file list; also 0 over both review records and `evidence/49/`; user-profile, temp and home path greps 0 |
| Observable behavior | PASS with one Low residual | 47:8 and 48:8 use `ticket-review` and `implementation-standard`; 49:8 and REQ-043:7 say "control plane"; README:31 is in Revision 04 terms. Profile names exist at `doc/runbooks/dispatch-model-profile.md:21-23`. Remaining vendor tokens are functional host or file names, or dated records. One live statement remains: 47:49 "stays on the Codex branch" (N49-03). |
| Boundary | PASS (subset) | `git diff --name-only 7335e78..34997e8f` lists 27 paths: ticket 49 only (its review record, `evidence/49/*`); both boundaries (spec, REQ-043, tickets 47/48/49, README); ticket 47 only (AGENTS.md, its review record, `evidence/47/*`, profile.py, router-control.md, two test files). In neither: none. Ticket 49's forbid paths appear in the shared commit only as ticket 47 boundary paths. |
| Receipt | PARTIAL | W1–W3 have results and headed captures (candidate = the content commit; results identical at both commits). The Observable-behavior row has no capture; Boundary has no row; "closure rebuilt before the fix" is not accurate (N49-01, N49-02). |

### Prior findings

| ID | Status | Evidence |
| --- | --- | --- |
| R49-01 | CLOSED | W2 re-cut in `3ffe1b12`; 48:49 rewritten in `fb55623f`; order correct |
| R49-02 | PARTIAL | the closure was rebuilt in `3ffe1b12` before `fb55623f`, but `fb55623f` then rewrote the corrections row at 49:45 (N49-01) |
| R49-03 | CLOSED | exemption accurate; W1 list explicit and includes the README; residual N49-04 |
| R49-04 | PARTIAL | pattern covers the spec header rows and the README paragraph; the extended pattern matched its own disposition row, rewritten in the implementation commit (N49-01) |
| R49-05 | CLOSED | boundary lists the leaf, the review record and `evidence/49/` at `3ffe1b12` |
| R49-06 | CLOSED (ticket 49 scope) | W3 added; Workspace rows and README path-free; ticket 47 review record scrubbed; residual N49-05 outside this boundary |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| N49-01 | `TICKET_DEFECT` | Medium | 49-…md:45 | As frozen in `3ffe1b12`, W1 Expected ("exactly three hits") could not be met: the R49-04 corrections row spelled the new literals. `fb55623f` rewrote that row of the frozen corrections table to pass W1: the same order defect as R49-02, against CodeReview §4 item 3; the table does not record it and the receipt says "closure rebuilt before the fix". Freeze the current text as a new closure revision, or define the corrections-table hits in Expected, then rerun W1–W3. | W1 at `3ffe1b12` gives 5 hits; `git show fb55623f -- …/49-…md` is a one-line change at the R49-04 row |
| N49-02 | `EVIDENCE_DEFECT` | Low | 49 review record, ImplementationReturn rows "Re-plan commit", "Observable behavior" | Observable behavior has no capture and relies on another review's denylist; Boundary has no row; "closure rebuilt before the fix" contradicts the 49:45 change. | `git ls-tree 34997e8f evidence/49/` holds only W1–W3 |
| N49-03 | `OUT_OF_SCOPE_HARDENING` | Low | 47-…md:49 | "stays on the Codex branch where it was written": a live location statement using a vendor name instead of the ref name; present at baseline; invisible to the W1 pattern. | grep at `7335e78` and `34997e8f` |
| N49-04 | `TICKET_DEFECT` | Low | 49-…md:33-35 | The W1/W3 file list is not exactly the boundary set: wider for the REQ entry (the directory, 14 files, instead of `REQ-20261103-043.md`), narrower on the two `create` entries. Results unaffected. | `git ls-tree` of the REQ directory; W3 extended to the review records and `evidence/49/` gives exit 1 |
| N49-05 | `OUT_OF_SCOPE_HARDENING` (route to ticket 47) | Low | `evidence/47/*.txt` raw pytest captures | The raw captures carry host absolute paths (checkout and interpreter). Conflicts with ticket 47's R49-06 disposition and the intent of Workflow §0. Outside ticket 49's boundary. | `git grep -l` drive-letter pattern over `evidence/` at `34997e8f` |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1–3 | reads of the ticket, CodeReview.md, AGENTS.md, Workflow.md section 0, the 49 review record and the `evidence/49/` captures at `34997e8f` | 0 |
| 4 | fresh `--no-hardlinks` clone of the branch, `git checkout 34997e8f` | 0 |
| 5 | W1 (worktree form and `git grep -c … 34997e8f`) | 0 (3 hits) |
| 6 | W2 | 0 (1 hit) |
| 7 | W3 over the W1 file list | 1 (0 hits) |
| 8 | broad vendor/model grep over the boundary files | 0 |
| 9–12 | `sed` of spec, README, ticket 47; `git show --stat` of `3ffe1b12`, `fb55623f`, `34997e8f`; `git show fb55623f --` and `3ffe1b12 --` 49, README, 48, spec, REQ; W1 at `3ffe1b12` | 0 (5 hits at `3ffe1b12`) |
| 13–15 | W3 pattern over `doc/reviews/workflow-governance/4*.md` and `evidence/49/`; user/temp/home path grep; vendor grep over both review records | 1 / 1 / 0 |
| 16 | `git log --oneline 7335e78..34997e8f; git diff --name-only 7335e78..34997e8f` | 0 (27 paths) |
| 17 | profile-name grep in `doc/runbooks/dispatch-model-profile.md`; role/grant/workspace grep over 47, 48, 49, REQ-043 | 0 |
| 18–19 | `git diff -U0 7335e78..34997e8f` added lines grepped for drive-letter paths, token, secret, password, key, email; chat-tone grep | hits only in `evidence/47` raw logs and the record's own command text; no chat tone |
| 20–21 | grep for the one external project name known to this seat over added lines and boundary files; line-number greps | 1 (0 hits) / 0 |

Not verified: the dispatch's source-project denylist (only the one external name known to this seat was checked); no pytest run, by instruction; ticket 47's own revision03 cells (only file attribution and the path observation in N49-05); R4-7's five-field receipt-cell schema was not applied because R4-7 binds the wave-2 implementation tickets and this is a documents ticket. Nothing was written inside the control plane's checkout; the reviewer's scratch clone remains on its host.

## ImplementationReturn (control plane, closure revision04)

Superseded by the revision05 return below: W4 and W5 were red in this run (`evidence/49/rev04-W4.txt`, `rev04-W5.txt`), W4 because the Expected named only ticket 47 as the other ticket on the line, W5 because the classifier did not recognise the short file reference "the codex-native reference".

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Candidate | `b927e48de565613307b1cba3da059f43050917b8` (the ticket text of revision04 and the one content change, ticket 47 line "stays on branch `codex/skill-improvement-checklist`", are both at this candidate; the commit that carries this section adds only the captures and this record) |
| Order | re-plan `bf6a4632` (revision03) → content `40ab88eb` → re-plan `b927e48d` (revision04: places (e) added, found while running W1, before any evidence) → this evidence |
| W1 | PASS — every hit classified into places (a)–(e); live role holder or location: 0; counts {'(a) the W1/W5 check row': 1, '(b) dated spec record': 2, '(c) Ticket corrections row': 1, '(d) review record line': 7, '(e) capture of a W1/W5 run': 4}; raw `evidence/49/rev04-W1.txt` |
| W2 | PASS — ticket 48 P4 names the dispatch file as the carrier and spells no name; raw `evidence/49/rev04-W2.txt` |
| W3 | PASS — zero hits (`git grep` exit 1); raw `evidence/49/rev04-W3.txt` |
| W4 | FAIL — every path in `7335e78..HEAD` tagged 47, 49 or both; paths in neither boundary: 1; raw `evidence/49/rev04-W4.txt` |
| W5 | FAIL — every hit classified; live role holder or location: 1; counts {'(a) the W1/W5 check row': 2, '(b) dated spec record': 2, '(c) Ticket corrections row': 1, '(d) review record line': 7, '(e) capture of a W1/W5 run': 4, 'LIVE ROLE HOLDER OR LOCATION': 1, 'functional host, file or ref name': 10}; raw `evidence/49/rev04-W5.txt` |
| Deviations | none |

## ImplementationReturn (control plane, closure revision05)

| Field | Value |
| --- | --- |
| Return | `COMPLETED` |
| Candidate | `0aae3bf8ffa389dbabd2b6b2a87dd6df76887b73` (the ticket text of revision05 and the one content change, ticket 47 line "stays on branch `codex/skill-improvement-checklist`", are both at this candidate; the commit that carries this section adds only the captures and this record) |
| Order | re-plan `bf6a4632` (revision03) → content `40ab88eb` → re-plan `b927e48d` (revision04) → evidence `746a1737` (W4, W5 red as recorded) → re-plan `0aae3bf8` (revision05, W4 wording) → this evidence |
| W1 | PASS — every hit classified into places (a)–(e); live role holder or location: 0; counts {'(a) the W1/W5 check row': 1, '(b) dated spec record': 2, '(c) Ticket corrections row': 1, '(d) review record line': 7, '(e) capture of a W1/W5 run': 19}; raw `evidence/49/rev05-W1.txt` |
| W2 | PASS — ticket 48 P4 names the dispatch file as the carrier and spells no name; raw `evidence/49/rev05-W2.txt` |
| W3 | PASS — zero hits (`git grep` exit 1); raw `evidence/49/rev05-W3.txt` |
| W4 | PASS — every path in `7335e78..HEAD` tagged with the tickets whose boundary covers it (47, 48, 49 or a combination); paths in neither boundary: 0; raw `evidence/49/rev05-W4.txt` |
| W5 | PASS — every hit classified; live role holder or location: 0; counts {'(a) the W1/W5 check row': 2, '(b) dated spec record': 2, '(c) Ticket corrections row': 2, '(d) review record line': 9, '(e) capture of a W1/W5 run': 31, 'functional host, file or ref name': 11}; raw `evidence/49/rev05-W5.txt` |
| Observable behavior | PASS — the ticket 48 dispatch file's P4 denylist run over `<B>` at `50731c4e`: hits=0; the names are not written in this record; raw `evidence/49/rev05-observable.txt`. Live role, grant, authority, workspace and handoff rows name roles, refs or "the control plane" (W1, W5) |
| Deviations | none |

Record correction after the revision05 initial review (NF-01, NF-02, NF-03): identifiers above corrected to revision05 and to the three-ticket tagging; Observable-behavior row and capture added; the W4 clause change recorded in the ticket's corrections table (commit `50731c4e`, whose message also claimed the record and capture changes that only this commit carries). Cell results unchanged.

## Revision05 initial review

**Verdict: `CHANGES_REQUESTED`**

| Field | Value |
| --- | --- |
| Candidate | `449f3bf9` (evidence commit of revision05) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; read-only, no pytest by instruction |
| Summary | All five cells pass as written. The order of commits and every hit classification hold. Three Low defects in the record block approval; none needs a content change. |

### Cell results

| Cell | Result | Evidence |
| --- | --- | --- |
| W1 | PASS | 51 hits at the candidate; 30 match `rev05-W1.txt` by path:line and equal the run at `0aae3bf8`; the other 21 are the rev05 captures themselves (place (e)). Each classification checked: (a) the W1 row; (b) spec:7 and spec:148; (c) one corrections row; (d) seven review-record lines; (e) capture lines. No live role holder or location. |
| W2 | PASS | 48:64 names the dispatch file as the carrier and spells no name. |
| W3 | PASS | 0 hits over `<B>`; a wider user-profile, temp and home path grep matches only the regex text of the W3 rows. |
| W4 | PASS | 37 paths; every tag checked against the three boundary blocks at the candidate; paths in no boundary: 0. |
| W5 | PASS | 96 hits; 57 match `rev05-W5.txt`; the rest are the rev05 captures and one review-record line. All 11 "functional host, file or ref name" hits hold up on reading. Live role holder or location: 0. |
| Observable behavior | PASS by the reviewer's own run; no receipt row | Live Grant, Workspace and Authority rows name roles, refs or "the control plane"; profile names exist in the runbook; model-tier grep 0 hits; no host path. The source-project clause rested only on the reviewer's own check (0 hits); no cell or receipt row of this ticket covered it. |
| Order | PASS | Linear history; every closure revision frozen in its own commit before the content or evidence it governs; the red `rev04-*` and `rev02-*` captures unchanged. One gap: the W4 forbid-clause replacement was not in the corrections table. |
| Receipt | PARTIAL | Every cell has a result and a headed capture; counts match. The Candidate row said "revision04" and the W4 row said "47, 49 or both"; no Observable-behavior row. |

### Prior findings

| ID | Status | Evidence |
| --- | --- | --- |
| R49-01 | CLOSED | 48:64 (W2). |
| R49-02 | CLOSED | Each closure revision frozen in its own commit before what it governs; the N49-01 order defect did not recur. |
| R49-03 | CLOSED | Exemption reason accurate; README in `<B>`. |
| R49-04 | CLOSED | Pattern covers the spec header rows and the README paragraph; dated spec rows exempt by name; corrections-table hits are place (c). |
| R49-05 | CLOSED | Leaf, review record and `evidence/49/` in the boundary. |
| R49-06 | CLOSED (ticket 49 scope) | W3 0 hits; the `evidence/47/` residual is N49-05. |
| N49-01 | CLOSED | Places (a)–(e) replace the count; the corrections row records the defect truthfully. |
| N49-02 | PARTIAL | W4 and W5 exist with captures; no Observable-behavior row (NF-02). |
| N49-03 | CLOSED | 47:49 names the ref. |
| N49-04 | CLOSED | `<B>` is exactly the 6 modify and 2 create entries. |
| N49-05 | ROUTED | Recorded for the wave-2 evidence-gate ticket; no PLANNED leaf yet, like the other wave-2 deferrals. |

### New findings

| ID | Class | Severity | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- |
| NF-01 | `EVIDENCE_DEFECT` | Low | this record, revision05 return rows "Candidate" and "W4" | The Candidate row said `0aae3bf8` carries "the ticket text of revision04" while the ticket there says revision05; the W4 row said "tagged 47, 49 or both" while the capture also uses [48] and [47+48+49]. Identifiers did not match the closure (CodeReview §1). Results correct. | `git show 0aae3bf8` line 5; `rev05-W4.txt` tags |
| NF-02 | `EVIDENCE_DEFECT` | Low | this record, revision05 return; 49:27 | No Observable-behavior row; the source-project clause had no capture of this ticket's own (W5 scans vendor and model tokens; ticket 48's P4 scans scripts and gate tests only). Suggested: a row whose capture runs the dispatch file's denylist over `<B>`, records the hit count, names the dispatch file and spells no name. | 48:64 scope; `evidence/49/` held only W1–W5 |
| NF-03 | `TICKET_DEFECT` (record only) | Low | 49:39, 49:60 | Revision05 replaced the revision04 W4 clause "no forbid path of either ticket outside the other's boundary" with "no path outside every boundary"; the corrections row recorded only "W4 names every ticket on this line". Result unaffected: every forbid-matched path is inside another ticket's boundary (49's library/, skills/, tests/ paths are in 47's; 48's AGENTS.md, library/ and doc/requirements/ paths are in 47's or 49's; none of 47's forbid paths touched). | `git show 0aae3bf8 -- 49` W4 hunk; the three boundary blocks |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1–3 | `git log`; reads of CodeReview.md, AGENTS.md, Workflow.md section 0, the ticket and this record at `449f3bf9` | 0 |
| 4 | scratch clone outside the checkout, `git checkout 449f3bf9` | 0 |
| 5 | W1 at the worktree and `git grep … 0aae3bf8 -- <B>`; path:line diff against `rev05-W1.txt` | 0 (51 / 30, identical to the capture) |
| 6–7 | W2; W3 | 0 (1 hit); 1 (0 hits) |
| 8–9 | W4 `git diff --name-only 7335e78..HEAD`; boundary blocks of 47 and 48 | 0 (37 paths) |
| 10 | W5 at the worktree and at `0aae3bf8`; diff against `rev05-W5.txt`; per-file classification counts | 0 (96 / 57) |
| 11–12 | `grep LIVE rev04-W5.txt`; `cat rev04-W4.txt`; REQ:18, spec:31, README:27/31, 47:49/90; `git show --stat` of all 12 commits and the re-plan/content diffs | 0 |
| 13–15 | wave-2 routing grep; profile-name and role/grant/workspace greps; model-tier and user/temp/home-path greps over `<B>` | 0 / 0 / 1 (0 hits) |
| 16–17 | added lines of `7335e78..449f3bf9 -- <B>` (562) grepped for target names, secret shapes, chat tone; capture and history linearity checks | 1 (0 target-name hits; secret words only in the record's own command text; 0 chat tone) / 0 |

Not verified: the dispatch file's denylist (only the target-project names known to this seat, 0 hits); the control plane's classifier (labels checked by hand); no pytest; tickets 47 and 48 own cells; R4-7's receipt-cell schema (binds wave 2).

## Revision05 correction review

**Verdict: `APPROVED`**

| Field | Value |
| --- | --- |
| Candidate | `5ad316bf` (record correction; content unchanged since `40ab88eb`) |
| Reviewer | independent `ticket-review` seat; authored nothing in this ticket; read-only, rev-qualified `git grep` and `git show` |
| Summary | All three findings are closed, all W1–W5 results hold at the candidate, and the two commits introduce no new defect. |

### Findings status

| ID | Status | Evidence |
| --- | --- | --- |
| NF-01 | CLOSED | Revision05 return: Candidate row says revision05; `0aae3bf8` is the revision05 re-plan commit and `40ab88eb` is its ancestor (`merge-base --is-ancestor` exit 0). The W4 row describes the three-ticket tagging, matching the `[47]`/`[48]`/`[49]`/`[47+48+49]` tags in `rev05-W4.txt`. Order-row identifiers all resolve to the commits their roles describe. |
| NF-02 | CLOSED | Observable-behavior row added, pointing to `evidence/49/rev05-observable.txt`, headed by cell, candidate (`50731c4e`) and command; the denylist appears only as a placeholder (8 alternatives); `hits=0`, `exit=1`, no name spelled. Reproduced with the P4 pattern of the ticket 48 dispatch file over `<B>` at `5ad316bf`, `50731c4e` and `449f3bf9`: 0 hits each. Positive control over the whole tree at `5ad316bf`: 200 hits in 55 files, so the pattern matches where names exist. |
| NF-03 | CLOSED | Ticket 49 corrections row: the "Was" clause is word for word the revision04 W4 Expected and the "Now" clause word for word the revision05 W4. Substance holds: over `7335e78..5ad316bf` each of the 6 forbid-matched paths (AGENTS.md, REQ-043, profile.py, router-control.md, the two test files) lies inside another ticket's modify/create set. |

### Cells

| Cell | Result | Evidence |
| --- | --- | --- |
| W1 | PASS (unchanged) | Hits outside the captures equal `rev05-W1.txt`: (a) 49:36; (b) spec:7, spec:148; (c) 49:57; (d) record lines 19, 21, 31, 32, 34, 84, 105. Capture hits now 40 (the rev05 captures are in the tree). `rev05-observable.txt` adds 0. |
| W2 | PASS (unchanged) | 48:64. |
| W3 | PASS (unchanged) | 0 hits; `rev05-observable.txt` has no drive-letter path. |
| W4 | PASS (unchanged) | 38 paths against the three boundary blocks at `5ad316bf`; paths in no boundary 0; the 6 new paths are the rev05 captures and the observable capture, all `[49]`; the paths `70c7a97c` touched stay covered. |
| W5 | PASS (unchanged) | Two extra hits since the capture, both classifiable: record line 149 (d) and ticket 47's R3-02 row "codex-native reference" (functional file reference, added by `70c7a97c`). None a live role holder or location. |
| Observable behavior | PASS | Denylist over `<B>`: 0 hits (reproduced). Live role, grant, workspace and handoff rows produce no live hit. |

No new findings. The record is honest about `50731c4e` (one file, +1 line; its message also claimed the record and capture that only `5ad316bf` carries). The diff `449f3bf9..5ad316bf` limited to ticket 49's files holds only the three changes; ticket 47's `70c7a97c` edits inside `<B>` add no denylist hit, host path or live vendor hit; added lines hold no secret, token, password or email.

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1–5 | `git log`; reads of CodeReview.md, AGENTS.md, Workflow.md section 0; `git diff --stat 449f3bf9 5ad316bf`; `git show 50731c4e 5ad316bf`; `git show --stat 70c7a97c`; `git show 5ad316bf:` ticket, record, captures; `git diff b927e48d 0aae3bf8 -- 49` | 0 |
| 6–8 | P4 pattern of the ticket 48 dispatch file extracted to a scratch file outside the checkout; `git grep -niE -f <P4> <c> -- <B>` for `5ad316bf`, `50731c4e`, `449f3bf9`; positive control over the whole tree | 1 / 1 / 1 (0 hits); 0 (200 hits, 55 files) |
| 9–12 | W1, W2, W3, W5 at `5ad316bf`; W5 and W3 patterns over `rev05-observable.txt` | 0 / 0 / 1 / 0; 1 (0 hits) |
| 13 | boundary blocks at `5ad316bf`; `git diff --name-only 7335e78..5ad316bf`; tagging and forbid-coverage script in the scratch directory | 0 (38 paths, 0 in no boundary, 6 forbid-matched paths covered) |
| 14 | `git log -1 746a1737 40ab88eb`; `git merge-base --is-ancestor 40ab88eb 0aae3bf8`; secret/email grep over added lines of `449f3bf9..5ad316bf` | 0 / 0 / 1 (no hits) |

Not verified: no pytest, by instruction, and no scratch clone (rev-qualified `git grep`/`git show` in the read-only checkout, HEAD `a47e976b`); classification of hits inside the captures accepted by file path; the `rev05-W4.txt` tagging logic not re-executed (own matcher used). For the integration gate to admit this candidate the record must hold this review against `5ad316bf`; the control plane appends both revision05 reviews.
