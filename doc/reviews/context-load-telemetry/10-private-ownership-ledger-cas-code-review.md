# Code Review — Private ownership-ledger CAS substrate

| Field | Value |
| --- | --- |
| Feature | `context-load-telemetry` |
| Ticket / closure | `10-private-ownership-ledger-cas` / `CLOSURE-CONTEXT-TELEMETRY-10-OWNERSHIP-LEDGER-CAS` revision 01 |
| Source baseline / final candidate | `23f4ae1ff68df48a7e02368690cc86236b3abe1d` / `a06c0fd5d2dc78e8b77eb671d9a304b74a0202a6` |
| Reviewer | `ticket-review` semantic profile — Terra/xhigh, root session |
| Conclusion | `APPROVED / INTEGRATED / AUTHORITY_PUSH_CONFIRMED` |

## Admission and scope

The effective Ticket 10, Specification Revision 07, Context Revision 07,
`PRD-20260827-041`, `CHG-20260827-041`, and ADRs `022` through `025` were read from committed
sources. Candidate `a06c0fd` descends from the ticket authority and adds exactly:

- `library/local_orchestration/telemetry_storage/ownership_ledger.py`;
- `tests/test_telemetry_ownership_ledger.py`.

The pre-existing Ticket 10 element index was not modified. The candidate leaves the public
contracts, package re-export, local lock adapter, legacy JSONL codec, public composition and
Ticket 06 worktree untouched. Its only runtime seam is a private lookup/CAS ledger below an
injected Johnny telemetry root; fixture provisioning is test-local and not production API. XSS,
provider, host, target-project, network, publication, release and deployment effects are not
applicable to this closure.

## Evidence

| Check | Result |
| --- | --- |
| OLA1–OLA7 | `7 passed, 5 subtests passed` |
| Existing strict storage-contract guard | `21 passed` |
| Strong typing / compilation / diff | `mypy --strict`, `compileall`, and `git diff --check` passed |
| Pre-provisioning | Missing, cross-identity and stale lookup inputs return finite no-effect results; no source path can create/register an entry. |
| CAS | Exact current revision advances one lifecycle/revision pair; stale repeat is `CONFLICT` with byte-identical post-state. |
| Ownership and containment | Malformed/traversal locator, malformed ledger, redirected-root signal and failed replacement return sanitized `BOUNDARY_REJECTED` without path disclosure. |
| Implementer mutations | OLM1–OLM4 each made its named focused proof red and were restored before return. |
| Independent reviewer mutation | On the `LocalTelemetryOwnershipLedger -> resolves_within_root` choke point, simulated rejection of the derived ledger check yielded `BOUNDARY_REJECTED`; changing that gate to accept yielded `FOUND` for the same seeded entry. The property is pinned. Native symbolic-link creation is unavailable on this Windows host (`WinError 1314`), so no new real-symlink runtime qualification is claimed. |
| Worktree hygiene | First review found ignored `.mypy_cache`; the same implementation owner removed it without source edits. Final worktree had no root/nested `.mypy_cache`, no `.pytest_cache`, and no untracked path other than the two candidate files before reviewer commit. |
| Integration gate | `admit_document_mutation` returned `INTEGRATED` with `integrated_commit=a06c0fd5d2dc78e8b77eb671d9a304b74a0202a6`, exactly equal to the reviewed candidate SHA. |

## Full-suite baseline qualification

The full suite on the exact source subsequently committed as the candidate completed in 578.43 seconds with `1822 passed`,
`31 skipped`, and `3784 subtests passed`. Three controls failed:

1. `test_plugin_publication.py::CandidateMetadataTests::test_l5_stale_candidate_pin_is_named_before_generation` — stale live plugin-publication pin.
2. `test_refusal_guidance.py::ClassificationAuditTests::test_every_failure_enum_in_the_library_is_covered_or_uncovered` — stale pre-existing refusal-guidance roster.
3. `test_runtime_dependency_lock.py::RunningPytestVersionMatchesDeclarationTests::test_running_pytest_version_matches_the_declared_version` — running pytest `9.0.3` differs from declared `9.1.1`.

The same three exact cells reran and failed unchanged against clean main without Ticket 10 source.
The candidate adds a `LedgerResolutionDecision`, not a `*Failure` enum, and direct audit readback
showed its covered/uncovered enum sets equal to main's. These are visible baseline/environment
defects and do not establish a Ticket 10 regression; the repository cannot be claimed globally
green.

## Conclusion and follow-up

No blocking implementation, evidence, ticket, security or requirement finding remains. The next
closure must compose this private ledger with the delivered lock port, durable transaction journal
and strict legacy-codec boundary for all five storage operations. It must add independent-process,
TOCTOU and restart-recovery evidence; it may not reopen Ticket 06 or weaken Ticket 10's
pre-provisioning/CAS invariants.

The docs-only closure record `9c2dddacad2e0f9d29d3006845f36492557a8057` was non-force pushed
to `origin/main`; direct remote SHA readback matched it exactly. This proves the closure docs are
authority-integrated. The implementation candidate remains the distinct ancestor
`a06c0fd5d2dc78e8b77eb671d9a304b74a0202a6` recorded above.
