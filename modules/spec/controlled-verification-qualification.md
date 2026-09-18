# Protected execution qualification specification

| Field | Value |
| --- | --- |
| Specification ID / revision | `SPEC-CONTROLLED-VERIFICATION-QUALIFICATION-20260909-01` / `07` |
| Status | `OWNER_APPROVED / CVQ01_SCHEMA_RESUMPTION_AUTHORIZED / NATIVE_EFFECTS_NOT_AUTHORIZED`; revision 07 records approval of revision 06 without changing behavior |
| Author / worktree / baseline | Current-session drafting assistant; `codex/controlled-verification-intake`; `d3c78b5b154b04a7fdaad544a3d00f1e91271dcb` |
| PRD / CHG | `PRD-20260908-051` / `CHG-20260908-051` |
| Context sources | [Wayfinder](../../doc/context/controlled-verification/wayfinder-r01.md), [architecture proposal](../../doc/context/controlled-verification/architecture-r01.md), [owner Grill packet](../../doc/context/controlled-verification/grill-r01.md), [managed index](../../doc/context/controlled-verification/README.md) |
| Shared Context | `CTX-CONTROLLED-VERIFICATION-20260909-01` revision 02, `OWNER_APPROVED / SEALED`; [exact leaf](../../doc/context/controlled-verification/main.md) through its managed index |
| Language / checker | Python 3.11, frozen validated contracts, `mypy --strict`; exact PowerShell native operational recipes are edge transport only |
| Maturity / intensity | POC / HIGH_ASSURANCE, derived from REQ-051's privileged cross-boundary workload; docs-only drafting has zero implementers |

## 1. Goal, scope and non-claims

Determine whether the accepted launcher/restricted-identity/protected-broker boundary can enforce
the requested invariants on the Windows lab and each declared Codex/Claude host surface. Produce
exact capability evidence, including honest unsupported results, before product adapters rely on
it. Missing capability is an output of the investigation, not permission to change the guarantee.

This SPEC does not deliver the final controlled verification product, install a production
service, publish a plugin, enroll the physical host, replace the Router or implement WA-04 again.
WA-04 keeps its approved source-admission contract and later independent ticket. No generic file
length limit, user-global governance copy, mandatory synchronous runner/receipt, provider call,
new real project workload or five-session stress suite is introduced.

## 2. Public contracts and independent authority

All objects are immutable, reject extra fields/coercions and use ordinary validated construction.
IDs/digests reuse the existing opaque-metadata and exact-digest conventions. Integers are strict
integers, never booleans/floats/strings. Optional data uses tagged alternatives, not correlated
nullable fields. Candidate source and operational paths never enter durable Router state.

| Contract | Required meaning |
| --- | --- |
| `QualificationScope` | Exact project/baseline, capability IDs and approved manifest revision/digest; each case has a tagged `PURE_CONTRACT` or `WINDOWS_LAB` binding. Pure cases contain no VM/process fields; native cases bind the lab prerequisites independently |
| `CapabilityKey` | Capability family, adapter revision, platform and exact host surface when applicable; `CODEX_CLI`, `CODEX_DESKTOP`, `CLAUDE_CODE_CLI` are distinct, never interchangeable |
| `QualificationPrerequisiteSet` | Ordered unique `PrerequisiteRequirement` keys resolved into exact `PrerequisiteEvidenceBinding` results by the independent port; matching/rejection algebra below is mandatory |
| `QualificationCase` | Unique cell ID, capability key, control/attack/reviewer-mutation role, immutable fixture/executable/dependency identities, exact argv/cwd/environment plan, expected oracle, prerequisite keys and resource/cleanup/evidence bounds |
| `QualificationManifest` | Nonempty ordered cases, exact source and owner-approved revision, single lane, explicit total budget, no implicit discovery expansion; duplicate cases/IDs or incomplete roster coverage reject |
| `AttemptBinding` | Tagged `PureContractBinding` or `NativePreLaunchBinding`; a distinct `LaunchObservation` can be appended only after actual launch. Pre-launch objects cannot contain invented future process identities |
| `CapabilityObservation` | Independent observer identity and evidence binding, exact key, finite result, native primitive/race/failure semantics where applicable, named case observations; a reported PASS without its required positive/refusal evidence is malformed |
| `QualificationReport` | Exact manifest/baseline and one tagged `CaseResult` per expected cell, reduced by the closed rules below; no model-authored test counts or review approval |
| `QualificationEvaluation` | Sole public tagged evaluation return: MANIFEST_REFUSED, REPORT_REJECTED or REPORT_ACCEPTED, with the exact payloads below; no nullable report/exception fallback |

Finite proposal vocabulary:

```text
CapabilityFamily = PLAN_BINDING | POLICY_ISOLATION | RESOURCE_CONTAINMENT
                 | OWNED_CLEANUP | ATTEMPT_RECONCILIATION | HOST_MEDIATION
                 | RESPONSIBILITY_ADMISSION
Observation = PROVEN | FAILED | UNAVAILABLE | NOT_RUN
Admission = ADMITTED | REFUSED
Refusal = SOURCE_MISMATCH | INVALID_MANIFEST | APPROVAL_UNRESOLVED
        | PREREQUISITE_UNPROVEN | RESOURCE_ENFORCEMENT_UNAVAILABLE
        | HOST_ROSTER_UNQUALIFIED | EVIDENCE_INVALID | RECOVERY_REQUIRED
ReportOutcome = QUALIFIED_FOR_DECLARED_SCOPE | CAPABILITY_UNAVAILABLE
              | QUALIFICATION_FAILED | INCOMPLETE
```

These are new qualification-domain contracts, not additions to `ProcessStage` or new global
Router enums. A `PROVEN` prerequisite is returned by its protected evidence resolver for an exact
scope, never trusted because the caller supplied that word. Production integration still requires
its own review and authority gate after qualification. A report may honestly close an
investigation with `CAPABILITY_UNAVAILABLE`; it cannot then close REQ-051 as implemented.

### Binding tags and time order

Common binding fields are `project_id`, `baseline_digest`, `manifest_revision`, `manifest_digest`,
`case_id`, `attempt_key`, `fixture_digest`, `approved_record_ref` and `evidence_scope_ref`. Revisions
are positive strict integers; references use opaque IDs; digests use the exact digest value type.

- `PureContractBinding(kind=PURE_CONTRACT)` contains those common fields only. It cannot contain a
  VM, subject SID, checkpoint, Job Object, process identity, native launch grant or host channel.
- `NativePreLaunchBinding(kind=WINDOWS_LAB)` adds protected-policy revision/digest/owner ref,
  restricted-subject ref, broker binary/configuration digests, launcher/enrollment refs,
  immutable snapshot ref, exact executable/dependency/argv/cwd/environment-plan digest,
  resource-plan ref, VM/guest/checkpoint refs and protected evidence-owner ref. These refs resolve
  to actual operational identities outside Router metadata. It contains **no future PID/Job ID**.
- `LaunchObservation` is a later immutable record: `attempt_key`, `prelaunch_binding_digest`,
  `observation_revision`, `observer_ref`, `os_execution_identity_ref`, `isolation_identity_ref`
  and `evidence_digest`. The protected observer must bind already-created native resources before
  untrusted work is permitted to run. An already-created suspended process may be observed before
  resume; that is not permission to execute first and attach protection afterward.

Required launch identity is never satisfied with dummy/null/PID placeholders. A refusal before
launch binds the requested case/manifest and refusal evidence, not a nonexistent LaunchObservation.
Pure rule checks may test native-contract rejection through fakes but cannot issue native or host
capability proof. A manifest may contain pure and lab cases for the same project/baseline; each
case is independently admitted under its own tag, so a missing VM does not invalidate pure cases.

### Prerequisite constituent contracts and comparison

`PrerequisiteKind = APPROVED_SOURCE | LAB_IDENTITY | CHECKPOINT | PROTECTED_BOOTSTRAP
| PROTECTED_IDENTITIES | IMMUTABLE_SNAPSHOT | RESOURCE_CONTROLS | ATTEMPT_CLAIM
| HOST_ROSTER_DISCOVERY | WA04_ADAPTER`.

`PrerequisiteKey` is the exact tuple `(kind, scope_id, capability_key, adapter_revision)`.
`PrerequisiteRequirement` contains that key plus `expected_observation_revision` and
`expected_evidence_digest`; these are pinned in the independently approved manifest, not chosen
by the invocation. `PrerequisiteEvidenceBinding` contains the same key, `observation_revision`,
`evidence_digest`, `observer_ref`, `source_ref` and disposition `PROVEN | FAILED | UNAVAILABLE`.
Its authenticity is checked by the independent evidence port; shape validation is not provenance.

The resolver returns exactly one of `FOUND(binding)`, `MISSING`, or `CONFLICTING`; malformed or
unauthenticated evidence is a conflict, not a success. There is no first-match/latest-wins rule.
Key, adapter revision, observation revision and digest must all match exactly. Missing, conflict,
stale/mismatched binding, FAILED and UNAVAILABLE all map to case refusal
`PREREQUISITE_UNPROVEN`, preserving distinct detail codes `MISSING`, `CONFLICTING`, `STALE`,
`FAILED`, `UNAVAILABLE`. Extra unrelated evidence is not used to satisfy another key.

`CaseKind = PURE_RULE | SOURCE_PROPERTY | TRUSTED_NATIVE_DISCOVERY | ADVERSARIAL_WORKLOAD
| REAL_HOST_PROPERTY`. PURE_CONTRACT permits PURE_RULE/SOURCE_PROPERTY only; WINDOWS_LAB
permits the remaining kinds only. Family identifies the rule being examined, while case kind
identifies what evidence it can establish; a PURE_RULE about RESOURCE_CONTAINMENT cannot prove
native RESOURCE_CONTAINMENT.

Pure cases require APPROVED_SOURCE only, plus WA04_ADAPTER only for an actual WA-04 source
property claim. Lab mutation requires LAB_IDENTITY, CHECKPOINT and PROTECTED_BOOTSTRAP;
adversarial workload/real-host cells additionally require PROTECTED_IDENTITIES, IMMUTABLE_SNAPSHOT,
RESOURCE_CONTROLS and ATTEMPT_CLAIM. REAL_HOST_PROPERTY additionally requires
HOST_ROSTER_DISCOVERY: approved configuration and actually discovered dispatch identities must
match before exercising the host. It contains **no enforcement verdict**. Trusted read-only roster
discovery does not require its own completed discovery result as a prerequisite. The exact required key set is frozen by
case kind before invocation. A trusted, fixed, bounded primitive-discovery recipe may collect
candidate resource evidence without already asserting RESOURCE_CONTROLS=PROVEN; it must not run
untrusted/project work or an escape attack. That separation prevents circular qualification.

### Case result algebra and report reduction

Every result binds `case_id`, manifest digest and requested binding digest. Closed variants:

| Variant | Additional fields / meaning |
| --- | --- |
| `EXECUTED` | Observer/evidence refs and tagged observation: `COMPLETE` carries the nonempty exact expected-check tuple, each `PASSED` or `FAILED`; `INCOMPLETE` carries reason `OUTPUT_OVERFLOW | TIMEOUT | INTERRUPTED` and evidence refs, never fabricated complete checks. Launch observations are required only for actual native launches. A successful test of an expected denial is EXECUTED/COMPLETE/PASSED even though the forbidden child effect starts zero times. |
| `REFUSED` | Case refusal `SOURCE_MISMATCH | APPROVAL_UNRESOLVED | PREREQUISITE_UNPROVEN | RESOURCE_ENFORCEMENT_UNAVAILABLE | HOST_ROSTER_UNQUALIFIED | RECOVERY_REQUIRED` and independent admission-evidence ref; only the PREREQUISITE_UNPROVEN variant additionally carries the finite prerequisite detail. The case itself did not run; no invented process identity or test output. |
| `UNAVAILABLE` | Capability key, unavailable reason `PRIMITIVE_UNSUPPORTED | HOST_ABSENT | OFFLINE_PATH_UNSUPPORTED | ADAPTER_ABSENT`, and exact probe-evidence ref; the case itself did not run. |
| `NOT_RUN` | Reason `NOT_STARTED | DEPENDENCY_STOP | TOTAL_BUDGET_EXHAUSTED | OWNER_CANCELLED` and plan/event-evidence ref; no test-result or capability-proof payload. |

Each result also carries cleanup disposition `NO_LAUNCH | CLEANUP_CONFIRMED | RECOVERY_REQUIRED`;
only confirmed cleanup carries its positive evidence ref. A pure result must use NO_LAUNCH.
Uncertain launch or missing native cleanup cannot use NO_LAUNCH; it is RECOVERY_REQUIRED.
Refused/unavailable/unrun cases still occupy their expected-cell slot. A malformed manifest
returns a top-level MANIFEST_REFUSED evaluation; it cannot produce a report based on an untrusted expected
cell set. A well-formed report must contain exactly the approved case IDs once each and valid
binding/evidence/check coverage; structural failure returns `EVIDENCE_INVALID`, not a report PASS.
After structural validation, reduce in this exact precedence:

1. Any failed complete executed check, refusal SOURCE_MISMATCH/APPROVAL_UNRESOLVED, or any
   RECOVERY_REQUIRED cleanup/refusal:
   `QUALIFICATION_FAILED`.
2. Otherwise any NOT_RUN or EXECUTED/INCOMPLETE observation: `INCOMPLETE`.
3. Otherwise any UNAVAILABLE or refusal `PREREQUISITE_UNPROVEN`,
   `RESOURCE_ENFORCEMENT_UNAVAILABLE`, `HOST_ROSTER_UNQUALIFIED`: `CAPABILITY_UNAVAILABLE`.
4. Otherwise all expected checks are EXECUTED/COMPLETE/PASSED with complete scope-bound evidence:
   `QUALIFIED_FOR_DECLARED_SCOPE`. A pure-contract scope qualifies pure rules only.

`EVIDENCE_INVALID` and `INVALID_MANIFEST` cannot be embedded as a successful executed check's
authority; expected-negative test inputs stay inside that check's fixture/oracle. Native-capability
aggregation requires executed native-property evidence; successful pure schema/report tests are
not candidates for that aggregation. A pure PASSED cell plus one prerequisite-refused native
cell reduces to CAPABILITY_UNAVAILABLE, retains both entries and does not suppress the pure pass.

The sole public return is this closed tagged union. `request_ref` is an opaque invocation
correlation assigned by the entry boundary before parsing; it carries no approval authority.

| `QualificationEvaluation` tag | Exact payload |
| --- | --- |
| `MANIFEST_REFUSED` | `request_ref`, reason `INVALID_MANIFEST | SOURCE_MISMATCH | APPROVAL_UNRESOLVED`, and `rejection_evidence_ref`; no trusted manifest digest, report or case-set claim is invented |
| `REPORT_REJECTED` | `request_ref`, independently resolved `manifest_digest`, reason `EVIDENCE_INVALID`, detail `INVALID_SHAPE | MISSING_CELL | DUPLICATE_CELL | BINDING_MISMATCH | CHECK_COVERAGE_MISMATCH | UNAUTHENTICATED_EVIDENCE | HOST_COVERAGE_MISMATCH`, and `rejection_evidence_ref`; no report payload |
| `REPORT_ACCEPTED` | `request_ref` and the structurally valid `QualificationReport`; that report's outcome may still be QUALIFICATION_FAILED, INCOMPLETE or CAPABILITY_UNAVAILABLE under the exact reduction above |

Only REPORT_ACCEPTED carries a report, and that tag means structurally accepted, not qualified
hardware, review approval or permission to execute. Exceptions are not
an alternate ordinary return contract. Invalid external dynamic inputs normalize to the tagged
refusal boundary without manufacturing a successful DTO via bypass construction.

## 3. Admission and immutable execution binding

1. Resolve the approved manifest independently of the requesting Agent; validate its scope and
   source identity. No arbitrary profile, command, retry count or load parameter is accepted by
   the public invocation. A manifest proposal has no execution authority.
2. Resolve every expected prerequisite and exact **discovery** roster; compute the dependent case set
   from committed data. Unknown/unobservable effect paths refuse affected host qualification.
3. Bind code plus transitive executable inputs to a protected immutable snapshot through launch.
   Hashing a writable file and executing it later is insufficient. Substitution after admission
   must either be impossible by the proved primitive or refuse before work starts.
4. Validate finite budgets and prove required native controls before untrusted/project work.
   Trusted fixed bootstrap/read-only primitive discovery is separate from hostile workload; it
   must not execute a malicious fixture to discover whether containment existed.
5. Claim one immutable attempt key through a proved exclusive/atomic claim boundary before launch.
   A caller-supplied duplicate key is not a new attempt and cannot obtain a new budget.
6. Wait through process/events with deadlines, observe exact terminal/cleanup evidence and assemble
   the report. No model progress polling, natural-language command reconstruction or hidden retry.

Manifest amendment creates a new reviewed revision and invalidates prior admission. The request
cannot convert five slots with exactly one loaded slot into five loaded slots, even when total
run count stays unchanged. Changing script bytes alone, environment, working directory, approval
owner, resource mapping or evidence destination is equally a new binding.

## 4. Resource scope and finite experiment policy

The following is a proposed lab ceiling, not a production default or current permission to run:

| Dimension | Qualification ceiling / semantics |
| --- | --- |
| Active lanes / automatic retries | Exactly one active lane; zero automatic retries |
| Work per case | Each declared control/attack runs once; reviewer weaken/observe/restore is a separately declared sequence, never an implicit rerun-until-green |
| Workload duration | At most 30 seconds per synthetic workload case; at most 1,200 seconds summed approved case deadlines in one manifest; no test launches that would exceed the remaining total bound |
| Cleanup | At most 10 seconds per launched case, counted within the manifest's total; failure produces `RECOVERY_REQUIRED` |
| CPU | At most 1 CPU-equivalent (1,000 millicpu) for the whole owned workload tree, expressed through an actually proved native hard cap |
| Memory / process count | At most 512 MiB committed memory across the workload tree; at most 4 owned workload processes including descendants |
| Disk/temp | At most 64 MiB of newly allocated writable data across **all** subject-writable roots: workspace outputs, TEMP, user profile/cache, redirected paths and descendants; alternate writable destinations must be denied or counted |
| Containers / build workers | Zero; this investigation does not launch containers or build workers as a fallback |
| Evidence | At most 32 MiB total protected evidence and 256 KiB per case output; overflow stops the case and marks evidence incomplete, never silently truncates a PASS |

Read-only fixture/dependency bytes are separately pinned; the restricted subject may not change
them. Protected evidence and VM checkpoints are outside the workload's 64 MiB only if that subject
cannot write them. Their separate capacity/preflight is mandatory. A free-space reading, dynamic
VHD maximum, command flag, application size check or periodic monitor is not a workload disk cap.
If all writable paths cannot be bounded, report `RESOURCE_ENFORCEMENT_UNAVAILABLE` and do not run
the dependent adversarial cases. Do not discover the limit by exhausting the guest/system disk.

The exact operational ticket must bind the concrete test executables, paths, native cap settings,
case expansion, identities and cleanup resources within these ceilings. Larger or longer work
requires a displayed amended plan and owner decision; an implementer cannot enlarge this table.
CLI startup that cannot fit a ceiling stays unavailable for that manifest, not silently exempt.

## 5. Attempt state and restart reconciliation

These are execution-attempt states, not a replacement workflow state machine:

```text
ABSENT -> CLAIMED -> LAUNCH_BOUND -> RETURN_RECORDED -> CLEANED
                      |                  |
                      +-> RECOVERY_REQUIRED <-+
CLAIMED -> RECOVERY_REQUIRED
```

`ABSENT` means the protected claim resolver proved no claim for this key; an empty transcript
does not establish it. Only the claiming invocation may proceed toward launch. Every state has a
monotonic recorded revision; unexpected transitions refuse. `LAUNCH_BOUND` requires a stable OS
identity tied to the exact attempt and isolation primitive, not a bare reusable PID.

A restarted observer never converts `CLAIMED` or a missing terminal record into a fresh launch.
It either reattaches to independently proved live owned work using one event wait, returns the
verified terminal result, or enters `RECOVERY_REQUIRED`. Crashes before/after native launch and
before/after return persistence must be separate cases; no exactly-once claim may be inferred
from a lock name or a filesystem existence check. Concurrent requests for the same key produce
at most one launch; unresolved native/ledger disagreement permits zero additional launches.

`CLEANED` is immutable final evidence that return and owned cleanup were observed. Replaying it
while a host UI still says Running returns the existing evidence and starts zero work. A failed
test may reach CLEANED; cleanup success does not turn its test result into PASS. Failed cleanup
blocks dependent execution and retains evidence until an owner-scoped recovery operation.

Recovery settlement is append-only and does not rewrite the original attempt. A separate
`RecoveryRecord` binds `recovery_id`, original attempt key and exact observation revision/digest,
owner recovery-grant ref, independent observer/evidence refs, and disposition
`CLEANUP_CONFIRMED | UNRESOLVED`. CLEANUP_CONFIRMED additionally requires exact cleanup and
sentinel evidence refs. The original attempt remains RECOVERY_REQUIRED with its original failure;
it is never relaunched or converted to a successful run. An independent dependency resolver may
clear the cleanup blocker only after validating that exact CLEANUP_CONFIRMED record and unchanged
original evidence. A later attempt requires a new approved attempt key; owner recovery does not
grant an automatic retry or extra budget. Unresolved/conflicting recovery leaves the blocker set.

## 6. Closed per-host effect roster

Each host surface/version/binary digest/enrolled configuration has its own committed roster.
Every offered or otherwise model-reachable effect entry maps to one of `DENIED`, `BROKER_ONLY`
or `READ_ONLY`, with actual reachability and a repeatable oracle. Required categories are shell
and unified execution, interactive stdin/continuation, direct edits/patches, code-mode/nested
execution, MCP/apps/plugins, browser/computer use and client-control/configuration channels.
Nonexistent categories require evidence of absence for that exact surface, not an empty list
supplied by the Agent. New/unmapped/dynamically unobservable entries yield
`HOST_ROSTER_UNQUALIFIED`; configuration readback alone cannot close a contradictory tool roster.

Test through the host's real tool registration/dispatch path using a deterministic offline fixture
only if the exact host supports it. A mock broker, direct call to the hook, isolated request parser
or a session omitting the installed plugin is not installed-host mediation proof. Incompatible
offline execution yields UNAVAILABLE; external model requests and credential transfer remain
forbidden. CLI qualification never qualifies Desktop. No new Desktop bridge is built under this
investigation. Every claimed surface needs both a permitted positive effect and denied bypasses,
including disabled/crashed/timed-out advisory hooks.

The typed coverage contract is mandatory, not a free-form string map:

- `HostEffectRosterKey`: host surface, exact version, binary digest, configuration digest,
  enrollment digest and adapter revision.
- `EffectCategory = SHELL_EXECUTION | INTERACTIVE_CONTINUATION | DIRECT_WRITE | NESTED_EXECUTION
  | EXTENSION_TOOL | BROWSER_COMPUTER | CLIENT_CONTROL`. `EffectDisposition = DENIED | BROKER_ONLY
  | READ_ONLY`; `EffectReachability = MODEL_REACHABLE | CLIENT_REACHABLE | BOTH`.
- `HostEffectEntry`: unique dispatch-entry ID, one EffectCategory, sorted unique alias IDs,
  EffectReachability, EffectDisposition, discovery-evidence ref and planned enforcement
  oracle/case refs. It represents a present entry only, not a completed enforcement observation.
- `HostCategoryCoverage`: exactly one tagged closure for each required category: `PRESENT` holds
  that category and a nonempty unique tuple of HostEffectEntry; `ABSENT` holds the category,
  discovery-surface ref and absence-evidence ref only. ABSENT has no invented dispatch ID,
  aliases, disposition or enforcement oracle. One category can have multiple present entries;
  it cannot be both PRESENT and ABSENT. Client-reachable channels stay within coverage.
- `DiscoveredEffectSet`: the exact roster key, unique actual offered/reachable dispatch-entry and
  alias identities, observer/evidence refs, and explicit nonnegative `unknown_entry_count` and
  `unobservable_surface_count`. Those counts come from the trusted discovery adapter, not a caller.
- `HostRosterDiscoveryCoverage`: approved roster ref/digest, discovered-set ref/digest and the
  comparison result. Canonical **PRESENT** entry/alias sets must match exactly, with no duplicate,
  missing, extra or newly discovered entry; both unknown counts must be zero. Every required
  category has one valid PRESENT/ABSENT closure. This proves discovery completeness only and may
  satisfy HOST_ROSTER_DISCOVERY before executing enforcement cases.
- `HostRosterEnforcementCoverage`: the accepted discovery-coverage ref/digest plus actual
  post-case denial/read-only/broker-only observation refs for every PRESENT entry. Missing,
  failed or wrong-key observations cannot qualify. ABSENT entries rely on discovery absence
  evidence and require no fictitious tool execution. This post-execution coverage is required
  for full-host mediation PROVEN; it is never a prerequisite for its own enforcement cases.

Discovery and enforcement evidence must match the same key. An unobservable dynamic MCP/plugin
surface is not an empty set. Any set/count/key/oracle disagreement returns
`HOST_ROSTER_UNQUALIFIED` and cannot produce a full-host capability PROVEN. For a partial observed
set, preserve the individual observations but do not manufacture a complete roster.

## 7. Acceptance cells and adversarial evidence

The ticket expands each dimension below into unique named cells with exact fixture/oracle refs;
the reviewer checks the frozen expansion before execution. No case is generated ad hoc by a model.

| AC | Required result / negative evidence |
| --- | --- |
| CVQ-AC01 | Ordinary public constructor/round-trip accepts the full positive scope/manifest/report. Missing/extra fields, null in required fields, bool-as-int, illegal enum, duplicate IDs, zero/negative limits and incompatible tagged data reject. |
| CVQ-AC02 | Each of candidate, script/dependency bytes, argv, cwd, environment, run order/count/load, policy owner/revision, resource scope and evidence destination drift causes zero launches. A candidate cannot approve its own altered manifest. |
| CVQ-AC03 | Missing/stale/conflicting prerequisite refuses dependent native/host cells; pure contract checks remain admissible without a VM, CLI, runner, receipt or external provider. |
| CVQ-AC04 | Restricted subject cannot modify protected policy/broker/config/approval/evidence; authorized broker observation remains possible. Workload token is not the protection-owner token; admission-to-launch substitution fails. |
| CVQ-AC05 | Each required resource cap has a native primitive, race model, failure semantics, pre-launch evidence and bounded adversarial reproduction. All disk/temp destinations are counted or denied; unsupported caps refuse before hostile work. |
| CVQ-AC06 | Cancellation, total deadline and disposable owner/broker loss terminate only the exact owned tree within cleanup deadline; unrelated sentinel survives. Breakaway/indirect-child/handle escape paths are tested or explicitly unqualified. |
| CVQ-AC07 | Same-key barrier concurrency launches at most once. Completed evidence plus stale UI launches zero times. Claim/launch/return crash gaps and conflicting PID/evidence never authorize automatic redispatch. |
| CVQ-AC08 | Exact Codex and Claude surface rosters cover all reachable effects and fail closed on unknown paths; real offline host dispatch positive and bypass cases are required independently. Hook failure cannot be promoted to enforcement success. |
| CVQ-AC09 | Every expected cell appears exactly once with bound evidence. Missing/duplicate/forged/wrong-candidate output, empty collection, zero expected mutation reds, timeout, overflow or cleanup failure cannot produce QUALIFIED. Reviewer reads unreduced admitted output; incomplete output remains incomplete. |
| CVQ-AC10 | Q8 reuses the separately delivered WA-04 contract/adapter, if available: forbidden dependency, outside-root construction, undeclared responsibility and missing seam reject; mechanical file splitting stays red and a cohesive large fixture passes. Missing WA-04 returns UNAVAILABLE for that capability, never a new duplicate validator. |

For every acceptance predicate that cannot be proven by strict types, name a reviewer-run reverse
mutation that weakens that predicate, makes the corresponding cell red and returns green after
exact restoration. At least one reviewer mutation must enter a different guard/path than the
implementer's example. Pure-report tests prove the reporting gate only; native and installed-host
evidence are separate and cannot be fabricated by fake ports. The independent helper supplies
finite adversarial evidence; the current-session reviewer alone concludes the review.

## 8. Composition, data, security and operations

The short-lived composition injects `ApprovedManifestPort`, `PrerequisiteEvidencePort`,
`AttemptClaimPort`, `ImmutableSnapshotPort`, `ProtectedExecutionPort`, `CompletionWaitPort` and
`EvidenceObservationPort`. Pure admission/report assembly never spawns, reads ambient credentials,
writes active policy, invokes Git integration or modifies VM state. Fake ports support deterministic
source-only tests; qualification of their real counterparts is a different result. Source modules
separate contracts, admission, execution, recovery, host adapters and evidence responsibilities.

Data/pipeline/lifetime ownership follows the architecture map. No target runtime dependency on
Johnny, new provider, database deployment, telemetry pipeline or cache service is required by this
qualification SPEC. Durable recovery storage must prove the claim/settlement semantics above;
its backend is investigated, not silently chosen during product implementation.

`XSS_NOT_APPLICABLE` for this CLI/OS slice: no untrusted Browser/WebView/HTML/JavaScript sink is
introduced. Any new renderer or privileged bridge is an upstream change, not a ticket detail.
Exact lab VM: `7701b26b-5b5a-42c0-b1e1-36d34dfdaa46` / `Johnny-MSIX-Lab-20260905`. Before effects,
bind fresh guest/VM identity, admitted protected OS/module bootstrap, owned checkpoint and concrete
subject/evidence roots. The previous name-import diagnostic script is not a mutating executor.
No physical-host account/ACL/service/policy change, external networking/model call, real credential
capture, package install or VM restore/delete is authorized by approving the pure contract slice.

Recovery is fail-closed. Preserve failed attempts; no reset to manufacture a clean result.
Checkpoint creation/restore, guest account/ACL work, fixture/tool transfer and native execution
each need an exact operational ticket/authority. Inspection capability is not effect authority.
No guessed account/service name, approval receipt or gateway is created to avoid this boundary.

## 9. Ticketing sequence — CVQ-01 preparation approved; execution not granted

1. **CVQ-01: qualification contracts and pure prerequisite/report admission.** One independently
   observable source-only slice: reject malformed/forged/incomplete qualification and permit exact
   pure cases while dependent OS/host cases remain unqualified. Proposed boundaries:
   `library/controlled_verification/qualification_contracts.py`,
   `library/controlled_verification/qualification_admission.py`,
   `library/controlled_verification/__init__.py`,
   `tests/test_verification_qualification_contracts.py`,
   `tests/test_verification_qualification_admission.py`. No subprocess, filesystem effect,
   broker implementation, VM access, production integration or central Router enlargement.
2. **CVQ-02: exact lab recovery/bootstrap operation.** Freeze a reviewed protected recipe, guest
   entry and owned checkpoint; read back actual identities before any new account/ACL/fixture.
   No reuse of the historical provisioning ticket as a new effect grant.
3. **CVQ-03: Windows primitive investigation.** Bind a finite subset of native identity/immutable
   launch/resource/cleanup/claim cases. Return native proofs or explicit unsupported semantics;
   required missing containment prevents dependent hostile execution.
4. **CVQ-04: host mediation and composed capability report.** Independent exact-surface rosters and
   offline evidence; unavailable surfaces stay unavailable. Q8 consumes WA-04 evidence only after
   its separately approved delivery. No release or replacement source validator.

CVQ-01's exact closure/model/profile and normal constructor/type preflight belong in its
ticket, not an implementation prompt. Standard implementation uses the registered
`implementation-standard`, review `ticket-review`; elevation follows the existing assessment rule,
not this document's profile name. Same-lifetime dispatch uses the existing owner lane and event wait.

## 10. Approval and continuation

### Owner signature — 2026-09-09

The human owner replied `核准` to SPEC revision 03 at
`161c4e095697fff6e4693b8d9bfce866878277dd`, LF SHA-256
`e5ed081dcbb3f1aadfbe43d874273fabafea521e49c6301496ea24b9054c46a5`, together with its exact
architecture, shared Context and [Grill](../../doc/context/controlled-verification/grill-r01.md).
CONTEXT records the first seal before this signature takes effect. Revision 04 adds lifecycle,
Context reattachment and this signature only; sections 1–8's approved behavior is unchanged.

`ACTION_COMPLETED -> AUTO_CONTINUE -> TICKETS` permits **CVQ-01 preparation only**. Its normal
ticket schema/type preflight, exact closure approval and dispatch confirmation remain required.
VM operations, other ticket preparation, source implementation, native effects, installation,
integration, push and release are not granted by this signature. No investigation result or
enforcement capability is claimed. Never report a prepared ticket as dispatched.

## 11. Proposed amendment — explicit claims and source grammar

This section plus the [wire appendix](controlled-verification-qualification-wire.md) is one
pending amendment to this SPEC, not a second specification. Sections 1–10 preserve approved
revision 04 (LF `4cad6a88b9d151a05bf409f8b61bc97580e80303f58a2377cb0301815b999a1d`).
Only the replacements enumerated here supersede those sections **after exact owner approval**.
Until then neither this draft nor revision 04 admits another correction to failed closure 02.

Authority: owner adopted convergence proposal 02 at `fa6b06a0beb9f9e25bb582a95b565c12e5d3595a`,
LF `3fbe8c18b15992d86b99487b769ae411caac410102bd6480c3a94e4c7b78e93d`, by replying 「採用」.
That settles design direction, not the exact field catalog below. D1/D2/D3, sealed Context,
lab bounds, attempt/recovery semantics and native/host proof requirements do not change.

### 11.1 Explicit claim applicability and connected observations

Replace section 2's nullable/"when applicable" interpretation by tagged `CapabilityKey`,
`CaseSubject`, `CapabilityProof` and the exact wire appendix. Case kind fixes claim scope:

| Case kind / subject | ClaimScope | Binding / roster |
| --- | --- | --- |
| PURE_RULE, SOURCE_PROPERTY | PURE_RULE | PURE_CONTRACT; NO_ROSTER even for a host-scoped rule |
| TRUSTED_NATIVE_DISCOVERY; non-HOST_MEDIATION family | NATIVE_PROBE | WINDOWS_LAB; NO_ROSTER; no prerequisite on its own probe |
| TRUSTED_NATIVE_DISCOVERY; HOST_MEDIATION family | HOST_DISCOVERY | WINDOWS_LAB; HOST_DISCOVERY subject and independent expected roster plan |
| ADVERSARIAL_WORKLOAD | NATIVE_PROPERTY | WINDOWS_LAB; NO_ROSTER; not full-host mediation proof |
| REAL_HOST_PROPERTY | HOST_PROPERTY | WINDOWS_LAB; HOST_PROPERTY subject, independently accepted discovery prerequisite |

HOST_MEDIATION requires HostCapabilityKey. Other families may use either key alternative as
explicitly approved; pure claims never qualify a native/host claim with the same key. Native
bindings require platform WINDOWS. Capability requirements name one declared capability ID,
one exact key, one scope and a nonempty exact case set; every case in that set must match all
three. `QualificationCase.capability_id` is required and must belong to scope.capability_ids;
its required `binding_digest` is the independent approval record's pin for that exact binding
body. Resolve the expected digest from the approved case before looking at report evidence;
every CaseResult and case/check/cleanup subject must match it. The approval composition binds
body and digest together; the pure evaluator compares both to the approved record, not a
caller-selected digest or a newly invented canonical hash of a self-referential manifest.
Requirement IDs are unique, not merged by capability family.

The report supplies only observation-ID/evidence-ref pairs for those requirements. The three
existing ports carry the complete graph: approved manifest plus expected roster plans; exact
prerequisite bindings; authenticated typed observed payloads (including capability observations).
There is no fourth resolver, ambient evidence map or caller-provided authenticity boolean.

The evidence adapter is independently composed against its protected, immutable observation
index. It checks record ref/digest/observer and supplies typed FOUND or real rejection evidence.
Admission compares each returned subject to a request derived from the approved case/requirement,
not a subject chosen in report JSON. Returned outer ref/observer must equal corresponding
payload fields; referenced digests must equal the separately resolved records. Future evidence
digests are **not** invented in the pre-launch plan. For a first observation its authenticity
comes from the bound resolver, not from comparing its self-reported hash to itself. Subsequent
discovery/prerequisite pins compare exact independently approved/resolved digests.

Ordinary schema validation is not authenticity. Missing/conflicting capability records or
subject/ref/digest/observer disagreement return REPORT_REJECTED / UNAUTHENTICATED_EVIDENCE.
Wrong case/binding/claim scope returns BINDING_MISMATCH; malformed shape INVALID_SHAPE; missing,
duplicate or extra observation IDs follow the corresponding exact-set rejection. Claim result
must match reduction of its already validated case subset: qualified→PROVEN, failed→FAILED,
incomplete→NOT_RUN, unavailable→UNAVAILABLE. NOT_RUN here means no completed capability verdict;
an interrupted case retains its actual execution record, not a fabricated unstarted case.

Proof alternatives are exhaustive: pure-rule proof; measured native proof (all three primitive,
race and failure refs); unavailable-probe proof; incomplete/not-run event proof; refused-claim
proof using actual admission evidence. The latter preserves section 2's pre-launch refusal
outcomes without inventing a measured primitive. It is a field-level transcription detail in
this pending packet, not an already-approved third correction. PROVEN requires complete passed
cases and PURE_RULE or MEASURED_NATIVE proof as appropriate. FAILED measured records retain all
primitive refs. Refused, unavailable and not-run evidence can never support PROVEN.

### 11.2 Expected plan versus observed host evidence

An approved roster plan contains planned presence/categories/entries/aliases/dispositions/oracles
only. It contains no discovery/absence evidence or future completion prerequisite. Section 6's
HostCategoryCoverage remains the later observed form. FOUND transports the actual DiscoveredEffectSet,
HostRosterDiscoveryCoverage and HostRosterEnforcementCoverage; neither a comparison enum nor an
opaque reference substitutes for those bodies. Validate exact key, seven categories, entry/alias
sets, observer and per-entry oracle/disposition bindings. Planned enforcement case IDs are future
intent: a discovery-only manifest need not contain those cases or their future evidence pins.
A later independently approved HOST_PROPERTY manifest binds completed discovery and requires its
requested case IDs to occur in the same-key plan. Do not require a future enforcement manifest
or discovery-result digest merely to approve the first probe. Absence has no invented entry,
oracle or launch. In this contract HOST_DISCOVERY requirements have exactly one case ID; this
single bounded trusted discovery case covers the entire roster. All present-entry discovery
evidence therefore derives its CaseEvidenceSubject from that one approved case and binding pin,
never by inspecting a returned payload and choosing a convenient case. Multiple independent
discovery requirements/host surfaces remain possible; multi-case aggregation within one discovery
requirement would need a separately approved mapping contract.

A later HOST_PROPERTY case resolves the independently accepted discovery prerequisite and its
exact coverage ref/digest/key; it does not re-run the discovery or require the earlier discovery
case to be in its own manifest. The protected accepted-discovery record attests the earlier
case/entry authenticity; the current evaluator still compares the returned coverage/set/category
bodies to the approved plan and exact accepted pins. For fresh HOST_DISCOVERY, all entry and
absence evidence is resolved/authenticated as above before any accepted-discovery claim. This
distinguishes consuming a qualified prerequisite from trying to recreate its earlier authority.

All-ABSENT discovery is valid only with seven independently authenticated absence closures,
matching approved empty plan, empty actual sets and zero unknown/unobservable counts. Its
enforcement shape is ZERO_PRESENT_ENTRIES with only the accepted discovery pin. It proves no
positive effect and cannot produce full-host PROVEN; dependent host-property admission returns
HOST_ROSTER_UNQUALIFIED. Nonempty expected versus empty actual is a mismatch, not this alternative.
Nonzero unknown/unobservable counts and MISMATCH may be retained as negative observations; they
cannot satisfy the discovery prerequisite. Section 6's permitted-positive and denied-bypass
requirements still apply through the approved expected check/oracle set; a pure fake cannot
authenticate actual host dispatch. No mocks, assumed tool absence or CLI/Desktop substitution.

### 11.3 Closed CQ11 source grammar

Apply the ticket's constituent DAG to every import scope, normalizing relative/absolute/package
forms and aliases. Resolve facade re-exports to their actual constituent; reject wildcard,
cycle, reverse edge or indirect forbidden dependency. Do not import/execute production to inspect it.

| Grammar part | Only permitted surface |
| --- | --- |
| Schema external imports | __future__.annotations; enum.Enum; typing.Annotated, Literal, Mapping, Protocol, TypeAlias, Union; pydantic.BaseModel, ConfigDict, Field, StringConstraints, Discriminator, Tag, model_validator |
| Behavior-only additional imports | pydantic.TypeAdapter, ValidationError; no effect library or json dependency |
| Builtin calls | len, set, frozenset, tuple, sorted, any, all, isinstance, enumerate, zip; ValueError and TypeError construction |
| Schema calls | Listed Pydantic schema constructors/decorators; exact checked DTO/enum constructors in the appendix |
| Mapping.get | Only within a local isinstance(receiver, Mapping) true branch, receiver unchanged; no arbitrary same-name method |
| Local helpers | Direct statically resolved module-local calls, typed parameters/return, whole-body inspection, acyclic call graph |
| Behavior model calls | model_validate/model_validate_json/model_dump/model_dump_json on the exact checked model; TypeAdapter construction and validate_python/validate_json/dump_python/dump_json on its resolved instance |
| Behavior port calls | resolve on one of the three explicit typed injected parameters only |
| Classes | Checked DTOs/enums/three Protocols; exact schema bases QualificationModel, _CommonBinding, _CaseResultIdentity. BaseModel/QualificationModel inheritance; enum (str, Enum) and Protocol are the only exceptions |
| Facades | Docstrings, future imports, explicit re-exports and literal immutable __all__ only |

Helpers/validators/discriminators allow scalar/tuple/set expressions, comparisons, comprehensions,
local assignment, conditionals, finite collection iteration, return and the listed exceptions.
Reject unlisted calls/imports/decorators, unresolved/dynamic receivers, shadowing/rebinding approved
callees, callable assignment aliases/parameters/returns, recursion, while, async/generator functions,
context managers, global/nonlocal or attribute/subscript writes, custom metaclasses/magic methods/
descriptors, Any/casts, bypass construction/copy-update and reflective/dynamic execution.
Module state allows immutable literals/tuples, checked aliases/schema declarations; only the common
base's literal ConfigDict is exempted for schema configuration. No ambient mutable service.

This bounded source grammar is neither an arbitrary Python purity proof nor a runtime sandbox.
Strict typing remains independent. Unsupported AST/resolution fails closed. A legitimate new
dependency requires an explicit policy amendment, not a broader checker fallback.

### 11.4 Approval object and migration

Exact approval must bind revision 06, wire appendix revision 02 and ticket document 06 / closure 03
by their final LF digests and common control commit. The old schema candidate stays historical;
additive source migration may begin only after that approval and fresh allocation/type preflight.
No constructor compatibility is promised for the never-integrated experimental candidate. External
authority, three-port composition, same-lifetime event waits and all native effects remain unchanged.

## 12. Exact owner approval — 2026-09-18

The owner replied **「核准」** to the final packet at
`965e16b00d6049be6552465ac1ce1cbac968a8cb`: this SPEC revision 06 LF
`80daa0bd591c3f1419c9b683bfdff53ea721ebfa1239ac1e68306552a9e95054`, wire appendix revision 02 LF
`580104e585ba46a81aff17f3ff18100164618973b67d5c3db0040e29f88958a8`, and CVQ-01 document 06 /
closure 03 LF `574b60b9a13ae4253d27ac17c932df67a110c436f265873fa8b031e3ed682c8e`.
Section 11 and the wire contract are now approved; their proposal/approval-pending prose above
is retained as the historical approval object, not a new unresolved decision. Revision 07 is
lifecycle/signature only. The new bounded schema phase and its two-phase ordering are authorized;
actual parent schema preflight remains necessary before behavior. No integration, push, release,
VM, provider, host enrollment or installation effect is granted. D1/D2/D3 and sealed Context stay
unchanged. Ticket document 07 records the exact owner/worktree/baseline and next route.
