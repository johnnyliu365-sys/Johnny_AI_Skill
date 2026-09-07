# ENV-MSIX-04 — Isolated SDK native operation qualification

| Field | Value |
| --- | --- |
| Artifact ID / revision | `ENV-MSIX-04` / `01` |
| State / closure | `ADMITTED / NOT_EXECUTED` / `CLOSURE-ENV-MSIX-04` revision 01 |
| Authority | Owner's 2026-09-07 authorization following ENV-MSIX-03 closure at `35d3a4147ccf3bb28b8f924db90fad2c7c3e3f6d`: qualify SDK native tools and clean Python packaging; this leaf scopes only the SDK half. |
| Sources | Approved installer SPEC revision 04 sections 7.1/8; sealed MSIX Context revision 03; ENV-MSIX-03 approved review/evidence at baseline above. No architecture/user-behavior change. |
| Owner / lane | Current-session parent environment action; no product implementer/source, same lifetime `NOT_REQUIRED`; same existing read-only adversarial helper. |
| Profile / language | POC / HIGH_ASSURANCE supply-chain; PowerShell/.NET native operations and data-only fixtures; no new public DTO/source language; `XSS_NOT_APPLICABLE`. |
| Root | Fresh exact `tests/.johnny-runtime/env-msix-04-sdk-native-20260907`; retained on any failure, never reused/overwritten by retry. |
| Result | Build-host exercised SDK pack/unpack and signature-verification capability, not app identity/installation/readiness or universal native compatibility. |

## Fixed input and permitted effects

The already authenticated SDK archive is read only from
`tests/.johnny-runtime/env-msix-03-sdk-replay-20260907-01/sdk.nupkg`,
SHA256 `8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed`.
No re-download or package manager. Recheck hash, non-reparse ancestry and exact
ENV-MSIX-03 review/index before mutation.

Extract only these selected archive members below the new root's `tools/`,
preserving SDK layout: prefix `bin/10.0.28000.0/x64/` with names
`makeappx.exe`, `signtool.exe`, `appxpackaging.dll`, `appxsip.dll`,
`opcservices.dll`, `mssign32.dll`, `wintrust.dll`,
`signtool.exe.manifest`, `wintrust.dll.ini`,
`Microsoft.Windows.Build.Appx.AppxPackaging.dll.manifest`,
`Microsoft.Windows.Build.Appx.AppxSip.dll.manifest`,
`Microsoft.Windows.Build.Appx.OpcServices.dll.manifest`,
`Microsoft.Windows.Build.Signing.mssign32.dll.manifest`,
`Microsoft.Windows.Build.Signing.wintrust.dll.manifest`,
`en-US/AppxPackaging.dll.mui`; and all direct `.xsd` members under
`schemas/10.0.28000.0/winrt/`. Reject duplicate/case-colliding paths, unsafe
segments, symlink/reparse flags or escape; maximum 128 members, 16 MiB each and
64 MiB total. CreateNew files only. Capture every selected member's size/hash.
No unrelated SDK utility is invoked. Require valid Microsoft Authenticode for
every extracted exe/dll before invoking either executable.

Use absolute SDK executable paths, isolated cwd/temp and process-only PATH
restricted to Windows system directories. No global configuration/trust/PATH
edit. Each process is finite (60-second ceiling, terminate only that owned
process on timeout, retain evidence, no retry). Record Windows/build/bitness,
native versions, command/arguments, complete stdout/stderr and native exits.
Existing OS DLLs/OS trust are an explicit trusted build-host prerequisite;
this is not resistance to a compromised same-user/admin/system actor.

## Data-only native probe

Create a tiny **framework test package**, not Johnny's application or a second
backend. Identity `Johnny.Toolchain.Probe`, Publisher
`CN=JohnnyToolchainProbe`, version `0.0.0.1`, x64. This unsigned fixture
identity is not a production Publisher decision. It has no Applications,
Capabilities, executable or package dependency. Include framework property,
Windows.Desktop target family (MinVersion 10.0.17763.0, MaxVersionTested
10.0.26200.0), en-US resource, a generated 50x50 PNG and fixed text payload.

- Positive: real `makeappx pack /v /no /h SHA256 /d <fixture> /p <new.msix>`,
  no `/nv` or weaker validation. Require exit 0.
- Round trip: real `makeappx unpack /v /no /p <new.msix> /d <fresh-unpack>`;
  compare each admitted input byte hash and distinguish generated metadata.
- Independent negative: separate fixture identical except Logo references an
  absent file. Same pack options must fail for the missing manifest file.
  Zero red is a finding. Do not add the missing file to manufacture green;
  the original valid fixture/pack remains the positive control.
- Idempotency/non-overwrite negative: pack again to the existing positive package
  with `/no`; require refusal and original package hash unchanged.
- Signing-tool probe: `signtool verify /pa /v <extracted-makeappx.exe>` must
  validate the already signed executable; `signtool verify /pa /v <unsigned.msix>`
  must reject lack of signature. No signing, new certificate or trust import.

No product source, MSIX registration/install/launch/update/removal, VM/network,
host activation, secret, company project, global installer, release or push effect.
Do not infer full-trust application identity from a framework fixture.

## Finite closure

| Cell | Required observation |
| --- | --- |
| NT1 | Exact admitted archive; fresh safe extraction; complete selected inventory and native signer/version evidence |
| NT2 | Real semantic-validation pack succeeds and fresh native unpack preserves input manifest/logo/text hashes |
| NT3 | Missing-logo fixture rejects for its intended cause; positive fixture preserved |
| NT4 | Existing-output `/no` refuses and package bytes remain unchanged |
| NT5 | SignTool verifies signed MakeAppx and refuses unsigned test MSIX without trust/signing changes |
| NT6 | Complete command/output evidence, original archive unchanged, clean tracked-source boundary, parent + same helper review; accurate consumed/lifecycle metadata |

Output: directly indexed `doc/reviews/local-orchestration-installer/env-msix-04-sdk-native-review.md`.
Capture raw output losslessly; final leaf write → LF digest → direct index → recompute
before commit. Once native action finishes, ticket/index must say executed/review
pending before helper dispatch. Review header binds the actual execution commit;
historical identities are separate. No repeated use of this action root.

Return `ACTION_COMPLETED / SDK_NATIVE_OPERATIONS_QUALIFIED` only after all cells.
Otherwise retain exact phase/native failure as `BLOCKED`; one bounded correction
under normal CodeReview rules, no blind retries or implicit security weakening.
The next serial action is clean Python/package-input qualification under its own
exact ticket, already within the owner's named environment authorization; this
ticket does not establish that Python is ready or permit app implementation.

Primary guidance checked 2026-09-07:
[MakeAppx](https://learn.microsoft.com/en-us/windows/msix/package/create-app-package-with-makeappx-tool),
[framework manifest](https://learn.microsoft.com/en-us/uwp/schemas/appxpackage/uapmanifestschema/element-f-framework).
MakeAppx validation is not a guarantee of installability.

