# Controlled verification and responsibility-admission intake

| Field | Value |
| --- | --- |
| Artifact ID / kind | `INTAKE-CONTROLLED-VERIFICATION-20260908-01` / `CHANGE_INTAKE` |
| Revision / state | `03` / `OWNER_SCOPE_APPROVED / CAPABILITY_INVESTIGATION / NOT_SEALED` |
| Requirement | [PRD/CHG-20260908-051](../../requirements/active/2026/environment-control/REQ-20260908-051.md) |
| Scoped technical finding | [Enforcement boundary and refusal matrix](enforcement-boundary-r01.md) |
| Baseline | `b697738d009db37318ebc8762107ef8329e014db` |
| Owner | Human project owner; current reviewer records facts and proposals only. |

## Normalized intake

```json
{
  "schema_version": "1",
  "intake_mode": "delta",
  "product_kind": "control_plane",
  "goal_statement": "Enforce exact approved verification execution, owned process lifetime and restart reconciliation, and reject ticket-declared source responsibility violations through automatically active qualified controls rather than model memory, without replacing the existing Router.",
  "known_constraints": [
    "Both Codex and Claude Code require independent qualification.",
    "Same-lifetime delegation remains bridge-free and completion-wait driven.",
    "Resource controls must be proven before affected process execution.",
    "Governance and shared engine stay outside target runtime dependencies.",
    "Human owner retains unresolved architecture and policy decisions.",
    "Responsibility and dependency checks are mandatory; generic line-count ceilings are excluded.",
    "Hook presence or model reminders alone cannot establish bypass-resistant enforcement.",
    "Owner-approved restrictions apply only to explicitly enrolled Johnny sessions and worktrees; unrelated projects and human terminals remain unchanged."
  ],
  "evidence_refs": ["owner-verification-request-20260908", "owner-responsibility-request-20260908", "owner-mandatory-enforcement-20260908", "owner-restricted-lane-approval-20260908"],
  "baseline_reference": "johnny-ai-skill@b697738d009db37318ebc8762107ef8329e014db",
  "delta_scope": ["approved-verification-execution", "wa-04-responsibility-admission", "owned-execution-recovery", "automatic-host-enforcement"],
  "workload": {
    "change_surface": "cross_boundary",
    "uncertainty": "novel",
    "recovery": "recoverable",
    "security_surface": "privileged",
    "external_effects": "local_host",
    "evidence_refs": ["enforcement-boundary-convergence-20260908", "owner-restricted-lane-approval-20260908"]
  }
}
```

This is committed intake input, not a successful Wayfinder result. The existing typed intensity
derivation yields HIGH_ASSURANCE: the requested effect crosses host/process/authority boundaries,
the complete-mediation mechanism is unqualified, and permission isolation is privileged. Recovery
must preserve an owner recovery path. Current activity is DOCS_ONLY plus read-only investigation;
it does not exercise the future local-host effect or downgrade its required assurance.

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
| Recovery/reconciliation | Attempt identity, terminal evidence and proven process ownership | Trust stale host UI as live execution, duplicate completed work or invent a success |
| Host adapter | Automatic entry registration and qualified pre-effect interception | Rewrite rejected commands, supply policy authority or claim unobserved tool paths are protected |
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

## Owner decision D1: answered, do not ask again

On 2026-09-08 the owner clarified that the requirement rejects coupling and mixed responsibilities,
not file length. Preserve the accepted responsibility-only rule. Do not introduce a numerical
ceiling or accept a mechanically split coupled candidate. The owner also explicitly requires
script-enforced plan integrity, process lifetime, reconciliation and automatic activation.
These answers are now recorded in the normalized intake and REQ-051 revision 02.

## Owner decision D2: answered, do not ask again

The [scoped finding](enforcement-boundary-r01.md) identifies documented bypasses and distinguishes
actual CLI feature availability from installed enforcement. A hook-only solution cannot satisfy
the requested hard guarantee while unrestricted alternate execution and policy mutation remain.
The owner accepted the explicitly enrolled Johnny session/worktree restriction after proposal
`6a093821592b1f007a570cd13eb9feeadf5b30aa`; the exact scope acceptance is recorded in REQ-051
revision 03. Continue qualification without another D2 prompt. Acceptance does not prove the
mechanism, authorize an unspecified service/account installation or affect unrelated projects.
No admin settings, host configuration or target files are modified by recording this decision.

## Completion and continuation

`ACTION_COMPLETED` covers only indexed intake/discovery documentation.
`OWNER_INPUT_PROVIDED` records D2 and resumes the bounded DELTA feasibility/capability action.
No wait remains for D1 or D2. A capability finding is not implementation dispatch authority.
No source, tests, skills, package, target, provider or release effect is claimed.
