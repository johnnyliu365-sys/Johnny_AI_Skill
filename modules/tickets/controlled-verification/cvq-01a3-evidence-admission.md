# CVQ-01A3 | Roster, proof and local evidence admission

| Field | Value |
| --- | --- |
| ID / kind / document / closure | `TICKET-CONTROLLED-VERIFICATION-CVQ-01A3` / `IMPLEMENTATION_TICKET_PROPOSAL` / `01` / `CLOSURE-CVQ-01A3` revision `01` |
| State / outcome | `OWNER_EXACT_APPROVAL_PENDING / DEPENDENCY_PENDING / NON_DISPATCHABLE`; one observable closure: ordinary roster/proof/result/evidence DTOs discriminate constructor-local invalidity (original CA06–07/09, CA10) |
| Dependency / baseline / view | [A2](cvq-01a2-case-manifest-admission.md) APPROVED candidate SHA NOT_YET_AVAILABLE, with A1 accepted regression, additive descendant of `070039b6227205f7bb4592f203a4fd7455311f31`; parent commits exact SHA/review/index binding, never latest HEAD. New `ctx-cvq-01a3-closure01` |
| Preparation authority | Owner adopted convergence revision 08 at `058b8256bb1b2601fabc30c21a42ecc48c831875`, LF `24021ef0467d56c1bc3924e98b15d2f993e0dc720228dec44177da2132c50392`; preparation only, exact ticket approval pending |
| SPEC / wire | [Qualification SPEC](../../spec/controlled-verification-qualification.md) revision 07 LF `545f5058d8347ab069d6a23fdb07daaf06ab836998efb67b2c30b80fee3b1716`, sections 2/6/7/11; [wire](../../spec/controlled-verification-qualification-wire.md) revision 03 LF `6eb9d0a088e105e7c2dd4c3c3b4001f970ac34195c7a0cd78459a2f6016e9222`, sections 1–6 |
| Requirement / Context | `PRD-20260908-051` / `CHG-20260908-051`; [REQ-051](../../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md) revision 11 LF `f52552cdafc857d605f1eda03bcdf3df4c3d0c49ad9adfb9f39335f4b341e272`; [sealed Context](../../../doc/context/controlled-verification/main.md) revision 02 LF `6f5465295cb3fd303bc555da655b3169d33292ad1f2ed4374748f82ddd6f2285`, READ_REFERENCE only |
| Owner / reviewer / profile | Retained `cve_wire_implementer`, implementation-standard; `root`, ticket-review; [dispatch profile](../../../doc/runbooks/dispatch-model-profile.md) REVISION_03; no elevation. POC / HIGH_ASSURANCE, one sequential source owner, then required evidence-only adversarial helper |
| Workspace / environment | Existing `.worktrees/cvq-01` / `codex/cvq-01`; fresh clean/containment/Git identity readback before dispatch. Python 3.11.9 / Pydantic 2.13.4 / mypy 2.3.0; no installation |
| Effects / XSS | `PRODUCTION_BEHAVIOR`, constructor-local defect correction and verification, not test-exempt. `XSS_NOT_APPLICABLE`; no UI, I/O adapter, evaluator, runtime/native capability qualification, VM/provider/target/configuration effect, integration, push, release or installation |

## Writable responsibility boundary

Production paths below are under `library/controlled_verification/`.

| Exact path | Writable symbols and responsibility |
| --- | --- |
| `roster_contracts.py` | Existing unique_planned_ids, matching_entries (plan/coverage), complete_planned_categories, unique_entry_ids, unique_discovered_ids, complete_category_set, unique_observations validators only |
| `report_contracts.py` | CompleteExecutionObservation.unique_checks, CapabilityObservation.proof_matches_result, QualificationReport.unique_report_cells; existing CaseResult selector helper only if needed to preserve frozen rejection algebra; no fields/default/tag changes |
| `qualification_ports.py` | payload_matches_subject methods of AuthenticatedDiscoveredSet, AuthenticatedDiscoveryCoverage, AuthenticatedEnforcementCoverage, AuthenticatedCapabilityObservation only |
| `tests/test_verification_qualification_evidence.py` (new) | QualificationEvidenceAdmissionTests; table's roster/proof/result/local authenticated-join assertions only |
| `tests/verification_qualification_fixtures.py` | Single owner of compatible scenario composition; preserve accepted predecessor results |
| `tests/test_verification_qualification_domains.py` | Move remaining evidence assertion portions to evidence module; explicit scalar/manifest/evidence TestCase imports plus locally defined QualificationDomainCollectionTests.test_collection_retains_split_cases only. Sole residual responsibility is collection accounting, no domain/scenario/policy implementation |

Values/bindings/prerequisites/manifest and ApprovedManifestFound, catalog, contracts/scalars/
manifest tests are READ_ONLY. Production DAG stays roster -> values; report -> values/bindings/
roster; ports -> existing constituents. No independently resolved identity/authenticity or report
reduction is added to constructor validators. This ticket must not repair earlier slices secretly.

## Finite acceptance closure

ER01–15 have their exact named methods in QualificationEvidenceAdmissionTests; ER16 explicitly
belongs to the independently collected QualificationDomainCollectionTests in domains.
Each enumerated field/member/scope is an independent subcase. For direct model-local validation
expect `loc=(), type="value_error"` AND intended predicate diagnostic; other locations/types are
explicit below. Ordinary positive then minimally invalid input, not reuse of invalid objects.

| ID / method | Valid control -> invalid data; exact target |
| --- | --- |
| ER01 / `test_every_refusal_reason_result_pair` | RefusedClaimProof: SOURCE_MISMATCH, APPROVAL_UNRESOLVED, RECOVERY_REQUIRED -> FAILED; PREREQUISITE_UNPROVEN, RESOURCE_ENFORCEMENT_UNAVAILABLE, HOST_ROSTER_UNQUALIFIED -> UNAVAILABLE. Each reason's valid pair and each other Observation value rejected. Mutate proof_matches_result reason partition / result comparison separately |
| ER02 / `test_other_proof_scope_result_pairs` | PURE_RULE proof only PURE_RULE scope and PROVEN/FAILED; MEASURED_NATIVE every nonpure scope with PROVEN/FAILED; UNAVAILABLE_PROBE result UNAVAILABLE; NOT_COMPLETED result NOT_RUN. For pure/measured test scope and terminal-result restrictions separately, including UNAVAILABLE and NOT_RUN with otherwise valid NONE roster. Mutate each corresponding proof_matches_result clause separately; mandatory pure terminal-result door (old CM3) |
| ER03 / `test_required_proof_references` | Each measured native_primitive_ref/race_model_ref/failure_semantics_ref; unavailable probe_evidence_ref; not-completed plan_event_evidence_ref; refused admission_evidence_ref present -> missing at that field, `missing`. Exact omission is shared wire predicate proved by A1 SW02; rerun named omissions here, do not alter frozen fields or claim a second independent semantic guard |
| ER04 / `test_roster_link_scope_and_result` | PURE_RULE/NATIVE_PROBE/NATIVE_PROPERTY require NO_OBSERVED_ROSTER; PROVEN HOST_DISCOVERY requires DISCOVERY; PROVEN HOST_PROPERTY requires ENFORCEMENT. Each wrong link variant separately; compatible failed/unavailable/not-run host + NONE remain valid. Mutate corresponding proof_matches_result roster branch. Discovery NONE rejection has two equivalent guards: disable both for NONE row, retain all other rules; wrong ENFORCEMENT isolates the broader guard |
| ER05 / `test_planned_entry_and_category_rules` | PlannedHostEffectEntry sorted distinct aliases/case refs -> duplicate alias, unsorted distinct aliases, duplicate case ref separately (unique_planned_ids). PresentHostCategoryPlan valid entries -> wrong category, duplicate only entry ID, duplicate only alias across otherwise distinct entries (matching_entries) |
| ER06 / `test_plan_global_coverage_and_uniqueness` | ApprovedHostRosterPlan seven distinct categories -> omit one, duplicate one while keeping seven valid categories covered; across different categories duplicate only entry ID / alias ID / planned_enforcement_case_ref ID separately (complete_planned_categories). Other IDs stay distinct; mandatory alias-only global door (old CM2). Case-ref tuples here mean the catalog's ID elements, not a new tuple record type |
| ER07 / `test_observed_entry_and_category_rules` | HostEffectEntry and PresentHostCategoryCoverage: same six independent entry/category/duplicate/sort cases as ER05, at unique_entry_ids / matching_entries |
| ER08 / `test_observed_global_coverage_and_uniqueness` | HostRosterDiscoveryCoverage: same five independent missing/duplicate-category/global-entry/global-alias/global-case-ref cases as ER06 (complete_category_set). DiscoveredEffectSet: duplicate only dispatch_entry_ids or alias_ids (unique_discovered_ids). PresentHostEnforcementCoverage duplicate only observation.dispatch_entry_id (unique_observations) |
| ER09 / `test_negative_and_zero_roster_shapes_remain_representable` | Positive all-ABSENT seven-category plan and observed coverage, empty actual ID sets, ZERO_PRESENT_ENTRIES, MISMATCH coverage, DiscoveredEffectSet unknown_entry_count=1 and separately unobservable_surface_count=1. Ordinary and alias round trips preserve these shapes. Temporary counterfactual restrictions are precisely listed below, not imaginary existing rejection guards |
| ER10 / `test_local_report_duplicates` | CompleteExecutionObservation distinct check IDs -> duplicate one; CapabilityObservation distinct case_ids -> duplicate one; QualificationReport results' case_id -> duplicate one; claims' observation_id -> duplicate one. Mutate unique_checks / proof_matches_result first guard / each unique_report_cells guard separately; all proof and roster data remain valid |
| ER11 / `test_result_shape_boundaries` | ExecutedPure, RefusedPrerequisite, RefusedOther, RefusedRecovery, Unavailable, NotRun reject added launch_observation at that field (`extra_forbidden`); ExecutedNativeRecovery/RefusedRecovery reject cleanup=CLEANUP_CONFIRMED at cleanup (`literal_error`). Each ordinary direct branch positive; alias selector omission/null/unknown retains A1's exact closed error algebra. Wire extra/literal predicate mutants are shared A1 evidence, not new field-write authority here; CaseResult selector regression maps _case_result_variant |
| ER12 / `test_authenticated_discovered_identity_joins` | AuthenticatedDiscoveredSet payload.roster_key == subject.roster_key; payload.observer_ref/evidence_ref == outer counterparts. Mutate each equality separately in payload_matches_subject. Each shared roster-key component is individually changed in the subject, valid payload retained |
| ER13 / `test_authenticated_discovery_identity_joins` | AuthenticatedDiscoveryCoverage payload vs subject roster_key / approved_roster_ref / approved_roster_digest. Each equality and each roster-key component independently mismatched, at payload_matches_subject |
| ER14 / `test_authenticated_enforcement_identity_joins` | AuthenticatedEnforcementCoverage payload vs subject discovery_coverage_ref / discovery_coverage_digest, each separately; both PRESENT_ENTRIES and ZERO_PRESENT_ENTRIES payload alternatives, payload_matches_subject |
| ER15 / `test_authenticated_capability_identity_joins` | AuthenticatedCapabilityObservation payload vs subject observation_id / capability_id / capability_key / claim_scope / case_ids, and payload vs outer observer_ref / evidence_ref. Change subject/outer only, keeping payload locally valid; every equality independently mutated. Key alternatives and each key component separately; both case-ID content and order mismatch |
| ER16 / domains.QualificationDomainCollectionTests.`test_collection_retains_split_cases` | A2's duplicates stay exercised through manifests TestCase, not copied. This locally defined always-collected witness checks exact test IDs from the three imported TestCases against literal accepted method inventory, each once. Remove EACH class import separately: this witness remains and fails, including removal of evidence TestCase. Do not place the witness inside any imported class |

For ER05–08, each declared guard family has its own targeted reverse mutation in the named
method. Missing category uses six categories; duplicate-category control retains all seven
plus an eighth duplicate, distinguishing cardinality from completeness. Local per-entry/per-
category negatives and cross-category negatives use different controls. Global alias mutation
must not also duplicate entry or case-ref IDs. Do not require all seven categories in each
PresentHostCategory object; exact category coverage belongs to the enclosing plan/coverage.

Shared roster-key components (ER12/13) are host_surface, host_version, binary_digest,
configuration_digest, enrollment_digest, adapter_revision. Capability-key components (ER15)
are family, adapter_revision, platform and, for HOST, host_surface. Choose another legal value
for each branch; change a whole key variant only to another ordinary valid variant. Do not
synthesize illegal HOST family changes then mistake nested field rejection for equality proof.
PLAIN AuthenticatedEvidence has no payload: no invented payload join. Enforcement subject
roster_key cannot be compared to a payload field that does not exist. Digest authenticity,
discovered-set vs coverage comparison and plan/oracle/disposition checks against separately
resolved records remain resolver-phase, not new constructor-local requirements.

ER09's explicitly bounded temporary counterfactuals, in a clean candidate-bound review snapshot
only: (1) add all-ABSENT rejection to ApprovedHostRosterPlan.complete_planned_categories;
(2) same to HostRosterDiscoveryCoverage.complete_category_set; (3) remove ZERO_PRESENT_ENTRIES
from HostRosterEnforcementCoverage union so its alias positive fails; (4) temporarily restrict
HostRosterDiscoveryCoverage.comparison to MATCH; (5/6) restrict each DiscoveredEffectSet counter
to zero independently. These are six named temporary negative-evidence exceptions to read-only
schema surfaces, not new committed validators or changed product semantics. ER09 records
constructor/alias positives and each restriction's red/restoration, never claims runtime
nonqualification. Existing semantic rejection validators do not exist for these allowed shapes.

ER16 may use unittest's existing default loader to enumerate (not execute recursively) the named
domains suite and compare literal fully qualified test IDs. No custom loader, runner or generic
collection framework. Include the locally defined witness itself once in the expected inventory;
never derive expected methods from the loaded suite. The three import-deletion mutants leave
the witness definition intact and cannot be mistaken for deletion of the entire test entrypoint.

### Genuine historical defects

On exact `5d7789db6b950d317e7b500b757aa77a54d609ed`, ER01's three UNAVAILABLE refusal positives
failed in the old validator, and ER05 unsorted planned aliases were incorrectly accepted.
Parent reproduced both with collectable probes on 2026-09-19, then observed the same probes
green on 070039b6; exact code/results are in the [convergence record](../../../doc/reviews/controlled-verification/cvq-01-convergence-proposal.md#14-owner-adoption-and-exact-ticket-packet--2026-09-19).
Retain those behavioral reds, not collection/import errors or an invented earlier chronology.
All other rows use observed starting behavior plus mapped reverse-mutation/restoration.

## Fixed final commands

```powershell
& $cvqPython -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_evidence.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
& $cvqPython -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
git diff --check
```

For ER01–15 use
`tests.test_verification_qualification_evidence.QualificationEvidenceAdmissionTests.<method>`.
For ER16 use `tests.test_verification_qualification_domains.QualificationDomainCollectionTests.test_collection_retains_split_cases`.
Do not pass all three new modules again to the full suite: domains imports their TestCases once.
Build/type/import smoke and ordinary constructors/JSON are the local seam; no native/full-repo run.

## Evidence and bounded execution

Use `C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe` as
`$cvqPython` after read-only version probes. One foreground process, 60 seconds per command,
1200 seconds per verification pass, zero automatic retries/load/container/background polling.
Enforce the command timeout with the existing bounded subprocess wrapper; do not create a launcher.
If insufficient, return BLOCKED with evidence; do not silently expand the plan.

At the pinned starting SHA first run the new named tests without a production fix. Record honest
green or behavioral red, not missing-module/collection failure. Historical reproduction is not
a claim about original TDD chronology. After any necessary local fix, run strict checking and the
focused suite. For each table predicate, pin candidate SHA and exact source symbol/expression,
save exact temporary patch, run its fully qualified named method with unreduced output, restore
the bytes, rerun the same method green. Use one in-process subTest ID per listed alternative.
Record command, exit, row ID and result; NOT_RUN/MISSING remains incomplete, zero red is a finding.
No generic mutation framework, new helper script, random campaign or reviewer-generated policy.

A counterexample starts from a separately observed valid ordinary constructor/JSON control.
Change only the named invariant, coordinating dependent identities solely to keep other
invariants valid. Expected locations/types come from literal field/domain contracts, never from
catching candidate exceptions or production reflection. Broad Exception, json_invalid and an
unrelated validator failure are not evidence. No Any/cast/type-ignore, constructor bypass,
model_copy(update), coercion or swallowed exceptions. Raw malformed data is negative input only.

Some predicates have redundant guards. The table identifies those explicitly; remove the minimum
set of equivalent guards together to expose that same predicate, with all other predicates live.
Do not require an impossible single-guard red, weaken an unrelated guard, or count a masked
rejection as mutation success. A newly discovered overlap/semantic ambiguity is BLOCKED or
CHANGE_DETECTED for parent review, not permission to redefine the rule.

Parent independently runs the focused checks and mapped mutations, at least one through a door
different from implementer examples. Reuse the evidence-only helper for SPEC_GAP / BOUNDARY_DATA /
CONSISTENCY / REGRESSION at the exact candidate, READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT, one
bounded return. Helper supplies evidence, root alone approves. No repeated progress inspection:
native dispatch -> wait_agent -> returned evidence -> parent review.

## Ownership, return and continuation

CA10 is preserved: `tests/verification_qualification_fixtures.py` alone composes valid scenarios;
the literal catalog alone owns expected schema data. Assertions import those owners. Existing
`_complete`, `_roster_key`, `_entry`, `_planned`, `_coverage` builders must not acquire a second
owner. Preserve each old assertion with an explicit old-method -> new-method/row relocation map;
do not silently drop it because another test is green. Keep predecessor accepted tests unchanged
except the explicitly authorized assertion relocation; rerun them as regression.

No new shared contract, DTO/field/default/enum/port, public API, new production file or import-DAG
edge. Facades, every `*_admission.py`, CQ11's existing test body, SPEC/Context, skills, global
rules, dependencies and all control/index docs are forbidden implementation writes. Tests are
responsibility-specific; no arbitrary line limit, generic validator or new all-purpose framework.
All unspecified paths/symbols are forbidden. Only owner commits its own additive source.

Return ImplementationReturn COMPLETED / BLOCKED / CHANGE_DETECTED with ticket/document/closure,
authority commit, actual starting SHA, candidate SHA, changed paths/symbols, relocation map,
commands/exits, per-row baseline and mutation/restore evidence, findings and scope deviations.
Parent alone writes review/index metadata. Initial plus one batched correction maximum for this
new finite closure; exhaustion returns convergence, not a third correction or automatic elevation.
Old CVQ-01 closure03 and CVQ-01A closure01 remain exhausted and their views CLOSED.

This document is a proposal, not a dispatch instruction. Exact owner approval must bind this
committed leaf and LF digest. After approval, passing predecessor review and committed exact
SHA/view binding is AUTO_CONTINUE metadata, not repeated ceremonial approval. Missing evidence
or changed scope halts. Same-lifetime dispatch does not require runner/queue/receipt/descriptor.
No partial integration: all three A slices and B must pass together before combined schema
admission; evaluator behavior, push and release remain ungranted. Preserve prior refs/candidates;
rollback/forward-fix is additive. Current return: ACTION_COMPLETED / TICKET_PROPOSED ->
WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING.

After actual review root records combined A1/A2/A3 approval at ONE SHA, confirms all original
CA01–10 obligations and preceding tests, then pins it for [B](cvq-01b-source-admission.md).
B's dependency amendment also needs exact owner approval; this proposal does not grant it.
