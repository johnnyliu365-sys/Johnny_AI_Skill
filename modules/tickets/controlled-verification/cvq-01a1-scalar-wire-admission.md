# CVQ-01A1 | Scalar and wire admission

| Field | Value |
| --- | --- |
| ID / kind / document / closure | `TICKET-CONTROLLED-VERIFICATION-CVQ-01A1` / `IMPLEMENTATION_TICKET` / `02` / `CLOSURE-CVQ-01A1` revision `01` |
| State / outcome | `OWNER_APPROVED / IMPLEMENTATION_ADMITTED`; one observable closure: ordinary public wire algebra and all scalar bounds discriminate valid from invalid values (original CA01–03, CA10) |
| Baseline / view | `070039b6227205f7bb4592f203a4fd7455311f31`; new `ctx-cvq-01a1-closure01` only after exact approval. Do not reset/rebase or reopen A closure01 |
| Preparation authority | Owner adopted convergence revision 08 at `058b8256bb1b2601fabc30c21a42ecc48c831875`, LF `24021ef0467d56c1bc3924e98b15d2f993e0dc720228dec44177da2132c50392`; preparation only, exact ticket approval pending |
| SPEC / wire | [Qualification SPEC](../../spec/controlled-verification-qualification.md) revision 07 LF `545f5058d8347ab069d6a23fdb07daaf06ab836998efb67b2c30b80fee3b1716`, sections 2/6/7/11; [wire](../../spec/controlled-verification-qualification-wire.md) revision 03 LF `6eb9d0a088e105e7c2dd4c3c3b4001f970ac34195c7a0cd78459a2f6016e9222`, sections 1–6 |
| Requirement / Context | `PRD-20260908-051` / `CHG-20260908-051`; [REQ-051](../../../doc/requirements/active/2026/environment-control/REQ-20260908-051.md) revision 11 LF `f52552cdafc857d605f1eda03bcdf3df4c3d0c49ad9adfb9f39335f4b341e272`; [sealed Context](../../../doc/context/controlled-verification/main.md) revision 02 LF `6f5465295cb3fd303bc555da655b3169d33292ad1f2ed4374748f82ddd6f2285`, READ_REFERENCE only |
| Owner / reviewer / profile | Retained `cve_wire_implementer`, implementation-standard; `root`, ticket-review; [dispatch profile](../../../doc/runbooks/dispatch-model-profile.md) REVISION_03; no elevation. POC / HIGH_ASSURANCE, one sequential source owner, then required evidence-only adversarial helper |
| Workspace / environment | Existing `.worktrees/cvq-01` / `codex/cvq-01`; fresh clean/containment/Git identity readback before dispatch. Python 3.11.9 / Pydantic 2.13.4 / mypy 2.3.0; no installation |
| Effects / XSS | `PRODUCTION_BEHAVIOR`, constructor-local defect correction and verification, not test-exempt. `XSS_NOT_APPLICABLE`; no UI, I/O adapter, evaluator, runtime/native capability qualification, VM/provider/target/configuration effect, integration, push, release or installation |

## Writable responsibility boundary

Paths in the first two rows are under `library/controlled_verification/`.

| Exact path | Writable symbols and sole responsibility |
| --- | --- |
| `qualification_values.py` | `QualificationModel.model_config` and seven scalar aliases' existing constraints only; existing enum/CapabilityKey declarations READ_ONLY; no internal imports |
| `manifest_contracts.py` | Existing field constraints of ResourceBounds, CleanupBounds, EvidenceBounds; QualificationManifest.active_lanes/total_budget_seconds only. No local-join validator changes |
| `tests/verification_qualification_catalog.py` | Literal expected field/default/alias/enum and scalar/error rows, independent of production; no scenario composition |
| `tests/verification_qualification_fixtures.py` | Add/reuse ordinary valid scalar/wire scenarios; preserve all existing caller results, no assertions/policy |
| `tests/test_verification_qualification_contracts.py` | Existing catalog/constructor/JSON/alias/default/configuration assertions and duplicate-builder removal only |
| `tests/test_verification_qualification_scalars.py` (new) | `QualificationScalarTests`, scalar/bound assertions only |
| `tests/test_verification_qualification_domains.py` | Relocate only scalar/bound assertions to scalars; explicit import of its TestCase as compatibility collection entry. Remaining case/evidence assertions unchanged, no duplicate collection |

The existing contracts + domains unittest entrypoints remain the complete A suite. New modules
are collected through explicit TestCase imports in domains, not also passed as full-suite inputs.
No custom discovery/loader/runner. Strict-check the new module directly. Other constituent
models, aliases and facades are READ_ONLY inputs to wire assertions.

Temporary negative-evidence exception, NEVER a committable implementation change: in a clean
candidate-bound review snapshot only, SW01 may change ResourceBounds.automatic_retry_count's
default; SW02 may give LaunchObservation.observation_revision a default; SW03 may change
binding_contracts.AttemptBinding's discriminator and qualification_values.Observation.PROVEN's
wire value. These four exact surfaces are the only extra read-only-symbol mutation grants.
Record the patch and restore exact bytes before any next mutation/final suite/commit. This
counterfactual evidence is not authorization to alter public wire semantics in the candidate.

## Finite acceptance closure

Literal names as well as counts must match the wire: 81 DTOs, 335 required field occurrences,
78 defaults, 751 omission/null/extra cells, 16 aliases / 63 branches, 32 enums / 131 members,
seven scalar aliases, three Protocols and three schema bases. All six wire §5 scenarios survive.
The complete existing catalog remains authoritative data, not a count or list learned from AST.

| ID / named method | Positive -> negative / expected error | Mutation door |
| --- | --- | --- |
| SW01 / contracts.`test_all_81_direct_constructor_and_json_rows`, `test_literal_wire_catalog_matches_source_ast` | Every named ordinary constructor + exact JSON round trip, exact names/fields/types/defaults; omitted expected row or changed declared field/default must fail the matching assertion | Remove one literal catalog row; separately change one real existing default temporarily. Catalog mutation is a test-oracle check, not production proof |
| SW02 / contracts.`test_required_null_and_extra_json_matrix` | Per literal DTO.field: valid -> omit (`missing` at field), null (literal predeclared field type error at field), extra (`extra_forbidden` at extra field). Exactly 751 rows, not merely count | One required scalar field made optional; base extra forbid -> ignore. Corresponding named missing/extra row red |
| SW03 / existing contracts default/alias/enum methods | 78 omission -> exact default, null -> named field type/literal error; wrong Literal constant -> `literal_error`, wrong Zero/Lane default-field value -> its integer constraint error, not a fabricated Literal error. 63 alias positives through TypeAdapter distinct from direct DTO positives; selector missing/null/unknown per branch; 131 enum values exact | One real default, one alias selector/discriminator, one enum member independently. Expected selector errors literal per alias: tagged unions missing `union_tag_not_found`, null/unknown `union_tag_invalid`; callable CaseResult closed-selector TypeError and EvidenceResolution UNKNOWN/tag error retain their distinct declared forms |
| SW04 / scalars.`test_identifier_digest_text_domains` | Id lengths 3/128 accepted; 2/129/empty/space/uppercase/non-ASCII/slash rejected (`string_pattern_mismatch`). Digest 64 lowercase hex accepted, 63/65/uppercase/nonhex rejected (same). Text 1/128 code points accepted; 0 -> `string_too_short`,129 -> `string_too_long`. Ordinary DTO field location | Each Id/Digest pattern, each Text min/max independently; keep all other DTO fields valid |
| SW05 / scalars.`test_integer_domains_are_strict` | Pos=1, NonNeg=0, Zero=0, Lane=1 ordinary field controls; EACH rejects EACH of bool / integral float / numeric string with `int_type` at named field, in constructor and JSON paths | Override strict=False at EACH alias separately; mandatory independent NonNegativeInteger door (old CM1) |
| SW06 / scalars.`test_integer_domain_edges` | Pos 0/-1 -> `greater_than`; NonNeg -1 -> `greater_than_equal`; Zero -1/+1 -> ge/le errors; Lane 0/2 -> ge/le errors. Control/domain-field location literal | Each gt/ge/le independently, respecting redundant base strictness covered by SW05 |
| SW07 / scalars.`test_every_resource_bound` | EACH of nine maxima below: max valid, max+1 -> `less_than_equal` at field. Retry/container/build-worker fields each 0 valid, ±1 reject ge/le | Each of nine Field.le separately; ZeroOnly's ge/le shared predicate exercised on all three zero-only fields |
| SW08 / contracts.`test_immutable_contract_configuration` | strict/frozen/extra-forbidden/assignment/revalidate-always configuration remains exact; ordinary assignment rejected `frozen_instance` at field; tuple fields accept JSON arrays but not arbitrary scalar/null | Base frozen and revalidate configuration independently; exact config assertion covers settings whose operational guard is redundant. Do not use bypass-built positives |

Nine maxima: ResourceBounds.workload_duration_seconds=30, cpu_millicpu=1000,
memory_bytes=536870912, process_count=4, disk_bytes=67108864;
CleanupBounds.cleanup_seconds=10; EvidenceBounds.total_bytes=33554432,
case_output_bytes=262144; QualificationManifest.total_budget_seconds=1200.
Scalar assertions use ordinary containing DTOs so inherited strictness is actually exercised.
For Id length mutations the regex includes length; remove that precise restriction independently
of alphabet where needed. Literal field/null families include int_type, string_type, tuple_type,
model_type/model_attributes_type, enum/literal and tagged-union selector errors as applicable;
each field's exact expected tuple is written before its negative run, not accepted as a broad set.

### Historical evidence amendment (approved direction, not fabricated red)

Original A §4's demand for case_output_bytes baseline-red on
`5d7789db6b950d317e7b500b757aa77a54d609ed` is SUPERSEDED for this replacement closure.
Parent reproduced limit=262144 green and limit+1 rejected with
`loc=("case_output_bytes",), type="less_than_equal"` on both 5d7789d and 070039b6.
SW07 must preserve that observed baseline green and prove weakening le makes the new named row
red, restoration green. No other historical defect requirement is waived; those belong to A2/A3.

## Fixed final commands

```powershell
& $cvqPython -B -m mypy --strict --follow-imports=silent library/controlled_verification tests/test_verification_qualification_contracts.py tests/test_verification_qualification_domains.py tests/test_verification_qualification_scalars.py tests/test_verification_qualification_boundaries.py tests/verification_qualification_fixtures.py tests/verification_qualification_catalog.py
& $cvqPython -B -m unittest -v tests.test_verification_qualification_contracts tests.test_verification_qualification_domains
git diff --check
```

For SW04–07 use `tests.test_verification_qualification_scalars.QualificationScalarTests.<method>`;
for SW01–03/08 use `tests.test_verification_qualification_contracts.QualificationContractTests.<method>`.
Build/type/import smoke and ordinary constructor/JSON are the local primary seam. CQ11 is not an
A acceptance oracle. No new formatter/linter or repository/native suite.

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

On actual approval root pins the A1 candidate for [A2](cvq-01a2-case-manifest-admission.md).
A1 completion alone does not complete A or qualify B.

## Exact approval and current continuation — 2026-09-19

Owner **「核准」** approves this document01 / closure01 in packet `b12dd7262606f7b951271cd51e336747f0638c38`,
LF `92bf356376024f51726411992f91caa5bb2eb892bec419571b8a5ad68287b57f`. Document02 records signature/state only; all
boundaries, predicates, temporary mutation exceptions, resource limits and return obligations
above remain unchanged. Earlier proposal/pending wording is historical, not a repeated gate.

Parent verified clean source `070039b6227205f7bb4592f203a4fd7455311f31` on
`codex/cvq-01`, repository-contained `.worktrees/cvq-01`, matching registered Git metadata,
and no ancestor reparse point. Python 3.11.9 / Pydantic 2.13.4 / mypy 2.3.0 read back.
Bounded `python -B -m unittest -v tests.test_verification_qualification_contracts`:
exit0, 11 tests OK (0.190s), complete unreduced output read. This is starting constructor
availability, not SW01–08 completion; the approved two-phase exception keeps unqualified CQ11
reserved for B. Main/direct origin/main remain b697738d009db37318ebc8762107ef8329e014db.

Bind fresh `ctx-cvq-01a1-closure01`, owner `cve_wire_implementer`, implementation-standard
(Luna/xhigh), reviewer root/ticket-review. The old host implementation seat is absent from the
current native agent inventory; allocate exactly one new native seat with that SAME owner
identity and preserve the existing source/worktree/branch. Subsequent approved tickets reuse
that seat with fresh ticket views. No other owner, source reset or model elevation is authorized.
Resolve exact committed ticket/upstream refs through this control commit with git show; do not
merge control documents into the implementation branch or load old ticket/review history.

ACTION_COMPLETED / EXACT_APPROVAL_RECORDED -> AUTO_CONTINUE / IMPLEMENT(CVQ-01A1), then
wait_agent -> parent review + required bounded helper. No runner/receipt/descriptor required.

All old exhausted views remain CLOSED. No integration, push, release, installation or evaluator
behavior grant is added. The packet also approves B document03's dependency amendment.
