# REVIEW — ticket 49 Vendor and model names out of governance documents

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
