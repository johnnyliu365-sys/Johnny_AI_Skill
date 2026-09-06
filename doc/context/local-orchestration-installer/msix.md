# MSIX installer delta Context

| Field | Value |
| --- | --- |
| Artifact ID / kind | `CTX-LOCAL-INSTALLER-MSIX-20260905-01` / `SHARED_CONTEXT` |
| Revision / state | `03` / `SEALED / OWNER_APPROVED` |
| Requirement / architecture | `PRD-20260905-050` / `CHG-20260905-050` / `ADR-20260905-038` |
| Intake scope | `DELTA`: Windows installer format, package/state ownership, host activation, upgrade and removal; existing control-plane product goals retained. |
| Baseline reference | `117346cf44fbbc75a08aca5677f223c38df0fb00`; [legacy Context](main.md) is historical discovery/implementation evidence, not current Inno dispatch authority. |

## Product boundary

Johnny remains an external, removable Windows local control plane for Codex and
Claude. Target repositories own their artifacts and do not acquire Johnny runtime
dependencies. Package state is not host readiness, and neither is provider login
or asynchronous event delivery. Shared governance and runtime boundaries are not
reimplemented in an installer.

The owner selected MSIX and accepted Johnny's one-click complete-removal entry point.
Direct Windows removal promises only its measured package scope, not external host
cleanup. The distinction is visible before activation and in removal guidance.
Technical capability proof and package-effect ticket admission remain separate.

## Interaction slices and data pipeline

| Slice | Validation → effect/storage → projection | Ownership / lifecycle |
| --- | --- | --- |
| Install package | Exact signed identity, version, architecture and dependencies → supported Windows deployment API → fresh package identity/location readback. | Windows owns package files; failure is not host activation. |
| Activate selected host | Canonical selected host + package/installation identity + supported lifecycle proof → host adapter effect + verified ownership ledger → exact active/blocked/partial result. | Codex/Claude owns registration mechanism; Johnny owns only proved entries, not global config. |
| Runtime status | Typed metadata request → bootstrap-admitted state + bounded Router delegation → finite capability/status projection. | Metadata-only Johnny state; no raw prompts, credentials or target contents. Missing bridge does not block synchronous work. |
| Upgrade | Exact old/new package identity + state schema/ownership check → Windows package update and separately controlled state migration → package/state/host readback. | No in-place writes to package; interrupted migration retains recovery and blocks use. |
| Complete removal | Johnny one-click entry + owned process/state/host proofs → stop owned work, host cleanup/readback, state settlement, package removal → independent absence result. | Owner accepted semantics; self-removal/readback primitive remains to be proved. Never infer foreign-state ownership by name. |
| Direct Windows removal | Windows package removal → fresh package observation and explicit external-cleanup limitation → narrow truthful status. | Owner accepted the narrower guarantee; no promise that arbitrary host cleanup scripts ran. |

## Composition map

| Root / scope | Injected responsibility | Test substitution |
| --- | --- | --- |
| Package build, one exact source candidate | Payload/dependency resolver, manifest renderer, pinned SDK pack/sign adapter; signing remains separate authority. | Deterministic fixture payload, fake command adapter; real SDK validation before build acceptance. |
| Johnny desktop activation/removal, one operation | Package readback, host lifecycle, owned-state ledger, bounded process/clock, result projection. | Fake package/host/process ports for finite fault tests; real disposable Windows user for lifecycle claims. |
| Bootstrap/runtime, one provisioning/event scope | Existing bootstrap root, Router grant and telemetry factory boundaries. | Existing admitted stores and fake ports; no new scheduler or queue requirement. |

The proposed language/runtime boundary remains Python 3.11. A clean, pinned
one-folder executable bundle inside MSIX is the build-time packaging proposal;
PyInstaller and Windows SDK inputs require qualification before use. No second
product backend is introduced for the native identity probe. The package remains
immutable, while mutable state belongs to Bootstrap. A minimal probe is not the
full runtime or either host's lifecycle proof.

Exact DTO/port fields and constructors belong to the SPEC and vertical tickets.
A change to accepted user behavior returns to owner; technical proof gaps do not
authorize a different behavior or a permanent observer service. Native removal
observation must be independent of the terminating package; its concrete mechanism
remains unproved, not inferred from the existence of an interface.

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

## Revision boundary

The owner approved revision 03 together with installer SPEC revision 04 on
2026-09-06, at `6282ca19e3e6f518d0c5b56eb4f7414f5013ff79`, Context LF SHA-256
`4de567817b3f1dfe11625104c61ea38f64c5293d4ce067afd6db83b949fca555`.
This approval/seal records the accepted packaging/proof boundaries; it does not
convert unproved capabilities into facts. Later ticket/implementation lanes read
this sealed revision only. Revision 02 remains provenance, not a competing source.

## Unresolved authority and verification

Release: publisher/signing identity,
trusted distribution and company policy. Engineering: pinned SDK/runtime, package
location/data behavior, host compatibility and self-removal evidence. No target,
host mutation, signing, trust-store change or installation is authorized by this
research Context. The accepted removal choice is not an outstanding owner question.

XSS: proposed native package/dialog/CLI surfaces are `XSS_NOT_APPLICABLE`; introducing
a WebView/HTML/JS surface requires its own source-to-sink review, not inherited exemption.
