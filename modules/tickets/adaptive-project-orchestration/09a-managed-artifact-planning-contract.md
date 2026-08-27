# R09A — Provider-neutral managed-artifact planning contract

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-ADAPTIVE-R09A-MANAGED-ARTIFACT-PLANNING` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2` Revision 10 / AC-17R9, AC-17R10 and TDD items 22–23 |
| Requirement / Context / ADR | `PRD-20260828-043` / `CHG-20260828-043` / `CTX-ADAPTIVE-PROJECT-ORCHESTRATION-20260828-09` (`bf077fdbce324527b7f95ea8382967a12ef42ad9ef6fb74c98ce020186cf8bfc`) / `ADR-20260828-031` |
| State / closure | `DRAFT / OWNER_APPROVAL_REQUIRED / NON_DISPATCHABLE`; `CLOSURE-ADAPTIVE-R09A-MANAGED-ARTIFACT-PLANNING-01`, ticket revision `r09a-01` |
| Document revision | `01` |
| Approval authority | Project owner approved exact SPEC Revision 10 at `b0a973a8a66d0dbbd88e94990eaa8dc6716b7954` and authorized reviewer opening of R09A only. This exact ticket remains unapproved. |
| Source baseline / dependency | `50476a658e33074d9b9c90db17188725dde544fe`; candidate must descend from the committed ticket-authority SHA created after this draft reaches `main`. Read-only dependencies are `library/workflow_router/artifact_tree.py`, its strict contracts in `library/workflow_router/contracts.py`, and the current target-document contracts. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh; sole Agent orchestrator and independent reviewer. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; `READY_LOW_MODEL` only after exact ticket approval, one synchronous owner lane and no helper. |
| Agent Context / worktree / branch | Unbound while this ticket is a draft. After approval, the reviewer creates `.worktrees/adaptive-r09a-managed-artifact-planning` on `implement/adaptive-r09a-managed-artifact-planning` from the exact approved ticket commit and binds one fresh side-context ID. |
| Delivery / language | `POC / STANDARD`; Python 3.11, frozen strict Pydantic contracts, complete annotations, `mypy --strict`, deterministic pure proof and independent review. |
| XSS / effects | `XSS_NOT_APPLICABLE`. Pure in-process planning over caller-supplied metadata and ephemeral candidate bytes; no filesystem, Git, host, provider, process, network, environment, queue, receipt, runner, hook, publication, installation or target mutation. |

## Boundary declaration

```johnny-boundary
create = library/workflow_router/managed_artifact_planning.py
modify = library/workflow_router/managed_artifact_planning.py
modify = library/workflow_router/target_document_contracts.py
create = tests/test_managed_artifact_planning.py
modify = tests/test_managed_artifact_planning.py
create = modules/element/python/adaptive-project-orchestration/09a-managed-artifact-planning/
modify = modules/element/python/adaptive-project-orchestration/09a-managed-artifact-planning/
forbid = library/workflow_router/__init__.py
forbid = library/workflow_router/contracts.py
forbid = library/workflow_router/artifact_tree.py
forbid = library/workflow_router/router.py
forbid = library/local_orchestration/
forbid = tests/test_workflow_artifact_tree.py
forbid = tests/test_target_document_management.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Create one provider-neutral, effect-free entry point:

```python
plan_managed_artifact(
    request: ManagedArtifactRequest,
) -> ManagedArtifactPlanningResult
```

It accepts exactly one tagged `CREATE`, `REVISE`, `REPLACE` or `ARCHIVE` request containing the
action's exact current/candidate path transitions and proposed document mutations. It returns
`PLANNED` only when the proposal is a complete, self-consistent semantic/document plan: every
changed terminal and every induced selected ancestor through root is represented exactly once,
every candidate present path resolves, every candidate absent path proves only terminal absence,
and no unselected mutation is present. Every other outcome is one finite no-effect rejection.

This ticket does not write the plan. R09B will own transactional persistence and post-write
resolution; R09C will own candidate admission; R09D/R09E will own Codex behavior and installed
qualification. R09A exposes no writer, hook, gate, Composition Root, retry, cache or background
service.

`TicketDecompositionDecision = READY_LOW_MODEL`: Revision 10 fixes the action matrix, state algebra,
ancestor closure, effect boundary and rollback expectations. R09A has one pure planning result, one
implementation owner, one source boundary and deterministic in-memory verification. File count is
not the admission reason.

## Frozen strict contracts

Add the Revision 10 types to `library/workflow_router/target_document_contracts.py` without changing
the behavior or serialized shape of existing `TargetDocumentMutation`, `TargetDocumentPlan`,
`DocumentWriteResult` or their consumers. Keep the new surface private to its exact modules;
`library.workflow_router.__init__` remains byte-identical.

The four request variants are a discriminated union on `action` and carry no action-dependent
nullable fields:

```text
CREATE  = destination_transition + proposed_document_mutations
REVISE  = selected_transition + proposed_document_mutations
REPLACE = current_transition + replacement_transition + proposed_document_mutations
ARCHIVE = active_transition + archive_transition + proposed_document_mutations
```

`ManagedArtifactPathSnapshot` carries family, root ref, at least three explicit path refs, expected
leaf ref, terminal state and path nodes. `PRESENT` supplies exactly one node per ref and ends in a
leaf. `ABSENT` supplies exactly the root and every partition (`len(nodes) = len(refs) - 1`), and its
last parent has no edge to the expected leaf. Missing earlier edges/nodes are invalid, not absence.

`ManagedArtifactNodeState` is the strict tagged union `ABSENT | PRESENT(revision, digest,
lifecycle)`. `ManagedArtifactNodeMutation` binds one artifact ref to exact expected and next states.
The three document variants each carry the same explicit `artifact_ref` so no tuple position or
path-name convention binds semantic and byte mutations:

```text
CREATE(artifact_ref, path, kind, content, content_digest, sealed)
UPDATE(artifact_ref, path, kind, expected_current_digest,
       content, content_digest, sealed = false)
DELETE(artifact_ref, path, kind, expected_current_digest)
```

`artifact_ref` is the explicit carrier for Revision 10's requirement that every semantic node
transition bind exactly one document mutation; it grants no authority. Create/update content must
use canonical LF and its SHA-256 must equal both the document mutation digest and the candidate
`PRESENT` node digest. Delete exposes no content, candidate digest or sealed field and its expected
digest must equal the current `PRESENT` node digest. Paths remain normalized target-relative paths.

The result is an exact variant:

```text
PLANNED(request_ref, plan)
| REJECTED(request_ref, decision)
```

`PLANNED` carries no rejection and `REJECTED` carries no plan. Rejections use only the applicable
Revision 10 finite decisions: path/tree/edge/lifecycle errors,
`TERMINAL_STATE_MISMATCH`, `ANCESTOR_CASCADE_INCOMPLETE`,
`DOCUMENT_MUTATION_MISMATCH` or `UNRELATED_MUTATION`. Cross-transition representations of the same
artifact ref that disagree are `ARTIFACT_TREE_INVALID`; no new catch-all/error-text status exists.
Plans contain deterministic action-slot path transitions, artifact-ref-sorted node mutations,
normalized-path-sorted document mutations and expected post-state snapshots.

R09A treats `baseline_commit` as an exact opaque plan binding and never claims it observed a Git
baseline. It therefore cannot emit `BASELINE_MISMATCH`; that enum member is reserved for R09B's
effect boundary. A test/source gate rejects any repository/Git read or R09A branch that fabricates
baseline verification.

All contracts are frozen, strict, extra-forbid and revalidate nested historical instances. They
reject `Any`, `object`, raw mappings, casts, dynamic lookup, bypass construction, callable/effect
fields, reserved-zero revision/digest values, absolute paths, URIs and control-plane paths. Raw
content is ephemeral plan input/output only and is never a log, Router-state or telemetry field.

## Exact planning order

1. Validate the tagged request and all ordinary nested models before evaluating semantics.
2. Validate each current and candidate snapshot's unique ordered refs/nodes, root/family/kind
   shape, non-reserved metadata and exact selected edges. A `PRESENT` snapshot must pass the existing
   `ArtifactTreeResolver`; an `ABSENT` snapshot must have a valid complete prefix and only the final
   edge absent.
3. Enforce the Revision 10 action table: create absent→present; revise present→same-leaf present;
   replace current present→absent plus distinct replacement absent→present; archive active
   present→absent plus explicit `ARCHIVE_LIBRARY` absent→`ARCHIVED` present.
4. Require every repeated artifact ref across action transitions to describe byte-identical current
   and candidate node states. Shared ancestors of replacement paths receive one candidate state,
   never competing updates.
5. Derive the exact changed-node set from the current/candidate union. Starting at each changed
   terminal, require the candidate parent edge update/removal; because that index digest/revision
   changes, repeat through every selected ancestor to root. Preserve every unselected sibling edge
   exactly and reject a missing induced ancestor.
6. Bind exactly one proposed document mutation to each changed artifact ref. Mode must match
   absent→present/create, present→present/update or present→absent/delete; path and content digests
   must be unique and exact. Reject any missing, duplicate or unrelated binding.
7. Return one canonically ordered `PLANNED` result. A rejection returns only request identity and its
   finite decision; it never leaks content, path, exception text or a partial plan.

## Reusable-module selection record

```text
selected: no new reusable module.
dependency evidence: existing target-owned ArtifactTreeResolver and strict artifact-tree contracts;
                     existing target-document path/digest validators.
read: exact selected-path resolver -> target-document contracts -> their focused tests.
rejected: a second tree resolver; filesystem/Markdown discovery; generic workflow engine;
          host/router/receipt/runner capability; document writer; public package export.
boundary: R09A only validates and normalizes one complete proposed plan in memory.
```

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| `MAP1` | Every action request, snapshot/state, document variant, plan and result constructs and JSON-round-trips through ordinary strict validators. Extra/missing/null/wrong finite fields, reserved metadata, bypass-built nested values, absolute/control paths and contradictory result shapes fail. |
| `MAP2` | `CREATE` absent→present and `REVISE` present→same-leaf present return deterministic `PLANNED`; each includes the changed leaf and every digest-induced ancestor mutation through root exactly once. |
| `MAP3` | `REPLACE` current present→absent plus distinct replacement absent→present and `ARCHIVE` active present→absent plus archive-library absent→archived present return one consistent plan, including delete/create bindings and a single update for shared ancestors. |
| `MAP4` | A missing intermediate segment, terminal edge on an `ABSENT` snapshot, absent node supplied as a leaf, invalid kind/family/order, stale edge, duplicate/cycle/parent, mismatched action slot or invalid lifecycle returns the exact finite rejection and no plan. |
| `MAP5` | Changing a leaf while omitting the nearest parent, grandparent or root mutation returns `ANCESTOR_CASCADE_INCOMPLETE`. Mutating/copy-changing an unselected sibling or disagreeing about a shared ancestor returns `UNRELATED_MUTATION` or `ARTIFACT_TREE_INVALID`; no sibling node/body is loaded. |
| `MAP6` | Missing/duplicate/unrelated semantic-to-document binding, wrong create/update/delete mode, stale expected digest, CRLF/mismatched candidate digest, duplicate target path or content on delete returns `DOCUMENT_MUTATION_MISMATCH` and no partial plan. |
| `MAP7` | Source/AST gates prove exactly one typed entry point, use of the existing resolver for present paths, no package export, `Any`, `object`, cast, dynamic access, raw mapping, broad catch, filesystem/Git/process/network/environment/host/provider/runner/queue/receipt/hook/write effect or exception-detail serialization. |
| `MAP8` | Focused tests, incoming artifact-tree/target-document regressions, strict type check, compilation and diff/scope checks pass. The element index names the exact ticket/SPEC/Context/source/test refs and records that planning is not persistence or authority. |
| `MPM1` | Reverse-mutate terminal absence to accept an earlier missing path segment; `MAP4` turns red, then exact restoration returns green. |
| `MPM2` | Reverse-mutate cascade derivation to omit one grandparent/root update; `MAP5` turns red, then exact restoration returns green. |
| `MPM3` | Reverse-mutate delete validation to accept content or the wrong expected digest; `MAP6` turns red, then exact restoration returns green. |
| `MPM4` | Reverse-mutate shared-ancestor reconciliation to accept two candidate states; `MAP3` or `MAP5` turns red, then exact restoration returns green. |

The authentic first red imports the absent tagged contracts and `plan_managed_artifact` entry point
from their exact private modules and fails before production mutation. Strong-type preflight then
constructs all request/result variants and JSON round trips, and uses bypass-built malformed objects
only in named negative rejection cells. No mock, cast, historical-object reuse or hand-built success
payload is admissible evidence.

## Applicable defect classes

| Class | Applies | Required R09A case |
| --- | --- | --- |
| Path-prefix mismatch | Yes | Exact normalized target-relative paths; equal-prefix, extra-character, trailing-slash, case variant, encoded separator, traversal and empty path inputs do not alias an authorized binding. |
| Null/empty/container | Yes | `None`, empty/whitespace IDs, empty path refs/nodes/mutations and extra empty action slots fail strict construction or return the exact no-plan decision. |
| Authority bypass | Yes, as absence proof | No package export, writer, Git, host or callback port exists; direct/internal invocation has the same pure contract and cannot grant integration authority. |
| Token/credential comparison | No | No token, Secret, credential or authentication input exists; source gates reject adding one. |
| Error-code consistency | Yes | Every semantic failure maps to one finite decision; rejected results contain no plan/path/content/exception detail and `BASELINE_MISMATCH` is impossible in R09A. |
| Dependency exception | Yes, bounded | The only collaborator is the pure existing resolver. Malformed inputs are normalized before it; no broad catch or serialization of exception text is allowed. |

Formal frontend composition is `N/A`: no UI component, DOM, renderer, design source, navigation,
state store, accessibility surface or runtime untrusted source-to-sink path is touched.

## Verification and reviewer-owned adversarial closure

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_managed_artifact_planning.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_workflow_artifact_tree.py tests/test_target_document_management.py
py -3.11 -m mypy --strict library/workflow_router/target_document_contracts.py library/workflow_router/managed_artifact_planning.py tests/test_managed_artifact_planning.py
py -3.11 -m compileall -q library/workflow_router/target_document_contracts.py library/workflow_router/managed_artifact_planning.py
git diff --check 50476a658e33074d9b9c90db17188725dde544fe HEAD
git status --short
```

The Terra/xhigh reviewer reads the exact ticket blob and reruns focused, regression, type and
compile gates without lossy output reduction. The reviewer independently constructs attacks for:
missing one action requirement; null/empty/extra/Unicode path metadata; wrong/duplicate state
order; repeated planning; shared-ancestor conflicts; stale baseline/digest; partial delete/create;
idempotent deterministic output; old resolver/target-document regression; and sanitized rejection
evidence. Concurrency, DB, tenant/permission and deployment-config attacks are `N/A` because R09A
has no effect port; the reviewer must verify that this absence is enforced, not assumed.

The reviewer personally performs one counter-mutation not used by the implementation owner—remove
either terminal-absence prefix validation or one root-cascade requirement—and proves the exact
governing cell turns red before byte-for-byte restoration. Passing tests are reference evidence;
reviewer approval and the document-mutation gate remain the only path toward integration.

## Ownership, return and rollback

This closure is same-lifetime synchronous: the Terra/xhigh reviewer dispatches, calls one bounded
`wait_agent`, receives the final return, reviews and only then commits the candidate. It requires no
runner, durable queue, receipt, descriptor, gateway, host workspace readback or asynchronous wake.
The Luna/xhigh implementation owner modifies only the declared boundary, does not commit or push,
does not edit documents and cannot control another Agent.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with MAP/MPM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or
`CHANGE_DETECTED -> REQUIREMENT_CHANGED`. Before integration, rollback is withholding the
candidate. After integration, rollback is a separately reviewed additive revert. No return
authorizes R09B, filesystem mutation, hook, target effect, integration, push, publication, release,
installation or deployment.

## Completion record

Pending exact ticket approval and implementation. No worktree, implementation owner, first-red,
source mutation, review, commit, gate, push or effect currently exists.
