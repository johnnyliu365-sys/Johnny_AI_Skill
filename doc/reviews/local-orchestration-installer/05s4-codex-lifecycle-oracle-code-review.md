# Ticket 05S4 Codex Lifecycle Oracle Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `05s4-codex-lifecycle-oracle` / `CLOSURE-LOCAL-INSTALL-T05S4-01` / O1-O6 |
| Reviewed baseline | `ff7fc8508331085e8d54469ada8c64fe4bf591d9` |
| Implementation | `9086c0c62c0de1d9ad247caa6e9eabc95c816c46` plus whitespace-only `32b67b71858568eed5ecd7ab90ecd91709647b1f` |
| Docs-only handoff | `e4d00ddc4cb54be5706cfc136245302250259993` |
| Branch / owner | Existing `codex/implementation-codex-protocol-fixture-05s3` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Review result | `CHANGES_REQUESTED / CORRECTION_REQUIRED` |

The submitted ancestry is additive and exact. The implementation changes only
the six ticket-authorized Python paths, and the handoff changes only
`doc/WorkProgressReport.md`. Both worktrees were clean and `git diff --check`
passed. Independent execution used a fresh immutable commit export and did not
modify the implementation worktree.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 6/6 focused and 201/201 full unittest tests in an isolated temporary root. |
| Strict typing / compile | PASS: strict mypy checked 102 source files; all repository Python files compiled in memory. |
| Scope / source / ancestry | PASS: exact authorized source and docs paths, additive ancestry, no production source or integrated 05S1-05S3 change. |
| O1-O3 nominal lifecycle | PASS for the serial owned add/list/remove/absence smoke and the committed unrelated-foreign preservation case. |
| O4 duplicate identity adversarial probe | **FAIL:** seeding the same coherent foreign marketplace record twice returned two `OracleForeignSeeded` results; a fresh child list returned `OracleCompleted` with two identical entries. |
| O6 failure cleanup adversarial probe | **FAIL:** after the fixed command file was created, an injected ordinary fixture `OSError` returned `PROCESS_FAILED` but left `.johnny-05s4-command.json` present. |
| Isolation / residue | PASS after typed teardown of each review lease. The interrupted review's exact marker-bound test roots were also removed through the integrated 05S1 teardown API. |

## Closure mapping

| Item | Result | Independent disposition |
| --- | --- | --- |
| `O1` | PASS | Initialization and exact owned add/list use new bounded children and physical payloads. |
| `O2` | PASS | Exact plugin then marketplace removal and final physical absence pass on the nominal path. |
| `O3` | PASS with O4 overlap | Committed unrelated/same-plugin-name foreign records remain unchanged and do not authorize owned removal. |
| `O4` | **FAIL** | Duplicate checks cover only owned collections. Duplicate coherent foreign identities survive strict state validation and are returned as accepted list truth. |
| `O5` | PASS | The parent selects only surface/action and the real child produces each response. |
| `O6` | **FAIL** | Cleanup happens only after `_fixture.run` returns normally; an ordinary dependency failure exits before the fixed command cleanup. |

## CodeReview.md mandatory checks

- **Clear strong types:** PASS for the public frozen result and state types, but
  the state invariant is incomplete because uniqueness is enforced only for
  owned collections.
- **Existing coding conventions:** PASS. The implementation follows the
  integrated strict Pydantic and typed child-process patterns.
- **Logic correctness:** FAIL CR-126 and CR-127. Persisted truth can contain a
  duplicate foreign identity, and a blocked operation can leave the fixed
  command artifact.
- **Edge cases:** FAIL the O4 duplicate-foreign and O6 post-command dependency
  failure cells. Other committed malformed-state and process cases pass.
- **Security / performance:** FAIL closed-state integrity for duplicate
  foreign identity. No production host, target-project, network or Secret
  boundary was crossed.
- **Test coverage / smoke:** FAIL CodeReview.md class 7. The six broad tests are
  green, but their assertions do not cover every behavior promised by the O4
  and O6 rows.
- **Dependency reasonableness:** PASS. No dependency changed.
- **Project specification:** FAIL O4/O6 until both finite regressions pass.

CodeReview.md class 1 passes for the committed payload-locator variants. Class
3 direct/indirect owned-removal authority passes for the tested foreign record.
Class 7 fails because the named test matrix overstates duplicate and cleanup
coverage. No token exists in this ticket.

## Findings

**CR-126 - `IMPLEMENTATION_DEFECT`, O4.**
`tests/staging/codex_lifecycle_oracle/contracts.py:181` and
`oracle_child.py:159` enforce uniqueness only for `marketplaces` / `plugins`.
The same coherent `foreign_marketplaces` identity can be persisted twice and a
fresh list child accepts and returns both entries. Revision-02 must reject a
duplicate identity within either foreign collection while preserving the
intentional same display-name/different opaque-ID foreign plugin case and the
permitted owned-versus-foreign name distinction described by O3.

**CR-127 - `IMPLEMENTATION_DEFECT`, O6.**
`tests/staging/codex_lifecycle_oracle/oracle.py:72-90` performs fixed command
cleanup only after `_fixture.run` returns. An injected ordinary `OSError` from
that dependency returns `OracleBlocked(PROCESS_FAILED)` at line 87 and leaves
the command file behind. Revision-02 must guarantee safe exact-file cleanup on
all ordinary completed/blocked dependency exits, report
`COMMAND_CLEANUP_FAILED` when the exact ordinary command cannot be removed, and
must not broadly catch or misclassify `MemoryError`, `KeyboardInterrupt` or
`SystemExit`.

## Conclusion and correction boundary

`CHANGES_REQUESTED / CORRECTION_REQUIRED`. CR-126 and CR-127 are the complete
blocking batch for closure revision 01. The owner instruction to inspect the
affected tickets and dispatch them together authorizes one revision-02
correction on the same task, worktree, branch, allocation owner and valid
ticket authority; no replacement branch or worktree is permitted.

Revision-02 is limited to `contracts.py`, `oracle_child.py`, `oracle.py` and
`test_codex_lifecycle_oracle.py`. It must add the two exact regressions above,
run focused/full/strict/compile/diff and reverse-mutation evidence, then return
one additive implementation commit and one `WorkProgressReport.md`-only
handoff. The next independent review is final; any blocker stops with
`CONVERGENCE_REVIEW_REQUIRED`. No integration, 05B/05C refreeze, new-role
ticket implementation, live Codex mutation, target-project write, push,
release or deployment is authorized by this review.

## Revision-02 final independent review

| Field | Value |
| --- | --- |
| Closure | `CLOSURE-LOCAL-INSTALL-T05S4-02`; CR-126 and CR-127 only |
| Control review baseline | `3012af96da2e4d7a2e64b6cb41c035e86ea43fa2` |
| Correction / handoff | `02f33efbcb6eba400dcf92b81ba948716dee8e56` / `52ab9c0e71c5b7dd4fcec72970d2bc6a7517c954` |
| Branch / owner | Existing `codex/implementation-codex-protocol-fixture-05s3` / task `019fcc9c-f34f-7d53-a313-c70c90bf3245` |
| Final result | `APPROVED / INTEGRATION_AUTHORIZED` |

The correction is additive from submitted handoff `e4d00dd` and changes only
the four authorized oracle/test paths; the handoff changes only
`doc/WorkProgressReport.md`. Review used a fresh immutable ZIP export of the
implementation commit and did not write to either implementation worktree.

### Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / full | PASS: 10/10 focused and 205/205 full unittest tests. |
| Strict type / compile | PASS: strict mypy with explicit package bases over 102 source files and in-memory compile over the same 102 files. |
| CR-126 | PASS: duplicate identity in either foreign collection is blocked in the parent state model; direct persisted duplicates are independently rejected by the fresh child. Owned-versus-foreign distinction remains permitted. |
| CR-127 | PASS: ordinary post-command dependency failure removes the exact command file; a non-ordinary command locator produces `COMMAND_CLEANUP_FAILED`. |
| Exception boundary | PASS: an injected `MemoryError` propagates and is not caught or misclassified. |
| Scope / ancestry / diff | PASS: exact four-file correction, one-file handoff, additive ancestry, source sentinel and `git diff --check`. |
| Isolation / residue | PASS: control and both implementation worktrees are clean; review export, external cache, fixed command/response file and owned staging roots read back absent after exact cleanup. |

### Mandatory-check mapping

- **Clear strong types:** PASS. The finite union and named block reasons remain
  strict; no nullable effect port or dynamic escape was added.
- **Existing coding conventions:** PASS. The correction follows the existing
  strict state/child validation and typed fixture seam.
- **Logic correctness:** PASS. Identity uniqueness is collection-local as O3
  requires, and every ordinary post-command result either cleans up or returns
  the cleanup-specific block.
- **Edge cases:** PASS. Seeded and raw-state duplicates, ordinary dependency
  error, non-ordinary cleanup target and excluded process-control exception
  were independently exercised.
- **Security / performance:** PASS. Exact-path and disposable-environment
  boundaries are unchanged; no live Codex, target project, network or Secret
  was accessed.
- **Test coverage / smoke:** PASS. The four named CR-126/CR-127 regressions
  pass in addition to the complete focused/full suites.
- **Dependency reasonableness:** PASS. No dependency or production file
  changed.
- **Project specification:** PASS. O1-O6 remain satisfied and CR-126/CR-127
  are closed without changing 05B/05C transaction semantics.

No new blocking finding exists. `APPROVED / INTEGRATION_AUTHORIZED`.
Allocation `aln_local_orchestration_install_05s4_r02_20260811` and receipt
`rcpt_local_orchestration_install_05s4_r02_20260811` remain active only until
guarded integration is verified. This review does not refreeze or dispatch
05B/05C, mutate live Codex, touch a target project, push, release or deploy.
