# UIX-02 | Reference-renderer evidence admission

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-PLUGIN-ADOPTION-QUALITY-UIX-02` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-JOHNNY-DESIGNERLESS-UI-CODESIGN-20260829-01` / AC-1, AC-2 and the renderer/evidence portion of AC-8 |
| Requirement / Context / ADR | `PRD-20260829-049` / `CHG-20260829-049` / `CTX-PLUGIN-ADOPTION-QUALITY-20260829-02` Revision 01, SHA-256 `dd776e27777b7a4679ce8573c05639e7d7ab24481e654cf431da45c81fb99a26` / `ADR-20260829-037` |
| State / closure | `OPEN / APPROVAL_REQUIRED / NON_DISPATCHABLE`; `CLOSURE-PLUGIN-ADOPTION-QUALITY-UIX-02`, revision 01 |
| Document revision | `01` |
| Opening authority | Project owner, 2026-08-31 (Asia/Taipei): authorized opening UIX-02 after UIX-01 closure. Exact ticket approval and implementation dispatch remain separate; no renderer, browser, provider, target write, publication, installation, release or deployment effect is granted. |
| Source baseline / dependency | `1d2be10e8de224909b2c46a4eb6f8ef63eb7265c`; UIX-01 contracts integrated at `2c7b5adafa0a84f7a4219e4287daea38d8d855a5`. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh after exact approval; `READY_LOW_MODEL`, one synchronous owner lane and no helper. Reviewer strength remains higher than the implementation owner. |
| Worktree / branch / task | After exact ticket approval, reviewer allocates `.worktrees/plugin-adoption-quality-uix-02` on `implement/plugin-adoption-quality-uix-02` from the then-current committed `main`, binds that exact baseline and reuses one existing Luna/xhigh implementation task. Same-lifetime dispatch uses one native call and one wait; no runner, queue, receipt, descriptor, gateway or host workspace readback. |
| Delivery / language | `POC / STANDARD`; Python 3.11, strict Pydantic models, complete annotations, `mypy --strict`, deterministic pure tests and independent review. |
| XSS / effects | `XSS_NOT_APPLICABLE`. This closure admits opaque evidence metadata only. It performs no Browser/WebView/DOM/JavaScript sink, renderer/provider call, filesystem write or target mutation. A later concrete renderer/target adapter must receive separate authority and XSS classification from its actual source/sink graph. |

## Boundary declaration

```johnny-boundary
create = library/workflow_router/ui_reference_renderer_admission.py
modify = library/workflow_router/ui_reference_renderer_admission.py
create = tests/test_ui_reference_renderer_admission.py
modify = tests/test_ui_reference_renderer_admission.py
create = modules/element/python/plugin-adoption-quality/uix-02-reference-renderer-evidence-admission/
modify = modules/element/python/plugin-adoption-quality/uix-02-reference-renderer-evidence-admission/
forbid = library/workflow_router/ui_codesign_contracts.py
forbid = library/workflow_router/__init__.py
forbid = library/workflow_router/contracts.py
forbid = library/local_orchestration/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Create one private, strict, effect-free module with one public entry inside that module:

```python
admit_reference_renderer(
    request: ReferenceRendererAdmissionRequest,
) -> ReferenceRendererAdmissionDecision
```

The request binds an opaque request ref, exact UIX-01 brief ID and approved-content digest,
`RendererCapabilityState`, `RendererTarget`, actual target, requested renderer state and one tagged
evidence variant. No raw file path, URL, provider payload, prompt, credential, markup or screenshot
bytes enter the model.

```text
RendererCapabilityState = AVAILABLE_AUTHORIZED | AVAILABLE_NOT_AUTHORIZED
                        | UNAVAILABLE | DECLINED
RendererTarget = DOM | NATIVE_ENGINE | NATIVE_MOBILE | TERMINAL | ANY

RenderedReferenceEvidence = {
  kind=RENDERED_AVAILABLE,
  desktop_screenshot_ref,
  mobile_screenshot_ref,
  desktop_digest,
  mobile_digest,
  renderer_observation_ref
}

ArtifactReferenceEvidence = {
  kind=ARTIFACT_ONLY,
  desktop_artifact_ref,
  mobile_artifact_ref,
  artifact_set_digest,
  owner_manual_open_acknowledgement=true
}

UnavailableReferenceEvidence = { kind=UNAVAILABLE }
```

The decision is exactly one tagged variant without action-dependent nullable fields:

```text
ADMITTED_RENDERED(evidence, renderer_state=RENDERED_AVAILABLE)
ADMITTED_ARTIFACT(evidence, renderer_state=ARTIFACT_ONLY)
WAIT(DESIGN_CAPABILITY_AUTHORITY_REQUIRED | UI_REFERENCE_RENDERER_REQUIRED)
REFUSED(TARGET_MISMATCH | STATE_EVIDENCE_MISMATCH | CONTENT_BINDING_MISMATCH
        | DUPLICATE_EVIDENCE | INPUT_INVALID)
```

`AVAILABLE_AUTHORIZED` may admit rendered evidence only when the declared renderer target matches
the actual target or is `ANY`. `AVAILABLE_NOT_AUTHORIZED` returns the authority wait before any
evidence is admitted. `UNAVAILABLE` or `DECLINED` may admit only `ARTIFACT_ONLY` evidence carrying
target-owned opaque refs plus literal manual-open acknowledgement; without that evidence it returns
`UI_REFERENCE_RENDERER_REQUIRED`. Capability absence is not an installation error and is never
silently promoted to rendered availability.

The admitted result carries the exact content digest and evidence identity needed to create the
matching UIX-01 `ProduceDirectionsEvent`; it neither constructs direction aesthetics nor mutates
the UI lifecycle. UIX-03 consumes this result when producing the zero-external-design-tool flow.

## Frozen responsibility and evidence rules

- Renderer capability, design-craft capability and design source remain three separate states.
- `REGIME` design-craft output may inform later direction proposals, but this ticket admits only
  reference-renderer evidence. It grants no Figma/image/craft provider effect or review authority.
- Screenshot evidence requires both desktop and mobile opaque refs plus their lowercase SHA-256
  digests and an independent renderer observation ref. Artifact fallback requires both comparable
  target-owned refs, one set digest and literal owner manual-open acknowledgement.
- Target mismatch rejects artifact-tier evidence. No DOM artifact is presented as a native-engine
  artifact merely because its design regime is portable.
- Evidence refs and digests must be unique and bound to the same request/content identity. Caller
  labels, manifest text and requested state cannot prove availability.
- No output means a screenshot was visually approved. Visual review and owner acceptance remain
  UIX-05/UIX-01 lifecycle responsibilities.

### Reusable-module selection record

```text
selected: workflow-router-poc@1d2be10e8de224909b2c46a4eb6f8ef63eb7265c
why: strict immutable RouterModel and UIX-01 discriminated evidence/lifecycle conventions match.
read: MODULE_CATALOG -> workflow-control index -> workflow_router/README -> public __init__;
      same-repository private dependency ui_codesign_contracts.py by exact ticket reference.
dependency: UIX-01 candidate 2c7b5adafa0a84f7a4219e4287daea38d8d855a5.
gap: catalog has no delivered renderer adapter; this ticket admits evidence and invents no effect.
rejected: Browser/Figma/image/provider and filesystem adapters; they are outside this closure.
boundary: no renderer invocation, target artifact write, screenshot capture or visual conclusion.
```

`TicketDecompositionDecision = READY_LOW_MODEL`: one pure admission transition, one implementation
owner, one private module, a finite result algebra and no unresolved design or external effect.

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| UIR1 | Every enum/request/evidence/decision variant ordinary-constructs, strict-validates and JSON-round-trips. Empty/whitespace IDs, wrong primitives, extra fields, `None`, malformed digests, raw paths/URLs/credentials/prompts and contradictory variants reject. Unicode bounded metadata round-trips without normalization. |
| UIR2 | `AVAILABLE_AUTHORIZED` plus matching target and complete desktop/mobile rendered evidence returns only `ADMITTED_RENDERED`; missing one ref/digest, duplicate refs or mismatched evidence kind refuses. |
| UIR3 | `AVAILABLE_NOT_AUTHORIZED` returns only `DESIGN_CAPABILITY_AUTHORITY_REQUIRED` and does not admit caller-supplied evidence. |
| UIR4 | `UNAVAILABLE` and `DECLINED` plus complete target-owned artifact evidence and literal manual-open acknowledgement return only `ADMITTED_ARTIFACT`; without it they return `UI_REFERENCE_RENDERER_REQUIRED`. |
| UIR5 | Renderer-target mismatch returns `TARGET_MISMATCH`. `ANY` matches every finite actual target; a DOM-only renderer cannot produce native-engine/mobile/terminal artifact evidence. |
| UIR6 | Approved-content or request identity mismatch, duplicate evidence and state/evidence cross-pairs return the named refusal without an admitted result. |
| UIR7 | AST/source checks prove one reducer entry, tagged no-null variants, private-module boundary and absence of filesystem/browser/DOM execution/Figma/image/provider/network/process/environment/Git/importlib/dynamic lookup/`Any`/`cast`/raw-mapping effects. |
| UIRM1 | Reverse-mutate `AVAILABLE_NOT_AUTHORIZED` to admit rendered evidence; UIR3 turns red, then exact restoration returns green. |
| UIRM2 | Reverse-mutate target matching to accept every target; UIR5 turns red, then exact restoration returns green. |
| UIRM3 | Reverse-mutate artifact fallback to omit manual acknowledgement; UIR4 turns red, then exact restoration returns green. |

Strong-type preflight constructs every success/wait/refusal variant through ordinary public
validators and round-trips. Negative bypass values are rejection evidence only. No ceremonial
baseline-red claim is accepted. The authentic first-red slot is the focused test command after the
test file defines UIR1–UIR7 but before the source module exists; it must fail for the missing
`ui_reference_renderer_admission` entry point, then turn green only after production source is
implemented.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_reference_renderer_admission.py
py -3.11 -B -m pytest -q -p no:cacheprovider tests/test_ui_codesign_contracts.py tests/test_workflow_router.py
py -3.11 -B -m mypy --strict --no-incremental library/workflow_router/ui_reference_renderer_admission.py tests/test_ui_reference_renderer_admission.py
py -3.11 -B -m compileall -q library/workflow_router/ui_reference_renderer_admission.py tests/test_ui_reference_renderer_admission.py
git diff --check 1d2be10e8de224909b2c46a4eb6f8ef63eb7265c HEAD
git status --short
```

The Terra/xhigh reviewer validates the exact ticket/baseline/boundary, strict variant construction,
capability/target/evidence truth table, absence of effects and UIX-01 compatibility. It reruns the
focused/regression/type/compile gates and performs one independent counter-mutation not selected by
the implementation owner.

## Ownership and return

Exact approval of this ticket permits the reviewer to allocate one repository-contained worktree
and reuse the existing Luna/xhigh implementation owner through one same-lifetime dispatch and one
completion wait. The owner modifies only declared source/test/element paths, does not commit or
push, and cannot invoke a renderer/provider or change UIX-01, SPEC, Context, ticket or skills.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with UIR/UIRM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or
`CHANGE_DETECTED -> REQUIREMENT_CHANGED`. No return authorizes rendering, target mutation,
integration, push, publication, installation, release or deployment.
