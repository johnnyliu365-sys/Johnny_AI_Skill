# CAP-MSIX-02 — Build-input research review

| Field | Value |
| --- | --- |
| Artifact ID / revision | `REVIEW-CAP-MSIX-02-20260906` / `01` |
| State | `RESEARCH_COMPLETE / METADATA_PINNED / BUILD_UNPROVED` |
| Query / candidate | CAP-MSIX-02 revision 01 at `a5e2847312c4b3f9a78b424af02f1fa2ac38a8f5` |
| Research / reviewer | Existing Luna/xhigh helper returned `FINDINGS`; current-session parent independently checked the items below. This is not implementation or deployment approval. |

## Findings and independent corrections

BI1: SDK `Microsoft.Windows.SDK.BuildTools` `10.0.28000.2705` is documented and listed,
published 2026-08-26; the local archive/tool is absent, not evidence that the public
package is unavailable. Acquisition URL:
[exact nupkg](https://api.nuget.org/v3-flatcontainer/microsoft.windows.sdk.buildtools/10.0.28000.2705/microsoft.windows.sdk.buildtools.10.0.28000.2705.nupkg).
Archive SHA-256, extraction layout and native closure await bounded execution.
The Artifact Signing integration's .NET requirement is not generalized into a
proven requirement for every bare SignTool operation.

Parent queried `https://api.nuget.org/v3/index.json`, selected its separately
published `RepositorySignatures/5.0.0` resource, and read
[repository signature metadata](https://api.nuget.org/v3-index/repository-signatures/5.0.0/index.json).
It reports `allRepositorySigned=true`. Its current certificate SHA-256 is
`1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d`, subject
`NuGet.org Repository by Microsoft`, validity 2024-02-23 through 2027-05-18.
This HTTPS service metadata, rather than a downloaded package's asserted signer,
is the allowlist source; verification still needs a valid code-signing/timestamp
chain and actual acquired bytes. The older 4.7.0 resource differs and is not the
selected acquisition protocol. No certificate was imported.

BI2/BI3: parent independently reran `Invoke-RestMethod` on every exact
`https://pypi.org/pypi/<name>/<version>/json`, required one compatible non-yanked
wheel and an upload before 2026-09-07T00:00:00+08:00. The helper's BI2 PyInstaller
hash had a transcription omission; its BI3 hash agrees with the official value
below. That inconsistent summary is not an accepted pin.

| Input | Exact wheel URL | SHA-256 | Uploaded UTC date |
| --- | --- | --- | --- |
| `pyinstaller==6.22.2` | [pyinstaller-6.22.2-py3-none-win_amd64.whl](https://files.pythonhosted.org/packages/3f/53/8ba1d0f6159b490f700eac6161a4be5f0d4672608a6dae9fd73679f183ee/pyinstaller-6.22.2-py3-none-win_amd64.whl) | `9b990fa6bbe143572f06644a984ad0d7aa2e2ccc6929d4916031343a5888e9a7` | 2026-08-17 |
| `altgraph==0.17.5` | [altgraph-0.17.5-py2.py3-none-any.whl](https://files.pythonhosted.org/packages/a9/ba/000a1996d4308bc65120167c21241a3b205464a2e0b58deda26ae8ac21d1/altgraph-0.17.5-py2.py3-none-any.whl) | `f3a22400bce1b0c701683820ac4f3b159cd301acab067c51c653e06961600597` | 2025-11-21 |
| `packaging==26.3` | [packaging-26.3-py3-none-any.whl](https://files.pythonhosted.org/packages/63/34/ba1c580383c9eada3711951fef0795c80b829a078d72188184bcab9dd527/packaging-26.3-py3-none-any.whl) | `d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c` | 2026-08-04 |
| `pefile==2024.8.26` | [pefile-2024.8.26-py3-none-any.whl](https://files.pythonhosted.org/packages/54/16/12b82f791c7f50ddec566873d5bdd245baa1491bac11d15ffb98aecc8f8b/pefile-2024.8.26-py3-none-any.whl) | `76f8b485dcd3b1bb8166f1128d395fa3d87af26360c2358fb75b80019b957c6f` | 2024-08-26 |
| `pyinstaller-hooks-contrib==2026.7` | [pyinstaller_hooks_contrib-2026.7-py3-none-any.whl](https://files.pythonhosted.org/packages/0a/67/350377af7b50416344ab8792756d414eef7629c618a73e9a0b13bb1552d9/pyinstaller_hooks_contrib-2026.7-py3-none-any.whl) | `24257a04c7a5a7a034cf28e39dcee20fbeeb9f043076729480f2e1b69904408a` | 2026-08-24 |
| `pywin32-ctypes==0.2.3` | [pywin32_ctypes-0.2.3-py3-none-any.whl](https://files.pythonhosted.org/packages/de/3d/8161f7711c017e01ac9f008dfddd9410dff3674334c233bde66e7ba65bbf/pywin32_ctypes-0.2.3-py3-none-any.whl) | `8a1513379d709975552d202d942d9837758905c8d01eb82b8bcc30918929e7b8` | 2024-08-14 |
| `setuptools==84.0.0` | [setuptools-84.0.0-py3-none-any.whl](https://files.pythonhosted.org/packages/95/9c/c510029fc6ef33a6275cd2c5d3cecd6613dfd6aa401d57c54f1c18852ccf/setuptools-84.0.0-py3-none-any.whl) | `51a52592b3b99e102b609654876bd65f19f999935166d1352678931132b0c670` | 2026-08-08 |

For Windows/Python 3.11, PyInstaller's default dependency edges are altgraph,
packaging>=22.0, pefile>=2022.5.30, hooks-contrib>=2026.6, pywin32-ctypes>=0.2.1,
setuptools>=42.0.0. Hooks-contrib adds packaging>=22.0. Python<3.10, Darwin and
optional extras are excluded. Setuptools has optional extra dependencies, not an
empty unconditional metadata list; no extras are selected. The seven-wheel set
is metadata-resolved, not installed or resolver/build-tested.

PyPI `has_sig=false` is not proof that every kind of attestation is absent. Parent
also queried the official [Integrity API](https://docs.pypi.org/api/integrity/)
for each exact wheel: packaging has provenance metadata claiming GitHub
`pypa/packaging`, `publish.yml`, environment `pypi`; the other six return HTTP 404.
No attestation was cryptographically verified in this query. TLS/hash pins establish
the recorded transport/byte identity, not independent author or build provenance.

BI4: parent reran exact native-binary signature/hash/version checks:

| Binary | Version/identity | Authenticode / SHA-256 |
| --- | --- | --- |
| Installed Python311 python.exe | CPython 3.11.9, owner-local Programs/Python/Python311 | Valid, Python Software Foundation; `5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec` |
| Same Python311 python311.dll | Interpreter DLL | Valid, Python Software Foundation; `0817a2a657a24c0d5fbb60df56960f42fc66b3039d522ec952dab83e2d869364` |
| Program Files/dotnet/dotnet.exe | SDK selected 10.0.302; verify command available | Valid, Microsoft .NET; `4377f10c78400f0370b88156773de9843c07f14e65b3232005ec3179ef38d463` |

The signature checks do not authenticate every installed stdlib file. Complete
runtime provenance remains unproved; copying a working-machine venv is prohibited.
No source-build ticket may claim a clean distributed runtime merely from these
three checks. Known SDK paths and MakeAppx/SignTool were absent in the helper's
bounded readback; that inventory is not an exhaustive machine scan.

BI5: native GetCurrentPackageFullName/GetCurrentPackagePath are two-pass APIs with
UINT32 length including NUL and LONG result; `APPMODEL_ERROR_NO_PACKAGE` differs
from API failure. Parent checked Microsoft's [full-name API](https://learn.microsoft.com/en-us/windows/win32/api/appmodel/nf-appmodel-getcurrentpackagefullname)
and [NuGet verification contract](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-nuget-verify).
The minimal full-trust manifest and pack/unpack recipes remain documented, not
executed. Unpackaged readback and future AUMID launch require distinct observations.

## Return and exact next boundary

`ResearchReturn.FINDINGS -> ACTION_COMPLETED` closes the read-only query. No helper
file/ref/package/VM effect occurred. Parent metadata and native installed-tool
queries also made no installation/trust change. Next is bounded SDK archive
acquisition and verification, not executing SDK tools, installing Python packages,
source implementation, signing, MSIX installation or a release. Full native/runtime
closure remains a required precursor to the unsigned build; no claim is promoted
from METADATA_PINNED to QUALIFIED by this report.
