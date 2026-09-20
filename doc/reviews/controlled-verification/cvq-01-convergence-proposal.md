# CVQ-01 — schema preflight convergence proposal

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01-CONVERGENCE` / `CODE_REVIEW` / `25` |
| Lifecycle / conclusion | `A1_A2_REVIEW_APPROVED / A3_SPLIT_EXECUTION_APPROVED / B_DEPENDENCY_PENDING / NOT_INTEGRATED`; earlier approvals and failed closures preserved |
| Control baseline | `dc45f31f6c56983613665f276bf15207419274e3` |
| Examined source | Closure-03 correction `5d7789db6b950d317e7b500b757aa77a54d609ed`; all prior candidates preserved |
| Ticket | [CVQ-01](../../../modules/tickets/controlled-verification/cvq-01-qualification-admission.md), document 10, current digest in its registry; closure 03 exhausted, unchanged. Historical document 09 at dc45f31f LF `babcceb227bf8f91356dfbbb90f5e14ad1adab19f43a99686bdae46e8acff16d` |
| Contract | [Qualification SPEC](../../../modules/spec/controlled-verification-qualification.md) revision 07 LF `545f5058d8347ab069d6a23fdb07daaf06ab836998efb67b2c30b80fee3b1716`; wire appendix revision 03 remains approved |
| Evidence | [Schema preflight](cvq-01-schema-preflight.md), revision 04, LF `66f2e6636869665665bd15f210f259a405686125d33eb9dc0ccbaa9180ac3f8a` |
| Responsibility | Parent owns the replan recommendation and review verdict. Reused Terra/xhigh supplied read-only adversarial evidence; parent ran the candidate checks/probes/mutations. No source implementation, model elevation or owner decision is granted by this proposal |

Sections 1–10 preserve earlier convergence/design/adoption history. D-CQ11/D-CLAIM, exact
closure-03 approval and A1/A2's responsibility splits have been answered. Section 29 is the current
disposition; historical pending routes do not reopen those answered decisions.

## 1. Diagnosis and retained boundary

The owner-approved two-phase exception was exercised, not ignored: schema construction first,
then actual reviewer preflight before behavior. Initial and one correction both failed that
preflight. Revision 02 evidence preserves real strict-type/test runs, malformed-JSON masking,
duplicate-report acceptance, zero-red guard removals and exact restoration. Repeating those
unchanged commands or renaming another correction would not resolve the control defect.

There are both implementation defects and underspecified control predicates. The implementation
omits already-required observer/roster evidence and exhaustive discriminating tests. The frozen
text also leaves two design decisions implicit: what closed static surface CQ11 admits, and
the applicability of host/native evidence. The parent must settle those before another dispatch;
the failure is not evidence that a stronger implementation model alone would fix the contract.

The approved architecture and sealed shared Context were reread. No changes to D1/D2/D3,
Python 3.11, three injected read-only ports, pure/native proof separation or repository authority
are proposed. No native capability, full dispatch, installation or release is claimed delivered.
The goal remains complete dispatch first, then one-click installation/removal; existing Git
rollback refs and unintegrated source candidates remain intact.

## 2. Two owner decisions — revision-02 proposal, adopted below

### D-CQ11: closed permitted surface for this pure package

Recommend a package-scoped positive import/call policy instead of an open-ended effect denylist.
This is the finite CQ11 predicate, not a new general-purpose analyzer or runtime sandbox.

- External imports for the schema slice: `__future__.annotations`; `enum.Enum`;
  `typing.Annotated`, `Literal`, `Mapping`, `Protocol`, `TypeAlias`, `Union`;
  `pydantic.BaseModel`, `ConfigDict`, `Field`, `StringConstraints`, `Discriminator`, `Tag`,
  `model_validator`. Every other external import rejects unless a reviewed policy revision adds it.
- Internal imports resolve to the ticket's constituent DAG, regardless of relative/absolute
  spelling, package-form import, aliases or function/class nesting. Wildcards reject. Reject
  cycles and imports through a facade that reach forbidden constituents.
- The call inventory below is the proposed closed symbol table, not permission for an implementer
  to decide what is "pure." Alias resolution preserves the original symbol; unresolved receivers,
  dynamic call targets, rebinding or parameter/variable shadowing of approved callees reject.
- Existing exclusions remain: `Any`, casts, Pydantic bypass construction/copy-update, dynamic
  import, `eval`/`exec`, reflective `getattr`/`setattr`, ambient mutable services and effect APIs.
  Match qualified and aliased forms throughout the AST, including unused renamed helpers.
- Facades permit only docstrings, future imports, explicit re-exports and a literal immutable
  `__all__`; not functions, classes, validators or initialization calls.

| Permitted calls | Exact boundary |
| --- | --- |
| Builtins | `len`, `set`, `frozenset`, `tuple`, `sorted`, `any`, `all`, `isinstance`, `enumerate`, `zip`; `ValueError` and `TypeError` construction. No other builtin calls |
| Schema construction | The listed Pydantic `ConfigDict`, `Field`, `StringConstraints`, `Discriminator`, `Tag`, `model_validator`; exact checked public DTO/enum constructors from the frozen inventory |
| Mapping lookup | `Mapping.get` only on a receiver proven by a local `isinstance(receiver, Mapping)` guard, with no rebinding and within that guard's body; not arbitrary `.get` calls |
| Named local functions | Direct calls to module-local functions whose full bodies pass this same policy; statically resolved acyclic call graph, all paths inspected, explicit typed parameters/return. Function name or a "pure" comment is not evidence |
| Later behavior slice only | Ordinary checked-model `model_validate`, `model_validate_json`, `model_dump`, `model_dump_json`; `pydantic.TypeAdapter` construction and its `validate_python`, `validate_json`, `dump_python`, `dump_json`. The receiver must resolve to the exact checked model/adapter, not an arbitrary same-named method |
| Later behavior port reads only | `resolve` on one of the three explicitly injected, typed port parameters. No lookup by name, callback registry or arbitrary object's `.resolve` |

For the later behavior slice the only additional external imports proposed are
`pydantic.TypeAdapter` and `pydantic.ValidationError`; no `json`, filesystem or effect library is
needed for the declared public JSON-validation seam. If a future requirement genuinely needs
another call/import, return to this policy's approval boundary rather than weakening the checker.
These later rows do not admit behavior before schema preflight.

Local-function checking admits ordinary scalar/tuple/set expressions, comparisons, comprehensions,
local assignments, conditionals, finite collection iteration, returns and the listed exception
construction. It rejects global/nonlocal writes, attribute/subscript writes, function-valued
parameters/returns or assignment aliases, recursion, `while`, async/generator functions and
context-manager/decorator hooks other than the listed schema decorators. Pydantic validators and
discriminator callbacks receive the same whole-body inspection; passing an arbitrary callback
is not allowed. Production classes are checked DTOs, enums, the three Protocols and the exact
schema bases `QualificationModel`, `_CommonBinding`, `_CaseResultIdentity` with their declared
BaseModel/QualificationModel inheritance only; enum `(str, Enum)` and Protocol inheritance are
the named exceptions, not permission for arbitrary extra bases. No custom metaclass, magic method
or descriptor. Module state permits immutable literals/
tuples, checked type aliases and schema declarations; the common base's literal `ConfigDict`
configuration is the explicit schema exception, not a mutable service store.

This is a bounded first-party source grammar. It does not decide arbitrary Python purity or
analyze installed dependency internals. The AST gate must reject unsupported syntax/receiver
resolution, not import or execute target code to find out. The existing strict checker remains
required; neither test is evidence of protected host execution or dependency supply-chain safety.

Tradeoff: adding a legitimate dependency needs a small explicit policy amendment. This is
preferable to claiming that seven forbidden module names cover all filesystem/network/process
effects. It does not claim to confine hostile arbitrary Python or replace protected execution.

### D-CLAIM: explicit evidence applicability, not nullable inference

Recommend an approved, tagged claim scope with the following finite applicability table. Exact
DTO names/fields and new tag vocabulary must be transcribed into the next SPEC/closure revision;
these proposed meanings are not current implementation authority.

| Actual case | Claim scope / required evidence |
| --- | --- |
| PURE_RULE or SOURCE_PROPERTY | Pure-rule claim only, even when its subject is a native or host rule; no native capability assertion |
| TRUSTED_NATIVE_DISCOVERY of a non-host primitive | Native-probe scope; no host roster and no prerequisite requiring its own completed probe |
| TRUSTED_NATIVE_DISCOVERY for HOST_MEDIATION | Exact host discovery scope; approved expected roster plus actual discovered set, not an enforcement verdict |
| ADVERSARIAL_WORKLOAD | Native-property scope; measured native behavior and bounded launch/cleanup evidence |
| REAL_HOST_PROPERTY | Exact host-property scope; independently accepted discovery prerequisite and later actual entry observations |

`CapabilityKey` identifies its subject separately: HOST_MEDIATION requires a host-scoped key;
other families may use an explicitly approved host-scoped or platform-scoped key. A host-scoped
key carries exactly one HostSurface; a platform-only key carries none. No empty/null stand-in and
no CLI/Desktop aliasing. Pure-rule results may describe a host-scoped rule but cannot prove that
host's enforcement.

For native claims, distinguish a measured primitive record (primitive, race-model and failure-
semantics refs all required) from an unsupported/unavailable probe record (finite reason and
probe evidence, no invented working primitive). A not-run record has only its real plan/event
evidence. Pure claims carry no native-proof payload. FAILED measured observations retain their
primitive evidence; UNAVAILABLE or NOT_RUN must not be upgraded to PROVEN. This replaces
"where applicable" with an executable tag predicate without requiring fake positive evidence.

## 3. Connected data graph — proposed transport placement

The three existing ports remain the only external data seams. Ordinary validation is shape
evidence, never authenticity. Proposed transport placement below closes S7/S8; the exact public
wire inventory must be frozen after the owner decisions, before a new schema dispatch.

| Owner / seam | Typed data made reachable | Time and authority rule |
| --- | --- | --- |
| Independently composed ApprovedManifestPort FOUND | Exact approved manifest and referenced approved roster **plan** bodies: key, plan ref/digest, expected category presence and expected entry/alias/disposition/oracle identities | Read independently of caller JSON. Planned presence/absence is intent, not observed HostCategoryCoverage; no future discovery or absence evidence is a prerequisite for the first probe |
| QualificationCase subject | Tagged no-roster, host-discovery subject or host-property subject; host subjects bind the exact roster key and approved roster ref/digest | Native primitive discovery is not automatically a host discovery case. Host discovery must not require its own future discovery-coverage ref |
| PrerequisiteEvidencePort FOUND | Existing exact prerequisite binding, including approved observation revision/evidence digest | HOST_ROSTER_DISCOVERY names a completed discovery result for a later host-property case; never an enforcement result |
| EvidenceObservationPort FOUND | Authenticated typed evidence subjects and their necessary observed payloads: discovery set/coverage or enforcement coverage as appropriate | Protected adapter resolves actual data; caller-supplied ref/digest/comparison is not self-authentication. MISSING/CONFLICTING retain real rejection evidence |
| Executed case observation | Observer identity plus exact check/evidence bindings; native launch identity only after launch | Add the missing observer for both pure and native execution; launch observer is not a substitute for pure execution observer |
| Report admission | Exact expected case/check coverage plus independently resolved roster bodies/observations | Compare actual sets and keys; never accept a comparison enum alone. Discovery completeness and enforcement remain separate predicates |

The evidence-subject union needs separate finite alternatives for case, check, cleanup,
prerequisite binding, roster absence, discovered set, discovery coverage and present-entry
enforcement. An ABSENT subject binds roster key/category/discovery surface; it must not require
dispatch-entry ID or enforcement oracle. An enforcement subject binds its actual entry and oracle.
Each returned subject, ref, digest and observer is compared to the requested approved binding.
No fourth port, ambient dictionary/service locator, deferred untyped JSON or additional authority
store is introduced.

Capability observations have one chosen carrier: an authenticated capability-payload alternative
of **EvidenceObservationPort FOUND**, not ApprovedManifestPort and not a self-authenticated report
DTO. Proposed manifest requirements bind `observation_id`, one declared `capability_id`, exact
CapabilityKey, claim scope and nonempty exact case IDs. Multiple distinct observations may concern
the same capability, but their IDs are unique and pure/native scopes are never combined into a
stronger claim. Report capability claims contain only `observation_id` and `evidence_ref`; their
IDs must exactly cover those independent manifest requirements. The resolver request derives its
key/scope/case set from the approved requirement, not from a caller's replacement tuple.

The FOUND payload carries the ordinary typed CapabilityObservation plus its evidence digest and
observer identity. Admission compares the requirement ID/key/scope/case set, evidence ref/digest
and observer binding, and verifies its finite result against those already-validated CaseResults.
A PROVEN payload conflicting with failed/incomplete/unavailable underlying results rejects; an
opaque ref alone never satisfies the requirement. Missing/conflicting capability records use the
existing unauthenticated-evidence rejection, not a fourth resolver or a nullable success payload.
The exact new constituent DTO names and required-wire catalog are transcription work for the
pending closure, not a further choice of transport or authority owner.

Observed HostCategoryCoverage stays in discovered evidence: PRESENT carries its real discovery
evidence; ABSENT carries its actual discovery-surface/absence evidence. Do not put those observed
records into the pre-probe plan. This separation prevents the proposed approved-roster snapshot
from accidentally reintroducing the SPEC section-2 circular qualification prohibition.

An all-ABSENT roster can have valid discovery coverage: seven authenticated absence closures,
empty discovered entry/alias sets, zero unknown/unobservable counts and matching exact key.
Its enforcement structural alternative is `ZERO_PRESENT_ENTRIES`, bound to that discovery
ref/digest and containing **no** fictitious entry/oracle/launch observations. This alternative is
not a full-host PROVEN result. SPEC section 6 still requires a permitted positive effect and denied
bypasses for a full mediation claim. Without those, a dependent full-host claim cannot qualify;
the proposed case refusal is existing `HOST_ROSTER_UNQUALIFIED`, not a false HOST_ABSENT claim.
A structurally invalid manifest still follows INVALID_MANIFEST. A nonempty expected roster versus
an actually empty discovery is a set mismatch, not the all-ABSENT success alternative.

The current nullable `host_roster_subject` additionally imposes a roster on *all*
TRUSTED_NATIVE_DISCOVERY cases (`manifest_contracts.py`, candidate lines 90–100). That is not
the SPEC's distinction between primitive discovery and host discovery. This is recorded now,
not silently added as a later surprise finding or implementation instruction.

## 4. Concrete coverage inventory and finite test work

This is the inspected candidate inventory, **not** a frozen count for the amended design. Internal
base classes and the three Protocol classes are not DTO rows. Facades own no independent DTOs.

| Constituent | Public concrete DTOs at `9796790` |
| --- | --- |
| values (1) | CapabilityKey |
| bindings (3) | PureContractBinding, NativePreLaunchBinding, LaunchObservation |
| prerequisites (7) | PrerequisiteKey, PrerequisiteRequirement, PrerequisiteEvidenceBinding, FoundPrerequisite, MissingPrerequisite, ConflictingPrerequisite, QualificationPrerequisiteSet |
| roster (9) | HostEffectRosterKey, HostRosterSubject, HostEffectEntry, PresentHostCategoryCoverage, AbsentHostCategoryCoverage, DiscoveredEffectSet, HostRosterDiscoveryCoverage, HostEffectObservation, HostRosterEnforcementCoverage |
| manifest (6) | QualificationScope, ResourceBounds, CleanupBounds, EvidenceBounds, QualificationCase, QualificationManifest |
| report (16) | CheckObservation, CompleteExecutionObservation, IncompleteExecutionObservation, CapabilityObservation, ExecutedPureCaseResult, ExecutedNativeConfirmedCaseResult, ExecutedNativeRecoveryCaseResult, RefusedPrerequisiteCaseResult, RefusedOtherCaseResult, RefusedRecoveryCaseResult, UnavailableCaseResult, NotRunCaseResult, QualificationReport, ManifestRefusedEvaluation, ReportRejectedEvaluation, ReportAcceptedEvaluation |
| ports (11) | ApprovedManifestFound, ApprovedManifestMissing, ApprovedManifestConflicting, CaseEvidenceSubject, CheckEvidenceSubject, CleanupEvidenceSubject, RosterEvidenceSubject, EvidenceObservationRequest, AuthenticatedEvidence, MissingEvidence, ConflictingEvidence |

The parent verified the named source declarations:
1 + 3 + 7 + 9 + 6 + 16 + 11 = **53 concrete public DTOs**. The enumerated names, not an estimated
module subtotal, are the expected inventory. There are also 7 constrained scalar aliases, 3 ports and 9 tagged
aliases with **30 total branches**:
AttemptBinding 2; PrerequisiteResolution 3; HostCategoryCoverage 2; ExecutionObservation 2;
CaseResult 8; QualificationEvaluation 3; ApprovedManifestResolution 3; EvidenceSubject 4;
EvidenceResolution 3.

The 30 enum types contain 119 named values at this candidate. Each enum value needs its own
enum-constructor/TypeAdapter round-trip row. **Do not demand an illegal DTO field placement just
to cover an enum:** public Admission and broad Refusal vocabulary do not all occur as accepted
values in current DTO fields. Test finite field-specific subsets and their rejections separately.

| Catalog section | Fixed evidence required before dispatch |
| --- | --- |
| Public DTO rows | Explicit public constructor, exact valid inputs/wire expectation and owning module for every target DTO; no bypass construction |
| Tagged alias rows | One ordinary TypeAdapter JSON round-trip per branch; direct DTO construction alone cannot prove union discrimination |
| Enum rows | Literal expected enum names/values, every value's round-trip; affected DTO subset positives and illegal-value negatives |
| Required-field rows | Hand-authored required-field list per public fixture; one omission and one JSON-null cell per required field, plus one extra-field cell per DTO |
| Other wire fields | Explicit default/optional behavior if allowed, including discriminator omission rules. Nullability is never inferred from what the implementation currently accepts |
| Domain rows | Distinct strict integer, positive, nonnegative, zero-only, opaque-ID, digest, duplicate, tag/binding and cleanup cells required by CQ02 |
| AST controls | Relative, absolute and package-form forbidden imports; aliases; nested/renamed helpers; indirect facade reachability; dynamic/bypass calls; facade logic and ambient mutable state |

For the current inventory there would be 53 direct DTO and 30 alias-branch positive rows, plus
119 enum rows. The required-field negative count is `2 × sum(explicit required fields) + DTO count`.
Do not declare that count complete until the amended public field inventory is frozen. Reflection
may produce the **observed** inventory for comparison, but may not generate its own expected
list from `model_fields`, schema or the same validators being tested. Compare identities as well
as counts. Changes to fields/variants cannot silently reduce coverage.

Negative fixtures start from valid JSON decoded structurally, remove/change exactly one field,
then serialize valid JSON. Assert the intended error location/type; `json_invalid` is not a
required-field rejection. Restore the positive/zero-only mutation cells removed in the correction
and test duplicate report IDs. These are finite table-driven checks, not one bespoke script per
fixture. Keep fixtures/data, contract assertions and AST policy in their existing separate owners;
no giant mixed test runner or new background process.

## 5. Bounded proposal audit — 2026-09-18

One reused Terra/xhigh helper audited committed revision 01 at
`5400b5bb062d7c4ecd81e602b3d1f8fa4c792da2`, with SPEC_GAP, STATE_TRANSITION and CONSISTENCY only;
isolation was READ_ONLY_INTENT_ONLY, effect scope NO_EXTERNAL_EFFECT, one pass, at most five
findings, no test execution. It returned three findings. Parent reread the cited SPEC/ticket
sections and owns these dispositions:

| Finding | Parent disposition in this proposal revision |
| --- | --- |
| P1: "pure helpers" and positive call table deferred another policy choice | Accepted. Section 2 now declares exact permitted call classes, receiver checks, finite helper-body/call-graph rules and unsupported-syntax refusal; no arbitrary Python purity claim |
| P2: CapabilityObservation has no chosen typed carrier | Accepted. Section 3 chooses EvidenceObservationPort FOUND with independently approved observation requirements, report refs and exact subject/result comparison |
| P3: all-ABSENT has no explicit structural enforcement alternative | Accepted with a constraint the parent independently checked at SPEC lines 280–284: complete absence is valid discovery, but cannot replace the required permitted-positive/denied-bypass proof. Zero-present carries no invented execution and cannot issue full-host PROVEN |
| Parent P4: pre-probe approved roster uses observed category closures | Corrected in proposal only. Expected roster plan and later observed discovery/absence records are separate, preserving first-probe admissibility under SPEC lines 121–127 |

Evidence in this section is document/source reasoning, not an executed AST checker, constructor
test or native experiment. Revision 02 has not received a second helper pass, implementation
approval or capability qualification. The original findings and revision-01 bytes remain in Git.

## 6. Decomposition and continuation

Do not split this shared contract into concurrent type-owner lanes, and do not disguise a third
correction as a new implementation ticket. The current phase has one coherent public-contract
boundary but an incomplete control inventory. Recommended sequence:

1. Owner decides D-CQ11 and D-CLAIM. This document is a proposal, not a completed owner Grill.
2. Parent transcribes those choices into a proposed SPEC amendment and closure revision 03,
   with exact public wire/required-field catalog, final counts, positive call policy and typed
   port-result graph. Preserve closure 02 and both candidates as historical evidence.
3. Obtain exact owner approval for that changed closure. The existing two-phase approval is not
   a blanket approval for new semantics or a third loop. Only then reassess low-model admission
   and dispatch a new bounded schema phase to the same Luna/xhigh owner, if admissible.
4. Parent reviews actual constructors, strict types and finite matrix; independent reverse
   mutations must fail the intended cells. Zero red is a finding. Behavior remains NOT_ADMITTED
   until all schema preflight requirements pass; no dummy reference or mocked capability can
   replace native evidence. Preserve the finite command/resource budget; no stress repetition.
5. Behavior stays separated into the already-owned prerequisite, roster, report and composition
   units. Each behavior slice needs its own observable test closure against the frozen contracts;
   integration/release and native/host qualification remain separate later authority boundaries.

This control action edits documentation only. No source candidate, main branch, sealed Context,
approved SPEC, host/provider/VM, publication or remote ref is changed. Return `ACTION_COMPLETED`
for the convergence proposal, then `WAIT_FOR_HUMAN` for the two named design decisions.

## 7. Owner adoption — 2026-09-18

The owner's **「採用」** adopts D-CQ11 and D-CLAIM in proposal revision 02 at
`fa6b06a0beb9f9e25bb582a95b565c12e5d3595a`, LF SHA-256
`3fbe8c18b15992d86b99487b769ae411caac410102bd6480c3a94e4c7b78e93d`.
These two choices are resolved; do not ask them again. Sections 2–6 retain the proposal wording
as the decision's historical object, not as a still-unanswered choice.

The control action transcribes the choice into qualification SPEC revision 06, its wire
appendix revision 02 and CVQ-01 document 06 / proposed closure 03 after the bounded audit below.
The approval object is that
whole exact packet, not the source inventory and not the previous failed candidate. The sealed
Context, D1/D2/D3, three external read ports, source-only scope and source-verification limits
are unchanged. Native/host capability, third source correction, integration and release remain
unapproved. The prior schema review remains failed historical evidence, not a superseded PASS.

The reused Luna/xhigh owner returned a read-only AST inventory of `9796790`: 53 concrete DTOs,
30 enum classes / 119 members and nine tagged aliases / 30 branches. No production module was
imported, no test or effect ran and no source was changed. Parent uses this only to locate the
current surface. In particular `Field(min_length=...)` or `Field(le=...)` **without an explicit
default is required**, despite the helper's syntactic `D:Field(...)` classification. Expected
fields must come from the amended contract, not copy this observation as a test oracle.

Current route: `ACTION_COMPLETED -> AUTO_CONTINUE / CONTRACT_TRANSCRIPTION`; subsequent exact
closure approval remains `OWNER_EXACT_APPROVAL_PENDING`. This records the owner's decision,
not a new implementer allocation or a reset of the exhausted closure-02 correction counter.

## 8. Transcription audit and parent disposition — 2026-09-18

Initial transcription was committed docs-only at `42e196d2772557e6aee08a8bf5a6238ae67a2df4`
(SPEC 05 / appendix 01 / ticket 05). One reused Terra/xhigh helper inspected that immutable
proposal under SPEC_GAP, STATE_TRANSITION and CONSISTENCY, one pass, maximum five findings,
READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT. It returned three findings without writes, tests,
production imports or approval. Parent performed independent catalog/link/hash inspection and
owns these batched corrections; no source candidate or runtime was inspected as passing.

| Finding | Parent disposition in SPEC 06 / appendix 02 / ticket 06 |
| --- | --- |
| Helper F1: case-to-capability-ID match has no represented field | Accepted. QualificationCase now requires capability_id, belonging to declared scope; requirement ID/key/scope comparison is executable. CQ05 changes the ID alone as a negative |
| Helper F2: report binding digest has no independently expected value | Accepted. QualificationCase requires the approval record's binding_digest, paired with its binding body. Case/check/cleanup requests derive it before report evidence; changing caller/result and returned digest together still fails CQ06 |
| Helper F3: two discovery cases leave entry evidence subject ambiguous | Accepted. This proposed version permits exactly one case per HOST_DISCOVERY requirement, covering the whole roster. All entry discovery subjects derive from that approved case. Independent requirements/surfaces remain separate; later property consumes accepted discovery rather than recreating its old case authority |
| Parent P5: case-insensitive recount included prose as a declaration | Fixed. Case-sensitive literal row parsing and type/alias resolution are used; final catalog has 81 DTOs, 335 required occurrences including the two newly added case fields, 78 defaults, 16 aliases/63 branches, 32 enums/131 members; required/null/extra cells = 751 |
| Parent P6: future property cells in first-discovery manifest reintroduce circularity | Fixed. Planned enforcement IDs are future intent. First discovery needs no future evidence pins/property cells; the later separately approved property manifest binds completed discovery. Scenario 3/4 and CQ09 distinguish these lifetimes |

Validation is document-level: independently recount names/fields/branches and resolve referenced
types, verify local Markdown links, verify leaf→registry→root LF digests after final bytes,
and run git diff --check. It is not public-constructor/strict-type/native proof. No additional
helper pass or source test run is claimed; no third correction was dispatched. The three-port
ownership, sealed Context and both failed source candidates remain unchanged. The final exact
approval request is the revised packet, not the earlier audited commit's unfixed text.

Current return: `ACTION_COMPLETED / CONTRACT_TRANSCRIPTION -> WAIT_FOR_HUMAN /
OWNER_EXACT_APPROVAL_PENDING`. Only the exact proposed replacement closure/resumption remains
pending; owner adoption of D-CQ11/D-CLAIM is complete and is not reopened.

## 9. Exact approval was exercised; closure 03 still failed

Owner approved the exact packet at `965e16b00d6049be6552465ac1ce1cbac968a8cb`, recorded in
`b10c08f1ae15080e4878bda09b0ab43ee5a134a6`. Root dispatched the same Luna/xhigh owner, waited
for `cf89ec33`, reviewed it and committed one batched correction at `acd6b140`. The same owner
returned `5d7789d`; parent and the required read-only helper reviewed that correction. This is
actual same-lifetime dispatch/wait/review, not a claim that an absent runner blocked the work.

Real progress: the 81-row DTO catalog, 751 required/extra negatives, 78 defaults, 63 alias
branches, 131 enum members, observer fields and much local consistency are now represented.
The exact remaining defects and independent zero-red mutations are in schema review revision 04.
The source is not approved, integrated or released; all reviewed commits and rollback refs remain.

The previous readiness assessment was too broad. CQ11 is not just listing nine allowed filenames:
it is a source recognizer with name/alias resolution, branch-sensitive receiver checks, helper
call-graph constraints and an independent negative syntax corpus. That verification responsibility
can be proved separately from DTO input algebra. Repeatedly packing both into one correction
has not closed either. This is a decomposition finding, not proof that every ticket needs a
stronger model, more test processes, larger timeouts or additional native infrastructure.

## 10. Proposed responsibility split — owner decision required

Recommend `SPLIT_REQUIRED` under ticket-decomposition.md, preserving the approved SPEC/wire,
D1/D2/D3, source-only two-phase exception and all original CQ obligations:

| Proposed observable closure | Sole responsibility and completion evidence |
| --- | --- |
| Contract-admission closure | Ordinary DTO construction accepts every approved shape and rejects local identity, applicability, refusal, roster-plan and duplicate inconsistencies. Exact literal wire/default/enum corpus and every stated scalar bound; one fixture owner, assertion runner separate from data. Named mutations prove each validation family. No source-analysis policy implementation or evaluator behavior. |
| Source-admission closure | The package-scoped CQ11 checker accepts the exact allowed syntax/typed symbol graph and rejects every frozen forbidden grammar family, including indirect recursion, receiver rebinding/branch escape, aliases and computed facade exports. Separate syntax resolution, closed policy and literal adversarial corpus responsibilities; no arbitrary Python purity claim, runtime sandbox or DTO semantics change. Check the actual completed contract package as well as the independent corpus. |

These are independently observable verification closures, not a frontend/backend/tests-later
split. The contracts remain the already-approved upstream input. Use one retained implementation
owner in sequence, never concurrent type owners. Finish/freeze contract predicates first; then
qualify the source gate against that exact candidate. The second boundary may allow only
semantics-preserving contract-source conformance adjustments if the new exact ticket declares
them; it may not silently relax the grammar. The combined CVQ schema admission still requires
both closures green together before any evaluator/behavior phase. Neither intermediate ticket
completion is authority to merge a partially qualified package or to claim full dispatch works.

The next control action, if this split is adopted, is to freeze two exact finite tickets and
their dependency/order/writable-symbol/mutation matrices. Existing failures become mandatory
counterexamples, not advisory history. No reset of closure-03's exhausted allowance and no
unchanged third-correction label. Specific new helper paths, public/internal checker seam and
strict-command additions must be explicit in those approval objects before any source write;
this recommendation itself grants none. Reusing coherent existing code is allowed only through
the eventual ticket's source boundary, not by copying a second policy or expected oracle.

Retain implementation-standard and ticket-review unless that concrete split reveals an
indivisible hard ticket. Only a named HardTicketAssessment can propose a single-ticket
implementation-elevated / elevated-review pair. No such elevation is granted or inferred here.
Parent retains the whole review context and verdict; adversarial helpers remain evidence-only.

Decision requested: adopt this two-closure decomposition so the parent can prepare exact new
ticket boundaries; do not lower the approved grammar/data invariants. Owner may instead choose
to defer this capability. Previously approved D-CQ11/D-CLAIM are not being asked again.
Current source action remains NONE. Route ACTION_COMPLETED / CONVERGENCE_REPLAN_PROPOSED ->
WAIT_FOR_HUMAN / OWNER_REPLAN_DECISION_PENDING. No push, release, install or native effect.

## 11. Split adoption and exact ticket proposals — 2026-09-18

Owner replied **「採用」** to revision 05 section 10 at
`dc45f31f6c56983613665f276bf15207419274e3`, LF
`6ad63ea17bf1750549d1f5087138e9bb447b477bcd8d683cac7405bed1262847`.
This is the adoption record, not a claim that the earlier proposal was already approved.
The decision authorizes preparation of two precise verification closures; it does not reset
CVQ-01 closure 03 or grant a third correction. D-CQ11/D-CLAIM remain unchanged and answered.

| New exact proposal | Sole observable closure / order |
| --- | --- |
| [CVQ-01A](../../../modules/tickets/controlled-verification/cvq-01a-contract-admission.md), document 01 / closure 01 | Contract construction/wire and local identity/applicability/roster/proof validation, including the actual failed probes. One fixture owner; separate literal-wire assertions from local-domain assertions. Starts only after exact approval, at preserved 5d7789d |
| [CVQ-01B](../../../modules/tickets/controlled-verification/cvq-01b-source-admission.md), document 01 / closure 01 | AST source admission with separate policy, symbol/graph resolution, grammar predicates and literal adversarial corpus; starts only after A review approval at an exact committed SHA. Rechecks the unchanged A contract suite at its final candidate |

The implementer sees one new ticket, not CVQ-01's full review history. Exact SPEC/wire/Context
references are supplied by each ticket. One retained implementation-standard owner executes
sequentially with fresh ticket-bound views; ticket-review retains the verdict and whole review
context. No model elevation is granted. The branch/candidates are preserved additively.

The limited two-phase exception remains explicit: A is permitted to reconstruct contract
predicates before the parent can qualify them; source grammar remains NOT_QUALIFIED until B.
No intermediate ticket permits integration or behavior. Combined schema preflight requires both
closures at one SHA. The later evaluator, actual protected dispatch, native capability and
one-click install/removal are still unfinished; no source-only pass can substitute for them.

### Bounded dependency audit and parent disposition

Reused Terra/xhigh inspected exact control dc45f31f and source 5d7789d, one read-only pass,
SPEC_GAP / CONSISTENCY, READ_ONLY_INTENT_ONLY / NO_EXTERNAL_EFFECT, at most three findings.
No tests, source execution, writes, commits or effects. It returned one authority-artifact
gap: section 10 still said owner decision pending. Accepted; this section records the actual
owner reply while both exact tickets remain approval-pending. No implementation grant is
inferred from the helper's task message.

It also located the existing acyclic source table (boundary test lines 505–514) and found no
direct ports/facade cycle. Parent independently inspected both modules and that table: ports
import constituent contracts; the terminal facade re-exports ports, and __init__ re-exports the
facade. CVQ-01B explicitly proposes that finite edge table to disambiguate the older phrase
"contracts only". The implementation's existing table is an observation, not an authority source;
owner approval of B binds the displayed table. No new port, moved public DTO or relaxed grammar
is proposed. This helper return is not review of the newly authored ticket text or source PASS.

### Control validation and return

This action is DOCS_ONLY. It does not rerun the failed implementation or claim new source
evidence. Parent checks exact upstream LF pins, finite matrix/ownership/command closure,
local links, D8 leaf → partition → root hashes, diff scope and git diff --check. Source tests,
mutation qualification, installation and release remain NOT_RUN in this action. The unchanged
schema review revision 04 preserves all actual failures.

Current return: ACTION_COMPLETED / SPLIT_ADOPTION_AND_TICKETS_RECORDED -> WAIT_FOR_HUMAN /
OWNER_EXACT_APPROVAL_PENDING for the two displayed tickets and source boundaries. A completion
SHA for B is DEPENDENCY_PENDING, not a request to approve an unknown candidate now. Once exact
tickets are approved, parent may record the actually reviewed A SHA for sequential B admission
without changing B's closure; a different contract or boundary requires renewed authority.
No source, main, remote, sealed Context, SPEC, profile, host/VM/provider or release changes.

## 12. Owner approval of the split tickets — 2026-09-18

Owner **「核准」** binds the whole exact two-ticket packet at
`6b49847fcab325442520b04f37d950ed31992149`: CVQ-01A document 01 LF
`ef7509f139c2cd4d94a6ebac38fbb974ab452a625765f8a94c5aa1d3726b9eb6` and CVQ-01B document 01 LF
`94a54d8cb1b39f90976684dd195b064c3044564704c89b693e002b03c7368c05`.
Their document 02 signatures do not change their closure 01 scope. The exact source boundary,
sequential dependency, finite tests and two-phase ordering are now approved, not source PASS.
A's signature records fresh clean source/control/environment readback and the exact current
AUTO_CONTINUE action. B remains blocked on A's actual review-approved SHA, not on another owner
decision. Old closure-03 source and failure records are unchanged. No integration/push/release.

ACTION_COMPLETED / EXACT_APPROVAL_RECORDED -> AUTO_CONTINUE / IMPLEMENT(CVQ-01A).

## 13. A correction exhausted: bounded evidence replan proposal — 2026-09-18

The approved A/B sequence was actually exercised. Initial A fd8c1a3 and its one correction
070039b6 were implemented by the retained Luna/xhigh owner, waited on, then reviewed by root
with required bounded read-only adversarial help. [A review revision 02](cvq-01a-contract-admission-code-review.md)
records three independent zero-red mutations on the correction, one genuine red/restore proving
the new property-plan membership guard, and missing remaining matrix cells. No agent is still
implementing, and no runner/receipt/callback capability caused this stop.

Two distinct causes need separate treatment:

1. **Evidence coverage is incomplete.** One large CA03–CA09 matrix still contains negative cases
   invalid for multiple reasons. Assertions and mutation records cover examples, not every frozen
   predicate family. Green totals do not distinguish that omission. This is not evidence that
   more wall-clock time, parallel owners, longer logs or larger verification loads are needed.
2. **A baseline clause was wrong.** Parent required CA03 case_output_bytes baseline-red at 5d7789d
   without checking that its le=262144 bound was already correct. Direct baseline construction
   now proves limit accepted/limit+1 rejected. That requirement must change through approval;
   it cannot be repaired by instructing the implementer to manufacture a historical red.

Recommendation: `SPLIT_REQUIRED`, plus a narrowly stated evidence-rule amendment, not another
unchanged A correction or model elevation. Prepare three sequential independently provable
contract-admission closures from the preserved correction, with existing wire/SPEC semantics:

| Proposed verification responsibility | Completion evidence and retained obligations |
| --- | --- |
| Scalar and wire admission | Existing CA01–03: ordinary public constructors, literal field/default/alias/error algebra, scalar domains and all bounds. Each intended error/mutation is a separate named row with an otherwise valid baseline. |
| Case and manifest admission | Existing CA04–05/08: local binding/applicability/prerequisite/requirement joins and exact roster-plan membership. Accept/reject constructor behavior and its own independent counter-mutations form one closure. |
| Roster, proof and local evidence admission | Existing CA06–07/09: roster uniqueness/negative observations, proof-result compatibility, report duplication and authenticated local joins. Cross-category entry/alias negatives are isolated, not three simultaneous violations. |

CA10 applies to every slice: one fixture-composition owner, independent expected catalog,
responsibility-specific assertion modules and retained old assertions. All three include any
needed local-validator fix plus its verification; none is a code-now/tests-later layer. Use one
retained owner sequentially, pin the actually reviewed predecessor SHA, and rerun preceding
accepted contract tests at each candidate. No public type/port addition or evaluator behavior.
The final combined candidate must still pass all original A obligations before B can start.

The proposed evidence amendment removes **only** the impossible case_output_bytes historical
red requirement: require observed green on exact 5d7789d, then a mapped weakening which makes
its named test red and exact restoration green. Retain genuine defect-baseline red requirements;
distinguish saved initial-red from later baseline reproduction and never replace unknown history
with assertion. Before freezing new tickets, parent must actually check each required baseline
predicate/test can collect and fail for its intended reason. Exact approval remains required.

Each future ticket should enumerate predicate -> positive -> single-invalid negative -> expected
location/type -> mutation symbol -> command/result, not just repeat the family name. This is a
finite ticket-owned evidence map, not permission to build a generic mutation engine, add scripts,
weaken the source grammar or expand fixture duties. Exact path/symbol boundaries and command
budgets must be committed in the proposed tickets before dispatch; this recommendation grants
none. Model profile remains implementation-standard / ticket-review, since further valid
decomposition exists; no HardTicketAssessment or automatic escalation is claimed.

Owner decision requested: adopt the three verification closures and this narrow historical
evidence amendment so their exact tickets can be prepared. Alternatively defer the capability.
Previous D1/D2/D3, D-CQ11/D-CLAIM, two-phase exception and B's source-admission semantics are not
reopened. A closure 01 remains exhausted regardless of that future decision. Candidate 070039b6,
all predecessors and rollback refs remain untouched; no main merge, push, release or install.

ACTION_COMPLETED / CONVERGENCE_REPLAN_PROPOSED -> WAIT_FOR_HUMAN /
OWNER_REPLAN_DECISION_PENDING. No third correction and no B dispatch.

## 14. Owner adoption and exact ticket packet — 2026-09-19

Owner **「核准」** adopts section 13 at `058b8256bb1b2601fabc30c21a42ecc48c831875`,
revision08 LF `24021ef0467d56c1bc3924e98b15d2f993e0dc720228dec44177da2132c50392`.
This approves preparing the three verification closures and the narrowly stated historical
evidence amendment. It does not approve unwritten exact tickets or reopen A closure01.
Main and direct origin/main were read back at `b697738d009db37318ebc8762107ef8329e014db`;
control was clean at 058b8256, source clean at `070039b6227205f7bb4592f203a4fd7455311f31`.
No source/host effect, main integration, push, release or installation occurred.

The prepared exact approval packet is:

| Ticket | Proposed document / closure | One verification responsibility and sequence |
| --- | --- | --- |
| [CVQ-01A1](../../../modules/tickets/controlled-verification/cvq-01a1-scalar-wire-admission.md) | 01 / 01 | CA01–03 scalar/wire; starts preserved 070039b6 |
| [CVQ-01A2](../../../modules/tickets/controlled-verification/cvq-01a2-case-manifest-admission.md) | 01 / 01 | CA04–05/08 + their local duplicate families; starts actual review-approved A1 SHA |
| [CVQ-01A3](../../../modules/tickets/controlled-verification/cvq-01a3-evidence-admission.md) | 01 / 01 | CA06–07/09 remaining roster/proof/result/local-evidence predicates; starts actual review-approved A2 SHA |
| [CVQ-01B amendment](../../../modules/tickets/controlled-verification/cvq-01b-source-admission.md#7-dependency-replacement-proposal--2026-09-19) | 03 / existing 01 | Dependency becomes combined A1/A2/A3 at one accepted SHA; name read-only split tests in strict check, no SG/source grammar change |

Each exact leaf's LF digest is in the ticket partition index in this same commit. All are
NON_DISPATCHABLE pending exact packet approval. After that approval, actual predecessor SHA,
review/index and fresh single-ticket view bindings are admitted metadata; they do not create
another approval loop. Keep the same sequential owner and current-session reviewer. Old failed
A ticket04 and review02 remain unchanged historical evidence, not resumed authority.

CA10 is enforced in each proposed boundary: one fixture owner, literal independent catalog,
three responsibility-specific assertion modules and a compatibility collection aggregate.
Predicates that share redundant guards are explicitly grouped for discriminatory mutation;
no demand for an impossible isolated guard-red, no unrelated failure accepted as evidence.
A2 owns manifest/prerequisite duplicates; A3 reruns them instead of recreating that responsibility.
This is not a generic mutation runner or coupling detector. The frozen wire and Context are
unchanged; speculative validator/resolver behavior stays outside all three tickets.

### Parent baseline preflight before freezing proposals

Purpose: demonstrate that the retained *historical* required-red predicates actually collect
and fail on their named baseline, while the one waived false-red is already green. This is
2026-09-19 reproduction, not reconstructed initial TDD chronology, not full A acceptance.

Six inline unittest methods below ran in the existing clean read-only detached snapshots:
`.worktrees/cvq-01-schema-review-closure03-correction` at
`5d7789db6b950d317e7b500b757aa77a54d609ed`, and
`.worktrees/cvq-01a-review-correction` at
`070039b6227205f7bb4592f203a4fd7455311f31`. No source file was modified.
The four ERROR subcases below are constructor rejection of valid input inside collected tests,
not import/collection errors. Five FAIL subcases are acceptance of invalid input. The bound
BG01 is green on both and explicitly asserts its location/type. Candidate six green proves
these probes only; previous zero-red findings still require the new closure evidence.

Command, independently in each named snapshot (same interpreter, one foreground command, 60s,
zero retries/load; the inline source is documentation, not a new executable script):

```powershell
$cvqProbe = @'
import json,unittest
from pydantic import ValidationError
from library.controlled_verification import ApprovedManifestFound,CapabilityFamily,CapabilityObservation,CaseKind,CaseRefusalReason,ClaimScope,EvidenceBounds,NoObservedRoster,NoRosterSubject,Observation,PlannedHostEffectEntry,Platform,PlatformCapabilityKey,QualificationCase,RefusedClaimProof
from tests.verification_qualification_fixtures import approved_roster_plan,capability_key,host_capability_key,native_case,planned_host_entry,qualification_case,qualification_manifest
class BaselinePredicateProbe(unittest.TestCase):
 def test_BR01_native_plan_joins(self):
  key=PlatformCapabilityKey(family=CapabilityFamily.PLAN_BINDING,adapter_revision=1,platform=Platform.WINDOWS)
  base=native_case("case-native",CaseKind.TRUSTED_NATIVE_DISCOVERY,key,NoRosterSubject())
  for field in ("argv_digest","cwd_digest","environment_plan_digest"):
   payload=json.loads(base.model_dump_json()); payload["binding"][field]="f"*64
   with self.subTest(field=field),self.assertRaises(ValidationError):
    QualificationCase.model_validate_json(json.dumps(payload))
 def test_BR02_pure_host_positive(self):
  payload=json.loads(qualification_case().model_dump_json()); key=host_capability_key().model_dump(mode="json")
  payload["capability_key"]=key; payload["prerequisite_keys"][0]["capability_key"]=key; payload["prerequisite_requirements"][0]["key"]["capability_key"]=key
  self.assertEqual(QualificationCase.model_validate_json(json.dumps(payload)).subject,NoRosterSubject())
 def test_BR03_refused_unavailable_positive(self):
  for reason in (CaseRefusalReason.PREREQUISITE_UNPROVEN,CaseRefusalReason.RESOURCE_ENFORCEMENT_UNAVAILABLE,CaseRefusalReason.HOST_ROSTER_UNQUALIFIED):
   with self.subTest(reason=reason.value):
    value=CapabilityObservation(observation_id="observation-cvq",capability_id="capability-cvq",capability_key=capability_key(),claim_scope=ClaimScope.PURE_RULE,case_ids=("case-pure",),observer_ref="observer-cvq",evidence_ref="evidence-cvq",result=Observation.UNAVAILABLE,proof=RefusedClaimProof(reason=reason,admission_evidence_ref="admission-cvq"),roster_evidence=NoObservedRoster())
    self.assertEqual(value.result,Observation.UNAVAILABLE)
 def test_BR04_planned_sorting(self):
  payload=json.loads(planned_host_entry().model_dump_json()); payload["alias_ids"]=["alias-z","alias-a"]
  with self.assertRaises(ValidationError): PlannedHostEffectEntry.model_validate_json(json.dumps(payload))
 def test_BR05_extra_pure_plan(self):
  with self.assertRaises(ValidationError): ApprovedManifestFound(manifest=qualification_manifest(),roster_plans=(approved_roster_plan(),))
 def test_BG01_case_output_bound(self):
  EvidenceBounds(total_bytes=1,case_output_bytes=262144)
  with self.assertRaises(ValidationError) as caught: EvidenceBounds(total_bytes=1,case_output_bytes=262145)
  self.assertEqual([(e["loc"],e["type"]) for e in caught.exception.errors()],[(("case_output_bytes",),"less_than_equal")])
unittest.main(verbosity=2)

'@
& 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c 'import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)' 'C:/Users/GameBoy/AppData/Local/Programs/Python/Python311/python.exe' -B -c $cvqProbe
```

Baseline 5d7789d exit 1, unreduced output (line endings normalized and trailing spaces removed
for Markdown hygiene; no lines or diagnostics filtered):

```text
test_BG01_case_output_bound (__main__.BaselinePredicateProbe.test_BG01_case_output_bound) ... ok
test_BR01_native_plan_joins (__main__.BaselinePredicateProbe.test_BR01_native_plan_joins) ...
  test_BR01_native_plan_joins (__main__.BaselinePredicateProbe.test_BR01_native_plan_joins) (field='argv_digest') ... FAIL
  test_BR01_native_plan_joins (__main__.BaselinePredicateProbe.test_BR01_native_plan_joins) (field='cwd_digest') ... FAIL
  test_BR01_native_plan_joins (__main__.BaselinePredicateProbe.test_BR01_native_plan_joins) (field='environment_plan_digest') ... FAIL
test_BR02_pure_host_positive (__main__.BaselinePredicateProbe.test_BR02_pure_host_positive) ... ERROR
test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) ...
  test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='PREREQUISITE_UNPROVEN') ... ERROR
  test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='RESOURCE_ENFORCEMENT_UNAVAILABLE') ... ERROR
  test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='HOST_ROSTER_UNQUALIFIED') ... ERROR
test_BR04_planned_sorting (__main__.BaselinePredicateProbe.test_BR04_planned_sorting) ... FAIL
test_BR05_extra_pure_plan (__main__.BaselinePredicateProbe.test_BR05_extra_pure_plan) ... FAIL

======================================================================
ERROR: test_BR02_pure_host_positive (__main__.BaselinePredicateProbe.test_BR02_pure_host_positive)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 16, in test_BR02_pure_host_positive
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\main.py", line 782, in model_validate_json
    return cls.__pydantic_validator__.validate_json(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for QualificationCase
  Value error, host mediation requires a host subject [type=value_error, input_value={'case_id': 'case-pure', ...'case_output_bytes': 1}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

======================================================================
ERROR: test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='PREREQUISITE_UNPROVEN')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 20, in test_BR03_refused_unavailable_positive
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation
  Value error, refused proof requires failed result [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

======================================================================
ERROR: test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='RESOURCE_ENFORCEMENT_UNAVAILABLE')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 20, in test_BR03_refused_unavailable_positive
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation
  Value error, refused proof requires failed result [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

======================================================================
ERROR: test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) (reason='HOST_ROSTER_UNQUALIFIED')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 20, in test_BR03_refused_unavailable_positive
  File "C:\Users\GameBoy\AppData\Local\Programs\Python\Python311\Lib\site-packages\pydantic\main.py", line 263, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for CapabilityObservation
  Value error, refused proof requires failed result [type=value_error, input_value={'observation_id': 'obser...g='NO_OBSERVED_ROSTER')}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

======================================================================
FAIL: test_BR01_native_plan_joins (__main__.BaselinePredicateProbe.test_BR01_native_plan_joins) (field='argv_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 11, in test_BR01_native_plan_joins
AssertionError: ValidationError not raised

======================================================================
FAIL: test_BR01_native_plan_joins (__main__.BaselinePredicateProbe.test_BR01_native_plan_joins) (field='cwd_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 11, in test_BR01_native_plan_joins
AssertionError: ValidationError not raised

======================================================================
FAIL: test_BR01_native_plan_joins (__main__.BaselinePredicateProbe.test_BR01_native_plan_joins) (field='environment_plan_digest')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 11, in test_BR01_native_plan_joins
AssertionError: ValidationError not raised

======================================================================
FAIL: test_BR04_planned_sorting (__main__.BaselinePredicateProbe.test_BR04_planned_sorting)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 24, in test_BR04_planned_sorting
AssertionError: ValidationError not raised

======================================================================
FAIL: test_BR05_extra_pure_plan (__main__.BaselinePredicateProbe.test_BR05_extra_pure_plan)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<string>", line 26, in test_BR05_extra_pure_plan
AssertionError: ValidationError not raised

----------------------------------------------------------------------
Ran 6 tests in 0.010s

FAILED (failures=5, errors=4)
```

Candidate 070039b6 exit 0, unreduced output:

```text
test_BG01_case_output_bound (__main__.BaselinePredicateProbe.test_BG01_case_output_bound) ... ok
test_BR01_native_plan_joins (__main__.BaselinePredicateProbe.test_BR01_native_plan_joins) ... ok
test_BR02_pure_host_positive (__main__.BaselinePredicateProbe.test_BR02_pure_host_positive) ... ok
test_BR03_refused_unavailable_positive (__main__.BaselinePredicateProbe.test_BR03_refused_unavailable_positive) ... ok
test_BR04_planned_sorting (__main__.BaselinePredicateProbe.test_BR04_planned_sorting) ... ok
test_BR05_extra_pure_plan (__main__.BaselinePredicateProbe.test_BR05_extra_pure_plan) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.008s

OK
```

Original A's case_output_bytes historical-red demand is SUPERSEDED by the approved evidence
amendment: retain BG01 baseline green, require SW07 weakening-red/restoration-green. Genuine
argv/cwd/environment, pure-host, refused-unavailable, planned-sort and extra-pure-plan baseline
defects remain in their new tickets. No other waived cell or new capability claim.

ACTION_COMPLETED / EXACT_TICKET_PACKET_PROPOSED -> WAIT_FOR_HUMAN /
OWNER_EXACT_APPROVAL_PENDING. Next authorized action after exact packet approval is A1
admission/dispatch, not a third A correction, B first, merge or release.

### Proposal feasibility review and independent accounting

Retained evidence-only Terra/xhigh helper reviewed the three draft tickets without source/test
execution or edits. Root accepted three findings and corrected them before this commit:
SW03 demanded a read-only-symbol mutation without an exception; ER09 referred to rejection
validators that do not exist for allowed shapes; ER16's witness could disappear with the
very import it had to detect. Exact temporary review-snapshot-only exceptions now distinguish
counterfactual test evidence from committable public-schema changes; ER09 names six such
restrictions; ER16 is defined locally in the aggregate, not inside a removable imported class.
No helper verdict substitutes for root review.

Root also found requirement-in-scope is implied by case existence/in-scope and matching
capability ID. A2 now distinguishes a redundant diagnostic check from an independently
discriminated ID-equality predicate; it no longer demands impossible single-guard admission.
All field-level predicates and accepted wire semantics remain unchanged.

The helper additionally alleged 333 required fields / 747 negatives. Root did not adopt that
claim: independent recount from the exact approved wire, not production/catalog introspection,
gives 413 expanded field occurrences minus 78 defaults = 335 required, and 2*335+81 = 751.
Constraint `<=` is not a default `=`. No wire/DTO change is authorized to chase a different total.

Read-only recount command (control worktree):

```powershell
$cvqWire = Get-Content -LiteralPath modules/spec/controlled-verification-qualification-wire.md
$cvqGroups = @{}
foreach ($line in $cvqWire) {
 if ($line -match '^(CommonBinding|CaseIdentity|EvidenceIdentity) = (.+)$') {
  $cvqGroups[$Matches[1]] = @($Matches[2].Split(';') | ForEach-Object { $_.Trim() })
 }
}
$cvqInDtos = $false
$cvqRows = @()
foreach ($line in $cvqWire) {
 if ($line -match '^## 2\.') { $cvqInDtos = $true; continue }
 if ($line -match '^## 3\.') { $cvqInDtos = $false }
 if ($cvqInDtos -and $line -match '^([A-Za-z]\w*) = (.+)$') {
  $cvqDtoName = $Matches[1]
  $cvqFields = @()
  foreach ($field in $Matches[2].Split(';')) {
   $cvqField = $field.Trim()
   if ($cvqField.StartsWith('@')) { $cvqFields += $cvqGroups[$cvqField.Substring(1)] }
   else { $cvqFields += $cvqField }
  }
  $cvqDefaults = @($cvqFields | Where-Object { $_ -match '(?<![<>])=' }).Count
  $cvqRows += [pscustomobject]@{ dto=$cvqDtoName; fields=$cvqFields.Count; defaults=$cvqDefaults; required=$cvqFields.Count-$cvqDefaults }
 }
}
$cvqTotals = [pscustomobject]@{ dtos=$cvqRows.Count; fields=($cvqRows | Measure-Object fields -Sum).Sum; defaults=($cvqRows | Measure-Object defaults -Sum).Sum; required=($cvqRows | Measure-Object required -Sum).Sum; cells=2*($cvqRows | Measure-Object required -Sum).Sum+$cvqRows.Count }
$cvqTotals | ConvertTo-Json -Compress
$cvqRows | Where-Object { $_.dto -in @('PureContractBinding','NativePreLaunchBinding','ResourceBounds','EvidenceBounds','QualificationManifest') } | Format-Table -AutoSize
```

Exit 0, output (line endings/trailing spaces normalized, no rows omitted):

```text
{"dtos":81,"fields":413.0,"defaults":78.0,"required":335.0,"cells":751.0}

dto                    fields defaults required
---                    ------ -------- --------
PureContractBinding        10        1        9
NativePreLaunchBinding     29        1       28
ResourceBounds              8        3        5
EvidenceBounds              2        0        2
QualificationManifest       9        1        8
```

Root's disposition is TICKET_PACKET_PROPOSED, not implementation approval or claim that all
future mutation experiments already ran. Prior failed closures and candidates remain untouched.

## 15. Exact packet approval and A1 admission — 2026-09-19

Owner **「核准」** approves packet `b12dd7262606f7b951271cd51e336747f0638c38`: A1/A2/A3 document01
and B document03 dependency amendment, with exact signatures retained in their new revisions.
No semantic closure changes. A1 document02 records clean source070039b6/environment/containment
and the 11-test constructor preflight, direct-lane owner/profile/fresh view and single host seat
allocation (the previous implementation seat is absent). A2/A3 and B are approved but dependency
pending. Actual predecessor SHA binding after review needs no repeated owner approval.

ACTION_COMPLETED / EXACT_APPROVAL_RECORDED -> AUTO_CONTINUE / IMPLEMENT(CVQ-01A1).
Then wait_agent, parent review and required evidence-only helper. Old exhausted closures remain
closed. This admits no source-layer B first, evaluator, main integration, push, release or install.

## 16. A1 initial review and additive correction — 2026-09-19

The exact approved split packet remains unchanged. Native duplicate-name spawn was rejected;
followup_task reused cve_wire_implementer, and wait_agent delivered candidate
`b1aa3fafaf03a7c47a869210b3934399124df933` without owner relay. No new host seat was allocated.
The screenshot's separate parent HTTP400/access_programs.cyber error is not ticket test evidence
or permission to change account/plugin settings.

[A1 review](cvq-01a1-scalar-wire-admission-code-review.md) revision01 records the complete
initial batch F01-F05: incomplete closed catalog/error/configuration assertions, dropped scalar
vectors and incomplete mutation evidence. Parent observed strict checking/26 tests green and two
independent ZERO_RED regressions; required helper findings were independently examined. No
source candidate is approved by those green counts. A1 document03 admits its one additive
correction on the same owner branch/profile, from b1aa3faf. A2/A3/B remain approved but pending.

ACTION_COMPLETED / CHANGES_REQUESTED -> AUTO_CONTINUE / A1_CORRECTION -> wait_agent -> root
correction review. No new authority is needed for this unchanged-closure correction; exhaustion
returns convergence. No integration, push, release, install or evaluator behavior is granted.

## 17. A1 correction exhausted; retain work and return decision — 2026-09-19

Candidate `1270664213d71eb2da524ecf7bf1885f28ffc82f` is additive and preserved. Root's
[A1 review](cvq-01a1-scalar-wire-admission-code-review.md) revision02, section 6, records
the exact correction authority, 26-test/strict-check readback, required helper evidence and four
parent experiments with restoration. The original missing separator/configuration guards in
the tests are now discriminating. The public schema and production source were not changed.

Remaining frozen evidence obligations are concrete: required/null/extra and selector
alternatives still lack their in-process cell IDs, and the complete per-predicate mutation
patch/command/output record is not authenticated. An import-time PydanticUserError is not a
behavioral mutation red; parent independently proved a valid discriminator-removal door.
Green aggregate counts cannot replace these obligations, but they also must not be mislabeled
as a newly discovered product defect or reason to redo all schema work.

A1 document04 is BLOCKED / CONVERGENCE_REVIEW_REQUIRED / NON_DISPATCHABLE; its view is CLOSED.
A2/A3/B retain their exact approvals but cannot advance past this dependency. The remaining
decision is how to make cell-identification and evidence production reliably executable under
a newly explicit convergence authority; no remedy, new closure, exception or model elevation
is silently selected here. Preserve existing candidates and do not rename a third correction.

ACTION_COMPLETED / CHANGES_REQUESTED -> WAIT_FOR_HUMAN / OWNER_CONVERGENCE_DECISION_REQUIRED.
This is not a host-wakeup blocker: both owner returns arrived natively. No integration, push,
release, installation, provider or VM effect occurred. The access_programs.cyber request-origin
diagnosis remains limited to the observed host rejection, not a claimed platform fix.

## 18. Owner-requested re-convergence — 2026-09-20

The owner requested re-convergence after control commit
`844edb5ffd15fa4eb230269b66c7e0f6b350567b`. This authorizes diagnosis and a concrete proposal,
not silent reopening of exhausted closure01. Root reread the complete A1 ticket and review,
then the affected methods at preserved candidate `1270664213d71eb2da524ecf7bf1885f28ffc82f`.
The missing per-alternative subTest wrappers remain observable at contracts lines 447–469
and 554–619. No new runtime/schema defect is claimed and no candidate was modified.

### Recommended convergence decision: separate assertion repair from evidence custody

Retain the same A1 ticket and source branch; propose closure02 with all SW01–08 predicates,
counts, literal oracles, independent review and execution limits preserved. Do not open an
equivalent replacement ticket just to reset the review counter. Two explicit responsibilities:

1. **Implementation owner:** a narrow additive test-only repair gives every existing negative
   alternative an in-process identity: DTO, field, path and omission/null/extra case; alias,
   branch, selector and missing/null/unknown case. Cover default alternatives consistently.
   Assertions, fixtures, error expectations, production symbols and public contracts are not
   rewritten. Only the existing contracts test's cell attribution is writable for this repair.
   A passing total alone is insufficient. Return one exact candidate with strict/focused results
   and one fully captured authorized mutation/restore example, not an unreferenced family summary.
2. **Root reviewer:** own the complete retained SW01–08 mutation-evidence record. Resolve a
   finite ledger from the existing table before dispatch, assigning each predicate an ID,
   candidate-bound patch, exact command, intended cell/error and restoration check. After the
   candidate returns, execute the mapped mutations in the reviewer snapshot and record full
   stdout/stderr, exit codes, identity and byte restoration in reviewer-owned evidence leaves.
   Missing raw output is MISSING, collection error is not behavioral red, and zero red is a
   finding. At least one reviewer door differs from the implementer's captured example.

This changes evidence-production ownership, not the required coverage or observation. The
implementer is no longer asked to produce a large transcript package while root independently
rebuilds the same package. Root still reads unreduced output under the current review policy;
the pending machine-evidence compiler does not become a prerequisite for this repair.
The required read-only helper supplies bounded findings once; root alone decides the verdict.

All evidence must be retrievable from the same exact candidate; an old output hash without its
bytes is not reused. Exact evidence destinations and the finite ledger belong to the proposed
closure before its next approval, not to a later improvised dispatch. No new generic mutation
framework, runner, helper-authored script, expanded campaign or model elevation is proposed.
Keep one foreground process, 60 seconds per command, 1200 seconds per pass, zero automatic
retry/load/background polling. Exhaustion stops rather than increasing those bounds.

### Alternatives and continuation

Repeating the unchanged implementer-wide evidence assignment has already failed twice and is
not recommended. Building a general evidence runner first would add a new implementation and
qualification dependency to a small attribution repair; leave that to the existing CVE work.
Neither option justifies dropping SW predicates or declaring the aggregate green suite sufficient.

The owner must adopt the changed evidence ownership before root freezes closure02 and its
exact ledger/destinations for approval. A1 document04 remains BLOCKED/NON_DISPATCHABLE;
its closed view stays closed. A2/A3/B retain their approvals but remain dependency-pending.
No third correction, production mutation, integration, push, release or installed update occurred.

The separate installed-profile defect and source-content/responsibility requirements are tracked
in [REQ-052](../../requirements/active/2026/plugin-adoption-quality/REQ-20260920-052.md).
They do not retroactively add acceptance requirements to A1 or reopen completed findings.
ACTION_COMPLETED / CONVERGENCE_PROPOSED -> WAIT_FOR_HUMAN / EVIDENCE_OWNERSHIP_DECISION.

## 29. Owner split accepted and execution bound — 2026-09-20

After the explicit remaining-work and allocation explanation, the owner directed separation
and execution. [A3 document06](../../../modules/tickets/controlled-verification/cvq-01a3-evidence-admission.md)
records closure02: the retained Luna owner makes four existing-method test corrections;
root produces the complete unchanged ER evidence campaign and owns the review verdict.
The precise source delta, baseline af7fc428, operator map, evidence destinations and fresh
ctx-cvq-01a3-closure02 are fixed there. This changes work allocation, not accepted semantics.
Closure01 stays exhausted; no historical approval/evidence is overwritten.

Installation closure is independent. REQ-052's existing local qualification and confirmed stale
publication binding remain actual results, not A3 prerequisites or public-release authority.
No new model/seat, production semantics, helper framework, main integration or public effect
is granted by this decision. ACTION_COMPLETED / OWNER_SPLIT_RECORDED -> AUTO_CONTINUE / IMPLEMENT.

## 28. A3 correction exhausted — owner decision pending, 2026-09-20

A3's exactly approved closure01 was exercised after accepted A2 ce49f735. Initial ce2d750
and sole correction af7fc428 are preserved. [A3 review02 section5](cvq-01a3-evidence-admission-code-review.md#5-correction-review--convergence-required-2026-09-20)
records strict17/focused38 green, four now-discriminating named counterexamples, one outer
constructor error, and a new zero-red scope-guard regression. Reused Terra/xhigh supplied
bounded static evidence; root alone issued CHANGES_REQUESTED. No activity polling or extra
implementation seats were used.

The correction restores fixture ownership and several missing controls, but loses the measured
proof/PURE_RULE negative and still constructs several positives outside their named cells.
The owner separately clarified that most of the required mutation ledger was not captured or
retrievable. The small source repair and complete evidence production remain bundled in A3's
old assignment, unlike the explicitly adopted A1/A2 division. This is an observed responsibility
allocation/return failure, not proof that the model tier or product architecture is inadequate.
Do not respond by silently weakening closure01 or by dispatching a third correction.

### Recommended owner decision — proposal only

Preserve af7fc428 and all closed findings. Apply the A1/A2 division explicitly to a NEW finite
A3 closure: retained Luna/xhigh receives only the enumerated remaining test-row/attribution
repairs in the existing responsibilities; root owns the complete candidate-bound mutation
ledger, raw capture, preservation/historical audit and final verdict, with the retained
evidence-only helper. Restore the original measured-scope rejection; do not add product rules.

The existing ER01–16 semantics, strong types, source boundary, one foreground/60s command/
1200s pass, no load/retry/framework and same-lifetime wait remain intact. A new exact closure
must name the remaining source rows and full reviewer evidence map/destinations before owner
approval and dispatch. This section neither supplies that unwritten map nor claims advance
approval. No model elevation, policy weakening or source work is authorized by this proposal.

Owner decision is required because A3 still explicitly assigns its full per-predicate evidence
to the implementation owner and its one correction is exhausted. Earlier A1/A2 exceptions do
not grant a global transfer. If the owner chooses another allocation, record it before preparing
the next exact approval object. Meanwhile A3 is NON_DISPATCHABLE, B dependency-blocked, A1/A2
approved but not integrated. REQ-052 local isolated packaging/install evidence remains
NOT_RELEASED; executable gates, combined integration and installation/publication closure are
not complete.

ACTION_COMPLETED / CONVERGENCE_PROPOSED -> WAIT_FOR_HUMAN / EVIDENCE_OWNERSHIP_DECISION.

## 26. A2 closure02 initial findings; same-owner correction — 2026-09-20

Exact owner approval at42643068 was recorded at f4ecfb1 and exercised: retained Luna returned
e6099dc on codex/cvq-01, changing only the admitted two methods/imports. Root's strict16 and
focused27 checks pass, but independent Q18 red cannot identify its cell because construction
precedes subTest. The required retained helper supplied static findings; root independently
confirmed the full batch in [A2 review03 section7](cvq-01a2-case-manifest-admission-code-review.md#7-closure02-initial-review--2026-09-20).

C02-F01–04 cover constructor attribution, binding common-identity isolation, missing PR/HR
literal prerequisite assertions and displaced old positive/full-roundtrip observations.
These violate existing closure02; no new requirement or owner decision is introduced.
Root's remaining41/five-history/preservation proof is incomplete, not delegated or waived.

ACTION_COMPLETED / REVIEW_CHANGES_REQUESTED -> AUTO_CONTINUE / IMPLEMENT_CORRECTION,
same owner and baselinee6099dc, ticket document08, fresh correction1 view, wait_agent only.
This uses closure02's one correction. A1 stays approved; A3/B await A2. Installation closure,
combined source integration and publication remain incomplete; no external effect is granted.

## 27. A2 approved; bind the approved successor — 2026-09-20

Candidate ce49f735 closes A2 under unchanged closure02. [Review04 section8](cvq-01a2-case-manifest-admission-code-review.md#8-closure02-correction-review--approved-2026-09-20)
records root's41 red/restored-green mutations, five historical old-red/current-green cells,
per-observation preservation audit and six old-method replay, strict16/full27 success.
Retained helper returned NO_FINDINGS; root alone approved. All source restoration hashes match.

ACTION_COMPLETED / REVIEW_APPROVED -> AUTO_CONTINUE / BIND_APPROVED_SUCCESSOR.
A3 exact owner approval already exists; pin its predecessor to ce49f735 and this immutable
review/index before reusing Luna with a fresh A3 view. No repeated owner ceremony is required.
A1/A2 are not integrated; A3/B, executable behavior and installation/publication are not done.

## 24. A2 division adopted; finite closure02 prepared — 2026-09-20

Owner 「啟用」 adopts section23 at a4ad0506, LF
`a21ccd9c68335e6b9a0e3deae249613ef2c5d9156794d3fdbbc04391a2af35c3`.
Do not ask that ownership decision again. [A2 document06](../../../modules/tickets/controlled-verification/cvq-01a2-case-manifest-admission.md)
proposes closure02 with one test-file/two-method source boundary:17 explicit legal key
controls,5 opposite-binding negatives and1 named WA04 positive, preserving existing rows.
Retained Luna/xhigh owns that source delta; root owns the complete evidence and final verdict.

The [reviewer evidence plan](cvq-01a2-closure02-evidence-plan.md) revision01 freezes41 exact
temporary predicate experiments,5 current named historical cells, commands and three indexed
destinations. Q24 specifies fail-open missing-case continuation instead of counting KeyError;
Q27 explicitly groups the redundant pure/no-roster guard with derived-scope comparison.
These temporary evidence isolation clauses are in the new approval object, not executed or
silently inherited from closure01. All product contracts and other predicates stay unchanged.

Root's read-only ordinary-constructor/JSON probe at c2fa4cd observed17 legal controls and
five correct root rejections. Source stayed clean; no closure mutation/implementation occurred.
The old contract/history remains immutable at a4ad0506, not copied into a new dispatch prompt.
No private runtime, receipt, new seat, framework, product file or model elevation is introduced.

Section23 explicitly required written exact closure/evidence-map approval before dispatch.
The ownership adoption does not claim a signature on those then-unwritten bytes. Root has now
prepared and indexed that object; old views remain closed and A2 is NON_DISPATCHABLE until
its exact document06 digest and evidence-plan revision01 are approved. Approval then permits
the declared native follow-up/wait/review route, without another ceremonial dispatch question.

ACTION_COMPLETED / CONVERGENCE_ADOPTED / CLOSURE02_PROPOSED -> WAIT_FOR_HUMAN /
OWNER_EXACT_APPROVAL_PENDING. A1 approval, A3/B dependency state and all no-integration/push/
release/install boundaries remain unchanged. Separate REQ-052 remains NOT_RELEASED.

## 25. Exact A2 closure02 approval and continuation — 2026-09-20

Owner 「核准,繼續工作,保持agent wait不要一直停下來等我」 binds the packet at
`42643068e7ab3cd570d8104c1690e1b089bc414e`: A2 document06 LF
`620b37e7e1a262ad852424c144ac7b88a0b1ad7e7379ffe86a7355a70dc796f0` and evidence-plan
revision01 LF `29427a6bff933c21ee5c74777f9453cc1960b3f991f0b75d92d4914c29c3b0de`.
Document07 records only the signature/admission; the approved finite work is unchanged.
The pending route in section24 and the frozen plan's proposal-era header are superseded.
The three evidence destinations remain NOT_RUN, never claimed as completed by approval.

Root verified owner baseline c2fa4cd, clean registered contained worktree, and unchanged
remote/local main b697738d. Retained Luna/xhigh receives one exact identifier-bound follow-up,
fresh ctx-cvq-01a2-closure02 and the unchanged one-file/two-method delta. Root owns the
41-mutation/five-historical-cell evidence and required helper/verdict. No activity polling.

ACTION_COMPLETED / APPROVAL_RECORDED -> AUTO_CONTINUE / IMPLEMENT -> wait_agent -> REVIEW.
No repeated approval request, third closure01 correction, main integration, push or release.
The persistent goal also includes installation closure; separate REQ-052 evidence is not a
claim that controlled verification is complete or publicly installed.

## 19. Evidence ownership adopted; exact finite closure prepared — 2026-09-20

Owner's "核准，先處理上述修正，再重新跑安裝打包驗證" adopts section18 at
`b70b6978b1ad81de175ff6fee4f1ebc9b925e7ff`. Do not ask that ownership question again.
[A1 document05](../../../modules/tickets/controlled-verification/cvq-01a1-scalar-wire-admission.md)
now freezes proposed closure02: three test methods' cell attribution only, 35 root-owned
mutation predicates, exact command map and three indexed evidence destinations. Existing SW01–08,
oracles, counts, ownership, resource bounds and no-partial-integration rule remain intact.

Section18 required that ledger/destinations exist before their exact approval. They did not
exist in b70b697, so the general adoption is not represented as a signature on unwritten bytes.
A1 stays NON_DISPATCHABLE pending document05's exact LF digest approval; closure01 stays closed.
No implementation seat was started for the blocked closure. Once approved, metadata binding and
native dispatch/wait are AUTO_CONTINUE, not another ownership or runner ceremony.

REQ-052's source-policy packaging checks are independent. They cannot qualify the pending
executable responsibility/content gates or turn the CVQ candidates into shipping payload.
ACTION_COMPLETED / CONVERGENCE_ADOPTED / CLOSURE02_PROPOSED -> WAIT_FOR_HUMAN /
OWNER_EXACT_APPROVAL_PENDING for A1 only.

Subsequent exact reply **"核准確定版，直接派工"** binds document05 at `1e50d2ef`,
LF `d25b6c3b3f873a95eccea88e0e8ab222848cb67b5a87ace23958b480a85d0bbf`.
A1 document06 records the signature and unchanged closure02 admission. The pending route in
this section is superseded: AUTO_CONTINUE -> IMPLEMENT -> wait_agent -> root review.

## 20. Closure02 implementation returned; M02 plan defect — 2026-09-20

The retained Luna/xhigh owner completed the bounded three-method attribution repair as
`8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc`. Root reproduced strict/26-test greens and the
required M03 named failure. The retained evidence-only helper found no static defect in that
limited candidate. Neither source-owner performance nor native event delivery is the blocker.

Root executed and captured all35 planned mutations. M02's real-default change makes shared
fixture composition reject before its intended named omission cell. This is a root-authored
closure/evidence-plan defect; do not count its exit1 as proof, or ask Luna to violate the
fixture read-only boundary. [Review revision03](cvq-01a1-scalar-wire-admission-code-review.md)
preserves the precise trace and separates captured outputs from full final review.

[A1 document07](../../../modules/tickets/controlled-verification/cvq-01a1-scalar-wire-admission.md)
proposes only a temporary explicit-valid-value keyword in the reviewer fixture for M02, no
candidate change, no new closure/correction cycle, and no rerun of the other34 captured rows.
All original controls and restoration requirements remain. Owner exact approval is required
because this fixture surface was explicitly forbidden. No exception was executed.

ACTION_COMPLETED / TICKET_DEFECT -> WAIT_FOR_HUMAN / OWNER_EXACT_APPROVAL_PENDING.
A2/A3/B stay dependency-pending; integration, push and publication remain ungranted.
Independent REQ-052 local packaging/install evidence is not an A1 approval or hard-gate claim.

## 21. A1 evidence complete; approved A2 continuation — 2026-09-20

Owner approved document07's exact M02 temporary-fixture amendment at e328f70a, LF
`dc81265a1c9e09ead157dd5049dd59b66dcb93a8805f3db649d39e38aba3dcd0`.
Root performed only that exception, preserving the failed original capture and unchanged
candidate `8d6b8291a03facec9d6d157794e7f4e8ba4d1cdc`. C1 declared-default and C3 named
omission1!=0 assertions turned red, exact restoration returned green, strict15 files and
complete26 tests passed. All35 raw mutation streams are now fully read and reviewed; no
repeat of the other34 experiments. A1 review revision04 is APPROVED / NOT_INTEGRATED.

C02-F01 was the root's fixture-reachability mistake, now closed without an implementation
correction or weaker oracle. Prior exhausted closures remain closed. The retained helper's
required narrow static evidence applies to the same source; root owns the final conclusion.

The already-approved A2 document02 allows exact predecessor/view binding as AUTO_CONTINUE.
Document03 binds8d6 and ctx-cvq-01a2-closure01 for the same retained Luna/xhigh owner.
A3/B remain dependency-pending; no new semantics/model elevation or owner decision is needed.
The reviewer must wait for native completion, then review and obtain the required bounded
adversarial evidence. No partial integration, main mutation, push or publication is granted.

REQ-052's separate local packaging/install verification remains complete but NOT_RELEASED;
its publication-suite timeout/pin gaps and unfinished executable gates are not waived by A1.
ACTION_COMPLETED / REVIEW_APPROVED -> AUTO_CONTINUE / IMPLEMENT(CVQ-01A2).

## 22. A2 initial review; same-closure correction — 2026-09-20

Retained Luna/xhigh returned95434d6 after accepted A1 candidate8d6, only three declared test
and fixture paths changed. Root's strict16-file and27-test checks passed, but independent
mutations found SOURCE_PROPERTY binding and extra nonempty-host-plan gaps with zero red.
The named-cell, complete applicability/preservation, prerequisite positive and raw evidence
gaps are one batch in [A2 review revision01](cvq-01a2-case-manifest-admission-code-review.md).
The retained Terra/xhigh helper supplied bounded static findings; root owns the verdict.

A2 document04 binds that review, exact95434d6 baseline and correction1 view. This consumes
the already-approved single batched correction allowance, not a new closure or owner decision.
No acceptance semantics, source boundary, resource plan or evidence-ownership exception is
changed. A1 remains APPROVED; A3/B await their declared predecessor. No partial integration.

ACTION_COMPLETED / REVIEW_CHANGES_REQUESTED -> AUTO_CONTINUE / CORRECT(CVQ-01A2), retained
Luna/xhigh, native wait_agent then root review. An unsuccessful correction returns convergence.
REQ-052 remains separately LOCAL_ISOLATED_VERIFIED / NOT_RELEASED. Main/push/release unchanged.

## 23. A2 correction exhausted; proposed evidence ownership split — 2026-09-20

The sole correction returnedc2fa4cd, only manifests.py changed. Root verified strict16 files,
27 tests, and real named reds/restoration for the prior SOURCE_PROPERTY and extra host-plan
counterexamples. The distinct prerequisite-pair positive is present. These improvements are
retained, not undone or described as no progress.

[A2 review revision02](cvq-01a2-case-manifest-admission-code-review.md) still finds three
classes incomplete: CM03 positive-control attribution; CM02 opposite-binding and legal key
alternatives; the full pinned raw predicate ledger/current named historical extraction.
R4 independently demonstrates rejecting legal non-HOST host keys without turning CM02 red.
That is an observable test blind spot, not a request for stylistic expansion or a new product
rule. Helper static findings support it; root alone determines CHANGES_REQUESTED.

The assignment still combines test implementation, full preservation mapping, and ownership of
a large mutation/transcript return. Four correction traces are not the whole frozen ledger.
The natural-language completion labels again outrun retrievable evidence. There is no proof
that model tier is the cause or that another identical dispatch will fix it. The source scope
is already small and constructor-local; do not invent a product rearchitecture.

### Recommended decision (OWNER_PENDING; not yet dispatchable)

Apply the previously successful A1 division explicitly to A2, without weakening CM01–07:

- Retained Luna/xhigh owns only the remaining CM02/CM03 test-row corrections in the existing
  manifests responsibility module: literal legal key alternatives, independently controlled
  opposite-binding cases, and named CM03 valid WA04 control. Preserve accepted tests, fixture
  ownership, product contracts and all closed findings. No arbitrary file-length rule.
- Root owns the exact complete predicate/evidence ledger, per-observation relocation audit,
  schema-compatible historical reproduction, unreduced capture and independent reverse
  mutations. Reuse authentic immutable evidence only where it actually proves the current
  obligation; old preflight history is not a substitute for unrun current named tests.
- Before another dispatch, prepare a new finite closure with the exact test rows, root
  mutation map and indexed evidence destinations written down; bind their final digests for
  owner approval. This is not a third repair under exhausted closure01, nor an implicit
  evidence-ownership transfer. The prior A1 exception alone does not authorize A2 changes.
- No model elevation, new framework/runner, policy weakening, budget expansion, implementation
  orchestration by the owner or additional source responsibility. Retain the declared
  one-foreground/60s-command/1200s-pass bounds and event-driven completion wait.

If the owner declines that split, A2 remains blocked until an explicit alternative closure is
approved; do not simply continue the old one. This packet records a proposal only. A1 stays
approved, A3/B await the accepted predecessor, and no partial integration/main mutation/push/
publication is granted. Separate REQ-052 packaging evidence remains NOT_RELEASED.

ACTION_COMPLETED / CONVERGENCE_PROPOSED -> WAIT_FOR_HUMAN / EVIDENCE_OWNERSHIP_DECISION.
