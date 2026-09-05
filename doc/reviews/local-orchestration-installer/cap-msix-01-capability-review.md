# CAP-MSIX-01 — MSIX lifecycle capability review

| Field | Value |
| --- | --- |
| Artifact ID / kind / revision | `REVIEW-CAP-MSIX-01-20260905` / `CAPABILITY_REVIEW` / `01` |
| Date / state | `2026-09-05 (Asia/Taipei)` / `RESEARCH_COMPLETE / LIFECYCLE_UNPROVED` |
| Query authority | `6b0b18be117689ae67718f869801e11df3d82533`; `CAP-MSIX-01` revision 01, LF SHA-256 `038dbc62aeb51c829c5213eeb02385ecace85ecdc525dcad9e05f09abac5be24` |
| Owner / helper | Current-session reviewer / existing Luna/xhigh lane, read-only `RESEARCH_HELPER`; no implementation owner or final-review delegation |
| Requirement / architecture | `PRD/CHG-20260905-050` revision 02 / `ADR-20260905-038` revision 02 |
| Effect scope | Read-only local observations and official documentation; no acquired tool execution, package build/deploy/remove, certificate operation, host activation or provider effect |

## Reviewer evidence independent of the research helper

### Package removal is a lifecycle boundary

`PackageManager.RemovePackageAsync` acts for the current user, provides an asynchronous
deployment result, and cannot cancel a removal request. Windows shuts down applications
associated with the package. Other users can retain the shared payload. Therefore a
packaged caller's callback cannot be the sole complete-removal witness; timeout is
unknown outcome, not proof that nothing happened and not permission for blind retry.
This is a design inference from the [native removal contract][remove-api], not a
Johnny self-removal experiment.

The PowerShell removal command accepts an exact package full name and normally applies
to the current user. Its `-WhatIf` option performs no removal, and it produces no result
object certifying Johnny cleanup. No all-user removal is proposed. An exact independent
post-operation query remains necessary. [Remove-AppxPackage][remove-command]

### A new Windows user is not sufficient certificate isolation

Microsoft's App Installer troubleshooting instructions require test-certificate trust
in the Local Computer Trusted People store, not merely CurrentUser. Consequently, a
new user on this workstation would not isolate that trust change from other users.
Use an approved disposable VM (or an equivalently proved isolated Windows machine)
for self-signed deployment tests; do not weaken the workstation trust store to make
a POC pass. [Microsoft signing troubleshooting][trust]

The parent ran only these relevant discovery commands:

```powershell
Get-Command WindowsSandbox.exe, vmconnect.exe, dotnet.exe, nuget.exe, cl.exe -ErrorAction SilentlyContinue
Test-Path -LiteralPath (Join-Path $env:windir 'System32\WindowsSandbox.exe')
dotnet.exe --list-sdks
Test-Path -LiteralPath (Join-Path $env:windir 'Microsoft.NET\Framework64\v4.0.30319\csc.exe')
```

Observed on this workstation:

```text
WindowsSandbox.exe NOT_ON_PATH; absolute System32 path absent
vmconnect.exe C:\Windows\system32\vmconnect.exe
dotnet.exe C:\Program Files\dotnet\dotnet.exe
nuget.exe NOT_ON_PATH
cl.exe NOT_ON_PATH
10.0.203 [C:\Program Files\dotnet\sdk]
10.0.302 [C:\Program Files\dotnet\sdk]
Framework64\v4.0.30319\csc.exe exists: True
```

Compiler/VM client presence does not prove a build, available VM, hypervisor, license,
MSIX deployment capability or valid signature. No VM inventory or certificate/key
material was read. `cl.exe` not on PATH does not prove it is absent from the machine.

### Existing ZIP composition is not the MSIX adapter

At the query-authority source, `johnny_live_install.py:108` runs a ZIP manifest,
writable-venv/payload/launcher transaction and persists its legacy uninstall ledger.
That is not package-manager deployment or proof of selected-host activation.
`live_uninstall_composition.py:58` still defines `_ScriptedShutdownPort` whose three
operations return `True`; it cannot be evidence of a live runner having stopped.
These are bounded source observations, not changes or a blanket claim that all other
host/runtime adapters are absent. Do not dispatch a wholesale rewrite of those modules.

## Replacement acceptance map — engineering proposal, not implementation authority

| Preserved requirement | Necessary MSIX-specific refinement / proof |
| --- | --- |
| AC-01 per-user ownership | Package deployment uses current-user scope on a policy/trust-qualified device; distinguish installation privilege from trust provisioning. Prove no target writes. |
| AC-02 host lifecycle | Package presence and each selected host's activation are separate states. Unsupported/failed host activation must not erase a useful package or claim full readiness. |
| AC-03 owned state | Resolve package identity/location through Windows; admit mutable state separately. Never assign WindowsApps or a legacy writable root to an arbitrary recursive cleanup owner. |
| AC-06 complete removal | Accepted Johnny order: stop owned work, remove/verify owned host integration, settle state, remove package, independently verify the current user's absence. Direct Windows removal retains the disclosed external-cleanup limitation. |
| AC-07 recovery | Persist only necessary metadata outside the disappearing package before removal; ambiguous/timeout/partial outcomes block completion and require fresh observation before a bounded retry. Prove final recovery-evidence retirement without a leftover runtime. |
| AC-12 immutable candidate | Bind exact source, SDK/runtime/dependency artifacts, manifest identity, unsigned/signed artifact hashes, signing policy and real isolated lifecycle evidence. Do not reuse Inno or ZIP qualification. |

Per-user absence must not be described as removal of another user's shared Windows
payload. Package rollback and mutable-schema rollback need separate acceptance.
The owner-selected removal behavior is not reopened by any engineering gap here.

## Reviewed MC1–MC5 capability matrix

Luna returned `FINDINGS` in this session after a read-only query. The parent reviewed
the cited primary sources and owns the following synthesis; recipes below were **not
executed**. This is research completion, not release/code-review approval.

| Cell | Status | Native mechanism / evidence | Race and failure boundary | Future adversarial reproduction |
| --- | --- | --- | --- | --- |
| MC1 | `DOCUMENTED_NOT_EXECUTED`; MakeAppx/SignTool `UNAVAILABLE` in searched locations | Microsoft SDK tools; [pinned NuGet package][sdk], [Microsoft acquisition route][sdk-route], [MakeAppx][pack], [NuGet verification][verify]. | A package name/version or valid archive is not proof of executable provenance, dependencies or compatibility. Pin before use; verify before starting acquired code. | Alter one acquired binary or substitute another SDK version; reject before execution. A successful unsigned pack must remain non-installation evidence. |
| MC2 | `DOCUMENTED_NOT_EXECUTED / REQUIRES_ISOLATED_EXECUTION` | `GetCurrentPackageFullName`, `GetCurrentPackagePath`, manifest AUMID activation and independent package query; [identity detection][identity], [path API][path], [AUMID][aumid]. | Update can change installed location. No-package and unexpected API error are distinct; never guess WindowsApps paths or treat an unpacked exe launch as packaged activation. | Compare an unpackaged launch against signed installation followed by AUMID launch; compare runtime identity/path with independent readback. Repeat after update. |
| MC3 | `DOCUMENTED_NOT_EXECUTED / REQUIRES_ISOLATED_EXECUTION` | Exact-current-user native removal plus independent observer; [remove API][remove-api], [command][remove-command]. | Caller may terminate; timeout is unresolved; shared payload can remain for another user. The observer's identity, lifetime, retry and evidence retirement are not yet proved. | Keep a packaged process/file open; request removal, preserve actual deployment result, independently query after completion or timeout. Separately test another user's registration in an approved isolated VM. |
| MC4 | `REQUIRES_ISOLATED_EXECUTION` | Exact candidate, trusted test signature, qualified disposable Windows environment and clean target/host sentinels; [trust prerequisite][trust], [package behavior][behavior]. | User isolation does not isolate machine certificate trust. Signer/Publisher, architecture, dependency and policy mismatches must not touch targets or falsely activate hosts. | Wrong Publisher/certificate, missing dependency, genuinely lower version, update interruption and foreign-state collision; record deployment result and unchanged target/host evidence. |
| MC5 | `REQUIRES_ISOLATED_EXECUTION` | Independent package, owned state and each selected host observation; accepted CHG-050 removal semantics. | Package presence, exit zero, local callback or echoed success is not complete activation/removal. Direct Windows removal does not promise external registration cleanup. | Deliberately skip host activation; interrupt removal; directly remove the package while an external-host sentinel remains. Reject every unjustified READY/COMPLETE result. |

### MC1 acquisition candidate, not a qualified toolchain

The parent read the exact NuGet page for `Microsoft.Windows.SDK.BuildTools`
`10.0.28000.2705`, published 2026-08-26, owned by Microsoft/WindowsSDK. Its metadata
lists no NuGet dependencies; that says nothing conclusive about native DLL/runtime
requirements. Microsoft documents the NuGet acquisition route. No archive was
downloaded, so its **actual internal tool paths, package hash and binary signatures
are not locally known**. SDK versions are build inputs, not the target OS version.
Windows 10 build 19045 compatibility must be tested, not inferred from this page.

The next acquisition must bind the official feed and exact version, verify NuGet
signature/provenance, inspect archive entries before extraction, then record precise
tool paths, native dependency closure, executable Authenticode identities and hashes.
`dotnet nuget verify --all` checks signatures; it is not full tool safety validation.
Any certificate fingerprint allowlist must come from independently authenticated
provenance, not from the candidate that it is meant to validate. Verification failure
blocks execution; it does not authorize disabling signature checks or adding trust.
The existing .NET SDK can run this verification command; a new global NuGet install
is not a prerequisite.

Helper observations at the authority commit: Windows 10 Pro `10.0.19045` x64;
PowerShell `7.6.5` Core; Python `3.11.9`. MakeAppx/SignTool were not on PATH, and both
`C:\Program Files (x86)\Windows Kits\10\bin` and its `App Certification Kit` sibling
were absent. These bounded negative probes do not claim an exhaustive disk search.

### Reviewer corrections to the helper return

- Do not label `0x80073CF9` uniquely as a missing-dependency error or combine
  same-version installation and downgrade into one case. Preserve actual HRESULT and
  deployment evidence; those two version cases are distinct.
- `DeferRemovalWhenPackagesAreInUse` appears in the [enum documentation][options],
  but its runtime behavior on the selected OS was not executed. Do not make that
  option or an in-use error code an assumed removal guarantee.
- NuGet's absence of declared dependencies does not mean standalone native tools.
- New-user staging is valid only within an appropriately isolated/trusted machine;
  the local VM client alone is no evidence of such an environment.

## Concrete next proof and remaining authority

The smallest useful next engineering slice is a disposable MSIX probe, not the full
installer: pinned user-local SDK acquisition; a minimal packaged desktop entry point
that reports its own identity/path; independent install/update/remove observations;
then the Johnny cleanup-before-removal path with fault injection. Host adapters and
legacy-state migration follow this proof instead of being rebuilt speculatively.

Before package-effect implementation, freeze that probe's exact source/runtime and
finite acceptance in a replacement SPEC/ticket. Build acceptance must include real
MakeAppx packing **and extraction** plus content/manifest comparison; no `/nv` bypass.
An unsigned artifact can close that build-only slice but cannot close deployment.
Production Python/dependency bundling is separate from a minimal probe's test runtime.

Live lifecycle execution requires an owner-named disposable Windows VM/machine and
explicit authority for test-only certificate creation/trust inside it. A new local
user or enabling Sandbox/Hyper-V is not silently substituted. Production publisher,
company trust/distribution and release remain later distinct authority. The report
does not authorize those effects, an external helper service, or a weakened removal
contract. The self-removal observer remains a named **unproved engineering mechanism**,
not a claim that MSIX is impossible.

Return: `ResearchReturn.FINDINGS -> ACTION_COMPLETED`. The CAP inquiry is complete
with bounded gaps; replacement implementation remains non-dispatchable until its
exact acceptance/authority is closed. No package lifecycle test ran, no code test was
claimed, no package was installed, and no push/release occurred.

[remove-api]: https://learn.microsoft.com/en-us/uwp/api/windows.management.deployment.packagemanager.removepackageasync?view=winrt-26100
[remove-command]: https://learn.microsoft.com/en-us/powershell/module/appx/remove-appxpackage?view=windowsserver2025-ps
[trust]: https://learn.microsoft.com/en-us/windows/msix/msix-troubleshooting-guide
[sdk]: https://www.nuget.org/packages/Microsoft.Windows.SDK.BuildTools/10.0.28000.2705
[sdk-route]: https://learn.microsoft.com/en-us/azure/artifact-signing/how-to-signing-integrations
[pack]: https://learn.microsoft.com/en-us/windows/msix/package/create-app-package-with-makeappx-tool
[verify]: https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-nuget-verify
[identity]: https://learn.microsoft.com/en-us/windows/msix/detect-package-identity
[path]: https://learn.microsoft.com/en-us/windows/win32/api/appmodel/nf-appmodel-getcurrentpackagepath
[aumid]: https://learn.microsoft.com/en-us/windows/configuration/store/find-aumid
[behavior]: https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes
[options]: https://learn.microsoft.com/en-us/uwp/api/windows.management.deployment.removaloptions?view=winrt-26100
