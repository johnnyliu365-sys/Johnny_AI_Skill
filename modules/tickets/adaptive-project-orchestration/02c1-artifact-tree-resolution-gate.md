# R02C1 — Generic Artifact-tree Resolution Gate

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` revision 05 / AC-17 |
| PRD / change | `PRD-20260815-022` / `CHG-20260815-022` |
| State | `IN_PROGRESS / REVISION_02_REVALIDATION_REQUIRED` |
| Closure | `CLOSURE-ADAPTIVE-ROUTER-R02C1-01` / ACX1-ACX8 / ticket revision `r02c1-02`; supersedes schema-incomplete `r02c1-01` without changing behavior or public contracts |
| Baseline | Change-control refreeze `3139bccc3ab08093519b91cc55e162bd98b6718b`; initial review `c71d06d795a31c1a71189dd718c1a326a2522636`; revision-02 refreeze is the commit containing `PRG-20260815-483` |
| Context / environment | `doc/context/adaptive-project-orchestration/main.md` at `SPEC_REVISION_05_APPROVED / ROUTER_PHASE_ACTIVE`; local pure-Python verification in the named permanent implementation worktree; no target, host or external environment effect |
| Implementation language / checker | Python 3.11; `python -m mypy --strict --explicit-package-bases --no-incremental` over every Python file under `library/` and `tests/` |
| Delivery profile / resource plan | `STANDARD`; `PRG-20260815-479`; one `gpt-5.6-luna` max implementation owner; no helper |
| Control owner / reviewer | Control task `019fb935-bbe1-7f71-8b4b-58ba20c81626`; sole Agent orchestrator |
| Implementation owner | Existing task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` |
| Branch | `codex/implementation-router-artifact-tree-r02c1` from the exact dispatch-registry commit |
| Prior dispatch | Registry `db9bc7d9d9e4b14ddda7082633e71148cdcc3ed2`; candidate implementation `458791b470629fe7c0e3bb263af87560b58e54b9`; handoff `b1ba51ccc13b0893783b5fd5e2b9e99e4d120d84`; prior side Context `scx-adaptive-router-r02c1-20260815-01` is invalidated by this ticket revision |
| Revalidation binding | Handoff `hnd-adaptive-router-r02c1-revalidation-20260815-02`; allocation `aln-adaptive-router-r02c1-20260815`; receipt `rcpt-adaptive-router-r02c1-revalidation-20260815-02`; question `q-adaptive-router-r02c1-revalidation-20260815-02`; correlation `corr-adaptive-router-r02c1-revalidation-20260815-02`; side Context `scx-adaptive-router-r02c1-20260815-02`; expected return `ret-artifact-tree-review-handoff-r02c1-r02`; inactive until the exact registry commit containing `PRG-20260815-484` |
| XSS / effects | `XSS_NOT_APPLICABLE`; pure metadata-only resolver, no source/body read, Agent, filesystem, Git, host or network effect |
| Operations / rollback | No runtime operation. Before integration, discard the candidate by withholding approval; after guarded integration, use a separately reviewed additive revert. Never reset, force or delete reviewed evidence. |

## One observable outcome

`ArtifactTreeResolver.resolve(...)` accepts only a caller-supplied, explicit
`root -> one-or-more partitions -> leaf` metadata path. It returns the expected exact leaf only
when every supplied parent contains one matching direct-child edge whose kind, revision, digest
and lifecycle equal the next supplied node. Invalid topology and a missing requested segment are
distinct finite outcomes.

The resolver receives only the selected branch plus direct-child metadata already present in
those indexes. It never discovers, scans, recursively loads or persists siblings, directories,
documents or leaf bodies. It does not implement active PRD/CHG retirement/archive lineage
(R02C2), archive/reusable-library selection policy (R02C3), model wake, ticket admission, UI
routing, initialization, staging, installer/package or 06G work.

## Frozen public contracts

Add and publicly export the following strict contracts from `library.workflow_router`:

```text
ArtifactTreeFamily = REQUIREMENT_CHANGE | SHARED_CONTEXT | AGENT_CONTEXT
                   | SPECIFICATION | TICKET | REVIEW | PROGRESS_EVIDENCE
                   | ADR_SECURITY | ARCHIVE_LIBRARY | REUSABLE_MODULE
ArtifactTreeNodeKind = ROOT_INDEX | PARTITION_INDEX | LEAF
ArtifactTreeLifecycle = ACTIVE | CLOSED | ARCHIVED
ArtifactTreeDecisionKind = RESOLVED | ARTIFACT_TREE_INVALID | ARTIFACT_PATH_NOT_FOUND
ArtifactTreeInvalidReason = REQUEST_BINDING_MISMATCH | DUPLICATE_NODE
                          | DUPLICATE_CHILD | DUPLICATE_PARENT | CYCLE
                          | DANGLING_PATH_NODE | FAMILY_MISMATCH
                          | KIND_TRANSITION | EDGE_METADATA_MISMATCH
                          | PATH_SEGMENT_MISSING

ArtifactTreeChildRef = {
  child_ref: OpaqueMetadataId,
  child_kind: ArtifactTreeNodeKind,
  child_revision: RevisionDigest,
  child_digest: EvidenceDigest,
  child_lifecycle: ArtifactTreeLifecycle
}

ArtifactTreeNode = {
  node_ref: OpaqueMetadataId,
  family: ArtifactTreeFamily,
  node_kind: ArtifactTreeNodeKind,
  revision: RevisionDigest,
  content_digest: EvidenceDigest,
  lifecycle: ArtifactTreeLifecycle,
  child_refs: tuple[ArtifactTreeChildRef, ...]
}

ArtifactTreeResolutionRequest = {
  request_ref: OpaqueMetadataId,
  family: ArtifactTreeFamily,
  root_ref: OpaqueMetadataId,
  explicit_path_refs: tuple[OpaqueMetadataId, ...],
  expected_leaf_ref: OpaqueMetadataId,
  path_nodes: tuple[ArtifactTreeNode, ...]
}

ArtifactTreeResolutionDecision = {
  request_ref: OpaqueMetadataId,
  family: ArtifactTreeFamily,
  decision: ArtifactTreeDecisionKind,
  invalid_reason: ArtifactTreeInvalidReason | None,
  resolved_leaf_ref: OpaqueMetadataId | None
}
```

All models inherit the existing frozen/strict/extra-forbid Router model. `explicit_path_refs` and
`path_nodes` contain at least root, one partition and leaf. Indexes contain metadata only; no contract exposes
body, text, content, payload, prompt, transcript, source or arbitrary mapping fields. Revisions
and digests reject reserved all-zero values. A leaf has no children. Decision construction is
exact: `RESOLVED` has only a resolved leaf and no reason; both rejection kinds have no resolved
leaf; `ARTIFACT_PATH_NOT_FOUND` uses only `PATH_SEGMENT_MISSING`; every other reason belongs only
to `ARTIFACT_TREE_INVALID`.

## Exact resolution order

The pure resolver applies this precedence without dynamic member lookup:

1. Reject duplicate supplied node IDs as `DUPLICATE_NODE`.
2. Reject a path whose first/last refs do not equal `root_ref`/`expected_leaf_ref`, which supplies
   a node outside the explicit path, or whose supplied nodes do not preserve explicit-path order
   as `REQUEST_BINDING_MISMATCH`. Missing path nodes remain eligible for step 4.
3. Reject repeated explicit path refs or an edge back to an ancestor as `CYCLE`.
4. Reject any explicit path ref without exactly one supplied node as `DANGLING_PATH_NODE`.
5. Require the first node to be `ROOT_INDEX`, every intermediate node `PARTITION_INDEX`, and the
   last node `LEAF`; otherwise return `KIND_TRANSITION`.
6. Require every supplied node to use the request family; otherwise return `FAMILY_MISMATCH`.
7. Across the supplied branch, reject duplicate direct-child IDs as `DUPLICATE_CHILD` and any
   non-root path node referenced by more than one supplied parent as `DUPLICATE_PARENT`.
8. For each adjacent path pair, no matching direct-child edge returns
   `ARTIFACT_PATH_NOT_FOUND / PATH_SEGMENT_MISSING`; more than one is a duplicate child.
9. A matching edge whose kind, revision, digest or lifecycle differs from the next node returns
   `EDGE_METADATA_MISMATCH`.
10. Only after every segment passes, return `RESOLVED` with exactly `expected_leaf_ref`.

Unselected child refs in a supplied index remain opaque metadata and need no supplied node. The
resolver must not follow or validate those sibling targets. R02C1 is lifecycle-neutral beyond
edge/node equality; active/archive reachability rules belong to R02C2/R02C3.

## Exact source boundary

- `library/workflow_router/contracts.py`
- new `library/workflow_router/artifact_tree.py`
- `library/workflow_router/__init__.py`
- new `tests/test_workflow_artifact_tree.py`
- one append-only `doc/WorkProgressReport.md` handoff after implementation

No other production, test, ticket, review or governance path is writable. In particular,
`router.py` and `tests/test_workflow_router.py` are read-only regression inputs, not R02C1 edit
targets.

For revision-02 revalidation, all four production/test paths are read-only. The owner may only
additively synchronize the exact `PRG-20260815-484` registry, resolve the single expected
append-only WPR overlap while retaining each record once and in order, run verification and
append one WPR-only revalidation handoff. Any changed source/test blob is `CHANGE_DETECTED`.

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `ACX1` | Every enum/model constructs and JSON-round-trips through strict public APIs; extra, missing, null, wrong finite, raw body/content/payload and reserved-zero metadata fail. Decision objects reject every contradictory result/reason/leaf shape. |
| `ACX2` | Root-to-one-partition-to-leaf and root-to-multiple-partitions-to-leaf paths resolve only through exact direct-child edges. Each of the ten artifact families has a positive resolution case. |
| `ACX3` | The request supplies only one selected path; unrelated sibling refs require no node/body and are never traversed. The resolver exposes no source, callable, optional-effect, filesystem, Git, Agent, host or network port. |
| `ACX4` | Duplicate node/child/parent, repeated path/cycle, dangling path node, wrong root/intermediate/leaf kind, family mismatch, extra supplied node and cross-root alias each fail with the frozen reason. |
| `ACX5` | Missing direct path segment returns only `ARTIFACT_PATH_NOT_FOUND`; stale edge kind/revision/digest/lifecycle returns `ARTIFACT_TREE_INVALID / EDGE_METADATA_MISMATCH`; neither exposes a leaf. |
| `ACX6` | Committed source gates enforce explicit annotations and reject `Any`, `object`, raw `str` domain fields, `type: ignore`, cast, dynamic member lookup, model-construction bypass, broad catches and effect imports introduced by R02C1. No line-count rule exists. |
| `ACX7` | Dedicated focused tests, incoming Router tests, six-module Router regression, full explicit serial unittest, strict full-tree mypy, in-memory compile, source/scope/diff/topology/porcelain/cache gates pass. |
| `ACX8` | Three bounded reversals turn their governing tests red and restore exact bytes: ignore edge revision/digest equality; remove duplicate-parent rejection; resolve a missing direct segment. |

## First red and revision-02 return

First red imports the absent contracts and `ArtifactTreeResolver` from the public package and
calls `resolve`; it must fail before production mutation because the R02C1 surface does not
exist. Preserve the failure and record the incoming focused Router/six-module/full/type/compile
baselines without changing their existing tests.

The immutable candidate first red failed before production mutation because the R02C1 public
surface did not exist. Candidate implementation `458791b470629fe7c0e3bb263af87560b58e54b9`
and its three reversal records remain the implementation evidence; revision 02 does not ask the
owner to recreate or rewrite them.

Return one WPR-only revalidation handoff after proving the candidate's four source/test blobs are
unchanged, ACX1-ACX8 still pass, the revised ticket/Context/language/checker bindings were read,
and focused/Router/six-module/full/mypy/compile/source/scope/topology/residue gates pass. Return
only `COMPLETED`, `BLOCKED` or `CHANGE_DETECTED`; progress-only final is not completion.

No helper/subagent, new worktree, self-review/integration, next ticket, R02C2-R06, 06G0P,
live model/Figma/Codex/home/App/target-project/network effect, push/staging publication,
package/install, Secret, release or deployment.
