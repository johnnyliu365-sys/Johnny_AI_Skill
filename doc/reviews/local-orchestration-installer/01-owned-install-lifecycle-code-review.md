# 01 Owned Install Lifecycle — Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `01-owned-install-lifecycle` |
| SPEC / change | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / `CHG-20260808-011` |
| Reviewed baseline | `15f6be8` |
| Implementation / docs handoff | `4b840cd` / `7c73b14` |
| Implementation owner | Codex implementation Agent / `codex/implementation-local-install-lifecycle-01-rework-2` |
| Reviewer | Codex / current `main` worktree |
| Result | `CHANGES_REQUESTED` |

## Traceability

- Approved Context: `doc/context/local-orchestration-installer/main.md`.
- Ticket scope: typed owned ledger, fake lifecycle ports and fail-closed install/uninstall only; no real host configuration, target project, Git adapter or package artifact is reviewed as delivered.
- Receipt `rcpt_local_orchestration_install_01_20260808` remains valid. The review result blocks the rework-2 implementation branch as historical evidence; it does not alter the approved SPEC, ticket scope or the planning lane's Ticket-02 dependency wait.

## Rework-2 review result

CR-38's normal partial-effect retries and CR-39's first-host verification rollback now reach finite outcomes. The CR-38 recovery-load behavior also passes reverse verification: replacing the recovery load with `None` in memory makes its partial-file retry test fail.

The ticket remains unapprovable because a valid-shaped recovery can skip required phases, selected-host receipts are not bound back to the request, two installation IDs can share and corrupt the one fixed root, and CR-40's mandatory matrix/red evidence remains incomplete.

### CR-40 remains open — mandatory matrix and red evidence are still incomplete

The focused suite expanded to 20 tests, but the approved ticket requires each applicable boundary and external port failure individually, plus a first failing test name/reason for every behavior. The committed evidence does not meet that bar:

- the five null/empty representations are grouped only for `installation_id`; they are not individually applied to manifest, host receipt and owned-path boundaries;
- `FakeFilesystem.fail_stage`, recovery-write and recovery-clear faults are not each exercised through their observable use cases;
- target-repository snapshots cover successful install plus failed/successful uninstall, but not the required failed-install path;
- the handoff lists red failures for normal lifecycle, CR-38 retries, one CR-39 case and a port-fault matrix, not each of the 20 committed behaviors;
- no test covers the valid-shaped recovery phase bypass, selected-host receipt mismatch or fixed-root cross-installation collision described below.

The implementation and all tests first appear together in `4b840cd`, so Git history cannot independently establish the missing per-behavior red → green order.

Required correction: execute the complete ticket matrix and record each new behavior's exact first-red test/reason before implementation. Grouping is allowed in one test method, but every required value/port/path must be an explicit subtest with externally observable assertions.

### CR-41 — typed recovery phase can skip removal and report false `REMOVED`

`RecoveryRecord` has no operation/phase progress invariant (`library/local_orchestration/contracts.py:223-233`). `_load_recovery_for_uninstall` accepts `UNINSTALL_LEDGER` based only on type, installation ID, operation and phase (`library/local_orchestration/lifecycle.py:202-223`), and `_resume_uninstall` then skips host/file work and deletes the ledger (`library/local_orchestration/lifecycle.py:289-397`).

Independent reproduction installed normally, replaced only the owned recovery entry with a strict `RecoveryRecord` at `UNINSTALL_LEDGER` using the exact ledger manifest/receipts but no completed progress, then invoked uninstall. Result: `REMOVED`; the main ledger and recovery were deleted while every payload file and one host registration still existed.

This is a direct AC-06/07 false-success and tampered-state bypass. Strong field types alone do not prove the preceding effects happened.

Required correction: make phase transitions evidence-bearing and fail closed. At minimum, phase/operation/path invariants must be model-validated; resuming file/ledger phases must reverify all host receipts are absent; entering/finalizing ledger phase must prove every manifest artifact is absent (not merely trust the phase enum). Add valid-shaped phase-forgery tests for every skippable transition.

### CR-42 — host receipt is not bound to the selected host

After `register`, the application checks only that the result is a `HostReceipt`, appends it and calls `verify` (`library/local_orchestration/lifecycle.py:90-103`). Neither this boundary nor `OwnedLedger._consistent` compares `receipt.host_id` to the loop's selected `host_id`.

Independent reproduction selected `host_codex`; a typed fake returned and verified a receipt for `host_claude`. Install returned `INSTALLED` and the ledger recorded only `host_claude`. This violates AC-02's per-selected-host `detect → register → verify → receipt` binding.

Required correction: before verification or ledger construction, require exact installation ID, selected host ID, unique registration identity and receipt-owned paths contained in the staged manifest. Any mismatch must begin finite rollback and never issue an install success ledger.

### CR-43 — two installation IDs collide inside the fixed root

The application checks only `ledger.load(request.installation_id)` (`library/local_orchestration/lifecycle.py:65-72`). The filesystem port receives the installation ID, but `FakeFilesystem.stage` discards it and writes the same relative paths below one fixed root (`library/local_orchestration/fakes.py:45-56`).

Independent reproduction installed two distinct valid installation IDs with the same payload. Both returned `INSTALLED`. Removing the first returned `REMOVED`, deleted the shared files and left the second host registration/ledger; removing the second then returned `MANIFEST_INVALID`.

This breaks fixed-root ownership and one-click detachability. Re-running Setup with a new generated ID must not silently create a second owner of the same paths.

Required correction: give the fixed root one authoritative active-owner record (or equivalently make every artifact path installation-scoped and prove independent ownership). Before staging, atomically reject a different active installation with `INSTALLATION_EXISTS`. Add two-ID install/remove interleaving tests, including interrupted recovery.

## Current independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `15f6be8 → 4b840cd → 7c73b14`; implementation worktree clean |
| `git diff --check 15f6be8..4b840cd` | Passed |
| `python -B -m unittest discover -s tests` | 151 passed |
| `python -B -m pytest -q -p no:cacheprovider` | 151 passed / 192 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 71 source files clean |
| In-memory compile / privacy sentinels | 5 local-orchestration modules compiled; passed |
| CR-38 reverse verification | Replacing recovery load with `None` makes `test_cr38_partial_file_delete_retry_reaches_removed` fail |
| Typed phase-forgery probe | Failed: returned `REMOVED` with files and host registration still present |
| Selected-host mismatch probe | Failed: selected Codex, accepted Claude receipt, returned `INSTALLED` |
| Two-ID fixed-root probe | Failed: both installed; removing one made the other `MANIFEST_INVALID` with registration retained |

## Current CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: values are typed, but CR-41 proves the state type lacks causal invariants. |
| Coding/architecture rules | Fail: fixed-root ownership is not represented by a single authoritative owner. |
| Logic correctness | Fail: CR-41 through CR-43 produce false success or cross-install corruption. |
| Boundary and exception behavior | Partial pass on finite exceptions; fail on the still-incomplete CR-40 matrix. |
| Security and ownership isolation | Fail: valid-shaped recovery and mismatched host receipt bypass required ownership transitions. |
| Test coverage | Fail: all three independent probes pass outside the committed suite; red evidence is incomplete. |
| Dependencies | Pass: no new external dependency. |
| SPEC/ticket compliance | Fail: AC-02, AC-06, AC-07 and ticket completion evidence are not fully met. |

## Current CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | The seven root cases pass; cross-install fixed-root ownership remains untested (CR-43). |
| 2 | null / empty / containers | Fail: required representations are not applied to each named model boundary. |
| 3 | Authorization bypass | Fail: CR-41 and CR-42 skip recovery/selected-host authority checks. |
| 4 | Token format/comparison | N/A by approved ticket; source sentinel passes. |
| 5 | Error-code consistency | Finite tested faults pass; CR-41 produces the wrong success state rather than a failure code. |
| 6 | Exception propagation | Tested host/runtime/process paths pass; stage/recovery write/clear matrix remains incomplete. |
| 7 | Tests cover described behavior | Fail: CR-40 and three independently reproduced gaps. |

## Required next rework

This branch is blocked historical evidence. The implementation owner must start another fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick or reuse of `4b840cd` or `7c73b14`. The original receipt remains valid; no second user dispatch confirmation is permitted.

The next allocation must address CR-40 through CR-43 with fresh behavior-specific red evidence, then return new implementation commit(s) plus a final docs-only handoff for independent review.

## Prior second-review result (`fd429fd`, `a222d89` / `8e39c99`)

CR-36 and the single-invocation portion of CR-37 are corrected. Runtime type rejection now occurs before deletion, absence is checked through a typed result bound to the same installation, host, registration and owned paths, and reversing either guard in memory makes its focused test fail.

The ticket is not approvable because durable recovery is written but never consumed, a required install failure escapes the finite result contract, and the committed tests/red evidence do not cover the ticket's mandatory matrix.

### CR-38 remains open — persisted recovery cannot be resumed

`InstallLedgerPort.load_recovery` exists, but neither `InstallControlPlane.install` nor `UninstallControlPlane.uninstall` calls it. `UninstallControlPlane.uninstall` always starts from the normal ledger/manifest/host verification path at `library/local_orchestration/installation.py:329-367`.

Independent probes demonstrate the consequence:

- partial owned-file deletion returns `PARTIAL_DELETION`; after the fault is removed, retry returns `MANIFEST_INVALID`;
- partial host unregister returns `HOST_UNREGISTER_FAILED`; after the fault is removed, retry returns `HOST_VERIFICATION_FAILED`;
- ledger-delete failure after complete filesystem deletion returns `LEDGER_DELETE_FAILED`; retry returns `MANIFEST_INVALID`.

All three retain a `RecoveryState`, but none can use it to finish or safely restore the operation. This fails the original CR-38 correction requirement and AC-07's retryable owned recovery state.

Required correction: add an explicit typed recovery-resume transition that loads and validates the exact recovery record before normal preconditions, resumes only the recorded owned phase/effects, and ends by clearing both ledger and recovery state. Red-first tests must invoke the operation a second time after removing each injected fault and assert a finite terminal outcome without foreign deletion or leftover owned state.

### CR-39 — host verification failure escapes as a Pydantic exception

`InstallControlPlane` appends a registration receipt only after host verification succeeds (`library/local_orchestration/installation.py:93-107`). When verification fails for the first host, `_rollback_install` constructs `RecoveryState` with an empty `host_receipts`, while that field requires at least one item (`library/local_orchestration/contracts.py:207-216`). The `ValidationError` occurs before `_rollback_install` enters its exception-handling block.

The independent probe with `FakeHostLifecycle.fail_verify = True` raised `ValidationError` instead of returning `INSTALL_BLOCKED`. This violates AC-02 and the ticket's stable-error/exception requirement and can leave the just-created host registration plus staged payload without a recovery result.

Required correction: model zero-receipt rollback explicitly and retain a receipt as soon as registration has produced an owned effect. Host detect/register/verify failures must each return a finite `INSTALL_BLOCKED` reason without propagating implementation exceptions, and cleanup/retry authority must match the effects that actually occurred.

### CR-40 — mandatory TDD matrix and red evidence are incomplete

The rework test module has 12 tests, but the approved ticket explicitly requires more cases than the committed tests execute:

- the path matrix omits the URL-encoded form;
- null/empty coverage does not separately exercise omitted fields, manifest, host receipt and owned-relative-path boundaries;
- normal lifecycle does not assert a second uninstall returns `NOT_INSTALLED` or prove every ledger-owned path/registration was removed;
- failure injection does not cover host detect/register/verify, runtime/process stop, tampered ledger/manifest and other ticket-listed ports one at a time;
- target-repository snapshots cover only the success path, not failed install and failed uninstall paths;
- the handoff records only a module-level `ModuleNotFoundError`, not the required first failing test name and reason for each CR-36/37/38 behavior.

The implementation and tests first appear together in `fd429fd`; the supplied evidence therefore cannot establish the required per-behavior red → green order. This is an implementation/evidence defect because the ticket already listed these cases.

Required correction: execute the complete ticket matrix, record each new behavior's first failing test name/reason before implementation, and keep assertions on externally observable effects. A collection failure for a missing package does not replace behavior-specific red evidence.

## Prior second-review independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `f297d4f → fd429fd → a6dfa2d → a222d89 → 8e39c99`; implementation worktree clean |
| `git diff --check f297d4f..a222d89` | Passed |
| `python -B -m unittest discover -s tests` | 143 passed |
| `python -B -m pytest -q -p no:cacheprovider` | 143 passed / 175 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 71 source files clean |
| In-memory compile / privacy sentinels | 5 local-orchestration modules compiled; passed |
| CR-36 reverse verification | Replacing the runtime proof-type guard in memory makes `test_structural_proof_object_is_rejected_before_deletion` fail |
| CR-37 reverse verification | Replacing the absence validation in memory makes `test_plausible_removal_proof_without_verified_absence_blocks` fail |
| Recovery retry probes | Failed as described in CR-38; persisted records are not consumed |
| Install verify-failure probe | Failed as described in CR-39 with propagated `ValidationError` |

## Prior second-review CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: proof/absence boundaries are typed; recovery transitions are not a complete executable state machine. |
| Coding/architecture rules | Fail: the declared recovery read port is unused by both use cases. |
| Logic correctness | Fail: CR-38 retries cannot progress and CR-39 escapes the finite result contract. |
| Boundary and exception behavior | Fail: required failure injections and null/path cases are absent; host verification propagates. |
| Security and ownership isolation | Single-invocation removal guards pass; no approval while retry transitions cannot prove safe owned completion. |
| Test coverage | Fail: CR-40 and behavior-specific red evidence are incomplete. |
| Dependencies | Pass: no new external dependency. |
| SPEC/ticket compliance | Fail: AC-02/06/07 and the ticket completion evidence are not fully met. |

## Prior second-review CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | Fail: URL-encoded case is missing from the required seven-case test matrix. |
| 2 | null / empty / containers | Fail: only installation-ID variants are grouped; required model boundaries are missing. |
| 3 | Authorization bypass | CR-36/37 direct guard tests pass; recovery-resume ownership cannot yet be reviewed because no resume path exists. |
| 4 | Token format/comparison | N/A by approved ticket; source sentinel passes. |
| 5 | Error-code consistency | Fail: CR-39 propagates `ValidationError` instead of a finite code. |
| 6 | Exception propagation | Fail: CR-39 and missing per-port failure cases. |
| 7 | Tests cover described behavior | Fail: CR-38 retry is not asserted and mandatory ticket cases/red evidence are missing. |

## Prior second-review required rework

This branch is blocked historical evidence. The implementation owner must start another fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick or reuse of `fd429fd`, `a222d89` or `8e39c99`. The original receipt remains valid; no second user dispatch confirmation is permitted.

The new allocation must address CR-38 through CR-40 with fresh behavior-specific red evidence, then return new implementation commit(s) plus a final docs-only handoff for independent review.

## Prior first-review findings (`010110a` / `7bc5fd5`)

### CR-36 — P0: dynamic removal proofs cross the deletion boundary

`UninstallControlPlane._validate_removal_proofs` accepts `tuple[object, ...]` and reads fields with `getattr` in `library/local_orchestration/installation.py`. Any unvalidated object that happens to expose matching attributes can authorize the next deletion step. This directly violates the P0 rule against unvalidated dynamic objects across a domain boundary.

Required correction: `HostLifecyclePort.unregister_all` must return `tuple[HostRemovalProof, ...]`; the application boundary must reject non-`HostRemovalProof` values before comparison, preserve the typed reason and run no filesystem deletion. Add a red-first regression with a structurally matching non-Pydantic object.

### CR-37 — P1: removal proof does not prove the host registration is absent

The current check compares fields in a returned proof but never asks the host adapter to verify that the exact receipt-owned registration/payload is gone. A faulty adapter can remove nothing, return a field-matching proof and cause owned payload deletion. This breaks AC-06/07's required `unregister → verify absent` lifecycle.

Required correction: add a strongly typed post-removal verification port/result bound to the same installation/host/registration/owned paths. The uninstaller must require every verification before ledger/filesystem deletion; a plausible-but-nonremoving fake must result in `UNINSTALL_BLOCKED`, retain recovery state and leave the filesystem untouched.

### CR-38 — P1: failed rollback/deletion can lose the recovery authority

Install failure invokes `_safe_unregister` and discards its result; if cleanup fails after a host registration, the operation reports blocked but has no durable receipt/ledger for retry. On uninstall, the ledger is deleted before filesystem deletion; if deletion partially changes the owned root and ledger restoration fails, the code swallows that restoration failure. Both paths can leave installer-owned residue without a reliable recovery record, contrary to AC-07 and the one-click detachability requirement.

Required correction: make rollback and delete progress an explicit durable, typed recovery state. Do not swallow failed host cleanup or failed ledger restoration. Add failure injection after partial host cleanup and after partial filesystem deletion/ledger restoration; each must expose a unique finite reason, leave only verified owned recovery data, never report success and allow a safe retry.

## Prior first-review independent verification

| Check | Result |
| --- | --- |
| `git diff --check 8e8caf7..010110a` | Passed |
| `python -B -m unittest discover -s tests` | 148 passed |
| `python -B -m pytest -q -p no:cacheprovider` | 148 passed / 175 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 71 source files clean |
| In-memory compile | 5 `local_orchestration` modules compiled |
| Metadata/privacy source scan | Passed; no raw Context/source/prompt sentinel in delivered source |
| TDD evidence | Handoff records an initial `ModuleNotFoundError` before implementation. It is credible for the initial module-creation behavior, but the CR-36/37/38 adversarial cases lack their required red-first tests. |

## Prior first-review CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | **Fail**: CR-36 admits untyped `object`/`getattr` at the removal proof boundary. |
| Coding/architecture rules | **Fail**: CR-36 and CR-38 allow implicit dynamic/recovery behavior instead of named typed state/ports. |
| Logic correctness | **Fail**: CR-37 permits a non-removing adapter to assert a matching proof. |
| Boundary and exception behavior | **Fail**: CR-38 swallows recovery failures; the failure state is not reliably retryable. |
| Security and ownership isolation | **Fail**: CR-36/37 can advance to deletion without verified proof of host removal. |
| Test coverage | **Fail**: existing tests cover malformed Pydantic proof and pre-effect fake failures, not structurally matching dynamic proof, nonremoval with plausible proof, or recovery-state loss after partial effects. |
| Dependencies | Pass: no new dependency was introduced. |
| SPEC/ticket compliance | **Fail**: AC-06/07 require proof-based full removal and fail-closed retry state, which the above cases do not guarantee. |

## Prior first-review CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | Partially covered by locator/root cases; no review approval while ownership proof is incomplete. |
| 2 | null / empty / containers | Covered at input/ledger boundaries. |
| 3 | Authorization bypass | **Fail**: CR-36/37 are direct and indirect removal-proof bypass paths. |
| 4 | Token format/comparison | N/A by ticket design; source scan found no credential/token storage or comparison. |
| 5 | Error-code consistency | Partially covered; CR-38 requires distinct durable-recovery codes. |
| 6 | Exception propagation | **Fail**: cleanup/restoration failures are intentionally swallowed without a durable recovery outcome. |
| 7 | Tests cover described behavior | **Fail**: required adversarial/mutation cases are absent. |

## Prior first-review required rework handoff

The current branch is blocked historical evidence. The implementation owner must receive a fresh control-plane rework handoff, create a new branch from that recorded current `main` baseline, and repeat red → minimal implementation → green for CR-36 through CR-38. It must not reset, overwrite, cherry-pick or reuse `010110a` / `7bc5fd5`. After its independent implementation and docs-only handoff, it returns `COMPLETED` for another review; receipt `rcpt_local_orchestration_install_01_20260808` remains valid without a second user confirmation.
