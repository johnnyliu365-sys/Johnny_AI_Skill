# Executor Routing Context — Revision 02

| Field | Value |
| --- | --- |
| Feature cluster | `executor-routing` |
| Artifact | `CTX-EXECUTOR-ROUTING-20260823-02` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED` |
| Authority / change | Project owner directive, 2026-08-23 (Asia/Taipei) / `PRD-20260822-032` / `CHG-20260822-032` |
| Replaces | `CTX-EXECUTOR-ROUTING-20260822-01`; the revision-01 leaf remains sealed historical evidence. |
| Shared baseline | `c69bb29954cea884513fb1d8b53dd9a04f5f0f3c` |
| Responsibility boundary | Provider-neutral profile data and a pure route resolver; POC manual reviewer orchestration records its evidence without asserting host workspace/profile readback. |
| Forbidden changes | Host launch, credential acquisition, receipt issuance/consumption, task/worktree creation, runner lifecycle, integration, automatic wake, or implementation source. |

## Stable facts revised under CHG-20260822-032

- `delivery_stage` is `POC`. P8R is a bounded feasibility closure, not a host-capability
  project.
- P8R's workload assessment is `STANDARD`, derived from `single_component` change surface,
  `known_domain` uncertainty, reversible recovery, no security surface and no external effect.
  The profile must be recorded in the replacement ticket; the prior `HIGH_ASSURANCE` label was
  not a substitute for that evidence-backed assessment.
- The normal implementation/review mapping is Luna/xhigh and Terra/xhigh respectively. The
  reviewer-strength invariant and the ticket-local Terra/Sol elevation rule remain unchanged.
- The resolver remains a pure domain service: injected routing-table and profile-registry inputs
  become one selected profile/review binding or a finite rejection. It reads or writes no host,
  receipt, task, workspace, Git, runner, credential or provider state.
- The current host cannot read back an implementation task's effective workspace/profile/effort/
  capability rank. Record that only as
  `KNOWN_GAP_WORKSPACE_BINDING_READBACK_UNAVAILABLE`; do not turn a task prompt, shell directory,
  model label, CLI login, runner state, or self-report into proof.

## POC evidence and ownership boundary

For the replacement P8R ticket, the reviewer owns manual orchestration and must preserve the
exact approved ticket boundary. The applicable document-mutation gate remains the integration
authority. Before accepting/integrating a candidate, the reviewer personally runs one
counter-mutation through a test path independent of the implementer's recorded mutations.

That POC evidence proves the ticket closure and test quality. It does not prove a host workspace
binding, consume a receipt, create a task, or claim automatic delivery/wake. Any such assertion
is outside this Context and fails closed. The ticket may not reintroduce a host-gateway
prerequisite merely to make this bounded resolver dispatchable.

## Composition and downstream artifacts

- `ExecutorRoutingResolver` receives only `ExecutorRoutingTable`, `ExecutorProfileRegistry` and
  `RouteRequest`; tests provide fakes for both injected data boundaries.
- `modules/spec/executor-routing.md` must be revised to bind this Context, record the POC stage
  and `STANDARD` assessment, and keep every host/effect port out of the resolver.
- The current P8R leaf is `APPROVED_NOT_DISPATCHED` under the superseded admission assumptions.
  A replacement ticket must bind this Context and `CHG-20260822-032`; it is the only future
  implementation authority.
- A later host-adapter task remains separate. If it crosses the privileged host boundary, it is
  `HIGH_ASSURANCE` and must satisfy the R07 readback rules without using this POC known gap as
  success evidence.

## Seal and provenance

- Shared Context reference: `CONTEXT.md`, stable-fact fingerprint `e8eabdd8`.
- Requirement lineage: `PRD-20260822-030` / `CHG-20260822-030`, amended by
  `PRD-20260822-032` / `CHG-20260822-032`.
- This revision supersedes the feature-local policy facts in
  `codex-provider-neutral-executor-routing.md`; it does not alter that sealed leaf.
