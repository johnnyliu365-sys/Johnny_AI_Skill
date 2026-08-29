# ADR-20260829-037 — Designerless UI co-design

- Date: `2026-08-29 (Asia/Taipei)`
- Status: `PROPOSED / OWNER_EXACT_APPROVAL_PENDING`
- Decision maker: Project owner
- Related change: `PRD-20260829-049` / `CHG-20260829-049`
- Extends: the optional design-source handoff without making a design provider mandatory.

## Context

The current workflow can consume a Figma node, screenshot, design brief or existing design system,
but it does not help an owner create an attractive, coherent visual source when no designer exists.
Stopping at `UI_DESIGN_SOURCE_REQUIRED` is correct when implementation is about to begin, yet a
separate design-craft stage can create candidates before that gate.

## Proposed decision

Ship an automatically discoverable `co-design-ui` skill to Codex and Claude Code with one shared
artifact contract and a bounded co-design loop:

```text
product/brand brief
  -> visual and interaction constraints
  -> at least two materially different rendered directions
  -> owner selects one
  -> target-owned UI regime is sealed
  -> per-feature UIImplementationContract
  -> implementation by a separate owner
  -> responsive/state/accessibility screenshots
  -> adversarial visual review
  -> owner acceptance
```

The skill may use an authorized Figma, image-generation or design-craft capability, but each is an
optional port. With no external capability it produces target-owned design briefs, tokens,
reference markup and locally rendered screenshots. Generated output is a proposal until the owner
selects it. Selection seals typography, colour, spacing, component language, breakpoint, motion and
interaction conventions so later tickets cannot silently reinvent them.

## Responsibility and composition map

- `UICodesignRouter` owns stage transitions and exact owner-decision waits only.
- `DesignBriefCompiler` normalizes product, audience, brand, accessibility and platform facts into
  one strict target-owned brief.
- `DesignCraftPort` optionally proposes or audits visual directions; its state/tier/target are
  classified before use.
- `ReferenceRendererPort` emits bounded target-platform candidates and screenshots. It cannot
  approve them or write production UI.
- `UIRegimeSealer` writes the owner-selected cross-feature regime and exact source references.
- `UIContractCompiler` creates one feature's component/state/responsive/accessibility contract.
- `VisualVerificationPort` reads actual implemented output at declared breakpoints and produces
  findings only; the reviewer owns the conclusion.

## Consequences

- A product owner can reach an implementation-ready visual source without Figma or a designer, but
  still makes the subjective direction decision.
- Design iteration happens before implementation authority. Implementation tickets consume the
  sealed regime rather than experimenting with new styles.
- The skill needs realistic behavioral forward-tests: zero-tool brief, optional image craft,
  authorized Figma, existing-design-system and implementation-review cases.
- Codex and Claude Code require independent skill-discovery and behavioral qualification. Neither
  host's output or invocation trace qualifies the other.
- XSS remains based on runtime data/sinks, not the design tool used.

## Alternatives rejected

- **Let each implementer choose styling.** It produces feature-by-feature drift and makes review
  subjective after code is already expensive to change.
- **Require Figma.** It blocks the exact no-designer/no-tool case and creates an unnecessary account
  dependency.
- **Generate one direction and call it approved.** Generation is not owner selection.
- **Let the UI implementer perform final visual approval.** It collapses implementation and review.

## Approval boundary

This ADR authorizes no design provider access, generated media, Figma write, UI implementation,
publication, installation or release. Exact owner approval is required before its first ticket.
