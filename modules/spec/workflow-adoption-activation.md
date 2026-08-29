# Workflow adoption activation and admission specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-JOHNNY-WORKFLOW-ADOPTION-20260829-01` |
| Status | `DRAFT / OWNER_EXACT_APPROVAL_PENDING` |
| Author / baseline | Codex architecture owner / `control/plugin-adoption-quality-architecture` / `79505f65e932541d06eac797a2ea165f74cd194e` |
| Context | `CTX-PLUGIN-ADOPTION-QUALITY-20260829-01` (`ARCHITECTURE_DRAFT`) |
| PRD / change / ADR | `PRD-20260829-048` / `CHG-20260829-048` / `ADR-20260829-036` |
| Implementation language | Python 3.11 strict typed core; bounded host/language adapters at edges |

## Problem, goal and out of scope

The installed plugin's governance is reliable only after its takeover skill is selected. Real
projects have therefore required repeated owner reminders to update document indexes, split code
responsibilities and delegate implementation to the ticket's lower-tier owner.

Success means an opted-in project exposes default activation plus executable integration checks
for facts source can prove, and honestly classifies native dispatch evidence it cannot prove.

Out of scope: machine-global policy, a background runner, receipt-bound synchronous dispatch,
generic size limits, automatic ticket approval, fabricated host provenance, target runtime imports
from this plugin and external provider effects.

## Public contracts and finite states

```text
HostInstructionKind = CODEX_AGENTS | CLAUDE_PROJECT_INSTRUCTION
ActivationState = ACTIVE | ABSENT | STALE | HOST_SURFACE_UNAVAILABLE
ActivationAction = CREATE_BLOCK | UPDATE_BLOCK | NO_CHANGE
AdmissionState = LOCAL_GATE_ENFORCED | REMOTE_GATE_ENFORCED | UNAVAILABLE
DispatchEvidence = NOT_REQUIRED | REVIEWER_OBSERVED | HOST_PROVEN | UNAVAILABLE
AdmissionDecision = ACCEPTED | DOCUMENT_TOPOLOGY_REJECTED
                  | RESPONSIBILITY_BOUNDARY_REJECTED | CAPABILITY_UNAVAILABLE
```

`ProjectActivationRequest` binds canonical repository identity, host kind, expected instruction
path identity, expected current digest and plugin/skill identity. Tagged create/update requests have
no action-dependent nullable fields. `ProjectActivationPlan` returns exact bounded content and
expected post-digest. The adapter rejects stale pre-state and performs readback.

`ResponsibilityBoundaryContract` is ticket-owned and names each responsibility unit, owned
behavior/state, public interface, allowed/forbidden dependencies, Composition Root, production
binding, test fake and language adapter. It is not inferred from the candidate after the fact.

`WorkflowAdmissionRequest` binds integration ref/baseline, candidate commit, exact ticket,
applicable managed-artifact roots, responsibility-contract revision and delivery profile. Results
contain codes, bounded paths/symbol IDs and digests only.

## User and system flows

### Project adoption

1. Owner selects one repository and host surface.
2. Pure planner reads exact current digest and returns create/update/no-change.
3. Owner approves the target mutation; host adapter applies only the delimited block and reads it
   back.
4. A disposable new session proves the host actually auto-loads the block and selects the takeover
   skill for a representative software-change request.

### Managed document candidate

1. Admission derives changed managed leaves/indexes from the actual candidate diff.
2. It resolves only each affected declared root path and validates leaf plus direct ancestors.
3. Missing, duplicate, stale, cyclic, orphaned or body-bearing index edges reject before
   integration. Unrelated source-only candidates remain not applicable.

### Source responsibility candidate

1. Ticket supplies the accepted responsibility contract and exact writable paths.
2. Strict checker plus language AST/source/schema adapter evaluate actual candidate symbols and
   dependency construction.
3. Undeclared responsibility, forbidden dependency direction, provider construction outside the
   Composition Root or missing test seam rejects before integration.

### Same-lifetime dispatch

1. The activated takeover skill routes an admitted ticket to the reviewer.
2. A distinct implementation owner is delegated once through the host-native operation; reviewer
   waits once, reviews and integrates.
3. Host provenance is reported only at the strength actually available. No durable bridge is
   created for this live call.

## Responsibility, dependency and composition map

| Component | Owns | Must not own |
| --- | --- | --- |
| `ProjectAdoptionPlanner` | pure activation decision and exact bounded plan | filesystem write, Git, dispatch |
| `ProjectInstructionAdapter` | approved delimited-block effect and readback for one host | governance text, integration, subagent control |
| `ArtifactTopologyAdmissionPort` | candidate managed-tree validation | content authoring, source architecture |
| `ResponsibilityBoundaryAdmissionPort` | ticket-bound code responsibility/dependency validation | document topology, integration |
| language admission adapter | strict AST/source/schema facts for one language | ticket policy or review conclusion |
| `NativeDispatchCoordinator` | live reviewer delegation/wait and observed return | runner, queue, receipt, Git proof fabrication |
| `WorkflowIntegrationAdmission` | compose applicable decisions before existing authority gate | planning, implementation, target runtime |

Production composition is one short-lived reviewer/gate invocation. Pure planner and validators
receive immutable contracts; filesystem/Git/host adapters are injected. Tests replace every adapter
with strict fakes and cannot bypass ordinary constructors.

## Data, security, Provider and operations

No database, cache, network provider or secret is required. Target instruction content and
responsibility contracts remain target-owned/versioned. Durable results exclude prompts, raw
source, host transcripts, credentials, absolute paths and PII. Remote-enforced status requires
separate direct ruleset/capability readback; it is not inferred from a local pass.

## Acceptance criteria and TDD cuts

1. Each host adapter proves `CREATE_BLOCK`, `UPDATE_BLOCK`, `NO_CHANGE`, stale pre-state refusal and
   exact post-digest readback without touching text outside its delimited block.
2. Installed disposable-project tests start a fresh session and distinguish `ACTIVE`, `ABSENT`,
   `STALE` and `HOST_SURFACE_UNAVAILABLE`; a manifest/default prompt alone cannot produce `ACTIVE`.
3. Document tests create, revise, replace and archive leaves; omitting any selected parent/root
   update, using a stale digest, adding a second parent or copying a child body into an index turns
   admission red, then exact restoration returns green.
4. Responsibility tests use a real small fixture and reverse-mutate one forbidden dependency,
   provider construction outside Composition Root, undeclared responsibility and missing fake
   seam. Each mutation turns the named gate red. A large cohesive module is not rejected by size.
5. Dispatch behavioral tests give the activated skill a real admitted ticket and observe one native
   child plus one wait and independent parent review. Without non-forgeable host callback the result
   is exactly `REVIEWER_OBSERVED`, never `HOST_PROVEN`.
6. Missing native delegation returns `UNAVAILABLE`; it neither lets the reviewer self-implement nor
   creates a runner/receipt fallback.
7. Repository admission refusal leaves the integration ref byte-for-byte unchanged. Local and
   remote enforcement states are tested independently.
8. Detach tests prove plugin removal does not delete target files and the conditional target block
   remains harmless when the skill is absent.

## Risks, compatibility, rollback and deployment prerequisites

The principal risk is overstating activation or dispatch proof. All UI/CLI output therefore carries
the three independent states. Rollback is forward removal/update of the exact delimited activation
block under owner authority plus plugin rollback; gates remain additive and fail closed. Publication
requires Codex and Claude disposable installed qualification and payload regeneration/repinning.

## Ticket partition after approval

1. `WA-01` strict activation contracts and pure planner.
2. `WA-02` Codex and Claude project-instruction adapters plus exact readback.
3. `WA-03` managed-document repository admission (R09C closure).
4. `WA-04` ticket-bound responsibility contract and one Python admission adapter.
5. `WA-05` native-dispatch behavioral qualification and evidence-strength reporting.
6. `WA-06` installed cross-host qualification, shipped skill updates and publication.

Each ticket is separately approved and dispatched. No ticket combines these responsibilities.

## Revision signature and approval

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-29 | Codex architecture owner / `control/plugin-adoption-quality-architecture` / `79505f65e932541d06eac797a2ea165f74cd194e` | Drafted project-scoped activation, executable admission and honest dispatch-evidence architecture from observed installed-project failures. |

Decision maker: Project owner. Exact approval pending.
