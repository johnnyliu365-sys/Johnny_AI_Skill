# Controlled verification — qualification-first architecture

| Field | Value |
| --- | --- |
| Artifact ID / kind / revision | `ARCH-CONTROLLED-VERIFICATION-20260909-01` / `ARCHITECTURE_PROPOSAL` / `01` |
| Lifecycle | `DRAFT / OWNER_GRILL_REQUIRED / NOT_SEALED` |
| Input | [DELTA Wayfinder](wayfinder-r01.md), [accepted D1/D2/D3](enforcement-boundary-r01.md), [REQ-051](../../requirements/active/2026/environment-control/REQ-20260908-051.md) |
| Author / baseline | Current-session drafting assistant for the human architecture owner; owned `codex/controlled-verification-intake` worktree at `d3c78b5b154b04a7fdaad544a3d00f1e91271dcb` |
| Maturity / intensity | POC / derived HIGH_ASSURANCE; no production support claim |

## Outcome and first delivery boundary

The requested product is mandatory execution and source admission, not a dashboard or a larger
instruction file. First deliver a finite capability verdict for the accepted protected-launch
boundary. A specification for that investigation must not pretend that its still-unproved
primitives are closed production interfaces. A qualified result permits later product ticketing;
an unavailable required primitive stops only dependent execution and returns its concrete evidence
to the owner. Pure plan/reconciliation work and existing WA-04 remain separate possible lanes.

The protected lane does not retroactively restrict this unrestricted drafting session. Neither
opening a VM console nor an elevated guest terminal establishes enrollment.

## Trust and responsibility boundaries

1. **Owner approval boundary:** the owner controls enrollment and approval of exact plan versions.
   A model may propose a change, but cannot write the active approval, execution-policy or final
   evidence store. Approval is an independently resolved record, not a caller-provided boolean,
   hash, profile label, ticket comment or JSON PASS.
2. **Protected launch boundary:** a dedicated launch entry binds exact host binary/configuration,
   policy revision and the restricted Windows subject. A protected broker owns the approved
   execution and evidence interfaces. The investigation must identify every principal able to
   change binaries, configuration, credentials, writable code search paths and broker endpoints.
3. **Workload boundary:** untrusted project/test code never runs with the broker's protection-owner
   token. Every writable destination and process escape path is part of the resource model,
   including profile/temp caches, inherited handles and indirect process creation.
4. **Repository authority:** verification evidence does not approve a ticket or move a branch.
   Existing review/integration gates remain final authority. WA-04 owns source responsibility
   checks; this feature does not introduce a competing validator or an arbitrary line ceiling.

Administrator/owner compromise and unrelated human terminals are outside D2. Denial must still
hold when the enrolled Agent changes prompts, supplies hostile tool arguments, disables an
advisory hook or modifies writable project files. A configured flag alone is not proof.

## Complete data pipelines

| Slice | Validate / normalize | Command / event | Storage owner and boundary | Read projection / returned state | Lifecycle and privacy |
| --- | --- | --- | --- | --- | --- |
| Approved verification | Parse finite typed request; resolve exact approved plan/candidate; reject all binding drift, including executable dependencies and environment; do not silently transform rejected intent | One immutable attempt request with ordered slots and finite limits | Target owns ticket/source/approval intent; protected broker owns admitted plan snapshot and actual attempt evidence, outside target runtime | Matched expected checks plus actual exits/cleanup; refusal or incomplete evidence cannot become success | Approval invalidates on source/config/policy change; retain failed attempts; bounded evidence capacity refuses further work rather than deleting failures |
| WA-04 responsibility | Resolve approved target contract and candidate facts through its language adapter | Existing responsibility-admission request, not a new workflow stage | Candidate/contract remain target-owned and versioned; transient source facts stay in admission invocation | Existing accepted/rejected/unavailable projection before integration | Bind exact candidate/contract/adapter revision; unsupported dynamic facts fail closed; no raw source copied into durable Router metadata |
| Owned recovery | Resolve attempt claim, terminal record and OS process identity; do not normalize missing evidence to never-started | Reconcile, cancel or reattach to that attempt only | Protected attempt ledger owns claim/launch/terminal facts; cleanup evidence owned separately from the untrusted workload | Completed, proven live, unresolved interruption or recovery-required; replay starts no new attempt | Claim/launch/settle crash windows tested explicitly; preserve conflicts; only exact owned resources may be terminated |
| Automatic host enforcement | Resolve enrolled subject and exact host/config/tool roster; independently qualify every offered effect route | Protected host launch or typed refusal | Owner controls enrollment/configuration; qualified adapter produces bounded provenance, not self-attested model output | Per-host/per-surface capability vector; unknown paths prevent a full-enforcement claim | Host/config/plugin/primitive changes invalidate old qualification; host transcripts remain local bounded fixtures, no provider credentials or private project content |

All projections entering the existing Router are opaque IDs, finite states, revisions and digests.
Raw paths, commands and synthetic fixture output belong only in their protected local operational
artifact, never in Router state, telemetry or prompts. A reviewer may receive a bounded sanitized
report with exact evidence references. No retention TTL or automatic pruning is introduced.

## Composition, lifetime and replacement seams

Python 3.11 remains the single backend language, frozen/validated contracts and `mypy --strict`.
PowerShell is limited to exact platform-native operational transport; it is not a second workflow
engine. Introducing another production runtime requires a separate language decision.

| Unit | Injected dependencies / planned concrete boundary | Lifetime | Test replacement |
| --- | --- | --- | --- |
| Thin request/result entry | Request decoder and qualification/verification use case; no subprocess or policy writes | One invocation | Captured typed request/result |
| Plan admission | Approved-record reader, immutable candidate resolver, capability-vector reader | One admission | Immutable plan/source/capability fixtures |
| Finite coordinator | Validated ordered plan, executor port, event/deadline port, evidence sink | One attempt | Scripted executor/events; no sleeps or real workload |
| Windows execution adapter | Qualified native identity, process, resource and immutable-source primitives | One admitted owned execution tree | Strict fake primitive results; real bounded guest cells separately |
| Reconciliation | Attempt ledger and process-identity observation port | One recovery invocation, not a background watcher | Crash-boundary and replay/concurrency schedules |
| Evidence assembler | Protected evidence reader and expected-cell manifest | One terminal/qualification report | Missing/duplicate/mismatched/forged-result fixtures |
| Codex / Claude adapters | Exact installed surface/configuration and qualified restricted launch transport | One enrolled session | Deterministic local host fixture only if compatible; otherwise unavailable |
| WA-04 adapter | Existing responsibility contract and source parser | One source-admission invocation | Real small source trees plus forbidden dependency/construction mutations |
| Composition Root | Builds the above from independently admitted dependencies; no global service locator or ambient credential discovery | One owner/reviewer invocation | Explicit fake composition with the same public constructors |

Production bindings are intentionally not claimed delivered: the Windows adapter and host
transports must acquire a qualification result naming actual primitives and exact versions before
product implementation can freeze those bindings. Implementers may not choose a weaker primitive
to satisfy a port name. The first qualification slice records that answer rather than shipping a
placeholder adapter. Ordinary constructors/validators are required; casts, bypass construction
and mutable object patching cannot establish a success path.

## Reuse and compatibility

Selected `workflow-router-poc@b697738d009db37318ebc8762107ef8329e014db`, READY via
`library/MODULE_CATALOG.md -> catalog/workflow-control/README.md -> workflow_router/README.md`.
Its public `library.workflow_router` exports `RouterEngine`, `ProcessStage` and
`CompletionEvidence`. The latter binds artifact/verification references and an evidence digest;
it is not a workload executor or capability proof. Do not add the new engine to its central
`contracts.py`/`router.py` or adopt its unrelated raw-path telemetry POC.

The approved [workflow adoption SPEC](../../../modules/spec/workflow-adoption-activation.md)
continues to own WA-04 and its Python source analysis. Its five-session probabilistic activation
policy is not the new deterministic OS qualification policy; neither replaces the other.
The approved [environment SPEC](../../../modules/spec/environment-capability-bootstrap.md)
continues to own EC-10 resource invariants and EC-15 platform support. No receipt or runner is
added to same-lifetime delegation. Existing target behavior and sealed Context are not rewritten.

## Alternatives and threat/failure matrix

| Alternative / failure | Decision or required proof |
| --- | --- |
| More user-global governance prose | Rejected: drifts, remains advisory and contradicts the accepted ownership boundary |
| Hook-only enforcement | Rejected as final authority; may remain an advisory entry inside independently protected execution |
| Job Object alone | Insufficient for policy authority, disk/temp writes and complete host effect mediation |
| Always-running new service/queue | Not chosen for qualification; exact short-lived owner-controlled experiment first, no persistent service installation |
| Finite disk/file cap implemented only by size checks or monitoring | Unavailable; an OS-enforced limit and all alternate writable destinations must be identified and exercised |
| Host supports disabling only some effect tools | Per-surface unavailable/partial result; do not market as fully enforced or silently replace the host |
| Owner/broker crashes between claim and launch or launch and settlement | Reconciliation must not assume no work; persist ambiguity, block dependent launch and retain recovery evidence |
| Untrusted workload emits forged terminal JSON | Ignore as authority; trusted observation/evidence matching decides result |
| Bootstrap resolves writable modules or inherited executable search path | Refuse before privilege/effect; reuse ENV-F2's protected-bootstrap invariant, not the diagnostic helper |
| Guest lacks an installed CLI or offline compatible host fixture | Mark only dependent host cells unavailable; no unapproved download, networking or external model fallback |

## Acceptance, rollback and owner boundary

The qualification must include a permitted positive effect, each named denial and reviewer
counter-mutation; a gate that disables everything is not proven. It must also preserve an
unrelated sentinel and prove bounded completion without model polling. See the
[qualification SPEC candidate](../../../modules/spec/controlled-verification-qualification.md)
for the proposed finite contract; it is not yet effective.

Before VM changes, bind its exact identity and an owned checkpoint; a checkpoint's existence
does not prove restoration. No restore, old-data deletion, new physical-host policy, production
service, provider call, push or release is implied. Failed cleanup stops dependent work and
retains evidence for owner-directed recovery.

XSS classification for the proposed CLI/OS qualification slice is `XSS_NOT_APPLICABLE`: no new
Browser/WebView/HTML/JavaScript sink. Desktop interaction remains a separate unqualified surface;
adding a renderer/privileged bridge re-enters XSS/architecture review.

Return: architecture proposal available for owner Grill, not an approved SPEC or sealed shared
Context. D1/D2/D3 are preserved. The [Grill packet](grill-r01.md) identifies precisely what is
confirmed and what still requires an owner response; no assistant or helper can answer for them.
