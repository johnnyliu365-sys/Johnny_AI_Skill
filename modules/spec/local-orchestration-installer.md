# Local orchestration installer — MSIX acceptance refreeze

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-LOCAL-ORCHESTRATION-INSTALLER-20260808-01KZ8L0C2E4G6J8M0P2R4T6V8X` |
| Document revision / state | `04` / `APPROVED / BOUNDED_TICKETING_AUTHORIZED` |
| Author / baseline | Codex, current `main`, `d584b7dfc6eaeef943a0a25ff9684879e4021ee5` |
| Effective requirement | [PRD/CHG-20260905-050](../../doc/requirements/active/2026/local-installer/REQ-20260905-050.md) |
| Retained requirement lineage | Format-neutral `PRD/CHG-20260808-011`, `20260812-014`, `20260813-015`, `20260814-018`; retired mechanism `ARCH-REQ-20260815-003` is evidence only. |
| Architecture / Context | [ADR-20260905-038](../../doc/adr/ADR-20260905-038-msix-delivery-boundary.md); [MSIX Context](../../doc/context/local-orchestration-installer/msix.md) revision 03, owner-approved/sealed |
| Discovery evidence | [CAP-MSIX-01 review](../../doc/reviews/local-orchestration-installer/cap-msix-01-capability-review.md), `RESEARCH_COMPLETE / LIFECYCLE_UNPROVED` |
| Language / stage | Python 3.11, strict typed contracts; Windows x64 POC. XML is package metadata; PowerShell is a bounded Windows effect adapter, not a second domain implementation. |

## 1. Authority and retained history

The owner already chose MSIX and Johnny-managed one-click complete removal. Direct
Windows uninstall has the accepted narrower package-only guarantee. This revision
does not reopen either decision. It translates the approved delta into proposed
package acceptance. The owner approved exact revision 04 at `6282ca19` on
2026-09-06; the approval binding is recorded below. This state-only writeback
does not qualify a toolchain or imply downstream package-effect authority.

This is a revision of the same installer capability, not a new parallel SPEC.
Inno/`Setup.exe`, its paired uninstaller, and a single writable payload root are
`SUPERSEDED` packaging assumptions. Their complete text and approval provenance
remain in this file at baseline `d584b7dfc6eaeef943a0a25ff9684879e4021ee5`.
Format-neutral AC-04/05/08/11/13 survive. AC-09/10 belong exclusively to the optional
cross-lifetime receipt-bound route, as narrowed by ADR-20260823-014 and
ADR-20260824-020; they never gate same-lifetime reviewer-owned delegation.

Unstarted tickets 04A–04I remain non-dispatchable until individually refrozen;
04B's Inno scope is superseded. No old ticket acquires MSIX authority through this
draft. Finished ZIP/CLI evidence stays valid in its original scope; the existing
installation remains untouched until a separately qualified migration.

Environment observations are prerequisites, not package acceptance:

- ENV-MSIX-01 created the disposable VM; ENV-MSIX-02 closed its temporary activation
  connection with native disconnected readback. Their exact tickets/reviews own that
  evidence. Owner screenshots report guest activation, not MSIX execution.
- No MakeAppx-built candidate, package identity launch, upgrade, complete removal or
  live MSIX host activation has passed yet.
- This document permits no working-host installation/certificate trust, guest
  reconnection, release, push, company account use or production signing. Source
  approval and an exact external-effect grant are different admissions.

## 2. Product, success and exclusions

Johnny is a removable local control plane for **both Codex and Claude**, external to
target repositories. Normal use installs a signed per-user MSIX, chooses supported
hosts, reads honest readiness, updates, and removes through Johnny's complete-removal
entry. No target acquires plugin source, runtime, build, CI or deployment dependencies.

Success is independently observed package, owned state, process and host lifecycle
closure for one declared installation/current user. It is not a green build, an
existing CLI install, a stopped runner or a screenshot of a package dialog.

Excluded: new service/database/queue/gateway framework, forced provider login or
model selection, automatic asynchronous-wake claims, ARM/multi-architecture bundle,
Store submission, public App Installer feed, production signing/trust policy, and
the future all-old-payload-cache elimination major version. MSIX alone proves none
of those. Packaged full-trust execution is **not an AppContainer sandbox**.

## 3. Observable slices and pipeline

| Slice | Boundary → use case → owned effect → independent projection |
| --- | --- |
| Package install | Exact signed artifact/environment → `DeployPackage` → Windows current-user deployment → fresh identity/version/path. `PACKAGE_INSTALLED` does not mean hosts are active. |
| Host activation | Nonempty canonical host selection + package identity + published capability → `ActivateHosts` → per-host register/readback and ledger → each host active, blocked, recovery-required or explicitly skipped. |
| Status/runtime | Strict metadata request → `ReadInstallationStatus` → package, ledger, host and process observations → separate dimensions, never one inferred ready flag. Runtime consumes existing Bootstrap/Router/telemetry composition. |
| Upgrade | Exact old/new identity + schema compatibility + operation lease → `UpgradeInstallation` → Windows update, separately admitted state transition → package/state/host readback or recovery-required. |
| Johnny removal | Exact installation ownership → `RemoveInstallation` → stop owned work, remove/read back owned hosts, settle owned state, remove exact package → independent final absence. |
| Direct Windows removal | Windows package lifecycle → package absence only, with external-cleanup limit disclosed before host activation and in removal guidance. |

Inputs validate into closed types before effect. Malformed values are rejected,
not silently normalized into a different identity. Native text/dialog status must
expose progress, no-host, skipped, failure, recovery and success without relying on
color. A formal/branded UI redesign needs a separately approved design handoff.
No Browser/WebView/HTML/JavaScript/Native Bridge: `XSS_NOT_APPLICABLE`.

## 4. Ownership and composition

| Owner/root | Owns | Prohibited responsibility |
| --- | --- | --- |
| Windows package manager | Immutable deployment, package identity and Windows-managed storage | Johnny cannot recursively delete WindowsApps, guess install location or patch installed files. |
| Host Bootstrap | Installation identity, mutable root and admitted state capabilities | No adopting legacy ZIP, foreign roots or other users' state by product-name matching. |
| Codex/Claude | Its documented registration interface | No hidden-format edits, copied credentials or blanket cache deletion. |
| Operation composition | One invocation's injected ports, lease, bounded process/clock and result | No ambient singleton, target/Git effects or second orchestration system. |
| Independent removal observer | One exact attempt's observation/recovery outside the removed package | No self-asserted completion from a terminating package, permanent service or arbitrary command endpoint. |

Dependency direction: native UI/CLI → application use case → domain contracts;
infrastructure implements injected ports. Build composition is separate from desktop
operations. Bootstrap/runtime remains root provision → Router delegation → telemetry
factory consumption; installer work does not rewrite runtime grant logic.

Production roots inject `PackageDeploymentPort`, `PackageObservationPort`,
`OwnedStatePort`, `HostLifecyclePort`, `OwnedProcessPort`, `OperationLeasePort`,
`RemovalObserverPort`, `ClockPort` and `EvidencePort`. Build injects source export,
dependency resolver, manifest renderer and bounded SDK commands. Lifetime is one
build or installation operation. Every port has a fake test substitution; fakes do
not qualify real Windows or host capability.

Existing seams are inputs to qualify, not interchangeable implementations:
`windows_package_manifest.PayloadManifest` describes the legacy ZIP allowlist;
`plugin_bundle_builder.PluginBundleBuilder` builds that archive;
`johnny_live_install.run_live_install` provisions a writable venv/ZIP layout;
`live_uninstall_composition._ScriptedShutdownPort` returns success without live
process-stop proof. Reuse applicable pure contracts after source review, not those
compositions wholesale. Do not broaden the legacy payload allowlist for arbitrary
native binaries; define a separate closed MSIX build manifest.

## 5. Contract surface to freeze in each vertical ticket

These are proposed contracts, **not a claim they exist**. Each admitted ticket gives
exact fields, constructors, limits, source locations, strict checker and finite
success/negative cells for the subset it implements.

| Contract | Meaning/invariants |
| --- | --- |
| `PackageIdentity` | Bounded name, publisher, four-part numeric version, architecture, observed full name/family; cross-check manifest and native observation, never echo the request. |
| `MsixBuildInputs` | Exact source/export, payload entries, Python/build-tool/runtime/dependency identities, SDK version/hash and manifest hash. No floating dependency, ambient PATH or working-machine venv copy. |
| `PackageArtifact` | Source/build-input lineage, unsigned hash and optional separately produced signed hash/verification. Unsigned cannot enter deployment. |
| `InstallationBinding` | Opaque installation ID, package family, typed current-user binding and Bootstrap root capability. Native paths/principals are transient adapter inputs, not durable target/PII telemetry. |
| `OperationRequest` | Finite operation, correlation, expected installation revision and exact artifact/binding; one installation lease. A duplicate observes/resumes its own attempt, not a competing effect. |
| `PackageObservation` | Discriminated `PRESENT(identity)`, `ABSENT`, `UNKNOWN(reason)`. Access denied, query failure and ambiguity never mean absent. |
| `HostObservation` | One canonical host and owned registration identity; `ACTIVE`, `ABSENT`, `SKIPPED`, `BLOCKED`, `UNKNOWN`; preserve partial outcomes. |
| `OperationResult` | Discriminated success, blocked-before-effect or recovery-required-after/unknown-effect, with exact failed phase/evidence. No success-shaped result hiding a failure. |
| `RecoveryRecord` | Attempt/install/artifact binding, last proved phase, remaining owned resources, sanitized reason. No prompts, target paths, credentials or raw host output. |

Null/missing, bool-as-number, extra fields, illegal enums, whitespace/case/prefix
aliases, overflow, traversal, reparse, foreign identity and stale/replayed bindings
fail at the boundary. `Any`, bypass constructors and unchecked dynamic values cannot
enter the domain. Windows interop requires explicit signatures and typed wrappers.
Plugin/CLI requests are not final trust: runtime revalidates safety invariants.

## 6. Acceptance and failure evidence

| AC | Required executable observation |
| --- | --- |
| AC-01 — Package/user scope | Install for the exact current user in the admitted VM and freshly query identity. VM-only test trust provisioning is separate; do not call it elevation-free. No target mutation. |
| AC-02 — Host readiness | Codex and Claude separately prove published detect/register/list/remove/absence, installed version and ownership. No selection is `PACKAGE_INSTALLED / HOSTS_NOT_SELECTED`, not activation. One host's failure preserves per-host partial state and compensates only owned effects; no aggregate success. |
| AC-03 — Ownership split | Native package location; mutable state outside immutable payload; reject foreign/ambiguous/reparse ownership and preserve sentinels. Package and state-schema versions are distinct. |
| AC-04 — Metadata/recovery | Retain metadata-only Router storage, reject replay/cross-installation input before routing, resume proved checkpoints without duplicate effects. |
| AC-05 — Git isolation | Retain registered project, lock, clean exact base and guarded fast-forward requirements; installer requests zero target/Git effects. Authority integration follows its declared-ref gate. |
| AC-06 — Complete removal | One intact Johnny action stops owned work → verifies host absence → settles state → removes exact current-user package → independently proves scoped absence. Second invocation is no-effect only after fresh absence of all owned dimensions. Shared Windows storage belonging to another user is reported separately, never deleted/claimed physically absent. |
| AC-07 — Fail closed | Inject each stop/host/state/package/observer failure. Unknown/timeout cannot become success or blind retry. Preserve evidence; finite bounded recovery only. `RECOVERY_REQUIRED` blocks normal use; failed rollback cannot authorize continued mutation/deletion. |
| AC-08 — Non-interference | Existing/empty representative target repos and foreign-host/state sentinels preserve byte/Git-status snapshots across success, failure, retry, upgrade and removal. No company repo for first proof. |
| AC-09/10 — Optional cross-lifetime | If installed, restricted-profile/gateway capability/removal remain separately proved and receipt-bound. Same-lifetime reviewer → wait → review → gate uses `NOT_REQUIRED`; absent bridge cannot block source dispatch or host activation. |
| AC-11 — Delivery staging | Before release build/system integration, independently read authorized remote staging equal to exact reviewed complete source. No force/reset or source change after freeze. Capability probes are not release candidates and cannot satisfy this gate. |
| AC-12 — Artifact lineage | Bind clean source/export, dependency lock/licenses, tools/SDK, manifest, unsigned/signed hashes, signature, environment, lifecycle and review. New bytes/toolchain/source mean a new candidate, not overwritten evidence or a self-referential digest. |
| AC-13 — Test ownership | Existing 05S1 tests retain checkout-owned `tests/.johnny-runtime/` leases. Package effects use only the separately admitted VM. No broad TEMP cleanup or sibling workspaces. |
| MSX-14 — Real build | Real MakeAppx pack with semantic validation, unpack to fresh owned output, compare admitted manifest/payload. `/nv`, renamed ZIP, mocked compiler or help/version alone cannot pass. Generated packaging metadata is distinguished from application entries. |
| MSX-15 — Identity/launch | Registered application launch; executable queries native full identity/location and matches fresh outside readback. Unpackaged launch differs from API failure. Echoed request is not observation. |
| MSX-16 — Update | Two same-family increasing versions; update, same-version repeat, lower-version rejection, wrong publisher, missing dependency and interruption tested separately. Read actual active package. Preserve native errors without inventing a unique cause for a broad HRESULT. |
| MSX-17 — State recovery | Old-app/new-schema, new-app/old-schema and interruption before/after package switch or during migration yield compatible use or blocked recovery. OS update is not state rollback. Lease contention/reordered/duplicate requests cannot cause competing effects. |
| MSX-18 — Direct removal | Exercise Windows removal separately; external-host/state sentinels demonstrate narrower scope. Disclosure precedes activation. No callback, host cleanup or absence is inferred. |
| MSX-19 — Independent observer | Prove exact-attempt observer survives package-process termination, independently queries absence and handles failure. Operator observation proves probe mechanics, not automated one-click removal. Final helper/evidence retirement leaves no installed Johnny component; only incomplete removal may retain recovery evidence. |

Tickets map finite closure cells to these ACs and executable predicates. Require
baseline red only when named tests can collect at that baseline; never fabricate
historical failures for newly introduced types. Reviewer performs an independent
reverse mutation, reads intended named red unreduced, restores exactly and reruns
green. Zero red is a finding. Adversarial helpers return findings; the parent owns
the final verdict. Code-review evidence is not source dispatch or effect authority.

## 7. Smallest serial proof plan — not opened tickets

These are future acceptance slices, not a grant to implement everything at once.

1. **Pinned build inputs and unsigned identity probe.** Qualify isolated SDK/Python
   executable packaging inputs; produce a minimal identity-reporting desktop MSIX.
   Validate pack/unpack and rejection paths. No host, daemon, signing or installation.
2. **VM package lifecycle.** Admit exact artifacts, transfer method, VM and VM-only
   test certificate; sign/verify, install, launch, update and direct-remove with
   independent operator readback. Never silently reconnect, enable sharing, transport
   credentials or trust a certificate on the working host to make transfer easier.
3. **One-click removal capability.** Prove an admitted independent observer and
   interruption semantics. If this requires changed trust/user behavior, return to
   owner/architecture; do not invent a hidden permanent service.
4. **Real runtime and hosts.** Package the exact Python runtime/dependency closure;
   qualify Codex and Claude independently, including cleanup and state-update faults.
   The smaller probe is not evidence for this larger payload; split host closures.
5. **Integrated delivery.** Exact staging/source/artifact chain, full normal and
   adversarial matrix, recovery/removal/status. Stop at cluster completion for
   owner-arranged cross-Agent review. Production distribution and old ZIP migration
   remain separately admitted.

After approval the first ticket is slice 1: exact source boundary, tool acquisition
plan, constructor preflight and finite tests. Do not pre-open all downstream tickets
with unproved prerequisites. Normal implementer uses `implementation-standard`,
parent review `ticket-review`; reuse the existing agent and wait for its return,
without activity polling.

## 8. Toolchain proposal and proof limits

Proposed executable packaging: **Python one-folder bundle inside MSIX**, with
PyInstaller as a build dependency to qualify. Retain the Python backend rather than
writing a parallel C#/C++ application merely to probe identity. Exclude one-file
self-extraction and copied working-machine venvs. Build from clean pinned Python and
dependencies; import discovery is not a distribution allowlist. Exact packaging-tool
and runtime versions/provenance must be established before slice 1 admission.

SDK candidate: `Microsoft.Windows.SDK.BuildTools` `10.0.28000.2705` from official
NuGet metadata, **not yet downloaded or qualified**. Verify package signature under
trusted policy, inspect entries before extraction, bind actual native DLL/tool
closure and test on build OS. Empty NuGet dependencies/PATH lookup do not prove native
compatibility. No global tool replacement, disabled signature verification or trust
bootstrapped solely from the candidate's own asserted certificate.

Primary guidance checked 2026-09-06, not local execution evidence:

- [Microsoft desktop packaging](https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-manual-conversion): manifest and desktop entry.
- [Microsoft MakeAppx](https://learn.microsoft.com/en-us/windows/msix/package/create-app-package-with-makeappx-tool): real pack/unpack and validation.
- [Microsoft identity](https://learn.microsoft.com/en-us/windows/msix/detect-package-identity): packaged versus unpackaged observation.
- [SDK candidate](https://www.nuget.org/packages/Microsoft.Windows.SDK.BuildTools/10.0.28000.2705): exact metadata, not locally verified tools.
- [PyInstaller operation](https://pyinstaller.org/en/stable/operating-mode.html): one-folder includes the selected interpreter/dependencies; one-file extraction differs. This motivates the proposal, not MSIX support proof.

Deployment review covers relevant boundary, state, concurrency, partial failure,
permission/config drift, worker/cache, migration, rollback, backup and smoke cases.
SQL/DB and production-account checks are not automatically applicable; exclusions
need candidate evidence. Missing capability is `BLOCKED`; unapproved production or
company access is `NOT_AUTHORIZED`, never a passed test.

## 9. Revision and approval

| Revision | Authority/provenance |
| --- | --- |
| Initial through 03 | Owner approvals dated 2026-08-08 through 2026-08-14 remain in this file at the baseline above. They do not approve MSIX packaging or revision 04. |
| 04 draft, 2026-09-06 | Codex, authorized MSIX convergence after capability research/environment preparation. Refreezes packaging acceptance, retains format-neutral invariants and the accepted removal decision. |
| 04 approval, 2026-09-06 | Project owner replied “核准” to SPEC revision 04 and Context revision 03 at `6282ca19e3e6f518d0c5b56eb4f7414f5013ff79`. Approved SPEC LF SHA-256: `b24ab772daa03c869faa30570158466acd202abe64824415f75f0394aeb933db`; approved Context LF SHA-256: `4de567817b3f1dfe11625104c61ea38f64c5293d4ce067afd6db83b949fca555`. |

Return: `APPROVAL_GRANTED -> ACTION_COMPLETED / APPROVAL_RECORDED`.
Continuation: `AUTO_CONTINUE -> TICKETS`, starting with the toolchain-input
qualification prerequisite to section 7 slice 1. Scope and tool versions must be
closed before source/build admission; approved unknowns are not fabricated facts.
The owner-authorized same-lifetime work may proceed without another ceremonial
confirmation; each exact ticket still binds its permitted action. No signing,
installation, VM reconnection, host change, push or release is granted here.
