# L11 — One-click refusal console-stream observability

| Field | Value |
| --- | --- |
| SPEC / AC | `environment-capability-bootstrap` `EC-09`; L9 `R3`, `R4`, `R5` |
| Requirement | Existing L9 refusal messages must remain observable from the complete Windows console stream even when PowerShell module discovery is unavailable. |
| State | `CONVERGENCE_REVIEW_REQUIRED / NOT_DISPATCHED / REVISION_04` |
| Baseline | `32bbf8d8122c3449de0dfabe9572d4d377c3b12d` |
| Delivery / model | `POC / STANDARD`; Luna / xhigh implementation, Terra / xhigh review. |
| Language / XSS | Python 3.11 strict test code / `XSS_NOT_APPLICABLE` |
| Worktree / branch | `.worktrees/live-install-binding-l11` / `implement/live-install-binding-l11-console-stream` |

## Problem

The original Revision 01 assumed that the refusal text existed but was only read from the wrong
stream. On this host's actual inherited PowerShell module path, the complete console observation
instead showed that `Get-FileHash` was unavailable before the wrapper could produce either
`DIGEST_MISMATCH` or reach the delegated `USER_DECLINED` gate. This violates L9's already-approved
R3/R4 behavior, so the test-only boundary was a `TICKET_DEFECT`. The product requirement has not
changed: the wrapper must calculate the SHA-256 and return its named refusal independently of
PowerShell module auto-loading; the tests must observe both visible console streams.

## Revision 02 convergence replan — module-independent digest and observation

One Luna/xhigh correction may change only `johnny-install.cmd` and
`tests/test_one_click_installer.py`. The wrapper must replace the module-dependent
`Get-FileHash` calculation with a built-in .NET SHA-256 file calculation that produces the same
lowercase 64-hex comparison value. It must retain the existing approved digest, bundle filename,
exit codes, staging/extraction/delegation flow, ASCII-only CRLF format and `pause` behavior. An
unreadable or unhashable bundle must still be a finite pre-extraction `BLOCKED` path; it must not
be mistaken for a matching digest or proceed to extraction.

The tests must make the module-discovery condition reproducible in a disposable subprocess
environment, prove that a tampered bundle returns named `DIGEST_MISMATCH` with exit 2 and no
extraction, and combine decoded stdout plus stderr when asserting user-visible messages. They
must retain the synthetic matching-bundle proof that reaches named `USER_DECLINED`. No live
bundle, package, release, installation, remote, tag or user configuration is in scope.

## Revision 03 convergence replan — stream-placement neutrality

Revision 02's module-independent .NET digest correction satisfies the real R3 contract: with
module discovery suppressed, a tampered bundle returns `DIGEST_MISMATCH`, exits 2 and remains
unextracted. Unlike the old failed command, the corrected wrapper's `Write-Output` is observed on
stdout on this host. The previous O5 requirement that stdout alone be insufficient therefore
contradicted the corrected implementation. Stream placement is not a release contract; observing
both streams is. This is a `TICKET_DEFECT` in the test evidence only, not a new product behavior
or an authorization change.

One Luna/xhigh additive correction may modify `tests/test_one_click_installer.py` only: remove
the stdout-negative placement assertion while retaining named-code assertions against the complete
decoded observation and the disposable suppressed-module fixture. The current uncommitted wrapper
and test changes are evidence only; rebase them onto this revision before the one permitted test
correction. A fresh Terra/xhigh review must independently run the suppressed-module tamper case,
assert the named refusal in the complete observation, and confirm that neither stream was
discarded. No generator, package, release or installation effect is authorized.

## Revision 04 convergence replan — refusal guidance and release dependency

The Revision 03 review found the corrected wrapper's finite
`DIGEST_UNREADABLE` refusal correctly before extraction, but the exhaustive refusal-guidance
audit rejected it because no registry entry exists. Classifying every newly emitted refusal is an
existing governance invariant, so the former L11 boundary was incomplete. This is a
`TICKET_DEFECT`, not permission to omit the refusal or to treat unreadable data as a digest match.

One Luna/xhigh correction may modify only `library/local_orchestration/refusal_guidance.py` and
`tests/test_refusal_guidance.py` in addition to the existing Revision 03 wrapper/test changes.
It must add exactly one `johnny-install.cmd` / `DIGEST_UNREADABLE` entry, classify it
`OWNER_MUST_DECIDE`, and give transport-safe next steps that preserve the immutable approved
digest and do not offer a bypass. The targeted test must bind that exact surface/code/category;
the exhaustive audit must return complete after the candidate wrapper is present. No other
guidance, installer behavior or release pin may change.

Revision 03's exact locked full-suite run is evidence, not a green claim: it contained the one
L11 guidance failure above and the separately known, unintegrated Ticket 08 publication
pin/tree failures. The latter cannot be repaired, waived or attributed to L11. L11 review must
make its own focused/refusal-guidance partition green and record the full-suite classification.
After L11 integration, Ticket 08 must rebase and run its own AC-9 full-suite gate before any
publication or installation. This resolves the ordering dependency without lowering either
ticket's release control.

## Boundary declaration

```johnny-boundary
modify = tests/test_one_click_installer.py
modify = johnny-install.cmd
modify = library/local_orchestration/refusal_guidance.py
modify = tests/test_refusal_guidance.py
forbid = install.ps1
forbid = requirements-dev.txt
forbid = requirements-runtime.lock
forbid = README.md
forbid = .gitattributes
forbid = library/NLP/
forbid = library/功能集群/
forbid = library/金流串接/
forbid = library/catalog/
forbid = library/workflow_router/
forbid = modules/spec/
forbid = doc/
```

## Acceptance closure

| ID | Required proof |
| --- | --- |
| O1 | With PowerShell module discovery suppressed in a disposable subprocess environment, the tampered-bundle test preserves `exit 2` and no-extraction assertions, and observes named `DIGEST_MISMATCH` in an explicitly decoded combined stdout/stderr console transcript. |
| O2 | The synthetic matching-bundle test preserves `exit 2` and no-stray-extraction assertions, and observes named `USER_DECLINED` in the same complete console observation. |
| O3 | The wrapper has no `Get-FileHash` dependency; it computes an exact lowercase SHA-256 through .NET, retains ASCII-only CRLF output, and its finite hash failure cannot proceed to extraction. The test helper does not discard either stream, use codepage-sensitive `text=True`, or accept an empty/pause-only transcript. |
| O4 | The focused L9/L10, runtime-lock and refusal-guidance tests pass under the exact `pytest==9.1.1` declared in `requirements-dev.txt`; strict mypy, compile and diff checks are green. A locked full-suite run is retained in full: it may not contain an L11 failure, while any still-unintegrated Ticket 08 publication failures remain explicitly assigned to Ticket 08 and block its release gate. |
| O5 | Terra independently runs the suppressed-module tamper fixture and proves the named refusal in the complete observation while retaining both captured streams. The test must not make stdout-versus-stderr placement a contract. |

## Implementation and review constraints

Before debugging read `modules/tickets/PITFALL-REGISTER.md`, especially D4, D5 and E platform
facts. Use the existing disposable verification venv only; implementation must not install,
upgrade or reconfigure host packages. The Revision 01 uncommitted test diff is evidence only and
must be rebased onto this ticket revision before work continues. No source commit by the
implementer. The reviewer writes the candidate commit only after a clean Luna handoff, repeats
the named console-stream reverse check, and may integrate only if O1--O5 are green. This ticket
has no remote, provider, release, runner, marketplace, cache or user-install effect.
