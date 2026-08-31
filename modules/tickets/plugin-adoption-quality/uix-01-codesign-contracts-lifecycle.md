# UIX-01 | UI co-design contracts and lifecycle reducer

| Field | Value |
| --- | --- |
| Artifact ID / kind | `TICKET-PLUGIN-ADOPTION-QUALITY-UIX-01` / `IMPLEMENTATION_TICKET` |
| SPEC / acceptance source | `SPEC-JOHNNY-DESIGNERLESS-UI-CODESIGN-20260829-01` / AC-3 through AC-5 and the strict lifecycle portions of AC-1, AC-4 and AC-7 |
| Requirement / Context / ADR | `PRD-20260829-049` / `CHG-20260829-049` / `CTX-PLUGIN-ADOPTION-QUALITY-20260829-02` Revision 01, SHA-256 `dd776e27777b7a4679ce8573c05639e7d7ab24481e654cf431da45c81fb99a26` / `ADR-20260829-037` |
| State / closure | `OPEN / APPROVED / DISPATCHABLE`; `CLOSURE-PLUGIN-ADOPTION-QUALITY-UIX-01`, revision 01 |
| Document revision | `02` |
| Approval authority | Project owner, 2026-08-31 (Asia/Taipei): approved exact ticket candidate `5b8adfee3201d8a945a775d5a238e8c6acfca8ee`. This authorizes one later UIX-01 Luna/xhigh implementation lane after WA-01 allocation is released; review, integration, push and every renderer/provider/target/publication effect remain separate. |
| Source baseline / dependency | `5ca212f2d7ce763a8942e68e96f2fb90cfe3b6e4`; no source ticket dependency. Candidate must descend from the committed ticket authority. |
| Control owner / reviewer | `ticket-review` semantic profile — Terra/xhigh. |
| Implementation owner | `implementation-standard` semantic profile — Luna/xhigh; `READY_LOW_MODEL`, one synchronous owner lane and no helper. |
| Worktree / branch / task | After exact ticket approval, reviewer allocates `.worktrees/plugin-adoption-quality-uix-01` on `implement/plugin-adoption-quality-uix-01` from the then-current committed `main`, then binds this exact ticket revision and baseline. Same-lifetime dispatch uses one native call and one wait; no runner, queue, receipt, descriptor, gateway or host workspace readback. |
| Delivery / language | `POC / STANDARD`; Python 3.11, Pydantic strict models, complete annotations, `mypy --strict`, deterministic pure tests and independent review. |
| XSS / effects | `XSS_NOT_APPLICABLE` for this pure schema/reducer closure. It renders no HTML/DOM, reads no screenshot and performs no filesystem, browser, Figma, image/provider, host, network, target-project, Git, publication, installation, release or deployment effect. |

## Boundary declaration

```johnny-boundary
create = library/workflow_router/ui_codesign_contracts.py
modify = library/workflow_router/ui_codesign_contracts.py
create = tests/test_ui_codesign_contracts.py
modify = tests/test_ui_codesign_contracts.py
create = modules/element/python/plugin-adoption-quality/uix-01-codesign-contracts-lifecycle/
modify = modules/element/python/plugin-adoption-quality/uix-01-codesign-contracts-lifecycle/
forbid = library/workflow_router/__init__.py
forbid = library/workflow_router/contracts.py
forbid = library/workflow_router/router.py
forbid = library/workflow_router/profile.py
forbid = library/local_orchestration/
forbid = modules/spec/
forbid = modules/tickets/
forbid = doc/
forbid = skills/
forbid = .claude-plugin/
forbid = README.md
```

## One observable closure

Create one private module, `library/workflow_router/ui_codesign_contracts.py`, containing strict
schemas and one pure reducer:

```python
reduce_ui_codesign(
    state: UICodesignSnapshot,
    event: UICodesignEvent,
) -> UICodesignDecision
```

The strict family freezes `UICodesignState`, `DesignSourceKind`, `DesignCapabilityState`,
`ReferenceRendererState`, `VisualVerificationState`, `VisualFindingSeverity`, `UIDesignBrief`,
`VisualDirectionCandidate`, `UIRegimeCandidate`, `SealedUIRegimeRef`,
`UIImplementationContract`, `VisualFinding` and `VisualReviewReport`.

The reducer accepts tagged events only and returns exactly one tagged decision:

```text
ADVANCE(next_snapshot, artifact)
| WAIT(OWNER_SELECTION_REQUIRED | UI_REFERENCE_RENDERER_REQUIRED
       | VISUAL_VERIFICATION_REQUIRED | OWNER_ACCEPTANCE_REQUIRED)
| REFUSE(INVALID_TRANSITION | DISTINCT_DIRECTION_REQUIRED
         | CONTEXT_SEAL_REQUIRED | REQUIRED_STATE_MISSING | EVIDENCE_MISMATCH)
```

No action-dependent nullable field is used. Owner selection yields only
`REGIME_CANDIDATE_SELECTED`; only a `CONTEXT_SEALED` event carrying an exact
`SealedUIRegimeRef` may reach `REGIME_SEALED`. The reducer does not write Context or claim that a
candidate is sealed. `ReferenceRendererState.UNAVAILABLE` cannot reach `DIRECTIONS_READY`;
`VisualVerificationState.UNAVAILABLE` cannot reach `COMPLETE`.

The complete legal transition table is frozen here; every other state/event pair returns
`REFUSE(INVALID_TRANSITION)` without changing the snapshot:

| Current state | Event | Result |
| --- | --- | --- |
| `BRIEF_DRAFT` | `APPROVE_BRIEF(exact_brief_id)` | `BRIEF_APPROVED` |
| `BRIEF_APPROVED` | `PRODUCE_DIRECTIONS(candidates, renderer_state)` | `DIRECTIONS_READY` when renderer evidence is valid; renderer wait otherwise |
| `DIRECTIONS_READY` | `REQUEST_OWNER_SELECTION` | `OWNER_SELECTION_REQUIRED` |
| `OWNER_SELECTION_REQUIRED` | `SELECT_DIRECTION(exact_candidate_id, owner_decision_ref)` | `REGIME_CANDIDATE_SELECTED` |
| `REGIME_CANDIDATE_SELECTED` | `CONTEXT_SEALED(exact_sealed_regime_ref)` | `REGIME_SEALED` |
| `REGIME_SEALED` | `COMPILE_FEATURE_CONTRACT(exact_contract)` | `FEATURE_CONTRACT_READY` |
| `FEATURE_CONTRACT_READY` | `ADMIT_IMPLEMENTATION(exact_ticket_ref)` | `IMPLEMENTATION_READY` |
| `IMPLEMENTATION_READY` | `REQUEST_VISUAL_REVIEW(verification_state, evidence_refs)` | `VISUAL_REVIEW_REQUIRED` when available; verification wait otherwise |
| `VISUAL_REVIEW_REQUIRED` | `COMPLETE_REVIEW(exact_report)` | `OWNER_ACCEPTANCE_REQUIRED` |
| `OWNER_ACCEPTANCE_REQUIRED` | `OWNER_ACCEPT(exact_report_id, owner_decision_ref)` | `COMPLETE` |

A `WAIT` retains the current state and immutable artifact identities. It is not an implicit retry,
advance or owner decision. Corrections replace the applicable input through a new typed event at
the same legal state; they cannot rewind a later state or alter a sealed regime.

`TicketDecompositionDecision = READY_LOW_MODEL`: the schemas and reducer are one pure observable
contract closure consumed by all later UIX tickets. No rendering, design generation, provider,
browser or target effect is included.

## Frozen contract and responsibility rules

- Reuse the existing `workflow-router-poc` strict `RouterModel` convention from
  `library.workflow_router.contracts`; do not modify or re-export it.
- `UIDesignBrief` contains bounded product/audience/job, brand personality/anti-goals, platform,
  hierarchy, density, accessibility baseline, locale/content constraints, required finite states
  and opaque reference IDs. It rejects credentials, raw URLs, prompts and unrestricted mappings.
- A valid direction names hierarchy, typography, density, component language, spacing, semantic
  colour, motion/interaction character and renderer-qualified evidence refs. Two candidates that
  differ only in palette are not materially distinct. It binds the same approved-content digest so
  different sample data cannot masquerade as a visual distinction.
- `ARTIFACT_ONLY` direction evidence is valid only as target-owned reference-artifact IDs plus
  owner manual-open acknowledgement. `RENDERED_AVAILABLE` requires desktop and mobile evidence IDs.
  These are separate tagged `ArtifactDirectionEvidence` and `RenderedDirectionEvidence` variants,
  not nullable fields on one shape. `UNAVAILABLE` returns the renderer wait and carries no invented
  evidence or direction candidate.
- Required feature states are finite: loading, empty, success, validation error, system error and
  permission/disabled, plus explicit applicable/not-applicable offline disposition. Responsive and
  accessibility contracts are mandatory.
- `SealedUIRegimeRef` binds Context artifact ID, revision, digest, selected candidate ID and owner
  approval ref. It can be consumed but never constructed by an owner-selection event alone.
- `VisualReviewReport` contains evidence refs and findings only. It has no owner-acceptance or
  implementation mutation field. The module stays private and exports nothing from package root.

### Reusable-module selection record

```text
selected: workflow-router-poc@5ca212f2d7ce763a8942e68e96f2fb90cfe3b6e4
why: strict immutable RouterModel and pure finite-transition conventions match this reducer.
read: MODULE_CATALOG -> workflow-control index -> workflow_router/README -> public __init__
      -> contracts.py RouterModel.
dependency: none beyond existing Pydantic/Router contract primitives.
gap: catalog has no delivered UI co-design module; no near-match is invented.
boundary: no renderer, browser, Figma/image/craft provider, Context writer or package export.
```

## Acceptance closure and TDD matrix

| Cell | Required executable behavior / named result |
| --- | --- |
| UI1 | Every enum/schema/event/decision variant constructs through ordinary strict validators and JSON round-trips. Empty/whitespace IDs, wrong primitives, extra fields, `None`, malformed digests, raw URL/credential/prompt fields and contradictory variants reject. Long bounded text and Unicode round-trip without case/locale normalization. |
| UI2 | A valid brief transitions only to `BRIEF_APPROVED`; two materially distinct candidates with the same approved content may reach `DIRECTIONS_READY`. Two candidates with identical hierarchy/type/density/component/motion and palette-only change return `DISTINCT_DIRECTION_REQUIRED`. |
| UI3 | `RENDERED_AVAILABLE` requires desktop/mobile evidence, `ARTIFACT_ONLY` requires target-owned artifacts plus manual-open acknowledgement, and `UNAVAILABLE` returns exactly `UI_REFERENCE_RENDERER_REQUIRED` without directions-ready state. |
| UI4 | Direction production returns owner-selection wait. Exact selection reaches only `REGIME_CANDIDATE_SELECTED`; a forged candidate ID refuses. Only a matching `CONTEXT_SEALED` event reaches `REGIME_SEALED`; direct selection-to-sealed mutation turns red. |
| UI5 | Feature contract validation requires every finite UI state, responsive breakpoints, accessibility behavior and exact sealed-regime ref. Omitting or duplicating a state, changing the selected candidate or using a stale Context digest returns the named refusal. |
| UI6 | A visual report carries evidence/findings but cannot carry acceptance. `VisualVerificationState.UNAVAILABLE` returns `VISUAL_VERIFICATION_REQUIRED`; available evidence plus reviewer result still waits for owner acceptance, and only an exact owner-acceptance event reaches `COMPLETE`. |
| UI7 | AST/source checks prove one reducer entry, tagged no-null variants, private-module boundary and absence of filesystem/browser/DOM/Figma/image/provider/network/process/environment/Git/importlib/dynamic lookup/`Any`/`cast`/raw-mapping effects. |
| UIM1 | Reverse-mutate distinctness to compare colour only; UI2 turns red, then exact restoration returns green. |
| UIM2 | Reverse-mutate selection to emit `REGIME_SEALED`; UI4 turns red, then exact restoration returns green. |
| UIM3 | Reverse-mutate unavailable verification to complete; UI6 turns red, then exact restoration returns green. |

Strong-type preflight constructs all success/wait/refusal variants and each artifact through
ordinary validators and round-trips. Negative malformed inputs prove rejection only. This is new
behavior, so no ceremonial baseline-red claim is required.

## Verification and review

Implementation-owner commands:

```text
py -3.11 -m pytest -q -p no:cacheprovider tests/test_ui_codesign_contracts.py
py -3.11 -m pytest -q -p no:cacheprovider tests/test_workflow_router.py
py -3.11 -m mypy --strict library/workflow_router/ui_codesign_contracts.py tests/test_ui_codesign_contracts.py
py -3.11 -m compileall -q library/workflow_router/ui_codesign_contracts.py
git diff --check 5ca212f2d7ce763a8942e68e96f2fb90cfe3b6e4 HEAD
git status --short
```

The Terra/xhigh reviewer validates the exact ticket blob/baseline/boundary, ordinary-constructor
preflight, no-null tagged states, structural direction distinction, renderer waits, canonical
CONTEXT-only sealing and reviewer/owner separation. It reruns focused/regression/type/compile gates
and performs one independent counter-mutation not selected by the implementer. Any full-suite
failure is compared unreduced with clean `main`; no baseline failure is reported as candidate
success.

## Ownership and return

After exact ticket approval, the Terra/xhigh reviewer dispatches once, waits once, reviews, commits
the candidate and submits it to `admit_document_mutation`. The Luna/xhigh implementation owner
modifies only the declared source/test/element paths, does not commit or push, and cannot change the
SPEC, Context, ticket, renderer/provider adapter, profile or another Agent.

Return exactly `ImplementationReturn.COMPLETED -> ACTION_COMPLETED` with UI/UIM/type/compile
evidence; `BLOCKED -> HALT` with the failed cell; or
`CHANGE_DETECTED -> REQUIREMENT_CHANGED`. No return authorizes rendering, Provider/Figma/image use,
target mutation, integration, push, publication, installation, release or deployment.
