# L9 — One-click Installer Wrapper (`johnny-install.cmd`)

| Field | Value |
| --- | --- |
| SPEC / AC | Plugin Distribution Revision 02 AC-05, AC-06 (approved-digest entry, explicit user confirmation) |
| Requirement | Owner-direct request 2026-08-19: a double-clickable install entry for the released 0.4.1 bundle |
| State | `CLOSED` — delivery `7613aeb` plus two P1 control-plane corrections (CR-L9-01) |
| Baseline | `v0.4.1` = `0f2af25` (pushed; release asset digest frozen) |
| Workload | `SMALL` per CHG-028/CHG-029: no baseline-red (not a bugfix), compact evidence rows in the line README |
| Language / XSS | Windows cmd batch + Python 3.11 strict tests / `XSS_NOT_APPLICABLE` |

## One outcome

A release asset `johnny-install.cmd` that the user downloads next to
`johnny-ai-skill-0.4.1.zip` and double-clicks. It refuses to continue unless
the bundle's SHA-256 equals the approved release digest pinned inside it,
then extracts `install.ps1` out of the verified bundle and delegates to it.
The explicit `INSTALL` confirmation inside `install.ps1` remains the human
gate; the wrapper never answers it.

## Frozen responsibility

- The approved digest and the exact bundle file name are pinned literals
  inside the wrapper. No environment variable, argument, or file may
  substitute another digest or bundle: the wrapper's inputs are caller data
  and must not be able to mint their own approval.
- Missing bundle, unavailable hash, digest mismatch, and extraction failure
  are finite `BLOCKED` outcomes with exit code 2, emitted before any install
  effect. A mismatched bundle is never extracted.
- The wrapper extracts only `install.ps1` from the digest-verified bundle
  and delegates. It reimplements no install logic; every existing
  `install.ps1` boundary (inside-repository refusal, `py -3.11` probe,
  dependency-plan display, `INSTALL` confirmation) stays authoritative.
- The file is ASCII-only with CRLF line endings (batch parser and cp950
  console robustness), enforced by `.gitattributes` and pinned by test.
- The wrapper is a release asset only. It is not part of the bundle payload;
  the payload whitelist in `windows_package_manifest.py` is unchanged.
- No admin, PATH, global-tool, or target-project effect.

## Authorized implementation scope

```text
johnny-install.cmd
.gitattributes
tests/test_one_click_installer.py
README.md                                      # user-facing install section
modules/tickets/live-install-binding/README.md # registry row + evidence
```

## Acceptance closure

| ID | Required evidence |
| --- | --- |
| `R1` | The wrapper pins exactly one approved digest (test carries the second entry of the double-entry pin), names exactly `johnny-ai-skill-0.4.1.zip`, and is ASCII-only with CRLF-only line endings. |
| `R2` | Missing bundle → `BUNDLE_NOT_FOUND`, exit 2, and no `install.ps1` appears beside the wrapper. |
| `R3` | A present bundle with any other digest → `DIGEST_MISMATCH`, exit 2, blocked before extraction (no `install.ps1` appears). |
| `R4` | Real-artifact chain smoke: with the released zip beside it, the wrapper verifies the digest, extracts `install.ps1`, and reaches the `INSTALL` prompt; a non-interactive run ends `USER_DECLINED` exit 2, proving the human gate is preserved rather than bypassed. |
| `R5` | `mypy --strict` clean on the new test file; full suite green; a clean-clone bundle build still returns `BUNDLED` (payload content rules unchanged by the new root file). |

## Known risk from the control-plane feasibility probe (2026-08-19)

A quick probe of the obvious extraction command failed: with the digest
check already passed, `tar -xf <bundle> -C <folder> install.ps1` (Windows
bsdtar) returned nonzero against the real release zip, so a naive wrapper
reaches `EXTRACT_FAILED` instead of the `INSTALL` prompt. Root cause was
not diagnosed. The implementer must pick and prove a working single-member
extraction (candidates: PowerShell `Expand-Archive` to a staging folder, or
`System.IO.Compression.ZipFile` single-entry extract exactly as
`install.ps1` itself does for the bootstrap) — R4 exists precisely to force
this chain to be proven against the real artifact.

## Environment facts the implementer needs

- Python is `py -3.11` (no `python`, no `pwsh`; Windows PowerShell 5.1).
- Console codepage is cp950: keep the wrapper ASCII-only and decode
  subprocess output as bytes/UTF-8 in tests, never `text=True`.
- The approved release digest is frozen by the published v0.4.1 release
  asset: `f67047f4780a63c08383fd3fce4af85d5dfb5cb9bbd857f8b99d6c4a8b90b464`.
- Working copies are CRLF; batch files must stay CRLF (enforce via
  `.gitattributes` and pin by test).
