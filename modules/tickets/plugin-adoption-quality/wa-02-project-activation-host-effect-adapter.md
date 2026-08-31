# WA-02 | Project activation host-effect adapter and detach/readback contract

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-PLUGIN-ADOPTION-QUALITY-WA-02` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-JOHNNY-WORKFLOW-ADOPTION-20260829-01` / AC-1, AC-2 and AC-8 |
| Requirement / Context / ADR | `PRD-20260829-048` / `CHG-20260829-048` / `CTX-PLUGIN-ADOPTION-QUALITY-20260829-01` Revision 01, SHA-256 `23cb8df55a9cf69730e7bff6303af1705dc7b479c1bd1a72e033ac6fed2bdd9e` / `ADR-20260829-036` |
| State / closure | `OPEN / CAPABILITY_BLOCKED / NON_DISPATCHABLE`; `CLOSURE-PLUGIN-ADOPTION-QUALITY-WA-02`, revision 01 |
| Document revision | `01` |
| Opening authority | Project owner, 2026-08-31 (Asia/Taipei): authorized opening WA-02 after WA-01 closure. This records the exact blocked implementation contract; it grants no ticket approval, dispatch, target mutation, host hook, external-effect grant, publication, installation, release or deployment effect. |
| Source baseline / dependency | `1d2be10e8de224909b2c46a4eb6f8ef63eb7265c`; WA-01 contracts integrated at `685ad93471b719a9abaf19da46b0c797a5af536a`. Runtime admission additionally requires an independently protected `HostExternalEffectGatewayCapability=AVAILABLE`; no such qualified capability is currently committed. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh for this decomposition record. Any later implementation revision must assign a reviewer whose capability is not lower than its implementation owner. |
| Implementation owner | Unassigned. `UPSTREAM_DECISION_REQUIRED / HIGH_ASSURANCE_REQUIRED`; no implementation lane may exist while the host external-effect gateway is unproved. |
| Worktree / branch / task | None may be allocated while blocked. A later approved dispatchable revision must name one repository-contained `.worktrees/plugin-adoption-quality-wa-02`, branch `implement/plugin-adoption-quality-wa-02`, exact then-current baseline and one same-lifetime owner task; no runner, queue, receipt, descriptor or bridge applies to that direct lane. |
| Delivery / language | `POC / HIGH_ASSURANCE`; Python 3.11 strict typed boundary, ordinary validation, real disposable target fixtures only after capability admission. |
| XSS / effects | `XSS_NOT_APPLICABLE`. Target instruction and Claude hook/config mutation are privileged filesystem/host effects. Plugin/CLI claims are untrusted; the runtime must revalidate every invariant and consume one independently protected, plan-bound, one-shot grant. |

## Proposed boundary after capability admission

```johnny-boundary
create = library/local_orchestration/project_adoption_effect_adapter.py
modify = library/local_orchestration/project_adoption_effect_adapter.py
create = tests/test_project_adoption_effect_adapter.py
modify = tests/test_project_adoption_effect_adapter.py
create = modules/element/python/plugin-adoption-quality/wa-02-project-activation-host-effect-adapter/
modify = modules/element/python/plugin-adoption-quality/wa-02-project-activation-host-effect-adapter/
forbid = library/workflow_router/project_adoption_contracts.py
forbid = library/local_orchestration/target_document_management.py
forbid = library/workflow_router/__init__.py
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

This boundary is frozen for planning only and is not writable until an approved dispatchable
revision exists. The legacy `TransactionalTargetDocumentWriter` is explicitly outside the
boundary: digest-check followed by `os.replace`, `rename` or `unlink` has a TOCTOU window and does
not prove the retained atomic-conditional-replace invariant.

## Observable closure held behind the capability gate

After the upstream capability is proved and this ticket receives a separately approved revision,
create one strict entry point:

```python
execute_project_adoption_effect(
    request: ProjectAdoptionEffectRequest,
    gateway: HostExternalEffectGatewayPort,
) -> ProjectAdoptionEffectResult
```

The request is a discriminated union with no action-dependent nullable fields:

```text
CODEX_INSTRUCTION(plan, target_document_ref, expected_baseline, grant_ref)
CLAUDE_INSTRUCTION(plan, target_document_ref, expected_baseline, grant_ref)
CLAUDE_INSTRUCTION_WITH_HOOK(plan, hook_bundle, expected_baseline, grant_ref)
DETACH_NO_TARGET_MUTATION(installed_identity, observed_target_refs)
```

The effect variants consume the exact WA-01 `ProjectActivationPlan`, canonical repository and host
identity, expected current/post digests, a finite immutable operation plan, one opaque grant ref
bound to that plan and one independently qualified gateway capability ref. The runtime revalidates
host/instruction pairing, path identity, baseline, grant binding, pre-state and proposed post-state
before any effect. The gateway owns reservation, one-shot consumption, atomic conditional mutation,
bounded rollback/recovery evidence and exact readback. The adapter cannot issue grants or derive
`HOST_GATE_ENFORCED` from a plan, instruction, manifest or caller claim.

Results are tagged and finite:

```text
APPLIED(post_digest, terminal_evidence_ref, observed_behavior_gate_state)
NO_CHANGE(verified_digest, terminal_evidence_ref, observed_behavior_gate_state)
DETACHED_NO_TARGET_MUTATION(observed_target_refs)
REFUSED(STALE_PRESTATE | HOST_KIND_MISMATCH | PLAN_BINDING_MISMATCH
        | GRANT_INVALID | GRANT_EXPIRED | GRANT_REPLAY_DETECTED
        | READBACK_MISMATCH | RECOVERY_REQUIRED)
UNAVAILABLE(HOST_EXTERNAL_EFFECT_GRANT_UNAVAILABLE)
```

`RECOVERY_REQUIRED` is fail-closed: it carries one opaque recovery-evidence ref, makes every later
operation return without target effect, and clears only through separately authorized recovery.
Detach never deletes or rewrites target-owned instructions, hooks, settings or application source;
forward removal/update is a distinct owner-approved target operation.

## Frozen responsibility and safety rules

- Codex accepts only `CODEX_AGENTS`; Claude accepts only `CLAUDE_PROJECT_INSTRUCTION`.
- Claude hook/config operations are a single finite plan and remain target-owned/self-contained.
  They may not import plugin cache, Johnny runtime, user-home scripts or credentials.
- Shorthand path/name resolution is forbidden. Canonical namespace/name must be exact; shorthand
  is accepted only when it resolves uniquely, and ambiguity is a named refusal rather than
  first-match-wins.
- A caller cannot supply success evidence. The gateway readback must independently bind target,
  baseline, plan digest, consumed grant, post-digests and observed gate state.
- Rollback failure performs only the approved finite retries, persists recovery evidence, returns
  `RECOVERY_REQUIRED` and prohibits continuation.
- Tests may use strict fakes to validate orchestration but cannot promote fake success into
  capability evidence. Production admission requires the separately qualified host primitive.

### Reusable-module selection record

```text
selected: workflow-router-poc@1d2be10e8de224909b2c46a4eb6f8ef63eb7265c
why: strict immutable contracts, WA-01 activation plans and finite host-state conventions match.
read: MODULE_CATALOG -> workflow-control index -> workflow_router/README -> public __init__;
      same-repository private dependency project_adoption_contracts.py by exact ticket reference.
dependency: WA-01 candidate 685ad93471b719a9abaf19da46b0c797a5af536a.
gap: no delivered catalog card or committed AVAILABLE host external-effect gateway exists.
rejected: target_document_management.py; check-then-replace cannot satisfy the retained invariant.
boundary: no target effect, hook installation or dispatch until upstream capability admission.
```

## Deferred TDD closure

The following cells are frozen but cannot serve as implementation authority until the capability
blocker is closed and an exact ticket revision is owner-approved:

| Cell | Required executable behavior / named result |
| --- | --- |
| WAE1 | Every request/result/grant/gateway DTO ordinary-constructs, strict-validates and JSON-round-trips; `None`, extra fields, wrong primitives, raw paths/URIs/secrets and contradictory variants reject. |
| WAE2 | Codex and Claude instruction plans apply only with exact host pairing, baseline, plan digest and reserved grant; readback must match every proposed post-digest. |
| WAE3 | Claude hook bundle remains finite, target-owned and self-contained; stale/disabled/bypassed/readback-mismatched hooks never report `HOST_GATE_ENFORCED`. |
| WAE4 | Missing, forged, expired, replayed or plan-mismatched grant returns the named refusal with zero target effects. |
| WAE5 | Forced partial failure fails closed; bounded rollback either proves restoration or records `RECOVERY_REQUIRED`, after which a second request performs zero effects. |
| WAE6 | Detach returns `DETACHED_NO_TARGET_MUTATION` and leaves every target file byte-identical. |
| WAE7 | Runtime revalidates invariants even when plugin/CLI input claims success; resolver ambiguity rejects without first-match selection. |
| WAE8 | Source/AST checks prove no grant issuance, fallback writer, plugin-cache dependency, plaintext secret, repository integration, provider, dispatch or publication effect. |
| WAEM1 | Reverse-mutate grant replay rejection; WAE4 turns red, then exact restoration returns green. |
| WAEM2 | Reverse-mutate readback comparison; WAE2 turns red, then exact restoration returns green. |
| WAEM3 | Reverse-mutate rollback failure to continue; WAE5 turns red, then exact restoration returns green. |

The authentic first-red slot is intentionally unexecuted while the ticket is blocked. A later
dispatchable revision must require tests to be committed in the candidate worktree before source
and must record the direct focused command failing for the missing adapter entry point; a fabricated
red from the unavailable gateway is not TDD evidence.

## Admission decision and return

`TicketDecompositionDecision = UPSTREAM_DECISION_REQUIRED` with blocker
`HOST_EXTERNAL_EFFECT_GATEWAY_UNPROVEN`. Opening this leaf is `ACTION_COMPLETED`; it is not an
implementation dispatch. The only legal next event is an approved upstream capability result and
architecture/ticket revision. Until then, any implementation request returns
`HALT / CAPABILITY_UNAVAILABLE` before source, filesystem, Agent or host effect.
