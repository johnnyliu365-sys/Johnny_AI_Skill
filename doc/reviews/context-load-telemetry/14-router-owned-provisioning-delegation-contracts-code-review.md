# Ticket 14 — Router-owned telemetry-provisioning delegation contracts: code review

| Field | Value |
| --- | --- |
| Conclusion | `APPROVED / INTEGRATED / AUTHORITY_PUSH_CONFIRMED` |
| Ticket / closure | `TICKET-CONTEXT-TELEMETRY-14-ROUTER-PROVISIONING-DELEGATION-CONTRACTS` / revision `02` |
| Authority | Specification Revision 11 / AC-22; `PRD-20260827-041` / `CHG-20260827-041`; Context Revision 11; `ADR-20260827-029` |
| Baseline / candidate | `ba01836183513b4f8c4b3a2e0bf88707bee4f5c6` / `9364fc89428df1a448d2ac60e4867bfe0d63e55e` |
| Candidate branch | `implement/context-load-telemetry-14-router-owned-provisioning-delegation-contracts` |
| Reviewer / implementation profiles | `ticket-review` — Terra/xhigh / `implementation-standard` — Luna/xhigh |
| Scope | `library/workflow_router/telemetry_provisioning_contracts.py`; `tests/test_telemetry_provisioning_contracts.py` |

## Admission and boundary

The candidate descends from the exact ticket authority and had only the two permitted source/test
paths. `git diff --check` was clean before review and after restoration. The committed ticket,
Revision 11 SPEC/Context/ADR references, `POC / STANDARD` profile, `READY_LOW_MODEL` decision,
Python strict type policy and `XSS_NOT_APPLICABLE` classification were independently read.

This was a same-lifetime reviewer-owned lane: no runner, queue, receipt, descriptor, gateway or
host workspace readback was asserted or required. The implementation owner had no commit, push,
document or orchestration effect; the reviewer committed the reviewed candidate.

## Closure evidence

| Closure item | Independent evidence |
| --- | --- |
| TPA1 | Exact approved registry/commit tuple returns the closed `AUTHORIZED` shape. A different `request_ref` retains its own correlation field but produces the same grant digest, proving the grant binds only the validated dispatch identity. |
| TPA2 | Each independent project/ticket/handoff/owner/ticket-commit/handoff-commit mismatch returns only `AUTHORITY_MISMATCH`, request reference and opaque denial fingerprint. |
| TPA3 | Strict Pydantic construction and JSON round trips reject malformed IDs/commits, `None`, raw root/locator fields, extras and contradictory outcome discriminants. |
| TPA4 | AST/source review verifies the one typed entry point, existing `resolve_approved_dispatch_artifact` choke point, domain-separated SHA-256 references, private module placement, no package-root export, and no storage/root/path/filesystem/host/provider/process/network/Router-engine/dynamic/bypass forms. |
| TPA5 | Target-owned element index resolves the exact ticket/source/test/registry/ADR and explicitly excludes bootstrap and durable provision. Focused test, Router regression, strict type, compilation and diff checks pass. |

Commands rerun by the reviewer:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_telemetry_provisioning_contracts.py
# 5 passed, 11 subtests passed

py -3.11 -m pytest -q -p no:cacheprovider tests/test_workflow_router.py
# 57 passed, 216 subtests passed

py -3.11 -m mypy --strict library/workflow_router/telemetry_provisioning_contracts.py tests/test_telemetry_provisioning_contracts.py
# Success: no issues found in 2 source files

py -3.11 -m compileall -q library/workflow_router/telemetry_provisioning_contracts.py
git diff --check ba01836183513b4f8c4b3a2e0bf88707bee4f5c6
```

## Correction and reviewer counter-mutation

The initial review found that the grant digest included caller-controlled `request_ref`. This
violated the ticket's six-coordinate authority binding, so `CHANGES_REQUESTED` returned to the
same branch and owner. The additive correction separates authority material from denial/correlation
material and proves distinct request references produce one authority reference.

For an independent test-truthfulness check, the reviewer reintroduced `request_ref` into the
production `_dispatch_material` function. `TPA1` turned red with the mismatched
`provisioning_authority_ref`; exact restoration returned all focused cells green. This entered by
the real grant-digest path, not the implementer's reported registry-bypass, omitted-document or
forbidden-source mutations.

## Full regression and residual risk

Candidate full suite:

```text
1841 passed, 31 skipped, 3805 subtests passed in 571.73s
```

The three failures were reproduced on clean `main` with the same interpreter and are therefore
not attributed to Ticket 14:

1. `test_l5_stale_candidate_pin_is_named_before_generation` — stale live plugin-publication pin.
2. `test_every_failure_enum_in_the_library_is_covered_or_uncovered` — refusal-guidance roster drift.
3. `test_running_pytest_version_matches_the_declared_version` — running `pytest 9.0.3` versus
   `requirements-dev.txt` declaration `9.1.1`.

No global-green claim is made. The reviewed closure introduces no root bootstrap, ledger/lock/
stream/journal/report write, storage reference/locator, public package export, Router route,
provider/host/network/target effect, runner/queue/receipt mechanism, publication, release or
deployment capability.

## Integration evidence

`admit_document_mutation` returned `INTEGRATED` with exact commit
`9364fc89428df1a448d2ac60e4867bfe0d63e55e`. The reviewer non-force pushed `main` and direct
`git ls-remote origin refs/heads/main` readback returned that same SHA. This review artifact is a
separate documents-only closure and must itself be authority-pushed before it is final evidence.
