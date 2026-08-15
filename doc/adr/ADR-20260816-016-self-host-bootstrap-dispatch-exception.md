# ADR-20260816-016 — Finite self-host bootstrap dispatch exception

- Date: `2026-08-16 (Asia/Taipei)`
- Status: `ACCEPTED`
- Decision makers: project owner and architecture owner
- Related change: `CHG-20260816-027`
- Related specification: Receipt-bound Role Supervision Revision 04

## Context

R03-01 implements the first durable live receipt components required by normal dispatch.
Requiring those already-integrated components before dispatching R03-01 is a circular dependency.
Sending a message and naming it a receipt would be forged authority; weakening normal dispatch
for every project would make the bootstrap defect permanent.

The current host also has no receipt-bound completion subscription. Until the complete R03 chain
is integrated and proven, a human must provide the wake signal without becoming the evidence or
technical decision maker.

## Decision

1. Define one project-specific bootstrap route for this repository and only R03-01, R03-02 and
   R03-03. It cannot be copied to another project or ticket.
2. R03-01 uses an owner-approved `BootstrapDispatchGrant` with no receipt. It is explicitly not
   a `TicketReceipt`, `StageWorkReceipt`, legacy approval transition or claim of live capability.
3. After R03-01 integration, R03-02 and R03-03 use real active `TicketReceipt` authority. A
   separate `BootstrapTransportGrant` bridges only the still-missing dispatch transport.
4. The Senior alone resolves the exact ticket revision and selects/binds owner, task, worktree,
   branch, baseline, model/profile, Context epoch and expected return. Architecture never fills
   those dispatch fields.
5. A grant becomes unusable when the Senior commits its immutable attempt leaf, before calling
   the host. A later immutable result records `DELIVERED`, `NO_EFFECT` or `EFFECT_UNCERTAIN`.
   Crash, timeout, ambiguous exception or missing exact delivery identity is uncertain and may
   not retry under that grant.
6. Every correction uses a new owner-approved one-shot correction/transport grant. R03-02/R03-03
   keep the same live receipt only when standard same-ticket receipt bindings remain unchanged.
7. Before automatic supervision exists, the user sends only a return-available hint plus the
   grant reference. The Senior independently reads committed Git/handoff evidence. Chat content
   is neither authority nor completion proof.
8. An independently approved review may produce a distinct one-shot bootstrap integration grant
   without another ceremonial owner prompt. It binds the exact implementation commit, review
   decision and current main baseline. Correction or mismatch cannot integrate.
9. R03-03 remains high assurance and needs separate ticket-specific approval. Only its reviewed
   integration plus real positive host and supervision readback emits `NORMAL_ACTIVE`.
10. `NORMAL_ACTIVE` permanently closes bootstrap dispatch. Normal Router auto-dispatch then
    applies only to one unique already-approved low/standard ticket with every ordinary gate
    proven. High assurance, external effects, ambiguity, changes and multiple candidates remain
    human decisions.

## Consequences

- The circular dependency is broken without pretending that a Markdown receipt or host message
  is normal live authority.
- Commit-before-effect may conservatively strand an attempt if the process fails before the host
  call. Recovery requires a new explicitly approved grant; duplicate implementation is avoided.
- Bootstrap adds several small target-owned provenance leaves, but no runtime, timer, watcher,
  polling loop or target-project dependency.
- The user temporarily spends one interaction to wake the Senior after each bootstrap return.
  This cost ends only after real R03-03 capability proof.

## Rejected alternatives

- Forge a normal receipt in a prompt or Markdown row: rejected because no live issuer/consumer
  exists.
- Let R03-02 claim the complete normal flow after only R03-01: rejected because R03-02 and R03-03
  still own admission/claim and gateway/supervision capabilities.
- Use bootstrap for every prerequisite without real receipts: rejected because R03-01 makes real
  receipt authority available for R03-02/R03-03.
- Retry after uncertain host result: rejected because the original dispatch may have succeeded.
- Have the architecture owner select or dispatch the Implementer: rejected by role ownership.
- Heartbeat, recurring read or polling: rejected by the standing owner policy.
