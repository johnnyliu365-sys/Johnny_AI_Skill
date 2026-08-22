# Executor Routing Context — Revision 03

| Field | Value |
| --- | --- |
| Feature cluster | `executor-routing` |
| Artifact | `CTX-EXECUTOR-ROUTING-20260823-03` / `SHARED_CONTEXT_REVISION` |
| Lifecycle | `SEALED` |
| Authority / change | Project owner authority, 2026-08-23 (Asia/Taipei) / `PRD-20260823-033` / `CHG-20260823-033` |
| Replaces | `CTX-EXECUTOR-ROUTING-20260823-02`; revision 02 remains sealed historical evidence. |
| Shared baseline | `cd85017418aaca999c69ba11f81d38bdd64b860d` |
| Responsibility boundary | Provider-neutral profile data, typed assessment verification, and a pure canonicalized route resolver. POC reviewer orchestration records only manual integration evidence and never asserts unavailable host readback. |
| Forbidden changes | Host launch, credential acquisition, receipt issuance/consumption, task/worktree creation, runner lifecycle, provider invocation, integration, automatic wake, or implementation source. |

## Stable facts revised under CHG-20260823-033

- `delivery_stage` remains `POC`; P8R remains a bounded, reversible pure resolver closure with
  `STANDARD` workload assessment. The normal implementation/review mapping remains Luna/xhigh
  and Terra/xhigh; the ticket-local Terra/Sol elevation rule remains unchanged.
- The resolver is a pure domain service. It receives only an injected routing table, profile
  registry, and request and returns a selected semantic profile/reviewer binding or a finite
  rejection. It does not read configuration or write state, and it has no host, receipt, task,
  workspace, Git, runner, credential, provider, or network port.
- Resolver admission canonicalizes its entire injected routing-table graph before its profile-
  registry graph through ordinary strict validation. A malformed table returns
  `ROUTING_TABLE_INVALID`; a malformed registry returns `PROFILE_REGISTRY_INVALID`; no bypass-
  created nested object may establish a selection or leak a validation exception. The current
  table contract treats duplicate route keys as table-invalid; `ROUTE_AMBIGUOUS` remains reserved
  for a later multiplicity-preserving valid routing source.
- Hard-ticket evidence is a typed fact, not an identifier convention. `AssessmentVerification`
  carries finite provenance and freshness plus exact verified ticket/closure and an independent
  verification record. Selection requires `INDEPENDENTLY_VERIFIED`, `CURRENT`, a present record,
  and exact matching bindings. `SELF_ASSERTED`, `UNVERIFIED`, `STALE`, `UNKNOWN`, missing,
  mismatched, or bypass-built verification evidence is
  `HARD_TICKET_ASSESSMENT_INVALID`.
- The current host still cannot read back an implementation task's effective workspace/profile/
  effort/capability rank. Record only
  `KNOWN_GAP_WORKSPACE_BINDING_READBACK_UNAVAILABLE`; never treat task prompts, shell paths,
  model labels, CLI login, runner state, or agent self-report as host proof.

## POC evidence and ownership boundary

For the replacement P8R ticket, the reviewer owns manual orchestration and the exact approved
ticket boundary. The applicable document-mutation gate remains the integration authority. Before
accepting/integrating a candidate, the reviewer personally runs a counter-mutation through a test
path independent of the implementer's recorded mutations.

That POC evidence proves only the ticket closure and test discrimination. It does not prove host
workspace binding, consume a receipt, create a task, or claim automatic delivery/wake. A
replacement ticket may not reintroduce a host-gateway prerequisite merely to make this bounded
resolver dispatchable.

## Composition and downstream artifacts

- `ExecutorRoutingResolver` receives only `ExecutorRoutingTable`, `ExecutorProfileRegistry`, and
  `RouteRequest`. Tests construct ordinary valid inputs and negative-only bypass inputs at this
  boundary; no Composition Root may pass a global singleton or effect client.
- `modules/spec/executor-routing.md` revision 03 must bind this Context and define the additive
  invalid-input statuses, canonical admission precedence, and typed assessment-verification
  semantics before any replacement ticket is approved.
- `P8R-EXECUTOR-ROUTING-03` is `BLOCKED / REQUIREMENT_CHANGED / CHG-20260823-033`; its
  uncommitted worktree source is not a baseline, candidate, or integration authority. A newly
  approved replacement ticket is the only future implementation authority.
- A later host-adapter task remains separate. If it crosses the privileged host boundary, it is
  `HIGH_ASSURANCE` and must satisfy the R07 readback rules without treating this POC known gap as
  success evidence.

## Seal and provenance

- Shared Context reference: `CONTEXT.md`, stable-fact fingerprint `e8eabdd8`.
- Requirement lineage: `PRD-20260822-030` / `CHG-20260822-030`, amended by
  `PRD-20260822-032` / `CHG-20260822-032` and `PRD-20260823-033` /
  `CHG-20260823-033`.
- This revision replaces only P8R's resolver-input and assessment-verification facts. It preserves
  the sealed POC manual-evidence/known-gap facts from revision 02.
