# Router R01 Versioned Route Instruction Contract Code Review

## Review scope and decision

| Field | Value |
| --- | --- |
| Ticket / closure | `01-route-instruction-contract` / `CLOSURE-ADAPTIVE-ROUTER-R01-01` R1-R7 revision 01 |
| Dispatch baseline | `11901565ca0dde46fc6913f4caa7d763fb5f0ab6` |
| Implementation | `bff21771d3dc10eae4b354097e40123eb2b13001` |
| Docs-only handoff | `a16dfc38eb6141e2aef5fa480be741b1f057ca57` |
| Branch / owner | `codex/implementation-router-route-instruction-r01` / task `019ffb0c-c9c7-7b30-b614-02dea7ed9042` |
| Review result | `CHANGES_REQUESTED / SAME_TICKET_REFREEZE_REQUIRED` |

The commit chain and file scope are valid: the implementation contains exactly the five
authorized Router/test paths, the handoff contains only `doc/WorkProgressReport.md`, and the
implementation worktree is clean. The new models are strict and the Router copies Profile
metadata exactly. The closure nevertheless fails its observable outcome because the Profile
does not identify the action policy or return produced by the selected next action.

## Independent verification

| Check | Result / evidence |
| --- | --- |
| Focused / six-module regression | PASS: `31/31` and `98/98` from the clean implementation worktree with bytecode disabled. |
| Strict typing | PASS: strict mypy with explicit package bases over `150` files and an external cache removed after readback. |
| Scope / ancestry / residue | PASS: exact five-file implementation, WPR-only handoff, additive ancestry, clean tracked/ignored porcelain and no repository cache residue. |
| Expected-return direction probe | **FAIL:** `INTAKE + INTAKE` selects Wayfinder but declares `ROUTER_EVENT(INTAKE)`; `router-control.md` requires the Wayfinder result (`WAYFINDER_GO` or `WAYFINDER_NO_GO`). |
| Policy identity probe | **FAIL:** every transition uses `rev-0000000000000001`, an all-zero SHA-256 digest and a synthetic `route-<stage>-<event>` ID that resolves to no current single-purpose reference. |

## Mandatory review checks

- **Clear strong types:** PASS for the data models and required non-null fields.
- **Existing conventions:** PASS for immutable strict Pydantic contracts and public exports.
- **Logic correctness:** FAIL CR-R01-001 and CR-R01-002. Input events are echoed as future
  returns, and policy identities are placeholders rather than exact versioned references.
- **Edge cases:** FAIL stop, human-wait, retry and implementation-return transitions because
  no exact transition-to-policy/return table is frozen or tested.
- **Security / performance:** PASS for absence of external effects and raw policy text, but an
  unresolvable policy reference must not be treated as executable routing authority.
- **Test coverage / smoke:** FAIL CodeReview.md class 7. The tests deliberately assert that the
  incoming event is present in the expected-return contract, so they prove the wrong direction.
- **Dependencies:** PASS. No dependency changed.
- **Specification:** FAIL AC-15 and R01's observable outcome until the exact action policy and
  next typed return are frozen per transition.

## Findings

**CR-R01-001 - `TICKET_DEFECT`, blocking.** Revision 01 froze the contract shape but omitted
the exact `(current stage, input event) -> selected policy -> expected next return` table. This
allowed an implementation to be structurally valid while semantically reversing input and
output. Revision 02 must freeze the complete existing POC transition table and state that
`RouterDecision.expected_return` describes the primary action selected by this decision, not
the event that caused the decision.

**CR-R01-002 - `IMPLEMENTATION_DEFECT`, blocking.**
`library/workflow_router/profile.py:142` derives every Router-event contract directly from the
incoming `event_kind`; `tests/test_workflow_router.py:1418` enshrines that echo. The independent
probe reproduced `INTAKE_EXPECTED_ACTUAL=('intake',)` while the authoritative Wayfinder return
is `('wayfinder_go', 'wayfinder_no_go')`. Stop/handoff must be `NO_RETURN`, human waits must
name the response event, smoke must name validation events, and an implementation retry must
name `ImplementationReturn` statuses.

**CR-R01-003 - `EVIDENCE_DEFECT`, blocking.**
`library/workflow_router/profile.py:121-138` uses one placeholder revision and an all-zero
digest for every policy, while generated IDs such as `route-intake-intake` identify no existing
single-purpose reference. The tests check only prefixes. Revision 02 must bind the exact
reference IDs and real content SHA-256 values frozen in the ticket, reject all-zero reference
metadata and reject competing metadata for one reference ID.

## Correction boundary

`CHANGES_REQUESTED`. The same ticket, owner, task, worktree, branch, allocation and valid
receipt remain in force. Revision 02 is additive from the submitted handoff and changes only
the original five implementation paths followed by one WPR-only handoff. It must close
CR-R01-001 through CR-R01-003; it does not open R02, add a policy reader/registry, change
`ArtifactRef`, touch 06G0P, create a worktree, push, package, install, release or deploy.

## Revision-02 terminal review

| Field | Value |
| --- | --- |
| Correction / handoff | `a961b59d3db60dbd74a9388621adad3112b4f721` / `21ced7b7f84a351074f65566603b4a2793334134` |
| Scope / ancestry | PASS: additive after `a16dfc3`; correction changes only `contracts.py`, `profile.py` and `test_workflow_router.py`; handoff is WPR-only; branch clean. |
| Implementer verification | PASS: focused `32/32`, six-module `99/99`, full `535/535`, strict mypy `150`, compile `150`, both revision-02 reversals and zero residue. |
| Independent semantic probe | PASS: Wayfinder GO/NO-GO, stop no-return, approval response, implementation retry statuses and all seven policy hashes match revision 02. |
| Terminal result | `CHANGES_REQUESTED / P0_TYPE_CORRECTION_REQUIRED` |

CR-R01-001 through CR-R01-003 are closed. One P0 source-type defect remains:

**CR-R01-004 - `IMPLEMENTATION_DEFECT`, blocking.** The new production
`_PolicyRoute.reference_id`, `_policy_reference_for` parameter and Profile reference-map key
use raw `str`; `_POLICY_REFERENCES` and `_POLICY_ROUTES` are unannotated module variables. The
new test oracle likewise represents policy ID, revision, digest and path as raw `str` and leaves
its route/policy constants unannotated. Strict mypy infers these shapes but does not make the
domain intent C++-readable, so the change violates the repository P0 source-type gate. The
test also spawns `git show` only to recover file bytes already available at a typed repository
path, making the evidence unnecessarily dependent on a live Git checkout.

Revision 03 is a same-ticket mechanical correction only: use the existing
`OpaqueMetadataId`, `RevisionDigest` and `EvidenceDigest` aliases, `PurePosixPath` for the test
policy path, explicit tuple/map annotations, and direct typed file-byte hashing without a Git
subprocess. The AST source gate must cover the new internal route/oracle dataclasses and module
constants. No route value, digest, public contract or behavior may change.
