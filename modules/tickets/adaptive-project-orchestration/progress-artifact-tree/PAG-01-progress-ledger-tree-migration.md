# PAG-01 — Progress ledger artifact-tree migration and integrity proof

## Admission

| Field | Value |
| --- | --- |
| Ticket ID | `PAG-01-progress-ledger-tree-migration` |
| State | `PLANNED / READY_LOW_MODEL / NON_DISPATCHED` |
| Closure set | `PAG-01-CS-01` |
| Authority | `PRD-20260815-022` / `CHG-20260815-022`; [`REQ-20260815-022`](../../../../doc/requirements/active/2026/adaptive-orchestration/REQ-20260815-022.md); [`adaptive-project-orchestration.md`](../../../spec/adaptive-project-orchestration.md) Revision 05 AC-17; [`DEC-20260816-519`](DEC-20260816-519.md) |
| Baseline | `471608b2abd361eeb16c29dc8728f85d173d8f57` |
| Context | sealed `CONTEXT.md`; no Context revision or append is authorised by this ticket |
| Logical implementation owner | one `IMPLEMENTATION_OWNER`, `gpt-5.6-luna`, high reasoning; task/worktree/branch/receipt are `UNBOUND` until a later Router admission |
| Reviewer | receipt-bound `SUPERVISOR_REVIEWER`, unbound until dispatch |
| Environment / resource plan | local Python 3.11; one implementation lane; no helper, network, provider, install, host, target-project, or external resource capability |
| Dependency | none; `PAG-02` depends on this ticket being `COMPLETE / APPROVED / INTEGRATED` |
| XSS / UI | `N/A`: Markdown is parsed as repository data only; no Browser, WebView, DOM renderer, JavaScript context, UI, or privileged bridge is introduced |

## One observable closure

Given the legacy flat `doc/WorkProgressReport.md` at this ticket's admitted baseline, one local
migration produces a compatibility root index plus the complete deterministic date tree
`doc/progress/<year>/<month>/<day>/<PRG-ID>.md`. Every unique legacy PRG record is represented
once by an immutable exact leaf that preserves its source record bytes, and the typed validator
accepts the resulting tree only when its source-to-leaf proof and all index invariants hold.

This is one data/effect boundary: the repository filesystem inside the exact paths below. No
runtime dependency or product behavior is introduced.

## Exact writable scope and ownership

The implementation may create or modify only these paths in its single migration integration
commit:

```text
doc/WorkProgressReport.md
doc/progress/<year>/README.md
doc/progress/<year>/<month>/README.md
doc/progress/<year>/<month>/<day>/README.md
doc/progress/<year>/<month>/<day>/PRG-YYYYMMDD-NNN.md
library/workflow_router/progress_artifact_tree.py
library/workflow_router/__init__.py                 # only if the typed public contract must export
tools/migrate_work_progress_report.py
tests/test_progress_artifact_tree.py
tests/fixtures/progress_artifact_tree/**
```

`doc/WorkProgressReport.md` becomes the compatibility `ROOT_INDEX`; it may contain its title
and direct-year metadata table only. It must not retain any `PRG-...` event body, descendant
inventory, ticket/spec prose, chat, or migration narrative. The `doc/progress` directory is a
path container, not a second root index. Each `README.md` may contain only direct-child rows with
exactly `ID`, `Kind`, `Revision`, `Digest`, `Lifecycle`, and `Exact reference` columns.

The legacy parser owns conversion from one flat report to `LegacyProgressRecord`; the pure domain
and validator own identity, byte-preservation, digest, direct-edge and lookup invariants; the
command composition root owns input/output paths and atomic staged replacement. No domain type
may perform filesystem I/O. The command must not inspect unrelated repository files.

## Frozen contract and errors

Use named, immutable Python types with complete parameter/return types and no `Any`, implicit
dynamic values, casts, `model_construct`, `type: ignore`, or unvalidated strings beyond the input
boundary:

| Contract | Required meaning |
| --- | --- |
| `ProgressRecordId` | exact `PRG-YYYYMMDD-NNN`, with year/month/day derived only from its ID |
| `LegacyProgressRecord` | non-empty raw record bytes, exact heading, ID, source ordinal, and derived date; no nullable field |
| `ProgressLeafRef` | one relative leaf reference under the bounded `doc/progress` date tree; no absolute path or traversal segment |
| `ProgressIndexEntry` | direct child ID/kind/revision/digest/lifecycle/exact reference only |
| `ProgressMigrationPlan` / `ProgressMigrationResult` | source IDs and digest, planned leaf refs, resulting IDs and digest; set equality proves completeness and uniqueness |
| `ProgressTreeValidationResult` | `VALID` or one finite failure reason, never a partial-success result |

The finite failure reasons are `MALFORMED_HEADING`, `IDENTITY_COLLISION`, `SOURCE_LEAF_MISMATCH`,
`DUPLICATE_PRG`, `ORPHAN_PRG`, `DIGEST_MISMATCH`, `REFERENCE_INVALID`,
`INDEX_BODY_FORBIDDEN`, `ROOT_BODY_FORBIDDEN`, and `INDEX_SHAPE_INVALID`. Any one failure
prevents replacement of the legacy root and produces no partial migration commit.

Each historical leaf is the original record span, including its `## PRG-...` heading and original
body, byte-for-byte. Index metadata uses `legacy-ledger-r01` and `FROZEN_HISTORICAL`; this is
provenance metadata only and must not reclassify a historical event. A new event writer writes one
new exact leaf and updates only its direct day/month/year/root indexes; it never appends event
content to `doc/WorkProgressReport.md`.

## TDD and strong-type preflight

| Cell | First-red command and expected failure | Green acceptance |
| --- | --- | --- |
| `PAG-01-T01` source completeness | `python -m unittest tests.test_progress_artifact_tree.ProgressMigrationTests.test_every_legacy_record_has_one_byte_identical_leaf` fails because the module/contract is absent | all source IDs equal leaf IDs, every raw record span is byte-identical, and no leaf is duplicated |
| `PAG-01-T02` root and direct indexes | `python -m unittest tests.test_progress_artifact_tree.ProgressIndexTests.test_root_and_indexes_reject_event_bodies_and_descendant_rows` fails before validation exists | root/year/month/day indexes contain only direct metadata; malformed body or descendant row fails closed |
| `PAG-01-T03` order-independent exact lookup | `python -m unittest tests.test_progress_artifact_tree.ProgressLookupTests.test_lookup_is_independent_of_index_row_order` fails before the resolver exists | shuffled valid direct rows resolve the same one exact leaf without sibling discovery |
| `PAG-01-T04` malformed/collision boundary | `python -m unittest tests.test_progress_artifact_tree.ProgressFailureTests.test_malformed_heading_and_identity_collision_leave_no_migration_output` fails before the parser/transaction exists | malformed heading, duplicate ID, collision, orphan, stale digest and bad reference each fail closed and leave the legacy input untouched |
| `PAG-01-T05` new-event fixture | `python -m unittest tests.test_progress_artifact_tree.ProgressFixtureTests.test_new_event_fixture_writes_leaf_and_direct_indexes_not_root_body` fails before the writer exists | checked fixture proves one new PRG leaf plus direct indexes and proves no root event-body append |
| `PAG-01-T06` type/source gate | `python -m unittest tests.test_progress_artifact_tree.ProgressSourceGateTests.test_progress_tree_source_is_strict_typed_and_effect_bounded` fails before the module exists | source gate rejects dynamic/bypass forms; one bounded reverse mutation for each explicit gate turns red and restoration returns green |

Before the first green claim, construct and round-trip every public success DTO/value/enum through
ordinary validation, then reverse-mutate the ID pattern, relative-reference allowlist, digest
comparison, body-exclusion guard, and duplicate-ID guard. The command uses staged output and
validates the complete staged tree before replacing the compatibility root/tree paths.

## Verification and completion evidence

```powershell
python -m unittest tests.test_progress_artifact_tree
python -m unittest discover -s tests
python -m mypy --strict library tests tools/migrate_work_progress_report.py
Get-ChildItem -LiteralPath 'library/workflow_router' -Filter '*.py' -File | ForEach-Object { python -m py_compile $_.FullName }
python -m tools.migrate_work_progress_report --verify-tree --root doc/WorkProgressReport.md --progress-root doc/progress
git diff --check
git status --short
```

The primary smoke path is a disposable checked fixture: migrate a copied flat fixture, validate
it, look up one leaf after a permutation of legal index rows, and assert that the root has no PRG
body. Evidence names source/result counts and digests, exact focused/full/type/compile output,
and no-cache readback.

Completion is one reviewed migration integration commit containing only this ticket's source,
tests, fixture, compatibility root, and generated progress tree. The sole rollback is to revert
that integration commit; do not reset, amend, delete Git history, or delete historical evidence.
The next progress handoff is a newly allocated exact progress leaf, never a separate
`WorkProgressReport.md` append commit.

## Typed return

Return `ImplementationReturn.COMPLETED` only with the integration commit, exact generated root
and leaf tree references, proof counts/digests, first-red and verification evidence. Return
`BLOCKED` for an unreadable/malformed legacy source or an identity collision, and
`CHANGE_DETECTED` only if an approved source changes during execution. Neither return grants
review, merge, release, dispatch, or any external effect.
