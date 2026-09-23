# Independent test-engineer review admission

| Field | Value |
| --- | --- |
| ID / revision | `SPEC-CV-D9-TEST-ADMISSION-20260924-01` / `02` |
| State | `OWNER_DELEGATED_CONTRACT / TWO_PHASE_IMPLEMENTATION_AUTHORIZED` |
| Author / baseline | root; `codex/controlled-verification-intake`; `8b4d22f69d22a78e3623fa1a042e5f2718d537e3` |
| Authority | Owner's explicit approval of D9 two-phase direct dispatch: root completes contracts/ticket, Luna constructs types/tests, root preflights, same Luna wires admission. No repeated document approval; new requirements, privilege or external effects return to owner. This is not a claim that the owner individually reviewed these new bytes. |
| Requirement | [REQ-051 revision13 D9](../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md#owner-decision-d9-independent-test-engineer-and-review-admission--2026-09-23) |
| Context | [sealed shared Context revision02](../../doc/context/controlled-verification/main.md), stable approval/execution/review separation only; D9 is the explicit new role authority. No sealed Context rewrite. |
| Language / classification | Python3.11, Pydantic2, mypy strict; POC / HIGH_ASSURANCE for review admission. XSS_NOT_APPLICABLE: metadata-only pure Python, no UI/rendering. |

## Observable closure and exclusions

An attempt to enter formal REVIEW, or complete REVIEW into HANDOFF, must independently resolve
the active test assignment/report and admit only complete bound PASS evidence. Implementer TDD
does not fill that independent observation. Reuse the existing Router, not a second state machine.
This slice supplies contracts, a pure admission gate and Router wiring. It does not implement
process capture, protected evidence storage, Docker/DB/staging launch, host write interception or
dispatch a real test engineer. Those belong to CVE-01/02/03/04 and qualified host/executor adapters.
Until a trusted resolver is composed, the new review boundary fails closed. Both host adapters
must eventually use this same gate; pure tests do not prove installed Codex/Claude enforcement.

## Composition and exact public contract

New `library/workflow_router/test_engineer_contracts.py` owns immutable strict DTOs/enums and
the `TestEvidenceResolver` Protocol only. Reuse OpaqueMetadataId/EvidenceDigest from contracts;
new DTO base uses frozen/extra-forbid/strict configuration. No Any/cast/coercion or bypass
constructors. Native JSON round trips may decode enum values/tuple arrays through Pydantic's
public JSON validator. Unknown fields, invalid enums, wrong primitives and required null reject.
IDs are exact validated metadata, never trimmed/normalized. Digests use existing `sha256_` form.
`CandidateSha` is exactly forty lowercase hexadecimal characters, excluding all-zero.

| Public type | Fields / invariant |
| --- | --- |
| `TestVerdict` | Exactly PASS, FAIL, BLOCKED, INCONCLUSIVE, same serialized uppercase values |
| `TestCleanup` | NOT_REQUIRED, CONFIRMED, UNCONFIRMED |
| `TestBinding` | scope_ref, project_ref, ticket_ref, candidate_sha, test_suite_digest, plan_digest, environment_digest, implementer_id, engineer_id, reviewer_id; three actor IDs pairwise distinct |
| `TestCellObservation` | cell_id, verdict, evidence_ref, evidence_digest, reason_ref (explicit nullable); PASS requires null reason, every non-PASS requires an opaque reason |
| `TestReviewAuthority` | binding, expected_report_ref, expected_cell_ids (1..512 unique), cleanup_required (strict bool); this is independently resolved active authority, not caller data |
| `IndependentTestReport` | report_ref, binding, declared_verdict, cells (0..512 observations), cleanup; empty/duplicate cells remain representable for the gate's exact coverage refusal |
| `ResolvedTestEvidence` | status literal FOUND, authority, report |
| `UnavailableTestEvidence` | status literal UNAVAILABLE, reason enum NOT_FOUND / UNAUTHORIZED / UNQUALIFIED |
| `TestEvidenceResolution` | Discriminated union of the preceding two, discriminator status |
| `ReviewAdmissionRequest` | project_ref, scope_ref, report_ref |
| `ReviewAdmissionReason` | EVIDENCE_UNAVAILABLE, RESOLVER_FAILURE, BINDING_MISMATCH, REPORT_MISMATCH, CELL_COVERAGE_MISMATCH, VERDICT_MISMATCH, CLEANUP_INCOMPLETE, TESTS_FAILED, TESTS_BLOCKED, TESTS_INCONCLUSIVE |
| `ReviewAdmissionStatus` | ADMITTED, DENIED |
| `ReviewAdmissionDecision` | status, verdict, reason (explicit nullable); ADMITTED iff verdict PASS and reason null; DENIED requires non-PASS and non-null reason |
| `TestEvidenceResolver.resolve` | keyword-only request: ReviewAdmissionRequest -> TestEvidenceResolution |

New `review_admission.py` owns `ReviewAdmissionGate(resolver=...).evaluate(request)` and reduction.
It may call the injected resolver once, never shell/model/network/filesystem or retries. The
resolver is composed by trusted control code; its contract is authenticated active authority and
independently captured/validated observations, not arbitrary caller JSON or a report-owned hash.
Fake resolvers prove gate logic only, not provenance or OS isolation. No production permissive
resolver is added. An Agent must not select/replace the resolver via its event.

## Admission algorithm

1. Resolver unavailable -> BLOCKED/EVIDENCE_UNAVAILABLE. Resolver exception ->
   INCONCLUSIVE/RESOLVER_FAILURE; expose no exception text. No fallback to event-supplied evidence.
2. Request project/scope must equal authority binding; report binding must equal authority
   binding in every field. Mismatch -> INCONCLUSIVE/BINDING_MISMATCH.
3. Request/report/authority report refs must all match the current expected_report_ref;
   mismatch -> INCONCLUSIVE/REPORT_MISMATCH. Thus an older PASS cannot replace a later attempt.
4. Require precisely the expected cell IDs once each, including separately required attempts;
   empty/missing/extra/duplicate -> INCONCLUSIVE/CELL_COVERAGE_MISMATCH. No count-only comparison.
5. Reduce authentic observations: FAIL > BLOCKED > INCONCLUSIVE > PASS. A demonstrated FAIL
   remains FAIL even if declared status or cleanup conflicts; reason TESTS_FAILED. Otherwise
   declared status must equal reduction or return INCONCLUSIVE/VERDICT_MISMATCH. Remaining
   BLOCKED/INCONCLUSIVE deny with TESTS_BLOCKED/TESTS_INCONCLUSIVE respectively.
6. For all-PASS only, required cleanup must be CONFIRMED; if not required, NOT_REQUIRED or
   CONFIRMED is valid. UNCONFIRMED always denies all-PASS as BLOCKED/CLEANUP_INCOMPLETE.
   Successful complete reduction -> ADMITTED/PASS. Original observations are never changed.

Expected first-red/mutation-red is a satisfied oracle (PASS cell) only after the independent
adapter validates actual failure causality/restoration. This gate cannot derive that from exit
code or test names. Semantic assertion adequacy, mock placement and test-code review remain with
root. Failed cells cannot disappear on retry; the approved expected slots/active report preserve
history. Accepted correction rebinds a new candidate/plan rather than changing an old report.

## Existing Router choke point

Add distinct ModelRole.TEST_ENGINEER serialized as `test_engineer`, never a RESEARCH_HELPER
alias. The profile validator retains exactly one assignment for each original four roles and
may accept at most one explicitly declared TEST_ENGINEER assignment, with all existing profile,
capability and evidence collision checks unchanged. Absence means unconfigured, not inherited
helper permissions or an auto-created host assignment; default profiles need no invented model
or capability evidence. This staged metadata compatibility does not qualify role dispatch.
Add RouterState.review_scope_ref and RouterEvent.test_report_ref
(optional opaque IDs default None for unrelated stages), and BlockerCode.TEST_REVIEW_NOT_ADMITTED.
RouterEngine receives optional constructor-injected test_evidence_resolver (default None).
Before any otherwise valid transition whose next_stage is REVIEW, and before REVIEW -> HANDOFF,
require both refs, a resolver, and a gate ADMITTED decision. Missing capability/ref or denied
decision returns existing SUSPEND/HALT with TEST_REVIEW_NOT_ADMITTED and no eligible capability.
Bind request project to state.project_id (validate via the new request, fail closed if invalid).
Apply to every matching profile rule/event, including AUDIT_COMPLETED and custom rules; checking
only the usual smoke event is insufficient. No compatibility bypass flag or caller PASS field.
Other routes retain behavior. No new top-level stage, receipt, queue, runner or auto-fix loop.
Root may diagnose non-PASS, but only bound re-verification can re-admit formal review.

## Acceptance

| AC | Required evidence |
| --- | --- |
| D9-1 | Ordinary constructors/JSON round trips for all types/states; invalid primitives, identities, enum, null, extra and actor collision reject |
| D9-2 | Four verdicts, mixed FAIL priority and expected-red satisfied observations; only valid complete PASS admits |
| D9-3 | Each binding/report ref independently changed rejects; old report cannot overwrite current result |
| D9-4 | Empty/missing/extra/duplicate cells, wrong declared verdict, missing cleanup, unavailable/throwing resolver never admit |
| D9-5 | Real Router rejects bare smoke-pass, alternative/custom REVIEW entry and REVIEW handoff bypass; complete bound report enables expected positive path; unrelated routes remain unchanged |
| D9-6 | No effects, report/candidate mutation or implementation-return masquerade; production modules only types/port, reduction, minimal Router integration |

Reviewer reverse mutations must weaken identity, coverage, verdict, cleanup and Router choke-point
guards separately and cause the corresponding named assertions to fail, then restore green.
Use an executable old-API bare-smoke probe for baseline-red; new constructor tests need no
collection-failure-as-red fiction. At least one root mutation differs from implementer evidence.
Rollback is an additive reviewed revert; default-unavailable safety must not be loosened to keep
old callers green. Shipping/installation and any external effect require later authority.
