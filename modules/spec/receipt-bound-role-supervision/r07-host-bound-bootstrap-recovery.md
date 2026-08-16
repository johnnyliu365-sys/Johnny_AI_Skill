# Receipt-bound Role Supervision Revision 07 — host-bound bootstrap no-effect recovery

| Field | Value |
| --- | --- |
| Kind | `SPEC_REVISION_LEAF` |
| Lifecycle | `OWNER_APPROVED / SENIOR_CORRECTION_TICKETING_AUTHORIZED / NO_DISPATCH` |
| Parent | `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2` Revision 06 |
| Requirement | `PRD-20260817-031` / `CHG-20260817-031` |
| Context | `doc/context/receipt-bound-role-supervision/revisions/rev08-host-bound-bootstrap-recovery.md` |
| Decision | `ADR-20260817-018` |
| Historical result | `BDR-R03-00-20260817-003` at settlement commit `0b397a08050e435d82632070c2a952c54dcb6d0d` |

## Root-cause closure

The target implementation task was on host `local`, but the Senior host call explicitly passed
the calling environment host. The host tool rejected that value at manager lookup. The target
task received no new turn, and a same-context read-only call resolved successfully when `local`
was explicit. Therefore the incident is before the delivery-effect boundary and is proved
no-effect.

The missing architecture controls were: no `target_host_id` in bootstrap authority, no
authoritative host readback before claim, and no typed distinction between manager lookup and
adapter invocation. This revision fixes those controls without rewriting historical evidence or
creating another grant/attempt cycle.

## Strongly typed contract delta

```text
opaque HostId
opaque ThreadHostBindingRef

enum HostBindingSource { TARGET_TASK_LIST_READBACK, TARGET_TASK_READBACK }
enum HostAdmissionKind {
  READY,
  TASK_NOT_FOUND,
  TASK_HOST_MISMATCH,
  HOST_MANAGER_UNREGISTERED,
  HOST_MANAGER_UNAVAILABLE
}
enum DeliveryEffectBoundary {
  BEFORE_MANAGER_RESOLUTION,
  BEFORE_ADAPTER_INVOCATION,
  ADAPTER_INVOCATION_STARTED,
  DELIVERY_ACKNOWLEDGED
}
enum HostFailureEffectKind { PROVED_NO_EFFECT, EFFECT_UNCERTAIN }
enum BootstrapContinuationLifecycle { AUTHORIZED, CALLED, SETTLED, QUARANTINED }
enum RemainingHostCalls { ZERO, ONE }

struct ThreadHostBinding {
  ProjectId project_id;
  TaskRef target_task_ref;
  HostId target_host_id;
  HostBindingSource source;
  HostTaskRevision observed_task_revision;
  EvidenceRefs readback_refs;
  ContentDigest binding_digest;
}

struct BootstrapHostBoundRegistryEntry {
  ProjectId project_id;
  TicketRef ticket_ref;
  TicketRevision ticket_revision;
  TaskRef target_task_ref;
  HostId target_host_id;
  ThreadHostBindingRef host_binding_ref;
  CommitId registry_commit;
  ContentDigest entry_digest;
}

struct HostAdmissionEvidence {
  HostAdmissionKind kind;
  std::optional<ThreadHostBinding> binding;
  DeliveryEffectBoundary boundary;
  std::optional<DispatchFailureRef> failure_ref;
  EvidenceRefs evidence_refs;
  ContentDigest result_digest;
}

struct BootstrapNoEffectCorrection {
  BootstrapResultId historical_result_id;
  CommitId historical_settlement_commit;
  BootstrapAttemptId attempt_id;
  BootstrapGrantId grant_id;
  DispatchOperationId dispatch_ref;
  CommitId claim_commit;
  ThreadHostBinding corrected_binding;
  HostFailureEffectKind corrected_effect;
  EvidenceRefs correction_evidence_refs;
  ReviewDecisionRef correction_review_ref;
  ContentDigest correction_digest;
}

struct BootstrapNoEffectContinuation {
  BootstrapNoEffectCorrection correction;
  BootstrapContinuationLifecycle lifecycle;
  RemainingHostCalls remaining_host_calls;
  HostId explicit_host_id;
  TaskRef target_task_ref;
  std::optional<EvidenceRefs> settlement_refs;
  ContentDigest continuation_digest;
}
```

`HostId` is opaque and must compare byte-for-byte with authoritative target-task readback. A
caller/current environment host, default, prompt field or guessed mapping is invalid. A
`BootstrapNoEffectContinuation` is settlement of the existing operation; it is not a member of
`BootstrapGrantKind`, not a new attempt and not implementation authority by itself.
`HostAdmissionEvidence::READY` requires a binding and forbids failure; every rejection requires a
failure, and `TASK_NOT_FOUND` forbids a binding. `AUTHORIZED` continuation requires
`remaining_host_calls=ONE` and no settlement refs; every terminal lifecycle requires
`remaining_host_calls=ZERO` and exact settlement refs.

## Acceptance criteria

### AC-57 — Exact host binding

Every new bootstrap registry, grant and attempt binds `target_host_id` and the target task. The
value comes only from `TARGET_TASK_LIST_READBACK` or `TARGET_TASK_READBACK`. Missing, stale,
calling-host, implicit/default or mismatched values halt before claim.

### AC-58 — Admission before claim

Senior performs one read-only task/host readback and proves host-manager resolution before
claim-before-effect. `TASK_NOT_FOUND`, `TASK_HOST_MISMATCH`, `HOST_MANAGER_UNREGISTERED` or
`HOST_MANAGER_UNAVAILABLE` creates no claim, consumes no grant and permits no host delivery call.

### AC-59 — Effect-boundary classification

An error returned at `BEFORE_MANAGER_RESOLUTION` or `BEFORE_ADAPTER_INVOCATION` is
`PROVED_NO_EFFECT`. At or after `ADAPTER_INVOCATION_STARTED`, missing an exact delivery identity
or typed no-effect proof is `EFFECT_UNCERTAIN`. Error text without a trusted stage is uncertain.

### AC-60 — Immutable historical evidence

BDG-003, BDA-003, BDR-003 and settlement commit
`0b397a08050e435d82632070c2a952c54dcb6d0d` remain byte-identical. Senior adds a correction
decision leaf referencing them; no existing result, grant, attempt or approval is edited.

### AC-61 — Exact incident proof

The correction decision must bind all four facts: the rejected host
  `slingshot:env_e_6a29e55ede90832fb63e141a9890800a`, target host `local`, absence of a new target
  delivery turn after `01a00a4f-4ce7-7d03-8b42-6bbaff6bf2b1`, and successful same-context read-only
  manager resolution with explicit `hostId=local` in diagnostic turn
  `01a00b6b-0675-7652-a668-f7847e6b1656`. Missing any fact leaves BDR-003 uncertain.

### AC-62 — One same-operation continuation

After an exact Senior correction ticket and independent `APPROVED` review, one continuation may
use only:

```text
project_id=AI控制工作workflow
dispatch_ref=bpb-r03-00-cs02-initial-20260817-003
claim_commit=ef2a5c1efd5029d8bb5698c0f9c44b0704d1f3d3
target_task_ref=019ffb0c-db88-7303-895c-aecfadde7c8d
target_host_id=local
remaining_host_calls=1
```

The existing identifiers-only envelope otherwise remains unchanged. The explicit `hostId=local`
is a port argument, not a seventh implementation prompt field.

### AC-63 — No fresh grant or attempt

The continuation creates no BDG-004, BDA-004, owner grant, receipt, task, worktree, branch or new
dispatch identity. A second call, changed identity, missing approved review or already-observed
delivery rejects before effect.

### AC-64 — Finite settlement

After the one call, one bounded readback records `DELIVERED`, typed `PROVED_NO_EFFECT`, or
`EFFECT_UNCERTAIN`. Delivered closes the continuation; proved no-effect returns to
Architecture/change control with zero calls remaining; uncertain quarantines it. None permits an
automatic second call.

### AC-65 — Resource and authority fence

The complete path is one read-only admission, at most one delivery and one bounded readback. It
uses no heartbeat, automation, cron, watchdog, background model wake, recurring thread read or
polling. Architecture approval authorizes Senior ticketing/review and the exact post-review
continuation only; Architecture never performs the call and this leaf is not a dispatch command.

## Verification matrix

1. Contract tests reject absent host, calling-host substitution, default host and target-task/host
   mismatch before claim.
2. State tests prove every host-admission rejection leaves grant and operation unconsumed.
3. Effect tests classify manager lookup rejection as no-effect and retain uncertainty for any
   untyped or post-invocation failure.
4. Fixture tests prove the BDR-003 evidence set yields exactly one correction identity and that a
   missing evidence member yields no continuation.
5. Replay tests reject BDG-004/BDA-004, new dispatch/claim identities, a second call and every
   task/host other than the exact incident binding.
6. Integration tests use one read-only preflight, one fake host call and one readback; no
   heartbeat, scheduler or recurring poll is created.
7. Repository tests prove the historical BDG/BDA/BDR-003 blobs and WorkProgressReport are
   unchanged by the architecture revision.

## Senior compilation boundary

Senior may now create one exact correction ticket covering the typed host binding, pre-claim
admission, effect-stage classification, immutable correction decision and incident-specific
continuation. Senior must obtain independent review before any continuation record or host call.
This approval creates no ticket, implementation branch, grant, attempt, message, integration or
deployment effect by itself.

## Approval record

- Decision maker: project owner.
- Decision/date: `APPROVED` / `2026-08-17 (Asia/Taipei)`.
- Approved decisions: bind target host; obtain it only from target-task readback; admit the host
  before claim; classify pre-manager failure as proved no-effect; preserve BDR-003 with an
  additive correction; permit one same-operation continuation at `hostId=local`; create no new
  grant or attempt.
- Next route: `TICKETS / SENIOR_CORRECTION_TICKET`.
