# 04A — Payload Manifest Contract

| Field | Value |
| --- | --- |
| SPEC / AC | Local installer SPEC / AC-01, AC-03, AC-04, AC-08, AC-12 |
| State | `PLANNED / DEPENDENCY_WAIT / NOT_DISPATCHED` |
| Closure | `CLOSURE-LOCAL-INSTALL-T04A-01` / manifest TDD closure below |
| Dependency | All runtime/host package prerequisites are resolved, approved and integrated |
| Implementation language | Python 3.11 with strict Pydantic models and `mypy --strict` |
| Owner / reviewer | Codex / current `main` worktree |
| Implementation owner | `UNALLOCATED`; exact dispatch is still required |
| Proposed source / test | `library/local_orchestration/windows_package_manifest.py`; `tests/test_windows_package_manifest.py` |
| XSS | `XSS_NOT_APPLICABLE` — no renderer or JavaScript context |

## Sole outcome

Create a pure strongly typed contract that converts an exact approved payload
set into canonical owned-relative-path manifest entries and one digest identity.
It performs no filesystem, compiler, build, install or remove effect.

## TDD closure

- Positive exact payload set yields deterministic ordered entries and manifest
  digest using named immutable DTO/value types.
- Reject `None`, omitted/empty/whitespace, absolute/traversal/URI,
  prefix-confusable, non-canonical separator/casing, duplicate destination,
  empty or malformed digest, foreign root and unapproved payload.
- Caller package name/path cannot grant ownership; dynamic mapping, `Any`, open
  callable and custom equality/hash/repr/serialization do not cross the boundary.
- Failure has finite stable status and distinct internal reason without raw
  path/Context/Secret leakage.
- Reverse relative-path admission, duplicate-destination and digest binding to
  named red tests, then restore exact blobs.

Completion requires first red, focused/full green, strict type/compile/source/
scope/residue evidence, implementation commit, WPR-only handoff and independent
review. It authorizes only later 04B selection.
