# 01 Owned Install Lifecycle — Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `01-owned-install-lifecycle` |
| SPEC / change | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / `CHG-20260808-011` |
| Reviewed baseline | `5142378` |
| Implementation / docs handoff | `7df74e1`, `e84dff0`, `14838d9` / `f90877d` |
| Implementation owner | Codex implementation Agent / `codex/implementation-local-install-lifecycle-01-rework-4` |
| Reviewer | Codex / current `main` worktree |
| Result | `CHANGES_REQUESTED` |

## Traceability

- Approved Context: `doc/context/local-orchestration-installer/main.md`.
- Ticket scope: typed owned ledger, fake lifecycle ports and fail-closed install/uninstall only; no real host configuration, target project, Git adapter or package artifact is reviewed as delivered.
- Receipt `rcpt_local_orchestration_install_01_20260808` remains valid. The review result blocks the rework-4 implementation branch as historical evidence; it does not alter the approved SPEC, ticket scope or the planning lane's Ticket-02 dependency wait.

## Rework-4 review result

The intended CR-44 order is materially improved: owner-release failure retains `UNINSTALL_FINALIZE`, recovery-clear failure retains the final record after releasing the owner, and both focused sequences retry to `REMOVED`. The committed manifest-mismatch and configured post-host checkpoint tests also clean the cooperative fake's effects and retry successfully.

The ticket remains unapprovable because four independent paths bypass or lose that recovery/ownership model. CR-40 also remains open: the fresh suite is smaller than the prior matrix and verifies only selected fault/value cases.

### CR-40 remains open — required boundary, port and red evidence is incomplete

`test_boundaries_cover_omitted_and_container_installation_and_owned_paths` covers the five absent representations for installation ID and owned path (`tests/test_owned_install_lifecycle.py:210-235`), but the approved ticket requires the same explicit matrix for manifest and host receipt. `test_root_variants_and_receipt_model_are_fail_closed` checks only an empty receipt-owned-path tuple (`tests/test_owned_install_lifecycle.py:237-243`), not `None`, omitted, empty string, whitespace, list/object and equivalent outcomes at the named receipt/manifest boundaries.

The port-failure suite covers stage, host verify, runtime, process and two recovery-write positions. It does not exercise owner read/claim, ledger read/write/delete, recovery read, host detect/register/detach/absence, filesystem delete/partial-delete, or the final ledger-delete/checkpoint split. The ticket explicitly requires each external dependency fault to assert finite result, side effects and retry state.

The recorded first red ran eight tests, while the final focused suite contains twelve. `e84dff0` adds target-repository coverage after the implementation, and `14838d9` adds new runtime/process/recovery assertions plus a production-code correction in the same commit; no first-red name/reason is recorded for these added behaviors. This does not establish the required behavior-first TDD order.

Required correction: restore the complete named boundary/port matrix and record the first observable failure for every new behavior before its correction. Every fault assertion must include filesystem, host, owner, success ledger and recovery state plus the retry terminal outcome where effects may have begun.

### CR-46 — ledger deletion can still destroy the finalization transition

At `library/local_orchestration/lifecycle.py:214-219`, `_resume_uninstall` executes `ledger.delete()` before persisting the `UNINSTALL_FINALIZE` record, but maps failure of either operation to `LEDGER_DELETE_FAILED`. If deletion succeeds and the subsequent recovery write fails, the durable record remains `UNINSTALL_LEDGER` while the success ledger is already absent. On retry, lines 167-172 require that ledger and return `LEDGER_INVALID`, so `_finalize` is never reached.

Independent injection at recovery write call six produced: first uninstall `UNINSTALL_BLOCKED / LEDGER_DELETE_FAILED`; second uninstall `UNINSTALL_BLOCKED / LEDGER_INVALID`; empty files/hosts/success ledger; stale `UNINSTALL_LEDGER` recovery and active owner; a foreign installation remained `INSTALLATION_EXISTS`.

Required correction: make ledger removal and the terminal checkpoint one atomic/idempotent port transition, or make `UNINSTALL_LEDGER` resume accept a proven already-absent ledger and deterministically recreate/advance terminal authority. Add first-red tests for failure before deletion, after deletion/before terminal checkpoint, and repeated retry.

### CR-38 reopened — `install()` erases an active uninstall recovery

`install()` loads the success ledger and recovery together, then if any `OwnedLedger` exists it clears any recovery and returns `INSTALLED` (`library/local_orchestration/lifecycle.py:31-42`). It does not validate the recovery operation or resume/reject an uninstall in progress.

Independent reproduction performed a partial host detach. Uninstall returned `HOST_DETACH_FAILED` with durable `UNINSTALL_HOSTS` recovery and the host effect already absent. Calling `install()` with the same ID then cleared that recovery and returned `INSTALLED`; a later uninstall returned `MANIFEST_INVALID`, with the active owner/ledger stranded and no host registration.

Required correction: an install call may only consume an exact install-rollback recovery. Any uninstall recovery must route to the uninstall continuation or return a stable conflict without mutation. An existing ledger may return idempotent `INSTALLED` only after exact owner, request/ledger, filesystem and selected-host live-state validation.

### CR-42 reopened — rollback trusts an invented receipt instead of the returned host effect

The application constructs deterministic `HostReceipt` objects before calling the host (`library/local_orchestration/lifecycle.py:50-53,259-269`) and persists them as though registration had already issued a cleanup receipt. If `register()` returns a different receipt, line 74 rejects it but rollback uses only the precomputed receipt. The actual returned effect is discarded.

A typed host fake that registered and retained the mismatched returned Claude receipt, rather than the planned Codex receipt used by the committed fake, reproduced the bypass: install returned `HOST_RECEIPT_INVALID`, files/owner/recovery were cleared, but one live Claude registration remained. The committed fake appends the planned receipt before returning the mismatch (`library/local_orchestration/fakes.py:164-170`), so its test cannot detect this real boundary behavior.

Required correction: distinguish pre-effect `HostRegistrationIntent` from host-issued `HostReceipt`. Durable recovery must record/reconcile the actual effect identity before treating cleanup as proven. A mismatched result cannot be discarded; cleanup must either verify that no effect occurred or retain authoritative recovery for the returned effect.

### CR-43 reopened — existing-ledger fast path bypasses the active owner

The existing-ledger fast path at `library/local_orchestration/lifecycle.py:36-42` executes before `_claim()` and checks only `isinstance(owned, OwnedLedger)`. It does not compare `active_owner`, request version/hosts/payload, filesystem completeness or live registrations.

Independent reproduction installed ID A, inserted a second fully typed ID-B ledger for the same fixed-root manifest, then called `install(ID_B)`. The application returned `INSTALLED` with the ID-B ledger while `active_owner` and the only live host receipt still belonged to ID A. This regresses the exclusive fixed-root guarantee even though all values are strongly typed.

Required correction: route every existing-ledger result through the same authoritative active-owner and physical-effect verification. A different owner, conflicting recovery, mismatched request or missing live receipt must fail closed without clearing state.

## Rework-4 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `5142378 → 7df74e1 → e84dff0 → 14838d9 → f90877d`; implementation worktree clean |
| `git diff --check 5142378..14838d9` | Passed |
| `python -B -m unittest discover -s tests` | 143 passed |
| `python -B -m pytest -q -p no:cacheprovider` | 143 passed / 196 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 71 source files clean |
| In-memory compile / privacy sentinels | 5 local-orchestration modules compiled; passed |
| Ledger-delete/final-checkpoint probe | Failed: retry remains `LEDGER_INVALID` with stale owner/recovery |
| Install-during-uninstall probe | Failed: returned `INSTALLED`, erased recovery, later uninstall blocked |
| Actual mismatched-host-effect probe | Failed: live Claude registration remained after rollback |
| Typed second-ledger probe | Failed: returned `INSTALLED` while active owner/live receipt belonged to ID A |

## Rework-4 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: types are explicit, but a planned registration is incorrectly represented as an issued receipt. |
| Coding/architecture rules | Fail: success-ledger and finalization paths bypass the single ownership/recovery state machine. |
| Logic correctness | Fail: CR-38/42/43 regressions and CR-46 produce false success or nonconvergent recovery. |
| Boundary and exception behavior | Fail: CR-40 omits named value and port failures. |
| Security and ownership isolation | Fail: a second typed ledger bypasses active owner and a mismatched host effect is orphaned. |
| Test coverage | Fail: four independently reproducible paths pass outside the committed suite; final tests lack complete red evidence. |
| Dependencies | Pass: no new external dependency. |
| SPEC/ticket compliance | Fail: AC-02/03/06/07 and Ticket-01 TDD/retry requirements are not met. |

## Rework-4 required next rework

The rework-4 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick or reuse of `7df74e1`, `e84dff0`, `14838d9` or `f90877d`. Receipt `rcpt_local_orchestration_install_01_20260808` continues; no second dispatch confirmation is valid. The next allocation is limited to the complete CR-40 matrix, CR-46 and reopened CR-38/42/43 while preserving every previously closed guard.

## Rework-3 review result

CR-41 through CR-43 are corrected. Recovery phases now carry validated evidence and recheck live host/filesystem absence, a receipt is bound to the exact selected host, and one active owner excludes a different installation ID from the fixed root. Each guard also passed independent reverse validation: bypassing it in memory makes its focused regression fail.

The ticket is still not approvable. The terminal cleanup order can discard every retry authority before owner release succeeds, and two install-failure paths leave staged or registered effects without a ledger or recovery record. CR-40 also remains open because the committed matrix asserts finite error codes but does not assert absence/retry of these partial effects and still omits required value variants.

### CR-40 remains open — the failure matrix does not prove clean or retryable outcomes

`test_storage_failures_return_finite_results_and_never_leave_a_ledger` asserts only the returned `STAGE_FAILED` / `RECOVERY_WRITE_FAILED` reason and an empty success ledger (`tests/test_owned_install_lifecycle.py:365-379`). It does not assert the fixed root, active owner, host receipts and recovery authority after recovery-write failure. The owner-release fault is never exercised. The manifest-mismatch path is also absent.

The value-boundary matrix remains incomplete at `tests/test_owned_install_lifecycle.py:504-605`: installation ID lacks the omitted-field case, while owned relative path lacks `None`, omitted, empty-list and empty-object cases. Grouping malformed strings does not replace the ticket's individually required null/undefined/empty/container outcomes.

Independent execution reproduced the missing behavior instead of merely identifying absent tests:

- recovery-write failure after a verified host effect returns `RECOVERY_WRITE_FAILED` while retaining two staged files, one registered host and an active owner, with no ledger or recovery record;
- a staged manifest mismatch returns `MANIFEST_INVALID` while retaining both staged files and the owner; later same-ID and different-ID installs return `STAGE_FAILED`, leaving those files unowned;
- owner-release failure after otherwise complete uninstall returns `OWNER_RELEASE_FAILED`, but both ledger and recovery are already gone; the retry returns `NOT_INSTALLED` and a different installation remains blocked by the stale owner.

Required correction: expand the red/green matrix to assert all persisted/effected state, not only finite result codes. Every failure after staging or host registration must either compensate verified owned effects in the same invocation or retain a durable typed recovery/owner record that a retry demonstrably consumes. Exercise owner-release failure and the remaining named boundary variants explicitly.

### CR-44 — terminal cleanup destroys retry authority before owner release

`_resume_uninstall` deletes the ownership ledger and then calls `_clear_then_release` (`library/local_orchestration/lifecycle.py:299-312`). `_clear_then_release` clears recovery before invoking the fallible `release_owner` port (`library/local_orchestration/lifecycle.py:381-390`). If release raises, the result correctly says `OWNER_RELEASE_FAILED`, but no durable record remains that can route the retry.

Independent reproduction: normal install succeeded; with only `fail_owner_release=True`, uninstall returned `UNINSTALL_BLOCKED / OWNER_RELEASE_FAILED`, files and host receipts were gone, `records` and `recoveries` were empty, but owner stayed `inst_0000000000000001`. After removing the fault, a second uninstall returned `NOT_INSTALLED`; installing `inst_0000000000000002` returned `INSTALLATION_EXISTS` forever.

This violates AC-07's necessary owned recovery-state guarantee and produces a false terminal state. Required correction: model finalization as a durable, retryable typed phase. Do not clear the last recovery authority until ledger deletion, recovery cleanup and owner release can be proven to converge idempotently. Add first-red and retry-to-terminal tests for recovery-clear and owner-release faults separately and in sequence.

### CR-45 — install failures can leave unowned staged and host effects

After `stage`, a manifest mismatch returns immediately (`library/local_orchestration/lifecycle.py:76-80`) without writing recovery or deleting the staged result. When `_begin_install_rollback` cannot write its recovery record, it also returns immediately (`library/local_orchestration/lifecycle.py:314-335`) without compensating staged files, detaching any receipt or preserving another retry authority.

Two independent probes demonstrated both paths. A fake that staged the exact payload but returned the manifest in a mismatching order left both files behind with no recovery; later installs could not adopt or delete them. Separately, host registration succeeded, host verification failed and recovery persistence was faulted: the result was `RECOVERY_WRITE_FAILED` with two files, one live host receipt, active owner and no durable ledger/recovery. This is precisely the partial-effect loss prohibited by AC-02/07 and the ticket's stable-exception requirement.

Required correction: acquire durable rollback intent before the first staged/host effect, or provide a verified compensation path whose own failure remains represented by an authoritative typed recovery state. Manifest mismatch must not strand paths that were actually created. Add retries proving the original installation can reach a safe terminal outcome and a foreign installation cannot claim residue.

## Rework-3 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `7cc8b38 → c91041a → ba74caf`; implementation worktree clean |
| `git diff --check 7cc8b38..c91041a` | Passed |
| `python -B -m unittest discover -s tests` | 147 passed |
| `python -B -m pytest -q -p no:cacheprovider` | 147 passed / 224 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 71 source files clean |
| In-memory compile / privacy sentinels | 5 local-orchestration modules compiled; passed |
| CR-41 reverse verification | Bypassing live host-absence guard makes the focused phase test fail |
| CR-42 reverse verification | Bypassing exact receipt binding makes the host-mismatch test fail |
| CR-43 reverse verification | Bypassing the active-owner gate makes the two-ID test fail |
| Owner-release recovery probe | Failed: retry says `NOT_INSTALLED` while stale owner blocks another installation |
| Manifest-mismatch recovery probe | Failed: staged files remain without ledger/recovery and later installs cannot converge |
| Recovery-write-after-host-effect probe | Failed: staged files and live receipt remain without durable recovery |

## Rework-3 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: primary contracts are typed; finalization lacks a durable state representing release completion. |
| Coding/architecture rules | Fail: fallible effects are ordered so the recovery authority can disappear first. |
| Logic correctness | Fail: CR-44 returns a false future `NOT_INSTALLED`; CR-45 strands effects. |
| Boundary and exception behavior | Fail: finite codes do not imply clean/retryable state, and CR-40 variants remain absent. |
| Security and ownership isolation | Fail: unowned staged/registered effects cannot be safely attributed or removed. |
| Test coverage | Fail: all three independent failure probes pass outside the committed suite. |
| Dependencies | Pass: no new external dependency. |
| SPEC/ticket compliance | Fail: AC-02/07 and Ticket-01 recovery/matrix requirements are not met. |

## Rework-3 required next rework

The rework-3 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick or reuse of `c91041a` / `ba74caf`. Receipt `rcpt_local_orchestration_install_01_20260808` continues; no second dispatch confirmation is valid. The new allocation is limited to CR-40, CR-44 and CR-45 with fresh behavior-specific red evidence.

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
