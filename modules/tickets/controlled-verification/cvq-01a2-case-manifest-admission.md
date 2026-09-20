# CVQ-01A2 | Case and manifest admission

| Field | Value |
| --- | --- |
| ID / kind / document / closure | `TICKET-CONTROLLED-VERIFICATION-CVQ-01A2` / `IMPLEMENTATION_TICKET` / `07` / approved `CLOSURE-CVQ-01A2` revision `02` |
| State / outcome | `OWNER_APPROVED / READY_FOR_SAME_LIFETIME_DISPATCH`; complete the existing case/manifest admission matrix, no new product behavior |
| Baseline / dependency | `c2fa4cdda1a785a4a8e2c7924a337c2fdd836160`, descendant of APPROVED A1 `8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc`; A2 closure01 is exhausted and remains historical |
| Preparation authority | Owner 「啟用」 adopts convergence section23 at `a4ad05066e7b52eedd83133dad89ce81d8f398f4`, LF `a21ccd9c68335e6b9a0e3deae249613ef2c5d9156794d3fdbbc04391a2af35c3`; permits this proposal, not signature on previously unwritten closure02 |
| SPEC / wire | [Qualification SPEC](../../spec/controlled-verification-qualification.md) revision07 LF `545f5058d8347ab069d6a23fdb07daaf06ab836998efb67b2c30b80fee3b1716`, sections2/6/7/11; [wire](../../spec/controlled-verification-qualification-wire.md) revision03 LF `6eb9d0a088e105e7c2dd4c3c3b4001f970ac34195c7a0cd78459a2f6016e9222`, sections1–6 |
| Requirement / Context | `PRD-20260908-051` / `CHG-20260908-051`; [REQ-051](../../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md) revision11 LF `f52552cdafc857d605f1eda03bcdf3df4c3d0c49ad9adfb9f39335f4b341e272`; [sealed Context](../../../doc/context/controlled-verification/main.md) revision02 LF `6f5465295cb3fd303bc555da655b3169d33292ad1f2ed4374748f82ddd6f2285`, READ_REFERENCE |
| Owner / reviewer / profile | Retained `cve_wire_implementer`, implementation-standard (Luna/xhigh); root, ticket-review (Terra/xhigh); approved REVISION_03 at `b12dd7262606f7b951271cd51e336747f0638c38:doc/runbooks/dispatch-model-profile.md`; no elevation |
| Workspace / view | `C:/Users/GameBoy/Desktop/Johnny_AI_Skill_latest/.worktrees/cvq-01` / `codex/cvq-01`; fresh `ctx-cvq-01a2-closure02`; clean Git/containment/readback verified at admission. Old views CLOSED |
| Language / resource | Python3.11.9, Pydantic2.13.4, mypy2.3.0; POC / HIGH_ASSURANCE; one sequential owner, required retained evidence-only helper after candidate; one foreground /60s-command /1200s-pass, zero automatic retries/load/container/background polling |
| Effect / XSS | Test-attribution/coverage change over constructor-local contracts; not verification-exempt. XSS_NOT_APPLICABLE: no UI, I/O adapter or untrusted render. No provider/VM/target/configuration/runtime capability, integration, push, release or installation effect |

## Current responsibility and writable boundary

Closure02 changes evidence ownership and narrows implementation, not CM01–07 semantics.
The former closure01 production/fixture write allowance does not survive into this closure.

- Only `tests/test_verification_qualification_manifests.py` is writable: imports directly
  required below, `QualificationManifestAdmissionTests.test_case_applicability_rows` and
  `test_prerequisite_applicability_and_order`. No other method/helper may change.
- All library source, fixtures, literal catalog, contracts/scalars/boundaries/domains tests,
  facades, every *_admission.py, CQ11, SPEC/Context, skills, indices and dependencies are
  READ_ONLY. No new file, DTO, field, default, alias, port, schema or import-DAG edge.
- Existing shared fixture functions alone compose scenarios. Construct immutable key values
  and call those functions; do not add a second fixture factory, generic matrix runner or
  all-purpose test helper. Necessary typed technical explanation may remain; no owner prompt,
  work-order body, correction narrative or workflow directive in source/scripts.
- Preserve every existing assertion/value/path and every closed finding, including F03's
  two-distinct-prerequisite positive and F04's nonempty-host extra-plan negative. Reuse an
  equivalent existing row rather than duplicating its test; parent verifies the exact map.
- Root owns the full mutation/historical/preservation evidence. The owner does not edit
  production temporarily, run a mutation campaign or write review evidence documents.

## Implementer delta (exact finite rows)

### C02.K — legal key alternatives in CM02 (17 positive rows)

Fixed representative key values (no unbounded enum/cartesian generator):
PN=PlatformCapabilityKey(PLAN_BINDING, WINDOWS, revision1);
HN=HostCapabilityKey(PLAN_BINDING, WINDOWS, CODEX_CLI, revision1);
HM=HostCapabilityKey(HOST_MEDIATION, WINDOWS, CODEX_CLI, revision1).
These distinguish the admitted key branches, not all possible family/platform combinations.
Retain pre-existing GENERIC pure and malformed-key rows unchanged.

Each table alternative is a separately named ordinary constructor + JSON roundtrip control,
`C02.K.<kind>.<key>`, with kind names lower_snake_case and key PN/HN/HM.
Check the literal expected binding and subject tag/class, not expectations read from candidate
logic. Shared functions remain the scenario owner; host subjects use their existing roster pins.

| Case kind | Keys (one row each) | Expected binding | Expected subject |
| --- | --- | --- | --- |
| PURE_RULE | PN, HN, HM | PURE_CONTRACT | NO_ROSTER |
| SOURCE_PROPERTY | PN, HN, HM | PURE_CONTRACT | NO_ROSTER |
| TRUSTED_NATIVE_DISCOVERY | PN, HN | WINDOWS_LAB | NO_ROSTER |
| TRUSTED_NATIVE_DISCOVERY | HM | WINDOWS_LAB | HOST_DISCOVERY |
| ADVERSARIAL_WORKLOAD | PN, HN, HM | WINDOWS_LAB | NO_ROSTER |
| REAL_HOST_PROPERTY | PN, HN, HM | WINDOWS_LAB | HOST_PROPERTY |

Additionally `C02.K.source_property.PR` and `C02.K.source_property.HR` use
RESPONSIBILITY_ADMISSION with the Platform/Host key respectively, same WINDOWS/revision1
and CODEX_CLI for Host. Both are PURE_CONTRACT + NO_ROSTER with the ordered
APPROVED_SOURCE, WA04_ADAPTER pair. Total15+2=17, not17 additional duplicates.
This freezes SPEC11.1's two key branches and the existing WA04 special case; no new behavior.

### C02.B — opposite binding, fixed case kind (five negative rows)

One `C02.B.<kind>` per five kinds above, start with its PN valid control.
Hold case.kind, key, subject, prerequisite order and all case fields fixed. Replace only the
binding body with an ordinary constructor-valid opposite variant: pure/source -> native_binding,
the three native kinds -> pure_binding, using the same case_id/common identity/fixture.
Keep native executable/dependency/argv/cwd/environment pins equal to the case.
The binding DTO itself must be valid; changing only its discriminator into a malformed union
does not exercise this join. Existing tests that change case.kind remain preserved.

Each must reject at root `loc=(), type=value_error`, literal diagnostic
`case kind and binding kind must agree`. No field/tag/JSON/other-validator failure counts.
The finite constructor preflight has already observed all five intended rejections without
source changes; this is honest baseline green, not a claimed first-red.

### C02.P — named WA04 positive in CM03

Inside `subTest(cell="C02.P.wa04_control")`, construct source_property_case() and perform the
existing two-key assertion plus literal ordered kinds APPROVED_SOURCE, WA04_ADAPTER.
Construction and assertion must both be inside this named cell. Preserve independently named
negative rows and their original diagnostic checks; do not remove them or infer their oracle
from caught exceptions. No fixture or product modification.

## Preserved acceptance matrix (reviewer-owned proof)

The following CM01–07 obligations remain unchanged. Only the two delta methods above are
implementation writes; the other methods are frozen regression inputs. Root owns their
complete predicate proof and old-observation relocation audit, not the implementation return.

All local comparisons below use direct containing DTO construction/JSON and expect
`ValidationError.errors()` at `loc=(), type="value_error"`; assert the intended predicate's
diagnostic as well as root/type where several root validators are reachable. Field/tag error is
not evidence for a join. Exception: CM02 directly constructs PlatformCapabilityKey with
HOST_MEDIATION and expects `loc=("family",), type="literal_error"`; native non-Windows uses
the root validator.
Each semicolon alternative is a separately named subcase, not an optional example.

| ID / method | Valid control -> one violated invariant | Exact mutation symbol/door |
| --- | --- | --- |
| CM01 / `test_case_and_scope_identity_joins` | Equal binding.case_id/fixture_digest -> change each separately; native binding executable/dependency/argv/cwd/environment digest -> change each separately; at manifest scope change each of project_id/baseline_digest/manifest_revision/manifest_digest, retaining valid case | QualificationCase.coherent_case each of seven equality comparisons; QualificationManifest.unique_cases_and_requirements each of four scope comparisons |
| CM02 / `test_case_applicability_rows` | All five case kinds and each legal key alternative follow SPEC11.1: PURE_RULE/SOURCE_PROPERTY -> pure + NO_ROSTER; discovery nonhost -> native + NO_ROSTER, host -> native + HOST_DISCOVERY; adversarial -> native + NO_ROSTER; real host -> native + HOST_PROPERTY. Pure HOST_MEDIATION + NO_ROSTER is valid. Change binding kind, subject variant separately; native WINDOWS -> GENERIC; host subject surface/revision change separately; platform-only HOST_MEDIATION rejects | coherent_case kind/binding, expected_subject, Windows and each host equality; capability key union restriction is unchanged wire regression (A1), not a new writable alias |
| CM03 / `test_prerequisite_applicability_and_order` | Pure kinds APPROVED_SOURCE only; SOURCE_PROPERTY+RESPONSIBILITY_ADMISSION additionally WA04_ADAPTER. Remove WA04 from the exact pair, add it to an ordinary pure pair, or replace approved source with native prereq; swap order of two requirement keys without swapping case keys; change one requirement key while case keys stay | coherent_case WA04 pair/pure-kind-set/order checks; WA04 missing is guarded twice (explicit WA04 and pure-kind-set), weaken those two equivalent protections together for that row; never weaken order to hide bad fixture |
| CM04 / `test_capability_requirement_joins` | Case capability in scope; requirement capability in scope; referenced case exists; requirement capability ID/key agree with case; derived claim scope agrees per each of five kinds and both discovery key variants; HOST_DISCOVERY exactly one distinct case | QualificationManifest.unique_cases_and_requirements case membership, case existence, ID/key equality, derived-scope/cardinality predicates. Requirement membership has the explicit implication exception below. Two-case host discovery uses two independently valid same-key discovery cases, no duplicate ID |
| CM05 / `test_manifest_and_prerequisite_duplicates` | Distinct -> duplicate separately: scope capability_ids; case dependency_digests / prerequisite_keys / prerequisite_requirements / expected_check_ids; CapabilityRequirement.case_ids; manifest case_ids / requirement observation_ids; QualificationPrerequisiteSet requirements.key | Corresponding unique_capabilities / coherent_case / unique_cases / unique_cases_and_requirements / unique_ordered_keys predicate, with the duplicate-key equivalence exception below |
| CM06 / `test_approved_plan_pin_coverage` | Correct unique host subject pins covered once -> missing, extra, duplicate plan; wrong roster key, ref, digest separately; pure-only and native-primitive-only manifests have empty plans -> add one host plan separately | ApprovedManifestFound.roster_plan_coverage exact-coverage comparison. All changed plans must remain constructor-valid. Host repeated subject pin is a positive requiring only one plan |
| CM07 / `test_discovery_intent_and_property_membership` | First discovery-only plan may name future property IDs without future evidence; later property ID present in its same-key/ref/digest plan -> remove only that property ID (replace with another valid distinct planned ID); keep another plan containing the ID to prove wrong-plan lookup rejects | roster_plan_coverage property membership and same-pin selection; exact coverage remains live. Positive same-key membership + negative wrong-plan/unlisted each run separately |

For CM05 the ordered key/requirement bijection makes duplicate full requirements also duplicate
keys; one cannot isolate those as two independent semantic failures. Positive distinct
key/requirement pairs, negative a repeated key with distinct requirement pins, and negative an
exact repeated requirement/key pair form named rows. For the full-pair row disable both
equivalent uniqueness guards together, keeping the ordered bijection check active. Do not claim
the later redundant guard alone was reached. Empty prerequisites/checks/policy/VM ref are scalar
wire rejection regressions from A1; no impossible after-validator red is demanded for a field
already rejected before that validator. These are evidence isolation rules, not changed semantics.

CM04 requirement-in-scope is logically implied by referenced-case existence, case-in-scope and
requirement/case capability equality. Retain its negative row and intended diagnostic; do not
demand it be accepted after removing only that redundant guard. The discriminator for the
capability-ID equality predicate uses TWO valid in-scope IDs, so the redundant membership
check cannot mask it. The outside-scope requirement row additionally records removal of just
the explicit membership guard changes its intended diagnostic (not admission success), while
the independent equality mutation supplies behavioral red. Keep those two evidence kinds
distinct; no implied property is waived and no unrelated predicate is removed.

CM02 kind/key alternatives are exactly SPEC11.1, not arbitrary native prerequisites invented by
the test. Ordinarily constructed native-shaped records are fake data, never native qualification.
CM07 membership remains local; actual resolver authenticity, native proof and report reduction
are out of scope. All joins requiring records absent from the DTO remain later behavior work.


## Root evidence contract (not implementer work)

[Closure02 evidence plan](../../../doc/reviews/controlled-verification/cvq-01a2-closure02-evidence-plan.md)
revision01 LF `29427a6bff933c21ee5c74777f9453cc1960b3f991f0b75d92d4914c29c3b0de`
freezes41 reviewer-owned mutation records Q01–41, five historical cells H01–05, exact method
commands, observation classes and three indexed destinations. Do not load its raw evidence
as implementer context or reproduce that campaign in the implementation seat.

Its Q24 missing-case fail-open branch avoids counting an incidental dictionary KeyError.
Q27 groups derived-scope and its redundant pure/no-roster guard for the same fact; all other
predicates remain live. These are explicit temporary reviewer-only isolation proposals, not
production changes or permission to weaken other checks. Exact closure02 approval binds them.

Root independently pins the final candidate, runs all mapped checks with unreduced output,
performs the different-door Q18 legal-domain narrowing, restores exact bytes, and obtains
one required retained helper return for SPEC_GAP/BOUNDARY_DATA/CONSISTENCY/REGRESSION,
READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT. Helper cannot approve or implement.
Root alone reviews. Any zero-red/unrelated failure/missing capture remains a finding.

## Fixed final commands

```powershell
& $cvqPython -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_manifests.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
& $cvqPython -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
git diff --check
```

Every CM row maps to
`tests.test_verification_qualification_manifests.QualificationManifestAdmissionTests.<method>`.
Full suite collects new TestCase through domains exactly once; includes all accepted A1 and
remaining evidence regressions. Strict checking/import and ordinary constructor/JSON are smoke.


## Execution, return and continuation

Use the fixed exact Python path in the evidence plan and existing60s bounded subprocess wrapper;
no installation or launcher. Owner runs current targeted methods before/after its test-only
edits and the fixed final strict/full-suite/diff checks, returning honest baseline green/red.
It does not need to fabricate an initial red in already-correct product code.

ImplementationReturn COMPLETED / BLOCKED / CHANGE_DETECTED includes ticket/document/closure,
authority commit, actual baseline, candidate, changed path/methods, C02.K/B/P row mapping,
commands/exits with full output, findings and scope deviations. It excludes the root-owned
41-mutation and historical campaign. Only this owner commits additive source in its worktree.
Parent writes all review/index metadata; no root source implementation override is granted.

No bypass constructors, model_copy(update), Any/cast/type-ignore/coercion, swallowed or broad
exceptions, expected values derived from production, raw source/work-order prose in Router
state, or new helper script. Counterexamples preserve other invariants; discovery of an
unexpected overlap is BLOCKED/CHANGE_DETECTED, not a silent plan extension.

After exact approval of this committed leaf and plan, reviewer readback/binding is AUTO_CONTINUE,
not another approval ceremony: retained native follow-up -> wait_agent -> root evidence/review
plus required helper. Do not poll progress. Fresh view replaces both exhausted closure01 views.
New closure02 permits one initial review plus one batched correction, not unlimited repair.

Only all A slices plus B approved together may reach combined schema integration. No partial
integration/main mutation/push/release/installation/evaluator authority is added here.
A1 remains APPROVED / NOT_INTEGRATED; A3/B remain dependency-pending until A2 approval.

## Immutable history and current approval state

Document05 / exhausted closure01, exact signature/dispatch/correction history and review remain
at `a4ad05066e7b52eedd83133dad89ce81d8f398f4`:
ticket LF `a4c88172da99c9648b8a30a846702c783dc9b7f0f20facc41af5e13515d97581`,
[A2 review02](../../../doc/reviews/controlled-verification/cvq-01a2-case-manifest-admission-code-review.md)
LF `595f1f57e06fec9661a04d7ce5539a6b380a97df2021b5f9e461f0cb01f072c6`.
No old source/ref is reset or overwritten. This revision replaces the working contract,
not historical evidence; closed transcripts and reviews are not implementation context.

Owner 「啟用」 settles the evidence ownership decision. This document06/closure02 was written
afterward, so exact approval still must bind its final bytes and evidence-plan revision01.
ACTION_COMPLETED / CONVERGENCE_ADOPTED / CLOSURE02_PROPOSED -> WAIT_FOR_HUMAN /
OWNER_EXACT_APPROVAL_PENDING. No implementation seat has been started under this proposal.

## Exact owner approval and native admission — 2026-09-20

The subsequent owner reply 「核准,繼續工作,保持agent wait不要一直停下來等我」 approves
document06 / closure02 at `42643068e7ab3cd570d8104c1690e1b089bc414e`, LF
`620b37e7e1a262ad852424c144ac7b88a0b1ad7e7379ffe86a7355a70dc796f0`, and the exact
reviewer evidence plan revision01 LF
`29427a6bff933c21ee5c74777f9453cc1960b3f991f0b75d92d4914c29c3b0de`.
This includes the explicitly proposed Q24/Q27 reviewer-only isolation clauses. That frozen
plan retains its proposal-era text; this signature supersedes its pending approval state.
No closure requirement, source boundary, model, resource limit or external effect is changed.

Root read back clean owner branch codex/cvq-01 at c2fa4cd, registered shared Git identity and
no reparse component in its repository-contained path. Direct origin/main readback and local
main both equal b697738d009db37318ebc8762107ef8329e014db. Retain the available owner,
implementation-standard Luna/xhigh; ticket-review remains root. The fresh view binds this
document07 and unchanged closure02; old closure01 views stay CLOSED.

ACTION_COMPLETED / APPROVAL_RECORDED -> AUTO_CONTINUE / IMPLEMENT via retained native
follow-up, then wait_agent, required evidence-only helper and root review. Bridge,
receipt, runner, queue, descriptor and host readback are NOT_REQUIRED on this direct lane.
No additional dispatch approval is needed. Installation closure remains a separate goal
track; neither partial source integration nor release is claimed by this approval record.
