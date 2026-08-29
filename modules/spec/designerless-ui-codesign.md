# Designerless UI co-design specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-JOHNNY-DESIGNERLESS-UI-CODESIGN-20260829-01` |
| Status | `DRAFT / OWNER_EXACT_APPROVAL_PENDING` |
| Author / baseline | Codex architecture owner / `control/plugin-adoption-quality-architecture` / `79505f65e932541d06eac797a2ea165f74cd194e` |
| Context | `CTX-PLUGIN-ADOPTION-QUALITY-20260829-02` (`ARCHITECTURE_DRAFT`) |
| PRD / change / ADR | `PRD-20260829-049` / `CHG-20260829-049` / `ADR-20260829-037` |
| Implementation language | Skill Markdown/YAML plus Python 3.11 strict helpers only where deterministic artifact validation is needed |

## Problem, goal and out of scope

The workflow can consume an approved visual source but cannot currently help a non-designer owner
create and converge one. Success is a repeatable owner/AI loop that yields an approved, target-owned
UI regime and implementation-ready feature contracts with rendered visual evidence.

Out of scope: replacing owner taste, making Figma/image generation mandatory, silent provider use,
letting generated output self-approve, production frontend frameworks/templates in the plugin,
implementer-owned final review and redesigning an approved human source without authority.

## Public contracts and lifecycle

```text
UICodesignState = BRIEF_DRAFT | BRIEF_APPROVED | DIRECTIONS_READY
                | OWNER_SELECTION_REQUIRED | REGIME_SEALED
                | FEATURE_CONTRACT_READY | IMPLEMENTATION_READY
                | VISUAL_REVIEW_REQUIRED | OWNER_ACCEPTANCE_REQUIRED | COMPLETE
DesignSourceKind = FIGMA | SCREENSHOT | DESIGN_BRIEF | EXISTING_DESIGN_SYSTEM | NONE
DesignCapabilityState = AVAILABLE_AUTHORIZED | AVAILABLE_NOT_AUTHORIZED
                      | UNAVAILABLE | DECLINED
VisualFindingSeverity = BLOCKING | MATERIAL | POLISH
SupportedHost = CODEX | CLAUDE_CODE
```

`UIDesignBrief` contains product/audience/job, brand personality and anti-goals, target platform,
content hierarchy, information density, accessibility baseline, locale/content constraints,
required states and references. No free-form provider credentials or URLs enter it.

`VisualDirectionCandidate` contains a stable ID, rationale, typography/colour/spacing/component/
motion decisions, macrostructure, accessibility notes and exact target-owned rendered evidence.

`UIRegime` is the owner-selected sealed cross-feature contract. `UIImplementationContract` is one
feature's component/state/responsive/accessibility mapping to that regime. `VisualReviewReport`
contains screenshot refs, breakpoint/state matrix, findings and evidence digests; it does not carry
owner acceptance.

## Co-design and implementation flow

1. Compile and show one bounded brief; unresolved product facts return one owner input round.
2. Classify design source and optional design-craft capability. Never install or access a tool
   implicitly.
3. Produce at least two materially distinct directions. Each has comparable desktop/mobile visual
   evidence and the same approved content, so the owner compares design rather than different data.
4. Wait for exact owner selection or a bounded correction. No direction selection is inferred.
5. Seal the selected target-owned regime and create per-feature `UIImplementationContract` leaves.
6. A separate implementation owner builds one complete observable component/flow per ticket.
7. Reviewer renders declared breakpoints and finite states, runs behavioral/accessibility tests and
   adversarial craft review, then asks the owner for final visual acceptance.

## Responsibility, dependency and composition map

| Component | Owns | Must not own |
| --- | --- | --- |
| `UICodesignRouter` | finite lifecycle and owner-decision waits | visual generation, source implementation |
| `DesignBriefCompiler` | strict target-owned brief normalization | style selection, provider effect |
| `DesignCraftPort` | optional direction proposals/audit findings | approval, requirements, review conclusion |
| `ReferenceRendererPort` | target-matched reference artifact and screenshots | production UI, regime sealing |
| `UIRegimeSealer` | selected regime identity/digest and target write plan | feature implementation, provider call |
| `UIContractCompiler` | feature component/state/responsive/a11y contract | visual approval, external service |
| `VisualVerificationPort` | actual implementation screenshot/test evidence | implementation mutation, owner acceptance |

The skill is the Composition Root for no-effect routing and capability selection only. Host tools
and renderers are injected. Production UI Composition Root remains inside each target project and
is fully specified by its feature ticket.

## UI, Provider, data, security and operations

The skill itself has no UI runtime. Output artifacts are target-owned briefs, token/regime files,
reference markup/screenshots and feature contracts. Optional Figma/image/craft capability state,
tier and target are classified before invocation. `AVAILABLE_NOT_AUTHORIZED` waits for exact
authority; `UNAVAILABLE`/`DECLINED` takes the local reference-renderer route.

Provider payloads, credentials, raw prompts and unrestricted responses are not persisted. XSS is
classified from target runtime data/sinks. A privileged Browser/WebView/DOM target invokes the
existing XSS reference before ticket admission.

## Visual acceptance rubric

Every direction and final review evaluates the same dimensions: information hierarchy,
typographic scale/rhythm, colour contrast and semantic colour, spacing/density, component
consistency, responsive reflow, keyboard/focus/touch behavior, motion/reduced-motion, content
stress (empty/long/Unicode/error) and target brand fit. The owner may weight brand-fit preferences;
WCAG/functional/state failures remain blocking.

## Acceptance criteria and TDD/forward tests

1. A zero-tool request yields a strict brief and at least two structurally distinct target-owned
   directions with rendered desktop/mobile evidence; absence of Figma is not an error.
2. `AVAILABLE_NOT_AUTHORIZED` waits before provider read/write. `UNAVAILABLE` and `DECLINED`
   choose local rendering without repeated tool prompts.
3. Directions using identical hierarchy/type/component/motion with only palette changes are
   rejected as insufficiently distinct.
4. No regime or implementation contract is emitted before exact owner selection. Replacing the
   selected candidate ID with another turns the seal verification red.
5. Feature contracts cover loading, empty, success, validation/system error, permission/disabled,
   applicable offline, desktop/mobile and accessibility states. Omitting any required state turns
   admission red.
6. Realistic skill forward-tests cover plain brief, existing screenshot/system, authorized Figma,
   optional image craft, owner correction and implemented-output review. Evaluators receive the
   request and skill, not the intended answer.
7. Visual review reads unreduced actual screenshots and test output. The implementer cannot emit
   the review conclusion or owner acceptance.
8. Detach leaves all target-owned design and implementation artifacts intact and removes no target
   runtime dependency.
9. Codex and Claude Code independently prove implicit skill discovery, zero-tool direction
   generation, exact owner-selection wait, feature-contract creation and review handoff. Either
   host failing leaves the plugin release unqualified for both-host support.

## Risks, compatibility, rollback and deployment prerequisites

Taste cannot be reduced to one score; the flow closes it through comparable alternatives and exact
owner selection. Generated reference markup may not match every platform, so artifact-tier output
is admitted only for a matching target while regime-level design can remain portable. A selected
regime changes only through requirement change and a new sealed revision. Publication requires
skill validation, realistic independent forward-tests, payload regeneration/repinning and fresh
Codex/Claude installed qualification.

## Ticket partition after approval

1. `UIX-01` strict brief/direction/regime/feature-contract schemas and lifecycle reducer.
2. `UIX-02` `co-design-ui` skill, UI metadata and zero-tool local workflow.
3. `UIX-03` optional design-craft/Figma/image capability routing adapters.
4. `UIX-04` target-matched reference rendering and visual-evidence contract.
5. `UIX-05` adversarial visual/accessibility review and realistic skill forward-tests.
6. `UIX-06` independent Codex/Claude Code installed qualification, payload publication and upgrade
   instructions.

Each ticket is separately approved and dispatched. UI implementation remains target-project work.

## Revision signature and approval

| Date | AI / worktree / baseline | Summary |
| --- | --- | --- |
| 2026-08-29 | Codex architecture owner / `control/plugin-adoption-quality-architecture` / `79505f65e932541d06eac797a2ea165f74cd194e` | Drafted a designerless owner/AI visual direction, regime sealing, implementation handoff and adversarial visual-review loop. |

Decision maker: Project owner. Exact approval pending.
