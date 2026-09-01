# UIX-02 | Reference-renderer evidence admission

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-PLUGIN-ADOPTION-QUALITY-UIX-02` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-JOHNNY-DESIGNERLESS-UI-CODESIGN-20260829-01` / AC-1, AC-2 and the renderer/evidence portion of AC-8 |
| Requirement / Context / ADR | `PRD-20260829-049` / `CHG-20260829-049` / `CTX-PLUGIN-ADOPTION-QUALITY-20260829-02` Revision 01, SHA-256 `dd776e27777b7a4679ce8573c05639e7d7ab24481e654cf431da45c81fb99a26` / `ADR-20260829-037` |
| State / closure | `CLOSURE_REVISION_03_APPROVED / NON_DISPATCHABLE`; `CLOSURE-PLUGIN-ADOPTION-QUALITY-UIX-02`, revision 03 |
| Document revision | `09` |
| Opening authority | Project owner, 2026-08-31 (Asia/Taipei): authorized opening UIX-02 after UIX-01 closure. Exact ticket approval and implementation dispatch remain separate; no renderer, browser, provider, target write, publication, installation, release or deployment effect is granted. |
| Approval authority | Project owner, 2026-08-31 (Asia/Taipei): approved exact ticket candidate/authority commit `4f501ccc4f4ecf943fd3f0f6be89871b7341a4ac`, leaf SHA-256 `22c3d12fd150ffc32273722510a4c725f670d45eb2c9135cca44c9a223cbfd45`. This authorizes one UIX-02 Luna/xhigh same-lifetime implementation lane after this approval writeback; review, integration, push and every external effect remain separate. |
| Review outcome | Candidate `faf3d05e07f83a8c7804313b4d3435d01da338b0` is not integrated. Independent audit and reviewer reproduction proved that revision-01 evidence variants cannot express the request/content binding required by UIR6; changing that public ticket contract requires an owner-approved closure revision. Additional frozen-contract findings are recorded in `REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02` revision 01. |
| Closure revision 02 proposal | Reviewer, 2026-08-31 (Asia/Taipei): proposes the exact evidence binding, truth-table, Unicode and canonical-field corrections below. This proposal is not approval and authorizes no correction dispatch or effect. |
| Closure revision 02 approval | Project owner, 2026-08-31 (Asia/Taipei): approved exact candidate `79414732c9123e9ba4bac7c5bdc625d1f16217d3`, ticket SHA-256 `f43b516b4c5589c36e5ffa093759726e9e0e8c8538367e695d9d4ff524a31d9b`. This authorizes one additive correction in the existing Luna/xhigh owner lane after this approval writeback; review, integration, push and every external effect remain separate. |
| Closure revision 02 initial review | Candidate `611959f69df9bb639509d7e9068e86fb8b3e4564` is not integrated. `REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02` revision 02 records one UIR1 unsafe-value implementation defect and one candidate-baseline evidence defect. The same owner may receive the closure's single additive correction; a second failure requires `CONVERGENCE_REVIEW_REQUIRED`. |
| Closure revision 02 correction review | Candidate `07edaff11bfe981987288a9c1b6becb67c4e69ad` is not integrated. The reviewer independently reproduced remaining credential/prompt bypasses and the absence of reproducible named baseline-red evidence. The one permitted correction is exhausted; no third correction may dispatch without control-plane convergence and a new owner-approved closure. |
| Closure revision 03 proposal history | At proposal time this awaited exact owner approval. Project owner authorized control-plane drafting on 2026-09-01 (Asia/Taipei), not approval. The later approval is recorded separately below. |
| Closure revision 03 approval | Project owner, 2026-09-01 (Asia/Taipei): approved exact document revision 08 at candidate authority commit `a616e561423fd40508dfbebcb33b798e071b5462`, LF-normalized leaf SHA-256 `7b35f9f80d5616e6e5d9ff8a83817e937d1c5094e3bb4cfa042a75af08aef953`. This activates closure revision 03 only. Implementation dispatch, a third correction, candidate integration, push, publication, target effect and provider effect remain separate and unauthorized. |
| Source baseline / dependency | `1d2be10e8de224909b2c46a4eb6f8ef63eb7265c`; UIX-01 contracts integrated at `2c7b5adafa0a84f7a4219e4287daea38d8d855a5`. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | If separately authorized later, `implementation-standard` semantic profile — Luna/xhigh; `READY_LOW_MODEL`, one synchronous owner lane and no helper. No implementation owner is allocated by this approval. Reviewer strength remains higher than the implementation owner. |
| Worktree / branch / task | No owner/worktree/task allocation is active. `.worktrees/plugin-adoption-quality-uix-02`, branch `implement/plugin-adoption-quality-uix-02` and candidate `07edaff11bfe981987288a9c1b6becb67c4e69ad` remain preserved evidence and must not move under this approval. Any later same-lifetime dispatch requires separate exact authority. |
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

ReferenceEvidenceBinding = {
  request_ref,
  brief_id,
  approved_content_digest
}

RenderedReferenceEvidence = {
  kind=RENDERED_AVAILABLE,
  binding: ReferenceEvidenceBinding,
  desktop_screenshot_ref,
  mobile_screenshot_ref,
  desktop_digest,
  mobile_digest,
  renderer_observation_ref
}

ArtifactReferenceEvidence = {
  kind=ARTIFACT_ONLY,
  binding: ReferenceEvidenceBinding,
  desktop_artifact_ref,
  mobile_artifact_ref,
  artifact_set_digest,
  owner_manual_open_acknowledgement=true
}

UnavailableReferenceEvidence = {
  kind=UNAVAILABLE,
  binding: ReferenceEvidenceBinding
}
```

The decision is exactly one tagged variant without action-dependent nullable fields:

```text
ADMITTED_RENDERED(evidence, renderer_state=RENDERED_AVAILABLE)
ADMITTED_ARTIFACT(evidence, renderer_state=ARTIFACT_ONLY)
WAIT(DESIGN_CAPABILITY_AUTHORITY_REQUIRED | UI_REFERENCE_RENDERER_REQUIRED)
REFUSED(TARGET_MISMATCH | STATE_EVIDENCE_MISMATCH | CONTENT_BINDING_MISMATCH
        | DUPLICATE_EVIDENCE)
```

Strict request/evidence construction rejects invalid input before the reducer; invalid dynamic
input is never converted into a caller-selectable `INPUT_INVALID` decision. The reducer order is
fixed: `AVAILABLE_NOT_AUTHORIZED` first returns the authority wait without admitting evidence;
otherwise compare the evidence binding with the outer request, reject duplicates, apply target
matching to rendered or artifact evidence, then apply the capability/state/evidence truth table.

`AVAILABLE_AUTHORIZED` admits only matching-target `RENDERED_AVAILABLE` evidence; artifact or
unavailable state/evidence returns `STATE_EVIDENCE_MISMATCH`. `UNAVAILABLE` or `DECLINED` admits
only matching-target `ARTIFACT_ONLY` evidence carrying target-owned opaque refs plus literal
manual-open acknowledgement; without complete artifact evidence it returns
`UI_REFERENCE_RENDERER_REQUIRED`. `AVAILABLE_NOT_AUTHORIZED` always returns
`DESIGN_CAPABILITY_AUTHORITY_REQUIRED` before evidence admission. Capability absence is not an
installation error and is never silently promoted to rendered availability.

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
- Every evidence variant carries one strict `ReferenceEvidenceBinding`; its request ref, brief ID
  and approved-content digest must byte-match the outer request or return
  `CONTENT_BINDING_MISMATCH`. Evidence refs and digests must be unique. This binding closes
  consistency and replay across different requests; it does not by itself prove renderer
  availability. Caller labels, manifest text and requested state cannot prove availability.
- Opaque identifiers contain 3 through 128 Unicode code points and accept only code points whose
  Unicode General Category begins with `L`, `M` or `N`. Every whitespace, separator, punctuation,
  symbol, `Cc` or `Cf` code point rejects, including zero-width and bidirectional controls. The
  gate rejects rather than transforms: no normalization, case-folding, trimming, escaping or
  replacement occurs, and admitted code points are preserved exactly. This grammar does not claim
  to distinguish encoded secret material from a legitimate opaque reference; callers remain
  responsible for keeping secrets out of refs. Only canonical field names are accepted and
  validation aliases are forbidden.
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
| UIR1 | Every enum/binding/request/evidence/decision variant ordinary-constructs, strict-validates and JSON-round-trips. Identifiers accept exactly 3–128 code points from Unicode General Categories `L*`, `M*` and `N*`; every other category rejects without transformation. Empty/whitespace/control/format/overlength IDs, wrong primitives, extra or aliased fields, `None`, malformed digests and contradictory variants reject. The nine retained fixtures — `mailto:owner@example.test`, `javascript:alert(1)`, `authorization:bearer-token`, `prompt injection`, `C:drive-relative`, `access_token=abc`, `Authorization Bearer abc`, `api-key=abc`, `ignore previous instructions` — all reject. Admitted bounded Unicode metadata preserves exact code points without normalization. |
| UIR2 | `AVAILABLE_AUTHORIZED` plus matching target and complete bound desktop/mobile rendered evidence returns only `ADMITTED_RENDERED`; missing one ref/digest, duplicate refs, artifact/unavailable evidence or mismatched requested state returns the named refusal. |
| UIR3 | `AVAILABLE_NOT_AUTHORIZED` returns only `DESIGN_CAPABILITY_AUTHORITY_REQUIRED` and does not admit caller-supplied evidence. |
| UIR4 | `UNAVAILABLE` and `DECLINED` plus complete bound target-owned artifact evidence and literal manual-open acknowledgement return only `ADMITTED_ARTIFACT`; without it they return `UI_REFERENCE_RENDERER_REQUIRED`. `AVAILABLE_AUTHORIZED` plus artifact evidence returns `STATE_EVIDENCE_MISMATCH`. |
| UIR5 | Renderer-target mismatch on rendered or artifact evidence returns `TARGET_MISMATCH`. `ANY` matches every finite actual target; a DOM-only renderer cannot produce native-engine/mobile/terminal evidence. An unavailable evidence variant carries no artifact target claim and follows the capability truth table. |
| UIR6 | A valid evidence binding whose request ref, brief ID or approved-content digest differs from the outer request returns `CONTENT_BINDING_MISMATCH`; duplicate evidence and remaining state/evidence cross-pairs return their named refusal without an admitted result. |
| UIR7 | AST/source checks prove one reducer entry, tagged no-null variants, private-module boundary and absence of filesystem/browser/DOM execution/Figma/image/provider/network/process/environment/Git/importlib/dynamic lookup/`Any`/`cast`/raw-mapping effects. |
| UIRM1 | Reverse-mutate `AVAILABLE_NOT_AUTHORIZED` to admit rendered evidence; UIR3 turns red, then exact restoration returns green. |
| UIRM2 | Reverse-mutate target matching to accept every target; UIR5 turns red, then exact restoration returns green. |
| UIRM3 | Reverse-mutate artifact fallback to omit manual acknowledgement; UIR4 turns red, then exact restoration returns green. |
| UIRM4 | Reverse-mutate the evidence-binding comparison to accept a valid-but-different request/content binding; UIR6 turns red, then exact restoration returns green. |
| UIRM5 | Reverse-mutate the positive identifier grammar to accept one separator or punctuation character; the direct UIR1 grammar cell turns red with unreduced output, then byte-exact restoration returns green. |

Strong-type preflight constructs every success/wait/refusal variant through ordinary public
validators and round-trips. Negative bypass values are rejection evidence only. Each named UIR
cell requires one reviewer-executed reverse mutation bound to the exact candidate SHA under
review, with the mutation, direct rerun command, named red assertion and complete unreduced output;
byte-exact restoration and the corresponding green rerun are mandatory. At least one reviewer
mutation must enter through a door different from every implementer-reported mutation. Zero red is
a finding, never a pass. The revision-02 baseline-defect table remains historical evidence and
must not be backfilled. A UIR4 baseline-red that the old schema can express may be attached
voluntarily but is not required and cannot substitute for the reviewer mutations.

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

## Closure revision 03 authority — APPROVED

The project owner approved exact document revision 08 at candidate authority commit
`a616e561423fd40508dfbebcb33b798e071b5462`, LF-normalized leaf SHA-256
`7b35f9f80d5616e6e5d9ff8a83817e937d1c5094e3bb4cfa042a75af08aef953`, on 2026-09-01
(Asia/Taipei). Revision 03 is now the effective closure and replaces only the UIR1 identifier rule
and the correction-baseline evidence rule as specified below. This approval does not authorize
implementation, a third correction, integration, push, publication, target mutation or provider
use.

### A. Closed positive identifier grammar

Replace the semantic unsafe-marker denylist with one executable positive predicate over exact
Unicode code points:

1. An opaque identifier contains 3 through 128 Unicode code points inclusive.
2. Every code point has a Unicode General Category beginning with `L`, `M` or `N`. This is the
   complete allowlist. Whitespace, every separator and every punctuation or symbol character —
   including `=`, `:`, `/`, `\\`, hyphen, underscore, dot, at-sign and brackets — rejects.
3. General Categories `Cc` and `Cf` always reject. This expressly includes zero-width characters
   and bidirectional override/control characters even when surrounding characters are otherwise
   admitted.
4. Validation is rejection, not transformation. The gate performs no Unicode normalization,
   case-folding, trimming, escaping or replacement; admitted identifiers preserve their exact code
   points.
5. This layer does not claim to distinguish an encoded secret from a legitimate opaque reference.
   A base64url- or hexadecimal-shaped value may satisfy the grammar. Keeping secret material out of
   references remains the caller's responsibility under
   `skills/johnny-project-takeover/references/security-boundary.md`.

UIR1 retains all nine known bypass strings as direct negative fixtures, not as an exhaustive
denylist:

```text
mailto:owner@example.test
javascript:alert(1)
authorization:bearer-token
prompt injection
C:drive-relative
access_token=abc
Authorization Bearer abc
api-key=abc
ignore previous instructions
```

Add `UIRM5`: reverse-mutate the positive grammar to accept a separator or punctuation character;
the direct UIR1 grammar cell must turn red with unreduced output, and byte-exact restoration must
return it green.

### B. Superseded correction-baseline rule and replacement evidence

The revision-02 sentence requiring the new UIR1, UIR2, UIR4 and UIR6 cells to turn red by name on
`faf3d05e07f83a8c7804313b4d3435d01da338b0` is `SUPERSEDED`. It must not be recreated or
backfilled as historical evidence. Those cells depend on `ReferenceEvidenceBinding`, which that
baseline does not define, so the combined revised test stops during collection and the named red
behavior is structurally unreachable.

The replacement evidence standard is:

1. Each named UIR cell is proved by one reviewer-executed reverse mutation against the exact
   candidate SHA under review.
2. Each record binds the mutation, exact candidate SHA, direct rerun command, named red assertion
   and complete unreduced output; byte-exact restoration and the corresponding green rerun are
   mandatory.
3. At least one reviewer mutation enters through a door different from every implementer-reported
   mutation. Zero red is a finding, never a pass.
4. The baseline-defect table already reproduced in `REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02`
   revision 02 remains unchanged as historical evidence.
5. The UIR4 `AVAILABLE_AUTHORIZED + ARTIFACT_ONLY` behavior can be expressed with the old schema;
   a baseline-red run on `faf3d05e07f83a8c7804313b4d3435d01da338b0` may be attached voluntarily,
   but is not required and cannot substitute for the reviewer mutations above.

Revision 03 is the effective acceptance closure. The ticket remains `NON_DISPATCHABLE` until a
separate implementation authority is committed, and candidate
`07edaff11bfe981987288a9c1b6becb67c4e69ad` remains non-integrated evidence only.

## Ownership and return

Exact approval of closure revision 03 changes the ticket contract only; it does not allocate an
implementation owner or permit a third correction. A separate committed implementation authority
is required before the reviewer may bind any same-lifetime owner lane. If later authorized, the
owner modifies only declared source/test/element paths, does not commit or push, and cannot invoke
a renderer/provider or change UIX-01, SPEC, Context, ticket or skills.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with UIR/UIRM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or
`CHANGE_DETECTED -> REQUIREMENT_CHANGED`. No return authorizes rendering, target mutation,
integration, push, publication, installation, release or deployment.
