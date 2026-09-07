# ENV-MSIX-03 — Quarantine and verify the exact SDK archive

| Field | Value |
| --- | --- |
| Artifact ID / revision | `ENV-MSIX-03` / `04` |
| State / closure | `OWNER_SINGLE_USE_REPLAY_ADMITTED / EVIDENCE_REPAIR_ONLY` / `CLOSURE-ENV-MSIX-03`, revision 02 (unchanged) |
| Kind / authority | Reviewer-owned environment preparation, decomposed from the owner's environment/project-convergence authorization and approved SPEC revision 04 sections 7.1/8. No app installation, SDK code execution, signing, VM or host registration authority. |
| Inputs | SPEC revision 04; sealed MSIX Context revision 03; CAP-MSIX-02 indexed research review; immutable action/registry commit supplied at execution |
| Action owner/reviewer | Current-session parent; zero implementation owners, no product source. One existing read-only adversarial helper may audit this exact action. |
| Profile / exemption | POC / HIGH_ASSURANCE supply-chain verification; `DOCS_ONLY` control record, native operational checks instead of invented unit tests |
| Workspace / lane | Parent's current repository; no new branch/worktree; same lifetime, bridge `NOT_REQUIRED` |
| Output root | Original `tests/.johnny-runtime/env-msix-03-sdk-20260906` retained untouched. The revision-04 single-use override below admits only fresh sibling `tests/.johnny-runtime/env-msix-03-sdk-replay-20260907-01`; artifacts remain quarantined, never executable inputs. |
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
- Parent creates only `nuget.config`, `sdk.nupkg`, one `sdk-tampered.nupkg`, one
  `nuget-wrong-signer.config` negative fixture, and
  .NET/NuGet operational-home/temp/cache children in the exact output root. Native
  stdout is evidence; no raw user config is read or copied. OS-managed certificate
  revocation/cache activity is not a trust-policy edit and is not claimed absent.
- Config contains only `signatureValidationMode=require`, a cleared package source
  list and the fixed NuGet trusted repository signer below; no ambient user/private
  feed configuration. Repository trust is checked through this config, not through
  a CLI fingerprint filter restricted to the primary signature.
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
dotnet nuget verify sdk.nupkg --all --configfile nuget.config --verbosity normal
```

Positive acceptance needs exit zero, signature output bound to the exact SDK
package/version and admitted repository signer, plus actual byte length and SHA-256.
A named archive entry observation via a read-only ZIP parser must agree on package
ID/version; no automatic extraction. Corrupt one byte in a **CreateNew sibling copy**
only, verify that copy with identical policy and require a nonzero result. Read the
unfiltered outputs. Then prove the original digest is unchanged and verify the
original again; no claim from a reduced summary or a request echo.

Also verify the intact archive with a CreateNew `nuget-wrong-signer.config`, identical
to the fixed config except that the repository certificate fingerprint is 64 zeroes.
Require a nonzero result explicitly rejecting the configured trust. An exit zero is
a finding that the configuration is not carrying the claimed control, never a pass.
Do not add any certificate observed only from the candidate to either trust policy.

| Cell | Required observation |
| --- | --- |
| EV1 | Fresh contained non-reparse root; exact existing verifier hash/signature/version; no acquired-code execution |
| EV2 | Exact successful bounded HTTP transfer; archive size/hash; no alternate origin/version/retry |
| EV3 | Exact archive verifies under independent repository-signer policy; native ID/version readback; wrong-signer config rejects the intact archive; no disabled verification |
| EV4 | Corrupted-copy native rejection, original digest unchanged, original reverify green |
| EV5 | Parent/reviewer and one read-only adversarial helper inspect the exact candidate record; absence of source/VM/trust/registration mutations; retained artifacts identified, not called installed |

Return `ACTION_COMPLETED / ARCHIVE_SIGNATURE_VERIFIED` only after EV1–EV5. Failure
is `BLOCKED` with exact phase/native result and retained relative evidence names.
Source/build dispatch still waits for native SDK closure and complete pinned runtime
qualification; it must not be unlocked by this archive-only result.

## Revision-01 failure and bounded correction

Owner's 2026-09-07 instruction resumes MSIX build/lifecycle qualification, with
release conditional on completion. This correction is the archive-only prerequisite;
it does not authorize SDK execution or deployment through this leaf.

At candidate `afb071b4ced5e92aabf74130ad1678ee4ce725d2`, EV2 downloaded exactly
22,297,017 bytes; archive SHA-256 is
`8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed`.
The original command added the repository fingerprint as `--certificate-fingerprint`;
native exit 1 / NU3034 refused because its primary author signer differs from the
repository countersigner. The existing read-only adversarial helper returned this
as a blocking command-contract defect, not proof that the archive is malicious.

Parent read the [NuGet verification implementation](https://github.com/NuGet/NuGet.Client/blob/dev/src/NuGet.Core/NuGet.Commands/VerifyCommand/VerifyCommandRunner.cs)
on 2026-09-07: config trust and CLI primary-signature filters are separate providers.
That upstream source explains the correction; local positive and two negative runs
must still prove behavior on the pinned installed verifier. Revision 02 removes only
the incompatible CLI filter and adds the wrong-config control. The original failure
remains historical evidence. One correction review uses the same helper; no automatic
third correction or quiet policy weakening is permitted if it remains defective.

## Correction-review disposition — 2026-09-07

Evidence candidate `1d11998eab5785859cf00d1464c5f39af54443fa`, executed against
`4f100786199bf0ccda5698fa3f025477db097bb6`, passed the recorded EV3/EV4
positive, wrong-signer, corrupted-copy and unchanged-original verification runs.
The existing read-only helper nevertheless returned `FINDINGS`: EV1/EV2 are not
fully supported by committed command/result records. The parent independently
checked the exact ticket and evidence leaf and accepts that evidence defect.

The original bounded HTTP transaction and the verifier/root preflight are described
in prose, not preserved as the required reproducible command/result observations.
Archive authenticity does not itself prove download timeout, redirect/retry policy
or the historical root/verifier checks. This is a record-completeness failure, not
a finding that the SDK signature is invalid. See the indexed
[correction review](../../../doc/reviews/local-orchestration-installer/env-msix-03-sdk-archive-review.md)
for the finite finding and retained successful observations.

Document revision 03 records the outcome only; it does not change closure revision
02, grant another correction, reconstruct missing historical output or authorize
reacquisition. Quarantine remains untouched. Return `VALIDATION_FAILED`, with
`BLOCKED / EVIDENCE_DEFECT / CONVERGENCE_REVIEW_REQUIRED`; no
`ARCHIVE_SIGNATURE_VERIFIED`, SDK execution, build, installation or release follows.
Further correction needs the documented owner-scoped single-use override or
reviewed replan required by the ticket-set convergence rule.

## Owner single-use evidence replay — 2026-09-07

At baseline `478c566fa8c3b575b30d7cc08570b4ffbec95c25`, the parent requested
one replay limited to SDK acquisition/verification evidence, without weakening
security conditions or executing installation. The owner replied `授權`. This is
the ticket-set's documented single-use convergence override, not an automatic
third correction and not new product-source authority.

- Bind this ticket/registry's next immutable commit before operations. Parent owns
  the one action; same-lifetime bridge `NOT_REQUIRED`, no implementation dispatch.
- Fresh root is exactly `tests/.johnny-runtime/env-msix-03-sdk-replay-20260907-01`.
  Prove it absent and its existing ancestors non-reparse before creation. Existing
  original quarantine is read only for exact archive/config preservation checks.
  Existing destination is a failure, not a resume or overwrite opportunity.
- Reuse the fixed public SDK URL/version, verifier identity, independently pinned
  repository signer, timeout/size limits, CreateNew writes and no-redirect/no-retry
  policy above. No credentials or alternate source. One fresh HTTP acquisition;
  native verification may read that archive for the four declared EV3/EV4 runs.
- Record full executable command bodies and all returned output/exit values for
  preflight, bounded HTTP result, config creation/readback, native verification,
  ZIP identity and original-quarantine preservation. Exact commands plus observed
  results, not printed policy slogans or historical reconstruction, carry evidence.
  Operational snippets are evidence of this action, not shipped runtime source.
- A new directly indexed review-family evidence leaf,
  `doc/reviews/local-orchestration-installer/env-msix-03-sdk-replay-evidence.md`,
  preserves this new run. Existing review retains its earlier failures and links
  the new evidence. Same read-only adversarial helper reviews the committed replay;
  parent decides EV1–EV5. No additional helper or implementation lane.
- The override is consumed by this single attempt whether it succeeds or fails.
  No extraction, SDK code execution, installation, certificate changes, VM effects,
  host changes, push, release or cleanup. Failures retain the fresh quarantine and
  return to convergence; success closes only archive-signature qualification.

Return on admission commit: `ACTION_COMPLETED / OWNER_OVERRIDE_RECORDED`.
Continuation: `AUTO_CONTINUE` to the single evidence replay above, then its finite
review and outcome writeback. Closure revision 02's security predicates are unchanged.
