# Private Router SaaS POC Specification

| Field | Value |
| --- | --- |
| Specification ID | `SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26` |
| Specification state | `APPROVED` |
| Authoring AI / baseline | Codex / current worktree / `cbdfa7751c21c0355cb3aaaae5b7f045d9e84154` |
| Investigation Context | `doc/context/private-router-saas/main.md` |
| Requirement archive | `ARCH-REQ-20260815-002` |
| Requirement change | Retired pair `PRD-20260804-008` / `CHG-20260804-008` |
| Shared Context backlink | `CONTEXT.md §衍生 SPEC 索引` |
| Implementation language | Python 3.11 for contracts and test-only service adapter; existing plugin metadata only after a separate approved ticket |

## Problem, Goal, and Non-goals

The current plugin distributes readable workflow guidance and a local POC Router. It cannot keep its decision logic private, cannot perform a remotely governed entitlement check, does not dispatch an Agent, and has an incomplete POC transition profile. It must evolve without making a customer project depend on this repository or uploading customer code.

This POC validates a private Router control plane. A local thin plugin submits only a strict `RouterRequestEnvelope` containing pseudonymous project metadata, account-scoped salted revision digests, typed stage events, entitlement mode, and structured redacted summary fields. The private service produces one strict `RouterResponseEnvelope` containing the next permitted user-facing action or a fail-closed result. Source content stays local and is read only after the local client receives a valid decision.

### In scope

- Strict Pydantic contracts for local-to-service request and service-to-local response envelopes.
- A private policy/Profile abstraction separated from local public contracts.
- A test-only private Router transport and fake entitlement port, with no real network, OAuth, payment, database, or secret.
- A complete POC Profile route from intake through handoff, including a fail-closed result for every undeclared state/event pair.
- An explicit continuation directive: safe declared transitions auto-continue, declared human gates wait, and invalid or unavailable paths halt without a local fallback.
- Local preflight validation that rejects unredacted, free-form, unknown, or oversized request data before transport.
- User-facing action labels that do not disclose internal Router stage names or private Profile logic.
- TDD, strict typing, source-leak sentinel tests, compatibility tests for existing Router and telemetry behaviour, and documentation.

### Out of scope

- Real user accounts, OAuth provider, billing, checkout, payment webhooks, refunds, taxes, support commitments, or public deployment.
- Model hosting, model credits, Agents SDK model execution, Temporal worker, external MCP server, external database, or cloud storage.
- Uploading raw source, raw document, path, filename, URI, prompt, secret, PII, ContextPacket, side-context content, unrestricted free-text summaries, or telemetry JSONL.
- A claim that the plugin can prevent a user from disabling it, copying local files, or using another AI tool.
- Any target-project source, configuration, CI, runtime, build, deployment, or git-history change.

## User Flow and Acceptance Criteria

The user sees only product-language actions. The local plugin retains the internal-to-external name map and must never expose the private Profile, rule list, score, or source-selection rationale.

1. The user starts one of four entry modes: new project, inherited-project audit, repair, or deployment preparation.
2. The local plugin constructs and validates a metadata-only request. A first-project, standard, or audit entitlement is represented by a fake typed entitlement in this POC.
3. The private Router emits exactly one of: a permitted user-facing next action with `AUTO_CONTINUE`, an explicit user approval wait with `WAIT_FOR_HUMAN`, or a fail-closed `HALT`.
4. Only after an allowed action may the local Context resolver read locally declared source spans into a temporary `ContextPacket`.
5. The local runtime records its existing metadata-only telemetry locally; the POC does not transmit that telemetry to the service.

Acceptance criteria:

1. A request model cannot contain raw source text, prompt, URI, path, filename, secret, PII, arbitrary dictionary, or unrestricted free-text field; unknown JSON fields are rejected.
2. A test sentinel placed in a local source snippet cannot appear in any serialized request, response, policy-store record, fake transport record, exception, or telemetry record.
3. The private Router returns a single typed decision for every declared state/event combination in the POC Profile; every unknown event, missing evidence, invalid digest, missing entitlement, missing approval, or unavailable capability returns `SUSPEND` or `STOP`.
4. The client cannot call the local Context resolver for a paid/gated capability before a valid Router decision permits it.
5. The same event retry preserves its correlation identifier; a different event produces a new opaque reference identifier. No persistent record contains a raw span or source text.
6. The external action label is one of the declared product labels and contains no internal stage name, Profile ID, policy version, or scoring detail.
7. Existing local Router and telemetry tests remain green; no existing approved POC behaviour silently changes.
8. A local continuation runner automatically invokes only the one action granted by a valid `AUTO_CONTINUE` decision and runs until it reaches a declared human approval gate, a fail-closed result, or its configured safety ceiling. It must not wait merely because a source, entitlement, service, or validation condition failed.

## Domain Model, Data Flow, and Responsibility Boundaries

```text
LocalPlugin
  ├─ LocalMetadataNormalizer
  ├─ LocalContextResolver
  └─ RouterServicePort
         │
         ▼
PrivateRouterService
  ├─ PrivateProfileStore
  ├─ EntitlementPort (fake in POC)
  └─ RouterDecisionService
```

The following public contracts are proposed. Names are implementation-facing and are never product UI text.

```text
ProjectEntryMode = NEW_PROJECT | INHERITED_AUDIT | REPAIR | DEPLOYMENT_PREPARATION
EntitlementMode = FIRST_PROJECT_FREE | STANDARD_PROJECT | ACTIVE_AUDIT | DENIED
SummaryClaimCode = typed finite codes only

RouterRequestEnvelope = {
  request_id,
  account_subject_id,
  opaque_project_id,
  project_entry_mode,
  entitlement_mode,
  workflow_state_descriptor,
  router_event_descriptor,
  account_scoped_revision_digests,
  structured_redacted_summary,
  requested_capability_ids,
  client_version
}

RouterResponseEnvelope = {
  request_id,
  decision_id,
  external_action_label,
  outcome,
  allowed_capability_ids,
  allowed_source_kinds,
  context_budget,
  opaque_reference_ids,
  blockers
}
```

`structured_redacted_summary` is not a text summary. It is a closed collection of finite category, maturity, evidence-status, risk-code, and count/bucket fields. This POC intentionally sacrifices semantic precision to maintain the privacy boundary. A later change is required before any new data class crosses the boundary.

`opaque_project_id` is service-issued after an account claims a project. Revision digests are account-scoped and salted. They support consistency checks only; they are not proof that a client has reported truthfully and must not be described as anonymous.

Local responsibilities:

- Read local sources only after an allowed decision.
- Construct ephemeral `ContextPacket` data and retain local side-context evidence.
- Redact/normalise before transport; reject invalid data locally.
- Display the product action and material blockers accurately.

Private service responsibilities:

- Keep Profile versions, transition rules, decision logic, entitlement state, and audit-event schema private.
- Validate request and response contracts; return a deterministic fail-closed result when its inputs are incomplete or inconsistent.
- Persist only metadata allowed by this specification in a later approved storage adapter.

## API / Event, Database, Provider, Permission, and Operations

The POC provides a Python `RouterServicePort`, not a deployed URL. A later MVP must implement this port as an OAuth-protected MCP service over HTTPS and add production storage. The POC has no provider credential, database, cache, or runtime service.

Proposed POC events:

- `PROJECT_CLAIM_REQUESTED`
- `ROUTER_DECISION_REQUESTED`
- `ROUTER_DECISION_EMITTED`
- `ROUTER_DECISION_BLOCKED`
- `CONTEXT_REFERENCE_CLOSED`

The event payloads use the same metadata-only boundary as `RouterRequestEnvelope`. They must never contain raw source text, a source locator, or a model prompt.

The future MVP's data stores are intentionally not selected here. Any selection must meet the following non-negotiable controls: encrypted transport, strict account isolation, minimal retention and deletion policy, webhook idempotency, provider-secret isolation, audit-event redaction, least-privilege service identity, and an explicit region/data-processing decision.

## Test Cuts and TDD Design

Each implementation ticket must start with a failing test and cover these observable cuts:

1. **Normal path:** valid local metadata and fake entitlement produce one permitted external action without transmitting a sentinel source string.
2. **Contract violation:** unknown field, free-form content, malformed digest, excessive field size, mismatched request ID, or an internal stage label at the external boundary is rejected.
3. **Authorization failure:** denied, expired, or mode-incompatible entitlement prevents Context resolution and returns a material blocker.
4. **External/service failure:** unavailable private service, malformed response, replayed correlation ID, or unavailable capability fails closed and does not fall back to local private rules.
5. **Regression and privacy:** current Router/telemetry behavior remains valid; source/prompt/URI/path sentinels never appear in serialised data, logs, or persistent projections.
6. **Continuity classification:** a POC flow auto-runs across the declared intake → discovery → design → evidence → context → specification path, pauses only at the specification approval gate, and halts rather than waits for invalid metadata, denied entitlement, service failure, response mismatch, replay, or an undeclared transition.

## Risks, Compatibility, Rollback, and Deployment Preconditions

- **Privacy versus utility:** metadata-only routing may be less accurate than content-aware routing. The POC must measure only deterministic protocol correctness, not promise semantic project understanding.
- **Client trust:** a local user can fabricate metadata or bypass the plugin. SaaS gating protects the product path and server-held logic, not a user's entire computer.
- **Availability:** if the private Router is unavailable, the gated route must suspend. It must not silently use a local copy of the private Profile.
- **Compatibility:** the existing v0.3 plugin, Router POC, and Claude Code metadata remain unchanged until a later approved ticket explicitly changes them.
- **Rollback:** remove the new optional service adapter and restore the prior plugin release; target projects remain unaffected because neither version is their runtime dependency.
- **MVP deployment prerequisite:** owner approval of a new MVP change covering payment provider, OAuth provider, hosting, data region, privacy policy, deletion, incident operation, and unit-cost evidence under the 70% gross-margin target.

## Convergence and Backlinks

- Historical Context backlink: `SPEC-AI-WORKFLOW-PRIVATE-ROUTER-SAAS-20260804-01KZ49YM6HA658QF7ME2A5BR26`, `modules/spec/private-router-saas.md`, POC contracts only, retired pair `PRD-20260804-008` / `CHG-20260804-008`, archived as `ARCH-REQ-20260815-002`.
- Requirement change convergence: this draft defines a private Router SaaS POC; real commercial operation is excluded and requires a separate MVP Wayfinder.
- Shared baseline commit: `cbdfa7751c21c0355cb3aaaae5b7f045d9e84154`; docs-only baseline publication is pending owner approval.

## Revision Signatures

| Date | AI / baseline SHA | Summary |
| --- | --- | --- |
| 2026-08-04 | Codex / `cbdfa7751c21c0355cb3aaaae5b7f045d9e84154` | Initial draft following approved POC Wayfinder, architecture, and Grill. |

## Approval Record

- Decision maker: project owner.
- Date: `2026-08-04 (Asia/Taipei)`.
- Approval scope: Private Router SaaS POC specification. Ticket creation is authorised; any source/plugin/service modification remains forbidden until a separate ticket approval.
