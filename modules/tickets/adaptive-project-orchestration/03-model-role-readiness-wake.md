# R03 — Model-role SPEC Readiness and Architecture Wake Gate

| Field | Value |
| --- | --- |
| SPEC / AC | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` revision 05 / AC-12 |
| PRD / change | `PRD-20260815-022` / `CHG-20260815-022` |
| Context / environment | `doc/context/adaptive-project-orchestration/main.md` at `SPEC_REVISION_05_APPROVED / ROUTER_PHASE_ACTIVE`; local pure-Python verification only; no target, host or external environment effect |
| State / closure | `COMPLETE / APPROVED / INTEGRATED`; `CLOSURE-ADAPTIVE-ROUTER-R03-01`, ACX1-ACX8, revision `r03-02` |
| Dependency / baseline | R02C3 guarded integration `93a66a4d8b8d7eacdc591ab4b7ef53f10b2b8447`; implementation authority exists only after the separate exact dispatch registry containing `PRG-20260815-507` |
| Implementation language / checker | Python 3.11; `python -B -m mypy --strict --explicit-package-bases --no-incremental library tests` |
| Delivery profile / resource plan | `STANDARD`; one `gpt-5.6-luna` max implementation owner; no helper |
| Control / implementation owner | Reviewer task `019fb935-bbe1-7f71-8b4b-58ba20c81626`; planned implementation task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` in its existing permanent worktree only |
| Lane | `codex/implementation-router-model-role-readiness-r03` from dispatch registry `PRG-20260815-507`; no new worktree |
| Dispatch binding | Handoff `hnd-adaptive-router-r03-20260815`; allocation `aln-adaptive-router-r03-20260815`; receipt `rcpt-adaptive-router-r03-20260815`; question `q-adaptive-router-r03-20260815`; correlation `corr-adaptive-router-r03-20260815`; side Context `scx-adaptive-router-r03-20260815-01`; expected return `ret-model-role-readiness-review-handoff-r03`; activated only by the exact registry containing `PRG-20260815-507` |
| XSS / effects | `XSS_NOT_APPLICABLE`; metadata-only pure validation, no Browser/WebView/HTML/DOM/JavaScript context, source/body read, filesystem, Git, Agent, host or network effect |
| Operations / rollback | No runtime operation. Before guarded integration, withhold approval; after it, a separately reviewed additive revert only. Never reset, force or delete reviewed evidence. |

## One observable outcome

`ModelRoleReadinessGate.assess(profile, request)` returns the one finite, typed decision that
controls whether the architecture owner may enter `SLEEPING` for the exact submitted SPEC/Profile
revision. It is deterministic and pure: it either returns `OWNER_APPROVAL_REQUIRED`,
`ARCHITECTURE_OWNER_REQUIRED` with one exact wake reason, or `READY_FOR_SUPERVISION` with no wake
reason. It does not choose a provider/model, grant authority, dispatch a ticket, mutate shared
Context, invoke an Agent, inspect source, or perform any host/effect operation.

## Frozen public contracts

Add and publicly export strict named types/models:

```text
ModelRole = ARCHITECTURE_OWNER | SUPERVISOR_REVIEWER
          | IMPLEMENTATION_OWNER | RESEARCH_HELPER
RoleActivityState = ACTIVE | SLEEPING | WAKE_REQUIRED
SpecificationReadinessDecision = READY_FOR_SUPERVISION
                               | ARCHITECTURE_OWNER_REQUIRED
                               | OWNER_APPROVAL_REQUIRED
SpecificationClosureKind = PUBLIC_CONTRACTS | FINITE_STATES | ERROR_MEANINGS
                         | OWNERSHIP_DEPENDENCY_EFFECT_BOUNDARIES
                         | ROLLBACK_FORWARD_FIX | ACCEPTANCE_CRITERIA
                         | DELIVERY_PROFILE | SECURITY_XSS | UI_SOURCE_CLASSIFICATION
SpecificationWakeReason = SPEC_AMBIGUOUS | SPEC_CONTRADICTORY
                        | PUBLIC_CONTRACT_UNDEFINED | ACCEPTANCE_UNPROVABLE
                        | ARCHITECTURE_CONFLICT | CROSS_TICKET_DESIGN_CONFLICT
                        | REQUIREMENT_CHANGED | NEW_EXTERNAL_PRIVILEGED_BOUNDARY
                        | HIGH_ASSURANCE_TRIGGER | MODEL_CAPABILITY_INSUFFICIENT
                        | CLOSURE_INCOMPLETE | OPEN_DESIGN_DECISION
                        | SUPERVISOR_CAPABILITY_UNAVAILABLE

ModelRoleAssignment = {
  project_profile_ref: OpaqueMetadataId,
  role: ModelRole,
  model_ref: OpaqueMetadataId,
  capability_refs: tuple[OpaqueMetadataId, ...],
  activity_state: RoleActivityState,
  evidence_refs: tuple[OpaqueMetadataId, ...]
}
SpecificationClosureEvidence = {
  kind: SpecificationClosureKind,
  evidence_ref: OpaqueMetadataId
}
SpecificationReadinessBlocker = {
  reason: SpecificationWakeReason,
  evidence_ref: OpaqueMetadataId
}
SpecificationReadinessRequest = {
  project_profile_ref: OpaqueMetadataId,
  project_profile_version: NonBlankText,
  specification_ref: OpaqueMetadataId,
  specification_revision: RevisionDigest,
  owner_approval_ref: OpaqueMetadataId | None,
  closure_evidence: tuple[SpecificationClosureEvidence, ...],
  open_design_decision_refs: tuple[OpaqueMetadataId, ...],
  blockers: tuple[SpecificationReadinessBlocker, ...]
}
SpecificationReadinessAssessment = {
  project_profile_ref: OpaqueMetadataId,
  project_profile_version: NonBlankText,
  specification_ref: OpaqueMetadataId,
  specification_revision: RevisionDigest,
  decision: SpecificationReadinessDecision,
  wake_reason: SpecificationWakeReason | None
}
```

All models inherit existing strict, frozen, extra-forbid `RouterModel`. Every identifier remains
opaque metadata only; no contract accepts a prompt, body, source, filesystem path, URI, callable,
untyped mapping or effect port. `ModelRoleAssignment.capability_refs` and `evidence_refs` are
non-empty, duplicate-free and disjoint; role/model/profile identifiers are distinct. A profile
has exactly one assignment for each of the four `ModelRole` values, all assignments bind its exact
`profile_id`, and `build_router_poc_profile()` binds four distinct opaque model/capability
references with the documented active architecture/supervisor/implementation lifecycle. Model
identity is never interpreted as authority.

`ProjectWorkflowProfile` gains the exact non-optional
`model_role_assignments: tuple[ModelRoleAssignment, ...]` field; all valid construction and
`model_validate` fixtures in its existing tests must supply the complete exact set. No default,
`None`, partial role set, duplicate role, cross-profile assignment or update/bypass construction is
allowed.

## Exact decision order

The gate compares the request's exact profile ref/version to the supplied profile before every
success result. A mismatch or malformed typed object fails public construction; it never becomes a
fallback decision.

For a valid request, apply this frozen precedence exactly:

1. If `owner_approval_ref is None`, return `OWNER_APPROVAL_REQUIRED` and `wake_reason=None`.
   This owner wait takes precedence over every other incomplete fact.
2. Otherwise, if `blockers` is non-empty, return `ARCHITECTURE_OWNER_REQUIRED` and the unique
   lowest declaration-order `SpecificationWakeReason` represented by the blockers. Duplicate
   blocker reasons fail construction. This covers every mandatory wake trigger without allowing
   the supervisor to infer a resolution.
3. Otherwise, if `closure_evidence` is not the exact complete, duplicate-free set of all nine
   `SpecificationClosureKind` values, return `ARCHITECTURE_OWNER_REQUIRED / CLOSURE_INCOMPLETE`.
4. Otherwise, if `open_design_decision_refs` is non-empty, return
   `ARCHITECTURE_OWNER_REQUIRED / OPEN_DESIGN_DECISION`.
5. Otherwise, require the profile's one `SUPERVISOR_REVIEWER` assignment to be `ACTIVE` with at
   least one capability reference. If not, return
   `ARCHITECTURE_OWNER_REQUIRED / SUPERVISOR_CAPABILITY_UNAVAILABLE`.
6. Otherwise, return `READY_FOR_SUPERVISION` and `wake_reason=None`.

The gate never changes an assignment's state. The caller/Routing layer performs any subsequent
state transition only after this decision; this ticket owns only the pure readiness proof.

## Exact source boundary

- `library/workflow_router/contracts.py`
- `library/workflow_router/profile.py`
- new `library/workflow_router/model_role_readiness.py`
- `library/workflow_router/__init__.py`
- `tests/test_workflow_model_role_readiness.py`
- `tests/test_workflow_router.py` only for existing `ProjectWorkflowProfile` construction fixtures
- one append-only `doc/WorkProgressReport.md` handoff after implementation

Integrated R01/R02 source and tests are read-only regressions except the narrow existing
`ProjectWorkflowProfile` fixtures above. No other path is writable.

## Acceptance closure

| ID | Acceptance |
| --- | --- |
| `ACX1` | All enums/models/profile construct and JSON-round-trip through ordinary strict APIs. Every missing/null/extra/duplicate/wrong finite value, raw path/body/prompt/source, partial or cross-profile role assignment, duplicate capability/evidence/blocker/closure kind and contradictory assessment shape fails construction. |
| `ACX2` | The default POC profile has exactly the four declared roles, each with opaque distinct model/capability evidence; no model reference itself grants an authority or dispatch capability. |
| `ACX3` | Missing owner approval always returns only `OWNER_APPROVAL_REQUIRED / None`, including when blockers, closure omissions, open decisions or unavailable supervisor coexist. |
| `ACX4` | Each of the ten mandatory typed blocker reasons independently returns only `ARCHITECTURE_OWNER_REQUIRED` with that exact reason; multiple blockers deterministically select the lowest enum declaration-order reason. |
| `ACX5` | Each omitted/duplicate closure kind returns only `ARCHITECTURE_OWNER_REQUIRED / CLOSURE_INCOMPLETE`; all nine exact closures are required. An open design ref returns only `OPEN_DESIGN_DECISION`. |
| `ACX6` | A complete approved request with all nine closures, no blockers/open decisions and an active supervisor returns only `READY_FOR_SUPERVISION / None`. A sleeping or wake-required supervisor returns only `SUPERVISOR_CAPABILITY_UNAVAILABLE`. |
| `ACX7` | The committed bounded source gate rejects `Any`, `object`, raw `str` domain fields, `type: ignore`, cast, dynamic member lookup, model-construction/copy/update bypass, broad catches, callable/optional effect ports and filesystem/Git/Agent/host/network imports in the R03-owned source. It rejects the exact semantic mutations listed below without writing or executing mutated source. |
| `ACX8` | First red, focused R03 plus profile/Router regression, explicit serial full unittest, strict full-tree mypy, in-memory compile, source/scope/diff/ancestry/topology/porcelain/cache gates all pass. |

## ACX7 semantic source-gate mutation table

The test must parse committed R03 production source and reject each in-memory replacement below;
the pristine source must pass. The test must not `exec`, `eval`, compile, import or write a mutated
module. A substring-only check is insufficient: the gate must inspect the decision function AST
and the exact compared enum/member operands.

| Label | Canonical semantic target | In-memory mutation | Required red assertion |
| --- | --- | --- |
| `owner-approval-precedence` | first decision branch compares `request.owner_approval_ref is None` and returns `OWNER_APPROVAL_REQUIRED` | replace `is None` with `is not None` | source gate rejects mutation |
| `blocker-wake-bypass` | non-empty `request.blockers` selects a declared blocker reason before closure/open-decision checks | replace the blocker condition with `False` | source gate rejects mutation |
| `closure-completeness-bypass` | exact set comparison requires every `SpecificationClosureKind` before READY | replace completeness condition with `True` | source gate rejects mutation |
| `open-decision-bypass` | `request.open_design_decision_refs` non-empty returns `OPEN_DESIGN_DECISION` | replace the condition with `False` | source gate rejects mutation |
| `supervisor-activity-bypass` | `SUPERVISOR_REVIEWER` assignment requires `RoleActivityState.ACTIVE` before READY | replace the active comparison with `RoleActivityState.SLEEPING` | source gate rejects mutation |

## First red and return

First red imports the absent public readiness contracts and `ModelRoleReadinessGate`, then asks a
complete approved request to return `READY_FOR_SUPERVISION`. It must fail before production
mutation because R03 does not exist. Preserve that failure, implement ACX1-ACX8 one behavior at a
time and keep integrated R01/R02 bytes unchanged except the frozen profile-fixture compatibility
scope.

Return one implementation commit changing exactly the six source/test paths, then one separate
WPR-only handoff containing first red, ACX mapping, five source-gate reversal reds/restorations,
full verification identities and final clean readback. Return only `COMPLETED`, `BLOCKED` or
`CHANGE_DETECTED`; progress-only final is not completion.

No helper/subagent, new worktree, self-review/integration, next ticket, R04-R06, live model,
Codex/home/App/target-project/network effect, push/staging publication, package/install, Secret,
release or deployment is authorized.
