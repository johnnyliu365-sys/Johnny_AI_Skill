# ENV-MSIX-03 — Quarantine and verify the exact SDK archive

| Field | Value |
| --- | --- |
| Artifact ID / revision | `ENV-MSIX-03` / `01` |
| State / closure | `OPEN / BOUNDED_ACTION_ADMITTED` / `CLOSURE-ENV-MSIX-03`, revision 01 |
| Kind / authority | Reviewer-owned environment preparation, decomposed from the owner's environment/project-convergence authorization and approved SPEC revision 04 sections 7.1/8. No app installation, SDK code execution, signing, VM or host registration authority. |
| Inputs | SPEC revision 04; sealed MSIX Context revision 03; CAP-MSIX-02 indexed research review; immutable action/registry commit supplied at execution |
| Action owner/reviewer | Current-session parent; zero implementation owners, no product source. One existing read-only adversarial helper may audit this exact action. |
| Profile / exemption | POC / HIGH_ASSURANCE supply-chain verification; `DOCS_ONLY` control record, native operational checks instead of invented unit tests |
| Workspace / lane | Parent's current repository; no new branch/worktree; same lifetime, bridge `NOT_REQUIRED` |
| Output root | Exact new child `tests/.johnny-runtime/env-msix-03-sdk-20260906` in this checkout; refuse pre-existing child or any reparse ancestor. Artifacts remain quarantined, not installed or used as executable inputs. |
| Language / XSS | No product language change; bounded PowerShell/.NET native tool operation; `XSS_NOT_APPLICABLE` |

## One closure

Download the exact public SDK archive once into a new owned quarantine, verify its
signature using the separately observed NuGet repository certificate and existing
trusted .NET verifier, and show a corrupted sibling archive is rejected. Return
`ARCHIVE_SIGNATURE_VERIFIED` or a named failure. Neither result qualifies SDK native
DLL closure, PyInstaller, Python runtime, MSIX build or deployment.

## Fixed input and effect boundaries

- HTTPS URL: `https://api.nuget.org/v3-flatcontainer/microsoft.windows.sdk.buildtools/10.0.28000.2705/microsoft.windows.sdk.buildtools.10.0.28000.2705.nupkg`.
- No redirects, credentials, alternate source/version or automatic retry. Maximum
  buffered download 512 MiB, HTTP timeout 180 seconds. Write exact
  `sdk.nupkg` with `CreateNew` only after complete successful HTTP transfer.
- Existing `C:\Program Files\dotnet\dotnet.exe` must match SHA-256
  `4377f10c78400f0370b88156773de9843c07f14e65b3232005ec3179ef38d463`,
  valid Microsoft Authenticode and selected SDK `10.0.302` before verification.
  Working host is trusted for its installed OS/.NET implementation; this is not a
  defense against compromised same-user/admin/system processes.
- Repository signer SHA-256:
  `1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d`,
  separately observed from NuGet's RepositorySignatures/5.0.0 resource. Never derive
  the allowlist from `sdk.nupkg` itself, and never allow an untrusted certificate root.
- Parent creates only `nuget.config`, `sdk.nupkg`, one `sdk-tampered.nupkg`, and
  .NET/NuGet operational-home/temp/cache children in the exact output root. Native
  stdout is evidence; no raw user config is read or copied. OS-managed certificate
  revocation/cache activity is not a trust-policy edit and is not claimed absent.
- Config contains only `signatureValidationMode=require`, a cleared package source
  list and the fixed NuGet trusted repository signer below; no ambient user/private
  feed configuration. CLI also supplies the exact certificate fingerprint.
- No extraction, execution of archive contents, pip/SDK installation, elevation,
  certificate create/import/export, VM changes, project-source changes, git push or
  delete/overwrite/cleanup. Failure retains quarantine for named recovery; no broad
  deletion or success claim. This ticket does not touch the working installation.

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <config><add key="signatureValidationMode" value="require" /></config>
  <packageSources><clear /></packageSources>
  <trustedSigners>
    <clear />
    <repository name="nuget.org" serviceIndex="https://api.nuget.org/v3/index.json">
      <certificate fingerprint="1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d" hashAlgorithm="SHA256" allowUntrustedRoot="false" />
    </repository>
  </trustedSigners>
</configuration>
```

## Native verification contract

Invoke only the admitted existing `dotnet.exe`, with a private operational home/temp
and the exact output root as cwd. Before using the acquired archive as anything
other than untrusted verifier input:

```text
dotnet nuget verify sdk.nupkg --all --certificate-fingerprint 1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d --configfile nuget.config --verbosity normal
```

Positive acceptance needs exit zero, signature output bound to the exact SDK
package/version and admitted repository signer, plus actual byte length and SHA-256.
A named archive entry observation via a read-only ZIP parser must agree on package
ID/version; no automatic extraction. Corrupt one byte in a **CreateNew sibling copy**
only, verify that copy with identical policy and require a nonzero result. Read the
unfiltered outputs. Then prove the original digest is unchanged and verify the
original again; no claim from a reduced summary or a request echo.

| Cell | Required observation |
| --- | --- |
| EV1 | Fresh contained non-reparse root; exact existing verifier hash/signature/version; no acquired-code execution |
| EV2 | Exact successful bounded HTTP transfer; archive size/hash; no alternate origin/version/retry |
| EV3 | Exact archive verifies under independent signer policy; native ID/version readback; no disabled verification |
| EV4 | Corrupted-copy native rejection, original digest unchanged, original reverify green |
| EV5 | Parent/reviewer and one read-only adversarial helper inspect the exact candidate record; absence of source/VM/trust/registration mutations; retained artifacts identified, not called installed |

Return `ACTION_COMPLETED / ARCHIVE_SIGNATURE_VERIFIED` only after EV1–EV5. Failure
is `BLOCKED` with exact phase/native result and retained relative evidence names.
Source/build dispatch still waits for native SDK closure and complete pinned runtime
qualification; it must not be unlocked by this archive-only result.
