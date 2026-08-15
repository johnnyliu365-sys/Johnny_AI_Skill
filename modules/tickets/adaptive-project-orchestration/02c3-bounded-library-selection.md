# R02C3 — Bounded Archive and Reusable-library Selection Gate

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` revision 05 / AC-17 |
| PRD / change | `PRD-20260815-022` / `CHG-20260815-022` |
| Context / environment | `doc/context/adaptive-project-orchestration/main.md` at `SPEC_REVISION_05_APPROVED / ROUTER_PHASE_ACTIVE`; local pure-Python verification only; no target, host or external environment effect |
| State / closure | `APPROVED / GUARDED_INTEGRATION_AUTHORIZED`; `CLOSURE-ADAPTIVE-ROUTER-R02C3-01`, ACX1-ACX7, revision `r02c3-01` |
| Dependency / baseline | R02C2/R02C2A guarded integration `701df3e448e316d3edf7bdc115e66693e3f54c61`; this ticket receives authority only from its separate exact dispatch registry |
| Implementation language / checker | Python 3.11; `python -B -m mypy --strict --explicit-package-bases --no-incremental library tests` |
| Delivery profile / resource plan | `STANDARD`; one `gpt-5.6-luna` max implementation owner; no helper |
| Control / implementation owner | Reviewer task `019fb935-bbe1-7f71-8b4b-58ba20c81626`; planned implementation task `019ffb0c-db88-7303-895c-aecfadde7c8d` in its existing permanent worktree only |
| Lane | `codex/implementation-router-library-selection-r02c3` from dispatch registry `PRG-20260815-498`; no new worktree |
| Dispatch binding | Handoff `hnd-adaptive-router-r02c3-20260815`; allocation `aln-adaptive-router-r02c3-20260815`; receipt `rcpt-adaptive-router-r02c3-20260815`; question `q-adaptive-router-r02c3-20260815`; correlation `corr-adaptive-router-r02c3-20260815`; side Context `scx-adaptive-router-r02c3-20260815-01`; expected return `ret-library-selection-review-handoff-r02c3`; activated only by the exact registry containing `PRG-20260815-498` |
| XSS / effects | `XSS_NOT_APPLICABLE`; metadata-only pure validation, no Browser/WebView/HTML/DOM/JavaScript context, body/source read, filesystem, Git, Agent, host or network effect |
| Operations / rollback | No runtime operation. Before guarded integration, withhold approval; after it, a separately reviewed additive revert only. Never reset, force or delete reviewed evidence. |

## One observable outcome

`LibrarySelectionGate.validate(...)` validates exactly one caller-supplied metadata path of
exactly three nodes: `root index -> partition index -> leaf`. The selection is either an
archive leaf or a reusable-module card leaf. It delegates the supplied path to the integrated
`ArtifactTreeResolver`; it never discovers an index, loads a sibling, flattens a tree, reads an
artifact body, or follows another branch.

`ARCHIVE` selects only `ArtifactTreeFamily.ARCHIVE_LIBRARY` with an `ARCHIVED` leaf.
`REUSABLE_MODULE` selects only `ArtifactTreeFamily.REUSABLE_MODULE` with an `ACTIVE` leaf.

## Frozen public contracts

Add and publicly export strict named types and models:

```text
LibrarySelectionKind = ARCHIVE | REUSABLE_MODULE
LibrarySelectionDecisionKind = SELECTED | LIBRARY_SELECTION_INVALID
LibrarySelectionInvalidReason = REQUEST_BINDING_MISMATCH | FAMILY_MISMATCH | PATH_INVALID
                              | LEAF_LIFECYCLE_MISMATCH | LEAF_METADATA_MISMATCH

LibrarySelectionRecord = {
  selection_ref: OpaqueMetadataId,
  kind: LibrarySelectionKind,
  root_ref: OpaqueMetadataId,
  partition_ref: OpaqueMetadataId,
  leaf_ref: OpaqueMetadataId,
  leaf_lifecycle: ArtifactTreeLifecycle,
  leaf_digest: EvidenceDigest
}

LibrarySelectionRequest = {
  request_ref: OpaqueMetadataId,
  selection: LibrarySelectionRecord,
  path: ArtifactTreeResolutionRequest
}

LibrarySelectionDecision = {
  request_ref: OpaqueMetadataId,
  selection_ref: OpaqueMetadataId,
  decision: LibrarySelectionDecisionKind,
  invalid_reason: LibrarySelectionInvalidReason | None,
  selected_leaf_ref: OpaqueMetadataId | None
}
```

All models inherit the existing strict, frozen, extra-forbid `RouterModel`. A record rejects
reserved all-zero `leaf_digest`; a request rejects a non-exact three-ref/three-node path. A
decision is exact: `SELECTED` has one selected leaf and no reason; invalid has one finite reason
and no leaf. No contract exposes title, body, prose, source, prompt, transcript, filesystem path,
arbitrary mapping, callable or effect port.

## Exact validation order

1. Require `path.root_ref`, `path.expected_leaf_ref`, `path.explicit_path_refs` and
   `path.path_nodes` to bind exactly to the record's root, partition and leaf references, in that
   order, and to have exactly three nodes. Otherwise return `REQUEST_BINDING_MISMATCH`.
2. Map the record kind to its only permitted family and leaf lifecycle. A wrong path family is
   `FAMILY_MISMATCH`; a record lifecycle or resolved leaf lifecycle outside that mapping is
   `LEAF_LIFECYCLE_MISMATCH`.
3. Delegate exactly that supplied path to `ArtifactTreeResolver`. Any non-`RESOLVED` result is
   `PATH_INVALID`.
4. Require the resolved leaf ref, leaf node ref, leaf node lifecycle and leaf node digest to equal
   the record. Otherwise return `LEAF_METADATA_MISMATCH`; otherwise return `SELECTED`.

The gate receives no sibling node or library content. A caller may select a second branch only by
making a separate request; it is outside this operation.

## Exact source boundary

- `library/workflow_router/contracts.py`
- new `library/workflow_router/library_selection.py`
- `library/workflow_router/__init__.py`
- new `tests/test_workflow_library_selection.py`
- one append-only `doc/WorkProgressReport.md` handoff after implementation

Integrated R02C1/R02C2 source and tests are read-only dependencies/regressions. No other path is
writable.

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `ACX1` | Every named enum/model/decision constructs and JSON-round-trips through ordinary strict APIs; extra, missing, null, wrong finite value, raw body/source/path, reserved-zero digest and every contradictory request/decision shape fail construction. |
| `ACX2` | One exact archive root/partition/ARCHIVED leaf path resolves to only `SELECTED`; one exact reusable-module root/partition/ACTIVE card path resolves to only `SELECTED`. |
| `ACX3` | Wrong root, partition, expected leaf, path length/order, family, kind, lifecycle, digest, leaf node ref, invalid resolver topology or missing path produce only their frozen finite invalid result. |
| `ACX4` | The test supplies only the selected three-node branch. Omitted sibling indexes/cards/archives are never traversed; no discovery, recursive loading, flattening or body read exists. |
| `ACX5` | No source/body, callable, optional effect, filesystem, Git, Agent, host or network port exists. |
| `ACX6` | A committed bounded source gate covers only this ticket's public declarations/module/import boundary and rejects `Any`, `object`, raw `str` domain fields, `type: ignore`, cast, dynamic member lookup, model-construction bypass, broad catches and effect imports. It proves three in-memory reversals: bypass kind/family binding; accept an ARCHIVED reusable leaf; accept an unselected sibling. No line-count rule exists. |
| `ACX7` | First red, focused library-selection plus artifact-tree/Router regression, explicit serial full unittest, strict full-tree mypy, in-memory compile, source/scope/diff/ancestry/topology/porcelain/cache gates all pass. |

## First red and return

First red imports the absent public contracts and `LibrarySelectionGate`, then validates one exact
archive selection. It must fail before production mutation because R02C3 does not exist. Preserve
that failure, implement ACX1-ACX7 one behavior at a time and keep integrated R02C1/R02C2 bytes
unchanged.

Return one implementation commit changing exactly the four source/test paths, then one separate
WPR-only handoff containing first red, ACX mapping, three reversal reds/restorations, full
verification identities and final clean readback. Return only `COMPLETED`, `BLOCKED` or
`CHANGE_DETECTED`; progress-only final is not completion.

No helper/subagent, new worktree, self-review/integration, next ticket, R03-R06, live model,
Codex/home/App/target-project/network effect, push/staging publication, package/install, Secret,
release or deployment is authorized.
