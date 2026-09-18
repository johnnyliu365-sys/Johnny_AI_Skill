# Qualification wire catalog — proposed appendix

| Field | Value |
| --- | --- |
| ID / kind / revision | `SPEC-APPENDIX-CVQ-WIRE-20260918-01` / `SPEC_CONTRACT_APPENDIX` / `03` |
| State | `OWNER_APPROVED / CVQ01_SCHEMA_RESUMPTION_AUTHORIZED`; revision 03 records approval only |
| Sole owning SPEC | [Qualification SPEC](controlled-verification-qualification.md), revision 07, sections 11–12; this appendix is not an independent specification |
| Scope | Exact public schema and finite constructor/alias/field catalog for proposed CVQ-01 closure 03; no source implementation or runtime claim |

## 1. Notation and field rules

The catalog below is normative proposed wire shape, not reflection of `9796790`. Each line is
one concrete public DTO: `Name = field:Type; ...`. Expand `@Group` before counting fields.
Every field is required except an explicit `=default` below. Fixed discriminator defaults are
allowed for **direct** constructors; tagged-union JSON must supply its discriminator. Wrong tags
and null always reject. No nullable field is permitted. `Field(...)` constraints alone do not
create defaults. Frozen extra-forbidden models; exact JSON values, no normalization/coercion.

`Id` = OpaqueMetadataId (`^[a-z][a-z0-9-]{2,127}$`); `Digest` = 64 lowercase hex;
`Text` = BoundedText (1..128 code points, no transform); `Pos` = PositiveInteger;
`NonNeg` = NonNegativeInteger; `Zero` = ZeroOnly; `Lane` = ActiveLaneCount (strict integer 1).
All integer types reject bool/float/string. `T+` = nonempty immutable tuple; `T*` = possibly empty
immutable tuple. JSON represents tuples as arrays. `L(V)` is literal V; `S(E:a,b)` is exactly
those values of enum E, not its other members. Field order below is constructor catalog order;
JSON object order is not a new equality/authority requirement.

Groups (not DTOs; inherited fields count once per concrete DTO):

```text
CommonBinding = project_id:Id; baseline_digest:Digest; manifest_revision:Pos; manifest_digest:Digest; case_id:Id; attempt_key:Id; fixture_digest:Digest; approved_record_ref:Id; evidence_scope_ref:Id
CaseIdentity = case_id:Id; manifest_digest:Digest; binding_digest:Digest
EvidenceIdentity = evidence_ref:Id; evidence_digest:Digest; observer_ref:Id
```

QualificationModel is the single immutable strict BaseModel configuration owner; _CommonBinding
and _CaseResultIdentity may factor those two groups. No other public/base DTO is inferred.
EvidenceIdentity is notation only, not permission for another schema base. Protocol methods:
`ApprovedManifestPort.resolve(request_ref: Id) -> ApprovedManifestResolution`;
`PrerequisiteEvidencePort.resolve(key: PrerequisiteKey) -> PrerequisiteResolution`;
`EvidenceObservationPort.resolve(request: EvidenceObservationRequest) -> EvidenceResolution`.
No write method or fourth port. Ordinary string enum values may parse from JSON; that is not
permission to coerce integers, trim IDs or use bypass constructors.

## 2. Concrete public DTO catalog

### Values and bindings

```text
PlatformCapabilityKey = tag:L(PLATFORM)=PLATFORM; family:S(CapabilityFamily:PLAN_BINDING,POLICY_ISOLATION,RESOURCE_CONTAINMENT,OWNED_CLEANUP,ATTEMPT_RECONCILIATION,RESPONSIBILITY_ADMISSION); adapter_revision:Pos; platform:Platform
HostCapabilityKey = tag:L(HOST)=HOST; family:CapabilityFamily; adapter_revision:Pos; platform:Platform; host_surface:HostSurface
PureContractBinding = @CommonBinding; kind:L(PURE_CONTRACT)=PURE_CONTRACT
NativePreLaunchBinding = @CommonBinding; kind:L(WINDOWS_LAB)=WINDOWS_LAB; protected_policy_revision:Pos; protected_policy_digest:Digest; protected_policy_owner_ref:Id; restricted_subject_ref:Id; broker_binary_digest:Digest; broker_configuration_digest:Digest; launcher_ref:Id; enrollment_ref:Id; immutable_snapshot_ref:Id; executable_digest:Digest; dependency_digest:Digest; argv_digest:Digest; cwd_digest:Digest; environment_plan_digest:Digest; resource_plan_ref:Id; vm_ref:Id; guest_ref:Id; checkpoint_ref:Id; protected_evidence_owner_ref:Id
LaunchObservation = attempt_key:Id; prelaunch_binding_digest:Digest; observation_revision:Pos; observer_ref:Id; os_execution_identity_ref:Id; isolation_identity_ref:Id; evidence_digest:Digest
```

### Prerequisites

```text
PrerequisiteKey = kind:PrerequisiteKind; scope_id:Id; capability_key:CapabilityKey; adapter_revision:Pos
PrerequisiteRequirement = key:PrerequisiteKey; expected_observation_revision:Pos; expected_evidence_digest:Digest
PrerequisiteEvidenceBinding = key:PrerequisiteKey; observation_revision:Pos; evidence_digest:Digest; observer_ref:Id; source_ref:Id; disposition:PrerequisiteDisposition
FoundPrerequisite = tag:L(FOUND)=FOUND; binding:PrerequisiteEvidenceBinding
MissingPrerequisite = tag:L(MISSING)=MISSING
ConflictingPrerequisite = tag:L(CONFLICTING)=CONFLICTING; evidence_ref:Id
QualificationPrerequisiteSet = requirements:PrerequisiteRequirement+
```

### Roster plan, case subjects and observations

```text
HostEffectRosterKey = host_surface:HostSurface; host_version:Text; binary_digest:Digest; configuration_digest:Digest; enrollment_digest:Digest; adapter_revision:Pos
PlannedHostEffectEntry = dispatch_entry_id:Id; category:EffectCategory; alias_ids:Id+; reachability:EffectReachability; disposition:EffectDisposition; planned_enforcement_oracle_ref:Id; planned_enforcement_case_refs:Id+
PresentHostCategoryPlan = tag:L(PRESENT)=PRESENT; category:EffectCategory; entries:PlannedHostEffectEntry+
AbsentHostCategoryPlan = tag:L(ABSENT)=ABSENT; category:EffectCategory
ApprovedHostRosterPlan = roster_key:HostEffectRosterKey; approved_roster_ref:Id; approved_roster_digest:Digest; categories:HostCategoryPlan+
NoRosterSubject = tag:L(NO_ROSTER)=NO_ROSTER
HostDiscoverySubject = tag:L(HOST_DISCOVERY)=HOST_DISCOVERY; roster_key:HostEffectRosterKey; approved_roster_ref:Id; approved_roster_digest:Digest
HostPropertySubject = tag:L(HOST_PROPERTY)=HOST_PROPERTY; roster_key:HostEffectRosterKey; approved_roster_ref:Id; approved_roster_digest:Digest; discovery_coverage_ref:Id; discovery_coverage_digest:Digest
HostEffectEntry = dispatch_entry_id:Id; category:EffectCategory; alias_ids:Id+; reachability:EffectReachability; disposition:EffectDisposition; discovery_evidence_ref:Id; planned_enforcement_oracle_ref:Id; planned_enforcement_case_refs:Id+
PresentHostCategoryCoverage = tag:L(PRESENT)=PRESENT; category:EffectCategory; entries:HostEffectEntry+
AbsentHostCategoryCoverage = tag:L(ABSENT)=ABSENT; category:EffectCategory; discovery_surface_ref:Id; absence_evidence_ref:Id
DiscoveredEffectSet = roster_key:HostEffectRosterKey; dispatch_entry_ids:Id*; alias_ids:Id*; observer_ref:Id; evidence_ref:Id; unknown_entry_count:NonNeg; unobservable_surface_count:NonNeg
HostRosterDiscoveryCoverage = roster_key:HostEffectRosterKey; approved_roster_ref:Id; approved_roster_digest:Digest; discovered_set_ref:Id; discovered_set_digest:Digest; comparison:RosterComparison; categories:HostCategoryCoverage+
HostEffectObservation = dispatch_entry_id:Id; roster_key:HostEffectRosterKey; disposition:EffectDisposition; oracle_ref:Id; evidence_ref:Id; observer_ref:Id; observation:Observation
PresentHostEnforcementCoverage = tag:L(PRESENT_ENTRIES)=PRESENT_ENTRIES; discovery_coverage_ref:Id; discovery_coverage_digest:Digest; observations:HostEffectObservation+
ZeroPresentHostEnforcementCoverage = tag:L(ZERO_PRESENT_ENTRIES)=ZERO_PRESENT_ENTRIES; discovery_coverage_ref:Id; discovery_coverage_digest:Digest
NoObservedRoster = tag:L(NO_OBSERVED_ROSTER)=NO_OBSERVED_ROSTER
DiscoveryEvidenceLink = tag:L(DISCOVERY)=DISCOVERY; discovery_coverage_ref:Id; discovery_coverage_digest:Digest
EnforcementEvidenceLink = tag:L(ENFORCEMENT)=ENFORCEMENT; discovery_coverage_ref:Id; discovery_coverage_digest:Digest; enforcement_coverage_ref:Id; enforcement_coverage_digest:Digest
```

### Manifest

```text
QualificationScope = project_id:Id; baseline_digest:Digest; capability_ids:Id+; manifest_revision:Pos; manifest_digest:Digest
ResourceBounds = workload_duration_seconds:Pos<=30; cpu_millicpu:Pos<=1000; memory_bytes:Pos<=536870912; process_count:Pos<=4; disk_bytes:Pos<=67108864; automatic_retry_count:Zero=0; container_count:Zero=0; build_worker_count:Zero=0
CleanupBounds = cleanup_seconds:Pos<=10
EvidenceBounds = total_bytes:Pos<=33554432; case_output_bytes:Pos<=262144
QualificationCase = case_id:Id; capability_id:Id; capability_key:CapabilityKey; kind:CaseKind; role:CaseRole; binding:AttemptBinding; binding_digest:Digest; fixture_digest:Digest; executable_digest:Digest; dependency_digests:Digest+; argv_digest:Digest; cwd_digest:Digest; environment_plan_digest:Digest; expected_oracle_ref:Id; prerequisite_keys:PrerequisiteKey+; prerequisite_requirements:PrerequisiteRequirement+; expected_check_ids:Id+; subject:CaseSubject; resource_bounds:ResourceBounds; cleanup_bounds:CleanupBounds; evidence_bounds:EvidenceBounds
CapabilityRequirement = observation_id:Id; capability_id:Id; capability_key:CapabilityKey; claim_scope:ClaimScope; case_ids:Id+
QualificationManifest = scope:QualificationScope; source_ref:Id; owner_approved_revision:Pos; owner_approved_digest:Digest; cases:QualificationCase+; capability_requirements:CapabilityRequirement+; active_lanes:Lane=1; total_budget_seconds:Pos<=1200; evidence_destination_ref:Id
```

### Report and evaluation

```text
CheckObservation = check_id:Id; result:CheckResult; evidence_ref:Id
CompleteExecutionObservation = tag:L(COMPLETE)=COMPLETE; observer_ref:Id; checks:CheckObservation+; evidence_refs:Id+
IncompleteExecutionObservation = tag:L(INCOMPLETE)=INCOMPLETE; observer_ref:Id; reason:IncompleteReason; evidence_refs:Id+
PureRuleProof = tag:L(PURE_RULE)=PURE_RULE
MeasuredNativeProof = tag:L(MEASURED_NATIVE)=MEASURED_NATIVE; native_primitive_ref:Id; race_model_ref:Id; failure_semantics_ref:Id
UnavailableProbeProof = tag:L(UNAVAILABLE_PROBE)=UNAVAILABLE_PROBE; reason:UnavailableReason; probe_evidence_ref:Id
NotCompletedProof = tag:L(NOT_COMPLETED)=NOT_COMPLETED; reason:NotCompletedReason; plan_event_evidence_ref:Id
RefusedClaimProof = tag:L(REFUSED_CLAIM)=REFUSED_CLAIM; reason:CaseRefusalReason; admission_evidence_ref:Id
CapabilityObservation = observation_id:Id; capability_id:Id; capability_key:CapabilityKey; claim_scope:ClaimScope; case_ids:Id+; observer_ref:Id; evidence_ref:Id; result:Observation; proof:CapabilityProof; roster_evidence:ObservedRosterLink
CapabilityClaim = observation_id:Id; evidence_ref:Id
ExecutedPureCaseResult = @CaseIdentity; tag:L(EXECUTED)=EXECUTED; cleanup:L(NO_LAUNCH)=NO_LAUNCH; execution:ExecutionObservation
ExecutedNativeConfirmedCaseResult = @CaseIdentity; tag:L(EXECUTED)=EXECUTED; cleanup:L(CLEANUP_CONFIRMED)=CLEANUP_CONFIRMED; cleanup_evidence_ref:Id; launch_observation:LaunchObservation; execution:ExecutionObservation
ExecutedNativeRecoveryCaseResult = @CaseIdentity; tag:L(EXECUTED)=EXECUTED; cleanup:L(RECOVERY_REQUIRED)=RECOVERY_REQUIRED; launch_observation:LaunchObservation; execution:ExecutionObservation
RefusedPrerequisiteCaseResult = @CaseIdentity; tag:L(REFUSED)=REFUSED; cleanup:L(NO_LAUNCH)=NO_LAUNCH; refusal_reason:L(PREREQUISITE_UNPROVEN)=PREREQUISITE_UNPROVEN; prerequisite_detail:PrerequisiteDetail; admission_evidence_ref:Id
RefusedOtherCaseResult = @CaseIdentity; tag:L(REFUSED)=REFUSED; cleanup:L(NO_LAUNCH)=NO_LAUNCH; refusal_reason:S(CaseRefusalReason:SOURCE_MISMATCH,APPROVAL_UNRESOLVED,RESOURCE_ENFORCEMENT_UNAVAILABLE,HOST_ROSTER_UNQUALIFIED); admission_evidence_ref:Id
RefusedRecoveryCaseResult = @CaseIdentity; tag:L(REFUSED)=REFUSED; cleanup:L(RECOVERY_REQUIRED)=RECOVERY_REQUIRED; refusal_reason:L(RECOVERY_REQUIRED)=RECOVERY_REQUIRED; admission_evidence_ref:Id
UnavailableCaseResult = @CaseIdentity; tag:L(UNAVAILABLE)=UNAVAILABLE; cleanup:L(NO_LAUNCH)=NO_LAUNCH; capability_key:CapabilityKey; unavailable_reason:UnavailableReason; probe_evidence_ref:Id
NotRunCaseResult = @CaseIdentity; tag:L(NOT_RUN)=NOT_RUN; cleanup:L(NO_LAUNCH)=NO_LAUNCH; not_run_reason:NotRunReason; plan_event_evidence_ref:Id
QualificationReport = manifest_digest:Digest; baseline_digest:Digest; results:CaseResult+; capability_claims:CapabilityClaim+; outcome:ReportOutcome
ManifestRefusedEvaluation = tag:L(MANIFEST_REFUSED)=MANIFEST_REFUSED; request_ref:Id; manifest_refusal_reason:ManifestRefusalReason; rejection_evidence_ref:Id
ReportRejectedEvaluation = tag:L(REPORT_REJECTED)=REPORT_REJECTED; request_ref:Id; manifest_digest:Digest; reason:L(EVIDENCE_INVALID)=EVIDENCE_INVALID; report_rejection_detail:ReportRejectionDetail; rejection_evidence_ref:Id
ReportAcceptedEvaluation = tag:L(REPORT_ACCEPTED)=REPORT_ACCEPTED; request_ref:Id; report:QualificationReport
```

Proof compatibility: PURE_RULE proof only with PURE_RULE scope and PROVEN/FAILED; MEASURED_NATIVE
only non-pure scope and PROVEN/FAILED. UNAVAILABLE_PROBE only UNAVAILABLE; NOT_COMPLETED only
NOT_RUN; REFUSED_CLAIM only FAILED for SOURCE_MISMATCH/APPROVAL_UNRESOLVED/RECOVERY_REQUIRED,
otherwise UNAVAILABLE. Its admission ref/reason must identify an actual controlling refused case.
Unavailable/not-completed reason/ref must identify an actual controlling unavailable/incomplete/
not-run case. All require evidence authentication; they never overwrite CaseResults or invent a
launch. For a failed native subset with no refused case, MEASURED_NATIVE evidence remains required.

### Three-port graph

```text
ApprovedManifestFound = tag:L(FOUND)=FOUND; manifest:QualificationManifest; roster_plans:ApprovedHostRosterPlan*
ApprovedManifestMissing = tag:L(MISSING)=MISSING; rejection_evidence_ref:Id
ApprovedManifestConflicting = tag:L(CONFLICTING)=CONFLICTING; rejection_evidence_ref:Id
CaseEvidenceSubject = tag:L(CASE)=CASE; case_id:Id; manifest_digest:Digest; binding_digest:Digest
CheckEvidenceSubject = tag:L(CHECK)=CHECK; case_id:Id; manifest_digest:Digest; check_id:Id; binding_digest:Digest
CleanupEvidenceSubject = tag:L(CLEANUP)=CLEANUP; case_id:Id; manifest_digest:Digest; binding_digest:Digest; cleanup:L(CLEANUP_CONFIRMED)=CLEANUP_CONFIRMED
PrerequisiteEvidenceSubject = tag:L(PREREQUISITE)=PREREQUISITE; key:PrerequisiteKey; observation_revision:Pos; evidence_digest:Digest
RosterAbsenceSubject = tag:L(ROSTER_ABSENCE)=ROSTER_ABSENCE; roster_key:HostEffectRosterKey; category:EffectCategory; discovery_surface_ref:Id
DiscoveredSetSubject = tag:L(DISCOVERED_SET)=DISCOVERED_SET; roster_key:HostEffectRosterKey
DiscoveryCoverageSubject = tag:L(DISCOVERY_COVERAGE)=DISCOVERY_COVERAGE; roster_key:HostEffectRosterKey; approved_roster_ref:Id; approved_roster_digest:Digest
EntryEnforcementSubject = tag:L(ENTRY_ENFORCEMENT)=ENTRY_ENFORCEMENT; roster_key:HostEffectRosterKey; dispatch_entry_id:Id; oracle_ref:Id; disposition:EffectDisposition
EnforcementCoverageSubject = tag:L(ENFORCEMENT_COVERAGE)=ENFORCEMENT_COVERAGE; roster_key:HostEffectRosterKey; discovery_coverage_ref:Id; discovery_coverage_digest:Digest
CapabilityEvidenceSubject = tag:L(CAPABILITY)=CAPABILITY; observation_id:Id; capability_id:Id; capability_key:CapabilityKey; claim_scope:ClaimScope; case_ids:Id+
EvidenceObservationRequest = evidence_ref:Id; subject:EvidenceSubject
AuthenticatedEvidence = @EvidenceIdentity; tag:L(FOUND)=FOUND; kind:L(PLAIN)=PLAIN; subject:PlainEvidenceSubject
AuthenticatedDiscoveredSet = @EvidenceIdentity; tag:L(FOUND)=FOUND; kind:L(DISCOVERED_SET)=DISCOVERED_SET; subject:DiscoveredSetSubject; payload:DiscoveredEffectSet
AuthenticatedDiscoveryCoverage = @EvidenceIdentity; tag:L(FOUND)=FOUND; kind:L(DISCOVERY_COVERAGE)=DISCOVERY_COVERAGE; subject:DiscoveryCoverageSubject; payload:HostRosterDiscoveryCoverage
AuthenticatedEnforcementCoverage = @EvidenceIdentity; tag:L(FOUND)=FOUND; kind:L(ENFORCEMENT_COVERAGE)=ENFORCEMENT_COVERAGE; subject:EnforcementCoverageSubject; payload:HostRosterEnforcementCoverage
AuthenticatedCapabilityObservation = @EvidenceIdentity; tag:L(FOUND)=FOUND; kind:L(CAPABILITY)=CAPABILITY; subject:CapabilityEvidenceSubject; payload:CapabilityObservation
MissingEvidence = tag:L(MISSING)=MISSING; rejection_evidence_ref:Id
ConflictingEvidence = tag:L(CONFLICTING)=CONFLICTING; rejection_evidence_ref:Id
```

The port's PLAIN form authenticates case/check/cleanup/prerequisite/absence/entry observations,
not a substitute empty payload for discovered sets/coverage/capabilities. Host entry discovery
evidence authenticates against the exact discovery case's CaseEvidenceSubject; enforcement refs
authenticate against EntryEnforcementSubject. Only actual confirmed cleanup uses CleanupEvidenceSubject.
Require requested and returned subjects to match fully; FOUND records cannot silently choose
another variant. Manifest FOUND roster plans exactly cover unique host subject plan pins, with
no duplicate/extra plan. Pure/native-primitive-only manifest has an empty tuple, not fabricated
host evidence. Case prerequisite keys equal requirement keys exactly once each.

CapabilityObservation's roster_evidence is the reachable root for observed host bodies:
DISCOVERY resolves discovery coverage, then its discovered set and per-category absence/entry
records for fresh discovery; ENFORCEMENT also resolves enforcement coverage and each present-entry
observation. A later property evaluation consumes its independently accepted discovery prerequisite
by exact ref/digest/key and checks the observed body against the plan; it does not request a fresh
CaseEvidenceSubject from an earlier manifest absent from current authority (SPEC 11.2).
Expected subjects come from the approved requirement/roster plan, and link digests must match the
independently resolved records. PROVEN HOST_DISCOVERY requires DISCOVERY; PROVEN HOST_PROPERTY
requires ENFORCEMENT. Pure/native non-host scopes require NO_OBSERVED_ROSTER. Non-PROVEN host
records may carry NO_OBSERVED_ROSTER when the case refused, was unavailable, never completed or
failed before full coverage existed; they cannot satisfy another case's discovery prerequisite.
Any supplied link is still authenticated/checked, not ignored because the record is negative.

## 3. Tagged aliases (literal branch inventory)

Every row is a public alias with these and only these branches. Single-level aliases use `tag`
except AttemptBinding (`kind`); CaseResult dispatches on `(tag, cleanup, refusal_reason for
REFUSED)` and EvidenceResolution on `(tag, kind for FOUND)`. Missing discrimination in alias JSON
rejects even though a direct branch constructor can use its constant default. Recognized REFUSED
reason subsets map to the exact branch, not first-match. Unknown/missing selector is union-tag
failure; negative branch-field fixtures otherwise retain all selector fields.

```text
CapabilityKey := PlatformCapabilityKey, HostCapabilityKey
AttemptBinding := PureContractBinding, NativePreLaunchBinding
PrerequisiteResolution := FoundPrerequisite, MissingPrerequisite, ConflictingPrerequisite
HostCategoryPlan := PresentHostCategoryPlan, AbsentHostCategoryPlan
CaseSubject := NoRosterSubject, HostDiscoverySubject, HostPropertySubject
HostCategoryCoverage := PresentHostCategoryCoverage, AbsentHostCategoryCoverage
HostRosterEnforcementCoverage := PresentHostEnforcementCoverage, ZeroPresentHostEnforcementCoverage
ObservedRosterLink := NoObservedRoster, DiscoveryEvidenceLink, EnforcementEvidenceLink
ExecutionObservation := CompleteExecutionObservation, IncompleteExecutionObservation
CapabilityProof := PureRuleProof, MeasuredNativeProof, UnavailableProbeProof, NotCompletedProof, RefusedClaimProof
CaseResult := ExecutedPureCaseResult, ExecutedNativeConfirmedCaseResult, ExecutedNativeRecoveryCaseResult, RefusedPrerequisiteCaseResult, RefusedOtherCaseResult, RefusedRecoveryCaseResult, UnavailableCaseResult, NotRunCaseResult
QualificationEvaluation := ManifestRefusedEvaluation, ReportRejectedEvaluation, ReportAcceptedEvaluation
ApprovedManifestResolution := ApprovedManifestFound, ApprovedManifestMissing, ApprovedManifestConflicting
PlainEvidenceSubject := CaseEvidenceSubject, CheckEvidenceSubject, CleanupEvidenceSubject, PrerequisiteEvidenceSubject, RosterAbsenceSubject, EntryEnforcementSubject
EvidenceSubject := CaseEvidenceSubject, CheckEvidenceSubject, CleanupEvidenceSubject, PrerequisiteEvidenceSubject, RosterAbsenceSubject, DiscoveredSetSubject, DiscoveryCoverageSubject, EntryEnforcementSubject, EnforcementCoverageSubject, CapabilityEvidenceSubject
EvidenceResolution := AuthenticatedEvidence, AuthenticatedDiscoveredSet, AuthenticatedDiscoveryCoverage, AuthenticatedEnforcementCoverage, AuthenticatedCapabilityObservation, MissingEvidence, ConflictingEvidence
```

## 4. Enum catalog

Member names equal exact wire values. Existing broad Admission/Refusal vocabularies remain public
but do not legalize their members in narrower DTO fields. Literal discriminator strings need
their alias cells; they are not additional enum classes by inference.

```text
CapabilityFamily :: PLAN_BINDING, POLICY_ISOLATION, RESOURCE_CONTAINMENT, OWNED_CLEANUP, ATTEMPT_RECONCILIATION, HOST_MEDIATION, RESPONSIBILITY_ADMISSION
Observation :: PROVEN, FAILED, UNAVAILABLE, NOT_RUN
Admission :: ADMITTED, REFUSED
Refusal :: SOURCE_MISMATCH, INVALID_MANIFEST, APPROVAL_UNRESOLVED, PREREQUISITE_UNPROVEN, RESOURCE_ENFORCEMENT_UNAVAILABLE, HOST_ROSTER_UNQUALIFIED, EVIDENCE_INVALID, RECOVERY_REQUIRED
ReportOutcome :: QUALIFIED_FOR_DECLARED_SCOPE, CAPABILITY_UNAVAILABLE, QUALIFICATION_FAILED, INCOMPLETE
BindingKind :: PURE_CONTRACT, WINDOWS_LAB
Platform :: GENERIC, WINDOWS
HostSurface :: CODEX_CLI, CODEX_DESKTOP, CLAUDE_CODE_CLI
PrerequisiteKind :: APPROVED_SOURCE, LAB_IDENTITY, CHECKPOINT, PROTECTED_BOOTSTRAP, PROTECTED_IDENTITIES, IMMUTABLE_SNAPSHOT, RESOURCE_CONTROLS, ATTEMPT_CLAIM, HOST_ROSTER_DISCOVERY, WA04_ADAPTER
PrerequisiteDisposition :: PROVEN, FAILED, UNAVAILABLE
PrerequisiteResolutionTag :: FOUND, MISSING, CONFLICTING
PrerequisiteDetail :: MISSING, CONFLICTING, STALE, FAILED, UNAVAILABLE
CaseKind :: PURE_RULE, SOURCE_PROPERTY, TRUSTED_NATIVE_DISCOVERY, ADVERSARIAL_WORKLOAD, REAL_HOST_PROPERTY
CaseRole :: CONTROL, ATTACK, REVIEWER_MUTATION
CaseResultTag :: EXECUTED, REFUSED, UNAVAILABLE, NOT_RUN
ExecutionObservationTag :: COMPLETE, INCOMPLETE
CheckResult :: PASSED, FAILED
IncompleteReason :: OUTPUT_OVERFLOW, TIMEOUT, INTERRUPTED
CleanupDisposition :: NO_LAUNCH, CLEANUP_CONFIRMED, RECOVERY_REQUIRED
CaseRefusalReason :: SOURCE_MISMATCH, APPROVAL_UNRESOLVED, PREREQUISITE_UNPROVEN, RESOURCE_ENFORCEMENT_UNAVAILABLE, HOST_ROSTER_UNQUALIFIED, RECOVERY_REQUIRED
UnavailableReason :: PRIMITIVE_UNSUPPORTED, HOST_ABSENT, OFFLINE_PATH_UNSUPPORTED, ADAPTER_ABSENT
NotRunReason :: NOT_STARTED, DEPENDENCY_STOP, TOTAL_BUDGET_EXHAUSTED, OWNER_CANCELLED
EvaluationTag :: MANIFEST_REFUSED, REPORT_REJECTED, REPORT_ACCEPTED
ManifestRefusalReason :: INVALID_MANIFEST, SOURCE_MISMATCH, APPROVAL_UNRESOLVED
ReportRejectionDetail :: INVALID_SHAPE, MISSING_CELL, DUPLICATE_CELL, BINDING_MISMATCH, CHECK_COVERAGE_MISMATCH, UNAUTHENTICATED_EVIDENCE, HOST_COVERAGE_MISMATCH
EffectCategory :: SHELL_EXECUTION, INTERACTIVE_CONTINUATION, DIRECT_WRITE, NESTED_EXECUTION, EXTENSION_TOOL, BROWSER_COMPUTER, CLIENT_CONTROL
EffectDisposition :: DENIED, BROKER_ONLY, READ_ONLY
EffectReachability :: MODEL_REACHABLE, CLIENT_REACHABLE, BOTH
RosterCoverageTag :: PRESENT, ABSENT
RosterComparison :: MATCH, MISMATCH
ClaimScope :: PURE_RULE, NATIVE_PROBE, NATIVE_PROPERTY, HOST_DISCOVERY, HOST_PROPERTY
NotCompletedReason :: NOT_STARTED, DEPENDENCY_STOP, TOTAL_BUDGET_EXHAUSTED, OWNER_CANCELLED, OUTPUT_OVERFLOW, TIMEOUT, INTERRUPTED
```

## 5. Cross-record predicates and fixture construction

Use the owning SPEC for exact comparison, time order, report reduction and prerequisite algebra.
Duplicate detection applies at construction to case IDs, prerequisite keys, capability IDs and
requirement IDs, per-report case/claim IDs, check IDs, category/entry/alias IDs and case-reference
tuples. Scope/case/binding project, manifest, baseline and fixture identities agree; native
execution identities and evidence are absent from pure/pre-launch values. Host keys match their
subject's HostSurface and adapter revision. Exact all-category coverage applies to both plan and
observed coverage, not a min_length=1 substitute. MISMATCH/failed observations are representable
negative evidence, not a reason to erase the record or an admitted complete discovery.

Each case has exactly one declared capability_id; requirements compare that ID, exact key and
case-kind-derived ClaimScope. Case binding_digest comes from the independent approved record,
not the report. HOST_DISCOVERY requirements contain exactly one case ID, so present-entry
discovery evidence requests use that approved case and binding digest; a second case ID rejects.
This does not cap the number of independently approved host-discovery requirements. An actual
WA-04 source claim is SOURCE_PROPERTY with family RESPONSIBILITY_ADMISSION; this investigation's
Q8 owns no other responsibility validator. That pair requires WA04_ADAPTER; other pure pairs do
not acquire a native prerequisite merely because their key is host-scoped.

Catalog tests hand-author independent expected field/default/name lists and expected wire values.
They may use a small fixture builder to compose **that literal data**, never production schema,
model_fields, reflection or validator-derived expectations. Observed AST/model inventories may
only be compared to the literal expected list. Private bases/Protocols and facade aliases are
excluded from concrete-DTO count; public concrete extras/omissions fail rather than adjust counts.

Positive fixture basis: project `project-001`, case `case-001`, observation `observation-001`,
capability `capability-001`, attempt `attempt-001`, check `check-001`, observer `observer-001`;
all other singular Id values `<field-name-with-hyphens>-001`, all digests 64 `a` characters,
revisions 1, host version `1.0`, positive capacities their listed upper bounds, counters 0,
zero-only controls 0, active lanes 1, immutable one-element tuples unless this section specifies
empty/all-category/multi-case. These are fixture values, never evidence/approval for a real host.
Hand-written expected dictionaries must explicitly preserve repeated identity links rather than
blindly assigning the field-name fallback where it would disagree with a referenced object.

The finite scenario set supplies every concrete/alias positive:

1. Pure PLAN_BINDING / PURE_RULE case with APPROVED_SOURCE, NO_ROSTER, pure binding, one passed
   check, complete observer and PURE_RULE/PROVEN observation. Empty approved roster plans.
2. Non-host WINDOWS primitive TRUSTED_NATIVE_DISCOVERY, NATIVE_PROBE, NO_ROSTER; exact native
   bootstrap requirements; measured complete result plus confirmed cleanup, no self prerequisite.
3. Host discovery with WINDOWS/CODEX_CLI HOST_MEDIATION key; one present shell entry `entry-001`,
   alias `alias-001`, MODEL_REACHABLE/BROKER_ONLY; six explicitly absent categories. Planned entry
   names the future same-key host-property case `case-002`/oracle `expected-oracle-ref-001` as
   planned intent only. The discovery-only manifest has no property case, completed-discovery
   prerequisite or future evidence digest; it depends only on its bootstrap prerequisites.
4. A separate later approved manifest for host property against that plan and now-completed
   discovery: actual per-entry observation and completed enforcement payload, with its own
   ordinary binding/check/observation identity and exact resolved discovery digest. The
   declared check set includes actual positive-effect and denied-bypass cells for full-host proof.
5. All-ABSENT host discovery, seven absence records, empty actual sets, ZERO_PRESENT_ENTRIES;
   a later dependent property request is refused HOST_ROSTER_UNQUALIFIED. No invented entry,
   oracle or enforcement launch (the actual discovery case still has its real native observation).
6. For each remaining result/proof/port/evaluation branch, replace only its indicated branch
   data in its compatible pure/native scenario: failed measured check, native recovery, each
   refused reason/detail, unavailable probe, each incomplete/not-run reason, MISSING/CONFLICTING,
   top-level manifest refusal and report rejection. Expected reduction follows the SPEC, not a
   caller-written PASS; broader enum values are independently covered, not forced into illegal DTOs.

Every positive must construct and round-trip through the ordinary public DTO; every alias branch
also round-trips through its TypeAdapter. Implementation supplies the literal fixtures as schema
phase output; parent verifies them before any behavior admission. This is the already-approved
two-phase ordering extended only if the owner approves this exact replacement closure.

## 6. Finite coverage accounting

Counts below are calculated from this document's literal rows, not the current source. They are
catalog coverage counts, not commands, stress repetitions or a mandate for one file per fixture.
Expand three field groups; constants with defaults are not required fields. Omission/null cells
use the direct DTO positive, preserving all other selectors and valid JSON. Assert the intended
field/location and missing/type/literal failure, not merely any exception or `json_invalid`.

Final row/field/alias/enum totals are recorded in the ticket's closure-03 catalog accounting after
independent recount. Before commit those exact totals and names must match this leaf. Required
negatives = `2 * required-field occurrences + concrete DTO count`; each explicit default also
gets omission→exact default, null→reject, wrong constant→reject cells. Aliases additionally test
each selector's omission, unknown value and null once per branch. These counts do not replace
CQ02's scalar bounds/duplicates/cross-record matrix or behavior-phase CQ03–CQ12.

## 7. Approval signature

Owner **「核准」** approves revision 02 at `965e16b00d6049be6552465ac1ce1cbac968a8cb`, LF
`580104e585ba46a81aff17f3ff18100164618973b67d5c3db0040e29f88958a8`, together with SPEC 06 and
ticket document 06 / closure 03. Revision 03 changes lifecycle/signature only: all catalog fields,
names, counts, fixtures and predicates remain byte-for-byte unchanged. Earlier proposal wording
is historical, not a repeated approval gate. Native/runtime proof is still not claimed or granted.
