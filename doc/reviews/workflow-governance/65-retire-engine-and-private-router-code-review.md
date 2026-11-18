# REVIEW — ticket 65 Router library retirement (1): the flow engine, the private router, the profile and the router telemetry

## Revision02 initial review

**Verdict: `CHANGES_REQUESTED`.** The retirement itself is clean. Exactly the 45 files of the delete list are deleted, and nothing else is. Every changed or added path is inside the boundary block, and no `forbid` path is touched. All 88 files that ticket 66 retires are byte-identical to the base. Both packages, and all 125 of their modules, import in a fresh isolated interpreter with `langgraph`, `temporalio`, `mcp`, `agents` and `openai` blocked, and no removed module is loaded. The repin rule is retired and nothing else: 11 hand-built admission fixtures give the same result at base and candidate on every non-repin step. CI run 44316784756 is green on both jobs at the candidate. CI installed `requirements-dev.txt` without the four dropped packages, and its failure counts equal the base run's. P9 and E1 pass when I rerun them, and every raw block is byte-identical to its capture.

One finding blocks approval, S65-01. The ticket's acceptance criterion says that `tests/test_wayfinder_gap.py` carries over "every case" of `test_wayfinder_info_gap.py`, "and anything else that file asserts". W5 and W6 also asserted the stage behaviour of the gap rule, and that is not carried. A blocking gap leaves the stage where it is (`next_stage is None`). Owner input re-enters exactly `WAYFINDER` (`next_stage is ProcessStage.WAYFINDER`) and expects exactly the three Wayfinder returns. `WayfinderGapDecision` has no field that can express any of this. The STATEMENT does not name the dropped assertions.

The other findings do not block. S65-02 is an evidence defect: the removed-module import guard accepts a `ModuleNotFoundError` raised for some other module, so my CM7 turns it zero-red. S65-04 is an evidence defect in the receipt. S65-03 is hardening, and S65-05 goes to the control plane.

| Field | Value |
| --- | --- |
| Ticket | `modules/tickets/workflow-governance/65-retire-engine-and-private-router.md`, closure revision02, read with `git show e581b037:…`. It contains the boundary block (6 `modify`, 2 `create`, 45 `delete`, 9 `forbid`) and the "Revision02" section. Revision01 was never reviewed |
| Spec / requirement | workflow-governance Revision 04 R4-1, R4-5; REQ-20261103-043, row "Owner decision 2026-11-18 (router library retirement, "1A 2A 3A 4A")", items (1) and (2) |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-65_dispatch.yaml`, base `c5848465830460188610bd399761e623fc9b8b96`. It still names "revision01"; see S65-05 |
| Candidate | `1e9f73dab720501e38844bd44ec3d8c83383c1b0` on `cp/wave3-65-retire-engine`. `git ls-remote origin` gives the same sha. It is one commit whose parent is `c5848465`, and `c5848465` is an ancestor of `cp/wave3` |
| Commit identity | Author and committer are `Johnny Liu <johnny.liu365@gmail.com>`. The trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` matches the model the STATEMENT names |
| Changed paths | 45 `D`, exactly the delete list (a sorted `diff` of the two lists is empty, and there are no renames). Modified: `ci/README.md`, `library/local_orchestration/control_plane_mutation.py`, `library/local_orchestration/refusal_guidance.py`, `library/workflow_router/README.md`, `library/workflow_router/__init__.py`, `requirements-dev.txt`, and five test files. Added: `library/workflow_router/wayfinder_gap.py` and `tests/test_wayfinder_gap.py`. All are inside `modify`/`create`. No `forbid` path, and no ticket-66 file, is touched. `ci/registered-failures.json` is unchanged |
| Review worktree | `.worktrees/65-retire-engine-and-private-router-review`, detached at the candidate. Porcelain was empty before and after. My first walk-import ran with `-I` and left ignored `__pycache__/` directories there, which I removed afterwards (see "Raw-log note") |
| Receipt | `.worktrees/65-retire-engine-and-private-router-out/RETURN.md` (LF, 57906 bytes, 0 CR) |
| CI run | 44316784756, event `push`, branch `cp/wave3-65-retire-engine`, `headSha` = candidate. `test (linux)` success, `test (windows)` success. Read with `gh run view` only |
| References applied | `AGENTS.md` (both P0 sections); `CodeReview.md` (whole file, §5 rule B); `review-checks.md` (test truthfulness with reviewer counter-mutation, exception behaviour, error-code consistency, missing values) |
| XSS / privileged JS | Not applicable. The change is library and test removal plus one stdlib function, with no browser, DOM or JavaScript surface |
| Secret / provider / external effect | Not applicable. There is no secret, log, provider or webhook. The only external effect is the seat's push of its own branch, which the dispatch authorised |
| Agent control / profile fan-out / POC ancestry | Not applicable. There is one implementer seat, no Agent-control path, and no POC or staging |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Exactly the delete list deleted; everything else inside the boundary; nothing forbidden touched | PASS | `git diff --name-status c5848465 1e9f73da` gives 45 `D`. Sorted, these equal the 45 `delete =` lines of the revision02 ticket. Each of the 13 other paths matches a `modify`/`create` prefix. No path under `skills/`, `template/`, `modules/spec/`, `doc/adr/`, `.claude-plugin/` or `.codex-plugin/`, and not `Workflow.md`, `AGENTS.md` or `CodeReview.md` |
| 2 | Nothing remaining imports a removed module; both packages import cleanly; `__all__` names only existing names | PASS | `git grep` for every removed module path, relative import and public name, outside `doc/` and `modules/`: the only hits are two docstrings (`review_return_consumption.py:4`, `wayfinder_gap.py:11`), the inert path strings `tests/test_control_plane_mutation.py:51-52`, and `tests/test_plugin_payload_boundary.py:383-384` (a string fed to `is_payload_path`; nothing is opened). No `importlib`, `__import__`, `runpy` or `-m` names a removed module. The only `-m` module is `event_runner_main`, which is a bridge module and present. `johnny_router_entry.py` → `johnny_live_cli` imports. `walk.py` (`-I`, fresh interpreter, `pkgutil.walk_packages` over both packages): 125 modules, 0 failures, `__all__` 166 + 259 names all present, 0 removed modules in `sys.modules`. The same walk with `langgraph`/`temporalio`/`mcp`/`agents`/`openai` blocked by a meta-path finder gives the same result |
| 3 | Ticket-66 bridge intact and passing | PASS | All 88 `delete =` paths of ticket 66 (read at `cp/wave3`) exist at the candidate, and `git diff --quiet c5848465 1e9f73da -- <those 88>` holds. In my F1, none of their test files has a failure (cell 12). The bridge test files all ran and passed |
| 4 | `test_wayfinder_info_gap.py` carried case by case | **FAIL: S65-01** | W1–W4 are carried verbatim (contract tests over `WayfinderInfoRequest`/`WayfinderInputGap`). W5 carries outcome `SUSPEND`, `WAIT_FOR_HUMAN` and `WAYFINDER_INPUT_GAP`, and `requires_human_approval` is implied by `WAIT_FOR_HUMAN`. It drops `rule.next_stage is None`. W6 carries `RETRY` and `AUTO_CONTINUE`. It drops `rule.next_stage is WAYFINDER`, `decision.next_stage is WAYFINDER` and `expected_return.router_events == (WAYFINDER_GO, WAYFINDER_NO_GO, WAYFINDER_INFO_REQUIRED)`. The two-round limit is carried and strengthened: a third round and a duplicated second round are refused, and `may_ask_again` is `False` after round two (M01 red). New: out-of-order rounds, widening, and no rounds → `ADVANCE` |
| 5 | Repin retirement removes only that rule | PASS | The diff removes the `_repin_failure` call in `admit_control_plane_mutation`, the four helpers, the constants, `_PIN`, the `hashlib`/`re` imports, the enum member, three `__all__` names and docstring text, and nothing else. `cp_probe.py` runs 11 hand-built fixtures against the base tree and the candidate tree. ticket-only → `INTEGRATED`; mixed → `RULE_AND_SUBJECT_IN_ONE_CHANGE`; wrong door → `CANDIDATE_NOT_CONTROL_PLANE`; nothing → `NOTHING_TO_INTEGRATE`; symlink → `REDIRECTION_ENTRY_NOT_ADMISSIBLE`; journal blocked → `JOURNAL_UNWRITABLE` with no journal line; wrong principal → `PRINCIPAL_NOT_HOST`. All of these are identical at base and candidate, including the offending path, "`main` moved" and the journal outcomes. Only the four policy fixtures differ: base `POLICY_REPIN_STALE`, candidate `INTEGRATED`. At base, an unpinned neighbour is refused once `profile.py` is absent, which confirms the CHANGE_DETECTED rationale. `tests/test_control_plane_mutation.py` passes with 45 tests at the candidate in my baseline (CM4 baseline), and CM4 shows that the retirement is pinned by behaviour, not only by the enum name |
| 6a | `test_adversarial_review_policy` | PASS | Only `test_tara7_review_checks_digest_is_repeated_at_both_policy_pins` is dropped, together with `_PROFILE`, `_PROFILE_TEST`, `hashlib` and the docstring count. It read only the two deleted files. TARA1–TARA6 are unchanged. No remaining pin of `review-checks.md` exists to test |
| 6b | `test_plugin_distribution_payload_manifest` | PASS | Only the three `build_router_graph` assertions are dropped. The fixture still imports `library.workflow_router` from the copied payload with the optional packages blocked, and asserts that it loads from the fixture root |
| 6c | `test_plugin_payload_boundary` | PASS | One declared escape is dropped: `modules/spec/context-load-telemetry.md`. Its only payload reference was the old `library/workflow_router/README.md` telemetry section, which the rewrite removes. The test requires the declared set to equal the escaping set, so the entry had to go, and CM5 proves it: re-adding the reference turns three closure tests red. `contracts.py` is still required (lines 482, 540) |
| 6d | `test_refusal_guidance` | PASS | Three roster entries drop out. They are the `Failure` enums of the deleted `johnny_router_composition.py`, `context_load_report.py` and `telemetry.py`, and the counts move from 51/48 to 48/45. Two `POLICY_REPIN_STALE` rows go as well: the named third-category codes, and the `ControlPlaneMutationFailure` value list. The audit still reads enums from the sources, and CM3 shows that an orphaned guidance entry is still caught. The installer surfaces are untouched |
| 7 | Dev dependencies unused | PASS | `git grep` finds no import of `langgraph`, `temporalio`, `mcp`, `agents` or `openai` in any `.py`. The only word match is the blocked-package tuple at `tests/test_plugin_distribution_payload_manifest.py:83`. The blocked walk in cell 2 imports everything without them. CI "Install development requirements" installed neither of them on either job, and the suite still matched the registered list. Linux 345 failed + 2 errors and Windows 5 failed, the same as the base run 44314843048 |
| 8 | Receipt honest | PASS, with S65-04 | P9 rerun: `receipt_check.py` on `RETURN_noP9.md` gives 5 `[ok]`, 0 defects, exit 0, byte-identical to `P9.txt` apart from its sha line. On `RETURN.md` it gives 6 `[ok]`, exit 0. E1 rerun with the dispatched arguments gives `cells=6 defects=0`, exit 0. `blocks.py`: 0 CR; P1, T1, M1, C1, F1 and P9 raw blocks are each byte-identical to their capture. Recomputed sha256: `P1.txt` 496e11d5…24dfe7, `F1.txt` 713e7c95…01fe382, `M1.txt` dbb051e0…bf6460a. `RETURN_noP9.md` equals `RETURN.md` up to `## P9`. Tool digests equal the sha256 of the scripts at the candidate (`receipt_check.py` 2106b1a3…, as P9.txt states). The seat's F1 names are all among the base names. See S65-04 for the STATEMENT and M1 inaccuracies |
| 9 | Reviewer counter-mutations | 7 run; CM7 zero-red (S65-02) | Table below |
| 10 | Strict type, stdlib, no `Any` | PASS | `mypy --strict --python-version 3.11` on `wayfinder_gap.py`, its test and both `__init__` files gives exit 0. The same on `control_plane_mutation.py` and `refusal_guidance.py` gives exit 0. `wayfinder_gap.py` imports only `collections.abc`, `dataclasses` and `.contracts`. There is no `Any` and no `type: ignore` |
| 11 | Seat CI | PASS | Both jobs `success`. 0 `UNREGISTERED_FAILURE` and 0 `REGISTERED_NOT_FAILING` lines in either log |
| 12 | Reviewer F1 under the host lock | PASS | `python -m pytest tests -q -p no:cacheprovider -rfE` in the review worktree gives 5 failed, 3533 passed, 32 skipped, 7648 subtests passed, exit 1 (1005 s). The 5 failure names are all among the 12 base names in `C:/Temp/claude/jas48_F1_base.txt` (`comm -23` is empty), so there is zero new red. They are the same 5 the seat reported. None is in a ticket-66 test file. Lock: I tried `mkdir` every 20 s while `jas69-run2` held it. I acquired it at 2026-11-18T22:34:43 as `65-rev02-initial-F1`, with `owner.txt` written. At acquisition, `procs_at_acquisition.txt` lists only my own runner, and no other pytest. I released it at 22:51:32: after checking that `owner.txt` still named my run, I renamed the directory to `jas-fullsuite.lock.released-65-rev02-initial-F1-<uuid>` and removed it. No mutation or other pytest of mine ran while I held it |

### Reviewer counter-mutations

These were run in the disposable clone `.worktrees/65-retire-engine-and-private-router-review-scratch/rv`, which was removed after the review, as was the base clone `base` (`git clone --no-hardlinks <main checkout>`, `checkout --detach 1e9f73da…`). Each one ran with the full test file (CM7 being the exception, by design), using `python -m pytest <file> -q -p no:cacheprovider -rfE` with default tracebacks and no output reducer. I read the unfiltered output in `cm/CM*.txt`. Each was restored with `git checkout -- . && git clean -fd`, and porcelain was empty after each. The doors differ from the seat's M01–M04, which were the round limit, `RouterEngine` in `workflow_router.__all__`, a `profile` import in `workflow_router/__init__.py`, and the enum member.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| CM1 | Removed file restored, nothing imports it (the other package) | Restore all six `library/local_orchestration/telemetry_storage/*.py` from the base | red: `test_removed_files_are_absent` ×6. **`test_removed_modules_raise_module_not_found` stays green**: the restored `contracts.py` imports the deleted `library.workflow_router.telemetry`, so the import raises `ModuleNotFoundError` for a different module |
| CM2 | Copy/first-match in the round validator | Drop the `answered_fields ⊆ first round` check | red: `test_rounds_out_of_order_or_widening_are_refused[second_round_answers_a_field_never_asked]`, `ValueError not raised` |
| CM3 | Guidance side, not enum side | Re-add a `POLICY_REPIN_STALE` `RefusalGuidance` entry, with no enum member | red: `ClassificationAuditTests::test_this_repository_is_complete_on_every_covered_surface`, which names `…ControlPlaneMutationFailure::POLICY_REPIN_STALE` as an entry for a code that no longer exists |
| CM4 | Behaviour, not name | In `admit_control_plane_mutation`, refuse a candidate that changes `references/review-checks.md` (reusing an existing failure code) | red: `test_a_policy_edit_is_no_longer_judged_against_pins` and `test_a_policy_edit_repinned_in_both_places_is_admitted`, `REFUSED is not INTEGRATED` |
| CM5 | Payload closure | Append a reference to `modules/spec/context-load-telemetry.md` to `library/workflow_router/README.md` | red: `test_every_reference_that_escapes_is_a_declared_exception`, `test_no_skill_or_command_points_at_our_own_development_material`, `test_the_committed_payload_is_closed` (plus the pre-existing pinned-sha failure) |
| CM6 | Attribute without `__all__`, other package | `build_router_poc_profile = None` at the end of `library/local_orchestration/__init__.py` | red: `test_no_removed_name_is_in_either_all[package=library.local_orchestration, name=build_router_poc_profile]`, `True is not false` |
| CM7 | Wrong-reason pass (overlap-masking) | Restore `library/workflow_router/telemetry_cli.py` only; run `test_removed_modules_raise_module_not_found` alone | **zero red**: 1 passed, 23 subtests passed. The module file is back, yet "importing it raises `ModuleNotFoundError`" holds only because its own `from .telemetry import …` fails. Only the file-absence test catches it (S65-02) |

Separately, the probe for S65-03 ran in its own clone (`pyc`, since removed). I imported `telemetry_storage` at the base with bytecode writing on, then checked out the candidate. Git leaves `telemetry_storage/__pycache__/`. `tests/test_wayfinder_gap.py` then gives 2 failed: the module imports as a namespace package, and the directory exists.

### Findings

| ID | Class | Severity | Blocks? | File:line | Observation | Verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S65-01 | `IMPLEMENTATION_DEFECT` (frozen AC "carries over every case … and anything else that file asserts") | Medium | **Yes** | `library/workflow_router/wayfinder_gap.py:37-44`; `tests/test_wayfinder_gap.py:250-266`; deleted `tests/test_wayfinder_info_gap.py:154-210` at `c5848465` | `WayfinderGapDecision` has `outcome`, `continuation`, `wait_reason` and `may_ask_again`, but no stage or expected-return field. The old W5 asserted that a gap round leaves the stage unchanged (`rule.next_stage is None`). The old W6 asserted that owner input re-enters exactly `ProcessStage.WAYFINDER` (rule and decision) and expects exactly `(WAYFINDER_GO, WAYFINDER_NO_GO, WAYFINDER_INFO_REQUIRED)`; its docstring reads "no other stage is reachable". None of this survives, and STATEMENT item 2 does not name the drop. `ProcessStage` and `RouterEventKind` are both in `contracts.py`, so the rule can carry them | Side-by-side reading of both files at `c5848465` and the candidate; the function's return type and every assertion of the new file | This correction. Add `next_stage: ProcessStage \| None` and `expected_return_events: tuple[RouterEventKind, ...]` to `WayfinderGapDecision`, and assert the three old values in W5/W6 with a mutation that turns them red. If the control plane decides that the stage semantics retired with the engine, that is a ticket change (the AC wording), not a silent drop |
| S65-02 | `EVIDENCE_DEFECT` | Low | No. The file-absence test covers the property today. If it is still open after the correction review, rule B carries it to the next change of this guard, because it would let a regression pass | `tests/test_wayfinder_gap.py:331-335` | `assertRaises(ModuleNotFoundError)` accepts an error raised for any module. A removed module restored with an import of another removed module passes the guard. TDD row 6, "importing a removed module raises `ModuleNotFoundError`", is pinned only by overlap with `test_removed_files_are_absent` | CM7: zero red. CM1: the guard stays green while six files are back | This correction: assert that `caught.exception.name` is the module or one of its removed parent packages |
| S65-03 | `OUT_OF_SCOPE_HARDENING` | Low | No | `tests/test_wayfinder_gap.py:331-335, 367-372` | Git does not remove an ignored `__pycache__/` left in a deleted package directory. `library/local_orchestration/telemetry_storage/` then survives as a directory, imports as an empty namespace package, and both guards go red. It also means "the removed package is unimportable" is not true on such a checkout. The host sets `PYTHONDONTWRITEBYTECODE=1` and CI clones fresh, so neither environment hits it today. The main checkout's `telemetry_storage/` has no `__pycache__` | `pyc` probe clone: 2 failed (`ModuleNotFoundError not raised`, `True is not false`) | Follow-up hardening: judge absence from `git ls-files` or the spec's `origin`, or note the cleanup in `ci/README.md` |
| S65-04 | `EVIDENCE_DEFECT` (receipt accuracy) | Low | No | `tests/test_control_plane_mutation.py:805-806`; `M1.txt` | (a) STATEMENT item 5 says the `stale_policy` helper of `NoMutationOnRefusalTests` "is also dropped". It is still defined, unused, at lines 805-806. (b) The M1 capture labels each tail "(unfiltered)", but it records no pytest command line. Each tail lacks the per-test section headers and traceback bodies that pytest prints by default, and keeps only `E` lines and the final frame. Compare my `cm/CM*.txt` under the same pytest. The RED verdicts can still be checked from the `FAILED`/`SUBFAILED` summary lines, so the conclusions stand, but under `review-checks.md` point 5 the label "unfiltered" is not supported by the capture | Reading the file at the candidate; reading `M1.txt` against my own unfiltered captures | This correction: delete the dead helper or correct the STATEMENT, and record the M1 pytest command |
| S65-05 | `TICKET_DEFECT` (control plane: dispatch identity) | Low | No | `C:/Temp/claude/jas-dispatch/JAS-65_dispatch.yaml:1, 7, cells P1/M1` | The dispatch still names "revision01", and its `ticket_leaf` resolves to the ticket blob in the seat worktree, which is revision01 (the base). Its `p1_tests` and `mutations` do not include the revision02 additions (`tests/test_control_plane_mutation.py`, `POLICY_REPIN_STALE`). The seat compensated: it read revision02 at `e581b037` and added both. The binding is still inferred, not dispatched | `grep revision` on the dispatch; `git show c5848465:<ticket>` differs from `e581b037` in the binding row and the Revision02 section | Control plane: reissue or amend the dispatch per revision for the correction |

### Commands

These ran from the main checkout unless noted. Python was `C:/Temp/claude/jas-venv/Scripts/python.exe` with `PYTHONUTF8=1`. My throwaway scripts lived in the session scratchpad. Clones and captures are in `.worktrees/65-retire-engine-and-private-router-review-scratch`.

- `git rev-parse 1e9f73da^` → `c5848465…`; `git rev-list --count c5848465..1e9f73da` → 1; `git ls-remote origin cp/wave3-65-retire-engine` → candidate; `git merge-base --is-ancestor c5848465 cp/wave3` → yes
- `git diff --name-status c5848465 1e9f73da`, sorted and compared with `sed -n 's/^delete = //p'` of the ticket at `e581b037` → equal (45)
- The ticket-66 delete list (`git show cp/wave3:…/66-retire-bridge.md`): `git cat-file -e` on each of the 88 at the candidate → all present; `git diff --quiet` → identical
- `git grep` sweeps (removed module paths, relative imports, public names, deleted test names, `import_module|__import__|runpy|-m`, the four packages)
- `walk.py <review worktree> removed.txt` and `walk_blocked.py walk.py …` → 125 modules, 0 failures, 0 removed loaded
- `cp_probe.py <scratch>/base` and `cp_probe.py <scratch>/rv` (`-I -B`) → `cp_base.json` and `cp_rv.json`, compared by hand (cell 5)
- Wayfinder edge probe: a gapless round built with `model_construct` gives `SUSPEND`/`WAIT_FOR_HUMAN`. It is not reachable through validated construction (W4), so this is noted only
- `python -m mypy --strict --python-version 3.11 --cache-dir <scratchpad>` on the four T1 files, then on the two changed library modules → exit 0, exit 0
- `gh run view 44316784756 --json …`; `gh run view 44316784756 --log` → 0/0 checker lines and the install lines without the four packages; `gh run list --commit c5848465…` → base run 44314843048; `gh run view 44314843048 --log` → summary lines
- `python -I -X utf8 doc/reviews/workflow-governance/evidence/48/receipt_check.py <out>/RETURN_noP9.md <review worktree>` → exit 0; the same on `RETURN.md` → exit 0
- `python -I -X utf8 skills/johnny-project-takeover/scripts/evidence_gate.py <out>/RETURN.md --repo <review worktree> --candidate 1e9f73da… --tool …/index_pins.py --tool …/receipt_fence_check.py --evidence-root <out> --require-cell P1 --require-cell T1 --require-cell M1 --require-cell F1` (run from the review worktree) → `cells=6 defects=0`, exit 0
- `blocks.py <out>` → every block equal to its capture; `sha256sum <out>/*.txt`
- `cm/run.sh CM1…CM7` → `cm/CM1.txt` … `cm/CM7.txt`
- `locked_f1.py` → `lock_log.txt`, `procs_at_acquisition.txt`, `F1.txt` (cell 12)

### Raw-log note

The files in the scratch directory are unedited tool output: `cm/CM*.txt`, `F1.txt`, `lock_log.txt` and `procs_at_acquisition.txt`. CI was read with `gh run view` only. Nothing was pushed, and no workflow run was triggered. No tracked file was modified anywhere, and every clone was made with `--no-hardlinks`. My first `walk.py` run used `-I`, which ignores the host's `PYTHONDONTWRITEBYTECODE`. It wrote ignored `__pycache__/` directories into the review worktree, under `library/`, `library/local_orchestration/`, `…/project_authority/` and `library/workflow_router/`. They hold bytecode of existing modules only, did not affect F1, and were removed afterwards with `git clean -fdX` in that worktree. I did not touch the seat's worktree, the seat's scratch clone `m1clone`, or ticket 69's worktree.

### Not verified

- A Linux interpreter on this host. Linux behaviour is taken from the CI job, whose counts equal the base run's.
- Whether any target project or installed runtime (`%LOCALAPPDATA%/JohnnyRouter`) still holds an older payload that names the removed CLI. The installer chain was exercised only through the test suite.
- Documents under `doc/` and `modules/` that still name removed modules. They load no code, and ticket 67 sweeps them.
- The seat's M01–M04 were not rerun. My CM1–CM7 are independent of them.

```review-verdict
candidate: 1e9f73dab720501e38844bd44ec3d8c83383c1b0
verdict: CHANGES_REQUESTED
reviewer: seat:ticket-review/65-rev02-initial
reviewed_at: 2026-11-18
```

## Revision02 correction review

**Verdict: `APPROVED`.** Correction 1 (`b185dea9`) closes S65-01, S65-02 and S65-04 as specified.

- **S65-01.** `WayfinderGapDecision` now carries `next_stage: ProcessStage | None` and `expected_return_events: tuple[RouterEventKind, ...]`, both typed from `contracts.py`. W5 and W6 of the deleted file are carried assertion by assertion, and the values match the retired profile exactly. My four counter-mutations on the two new fields all turn red.
- **S65-02.** The removed-module guard now accepts only a `ModuleNotFoundError` that names the module or one of its removed parents. My CM7 rerun, which was zero-red at the initial review, is now red for the intended reason. A new door, CM12, which leaves a namespace parent with a restored submodule, is also red.
- **S65-04.** The `stale_policy` helper is gone. M1 now records each pytest command and keeps pytest's default headers and tracebacks.

The correction touches only three files: the Wayfinder module, its test, and the control-plane mutation test. All three are inside the boundary. By the coordinator's rule, I did not rerun the full suite; the seat's locked F1 at the candidate and CI run 44329348013 cover it. P9 and E1 pass when I rerun them.

Three findings stay open, and none blocks approval under rule B:
- **S65-03** is out-of-scope hardening, carried to a follow-up.
- **S65-05** is the control plane's dispatch-identity defect. It has no effect on exit codes, safety, scope or P0.
- **S65-06** is new hardening: after round two, the owner-input decision still lists `WAYFINDER_INFO_REQUIRED` as an expected return, even though `may_ask_again` is false.

No implementation or evidence defect remains open.

| Field | Value |
| --- | --- |
| Ticket | Unchanged: closure revision02 at `e581b037` |
| Dispatch | `C:/Temp/claude/jas-dispatch/JAS-65_dispatch.yaml`, unchanged since 21:35 and still naming revision01 (S65-05). The coordinator relayed the correction scope |
| Candidate | `b185dea97b0b4035eacbee9dc5c4dbcbed53899d` on `cp/wave3-65-retire-engine`. `git ls-remote origin` gives the same sha. It is one additive commit whose parent is `1e9f73da`; there was no amend or force |
| Commit identity | Author and committer are `Johnny Liu <johnny.liu365@gmail.com>`. The trailer `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` matches the seat model in the STATEMENT |
| Changed paths (`1e9f73da..b185dea9`) | `library/workflow_router/wayfinder_gap.py` (+26/−3), `tests/test_wayfinder_gap.py` (+41/−1), `tests/test_control_plane_mutation.py` (−3). All are inside `create`/`modify`. Nothing forbidden is touched, and no ticket-66 file |
| Review worktree | `.worktrees/65-retire-engine-and-private-router-review`, detached at `b185dea9`. Porcelain, including ignored files, was empty before and after |
| Receipt | `.worktrees/65-retire-engine-and-private-router-out/RETURN.md` (69131 bytes, LF, 0 CR). Its candidate is `b185dea9`, as is every cell's |
| CI run | 44329348013, event `push`, `headSha` = candidate. `test (linux)` success, `test (windows)` success. 0 `UNREGISTERED_FAILURE` and 0 `REGISTERED_NOT_FAILING` lines. Passed counts are 3279 on Linux and 3539 on Windows, each 2 more than at `1e9f73da` (the two new tests). Failures are unchanged: Linux 345 + 2 errors, Windows 5 |
| References applied | As in the initial review, plus `CodeReview.md` §5 rule B for this correction review |
| XSS / secrets / Agent control / profile / POC | Not applicable, for the same reasons as the initial review |

### Cell results

| # | Check | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Correction touches only boundary paths | PASS | `git diff --stat 1e9f73da b185dea9` lists exactly the three files above. Each is under `library/workflow_router/` or `tests/`. The full suite was not rerun: the change is limited to the Wayfinder module, its test and the control-plane mutation test, which is the coordinator's no-rerun case |
| 2 | S65-01: W5 of `c5848465:tests/test_wayfinder_info_gap.py:154-178`, case by case | PASS | `decision.outcome is SUSPEND`, `continuation is WAIT_FOR_HUMAN` and `wait_reason is WAYFINDER_INPUT_GAP` are carried in `test_a_blocking_gap_is_a_declared_owner_wait`. `rule.requires_human_approval` is implied by `WAIT_FOR_HUMAN`. `rule.next_stage is None` is now `assertIsNone(decision.next_stage)` in `test_a_blocking_gap_leaves_the_stage_unchanged`, for one and for two rounds. That test also asserts that the expected return is `(OWNER_INPUT_PROVIDED,)`, and this equals the retired profile's `_PolicyRoute(WAYFINDER, WAYFINDER_INFO_REQUIRED, …, (OWNER_INPUT_PROVIDED,))` (`c5848465:library/workflow_router/profile.py:266-272`) |
| 3 | S65-01: W6 of `c5848465:…:180-210`, case by case | PASS | `outcome is RETRY` and `continuation is AUTO_CONTINUE` are carried in `test_owner_input_reenters_wayfinder`. `rule.next_stage is WAYFINDER` and `decision.next_stage is WAYFINDER` become `assertIs(decision.next_stage, ProcessStage.WAYFINDER)`. `rule.expected_return.router_events == (WAYFINDER_GO, WAYFINDER_NO_GO, WAYFINDER_INFO_REQUIRED)` becomes an `assertEqual` on `expected_return_events`, with the same three in the same order. Both are in `test_owner_input_reenters_exactly_the_wayfinder_stage`, for one and for two rounds. The values equal the profile route at `profile.py:274-285` and the transition rule at `:645-657` (`next_stage=ProcessStage.WAYFINDER`). The rule and the decision collapse into one function result, which leaves nothing uncarried |
| 4 | S65-02 | PASS | `tests/test_wayfinder_gap.py:361-374` asserts `caught.exception.name` is in {the module, each removed parent package}. CM7r and CM12 are red (table below) |
| 5 | S65-03 | CARRIED | STATEMENT item 0 records it as out-of-scope hardening, with its reason |
| 6 | S65-04 | PASS | `grep -c stale_policy tests/test_control_plane_mutation.py` gives 0. `M1.txt` has a `--- command: python -m pytest <file> -q -rfEs -p no:cacheprovider` line for each mutation, and the full per-test section headers and traceback bodies. The seat adds M05 (owner-input `next_stage` set to `None`) and M06 (my CM7), and both are red |
| 7 | Receipt | PASS | P9 rerun: `receipt_check.py` on `RETURN_noP9.md` gives 5 `[ok]`, 0 defects, exit 0. On `RETURN.md` it gives 6 `[ok]`, exit 0. E1 rerun with the dispatched arguments, `--candidate b185dea9…`, run from the review worktree, gives `cells=6 defects=0`, exit 0. `blocks.py`: P1, T1, M1, C1, F1 and P9 raw blocks are each byte-identical to their capture. Recomputed sha256: `P1.txt` 2d59f2ef…cd7539d2, `M1.txt` 28c71743…dfd0405, `F1.txt` b40e51aa…d8eef04. `RETURN_noP9.md` equals `RETURN.md` up to `## P9` |
| 8 | Seat F1 at the candidate | PASS | 5 failed, 3535 passed, 32 skipped, exit 1. The 5 names are a subset of the base names, so there is zero new red. The lock log names one foreign pytest at acquisition, `tests/test_gate_evidence.py` (ticket 69, PIDs 36956/40296), and STATEMENT item 12 names it as the dispatch requires |
| 9 | Strict type | PASS | `mypy --strict --python-version 3.11` on the four T1 files gives exit 0. Over `tests/test_control_plane_mutation.py` it reports 4 unused `type: ignore` comments (lines 740, 744, 832, 841). Those comments come from older tickets, not this one: the file holds 7 `type: ignore` both at `c5848465` and at the candidate, the ticket's diff adds none, and the file is outside T1 |
| 10 | Wayfinder function, other cases | PASS (S65-06 noted) | No rounds still gives `ADVANCE` with `next_stage` `None` and `expected_return_events` `()` (dataclass defaults). This case is new and has no counterpart in the old file. After round two, the owner-input decision expects `WAYFINDER_INFO_REQUIRED` while `may_ask_again` is `False` (S65-06) |

### Reviewer counter-mutations (correction)

These ran in the disposable clone `rv2` (`git clone --no-hardlinks <main checkout>`, detached at `b185dea9`), with a `base2` clone at `c5848465` used as the source of restored files. Both were removed afterwards. Baseline: `tests/test_wayfinder_gap.py` plus `tests/test_control_plane_mutation.py` gave 61 passed, 628 subtests passed. Commands were `python -m pytest <target> -q -p no:cacheprovider -rfE` with default tracebacks and no reducer, read unfiltered in `cm/CM7r.txt` and `cm/CM8.txt`–`cm/CM12.txt`. Each was restored with `git checkout -- . && git clean -fd`, and porcelain was empty after each. CM8–CM11 differ from the seat's M05, which set the owner-input `next_stage` to `None`.

| ID | Door | Mutation | Result |
| --- | --- | --- | --- |
| CM7r | Wrong-reason pass (rerun of CM7) | Restore `library/workflow_router/telemetry_cli.py`; run `test_removed_modules_raise_module_not_found` alone | red: `SUBFAILED(module='library.workflow_router.telemetry_cli')`, `'library.workflow_router.telemetry' not found in {'library.workflow_router.telemetry_cli'}`. Zero red at the initial review; now red for the intended reason |
| CM8 | Wrong stage, not absent stage | Owner input re-enters `ProcessStage.ARCHITECTURE` | red: `test_owner_input_reenters_exactly_the_wayfinder_stage[rounds=1]` and `[rounds=2]` |
| CM9 | Wait contract emptied | Blocking gap `expected_return_events` set to `()` | red: `test_a_blocking_gap_leaves_the_stage_unchanged[rounds=1]` and `[rounds=2]` |
| CM10 | First match / subset | Drop `WAYFINDER_INFO_REQUIRED` from `WAYFINDER_RETURN_EVENTS` (GO and NO_GO only) | red: `test_owner_input_reenters_exactly_the_wayfinder_stage[rounds=1]` and `[rounds=2]` |
| CM11 | Stage moves on a wait | Blocking gap `next_stage` set to `ProcessStage.WAYFINDER` | red: `test_a_blocking_gap_leaves_the_stage_unchanged[rounds=1]` and `[rounds=2]` |
| CM12 | Namespace parent plus restored submodule | Recreate `library/local_orchestration/telemetry_storage/` with only `composition.py` (no `__init__`) | red: the package imports as a namespace (`ModuleNotFoundError not raised`), and `…composition` fails naming `…telemetry_storage.contracts`, which is not in the allowed set |

### Findings (status after correction 1)

| ID | Class | Severity | Status | Blocks? | File:line | Observation / verification | Route |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S65-01 | `IMPLEMENTATION_DEFECT` | Medium | **Closed** | — | `library/workflow_router/wayfinder_gap.py:40-58, 84-100`; `tests/test_wayfinder_gap.py:261-296` | Every W5/W6 assertion is carried (cells 2–3), with values equal to the retired profile. CM8–CM11 are red | — |
| S65-02 | `EVIDENCE_DEFECT` | Low | **Closed** | — | `tests/test_wayfinder_gap.py:361-374` | The guard checks `exception.name`. CM7r and CM12 are red | — |
| S65-03 | `OUT_OF_SCOPE_HARDENING` | Low | Carried | No (hardening) | `tests/test_wayfinder_gap.py` removed-module guards | Unchanged: a leftover ignored `__pycache__/` in a deleted package directory makes both guards falsely red. Neither the host nor CI hits it | Follow-up hardening ticket |
| S65-04 | `EVIDENCE_DEFECT` | Low | **Closed** | — | `tests/test_control_plane_mutation.py`; `M1.txt` | The helper is removed; M1 records commands and keeps full tracebacks (cell 6) | — |
| S65-05 | `TICKET_DEFECT` (dispatch identity) | Low | Open, owned by the control plane | No. Under rule B it changes no exit-code classification, breaks no safety or scope boundary, and violates no P0 | `C:/Temp/claude/jas-dispatch/JAS-65_dispatch.yaml:1` | The dispatch still reads "revision01". The receipt binds revision02 at `e581b037`, so the candidate's authority is readable | Control plane |
| S65-06 | `OUT_OF_SCOPE_HARDENING` | Low | New | No (hardening) | `library/workflow_router/wayfinder_gap.py:84-91`; `tests/test_wayfinder_gap.py:282-296` | After round two, the owner-input decision lists `WAYFINDER_INFO_REQUIRED` as an expected return while `may_ask_again` is `False`, and the function refuses the third round that return would lead to. The two fields of one decision disagree. Behaviour is fail-closed, and the old profile had no round awareness either. The test pins this for `rounds=2`, and the STATEMENT names it as deliberate | Follow-up hardening: drop `INFO_REQUIRED` from the expected returns when `may_ask_again` is false, or document the precedence |

### Commands (correction)

- `git rev-parse b185dea9^` gives `1e9f73da`. `git ls-remote origin cp/wave3-65-retire-engine` gives the candidate. `git diff --stat` and `git diff 1e9f73da b185dea9`
- `git show c5848465:library/workflow_router/profile.py`, lines 262-290 and 630-660 (the expected-return table and the transition rules)
- `gh run view 44329348013 --json …` and `gh run view 44329348013 --log`: checker lines and summary counts
- `receipt_check.py` on `RETURN_noP9.md` and on `RETURN.md`, then `evidence_gate.py … --candidate b185dea9…`, then `blocks.py <out>`
- `python -m mypy --strict --python-version 3.11 --cache-dir <scratchpad>` on the four T1 files; then the same set plus `tests/test_control_plane_mutation.py` (cell 9)
- `cm/mut.py rv2 CM8…CM11` and `cm/run.sh` for CM7r–CM12, giving `cm/CM7r.txt`, `cm/CM8.txt`–`cm/CM12.txt`

### Raw-log note (correction)

The `cm/CM7r.txt` and `cm/CM8.txt`–`cm/CM12.txt` captures are unedited pytest output. CI was read with `gh run view` only. Nothing was pushed, and no run was triggered. No tracked file was modified. Both clones were made with `--no-hardlinks` and were removed afterwards. The host lock was not taken, because no full suite was needed. I did not touch the seat's worktree or ticket 69's worktree.

### Not verified (correction)

- A reviewer full suite at `b185dea9`. It was not required for this file set. The seat's locked F1 and both CI jobs cover it, and my targeted baseline over the two changed test files was green.
- Linux behaviour of the two new tests, beyond the CI Linux job's +2 passed.

```review-verdict
candidate: b185dea97b0b4035eacbee9dc5c4dbcbed53899d
verdict: APPROVED
reviewer: seat:ticket-review/65-rev02-correction
reviewed_at: 2026-11-18
```

## Seat token use (readiness criterion 5)

Host-reported usage per seat, summed per unique message id, compared with the expectation the owner confirmed on 2026-11-18 ("1A"). The same values go into the receipt as `USAGE` cells once ticket 69 is integrated.

| Seat | Model | input | cache write | cache read | output | processed | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `seat:implementation-standard/65-impl` | claude-sonnet-5-5 | 292 | 461156 | 22802522 | 88467 | 23263970 | WITHIN |
| `seat:ticket-review/65-rev02` | claude-opus-5-5 | 254 | 756021 | 23390088 | 91014 | 24146363 | OVER_PROCESSED |

The implementation seat covers revision01 (returned `CHANGE_DETECTED`), revision02 and correction 1. The review seat covers the initial and the correction review. It is over its processed expectation by 1146363 tokens (5.0 %), because one seat held both reviews and re-read its first context for the second; the two reviews together stay below two expectations. Over is explained here and does not block integration (owner decision 2026-11-18 "1A").
