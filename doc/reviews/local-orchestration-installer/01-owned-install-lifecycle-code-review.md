# 01 Owned Install Lifecycle — Code Review

| Field | Value |
| --- | --- |
| Feature / ticket | `local-orchestration-installer` / `01-owned-install-lifecycle` |
| SPEC / change | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` / `CHG-20260808-011` |
| Reviewed baseline | `88412e1` |
| Implementation / docs handoff | `71c6704` / `ffeea79` |
| Implementation owner | Codex implementation Agent / `codex/implementation-local-install-lifecycle-01-rework-12` |
| Reviewer | Codex / current `main` worktree |
| Result | `CHANGES_REQUESTED` |

## Traceability

- Approved Context: `doc/context/local-orchestration-installer/main.md`.
- Ticket scope: typed owned ledger, fake lifecycle ports and fail-closed install/uninstall only; no real host configuration, target project, Git adapter or package artifact is reviewed as delivered.
- Receipt `rcpt_local_orchestration_install_01_20260808` remains valid. The review result blocks the rework-12 implementation branch as historical evidence; it does not alter the approved SPEC, ticket scope or the planning lane's Ticket-02 dependency wait.

## Rework-12 review result

The submitted branch separates `FINALIZE_INTENT` from `FINALIZE_OBSERVED`, retains root authority for the submitted owner-release and recovery-write fault cases, and independently reproduces its 140-test / 233-subtest regression, strict mypy, in-memory compile, source sentinel, Git-isolation and clean-diff evidence. It remains `CHANGES_REQUESTED`: a returned host receipt that differs from deterministic intent is never recorded for cleanup; a shape-valid forged pre-delete intent deletes the authoritative ledger before proving terminal absence; ownerless live ledgers are reported as `NOT_INSTALLED`; and an ownerless forged install-cleanup record is accepted as deletion authority.

### CR-69 — P0: actual registration receipt mismatch creates an unreachable live effect

After `host.register` returns, `_new_install` compares the actual receipt with the deterministic expected receipt and immediately invokes `_cleanup_install(prepared)` on mismatch (`library/local_orchestration/lifecycle.py:111-117`). `prepared.receipts` contains only deterministic expected receipts, so cleanup cannot name or remove a different returned actual receipt. The cooperative fake never returns a mismatch (`library/local_orchestration/fakes.py:152`), and the committed suite has no actual-receipt mismatch provider.

An independent adapter returned a schema-valid receipt with a different host and registration ID while registering that exact actual effect. The first and second calls both returned `INSTALL_BLOCKED/HOST_PROOF`; the actual registration remained live while owner, ledger and recovery were all absent. Required correction: persist a deterministic pre-registration intent before the call, then durably bind every returned actual receipt to that intent before any later fallible verification/cleanup. Every field mismatch and retry must remove the exact actual effect or retain exact cleanup authority; expected receipt cleanup cannot substitute for actual-effect observation.

### CR-70 — P0: forged `FINALIZE_INTENT` destructively deletes the ledger before absence is proven

Any structurally valid `FINALIZE_INTENT` is routed directly to `_finish_finalize_intent` (`lifecycle.py:195-199`). That function accepts either a matching ledger or ledger absence, constructs a deterministic deletion target, deletes the ledger, and only afterwards calls filesystem/host absence ports (`lifecycle.py:234-250`). A forged intent therefore performs an irreversible authority mutation before its claimed causal predecessor effects are established.

An independent probe installed live files and one host receipt, replaced recovery with a fully schema-valid `FINALIZE_INTENT`, and called uninstall. It returned `UNINSTALL_BLOCKED/PORT_FAILURE`, but the ledger was deleted while owner/recovery and the live effects remained. Every retry repeated the same blocked result permanently. Required correction: a durable intent must be bound to an exact prior state-machine transition that cannot be reconstructed from predictable manifest data alone. Before ledger deletion, freshly prove runtime/process stopped plus exact host/filesystem absence and exact owner/ledger/recovery identity. Deletion proof/read-back may advance only that authenticated transition.

### CR-71 — P0: ownerless durable authority is treated as terminal absence

When no active recovery exists, `_uninstall` returns `NOT_INSTALLED/ABSENT` solely because `root_owner()` is `None`, before reading the ledger (`lifecycle.py:176-186`). An independent probe retained the exact ledger, file and host receipt but removed only the root owner; uninstall returned `NOT_INSTALLED`, leaving all durable/live effects untouched. This is false terminal success and prevents the caller from distinguishing clean absence from orphaned authority.

Required correction: terminal absence must be a conjunction of no owner, no ledger, no recovery and freshly observed no owned host/filesystem effects. Any ownerless ledger/recovery or observed live effect is a typed fail-closed repair state, never `NOT_INSTALLED`.

### CR-72 — P0: ownerless forged install cleanup is accepted as destructive authority

`_cleanup_install` explicitly accepts `owner is None` when the active recovery equals the supplied install recovery (`lifecycle.py:128-134`). It then removes all named host/filesystem effects and the ledger before clearing recovery (`lifecycle.py:136-170`). An independent probe installed normally, replaced recovery with an exact-shaped `INSTALL_CLEANUP`, removed only the owner, and injected a later clock fault. The next install returned `INSTALL_BLOCKED/CLOCK_CHECKPOINT` after deleting the original file, host receipt, ledger and recovery.

Required correction: no cleanup effect may run without the exact fixed-root owner and a causal recovery record tied to the actual effects. Ownerless recovery is a repair-required authority fault; it may be observed and reported but not used as deletion capability. Prove the owner/manifest/receipt/ledger/recovery tuple again immediately before each effectful cleanup transition.

### CR-40 remains open — retained adversarial coverage regressed again

The fresh suite contains eight test methods. Its forged-finalize test covers `FINALIZE_OBSERVED`, not the destructive `FINALIZE_INTENT` path; `TypedHost.register` always returns the expected receipt; uninstall tests do not cover ownerless ledger/live-effect state; and cleanup tests do not cover ownerless forged recovery. The suite also substantially reduces the retained one-fault and boundary surface from earlier accepted reworks. The handoff claim that CR-59 through CR-65 were preserved is therefore unsupported by committed tests.

## Rework-12 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `88412e1 -> 71c6704 -> ffeea79`; implementation worktree clean |
| `git diff --check 88412e1..ffeea79` | Passed |
| `python -m unittest discover -s tests` | 140 passed |
| `python -m pytest -q` | 140 passed / 233 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 72 source files clean |
| In-memory compile / source sentinel | 54 library modules compiled; submitted sentinel passed |
| Actual registration receipt mismatch probe | Failed: repeated `INSTALL_BLOCKED/HOST_PROOF`; actual host effect live; owner/ledger/recovery absent |
| Forged `FINALIZE_INTENT` probe | Failed: repeated `UNINSTALL_BLOCKED/PORT_FAILURE`; ledger deleted while owner/recovery and live file/host remained |
| Ownerless ledger probe | Failed: returned `NOT_INSTALLED/ABSENT` with exact ledger, file and host receipt still live |
| Ownerless forged install-cleanup probe | Failed: deleted original file, host receipt, ledger and recovery without exact owner authority |
| Worktree non-interference | Probes used `python -B` with bytecode writes disabled; final implementation worktree clean |

## Rework-12 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: DTOs and ports are named, but causal transition authority is reconstructible from predictable values. |
| Coding/architecture rules | Partial pass: DI and fixed-root concepts exist; returned actual effects and orphaned authority are not represented durably. |
| Logic correctness | Fail: CR-69 strands a live effect, CR-70 destroys ledger authority, CR-71 returns false terminal absence and CR-72 performs ownerless deletion. |
| Boundary and exception behavior | Fail: valid-shaped persisted states reach destructive or false-success branches instead of finite repair states. |
| Security and ownership isolation | Fail: ownerless recovery acts as a deletion capability and ownerless live authority is hidden as absent. |
| Test coverage | Fail: CR-40 omits all four independently reproduced sequences and the retained full matrix. |
| Dependencies | Pass: no new runtime dependency. |
| SPEC/ticket compliance | Fail: AC-06/07/08 and retained CR-54/59/63 guarantees remain incomplete. |

## Rework-12 required next rework

The rework-12 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick, source copy or reuse of `71c6704` or `ffeea79`. Receipt `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` continue; no second dispatch confirmation is valid.

The next allocation must retain the submitted CR-66 through CR-68 corrections while restoring durable actual-receipt authority, non-forgeable causal pre-delete transitions, conjunction-based terminal absence and exact-owner authorization before every cleanup effect.

## Rework-11 review result

The submitted branch restores one exclusive fixed-root owner, recursively revalidates the covered command/path models, verifies live install effects and consumes the cooperative terminal proofs exercised by its suite. Its 149-test regression, 262 pytest subtests, strict mypy, in-memory compile and source sentinel are independently reproducible. It remains `CHANGES_REQUESTED`: a shape-valid but non-causal `FINALIZE` record still erases all authority while live files and registrations remain; install cleanup can clear its only recovery record before owner release is proven; and a mismatched recovery-write proof can release the owner after the recovery was durably written.

### CR-66 — P0: asserted `FINALIZE` evidence is accepted as causal post-delete proof

`Recovery.FINALIZE` requires fields whose values are deterministic from the manifest and receipts (`library/local_orchestration/contracts.py:159-192`). `_uninstall` routes any structurally valid `FINALIZE` directly to `_complete_finalize`, which deletes the ledger, releases the fixed root and clears recovery without re-observing runtime, process, host or filesystem absence (`library/local_orchestration/lifecycle.py:226-235,297-317`). The stored `ledger_delete_proof` is also the expected proof written before ledger deletion (`lifecycle.py:284-295`), not the actual returned proof durably checkpointed after deletion.

An independent probe installed one live host and file, replaced recovery with a fully valid `FINALIZE` containing all expected proof/absence values, then called uninstall. The result was `REMOVED`; the live file and host registration remained, while owner, ledger and recovery were all `None`. Required correction: model pre-delete intent and post-delete observation as distinct causal states, durably persist the exact returned ledger-deletion proof only after read-back confirms absence, and re-observe exact runtime/process/host/filesystem terminal absence before discarding root authority. A predictable assertion must never substitute for an observed transition.

### CR-67 — P0: install cleanup clears recovery before owner release is proven

`_cleanup_install_exact` clears the exact recovery at `lifecycle.py:219` and only then calls `release_root`; that return is compared but the root owner is not read back (`lifecycle.py:221-224`). When stage returns a foreign proof and owner release also returns a foreign proof, the independent probe returned `INSTALL_BLOCKED/INSTALL_CLEANUP_PENDING` with the root still owned, but ledger and recovery absent. Every retry then returned `INSTALL_BLOCKED/OWNER_WITHOUT_AUTHORITY`.

Required correction: make cleanup terminalization a root-scoped, durable transition that survives either recovery-clear or owner-release failure. No ordering may expose an owner without recovery/ledger or an ownerless recovery to another installation. Exact owner-release proof plus root-owner read-back is mandatory, and every one-step foreign/replayed/no-op/exception outcome must converge on retry.

### CR-68 — P0: a mismatched recovery-write proof can orphan the persisted recovery

`_write_recovery` correctly compares proof and read-back (`lifecycle.py:379-383`), but `_new_install` treats any false result as if no recovery exists and immediately releases the root (`lifecycle.py:92-95`). An injected adapter persisted `INSTALL_PREPARED` and returned the same typed proof with `replay=1`. The first call returned `INSTALL_BLOCKED/PREPARE_CHECKPOINT`, released the owner and retained the recovery; the second returned `INSTALL_BLOCKED/ORPHANED_AUTHORITY` permanently.

Required correction: branch on the authoritative read-back after every write/checkpoint mismatch. If exact recovery was persisted, retain the fixed-root owner and resume it; if nothing was persisted, release only after exact absence and owner-release proof/read-back. Cover foreign, replayed, no-op and exception results for every recovery-write phase, not only recovery clear.

### CR-40 remains open — required retained adversaries are not in the committed suite

The fresh suite tests malformed `FINALIZE` with missing evidence, owner-release faults only on the normal uninstall terminal path, and recovery-clear proof faults. It does not test a fully valid forged `FINALIZE` with live effects, owner-release proof failure during install cleanup, or recovery-write foreign/replayed/no-op proof after persistence. The implementation return's claim that all terminal/checkpoint effects have exact proof plus read-back validation is therefore not supported by the committed tests.

## Rework-11 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `50b0591 → f17da74 → 8193067 → 95ec79a`; implementation worktree clean |
| `git diff --check 50b0591..95ec79a` | Passed |
| `python -m unittest discover -s tests` | 149 passed |
| `python -m pytest -q` | 149 passed / 262 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 72 source files clean |
| In-memory compile / source sentinel | 54 library modules compiled; no `type: ignore`, `Any`, dynamic attribute or eval/exec shortcut in the delivered surface |
| Exact-shaped live-effect `FINALIZE` probe | Failed: returned `REMOVED`, retained one live host and the file, cleared owner/ledger/recovery |
| Install-cleanup owner-release probe | Failed: first `INSTALL_CLEANUP_PENDING`, retry permanent `OWNER_WITHOUT_AUTHORITY` |
| Persisted recovery-write replay probe | Failed: first `PREPARE_CHECKPOINT`, retry permanent `ORPHANED_AUTHORITY` |
| Worktree non-interference | Generated Python caches were removed by the implementation owner; final worktree clean |

## Rework-11 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: named DTOs/ports exist, but `FINALIZE` evidence is an asserted predictable value rather than a causal observation. |
| Coding/architecture rules | Partial pass: DI and root exclusivity exist; terminal state cannot atomically retain authority through checkpoint failures. |
| Logic correctness | Fail: CR-66 returns false `REMOVED`; CR-67/68 create permanently non-resumable states. |
| Boundary and exception behavior | Fail: exact-shaped persisted state and typed proof mismatch do not remain fail-closed and retryable. |
| Security and ownership isolation | Fail: forged terminal evidence can discard all ownership while owned effects remain live. |
| Test coverage | Fail: CR-40 omits all three independently reproduced state/proof sequences. |
| Dependencies | Pass: no new runtime dependency. |
| SPEC/ticket compliance | Fail: AC-06/07/08 and the retained CR-50/58/63/65 guarantees are incomplete. |

## Rework-11 CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | Submitted raw/constructed canonical-path matrix passes. |
| 2 | null / empty / containers | Submitted public and persisted-state boundary cases pass. |
| 3 | Authorization bypass | Fail: CR-66 accepts asserted terminal evidence as deletion/release authority. |
| 4 | Token format/comparison | N/A by ticket; source sentinel passes. |
| 5 | Error-code consistency | Fail: CR-66 returns false success and CR-67/68 return permanent blocked states rather than retry convergence. |
| 6 | Exception propagation | Public exceptions are finite, but proof/checkpoint failures corrupt the recoverable state invariant. |
| 7 | Tests cover described behavior | Fail: the three independent probes are absent from the committed suite and contradict the handoff claim. |

## Rework-11 required next rework

The rework-11 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick, source copy or reuse of `f17da74`, `8193067` or `95ec79a`. Receipt `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` continue; no second dispatch confirmation is valid.

The next allocation must preserve CR-59 through CR-65's passing direct guards while adding causal post-delete terminal evidence, retry-safe cleanup terminalization and authoritative recovery-write mismatch handling for CR-66 through CR-68.

## Rework-10 review result

The submitted branch corrects the direct CR-59 receipt-mismatch cleanup, compares exact stage/completion/host proofs on its cooperative adapters, and recursively revalidates the constructed values covered by its focused suite. Its 151-test regression, 242 pytest subtests and strict mypy result are independently reproducible. It remains `CHANGES_REQUESTED`: the fresh implementation regresses the already-retained exclusive fixed-root owner and causal recovery invariants, accepts non-canonical owned locators that execute effects or throw, and discards typed terminal proofs.

### CR-62 — P0: two installations can own and corrupt the same fixed root

`_new_install` claims ownership only by `InstallationId` and never acquires one authoritative owner for the fixed root (`library/local_orchestration/lifecycle.py:140-153`). `TypedOwnership` stores owners, ledgers and recovery independently per installation while `TypedFilesystem` writes every manifest into the same root (`fakes.py:192-225,361-419`). This reopens the retained CR-43 exclusive-owner requirement.

An independent two-ID probe installed `inst-alpha` and `inst-beta` with the same owned path. Both returned `INSTALLED`, two owners and two host effects existed, and uninstalling alpha returned `REMOVED` while deleting beta's shared file. Beta then returned `INSTALL_BLOCKED` with its host/ledger still present. Required correction: atomically bind the fixed root to exactly one installation across normal install, recovery and retry; a second valid installation must fail before filesystem/host effects and may not be admitted until the exact first lifecycle is absent.

### CR-63 — P0: recovery phase and intent evidence are not causally bound to the success ledger

`Recovery` checks only same-installation manifest/owner and that an observation names one listed intent (`contracts.py:175-193`). It does not bind every intent's expected receipt to the manifest/selected host, require the observation tuple to be unique and complete, or prove that `FINALIZE` was reached through exact prior phases. `_recovery_matches_ledger` compares only owner, manifest and actual-receipt tuple (`lifecycle.py:384-390`), while `_cleanup_install_recovery` deletes host/files before checking the active owner (`lifecycle.py:213-240`) and `FINALIZE` skips ledger comparison (`lifecycle.py:285-318`).

Three independent probes reproduced destructive bypasses. A foreign intent ID paired with the exact ledger receipt returned `REMOVED`, retained one live host registration and cleared owner/ledger/recovery. A forged `INSTALL/CLEANUP` recovery with a foreign owner deleted the real host and files before returning `PROOF_MISMATCH`. A forged `UNINSTALL/FINALIZE` recovery naming absent foreign subjects returned `REMOVED`, left the real host and files live, and discarded all authority. Required correction: encode legal operation/phase/evidence combinations, validate every expected-intent/actual observation against the exact ledger and selected hosts, and require exact active owner plus ledger/recovery identity before every cleanup/finalize effect. Ledger absence may be accepted only with a durable, exact post-delete checkpoint.

### CR-64 — P0: owned-path canonical validation permits effectful URI/drive/dot variants

`OwnedPath.must_be_canonical_relative` rejects a few substrings but accepts `.`, `./owned/router.json`, `C:/escape` and `file:escape` (`contracts.py:58-73`). Independent calls with `.` and `C:/escape` raised uncaught `ValueError` after owner/recovery/clock effects; `./owned/router.json` and `file:escape` returned `INSTALLED`. This violates the ticket's zero-effect path boundary and finite public result contract and leaves the CR-61 path/URI extension incomplete.

Required correction: define one parsed canonical-relative path value that rejects empty/dot segments, drive or scheme prefixes, absolute/UNC/device paths, alternate separators, encoded separators/traversal and non-normalized equivalents before the first port call. Add raw and `model_construct` cases plus reverse validation.

### CR-65 — P0: terminal lifecycle proofs are returned but discarded

Uninstall ignores both `RuntimeStopProof` and `ProcessStopProof` (`lifecycle.py:294-297`). Install and uninstall also discard the returned `Recovery` from `clear_recovery` (`lifecycle.py:184,237,317`), and install cleanup discards the returned ledger proof from `delete_ledger` (`lifecycle.py:232`). A typed runtime adapter that returned a proof for `inst-foreign` without stopping its live state still produced `REMOVED` and cleared owner/ledger. A typed ownership adapter whose `clear_recovery` was a no-op returned `INSTALLED` with durable install recovery still present.

Required correction: compare every effect-bearing return with the exact requested installation, owner, manifest, receipt, operation and expected absence/checkpoint before discarding authority. Unavailable, foreign, replayed or no-op proof must return a finite blocked state that preserves a safe retry.

### CR-40 remains open — retained guards are missing from the fresh regression surface

The submitted suite directly covers CR-59/60/61 and cooperative terminal faults, but it does not preserve the ticket's already-recorded CR-41/42/43 recovery and exclusive-root adversaries, canonical owned-locator matrix, or untrusted terminal-proof providers. Passing the suite therefore does not prove the stated preserved surface.

## Rework-10 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `85b7e96 → ea99ccc → 415f2bd`; both worktrees clean |
| `git diff --check 85b7e96..415f2bd` | Passed |
| `python -m unittest discover -s tests -v` | 151 passed |
| `python -m pytest -q -p no:cacheprovider` | 151 passed / 242 subtests |
| `python -m mypy --strict --no-incremental library tests` | 73 source files clean |
| In-memory compile | 54 library modules passed |
| Two-ID fixed-root probe | Failed: both installed; removing alpha deleted beta's file and left beta blocked |
| Forged intent / recovery probes | Failed: terminal success or destructive blocked result occurred outside exact causal authority |
| Owned locator probes | Failed: dot/drive values threw after three effects; relative-dot and scheme-like values installed |
| Runtime / recovery-clear proof probes | Failed: terminal success accepted foreign/no-op typed proof |
| Worktree non-interference | Independent verification left both worktrees clean |

## Rework-10 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: DTOs are named, but recovery invariants and terminal proof consumption are incomplete. |
| Coding/architecture rules | Partial pass: DI remains; the fixed-root owner is modeled per installation rather than per exclusive root. |
| Logic correctness | Fail: CR-62/63 produce cross-install corruption, live-effect residue and false terminal success. |
| Boundary and exception behavior | Fail: CR-64 accepts non-canonical locators and lets `ValueError` escape after effects. |
| Security and ownership isolation | Fail: forged recovery and ignored proof identities can discard exact authority while effects remain live. |
| Test coverage | Fail: CR-40 omits retained exclusive-root/recovery/path/proof adversaries. |
| Dependencies | Pass: no new runtime dependency. |
| SPEC/ticket compliance | Fail: AC-01/03/06/07/08 and retained CR-41/42/43 are incomplete. |

## Rework-10 CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | Fail: owned dot/drive/scheme variants execute effects or escape. |
| 2 | null / empty / containers | Submitted cases pass; canonical owned-path variants remain incomplete. |
| 3 | Authorization bypass | Fail: fixed-root multi-owner and forged recovery paths bypass exact authority. |
| 4 | Token format/comparison | N/A by ticket; no credential comparison introduced. |
| 5 | Error-code consistency | Fail: invalid paths can throw; forged state can return false `REMOVED`. |
| 6 | Exception propagation | Fail: `ValueError` escapes after durable effects and typed no-op proofs are swallowed as success. |
| 7 | Tests cover described behavior | Fail: reverse/independent probes reproduce CR-62 through CR-65 outside the submitted suite. |

## Rework-10 required next rework

The rework-10 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick, source copy or reuse of `ea99ccc` / `415f2bd`. Receipt `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` continue; no second dispatch confirmation is valid.

The next allocation must retain the direct CR-59/60/61 corrections while restoring exclusive fixed-root ownership, causal recovery/phase evidence, complete canonical locator validation and exact consumption of every terminal typed proof.

## Rework-9 review result

The submitted branch consumes exact host/filesystem removal and absence proof identities and closes the cooperative CR-58 terminal retry sequence. Its 151-test regression, 279 subtests and strict mypy result are independently reproducible. It is nevertheless `CHANGES_REQUESTED`: four actual-receipt mismatch classes strand an untracked live registration, installation success ignores stage/completion and existing-effect verification, and an already-constructed invalid root bypasses boundary validation.

### CR-59 — P0: four receipt-mismatch paths strand a live effect outside recovery authority

`_handle_mismatched_registration` records the actual receipt only when installation, host, manifest digest and owned paths already match (`library/local_orchestration/lifecycle.py:298-321`). If any of those four fields differs, it immediately returns `INSTALL_BLOCKED/AUTHORITY_MISMATCH` without persisting the returned actual receipt or removing it. The precommitted recovery contains only the expected receipt.

Independent probes for installation, host, manifest and owned-path mismatches each produced a first `INSTALL_BLOCKED`, retained one live actual host registration, and left owner/recovery without authority matching that effect. The second call returned `INSTALL_BLOCKED/PROOF_MISMATCH`; the state remained permanently stranded. The submitted test explicitly accepts `registration_count == 1` for these four cases, so it proves the defect rather than the required cleanup.

Required correction: persist a strongly typed expected-intent/actual-observation association for every returned receipt before cleanup, including all one-field mismatches. Cleanup must act on the exact actual effect created by that call, retain authority through every checkpoint failure and converge without deleting unrelated effects. Preserve the complete CR-56 one-field matrix; no mismatch may leave an unreachable registration.

### CR-60 — P0: `INSTALLED` does not require exact stage/completion or live-effect proof

The fresh install path discards both `StageProof` and `CompletionProof` values (`lifecycle.py:131-133`). The existing-ledger success check `_is_completed_install` validates only structural DTO equality (`lifecycle.py:419-437`) and never asks filesystem or host ports to prove the manifest and receipts are live.

Two independent probes reproduced the failure. A typed filesystem returned shape-valid stage/completion proofs for a different installation while writing nothing; install returned `INSTALLED`, persisted a ledger and host registration, but the requested manifest was absent. Separately, after a valid install, removing the exact host and files outside the lifecycle while retaining the ledger caused a repeated install to return `INSTALLED` with zero host registrations and no files.

Required correction: compare every returned stage/completion proof with the exact requested manifest and require exact filesystem completeness plus every receipt's host verification before either new or existing-ledger `INSTALLED`. Wrong, unavailable or stale proof must return finite blocked state without treating the ledger as live. Add adversarial foreign-proof and stale-ledger tests plus reverse mutations.

### CR-61 — P0: constructed nested root bypass reaches effects and succeeds

`install` passes an existing `InstallCommand` directly through `TypeAdapter.validate_python` (`lifecycle.py:89-95`). Pydantic accepts its already-constructed nested models without revalidating the `InstallRoot` literal. An independent command using `InstallRoot.model_construct(value="ForeignRoot")` returned `INSTALLED` and executed ten port effects. This reopens the constructed-object boundary bypass previously closed by the rework-7 surface.

Required correction: explicitly revalidate all model instances from a strict primitive dump, or configure recursive instance revalidation at every nested domain boundary. Add constructed invalid root, installation, manifest, artifact/path, host and receipt tests asserting zero port calls; extend path/URI canonical variants as required by the ticket.

### CR-40 remains open — submitted tests omit or normalize the blocking behavior

The suite covers raw dictionaries and cooperative proof faults, but not nested `model_construct` instances, foreign stage/completion proofs, stale success-ledger effects, or cleanup of four non-registration receipt mismatches. The receipt test treats a retained live registration as expected. Passing the suite therefore cannot prove preserved CR-36/40/52/56 behavior.

## Rework-9 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `8ea2983 → 815d126 → 5405c24`; implementation worktree clean |
| `git diff --check 8ea2983..5405c24` | Passed |
| `python -m unittest discover -s tests -v` | 151 passed |
| `python -m pytest -q` | 151 passed / 279 subtests |
| `python -m mypy --strict library tests` | 75 source files clean |
| Four receipt-mismatch retry probes | Failed: live registration retained; retry remains `INSTALL_BLOCKED/PROOF_MISMATCH` |
| Foreign stage/completion proof probe | Failed: returned `INSTALLED` with requested files absent |
| Stale ledger/effects probe | Failed: returned `INSTALLED` with zero host registrations and files absent |
| Constructed invalid-root probe | Failed: returned `INSTALLED` after ten port effects |
| Worktree non-interference | Independent verification left the implementation worktree clean |

## Rework-9 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: proof DTOs are explicit; success proofs and actual mismatch observations are not completely consumed. |
| Coding/architecture rules | Partial pass: DI remains; application/live-state verification is incomplete. |
| Logic correctness | Fail: CR-59 strands returned effects and CR-60 reports installation for absent effects. |
| Boundary and exception behavior | Fail: CR-61 bypasses strict nested validation. |
| Security and ownership isolation | Fail: recovery cannot reach four effects it caused, while stale/foreign proof state is trusted. |
| Test coverage | Fail: CR-40 omits or accepts all reproduced paths. |
| Dependencies | Pass: no new runtime dependency. |
| SPEC/ticket compliance | Fail: AC-01/02/06/07/08 and the preserved rework-8 surface are incomplete. |

## Rework-9 CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | Fail: constructed invalid root bypasses validation and reaches effects. |
| 2 | null / empty / containers | Raw matrices pass; constructed nested values are not recursively revalidated. |
| 3 | Authorization bypass | Fail: stale ledger and foreign stage/completion proof can authorize `INSTALLED`. |
| 4 | Token format/comparison | N/A by ticket; source sentinel passes. |
| 5 | Error-code consistency | Finite codes are returned, but four receipt mismatches become permanent proof mismatch. |
| 6 | Exception propagation | Submitted port faults are contained; invalid constructed models are not fully normalized. |
| 7 | Tests cover described behavior | Fail: CR-59/60/61 are reproducible outside the submitted suite. |

## Rework-9 required next rework

The rework-9 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick, source copy or reuse of `815d126` / `5405c24`. Receipt `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` continue; no second dispatch confirmation is valid.

The next allocation must preserve the passing exact removal/absence proof and terminal retry guards while restoring full actual-receipt observation cleanup, live install proof verification and recursively strict constructed-input boundaries.

## Rework-8 review result

The submitted branch closes CR-54 through CR-56 on its cooperative adapters: pre-finalize uninstall recovery is matched to the exact success ledger, deterministic receipt intents are durable before registration, and complete receipt equality is enforced. The reported 151-test regression, 250 subtests and strict mypy result are independently reproducible. It is nevertheless `CHANGES_REQUESTED`: the application discards every returned removal/absence proof without checking that it proves the requested effect, and an install-cleanup checkpoint fault can strand recovery after owner release so every retry remains blocked.

### CR-57 — P0: foreign typed proofs authorize `REMOVED` while a host effect remains live

The port contracts return `RemovalProof` and `AbsenceProof`, but `_cleanup_install`, `_resume_uninstall` and `_finalize` ignore their values (`library/local_orchestration/lifecycle.py:195-198,240-251,267-274`). Consequently the application verifies neither proof owner nor registration/manifest subject before deleting the ledger, releasing the owner, clearing recovery and returning `REMOVED`.

An independent adversarial `HostPort` delegated install normally, then made `remove` a no-op that returned a shape-valid proof for `foreign-install/foreign-registration` and made `verify_absent` return a shape-valid foreign absence proof. Uninstall returned `REMOVED` with one host registration still live, while owner, ledger and recovery were all deleted. This violates AC-06/07 and the explicit exact owner/manifest/receipt/proof/absence boundary.

Required correction: every returned removal and absence proof must be strongly compared with the exact requested installation, registration and manifest/subject before any terminal authority is discarded. A missing, foreign, mismatched or replayed proof must produce finite `*_BLOCKED`, preserve owner/ledger/recovery, and permit a safe retry. Add adversarial typed-provider tests; cooperative fakes alone cannot prove this boundary.

### CR-58 — P1: install cleanup releases owner before a fallible recovery clear and cannot resume

`_cleanup_install` releases the active owner before clearing recovery (`lifecycle.py:204-205`). If `clear_recovery` fails, the durable install recovery remains but the owner is absent. `_install` treats owner absence plus any recovery as `AUTHORITY_MISMATCH`, so no subsequent call can consume or repair the state.

An independent probe skipped physical staging to enter cleanup and injected `CLEAR_RECOVERY` at the terminal substep. The first call returned `INSTALL_BLOCKED`; the second and third also returned `INSTALL_BLOCKED/AUTHORITY_MISMATCH`, with `owner=None` and recovery still present. This reopens CR-40/44 for a reachable declared-port ordering.

Required correction: checkpoint the terminal cleanup transition or order/compensate owner release and recovery clear so every single fault leaves a state a retry can recognize and converge. Add the exact clear-after-release red/green probe plus equivalent proof-validation failure/retry cases.

### CR-40 remains open — cooperative fault matrix misses terminal ordering and untrusted proof behavior

The submitted matrix injects individual enum faults and exercises the new CR-54/55/56 guards, but it does not inject `CLEAR_RECOVERY` after cleanup owner release and does not use a typed port returning mismatched proofs without performing the effect. Passing the current suite therefore cannot prove the ticket's clean-or-durable-retryable or exact-proof acceptance requirements.

## Rework-8 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `ed1a282 → 8a7b221 → 8f867cc`; implementation worktree clean |
| `git diff --check ed1a282..8f867cc` | Passed |
| `python -m unittest discover -s tests -v` | 151 passed |
| `python -m pytest -q` | 151 passed / 250 subtests |
| `python -m mypy --strict library tests` | 73 source files clean |
| Clear-after-release retry probe | Failed: repeated `INSTALL_BLOCKED/AUTHORITY_MISMATCH`, `owner=None`, recovery retained |
| Foreign typed proof probe | Failed: returned `REMOVED`, retained one live host registration, deleted owner/ledger/recovery |
| Worktree non-interference | Independent verification left the implementation worktree clean |

## Rework-8 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: proof DTOs are named, but their returned identities are never consumed. |
| Coding/architecture rules | Partial pass: DI/ports are preserved; application trust validation is absent at the effect boundary. |
| Logic correctness | Fail: CR-57 returns terminal success with a live effect; CR-58 cannot converge after a reachable fault. |
| Boundary and exception behavior | Fail: typed foreign proofs are accepted and terminal cleanup retry is stranded. |
| Security and ownership isolation | Fail: a provider can erase authoritative state without proving removal of the exact owned effect. |
| Test coverage | Fail: CR-40 omits the two independently reproduced sequences. |
| Dependencies | Pass: no new runtime dependency. |
| SPEC/ticket compliance | Fail: AC-06/07/08 and exact owned removal remain incomplete. |

## Rework-8 CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | Existing fixed-root/path tests pass. |
| 2 | null / empty / containers | Existing public and persisted raw-state matrices pass. |
| 3 | Authorization bypass | Fail: CR-57 accepts foreign typed proof identity as terminal authority. |
| 4 | Token format/comparison | N/A by ticket; source sentinel passes. |
| 5 | Error-code consistency | Finite codes are returned, but CR-58 repeats a non-recoverable authority mismatch. |
| 6 | Exception propagation | Exceptions are contained; terminal state consistency is not. |
| 7 | Tests cover described behavior | Fail: CR-57/58 are reproducible outside the submitted suite. |

## Rework-8 required next rework

The rework-8 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick, source copy or reuse of `8a7b221` / `8f867cc`. Receipt `rcpt_local_orchestration_install_01_20260808` and bounded authority `PRG-20260809-042` continue; no second dispatch confirmation is valid.

The next allocation must preserve the passing rework-8 contract, CR-54/55/56 guards and full matrix while adding exact proof consumption plus recoverable install-cleanup terminal ordering.

## Rework-7 review result

The submitted branch restores the full strict contract/port surface, physically stages payloads, processes all selected hosts, returns finite public results, and supplies the requested boundary/fault/Git matrices. Its reported 150-test regression, 239 subtests, strict mypy, in-memory compilation and diff checks are independently reproducible. It is nevertheless `CHANGES_REQUESTED`: persisted recovery can authorize effects before it is matched to the success ledger, a host effect can occur before durable receipt authority exists, and receipt identity comparison omits the registration ID.

### CR-54 — P0: shape-valid tampered recovery deletes before ledger authorization

When an exact owner has a persisted recovery, `_uninstall_typed` immediately calls `_continue_uninstall` without first requiring the pre-delete recovery manifest and receipts to equal the success ledger (`library/local_orchestration/installation.py:217-220`). The `UNINSTALL_FILES` phase then deletes the recovery manifest (`installation.py:255-272`); the ledger comparison occurs only later in `_finalize_uninstall` (`installation.py:285-290`).

An independent probe installed the normal manifest, then supplied a shape-valid `UNINSTALL_FILES` recovery for the same installation ID but a different manifest targeting `foreign/tampered.txt`. Uninstall returned `UNINSTALL_BLOCKED`, but the foreign file had already been deleted and the filesystem's exact-owner staging record was removed. This directly violates the ticket's promise that foreign/tampered state causes no deletion and reopens the recovery-authorization part of CR-49.

Required correction: before any `UNINSTALL_HOSTS` or `UNINSTALL_FILES` effect, require a present, strictly loaded ledger whose installation ID, manifest and complete receipt tuple exactly match recovery. Ledger absence is legal only for the already-checkpointed `FINALIZE` post-ledger-delete retry. Add shape-valid manifest and receipt mismatch tests proving zero host/filesystem mutation.

### CR-55 — P0: host effect precedes durable recovery authority

Install invokes `HostPort.register` before adding the returned receipt to recovery and before persisting that checkpoint (`installation.py:147-159`). A registration may therefore exist when the following clock or recovery-write call fails. The public boundary returns `INSTALL_BLOCKED`, but the persisted recovery still has no receipt capable of locating or removing that live effect.

An independent adapter probe made the second `write_recovery` call fail after the host registration was stored. The result was `INSTALL_BLOCKED`; `HostPort.verify` proved the expected registration remained live, while the persisted recovery contained zero receipts. The committed fault matrix exercises only the first recovery-write/clock call before effects, so it does not detect this lost-authority sequence. This reopens CR-45.

Required correction: durably checkpoint the deterministic expected receipt before calling `register`, or use a typed idempotent registration operation whose failure can always be queried and removed by that precommitted identity. Test register-after-effect exception, post-register clock failure and post-register recovery-write failure; every result must be clean or retain exact retry authority.

### CR-56 — P1: exact receipt comparison omits registration identity

`_exact_selected_receipt` compares installation ID, host ID, manifest digest and owned paths but not `registration_id` (`installation.py:333-340`). A host adapter that returns the expected host/manifest/paths with a different registration ID therefore passes verification, is written to the ledger and causes `INSTALLED`.

The independent probe returned registration ID `unexpected-registration` with every other field valid. Install returned `INSTALLED` and persisted that unexpected ID. Required correction: compare the complete strongly typed receipt, including registration ID, and add a one-field-at-a-time mismatch matrix for installation, host, registration, manifest digest and owned paths.

### CR-40 remains open — required tests do not cover the blocking sequences

The new matrices substantially improve coverage, but they inject each enum fault only at its first reachable call. They do not cover the later recovery-write/clock positions after a host effect, shape-valid recovery-versus-ledger mismatches, or a registration-ID-only mismatch. The five mutation probes likewise omit these paths. Passing the current suite cannot prove the ticket's durable exact-authority guarantee.

Required correction: add behavior-specific red tests for CR-54 through CR-56, then keep the complete existing matrix and mutation guards. Every effect-producing call followed by a fallible checkpoint must be tested at that precise ordering boundary.

## Rework-7 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `5e772ec → 49a250e → aafe154`; implementation worktree clean |
| `git diff --check 5e772ec..aafe154` | Passed |
| `python -B -m unittest discover -s tests` | 150 passed |
| `python -B -m pytest -q -p no:cacheprovider` | 150 passed / 239 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 73 source files clean |
| In-memory library compile | Passed |
| Source sentinel | No broad-clear, `type: ignore`, dynamic `Any`, destructive filesystem or shell use in delivered lifecycle source; test-only subprocess is limited to Git non-interference snapshots |
| Registration-ID mismatch probe | Failed: returned `INSTALLED` with `unexpected-registration` |
| Shape-valid recovery mismatch probe | Failed: returned `UNINSTALL_BLOCKED` only after deleting the mismatched recovery target |
| Post-host checkpoint-fault probe | Failed: live host registration with zero receipts in persisted recovery |

## Rework-7 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Pass structurally; CR-55 shows durable identity is recorded too late. |
| Coding/architecture rules | Partial pass: DI and port layering are restored; transition ordering violates durable recovery authority. |
| Logic correctness | Fail: CR-54 mutates before authorization and CR-56 accepts a non-exact receipt. |
| Boundary and exception behavior | Fail: CR-55 loses returned-effect authority at later fallible checkpoints. |
| Security and ownership isolation | Fail: CR-54 permits deletion driven by shape-valid tampered recovery. |
| Test coverage | Fail: CR-40 lacks CR-54/55/56 ordering and mismatch paths. |
| Dependencies | Pass: no new runtime dependency. |
| SPEC/ticket compliance | Fail: AC-02/06/07/08 and exact owned removal are not fully delivered. |

## Rework-7 CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | Canonical root/path and physical containment tests pass. |
| 2 | null / empty / containers | Required public and persisted raw-state matrices pass. |
| 3 | Authorization bypass | Fail: CR-54 executes recovery effects before matching the authoritative ledger. |
| 4 | Token format/comparison | N/A by ticket; source sentinel passes. |
| 5 | Error-code consistency | Public calls return finite codes, but CR-55's code hides lost cleanup authority. |
| 6 | Exception propagation | Public exception containment passes; durable post-effect state does not. |
| 7 | Tests cover described behavior | Fail: CR-54/55/56 are reproducible outside the submitted suite. |

## Rework-7 required next rework

The rework-7 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick or reuse of `49a250e` / `aafe154`. Receipt `rcpt_local_orchestration_install_01_20260808` continues; no second dispatch confirmation is valid.

The next allocation must preserve all passing rework-7 contracts, matrices, physical staging, all-host processing, finite results, mutation guards and Git isolation while closing CR-54/55/56 with behavior-specific red evidence.

## Rework-6 review result

The submitted branch restores named domain contracts and injected ports, and its reported regression/type/compile checks are reproducible. It is nevertheless not the approved owned lifecycle: durable recovery is not written around ordinary install/uninstall effects, the filesystem fake can report a complete installation without writing the payload, only the first selected host is registered, and most declared port failures still escape the finite result contract. The branch is `CHANGES_REQUESTED` and must not be merged.

### CR-50 — P0: `FINALIZE` recovery discards authority while live effects remain

`OwnedLifecycle.uninstall` treats any exact-owner `FINALIZE` recovery with no success ledger as sufficient to release the owner, clear recovery and return `REMOVED` (`library/local_orchestration/lifecycle.py:50-56`). It does not verify the recovery-bound receipts are absent or the recovery-bound manifest is absent before destroying the only retry authority.

An independent shape-valid probe supplied an exact-owner `FINALIZE` recovery, no success ledger, a live fake host receipt and a live owned manifest. The call returned `REMOVED`, left both effects live, released the owner and cleared recovery. This violates AC-06/07 and reopens CR-49 through the full port surface.

Required correction: every recovery phase must encode and revalidate its exact owner, manifest, receipt, removal-proof and absence evidence. `FINALIZE` may release owner/clear recovery only after the host and filesystem ports prove all recovery-owned effects absent. A live or unverifiable effect must return a finite blocked result and retain retry authority.

### CR-51 — P0: ledger-delete fault escapes and makes residue non-retryable

The ordinary uninstall path removes hosts and files, then performs `delete_ledger`, `clear_recovery` and `release` as an unguarded statement sequence (`lifecycle.py:61-67`). It never writes an uninstall recovery checkpoint before those effects. `TypedOwnership.delete_ledger` even models the required post-delete fault by removing the ledger and then raising (`fakes.py:98-102`), but `uninstall` does not catch it.

The independent probe produced an uncaught `OSError`; the ledger and effects were gone, the owner remained active, no recovery existed, and the next call returned `NOT_INSTALLED`. This is the exact CR-46 lost-terminal-transition failure, not a successful retry implementation.

Required correction: persist an evidence-bearing uninstall checkpoint before each irreversible phase, return finite results for every ownership-store fault, and make retry converge to `REMOVED` without losing owner/recovery authority. No port exception may cross the use-case boundary.

### CR-52 — P1: `INSTALLED` is reported without staging physical payload

`TypedFilesystem.stage` records only an in-memory manifest (`fakes.py:25-28`); it does not write payload bytes below the fixed root. `complete` compares only that dictionary to the ledger (`fakes.py:30-31`) and never checks file existence or digest. The independent normal-install probe returned `INSTALLED` while `JohnnyAIWorkflow/owned/router.json` did not exist, and `complete` still returned true.

Required correction: the temporary-root filesystem adapter must physically stage every payload part, verify resolved-root containment, bytes/digest and complete manifest, and delete only those verified artifacts. `INSTALLED` is illegal until physical completeness and every host receipt are proven.

### CR-53 — P1: multi-host requests silently install only the first host

`install` selects `request.selected_hosts[0]` and writes a ledger with one receipt (`lifecycle.py:22-32`). A valid two-host request returned `INSTALLED` with one receipt. This violates AC-02's requirement that every selected host completes `register → verify → receipt` before success and prevents complete uninstall of the requested configuration.

Required correction: register every selected host, bind each actual receipt to its requested host and manifest, and roll back/recover the exact effects if any host fails. Add one-host, multi-host, mid-sequence failure and retry tests.

### CR-40 remains open — declared port and boundary matrix is still absent

The two delivered lifecycle test files contain fourteen tests. They validate root, installation-ID and owned-path model rejection plus selected focused behaviors, but they do not implement manifest/receipt absent-value matrices, an EffectJournal, individual owner/ledger/recovery/host/filesystem/runtime/process/clock faults, complete first-state/retry assertions, or existing/empty Git success/failure snapshots. The root and value tests only assert Pydantic exceptions/results; they do not assert all port invocation counts are zero.

The application also catches only the clock and combined runtime/process exceptions. An independent `FilesystemPort.stage` fault propagated `OSError`; the same unguarded pattern exists around ownership, host and finalization operations. Passing the repository's existing 146 tests therefore does not prove the ticket's required failure surface.

Required correction: implement the exact CR-40 matrix from the approved ticket and rework-6 handoff. Each injected operation must have a named typed fault, finite result, complete owner/ledger/recovery/host/filesystem state assertion and retry terminal outcome. Record first-red test names/reasons before correcting each behavior.

## Rework-6 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `263e30c → e6b067c → f1301be`; implementation worktree clean |
| `git diff --check 263e30c..f1301be` | Passed |
| `python -B -m unittest discover -s tests` | 146 passed |
| `python -B -m pytest -q -p no:cacheprovider` | 146 passed / 195 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 72 source files clean |
| `python -B -m compileall -q library` | Passed |
| FINALIZE live-effect probe | Failed: returned `REMOVED`, retained host/files, cleared owner/recovery |
| Post-ledger-delete fault/retry probe | Failed: uncaught `OSError`; retry returned `NOT_INSTALLED` with owner stranded |
| Physical staging probe | Failed: returned `INSTALLED` while payload path was absent; fake `complete` returned true |
| Two-host probe | Failed: returned `INSTALLED` with one receipt |
| Filesystem stage-fault probe | Failed: uncaught `OSError` |

## Rework-6 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Partial pass: contracts/ports are named; public bool faults and missing durable transition contracts remain. |
| Coding/architecture rules | Fail: use case does not drive its declared recovery state through irreversible effects. |
| Logic correctness | Fail: CR-50/51 report removal/absence while cleanup authority or owner state is inconsistent. |
| Boundary and exception behavior | Fail: CR-40 and stage-fault probe show uncaught port exceptions and missing matrices. |
| Security and ownership isolation | Fail: CR-50 destroys exact-owner recovery authority before proving effects absent. |
| Test coverage | Fail: mandatory manifest/receipt, port-fault/retry and Git non-interference matrices are absent. |
| Dependencies | Pass: no new external dependency. |
| SPEC/ticket compliance | Fail: AC-01/02/06/07/08 are not fully delivered. |

## Rework-6 CodeReview §2.1 defect audit

| # | Category | Result |
| --- | --- | --- |
| 1 | Path-prefix mismatch | Contract variants are checked; physical resolved-root containment is not proven because install writes no file. |
| 2 | null / empty / containers | Installation ID and owned path covered; required persisted manifest/receipt matrices absent. |
| 3 | Authorization bypass | Fail: CR-50 clears recovery/owner without proof that recovery-bound effects are absent. |
| 4 | Token format/comparison | N/A by ticket; no authentication token is introduced. |
| 5 | Error-code consistency | Fail: CR-51 and stage-fault probe propagate exceptions instead of finite codes. |
| 6 | Exception propagation | Fail: most injected ports are unguarded. |
| 7 | Tests cover described behavior | Fail: passing suite omits required matrices and all five independent failures. |

## Rework-6 required next rework

The rework-6 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick or reuse of `e6b067c` / `f1301be`. Receipt `rcpt_local_orchestration_install_01_20260808` continues; no second dispatch confirmation is valid.

The next allocation must first establish the complete required tests and behavior-specific red evidence, then implement a durable phase machine over the existing strict contracts and ports. It must close CR-40/46/50/51/52/53 while preserving CR-36/37/38/39/41/42/43/48/49 guards. The return again requires implementation commit(s), full independent-verifiable evidence and a final docs-only handoff.

## Rework-5 review result

The four focused tests pass inside the submitted model, but the model is not the approved Ticket-01 lifecycle. The implementation replaces the port-driven owned installer with a 93-line mutable-memory simulation and four tests. Consequently it cannot close CR-40, CR-46 or reopened CR-38/42/43 against the actual acceptance surface.

### CR-47 — approved lifecycle and DI surface was replaced by a toy model

The approved ticket requires a fixed `InstallRoot`, typed payload/manifest/digests and owned paths, host-issued registration/removal/absence evidence, filesystem/ownership-ledger/host/runtime/process/clock ports, injected adapters, target-repository isolation and finite install/uninstall results. Submitted `library/local_orchestration` contains only `contracts.py`, `lifecycle.py` and `__init__.py`; there is no `ports.py`, `fakes.py`, payload, manifest digest, owned-path proof, removal proof, host absence, process/runtime boundary or filesystem boundary.

`Lifecycle` directly mutates public `Memory` sets/dictionaries (`library/local_orchestration/lifecycle.py:11-19,22-24`). `_ARTIFACT` and `_HOST` are hard-coded globals (`lifecycle.py:7-8`). The public install API accepts only an installation ID (`lifecycle.py:26`), so it cannot validate version, selected hosts, payload, manifest, fixed root or caller-visible host results. The test suite contains four in-memory tests and no filesystem/Git sandbox, adapter failure matrix or one-click owned-root smoke.

This is a silent public-contract, architecture and acceptance reduction by the implementation owner, not an approved requirement change. Required correction: rebuild the full approved Ticket-01 domain/application/port surface and tests in the fresh branch. A small state machine may coordinate the ports, but it cannot replace them or expose mutable infrastructure state as the application contract.

### CR-40 remains open — four tests do not implement the mandatory matrix

The handoff itself reports only four focused tests. There is no seven-case fixed-root matrix; no five-form matrix for installation ID, manifest, host receipt and owned path; no direct/indirect deletion authority cases; and no individual fault injection for owner, ledger, recovery, host, filesystem, runtime, process and clock boundaries. No representative existing/empty Git repository is created or snapshotted.

The recorded red evidence also covers only the four simplified behaviors. It cannot establish red/green ordering for the complete Ticket-01 behaviors required by the handoff. Required correction: every named boundary and port row in Ticket 01 and rework-5 handoff must have a first-red name/reason, full state assertions, retry terminal outcome where applicable, and target-repository non-interference.

### CR-48 — invalid installation IDs have inconsistent and exception-throwing behavior

`install()` checks only `isinstance(str)` plus `startswith("inst_")` (`library/local_orchestration/lifecycle.py:26-28`), then constructs Pydantic models without catching `ValidationError`. `uninstall()` checks only `isinstance(str)` (`lifecycle.py:57-59`). `Result.installation_id` is an unconstrained `str` (`contracts.py:63-66`).

Independent matrix results:

- `install("inst_")` and `install("inst_nothex")` raise uncaught `ValidationError`;
- `uninstall("inst_")`, `uninstall("inst_nothex")`, `uninstall("bogus")` and `uninstall("")` return `NOT_INSTALLED`;
- non-string containers return finite invalid results after being stringified into the output identifier.

The same invalid identity therefore throws, reports absence or reports invalid depending on entrypoint/shape. This violates P0 strong typing, AC-03 and the stable-error/exception matrix. Required correction: validate one opaque `InstallationId` boundary identically before every state read/effect, never stringify rejected caller objects into a typed result, and add all null/omitted/empty/whitespace/container/malformed-format cases for both operations.

### CR-49 — recovery can delete effects and release a foreign owner

`Recovery` has no operation/phase invariant beyond enum membership (`contracts.py:55-60`). `install()` invokes `_compensate()` for any install recovery (`lifecycle.py:29-34`), while `uninstall()` invokes `_finish()` for any uninstall recovery regardless of phase (`lifecycle.py:60-65`). Both helpers unconditionally clear the global owner and named physical effects without proving the owner equals the recovery installation (`lifecycle.py:75-89`).

Two independent shape-valid probes set owner to ID B and inserted an ID-A recovery:

- an uninstall recovery with phase `ROLLBACK` returned `REMOVED`, deleted the artifact/receipt and cleared ID B's owner;
- an install recovery with phase `FINALIZE` returned `INSTALL_BLOCKED / RECOVERY`, but still deleted the artifact/receipt and cleared ID B's owner.

This is a direct cross-installation authority bypass and proves the focused CR-38/46 tests do not cover reachable recovery phases. Required correction: encode valid operation/phase/evidence combinations in immutable types; before every compensation/finalization effect require exact active owner, ledger/recovery identity, receipt/path evidence and live/absence checks through injected ports. Invalid or foreign recovery must halt with zero mutation.

### Reopened CR-38/42/43 and CR-46 are not proven on the approved surface

- CR-46's `fail_after_ledger_delete` flag mutates one in-memory dictionary; no ledger/checkpoint port split exists, so it cannot prove durability or idempotency across injected persistence failures.
- CR-38 blocks install on an uninstall recovery in this toy route, but CR-49 shows unsupported phases still execute destructive helpers and there is no real ledger/physical verification path.
- CR-42 varies only `host_id` while `live_receipts` stores registration-ID strings (`lifecycle.py:47-52`); the returned mismatch uses the same registration ID, so it does not model a distinct actual host effect, owned paths, proof or absence verification.
- CR-43 tests only changing `state.owner`; it does not inject a second typed ledger/receipt and cannot validate fixed-root files or host effects because those ports/contracts do not exist.

Required correction: reproduce the exact four rework-4 probes through the full port-driven lifecycle, not through a reduced substitute.

## Rework-5 independent verification

| Check | Result |
| --- | --- |
| Branch ancestry / cleanliness | `14be507 → a3dc5a2 → 7573a74`; implementation worktree clean |
| `git diff --check 14be507..a3dc5a2` | Passed |
| `python -B -m unittest discover -s tests` | 135 passed |
| `python -B -m pytest -q -p no:cacheprovider` | 135 passed / 175 subtests |
| `python -B -m mypy --strict --no-incremental library tests` | 69 source files clean |
| In-memory compile / privacy sentinels | 3 local-orchestration modules compiled; passed |
| Approved-surface inventory | Failed: ports/fakes, filesystem, manifest/digest, owned path, proofs/absence, process/runtime/clock boundaries absent |
| Invalid-ID probe | Failed: two malformed `inst_` strings throw; uninstall reports them `NOT_INSTALLED` |
| Foreign-owner uninstall-recovery probe | Failed: returned `REMOVED` and cleared foreign owner/effects |
| Foreign-owner install-recovery probe | Failed: blocked result still cleared foreign owner/effects |

## Rework-5 CodeReview standard check

| Requirement | Result / evidence |
| --- | --- |
| Clear and strongly typed | Fail: unconstrained result ID, weak prefix parsing and mutable public memory replace domain values/ports. |
| Coding/architecture rules | Fail: approved domain/application/DI architecture is absent. |
| Logic correctness | Fail: CR-49 permits cross-owner deletion; invalid IDs diverge by entrypoint. |
| Boundary and exception behavior | Fail: CR-40/48 demonstrate missing cases and uncaught validation. |
| Security and ownership isolation | Fail: recovery operation/phase can bypass owner authority. |
| Test coverage | Fail: four focused tests cannot cover or prove the approved ticket and exact handoff matrix. |
| Dependencies | Pass: no new external dependency. |
| SPEC/ticket compliance | Fail: AC-01/02/03/06/07/08 and the named Ticket-01 surface are not delivered. |

## Rework-5 required next rework

The rework-5 branch is blocked historical evidence. The implementation owner must start a fresh branch directly from the next control-plane docs-only handoff baseline, without reset, merge, rebase, cherry-pick or reuse of `a3dc5a2` / `7573a74`. Receipt `rcpt_local_orchestration_install_01_20260808` continues; no second dispatch confirmation is valid. The next allocation must restore the complete approved Ticket-01 surface first, then close CR-40, CR-46, CR-48, CR-49 and reopened CR-38/42/43 with exact behavior-first evidence.

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
