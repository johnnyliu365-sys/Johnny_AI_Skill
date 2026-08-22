# Provider-neutral Executor Routing Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-EXECUTOR-ROUTING-20260822-01M4P6R8T0V2X4Z6B8D0F2H4J6` |
| Status | `APPROVED / REVIEWER_DECOMPOSITION_AUTHORIZED / REVISION_02` |
| Author / baseline | Codex architecture owner / `c0b52f7ff48002c09726aebcbf1186e624bd0a57` |
| Feature Context | `doc/context/executor-routing/codex-provider-neutral-executor-routing-r02.md` (`SEALED / CTX-EXECUTOR-ROUTING-20260823-02`) |
| PRD / change | `PRD-20260822-030` / `CHG-20260822-030`, amended by `PRD-20260822-032` / `CHG-20260822-032` |
| Delivery stage / profile | `POC` / `STANDARD`: a single, reversible pure resolver has a known-domain contract, no security surface and no external effect. |
| Implementation language | Python 3.11; frozen Pydantic contracts, explicit finite enums and `mypy --strict`. |
| XSS classification | `N/A`: this feature accepts no Browser/WebView/HTML/DOM/JavaScript input or renderer. |

## Problem and goal

Dispatch currently relies on prose that names specific provider models. That makes provider
identity look like workflow policy, leaves unavailable credentials indistinguishable from a
valid selection, and permits a caller to narrate an escalation without typed evidence.

The goal is a pure, typed resolver that selects one already-registered executor profile from
semantic routing data. It must fail closed for every absent, ambiguous, unavailable or
insufficient-evidence case. It returns a profile reference only; host invocation remains a
separate high-assurance, receipt-bound effect.

## User, data, error and effect boundary

The architecture owner or admitted reviewer supplies only typed profile, ticket and assessment
references that have already passed its own authority gate. An injected registry boundary
normalizes provider/model/effort configuration and capability evidence into named types before
the resolver reads it. The resolver returns either a selected profile/reviewer binding or one
finite rejection; it writes no state and starts no provider, process, receipt, task, worktree or
runner. Registry parse/read failure, duplicate/missing route data, unavailable capability,
invalid hard-ticket assessment and weaker-reviewer binding are all fail-closed results.

## Scope and non-goals

In scope:

- typed semantic role, work classification, attempt state, executor-profile reference,
  profile availability and failure/override evidence;
- a provider-neutral routing-table and profile-registry contract;
- deterministic route resolution and finite rejection results;
- source and reverse-mutation checks that prevent host invocation or receipt authority from
  entering the resolver.

Out of scope:

- provider login, credential storage, host command execution, agent creation, task/worktree
  control, runner control, receipt issuance/consumption, integration or automatic wake;
- persistence or UI for profile configuration;
- replacing an unavailable profile with another provider, automatically elevating an
  implementer, or selecting another implementer after a bounded cycle is exhausted;
- changing shared Context outside the approved revision path or dispatching any ticket before its
  replacement ticket is approved.

## Typed contract and route semantics

The following is notation; production code uses frozen, validated named types and accepts no
unvalidated dynamic object or string convention.

```text
enum RoutingPurpose {
  PROJECT_INITIAL_REVIEW, REQUIREMENT_CHANGE_COMPLEX_DECISION_REVIEW,
  TICKET_OPENING, INDEPENDENT_TICKET_REVIEW, IMPLEMENTATION
}
enum ProfileAvailability { AVAILABLE, UNAVAILABLE, STALE, UNKNOWN }
enum VerifiedCapabilityRank { TIER_1, TIER_2, TIER_3 }
enum ResolutionStatus {
  SELECTED, ROUTE_NOT_FOUND, ROUTE_AMBIGUOUS, PROFILE_NOT_FOUND,
  PROFILE_UNAVAILABLE, HARD_TICKET_ASSESSMENT_MISSING,
  HARD_TICKET_ASSESSMENT_INVALID, REVIEWER_CAPABILITY_INSUFFICIENT,
  OVERRIDE_RECORD_MISSING, OVERRIDE_PROFILE_INVALID,
  MODEL_CAPABILITY_INSUFFICIENT, ARCHITECTURE_OWNER_REQUIRED
}

struct ExecutorProfileRef { ProfileId value; }
struct ExecutorProfile {
  ExecutorProfileRef ref;
  ProviderId provider;
  ModelId model;
  EffortTier effort;
  VerifiedCapabilityRank verified_capability_rank;
  ProfileAvailability availability;
  CapabilityEvidenceRef availability_evidence;
}
struct RoutingKey {
  ModelRole role;
  RoutingPurpose purpose;
}
struct HardTicketAssessment {
  TicketRef ticket;
  ClosureRevision closure_revision;
  NoFurtherDecompositionEvidenceRef no_further_decomposition;
  CapabilityGapEvidenceRef exceeds_standard_implementation;
}
struct ReviewBinding {
  ExecutorProfileRef implementation_profile;
  ExecutorProfileRef reviewer_profile;
  TicketRef ticket;
  ClosureRevision closure_revision;
}
struct OwnerOverrideRecord {
  OwnerDecisionRef decision;
  ExecutorProfileRef selected_profile;
  OverrideReason reason;
}
struct RouteRequest {
  RoutingKey key;
  TicketRef ticket;
  ClosureRevision closure_revision;
  optional<HardTicketAssessment> hard_ticket_assessment;
  optional<OwnerOverrideRecord> owner_override;
}
struct RouteResolution {
  ResolutionStatus status;
  optional<ExecutorProfileRef> selected_profile;
  optional<ReviewBinding> review_binding;
  optional<NamedRejection> rejection;
}
```

`ARCHITECTURE_OWNER` remains human-owned. The resolver may select profiles for permitted
assistance/review or implementation roles only when the caller already has the role authority;
the selected profile does not create that authority.

The route table contains semantic profile references, never provider/model/effort literals. The
profile registry owns the provider/model/effort tuple, verified capability rank and capability
evidence. Current profile intent is represented by registry data: Sol/high for project-initial
review, complex requirement-change decision inventory and an elevated ticket's review;
Terra/xhigh for normal ticket opening and review; Luna/xhigh for normal implementation. An
authenticated Claude profile can use analogous tiers without resolver code changes. Tests use
fictitious provider/model values.

A normal implementation resolves Luna/xhigh with a Terra/xhigh reviewer binding. Terra/xhigh
implementation is permitted only for a ticket-bound `HardTicketAssessment`: it proves the
ticket cannot be further decomposed without breaking its observable closure and that its named
reasoning need exceeds the standard implementation profile. That same resolution must bind
Sol/high review for that ticket alone. Validation requires the review profile's
`verified_capability_rank` to be greater than or equal to the implementation profile's rank;
the resolver rejects a weaker reviewer rather than selecting a fallback.

Sol/high is not a general ticket-opening or implementation profile. It is selectable only for
`PROJECT_INITIAL_REVIEW`, `REQUIREMENT_CHANGE_COMPLEX_DECISION_REVIEW`, or the reviewer side of
a valid Terra implementation elevation. A bounded failed implementation/review cycle returns
`MODEL_CAPABILITY_INSUFFICIENT` and then `ARCHITECTURE_OWNER_REQUIRED`; it does not automatically
select another implementation profile.

An owner override is an input record, not a boolean. It must name one registered `AVAILABLE`
profile and an owner decision reference. It cannot select an unregistered/unavailable profile,
bypass a required hard-ticket assessment, weaken the reviewer binding or grant authority.

## Composition and boundaries

`ExecutorRoutingResolver` is a pure domain service. It receives an
`ExecutorRoutingTable`, an `ExecutorProfileRegistry` and a `RouteRequest`; it returns only a
`RouteResolution`. Registry loading/parsing is an injected boundary that normalizes raw
configuration before construction. Read failure, malformed data, duplicate key, duplicate
profile reference, missing profile, unknown availability or stale evidence is a named rejection.

The resolver imports neither host adapters nor `dispatch_session`, `dispatch_authority`,
`worker_assignment`, `work_queue`, `document_mutation_gate`, credential stores, process
launchers or runner modules. A later approved host adapter may consume a selected profile only
after high-assurance receipt/host admission; this SPEC grants no such effect. The POC ticket may
use reviewer-owned manual orchestration, but that route is integration evidence only: it does not
assert a host workspace/profile binding, consume a receipt, or claim automatic delivery/wake.

## Acceptance criteria

1. The same semantic table resolves registered profiles from at least two fictitious providers
   without source changes, and resolver source contains no provider/model literals.
2. Project-initial review and complex requirement-change decision review select only their
   configured decision-support profile. General ticket opening and review select only their
   configured supervisor/reviewer profile.
3. A normal implementation resolves its configured implementation profile and a reviewer
   binding whose verified capability rank is not lower than the implementation profile's rank.
4. Terra implementation is selected only from a valid same-ticket hard-ticket assessment and
   binds the configured higher-capability reviewer for that ticket alone. Missing, stale,
   cross-ticket, wrong-closure or self-asserted assessments reject.
5. A reviewer binding with a lower verified capability rank than its implementation profile
   returns `REVIEWER_CAPABILITY_INSUFFICIENT`; it cannot fall back to a weaker reviewer.
6. Missing/empty/malformed table, duplicate/ambiguous key, absent profile, unavailable/stale/
   unknown profile and registry-read failure each return distinct finite fail-closed results;
   no default profile exists.
7. An owner override without a decision record, with an unknown profile or with an unavailable
   profile rejects. A valid override is auditable and cannot bypass a hard-ticket assessment or
   weaken the reviewer binding.
8. A bounded failed implementation/review cycle returns `MODEL_CAPABILITY_INSUFFICIENT` and
   `ARCHITECTURE_OWNER_REQUIRED`; it never chooses another implementer by heuristic.
9. Static namespace tests prove the resolver has no receipt, dispatch, host-launch, credential
   or runner authority.
10. Reverse mutations make red: adding a default fallback; accepting a forged hard-ticket
    assessment; accepting a weaker reviewer binding; accepting an unavailable override profile;
    and adding a provider/model literal to resolver source. Exact restoration returns green.
11. The replacement P8R ticket records the `POC` / `STANDARD` assessment, the named
    `KNOWN_GAP_WORKSPACE_BINDING_READBACK_UNAVAILABLE`, the applicable document-mutation gate,
    and a reviewer-run counter-mutation through a distinct test path. None of these artifacts may
    assert host binding, receipt delivery, runner activation or automatic wake.

## Verification and approval path

The replacement implementation ticket must contain focused TDD, strict typing, source-boundary
checks, all named negative cases and the five reverse mutations above. The reviewer runs the
full suite and independent mutation review before integration. It replaces the old P8R leaf,
which is not dispatch authority after `CHG-20260822-032`.

Owner approval must name this exact SPEC revision. Approval then seals the feature Context,
permits a replacement P8 ticket to bind this SPEC/Context/PRD/CHG baseline, and permits a
separate host-profile/adaptor ticket only if its external credential and invocation boundaries
are explicitly authorized.

## Risk, compatibility and rollback

The principal risk is an incorrect profile or reviewer choice weakening independent review.
Every resolution remains pure and fail-closed, so a rejection causes no host or source effect;
correction is an additive profile/spec/ticket revision rather than a hidden fallback. POC manual
evidence is deliberately not host evidence. Existing dispatch, receipt, host-adapter and runner
contracts remain read-only dependencies and retain their high-assurance requirements.

## Revision signature and approval record

| Revision | Authority | Decision |
| --- | --- | --- |
| 01 | Project owner, 2026-08-22 (Asia/Taipei) | Approved this exact provider-neutral routing policy, the single-ticket Terra implementation exception, and the reviewer-strength invariant. Reviewer decomposition is authorized; dispatch and host effects are not. |
| 02 | Project owner, 2026-08-23 (Asia/Taipei) / `CHG-20260822-032` | Reclassified the pure P8R closure as `POC` / `STANDARD`, bound Context revision 02, and requires explicit manual-evidence/known-gap recording. Host binding remains a separate `HIGH_ASSURANCE` path. |
