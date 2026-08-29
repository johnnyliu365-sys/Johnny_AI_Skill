# ADR-20260829-035 — Host External-Effect Gateway capability

- Date: `2026-08-29 (Asia/Taipei)`
- Status: `DRAFT / OWNER_EXACT_APPROVAL_PENDING`
- Decision maker: Project owner
- Related change: `PRD-20260829-047` / `CHG-20260829-047`
- Amends: `ADR-20260829-034` without making its remote-authority route available.

## Context

The first `CAP-REMOTE-AUTHORITY-01` live attempt correctly stopped because its bounded output was
not retained. The resulting candidate then exposed the deeper problem: its live activation could
be reconstructed from caller-selected environment values and ordinary file paths. The same
implementation process could manufacture, replay, redirect or delete those inputs. They are an
owner-intent marker at most, not a trust boundary.

The project already separates synchronous collaboration from cross-lifetime delivery. Same-lifetime
reviewer dispatch has a live reviewer and a native completion wait; it needs neither runner,
receipt, descriptor nor host readback. That design must not be made contingent on a solution for a
different problem: authorizing an external Git/provider effect after the reviewer/runtime lifecycle
has reached a privileged boundary.

`ADR-20260827-029` also separates root provision, runtime delegation and telemetry composition.
That separation is retained. A privileged external-effect operation must not be smuggled into any
of those existing responsibilities merely because they are host-adjacent.

## Proposed decision

1. Introduce a separately qualified `HostExternalEffectGateway` capability. It is the only
   component allowed to consume an external-effect grant and invoke a privileged remote/provider
   effect. It is not implemented by a plugin, CLI command, Router record, environment variable or
   ordinary user-writable file.
2. `HostBootstrap` may establish root readiness and report whether the gateway capability is
   genuinely available. It neither issues nor consumes an external-effect grant. The `Router` may
   delegate an immutable approved plan plus an opaque grant reference, but has no grant material or
   privileged transport. The telemetry composition factory receives metadata-only terminal outcome
   records and cannot reissue an operation.
3. An `ExternalEffectGrant` is valid only when an independently protected host operation can prove
   the calling runtime cannot create, read, modify, erase, substitute or replay its material, or
   cause a grant-bound effect without an owner-issued grant. The gateway atomically reserves and
   consumes it once before executing the immutable finite plan.
4. The grant binds one immutable plan digest: canonical credential-free repository identity,
   declared read-only production ref, exact isolated target, qualified actor/role and transport,
   expected observations/candidate identities, finite allowed effect set, correlation and expiry.
   The gateway rereads/revalidates these values itself immediately before effect.
5. Cleanup is also an effect. It requires durable pre-cleanup evidence plus direct target readback
   equal to the gateway-owned expected SHA before protection removal or ref deletion. The final
   deletion itself must be atomically conditional on that SHA; observation followed by ordinary
   deletion leaves a TOCTOU gap and does not qualify. Any uncertainty, missing primitive or
   persistence failure is `RECOVERY_REQUIRED` and leaves the remote target untouched.
6. If the tuple cannot demonstrate this independent boundary, the only valid result is
   `HOST_EXTERNAL_EFFECT_GRANT_UNAVAILABLE`. It neither restarts CAP-REMOTE nor admits a remote
   writer. A future ticket must demonstrate the actual host protection primitive, actor separation,
   grant lifecycle race model and adversarial tamper/replay/cleanup probes before it can qualify
   `AVAILABLE`.

## Consequences

- `CAP-REMOTE-AUTHORITY-01` remains blocked. `6783385` is not repaired or integrated, and no second
  remote probe is authorized by this draft.
- RWW6 and the Remote Authority Commit's no-local-write/no-force/no-delete/no-retry properties
  remain intact.
- A host may honestly support ordinary implementation dispatch while reporting this privileged
  gateway as unavailable. That is a supported, non-degraded state for dispatch and a fail-closed
  state for remote effects.
- A provider adapter remains provider-neutral. GitHub, another Git service or any future provider
  must separately demonstrate that it can perform the plan's conditional effect and readback
  without exposing credentials to control-plane artifacts.

## Alternatives rejected

- **Treat a same-user file, environment variable or plugin cache as a grant.** The runtime can
  forge or alter it; this only labels caller-supplied proof as privileged.
- **Reuse receipt-bound dispatch authority.** Receipts answer cross-lifetime delivery, not external
  provider authorization. Reusing them would wrongly make synchronous dispatch depend on a bridge.
- **Let Host Bootstrap issue the grant.** It collapses root readiness with privileged effect control
  and contradicts the established responsibility split.
- **Retry the existing remote probe with more logging.** Better logging cannot turn a forgeable
  activation boundary into a trusted one.
- **Make the remote writer available on unproved hosts.** This weakens the failure mode that
  CAP-REMOTE correctly exposed.

## Approval boundary

This ADR is a directionally authorized draft, not an external-effect authorization. Exact owner
approval is required before revising the sealed shared Context, opening the host-capability ticket,
implementing a gateway, requesting credentials or remote scope, or performing any provider/Git
effect.
