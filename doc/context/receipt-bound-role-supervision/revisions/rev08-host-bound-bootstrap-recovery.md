# Receipt-bound Role Supervision Context Revision 08 — host-bound bootstrap recovery

| Field | Value |
| --- | --- |
| Kind | `CONTEXT_REVISION_LEAF` |
| State | `SEALED / OWNER_APPROVED / SENIOR_CORRECTION_TICKETING_AUTHORIZED` |
| Parent Context | `doc/context/receipt-bound-role-supervision/main.md` Revision 07 |
| Requirement | `PRD-20260817-031` / `CHG-20260817-031` |
| Decision | `ADR-20260817-018` |
| Trigger | `HALT / EFFECT_UNCERTAIN` recorded by `BDR-R03-00-20260817-003` after a wrong-host manager lookup |

## Confirmed facts

- Senior's actual tool call explicitly supplied
  `hostId=slingshot:env_e_6a29e55ede90832fb63e141a9890800a`; it did not omit the optional
  field. The tool failed at `AppServerManager` lookup before resolving a delivery adapter.
- Implementer-2 task `019ffb0c-db88-7303-895c-aecfadde7c8d` is bound to host `local`. Its latest
  turn remained `01a00a4f-4ce7-7d03-8b42-6bbaff6bf2b1`; no BDA-003 delivery appeared.
- From the same Senior context, an explicit read-only call with `hostId=local` resolved
  successfully in diagnostic turn `01a00b6b-0675-7652-a668-f7847e6b1656` and returned target task
  state without any write, message or external effect.
- The direct cause was wrong host selection. The architecture cause was a missing host binding,
  no pre-claim manager admission and an error algebra that treated a pre-manager rejection as an
  ambiguous delivery.
- BDG-003, BDA-003, BDR-003 and settlement commit
  `0b397a08050e435d82632070c2a952c54dcb6d0d` remain immutable. Their original wording records the
  knowledge available at settlement time and is not rewritten.
- Future bootstrap registry/grant/attempt sources bind `target_host_id` from authoritative target
  task readback and prove host-manager resolution before claim.
- Failure before manager/adapter invocation is `PROVED_NO_EFFECT`; ambiguity begins only once the
  delivery adapter may have been invoked.
- For this incident only, one additive correction decision may reclassify the operation and allow
  one same-operation continuation after a Senior correction ticket receives independent approval.
  It uses the existing dispatch ref and claim commit with explicit `target_host_id=local`; it is
  not a new grant or attempt.
- No second host call, new owner grant, BDG-004 or BDA-004 is permitted. Any mismatch or ambiguous
  continuation result halts.
- The bounded shape uses one read-only admission, one delivery and one post-call readback. It adds
  no heartbeat, timer, automation or polling.

## Continuation

The single next governed action is `TICKETS / SENIOR_CORRECTION_TICKET`. Senior compiles SPEC
Revision 07 into one exact correction ticket and obtains independent review. Architecture does
not create that ticket, grant, attempt or host effect. Owner approval of this Context/SPEC already
covers the one same-operation continuation after those gates; no new owner grant is requested.
