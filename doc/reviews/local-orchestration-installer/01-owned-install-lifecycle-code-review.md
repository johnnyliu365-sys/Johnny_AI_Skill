# 01 Owned Install Lifecycle — Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `01-owned-install-lifecycle` |
| Current result | `CHANGES_REQUESTED` |
| Reviewer | Codex / current `main` worktree |
| Implementation worktree | `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` |
| Single branch | `codex/implementation-local-install-lifecycle-01` |
| Governing closure | `CLOSURE-LOCAL-INSTALL-T01-REOPEN-01` / `C1..C8` |

## Superseded experiment

The earlier Ticket-01 implementation experiment produced fourteen unmerged
branches and fourteen different source trees. Thirteen were rejected and the
last was never approved. On 2026-08-09 the project owner revoked that lane; all
fourteen branch refs were deleted and the implementation worktree was returned
clean to detached control commit `846caaf`. No `library/local_orchestration`
source from that experiment entered `main`.

Those historical commits and CR-36..72 are not acceptance requirements for the
reopened ticket. They may not be copied into the new implementation or used to
expand review. The formal history remains available in Git reflog and prior
control-plane commits until normal garbage collection.

## Reopened review boundary

The reopened ticket is a small synchronous fake lifecycle. Review must:

1. Inspect only the five authorized source files and one authorized test file.
2. Execute and map every `C1..C8` item once.
3. Verify the hard file/line ceiling and out-of-scope sentinel.
4. Batch all findings in one report.
5. Keep any single correction on the same implementation branch/worktree.

No crash-recovery state machine, transition-grant framework, exhaustive fault
matrix, real installer/host behavior or Ticket-02+ behavior is part of this
review.

## Initial independent review — `REV-LOCAL-INSTALL-T01-REOPEN-01`

| Field | Evidence |
| --- | --- |
| Reviewed revisions | Baseline `8704ada`; implementation `ddd9f55`; docs-only handoff `c29f8ed`. |
| Scope integrity | Implementation commit adds exactly the five authorized production files and `tests/test_owned_install_lifecycle.py`; handoff commit changes only `doc/WorkProgressReport.md`. Both descend from the required baseline and the implementation worktree is clean. |
| Ceiling | Production `517 / 600` non-blank lines; test `349 / 500`. |
| Independent green run | `python -B -m unittest tests.test_owned_install_lifecycle`: 8/8 passed. `mypy --strict --no-incremental` over the six ticket files: no issues. Six-file in-memory compile and `git diff --check` passed. |
| Actual Git isolation | Two actual temporary Git repositories retained byte-identical snapshots and unchanged `git status --porcelain=v1` (`?? existing.txt` / empty) across an install success and blocked uninstall. |
| Reverse mutation | C1 and C3..C8 each failed when its governing behavior was reversed in an isolated archive. C2 remained green after removing the real file unlink; see `CR-REOPEN-01`. |

## Closure mapping

| Closure | Result | Independent evidence |
| --- | --- | --- |
| `C1` | PASS | Valid install returned `InstallSucceeded`; ledger read-back and receipt binding matched. Reversing the success result failed `test_c1_*`. |
| `C2` | FAIL | Baseline behavior passed, but removing `FakeOwnedFilesystem.remove_manifest()`'s `target.unlink()` left C2 green because `has_owned_effects()` only observes the ownership set after it is discarded. |
| `C3` | PASS | Exact root plus suffix, trailing separator, casing, encoded separator, traversal and empty variants are mapped; bypassing the exact-root validator produced six failures. |
| `C4` | PASS | `None`, omitted, empty, whitespace and empty-container inputs are covered for installation ID, manifest and owned path; bypassing nonblank validation failed the test. |
| `C5` | PASS | Foreign ID, tampered digest, foreign receipt and indirect directory/helper deletion remain mutation-free; bypassing the manifest match failed the test. |
| `C6` | PASS | The four frozen one-shot failures return blocked without unrelated deletion; propagating the stage failure produced an uncaught test error. |
| `C7` | PASS | Both the committed test and an external actual-Git probe passed; an isolated fake-filesystem mutation touching sibling `.git/HEAD` failed C7. |
| `C8` | PASS | Ticket source has no forbidden capability; injecting a forbidden subprocess marker failed C8. |

## CodeReview.md checks

| Check | Result |
| --- | --- |
| Clear, strongly typed, layered | PASS — named immutable Pydantic models, finite enums/results and typed injected ports; no `Any` or `type: ignore`. |
| Logic, boundaries, failures | PASS except the C2 evidence gap below; the reviewed implementation behavior itself passed the frozen cases. |
| Security / reachability | PASS — the application service is the only lifecycle use case; direct foreign/tampered ownership and the indirect helper path converge on the same pre-delete checks. No real host, process, Git, network or target-project capability exists. |
| Path-prefix interception | PASS — all seven required root cases map one-to-one to C3. |
| Permission-bypass interception | PASS — direct ID/receipt/digest and indirect helper paths map to C5 and are effect-free. |
| Test-description truthfulness | FAIL for C2 only — the assertion describes physical removal but observes only fake bookkeeping. |
| Dependencies / project specification | PASS — no new dependency; Pydantic and Python versions match the approved ticket. |

## Batched finding

### `CR-REOPEN-01` — `EVIDENCE_DEFECT` / Closure `C2`

- Location: `tests/test_owned_install_lifecycle.py:65-81`, specifically the final `has_owned_effects()` assertion; governing effect is `library/local_orchestration/fakes.py:70-82`.
- Impact: a regression that skips `target.unlink()` while discarding the ownership-set entry can return `REMOVED`, make repeat uninstall return `NOT_INSTALLED`, and still leave the owned payload on disk without failing C2.
- Reproduction: in an isolated archive of `c29f8ed`, replace the line `target.unlink()` with `pass`, then run only `test_c2_owned_uninstall_is_exact_and_idempotent`; it exits successfully.
- Required same-branch correction: add a direct observable assertion that the installed owned payload path no longer exists after uninstall (for example, assert `FakeOwnedFilesystem.read(OwnedRelativePath(value="payload/plugin.txt"))` raises `FileNotFoundError`). Keep the existing helper-retention, ledger, receipt and idempotency assertions. No production behavior, new file, branch, worktree or closure item is requested.
- Required return: one additive correction commit on `codex/implementation-local-install-lifecycle-01`, full C1..C8 / strict-mypy / compile / sentinel / actual-Git rerun, and updated docs-only handoff evidence.

## Conclusion

`CHANGES_REQUESTED`. This is the single permitted correction review for
`CLOSURE-LOCAL-INSTALL-T01-REOPEN-01`. All discoverable initial-review findings
are batched above; no other closure item is open.
