# Receipt-bound Role Supervision Revision 08 — Senior pre-effect admission correction

| Field | Value |
| --- | --- |
| Kind | `SPEC_REVISION_LEAF` |
| Lifecycle | `OWNER_APPROVED / IMMEDIATE_SENIOR_ACTION_AUTHORIZED / NO_EMPTY_REVIEW` |
| Parent | Receipt-bound Role Supervision Revision 07 |
| Requirement | `PRD-20260817-032` / `CHG-20260817-032` |
| Context | `doc/context/receipt-bound-role-supervision/revisions/rev09-senior-pre-effect-admission.md` |
| Decision | `ADR-20260817-019` |
| Corrected ticket | `R03-00-host-bound-no-effect-correction` at `887742ad1cee16e5b00991b067ebb1aa55eb7d57` |

## Normative correction

Revision 07 remains authoritative except for every requirement that a formal independent review
must approve the unexecuted Senior control ticket before correction/host effect. Those phrases are
superseded by this exact `PRE_EFFECT_ADMISSION_REQUIRED` gate.

The Senior is already the sole Reviewer. It does not review an absent implementation and does not
send the control ticket to an Implementer. It independently reads the authoritative evidence,
commits one additive ticket decision plus correction/continuation state, performs the exact
owner-approved effect and later reviews the real implementation return.

## Finite state correction

```text
enum SeniorPreEffectAdmissionKind {
  READY,
  SOURCE_MISMATCH,
  TARGET_TASK_MISMATCH,
  TARGET_HOST_MISMATCH,
  OUT_OF_BAND_TURN_UNRECONCILED,
  WORKTREE_CHANGED,
  MANAGER_UNAVAILABLE,
  OPERATION_IDENTITY_MISMATCH
}

enum OutOfBandTurnKind { NON_OPERATIONAL_HALT }

struct OutOfBandTurnReconciliation {
  TaskRef target_task_ref;
  HostId target_host_id;
  HostTaskRevision observed_turn_revision;
  OutOfBandTurnKind kind;
  NoMutationProofRef no_mutation_proof_ref;
  ContentDigest reconciliation_digest;
}

struct SeniorPreEffectAdmission {
  SeniorPreEffectAdmissionKind kind;
  RoleRef senior_ref;
  TaskRef senior_task_ref;
  TicketRef control_ticket_ref;
  CommitId control_ticket_commit;
  OutOfBandTurnReconciliation out_of_band_turn;
  ThreadHostBinding target_binding;
  DispatchOperationId dispatch_ref;
  CommitId claim_commit;
  EvidenceRefs evidence_refs;
  std::optional<DispatchFailureRef> failure_ref;
  ContentDigest admission_digest;
}
```

`READY` requires no failure and exact evidence for every field. Every other result requires one
finite failure and produces zero correction/host effects. No dynamic or prompt-derived value may
enter these contracts.

## Acceptance criteria

### AC-66 — No empty Code Review

Before implementation exists, `R03-00-host-bound-no-effect-correction` never enters `REVIEW`,
never produces `APPROVED/CHANGES_REQUESTED/BLOCKED`, and is never sent to an Implementer. The only
stage is `MANUAL_BOOTSTRAP / SENIOR_PRE_EFFECT_ADMISSION`.

### AC-67 — Immutable additive ticket correction

Commit `887742ad1cee16e5b00991b067ebb1aa55eb7d57` remains unchanged. Senior adds one decision leaf
that marks its review-gate wording `SUPERSEDED_BY_SPEC_REVISION_08` and the action
`PRE_EFFECT_ADMISSION_REQUIRED / READY_FOR_SENIOR_ACTION`. No second ticket, Reviewer, owner
approval, grant, attempt or receipt is created.

### AC-68 — Out-of-band turn reconciliation

Admission binds target turn `01a00b7d-580f-7c41-a462-067659223f33`, proves it was user-origin,
did not contain `dispatch_ref=bpb-r03-00-cs02-initial-20260817-003`, returned
`NON_DISPATCHED`, and left the implementation worktree unchanged. It is
`NON_OPERATIONAL_HALT` and consumes zero continuation calls.

### AC-69 — One authoritative pre-effect readback

Senior performs exactly one bounded readback of task
`019ffb0c-db88-7303-895c-aecfadde7c8d` with explicit `hostId=local` and one read-only Git/worktree
check. It must observe the reconciled turn, exact task/host binding, clean worktree and resolvable
host manager. Failure halts without a correction record or delivery.

### AC-70 — Commit-before-effect correction

After `READY`, Senior commits additive `BootstrapNoEffectCorrection` and
`BootstrapNoEffectContinuation` records bound to the existing dispatch ref, claim commit, target
task and host. The introduction commit is read back before the host call. These records do not
create or reuse a grant/attempt; they settle the already-approved operation.

### AC-71 — Original ticket only

The only host delivery uses explicit port argument `hostId=local` and this unchanged envelope:

```text
ACTION_REQUIRED
dispatch_ref=bpb-r03-00-cs02-initial-20260817-003
registry_commit=3899fc9e99df636fe4ab9f3b5a272e581c31d23c
ticket=R03-00-policy-correction-prerequisite
bootstrap_grant=BDG-R03-00-20260816-003
owner_task=019ffb0c-db88-7303-895c-aecfadde7c8d
claim_commit=ef2a5c1efd5029d8bb5698c0f9c44b0704d1f3d3
```

`R03-00-host-bound-no-effect-correction` is forbidden in every Implementer message.

### AC-72 — Settlement then real review

Senior performs one bounded post-call readback and records the finite settlement. No second call
is permitted. Only a real implementation return with diff/evidence may then enter normal Code
Review; a new halt follows its declared Router/change-control route.

### AC-73 — Resource and authority fence

The correction uses the existing Senior and Implementer tasks, one admission read, at most one
delivery and one readback. No heartbeat, polling, automation, new model/task, grant, attempt,
receipt, owner prompt, push, release or deployment is permitted.

## Exact next action

```text
stage=MANUAL_BOOTSTRAP
action=SENIOR_PRE_EFFECT_ADMISSION
owner=SUPERVISOR_REVIEWER
owner_task=019fb935-bbe1-7f71-8b4b-58ba20c81626
target_task=019ffb0c-db88-7303-895c-aecfadde7c8d
target_host_id=local
continuation=AUTO_CONTINUE
expected_return=BOOTSTRAP_CONTINUATION_SETTLED | HALT/<finite reason>
```

Architecture does not create the ticket decision or call the host. Senior performs the exact
action immediately from this committed, owner-approved revision; no additional approval or Review
stage exists before it.

## Approval record

- Decision maker: project owner.
- Decision/date: `APPROVED` / `2026-08-17 (Asia/Taipei)`.
- Direction: fix the deadlock; do not review work that has not been done.
- Next route: `MANUAL_BOOTSTRAP / SENIOR_PRE_EFFECT_ADMISSION / AUTO_CONTINUE`.
