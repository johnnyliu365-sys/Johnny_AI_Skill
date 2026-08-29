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
- A UI regime is cross-feature and must be owner-approved and sealed before feature tickets consume
  it. Per-ticket reinvention creates drift.
- Design-craft capability output is input/finding only. It cannot decide requirements, approve a
  direction, authorize source changes or conclude review.
- The owner can make the subjective visual-direction decision without being a professional
  designer when alternatives and rendered evidence are concrete.

## Stable architecture facts

- `co-design-ui` is a separate automatically discoverable skill in the existing Johnny plugin.
- The no-external-tool path is first class: design brief, tokens, reference markup and rendered
  screenshots remain target-owned.
- Visual directions differ structurally, not only by palette. The owner selects one before regime
  sealing or implementation ticketing.
- Feature contracts preserve component, finite-state, responsive, accessibility, asset and
  interaction boundaries from the sealed regime.
- A separate reviewer evaluates actual rendered output. Figma/image/craft tools are optional ports.

## Data and effect flow

```text
target product facts
  -> strict design brief
  -> direction candidates + bounded visual evidence
  -> owner selection
  -> sealed target-owned UI regime
  -> feature UI contract
  -> separate implementation
  -> rendered state/breakpoint evidence
  -> adversarial visual review + owner acceptance
```

Kept artifacts live in the target repository. Optional provider payloads, credentials, raw prompts
and unrestricted tool output do not enter Router state, Context or review evidence.

## Boundary

This draft is not sealed. It authorizes no provider access, image generation, Figma write, UI
implementation, publication, installation or release.
