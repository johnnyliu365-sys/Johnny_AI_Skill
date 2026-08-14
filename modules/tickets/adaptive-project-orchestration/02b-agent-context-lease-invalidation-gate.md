# R02B — Ticket-scoped Agent Context Lease Gate

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` revision 04 / AC-16 |
| PRD / change | `PRD-20260815-021` / `CHG-20260815-021` |
| State | `COMPLETE / APPROVED / INTEGRATED` |
| Closure | `CLOSURE-ADAPTIVE-ROUTER-R02B-01` / ACX1-ACX8 |
| Baseline | Proposal `ec41373ba29f363c95d4083a7549053c0588d661`; exact dispatch registry is the commit containing `PRG-20260815-471` |
| Delivery profile | `STANDARD`; one Luna implementation owner; no helper |
| Control owner / reviewer | Control task `019fb935-bbe1-7f71-8b4b-58ba20c81626`; sole Agent orchestrator |
| Planned implementation owner | Task `019ffb0c-c9c7-7b30-b614-02dea7ed9042`; permanent worktree `C:\Users\<user>\Desktop\AI控制工作workflow-implementation` |
| Branch | `codex/implementation-router-agent-context-r02b` from the exact dispatch-registry commit |
| Dispatch binding | Handoff `hnd-adaptive-router-r02b-20260815`; allocation `aln-adaptive-router-r02b-20260815`; receipt `rcpt-adaptive-router-r02b-20260815`; question `q-adaptive-router-r02b-20260815`; correlation `corr-adaptive-router-r02b-20260815`; side Context `scx-adaptive-router-r02b-20260815-01`; expected return `ret-agent-context-review-handoff-r02b` |
| XSS / effects | `XSS_NOT_APPLICABLE`; pure metadata-only gate, no source read, Agent, filesystem, Git, host or network effect |

## One observable outcome

`RouterEngine.decide_agent_context_transition(...)` admits only five finite operations for one
implementation owner's single-ticket Context lease: open, exact resume, same-ticket correction
rebind, different-ticket switch, and close. It invalidates or closes the prior metadata view
before returning a replacement and rejects every stale or mismatched binding before any source
or Agent effect can exist.

This ticket does not resolve artifact-tree paths, load source leaves, validate PRD/CHG/archive or
library indexes, create an Agent packet, invoke an Agent, select a model, implement R02C-R06, or
resume installer/package/06G0P work.

## Frozen public contracts

Add and publicly export these strict contracts in `library.workflow_router`:

```text
AgentContextKind = IMPLEMENTATION_TICKET
AgentContextActorRole = IMPLEMENTATION_OWNER
AgentContextLifecycle = ACTIVE | CLOSED | INVALIDATED
AgentContextOperation = OPEN | RESUME | REBIND_CORRECTION | SWITCH_TICKET | CLOSE
AgentContextUpstreamState = CURRENT | MISSING | REQUIREMENT_CHANGED
AgentContextDecisionKind = ALLOW | AGENT_CONTEXT_BINDING_MISMATCH
                         | AGENT_CONTEXT_STALE | UPSTREAM_DECISION_REQUIRED
                         | REQUIREMENT_CHANGED

AgentContextLease = {
  lease_ref: OpaqueMetadataId,
  project_id: ProjectId,
  context_kind: AgentContextKind,
  lifecycle: AgentContextLifecycle,
  actor_role: AgentContextActorRole,
  actor_capability_ref: OpaqueMetadataId,
  artifact_path_refs: tuple[OpaqueMetadataId, ...],
  ticket_ref: OpaqueMetadataId,
  ticket_revision: RevisionDigest,
  receipt_ref: OpaqueMetadataId,
  owner_ref: OpaqueMetadataId,
  worktree_ref: WorktreeFingerprint,
  branch_ref: BranchFingerprint,
  baseline_revision: RevisionDigest,
  control_baseline_ref: ReviewedCommitReference,
  side_context_id: OpaqueMetadataId,
  expected_return_ref: OpaqueMetadataId,
  invalidation_refs: tuple[OpaqueMetadataId, ...]
}

AgentContextTransitionRequest = {
  request_ref: OpaqueMetadataId,
  operation: AgentContextOperation,
  upstream_state: AgentContextUpstreamState,
  expected_current_lease_ref: OpaqueMetadataId | None,
  expected_current_side_context_id: OpaqueMetadataId | None,
  candidate_lease: AgentContextLease | None
}

AgentContextTransitionDecision = {
  request_ref: OpaqueMetadataId,
  operation: AgentContextOperation,
  decision: AgentContextDecisionKind,
  prior_lease_result: AgentContextLease | None,
  active_lease: AgentContextLease | None
}
```

`AgentContextLease` is metadata only. Artifact refs are opaque exact-leaf identifiers; R02B does
not traverse them. The tuple is non-empty and duplicate-free. Revisions reject reserved all-zero
values. Actor capability equals the exact owner ref. An active candidate cannot invalidate its
own side-context ID. Closed/invalidated objects remain immutable audit metadata and cannot be
submitted as candidates.

Request shape is exact: `OPEN` has neither expected-current field and has one active candidate;
`RESUME`, `REBIND_CORRECTION`, and `SWITCH_TICKET` have both expected-current fields and one
active candidate; `CLOSE` has both expected-current fields and no candidate. Extra fields,
malformed finite values, partial expected binding, or wrong null shape fail construction and JSON
round-trip. No validation uses `model_construct`, copy/update bypass, dynamic lookup or raw
untyped mapping.

## Exact transition table and precedence

`upstream_state=MISSING` returns `UPSTREAM_DECISION_REQUIRED` without an active replacement.
`REQUIREMENT_CHANGED` returns `REQUIREMENT_CHANGED`, invalidates an active prior lease and
returns no active replacement. These outcomes precede operation admission and cannot preserve a
usable packet.

For `CURRENT`, a closed/invalidated current lease returns `AGENT_CONTEXT_STALE`; a non-open
operation without a current lease is also stale. Expected lease/side-context mismatch returns
`AGENT_CONTEXT_BINDING_MISMATCH`. Then apply this table:

| Operation | Exact admission | Result |
| --- | --- | --- |
| `OPEN` | no current lease; active candidate with empty invalidation refs | `ALLOW`; candidate is active |
| `RESUME` | active current; candidate byte-equivalent as a typed value | `ALLOW`; current remains active |
| `REBIND_CORRECTION` | same project/kind/role/capability/ticket/ticket revision/receipt/owner/worktree/branch/expected return; fresh lease, side-context, baseline, control baseline and artifact refs; invalidation refs exactly contain the prior side-context | `ALLOW`; prior becomes `INVALIDATED`, candidate active |
| `SWITCH_TICKET` | same project/kind/role/capability/owner/worktree; different ticket, receipt and branch; fresh lease/side-context/baselines/expected return; invalidation refs exactly contain the prior side-context | `ALLOW`; prior becomes `CLOSED`, candidate active |
| `CLOSE` | exact active current and expected binding | `ALLOW`; prior becomes `CLOSED`, no active lease |

Any deviation from an otherwise current row returns `AGENT_CONTEXT_BINDING_MISMATCH` with the
incoming lease unchanged and no active replacement. A changed ticket revision is never a
same-ticket correction. A different ticket is admitted only by `SWITCH_TICKET`; it never resumes
or reuses the prior side-context ID.

The method is pure and receives only validated models plus `current_lease:
AgentContextLease | None`. It has no source, callable, optional effect, Agent, filesystem, Git,
host or network port and does not catch broad exceptions.

## Exact source boundary

- `library/workflow_router/contracts.py`
- `library/workflow_router/router.py`
- `library/workflow_router/__init__.py`
- `tests/test_workflow_router.py`
- one append-only `doc/WorkProgressReport.md` handoff after implementation

No other production, test, ticket, review or governance path is writable.

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `ACX1` | Every enum/model constructs and JSON-round-trips through strict public APIs; the complete operation-specific missing/extra/null/wrong matrix fails. |
| `ACX2` | All five admitted rows return the exact lifecycle/result pair; a ticket switch closes the prior view and creates fresh ticket/receipt/branch/lease/side-context identities. |
| `ACX3` | Ticket ID, ticket revision, receipt, owner, worktree, branch, baseline, control baseline, lease and side-context mismatches are independently rejected before effect. |
| `ACX4` | Same-ticket correction preserves only the frozen stable binding, requires fresh correction/review metadata and invalidates the prior side-context; changed ticket revision rejects. |
| `ACX5` | Closed or invalidated leases cannot resume, rebind, switch or close again; missing upstream returns its finite decision and requirement change invalidates an active lease. |
| `ACX6` | Lease/request/decision serialization contains only typed identifiers, revisions and lifecycle values; attempted transcript, prompt, raw packet/body, resume prose, URI/path, source text or untyped payload fields reject. |
| `ACX7` | Focused Router, six-module Router regression, full explicit serial unittest, strict full-tree mypy, in-memory compile, source/scope/diff/topology/porcelain/cache gates pass. |
| `ACX8` | Three bounded reversals turn their governing tests red and restore byte-for-byte: permit changed ticket revision as correction; replay a closed lease; switch ticket while reusing the prior side-context ID. |

## First red, source gates and return

First red imports the six enums and three models above and calls
`RouterEngine.decide_agent_context_transition`; it fails before production mutation because the
public surface does not exist. Preserve the failure and confirm the incoming focused Router
`43/43` and six-module Router `110/110` baselines.

Committed source gates inspect new public annotations and reject `Any`, `object`, raw `str`
domain fields, `type: ignore`, cast, dynamic member lookup, constructor bypass, callable/`None`
effect ports, broad catches and subprocess/Git/filesystem/network imports introduced by R02B.
There is no line-count rule.

Return one implementation commit changing exactly the four production/test paths, then one
separate WPR-only handoff commit containing first red, ACX1-ACX8, three reversal
reds/restorations, full verification identities and final clean readback. Return only
`COMPLETED`, `BLOCKED` or `CHANGE_DETECTED`; progress-only final is not completion.

No helper/subagent, new worktree, self-review/integration, next ticket, R02C-R06, 06G0P,
live model/Figma/Codex/home/App/target-project/network effect, push/staging publication,
package/install, Secret, release or deployment.
