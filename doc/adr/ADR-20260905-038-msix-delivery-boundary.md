# ADR-20260905-038 — MSIX package ownership and host activation boundary

| Field | Value |
| --- | --- |
| Date / revision | `2026-09-05 (Asia/Taipei)` / `02` |
| Status | `ACCEPTED / JOHNNY_COMPLETE_REMOVAL / CAPABILITY_FIRST` |
| Decision maker | Project owner; accepted Johnny-managed complete removal and narrower direct Windows removal on 2026-09-05. |
| Requirement | [PRD/CHG-20260905-050](../requirements/active/2026/local-installer/REQ-20260905-050.md) |
| Context / SPEC | [MSIX draft](../context/local-orchestration-installer/msix.md) / [installer SPEC](../../modules/spec/local-orchestration-installer.md) |
| Superseded slice | Inno/paired-EXE packaging in ADR-20260808-003 and ADR-20260812-006; ownership, isolation and immutable release lineage survive. |

## Decision and evidence

MSIX replaces the unimplemented Inno packaging goal. Do not wrap the old arbitrary
writable-root installer and call the resulting package a lifecycle proof. Package
files are read-only; package identity/location and data locations must be resolved
through supported Windows facilities, not inferred from a guessed WindowsApps path.
A packaged full-trust desktop process is not automatically an AppContainer sandbox.
[Microsoft: packaged desktop behavior](https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes)

Separate three ownership domains:

| Domain | Owner and permitted operation | Must not imply |
| --- | --- | --- |
| Signed package files/identity | Windows package manager installs, updates and removes immutable payload. Johnny reads its resolved installed location. | Writable venv, runtime journals or mutable config inside the package. |
| Mutable Johnny state | Bootstrap provisions identity-bound storage; Router delegates bounded runtime operations; telemetry composition consumes admitted storage. | Package identity alone grants ownership of old `JohnnyRouter` or foreign files. |
| Codex/Claude integration | Selected host adapter uses documented lifecycle and independently verifies exact owned registration/removal. | Package installation proves host activation, login, restricted tools or event delivery. |

The MVP should remain a packaged desktop control plane, not introduce a web service,
database, generalized installer framework or new router merely to package existing
capabilities. Exact desktop manifest/runtime behavior remains a qualification input.

## Installation is not activation

Use separate observations for `PACKAGE_INSTALLED`, `HOST_ACTIVATED`, and feature
readiness. A missing/unavailable host may leave the package installed but cannot be
reported as activated. The user selects Codex and/or Claude; every selected host must
pass its own activation acceptance. Login remains in the host's supported flow.
No provider call or credential capture is an installer test.

Root provision remains Host Bootstrap; runtime delegation remains Router; telemetry
storage consumption remains its composition factory (ADR-20260827-029). Same-lifetime
delegation remains runner/queue/receipt-free (ADR-20260823-014). MSIX does not supply a
missing host external-effect trust boundary (ADR-20260829-035).

## Removal decision — owner accepted Johnny entry point

Ordinary package removal does not establish cleanup of external host registrations.
The manifest `desktop6:UninstallActions` facility is currently restricted to desktop
games packaged as MSIXVC, so it is not a general solution for Johnny.
[Microsoft: UninstallActions](https://learn.microsoft.com/en-us/uwp/schemas/appxpackage/uapmanifestschema/element-desktop6-uninstallactions)

PSF start/end scripts surround application execution, not arbitrary package uninstall;
they cannot be used as evidence of an uninstall callback.
[Microsoft: PSF scripts](https://learn.microsoft.com/en-us/windows/msix/psf/run-scripts-with-package-support-framework)

Accepted path: one Johnny entry point first stops owned work, removes and
reads back exact owned host registrations, settles owned state, and only then requests
package removal. A cleanup failure retains recovery evidence and forbids a false
complete-removal claim. The final self-removal/result-readback mechanism must itself
be proved; launching a removal command is not completion. Direct Windows uninstall
guarantees only its measured package scope, not complete external cleanup. Show this
difference before host activation and in the removal UI/guidance. The owner expressly
accepted this tradeoff; do not ask for the same decision again.

Not selected: requiring Windows uninstall itself to clean every external registration.
This alternative is historical, not a parallel acceptance path. The accepted Johnny
path still requires proof of its final self-removal/readback mechanism; no background
cleanup service or fabricated success is implied by the decision.

## Signing, runtime and migration

- Installation needs an appropriately trusted signature. Developer/test trust and
  enterprise/production trust are distinct. Record exact publisher identity and
  certificate policy before a release; do not create trust or export signing keys
  from an ambient account. Per-user installation does not promise permission-free
  certificate provisioning on a company machine.
  [Microsoft: distribution prerequisites](https://learn.microsoft.com/en-us/windows/msix/app-installer/installing-windows10-apps-web)
- Resolve bundled Python/dependency closure from pinned artifacts and prove launch
  in a clean user without development tools. Do not copy a machine-specific venv or
  run network pip installation into package files.
- Upgrade preserves explicitly owned compatible mutable state, with finite blocked
  and recovery results. Package rollback and state-schema rollback are separate tests.
- Legacy ZIP/CLI adoption requires old identity/manifest/readback, collision checks
  and reversible transfer before retirement. Foreign or ambiguous state blocks.
- MSIX does not itself prove that no old payload bytes exist anywhere on disk.
  The next-major-version cache-retention objective needs its own measured contract.
- `.appinstaller` auto-update and public distribution are deferred, not prerequisites
  for the first qualified MSIX or authority to publish it.

## Converged delivery sequence

1. Owner removal semantics are closed. Perform the bounded CAP-MSIX-01 investigation
   before freezing any package-effect implementation ticket; do not replace capability
   evidence with a stack of fake-only installer abstractions.
2. Prove the smallest real MSIX vertical slice: identity, clean launch, mutable-state
   location, update and both removal routes in a disposable Windows user. Unit fakes
   and XML validation cannot replace Windows evidence.
3. Reuse qualified host/runtime pieces; add only the missing MSIX packaging/lifecycle
   adapters. Audit Codex and Claude independently, including foreign-state protection.
4. Reviewer runs adversarial interruption, wrong identity/signature, partial cleanup,
   stale ownership, upgrade/schema and target-isolation cases. Stop at any missing proof.
5. Freeze exact source and artifact identity, qualify signing/distribution, then request
   the separately scoped release/install effect. A cluster completion awaits cross-Agent review.

The owner product decision is accepted and the removal Grill fork is closed. This
is not a built package, a proved self-removal primitive, signing authority or a release.
CAP-MSIX-01 may return a capability gap without reopening the accepted user behavior.
