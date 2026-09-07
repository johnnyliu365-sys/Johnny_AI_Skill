# ENV-MSIX-05 — Clean isolated Python packaging qualification

| Field | Value |
| --- | --- |
| Artifact ID / revision | `ENV-MSIX-05` / `04` |
| State / closure | `HALT / TOOL_POLICY_BLOCKED / NOT_EXECUTED` / `CLOSURE-ENV-MSIX-05` revision 01 |
| Authority | Owner's 2026-09-07 authorization for SDK native tools and clean Python packaging; SDK half closed at `0de3fae7473dff907c7c5f3ae0707cb90b62e286`. |
| Sources | Approved installer SPEC revision 04 sections 7/8; sealed MSIX Context revision 03; CAP-MSIX-02 exact build-input review revision 01 LF SHA256 `bf2c0419372b5962d30753237c60bc5eba9beb7699bfadbe96eb5deb44461222`. |
| Owner / lane | Parent environment action, no product implementation; same lifetime NOT_REQUIRED; same existing read-only adversarial helper, parent owns verdict. |
| Profile / language | POC / HIGH_ASSURANCE supply-chain; isolated PowerShell/.NET operations and tiny typed Python diagnostic, no product/backend/API; XSS_NOT_APPLICABLE. |
| Exact root | Fresh `tests/.johnny-runtime/env-msix-05-python-20260907`; retain on failure, no blind retry/root reuse. |
| Result boundary | Clean fixed-version build-tool runtime and one-folder diagnostic execution on this host, not Johnny runtime/MSIX/VM qualification or production security currency. |

## Fixed sources and trust

CPython's [Windows CI distribution guidance](https://docs.python.org/3.11/using/windows.html#the-nuget-org-packages)
identifies the official 64-bit NuGet `python` family for builds/scripts.
Choose exact [3.11.9](https://www.nuget.org/packages/python/3.11.9) side-by-side,
not copied installed stdlib/venv, embeddable pip workaround, global installer
or a new backend. This is the previously selected Python 3.11 toolchain, not a
claim that 3.11.9 is the newest security release.

Acquire once:
`https://api.nuget.org/v3-flatcontainer/python/3.11.9/python.3.11.9.nupkg`.
Independent pre-acquisition [NuGet catalog metadata](https://api.nuget.org/v3/catalog0/data/2024.04.02.13.14.51/python.3.11.9.json)
observed 2026-09-07: id python, version 3.11.9, published 2024-04-02,
size 17,478,009 bytes, SHA512/base64
`41On79FZ75irnOEBGFSjDV13j1nZb8m7EbB87SmQs1XwMEhrBwf3mMc8RCAXOrERh2qW6tWYFxi2BMTN1xxVjQ==`.
Require both exact metadata digest/size and native NuGet verification before extraction.

Use only existing absolute `C:/Program Files/dotnet/dotnet.exe`,
whole-file SHA256
`4377f10c78400f0370b88156773de9843c07f14e65b3232005ec3179ef38d463`,
Valid Microsoft .NET Authenticode, selected SDK 10.0.302; no verifier install/update.
Private config: signatureValidationMode=require; packageSources clear;
trustedSigners clear; repository nuget.org, serviceIndex
`https://api.nuget.org/v3/index.json`, allowUntrustedRoot=false.
Allowed repository certificate SHA256 values are the two certificates valid at
the package's April 2024 publication, independently read from
[NuGet RepositorySignatures/5.0.0](https://api.nuget.org/v3-index/repository-signatures/5.0.0/index.json):
`5a2901d6ada3d18260b9c6dfe2133c95d74b9eef6ae0e5dc334c8454d1477df4`
(2021-02-16..2024-05-15) and
`1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d`
(2024-02-23..2027-05-18). Native code-signing/timestamp chain must validate;
expired-at-present is not bypassed by disabling trust checks. No candidate-derived
signer addition or certificate import. A separate wrong-signer config uses only
64 zeroes and must fail NU3034 before extraction. DTD-prohibited nuspec read
must confirm python/3.11.9, not trust its filename alone.

Acquire the **seven exact wheels and SHA256 pins** in CAP-MSIX-02's table,
unchanged, once each, to private wheels/. Source URLs must match that committed
table byte-for-byte. TLS/byte identity only: no claim of independently verified
wheel-author/build attestation. No source distribution, extras, git dependency,
alternate mirror, version substitution, automatic update or network pip resolver.
PyInstaller 6.22.2, altgraph 0.17.5, packaging 26.3, pefile 2024.8.26,
hooks-contrib 2026.7, pywin32-ctypes 0.2.3, setuptools 84.0.0.

Every HTTP transfer: HTTPS exact URI, no redirects/proxy/default credentials/
cookies, 60-second ceiling, maximum 64 MiB memory buffer, CreateNew file.
Check expected digest before disk publication and again after. Record full command,
status/URI/length/digest; no retries, private feeds, secrets or global config.
The trusted OS/.NET network/trust stack remains an explicit prerequisite, not
same-user/admin-compromise resistance or a zero OS-managed-cache-I/O claim.

## Isolated execution scope

Require fresh root and non-reparse ancestors before mutation. Extract only tools/
members from verified NuGet ZIP into python/, safe exact prefix/segments, no
case-colliding paths, links, device names, trailing-dot/space or escape; maximum
4096 files, 32 MiB/member, 256 MiB total, CreateNew only. Check extracted bytes
against member bytes; generate complete member hash inventory under the private
root and capture its digest/count. Require valid Python Software Foundation
Authenticode on python.exe/python311.dll; record all native file names/hashes/
signature status, without requiring every catalog-signed extension to have an
embedded signature. The verified archive authenticates stdlib and bundled pip.

Execute by absolute paths only, private cwd/temp/user/cache, process-only minimal
environment (Windows system PATH; no inherited Python/pip/provider settings),
Python `-I -B` where applicable. No global PATH/registry/file association/SDK
or existing Python mutation. Capture full native stdout/stderr/exits.
Each process <=60 seconds; kill only its owned PID on timeout, preserve state,
no retry. Environment intent is not a kernel sandbox.

Before installing wheels, prove interpreter 3.11.9/x64, isolated mode, sys.prefix
and import paths under this new root; import stdlib json/hashlib/ssl/sqlite3/ctypes
and read bundled pip's version/location. Run pip offline with --isolated,
PIP_CONFIG_FILE=NUL, --no-index, --no-deps, --require-hashes, --only-binary=:all:,
--no-cache-dir and exact local wheel paths from a private lock. --ignore-installed
is permitted only inside this fresh extracted Python, so bundled setuptools cannot
silently satisfy the new pin; never target the working host's installation.
First use a separate bad-hash requirements fixture for one wheel and a fresh
negative --target directory: intended hash mismatch must reject, no installed
package. Then install the valid seven wheels to this new interpreter's own prefix;
read exact versions/locations, run pip check, require no dependency conflicts.

Create a diagnostic-only Python file (main -> int, prints a fixed marker and
Python version; frozen validation checks sys.frozen and sys._MEIPASS containment).
It performs no network/file/registry operation. Real PyInstaller --onedir --noupx
build to fresh private dist/work/spec directories; no onefile, overwrite,
product import, copied venv or packaging fallback. Execute produced EXE from a
separate empty private cwd with Windows-only PATH and no Python environment;
require marker, frozen=true and runtime path under that bundle. Record output
tree inventory hash and verify original interpreter/archive inputs unchanged.
This is not proof of the future product's optional/native dependency closure.

## Finite closure

| Cell | Required observation |
| --- | --- |
| PY1 | Exact safe fresh root, trusted pinned verifier; eight bounded fixed-source transfers and byte hashes, no changed pins |
| PY2 | Python archive metadata digest/size, NuGet positive and intended wrong-signer rejection, nuspec identity, safe verified extraction/native identity |
| PY3 | Fresh isolated interpreter/stdlib/bundled pip provenance and prefix/import path readback |
| PY4 | Native pip wrong-hash rejection before install; exact offline seven-wheel install/version/location checks and pip check |
| PY5 | Real one-folder diagnostic build and produced EXE run without ambient Python, frozen/runtime path correct; no application/MSIX claim |
| PY6 | Complete commands/unreduced outputs and inventory bindings, unchanged original inputs, consumed state before same-helper review; parent final adjudication |

Output: directly indexed
`doc/reviews/local-orchestration-installer/env-msix-05-python-packaging-review.md`.
D8: final leaf write → LF hash → direct index → recompute before each commit.
No product source, MSIX registration/install/launch/upgrade/removal, VM/network
configuration, trust import, host activation, company project, signing, push or
release. Diagnostic build/run is not a product implementation lane.

Return `ACTION_COMPLETED / PYTHON_PACKAGING_QUALIFIED` only after PY1–PY6.
If any fails, record exact phase and retain root as BLOCKED; one bounded correction
under normal CodeReview, no blind retry/security weakening. Any needed change to
these fixed effects/pins requires explicit replan, not a quiet substitution.
Next declared stage is minimal real application-identity unsigned-build ticketing
under approved SPEC, after both environment qualifications; installation/signing
remain separate exact effect admission. No production certificate decision is
inferred from this environment ticket.

## Operational halt — 2026-09-07

At admitted baseline `275858692716b2ed06d7f76e1adb6cc114728466`, the execution
tool rejected process creation for the proposed qualification command with
`blocked by policy`. No native command ran; post-denial readback confirms the
exact action root absent and tracked worktree clean. All PY cells remain unproved.
The directly indexed [blocker record](../../../doc/reviews/local-orchestration-installer/env-msix-05-python-packaging-review.md)
preserves the exact unexecuted command and actual readback. No alternate-channel
retry or policy bypass. Resolve the tool-capability restriction through authorized
controls before Router continuation; prior owner authority is not missing.

## Owner-requested bounded resumption — 2026-09-07

Owner explicitly requested immediate handling and continuation after the recorded
pre-execution rejection. Read-only diagnostics found zero PowerShell parse errors,
no matching user execpolicy rule, and the exact root still absent. This does not
prove every host policy allows the request or establish the hidden rejection cause.
One submission through the same execution tool is admitted under this new owner
instruction, keeping all fixed sources, hashes, scopes and security checks; if the
tool denies again, retain that actual result and do not switch tools or policies.
No HTTP/native attempt previously occurred, so this is not an acquisition replay.

The read-only check also found an ordinary unexecuted wrapper bug: Get-LfDigest
joined repository cwd to an already absolute path, producing a nonexistent path.
Pass the canonical repository-relative CAP review path to that function; do not
remove its digest check. Rebind only the execution baseline to this revision's
admission commit. This wrapper correction is not asserted to explain the tool denial.

The bounded same-tool submission at `29fdb5d76fd4d4ed0897408e83785f8e37abfe88`
was again rejected before process creation with blocked by policy. The action root
remains absent; no native/HTTP/install attempt occurred. Review revision 03 captures
the exact request/error and read-only checks. The one requested resubmission is
consumed; no alternate channel or security-policy change. Host-side rejection
diagnosis/resolution is required, not another ceremonial owner approval.
