# Executor Routing Context

| Field | Value |
| --- | --- |
| Feature cluster | `executor-routing` |
| Agent / worktree | Codex / `codex/provider-neutral-executor-routing` |
| Shared baseline | `0fc6bbf05e2f5cd970f5b97b1386811b3fed401d` |
| State | `SEALED / CTX-EXECUTOR-ROUTING-20260822-01` |
| Responsibility boundary | Provider-neutral executor/reviewer profile data, pure route resolution, availability admission, ticket-local hard-elevation and reviewer-strength validation. |
| Forbidden changes | Host launching, credential acquisition, receipt issuance/consumption, task/worktree creation, runner lifecycle, integration, source implementation and global/shared Context mutation. |

## Shared Context reference

- Shared baseline commit: `0fc6bbf05e2f5cd970f5b97b1386811b3fed401d`
- `CONTEXT.md` section: `Stable project facts and boundaries`
- Reference fingerprint: `e8eabdd8` (the referenced section at the baseline)
- Line span (non-normative): 6-37

## Existing artifact preflight

| Artifact | State | Reuse / no-rewrite boundary | This change |
| --- | --- | --- | --- |
| `modules/spec/adaptive-project-orchestration.md` | Approved earlier phase | Role authority, typed Profile concept, reviewer-only orchestration and wake semantics remain authoritative. | Reuse; do not revise in place. |
| `modules/tickets/workstation-dispatch/p8-routing-is-data-not-a-runbook.md` | Unbound / not dispatched | Historical diagnosis and boundary declaration remain evidence only. | Supersede; do not dispatch. |
| `doc/runbooks/dispatch-model-profile.md` | Current host mapping | Current values are not executable routing authority. | Replace only after this SPEC is approved. |

## Confirmed facts and constraints

- Provider/model/effort identity never grants a workflow role, receipt, source-write or integration authority.
- The human owner remains `ARCHITECTURE_OWNER`. Sol/high is selected only for project-initial review, requirement-change review that needs a complex-decision inventory, or a one-ticket reviewer uplift when Terra implements. It is never the normal ticket-opening or implementation profile.
- Terra/xhigh is the intended current Codex profile for normal ticket opening and independent review. Luna/xhigh is the normal implementation profile. A closed hard-ticket assessment may elevate implementation to Terra/xhigh and must bind that same ticket's reviewer to Sol/high.
- Every implementation plan has one reviewer profile whose verified capability rank is greater than or equal to the implementation profile's rank. The profile registry supplies those ranks as capability data; model names are not the comparison mechanism.
- Johnny Router `0.4.9` is installed and its launcher status is `OK`; runner automation is not armed for this repository.
- The Codex CLI is available. Claude Code CLI is installed, but its credential capability is currently unavailable; no Claude executor profile is selectable or dispatched from this fact.
- Capability state is an explicit routing input. Missing, stale, ambiguous or unavailable capability evidence rejects the route; it never falls back to another profile.
- Credentials, token values, raw host configuration, host command output and provider payloads are outside this Context and outside durable routing state.
- A pure resolver may return a profile reference only. A later, separately approved host-adapter boundary is responsible for invoking a provider.

## Approval and downstream dependencies

- The owner approved `SPEC-AI-WORKFLOW-EXECUTOR-ROUTING-20260822-01M4P6R8T0V2X4Z6B8D0F2H4J6` on 2026-08-22 (Asia/Taipei). This seals this Context revision and authorizes reviewer decomposition only.
- A future host-profile/adaptor ticket must prove each provider's credential and invocation capability separately; Claude authentication remains owner-guided user action.
- No automatic second implementation elevation is configured. If the ticket's bounded implementation/review cycle is insufficient, the Router returns the typed architecture-owner route rather than selecting another implementer by inference.

## Seal and downstream binding

- Feature Context revision: `CTX-EXECUTOR-ROUTING-20260822-01` (sealed; downstream artifacts bind this file through the exact approved baseline commit).
- Shared Context sealed revision/digest: `CONTEXT.md` / `e8eabdd8` reference span.
- PRD / requirement change: `PRD-20260822-030` / `CHG-20260822-030`.
- Emitted SPEC: `SPEC-AI-WORKFLOW-EXECUTOR-ROUTING-20260822-01M4P6R8T0V2X4Z6B8D0F2H4J6` / `modules/spec/executor-routing.md`.
- This Context is invalidated by a profile-policy change, provider capability change, new host effect or approved requirement change.
