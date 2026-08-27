# Code Review — Lock-bound telemetry transaction adapter

| Field | Value |
| --- | --- |
| Feature | `context-load-telemetry` |
| Ticket / closure | `12-lock-bound-transaction-adapter` / `CLOSURE-CONTEXT-TELEMETRY-12-LOCK-BOUND-TRANSACTION-ADAPTER` revision 02 |
| Source baseline / final candidate | `4d747f6253c6d2741af980f3b9ff82c68df8fedb` / `c359d92efc6eb2ca4aeb5c613f4fe7c976cd6e74` |
| Reviewer | `ticket-review` semantic profile — Terra/xhigh, root session |
| Conclusion | `APPROVED / INTEGRATED / AUTHORITY_PUSH_CONFIRMED` |

## Admission and scope

The committed Ticket 12, Specification Revision 09, Context Revision 09,
`PRD-20260827-041`, `CHG-20260827-041`, and ADRs `022`, `025`–`027` were read as the
review authority. Candidate `c359d92` descends from the ticket authority and changes exactly:

- `library/local_orchestration/telemetry_storage/johnny_owned_adapter.py`;
- `tests/test_johnny_owned_telemetry_storage_adapter.py`.

The pre-existing Ticket 12 element index was not changed. No public contract/export, ledger,
lock adapter, legacy codec, composition root, target project, Git, provider, host, network,
publication, release or deployment path was changed. The candidate is the direct private
`TelemetryStoragePort` implementation only; it is not bound into composition.

## Evidence

| Check | Result |
| --- | --- |
| TTA1–TTA7 | `9 passed, 7 subtests passed` |
| Existing storage guards | `36 passed, 7 subtests passed` across ownership-ledger, lock-adapter and storage-contract suites |
| Strong typing / compilation / whitespace | `mypy --strict`, `compileall`, and no-index `git diff --check` passed |
| Exact operation path | Every request performs preliminary exact ownership admission, acquires the exact lock, recovers with `resolve_current`, re-admits exact identity/revision/lifecycle under lock, then reaches the codec only on success. |
| Transaction protocol | Journal/snapshots are under the exact four-coordinate SHA-256 directory; snapshots and journal use derived, containment-checked paths plus same-directory atomic writes. The accepted pre/post recovery grid is closed; malformed or incompatible state retains the journal and becomes finite boundary failure. |
| Controlled codec and responses | The adapter alone uses the legacy reader in this private boundary and never calls `append`; it writes canonical JSONL itself. All five normal response constructors are the existing finite DTOs, and no public response/failure ref contains a filesystem path or exception detail. |
| Contention, TOCTOU and release | A real independent holder returns `LOCK_CONTENDED` with zero stream/journal effect; a final under-lock ledger change is rejected before codec effect; release failure overrides otherwise successful response. |
| Implementer mutations | TTM1–TTM5 were reported red then restored before return. |
| Independent reviewer mutation | The reviewer changed the real `STREAM_APPLIED` recovery guard from `ledger_pre` to `ledger_post`. In TTA4's forced `AFTER_LEDGER_CAS` restart, expected two-record post-state became one-record pre-state; exact restoration returned the focused cell green. |
| Integration gate | `admit_document_mutation` returned `INTEGRATED` with `integrated_commit=c359d92efc6eb2ca4aeb5c613f4fe7c976cd6e74`, exactly equal to the reviewed candidate SHA. The non-force source push was directly read back from `origin/main` at that same SHA. |

## Full-suite baseline qualification

The full suite on exact candidate `c359d92` completed in 580.78 seconds with `1831 passed`,
`31 skipped`, and `3791 subtests passed`. It reported three failures:

1. `test_plugin_publication.py::CandidateMetadataTests::test_l5_stale_candidate_pin_is_named_before_generation` — stale live plugin-publication pin.
2. `test_refusal_guidance.py::ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered` — stale pre-existing refusal-guidance roster.
3. `test_runtime_dependency_lock.py::RunningPytestVersionMatchesDeclarationTests::test_running_pytest_version_matches_the_declared_version` — running pytest `9.0.3` differs from declared `9.1.1`.

The same three exact tests reran with complete traceback on clean `main` at
`4d747f6253c6d2741af980f3b9ff82c68df8fedb`, without Ticket 12 source. They are baseline or
environment defects rather than a Ticket 12 regression; this repository is not claimed globally
green.

## Conclusion

No blocking source, evidence, scope, type, security or requirement finding remains. The reviewed
private adapter is integrated at `c359d92efc6eb2ca4aeb5c613f4fe7c976cd6e74`. Any subsequent
composition work must be a separately authorized ticket and may not widen the closed public
storage contract or treat this private adapter as provisioned by default.

The closure/review documentation commit
`88a742dc88199c8b52faaf18ac73c21ee119c711` was non-force pushed to `origin/main`; fresh direct
remote SHA readback matched it exactly. This proves the review and closure evidence are
authority-integrated. The reviewed source candidate remains the distinct ancestor
`c359d92efc6eb2ca4aeb5c613f4fe7c976cd6e74` recorded above.
