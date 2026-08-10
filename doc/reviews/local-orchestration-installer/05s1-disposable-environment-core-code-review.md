# Ticket 05S1 Disposable Environment Core Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05s1-disposable-environment-core` / `CLOSURE-LOCAL-INSTALL-T05S1-01` / E1-E4 and T1-T4 |
| Reviewed baseline | `f88e10f73f9014fb276d99974eaf1a2074c9a7d0` |
| Implementation | Initial `e0898cdca76c360713bef35b1848c0b8b8bd3681`; owner-scoped correction `41d5ce4c4c90b0e84c9d756edc81c21ae33b1e27` |
| Docs-only handoff | Initial `ecce06ae8ff46ca770770375c166ba503bb7f17e`; final `e1087d32e52f3a86a79dd08ad95700e59d731d66` |
| Branch / owner | `codex/implementation-disposable-environment-core-05s1` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Review result | `APPROVED / INTEGRATION_AUTHORIZED` after the single owner-scoped correction |

The submitted ancestry is exact: `f88e10f -> e0898cd -> ecce06a`. The
implementation commit adds only the four authorized Python files; the handoff
commit changes only `doc/WorkProgressReport.md`. Both worktrees were clean and
`git diff --check` passed. This review used a disposable `git archive` export
and did not modify the implementation worktree.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused command | PASS: `python -B -m unittest tests.test_disposable_environment_core -v`, 4/4. |
| Full command | PASS: `python -B -m unittest discover -s tests -v`, 176/176. |
| Strict typing | PASS: Python 3.11, `mypy --strict --explicit-package-bases --no-incremental`, 86 source files, repository-external cache. |
| Compile / source guard | PASS: all 86 exported Python files compiled in memory; no `Any`, `type: ignore`, subprocess, shell execution or broad `shutil.rmtree` in the 05S1 scope. |
| Git / residue | PASS: control and implementation worktrees stayed clean; repository cache readback and final `johnny-stage-env-*` root readback were empty. |
| Physical child escape | PASS: a real Windows child junction returned `BLOCKED / CHILD_ESCAPE`, preserved the external sentinel bytes, and allowed exact cleanup after the junction was removed. |
| Physical root reparse | FAIL: PowerShell reported `LinkType=Junction` and `Attributes=Directory, ReparsePoint`, while Python 3.11.9 `Path.is_symlink()` returned `False`. Teardown followed the junction far enough to read the external marker and returned `BLOCKED / CHILD_ESCAPE`, not `ROOT_REPARSE`. |

## Closure mapping

| Item | Result | Independent result |
| --- | --- | --- |
| `E1` / `T1` | PASS | Distinct owners produced distinct direct OS-temp roots; malformed and replayed owners were rejected before new effects. |
| `E2` / `T2` | PASS | The overlay contains exactly the six fixed owned paths and parent environment values remain unchanged. |
| `E3` / `T3` | FAIL | Marker mismatch, absence, child escape, exact removal and replay work, but the real Windows root-reparse case is not recognized at the root boundary and the committed test proves only a mocked `Path.is_symlink()` branch. |
| `E4` / `T4` | PASS | The two frozen initialization faults leave no new roots and preserve unrelated sibling bytes. |

## CodeReview.md mandatory checks

- **Clear strong types:** PASS. The boundary uses named frozen models, enums and
  finite result unions; no optional effect port or unchecked dynamic object
  crosses inward.
- **Existing coding conventions:** PASS. Python 3.11, Pydantic strict models,
  `pathlib` and `unittest` match the repository's current test-support style.
- **Logic correctness:** FAIL only for the E3 root-reparse classification and
  pre-read boundary described in CR-118.
- **Edge cases:** FAIL closure because the physical root junction case is not
  implemented or tested truthfully. Other frozen invalid, replay, marker,
  cleanup and child-escape cases pass.
- **Security / performance:** FAIL isolation at the root-reparse boundary: the
  implementation reads a marker through an unrecognized junction before
  returning a block. No deletion escaped the root and no material performance
  concern was found.
- **Test coverage / smoke:** FAIL E3 despite green focused/full commands. The
  root-reparse assertion replaces `Path.is_symlink` and does not exercise the
  Windows filesystem behavior it claims.
- **Dependency reasonableness:** PASS. No dependency or production-library file
  changed.
- **Project specification:** FAIL until E3 is independently satisfied; 05S2
  remains dependency-waiting.
- **Path-prefix boundary (CodeReview.md section 2.1 class 1):** PASS. Root parent
  comparison resolves and compares the exact OS-temp parent; no adjacent-prefix
  acceptance was observed.
- **Authority bypass (class 3):** PASS within the frozen closure. Invalid and
  replayed owners and marker mismatches block. Foreign-state hardening is
  explicitly outside 05S1 and was not used to expand this review.
- **Test truthfulness (class 7):** FAIL E3. The mock proves the conditional body,
  not that a Windows reparse point reaches it.

## Batched findings

1. **CR-118 - `IMPLEMENTATION_DEFECT`, E3/T3.**
   `tests/staging/environment_core/environment.py:95-108` treats only
   `Path.is_symlink()` as `ROOT_REPARSE`. On the supported Python 3.11 Windows
   runtime, a real directory junction is a reparse point but
   `Path.is_symlink()` is false. The allocator therefore reads the marker
   through the junction and misclassifies the root as `CHILD_ESCAPE`. E3/T3
   require the root reparse to be refused at the exact root boundary with the
   matching finite reason.
2. **CR-119 - `EVIDENCE_DEFECT`, E3/T3.**
   `tests/test_disposable_environment_core.py:93-98` monkeypatches
   `Path.is_symlink`; it never creates or observes a physical reparse point.
   The handoff discloses a symbolic-link privilege failure but overlooks a
   normal Windows junction, which the independent account created without that
   privilege. Its statement that production checks the actual reparse state
   before deletion is therefore not replayable.

## Control-plane metadata correction

The dispatched ticket omitted the explicit `Implementation language` table
field required by `Workflow.md` section 9.3, although its approved SPEC and
authorized paths already fixed Python 3.11. This review records the omission as
a resolved `TICKET_DEFECT` and adds the missing field without changing closure
E1-E4/T1-T4 or granting implementation authority.

## Conclusion

`CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED`. Per the owner-approved 05S1
loop boundary, this initial blocking review stops the lane. There is no
automatic correction, replacement branch/worktree, merge, 05S2 dispatch, live
Codex action, target-project write, push, release or deployment. The submitted
implementation and handoff commits remain immutable review evidence.

## Post-review owner disposition

The project owner explicitly authorized one bounded continuation after this
terminal result. Override `OVR-LOCAL-INSTALL-T05S1-REPARSE-20260811-01` retains
the same ticket, closure, implementation owner, worktree, branch, allocation
and receipt. It permits only CR-118/CR-119 correction: early physical Windows
reparse detection and a real root-junction test. This disposition does not
change the review result above, approve the submitted commits, start 05S2 or
authorize another correction after the next independent review.

## Final owner-scoped correction review

The final submitted ancestry is exact:
`ecce06a -> 41d5ce4 -> e1087d3`. The correction commit changes only
`tests/staging/environment_core/environment.py` and
`tests/test_disposable_environment_core.py`; the final handoff changes only
`doc/WorkProgressReport.md`. Both worktrees were clean and `git diff --check`
passed. No new branch or worktree was created.

| Check | Independent result |
| --- | --- |
| Focused command | PASS: an exported checkout ran `python -B -m unittest tests.test_disposable_environment_core -v`, 5/5. |
| Full command | PASS: the same export ran `python -B -m unittest discover -s tests -v`, 177/177. |
| Strict typing / compile | PASS: strict mypy checked 86 source files with an external temporary cache; all 86 Python files compiled in memory. |
| Physical root reparse | PASS: the committed test created a real Windows junction, observed `FILE_ATTRIBUTE_REPARSE_POINT`, proved zero marker-read calls, returned `BLOCKED / ROOT_REPARSE`, preserved the junction and external sentinel, then removed only its test-owned artifacts. |
| Source / scope | PASS: no `Any`, `type: ignore`, broad delete, shell execution or production subprocess. The sole bounded `subprocess.run` is the explicitly authorized physical-junction fixture with fixed argv, `shell=False` and timeout 5. |
| Isolation / residue | PASS: control and implementation worktrees remained clean; exported review artifacts were removed; repository cache and final `johnny-stage-env-*` root readbacks were empty. |

CR-118 and CR-119 are resolved. Reparse detection now reads the Windows file
attribute through `lstat` before root existence, marker access or traversal;
the physical regression test fails if marker access occurs through the
junction. E1-E4 and T1-T4 therefore pass without importing 05S2 behavior.

## Final conclusion

`APPROVED / INTEGRATION_AUTHORIZED`. This approval applies only to Ticket 05S1
and commits `e0898cd`, `41d5ce4`, `ecce06a` and `e1087d3` in their reviewed
ancestry. It authorizes a guarded integration that preserves the control-plane
review and handoff ledger; it does not authorize push, release, deployment,
live Codex mutation, target-project access or silent conflict resolution.
