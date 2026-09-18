# CVQ-01 — schema preflight convergence proposal

| Field | Value |
| --- | --- |
| ID / kind / revision | `REVIEW-CONTROLLED-VERIFICATION-CVQ-01-CONVERGENCE` / `CODE_REVIEW` / `03` |
| Lifecycle / conclusion | `OWNER_DESIGN_ADOPTED / EXACT_CONTRACT_APPROVAL_PENDING / NON_DISPATCHABLE` |
| Control baseline | `89d91e68f00ef509537a57b85a32b450e6cca81b` |
| Examined source | `9796790d33b6d1374469fad1b37e1f4991262a43`; initial `cd228a790b2f37bc2cad109978f8822ad5bb2da6` preserved |
| Ticket | [CVQ-01](../../../modules/tickets/controlled-verification/cvq-01-qualification-admission.md), document 04, LF `1ab65b3a70b7bedd43eb017943adbe7bf89509dd18aeb8c3c2d6bcb7876de872`; closure 02 unchanged |
| Contract | [Qualification SPEC](../../../modules/spec/controlled-verification-qualification.md), revision 04, LF `4cad6a88b9d151a05bf409f8b61bc97580e80303f58a2377cb0301815b999a1d` |
| Evidence | [Schema preflight](cvq-01-schema-preflight.md), revision 02, LF `28d8dbd7f3836ac3088829385cf45a0e816e5e27014d28aa8fdbdde27b30eb06` |
| Responsibility | Parent owns this conclusion. Reused Terra/xhigh helper supplied read-only symbol/fixture/AST inventory; no implementation, test execution or approval was delegated in this convergence action |

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

The next control action transcribes the choice into qualification SPEC revision 05, its wire
appendix revision 01 and CVQ-01 document 05 / proposed closure 03. The approval object is that
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
