# MSIX installer delta Context

| Field | Value |
| --- | --- |
| Artifact ID / kind | `CTX-LOCAL-INSTALLER-MSIX-20260905-01` / `SHARED_CONTEXT` |
| Revision / state | `01` / `DRAFT / OWNER_LIFECYCLE_DECISION_PENDING` |
| Requirement / architecture | `PRD-20260905-050` / `CHG-20260905-050` / `ADR-20260905-038` |
| Intake scope | `DELTA`: Windows installer format, package/state ownership, host activation, upgrade and removal; existing control-plane product goals retained. |
| Baseline reference | `117346cf44fbbc75a08aca5677f223c38df0fb00`; [legacy Context](main.md) is historical discovery/implementation evidence, not current Inno dispatch authority. |

## Product boundary

Johnny remains an external, removable Windows local control plane for Codex and
Claude. Target repositories own their artifacts and do not acquire Johnny runtime
dependencies. Package state is not host readiness, and neither is provider login
or asynchronous event delivery. Shared governance and runtime boundaries are not
reimplemented in an installer.

The owner selected MSIX. The exact user-facing complete-removal contract is pending;
this draft does not seal a relaxed replacement for the old one-click cleanup promise.

## Interaction slices and data pipeline

| Slice | Validation → effect/storage → projection | Ownership / lifecycle |
| --- | --- | --- |
| Install package | Exact signed identity, version, architecture and dependencies → supported Windows deployment API → fresh package identity/location readback. | Windows owns package files; failure is not host activation. |
| Activate selected host | Canonical selected host + package/installation identity + supported lifecycle proof → host adapter effect + verified ownership ledger → exact active/blocked/partial result. | Codex/Claude owns registration mechanism; Johnny owns only proved entries, not global config. |
| Runtime status | Typed metadata request → bootstrap-admitted state + bounded Router delegation → finite capability/status projection. | Metadata-only Johnny state; no raw prompts, credentials or target contents. Missing bridge does not block synchronous work. |
| Upgrade | Exact old/new package identity + state schema/ownership check → Windows package update and separately controlled state migration → package/state/host readback. | No in-place writes to package; interrupted migration retains recovery and blocks use. |
| Complete removal | Owner-selected entry point + owned process/state/host proofs → ordered cleanup and package removal → independent absence result. | Final semantics and self-removal readback are pending. Never infer foreign-state ownership by name. |
| Direct Windows removal | Windows package removal → fresh package and external-state observations → narrow truthful status. | Does not presume arbitrary host cleanup scripts ran. Complete-cleanup guarantee needs owner decision/capability proof. |

## Composition map

| Root / scope | Injected responsibility | Test substitution |
| --- | --- | --- |
| Package build, one exact source candidate | Payload/dependency resolver, manifest renderer, pinned SDK pack/sign adapter; signing remains separate authority. | Deterministic fixture payload, fake command adapter; real SDK validation before build acceptance. |
| Johnny desktop activation/removal, one operation | Package readback, host lifecycle, owned-state ledger, bounded process/clock, result projection. | Fake package/host/process ports for finite fault tests; real disposable Windows user for lifecycle claims. |
| Bootstrap/runtime, one provisioning/event scope | Existing bootstrap root, Router grant and telemetry factory boundaries. | Existing admitted stores and fake ports; no new scheduler or queue requirement. |

Exact public DTO/port definitions belong to the replacement SPEC/tickets, not an
unreviewed Context invention. A lifecycle decision that changes these slices
requires owner convergence before this draft is sealed.

## Reuse selection and gaps

Installed `0.4.14` catalog → workflow-control partition has only
`workflow-router-poc`; it declares no MSIX installer capability. Selected reusable
MSIX module: **none**. Do not infer an installer API from a nearby module name.

Existing repository-local `windows_package_manifest.py`, `plugin_bundle_builder.py`,
`johnny_live_install.py` and `live_uninstall_composition.py` are candidate integration
inputs to inspect at their specific seam. ZIP manifest/build or installed runtime
evidence does not qualify MSIX. Existing host-specific CLI paths must be distinguished
from legacy emulators and individually requalified; this draft makes no blanket
claim that every host lifecycle is implemented or absent.

## Unresolved authority and verification

Owner: complete-removal entry point/guarantee. Release: publisher/signing identity,
trusted distribution and company policy. Engineering: pinned SDK/runtime, package
location/data behavior, host compatibility and self-removal evidence. No target,
host mutation, signing, trust-store change or installation is authorized by this draft.

XSS: proposed native package/dialog/CLI surfaces are `XSS_NOT_APPLICABLE`; introducing
a WebView/HTML/JS surface requires its own source-to-sink review, not inherited exemption.
