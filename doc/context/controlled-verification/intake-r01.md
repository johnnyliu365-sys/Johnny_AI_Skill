# Controlled verification and responsibility-admission intake

| Field | Value |
| --- | --- |
| Artifact ID / kind | `INTAKE-CONTROLLED-VERIFICATION-20260908-01` / `CHANGE_INTAKE` |
| Revision / state | `01` / `OWNER_DECISION_REQUIRED / NOT_SEALED` |
| Requirement | [PRD/CHG-20260908-051](../../requirements/active/2026/environment-control/REQ-20260908-051.md) |
| Baseline | `b697738d009db37318ebc8762107ef8329e014db` |
| Owner | Human project owner; current reviewer records facts and proposals only. |

## Normalized intake

```json
{
  "schema_version": "1",
  "intake_mode": "delta",
  "product_kind": "control_plane",
  "goal_statement": "Execute only an approved bounded verification plan and reject ticket-declared source responsibility violations before integration, without replacing the existing Router.",
  "known_constraints": [
    "Both Codex and Claude Code require independent qualification.",
    "Same-lifetime delegation remains bridge-free and completion-wait driven.",
    "Resource controls must be proven before affected process execution.",
    "Governance and shared engine stay outside target runtime dependencies.",
    "Human owner retains unresolved architecture and policy decisions."
  ],
  "evidence_refs": ["owner-verification-request-20260908", "owner-responsibility-request-20260908"],
  "baseline_reference": "johnny-ai-skill@b697738d009db37318ebc8762107ef8329e014db",
  "delta_scope": ["approved-verification-execution", "wa-04-responsibility-admission"],
  "workload": null
}
```

This is committed intake input, not a successful Wayfinder result. Null workload cannot claim
COMPACT; effect/admission tickets require an evidence-backed assessment before dispatch.

## Readback facts and non-claims

- `library/workflow_router/router.py:RouterEngine` is a pure state/event evaluator.
  `contracts.py` already defines `ProcessStage` and `CompletionEvidence`. These are reuse points,
  not proof that a live verification executor exists.
- `modules/spec/environment-capability-bootstrap.md` EC-10 requires hard resource controls,
  positive bounded plans, no post-launch attachment race and separately approved heavy work.
  EC-15 already scopes first-version production adapters to Windows x64; no new Linux/macOS
  host support promise is needed to begin this work.
- `modules/spec/workflow-adoption-activation.md` names WA-04: ticket-bound responsibility
  contracts plus one Python admission adapter. Its ticket registry has no WA-04 leaf.
  WA-02's target-effect blocker is not evidence that the read-only WA-04 validator needs a
  runner or host-write gateway.
- Targeted symbol/path searches found no `ResourceEnforcerPort`, Job Object implementation or
  `ResponsibilityBoundaryAdmissionPort` in current library/test Python sources. Do not treat
  planning requirements as delivered capabilities. A broader alias audit may refine this fact.
- Main is locally ahead of the directly observed remote main. This proposal stays on its own
  branch; it does not push the thirteen pre-existing local commits or claim remote equality.
- The external incident diagnosis is owner-supplied, not independently reproduced here.
  Empty transcript files cannot alone prove no work happened; wall time minus synchronous
  tool waits cannot isolate model compute when background work overlaps.

## Proposed execution responsibility map

| Component | Owns | Must not own |
| --- | --- | --- |
| Thin skill/CLI | Exact identifiers and human-readable result presentation | Choose run counts, approve plans, invent evidence or own workflow transitions |
| Plan admission | Resolve approved source and compare exact candidate/policy/plan bindings | Spawn processes or accept caller-minted approval |
| Verification coordinator | Ordered finite run/retry policy and one terminal result | OS primitives, review verdict, Git integration or model polling |
| Resource/process adapter | Proven caps before work, bounded wait and exact process-tree cleanup | Change acceptance rules, approve its own capability or kill foreign work |
| Evidence adapter | Actual attempt outcomes, expected-check matching, bounded evidence identity | Convert unknown/unrun checks into PASS or discard failed attempts |
| Existing Router/integration composition | Admit the next existing transition after required evidence and review | Reimplement the test runner or treat verification success as review approval |
| Existing WA-04 language adapter | Source facts under the approved responsibility/dependency contract | Infer a new contract from the candidate or claim universal semantic understanding |

These are proposed responsibility boundaries, not a frozen DTO or a new parallel state machine.
Layering follows the existing direction: domain rules and typed ports inward, language/OS/I/O
adapters outward, concrete construction in one bounded Composition Root. Separate test files
follow observable responsibilities. Splitting a file without changing coupling is not acceptance.

## Proposed implementation order after convergence

1. Compile the existing WA-04 scope into a separately approved ticket with a bounded Python
   language contract and reverse-mutation fixtures. Validate source facts, not file names alone.
2. Freeze the verification plan/admission contract and candidate/evidence binding. Reuse the
   existing Router conventions without adding the feature wholesale to its large central files.
3. Prove the selected Windows execution/resource/cleanup capability on a disposable fixture.
   An unavailable required cap must remain a refusal; no real target load or busy-loop stress.
4. Compose one real bounded verify action and its exact evidence adapter, then test the path
   from CLI request through result admission. Isolated unit seams alone cannot close this step.
5. Perform adversarial review and separate Codex/Claude installed qualification under a later
   exact release authority. Readiness is not publication or automatic target adoption.

No item above is an implementation ticket or a dispatch. The reviewer must not invent frozen
contracts while assigning it. A missing execution capability blocks its dependent work only.

## Owner decision D1: what does the size requirement forbid?

Source: the owner requests enforced responsibility separation and no oversized 1000-plus-line
coupled files. Accepted ADR-036 consequences and SPEC AC-4 explicitly prohibit a generic size
gate and require that a large cohesive module not fail merely for length.

- **A — responsibility gate (recommended):** preserve that accepted rule. Reject mixed declared
  responsibilities, forbidden dependency direction, out-of-root concrete construction and missing
  test seams regardless of line count. Do not accept a mechanically split coupled candidate.
  Size is a review signal, not standalone authority to reject a cohesive module.
- **B — responsibility gate plus an absolute size ceiling:** add a new owner-approved policy
  overriding the relevant ADR/SPEC clauses. Before freezing, define what is counted, generated
  source treatment, existing oversized-file treatment and who can approve exceptions. An
  implementer cannot self-exempt or satisfy this by arbitrary slicing.

Decision is not inferred. No ADR/SPEC/skill body has been changed, and no new numerical threshold
has been frozen. This is the first owner interpretation question, not a request to approve a
finished implementation. The verification requirement does not become a source dispatch before
its own contracts and capability dependencies are frozen.

## Completion and continuation

`ACTION_COMPLETED` covers only indexed intake/discovery documentation.
Next: `WAIT_FOR_HUMAN / OWNER_POLICY_DECISION_REQUIRED` for D1, then resume scoped convergence.
The named reason is this intake's explanatory label, not a newly implemented Router enum.
No source, tests, skills, package, target, provider or release effect is claimed.
