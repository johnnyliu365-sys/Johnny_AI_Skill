# Review assurance — Grill Context

| Field | Value |
| --- | --- |
| Context state | `GRILL_COMPLETE_TO_SPEC` |
| Router event | `REQUIREMENT_CHANGED` — owner-authorized review/deployment assurance expansion on 2026-08-27 |
| Delivery stage / profile | `POC / HIGH_ASSURANCE` — the source slice changes controls for release, deployment and external-effect evidence, even though it performs none. |
| Requirement | `PRD-20260827-042` / `CHG-20260827-042` |
| Baseline | `ac68374546d3f324ca60c175014e7eb6bf2751f9` |
| Owner / reviewer | Project owner / current supervisor reviewer |
| Implementation owner | Reused low-tier implementation owner only after Ticket 01 admission; reviewer remains the sole conclusion and integration authority. |

## Confirmed facts

- `CodeReview.md` already requires reviewer-owned reverse mutation. It does not permit that evidence to be replaced by another Agent's claim.
- `delivery-profile.md` requires adversarial verification and an adversarial review record at `HIGH_ASSURANCE`, but does not define the auditor's scope, finite return, availability semantics or deployment attack matrix.
- `model-role-routing.md` already supplies the only suitable delegated role: the reviewer-owned, read-only/no-code `RESEARCH_HELPER`. No new Agent authority role, runner, queue, receipt issuer or host gateway is needed.
- A same-lifetime reviewer dispatches, waits, receives and reviews directly. Its bridge disposition is `NOT_REQUIRED`; receipt, live descriptor, runner and host readback remain exclusive to the cross-lifetime route.
- A host cannot be assumed to physically enforce a helper's read-only intent. Therefore the reviewer binds the auditor to an immutable candidate identity, records the isolation capability honestly, and re-reads the candidate/worktree state before relying on its return. Missing isolation is never reported as isolation.
- Production data, real accounts, credentials, migrations, release and deployment are external effects. A review request cannot confer those authorities, and evidence must remain sanitized and metadata-only.

## Grill decisions

| Question | Decision |
| --- | --- |
| Does every ticket require a second model? | No. The reviewer may choose an auditor for `COMPACT` and `STANDARD` tickets from risk evidence. `HIGH_ASSURANCE` requires the adversarial record; unavailable required evidence blocks the review rather than being fabricated. |
| Who owns the verdict? | The reviewer alone. An auditor may return `FINDINGS`, `NO_FINDINGS`, `BLOCKED`, `UNAVAILABLE` or `NOT_APPLICABLE`; it cannot change code, issue an approval, decide integration, route the workflow or perform an effect. |
| What is the dispatch model? | One reviewer-owned, bounded same-lifetime helper invocation followed by one completion wait. It has no cross-lifetime receipt/descriptor/runner dependency. |
| What must be attacked? | Every selected review plan covers requirement gaps, boundary data, state transitions, concurrency, errors, authorization, consistency, idempotency, regression and observability. The deployment matrix adds only the listed operational/data vectors whose applicability is evidenced. |
| May an auditor test a production system? | No, unless a separate target-specific ticket and exact owner authority admit that one bounded action. Otherwise it identifies the missing proof as `NOT_AUTHORIZED` or `BLOCKED`; it never substitutes a claim. |
| How is non-applicability kept honest? | Every matrix row is `APPLICABLE`, `NOT_APPLICABLE`, `BLOCKED` or `NOT_AUTHORIZED`; `NOT_APPLICABLE` names the inspected candidate surface that excludes it. |

## Alternatives rejected

1. **Make an auditor mandatory for every ticket.** Rejected: it turns a risk-scaled control into ceremony and needlessly blocks deterministic compact work.
2. **Let the auditor approve or merge.** Rejected: it duplicates the reviewer gate and confuses an attack finding with the accountable conclusion.
3. **Treat all missing audit capabilities as a runner failure.** Rejected: same-lifetime review needs no runner; required evidence is either present or honestly `BLOCKED`.
4. **Use production data or real accounts by default.** Rejected: a test is still an external effect and cannot bypass the project's security/owner boundary.

## Convergence

The Grill result is **GO to specification**. The resulting policy implementation is source-only:
it changes governance documents, one pinned policy digest and regression tests. It creates no
runtime worker, provider call, local queue, release, deployment, migration, secret access or
target-project mutation. A later plugin publication remains a separate effect.
