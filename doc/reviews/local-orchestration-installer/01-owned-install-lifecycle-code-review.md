# 01 Owned Install Lifecycle — Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `01-owned-install-lifecycle` |
| SPEC / change | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / `CHG-20260808-011` |
| Reviewed baseline | `8e8caf7` |
| Implementation / docs handoff | `010110a` / `7bc5fd5` |
| Implementation owner | Codex implementation Agent / `codex/implementation-local-install-lifecycle-01` |
| Reviewer | Codex / current `main` worktree |
| Result | `CHANGES_REQUESTED` |

## Traceability

- Approved Context: `doc/context/local-orchestration-installer/main.md`.
- Ticket scope: typed owned ledger, fake lifecycle ports and fail-closed install/uninstall only; no real host configuration, target project, Git adapter or package artifact is reviewed as delivered.
- Receipt `rcpt_local_orchestration_install_01_20260808` remains valid. The review result blocks only the current implementation branch; it does not alter the approved SPEC, ticket scope or the planning lane's Ticket-02 dependency wait.

## Findings

### CR-36 — P0: dynamic removal proofs cross the deletion boundary

`UninstallControlPlane._validate_removal_proofs` accepts `tuple[object, ...]` and reads fields with `getattr` in `library/local_orchestration/installation.py`. Any unvalidated object that happens to expose matching attributes can authorize the next deletion step. This directly violates the P0 rule against unvalidated dynamic objects across a domain boundary.

Required correction: `HostLifecyclePort.unregister_all` must return `tuple[HostRemovalProof, ...]`; the application boundary must reject non-`HostRemovalProof` values before comparison, preserve the typed reason and run no filesystem deletion. Add a red-first regression with a structurally matching non-Pydantic object.

### CR-37 — P1: removal proof does not prove the host registration is absent

The current check compares fields in a returned proof but never asks the host adapter to verify that the exact receipt-owned registration/payload is gone. A faulty adapter can remove nothing, return a field-matching proof and cause owned payload deletion. This breaks AC-06/07's required `unregister → verify absent` lifecycle.

Required correction: add a strongly typed post-removal verification port/result bound to the same installation/host/registration/owned paths. The uninstaller must require every verification before ledger/filesystem deletion; a plausible-but-nonremoving fake must result in `UNINSTALL_BLOCKED`, retain recovery state and leave the filesystem untouched.

### CR-38 — P1: failed rollback/deletion can lose the recovery authority

Install failure invokes `_safe_unregister` and discards its result; if cleanup fails after a host registration, the operation reports blocked but has no durable receipt/ledger for retry. On uninstall, the ledger is deleted before filesystem deletion; if deletion partially changes the owned root and ledger restoration fails, the code swallows that restoration failure. Both paths can leave installer-owned residue without a reliable recovery record, contrary to AC-07 and the one-click detachability requirement.

Required correction: make rollback and delete progress an explicit durable, typed recovery state. Do not swallow failed host cleanup or failed ledger restoration. Add failure injection after partial host cleanup and after partial filesystem deletion/ledger restoration; each must expose a unique finite reason, leave only verified owned recovery data, never report success and allow a safe retry.

## Independent verification

| Check | Result |
| --- | --- |
| `git diff --check 8e8caf7..010110a` | Passed |
| `python -B -m unittest discover -s tests` | 148 passed |
| `python -B -m pytest -q -p no:cacheprovider` | 148 passed / 175 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 71 source files clean |
| In-memory compile | 5 `local_orchestration` modules compiled |
| Metadata/privacy source scan | Passed; no raw Context/source/prompt sentinel in delivered source |
| TDD evidence | Handoff records an initial `ModuleNotFoundError` before implementation. It is credible for the initial module-creation behavior, but the CR-36/37/38 adversarial cases lack their required red-first tests. |

## CodeReview standard check

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

## CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | Partially covered by locator/root cases; no review approval while ownership proof is incomplete. |
| 2 | null / empty / containers | Covered at input/ledger boundaries. |
| 3 | Authorization bypass | **Fail**: CR-36/37 are direct and indirect removal-proof bypass paths. |
| 4 | Token format/comparison | N/A by ticket design; source scan found no credential/token storage or comparison. |
| 5 | Error-code consistency | Partially covered; CR-38 requires distinct durable-recovery codes. |
| 6 | Exception propagation | **Fail**: cleanup/restoration failures are intentionally swallowed without a durable recovery outcome. |
| 7 | Tests cover described behavior | **Fail**: required adversarial/mutation cases are absent. |

## Required rework handoff

The current branch is blocked historical evidence. The implementation owner must receive a fresh control-plane rework handoff, create a new branch from that recorded current `main` baseline, and repeat red → minimal implementation → green for CR-36 through CR-38. It must not reset, overwrite, cherry-pick or reuse `010110a` / `7bc5fd5`. After its independent implementation and docs-only handoff, it returns `COMPLETED` for another review; receipt `rcpt_local_orchestration_install_01_20260808` remains valid without a second user confirmation.
