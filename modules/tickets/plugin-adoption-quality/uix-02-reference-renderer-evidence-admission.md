# UIX-02 | Reference-renderer evidence admission

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-PLUGIN-ADOPTION-QUALITY-UIX-02` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-JOHNNY-DESIGNERLESS-UI-CODESIGN-20260829-01` / AC-1, AC-2 and the renderer/evidence portion of AC-8 |
| Requirement / Context / ADR | `PRD-20260829-049` / `CHG-20260829-049` / `CTX-PLUGIN-ADOPTION-QUALITY-20260829-02` Revision 01, SHA-256 `dd776e27777b7a4679ce8573c05639e7d7ab24481e654cf431da45c81fb99a26` / `ADR-20260829-037` |
| State / closure | `APPROVED / LOCAL_INTEGRATION_PENDING`; effective `CLOSURE-PLUGIN-ADOPTION-QUALITY-UIX-02`, revision 05; production contract inherited unchanged from revision 04 |
| Document revision | `16` |
| Opening authority | Project owner, 2026-08-31 (Asia/Taipei): authorized opening UIX-02 after UIX-01 closure. Exact ticket approval and implementation dispatch remain separate; no renderer, browser, provider, target write, publication, installation, release or deployment effect is granted. |
| Approval authority history | Project owner, 2026-08-31 (Asia/Taipei): approved exact ticket candidate/authority commit `4f501ccc4f4ecf943fd3f0f6be89871b7341a4ac`, leaf SHA-256 `22c3d12fd150ffc32273722510a4c725f670d45eb2c9135cca44c9a223cbfd45`. This authorized the initial UIX-02 Luna/xhigh same-lifetime implementation lane; that lane was consumed and grants no current authority. Review, integration, push and every external effect remained separate. |
| Review outcome | Candidate `faf3d05e07f83a8c7804313b4d3435d01da338b0` is not integrated. Independent audit and reviewer reproduction proved that revision-01 evidence variants cannot express the request/content binding required by UIR6; changing that public ticket contract requires an owner-approved closure revision. Additional frozen-contract findings are recorded in `REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02` revision 01. |
| Closure revision 02 proposal | Reviewer, 2026-08-31 (Asia/Taipei): proposes the exact evidence binding, truth-table, Unicode and canonical-field corrections below. This proposal is not approval and authorizes no correction dispatch or effect. |
| Closure revision 02 approval history | Project owner, 2026-08-31 (Asia/Taipei): approved exact candidate `79414732c9123e9ba4bac7c5bdc625d1f16217d3`, ticket SHA-256 `f43b516b4c5589c36e5ffa093759726e9e0e8c8538367e695d9d4ff524a31d9b`. This authorized the revision-02 additive-correction cycle; that authority is exhausted as recorded below and grants no current lane. Review, integration, push and every external effect remained separate. |
| Closure revision 02 initial review | Candidate `611959f69df9bb639509d7e9068e86fb8b3e4564` is not integrated. `REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02` revision 02 records one UIR1 unsafe-value implementation defect and one candidate-baseline evidence defect. At that review point the same owner could receive the closure's single additive correction; the later correction exhausted it. |
| Closure revision 02 correction review | Candidate `07edaff11bfe981987288a9c1b6becb67c4e69ad` is not integrated. The reviewer independently reproduced remaining credential/prompt bypasses and the absence of reproducible named baseline-red evidence. The one permitted correction is exhausted; no third correction may dispatch without control-plane convergence and a new owner-approved closure. |
| Closure revision 03 proposal history | At proposal time this awaited exact owner approval. Project owner authorized control-plane drafting on 2026-09-01 (Asia/Taipei), not approval. The later approval is recorded separately below. |
| Closure revision 03 approval | Project owner, 2026-09-01 (Asia/Taipei): approved exact document revision 08 at candidate authority commit `a616e561423fd40508dfbebcb33b798e071b5462`, LF-normalized leaf SHA-256 `7b35f9f80d5616e6e5d9ff8a83817e937d1c5094e3bb4cfa042a75af08aef953`. This activates closure revision 03 only. Implementation dispatch, a third correction, candidate integration, push, publication, target effect and provider effect remain separate and unauthorized. |
| Closure revision 03 adversarial review | Docs candidate `7abe2a997e2e68c7e3adb97442d2324c380d4094` is blocked. A Terra/xhigh read-only helper found, and the reviewer independently reproduced, that the `L* / M* / N*` allowlist admits zero-width `Mn` code points while the same closure claims zero-width characters reject. This is `TICKET_DEFECT`, not implementation authority. |
| Closure revision 04 direction authority history | Project owner, 2026-09-01 (Asia/Taipei): approved drafting the minimal `L* / N*`-only repair direction after the adversarial finding. Exact artifact approval was separate and is recorded below. This direction granted no implementation dispatch, third correction, integration, push, publication, target effect or provider effect. |
| Closure revision 04 proposal review | Docs candidate `f910b8db8c3fa28e4ce07b46317d87e383f771d0` is blocked. A Terra/xhigh read-only helper found, and the reviewer independently reproduced, that the proposal did not explicitly replace the operative UIR1 row and that its single-code-point mark fixtures were masked by the three-code-point minimum. Document revision 11 applied one additive proposal correction; its later exact approval is recorded below. |
| Closure revision 04 approval | Project owner, 2026-09-01 (Asia/Taipei): approved exact document revision 11 at candidate authority commit `515e2fd81f8b54030c5fd27abbd43cd63d5df3bc`, LF-normalized leaf SHA-256 `348a5c2f12a773b77898616b71ce70947625f1f9fb6db021b0c4ca171fa437fb`. This activates closure revision 04 only. Implementation dispatch, a third correction, candidate integration, push, publication, target effect and provider effect remain separate and unauthorized. |
| Source baseline / dependency | `1d2be10e8de224909b2c46a4eb6f8ef63eb7265c`; UIX-01 contracts integrated at `2c7b5adafa0a84f7a4219e4287daea38d8d855a5`. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | Reuse `/root/plugin_adoption_implementer`, `implementation-standard` — Luna/xhigh, one same-lifetime lane, no helper. Owner's subsequent 2026-09-05 convergence/completion authority permits the bounded evidence-only revision-05 work below; earlier cycles remain exhausted. The current-session reviewer retains final review responsibility. |
| Worktree / branch / task | Preserve `.worktrees/plugin-adoption-quality-uix-02`, branch `implement/plugin-adoption-quality-uix-02`, task `/root/plugin_adoption_implementer`; current candidate `b419954bc57777661d7522247ffc26977f668ca7` over initial candidate `18ed02c736812e2e7fab738dc2b8a7036d1da987` and prior baseline `07edaff11bfe981987288a9c1b6becb67c4e69ad`. Historical commits remain immutable and unintegrated. |
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
  Unicode General Category begins with `L` or `N`. Every `M*`, `C*`, separator, punctuation,
  symbol, unassigned, private-use and surrogate category rejects. The gate rejects rather than
  transforms: no normalization, case-folding, trimming, escaping or replacement occurs, and
  admitted code points are preserved exactly. Precomposed letters may admit; decomposed forms
  containing any combining mark reject. This grammar does not claim to distinguish encoded secret
  material from a legitimate opaque reference; callers remain responsible for keeping secrets out
  of refs. Only canonical field names are accepted and validation aliases are forbidden.
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
| UIR1 | Every enum/binding/request/evidence/decision variant ordinary-constructs, strict-validates and JSON-round-trips. Identifiers accept exactly 3–128 code points from Unicode General Categories `L*` and `N*`; every other category rejects without transformation. Empty/whitespace/control/format/mark/overlength IDs, wrong primitives, extra or aliased fields, `None`, malformed digests and contradictory variants reject. The retained bypass fixtures — `mailto:owner@example.test`, `javascript:alert(1)`, `authorization:bearer-token`, `prompt injection`, `C:drive-relative`, `access_token=abc`, `Authorization Bearer abc`, `api-key=abc`, `ignore previous instructions` — plus length-valid `U+034F × 3`, `U+FE0F × 3` and `e + U+0301 + e` all reject. Precomposed `éab` admits as three `L*` code points, remains distinct from its decomposed representation and preserves exact code points without normalization. |
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
| UIRM6 | Reverse-mutate the category predicate from `L* / N*` to `L* / M* / N*`; `U+034F × 3` and `e + U+0301 + e` become admitted, their direct UIR1 rejection assertions turn red with complete unreduced output, and byte-exact restoration returns green. |

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

## Closure revision 03 authority — SUPERSEDED BY REVISION 04

The project owner approved exact document revision 08 at candidate authority commit
`a616e561423fd40508dfbebcb33b798e071b5462`, LF-normalized leaf SHA-256
`7b35f9f80d5616e6e5d9ff8a83817e937d1c5094e3bb4cfa042a75af08aef953`, on 2026-09-01
(Asia/Taipei). Revision 03 was effective until the later exact approval of revision 04. Its
identifier grammar below is retained as historical evidence only and is no longer operative. Its
correction-baseline evidence rule remains inherited by revision 04. Neither approval authorizes
implementation, a third correction, integration, push, publication, target mutation or provider
use.

### A. Historical positive identifier grammar — SUPERSEDED

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

Revision 03 is superseded by revision 04. The separate implementation authority is recorded below;
candidate `07edaff11bfe981987288a9c1b6becb67c4e69ad` remains non-integrated historical evidence.

## Closure revision 04 authority — APPROVED

Adversarial review of docs candidate `7abe2a997e2e68c7e3adb97442d2324c380d4094`
proved that revision 03 is internally inconsistent: `U+034F COMBINING GRAPHEME JOINER` and
`U+FE0F VARIATION SELECTOR-16` are both Unicode General Category `Mn`, so three copies satisfy the
declared 3–128 / `L* | M* | N*` predicate even though the same closure says zero-width characters
reject. The reviewer independently reproduced both admissions with Python 3.11 `unicodedata`.

The project owner approved exact document revision 11 at candidate authority commit
`515e2fd81f8b54030c5fd27abbd43cd63d5df3bc`, LF-normalized leaf SHA-256
`348a5c2f12a773b77898616b71ce70947625f1f9fb6db021b0c4ca171fa437fb`, on 2026-09-01
(Asia/Taipei). Revision 04 replaces every operative occurrence of revision 03's identifier grammar
and adds one discriminating mutation cell. Historical proposal/review evidence remains unchanged:

1. An opaque identifier contains 3 through 128 Unicode code points inclusive.
2. Every code point has a Unicode General Category beginning with `L` or `N`. This is the complete
   allowlist. Every `M*`, `C*`, separator, punctuation, symbol and unassigned/private-use/surrogate
   category rejects.
3. Validation rejects rather than transforms. It performs no Unicode normalization, case-folding,
   trimming, escaping or replacement; admitted identifiers preserve exact code points.
4. Precomposed letters remain admissible when the whole identifier otherwise satisfies the
   grammar. Decomposed forms containing a combining mark reject because every `M*` rejects. This
   is an intentional closure tradeoff, not an implicit normalization step.
5. The operative UIR1 row retains the existing nine bypass strings and adds length-valid direct
   rejection fixtures: `U+034F × 3`, `U+FE0F × 3`, and `e + U+0301 + e`. It also adds the
   length-valid positive control `éab`, whose three code points are all `L*`; the exact precomposed
   code point is preserved without normalization.
6. `UIRM6` reverse-mutates the category predicate from `L* / N*` to `L* / M* / N*`;
   `U+034F × 3` and `e + U+0301 + e` become admitted, so their direct UIR1 rejection assertions
   must turn red with complete unreduced output. Byte-exact restoration must return them green.
7. This approval replaces the operative grammar in all three normative locations: the
   `Frozen responsibility and evidence rules` identifier bullet, the UIR1 TDD-matrix row, and
   closure revision 03 section A. No remaining operative `L* / M* / N*` rule may coexist with
   revision 04.

The revision-03 `L* / M* / N*` rule and its former operative UIR1/frozen-rule copies are
`SUPERSEDED`. Revision 04 is the effective closure. At exact closure approval time the ticket
remained `NON_DISPATCHABLE`; execution authority was granted separately as recorded below.

## Execution authority — 2026-09-05

The project owner instructed: "先把最新版本下載下來，然後授權執行". Remote fetch and direct
readback confirmed `origin/main = be463ae4c838af3cc09c88271215c542c72f107c`; local main
`71273537c78afb4318f4e98b539424b0790f332f` contains that commit plus ten previously authorized
control-plane commits, with no incoming remote commits and a clean working tree.

This authorizes implementation of the already approved closure revision 04, including the
previously blocked additive correction, reuse of the existing Luna/xhigh owner/worktree, local
verification and reviewer-owned candidate commits. It does not revise the closure or resurrect
the superseded baseline-red requirement. The reviewed historical commits must not be reset,
amended or overwritten. Candidate integration, push, publication, installation, deployment and
target/provider effects remain outside this grant.

The reviewer binds `ContextView UIX02R13-20260905` to this exact ticket/registry commit, the
existing branch/baseline above, the sealed Context revision 01 and `POC / STANDARD` under
`doc/runbooks/dispatch-model-profile.md` revision 03. Previous ticket views are stale. The
same-lifetime route is `TICKET_DISPATCH_REQUIRED -> AUTO_CONTINUE / IMPLEMENT`, bridge disposition
`NOT_REQUIRED`: reuse the existing owner, wait for its typed return, arrange independent read-only
adversarial findings, then perform the current-session review and candidate-bound reverse
mutations. No runner, receipt, queue or cross-lifetime wake is required or claimed.

## Ownership and return

### Convergence review outcome — 2026-09-05

Closure revision 05 source/test candidate `448ea232761a7fbd0152efe7279bcea0a7c442e3`
received one evidence-only correction `5405ed8d7c03762cbb22744110ae4524edfcd4ff`.
The current-session reviewer independently reproduced nine red/restore/green mutations
covering UIR1–UIR7 and UIRM1–UIRM6, plus the complete 75-test / 300-subtest regression,
strict typing and compile gates. The reused read-only adversarial helper found no new
source/test defect. `REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02` revision 14 records the
parent's APPROVED verdict and complete unreduced evidence. Product source remains
byte-exact to `b419954...`; the evidence correction changes no source or test.

Implementation ContextView `UIX02R15-20260905` is closed; no further implementation
dispatch is outstanding. The reviewer may carry current control-plane ancestry into
the existing candidate without rewriting historical commits, verify the unchanged
ticket-only delta, and pass `admit_document_mutation`. The return is `ACTION_COMPLETED`
with continuation `AUTO_CONTINUE / GUARDED_LOCAL_INTEGRATION`. Only actual gate
readback can establish LOCAL_INTEGRATED. No push/authority-integration, release,
installation or provider/target effect is claimed or granted.

### Owner-authorized convergence revision 05 — 2026-09-05

After the revision-04 blocked review, the owner answered the request for control-plane convergence:
"授權，依照我的專案目標，用資深工程/架構師的方式思考、收斂，完成專案". This records
scope-based execution authority for the three named evidence defects, not a claim that the owner
pre-approved an unseen commit SHA. The separate MSIX installer requirement does not change this
ticket's pure renderer-evidence contract or authorize a renderer/provider effect.

Convergence diagnosis: the production reducer/grammar already implements the approved contract.
The remaining failures are an open-ended name blacklist, an overlapping uniqueness fixture, and
a validation assertion located in the wrong named cell. Preserve production source byte-for-byte
from `b419954bc57777661d7522247ffc26977f668ca7`; the revision-05 implementation delta is tests
and indexed element evidence only. The overall ticket boundary above is retained for subsequent
review of the complete, still-unintegrated source lineage. No new public API, generic AST scanner,
runtime security sandbox or production hardening is part of this convergence.

`READY_LOW_MODEL`: one finite acceptance-proof closure at the existing test seam. Splitting its
three checks into new production features would not produce separate user outcomes; the clarified
finite policy removes the open-ended inference task. No model elevation is needed. Use baseline
`b419954bc57777661d7522247ffc26977f668ca7`, the existing branch/worktree, exact revision-15
ticket/registry commit and fresh `ContextView UIX02R15-20260905`. Prior views remain closed.
The direct continuation is `TICKET_DISPATCH_REQUIRED -> AUTO_CONTINUE / IMPLEMENT`, bridge
`NOT_REQUIRED`, followed by `wait_agent`, independent adversarial findings and current-session
review. This is a new owner-authorized convergence closure, not a third revision-04 correction.

#### Finite revision-05 acceptance additions

1. **UIR7 / closed source grammar.** Factor a test-owned validator over `ast.Module` and invoke it
   on the actual production module source. Its allowed imports are literal policy data, not a
   set inferred from the same source being checked. Reject star imports, every import alias,
   unlisted module/symbol or wrong relative level. The exact import grammar is:

   | Form | Level / module | Exact allowed members |
   | --- | --- | --- |
   | import | `unicodedata` | no alias |
   | from | `0 / __future__` | `annotations` |
   | from | `0 / enum` | `Enum` |
   | from | `0 / typing` | `Annotated`, `Literal`, `Self`, `TypeAlias`, `Union` |
   | from | `0 / pydantic` | `AfterValidator`, `ConfigDict`, `Field`, `TypeAdapter`, `field_validator`, `model_validator` |
   | from | `1 / contracts` | `RouterModel` |
   | from | `1 / ui_codesign_contracts` | `ContentDigest`, `ReferenceRendererState` |

   Every loaded double-underscore name and every double-underscore attribute rejects, including
   `__builtins__`; `__all__` assignment remains allowed. Call targets must be literal members of
   the following production-specific policy (not an inferred inventory or string-substring test):
   `AdmittedArtifactDecision`, `AdmittedRenderedDecision`, `AfterValidator`, `ConfigDict`, `Field`,
   `RendererRefusedDecision`, `RendererWaitDecision`, `TypeAdapter`, `ValueError`,
   `_evidence_binding_matches_request`, `_evidence_is_duplicate`,
   `_evidence_matches_requested_state`, `_refuse`, `_target_matches`, `_wait`, `all`, `any`,
   `field_validator`, `isinstance`, `len`, `model_validator`, `ord`, `type`,
   `_REQUEST_ADAPTER.validate_python`, `unicodedata.category`, `value.strip`.
   Reject other call-expression shapes, unlisted targets, starred positional arguments and
   unpacked keyword arguments. Retain the existing no-Any/no-cast/no-raw-mapping, finite reducer,
   tagged-no-null and private-export checks. This is a review guard for this source module, not a
   claim of safety for arbitrary Python or permission to execute untrusted code.

   Required independent rejection fixtures include `typing.Any` through a module alias, aliased
   `typing.cast`, ordinary imported `Any` under multiple alias spellings, direct and indirect
   `__builtins__` dynamic imports, an attribute call on a call result, star imports and an unknown
   callee. Parse hostile snippets only; never execute them. In addition to fixture checks, the
   reviewer must mutate the production source and run the real UIR7 cell. Exact-original source
   remains the positive control; AST/hash snapshots alone are not behavioral evidence.

2. **UIR6 / independent observation uniqueness.** Add separate desktop/observation and
   mobile/observation collisions with otherwise unique screenshot refs and digests, and assert
   `DUPLICATE_EVIDENCE`. Reverse mutation removes observation membership AND changes expected set
   size 3 to 2; both named collision assertions must turn red. Keep existing independent
   screenshot/digest/artifact and all three request-binding cases.

3. **UIR4 / strict acknowledgement at the named seam.** UIR4 itself tests missing acknowledgement
   and false/null/int/float/string values with all other artifact fields valid, via ordinary
   direct and nested validators, plus literal-true admitted fallback for UNAVAILABLE and DECLINED.
   UIR1 retains its strict-construction cases. Giving acknowledgement a default true must turn
   the named UIR4 missing-field assertion red, satisfying UIRM3 without changing its meaning.

All existing UIR1–UIR7 and UIRM1–UIRM6 obligations remain. For evidence corrections, use the old
test/source candidate above as the defective baseline; do not invent a faf3d05 baseline-red.
Record exact mutations, direct named commands and unreduced red/restore/green outputs in a leaf
under the declared element directory, with its README direct-child revision/digest edge updated
after the last leaf edit. The reviewer independently repeats the three convergence probes and
at least one different source mutation, validates every named UIR cell, creates a local candidate
commit, and may perform guarded local integration only after APPROVED. No remote push, package
signing, installation, publication or target/provider effect is authorized by this evidence lane.

### Historical revision-04 execution outcome — 2026-09-05

The current-session reviewer and reused read-only adversarial helper completed closure-04 initial
review and its one additive correction review. Source candidate
`b419954bc57777661d7522247ffc26977f668ca7` passes 75 tests and 275 subtests, strict mypy and
compile, but remains `BLOCKED`: UIR7 still misses qualified/aliased forbidden typing and indirect
dynamic import, UIR6 does not independently pin observation-ref uniqueness, and UIRM3's missing
acknowledgement mutation leaves the specified UIR4 green (UIR1 catches it instead).

`REVIEW-PLUGIN-ADOPTION-QUALITY-UIX-02` revision 13 records the exact candidate, unreduced
reproductions and restoration evidence. These are remaining `EVIDENCE_DEFECT` findings, not proof
of a production effect or authority bypass. Under `CodeReview.md` section 5, further correction
requires control-plane convergence; no third correction is dispatched. ContextView
`UIX02R13-20260905` is closed. No integration, push or publication was performed.

The 2026-09-05 execution authority bound the now-completed same-lifetime owner lane. The owner modifies only
declared source/test/element paths, does not commit or push, and cannot invoke a renderer/provider
or change UIX-01, SPEC, Context, ticket or skills. The reviewer, not the implementation owner,
creates local candidate commits and owns the final review verdict.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with UIR/UIRM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or
`CHANGE_DETECTED -> REQUIREMENT_CHANGED`. No return authorizes rendering, target mutation,
integration, push, publication, installation, release or deployment.
