# Ticket 05B4B2E4 Codex Registration Success Acceptance Code Review

## Revision-03 terminal review

`APPROVED / READY_TO_MERGE`

Revision-03 closes CR-165 and CR-166 without changing the immutable staging
source. The branch history-preservingly merges the project-owned runtime
foundation, then changes only the focused acceptance test and one WPR handoff.

| Field | Reviewer evidence |
| --- | --- |
| Reviewed chain | Existing E4 handoff `5cf2235` plus control registry `334757c` -> two-parent merge `55a12fdb9a1e071e7ccef1efbeaf3d1c6f42e71b` -> correction `dc909da63cbd1aaedf73877d47bbceaa5d7e2952` -> WPR-only handoff `63b84949b2a9c7dd27872a6c0f56aa02207ed65b`. |
| Exact scope | Merge resolves only the predicted WPR append conflict; correction changes only `tests/test_codex_registration_success_acceptance.py`; handoff changes only WPR. Original staging source blob remains `d5e4f0e66c5a5abd65eb7b937a4cce3c63092dc8`. |
| Fresh immutable export | PASS. Unicode library trees are present; focused `5/5`; full explicit serial discovery `419/419`; strict mypy `136/136`; in-memory compile `136/136`; external cache removed. |
| CR-165 | CLOSED. The clean child now requires exactly one owned marketplace/plugin and zero foreign records. Post-receipt foreign seeding/list evidence and its helpers/imports are absent; compensation remains E5 responsibility. |
| CR-166 | CLOSED. The committed test name now claims only executed child evidence. Reviewer surrounded the run with manifests for control and both permanent implementation worktrees; tracked byte digests, branches, HEADs, tracked/untracked and ignored porcelain were identical before/after. |
| S8 truth | PASS. Reviewer independently reversed observed operation order, same-port proof settlement and physical-payload verification. The named tests failed with child exits `4`, `2` and `3`; each temporary mutation was removed, exact source/test SHA-256 was restored, and focused returned `5/5`. |
| Runtime / cleanup | PASS. All child leases use `from_project_runtime()` and exact typed teardown. Fresh export and all permanent worktrees have no runtime/cache residue; no OS-global TEMP staging root was inspected or cleaned. |
| XSS / privileged capability | `XSS_NOT_APPLICABLE`. No Browser, WebView, HTML/DOM renderer, JavaScript context, bridge, IPC or extension capability changed. |

CodeReview.md mandatory checks pass: strong exact types, finite error results,
lease-derived paths, same-port proof authority, honest test claims, dependency
traceability, exact owner/task/worktree binding and proportionate one-owner/no-
helper profile. No blocking finding remains.

Guarded integration must merge the complete E4 history, not copy the correction
alone. Preserve both WPR append sets exactly once, then rerun focused/full/static,
diff and residue checks. No force, reset, push, package/build/install, live Codex,
target-project write, release or deployment is authorized.

## Review decision

`CHANGES_REQUESTED / TICKET_REFREEZE_REQUIRED`

The implementation return is structurally clean and its submitted tests pass,
but the frozen S4 closure is inconsistent with the approved SPEC and the
committed success test avoids that inconsistency by adding foreign records only
after the receipt has already been issued. The ticket must be refrozen before
an implementation correction can be judged.

## Blocking findings

### CR-165 — `TICKET_DEFECT`: S4 mixes foreign-registration blocking into the clean success path

The approved SPEC AC-02 classifies a foreign registration as
`INSTALL_BLOCKED` and forbids a success receipt. E4 is explicitly the clean
success ticket and excludes compensation, yet frozen S4 requires final owned
state while seeded foreign records remain unchanged. The submitted child calls
`run_registration_success_acceptance` first and only then seeds its foreign
marketplace and plugin, so the named S4 test does not prove success in the
presence of pre-existing foreign state.

The reviewer pre-seeded the same foreign marketplace/plugin before invoking
the exact submitted acceptance composition. The result was finite
`REGISTRATION_SUCCESS_BLOCKED / CLAIM_BLOCKED`, no receipt was issued, and the
oracle bytes changed from 925 to 1637 because the owned add transitions had
already occurred. This is consistent with E2 proof admission and the later E5
compensation responsibility, but it cannot satisfy the current wording of S4.

Required control-plane correction: refreeze E4 as a clean, initially empty
owned lease success closure. Pre-existing foreign registration must remain a
blocked/no-false-receipt case and its compensating preservation belongs to E5.
Do not redefine post-success foreign seeding as success evidence.

### CR-166 — `EVIDENCE_DEFECT`: the committed S7 test does not prove its three-worktree claim

The named test
`test_s3_s4_s5_s7_exact_child_success_preserves_foreign_and_parent_state`
checks its child return and parent environment tuple, but it does not compute or
compare byte manifests and Git porcelain for the control and both permanent
implementation worktrees. The reviewer independently surrounded the exact
success child with those readbacks and all three worktrees remained byte- and
porcelain-identical, so no product defect was found. The frozen ticket must
separate committed child-process evidence from reviewer-owned external
non-interference evidence instead of letting a test name claim assertions it
does not execute.

## Reviewed immutable return

| Field | Evidence |
| --- | --- |
| Ticket / closure | `05b4b2e4-codex-registration-success-acceptance`; `CLOSURE-LOCAL-INSTALL-T05B4B2E4-01`; S1-S8 |
| Owner binding | Local project `6d2ebb66-1ae7-48b4-96da-53ffba88ef1f`; task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; workspace `wsb_local_orchestration_install_05b4b2e4_20260813_01`; permanent owner worktree |
| Chain | Dispatch `472201b1f82416d0fc00ec03582d0175f9f97048` -> implementation `33752375a5dace8e06547a7732bbd08d4c3deb45` -> WPR-only handoff `5cf2235ad755bd1f5935f7139789bfa6f9a4c970` |
| Scope | Implementation adds exactly the two frozen staging source/test paths; handoff changes only `doc/WorkProgressReport.md`; ancestry and `git diff --check` pass. |

## Independent verification

| Gate | Reviewer result |
| --- | --- |
| Submitted green suite | PASS in an exact detached local clone: focused 5/5, full serial 414/414, strict mypy 136/136 files, in-memory compile 136/136 files. |
| S1-S3, S5 | PASS for the clean submitted path. Exact type gates reject invalid/constructed/subclass/mismatched inputs finitely; the phase order and physical owned payload are observable. |
| S4 | FAIL / CR-165. Post-success foreign seeding is not evidence for the frozen or SPEC-defined pre-existing foreign case. |
| S6 | PASS through the E4 replay/fabrication checks plus integrated proof-settlement tests for wrong port, mismatched/constructed claims and one-shot settlement. |
| S7 | Product behavior PASS by reviewer readback; committed evidence FAIL / CR-166. The exact success child left 406 control files, 408 owner1 files and 410 owner2 files byte-identical with unchanged porcelain. |
| S8 reversals | PASS. Independent detached-clone mutations of operation order, same-port settlement and payload verification made the named tests fail respectively with child exits 4, 2 and 3. |
| Strong typing / source | PASS. No `Any`, `type: ignore`, dynamic member lookup, broad clear, `None` port, renderer/DOM/JavaScript surface or new dependency occurs in the two implementation paths. |
| CodeReview category 1 | PASS. Exact lease-derived locators and typed identity comparisons are used; no prefix-based authorization/routing check was introduced. |
| CodeReview category 3 | PASS for the clean success path. Exact E2/forward/settlement/proof capabilities gate receipt issuance; wrong-port reversal is observable. |
| CodeReview category 7 | FAIL only for CR-166 test-truth mapping; the other named behaviors and three S8 reversals are observable. |
| CodeReview category 8 | `XSS_NOT_APPLICABLE`. No Browser, WebView, HTML/DOM renderer, JavaScript context or privileged bridge is introduced. |
| CodeReview category 9 | PASS. Product cwd, canonical root, linked Git metadata and opaque workspace binding match the permanent owner worktree; exactly three original worktrees remain. |

## Required continuation

Control plane must first publish a revision-02 ticket freeze that:

1. makes E4 an initially clean lease success closure with no pre-existing
   foreign registration;
2. keeps pre-existing foreign state as `INSTALL_BLOCKED` with no false receipt,
   while deferring compensating preservation to E5;
3. assigns whole-worktree byte/porcelain non-interference to independent review,
   while the committed child test owns parent-environment preservation and exact
   lease-root teardown; and
4. requires the same implementation owner to make only the bounded test/evidence
   correction on the existing branch, followed by one WPR-only handoff.

No integration, new worktree/branch, staging push, package/build/install, live
Codex, target-project write, release or deployment is authorized by this review.
