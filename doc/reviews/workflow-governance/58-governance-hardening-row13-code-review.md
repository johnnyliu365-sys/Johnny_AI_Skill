# REVIEW — ticket 58 Governance hardening (row 13 and wave-1 carried findings)

## Revision01 initial review

**Verdict: `CHANGES_REQUESTED`.** Part B and part C do what the ticket asks. Both part C scripts behave as stated, the receipt passes both checkers, and the three ticket test files, `mypy --strict` and the full suite are green with no new red. Part A is where the problems are. The consistency test carries the ticket 47 rules forward, but three of its own exemptions or pins still let a retired-rule sentence through on the real tree: S58-01 (a Chinese reviewer-executor sentence is masked by any 不得/不可/不是 elsewhere in the sentence), S58-02 (a backticked `reviewer` is never a person) and S58-03 (the precedence sentence reversed by a negation stays green). These are additive fixes inside `tests/test_governance_consistency.py`. S58-05 is an evidence gap in the same file. S58-08 and S58-09 are evidence gaps in the two script test files: the scripts behave correctly, but my counter-mutations stay green. S58-04 goes to the control plane: the ticket's "git environment rules of the wave-2 gates" names no list, and the gates disagree. Under rule B, S58-04 is the only finding in a blocking family (an inherited variable turns a correct index into exit 1), and it was already there at the base. No other finding would block approval on its own.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/58-governance-hardening-row13.md`, revision01 (state `IN_PROGRESS`, initial review dispatched) |
| Spec | workflow-governance Revision 04 R4-1, R4-2, R4-4; ticket 47 D7, D8, D9, N8-04, N9-03 to N9-06, R3-07, F-07; ticket 48 F-06, NF-04, NF-08, NF-16, NF-17; change-log row 13 |
| Candidate | `49c2c43cee546cf28a15eb3099c7c8254ecad810` on `cp/wave2-58-governance-hardening-row13` |
| Base | `dddc21266933b508955578f7e1370ee8ea2d7d50` (the dispatch base, parent of `f85b4917`) |
| Commits | `f85b4917` (implementation), `49c2c43c` (tests only). Author and committer on both: `Johnny Liu <johnny.liu365@gmail.com>`. Trailer on both: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. That is the correct form: the trailer names the model that did the work. Which model ran the seat is not verified here |
| Review worktree | `.worktrees/58-governance-hardening-row13-review`, detached at the candidate, porcelain empty before and after |
| Scratch | `.worktrees/58-governance-hardening-row13-review-scratch` (a `--no-hardlinks` clone at the candidate for the mutations, probe repositories, captures) |
| Receipt | `.worktrees/58-governance-hardening-row13-out/RETURN.md` (LF, 159619 bytes, 0 CR) |
| References applied | `CodeReview.md` (whole file, §5 rule B); `review-checks.md` (test truthfulness and reviewer counter-mutation, error-code consistency, exception behaviour, path identity, missing values) |
| XSS / privileged JS | Not applicable: a Python test, two stdlib command-line scripts, a README and two Markdown sentences. No browser, DOM or JavaScript surface |
| Agent control / task-worktree / profile fan-out / POC ancestry | Not applicable. No Agent control path; one implementer seat; no POC or staging |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Boundary | PASS | `git diff --name-only dddc2126 49c2c43c` gives exactly 8 paths, all `modify`/`create` entries of the boundary block. Nothing under `doc/reviews/`, `library/`, `.github/`, `template/`, and no forbidden script |
| 2 | Identity, stdlib, `Any`, names | PASS | Author/committer as above. Added imports: `os` (index_pins) and `re, shutil, sys, tempfile, unittest, collections.abc, dataclasses, pathlib` (new test). No `Any`, no `type: ignore`. The added lines name no company address, no target project, no vendor and no host path |
| 3 | P1 (three ticket test files) | PASS | My run with `-rA`: `198 passed, 198 subtests passed`, exit 0. The seat's run: the same counts |
| 4 | T1 (`mypy --strict --python-version 3.11`) | PASS | mypy 2.3.0: `Success: no issues found in 3 source files`, exit 0 |
| 5 | Payload boundary | PASS | `tests/test_plugin_payload_boundary.py`: `1 failed, 40 passed, 226 subtests`; the one failure is `CommittedPinTests::test_the_pinned_sha_exists` |
| 6 | F1 (full suite under the host lock) | PASS | `8 failed, 3332 passed, 35 skipped, 6595 subtests passed in 735.89s`, exit 1. All 8 `FAILED` names are among the 12 base names of `jas48_F1_base.txt`: zero new red. The seat's F1 has the same 8 names |
| 7 | Receipt: committed ticket 48 checker | PASS | `receipt_check.py RETURN.md <review worktree>`: `receipt defects: 0`, exit 0 |
| 8 | Receipt: evidence gate | PASS | `evidence_gate.py` with the three wave-1 tools (`dispatch_lint.py`, `index_pins.py`, `receipt_fence_check.py`), `--evidence-root` the out dir and `--require-cell P1 T1 M1 F1`: `cells=6 defects=0`, exit 0. That equals `E1.txt` |
| 9 | Receipt: form | PASS | My own reader: 0 CR in the receipt and in all 7 captures. Every raw block is byte-identical to its capture file. Every `exit:` list equals the `exit=` lines of its capture in order (M1: 85 entries). Every cell names the candidate. Every `tool_digest` equals the sha256 of the blob at the candidate. The M1 tails are contiguous pytest tails with failure lines and summaries, not filtered to counts |
| 10 | M1 (the seat's 82 mutations) | PASS, one equivalence accepted | 3 baselines, 81 red, 1 marked equivalent (mutation 85). See "Equivalence claim" |
| 11 | Widened sweep, own run | PASS | See "Seat choice 2" |
| 12 | Part B wording | PASS | See "Part B diff" |
| 13 | Reviewer counter-mutations | 18 run: 3 red (CM3 only incidentally, CM9 is a control, CS3), 14 green, 1 expected equivalent (CS4) | Tables below. The doors that stay green on the production check are S58-01, -02, -03, -06, -08 and -09 |

### Part A rows

| Row | Status | Evidence |
| --- | --- | --- |
| Row 13 sweep: D7 patterns over the routed set (D7 roots) plus every SPEC under `modules/spec/` and every runbook under `doc/runbooks/` | PASS | `ROUTED_ROOTS` equals the D7 `ROOTS` of revision09. `historical_files` covers 18 historical SPECs and 2 runbooks (the handover runbook and `live-verification-047.md`). The real tree: 0 live hits, 0 defects |
| A routed hit is red; a historical hit is red unless the file carries the D8 note | PASS | `classify(..., historical=True)` gives `TOLERATED_NOTE` only when `carries_note`. Injection cases remove the note and append a retired sentence, and the result is LIVE plus `NOTE_MISSING` (SPEC and dated runbook). Seat mutations 4–6 are red |
| Tolerated-hit report by file and count | PASS on content; evidence gap S58-05 | `-rA` output: `handover-2026-08-22-plugin-distribution.md: 3`, `adaptive-project-orchestration.md: 1`, `claude-code-plugin-distribution.md: 1`, `executor-routing.md: 2`, `project-authority-integration.md: 1`. I read all 8 sentences; each is in a file that carries the note. A plain `pytest -q` run (P1, F1) shows none of it |
| A missing routed file is red, not skipped | PASS | `read_strict` and `markdown_under` add `MISSING_OR_UNREADABLE`, `MISSING_ROOT`, `EMPTY_ROOT` and `UNDECODABLE` defects, and the real-tree test asserts `defects == []`. Injection cases delete `AGENTS.md`, delete `template/`, empty `doc/runbooks/` and write undecodable bytes, and each one is red. Seat mutation 7 is red |
| N8-04: both halves of R4-1, as retired phrasings and positively in `AGENTS.md`, `Workflow.md` §0 and R4-1 | PASS for the positive pins; narrow negative patterns (S58-06) | Removing either half from any of the three scopes gives `R41_HALF_MISSING`, and a half moved below §0 does not count. `h1`/`h2` catch the listed forms (派工以整合佇列列表示 among them). Paraphrases with an adverb or "rows of the merge queue" stay green (CM5–CM7) |
| R3-07: an execution sentence names the integration script; reviewer, fixed integrator, "the reviewer who approved it", 代為 commit are red | PARTIAL (S58-01, S58-02) | `EXECUTION_SENTENCE` without `integration script` is red. R4-4 and CodeReview are pinned positively ("by whoever holds budget", no fixed integrator). CM1 and CM2 below are green |
| N9-06: no integration-script mask; merge/push/land verbs; 代為 commit; queue-row dispatch; eight ticket-47 injections and F-07 red | PASS for the named gaps; new masks S58-01, S58-02 | `PatternTableTests` asserts that no reviewer-family exemption matches "integration script", 整合腳本 or R4-4. All 8 `INJECTIONS` and the R4-4 F-07 edit are red, asserted by pattern name, so an overlapping pattern cannot mask a removed one. Seat mutations 9–26 are red. Ticket 47's record does not list its eight injections ("8 injections, 2 caught"), so the seat built eight from the N9-06 text; each gap N9-06 names has at least one |
| N9-04: absence and presence with one regular expression | PASS | `carries_note` (first five non-empty lines) and `note_anywhere` (every line) both use `PRECEDENCE_NOTE`, the D8 expression. The old exact substring is kept as an extra check. Reworded notes, a note far below the head, and the old substring on the template and the index are all red |
| N9-05: precedence sentence by rule and place | PARTIAL (S58-03) | Place: exactly one occurrence, inside `## 0.`; moving it out or duplicating it is red. Rule: six expressions over the bullet. Reversal by rewording ("以該 SPEC 為準") is red. Reversal by negation ("衝突處不以本修訂為準") is green on the real-tree check (CM3) |

### Part B diff

`git diff dddc2126 49c2c43c -- Workflow.md doc/runbooks/` changes two lines and nothing else:

- `Workflow.md:86`: "早於 Revision 04 的專案 SPEC（workflow-governance SPEC 以外者）" becomes "…以外者），以及 runbooks 目錄下帶有同一優先序註記的日期化交接 runbook，". The rest of the sentence is byte-identical.
- `doc/runbooks/handover-2026-08-22-plugin-distribution.md:3`: "prevail;" becomes "prevail, as the precedence sentence in `Workflow.md` section 0 states for dated handover runbooks that carry this note;", and "is not a competing reference and" is inserted before "raises no". That is the citation part B asks for, written in the sentence's own terms. The note still matches D8 (`d8_precedence.py` exit 0, 19 covered files).
- No other runbook changed. The scripts README gained the F-06, NF-04, NF-08, NF-16 and NF-17 paragraphs and changed nothing else.

**Seat choice 1: "runbooks 目錄" instead of `doc/runbooks/`.** The sentence is unambiguous in this repository. There is one runbooks directory (`git ls-files` shows only `doc/runbooks/`), and the clause is bounded twice: dated handover runbooks, and only those that carry the same precedence note. Part A pins it by place (§0, once) and by rule (`PRECEDENCE_RUNBOOK_SCOPE`, `PRECEDENCE_RUNBOOK_NOTE`, each with a red injection). It is not a ticket conflict. The payload test refuses only a *backticked* path token. I reproduced that (`` `doc/runbooks/` `` gives `KeyError: 'doc/runbooks/'` and three closure failures). The plain words `doc/runbooks/ 下` pass the payload test (`1 failed, 40 passed`, the pinned-sha failure only). So the ticket's path could have been named, and the STATEMENT overstates the conflict. The seat's wording also avoids naming non-shipped development material in a payload document. I record it as S58-07 (note, non-blocking) and leave the wording to the control plane.

**Seat choice 2: no runbook gained a note.** Confirmed by two independent runs. (a) The test's own `sweep` on the candidate: 0 live, 0 defects, the 8 tolerated hits above, all in noted files; `note_defects` empty. (b) The committed `d7_sweep.py`, copied to scratch with `ROOTS = ['modules/spec', 'doc/runbooks']` and run on the candidate: 69 hits, 1 LIVE. That one is the handover runbook's own note at line 3 ("Where it has the reviewer commit, submit …"), and that file carries the note. The only runbook without a note is `live-verification-047.md`, which has 0 hits in both runs. I also read its 20 governance-term lines by hand and found no retired rule. `d8_precedence.py` exit 0.

### Part C rows

| Row | Status | Evidence |
| --- | --- | --- |
| F-06 zero fences | PASS | CLI probe: a section with prose only gives `FAIL NO_FENCES …`, `fences=0 failures=1`, exit 1. A scanned section with a capture line and no fence gives `NO_FENCES`, exit 1 (test) |
| F-06 empty scan | PASS | `--scan` of an empty directory gives `SCAN_NO_RECEIPTS`, exit 1. Receipts with no checked section give `SCAN_NOTHING_CHECKED`, exit 1. A missing scan root stays exit 2 |
| F-06 `--help` 3 | PASS | `--help` 3, `-h` 3 (CLI and subprocess test) |
| F-06 extra positional arguments to `--scan` 3 | PASS | `--scan d extra` gives exit 3 and `error: --scan takes one directory and no other argument: extra`, with nothing on stdout |
| F-06 `--require-cmd` gone (3) | PASS | Not in the parser. It gives exit 3 in both the explicit and the scan form |
| NF-04 quotepath and `-z` | PASS | Every git child gets `--no-replace-objects -c core.quotepath=false`, and `ls-files -z` is split on NUL. CLI probe in a repository with `core.quotepath` default: `git ls-files` prints `"\350\246\217…"`, yet `index_pins --check` on a row for `規格/葉子.md` gives `drift=0 … defects=0`, exit 0. The test pins the same with `core.quotepath=true` set |
| NF-08 unborn HEAD exit 2, README | PASS | CLI probe: `tool fault: git log -1 -- leaf.md failed with exit 128: fatal: your current branch 'main' does not have any commits yet`, exit 2. The README and the docstring state it. The test checks `--check` and `--write` and that the index is not written |
| NF-17 non-commit revision exit 1 with a named code | PASS | CLI probe: a sealed row on an annotated tag (correct digest) gives `SEALED_REV_NOT_COMMIT … is a tag object, not a commit`, exit 1. The same row on the commit gives exit 0. A tree object gives `SEALED_PIN_INVALID`, exit 1 (the existing code, kept by the existing tests; the ticket asks for "a named code", which this is). A failing `cat-file -t` is a `GitFault` (exit 2) |
| NF-16 README note | PASS | README: "`evidence_gate.py` … supersedes the ticket 48 receipt checker … and the committed checker is not edited". `receipt_check.py` is unchanged |
| Wave-2 git environment | PASS as written; list undefined (S58-04) | `git_environment()` removes the 9 variables of `contract_gate.py` and every `GIT_CONFIG*` (case-insensitive), and sets `GIT_NO_REPLACE_OBJECTS=1` and `GIT_NO_LAZY_FETCH=1`. It is applied to `git_text`, `git show` and `rev-parse --show-toplevel`, which are all of the script's git children. `evidence_gate.py` removes 13 (adding `GIT_QUARANTINE_PATH`, `GIT_REPLACE_REF_BASE`, `GIT_GRAFT_FILE`, `GIT_SHALLOW_FILE`) |
| One-line escaping in every print and git message touched | PASS | Every `print` in `receipt_fence_check.py` that carries a subject goes through `say`/`one_line`. In `index_pins.py`, the usage, fault, `SHALLOW_HISTORY`, stale, per-file and defect lines are escaped. C0, DEL, C1, U+2028 and U+2029 are escaped (the bytes of `_UNPRINTABLE` read back as `e2 80 a8` and `e2 80 a9`). A backslash is not escaped, so a literal `\x0a` in a name prints the same as an escaped newline. It is still one line |
| Exit codes per R4-2 | PASS | New reds `NO_FENCES`, `SCAN_NO_RECEIPTS`, `SCAN_NOTHING_CHECKED` and `SEALED_REV_NOT_COMMIT` are exit 1. Unborn HEAD and a failing type query are exit 2. `--help`, `-h`, `--require-cmd` and extra `--scan` arguments are exit 3. The `main` catch-all is still exit 2 |

### Equivalence claim (mutation 85)

Accepted. `_run` builds `_Parser(add_help=False)`, and `_Parser.error` raises `_UsageError`. In Python 3.11, argparse reaches `SystemExit` only through `exit()`, which only the help/version actions and the default `error()` call. Neither exists here, so `except SystemExit` cannot run, and rewriting its `else 3` to `else 0` cannot be observed. The guard is defensive only. The equivalence holds as long as no help or version action is added.

### Reviewer counter-mutations (documents; `tests/test_governance_consistency.py` on the scratch clone, each restored, porcelain 0)

Each mutation goes through a door the seat's M1 did not use. The seat removed or weakened rules; I kept the rules and wrote sentences that should be red.

| ID | Door | Result | Reading |
| --- | --- | --- | --- |
| CM1 | `Workflow.md` + "審閱者核准後代為 commit 到候選分支，不得略過閘門。" | GREEN (43 passed) | S58-01: the 不得 of an unrelated clause exempts the 代為 commit sentence |
| CM2 | `CodeReview.md` + "After approval the `reviewer` merges the candidate into main." | GREEN | S58-02 |
| CM3 | `Workflow.md` §0 "衝突處以本修訂為準" → "衝突處不以本修訂為準" | `precedence_defects` on the tree = `[]`; the file run is 1 failed, but only because the reversed-precedence injection's `str.replace` no longer finds its phrase and becomes a no-op. "R4-1、R4-4 以外的衝突處以本修訂為準" also gives `[]` | S58-03 |
| CM4 | `AGENTS.md` + "The ticket-review seat integrates the approved candidate by hand." | GREEN | S58-06 (vocabulary) |
| CM5 | `AGENTS.md` + "The merge queue also holds every pending dispatch." | GREEN | S58-06 (`h2` needs the verb right after "queue") |
| CM6 | `AGENTS.md` + "整合佇列也承載每一筆派工。" | GREEN | S58-06 |
| CM7 | `AGENTS.md` + "Pending dispatches are recorded as rows of the merge queue." | GREEN | S58-06 (`h1` needs "queue row/entry") |
| CM8 | `Workflow.md` + "The approver runs the integration script and pushes the result." | GREEN | S58-06 (vocabulary) |
| CM9 | control: the seat's own 代為 commit injection without a negation word | RED (6 failed, LIVE `c 審閱者整合 (zh)`) | the sweep reaches the appended text; CM1 is green only because of the negation word |

### Reviewer counter-mutations (scripts; their test files on the scratch clone, each restored, porcelain 0) and probes

| ID | Door | Result | Reading |
| --- | --- | --- | --- |
| CS1 | `receipt_fence_check.py` explicit mode: `if fences == 0:` becomes `if fences == 0 and not self_note:` | GREEN (60 passed) | S58-08. The candidate is right (CLI probe: `--self-note` on a zero-fence section gives `NO_FENCES`, exit 1); no test pins it |
| CS2 ×6 | `index_pins.py`: one of `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_PREFIX` dropped from `GIT_SELECTING_VARIABLES` | GREEN ×6 (95 passed each) | S58-09. The spy test injects and checks only `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` and four `GIT_CONFIG*` names. The seat's mutation 65 dropped all of them at once |
| CS3 | `index_pins.py` `_UNPRINTABLE` without the C1 range | RED (`test_one_line_escapes_control_characters_and_line_separators`) | pinned |
| CS4 | `receipt_fence_check.py` scan: `elif section_count == 0 or fences == 0` becomes `elif section_count == 0` | GREEN, equivalent | when a section was counted and the total is 0 fences, every counted section already has `NO_FENCES`, so the second disjunct never decides the exit |

| Probe | Result |
| --- | --- |
| `GIT_GRAFT_FILE` naming a graft that gives HEAD no parent, on a correct open pin | Candidate: `STALE INDEX.md:3 leaf.md`, exit 1 (without the variable: exit 0). The base script gives the same, so this is not a regression (S58-04) |

### New findings

| ID | Class | Severity | Rule B | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| S58-01 | `IMPLEMENTATION_DEFECT` (part A rows R3-07 and N9-06) | Low | Not blocking (no exit-code, confinement or P0 effect). It is a gate gap that would let a regression through, so it is fixed in the next change to this test | `tests/test_governance_consistency.py:87` (`REVIEWER_NEGATED_ZH`), `:395` | The Chinese exemptions (不是, 不由, 不得, 不等於, 不指定, 並非, 而非, 不可) match anywhere in the sentence, and `，` does not split a sentence. So "審閱者核准後代為 commit 到候選分支，不得略過閘門。" is exempt even though the negation is not about the executor. STATEMENT choice 3 ("negations of the executor only") is true of the English list, not of this one. This is the N9-06 shape (an exemption masks a reviewer named as executor in the same sentence) through a different word. Fix: tie the negation to the reviewer or the verb (for example 不由審閱者, 審閱者不得(整合\|合併\|推送\|代為)), and add CM1 as an injection | CM1 green; CM9 control red |
| S58-02 | `IMPLEMENTATION_DEFECT` (part A rows R3-07 and N9-06) | Low | Not blocking, same reasoning as S58-01 | `tests/test_governance_consistency.py:373,383` (`FIELD_NAME`) | Every backticked `reviewer`, `submitter` or `review_candidate` is replaced by `FIELD` before any pattern runs, so "the `reviewer` merges the candidate" can never be red. D7 had no such exemption. Without it, the real tree has exactly one hit, `modules/spec/workflow-governance.md:204` ("The integration script reads `review_candidate` and `reviewer` from the review record …"). Fix: exempt that field-list form only (for example a backticked name followed by "from the review record", or a sentence whose subject is the integration script), and add CM2 as an injection | CM2 green; scratch run with `FIELD_NAME` disabled shows the single R4-7 hit |
| S58-03 | `IMPLEMENTATION_DEFECT` (part A row N9-05, "reversing the precedence … is red") | Low | Not blocking | `tests/test_governance_consistency.py:573` (`PRECEDENCE_REVERSED_OK`), `:1033` | `R4-1[、，, 及和]*R4-4[^；。]{0,12}衝突[^；。]{0,12}以本修訂為準` accepts "衝突處不以本修訂為準" and "R4-4 以外的衝突處以本修訂為準", the two shortest ways to reverse the rule. The reversed-precedence case uses `str.replace`, which does nothing when its phrase is absent. Other cases use `removed()`, which asserts the phrase is present. Fix: pin `與 R4-1、R4-4 衝突處以本修訂為準` exactly (or refuse 不/以外 between the parts), use `removed()` in every case, and add both doors as cases | CM3 |
| S58-04 | `TICKET_DEFECT` (part C, "the git environment rules of the wave-2 gates") | Medium | In a blocking family: an inherited variable turns a correct index into exit 1, an environment input reported as a contract red (R4-2). It was already there at the base and is not a regression | ticket part C; `skills/johnny-project-takeover/scripts/index_pins.py:116-120`; `contract_gate.py:120-131` vs `evidence_gate.py:98-112`; `tests/test_gate_index_pins.py:660-676` | The ticket lists "repository-selecting `GIT_*`" without defining the set, and the wave-2 gates disagree: `contract_gate.py` removes 9 variables, `evidence_gate.py`, `coverage_map.py` and `repair_guard.py` also remove `GIT_GRAFT_FILE` and `GIT_SHALLOW_FILE`. The seat followed `contract_gate.py`. A graft file turns a correct open pin into `STALE`, exit 1, and `--write` would then repin to the wrong commit. Removing `GIT_SHALLOW_FILE` would break a ticket 48 test that pins "an inherited shallow file is a tool fault", which is why the seat kept it (STATEMENT choice 8). The control plane names one list, and decides that test and whether `GIT_GRAFT_FILE` is removed in this ticket's correction | graft probe at the candidate and at the base: exit 1 both, exit 0 without the variable |
| S58-05 | `EVIDENCE_DEFECT` (part A row 13, "reports every tolerated hit by file and count in its output") | Low | Not blocking | `tests/test_governance_consistency.py:699-713`; receipt P1, F1 | The report is printed to stderr from a passing test. `pytest -q` captures it and drops it, so neither P1 nor F1 contains a single `tolerated under` line. It shows only with `-rA` or `-s` (my P1 run shows all 5 lines). The test also checks the report only against the same `Sweep` it was built from, so a new or vanished tolerated file never changes the result. Fix: run the P1 cell with `-rA` (or emit the report as part of a test result), and decide whether the tolerated set should be pinned | `grep -c "tolerated under"` = 0 in `P1.txt` and `F1.txt`; 5 in my `-rA` run |
| S58-06 | `OUT_OF_SCOPE_HARDENING` | Low | Not blocking | `tests/test_governance_consistency.py:102-199` | The sweep's vocabulary is D7's: `reviewers?\b` misses "the ticket-review seat" and "the approver" (CM4, CM8). `h1`/`h2` miss an adverb between noun and verb and "rows of the merge queue" (CM5–CM7). None of these is live in the tree today. Route to the next change of this test, next to the contract-gate pin of R4-1 | CM4–CM8 |
| S58-07 | `OUT_OF_SCOPE_HARDENING` (note) | Low | Not blocking | `Workflow.md:86`; STATEMENT choice 5 | The sentence says "runbooks 目錄", not the ticket's `doc/runbooks/`. It is unambiguous here and pinned by rule and place (see "Seat choice 1"). The plain words `doc/runbooks/` would have passed the payload test; only the backticked token fails. The control plane accepts the wording or asks for the plain path in the correction. If it asks for the path, `PRECEDENCE_RUNBOOK_SCOPE` must follow | payload test on the clone, both wordings |
| S58-08 | `EVIDENCE_DEFECT` (part C F-06, "a section with zero fences … exit 1") | Low | Not blocking. The candidate is correct, but a regression would let an empty self-note run pass, so it is fixed with the next change to this script | `tests/test_gate_receipt_fence_check.py:1610-1727` | No test runs `--self-note` on a section with no fence, so exempting self-note runs from `NO_FENCES` stays green | CS1; CLI probe at the candidate: exit 1 |
| S58-09 | `EVIDENCE_DEFECT` (part C, git environment rules) | Low | Not blocking. The candidate is correct; a dropped variable would go unnoticed, so it is fixed with the next change to this script | `tests/test_gate_index_pins.py` `test_every_git_child_runs_with_the_hardened_command_line_and_environment` | Six of the nine removed variables can each be dropped from `GIT_SELECTING_VARIABLES` with every test green. Fix: inject and assert every name in the tuple (and whatever S58-04 adds), or compare the tuple with the shared list | CS2 ×6 |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | `git log`, `git diff --stat`/`--name-only`/`--word-diff` `dddc2126..49c2c43c`; `git status --porcelain` (review worktree, main checkout) | 0; porcelain empty |
| 2 | `git clone --no-hardlinks --no-checkout` of the review worktree into scratch; checkout `49c2c43c` | 0 |
| 3 | `sweep_report.py` (the test module's `sweep`, `tolerated_report`, `note_defects`, `r41_defects`, `r307_defects`, `precedence_defects`, `handover_citation_defects` on the candidate) | 0 (0 live, 0 defects, 8 tolerated) |
| 4 | `d7_sweep.py` copied with `ROOTS = ['modules/spec', 'doc/runbooks']`; `d8_precedence.py` | 1 (one LIVE, the noted handover note); 0 |
| 5 | payload test on the clone: as committed; plain `doc/runbooks/`; backticked `` `doc/runbooks/` `` | 1 (pinned sha only); 1 (pinned sha only); 1 (KeyError + 3 closure failures + pinned sha) |
| 6 | `receipt_check.py` on `RETURN.md`; `evidence_gate.py … --require-cell P1 T1 M1 F1` with the three wave-1 tools; `verify_receipt.py` (LF, raw blocks, exit lists, candidate, digests) | 0; 0; all equal |
| 7 | CLI probes: `receipt_fence_check.py` (zero fences, empty scan, idle scan, `--help`, `-h`, extra argument, `--require-cmd` ×2, missing root, two positionals) | 1, 1, 1, 3, 3, 3, 3, 3, 2, 3 |
| 8 | CLI probes: `index_pins.py` (non-ASCII leaf, tag sealed, commit sealed, tree sealed, unborn HEAD; graft at candidate and base) | 0, 1, 0, 1, 2; 1, 1 |
| 9 | `python -m mypy --strict --python-version 3.11` on the two scripts and the new test | 0 |
| 10 | `python -m pytest tests/test_governance_consistency.py tests/test_gate_index_pins.py tests/test_gate_receipt_fence_check.py -q -p no:cacheprovider -rA` (review worktree) | 0 (198 passed) |
| 11 | `cm_docs.sh`: CM1–CM9, each with `tests/test_governance_consistency.py`, restored by `git checkout`; `cm_harness.py` (CM3 on `precedence_defects`, `FIELD_NAME` disabled) | see table |
| 12 | host lock `C:/Temp/claude/jas-fullsuite.lock` with `mkdir`, retried every 30 s: waited from 18:45Z while runs `60-rev01-initial` and `jas59b-f1-1311949` held it (never removed); acquired 19:08:24Z with `run.txt` = `run=58-rev01-initial`; `Get-CimInstance Win32_Process` at acquisition: no pytest or mutation process (only two `tail`/`grep` watchers started 2026-10-27 from a checkout outside this repository, and the query itself); released 19:20:42Z after checking that `run.txt` still named this run | 0 |
| 13 | `python -m pytest tests -q -p no:cacheprovider` (review worktree, under the lock, no other pytest of mine running); `FAILED` names compared with `C:/Temp/claude/jas48_F1_base.txt` (CR removed, `^FAILED` lines) | 1 (8 failed, all base names) |
| 14 | `cm_scripts.sh`: CS1–CS4, each with its full test file, restored by `git checkout` | see table |

Raw logs: kept by the reviewer seat in `.worktrees/58-governance-hardening-row13-review-scratch` (`cm_docs.txt`, `cm_scripts.txt`, `d7_widened.txt`, `p1_mine.txt`, `t1_mine.txt`, `f1_mine.txt`, `procs_at_acquire.txt`, `fullsuite.log`, `e1_mine.txt`, `p9_full.txt`); not committed. P1, F1, the payload runs and mypy were judged on their unfiltered output (`p1_mine.txt` with `-rA`, `f1_mine.txt`). The counter-mutation scripts write filtered extracts to their logs (the diff, `FAILED` lines, `E` lines, the summary line and the exit code), and the full output of each run was overwritten by the next one. For the green runs the summary and exit code are the whole signal. For the three red runs I read the failing test names and assertion lines. The reason CM3 went red was established separately on the unfiltered `precedence_defects` result (`cm_harness.py`).

Not verified: the ticket 47 review's own eight injections (the record gives only "8 injections, 2 caught"), so I compared the seat's eight with the gaps N9-06 names, not with the originals; which model ran the implementation seat; Linux and macOS behaviour of the two scripts (the probes ran on this Windows host only); Markdown rendering; whether `GIT_SHALLOW_FILE` should be removed despite the ticket 48 test (S58-04, the control plane's call).

```review-verdict
candidate: 49c2c43cee546cf28a15eb3099c7c8254ecad810
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/58-rev01-initial
reviewed_at: 2026-11-06
```

## Revision02 initial review

**Verdict: `CHANGES_REQUESTED`.** Correction 1 closes S58-03, -04, -05, -08 and -09 completely. Every door I left open in revision01 is now red: CM1, CM2, both CM3 doors, CS1 and the six CS2 drops. The graft probe and the shallow-file probe give exit 0 on a correct pin, also under `--write`, which leaves the index unchanged. The receipt passes both checkers. P1, `mypy --strict` and the full suite are green with no new red. Two rows are only partly closed, and each leaves a new door: S58-10 (row S58-01: `審閱者不得…` about another verb still exempts an executor clause in the same sentence) and S58-11 (row S58-02: the field-list lookahead accepts `must`, `are`, `is` and seven more words that the tree does not need, so "`reviewer` and `submitter` must merge the candidate" stays green). Both are Low, both are additive fixes of one expression each in `tests/test_governance_consistency.py`, and under rule B neither would block approval. S58-12 is hardening, and S58-13 is a receipt-order note.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/58-governance-hardening-row13.md` at `56f6cd75`, closure revision02 (part C names the git environment list; section "Revision02") |
| Candidate | `71b0d8ff99ac17e7527a12587fe610a3cfaf41b9` on `cp/wave2-58-governance-hardening-row13`, one additive commit on the revision01 candidate `49c2c43c` |
| Commit | Author and committer `Johnny Liu <johnny.liu365@gmail.com>`; trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, which is the correct form (it names the model that did the work; which model ran the seat is not verified here) |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-58b_dispatch.yaml` |
| Review worktree | `.worktrees/58-governance-hardening-row13-review`, detached at the candidate, porcelain empty before and after |
| Scratch | `.worktrees/58-governance-hardening-row13-review-scratch/rev02` (a `--no-hardlinks` LF clone at the candidate, captures) |
| Receipt | `.worktrees/58-governance-hardening-row13-out-c1/RETURN.md` (LF, 249801 bytes, 0 CR) |
| References applied | `CodeReview.md` (§5, rule B); `review-checks.md` (test truthfulness and reviewer counter-mutation, error-code consistency, exception behaviour) |
| XSS / Agent control / profile / POC | Not applicable, as in revision01: a test, one script, two test files and a README; no browser surface, no Agent control path, one seat, no POC |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Boundary | PASS | `49c2c43c..71b0d8ff` touches 5 paths (`index_pins.py`, scripts `README.md`, the three ticket test files), all in the boundary block. `dddc2126..71b0d8ff` touches the same 8 paths as revision01. Nothing under `doc/reviews/` |
| 2 | Part B unchanged | PASS | `git diff 49c2c43c 71b0d8ff -- Workflow.md doc/runbooks/` is empty |
| 3 | Stdlib, `Any`, names | PASS | No new import, no `Any`, no `type: ignore`. The added lines name no company address, no target project, no vendor and no host path |
| 4 | T1 `mypy --strict --python-version 3.11` (two scripts, new test) | PASS | `Success: no issues found in 3 source files`, exit 0 |
| 5 | P1 in the receipt (`-rA`) | PASS | `204 passed, 389 subtests passed`, exit 0. The capture holds the 5 `tolerated under the precedence note` lines |
| 6 | F1, own full suite under the host lock | PASS | `8 failed, 3338 passed, 35 skipped, 6788 subtests passed in 761.97s`, exit 1. All 8 `FAILED` names are among the 12 base names: zero new red. That equals the seat's F1 |
| 7 | `receipt_check.py` (ticket 48) on the receipt | PASS | `receipt defects: 0`, exit 0 |
| 8 | `evidence_gate.py`, three wave-1 tools, `--require-cell P1 T1 M1 F1` | PASS | `cells=6 defects=0`, exit 0, the same text as `E1.txt` (order note S58-13) |
| 9 | Receipt form | PASS | 0 CR in the receipt and in every capture. Every raw block is byte-identical to its capture. Every exit list equals the `exit=` lines in capture order (M1: 35). Every cell names the candidate. Every `tool_digest` equals the sha256 of the blob at the candidate |
| 10 | M1 merged from four clones | PASS | 35 blocks numbered 1–35 without gaps. Each block has exactly one header, `test file`, diff, `pytest tail`, one summary line, `verdict` and `exit=`. Every RED block has exit 1 and a `FAILED`/`SUBFAILED` line; the baselines and mutation 35 have exit 0. Then 5 restore records with empty porcelain: one for all four clones, and one per clone with hashes (`9332804a22db`, `2755ab9a1fb7`, `b3efa3627c62`). Those hashes equal the sha256 of the candidate blobs with CRLF line ends, so each clone was restored to the bytes of its own checkout |
| 11 | `receipt_fence_check.py` runs no git child | PASS | No `subprocess` import or call in the script; it is unchanged in this commit |
| 12 | Every revision01 rule still holds | PASS | All revision01 tests pass in P1. The changed assertions are the ones the rows name: the Chinese negation list (S58-01), `FIELD_NAME` → `mask_field_lists` (S58-02), the precedence pin and `removed()` everywhere (S58-03), the replaced shallow test (S58-04), and the spy test's injected set, a superset of the old one (S58-09). My CM9 control (the 代為 commit injection without a negation) is still red |

### Status of S58-01 to S58-09

| ID | Status | Evidence |
| --- | --- | --- |
| S58-01 | PARTIAL (S58-10) | CM1 rerun is red: `RealTreeTests::test_no_retired_rule_is_live…` lists `Workflow.md:318 (c 審閱者整合 (zh))`; it is also an injection in `INJECTIONS`. `審閱者不得代為 commit 或整合候選` and `整合不由審閱者執行` stay green. Open: the negation after the reviewer exempts the sentence whatever verb it negates (CM10) |
| S58-02 | PARTIAL (S58-11) | CM2 rerun is red, through the real-tree test, and it is an injection. The R4-7 sentence at `modules/spec/workflow-governance.md:204` stays green through `mask_field_lists`. Open: lists followed by `must`/`are` are masked too (CM12, CM13) |
| S58-03 | CLOSED | `PRECEDENCE_REVERSED_OK` is the exact text `與 R4-1、R4-4 衝突處以本修訂為準`. Both CM3 doors, rerun on the tree, are red through `RealTreeTests::test_the_precedence_sentence_is_pinned_by_rule_and_place` (`PRECEDENCE_RULE_MISSING: Revision 04 (R4-1, R4-4) prevails …`). Every case goes through `removed()`/`removed_pattern()`, which raise when the phrase is absent, and a test pins that |
| S58-04 | CLOSED | `GIT_SELECTING_VARIABLES` is the 13 names of `evidence_gate.py`; `GIT_REMOVED_PREFIXES = ("GIT_CONFIG", "GIT_TEST_")`, matched on `name.upper()`. Graft probe from revision01 at the candidate: `--check` exit 0, `--write` exit 0 with `rewrote=0` and the index byte-identical. Was exit 1 `STALE`. An inherited `GIT_SHALLOW_FILE` naming HEAD: exit 0 for `--check` and `--write`, index unchanged. `GIT_QUARANTINE_PATH`, `GIT_REPLACE_REF_BASE`, `GIT_TEST_FOO` and `GIT_CONFIG_PARAMETERS` each give exit 0. The README and the docstring state the list. `receipt_fence_check.py` runs no git (cell 11) |
| S58-05 | CLOSED | `EXPECTED_TOLERATED` holds the 5 files and counts, and the real-tree test asserts equality. P1 runs with `-rA` and shows the report. The seat's mutations 15–18 (a file removed, a wrong count, an empty report, a growing set) are red |
| S58-06 | CARRIED | As routed: the next change of the consistency test |
| S58-07 | ACCEPTED | The control plane accepts "runbooks 目錄" (ticket Revision02 section) |
| S58-08 | CLOSED | CS1 rerun is red: `test_a_self_note_run_on_a_section_with_zero_fences_is_exit_1_no_fences` |
| S58-09 | CLOSED | All six CS2 drops rerun are red, each through `test_each_name_of_the_list_is_removed_one_by_one` with `SUBFAILED(name=…)` for the dropped name. Four of them also go red through the spy test's per-command subtests. The test lists the names itself (`REMOVED_GIT_NAMES`) and compares that set with the script's tuple |

### Question 2: the replaced ticket 48 test

`test_shallow_reported_without_a_shallow_file_is_a_tool_fault` is now `test_an_inherited_shallow_file_changes_nothing` (`tests/test_gate_index_pins.py:669`). That follows the row. The row asks for exactly this rename of the rule, and the STATEMENT names it. The new test is a real pin. It first asserts the premise: under the variable, plain `git rev-parse --is-shallow-repository` says `true`. It then compares the whole `(exit, stdout, stderr)` triple with the run without the variable. If `GIT_SHALLOW_FILE` were kept, the script would see a shallow repository with no shallow file and exit 2, so the comparison would fail (the seat's mutation 32 is red). The old test pinned four things:

- (a) an inherited `GIT_SHALLOW_FILE` is a fault. This is reversed on purpose by the row.
- (b) "git says shallow, but the common directory holds no shallow file" is a fault. This is still pinned by `test_a_simulated_shallow_answer_without_a_shallow_file_is_a_tool_fault` (`:683`), at the `Repo.shallow_boundary` level with a mocked git answer. The variable was the only way to produce this state on a real repository, so an end-to-end CLI test of it is no longer possible.
- (c) `--write` writes nothing when it faults. This is still pinned for faults in general (for example the unborn-HEAD test checks `--check` and `--write` and that the index is unchanged).
- (d) The `--write` mode with the variable set. The new test runs `--check` only. My probe shows `--write` with the variable gives exit 0 and `rewrote=0` on a correct index.

Nothing that should still hold has become unpinned. (d) is a small coverage difference, not a finding.

### Question 3: mutation 35 (names matched case-sensitively)

The equivalence is real on Windows, and not only there. On this host `os.environ` upper-cases every name (probe: after `mock.patch.dict(os.environ, {"git_dir": …, "Git_Test_Y": …})` the keys read back as `GIT_DIR`, `GIT_TEST_Y`), so the mutant sees the same names as the candidate.

On a case-preserving environment I replaced `os.environ` with a plain dict. There the candidate keeps only `KEEP`, while the mutant also keeps `git_dir`, `Git_Graft_File` and `git_test_z`. The existing case tests (`test_the_removed_variables_are_matched_case_insensitively…`, the lower-case and mixed-case names in `test_each_name_of_the_list_is_removed_one_by_one`, `git_test_lower` in the spy test) assert on that dict, so on Linux CI the mutant goes red. It is killed where it can be observed.

Its effect on a verdict is nil on POSIX as well, because git reads its variables by their exact upper-case names there. The case-insensitive match is the rule the ticket writes ("case-insensitive"), and the POSIX run pins it. I accept the marker: it is equivalent on this host and pinned on Linux. No finding.

### Reviewer counter-mutations (scratch clone at the candidate, each restored, porcelain 0; unfiltered output kept per run)

| # | Door | Result | Reading |
| --- | --- | --- | --- |
| 1 | CM1 rerun | RED (8 failed: real-tree LIVE `c`, the unmodified-copy test, the green-negation subtests) | S58-01 door closed |
| 2 | CM2 rerun | RED (8 failed, real-tree LIVE `g1`) | S58-02 door closed |
| 3 | CM3 door 1 rerun (`衝突處不以本修訂為準`) | RED (5 failed, real-tree `PRECEDENCE_RULE_MISSING`) | closed on the production check |
| 4 | CM3 door 2 rerun (`R4-1、R4-4 以外的衝突處`) | RED (5 failed, same) | closed |
| 5 | CS1 rerun | RED (1 failed, the new S58-08 test) | closed |
| 6–11 | CS2 reruns: `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_PREFIX` dropped | RED ×6 (3, 9, 9, 9, 3, 9 failed) | each through `SUBFAILED(name=<that name>)` of the one-by-one test |
| 12 | CM9 control rerun | RED | the sweep still reaches appended text |
| 13 | CM10: `Workflow.md` + "審閱者不得略過閘門，核准後代為 commit 到候選分支。" | GREEN (46 passed) | S58-10 |
| 14 | CM11: `CodeReview.md` + "After approval the reviewer merges the candidate into main, and the submitter does not merge anything." | GREEN | S58-12 |
| 15 | CM12: `CodeReview.md` + "After approval `reviewer` and `submitter` must merge the candidate into main." | GREEN | S58-11 |
| 16 | CM13: `CodeReview.md` + "After approval `reviewer`, `submitter` are the ones who merge the candidate into main." | GREEN | S58-11 |
| — | Probe: rebuild `FIELD_LIST` without each lookahead word in turn and sweep the real tree | Only `from` is needed (dropping it gives the one R4-7 hit at `workflow-governance.md:204`). Dropping `of`, `in`, `at`, `differs`, `are`, `is`, `as`, `must`, `=` or the punctuation branch gives 0 live hits | S58-11 |

### New findings

| ID | Class | Severity | Rule B | File:line | Observation | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| S58-10 | `IMPLEMENTATION_DEFECT` (Revision02 row S58-01: "only when it negates the reviewer as executor") | Low | Not blocking. A gate gap that would let a regression pass, so it is fixed with the next change to this test | `tests/test_governance_consistency.py:91-94` | The after-form `審閱者(本人\|自己)?(不得\|不可\|…)` accepts any following verb. "審閱者不得略過閘門，核准後代為 commit 到候選分支" negates the reviewer as the one who skips the gate, not as executor, and `，` does not split the sentence, so the 代為 commit clause is exempt again. Fix: require an executor verb right after the negation (for example `審閱者(本人\|自己)?(不得\|不可\|不能\|不會)(代為\|整合\|合併\|推送\|落地\|執行\|commit)`), give the before-form the same check, and add CM10 as an injection | CM10 green |
| S58-11 | `IMPLEMENTATION_DEFECT` (Revision02 row S58-02: "exempt only in the field-list form R4-7 uses (read from the review record)") | Low | Not blocking, same reasoning | `tests/test_governance_consistency.py:386-390` (`FIELD_LIST` lookahead) | The lookahead accepts punctuation or any of `from, of, in, at, differs, are, is, as, must, =`. The real tree needs only `from`. With every other word and the punctuation branch removed, the sweep still has 0 live hits. So a list followed by `must` or `are` and then a merge verb is masked, and "`reviewer` and `submitter` must merge the candidate" is green. STATEMENT choice 1 says "a list followed by a verb is a person", but `must merge` and `are the ones who merge` are verbs after the list, and both are masked. Fix: limit the lookahead to what R4-7 uses (`from` and, if needed for the Entry list, a closing bracket or a full stop), and add CM12 and CM13 as injections | CM12, CM13 green; lookahead probe |
| S58-12 | `OUT_OF_SCOPE_HARDENING` | Low | Not blocking | `tests/test_governance_consistency.py:81-86` (`REVIEWER_NEGATED`) | The English markers (`does not (integrate\|merge\|push\|land)`, `not the reviewer`, `differs from`, `superseded`, …) match anywhere in the sentence, the S58-01 shape in English: an unrelated "the submitter does not merge anything" exempts "the reviewer merges the candidate". This corrects my revision01 record, which called the English list executor-only. No Revision02 row covers it; carry it with S58-06 | CM11 green |
| S58-13 | `EVIDENCE_DEFECT` (receipt rule "E1 on the receipt as returned") | Low | Not blocking; the result is unchanged | `.worktrees/58-governance-hardening-row13-out-c1/` | `E1.txt` was written at 04:37:52 local, before the final `M1.txt` (04:45:05), `P9.txt` (04:45:18) and `RETURN.md` (04:45:19). So the seat's E1 did not run on the receipt as returned. My run of the same command on the returned receipt gives the identical `cells=6 defects=0`, exit 0. The STATEMENT also says M1 ran in "a disposable --no-hardlinks clone", while the capture says four. From the pytest durations (1423 s in total, at most 84 s each) and the file times, the four-clone run fits after F1 ended at 04:37:11, so it did not overlap the lock. In the next receipt, run E1 last and describe the clones as the capture does | `stat` of the out dir; own E1 |

### Commands

| # | Command | Exit |
| --- | --- | --- |
| 1 | `git log`/`diff --stat` `49c2c43c..71b0d8ff`; `git diff --name-only dddc2126 71b0d8ff`; `git diff 49c2c43c 71b0d8ff -- Workflow.md doc/runbooks/`; ticket and dispatch read with `git show 56f6cd75:…` | 0; part B diff empty |
| 2 | `git clone --no-hardlinks` (LF, `core.autocrlf=false`) into `rev02/clone`; checkout `71b0d8ff` | 0 |
| 3 | `receipt_check.py` on the receipt; `evidence_gate.py … --tool dispatch_lint.py --tool index_pins.py --tool receipt_fence_check.py --require-cell P1 T1 M1 F1`; `verify_receipt.py` (LF, raw blocks, exit lists, candidate, digests); M1 block checker; `stat` of the out dir | 0; 0; all equal; 35 intact blocks, 5 clean restore records |
| 4 | `cm_rev02.sh`: 16 runs, each with its full test file, restored by `git checkout`, full output in `rev02/cm_rev02_raw/<n>.txt` | 1 ×12, 0 ×4 |
| 5 | `index_pins.py` probes on the revision01 probe repository: plain, `GIT_GRAFT_FILE` (`--check`, `--write`), `GIT_SHALLOW_FILE` (`--check`, `--write`), `GIT_QUARANTINE_PATH`, `GIT_REPLACE_REF_BASE`, `GIT_TEST_FOO`, `GIT_CONFIG_PARAMETERS` | 0 every run; index byte-identical |
| 6 | `case_probe.txt`: `os.environ` read-back on Windows; `git_environment()` on a case-preserving dict, candidate against mutant 35 | candidate keeps `KEEP` only; mutant keeps three more |
| 7 | `fieldlist_probe.txt`: `FIELD_LIST` without each lookahead word, sweep of the real tree | only `from` needed |
| 8 | `python -m mypy --strict --python-version 3.11` on the two scripts and the new test | 0 |
| 9 | host lock `C:/Temp/claude/jas-fullsuite.lock` by `mkdir`, retried every 30 s: waited 20:58:38Z–21:09:16Z while run `jas62-F1` held it (not touched); acquired 21:09:46Z with `owner.txt` = `run_id=58-rev02-initial`. `Get-CimInstance Win32_Process` at acquisition: no pytest or mutation process (two `tail`/`grep` watchers started 2026-10-27 from a checkout outside this repository, and the query itself). Released 21:22:30Z: `owner.txt` checked, the directory renamed to `jas-fullsuite.lock.released-58-rev02-initial-<pid>-<epoch>`, `owner.txt` checked again in the renamed directory, then removed | 0 |
| 10 | `python -m pytest tests -q -p no:cacheprovider` (review worktree, under the lock); `FAILED` names compared with `C:/Temp/claude/jas48_F1_base.txt` (CR removed, `^FAILED` lines) | 1 (8 failed, all base names) |

Raw logs: kept by the reviewer seat in `.worktrees/58-governance-hardening-row13-review-scratch/rev02` (`cm_rev02.txt`, `cm_rev02_raw/1.txt`–`16.txt`, `case_probe.txt`, `fieldlist_probe.txt`, `p9_full.txt`, `e1_mine.txt`, `t1_mine.txt`, `f1_mine.txt`, `procs_at_acquire.txt`, `fullsuite.log`); not committed. Every counter-mutation was judged on its full pytest output (the reason for each red was read in `cm_rev02_raw`). The log file holds extracts only.

Not verified: a POSIX run of the case tests (no Linux host here; the Linux claim rests on reading the tests and on the dict probe); whether git on Windows would honour a lower-case name passed in a child environment (moot, because `os.environ` never yields one); which model ran the seat; whether the seat's first, discarded M1 run differed from the committed one in anything but mutation 35's marker (it is not in the receipt); the order of the seat's M1 slices against other seats' runs on the host.

```review-verdict
candidate: 71b0d8ff99ac17e7527a12587fe610a3cfaf41b9
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/58-rev02-initial
reviewed_at: 2026-11-06
```
