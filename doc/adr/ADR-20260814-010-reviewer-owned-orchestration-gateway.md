# ADR-20260814-010 — Reviewer-owned Johnny Orchestration Gateway

## Status

`ACCEPTED`

## Context

The project requires the named reviewer to be the only Agent that can create,
dispatch, steer, wait for, interrupt or close an implementation task. The
first design relied on separate Codex reviewer and implementation profiles.
Ticket 06A proved that their static schemas can be represented, but the current
installed desktop-host path cannot provide the supported effective-session
readback needed to prove the tool difference: direct invocation of its bundled
Codex executable is access-denied, and the exposed App task-creation contract
does not bind a custom-agent profile.

A prompt, model name or profile file is not an authority boundary. Conversely,
discarding host least privilege would leave a second orchestration surface in
the implementation session even if the product Router rejected its own calls.

## Decision

1. Johnny's local control plane owns the single orchestration gateway and all
   Agent-control effect ports. It is transport-agnostic and introduces no
   network or MCP service in this POC.
2. A named reviewer receives a consumable `ReviewerGatewayGrant` only after the
   Router matches one live `PendingDispatchDescriptor`. Every effect validates
   project, ticket, reviewed handoff, receipt, target implementation owner,
   worktree, branch, expected baseline, action and correlation.
3. An implementation owner receives no gateway port, credential or alias. Its
   effective host session must additionally remove/disable built-in
   multi-agent and thread-control tools through a supported host configuration
   and launch transport. Both controls are required.
4. Direct built-in calls, indirect adapters, MCP aliases, copied or forged
   grants, replay, role substitution and any binding mismatch fail before the
   host fake or real host effect with `HALT / ROLE_FORBIDDEN` or the exact typed
   receipt/baseline error.
5. Static config bytes are only candidate configuration. Support is projected
   only after a disposable effective-session test proves the exact restricted
   implementer is bound to the exact worktree and lacks the forbidden tools.
   Missing launch/profile binding or effective readback remains
   `INSTALL_BLOCKED / ROLE_ISOLATION_UNPROVEN`.
6. Profile and gateway lifecycle artifacts become installer-owned only after
   exact digest/readback receipts. Removal deletes only receipt-matched owned
   artifacts and preserves foreign/global host state and target repositories.

## Consequences

- Authority becomes centralized, finite and auditable instead of being spread
  across prompts and host-specific tool surfaces.
- Defense in depth is explicit: gateway non-possession does not replace host
  tool removal, and host tool removal does not replace gateway authorization.
- The current inaccessible desktop CLI and profile-unaware App creation surface
  are blockers to be measured by a small transport proof, not worked around by
  undocumented configuration or synthetic green evidence.
- 06A remains valid historical evidence. 06B/06C are superseded; 06G0P-06G4
  replace them. Dispatch preflight requires 06G0P to close the 06A result-state
  defect before 06G0 can measure a transport.
- Package, installation and staging work remain blocked until the new sequence
  is independently approved and integrated.

## Rejected alternatives

- Prompt-only reviewer/implementer instructions: rejected because the
  implementation session still possesses the capability.
- Profile-only enforcement: rejected because the current supported launch path
  cannot prove which profile is effective in the created task.
- Gateway-only enforcement while leaving implementer built-in tools enabled:
  rejected because it creates an uncontrolled second orchestration route.
- Undocumented host-config edits or a new network/MCP service: rejected because
  they expand scope and cannot provide the required owned removal proof.
