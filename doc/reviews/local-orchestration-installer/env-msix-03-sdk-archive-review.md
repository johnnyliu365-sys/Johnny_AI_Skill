# ENV-MSIX-03 — SDK archive verification correction review

| Field | Value |
| --- | --- |
| Artifact ID / revision | `REVIEW-ENV-MSIX-03-20260907` / `03` |
| State | `REPLAY_REVIEW_PENDING / PRIOR_FINDING_OPEN` |
| Execution candidate / closure | `4f100786199bf0ccda5698fa3f025477db097bb6` / `CLOSURE-ENV-MSIX-03` revision 02 |
| Parent / scope | Current-session reviewer; archive verification only, no acquired SDK code executed. |

## Finding and correction

Revision 01 at `afb071b4` failed EV3 with native exit 1 / NU3034 because its CLI primary-signature fingerprint filter used the NuGet repository countersigner. The original helper identified a ticket-command defect. Revision 02 removed only that incompatible filter; `signatureValidationMode=require`, the original independently sourced repository fingerprint and `allowUntrustedRoot=false` are unchanged. No candidate-derived author was added to trust.

The original archive is 22,297,017 bytes, SHA256 `8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed`. It remains in `tests/.johnny-runtime/env-msix-03-sdk-20260906`, with its original config, fresh wrong-signer config, one corrupted sibling and private .NET home/cache/temp children. No cleanup, extraction, installation, VM mutation, trust-store change or release occurred. Original EV1/EV2 creation/download are historical execution evidence; this correction rechecked containment/non-reparse ancestry and original hash instead of repeating acquisition.

## Native verifier and command environment

Exact executable `C:\Program Files\dotnet\dotnet.exe`, SHA256 `4377f10c78400f0370b88156773de9843c07f14e65b3232005ec3179ef38d463`, valid Microsoft .NET Authenticode, selected SDK `10.0.302` were reread before these runs. Cwd is the exact quarantine. Process-only DOTNET_CLI_HOME, NUGET_PACKAGES, TEMP/TMP point to its existing dotnet-home/cache/temp children; telemetry/no-logo flags are set only for the invocation. Existing OS/.NET certificate trust is used without policy edits. OS revocation/cache activity is not claimed absent.

All stdout below is unreduced tool output, with only CRLF rendered as LF. These are non-production qualification commands, not provider/user transcripts. Native exit markers are explicit; the surrounding shell's exit is not substituted for them. Wrong-signer trust changes and corrupt bytes are different attack doors. The two negative errors are expected and are not suppressed. Success is archive-scoped, not host/package readiness.

## EV3 positive

Command: `dotnet nuget verify sdk.nupkg --all --configfile nuget.config --verbosity normal`

```text
2026-09-07T05:49:17.8464921Z
X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行程式碼簽署。
X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行時間戳記。

正在驗證 Microsoft.Windows.SDK.BuildTools.10.0.28000.2705
內容雜湊: TZQ96xtu7+fyFsyJCgj6Hazru0H8G1kiE1CeZLGpsqT4xKQmkxWu9yRuxYLeHJECjqEHN7duZUTcdbt8zlQ8OQ==
C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\tests\.johnny-runtime\env-msix-03-sdk-20260906\sdk.nupkg
簽章雜湊演算法: SHA256

簽章類型: Author
正在利用以下憑證驗證 作者主要簽章: 
  主體名稱: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
  SHA1 雜湊: F25C45D17C53D4E0D1DC9FB9DFD0731FCF904B77
  SHA256 雜湊: 566A31882BE208BE4422F7CFD66ED09F5D4524A5994F50CCC8B05EC0528C1353
  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2023/7/27 上午 08:00:00 至 2026/10/18 上午 07:59:59
時間戳記: 2026/8/15 上午 04:35:41
正在利用以下時間戳記服務憑證，驗證 作者主要簽章 的時間戳記: 
  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O="DigiCert, Inc.", C=US
  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E
  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33
  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59

簽章類型: Repository
服務索引: https://api.nuget.org/v3/index.json
擁有者: Microsoft, WindowsSDK
正在利用以下憑證驗證 存放庫副署: 
  主體名稱: CN=NuGet.org Repository by Microsoft, O=NuGet.org Repository by Microsoft, L=Redmond, S=Washington, C=US
  SHA1 雜湊: C72FE7739A9EECB8EC1E4F596DB3BB74039B1DE2
  SHA256 雜湊: 1F4B311D9ACC115C8DC8018B5A49E00FCE6DA8E2855F9F014CA6F34570BC482D
  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2024/2/23 上午 08:00:00 至 2027/5/19 上午 07:59:59
時間戳記: 2026/8/26 下午 12:54:00
正在利用以下時間戳記服務憑證，驗證 存放庫副署 的時間戳記: 
  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O="DigiCert, Inc.", C=US
  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E
  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33
  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59

已成功驗證套件 'Microsoft.Windows.SDK.BuildTools.10.0.28000.2705'。
EV3_POSITIVE_EXIT=0
```

## EV3 independent wrong-signer policy control

Command: `dotnet nuget verify sdk.nupkg --all --configfile nuget-wrong-signer.config --verbosity normal`

```text
2026-09-07T05:49:39.8254797Z
X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行程式碼簽署。
X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行時間戳記。

正在驗證 Microsoft.Windows.SDK.BuildTools.10.0.28000.2705
內容雜湊: TZQ96xtu7+fyFsyJCgj6Hazru0H8G1kiE1CeZLGpsqT4xKQmkxWu9yRuxYLeHJECjqEHN7duZUTcdbt8zlQ8OQ==
C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\tests\.johnny-runtime\env-msix-03-sdk-20260906\sdk.nupkg
簽章雜湊演算法: SHA256

簽章類型: Author
正在利用以下憑證驗證 作者主要簽章: 
  主體名稱: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
  SHA1 雜湊: F25C45D17C53D4E0D1DC9FB9DFD0731FCF904B77
  SHA256 雜湊: 566A31882BE208BE4422F7CFD66ED09F5D4524A5994F50CCC8B05EC0528C1353
  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2023/7/27 上午 08:00:00 至 2026/10/18 上午 07:59:59
時間戳記: 2026/8/15 上午 04:35:41
正在利用以下時間戳記服務憑證，驗證 作者主要簽章 的時間戳記: 
  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O="DigiCert, Inc.", C=US
  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E
  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33
  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59

簽章類型: Repository
服務索引: https://api.nuget.org/v3/index.json
擁有者: Microsoft, WindowsSDK
正在利用以下憑證驗證 存放庫副署: 
  主體名稱: CN=NuGet.org Repository by Microsoft, O=NuGet.org Repository by Microsoft, L=Redmond, S=Washington, C=US
  SHA1 雜湊: C72FE7739A9EECB8EC1E4F596DB3BB74039B1DE2
  SHA256 雜湊: 1F4B311D9ACC115C8DC8018B5A49E00FCE6DA8E2855F9F014CA6F34570BC482D
  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2024/2/23 上午 08:00:00 至 2027/5/19 上午 07:59:59
時間戳記: 2026/8/26 下午 12:54:00
正在利用以下時間戳記服務憑證，驗證 存放庫副署 的時間戳記: 
  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O="DigiCert, Inc.", C=US
  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E
  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33
  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59

已完成，有 1 個錯誤和 0 個警告。
error: NU3034: 此套件已簽署，但不是由受信任簽署者所簽署。

套件特徵標記驗證失敗。
EV3_WRONG_SIGNER_EXIT=1
```

## EV4 corrupted sibling and restored original

Command: `CreateNew sibling: byte 11148508 XOR 1; dotnet nuget verify sdk-tampered.nupkg --all --configfile nuget.config --verbosity normal; then original digest and original verify`

```text
2026-09-07T05:50:03.6870540Z
TAMPER_OFFSET=11148508 BEFORE=162 AFTER=163
X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行程式碼簽署。
X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行時間戳記。

正在驗證 Microsoft.Windows.SDK.BuildTools.10.0.28000.2705
內容雜湊: mZ5bE870O3M8HcsV09GggAINNAeoIOqygIxbvKYhr0B2C3+k/n8Ubq5IWZ2exIvHGLjtY2T/G7eRXhRjj9qFOQ==
C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\tests\.johnny-runtime\env-msix-03-sdk-20260906\sdk-tampered.nupkg
簽章雜湊演算法: SHA256

簽章類型: Author
正在利用以下憑證驗證 作者主要簽章: 
  主體名稱: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
  SHA1 雜湊: F25C45D17C53D4E0D1DC9FB9DFD0731FCF904B77
  SHA256 雜湊: 566A31882BE208BE4422F7CFD66ED09F5D4524A5994F50CCC8B05EC0528C1353
  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2023/7/27 上午 08:00:00 至 2026/10/18 上午 07:59:59
時間戳記: 2026/8/15 上午 04:35:41
正在利用以下時間戳記服務憑證，驗證 作者主要簽章 的時間戳記: 
  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O="DigiCert, Inc.", C=US
  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E
  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33
  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59

簽章類型: Repository
服務索引: https://api.nuget.org/v3/index.json
擁有者: Microsoft, WindowsSDK
正在利用以下憑證驗證 存放庫副署: 
  主體名稱: CN=NuGet.org Repository by Microsoft, O=NuGet.org Repository by Microsoft, L=Redmond, S=Washington, C=US
  SHA1 雜湊: C72FE7739A9EECB8EC1E4F596DB3BB74039B1DE2
  SHA256 雜湊: 1F4B311D9ACC115C8DC8018B5A49E00FCE6DA8E2855F9F014CA6F34570BC482D
  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2024/2/23 上午 08:00:00 至 2027/5/19 上午 07:59:59
時間戳記: 2026/8/26 下午 12:54:00
正在利用以下時間戳記服務憑證，驗證 存放庫副署 的時間戳記: 
  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O="DigiCert, Inc.", C=US
  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E
  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33
  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59

已完成，有 1 個錯誤和 0 個警告。
error: NU3008: 套件完整性檢查失敗。套件在簽署後已變更。嘗試清除本機 HTTP 快取，然後再次執行 NuGet 作業。

套件特徵標記驗證失敗。
EV4_TAMPERED_EXIT=1
ORIGINAL_SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed
X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行程式碼簽署。
X.509 憑證鏈結驗證會使用 .NET 選取的預設信任存放區進行時間戳記。

正在驗證 Microsoft.Windows.SDK.BuildTools.10.0.28000.2705
內容雜湊: TZQ96xtu7+fyFsyJCgj6Hazru0H8G1kiE1CeZLGpsqT4xKQmkxWu9yRuxYLeHJECjqEHN7duZUTcdbt8zlQ8OQ==
C:\Users\GameBoy\Desktop\Johnny_AI_Skill_latest\tests\.johnny-runtime\env-msix-03-sdk-20260906\sdk.nupkg
簽章雜湊演算法: SHA256

簽章類型: Author
正在利用以下憑證驗證 作者主要簽章: 
  主體名稱: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
  SHA1 雜湊: F25C45D17C53D4E0D1DC9FB9DFD0731FCF904B77
  SHA256 雜湊: 566A31882BE208BE4422F7CFD66ED09F5D4524A5994F50CCC8B05EC0528C1353
  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2023/7/27 上午 08:00:00 至 2026/10/18 上午 07:59:59
時間戳記: 2026/8/15 上午 04:35:41
正在利用以下時間戳記服務憑證，驗證 作者主要簽章 的時間戳記: 
  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O="DigiCert, Inc.", C=US
  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E
  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33
  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59

簽章類型: Repository
服務索引: https://api.nuget.org/v3/index.json
擁有者: Microsoft, WindowsSDK
正在利用以下憑證驗證 存放庫副署: 
  主體名稱: CN=NuGet.org Repository by Microsoft, O=NuGet.org Repository by Microsoft, L=Redmond, S=Washington, C=US
  SHA1 雜湊: C72FE7739A9EECB8EC1E4F596DB3BB74039B1DE2
  SHA256 雜湊: 1F4B311D9ACC115C8DC8018B5A49E00FCE6DA8E2855F9F014CA6F34570BC482D
  核發者: CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2024/2/23 上午 08:00:00 至 2027/5/19 上午 07:59:59
時間戳記: 2026/8/26 下午 12:54:00
正在利用以下時間戳記服務憑證，驗證 存放庫副署 的時間戳記: 
  主體名稱: CN=DigiCert SHA256 RSA4096 Timestamp Responder 2025 1, O="DigiCert, Inc.", C=US
  SHA1 雜湊: DD6230AC860A2D306BDA38B16879523007FB417E
  SHA256 雜湊: 4AA03FA22CD75C84C55C938F828E676B9CAECAB33FE36D269AA334F146110A33
  核發者: CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O="DigiCert, Inc.", C=US
  有效前間: 2025/6/4 上午 08:00:00 至 2036/9/4 上午 07:59:59

已成功驗證套件 'Microsoft.Windows.SDK.BuildTools.10.0.28000.2705'。
EV4_ORIGINAL_REVERIFY_EXIT=0
```

## ZIP identity and retained artifacts

Command: `Read exact Microsoft.Windows.SDK.BuildTools.nuspec through DTD-prohibited XmlReader (1 MiB limit), no extraction; SHA256 each retained file`

```text
NUSPEC_ID=Microsoft.Windows.SDK.BuildTools VERSION=10.0.28000.2705

FullName                                                                        Length
--------                                                                        ------
bin/10.0.28000.0/arm64/appxpackaging.dll                                       2564560
bin/10.0.28000.0/x64/appxpackaging.dll                                         2443720
bin/10.0.28000.0/x86/en-US/AppxPackaging.dll.mui                                 97224
bin/10.0.28000.0/x64/en-US/AppxPackaging.dll.mui                                 97224
bin/10.0.28000.0/x86/appxpackaging.dll                                         2077680
bin/10.0.28000.0/arm64/en-US/AppxPackaging.dll.mui                               97272
schemas/10.0.28000.0/winrt/AppxManifestSchema.xsd                                35530
schemas/10.0.28000.0/winrt/AppxManifestSchema2010_v2.xsd                         36908
schemas/10.0.28000.0/winrt/AppxManifestSchema2013.xsd                            12335
bin/10.0.28000.0/arm64/makeappx.exe                                             591320
bin/10.0.28000.0/x64/makeappx.exe                                               588272
bin/10.0.28000.0/x86/makeappx.exe                                               465352
bin/10.0.28000.0/x86/Microsoft.Windows.Build.Appx.AppxPackaging.dll.manifest      1924
bin/10.0.28000.0/arm64/Microsoft.Windows.Build.Appx.AppxPackaging.dll.manifest    1924
bin/10.0.28000.0/x64/Microsoft.Windows.Build.Appx.AppxPackaging.dll.manifest      1924
bin/10.0.28000.0/x86/signtool.exe                                               409544
bin/10.0.28000.0/arm64/signtool.exe                                             555008
bin/10.0.28000.0/x86/signtool.exe.manifest                                         968
bin/10.0.28000.0/arm64/signtool.exe.manifest                                       968
bin/10.0.28000.0/x64/signtool.exe                                               551368
bin/10.0.28000.0/x64/signtool.exe.manifest                                         968

sdk.nupkg SHA256=8bfdfb6ca2633f531cf80b5fa22512ba61a394d7988f0970db83baadc67929ed
sdk-tampered.nupkg SHA256=06add73b37945dae1488b34dcc8c92c8bd0acfded7af01c4ce14ff83544faae2
nuget.config SHA256=f297aae534f103b2572d56f9a973f824779afa952aa447ba72b32f3687c2679e
nuget-wrong-signer.config SHA256=776c18560e1f814b78d9d8a26c807168c49f599cb630cc013c120cc6748fe364
```

## Review plan and continuation

Reuse the existing read-only adversarial helper for the one correction review, bound to this record's committed evidence and the execution candidate. REQUIRED; categories SPEC_GAP, AUTHORIZATION, ERROR_PARTIAL_FAILURE, CONSISTENCY, OBSERVABILITY; isolation READ_ONLY_INTENT_ONLY; effect NO_EXTERNAL_EFFECT. It may read this ticket/report and return finite findings; it must not run tools from the archive or alter any file, ref, trust or VM. The parent alone decides closure.

Native DLL/tool closure and clean pinned Python/runtime packaging remain unqualified. Next admissible work after archive closure is bounded toolchain qualification, not a production MSIX release. No helper result can bypass that boundary.

## Correction-review result and parent conclusion — 2026-09-07

The planned helper review returned `FINDINGS` for exact evidence candidate
`1d11998eab5785859cf00d1464c5f39af54443fa` and execution candidate
`4f100786199bf0ccda5698fa3f025477db097bb6`. Both indexed leaf digests matched.
The parent reread the finite closure and committed report, independently accepts
the finding below, and owns the final `BLOCKED` conclusion. The helper did not
approve, execute the SDK, change files or acquire any additional effect authority.

### F-ENV3-01 — EV1/EV2 evidence completeness

- Classification: `EVIDENCE_DEFECT`, blocking; existing closure cells EV1 and EV2.
- Evidence: this report at `1d11998e` lines 14–18 narrates original acquisition and
  verifier/root preflight but does not preserve their complete command/result
  observations. The displayed native commands use bare `dotnet` rather than
  recording the absolute executable invocation and its preflight together.
- Missing binding: contained/non-reparse root observation; absolute verifier
  hash, valid Authenticode and selected SDK observation; original one-shot bounded
  HTTP transaction, including no redirect/alternate/retry. The archive size/hash
  and signature output do not establish those historical process properties.
- Scope: this does not invalidate the recorded native EV3/EV4 results. It prevents
  claiming the whole EV1–EV5 closure is discharged. Current filesystem readback
  would be a new observation, not retroactive evidence of the original transfer.
- Responsibility: the parent failed to persist the complete operational evidence.
  No implementer was involved; this is not attributed to implementer performance.

| Closure observation | Correction-review disposition |
| --- | --- |
| EV1 root / verifier preflight | Incomplete committed command/result binding; blocking |
| EV2 acquisition | Historical bounded transfer not fully recorded; blocking |
| EV3 positive / wrong signer | Native exit 0 / exit 1 NU3034 preserved above |
| EV4 tampered / original | Native exit 1 NU3008 / unchanged digest / exit 0 preserved above |
| EV5 review | Parent and existing helper completed the correction review; findings remain open |

The original `EVIDENCE_COMPLETE` header was premature and is superseded by this
revision's blocked conclusion; the original native outputs remain unaltered.
Per the ticket's one-correction limit and CodeReview section 5, there is no automatic
third correction, weaker trust policy, SDK extraction/execution or build/release.
No replay or reacquisition has been performed to fill the gap.

Suggested owner-scoped recovery, not admitted by this report: one evidence-only
replay with a fresh isolated acquisition and complete preflight/command/output
capture, retaining the original quarantine and all prior failures. Keep the exact
source/version, certificate policy and rejection controls; do not relabel the new
observations as the missing historical run. A documented single-use override or
reviewed replan must precede execution. MSIX build, install, upgrade, removal and
publication remain unproved; an archive review is not their substitute.

## Owner-authorized replay submitted for review — 2026-09-07

The owner granted the requested evidence-only single-use replay. Its admission is
committed at `4e8746817bd25f9a7813acd7de60aa7af640da48`, ENV-MSIX-03 document
revision 04, closure revision 02. No security predicate or signer changed. The
single attempt is now consumed; it does not grant another acquisition.

The new [replay evidence](env-msix-03-sdk-replay-evidence.md) records every actual
PowerShell command, complete returned output and exit code for EV1–EV4. This run
is not a reconstruction of the missing historical output. The original quarantine
and the historical F-ENV3-01 finding remain preserved.

The parent read the full results: 0 positive, 1/NU3034 wrong signer, 1/NU3008
corrupted copy, 0 unchanged-original reverify; HTTP transfer and absolute verifier
preflight are now captured. Config files were generated from the committed ticket
template into CreateNew fixtures, not copied from ambient user configuration.
Operational commands create only the admitted quarantine artifacts; no product
source, SDK execution, installation, VM, trust-store, host, push or release effect
is admitted or requested. Successful native archive checks are not package readiness.

Review plan: reuse the same existing read-only helper for the finite review of this
committed replay; REQUIRED; categories SPEC_GAP, AUTHORIZATION,
ERROR_PARTIAL_FAILURE, CONSISTENCY, OBSERVABILITY; isolation READ_ONLY_INTENT_ONLY;
effect NO_EXTERNAL_EFFECT. It reads only the exact ticket, this review and replay
evidence plus their direct index rows, and returns findings, not approval. Parent
alone adjudicates F-ENV3-01 and EV1–EV5. Until that outcome is written, no closure
approval or build/installation continuation is inferred.
