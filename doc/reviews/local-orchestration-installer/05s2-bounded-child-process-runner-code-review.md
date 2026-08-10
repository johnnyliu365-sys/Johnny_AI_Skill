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
