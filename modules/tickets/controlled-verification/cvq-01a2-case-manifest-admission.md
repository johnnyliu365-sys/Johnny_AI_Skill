# CVQ-01A2 | Case and manifest admission

| Field | Value |
| --- | --- |
| ID / kind / document / closure | `TICKET-CONTROLLED-VERIFICATION-CVQ-01A2` / `IMPLEMENTATION_TICKET` / `02` / `CLOSURE-CVQ-01A2` revision `01` |
| State / outcome | `OWNER_APPROVED / DEPENDENCY_PENDING / NON_DISPATCHABLE`; one observable closure: case/binding/applicability/requirement joins and approved manifest plan coverage (original CA04–05/08, relevant CA09 duplicates, CA10) |
| Dependency / baseline / view | [A1](cvq-01a1-scalar-wire-admission.md) APPROVED candidate SHA NOT_YET_AVAILABLE, additive descendant of `070039b6227205f7bb4592f203a4fd7455311f31`; parent commits exact SHA/review/index binding before dispatch, never latest HEAD. New `ctx-cvq-01a2-closure01` |
| Preparation authority | Owner adopted convergence revision 08 at `058b8256bb1b2601fabc30c21a42ecc48c831875`, LF `24021ef0467d56c1bc3924e98b15d2f993e0dc720228dec44177da2132c50392`; preparation only, exact ticket approval pending |
| SPEC / wire | [Qualification SPEC](../../spec/controlled-verification-qualification.md) revision 07 LF `545f5058d8347ab069d6a23fdb07daaf06ab836998efb67b2c30b80fee3b1716`, sections 2/6/7/11; [wire](../../spec/controlled-verification-qualification-wire.md) revision 03 LF `6eb9d0a088e105e7c2dd4c3c3b4001f970ac34195c7a0cd78459a2f6016e9222`, sections 1–6 |
| Requirement / Context | `PRD-20260908-051` / `CHG-20260908-051`; [REQ-051](../../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md) revision 11 LF `f52552cdafc857d605f1eda03bcdf3df4c3d0c49ad9adfb9f39335f4b341e272`; [sealed Context](../../../doc/context/controlled-verification/main.md) revision 02 LF `6f5465295cb3fd303bc555da655b3169d33292ad1f2ed4374748f82ddd6f2285`, READ_REFERENCE only |
| Owner / reviewer / profile | Retained `cve_wire_implementer`, implementation-standard; `root`, ticket-review; [dispatch profile](../../../doc/runbooks/dispatch-model-profile.md) REVISION_03; no elevation. POC / HIGH_ASSURANCE, one sequential source owner, then required evidence-only adversarial helper |
| Workspace / environment | Existing `.worktrees/cvq-01` / `codex/cvq-01`; fresh clean/containment/Git identity readback before dispatch. Python 3.11.9 / Pydantic 2.13.4 / mypy 2.3.0; no installation |
| Effects / XSS | `PRODUCTION_BEHAVIOR`, constructor-local defect correction and verification, not test-exempt. `XSS_NOT_APPLICABLE`; no UI, I/O adapter, evaluator, runtime/native capability qualification, VM/provider/target/configuration effect, integration, push, release or installation |

## Writable responsibility boundary

Production paths are under `library/controlled_verification/`.

| Exact path | Writable symbols and responsibility |
| --- | --- |
| `manifest_contracts.py` | QualificationScope.unique_capabilities, QualificationCase.coherent_case, CapabilityRequirement.unique_cases, QualificationManifest.unique_cases_and_requirements; constructor-local predicates only |
| `prerequisite_contracts.py` | QualificationPrerequisiteSet.unique_ordered_keys only |
| `qualification_ports.py` | ApprovedManifestFound.roster_plan_coverage only, no authenticated wrappers, resolver/port/signature change |
| `tests/test_verification_qualification_manifests.py` (new) | QualificationManifestAdmissionTests, table's case/manifest/prerequisite assertions only |
| `tests/verification_qualification_fixtures.py` | Sole compatible scenario composition, preserve predecessor tests/results |
| `tests/test_verification_qualification_domains.py` | Move this table's assertion portions into manifests; explicit TestCase import preserves compatibility collection. Other remaining assertions unchanged |

Values/bindings/roster/report, literal catalog, contracts/scalars tests and facades are READ_ONLY.
Keep production constituent DAG: manifest -> values/binding/prerequisite/roster; prerequisite ->
values; ports -> values/manifest/prerequisite/roster/report. Existing field/union constraints
are frozen. No model-field/alias edits in this closure.

## Finite acceptance closure

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

### Genuine historical defects

Preserve behavioral reds on exact 5d7789d for CM01 argv/cwd/environment (invalidity previously
accepted) and CM02 pure host + NO_ROSTER (validity previously rejected), plus CM06 extra pure
plan (invalidity accepted). Parent's 2026-09-19 preflight collected all these on 5d7789d and
observed those failures; same probes pass on 070039b6. The [convergence record](../../../doc/reviews/controlled-verification/cvq-01-convergence-proposal.md#14-owner-adoption-and-exact-ticket-packet--2026-09-19)
contains exact reproduction. New tests must stay collectable on that schema for these named
cells; extract only schema-compatible tests/fixtures when reproducing, do not require nonexistent
new test modules in the old tree. Record exact test patch/command; no inferred original chronology.

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

On actual approval root pins the A2 candidate for [A3](cvq-01a3-evidence-admission.md).
Original CA09 duplicate obligations owned here are retained by A3 through regression, not
implemented a second time. No B source admission yet.

## Exact approval and current continuation — 2026-09-19

Owner **「核准」** approves this document01 / closure01 in packet `b12dd7262606f7b951271cd51e336747f0638c38`,
LF `fab6c428ec744f33dde79fdb81d1e07557dd9cb6c686394798a319b0bc6c5978`. Document02 records signature/state only; all
boundaries, predicates, temporary mutation exceptions, resource limits and return obligations
above remain unchanged. Earlier proposal/pending wording is historical, not a repeated gate.

This slice remains dependency-blocked, not awaiting another owner decision. Parent will commit
the actual accepted predecessor SHA/review/index and fresh view binding before dispatch to the
same sequential owner. Metadata binding is AUTO_CONTINUE under this exact approval. It cannot
substitute a latest HEAD or bypass the predecessor's tests, reverse mutations or parent verdict.
ACTION_COMPLETED / EXACT_APPROVAL_RECORDED -> DEPENDENCY_PENDING; no premature source write.

All old exhausted views remain CLOSED. No integration, push, release, installation or evaluator
behavior grant is added. The packet also approves B document03's dependency amendment.
