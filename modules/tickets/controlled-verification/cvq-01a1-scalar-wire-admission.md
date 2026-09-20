# CVQ-01A1 | Scalar and wire admission

| Field | Value |
| --- | --- |
| ID / kind / document / closure | `TICKET-CONTROLLED-VERIFICATION-CVQ-01A1` / `IMPLEMENTATION_TICKET` / `07` / approved `CLOSURE-CVQ-01A1` revision `02`; proposed evidence amendment01 is NOT approved |
| State / outcome | `BLOCKED / TICKET_DEFECT / OWNER_EXACT_APPROVAL_PENDING / NON_DISPATCHABLE`; M02 cannot reach its frozen cell with the permitted fixture. Original SW01–08 behavior remains unchanged |
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

## Initial review and sole correction binding — 2026-09-19

Current disposition supersedes the admission-only metadata above. Candidate
`b1aa3fafaf03a7c47a869210b3934399124df933` returned from the retained native owner through
wait_agent; the attempted new seat was rejected as already existing, so no new seat was created.
The source worktree/branch/profile and `ctx-cvq-01a1-closure01` remain bound to that owner.

[A1 review](../../../doc/reviews/controlled-verification/cvq-01a1-scalar-wire-admission-code-review.md)
revision01 records CHANGES_REQUESTED, F01-F05 under unchanged SW01-08. Root reproduced clean
ancestry, 26 green methods and strict checking, but independent revalidation/separator mutations
were ZERO_RED. Required helper supplied static evidence, not a verdict. These are evidence
defects under existing authority, not a new closure or architecture decision.

Document03 binds the sole additive correction from b1aa3faf and the exact review revision01 in
this control commit. Preserve the original baseline/candidate, source ownership, path/symbol
boundaries, resource ceiling and all upstream digests. Do not merge these control files into the
source branch. Complete the entire frozen evidence matrix together; missing evidence is not pass.

ACTION_COMPLETED / CHANGES_REQUESTED -> AUTO_CONTINUE / IMPLEMENT(A1 correction01) -> wait_agent
-> parent final correction review. If blocking defects remain, return CONVERGENCE_REVIEW_REQUIRED
without a third correction. A2/A3/B remain dependent; no integration/push/release is granted.

## Final correction disposition — 2026-09-19

Current disposition supersedes the AUTO_CONTINUE entries above. Additive candidate
`1270664213d71eb2da524ecf7bf1885f28ffc82f` returned through wait_agent. Review revision02,
section 6, records strict checking/26 tests green and repaired F03/F04 counterexamples, but
F02's in-process negative-cell identities and F05's complete authenticated mutation record
remain unresolved. Required helper evidence was read and independently assessed by root.

Closure01 initial and correction reviews are exhausted. `ctx-cvq-01a1-closure01` is CLOSED;
retain owner, worktree, source commits and upstream signatures as history, not dispatch authority.
Document04 changes state/evidence only; it does not relax or revise the closure. Do not start
A2/A3/B, invent a renamed third correction, or elevate the model.

ACTION_COMPLETED / CHANGES_REQUESTED / CONVERGENCE_REVIEW_REQUIRED -> WAIT_FOR_HUMAN /
OWNER_CONVERGENCE_DECISION_REQUIRED. No new implementation, integration, push or release grant.

## Closure02 exact proposal — 2026-09-20

Owner approved the changed evidence ownership in convergence proposal revision13, section18,
at `b70b6978b1ad81de175ff6fee4f1ebc9b925e7ff`, LF
`8587879661626f0cfb81cf29eb32746301c8a94cd7947c33112d4132b2c6c182`.
This section freezes the promised finite ledger and evidence destinations for exact approval.
It does not turn adoption of the plan into approval of a then-unwritten ledger. Closure01 and
its view stay CLOSED; no third correction under that closure is authorized.

### Current implementation boundary and admission

- Start from preserved `1270664213d71eb2da524ecf7bf1885f28ffc82f` in `.worktrees/cvq-01`,
  branch `codex/cvq-01`; retain `cve_wire_implementer`. If its native seat is absent, allocate
  one seat for that same owner after inventory, not a replacement branch or parallel owner.
- Profile: bundled `JOHNNY-DISPATCH-DEFAULTS/01` at `de624ec43ea047955a395dee4ec4e697d8f6d767`;
  implementation-standard (Luna/xhigh), root ticket-review. No elevation. Existing approved
  SPEC07/wire03/Context02 and their exact digests above remain bound.
- Proposed fresh view `ctx-cvq-01a1-closure02`. Same-lifetime native dispatch and wait;
  no runner, receipt, queue, descriptor or host readback prerequisite.
- **Only writable source:** `tests/test_verification_qualification_contracts.py`, in
  `test_required_null_and_extra_json_matrix`,
  `test_all_78_default_omission_null_and_wrong_constant_cells`, and
  `test_alias_branch_counts_and_selector_negatives`.
- Change only subTest attribution/nesting: each negative has model/field/path/case, or
  alias/branch/selector/path/case. Existing missing, null, extra, wrong-default and selector
  alternatives retain their exact assertions, values, error tuples and counts. Move each
  assertion into its own subTest so one failed alternative cannot skip later alternatives.
  Positive controls and the complete 26-method collection stay intact.
- All production, catalog, fixtures, other test methods/files, policy and control documents
  are read-only. No cleanup/refactor, new runner, test framework, dependency or public schema.
  Source must contain technical explanations only, not this work order.

Baseline evidence for this repair is the existing F02/R0 failure's missing cell attribution,
not a false claim that the unchanged constructor suite is red. The returned candidate must
produce a collected failure identifying `LaunchObservation / observation_revision / json /
missing` for M03 below, and then the same method green after exact restoration. A green total
without this identity is insufficient. Capture that single implementer example in full.
Root owns the remaining complete ledger; the implementer does not produce another full campaign.

### Finite reviewer mutation ledger

All rows are temporary, one-at-a-time edits in a clean reviewer snapshot of the returned exact
candidate. These are not candidate edits. Every row pins source SHA, exact patch, command,
expected collected cell/reason, raw stdout/stderr and exits, restored source byte SHA-256 and
the same command's green output. Root reads the full output before deciding. Missing output,
collection error, wrong-reason red and zero red do not pass. Root M18 is a different door from
the implementer's M03. No discretionary expansion or random campaign is authorized.

Aliases below are file-qualified command suffixes, not new runners:

| Key | Fully qualified unittest method |
| --- | --- |
| C1 | `tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_wire_catalog_matches_source_ast` |
| C2 | `tests.test_verification_qualification_contracts.QualificationContractTests.test_required_null_and_extra_json_matrix` |
| C3 | `tests.test_verification_qualification_contracts.QualificationContractTests.test_all_78_default_omission_null_and_wrong_constant_cells` |
| C4 | `tests.test_verification_qualification_contracts.QualificationContractTests.test_alias_branch_counts_and_selector_negatives` |
| C5 | `tests.test_verification_qualification_contracts.QualificationContractTests.test_literal_enum_members_and_json_rows` |
| C6 | `tests.test_verification_qualification_contracts.QualificationContractTests.test_immutable_contract_configuration` |
| S1 | `tests.test_verification_qualification_scalars.QualificationScalarTests.test_identifier_digest_text_domains` |
| S2 | `tests.test_verification_qualification_scalars.QualificationScalarTests.test_integer_domains_are_strict` |
| S3 | `tests.test_verification_qualification_scalars.QualificationScalarTests.test_integer_domain_edges` |
| S4 | `tests.test_verification_qualification_scalars.QualificationScalarTests.test_every_resource_bound` |

Each command is the already-approved 60-second bounded subprocess invocation of
`python -B -m unittest -v <fully-qualified-method>`; multiple keys mean separate commands.
No output-reducing wrapper or new script. `values` means
`library/controlled_verification/qualification_values.py`; `manifest` means
`library/controlled_verification/manifest_contracts.py`; `binding` means
`library/controlled_verification/binding_contracts.py`.

| ID / SW | Exact temporary predicate change | Command / required observation |
| --- | --- | --- |
| M01 / SW01 | Delete only `DTO_FIELDS["qualification_values"]["PlatformCapabilityKey"]` row in `tests/verification_qualification_catalog.py` | C1: literal DTO inventory disagreement; test-oracle probe, not production proof |
| M02 / SW01,03 | manifest `ResourceBounds.automatic_retry_count: ZeroOnly = 0` -> `= 1` | C1 and C3: declared default disagreement / ResourceBounds automatic_retry_count omission value differs from literal 0 |
| M03 / SW02 | binding `LaunchObservation.observation_revision: PositiveInteger` -> `PositiveInteger = 1` | C2: named LaunchObservation observation_revision/json/missing rejection no longer raised |
| M04 / SW02 | values `QualificationModel.model_config.extra="forbid"` -> `"ignore"` | C2: named DTO extra_matrix_field/json/extra cells no longer rejected |
| M05 / SW03 | binding `AttemptBinding` only: `Field(discriminator="kind")` -> `Field()` | C4: collected AttemptBinding/PureContractBinding/kind/json/missing no longer rejected; import failure is not acceptable |
| M06 / SW03 | values `Observation.PROVEN = "PROVEN"` -> `"PROVEN_MUTATED"` | C5: exact Observation wire member disagrees with literal expected vocabulary |
| M07 / SW04 | values OpaqueMetadataId quantifier `{2,127}` -> `{0,127}` | S1: project_id `ab` rejection no longer raised |
| M08 / SW04 | same alias `{2,127}` -> `{2,128}` | S1: project_id length129 rejection no longer raised |
| M09 / SW04 | same alias pattern -> `^[A-Za-z][A-Za-z0-9._/-]{2,127}$` | S1: uppercase/separator cells no longer rejected; length restriction remains |
| M10 / SW04 | values Digest `{64}` -> `{63,64}` | S1: baseline_digest length63 rejection no longer raised |
| M11 / SW04 | same alias `{64}` -> `{64,65}` | S1: baseline_digest length65 rejection no longer raised |
| M12 / SW04 | same alias `[0-9a-f]` -> `[0-9a-gA-F]`, exact length64 retained | S1: uppercase/nonhex digest cells no longer rejected |
| M13 / SW04 | values BoundedText `min_length=1` -> `min_length=0` | S1: host_version length0 rejection no longer raised |
| M14 / SW04 | same alias `max_length=128` -> `max_length=129` | S1: host_version length129 rejection no longer raised |
| M15 / SW05 | values PositiveInteger `Field(gt=0)` -> `Field(strict=False, gt=0)` | S2: PositiveInteger constructor/JSON cells cease to produce exact int_type |
| M16 / SW05 | values ZeroOnly add `strict=False`, preserving ge/le | S2: ZeroOnly constructor/JSON cells cease to produce exact int_type (other bounds remain live) |
| M17 / SW05 | values ActiveLaneCount `strict=True` -> `False`, preserving ge/le | S2: active_lanes constructor/JSON cells cease to produce exact int_type |
| M18 / SW05 | values NonNegativeInteger `Field(ge=0)` -> `Field(strict=False, ge=0)` | S2: DiscoveredEffectSet counters constructor/JSON cells cease to produce exact int_type; independent reviewer door |
| M19 / SW06 | values PositiveInteger `gt=0` -> `ge=0` | S3: value0 no longer rejected as greater_than; negative value's exact error also disagrees |
| M20 / SW06 | values NonNegativeInteger `ge=0` -> `ge=-1` | S3: counters value-1 no longer rejected |
| M21 / SW06,07 | values ZeroOnly `ge=0` -> `ge=-1`, preserve le | S3 and S4: all three ResourceBounds zero-only fields accept -1 |
| M22 / SW06,07 | values ZeroOnly `le=0` -> `le=1`, preserve ge | S3 and S4: all three ResourceBounds zero-only fields accept +1 |
| M23 / SW06 | values ActiveLaneCount `ge=1` -> `ge=0`, preserve strict/le | S3: active_lanes0 no longer rejected |
| M24 / SW06 | values ActiveLaneCount `le=1` -> `le=2`, preserve strict/ge | S3: active_lanes2 no longer rejected |
| M25 / SW07 | manifest ResourceBounds.workload_duration_seconds `le=30` -> `le=31` | S4: named field max+1 no longer rejected |
| M26 / SW07 | ResourceBounds.cpu_millicpu `le=1_000` -> `le=1_001` | S4: named field max+1 no longer rejected |
| M27 / SW07 | ResourceBounds.memory_bytes `le=536_870_912` -> `le=536_870_913` | S4: named field max+1 no longer rejected |
| M28 / SW07 | ResourceBounds.process_count `le=4` -> `le=5` | S4: named field max+1 no longer rejected |
| M29 / SW07 | ResourceBounds.disk_bytes `le=67_108_864` -> `le=67_108_865` | S4: named field max+1 no longer rejected |
| M30 / SW07 | CleanupBounds.cleanup_seconds `le=10` -> `le=11` | S4: named field max+1 no longer rejected |
| M31 / SW07 | EvidenceBounds.total_bytes `le=33_554_432` -> `le=33_554_433` | S4: named field max+1 no longer rejected |
| M32 / SW07 | EvidenceBounds.case_output_bytes `le=262_144` -> `le=262_145` | S4: named field max+1 no longer rejected; no invented historical baseline-red |
| M33 / SW07 | QualificationManifest.total_budget_seconds `le=1_200` -> `le=1_201` | S4: named field max+1 no longer rejected |
| M34 / SW08 | values QualificationModel `frozen=True` -> `False` | C6: exact frozen configuration assertion fails |
| M35 / SW08 | values QualificationModel `revalidate_instances="always"` -> `"never"` | C6: exact revalidate configuration assertion fails |

M25–33 all modify only the named field in `manifest`; no class validator changes. M02/M03/M05/M06
reuse the four existing read-only-symbol exceptions. No other production surface is granted.
For mutations whose same predicate is covered in two methods, retain both observations; do not
count two methods as two independent predicates. SW08's positive assignment and tuple controls
remain in the final suite even when an earlier exact-config assertion detects its mutation.

### Evidence custody and return

Root writes evidence into these exact new leaves under `doc/reviews/controlled-verification/`
only after execution, indexing each in that partition and then its parent with LF digests:

- `cvq-01a1-closure02-sw01-03-evidence.md`: M01–M06 plus the implementer's raw M03 return.
- `cvq-01a1-closure02-sw04-06-evidence.md`: M07–M24.
- `cvq-01a1-closure02-sw07-08-evidence.md`: M25–M35 and final strict/full-suite output.

Every leaf has artifact ID/revision, exact candidate and scoped execution identity. Raw captured
outputs belong in these evidence leaves, never source code. No output hash without bytes. Root
alone updates the existing review and ticket/index states. One required evidence-only helper at
the exact candidate returns finite SPEC_GAP/BOUNDARY_DATA/CONSISTENCY/REGRESSION findings; it
cannot write scripts or approve. Root alone owns verdict and integration.

The existing fixed strict command and contracts+domains suite apply unchanged. One foreground
process, 60 seconds per command, 1200 seconds per verification pass, zero retries/load/containers/
background polling. Insufficient bounds or an uncollectable/unreachable row stops with evidence.
Closure02 admits one initial plus one batched correction review, not unlimited repairs.

ImplementationReturn includes authority revision/SHA, starting/candidate SHA, exact changed
symbols/files, strict and focused checks/exits, full M03 patch/red/restore output and byte hashes,
findings/deviations. All other mutation rows are root's obligation, not omitted evidence.
After exact owner approval of this document05 LF digest, record the signature and fresh view,
then AUTO_CONTINUE -> IMPLEMENT -> wait_agent -> root review. A2/A3/B stay dependency-pending;
no partial integration, push or release. Packaging of the separate REQ-052 policy correction
does not admit CVQ source or qualify the responsibility gate.

ACTION_COMPLETED / CLOSURE02_PROPOSED -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING.

### Closure02 exact approval and dispatch binding

Owner answered **"核准確定版，直接派工"** to the question naming control commit
`1e50d2ef457a7a5de392fb8b34eb9fc2a8f51011`, document05/closure02, LF
`d25b6c3b3f873a95eccea88e0e8ab222848cb67b5a87ace23958b480a85d0bbf`.
Document06 records approval/admission only; no predicate, destination, resource limit or source
boundary changes. The proposed/pending text immediately above is now historical.

Root read back clean `codex/cvq-01` at `1270664213d71eb2da524ecf7bf1885f28ffc82f`, the exact
registered Git worktree under this repository, no ancestor reparse point and the admitted
Python/Pydantic/mypy versions. Bind `ctx-cvq-01a1-closure02`; the previous native source-owner
seat is absent, so allocate one Luna/xhigh seat for retained owner `cve_wire_implementer`.
Root remains reviewer and sole orchestrator. Dispatch the bounded current section, not history.
Implementation source is committed only by its owner. Parent may provide that same owner a
fresh exact-candidate evidence snapshot for M03; this does not create another implementation
owner or move another owner's checkout. Root alone controls the separate full review snapshot.

ACTION_COMPLETED / EXACT_APPROVAL_RECORDED -> AUTO_CONTINUE / IMPLEMENT(CVQ-01A1 closure02)
-> wait_agent -> candidate evidence and root review. No main integration, push or release grant.

## Closure02 initial return and proposed M02 evidence amendment01

The retained Luna/xhigh owner returned additive candidate
`8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc`, parent `1270664213d71eb2da524ecf7bf1885f28ffc82f`.
Only the three authorized contracts-test methods changed. Root reproduced strict checking and
the complete 26-test suite, and the named M03 cell now fails with the required identity. The
existing native seat was reused; the duplicate-name allocation was rejected, not a new owner.
The required evidence-only helper returned no static finding in this exact limited patch.

Root executed the 35 frozen mutations and exact restorations. M02 C1 detects the changed
default, but C3 fails while constructing all_direct_rows: QualificationCase revalidates
ResourceBounds.automatic_retry_count=1 before the omission subTest can execute. This is a
wrong-reason red, not the required named cell. Changing the fixture is outside the approved
closure02 boundary; asking the implementer to do so would violate the dispatch. The defect is
in the root-authored evidence plan, not a product-behavior or implementer defect. Full captures
and the exact disposition are in [review section 7](../../../doc/reviews/controlled-verification/cvq-01a1-scalar-wire-admission-code-review.md).

### Proposed exact exception (owner approval required)

Retain this candidate, closure02 and every SW predicate. Authorize root, only in a detached
review snapshot pinned to 8d6b8291, to add the explicit keyword `automatic_retry_count=0` in
`tests/verification_qualification_fixtures.py::resource_bounds()` for the M02 experiment only.
This is an ordinary valid constructor argument, not a bypass, coercion or changed expected
value. No other fixture, assertion, oracle, production predicate or source-owner edit is allowed.

Order after exact approval of document07 and its LF digest:

1. Record pristine fixture bytes/hash. Add that one keyword, then run C1 and C3 green with
   production untouched. If the controls do not pass, stop; do not improvise another patch.
2. Apply only the existing M02 production patch (`automatic_retry_count = 0` -> `= 1`).
   Run C1 and C3 once each. Require C1 declared-default disagreement and the C3 named
   `ResourceBounds / automatic_retry_count / json / omission` value comparison `1 != 0`.
   An earlier error, zero red or another reason remains incomplete.
3. Restore the production file and rerun both commands green while the explicit-value fixture
   remains. Restore the fixture to the original candidate bytes, verify both hashes/clean tree,
   then run the existing strict command and complete 26-test suite once.
4. Preserve the failed original M02 evidence; append this separately identified run to the
   existing SW01–03 evidence leaf. Read the remaining stored raw streams for final review;
   do not rerun the other 34 mutations merely to reproduce their already-captured outputs.

Same existing per-command60s/pass1200s limits, one foreground process, no retries/load/new runner.
No committable source change or renewed implementer correction is proposed. This is a narrow
review-fixture exception, not closure03, an evidence waiver, or reset of exhausted closures.
Root alone may record approval after all evidence meets the unchanged closure; A2/A3/B remain
dependency-pending until then. All integration/push/release restrictions remain.

ACTION_COMPLETED / TICKET_DEFECT / EVIDENCE_AMENDMENT_PROPOSED -> WAIT_FOR_HUMAN /
OWNER_EXACT_APPROVAL_PENDING. Do not execute the proposed exception before approval.
