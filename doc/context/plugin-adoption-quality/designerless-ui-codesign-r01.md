# Designerless UI co-design Context

| Field | Value |
| --- | --- |
| Artifact ID / revision | `CTX-PLUGIN-ADOPTION-QUALITY-20260829-02` / `REVISION_01` |
| State | `ARCHITECTURE_DRAFT / OWNER_EXACT_APPROVAL_PENDING` |
| Requirement / ADR | `PRD-20260829-049` / `CHG-20260829-049` / `ADR-20260829-037` |
| Authority | Project owner requires a no-designer UI co-design workflow on 2026-08-29 (Asia/Taipei). This draft grants no design-provider or implementation effect. |

## Confirmed facts

- The existing UI handoff accepts `FIGMA`, `SCREENSHOT`, `DESIGN_BRIEF`,
  `EXISTING_DESIGN_SYSTEM` or `NONE`, and keeps design tools optional.
- A UI regime is cross-feature and must be owner-approved and sealed by the canonical CONTEXT stage
  before feature tickets consume it. Per-ticket reinvention creates drift.
- Design-craft capability output is input/finding only. It cannot decide requirements, approve a
  direction, authorize source changes or conclude review.
- The owner can make the subjective visual-direction decision without being a professional
  designer when alternatives and the strongest honestly available evidence are concrete.

## Stable architecture facts

- `co-design-ui` is a separate automatically discoverable skill in the existing Johnny plugin for
  both Codex and Claude Code.
- The no-external-design-tool path is first class: design brief, tokens and reference markup remain
  target-owned. Renderer state is separate: `RENDERED_AVAILABLE`, `ARTIFACT_ONLY` or `UNAVAILABLE`.
- Visual directions differ structurally, not only by palette. Co-design runs in
  `ARCHITECTURE`/`GRILL`; owner selection creates a regime candidate, and only
  `context-routing.md` CONTEXT seals the approved revision before implementation ticketing.
- Feature contracts preserve component, finite-state, responsive, accessibility, asset and
  interaction boundaries from the sealed regime.
- A separate reviewer evaluates actual rendered output. Figma/image/craft tools are optional ports.
- Codex and Claude Code consume the same target-owned design contracts but prove discovery,
  capability routing and review handoff independently.
- Five fresh sessions per host/scenario form one immutable behavioral evidence set: at least four
  route correctly and all five avoid unauthorized effect/self-approval. Extra retries cannot erase
  a failure.
- UIX closure produces readiness only. Shared `PAQ-REL-01` alone owns the composed release effect.

## Data and effect flow

```text
target product facts
  -> strict design brief
  -> classify renderer
  -> direction candidates + rendered or artifact-only evidence
  -> owner selection
  -> regime candidate
  -> canonical CONTEXT sealing of owner-approved target-owned UI regime
  -> feature UI contract
  -> separate implementation
  -> rendered state/breakpoint evidence
  -> adversarial visual review + owner acceptance
```

`UNAVAILABLE` reference rendering returns
`WAIT_FOR_HUMAN / UI_REFERENCE_RENDERER_REQUIRED`; unavailable actual-output verification returns
`WAIT_FOR_HUMAN / VISUAL_VERIFICATION_REQUIRED`. Neither path may claim completion.

Kept artifacts live in the target repository. Optional provider payloads, credentials, raw prompts
and unrestricted tool output do not enter Router state, Context or review evidence.

## Boundary

This draft is not sealed. It authorizes no provider access, image generation, Figma write, UI
implementation, publication, installation or release.
