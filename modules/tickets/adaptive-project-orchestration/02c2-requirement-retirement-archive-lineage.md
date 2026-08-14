# R02C2 — Requirement Retirement and Archive Lineage Gate

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` revision 05 / AC-17 |
| PRD / change | `PRD-20260815-022` / `CHG-20260815-022` |
| Context / environment | `doc/context/adaptive-project-orchestration/main.md` at `SPEC_REVISION_05_APPROVED / ROUTER_PHASE_ACTIVE`; local pure-Python verification in the named permanent implementation worktree; no target, host or external environment effect |
| State | `IN_PROGRESS / RECEIPT_BOUND` |
| Closure | `CLOSURE-ADAPTIVE-ROUTER-R02C2-01` / ACX1-ACX8 / ticket revision `r02c2-01` |
| Dependency / baseline | R02C1 guarded integration `5b887c726a91053190050abf7f0267b48503cb5e`; proposal `efef364c4072947f32f5ee9f0d5932187ae811d0`; exact dispatch registry is the commit containing `PRG-20260815-489` |
| Implementation language / checker | Python 3.11; `python -m mypy --strict --explicit-package-bases --no-incremental` over every Python file under `library/` and `tests/` |
| Delivery profile / resource plan | `STANDARD`; `PRG-20260815-488`; one `gpt-5.6-luna` max implementation owner; no helper |
| Control owner / reviewer | Control task `019fb935-bbe1-7f71-8b4b-58ba20c81626`; sole Agent orchestrator |
| Implementation owner / lane | Existing task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation`; planned branch `codex/implementation-router-requirement-lineage-r02c2` |
| Dispatch binding | Handoff `hnd-adaptive-router-r02c2-20260815`; allocation `aln-adaptive-router-r02c2-20260815`; receipt `rcpt-adaptive-router-r02c2-20260815`; question `q-adaptive-router-r02c2-20260815`; correlation `corr-adaptive-router-r02c2-20260815`; side Context `scx-adaptive-router-r02c2-20260815-01`; expected return `ret-requirement-lineage-review-handoff-r02c2`; activated only by the exact registry containing `PRG-20260815-489` |
| XSS / effects | `XSS_NOT_APPLICABLE`; pure metadata-only validation, no source/body read, filesystem, Git, Agent, host or network effect |
| Operations / rollback | No runtime operation. Before integration, withhold approval; after guarded integration, use a separately reviewed additive revert. Never reset, force or delete reviewed evidence. |

## One observable outcome

`RequirementLineageGate.validate(...)` validates exactly one caller-supplied lineage branch. An
active `PRD-YYYYMMDD-NNN` and `CHG-YYYYMMDD-NNN` pair is valid only when both active roots resolve
the same ACTIVE leaf. A retired pair is valid only when both former active paths are absent and
one exact ARCHIVED archive-library leaf resolves to an immutable bundle containing the retired
pair and historical metadata.

The gate consumes only typed metadata and delegates exact path resolution to the integrated
`ArtifactTreeResolver`. It does not discover indexes, scan other active/archive branches, load
requirement bodies, move files or perform retirement. R02C3 owns archive/reusable-library
partition selection and bounded catalog behavior.

## Frozen public contracts

Add and publicly export strict named types and models:

```text
RequirementId       = PRD-YYYYMMDD-NNN
RequirementChangeId = CHG-YYYYMMDD-NNN
RequirementArchiveId = ARCH-REQ-YYYYMMDD-NNN

RequirementLifecycle = ACTIVE | ARCHIVED
RequirementLineageDecisionKind = ACTIVE_PAIR_VALID | RETIREMENT_VALID
                               | REQUIREMENT_LINEAGE_INVALID
RequirementLineageInvalidReason = REQUEST_BINDING_MISMATCH
                                | IDENTIFIER_PAIR_MISMATCH
                                | ACTIVE_PATH_INVALID
                                | ACTIVE_LEAF_MISMATCH
                                | RETIRED_PATH_STILL_ACTIVE
                                | ARCHIVE_PATH_INVALID
                                | ARCHIVE_BUNDLE_MISMATCH
                                | REPLACEMENT_PAIR_MISMATCH

RequirementArchiveBundle = {
  archive_id: RequirementArchiveId,
  archive_leaf_ref: OpaqueMetadataId,
  retired_prd_id: RequirementId,
  retired_change_id: RequirementChangeId,
  retired_leaf_ref: OpaqueMetadataId,
  last_active_revision: RevisionDigest,
  retirement_reason_ref: OpaqueMetadataId,
  replacement_prd_id: RequirementId | None,
  replacement_change_id: RequirementChangeId | None,
  historical_source_commit: CommitDigest,
  content_digest: EvidenceDigest
}

RequirementLineageRecord = {
  lineage_ref: OpaqueMetadataId,
  prd_id: RequirementId,
  change_id: RequirementChangeId,
  lifecycle: RequirementLifecycle,
  active_leaf_ref: OpaqueMetadataId | None,
  archive_id: RequirementArchiveId | None,
  archive_leaf_ref: OpaqueMetadataId | None,
  revision: RevisionDigest,
  content_digest: EvidenceDigest
}

RequirementLineageValidationRequest = {
  request_ref: OpaqueMetadataId,
  lineage: RequirementLineageRecord,
  prd_root_ref: OpaqueMetadataId,
  change_root_ref: OpaqueMetadataId,
  prd_active_path: ArtifactTreeResolutionRequest,
  change_active_path: ArtifactTreeResolutionRequest,
  archive_root_ref: OpaqueMetadataId | None,
  archive_path: ArtifactTreeResolutionRequest | None,
  archive_bundle: RequirementArchiveBundle | None
}

RequirementLineageValidationDecision = {
  request_ref: OpaqueMetadataId,
  lineage_ref: OpaqueMetadataId,
  decision: RequirementLineageDecisionKind,
  invalid_reason: RequirementLineageInvalidReason | None,
  resolved_lineage_leaf_ref: OpaqueMetadataId | None
}
```

All models inherit the existing strict/frozen/extra-forbid Router model. ACTIVE records require
exactly `active_leaf_ref` and forbid archive fields. ARCHIVED records require `archive_id` and
`archive_leaf_ref` and forbid `active_leaf_ref`. Archive request/root/bundle fields follow that
same lifecycle shape. Replacement IDs are both present or both absent. Reserved all-zero
revision, content digest and historical commit values fail construction. No contract exposes
title, body, prose, source, prompt, transcript, filesystem path or arbitrary mapping fields.

Decisions are exact: either success kind has one resolved leaf and no reason; invalid has one
reason and no leaf. `ACTIVE_PAIR_VALID` returns the active leaf; `RETIREMENT_VALID` returns the
archive bundle leaf.

## Exact validation order

1. Bind distinct PRD/change roots to their respective path requests. Both active paths use
   family `REQUIREMENT_CHANGE`. ACTIVE expected leaves equal `active_leaf_ref`; ARCHIVED expected
   leaves equal the bundle's `retired_leaf_ref`. An ARCHIVED archive request uses family
   `ARCHIVE_LIBRARY`, its exact archive root and expected bundle leaf. Otherwise
   `REQUEST_BINDING_MISMATCH`.
2. Require PRD and CHG date/sequence suffixes to match. When replacement IDs exist, require their
   suffixes to match. Return `IDENTIFIER_PAIR_MISMATCH` or `REPLACEMENT_PAIR_MISMATCH`.
3. For ACTIVE, both delegated resolutions must be `RESOLVED`, select the same exact leaf and end
   in an ACTIVE leaf. A rejected resolver result is `ACTIVE_PATH_INVALID`; a different or
   non-active leaf is `ACTIVE_LEAF_MISMATCH`. Otherwise return `ACTIVE_PAIR_VALID`.
4. For ARCHIVED, require the bundle archive ID/ref, retired IDs and retired leaf to match the
   lineage and supplied retired pair. The bundle's last-active revision, reason and historical
   commit are required non-reserved evidence fields; they are not inferred from the later
   archive-lineage revision. Otherwise `ARCHIVE_BUNDLE_MISMATCH`.
5. Resolve both former active paths. Any `ARTIFACT_TREE_INVALID` is `ACTIVE_PATH_INVALID`; either
   `RESOLVED` is `RETIRED_PATH_STILL_ACTIVE`; both must be `ARTIFACT_PATH_NOT_FOUND`.
6. Resolve the exact archive path. It must be `RESOLVED`, end at the bundle's exact ARCHIVED leaf,
   match the bundle content digest and carry edge/node metadata equality already enforced by R02C1. Otherwise
   `ARCHIVE_PATH_INVALID`. Then return `RETIREMENT_VALID`.

No unselected sibling needs a supplied node. Historical source commit and retirement reason are
opaque metadata references; their contents are never resolved by this gate.

## Exact source boundary

- `library/workflow_router/contracts.py`
- new `library/workflow_router/requirement_lineage.py`
- `library/workflow_router/__init__.py`
- new `tests/test_workflow_requirement_lineage.py`
- one append-only `doc/WorkProgressReport.md` handoff after implementation

Integrated `artifact_tree.py`, its tests, `router.py` and existing Router tests are read-only
dependencies/regressions. No other path is writable.

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `ACX1` | Every named ID, enum/model and decision constructs and JSON-round-trips through ordinary strict APIs; extra, missing, null, wrong finite, raw body/source/path and reserved-zero metadata fail. Every contradictory lifecycle/request/decision shape fails construction. |
| `ACX2` | Matching active PRD/CHG IDs resolve from distinct active roots to the same exact ACTIVE leaf and return only `ACTIVE_PAIR_VALID`. |
| `ACX3` | Retirement succeeds only when both former active paths are absent and one exact ARCHIVED archive-library bundle leaf resolves with matching retired IDs, leaf and bundle digest plus required non-reserved last-active revision, reason and historical commit metadata. |
| `ACX4` | Mismatched PRD/CHG or replacement suffixes, wrong roots/families/expected leaves, one missing active path, differing/non-active active leaves, stale/invalid path metadata, bundle mismatch and active/archive overlap return their frozen finite reason. |
| `ACX5` | Unselected active/archive siblings need no supplied node and are never traversed. No source/body, callable, optional effect, filesystem, Git, Agent, host or network port exists. |
| `ACX6` | Committed source gates enforce annotations and reject `Any`, `object`, raw `str` domain fields, `type: ignore`, cast, dynamic member lookup, model-construction bypass, broad catches and effect imports introduced by R02C2. No line-count rule exists. |
| `ACX7` | Dedicated, artifact-tree/Router regression, full explicit serial unittest, strict full-tree mypy, in-memory compile, source/scope/diff/topology/porcelain/cache gates pass. |
| `ACX8` | Three bounded reversals turn governing tests red and restore exact bytes: bypass PRD/CHG suffix equality; accept one still-active retired path; accept stale archive edge revision/digest metadata. |

## First red and return

First red imports the absent public lineage contracts and `RequirementLineageGate`, then validates
one active pair. It fails before production mutation because R02C2 does not exist. Preserve that
failure, implement ACX1-ACX8 one behavior at a time and keep integrated R02C1 bytes unchanged.

Return one implementation commit changing exactly the four source/test paths, then one separate
WPR-only handoff containing first red, ACX mapping, three reversal reds/restorations, full
verification identities and final clean readback. Return only `COMPLETED`, `BLOCKED` or
`CHANGE_DETECTED`; progress-only final is not completion.

No helper/subagent, new worktree, self-review/integration, next ticket, R02C3-R06, live model,
Codex/home/App/target-project/network effect, push/staging publication, package/install, Secret,
release or deployment.
