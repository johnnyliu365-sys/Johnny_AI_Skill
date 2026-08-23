# L11 — One-click refusal console-stream observability

| Field | Value |
| --- | --- |
| SPEC / AC | `environment-capability-bootstrap` `EC-09`; L9 `R3`, `R4`, `R5` |
| Requirement | Existing L9 refusal messages must be observed from the same Windows console stream that a user sees; no product behavior changes. |
| State | `READY / NOT_DISPATCHED / REVISION_01` |
| Baseline | `32bbf8d8122c3449de0dfabe9572d4d377c3b12d` |
| Delivery / model | `POC / STANDARD`; Luna / xhigh implementation, Terra / xhigh review. |
| Language / XSS | Python 3.11 strict test code / `XSS_NOT_APPLICABLE` |
| Worktree / branch | `.worktrees/live-install-binding-l11` / `implement/live-install-binding-l11-console-stream` |

## Problem

On Windows, the wrapper invokes `powershell.exe` as a non-zero child for a refusal. The child
prints the named refusal (`DIGEST_MISMATCH` or `USER_DECLINED`), but `cmd.exe` can surface that
text through stderr while `pause` alone is captured through stdout. L9's tests currently inspect
only stdout, so they report a false regression even though they did not observe the complete
user-visible console stream. This ticket changes no wrapper output, digest, bundle, release,
installer, runtime or live-install behavior.

## Boundary declaration

```johnny-boundary
modify = tests/test_one_click_installer.py
forbid = johnny-install.cmd
forbid = install.ps1
forbid = requirements-dev.txt
forbid = requirements-runtime.lock
forbid = README.md
forbid = .gitattributes
forbid = library/
forbid = modules/spec/
forbid = doc/
```

## Acceptance closure

| ID | Required proof |
| --- | --- |
| O1 | The tampered-bundle test preserves its `exit 2` and no-extraction assertions, and finds `DIGEST_MISMATCH` in an explicitly named, decoded combined console observation built from both captured stdout and stderr. |
| O2 | The synthetic matching-bundle test preserves its `exit 2` and no-stray-extraction assertions, and finds `USER_DECLINED` in that same combined console observation. |
| O3 | The helper or local test logic does not silently discard either stream, does not use platform/codepage-sensitive `text=True`, and does not weaken an assertion to accept an empty or pause-only transcript. |
| O4 | The focused L9/L10 and runtime-lock tests pass under the exact `pytest==9.1.1` declared in `requirements-dev.txt`; strict mypy, compile, JSON/diff checks and the whole suite are green in that environment. |
| O5 | Terra independently proves one negative: observing stdout alone is insufficient for the tampered fixture on this host, while the completed console observation contains the named refusal; restoration remains green. |

## Implementation and review constraints

Before debugging read `modules/tickets/PITFALL-REGISTER.md`, especially D4, D5 and E platform
facts. Use the existing disposable verification venv only; implementation must not install,
upgrade or reconfigure host packages. No source commit by the implementer. The reviewer writes
the candidate commit only after a clean Luna handoff, repeats the named console-stream reverse
check, and may integrate only if O1--O5 are green. This ticket has no remote, provider, release,
runner, marketplace, cache or user-install effect.
