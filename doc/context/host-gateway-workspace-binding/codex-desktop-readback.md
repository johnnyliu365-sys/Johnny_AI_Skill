# Host Gateway Workspace Binding Context

| Field | Value |
| --- | --- |
| Feature cluster | `host-gateway-workspace-binding` |
| Agent / worktree | Codex / `control/executor-routing-p8-owner-override` |
| Shared baseline | `db936db802a0c12decb28c40ea58aed228a962d1` |
| State | `SEALED / CTX-HOST-GATEWAY-20260822-01` |
| Responsibility boundary | Reviewer-owned, receipt-bound host capability/readback admission for a prospective implementation task; no provider or task effect in this architecture action. |
| Forbidden changes | Provider login/invocation, credential storage, task creation, message delivery, receipt consumption, runner/subscription/wake lifecycle, Git/worktree creation, P8R source, and shared `CONTEXT.md` mutation. |

## Shared Context reference

- Shared baseline commit: `db936db802a0c12decb28c40ea58aed228a962d1`
- `CONTEXT.md` section: `Stable project facts and boundaries`
- Reference fingerprint: `e8eabdd8` (the bounded section is unchanged from the prior sealed reference)
- Line span (non-normative): 6-37

## Existing artifact preflight

| Artifact | State | Reuse / no-rewrite boundary | This change |
| --- | --- | --- | --- |
| `modules/spec/adaptive-project-orchestration.md` Revision 06, AC-03/AC-04 | Approved but contract-incomplete | Defines isolated workspace and reviewer-first activation; does not define the strict host-readback algebra. | Amend as the sole downstream SPEC lineage. |
| `modules/tickets/adaptive-project-orchestration/project-isolation/r06-project-isolation-upstream-decision.md` | `UPSTREAM_DECISION_REQUIRED / NON_DISPATCHABLE` | `TAD-ADAPTIVE-R06-ISOLATION-01` requires a workspace/readback contract before any ticket. | Reuse as the admission dependency; do not dispatch it. |
| `library/workflow_router/thread_host_contracts.py` and `library/local_orchestration/codex_thread_host_binding.py` | Existing pure binding primitives | Validate strict directory/readback payloads, normalize workspace comparison, and retain only digests in the public binding. | Reuse their public contract direction; do not broaden their host effect boundary in this action. |
| `library/local_orchestration/codex_thread_dispatch.py` | Existing one-shot delivery composition | A host send is receipt-bound and occurs after binding. | Remain downstream; no delivery adapter is authorized yet. |
| `modules/tickets/workstation-dispatch/p8-provider-neutral-executor-routing.md` | Approved, not dispatched | Pure profile resolver and its ticket-local owner override remain unchanged. | Re-evaluate only after a compatible gateway is admitted. |

## Confirmed facts and architecture decision

- The current desktop host supplies a typed directory response and an exact-thread readback
  response matching the existing binding adapter's schema families. The project registry also
  identifies this repository as a Git project. These observations are transient; raw paths,
  titles, prompts, and host payloads are not stored here.
- The current control thread has no host project identity. It therefore cannot satisfy the
  binding adapter's non-null project requirement and must fail closed rather than be reused as
  an implementation task.
- Existing thread readback contains task/thread, host, project, activity and workspace data, but
  does not prove the task's effective model, effort, or verified capability rank. A model request
  or tool configuration is an assertion, not capability evidence.
- The generic collaboration subagent interface likewise cannot supply the required active
  workspace and effective-profile readback. It is not a fallback transport for this gateway.
- The selected architecture is a provider-neutral two-layer boundary:
  1. a no-effect `HostCapabilityReadbackPort` normalizes project-directory, exact-thread and
     effective-profile evidence into strict transient values;
  2. a reviewer-owned admission coordinator compares that evidence with Git worktree identity
     and the live descriptor, then returns one metadata-only binding or a finite failure.
- A later, separate receipt-bound host-control port may create/reuse a task or deliver an
  identifier-only handoff only after the coordinator returns a valid binding. It must not use
  the architecture probe as authority to create a task.
- Workspace proof must satisfy all three existing admission checks: normalized absolute root,
  resolved filesystem identity, and Git linked-worktree/registered metadata. Path equality alone
  is insufficient.
- Selected profiles remain semantic references from the provider-neutral resolver. The gateway
  may bind them only to host-read effective capability evidence; unavailable, stale, absent or
  weaker-reviewer evidence returns a named rejection with no fallback.

## Required contract families and failure precedence

The Revision 06 amendment must define these public, frozen contract families before any
implementation ticket:

1. `HostCapabilityReadbackRequest` / `HostCapabilityReadbackResult`: exact host/project/task
   identity, finite availability status, effective profile reference, effective effort and
   verified capability-rank evidence. Missing or malformed host output is
   `CAPABILITY_UNAVAILABLE` before a task, source, receipt or Git effect.
2. `WorkspaceIdentityVerificationRequest` / result: transient path normalization plus resolved
   filesystem and Git-metadata proof; the durable result carries opaque workspace/worktree refs
   and evidence digest only. Directory/readback disagreement is `TASK_WORKSPACE_MISMATCH`.
3. `ReceiptBoundHostAdmissionRequest` / result: reviewer capability, exact approved artifact,
   unconsumed receipt, descriptor correlation, profile readback and workspace proof. Identity or
   replay failures precede all host-control effects; a successful result exposes only a narrowly
   scoped downstream port.

At the current host capability level, absence of effective-profile readback is an expected
finite `CAPABILITY_UNAVAILABLE` result. It is not an error to be bypassed with a prompt, CLI
login, static model label, agent self-report, runner state, or owner message.

## Threat and failure matrix

| Threat / failure | Required response | Effect permitted |
| --- | --- | --- |
| Unavailable, malformed, stale or ambiguous directory/readback | Named capability failure | None |
| Current or candidate task lacks project identity | `PROJECT_REQUIRED` / capability failure | None |
| Workspace path, filesystem identity or Git metadata disagrees | `TASK_WORKSPACE_MISMATCH` | None |
| Effective profile/rank absent, stale, unavailable or below review binding | `CAPABILITY_UNAVAILABLE` or reviewer-capability rejection | None |
| Receipt, correlation, task, branch or baseline replay/mismatch | Named admission rejection | None |
| Directory and exact readback change between observations | `READBACK_MISMATCH` | None |
| Valid admitted binding followed by one host delivery call | Existing one-shot dispatch composition determines settlement | Only that receipt-bound delivery effect |

## Approved decision and downstream binding

- `TAD-ADAPTIVE-R06-ISOLATION-01` requires an approved Revision 06 SPEC amendment (or linked
  ADR with that amendment) to close the three contract families and declare their serial
  dependency. A standalone host-gateway SPEC is not an admissible substitute.
- The project owner approved the exact amended parent SPEC on `2026-08-22`.
  The approved draft-content baseline is
  `1897339679312d92944403747aa7a2b1595d9c3e`; this Context is now sealed as its
  supporting architecture reference. The reviewer may decompose only the first
  no-effect strict-contract/readback closure; implementation still requires that
  ticket's own approval and receipt.
- P8R remains `APPROVED_NOT_DISPATCHED`; it gains no receipt, worktree, task, source or provider
  authority from this draft.

## Seal and downstream binding

- Feature Context revision: `CTX-HOST-GATEWAY-20260822-01` / `SEALED`
- Shared Context sealed revision/digest: `CONTEXT.md` / `e8eabdd8` reference span
- PRD / requirement change: `PRD-20260822-031` / `CHG-20260822-031`
- Required downstream artifact: approved amendment to
  `SPEC-AI-WORKFLOW-ADAPTIVE-PROJECT-ORCHESTRATION-20260813-01M0A2C4E6G8J0L2N4P6R8T0V2`
  Revision 06.
- The project owner approved the exact Revision 07 draft content on `2026-08-22` at
  `1897339679312d92944403747aa7a2b1595d9c3e`; this record is the resulting
  seal-only authority transition. Later changed host capability or external effect
  requires a new change-controlled architecture revision.
