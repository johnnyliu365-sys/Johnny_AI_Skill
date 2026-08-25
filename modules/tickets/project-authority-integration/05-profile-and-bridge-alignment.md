# Ticket 05 — profile and bridge alignment

| Field | Value |
| --- | --- |
| Ticket ID | PAI-05-PROFILE-AND-BRIDGE-ALIGNMENT |
| State | READY_LOW_MODEL / EVIDENCE_CORRECTION_REQUIRED |
| Acceptance Closure Set | ACS-PAI-05-REVISION-01 |
| Dependencies | PAI-01 through PAI-04 accepted |
| Source specification | Project authority integration SPEC Revision 11, ticket order item 05 and its existing exact `BridgeCapability` contract |
| Planning baseline | main at 83f0fc8c82e636803f1fa77082885391abd4c813; the implementation-admission baseline is the clean current integration main recorded by the reviewer at dispatch. |
| Delivery / model | POC test-only evidence correction; Luna/xhigh implementation owner and Terra/xhigh supervisor-reviewer. Reviewer capability is not lower than implementer capability. |
| Writable-source status | Test-only: add an exact finite-members assertion to the existing PAI-01 contract test. |
| Effect boundary | Local test-only evidence correction; no runner, queue, receipt issuer, polling, wake probe, remote, provider, payload, release, or host effect. |

## Vertical closure reserved

Preserve separate maturity, assurance, and topology axes; require profile-scaled meaningful
counter-mutations; and align same-lifetime reviewer wait, review, and guarded integration with
the bridge-free rule. Cross-lifetime capability remains exactly NOT_REQUIRED, AVAILABLE, or
UNAVAILABLE; UNAVAILABLE means owner-mediated artifact relay and never a fabricated wake.

The PAI-08 reviewer independently removed `NOT_REQUIRED` from the real production enum and the
previous focused test stayed green. This is an `EVIDENCE_DEFECT`, not new behavior: PAI-01 already
integrated the three-state production type, but its test did not pin the exact member set. This
correction may not turn cross-lifetime supervision into a synchronous precondition or authorize
any effect.

## Exact writable boundary

The implementation may modify only:

```johnny-boundary
modify = tests/test_project_authority_contracts.py
forbid = library/local_orchestration/project_authority/
forbid = modules/
forbid = doc/
forbid = skills/
```

No production type, public export, payload, governance wording, plugin version, release tag,
remote, provider, runner, queue, receipt, descriptor, or host capability is in scope.

## Acceptance and TDD matrix

| Cell | Required observable assertion |
| --- | --- |
| PAI-05-T01 | `set(BridgeCapability)` is exactly `{NOT_REQUIRED, AVAILABLE, UNAVAILABLE}`; each ordinary enum round trip returns its matching member, and an unknown value remains rejected. |
| PAI-05-T02 | In a disposable reviewer or implementer overlay, removing the actual production `NOT_REQUIRED` member makes PAI-05-T01 red. Byte-for-byte restoration returns green. |
| PAI-05-T03 | The actual contract-test source continues to parse and execute through the public package import; the assertion is not a fixture or duplicated enum. |

The implementation owner records the first red, green, and restore-backed mutation. The Terra
reviewer must independently repeat the real production-member removal through a disposable
worktree and observe PAI-05-T01 red; a zero-red result remains an evidence defect.

## Verification commands and return

```powershell
python -m pytest -q -p no:cacheprovider tests/test_project_authority_contracts.py
python -m mypy --strict tests/test_project_authority_contracts.py
git diff --check <implementation-admission-baseline> HEAD
```

`ImplementationReturn.COMPLETED` carries the runtime-bound baseline, exact changed-path evidence,
first-red/green/restore evidence, and no commit. The reviewer alone writes a candidate commit
after approval and submits it through `admit_document_mutation`. The profile/governance prose
alignment remains deferred to PAI-07; this correction cannot alter skills, payload, or plugin
version.
