# Ticket 05S1R Project-owned Disposable Runtime Root Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05s1r-project-owned-disposable-runtime-root` / `CLOSURE-LOCAL-INSTALL-T05S1R-01` / R1-R8 |
| Reviewed control baseline | `fceba60975ec3cbeeb24a35a865a311c9a24102a` |
| Implementation | `46dda341e2987cd52cf162b76ac1da2b6a94dedf` |
| WPR-only handoff | `b33314ca927532a3c0f74508117b3fd378c90d6a` |
| Branch / owner | `codex/implementation-project-owned-disposable-runtime-05s1r` / task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` |
| Review result | `CHANGES_REQUESTED / SAME_BRANCH_CORRECTION_REQUIRED` |

The ancestry is exact: `fceba609 -> 46dda341 -> b33314ca`. The implementation
commit changes only the eight frozen implementation paths and the handoff
commit changes only `doc/WorkProgressReport.md`. `git diff --check`, exact
three-worktree topology and final tracked/ignored/cache/runtime readbacks pass.
The implementation lane is clean. Review used immutable `git archive` exports
and did not modify the implementation worktree.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused matrix outside OS TEMP | PASS: the six frozen suites ran `77/77`; `tests/.johnny-runtime` was absent afterward. |
| Full serial suite | PASS: `python -B -m unittest discover -s tests -v`, `412/412`; runtime root absent afterward. |
| Strict typing / compile | PASS: `mypy --strict --explicit-package-bases --no-incremental` checked `134` files using a repository-external cache; all `134` Python files compiled in memory. |
| Exact scope / source / XSS | PASS: exact implementation and WPR-only path sets, ancestry, diff and source sentinels passed. `XSS_NOT_APPLICABLE`: no Browser, WebView, HTML/DOM renderer, JavaScript execution context or privileged bridge is present. |
| Prefix-similar lease probe | FAIL: a constructed marker-bound direct child named `johnny-stage-env-prefix-similar` returned `REMOVED / NONE` and was deleted. |
| Delete-failure probe | FAIL: forcing the exact tree removal operation to raise `PermissionError` propagated that exception instead of a finite `TeardownResult`. The reviewer then removed only its own exact probe residue. |
| TEMP-located checkout | FAIL: a fresh exact export beneath the system TEMP directory failed at `test_disposable_environment_core.py:39`, left its newly provisioned checkout-local lease behind, and caused dependent suites to reject the unclaimed residue. |

## Closure mapping

| Item | Result | Independent result |
| --- | --- | --- |
| `R1` | PASS | Old factory removal and exact eight-path implementation scope are present. |
| `R2` | FAIL | Source derives the runtime parent from module location, but the committed test rejects the same valid derivation whenever the checkout itself is below OS TEMP. |
| `R3` | PASS | Distinct owners, exact descendant overlays and parent-environment isolation pass in the non-TEMP immutable export. |
| `R4` | FAIL | Source creates no direct `%TEMP%/johnny-stage-env-*` root, but the test substitutes a broader and incorrect rule that the entire checkout-derived root must not be beneath TEMP. |
| `R5` | FAIL | Prefix-similar direct children are admitted and delete failures are not finite. Exact normal teardown, marker mismatch, reparse and escape cases otherwise pass. |
| `R6` | PASS | Unclaimed, malformed and unexpected project-local residue blocks without deletion. |
| `R7` | FAIL | Direct callers and old-symbol absence pass, but the required full focused readback is not location-independent and can leave ignored runtime residue. |
| `R8` | FAIL | Submitted reversals and static checks pass, but independent prefix-shape, delete-failure and test-truth adversarial cases fail. |

## CodeReview.md mandatory checks

- **Clear strong types:** PASS. Named Pydantic models, enums and finite unions
  remain at the boundary; no `Any`, `type: ignore` or optional effect port was
  introduced.
- **Existing coding conventions:** PASS. Python 3.11, `pathlib`, Pydantic and
  `unittest` match the existing staging-support implementation.
- **Logic correctness / edge cases:** FAIL for exact lease-name admission and
  finite cleanup failure handling (CR-167 and CR-168).
- **Security / isolation:** FAIL closed in most ownership and reparse cases,
  but prefix-similar authorization can delete a path outside the frozen exact
  lease-name shape. No external sentinel was deleted by reviewer probes.
- **Test truth / smoke:** FAIL CR-169. Green results depend on the checkout not
  being under OS TEMP, which is not a frozen prerequisite; the failing assertion
  occurs before exact teardown.
- **Dependencies / project specification:** PASS for dependency scope and
  AC-13 alignment of the intended design. No requirement change is needed.
- **Agent-role / orchestration boundary:** PASS. No Agent-control surface or
  authority change is in this ticket.
- **Adaptive profile / staging lifecycle:** NOT APPLICABLE to this prerequisite
  migration; it does not dispatch post-POC staging development.

## Batched findings

1. **CR-167 - `IMPLEMENTATION_DEFECT`, R5/R8.**
   `tests/staging/environment_core/environment.py:179-185` accepts any direct
   child whose name merely begins with `johnny-stage-env-`. The frozen
   path-prefix matrix requires the exact generated lease shape and explicit
   prefix-similar rejection. A typed lease and exact marker for
   `johnny-stage-env-prefix-similar` reached teardown and was deleted.
2. **CR-168 - `IMPLEMENTATION_DEFECT`, R5/R8.**
   `tests/staging/environment_core/environment.py:113-118` invokes recursive
   deletion without converting filesystem delete/permission failures into a
   finite result. An exact injected `PermissionError` escaped the public
   teardown boundary. The same correction must cover any rollback cleanup path
   that is required to remain finite without claiming false absence.
3. **CR-169 - `IMPLEMENTATION_DEFECT`, R2/R4/R7/R8.**
   `tests/test_disposable_environment_core.py:31-41` and `:43-76` assert that a
   checkout-derived lease cannot be under `tempfile.gettempdir()`. AC-13 forbids
   direct OS-global staging roots; it does not forbid a valid checkout from
   being located under TEMP. The first assertion also precedes teardown, so a
   failure leaves test-created residue and corrupts subsequent test truth.

## Conclusion

`CHANGES_REQUESTED / SAME_BRANCH_CORRECTION_REQUIRED`. All findings were
collected in this single initial review and map to the existing R1-R8 closure;
there is no `REQUIREMENT_CHANGED`. Keep the same ticket, implementation owner,
permanent worktree, branch, allocation and valid receipt. The submitted commits
remain immutable evidence. No new branch/worktree, integration, E3D/E4 resume,
staging push, package/build/install, live Codex/target-project mutation,
release or deployment is authorized by this review.

## Revision 02 terminal correction review

| Field | Value |
| --- | --- |
| Correction | `0cca9dee7a73a78e55fc739cca1ce5263a0e68ca` |
| WPR-only handoff | `ef69fb8c459309891d53523fc63be33e574b25eb` |
| Exact ancestry | `b33314ca -> 0cca9dee -> ef69fb8c` |
| Result | `CONVERGENCE_REVIEW_REQUIRED / CR-169_OPEN` |

The correction changes exactly the authorized contracts, allocator and focused
test paths; the handoff changes only `doc/WorkProgressReport.md`. The permanent
implementation worktree is clean and exact three-worktree topology is
unchanged.

| Check | Independent result |
| --- | --- |
| Outside-TEMP focused matrix | PASS: immutable export ran `79/79`; project runtime was absent afterward. |
| Targeted strict typing / compile | PASS: strict mypy passed the three changed Python files; all `134` repository Python files compiled in memory. The submitted handoff additionally records full-tree mypy `134/134` and full serial `414/414`. |
| CR-167 | CLOSED: exact lowercase 32-hex name admission rejects prefix-similar, short, long, non-hex and uppercase forms before marker read or deletion. |
| CR-168 | CLOSED: exact delete failure returns `BLOCKED / DELETE_FAILED`, preserves the root/marker and retains the live claim for an intact retry. |
| Checkout-under-TEMP core | FAIL: fresh exact export ran `8/10`; T1 fails at line 109 and leaves two leases, after which the physical-junction test errors because the runtime parent remains. |
| Checkout-under-TEMP six-suite matrix | FAIL: fresh exact export ran `79` tests with fourteen failures and one error; later child processes correctly reject the unclaimed residue. |
| Source / XSS / task binding | PASS: no forbidden dynamic typing or renderer/JavaScript capability; `XSS_NOT_APPLICABLE`; exact owner task is idle and bound to the permanent implementation worktree. |

CR-169 was only partially corrected. The first runtime-root test now registers
cleanup before its location assertions, but
`tests/test_disposable_environment_core.py:93-116` still asserts that each
checkout-derived lease is outside the entire system TEMP tree. That is not the
AC-13 rule: only a direct OS-global `TEMP/johnny-stage-env-*` root is forbidden.
The two leases are also not registered for exact cleanup before that assertion,
so the failed test poisons later evidence.

Final result is `CONVERGENCE_REVIEW_REQUIRED`. Workflow section 8.1 prohibits a
third correction on this closure. CR-169 must move to one finite evidence-only
child ticket; the submitted parent and correction commits remain immutable
evidence. No integration, E3D/E4 resume, package lane, new worktree, push,
release or deployment is authorized by this terminal review.
