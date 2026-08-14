# ADR-20260814-011 — Tiered Model Router Lifecycle and Optional Design Sources

## Status

`ACCEPTED / ROUTER_PHASE_AUTHORIZED`

## Context

The Router POC already closes workflow transitions, metadata-only state, receipts and bounded
continuation, but it does not yet express the intended capability handover. A highest-capability
model should converge architecture and the SPEC with the human owner, a persistent supervisor
should compile the approved SPEC into small tickets, and a lower-cost implementation model
should spend its context on one complete implementation closure. Without explicit readiness,
wake and ticket-admission states, the supervisor or implementer would have to infer missing
design decisions, recreating the long-context and rework problem this workflow is meant to
avoid.

UI work also has several legitimate design sources. Treating Figma as mandatory would make a
third-party integration an installation prerequisite even when a screenshot, design brief or
existing design system is sufficient.

## Decision

1. `ProjectWorkflowProfile` binds semantic roles to versioned opaque model/capability refs.
   The current default mapping is highest-capability architecture owner, Terra
   supervisor/reviewer and Luna implementation owner. Model identity never grants authority.
2. The architecture owner may sleep only after a typed SPEC-readiness gate proves one exact
   owner-approved SPEC revision has closed public contracts, state/error meanings, ownership,
   effects, security/UI classifications, rollback and acceptance.
3. The supervisor acts as a compiler over that SPEC. It may split or normalize closed meaning,
   but may not invent requirements, resolve architecture ambiguity or weaken AC.
4. Low-model ticket admission has four finite results: `READY_LOW_MODEL`, `SPLIT_REQUIRED`,
   `UPSTREAM_DECISION_REQUIRED` and `HIGH_ASSURANCE_REQUIRED`.
5. Requirement/contract/architecture conflicts, unprovable AC, new external boundaries,
   high-assurance triggers and bounded convergence failure wake the architecture owner through
   the Router. The implementer never controls another Agent.
6. Figma is an optional design source. The Router classifies source kind and capability state,
   and can continue with an approved screenshot, brief or existing design system. It never
   forces installation. Missing required visual input waits for the owner; an inaccessible exact
   Figma node halts only when the approved SPEC explicitly requires it.
7. UI tickets remain vertical observable component/frame slices containing markup, styling,
   responsive states and behavioral states together. Runtime renderer data, not design metadata
   alone, determines the XSS gate.
8. Router policy/source implementation is completed and independently accepted before any
   adaptive-bootstrap, packaging or other subsequent feature/rework ticket resumes.

## Consequences

- High-cost architecture reasoning can sleep after a provable handover and wake only on typed
  design conditions.
- Terra can decompose deterministically without carrying the whole discovery conversation.
- Luna receives a complete small contract instead of an underspecified task.
- Design-tool availability changes the input route, not the governance baseline.
- The current 06G0P implementation return remains immutable and pending review; its review,
  integration and dependent 06G tickets pause until the Router phase is accepted.
- Exact provider model names remain replaceable Profile mappings and can change without
  changing policy or authority.

## Rejected alternatives

- Let the supervisor infer missing SPEC details: rejected because it collapses architecture and
  implementation authority and makes later review discover requirements.
- Make Figma mandatory for UI: rejected because the capability is optional and not every project
  has or authorizes it.
- Split by file count, line count or frontend/backend layer: rejected because those units do not
  produce independently observable closure.
- Continue packaging/installer tickets while changing Router policy: rejected because new work
  would be dispatched through a known-incomplete control contract.
