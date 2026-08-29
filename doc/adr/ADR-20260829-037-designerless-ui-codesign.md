# ADR-20260829-037 — Designerless UI co-design

- Date: `2026-08-29 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision maker: Project owner
- Related change: `PRD-20260829-049` / `CHG-20260829-049`
- Extends: the optional design-source handoff without making a design provider mandatory.

## Context

The current workflow can consume a Figma node, screenshot, design brief or existing design system,
but it does not help an owner create an attractive, coherent visual source when no designer exists.
Stopping at `UI_DESIGN_SOURCE_REQUIRED` is correct when implementation is about to begin, yet a
separate design-craft stage can create candidates before that gate.

## Decision

Ship an automatically discoverable `co-design-ui` skill to Codex and Claude Code with one shared
artifact contract and a bounded co-design loop:

```text
product/brand brief
  -> visual and interaction constraints
  -> at least two materially different directions with classified evidence
  -> owner selects one
  -> regime candidate enters canonical CONTEXT sealing
  -> per-feature UIImplementationContract
  -> implementation by a separate owner
  -> responsive/state/accessibility screenshots
  -> adversarial visual review
  -> owner acceptance
```

The skill may use an authorized Figma, image-generation or design-craft capability, but each is an
optional port. With no external design-craft capability it produces target-owned design briefs,
tokens and reference markup. A separately classified renderer produces screenshots when available;
artifact-only mode asks the owner to open and acknowledge comparable target-owned references, while
total renderer absence waits with `UI_REFERENCE_RENDERER_REQUIRED`. Generated output remains a
proposal until the owner selects it. The co-design loop runs in `ARCHITECTURE`/`GRILL`; selection
creates a regime candidate, and only the canonical CONTEXT stage under `context-routing.md` seals
the exact owner-approved revision following `ui-design-handoff.md`.

## Responsibility and composition map

- `UICodesignRouter` owns stage transitions and exact owner-decision waits only.
- `DesignBriefCompiler` normalizes product, audience, brand, accessibility and platform facts into
  one strict target-owned brief.
- `DesignCraftPort` optionally proposes or audits visual directions; its state/tier/target are
  classified before use.
- `ReferenceRendererPort` classifies `RENDERED_AVAILABLE`, `ARTIFACT_ONLY` or `UNAVAILABLE` and
  emits only the evidence supported by that state. It cannot approve or write production UI.
- `UIRegimeCandidateCompiler` emits selected identity/digest as bounded input to canonical CONTEXT;
  it cannot seal or write the authoritative revision.
- `UIContractCompiler` creates one feature's component/state/responsive/accessibility contract.
- `VisualVerificationPort` reads actual implemented output at declared breakpoints and produces
  findings only; the reviewer owns the conclusion.

## Consequences

- A product owner can reach an implementation-ready visual source without Figma or a designer, but
  still makes the subjective direction decision. Missing all usable reference evidence waits
  honestly instead of inventing screenshots.
- Design iteration happens before implementation authority. Implementation tickets consume the
  sealed regime rather than experimenting with new styles.
- The skill needs realistic behavioral forward-tests: zero-tool brief, optional image craft,
  authorized Figma, existing-design-system and implementation-review cases.
- Codex and Claude Code require independent skill-discovery and behavioral qualification. Neither
  host's output or invocation trace qualifies the other.
- Behavioral qualification is a fixed five-session evidence set per host/scenario: at least four
  route correctly and all five avoid unauthorized effects/self-approval. Extra retry-until-green is
  forbidden.
- UIX closure emits readiness only; shared `PAQ-REL-01` owns the single composed release effect.
- XSS remains based on runtime data/sinks, not the design tool used.

## Alternatives rejected

- **Let each implementer choose styling.** It produces feature-by-feature drift and makes review
  subjective after code is already expensive to change.
- **Require Figma.** It blocks the exact no-designer/no-tool case and creates an unnecessary account
  dependency.
- **Generate one direction and call it approved.** Generation is not owner selection.
- **Let the UI implementer perform final visual approval.** It collapses implementation and review.

## Approval boundary

This accepted ADR authorizes reviewer opening of `UIX-01` only. Ticket approval and dispatch remain
separate. It grants no design provider access, generated media, Figma write, UI implementation,
publication, installation or release.
