# R02A — Shared Context Lifecycle Authority Gate

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` revision 04 / AC-15 |
| PRD / change | `PRD-20260815-020` / `CHG-20260815-020` |
| State | `IN_PROGRESS / DISPATCH_CONFIRMED` |
| Closure | `CLOSURE-ADAPTIVE-ROUTER-R02A-01` / SC1-SC8 |
| Baseline | Tree/context governance `fa47a878c15f86cc4400a7a2914576c3fde0b9b3` |
| Delivery profile | `STANDARD`; one Luna implementation owner; no helper |
| Control owner / reviewer | Control task `019fb935-bbe1-7f71-8b4b-58ba20c81626`; sole Agent orchestrator |
| Planned implementation owner | Task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` |
| Planned branch | `codex/implementation-router-shared-context-r02a` from the exact dispatch-registry commit |
| Dispatch binding | Handoff `hnd_adaptive_router_r02a_20260815`; allocation `aln_adaptive_router_r02a_20260815`; receipt `rcpt_adaptive_router_r02a_20260815`; question `q-adaptive-router-r02a-20260815`; correlation `corr-adaptive-router-r02a-20260815`; registry `PRG-20260815-460` |
| Agent Context binding | Ticket revision `r02a-01`; receipt `rcpt_adaptive_router_r02a_20260815`; owner/worktree/branch above; exact registry baseline; `scx-adaptive-router-r02a-20260815-01` |
| XSS / effects | `XSS_NOT_APPLICABLE`; pure typed Router/Profile gate and tests, no filesystem, Agent, Git, host or network effect |

## One observable outcome

`RouterEngine.decide_shared_context_access(...)` admits only the exact architecture-owned
shared-Context lifecycle: create/update an unsealed draft during `ARCHITECTURE`/`GRILL`, reopen
a sealed revision only through approved change control, seal the exact draft at `CONTEXT`, and
read the exact sealed revision from later stages. Every other valid request returns one finite
fail-closed decision before any writer/effect can be invoked.

This ticket does not create a filesystem writer, parse document bodies, implement ticket-scoped
Agent Context, traverse artifact trees, validate PRD/CHG archives, route model sleep/wake, admit
low-model tickets, handle UI sources or resume any installer/package lane.

## Frozen public contracts

Add and publicly export these strict finite contracts in `library.workflow_router`:

```text
SharedContextOperation = CREATE_DRAFT | REVISE_DRAFT | SEAL | READ_REFERENCE
SharedContextLifecycle = ABSENT | ARCHITECTURE_DRAFT | SEALED
SharedContextActorRole = ARCHITECTURE_OWNER | SUPERVISOR_REVIEWER
                       | IMPLEMENTATION_OWNER | RESEARCH_HELPER
SharedContextMutationDecision = ALLOW | REQUIRE_CHANGE_CONTROL
                              | FORBID_ROLE_OR_STAGE | STALE_REVISION

SharedContextContentManifest = {
  revision: RevisionDigest,
  content_digest: EvidenceDigest,
  stable_fact_refs: tuple[OpaqueMetadataId, ...],
  invariant_boundary_refs: tuple[OpaqueMetadataId, ...],
  artifact_index_refs: tuple[OpaqueMetadataId, ...]
}

SharedContextState = {
  context_ref: OpaqueMetadataId,
  lifecycle: SharedContextLifecycle,
  revision: RevisionDigest | None,
  content_digest: EvidenceDigest | None
}

SharedContextAccessRequest = {
  request_ref: OpaqueMetadataId,
  context_ref: OpaqueMetadataId,
  operation: SharedContextOperation,
  process_stage: ProcessStage,
  actor_role: SharedContextActorRole,
  actor_capability_ref: OpaqueMetadataId,
  expected_current_revision: RevisionDigest | None,
  candidate_manifest: SharedContextContentManifest | None,
  change_authority_state: AuthorityState,
  approved_change_ref: OpaqueMetadataId | None
}

SharedContextAccessDecision = {
  request_ref: OpaqueMetadataId,
  context_ref: OpaqueMetadataId,
  operation: SharedContextOperation,
  decision: SharedContextMutationDecision,
  resulting_state: SharedContextState
}
```

`SharedContextState` permits null revision/digest only together in `ABSENT`; draft and sealed
states require both and reject all-zero metadata. `SharedContextContentManifest` requires at
least one reference, rejects duplicates across all three tuples and contains no raw body,
progress, ticket, commit, test, review, branch/worktree or policy-prose field. Strict extra-field
rejection is the content-schema gate; there is no line-count test.

`SharedContextAccessRequest` has these exact shape rules:

- `CREATE_DRAFT`: no expected revision, one candidate manifest, `NOT_REQUIRED` change authority
  and no change ref;
- `REVISE_DRAFT`: exact expected revision and one candidate manifest; change fields may be
  supplied only for this operation;
- `SEAL` and `READ_REFERENCE`: exact expected revision, no candidate manifest, `NOT_REQUIRED`
  change authority and no change ref;
- missing, extra, null-in-wrong-state, wrong finite value or malformed metadata fails ordinary
  construction/JSON round-trip; no `model_construct`/copy/update bypass is accepted.

Extend `ProjectWorkflowProfile` with exact `shared_context_ref: OpaqueMetadataId` and
`architecture_owner_capability_ref: OpaqueMetadataId`; `build_router_poc_profile()` sets
`ctx-shared-project` and `cap-architecture-owner`, and advances `profile_version` from `1` to
`2`. These fields are policy metadata, not a host authority grant.

## Exact decision table and precedence

Before operation-specific rules, a request/profile/state `context_ref` mismatch or an
`expected_current_revision` mismatch returns `STALE_REVISION` with the incoming state unchanged.
For write operations, a role other than `ARCHITECTURE_OWNER`, a capability other than the
Profile's exact architecture owner, or a wrong stage returns `FORBID_ROLE_OR_STAGE` unchanged.

| Operation / incoming lifecycle | Exact admission | Result |
| --- | --- | --- |
| `CREATE_DRAFT / ABSENT` | exact writer; stage `ARCHITECTURE` or `GRILL`; valid candidate | `ALLOW`; candidate becomes `ARCHITECTURE_DRAFT` |
| `REVISE_DRAFT / ARCHITECTURE_DRAFT` | exact writer/stage; exact prior; candidate revision differs | `ALLOW`; candidate remains `ARCHITECTURE_DRAFT` |
| `REVISE_DRAFT / SEALED` | exact writer/stage/prior; `APPROVED` authority and non-null change ref; candidate revision differs | `ALLOW`; candidate becomes `ARCHITECTURE_DRAFT` |
| `REVISE_DRAFT / SEALED` without both change proofs | otherwise exact | `REQUIRE_CHANGE_CONTROL`; unchanged |
| `SEAL / ARCHITECTURE_DRAFT` | exact writer at `CONTEXT`; exact prior | `ALLOW`; same revision/digest becomes `SEALED` |
| `READ_REFERENCE / SEALED` | stage `SPEC`, `TICKETS`, `IMPLEMENT`, `SMOKE_TEST`, `REVIEW` or `HANDOFF`; any finite actor role with valid capability ref | `ALLOW`; unchanged |
| Any other lifecycle/operation combination | otherwise exact | `FORBID_ROLE_OR_STAGE`; unchanged |

The gate is pure. It receives already validated metadata and returns a decision; it never reads,
writes or deletes Context, invokes a callable/optional port, scans a worktree or catches broad
exceptions. A caller may perform a later effect only after `ALLOW`; no effect port exists in
this ticket.

## Exact source boundary

- `library/workflow_router/contracts.py`
- `library/workflow_router/profile.py`
- `library/workflow_router/router.py`
- `library/workflow_router/__init__.py`
- `tests/test_workflow_router.py`
- one append-only `doc/WorkProgressReport.md` handoff after implementation

No other production, test, ticket, review or governance path is writable.

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `SC1` | All enums/models above construct and JSON-round-trip through ordinary strict public APIs; the complete operation-dependent missing/extra/null/wrong matrix fails. |
| `SC2` | The default Profile exposes exact shared Context and architecture-owner capability refs and version `2`; missing, equal, locator-like, prompt/Secret-like or conflicting metadata is rejected. |
| `SC3` | Every `ALLOW` row in the table returns the exact deterministic resulting state and copies request/context/operation metadata. |
| `SC4` | Wrong role/capability/stage and every illegal lifecycle transition return `FORBID_ROLE_OR_STAGE` unchanged before any effect surface. |
| `SC5` | Wrong context ref/prior revision and reused candidate revision return `STALE_REVISION`; sealed revision without exact approved change proof returns `REQUIRE_CHANGE_CONTROL`. |
| `SC6` | Manifest tests reject empty/all-zero/duplicate refs and attempted `progress_refs`, `ticket_refs`, `commit_refs`, `test_refs`, `review_refs`, raw text/path/URI/prompt/Secret fields without a line-count rule. Decision serialization remains metadata-only. |
| `SC7` | Existing focused and six-module Router suites, full explicit serial unittest, strict full-tree mypy, in-memory compile, scope/diff/topology/porcelain/cache gates remain green. |
| `SC8` | Two bounded reversals turn exact tests red and are restored byte-for-byte: admit `SUPERVISOR_REVIEWER` for one write; admit sealed `REVISE_DRAFT` without approved change proof. |

## First red, source gates and return

First red imports the four enums and four models from `library.workflow_router` and calls
`RouterEngine.decide_shared_context_access`; it fails before production mutation because the
public contracts/method do not exist. Preserve the exact failure and confirm incoming focused
Router regression `32/32` plus six-module `99/99`.

Committed source gates inspect new class/field/constant annotations and reject `Any`, `object`,
raw `str` domain fields, `type: ignore`, cast, dynamic member lookup, `model_construct`/copy/update,
callable/`None` ports, broad catches and subprocess/Git/filesystem/network imports introduced by
this closure.

Return one implementation commit changing exactly the five production/test paths, then one
separate WPR-only handoff commit containing first red, SC1-SC8, both reversal reds/restorations,
full verification identities and final clean readback. Return status is only `COMPLETED`,
`BLOCKED` or `CHANGE_DETECTED`; progress-only final is not completion.

No helper/subagent, new worktree, self-review/integration, next ticket, 06G0P review/mutation,
live model/Figma/Codex/home/App/target-project/network effect, push/staging publication,
package/install, Secret, release or deployment.
