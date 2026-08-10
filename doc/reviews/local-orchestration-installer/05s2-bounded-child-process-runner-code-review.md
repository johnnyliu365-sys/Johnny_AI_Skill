# Ticket 05S2 Bounded Child-Process Runner Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05s2-bounded-child-process-runner` / `CLOSURE-LOCAL-INSTALL-T05S2-01` / P1-P4 and T1-T4 |
| Reviewed baseline | `622e78d950a2d35cacf4e5d49fe27fdf7e58e6a1` |
| Implementation | `52d74554c930a53ee2b84838d0ee31afde9f6b80` |
| Docs-only handoff | `72ccfaab44429749c61a77177567deb81d7f29dc` |
| Branch / owner | `codex/implementation-bounded-child-process-runner-05s2` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Review result | `CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED` |

The submitted ancestry is exact: `622e78d -> 52d7455 -> 72ccfaa`.
The implementation commit adds only the five authorized Python files and the
handoff commit changes only `doc/WorkProgressReport.md`. Both worktrees were
clean and `git diff --check` passed. Review execution used a fresh `git archive`
export and never modified the implementation worktree.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused command | PASS: `python -B -m unittest tests.test_bounded_child_process_runner -v`, 5/5. |
| Full command | PASS: `python -B -m unittest discover -s tests -v`, 182/182. |
| Strict typing / compile | PASS: strict mypy checked 91 source files with an external temporary cache; all 91 Python files compiled in memory. |
| Source / scope | PASS: no `Any`, `type: ignore`, command-string execution, `shell=True`, raw stdout/stderr result or rejected-05S source reuse. |
| Physical launch matrix | PASS: the submitted tests replayed real success, nonzero, timeout, WinError 2, WinError 5 and FileNotFoundError-class WinError 206 as distinct named outcomes. |
| Extended timeout probe | PASS runtime behavior: after a 100 ms timeout, an independent 2.3 second wait still found no completion sentinel and exact teardown succeeded. |
| Physical working-directory escape | FAIL: replacing the lease's `profile` directory with a real Windows junction caused request validation to pass. A real child returned `SUCCESS` and wrote `outside` through relative path `escaped.txt` into the external junction target. |
| Malformed executable boundary | FAIL: `AbsoluteExecutable` accepted `C:\\ticket05s2\\bad\0.exe`; `run` then leaked `ValueError: embedded null character` instead of rejecting before effects or returning a finite typed result. |
| Git / residue | PASS: both worktrees stayed clean; review export, caches, external junction/target, late sentinel and `johnny-stage-env-*` roots were absent after cleanup. |

## Closure mapping

| Item | Result | Independent result |
| --- | --- | --- |
| `P1` / `T1` | FAIL | Relative executables and malformed arguments are rejected, but an embedded-NUL absolute executable crosses the contract and produces an untyped runtime exception. |
| `P2` / `T2` | FAIL | Normal exact overlay/cwd and ambient isolation pass, but the live ownership check follows a directory junction and permits a child effect in an external working directory. |
| `P3` / `T3` | PARTIAL / TICKET DEFECT | The six frozen normal outcomes and physical WinError mapping pass. The started-child timeout cleanup uses an unbounded second wait and the frozen union has no termination-failure state if kill/wait fails. |
| `P4` / `T4` | PASS with evidence caveat | Invocation and started truth are named and raw output is absent. The committed no-late-sentinel assertion observes only 0.2 seconds although the fixture waits 2 seconds; independent extended replay passes but the committed assertion is not truth-preserving. |

## CodeReview.md mandatory checks

- **Clear strong types:** FAIL only at the executable NUL boundary and the
  missing typed started-child termination-failure state. Other request/result
  models are named, frozen and strictly validated.
- **Existing coding conventions:** PASS. Python 3.11, Pydantic strict models,
  `pathlib` and `unittest` match the integrated staging support.
- **Logic correctness:** FAIL CR-120/CR-121. A lexical owned-path comparison
  plus `Path.is_dir()` is not a physical ownership proof, and `Popen` can leak
  a non-`OSError` malformed-input exception.
- **Edge cases:** FAIL the physical reparse substitution, executable NUL and
  finite termination-failure closure. Physical normal launch classes pass.
- **Security / performance:** FAIL isolation: a child effect can be redirected
  outside its lease root through a junction. No unrelated performance defect
  was found.
- **Test coverage / smoke:** FAIL T2/T4 despite green focused/full suites. No
  working-directory reparse case exists and the late-sentinel wait is shorter
  than the fixture's delayed write.
- **Dependency reasonableness:** PASS. No dependency or production-library file
  changed.
- **Project specification:** FAIL until P1/P2 are fixed and P3 is refrozen to
  represent termination failure. 05S3 remains dependency-waiting.
- **Path-prefix/reparse boundary (defect class 1):** FAIL. The exact lexical
  child is accepted even after physical redirection to an external target.
- **Exception/result consistency (defect classes 5/6):** FAIL. Embedded NUL
  leaks `ValueError`; started-child kill/wait failure has no finite result.
- **Test truthfulness (defect class 7):** FAIL the committed late-sentinel
  timing and missing physical junction case.

## Batched findings

1. **CR-120 - `IMPLEMENTATION_DEFECT`, P2/T2.**
   `tests/staging/process_runner/contracts.py:85-94` checks membership by the
   stored locator and then calls `is_dir()`, which follows a junction. The
   runner at `runner.py:35-42` consequently launches in that redirected cwd.
   Independent replay produced `SUCCESS` and external bytes `outside`. Before
   launch, the live root, marker, cwd and all overlay paths must be revalidated
   as exact non-reparse objects beneath the same owned lease.
2. **CR-121 - `IMPLEMENTATION_DEFECT`, P1/T1.**
   `contracts.py:20-29` does not reject NUL in the executable locator. The model
   accepts the value and `subprocess.Popen` raises `ValueError`, outside the
   finite observation union and after boundary admission. Reject malformed
   executable locators before any process call and add the physical assertion.
3. **CR-122 - `EVIDENCE_DEFECT`, T3/T4.**
   `fixture_child.py:135` delays completion for 2 seconds, but
   `tests/test_bounded_child_process_runner.py:128` checks only 0.2 seconds
   after return. A runner that returns without terminating the child can pass
   this assertion and write later. The test must observe beyond the scheduled
   write or prove the exact process handle is terminated and reaped.
4. **CR-123 - `TICKET_DEFECT`, P3/T3.**
   The control-plane freeze required a finite discriminated union and a bounded
   timeout, but omitted the state and secondary bound needed when `kill()` or
   post-kill `wait()` fails. `runner.py:48-51` therefore performs an unbounded
   wait and can leak an exception or child. The ticket must be refrozen with an
   exact termination-failure result and finite cleanup budget before any
   correction is authorized; this omission belongs to the control plane, not
   to implementation scope inference.

## Conclusion

`CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`. The normal runner behavior
is materially better isolated than the rejected combined staging attempt, but
P1/P2 and the finite P3 closure are not complete. Per the 05S2 loop boundary,
this review does not authorize an automatic correction, new branch/worktree,
merge, 05S3 dispatch, live Codex action, target-project write, push, release or
deployment. Allocation `aln_local_orchestration_install_05s2_20260811` is
released and receipt `rcpt_local_orchestration_install_05s2_20260811` is
closed against replay. Submitted commits remain immutable review evidence.

## Owner-authorized disposition

Owner override `OVR-LOCAL-INSTALL-T05S2-REFREEZE-20260811-01` accepts the
control-plane responsibility for CR-123 and refreezes only CR-120..CR-123 as
`CLOSURE-LOCAL-INSTALL-T05S2-02`. It authorizes one additive correction on the
same task, worktree and branch at submitted HEAD `72ccfaa`; revision-01 commits
and this review remain immutable. The next review is final for this override:
any blocker stops without another correction, branch/worktree replacement or
05S3 dispatch.

## Revision-02 final independent review

| Field | Value |
| --- | --- |
| Closure | `CLOSURE-LOCAL-INSTALL-T05S2-02`; P1-P4 / T1-T4 |
| Reviewed baseline | Control `a5ebc98f40f199b86a7ad43941aa0ffafc55e457`; submitted HEAD `72ccfaab44429749c61a77177567deb81d7f29dc` |
| Correction / handoff | `34babbd2ff200715c350b4a46c99d47db84de7e8` / `c324c52669cfa16c57433e0f0cf14ee2b00b0d69` |
| Final result | `CHANGES_REQUESTED / FINAL_REVIEW_STOPPED / TICKET_DEFECT` |

The ancestry is exact and additive: `72ccfaa -> 34babbd -> c324c52`.
Correction scope is exactly the four authorized Python files; the later commit
changes only `doc/WorkProgressReport.md`. Both worktrees remained clean and
only the original control and implementation worktrees exist.

### Revision-02 verification

| Check | Result / evidence |
| --- | --- |
| Fresh export | PASS after using ZIP to preserve the repository's Unicode paths; no implementation-worktree write. |
| Focused / full | PASS: 10/10 focused and 187/187 full tests. |
| Strict type / compile | PASS: strict mypy and in-memory compile across 91 Python files; external mypy cache removed after review. |
| Scope / source / diff | PASS: authorized file sets, additive ancestry, P0 source sentinel and `git diff --check`. |
| CR-120 / CR-121 | PASS: physical root/cwd/five-child/overlay junctions and marker tamper stop before the process port; NUL executable is rejected at construction. |
| CR-122 / CR-123 | PASS: committed wait exceeds the fixture late-write deadline; normal bounded reap and all three named kill/reap failure results pass. |
| Residue | PASS: zero `johnny-stage-env-*` roots, junction targets, late sentinels and repository cache directories. |
| Started-child wait-error reverse probe | **FAIL:** the first `wait()` raised `OSError`, not `TimeoutExpired`; kill succeeded, bounded reap returned 137, and the runner returned `TIMEOUT_AFTER_START` (`kills=1`, `waits=2`). |

### CR-124 — `TICKET_DEFECT`, P3/T3

`tests/staging/process_runner/runner.py:87-92` handles both
`subprocess.TimeoutExpired` and a first-wait `OSError` by calling
`_terminate_after_timeout`. The latter path can therefore return confirmed
`TIMEOUT_AFTER_START` even though no timeout was observed. This violates result
truth and the port's documented exception surface. CodeReview.md defect classes
5, 6 and 7 apply: the TDD matrix omitted the first-wait error case, and the
frozen union has no exact started-child observation-failure state. This is a
ticket-design omission rather than authority for the implementation owner to
invent a new result.

### Final conclusion

`CHANGES_REQUESTED / FINAL_REVIEW_STOPPED`. The one correction authorized by
`OVR-LOCAL-INSTALL-T05S2-REFREEZE-20260811-01` is consumed. Per the explicit
loop boundary, this review does not dispatch another correction, create or
replace a branch/worktree, integrate 05S2, or dispatch 05S3. No push, release,
deployment, live Codex mutation or target-project access occurred.
