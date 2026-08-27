# Code Review — Per-stream ownership-ledger readiness

| Field | Value |
| --- | --- |
| Feature | `context-load-telemetry` |
| Ticket / closure | `11-per-stream-ownership-ledger-readiness` / `CLOSURE-CONTEXT-TELEMETRY-11-PER-STREAM-OWNERSHIP-LEDGER-READINESS` revision 01 |
| Source baseline / final candidate | `b8a5dfdc7f482812451e336f6293510eedaa75ad` / `e05f03adf8751f635df8fba6eb204a3922727ec4` |
| Reviewer | `ticket-review` semantic profile — Terra/xhigh, root session |
| Conclusion | `APPROVED / INTEGRATED` |

## Admission and scope

The effective Ticket 11, Specification Revision 08, Context Revision 08,
`PRD-20260827-041`, `CHG-20260827-041`, and ADRs `025`–`026` were independently read from
committed sources. Candidate `e05f03a` descends from the Ticket 11 authority and modifies exactly:

- `library/local_orchestration/telemetry_storage/ownership_ledger.py`;
- `tests/test_telemetry_ownership_ledger.py`.

The already-committed Ticket 11 element index was not changed. The candidate changes no public
contract/export, lock adapter, legacy JSONL codec, composition root, stream/journal operation or
Ticket 06 artifact. It converts the private aggregate ledger into one entry document per exact
four-coordinate identity and adds recovery-only `resolve_current`; it neither provisions nor
repairs entries. XSS, provider, host, target-project, network, publication, release and deployment
effects are not applicable.

## Evidence

| Check | Result |
| --- | --- |
| LRA1–LRA7 | `7 passed, 3 subtests passed` |
| Existing strict storage-contract guard | `21 passed` |
| Strong typing / compilation / diff | `mypy --strict`, `compileall`, and `git diff --check` passed |
| Per-stream representation | The domain-separated SHA-256 includes all four immutable coordinates; distinct streams write distinct entry documents. |
| Normal versus recovery admission | Normal lookup/CAS retains exact revision and closed-lifecycle checks. `resolve_current` reads the exact current immutable entry without trusting candidate revision and has no mutation path. |
| Legacy and containment | Aggregate ledger, malformed/extra-field entry, stored-coordinate mismatch, redirected root/ancestor and failed replacement return sanitized `BOUNDARY_REJECTED` without migration or path disclosure. Native symlink creation is unavailable to this Windows session; the test's documented containment signal fallback was exercised, so no unobserved real-symlink qualification is claimed. |
| Cross-process preservation | Two spawned independent processes CAS distinct seeded identities and retain both requested post-states; no aggregate document is created. |
| Implementer mutations | LRM1–LRM4 each made its named focused proof red and were restored before return. |
| Independent reviewer mutation | The reviewer changed the real `_identity_matches` production choke point to accept every stored entry. LRA5 then failed exactly because malformed stored coordinates returned `FOUND` instead of `BOUNDARY_REJECTED`; byte-exact restoration returned all focused cells green. |
| Integration gate | `admit_document_mutation` returned `INTEGRATED` with `integrated_commit=e05f03adf8751f635df8fba6eb204a3922727ec4`, exactly equal to the reviewed candidate SHA. |

## Full-suite baseline qualification

The full suite on the exact candidate completed in 577.86 seconds with `1822 passed`,
`31 skipped`, and `3783 subtests passed`. Three controls failed:

1. `test_plugin_publication.py::CandidateMetadataTests::test_l5_stale_candidate_pin_is_named_before_generation` — stale live plugin-publication pin.
2. `test_refusal_guidance.py::ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered` — stale pre-existing refusal-guidance roster.
3. `test_runtime_dependency_lock.py::RunningPytestVersionMatchesDeclarationTests::test_running_pytest_version_matches_the_declared_version` — running pytest `9.0.3` differs from declared `9.1.1`.

The three exact cells reran and failed unchanged against clean main without Ticket 11 source.
They are visible baseline/environment defects and do not establish a Ticket 11 regression; the
repository cannot be claimed globally green.

## Conclusion and follow-up

No blocking implementation, evidence, ticket, security or requirement finding remains. The source
candidate is integrated. The next ticket may compose this corrected private ledger with the
delivered lock port, a durable transaction journal and the strict legacy-codec boundary for the
five storage operations. It must add restart/phase interruption, TOCTOU and release-failure
evidence; it may not create a public provision surface, silently migrate the aggregate ledger or
weaken Ticket 11's exact-identity guard.
