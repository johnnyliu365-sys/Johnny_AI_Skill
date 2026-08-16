# Receipt-bound Role Supervision Revision 06 — R03-00 immutable admission recovery

| Field | Value |
| --- | --- |
| Lifecycle | `OWNER_APPROVED / SENIOR_BRIDGE_02_REVIEW_REQUIRED / NO_SUCCESSOR_TICKET_YET` |
| Requirement | `PRD-20260816-030` / `CHG-20260816-030` |
| Context | `doc/context/receipt-bound-role-supervision/revisions/rev07-r03-00-immutable-admission.md` |
| Parent SPEC | `SPEC-AI-WORKFLOW-RECEIPT-BOUND-ROLE-SUPERVISION-20260815-01M0R2S4T6V8X0Z2B4D6F8H0J2` Revision 05 |
| Successor bridge | `BPB-R03-00-20260816-002` |

## Problem statement

The first R03-00 bootstrap delivery named registry
`e0a710d217624cd90f902e14fe216d945e5ef0fa`. That registry's immutable ticket source says
`BLOCKED / NON_DISPATCHED`, so the Implementer correctly rejected the work before mutation. The
later bridge and grant were not part of that ticket's admission source and could not override it.
The grant also named baseline `104d354e753c36c58509169fc70ead31c103b2c1`, which predates the
grant and attempt; a fresh branch from that baseline could not read those authority artifacts.

## Acceptance contracts

### AC-48 — Immutable historical fence

The following are append-only historical evidence and never dispatch authority for a new attempt:

- ticket closure `R03-00-CS-01` and registry
  `e0a710d217624cd90f902e14fe216d945e5ef0fa`;
- `BPB-R03-00-20260816-001` and review/clarification records `CR-BPB-R03-00-001` through `003`;
- `BDG-R03-00-20260816-001`, `BDA-R03-00-20260816-001` and
  `BDR-R03-00-20260816-001`, including claim commit
  `a7cb3d011594f4a08cfa7a925ae7888231ed381d` and delivery commit
  `336238ed71c24dc0487013775cb269d884d186ce`; and
- Implementer return turn `01a00a4f-4ce7-7d03-8b42-6bbaff6bf2b1`.

No artifact is edited, superseded in place, retried or interpreted as incomplete authority. The
consumed grant remains consumed.

### AC-49 — Exact successor bridge

`BPB-R03-00-20260816-002` is the only successor policy bridge. It binds project
`AI控制工作workflow`, ticket `R03-00-policy-correction-prerequisite` and future closure
`R03-00-CS-02`. It cannot bind a ticket blob before the Senior creates that immutable source.
Bridge approval permits only independent Senior review. BPB-001 cannot cover the revised closure,
and BPB-002 cannot cover R03-01A through R03-01D or another project.

### AC-50 — Ticket source admits its own exact route

Only after the exact BPB-002 commit has an independent `APPROVED` Senior review may the Senior
create an additive `R03-00-CS-02` ticket/admission source. Its state is exactly:

```text
ADMITTED_FOR_BPB_ROUTE / HIGH_ASSURANCE_REQUIRED / OWNER_GRANT_REQUIRED
```

The source must not contain `BLOCKED`, `NON_DISPATCHED` or
`BOOTSTRAP_POLICY_BRIDGE_MISSING`. It must bind the actual Senior-selected implementation owner,
task, opaque worktree, branch, model/profile, ContextView, writable scope, TDD matrix and expected
return. A placeholder identity is not admitted.

### AC-51 — Additive registry and admission preflight

The Senior creates new direct-child ticket, decision and registry leaves without modifying any
CS-01 leaf or prior index entry. The new registry commit binds the exact CS-02 path, Git blob ID,
SHA-256 digest, closure, BPB-002 reference and execution bindings. Strong-type/source preflight
must prove the ticket state, bridge review, blob/digest and bindings agree before a grant can be
drafted. A missing or mismatched value returns `HALT / ROUTE_REFERENCE_INVALID` before effect.

### AC-52 — Claim-introduction execution baseline

The successor grant binds the exact CS-02 registry/blob/digest and declares:

```text
baseline_rule=CLAIM_INTRODUCTION_COMMIT
```

It does not embed an earlier `expected_baseline_commit`. After project-owner approval of that
exact grant, the Senior commits one immutable consuming attempt. The Git commit that first
introduces the attempt is derived by authoritative Git readback and is the exact branch baseline.
It must be a descendant of the CS-02 registry and contain the exact BPB-002 review, ticket registry,
grant and attempt bytes. The attempt leaf does not embed its own commit hash.

The one-shot identifiers-only dispatch envelope includes the derived `claim_commit` and the
Implementer validates that it equals the attempt introduction commit before branch creation or
source mutation. Missing ancestry, bytes, grant approval or exact readback returns a finite halt.

### AC-53 — Manual bridge only

The Senior remains the sole Agent-to-Agent orchestrator. After a valid claim, exactly one host
delivery call is permitted. The route does not issue a receipt, create a live pending descriptor,
register a subscription, prove the Router is normal-active or auto-dispatch any later ticket.
R03-01A through R03-01D remain blocked until R03-00 is independently reviewed and integrated.

### AC-54 — Assurance and model binding

`HIGH_ASSURANCE_REQUIRED` selects the assurance lane, not a hard-coded model. Senior applies the
approved delivery profile and records one exact model/tier/effort in CS-02. The later grant must
match it and the project owner approves that exact execution binding. A model change requires a
new ticket/admission or separately lawful correction; it cannot be inferred at dispatch.

### AC-55 — Ordered authority chain

The only legal order is:

1. Architecture commits owner-approved Revision 06 and BPB-002;
2. Senior independently reviews that exact bridge commit;
3. after `APPROVED`, Senior creates and preflights CS-02 plus its new immutable registry;
4. Senior drafts one exact successor grant;
5. project owner approves that exact committed grant;
6. Senior commits one consuming attempt and derives its introduction commit;
7. Senior performs one host call with the derived claim commit; and
8. user relay may later wake Senior for one return readback under the existing manual rule.

Skipping, reordering or deriving authority from chat text returns a typed halt. Architecture owns
steps 1 only; Senior owns steps 2–4 and 6–8; the project owner owns step 5.

### AC-56 — Resource and effect boundary

No heartbeat, automation, cron, watchdog, active-turn wait, recurring thread/Git/filesystem read,
timed polling, helper lane, push, release or deployment is authorized. This recovery adds only
target-owned committed governance metadata until a later separately approved one-shot grant.

## Approval record

- Architecture/Grill decision: successor immutable admission plus claim-introduction baseline.
- Project owner decision/date: `APPROVED` / `2026-08-16 (Asia/Taipei)`.
- Approval effect: seal Revision 06 and route only the exact BPB-002 commit to independent Senior
  review. It creates no CS-02 ticket, registry, grant, attempt, host call or implementation effect.
