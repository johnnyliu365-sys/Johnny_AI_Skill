# 04B — Inno Installer Build Source

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC / AC-01 through AC-12 |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T04B-01` / build-source TDD closure below |
| Dependency | 04A independently approved and guarded-integrated |
| Implementation language | Inno Setup 6.7.3 plus Python 3.11 with strict Pydantic models and `mypy --strict` at the build boundary |
| Owner / reviewer | Codex / current `main` worktree |
| Implementation owner | `UNALLOCATED`; exact dispatch is still required |
| Proposed source / test | `installer/JohnnyAIWorkflow.iss`; `installer/build_package.py`; `tests/test_windows_installer_source.py` |
| XSS | `XSS_NOT_APPLICABLE`; Browser/WebView/HTML/DOM/JavaScript UI is requirement change |

## Sole outcome

Implement bounded user-scope Inno/build source consuming the integrated 04A
manifest. Verification may compile to disposable output that is deleted after
evidence. No version-one artifact is accepted, installed or published.

## TDD closure

- Positive canonical inputs render/compile one user-scope setup/uninstaller
  source graph with composition-only UI and no target-project/live-host effect.
- Reject manifest/source drift, unsupported payload, toolchain/version/signature
  mismatch, admin/system/arbitrary root, unsafe destination, embedded Secret/raw
  Context/target path and ownership inferred by name.
- Inject compiler absent/nonzero/exception, manifest read failure and unexpected
  output; retain finite stable block and distinct internal reason.
- Reverse manifest consumption, user-scope and compiler identity to named red
  tests, then restore exact blobs.

Completion requires red/green/reversal, strict typing/source compilation,
disposable compile smoke, exact scope/residue, implementation commit, WPR-only
handoff and independent review. Only guarded integration permits 04C.
