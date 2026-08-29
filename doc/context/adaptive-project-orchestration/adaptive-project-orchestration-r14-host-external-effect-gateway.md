# Host External-Effect Gateway Context

| Field | Value |
| --- | --- |
| Artifact ID / revision | `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260829-14` / `REVISION_14` |
| State | `ARCHITECTURE_DRAFT / OWNER_DIRECTION_ACCEPTED / SPEC_EXACT_APPROVAL_PENDING` |
| Requirement / ADR | `PRD-20260829-047` / `CHG-20260829-047` / `ADR-20260829-035` |
| Authority | Project owner accepted the host-external-effect-gateway direction on 2026-08-29 (Asia/Taipei). This draft is not sealed and grants no new ticket, implementation or external effect. |
| Supersession | Refines only the unproved authorization premise of Revision 13's evidence ticket. RWW6, R09A, R09B1, the R09B2 supersession and the Remote Authority Commit data-tree model remain unchanged. |

## Confirmed facts

- `CAP-REMOTE-AUTHORITY-01` is `BLOCKED / REQUIREMENT_CHANGED / CANDIDATE_NOT_INTEGRATED`.
  Its test harness could not provide a non-forgeable external-effect grant; its initial live output
  was unretained and is not positive evidence.
- A same-process environment value, ordinary file, user cache, plugin state, receipt or Router
  metadata is not an independent authorization boundary. It may express owner intent but cannot
  prove that the caller cannot manufacture or alter the proof.
- Same-lifetime implementation dispatch remains `reviewer -> wait_agent -> review -> gate` and is
  independent of external-effect grants. Missing runners/receipts/descriptors/gateway/readback
  must not turn that synchronous route into a blocked state.
- The existing responsibility split remains: Host Bootstrap establishes root readiness; Router
  delegates runtime work; the telemetry composition factory consumes metadata-only outcomes.
  None of those responsibilities gains implicit remote/provider authority.
- The reusable-module catalog contains no `READY` host-protected external-effect-grant module.
  This is a capability gap, not permission to reuse uncatalogued internal code.

## Draft architecture boundary and data pipeline

```text
owner-approved immutable ExternalEffectPlan
  -> independently protected host grant issuance
  -> opaque ExternalEffectGrantRef
  -> Router delegation (plan ref + opaque grant ref only)
  -> HostExternalEffectGateway revalidation + atomic one-shot consume
  -> one declared remote/provider effect + direct readback
  -> bounded terminal metadata
  -> telemetry composition factory
```

The calling runtime never receives grant material, a reusable credential or unconstrained transport
handle. The gateway accepts only canonical plan bindings it can independently validate. A plan
cannot choose the grant storage location, remote, actor, ref, effect list or evidence destination.

## Composition, lifetime and trust

- `HostBootstrapPort` reports root and gateway-capability readiness only. It cannot create an
  `ExternalEffectGrant`.
- `ExternalEffectPlanPort` normalizes the owner-approved plan into immutable, credential-free
  bindings before Router delegation.
- `HostExternalEffectGatewayPort` is a host-owned privileged seam. It owns grant issuance,
  one-shot reservation/consumption, transport invocation, direct readback and conditional cleanup.
  Its `AVAILABLE` claim requires tuple-specific proof of independent host protection.
- `RouterExternalEffectDelegationPort` carries opaque references only. It cannot synthesize an
  `AVAILABLE` result or convert `UNAVAILABLE` into a retry path.
- `TelemetryCompositionFactory` accepts only typed outcome/evidence references after the gateway
  terminal result. It neither invokes nor replays the effect.

## Failure and recovery facts

`HOST_EXTERNAL_EFFECT_GRANT_UNAVAILABLE`, grant mismatch, expiry, caller mismatch, plan mismatch,
remote identity mismatch and absent direct readback all stop before effect. A durable-evidence
failure before cleanup, a changed/missing isolated ref or an ambiguous cleanup comparison is
`RECOVERY_REQUIRED`: do not remove protection, delete the ref, retry or redirect to production.
An observation followed by ordinary ref deletion is not a cleanup proof; the deletion primitive
must be conditional on the gateway-owned expected SHA.
Any later correction is a newly approved plan/grant, never a reused grant.

## Boundary

This draft has no implementation authority. It may become a sealed Context only after exact owner
approval of Revision 14. A later evidence-only host-capability ticket must establish the supported
host/platform protection primitive and adversarial proof before CAP-REMOTE can be re-scoped.
