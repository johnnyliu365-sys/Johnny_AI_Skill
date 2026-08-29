# Host External-Effect Gateway Context

| Field | Value |
| --- | --- |
| Artifact ID / revision | `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260829-14` / `REVISION_14` |
| State | `SEALED / SPEC_REVISION_14_HOST_EXTERNAL_EFFECT_GATEWAY_APPROVED / CAP_HOST_EFFECT_GRANT_01_TICKET_OPENING_AUTHORIZED` |
| Requirement / ADR | `PRD-20260829-047` / `CHG-20260829-047` / `ADR-20260829-035` |
| Authority | Project owner approved exact candidate `c3da092eb5cbd78938fb6f43480c525a9ee2258e` on 2026-08-29 (Asia/Taipei), sealing this Context and authorizing reviewer opening of `CAP-HOST-EFFECT-GRANT-01` only. |
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

This sealed Context authorizes only reviewer opening of the evidence-only
`CAP-HOST-EFFECT-GRANT-01` ticket. It grants no gateway implementation, credential, remote scope,
provider/Git effect, CAP-REMOTE retry, publication, installation, release or deployment authority.
That ticket must establish the supported host/platform protection primitive and adversarial proof
before CAP-REMOTE can be re-scoped.
