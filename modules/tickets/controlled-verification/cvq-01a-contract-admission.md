# CVQ-01A | Qualification contract admission closure

| Field | Value |
| --- | --- |
| ID / kind / document revision | `TICKET-CONTROLLED-VERIFICATION-CVQ-01A` / `IMPLEMENTATION_TICKET` / `02` |
| State / closure | `OWNER_APPROVED / CONTRACT_RECONSTRUCTION_AUTHORIZED`; `CLOSURE-CVQ-01A` revision `01`; actual parent preflight remains required |
| Preparation authority | Owner adopted convergence proposal revision 05, commit `dc45f31f6c56983613665f276bf15207419274e3`, LF `6ad63ea17bf1750549d1f5087138e9bb447b477bcd8d683cac7405bed1262847`; adoption authorizes this proposal, not source execution |
| Outcome / change class | One independently provable verification closure: ordinary qualification DTOs accept the frozen wire algebra and reject constructor-local invalidity; `PRODUCTION_BEHAVIOR`, defect correction against the preserved experimental candidate, not test-exempt |
| SPEC | [Qualification SPEC](../../spec/controlled-verification-qualification.md) revision 07, LF `545f5058d8347ab069d6a23fdb07daaf06ab836998efb67b2c30b80fee3b1716`, sections 2, 6, 7, 11; [wire appendix](../../spec/controlled-verification-qualification-wire.md) revision 03, LF `6eb9d0a088e105e7c2dd4c3c3b4001f970ac34195c7a0cd78459a2f6016e9222`, sections 1–6 |
| Requirement / Context | `PRD-20260908-051` / `CHG-20260908-051`; [REQ-051](../../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md) revision 11 LF `f52552cdafc857d605f1eda03bcdf3df4c3d0c49ad9adfb9f39335f4b341e272`; [sealed Context](../../../doc/context/controlled-verification/main.md) revision 02 LF `6f5465295cb3fd303bc555da655b3169d33292ad1f2ed4374748f82ddd6f2285`, READ_REFERENCE only |
| Baseline | Exact source `5d7789db6b950d317e7b500b757aa77a54d609ed`; control proposal based on `dc45f31f6c56983613665f276bf15207419274e3`; no reset/rebase/replacement of failed candidates |
| Owner / reviewer | Reuse `cve_wire_implementer`, `implementation-standard`; current-session `root`, `ticket-review`; [profile](../../../doc/runbooks/dispatch-model-profile.md) REVISION_03. No elevation granted |
| Workspace / allocation | Proposed same existing `.worktrees/cvq-01`, branch `codex/cvq-01`; one sequential owner, fresh clean/containment/Git identity readback and new `ctx-cvq-01a-closure01` before authorized dispatch; closure-03 views stay CLOSED |
| Delivery / resource | POC / HIGH_ASSURANCE retained; one implementer, one subsequent required evidence-only adversarial helper; no parallel source owners |
| Language / environment | Python 3.11.9 / Pydantic 2.13.4 / mypy 2.3.0; exact interpreter and bounded commands below; no dependency installation |
| XSS / effects | `XSS_NOT_APPLICABLE`, no renderer; source-only, no execution broker, host/VM/provider/target/configuration effects, integration, push, release or install |

## 1. Frozen inputs and scope

This is the contract-admission half of the adopted split, not another correction under exhausted
CVQ-01 closure 03. CVQ-AC01 and the constructor-local portions of CVQ-AC02/03/09 are its outcome.
All existing approved predicates survive. Native proof, independent resolver authenticity,
report reduction, CQ11 source-policy qualification and evaluator behavior are not claimed here.
The [schema review](../../../doc/reviews/controlled-verification/cvq-01-schema-preflight.md)
revision 04 is counterexample evidence, not another implementation instruction source.

The wire appendix owns all public fields, defaults, tags, finite enums and three port signatures.
No public schema change, extra DTO/base/port, altered grammar or new shared Context is allowed.
Constructor-local means the complete inputs needed for a comparison are fields within that
constructed object; comparisons needing independently resolved records remain phase 2. In
particular, validating an ApprovedManifestFound's manifest/plan tuple is local; authenticating
those approved records is not. No fake capability record counts as native evidence.

## 2. Exact writable responsibility boundary

All production paths below are under `library/controlled_verification/`. Only already-declared
types and their local validators may change; imports must keep the original constituent DAG.

| Path | Writable responsibility / direct dependencies |
| --- | --- |
| `qualification_values.py` | Seven scalar domains, exact enum/CapabilityKey shapes, QualificationModel strict/frozen/extra-forbidden configuration; no internal imports |
| `binding_contracts.py` | Existing binding/launch shapes and local identity checks; values only |
| `prerequisite_contracts.py` | Existing key/requirement/resolution/set shapes and uniqueness; values only |
| `roster_contracts.py` | Existing plan/observed roster shapes, local category/entry/alias constraints; values only |
| `manifest_contracts.py` | Existing limits, scope/case/binding/requirement-local joins; values, bindings, prerequisites, roster |
| `report_contracts.py` | Existing proof/result compatibility, result/check/claim uniqueness; values, bindings, roster |
| `qualification_ports.py` | Existing resolution DTO local joins, especially ApprovedManifestFound plan coverage; no new port/signature or resolver behavior; existing contract-constituent imports only |

| Exact test path | Sole responsibility |
| --- | --- |
| `tests/verification_qualification_catalog.py` | Literal expected wire names/fields/defaults/enum/alias rows and domain expectation data from the approved appendix; never derive expected values from production |
| `tests/verification_qualification_fixtures.py` | The single owner of valid DTO/scenario composition and ordinary fake values; no assertions or source policy |
| `tests/test_verification_qualification_contracts.py` | Catalog, constructor/JSON/alias/default/enum/configuration assertions; remove duplicate scenario constructors in favor of the fixture owner |
| `tests/test_verification_qualification_domains.py` (new) | Named scalar and constructor-local domain assertions below, using the same fixtures/catalog; no independent fixture factory or AST policy |
| `tests/test_verification_qualification_boundaries.py` (limited relocation) | Move only non-CQ11 domain test methods/imports to the domains module; retain the existing `test_architecture_dependency_gate` body and its embedded policy/corpus unchanged as known-unqualified evidence |

Both facades, every `*_admission.py`, other library modules, global rules, skills, manifests,
dependencies, SPEC, Context, tickets/indexes and element docs are forbidden implementation writes.
No new generic validator, generator, CLI, daemon, test launcher or helper script. Table-driven
rows are in-process cases, not one file/process per cell. File length is not a substitute for
the declared ownership boundary. Reviewer owns any later documentation/index writeback.

## 3. Finite closure and mandatory counterexamples

The suite must compare exact names, not only totals: 81 DTOs; 335 required field occurrences;
78 defaults; 751 required-omission/null/extra cases; 16 aliases/63 branches; 32 enums/131 members;
seven scalar aliases, three Protocols and three schema bases. Concrete constructor positives
and alias JSON discrimination are distinct. No nullable values or constructor bypasses.

| Cell / named test | Exact observable predicate and mutation target |
| --- | --- |
| CA01 `test_all_81_direct_constructor_and_json_rows` | All 81 ordinary constructors and exact JSON round trips use compatible scenario data; preserve the appendix's six scenario recipes and enum/alias/default tests. Remove one literal expected row or change one real field default: the corresponding catalog/default assertion fails |
| CA02 `test_required_null_and_extra_json_matrix` | Every required-field omission/null and each extra field rejects on its intended field/location AND finite Pydantic error type; `json_invalid`, broad `Exception`, unrelated root validator and count-only evidence are invalid. Relax one required field/extra-forbidden configuration: that exact named row fails |
| CA03 `test_scalar_domains_and_all_bounds` | Id 3/128 accepted, 2/129/empty/space/uppercase/non-ASCII/separator rejected; Digest 64 lowercase hex accepted, 63/65/uppercase/nonhex rejected; Text 1/128 accepted, 0/129 rejected; strict ints reject bool/float/string; Pos 1 versus 0/-1, NonNeg 0 versus -1, Zero 0 versus ±1, Lane 1 versus 0/2. Each upper limit below has limit PASS and limit+1 rejection. Mutate each declared bound independently; each corresponding subcase fails |
| CA04 `test_case_binding_identity_matrix` | Change one scope/case/binding identity at a time: project, baseline, manifest revision/digest, case, fixture; native executable, dependency, argv, cwd, environment plan. Preserve all other prerequisites so the intended local join rejects. Mutate the matching comparison, including each of the three previously accepted argv/cwd/environment mismatches |
| CA05 `test_kind_key_subject_applicability_matrix` | All five SPEC 11.1 rows, both key alternatives where legal, pure HOST_MEDIATION with NO_ROSTER, native WINDOWS, host surface/revision equality; pure host rule must not acquire native requirements. Reject wrong binding/subject pair, platform-only HOST_MEDIATION, wrong capability membership/requirement key/scope, duplicate/disagreeing prerequisite keys, two case IDs in HOST_DISCOVERY, omitted WA04_ADAPTER for its exact source-property pair. Mutate each applicability/join family separately |
| CA06 `test_refusal_proof_result_matrix` | Every RefusedClaimProof reason: SOURCE_MISMATCH/APPROVAL_UNRESOLVED/RECOVERY_REQUIRED require FAILED; other three require UNAVAILABLE. Test valid and wrong result separately for all six. PURE_RULE/MEASURED_NATIVE/UNAVAILABLE_PROBE/NOT_COMPLETED retain their exact allowed scope/result and required evidence fields. Removing each compatibility branch must fail its named pair |
| CA07 `test_roster_local_invariants` | Plan and observed coverage contain all seven categories exactly once; entry category agrees; global entry/alias and case-reference tuples are unique; planned and observed alias tuples are sorted without transformation. Include cross-category duplicates, unsorted planned aliases, valid all-ABSENT/zero-present shape and representable MISMATCH/nonzero negative observations. Disable each local family separately; the matching counterexample fails |
| CA08 `test_approved_manifest_plan_coverage` | Required roster_plans tuple exactly covers unique host subject key/ref/digest pins, once each; reject missing/extra/duplicate/wrong pin, including extra host plan for pure/native-primitive-only manifest. First discovery accepts future enforcement IDs as intent, not future evidence; later property case references occur in its same-key plan. Removing coverage comparison must make extra-pure-plan and mismatched-pin cells fail |
| CA09 `test_local_result_and_evidence_consistency` | Case/claim/check/requirement/capability IDs and reference tuples reject each appendix duplicate family. Pure/prelaunch reject launch fields; recovery rejects positive cleanup; capability PROVEN needs scope-compatible roster link, negative host observations may have NONE; supplied local subject/payload/outer observer/ref/key identities agree wherever the body contains both. Weaken each named local family, assert its own failure; authenticity/reduction remains excluded |
| CA10 ownership review | Parent checks the exact existing duplicate builders `_complete`, `_roster_key`, `_entry`, `_planned`, `_coverage`: scenario construction has one owner in fixtures and assertion modules import it. Literal catalog remains independent of production introspection. All relocated non-CQ11 test methods remain collected/exercised. This is a bounded source review, not an invented general semantic-coupling detector |

CA03 upper limits (field-level rows, never only the enclosing object's name): ResourceBounds
workload_duration_seconds=30, cpu_millicpu=1000, memory_bytes=536870912, process_count=4,
disk_bytes=67108864; CleanupBounds.cleanup_seconds=10; EvidenceBounds.total_bytes=33554432
AND case_output_bytes=262144; QualificationManifest.total_budget_seconds=1200. Zero-only
automatic_retry_count/container_count/build_worker_count and Lane are separate rows.

Expected error categories are authored per literal field family (missing, extra_forbidden,
integer/string/tuple/model/enum/literal constraint, or the named model-local value_error).
The specific assertion must identify the mutated field or intended local predicate. Do not
learn the expected error by catching the current candidate's exception. Negative fixtures are
valid structural JSON; first satisfy every unmodified guard (PITFALL C16).

## 4. Evidence, finite commands and return

Defect baseline-red is required for CA03 case_output_bytes, CA04 argv/cwd/environment, CA05 pure
host rule, CA06 refusal result, CA07 planned sorting, CA08 extra-pure-plan. New tests must collect
on 5d7789d before fixing; import/collection failure is not a red cell. Other retained coverage
gets observed green plus the mapped reverse mutations, not a fabricated historical first-red.

Use `C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe` as `$cvqPython` after
read-only version probes. Run in the bound owner worktree; one foreground process at a time,
60 seconds per command, 1200 seconds total per verification pass, zero automatic retries, no
CPU load/container/background polling. Each named mutation uses the same unittest command with
one fully qualified matrix method (subcase identifies the field). After exact byte restoration,
rerun that method; run the whole suite once at final candidate. Read complete unreduced output.

```powershell
& $cvqPython -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
& $cvqPython -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
git diff --check
```

The unchanged legacy CQ11 body is retained for B and is not an A acceptance oracle. A's two-module
suite must exercise every relocated domain assertion; this narrows the closure, not the final
combined obligations. Strict typing and Python test-module loading are the declared type/build smoke; direct constructor
plus JSON path is the real local primary seam. No separate configured formatter/linter is added
by this ticket. Existing pytest version mismatch is not repaired or reported as a qualified full
dependency environment. If a bound is insufficient, return BLOCKED with evidence, do not expand it.

Parent independently repeats checks and mapped mutations, with at least one door different from
the implementer's examples. Required reused evidence-only helper checks SPEC_GAP, BOUNDARY_DATA,
CONSISTENCY and REGRESSION at the exact candidate, READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT,
one bounded return, no source writes or approval. Parent alone decides. Zero mutation red is a
finding. Each predicate family needs a named candidate symbol and an unreduced command result;
one generic green count cannot discharge the matrix.

ImplementationReturn is COMPLETED / BLOCKED / CHANGE_DETECTED with ticket/revision/authority
commit, source baseline, additive candidate SHA, changed paths, checks (commands/exit/result),
named baseline-red and mutation/restore evidence, findings and scope deviations. Only the owner
commits its source; it does not write control docs or claim review/integration. Initial plus one
batched correction is the maximum for this new closure; preserve exhausted CVQ-01 history.

## 5. Sequential admission and rollback

This proposal requests exact owner approval for the stated contract-only reconstruction under
the already-approved two-phase exception. It does not claim preflight is green before those DTO
fixes exist. After approval, bind the fresh view/clean baseline, dispatch the retained owner,
wait_agent, then run actual parent contract preflight. No runner/queue/receipt/descriptor required.

Approval of CA01–CA10 freezes a candidate for [CVQ-01B](cvq-01b-source-admission.md); its exact SHA
must be recorded by the parent before B starts. The source gate is still NOT_QUALIFIED even if
its old test happens to print green. No integration/release or evaluator behavior follows A alone.
B must preserve A's wire/constructor verdict, and both must pass together before combined schema
admission. Existing Git rollback refs/candidates remain; recovery is additive, never reset/force.
Current return: ACTION_COMPLETED / TICKET_PROPOSED -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING.

## 6. Exact approval and admitted continuation — 2026-09-18

Owner replied **「核准」** to the two-ticket packet at
`6b49847fcab325442520b04f37d950ed31992149`: A document 01 LF
`ef7509f139c2cd4d94a6ebac38fbb974ab452a625765f8a94c5aa1d3726b9eb6`, B document 01 LF
`94a54d8cb1b39f90976684dd195b064c3044564704c89b693e002b03c7368c05`.
Document 02 is signature/status only. Sections 1–5 retain the exact approved scope and closure;
their proposal/pending wording is historical, not a request for another approval.

Parent read back clean control 6b49847f, clean source
`5d7789db6b950d317e7b500b757aa77a54d609ed` on `codex/cvq-01`, repository-contained
`.worktrees/cvq-01` with matching Git pointer/common directory and no ancestor reparse point.
Main and direct origin/main remained `b697738d009db37318ebc8762107ef8329e014db`.
Interpreter readback: Python 3.11.9, Pydantic 2.13.4, mypy 2.3.0; no install or config effect.
This proves source/environment identity, not working constructor predicates or native isolation.

Admit one contract-reconstruction action under the approved two-phase exception: retained
`cve_wire_implementer` (implementation-standard / Luna xhigh), reviewer `root` (ticket-review),
fresh single-ticket view `ctx-cvq-01a-closure01`. Prior CVQ-01 views stay closed. Bind this exact
committed revision/registry and the source SHA above; do not merge control docs into owner source.
Resolve authority using git show at the committed control identity, not working-tree prose.
Native followup_task reuses the existing owner under the owner's explicit reuse instruction;
no additional agent, receipt or bridge is created. Return the section-4 ImplementationReturn.

Route ACTION_COMPLETED / EXACT_APPROVAL_RECORDED -> AUTO_CONTINUE / IMPLEMENT(CVQ-01A), followed
by wait_agent -> parent review and required adversarial evidence. Passing A permits only the
exact reviewed-candidate binding for B; neither ticket permits integration, evaluator behavior,
push, release or installation. No claim that an exhausted prior closure was reopened.
